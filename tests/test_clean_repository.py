from guardian_assurance.engine import verify
from guardian_assurance.policy import load_policy

def test_clean_repository_is_verified(clean_repo):
    result = verify(clean_repo, load_policy())
    assert result.result == "VERIFIED"
    assert all(c.status == "PASS" for c in result.checks)
    assert len(result.receipt["revision"]) == 40
    assert len(result.receipt["tree"]) == 40
