from __future__ import annotations

from pathlib import Path
from . import CheckResult, Finding
from ..repository_view import run_git

def run(root: Path, policy: dict) -> CheckResult:
    cfg = policy["provenance"]
    top = run_git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        if cfg.get("require_git", True):
            return CheckResult("provenance", "INDETERMINATE", "target is not a resolvable Git repository")
        return CheckResult("provenance", "PASS", "Git provenance not required by policy")

    try:
        repo_root = Path(top.stdout.strip()).resolve()
        target_root = root.resolve()
    except OSError:
        return CheckResult("provenance", "INDETERMINATE", "could not resolve repository path")
    if repo_root != target_root:
        return CheckResult("provenance", "INDETERMINATE", "target must be the Git repository root")

    sha = run_git(root, "rev-parse", "HEAD")
    tree = run_git(root, "rev-parse", "HEAD^{tree}")
    if sha.returncode != 0 or tree.returncode != 0:
        return CheckResult("provenance", "INDETERMINATE", "could not resolve Git revision")

    if cfg.get("require_clean_tracked_worktree", True):
        status = run_git(root, "status", "--porcelain", "--untracked-files=no")
        if status.returncode != 0:
            return CheckResult("provenance", "INDETERMINATE", "could not inspect tracked worktree state")
        if status.stdout.strip():
            return CheckResult(
                "provenance",
                "FAIL",
                "tracked worktree differs from the verified revision",
                (Finding("TRACKED_WORKTREE_DIRTY", None, "tracked changes exist outside HEAD"),),
            )

    return CheckResult(
        "provenance",
        "PASS",
        "Git revision and tracked worktree state resolved",
        metadata={"revision": sha.stdout.strip(), "tree": tree.stdout.strip()},
    )
