from __future__ import annotations

from pathlib import Path
from . import CheckResult, Finding
from ..repository_view import tracked_files


def run(root: Path, policy: dict) -> CheckResult:
    cfg = policy["repository"]
    findings: list[Finding] = []

    files, verified = tracked_files(root)
    if not verified:
        return CheckResult("repository", "INDETERMINATE", "tracked Git file inventory unavailable")
    tracked = {rel.as_posix() for rel in files}

    for required in cfg.get("required_files", []):
        if required not in tracked:
            findings.append(
                Finding(
                    "REQUIRED_FILE_NOT_TRACKED",
                    required,
                    "required publication file is not part of the attested revision",
                )
            )
        elif not (root / required).is_file():
            findings.append(
                Finding(
                    "REQUIRED_FILE_MISSING",
                    required,
                    "required publication file is absent from the working tree",
                )
            )

    names = set(cfg.get("forbidden_tracked_names", []))
    segments = set(cfg.get("forbidden_tracked_segments", []))
    for rel in files:
        if rel.name in names:
            findings.append(
                Finding(
                    "FORBIDDEN_TRACKED_FILE",
                    rel.as_posix(),
                    "machine/local artifact is tracked",
                )
            )
        elif any(part in segments for part in rel.parts):
            findings.append(
                Finding(
                    "FORBIDDEN_TRACKED_PATH",
                    rel.as_posix(),
                    "machine/local path segment is tracked",
                )
            )

    if findings:
        return CheckResult(
            "repository",
            "FAIL",
            "repository publication controls require attention",
            tuple(findings),
        )
    return CheckResult(
        "repository",
        "PASS",
        "required repository publication controls are present and tracked",
    )
