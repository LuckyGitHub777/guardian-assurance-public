"""Confirm the collection grows from reviewed data without hand-editing HTML."""

from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]


def test_an_extra_work_and_category_render_from_catalog():
    api = runpy.run_path(str(ROOT / "tools" / "render_selected_works.py"))
    collections, works = api["read_catalog"]()
    extra = {
        "collection": "new-medium",
        "title": "Sample Reviewed Work",
        "summary": "A hypothetical reviewed work for offline test coverage",
        "site": "https://luckygithub777.github.io/sample-reviewed-work/",
        "source": "https://github.com/LuckyGitHub777/sample-reviewed-work",
    }
    future_collections = collections + [{"id": "new-medium", "title": "New Medium"}]
    future_works = works + [extra]

    page = api["render_html"](future_collections, future_works)
    listing = api["render_markdown"](future_collections, future_works)
    n = len(future_works)

    assert f'Showing {n} of {n} works' in page
    assert f'<button type="button" data-filter="new-medium"' in page
    assert '<h2 id="heading-new-medium">New Medium</h2><span>1 work</span>' in page
    assert page.count('<article class="work"') == n
    assert page.count('target="_blank"') == 2 * n
    assert f'**{n} public repositories**' in listing
    assert '## New Medium' in listing
    assert 'Sample Reviewed Work' in listing
    assert 'sample-reviewed-work' in page
