"""Static gallery quality checks for a growing, catalog-driven collection."""

from html import unescape
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "SELECTED_PUBLIC_WORKS.html"
CATALOG = ROOT / "collection" / "catalog.json"


def inventory():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def test_generation_is_reproducible_without_network():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "render_selected_works.py"), "--check"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=10,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_collection_titles_are_short_and_punctuation_free():
    html = GALLERY.read_text(encoding="utf-8")
    data = inventory()
    titles = [unescape(x) for x in re.findall(r"<h2[^>]*>(.*?)</h2>", html)]
    buttons = [unescape(x) for x in re.findall(r'<button[^>]*data-filter="(?:security|learning|science|creative)"[^>]*>(.*?)</button>', html)]
    expected = [x["title"] for x in data["collections"]]
    assert titles == buttons == expected
    assert all(not title.endswith((".", "!", "?")) for title in titles)
    assert "<h1>Ideas in<br>motion</h1>" in html


def test_static_links_and_card_copy_match_catalog():
    html = GALLERY.read_text(encoding="utf-8")
    works = inventory()["works"]
    n = len(works)
    assert html.count('<article class="work"') == n
    assert html.count('aria-label="View source repository for ') == n
    assert html.count('>View the source</a>') == n
    assert html.count('target="_blank"') == n * 2
    assert html.count('rel="noopener noreferrer"') == n * 2
    assert html.count('href="./divine-architecture/"') == 1
    captions = re.findall(r'<p class="work-description">(.*?)</p>', html)
    assert len(captions) == n
    assert all(caption and not caption.endswith((".", "!", "?")) for caption in captions)


def test_darker_luxury_design_has_centered_all_works_and_middle_axis():
    html = GALLERY.read_text(encoding="utf-8")
    assert 'color-scheme:dark' in html
    assert '.filter-all{display:flex;align-items:center;justify-content:center;width:100%;margin:0 auto}' in html
    assert '<div class="filter-all"><button type="button" data-filter="all" aria-pressed="true" disabled>All Works</button></div>' in html
    assert '.filter-categories{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;' in html
    assert '.group-title:before' in html and 'header:after' in html
    assert 'justify-content:center;align-items:stretch;gap:17px;max-width:1160px' in html
    assert '.group[data-collection="security"] .cards{max-width:870px}' in html
    assert 'background:rgba(213,190,148,.11)' in html
    assert "@media(max-width:740px)" in html
    assert "@media(max-width:650px)" in html
    assert "@media(prefers-reduced-motion:reduce)" in html
    assert "@media(forced-colors:active)" in html


def test_search_and_no_javascript_fallback_remain_available():
    html = GALLERY.read_text(encoding="utf-8")
    assert 'id="empty" class="empty-state" hidden' in html
    assert 'empty.hidden=visible!==0;' in html
    assert 'c.querySelector("h3").textContent' in html
    assert 'c.querySelector(".work-description").textContent' in html
    assert "No works found" in html
    assert 'id="find" type="search"' in html
    assert '<a class="skip" href="#collection">' in html
    assert 'default-src \'none\'' in html
    assert 'fetch(' not in html and 'localStorage' not in html
