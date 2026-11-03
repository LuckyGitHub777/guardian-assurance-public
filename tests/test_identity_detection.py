from guardian_assurance.engine import verify
from guardian_assurance.policy import load_policy
from conftest import make_repo

def test_placeholder_identity_blocks_release(tmp_path):
    repo = make_repo(tmp_path / "repo", email="user@example.com")
    result = verify(repo, load_policy())
    assert result.result == "ACTION_REQUIRED"
    identity = next(c for c in result.checks if c.name == "identity")
    assert identity.status == "FAIL"
    assert "user@example.com" not in str(result.receipt)
