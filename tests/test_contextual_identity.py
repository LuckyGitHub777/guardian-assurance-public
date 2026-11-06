"""Synthetic-only tests. No actual identity or secret terms may be committed."""
from __future__ import annotations

from pathlib import Path

from conftest import git
from guardian_assurance.engine import verify
from guardian_assurance.policy import load_policy


def test_normal_development_does_not_claim_contextual_coverage(clean_repo, monkeypatch):
    monkeypatch.delenv("GUARDIAN_OPSEC_DENYLIST", raising=False)
    monkeypatch.delenv("GUARDIAN_REQUIRE_CONTEXT", raising=False)
    result = verify(clean_repo, load_policy())
    assert "contextual_identity" not in result.receipt["checks"]


def test_required_context_missing_is_indeterminate(clean_repo, monkeypatch):
    monkeypatch.delenv("GUARDIAN_OPSEC_DENYLIST", raising=False)
    monkeypatch.setenv("GUARDIAN_REQUIRE_CONTEXT", "1")
    result = verify(clean_repo, load_policy())
    assert result.result == "INDETERMINATE"
    assert result.receipt["checks"]["contextual_identity"]["status"] == "INDETERMINATE"


def test_content_match_fails_without_echoing_private_value_or_path(clean_repo, monkeypatch):
    secret_term = "synthetic-subject-xyz"
    name = "synthetic-document.md"
    (clean_repo / name).write_text("Sample content: " + secret_term, encoding="utf-8")
    git(clean_repo, "add", name)
    git(clean_repo, "commit", "-m", "synthetic test")
    monkeypatch.setenv("GUARDIAN_OPSEC_DENYLIST", secret_term)
    monkeypatch.setenv("GUARDIAN_REQUIRE_CONTEXT", "1")

    result = verify(clean_repo, load_policy())
    assert result.result == "ACTION_REQUIRED"
    result_text = str(result.receipt)
    assert "PRIVATE_CONTEXT_CONTENT" in result_text
    assert secret_term not in result_text
    assert name not in result_text


def test_filename_match_fails_with_redacted_finding(clean_repo, monkeypatch):
    secret_term = "synthetic-filename-xyz"
    name = secret_term + ".txt"
    (clean_repo / name).write_text("ordinary harmless fixture", encoding="utf-8")
    git(clean_repo, "add", name)
    git(clean_repo, "commit", "-m", "synthetic filename")
    monkeypatch.setenv("GUARDIAN_OPSEC_DENYLIST", secret_term)
    result = verify(clean_repo, load_policy())
    finding = result.receipt["checks"]["contextual_identity"]["findings"][0]
    assert result.result == "ACTION_REQUIRED"
    assert finding["code"] == "PRIVATE_CONTEXT_PATH"
    assert "path" not in finding
    assert secret_term not in str(result.receipt)


def test_oversized_expected_text_is_indeterminate(clean_repo, monkeypatch):
    path = clean_repo / "long-input.txt"
    path.write_text("harmless text " * 100, encoding="utf-8")
    git(clean_repo, "add", path.name)
    git(clean_repo, "commit", "-m", "synthetic oversized")
    monkeypatch.setenv("GUARDIAN_OPSEC_DENYLIST", "synthetic-subject-xyz")
    policy = load_policy()
    policy["repository"]["max_text_bytes"] = 32
    result = verify(clean_repo, policy)
    assert result.receipt["checks"]["contextual_identity"]["status"] == "INDETERMINATE"



def test_mixed_valid_and_short_private_terms_fail_closed(clean_repo, monkeypatch):
    # A valid term must never hide an unsupported second term.
    valid = "synthetic-marker-alpha"
    short = "xy"
    monkeypatch.setenv("GUARDIAN_OPSEC_DENYLIST", valid + "\n" + short)
    monkeypatch.setenv("GUARDIAN_REQUIRE_CONTEXT", "1")
    result = verify(clean_repo, load_policy())
    check = result.receipt["checks"]["contextual_identity"]
    assert result.result == "INDETERMINATE"
    assert check["status"] == "INDETERMINATE"
    assert valid not in str(result.receipt)
    assert short not in str(result.receipt)


def test_blank_lines_do_not_invalidate_valid_private_context(clean_repo, monkeypatch):
    monkeypatch.setenv("GUARDIAN_OPSEC_DENYLIST", "\n  synthetic-marker-alpha  \n\n")
    monkeypatch.setenv("GUARDIAN_REQUIRE_CONTEXT", "1")
    result = verify(clean_repo, load_policy())
    assert result.result == "VERIFIED"
    assert result.receipt["checks"]["contextual_identity"]["status"] == "PASS"


def test_short_term_never_silently_dropped_even_if_repeated(clean_repo, monkeypatch):
    monkeypatch.setenv(
        "GUARDIAN_OPSEC_DENYLIST",
        "synthetic-marker-alpha\nxy\nxy\nother-valid-marker",
    )
    result = verify(clean_repo, load_policy())
    assert result.result == "INDETERMINATE"
    assert "unsupported short terms" in result.receipt["checks"]["contextual_identity"]["summary"]

def test_short_invalid_context_does_not_turn_green(clean_repo, monkeypatch):
    monkeypatch.setenv("GUARDIAN_OPSEC_DENYLIST", "xx\n ")
    result = verify(clean_repo, load_policy())
    assert result.result == "INDETERMINATE"
