"""Website release contract: a standalone public page, not private manuscript publication.

Every assertion is offline and exact-source scoped; live HTTPS evidence is separate.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "divine-architecture/index.html"
PAGE_URL = "https://luckygithub777.github.io/guardian-assurance-public/divine-architecture/"


def test_educational_site_is_independent_and_no_external_io():
    html = PAGE.read_text(encoding="utf-8")
    assert '<html lang="en">' in html
    assert '<meta name="robots" content="index, follow">' in html
    assert "default-src 'none'" in html
    assert '<a class="skip" href="#content">' in html
    assert '<meta name="viewport"' in html
    assert "Euler's formula states" in html
    assert "not reproduce or release any private manuscript" in html
    assert "does not, on its own, establish claims about physics" in html
    for forbidden in (
        "<script", "<iframe", "<form", "<img", "<link rel=\"stylesheet\"",
        "<link rel=\"preconnect\"", "http://", "https://",
        "localStorage",
        "sessionStorage", "fetch(", "utm_source",
    ):
        assert forbidden.lower() not in html.lower(), forbidden
    assert re.search(r"<h1\b", html) and len(re.findall(r"<h1\b", html)) == 1


def test_public_site_is_discoverable_without_changing_source_gallery_count():
    md = (ROOT / "SELECTED_PUBLIC_WORKS.md").read_text(encoding="utf-8")
    gallery = (ROOT / "SELECTED_PUBLIC_WORKS.html").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert md.count(PAGE_URL) == 1
    # Keep the Guardian product README scoped to Guardian. The independent
    # educational site belongs in the dedicated gallery navigation, not here.
    assert PAGE_URL not in readme
    assert "## Independent educational website" not in readme
    assert "## Independent public works" not in readme
    assert "Guardian is a local-first, read-only publication assurance tool" in readme
    assert "https://github.com/LuckyGitHub777/" not in readme
    assert gallery.count('href="./divine-architecture/"') == 1
    repo_links = r"https://github[.]com/LuckyGitHub777/([a-z0-9-]+)"
    assert len(re.findall(repo_links, md)) == 34
    assert len(re.findall(repo_links, gallery)) == 34
    assert "does not publish a private manuscript" in gallery
