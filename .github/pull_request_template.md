## Change

Describe the smallest intended outcome.

## Evidence

- [ ] `python -m pytest -q` passes.
- [ ] `guardian-pa verify . --receipt ../guardian-receipt.json` returns `VERIFIED`.
- [ ] No secrets, machine-specific identity, private context, or unrelated artifacts are included.
- [ ] Assurance semantics changed only with corresponding tests and documentation.
