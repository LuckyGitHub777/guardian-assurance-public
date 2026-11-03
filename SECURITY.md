# Security Policy

## Supported versions

Security fixes are supported for the latest released Guardian version.

The `v1.0.0` reusable-workflow tag predates caller-input shell hardening and is superseded. Do not use that tag as a reusable-workflow reference. Until a superseding release is published, pin reusable-workflow callers to a reviewed, immutable commit SHA from the current `main` history.

## Reporting a vulnerability

Please do not place secrets, private repository contents, exploit payloads containing real credentials, or machine-specific evidence in a public issue.

For security-sensitive reports, use GitHub's private vulnerability reporting feature when enabled. If private reporting is unavailable, open a minimal public issue asking for a private contact path without including sensitive details.

## Safety boundary

Guardian is a sensor, verifier, and evidence generator. Its default verification path is local-first, network-off, and read-only with respect to the target repository.

Guardian does not claim to guarantee security, certify compliance, eliminate risk, or detect every possible secret format.
