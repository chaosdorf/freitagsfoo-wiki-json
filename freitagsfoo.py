#!/usr/bin/env python3
from mwclient.client import Site
from mwclient.page import Page
import wikitextparser as wtp
import datetime
import json
from typing import List, Tuple
from mypy_extensions import TypedDict

Talk = TypedDict("Talk", {
    "title": str,
    # "description": str,
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


def parse_talks(sections: List[wtp.Section]) -> List[Talk]:
    """Parse the remaining sections: the talks."""
    talks: List[Talk] = list()
    for section in sections[1:]:
        title = section.title.strip()
        # TODO: description
        persons: List[str] = list()
        section = wtp.parse(section.string)  # bug!
        # `[[User:FIXME|FIXME]]`
        for wikilink in section.wikilinks:
            if wikilink.target.startswith("User:"):
                persons.append(
                    wikilink.target.replace("User:", "").lower()
                )
        # `{{U|FIXME}}`
        for template in section.templates:
            if template.name == "U":
                persons.append(
                    template.arguments[0].value.lower()
                )
        talks.append({
            "title": title,
            # "description": description,
            "persons": persons,
        })
    return talks


def parse_page(page: Page) -> Result:
    """Parse the given sections returning a dict."""
    hosts, date = parse_top_section(page)
    sections = wtp.parse(page.text()).sections
    talks = parse_talks(sections)
    return {
        "hosts": hosts,
        "date": date,
        "talks": talks
    }


site = Site("wiki.chaosdorf.de", path="/")
date = get_friday()
page = load_page_for_date(site, date)
result = parse_page(page)
assert result["date"] == str(date)
json.dump(result, open("freitagsfoo.json", "w"))
