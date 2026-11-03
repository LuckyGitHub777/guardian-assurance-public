from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import hashlib
import json


class PolicyError(ValueError):
    pass


MAX_TEXT_BYTES = 16 * 1024 * 1024


DEFAULT_POLICY = {
    "schema": "guardian-policy-v1",
    "version": "1",
    "repository": {
        "required_files": [
            "README.md",
            "LICENSE",
            "SECURITY.md",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
            "pyproject.toml",
        ],
        "forbidden_tracked_names": [
            ".env",
            ".DS_Store",
            "Thumbs.db",
        ],
        "forbidden_tracked_segments": [
            "__pycache__",
            ".pytest_cache",
            ".venv",
            "venv",
            ".idea",
            ".vscode",
        ],
        "max_text_bytes": 1048576,
    },
    "identity": {
        "forbidden_author_fragments": [
            "@localhost",
            ".local",
            "@example.com",
            "root@",
            "user@",
        ]
    },
    "environment": {
        "block_absolute_user_paths": True
    },
    "secrets": {
        "enabled_rules": [
            "github_classic",
            "github_fine_grained",
            "aws_access_key",
            "private_key",
            "slack_token",
            "stripe_live_key",
            "google_api_key",
        ]
    },
    "provenance": {
        "require_git": True,
        "require_clean_tracked_worktree": True,
    },
}


def _require_exact_keys(section: dict, expected: set[str], name: str) -> None:
    actual = set(section)
    missing = sorted(expected - actual)
    extra = sorted((str(key) for key in actual - expected))
    if missing:
        raise PolicyError(f"missing policy field(s) in {name}: {', '.join(missing)}")
    if extra:
        raise PolicyError(f"unknown policy field(s) in {name}: {', '.join(extra)}")


def _require_string_list(section: dict, key: str, name: str) -> None:
    value = section[key]
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise PolicyError(f"{name}.{key} must be an array of non-empty strings")


def _require_boolean(section: dict, key: str, name: str) -> None:
    if type(section[key]) is not bool:
        raise PolicyError(f"{name}.{key} must be a boolean")


def validate_policy(policy: object) -> None:
    if not isinstance(policy, dict):
        raise PolicyError("policy document must be a JSON object")

    top_level = {
        "schema",
        "version",
        "repository",
        "identity",
        "environment",
        "secrets",
        "provenance",
    }
    _require_exact_keys(policy, top_level, "policy")

    if policy.get("schema") != "guardian-policy-v1":
        raise PolicyError("unsupported or missing policy schema")
    if type(policy.get("version")) is not str or policy["version"] != "1":
        raise PolicyError("unsupported or missing policy version")

    section_fields = {
        "repository": {
            "required_files",
            "forbidden_tracked_names",
            "forbidden_tracked_segments",
            "max_text_bytes",
        },
        "identity": {"forbidden_author_fragments"},
        "environment": {"block_absolute_user_paths"},
        "secrets": {"enabled_rules"},
        "provenance": {"require_git", "require_clean_tracked_worktree"},
    }

    for name, expected in section_fields.items():
        section = policy.get(name)
        if not isinstance(section, dict):
            raise PolicyError(f"missing or invalid policy section: {name}")
        _require_exact_keys(section, expected, name)

    repository = policy["repository"]
    for key in ("required_files", "forbidden_tracked_names", "forbidden_tracked_segments"):
        _require_string_list(repository, key, "repository")
    if (
        type(repository["max_text_bytes"]) is not int
        or not 1 <= repository["max_text_bytes"] <= MAX_TEXT_BYTES
    ):
        raise PolicyError(f"repository.max_text_bytes must be between 1 and {MAX_TEXT_BYTES}")

    _require_string_list(policy["identity"], "forbidden_author_fragments", "identity")
    _require_boolean(policy["environment"], "block_absolute_user_paths", "environment")
    _require_string_list(policy["secrets"], "enabled_rules", "secrets")
    _require_boolean(policy["provenance"], "require_git", "provenance")
    _require_boolean(
        policy["provenance"],
        "require_clean_tracked_worktree",
        "provenance",
    )


def load_policy(path: str | Path | None = None) -> dict:
    if path is None:
        policy = deepcopy(DEFAULT_POLICY)
    else:
        p = Path(path)
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise PolicyError(f"cannot read policy: {exc}") from exc
        try:
            policy = json.loads(text)
        except json.JSONDecodeError as exc:
            raise PolicyError(
                "v1 policy files use JSON syntax (valid YAML 1.2); parsing failed"
            ) from exc
    validate_policy(policy)
    return policy


def policy_digest(policy: dict) -> str:
    canonical = json.dumps(policy, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()
