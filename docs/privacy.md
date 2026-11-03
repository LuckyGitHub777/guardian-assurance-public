# Privacy

Guardian is local-first and network-off by design.

Receipts intentionally exclude:

- secret values;
- usernames;
- hostnames;
- home directories;
- machine identifiers;
- environment-variable dumps;
- absolute local user paths.

Findings use repository-relative paths and safe rule identifiers. Secret values are never copied into receipt output.
