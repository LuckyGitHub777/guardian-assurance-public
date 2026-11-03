from guardian_assurance.engine import verify
from guardian_assurance.policy import load_policy
from conftest import git


def test_missing_required_file_blocks_release(clean_repo):
    (clean_repo / "SECURITY.md").unlink()
    git(clean_repo, "add", "-u")
    git(clean_repo, "commit", "-m", "remove security policy")
    result = verify(clean_repo, load_policy())
    assert result.result == "ACTION_REQUIRED"


def test_untracked_required_file_does_not_satisfy_policy(clean_repo):
    (clean_repo / "SECURITY.md").unlink()
    git(clean_repo, "add", "-u")
    git(clean_repo, "commit", "-m", "remove security policy")
    (clean_repo / "SECURITY.md").write_text("# local-only replacement\n", encoding="utf-8")

    result = verify(clean_repo, load_policy())
    repository = next(check for check in result.checks if check.name == "repository")

    assert result.result == "ACTION_REQUIRED"
    assert repository.status == "FAIL"
    assert any(
        finding.code == "REQUIRED_FILE_NOT_TRACKED"
        for finding in repository.findings
    )
