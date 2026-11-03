from __future__ import annotations

from pathlib import Path
import subprocess
import pytest

REQUIRED = ["README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md", "pyproject.toml"]

def git(root: Path, *args: str):
    return subprocess.run(["git", "-C", str(root), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def make_repo(root: Path, email: str = "123+tester@users.noreply.github.com") -> Path:
    root.mkdir()
    for name in REQUIRED:
        (root / name).write_text(f"# {name}\n", encoding="utf-8")
    git(root, "init", "-b", "main")
    git(root, "config", "user.name", "Guardian Test")
    git(root, "config", "user.email", email)
    git(root, "add", ".")
    git(root, "commit", "-m", "test fixture")
    return root

@pytest.fixture
def clean_repo(tmp_path):
    return make_repo(tmp_path / "repo")
