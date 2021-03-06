#!/usr/bin/env python3
from bs4 import BeautifulSoup
from mwclient.client import Site
from mwclient.page import Page
import wikitextparser as wtp
import datetime
import json
from typing import Callable, List, Tuple
from mypy_extensions import TypedDict

Talk = TypedDict("Talk", {
    "title": str,
    "description": str,
    "persons": List[str],
})
Result = TypedDict("Result", {
    "hosts": List[str],
    "date": str,
    "talks": List[Talk],
})


def get_friday() -> datetime.date:
    """Calculate the date of the current week's Friday."""
    today = datetime.date.today()
    return today + datetime.timedelta(days=4-today.weekday())


def load_page_for_date(site: Site, date: datetime.date) -> Page:
    """Load the Freitagsfoo wiki page for the given date."""
    return site.pages["Freitagsfoo/{}".format(date)]


def parse_top_section(page: Page) -> Tuple[List[str], str]:
    """Parse the top section, return hosts and date as YYYY-MM-DD."""
    top_section = page.text(section=0)
    parsed_top_section = wtp.parse(top_section)
    parsed_event = parsed_top_section.templates[0]
    hosts = list()
    for host in parsed_event.get_arg("Host").value.split(","):
        hosts.append(host.strip().lower())
    date = parsed_event.get_arg("Date").value.strip()
    return hosts, date


def parse_talks(
    sections: List[wtp.Section], render_function: Callable[[str], str] = None
) -> List[Talk]:
    """
    Parse the remaining sections: the talks.
    
    If given a render_function,
    let it convert the wikitext descriptions to plain text.
    """
    talks = list()  # type: List[Talk]
    if render_function is None:
        print("[WARN] Don't know how to render wikitext.")
        print("[WARN] Descriptions will be empty.")
    for section in sections[1:]:
        # ignore section if depth is greater than 2
        if section.level > 2:
            continue
        title = section.title.strip()
        persons = list()  # type: List[str]
        section_ = wtp.parse(section.string)  # bug!
        # `[[User:FIXME|FIXME]]`
        for wikilink in section_.wikilinks:
            if wikilink.target.startswith("User:"):
                persons.append(
                    wikilink.target.replace("User:", "").lower()
                )
        # `{{U|FIXME}}`
        for template in section_.templates:
            if template.name in ("U", "u"):
                persons.append(
                    template.arguments[0].value.lower()
                )
        # description
        if render_function is not None:
            description = render_function(section.contents)
        else:
            description = ""
        talks.append({
            "title": title,
            "description": description,
            "persons": persons,
        })
    return talks


def parse_page(
    page: Page, render_function: Callable[[str], str] = None
) -> Result:
    """
    Parse the given sections returning a dict.
    
    If given a render_function,
    use it to convert the wikitext descriptions to plain text.
    """
    hosts, date = parse_top_section(page)
    sections = wtp.parse(page.text()).sections
    talks = parse_talks(sections, render_function)
    return {
        "hosts": hosts,
        "date": date,
        "talks": talks
    }


def create_online_html_render_function(site: Site) -> Callable[[str], str]:
    """Create a function (str) -> str that converts wikitext to plain text."""
    def online_html_render_function(wikitext: str) -> str:
        """Convert wikitext to plain text by rendering it on the server."""
        html = site.parse(text=wikitext)["text"]["*"]
        soup = BeautifulSoup(html)
        return soup.text.strip()
    return online_html_render_function


if __name__ == "__main__":
    site = Site("wiki.chaosdorf.de", path="/")
    date = get_friday()
    page = load_page_for_date(site, date)
    result = parse_page(page, create_online_html_render_function(site))
    assert result["date"] == str(date)
    json.dump(result, open("freitagsfoo.json", "w"), ensure_ascii=False)
