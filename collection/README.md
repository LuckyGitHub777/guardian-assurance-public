# The Collection

One intentional source of truth: [`catalog.json`](catalog.json)

The gallery is a static publication, not a live list of every repository. This protects the distinction between **public and ready to exhibit** and **private, unfinished, or not yet reviewed**.

## Add a work

1. Confirm that the intended repository, public website, history, media, rights, and visitor experience have been reviewed and approved for publication
2. Add one `works` item to `catalog.json` with `collection`, `title`, `summary`, `site`, and `source`
3. Put the item in the desired order within its collection. To add a new collection, append an `id` and a short `title` under `collections`
4. From the repository root, run:

```bash
python tools/render_selected_works.py
python tools/render_selected_works.py --check
python -m pytest -q
```

5. Review the generated gallery and Markdown index, including narrow-screen reading and link destinations, then publish through the normal reviewed PR process

The renderer automatically recalculates section counts, card numbering, category filters, link labels, and the Markdown inventory. The public visitor sees the generated static HTML, including all links if JavaScript is disabled.

## Boundaries

- Nothing is auto-discovered, made public, scheduled, or imported from private repositories
- No GitHub API keys, background analytics, font downloads, or remote runtime dependencies
- The website host allowlist is deliberately narrow; approving a new custom domain requires a deliberate change to the renderer
- Project display names may differ from repository slugs; existing repository names and URLs remain unchanged
- Do not use personal identifiers, internal planning language, secrets, unpublished work, or unreleased evidence in the catalog
- A source repository and a web experience are separate destinations, never an implied security certification

The collection grows by adding reviewed data, not by copying card markup.
