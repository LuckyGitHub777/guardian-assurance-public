from guardian_assurance.engine import verify
from guardian_assurance.policy import load_policy
from conftest import git

def test_absolute_windows_user_path_blocks_release(clean_repo):
    value = "C:" + "\\\\Users\\\\Alice\\\\Desktop\\\\private.txt"
    (clean_repo / "notes.txt").write_text(value, encoding="utf-8")
    git(clean_repo, "add", "notes.txt")
    git(clean_repo, "commit", "-m", "add local path")
    result = verify(clean_repo, load_policy())
    assert result.result == "ACTION_REQUIRED"
    assert "Alice" not in str(result.receipt)

def test_env_file_blocks_release(clean_repo):
    (clean_repo / ".env").write_text("SAFE_TEST=1\n", encoding="utf-8")
    git(clean_repo, "add", "-f", ".env")
    git(clean_repo, "commit", "-m", "add env file")
    result = verify(clean_repo, load_policy())
    assert result.result == "ACTION_REQUIRED"
