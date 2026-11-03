from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from .checks import CheckResult
from .checks import identity, environment, secrets, repository, provenance, contextual_identity
from .evidence import build_receipt
from .policy import validate_policy

CHECKS = (identity, environment, secrets, repository, provenance)

@dataclass(frozen=True)
class Verification:
    result: str
    checks: tuple[CheckResult, ...]
    receipt: dict

def verify(root: str | Path, policy: dict) -> Verification:
    validate_policy(policy)
    target = Path(root).resolve()
    if not target.is_dir():
        synthetic = CheckResult("repository", "INDETERMINATE", "target is not a directory")
        results = [synthetic]
    else:
        results = [module.run(target, policy) for module in CHECKS]
        # Keep normal development unchanged; publication callers explicitly opt in.
        if os.environ.get("GUARDIAN_OPSEC_DENYLIST") or os.environ.get("GUARDIAN_REQUIRE_CONTEXT") == "1":
            results.append(contextual_identity.run(target, policy))

    statuses = {r.status for r in results}
    if "FAIL" in statuses:
        overall = "ACTION_REQUIRED"
    elif "INDETERMINATE" in statuses:
        overall = "INDETERMINATE"
    else:
        overall = "VERIFIED"

    receipt = build_receipt(policy, results, overall)
    return Verification(overall, tuple(results), receipt)
