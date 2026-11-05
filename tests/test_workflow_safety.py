from pathlib import Path


def test_reusable_workflow_does_not_interpolate_profile_into_shell():
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "guardian-reusable.yml"
    ).read_text(encoding="utf-8")

    assert "GUARDIAN_PROFILE: ${{ inputs.profile }}" in workflow
    assert 'case "$GUARDIAN_PROFILE" in' in workflow
    assert "printf 'Unsupported Guardian profile: %s\\n'" in workflow
    assert 'case "${{ inputs.profile }}" in' not in workflow
    assert 'Unsupported Guardian profile: ${{ inputs.profile }}' not in workflow


def test_example_caller_keeps_guardian_opt_in_at_publication_boundary():
    workflow = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / "github"
        / "guardian.yml"
    ).read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "public:" in workflow
    assert "release:" in workflow
    assert "pull_request:" not in workflow
    assert "push:" not in workflow
    assert "profile: ${{ inputs.profile }}" in workflow
    assert "profile: baseline" in workflow
    assert "profile: release" in workflow


def test_public_workflow_package_install_keeps_console_output_minimal():
    root = Path(__file__).resolve().parents[1]
    paths = {
        ".github/workflows/verify.yml": "python -m pip install --quiet '.[dev]'",
        ".github/workflows/guardian-reusable.yml": "python -m pip install --quiet ./.guardian-tool",
    }
    for name, command in paths.items():
        source = (root / name).read_text(encoding="utf-8")
        assert source.count(command) == 1
        assert "python -m pip install '.[dev]'" not in source
        assert "python -m pip install ./.guardian-tool" not in source
