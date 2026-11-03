import json
from pathlib import Path

import pytest

from guardian_assurance.policy import PolicyError, load_policy, policy_digest


def test_policy_digest_is_stable():
    p1 = load_policy()
    p2 = load_policy()
    assert policy_digest(p1) == policy_digest(p2)


def test_default_policy_file_matches_builtin_policy():
    root = Path(__file__).resolve().parents[1]
    file_policy = json.loads(
        (root / "policies" / "default.yaml").read_text(encoding="utf-8")
    )
    assert file_policy == load_policy()


def test_minimal_example_policy_is_valid():
    root = Path(__file__).resolve().parents[1]
    policy = load_policy(root / "examples" / "policy.minimal.yaml")
    assert policy["secrets"]["enabled_rules"]


@pytest.mark.parametrize(
    "name", ["development.yaml", "static-web.yaml", "baseline.yaml", "release.yaml"]
)
def test_bundled_automation_policies_are_valid(name):
    root = Path(__file__).resolve().parents[1]
    policy = load_policy(root / "policies" / name)
    assert policy["schema"] == "guardian-policy-v1"
    assert policy["version"] == "1"


def test_automation_policy_profiles_are_progressively_stricter():
    root = Path(__file__).resolve().parents[1]
    development = load_policy(root / "policies" / "development.yaml")
    static_web = load_policy(root / "policies" / "static-web.yaml")
    baseline = load_policy(root / "policies" / "baseline.yaml")
    release = load_policy(root / "policies" / "release.yaml")
    python = load_policy()

    development_files = set(development["repository"]["required_files"])
    static_web_files = set(static_web["repository"]["required_files"])
    baseline_files = set(baseline["repository"]["required_files"])
    release_files = set(release["repository"]["required_files"])
    python_files = set(python["repository"]["required_files"])

    assert not development_files
    assert static_web_files == {"index.html"}
    assert development_files < baseline_files < release_files < python_files
    assert "pyproject.toml" not in release_files
    assert "pyproject.toml" in python_files


def test_automation_profiles_preserve_core_assurance_checks():
    root = Path(__file__).resolve().parents[1]
    python = load_policy()
    for name in ("development.yaml", "static-web.yaml", "baseline.yaml", "release.yaml"):
        policy = load_policy(root / "policies" / name)
        for section in ("identity", "environment", "secrets", "provenance"):
            assert policy[section] == python[section]


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda p: p["secrets"].pop("enabled_rules"), id="missing-secret-rules"),
        pytest.param(lambda p: p["identity"].pop("forbidden_author_fragments"), id="missing-identity-rules"),
        pytest.param(lambda p: p["repository"].pop("required_files"), id="missing-required-files"),
        pytest.param(lambda p: p["environment"].update(block_absolute_user_paths="false"), id="string-instead-of-bool"),
        pytest.param(lambda p: p["provenance"].update(require_git="false"), id="mistyped-provenance"),
        pytest.param(lambda p: p["repository"].update(max_text_bytes=True), id="bool-instead-of-int"),
        pytest.param(lambda p: p["repository"].update(max_text_bytes=16777217), id="text-limit-over-hard-cap"),
        pytest.param(lambda p: p["secrets"].update(enabled_rules="github_classic"), id="string-instead-of-list"),
        pytest.param(lambda p: p["repository"].update(unexpected=True), id="unknown-field"),
    ],
)
def test_incomplete_or_mistyped_policy_is_rejected(tmp_path, mutate):
    policy = load_policy()
    mutate(policy)
    path = tmp_path / "bad-policy.json"
    path.write_text(json.dumps(policy), encoding="utf-8")
    with pytest.raises(PolicyError):
        load_policy(path)


def test_policy_document_must_be_an_object(tmp_path):
    path = tmp_path / "bad-policy.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(PolicyError):
        load_policy(path)


def test_invalid_policy_json_is_rejected(tmp_path):
    path = tmp_path / "bad-policy.json"
    path.write_text("not json", encoding="utf-8")
    with pytest.raises(PolicyError):
        load_policy(path)


def test_programmatic_verify_rejects_unvalidated_policy(clean_repo):
    from guardian_assurance.engine import verify

    with pytest.raises(PolicyError):
        verify(clean_repo, {})
