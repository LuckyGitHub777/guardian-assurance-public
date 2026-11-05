from __future__ import annotations

from pathlib import Path
import re
from . import CheckResult, Finding
from ..repository_view import tracked_files, read_text, requires_text_scan

WINDOWS_USER_PATH = re.compile(r"(?i)[A-Z]:[\\/]+Users[\\/]+[^\\/\s\"'<>]+")
UNIX_USER_PATH = re.compile(r"/(?:home|Users)/[^/\s\"'<>]+")

def run(root: Path, policy: dict) -> CheckResult:
    if not policy["environment"].get("block_absolute_user_paths", True):
        return CheckResult("environment", "PASS", "absolute user-path check disabled by policy")

    max_bytes = int(policy["repository"].get("max_text_bytes", 1048576))
    files, verified = tracked_files(root)
    if not verified:
        return CheckResult("environment", "INDETERMINATE", "tracked Git file inventory unavailable")
    findings: list[Finding] = []
    skipped_text = 0
    for rel in files:
        text = read_text(root, rel, max_bytes)
        if text is None:
            if requires_text_scan(rel):
                skipped_text += 1
            continue
        if WINDOWS_USER_PATH.search(text) or UNIX_USER_PATH.search(text):
            findings.append(Finding("LOCAL_USER_PATH", rel.as_posix(), "machine-specific user path detected; value redacted"))

    if findings:
        return CheckResult("environment", "FAIL", "machine-specific environment data requires attention", tuple(findings))
    if skipped_text:
        return CheckResult(
            "environment", "INDETERMINATE",
            "expected text files were not fully inspected",
            metadata={"uninspected_text_files": str(skipped_text)},
        )
    return CheckResult("environment", "PASS", "no common machine-specific user paths detected")
