from pathlib import Path

from guardian_assurance.repository_view import read_text


class RecordingReader:
    def __init__(self, handle, requested):
        self.handle = handle
        self.requested = requested

    def __enter__(self):
        self.handle.__enter__()
        return self

    def __exit__(self, *args):
        return self.handle.__exit__(*args)

    def read(self, size=-1):
        self.requested.append(size)
        return self.handle.read(size)


def test_text_reader_reads_only_limit_plus_one(tmp_path, monkeypatch):
    target = tmp_path / "large.txt"
    target.write_bytes(b"x" * 10000)
    original_open = Path.open
    requested = []

    def recording_open(path, *args, **kwargs):
        handle = original_open(path, *args, **kwargs)
        if path == target:
            return RecordingReader(handle, requested)
        return handle

    monkeypatch.setattr(Path, "open", recording_open)

    assert read_text(tmp_path, Path("large.txt"), 32) is None
    assert requested == [33]


def test_binary_suffix_is_not_opened_by_text_scanner(tmp_path, monkeypatch):
    target = tmp_path / "large.png"
    target.write_bytes(b"\x89PNG" + (b"x" * 10000))
    original_open = Path.open

    def forbidden_open(path, *args, **kwargs):
        if path == target:
            raise AssertionError("binary file must not be opened by text scanner")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", forbidden_open)

    assert read_text(tmp_path, Path("large.png"), 32) is None
