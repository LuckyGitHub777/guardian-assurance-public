# Contributing

Guardian favors small, reviewable, evidence-backed changes.

1. Open or reference a focused issue when the change is material.
2. Create a narrow branch.
3. Add or update tests before changing assurance semantics.
4. Run `python -m pytest -q`.
5. Run `guardian-pa verify . --receipt ../guardian-receipt.json`.
6. Confirm no private context, machine-specific identity, real credentials, or unrelated artifacts are included.
7. Submit a pull request.

Do not weaken a valid gate to make CI pass. If a required check cannot be performed reliably, preserve `INDETERMINATE` rather than converting uncertainty into success.
