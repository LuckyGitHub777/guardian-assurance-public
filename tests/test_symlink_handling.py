"""Real symlink tests run on POSIX and Windows hosts with link privileges.

On ordinary Windows sessions the OS may deny symlink creation (WinError 1314).
Skip only that unavailable filesystem capability; Linux CI still exercises the
security assertions against real tracked symlinks on all supported versions.
"""

import os
from pathlib import Path

import pytest

from guardian_assurance.engine import verify
from guardian_assurance.policy import load_policy
from conftest import git


def _create_test_symlink(path: Path, target: Path | str) -> None:
    try:
        path.symlink_to(target)
    except OSError as exc:
        if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
            pytest.skip("Windows symlink privilege unavailable; Linux CI verifies real symlinks")
        raise
    except NotImplementedError:
        if os.name == "nt":
            pytest.skip("Windows symlinks unsupported; Linux CI verifies real symlinks")
        raise


def test_symlink_is_scanned_as_link_text_not_external_target(clean_repo, tmp_path):
    synthetic_secret = "github_pat_" + ("A" * 40)
    external = tmp_path / "outside.txt"
    external.write_text(synthetic_secret, encoding="utf-8")
    _create_test_symlink(clean_repo / "external.txt", external)

    git(clean_repo, "add", "external.txt")
    git(clean_repo, "commit", "-m", "add external symlink")

    result = verify(clean_repo, load_policy())
    assert result.result == "VERIFIED"
    assert synthetic_secret not in str(result.receipt)


def test_absolute_user_path_in_symlink_target_is_detected(clean_repo):
    _create_test_symlink(clean_repo / "private.txt", "/" + "home/alice/private.txt")
    git(clean_repo, "add", "private.txt")
    git(clean_repo, "commit", "-m", "add local path symlink")

    result = verify(clean_repo, load_policy())
    assert result.result == "ACTION_REQUIRED"
    environment = next(c for c in result.checks if c.name == "environment")
    assert environment.status == "FAIL"
    assert "alice" not in str(result.receipt)
