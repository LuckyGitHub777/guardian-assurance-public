"""Editorial gallery invariants for a centered and accessible public collection."""

from html import unescape
from pathlib import Path
import re

GALLERY = (Path(__file__).resolve().parents[1] / "SELECTED_PUBLIC_WORKS.html")


def test_gallery_uses_short_punctuation_free_collection_headings():
    html = GALLERY.read_text(encoding="utf-8")
    headings = [unescape(x) for x in re.findall(r"<h2>(.*?)</h2>", html)]
    filters = [unescape(x) for x in re.findall(r'<button[^>]*data-filter="[0-3]"[^>]*>(.*?)</button>', html)]
    assert headings == [
        "Security & Assurance",
        "Learning & Practice",
        "Science & Inquiry",
        "Art & Expression",
    ]
    assert filters == headings
    assert all(not title.endswith((".", "!", "?")) for title in headings)
    assert "<h1>Where ideas<br>take form</h1>" in html


def test_gallery_preserves_accessible_navigation_and_independent_sources():
    html = GALLERY.read_text(encoding="utf-8")
    assert html.count('<article class="work"') == 34
    assert html.count('aria-label="View source repository for ') == 34
    assert html.count('>View the source</a>') == 34
    assert html.count('target="_blank"') == 68
    assert html.count('rel="noopener noreferrer"') == 68
    assert html.count('href="./divine-architecture/"') == 1
    captions = re.findall(r'<p class="work-description">(.*?)</p>', html)
    assert len(captions) == 34
    assert all(caption and not caption.endswith((".", "!", "?")) for caption in captions)


def test_middle_axis_and_responsive_card_rhythm():
    html = GALLERY.read_text(encoding="utf-8")
    assert ".group-title:before" in html
    assert "justify-content:center;gap:19px;max-width:1160px" in html
    assert '.group[data-collection="security"] .cards{max-width:875px}' in html
    assert "@media(max-width:740px)" in html
    assert "@media(max-width:650px)" in html
    assert "@media(prefers-reduced-motion:reduce)" in html
    assert "@media(forced-colors:active)" in html


def test_zero_results_have_guidance_and_search_excludes_generic_source_text():
    html = GALLERY.read_text(encoding="utf-8")
    assert 'id="empty" class="empty-state" hidden' in html
    assert "empty.hidden=visible!==0;" in html
    assert 'c.querySelector("h3").textContent' in html
    assert 'c.querySelector(".work-description").textContent' in html
    assert "No works found" in html
