from guardian_assurance.engine import verify
from guardian_assurance.policy import load_policy

def test_non_git_target_is_indeterminate(tmp_path):
    root = tmp_path / "plain"
    root.mkdir()
    for name in ("README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md", "pyproject.toml"):
        (root / name).write_text(f"# {name}\n", encoding="utf-8")
    result = verify(root, load_policy())
    assert result.result == "INDETERMINATE"

def test_dirty_tracked_file_blocks_release(clean_repo):
    (clean_repo / "README.md").write_text("changed but uncommitted\n", encoding="utf-8")
    result = verify(clean_repo, load_policy())
    assert result.result == "ACTION_REQUIRED"


def test_missing_git_is_indeterminate_not_a_crash(clean_repo, monkeypatch):
    monkeypatch.setenv("PATH", "")
    result = verify(clean_repo, load_policy())
    assert result.result == "INDETERMINATE"
    identity = next(c for c in result.checks if c.name == "identity")
    provenance = next(c for c in result.checks if c.name == "provenance")
    assert identity.status == "INDETERMINATE"
    assert provenance.status == "INDETERMINATE"
