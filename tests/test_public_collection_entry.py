"""Offline public-collection invariants. No network, secrets or release automation."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OWNER = "LuckyGitHub777"
LINK = re.compile(r"https://github[.]com/" + OWNER + r"/([a-z0-9-]+)")


def test_gallery_and_markdown_contain_same_public_repositories():
    markdown = (ROOT / "SELECTED_PUBLIC_WORKS.md").read_text(encoding="utf-8")
    html = (ROOT / "SELECTED_PUBLIC_WORKS.html").read_text(encoding="utf-8")
    a, b = LINK.findall(markdown), LINK.findall(html)
    assert len(a) == len(set(a)) == 34
    assert len(b) == len(set(b)) == 34
    assert set(a) == set(b)


def test_static_entrypoint_has_no_outbound_dependency_or_unsafe_input():
    source = (ROOT / "index.html").read_text(encoding="utf-8")
    assert '<title>Guardian | Publication Assurance</title>' in source
    assert '<meta name="description"' in source
    assert 'guardian-pa verify .' in source
    assert '<h1>Publish with proof.' in source
    assert '<meta http-equiv="refresh"' not in source
    assert 'href="./SELECTED_PUBLIC_WORKS.html"' in source
    assert 'href="./SELECTED_PUBLIC_WORKS.md"' in source
    assert 'default-src \'none\'' in source
    assert "<script" not in source.lower()
    assert "http://" not in source and "https://" not in source
    assert "chatgpt.com" not in source.lower()
    assert "\\Users\\" not in source


def test_published_browser_experiences_are_visible_in_both_collection_formats():
    """Link separately deployed project sites while retaining exactly one repo card each."""
    markdown = (ROOT / "SELECTED_PUBLIC_WORKS.md").read_text(encoding="utf-8")
    html = (ROOT / "SELECTED_PUBLIC_WORKS.html").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for repo in ("gravitas-check", "mysteries-of-eleusis"):
        url = f"https://luckygithub777.github.io/{repo}/"
        assert markdown.count(f"[Browser experience]({url})") == 1
        assert html.count(f'href="{url}"') == 1
        # Keep the Guardian product README focused on Guardian itself.
        assert url not in readme
    assert len(LINK.findall(markdown)) == len(LINK.findall(html)) == 34
