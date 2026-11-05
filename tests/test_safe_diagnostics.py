"""Outward diagnostics must not echo caller-controlled file or author names."""
import json

from conftest import git, make_repo
from guardian_assurance.cli import main
from guardian_assurance.engine import verify
from guardian_assurance.policy import load_policy


def test_verbose_cli_and_receipt_never_echo_matched_file_path(clean_repo, tmp_path, capsys):
    filename = "synthetic-private-context-filename-xyz.txt"
    marker = "github_pat_" + ("Q" * 40)
    (clean_repo / filename).write_text(marker + "\n", encoding="utf-8")
    git(clean_repo, "add", filename)
    git(clean_repo, "commit", "-m", "synthetic diagnostics fixture")
    target_receipt = tmp_path / "synthetic-output.json"

    code = main(["verify", str(clean_repo), "--verbose",
                 "--receipt", str(target_receipt)])
    output = capsys.readouterr()
    data = json.loads(target_receipt.read_text(encoding="utf-8"))

    assert code == 1
    assert "SECRET_PATTERN" in output.out
    for rendered in (output.out, output.err, json.dumps(data)):
        assert filename not in rendered
        assert marker not in rendered
        assert str(target_receipt) not in rendered
    assert data["result"] == "ACTION_REQUIRED"
    assert all(set(finding) == {"code"} for check in data["checks"].values()
               for finding in check["findings"])


def test_json_output_redacts_path_and_free_text(clean_repo, capsys):
    filename = "synthetic-file-context-xyz.txt"
    (clean_repo / filename).write_text(
        "-----BEGIN PRIVATE KEY-----\nsynthetic\n", encoding="utf-8")
    git(clean_repo, "add", filename)
    git(clean_repo, "commit", "-m", "synthetic private key marker")
    status = main(["verify", str(clean_repo), "--json"])
    output = capsys.readouterr()
    doc = json.loads(output.out)
    assert status == 1
    assert doc["result"] == "ACTION_REQUIRED"
    assert filename not in output.out
    assert "SECRET_PATTERN" in output.out


def test_author_domain_not_retained_in_check_metadata(tmp_path):
    repo = make_repo(tmp_path / "author-test", email="synthetic@reserved.invalid")
    check = next(x for x in verify(repo, load_policy()).checks if x.name == "identity")
    assert check.status == "PASS"
    assert check.metadata == {}
