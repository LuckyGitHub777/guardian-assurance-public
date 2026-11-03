from guardian_assurance.engine import verify
from guardian_assurance.policy import load_policy
from conftest import git

def test_receipt_redacts_secret_and_absolute_path(clean_repo):
    fake = "ghp_" + ("Z" * 30)
    local = "/" + "home/alice/private/source.txt"
    (clean_repo / "bad.txt").write_text(fake + "\n" + local + "\n", encoding="utf-8")
    git(clean_repo, "add", "bad.txt")
    git(clean_repo, "commit", "-m", "synthetic privacy fixture")
    receipt = verify(clean_repo, load_policy()).receipt
    rendered = str(receipt)
    assert fake not in rendered
    assert ("/" + "home/alice") not in rendered
    assert "alice" not in rendered.lower()
    assert "bad.txt" in rendered
