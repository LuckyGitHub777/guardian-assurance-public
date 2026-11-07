"""Render a reviewed, static public collection from one local catalog.

No GitHub API, network, telemetry, or automatic publication of new repositories.
Usage: python tools/render_selected_works.py [--check]
"""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "collection" / "catalog.json"
HTML = ROOT / "SELECTED_PUBLIC_WORKS.html"
MARKDOWN = ROOT / "SELECTED_PUBLIC_WORKS.md"
START = "<!-- COLLECTION:START -->"
END = "<!-- COLLECTION:END -->"
SOURCE_RE = re.compile(r"https://github[.]com/LuckyGitHub777/[a-z0-9-]+\Z")
ID_RE = re.compile(r"[a-z][a-z0-9-]*\Z")
APPROVED_HOSTS = {"luckygithub777.github.io", "eulers.id"}


def read_catalog():
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported catalog version")
    collections = data.get("collections")
    works = data.get("works")
    if not isinstance(collections, list) or not isinstance(works, list) or not collections or not works:
        raise ValueError("Catalog requires nonempty collections and works")
    ids = []
    for collection in collections:
        ident, title = collection["id"], collection["title"]
        if not ID_RE.fullmatch(ident) or not title.strip() or title.endswith((".", "!", "?")):
            raise ValueError("Invalid collection")
        ids.append(ident)
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate collection")
    sources = set()
    sites = set()
    for work in works:
        title, summary, site, source = (work[k] for k in ("title", "summary", "site", "source"))
        if work["collection"] not in ids or not title.strip() or not summary.strip():
            raise ValueError("Incomplete work entry")
        if title.endswith((".", "!", "?")) or summary.endswith((".", "!", "?")):
            raise ValueError("Display copy must be punctuation-free")
        if not SOURCE_RE.fullmatch(source):
            raise ValueError("Source must be an explicit public owner/repository URL")
        url = urlparse(site)
        if url.scheme != "https" or url.hostname not in APPROVED_HOSTS or url.query or url.fragment or url.username:
            raise ValueError("Unapproved project website")
        if source in sources or site in sites:
            raise ValueError("Duplicate source or website")
        sources.add(source)
        sites.add(site)
    if any(not any(w["collection"] == ident for w in works) for ident in ids):
        raise ValueError("Empty collection")
    return collections, works


def render_html(collections, works):
    total = len(works)
    buttons = "".join(
        f'<button type="button" data-filter="{escape(c["id"])}" aria-pressed="false" disabled>{escape(c["title"])}</button>'
        for c in collections
    )
    controls = (
        '<div class="controls" id="collection" role="search"><label class="search-field"><span class="visually-hidden">Search works</span>'
        '<input id="find" type="search" placeholder="Find something extraordinary" aria-label="Search works" disabled></label>'
        '<div class="filters" role="group" aria-label="Browse by collection"><div class="filter-all">'
        '<button type="button" data-filter="all" aria-pressed="true" disabled>All Works</button></div>'
        f'<div class="filter-categories">{buttons}</div></div>'
        f'<span id="count" class="count" aria-live="polite">Showing {total} of {total} works</span>'
        '<p id="empty" class="empty-state" hidden>No works found<span>Try a new search or return to All Works</span></p></div>'
    )
    groups = []
    for collection in collections:
        ident = escape(collection["id"])
        selected = [w for w in works if w["collection"] == collection["id"]]
        cards = []
        for number, item in enumerate(selected, 1):
            title = escape(item["title"])
            cards.append(
                f'<article class="work" data-category="{ident}">'
                f'<div class="work-no">{number:02d}</div>'
                f'<h3><a href="{escape(item["site"])}" target="_blank" rel="noopener noreferrer">'
                f'{title}<span aria-hidden="true"> ↗</span></a></h3>'
                f'<p class="work-description">{escape(item["summary"])}</p>'
                f'<div class="work-footer"><a href="{escape(item["source"])}" '
                f'aria-label="View source repository for {title}" target="_blank" rel="noopener noreferrer">'
                'View the source</a></div></article>'
            )
        cards_html = "\n".join(cards)
        groups.append(
            f'<section class="group" data-collection="{ident}" data-group aria-labelledby="heading-{ident}">'
            f'<div class="group-title"><h2 id="heading-{ident}">{escape(collection["title"])}</h2>'
            f'<span>{len(selected)} {"work" if len(selected) == 1 else "works"}</span></div>'
            f'<div class="cards">{cards_html}</div></section>'
        )
    return controls + "\n" + "\n".join(groups)


def render_markdown(collections, works):
    total = len(works)
    pages = sum(w["site"].startswith("https://luckygithub777.github.io/") for w in works)
    other = total - pages
    lines = [
        "# Selected public works",
        "",
        f"A browseable collection of **{total} public repositories**, with **{pages} GitHub Pages project URLs** and **{other} custom-domain experience{'s' if other != 1 else ''}**. "
        "Select a project title to open its website, or select **View source repository** to inspect its public GitHub files. Gallery links open in a new tab. "
        "A hosted page may present an interactive experience, an educational showcase, or an introduction to downloadable software.",
        "",
        "Some works have different scopes and technical requirements. The public gallery is not a security certification, license grant, or endorsement. "
        "Private origins, unpublished releases, and internal review materials are not part of this collection.",
        "",
        "## Independent educational website",
        "",
        "- [Euler’s Identity · Mathematical Form and Reflection](https://luckygithub777.github.io/guardian-assurance-public/divine-architecture/) · "
        "A separate educational study, outside the source-repository collection",
        "",
    ]
    for collection in collections:
        lines += [f'## {collection["title"]}', ""]
        for item in works:
            if item["collection"] != collection["id"]:
                continue
            line = f'- [{item["title"]}]({item["site"]}) · {item["summary"]}. [View source repository]({item["source"]})'
            if item.get("browser_experience"):
                line += f' · [Browser experience]({item["site"]})'
            lines.append(line)
        lines.append("")
    lines += [
        "---",
        "",
        "This curated list is rendered from `collection/catalog.json` using `python tools/render_selected_works.py`. "
        "Only intentionally reviewed public entries belong in the catalog. No service, tracking, scheduled discovery, or third-party integration is required.",
        "",
        "[Browse the visual gallery](https://luckygithub777.github.io/guardian-assurance-public/SELECTED_PUBLIC_WORKS.html) · "
        "[View the source HTML](SELECTED_PUBLIC_WORKS.html)",
        "",
    ]
    return "\n".join(lines)


def render_page(existing, fragment):
    if existing.count(START) != 1 or existing.count(END) != 1:
        raise ValueError("Missing unique gallery generation markers")
    prefix, rest = existing.split(START, 1)
    _, suffix = rest.split(END, 1)
    return prefix + START + "\n" + fragment + "\n" + END + suffix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated outputs are current without writing")
    options = parser.parse_args()
    categories, works = read_catalog()
    current_html = HTML.read_text(encoding="utf-8")
    expected_html = render_page(current_html, render_html(categories, works))
    expected_md = render_markdown(categories, works)
    stale = [str(path.name) for path, wanted in ((HTML, expected_html), (MARKDOWN, expected_md))
             if path.read_text(encoding="utf-8") != wanted]
    if options.check:
        if stale:
            parser.exit(1, "Gallery out of date: " + ", ".join(stale) + "\nRun python tools/render_selected_works.py\n")
        print(f"OK: {len(works)} reviewed works, {len(categories)} collections, both pages in sync")
        return
    HTML.write_text(expected_html, encoding="utf-8")
    MARKDOWN.write_text(expected_md, encoding="utf-8")
    print(f"Rendered {len(works)} works in {len(categories)} collections")


if __name__ == "__main__":
    main()
