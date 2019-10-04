#!/usr/bin/env python3
from mwclient.client import Site
from mwclient.page import Page
import wikitextparser as wtp
import json
from typing import List, Tuple
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


def load_page(site: Site) -> Page:
    """Load the wiki page."""
    return site.pages["18_Jahre_Chaosdorf_Lightningtalks"]


def parse_top_section(page: Page) -> Tuple[List[str], str]:
    """Parse the top section, return hosts and date as YYYY-MM-DD."""
    top_section = page.text(section=0)
    parsed_top_section = wtp.parse(top_section)
    hosts = list()
    # `[[User:FIXME|FIXME]]`
    for wikilink in parsed_top_section.wikilinks:
        if wikilink.target.startswith("User:"):
            hosts.append(
                wikilink.target.replace("User:", "").lower()
            )
    # `{{U|FIXME}}`
    for template in parsed_top_section.templates:
        if template.name in ("U", "u"):
            hosts.append(
                template.arguments[0].value.lower()
            )

    date = "2019-10-12"
    return hosts, date


def parse_talks(sections: List[wtp.Section]) -> List[Talk]:
    """Parse the remaining sections: the talks."""
    talks = list()  # type: List[Talk]
    for section in sections[1:]:
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
        description = ""
        for line in section.contents.splitlines():
            if not line.strip():
                continue
            # This tries to filter out lines like "by {{U|FIXME}}".
            if all((person in line.lower() for person in persons)):
                if len(line) < len(",".join(persons)) + len(persons)*10 + 5:  # guessed
                    continue
            description += line.strip() + " "
        description = description.strip()
        talks.append({
            "title": title,
            "description": description,
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
page = load_page(site)
result = parse_page(page)
json.dump(result, open("lightning-talks.json", "w"))
