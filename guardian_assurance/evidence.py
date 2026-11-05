from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
from . import __version__
from .checks import CheckResult
from .policy import policy_digest

def build_receipt(policy: dict, results: list[CheckResult], result: str) -> dict:
    provenance = next((r for r in results if r.name == "provenance"), None)
    revision = provenance.metadata.get("revision") if provenance else None
    tree = provenance.metadata.get("tree") if provenance else None

    checks = {}
    for r in results:
        checks[r.name] = {
            "status": r.status,
            "finding_count": len(r.findings),
            # Export only stable finding codes. Paths and free-form details
            # can contain caller-controlled names or identifying context.
            "findings": [{"code": f.code} for f in r.findings],
        }

    return {
        "schema": "guardian-receipt-v1",
        "guardian_version": __version__,
        "policy_version": str(policy["version"]),
        "policy_digest": policy_digest(policy),
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": "READ_ONLY",
        "network": "DISABLED_BY_DESIGN",
        "revision": revision,
        "tree": tree,
        "checks": checks,
        "result": result,
    }

def write_receipt(receipt: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
