# Changelog

All notable changes to Guardian are documented here.

## [Unreleased]

### Added

- Reusable GitHub Actions publication gate for caller repositories.
- Development, static-web, baseline, and release policy profiles for staged assurance.
- Automation contract for on-demand publication preflight and post-publication audits.
- Opt-in caller workflow template with manual pre-publication runs and post-event audits; no routine PR/push trigger.
- Strict static-web publication profile for one-artifact web experiences without software-package document ceremony.
- Regression coverage for incomplete and mistyped policy files, symlink handling, and additional private-key formats.
- Regression coverage ensuring the example caller remains opt-in and does not gate routine development.

### Changed

- Guardian's own verification workflow now cancels stale runs when a newer revision supersedes it.
- Routine development remains on each consumer repository's existing CI; Guardian is not a default PR/push dependency.
- Unreadable tracked files outside the explicit common-binary suffix allowlist now produce `INDETERMINATE`.
- Reusable workflow profile inputs are passed through environment variables rather than interpolated into shell commands.
- Policy v1 now rejects missing, mistyped, and unknown nested fields before checks run.
- Tracked symlinks are inspected as link-target text without dereferencing local targets.
- Private-key detection includes DSA, encrypted PKCS#8, and PGP private-key headers.
- The v1.0.0 reusable-workflow tag is superseded by the caller-input hardening merged after that release.

## [1.0.0] - 2026-11-01

### Added

- Clean public repository architecture.
- Dependency-free Guardian verification core.
- Executable UAT and privacy tests.
- Revision-bound evidence receipt schema.
- Pinned GitHub Actions verification workflow.
- Required publication files must be tracked in the attested Git revision.
- CI matrix execution across Python 3.11, 3.12, and 3.13 without fail-fast cancellation.

### Release posture

- Package maturity is classified as Beta for the first public release; verification claims remain evidence-bound to the exact revision and policy.
