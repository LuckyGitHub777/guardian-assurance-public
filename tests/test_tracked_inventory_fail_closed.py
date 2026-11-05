"""Fail-closed regression for unavailable Git tracked-file inventories.

A filesystem fallback must never be reported as an attested Git inventory.
The mock changes only git ls-files; provenance and other Git reads still work.
"""

import subprocess

from guardian_assurance import repository_view
from guardian_assurance.engine import verify
from guardian_assurance.policy import load_policy


def test_unavailable_tracked_git_inventory_is_indeterminate(clean_repo, monkeypatch):
    original = repository_view.run_git

    def unavailable_listing(root, *args):
        if args == ("ls-files", "-z"):
            return subprocess.CompletedProcess(
                ["git", "ls-files", "-z"], 128,
                stdout="", stderr="synthetic unavailable",
            )
        return original(root, *args)

    monkeypatch.setattr(repository_view, "run_git", unavailable_listing)
    result = verify(clean_repo, load_policy())

    assert result.result == "INDETERMINATE"
    for name in ("secrets", "environment", "repository"):
        check = next(c for c in result.checks if c.name == name)
        assert check.status == "INDETERMINATE"
        assert "tracked Git file inventory unavailable" == check.summary
        assert not check.findings
    assert not any(c.status == "FAIL" for c in result.checks)
    assert "synthetic unavailable" not in str(result.receipt)


def test_restored_tracked_git_inventory_can_verify(clean_repo):
    result = verify(clean_repo, load_policy())
    assert result.result == "VERIFIED"
    assert all(c.status == "PASS" for c in result.checks)
