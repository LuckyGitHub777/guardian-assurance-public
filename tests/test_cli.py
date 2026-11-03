from guardian_assurance.cli import main

def test_cli_rejects_receipt_inside_target(clean_repo):
    code = main(["verify", str(clean_repo), "--receipt", str(clean_repo / "receipt.json")])
    assert code == 2
    assert not (clean_repo / "receipt.json").exists()

def test_cli_writes_external_receipt(clean_repo, tmp_path):
    receipt = tmp_path / "receipt.json"
    code = main(["verify", str(clean_repo), "--receipt", str(receipt)])
    assert code == 0
    assert receipt.exists()
