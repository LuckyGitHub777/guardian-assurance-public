from guardian_assurance.engine import verify
from guardian_assurance.policy import load_policy
from conftest import git
import pytest


def test_synthetic_github_secret_blocks_release(clean_repo):
    fake = "github_pat_" + ("A" * 40)
    (clean_repo / "credential.txt").write_text(fake + "\n", encoding="utf-8")
    git(clean_repo, "add", "credential.txt")
    git(clean_repo, "commit", "-m", "add synthetic secret")
    result = verify(clean_repo, load_policy())
    assert result.result == "ACTION_REQUIRED"
    secrets = next(c for c in result.checks if c.name == "secrets")
    assert secrets.status == "FAIL"
    assert fake not in str(result.receipt)


def test_private_key_header_blocks_release(clean_repo):
    header = "-----BEGIN " + "PRIVATE KEY-----"
    (clean_repo / "private.txt").write_text(
        header + "\nsynthetic\n",
        encoding="utf-8",
    )
    git(clean_repo, "add", "private.txt")
    git(clean_repo, "commit", "-m", "add synthetic key marker")
    result = verify(clean_repo, load_policy())
    assert result.result == "ACTION_REQUIRED"


@pytest.mark.parametrize(
    ("prefix", "suffix"),
    [
        ("DSA ", "PRIVATE KEY-----"),
        ("ENCRYPTED ", "PRIVATE KEY-----"),
        ("PGP ", "PRIVATE KEY BLOCK-----"),
    ],
)
def test_additional_private_key_headers_block_release(clean_repo, prefix, suffix):
    header = "-----BEGIN " + prefix + suffix
    (clean_repo / "private.txt").write_text(header + "\nsynthetic\n", encoding="utf-8")
    git(clean_repo, "add", "private.txt")
    git(clean_repo, "commit", "-m", "add synthetic private key marker")
    result = verify(clean_repo, load_policy())
    assert result.result == "ACTION_REQUIRED"
    secrets = next(c for c in result.checks if c.name == "secrets")
    assert secrets.status == "FAIL"


def test_oversized_tracked_text_is_indeterminate_not_verified(clean_repo):
    policy = load_policy()
    policy["repository"]["max_text_bytes"] = 48
    (clean_repo / "evidence.md").write_text("x" * 80, encoding="utf-8")
    git(clean_repo, "add", "evidence.md")
    git(clean_repo, "commit", "-m", "synthetic oversized text")
    result = verify(clean_repo, policy)
    assert result.result == "INDETERMINATE"
    for name in ("secrets", "environment"):
        check = next(c for c in result.checks if c.name == name)
        assert check.status == "INDETERMINATE"
        assert check.metadata.get("uninspected_text_files") == "1"


def test_invalid_utf8_text_is_indeterminate_without_leaking_content(clean_repo):
    (clean_repo / "notes.txt").write_bytes(b"private:\xff")
    git(clean_repo, "add", "notes.txt")
    git(clean_repo, "commit", "-m", "synthetic undecodable text")
    result = verify(clean_repo, load_policy())
    assert result.result == "INDETERMINATE"
    assert "private:" not in str(result.receipt)


def test_binary_asset_is_not_misclassified_as_utf8_text(clean_repo):
    (clean_repo / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n\xff\x00")
    git(clean_repo, "add", "image.png")
    git(clean_repo, "commit", "-m", "synthetic image")
    result = verify(clean_repo, load_policy())
    assert result.result == "VERIFIED"


def test_detected_secret_still_fails_when_other_text_is_unreadable(clean_repo):
    policy = load_policy()
    policy["repository"]["max_text_bytes"] = 80
    (clean_repo / "large.md").write_text("x" * 81, encoding="utf-8")
    (clean_repo / "test-secret.txt").write_text(
        "github_pat_" + ("A" * 40),
        encoding="utf-8",
    )
    git(clean_repo, "add", "large.md", "test-secret.txt")
    git(clean_repo, "commit", "-m", "synthetic mixed evidence")
    result = verify(clean_repo, policy)
    assert result.result == "ACTION_REQUIRED"
    check = next(c for c in result.checks if c.name == "secrets")
    assert check.status == "FAIL"


def test_unrecognized_unreadable_file_is_indeterminate(clean_repo):
    (clean_repo / "payload.bin").write_bytes(b"\xff\x00")
    git(clean_repo, "add", "payload.bin")
    git(clean_repo, "commit", "-m", "synthetic unrecognized binary")
    result = verify(clean_repo, load_policy())
    assert result.result == "INDETERMINATE"
    for name in ("secrets", "environment"):
        check = next(c for c in result.checks if c.name == name)
        assert check.status == "INDETERMINATE"
        assert check.metadata.get("uninspected_text_files") == "1"
