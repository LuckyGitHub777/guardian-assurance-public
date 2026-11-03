from __future__ import annotations

from pathlib import Path
from . import CheckResult, Finding
from ..repository_view import run_git

def run(root: Path, policy: dict) -> CheckResult:
    cp = run_git(root, "log", "-1", "--format=%ae")
    if cp.returncode != 0 or not cp.stdout.strip():
        return CheckResult("identity", "INDETERMINATE", "could not resolve Git author identity")

    email = cp.stdout.strip()
    lowered = email.lower()
    findings: list[Finding] = []
    for fragment in policy["identity"].get("forbidden_author_fragments", []):
        if fragment.lower() in lowered:
            findings.append(Finding("AUTHOR_IDENTITY_PLACEHOLDER", None, "Git author identity matches a forbidden local/test pattern"))
            break

    if findings:
        return CheckResult("identity", "FAIL", "publication identity requires attention", tuple(findings))

    domain = email.rsplit("@", 1)[-1] if "@" in email else "unknown"
    return CheckResult("identity", "PASS", "Git author identity is not an obvious local/test placeholder", metadata={"author_domain": domain})
