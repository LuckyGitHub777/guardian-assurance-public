from __future__ import annotations

import os
from pathlib import Path
import subprocess

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "build", "dist"}

# Only common binary formats are exempt from the expected-text coverage gate.
# Unknown or extensionless files that cannot be inspected fail closed.
BINARY_SUFFIXES = {
    ".7z", ".a", ".aac", ".aiff", ".apk", ".avi", ".avif", ".bmp",
    ".bz2", ".class", ".dmg", ".doc", ".docx", ".dylib", ".eot", ".exe",
    ".flac", ".gif", ".gz", ".heic", ".ico", ".icns", ".jar", ".jpeg",
    ".jpg", ".lib", ".m4a", ".mkv", ".mov", ".mp3", ".mp4", ".o",
    ".otf", ".pdf", ".png", ".ppt", ".pptx", ".psd", ".pyc", ".rar",
    ".so", ".sqlite", ".sqlite3", ".tar", ".tgz", ".tif", ".tiff",
    ".ttf", ".wasm", ".wav", ".webm", ".webp", ".woff", ".woff2",
    ".xls", ".xlsx", ".xz", ".zip", ".zst",
}


def requires_text_scan(rel: Path) -> bool:
    return rel.suffix.lower() not in BINARY_SUFFIXES


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    command = ["git", "-C", str(root), *args]
    try:
        return subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            errors="surrogateescape",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        # Missing or unlaunchable Git is evidence unavailability, not a crash.
        return subprocess.CompletedProcess(
            command,
            127,
            stdout="",
            stderr=f"git execution unavailable: {type(exc).__name__}",
        )


def tracked_files(root: Path) -> tuple[list[Path], bool]:
    """Return repository-relative files and whether Git supplied the list."""
    cp = run_git(root, "ls-files", "-z")
    if cp.returncode == 0:
        rels = [Path(x) for x in cp.stdout.split("\0") if x]
        return rels, True

    rels: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        rels.append(rel)
    return sorted(rels), False


def read_text(root: Path, rel: Path, max_bytes: int) -> str | None:
    path = root / rel
    try:
        # Git stores a symlink's target as text. Inspect that text directly;
        # never follow a tracked link into an unrelated local file.
        if path.is_symlink():
            target = os.readlink(path)
            if len(target.encode("utf-8", errors="surrogateescape")) > max_bytes:
                return None
            return target
        if not requires_text_scan(rel):
            return None
        # Read only one byte beyond the configured limit. This bounds memory
        # use for oversized tracked files instead of loading them in full.
        with path.open("rb") as handle:
            data = handle.read(max_bytes + 1)
    except OSError:
        return None
    if len(data) > max_bytes or b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None
