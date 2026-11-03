from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Status = Literal["PASS", "FAIL", "INDETERMINATE"]

@dataclass(frozen=True)
class Finding:
    code: str
    path: str | None = None
    detail: str | None = None

@dataclass(frozen=True)
class CheckResult:
    name: str
    status: Status
    summary: str
    findings: tuple[Finding, ...] = field(default_factory=tuple)
    metadata: dict[str, str] = field(default_factory=dict)
