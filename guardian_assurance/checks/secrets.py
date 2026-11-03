from __future__ import annotations

from pathlib import Path
import re
from . import CheckResult, Finding
from ..repository_view import tracked_files, read_text, requires_text_scan

RULES = {
    "github_classic": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "github_fine_grained": re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    "aws_access_key": re.compile(r"(?:AKIA|ASIA)[A-Z0-9]{16}"),
    "private_key": re.compile(
        "-----BEGIN "
        + r"(?:(?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY|PGP PRIVATE KEY BLOCK)-----"
    ),
    "slack_token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    "stripe_live_key": re.compile(r"sk_live_[A-Za-z0-9]{20,}"),
    "google_api_key": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
}


def run(root: Path, policy: dict) -> CheckResult:
    enabled = policy["secrets"].get("enabled_rules", [])
    unknown = sorted(set(enabled) - set(RULES))
    if unknown:
        return CheckResult("secrets", "INDETERMINATE", "policy references unknown secret-detection rules")

    max_bytes = int(policy["repository"].get("max_text_bytes", 1048576))
    files, _ = tracked_files(root)
    findings: list[Finding] = []
    skipped_text = 0
    for rel in files:
        text = read_text(root, rel, max_bytes)
        if text is None:
            if requires_text_scan(rel):
                skipped_text += 1
            continue
        for rule_name in enabled:
            if RULES[rule_name].search(text):
                findings.append(Finding("SECRET_PATTERN", rel.as_posix(), f"{rule_name} pattern detected; value redacted"))

    if findings:
        return CheckResult("secrets", "FAIL", "potential secret material detected", tuple(findings))
    if skipped_text:
        return CheckResult(
            "secrets", "INDETERMINATE",
            "expected text files were not fully inspected",
            metadata={"uninspected_text_files": str(skipped_text)},
        )
    return CheckResult("secrets", "PASS", "no enabled secret patterns detected")
