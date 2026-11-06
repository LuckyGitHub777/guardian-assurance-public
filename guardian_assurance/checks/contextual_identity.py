"""Optional, redacted contextual identity screening at a publication boundary.

Private match terms are supplied only through the process environment. This
check covers the current tracked text tree; Git history and binaries are
separate mandatory release-review decisions.
"""
from __future__ import annotations

import os
from pathlib import Path

from . import CheckResult, Finding
from ..repository_view import read_text, requires_text_scan, tracked_files


def run(root: Path, policy: dict) -> CheckResult:
    raw = os.environ.get("GUARDIAN_OPSEC_DENYLIST", "")
    # Bound work and reject malformed or missing required private input.
    if len(raw) > 65536:
        return CheckResult("contextual_identity", "INDETERMINATE", "private context exceeds supported size")
    supplied = [term.strip() for term in raw.splitlines() if term.strip()]
    # Do not silently drop a requested short term when longer terms also
    # exist: that would allow a partial scan to claim full contextual PASS.
    # Reject without emitting the private term or a filename in the receipt.
    if any(len(term) < 3 for term in supplied):
        return CheckResult("contextual_identity", "INDETERMINATE", "private context contains unsupported short terms")
    terms = tuple(dict.fromkeys(term.casefold() for term in supplied))
    if len(terms) > 256:
        return CheckResult("contextual_identity", "INDETERMINATE", "too many private context terms")
    if not terms:
        return CheckResult("contextual_identity", "INDETERMINATE", "private contextual screening not configured")

    files, verified = tracked_files(root)
    if not verified:
        return CheckResult("contextual_identity", "INDETERMINATE", "tracked file inventory unavailable")

    max_bytes = int(policy["repository"]["max_text_bytes"])
    findings: list[Finding] = []
    skipped = 0
    for rel in files:
        # A matching filename is never reproduced in a public or private receipt.
        if any(term in rel.as_posix().casefold() for term in terms):
            findings.append(Finding("PRIVATE_CONTEXT_PATH", None, "private filename match; value and path redacted"))
        text = read_text(root, rel, max_bytes)
        if text is None:
            if requires_text_scan(rel):
                skipped += 1
            continue
        if any(term in text.casefold() for term in terms):
            findings.append(Finding("PRIVATE_CONTEXT_CONTENT", None, "private content match; value and path redacted"))

    if findings:
        return CheckResult(
            "contextual_identity", "FAIL",
            "private contextual identity material detected",
            tuple(findings),
        )
    if skipped:
        return CheckResult(
            "contextual_identity", "INDETERMINATE",
            "some expected text files could not be inspected",
            metadata={"uninspected_text_files": str(skipped)},
        )
    return CheckResult(
        "contextual_identity", "PASS",
        "no private contextual matches in the inspected current tracked text tree",
    )
