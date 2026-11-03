# Automation

Guardian is an **optional, publication-focused assurance capability**. It exists for moments when a repository is about to cross a publication boundary or when a targeted hygiene check is worth running.

It is not a required dependency for everyday development, is not a global control plane, and should not be wired into every repository's pull requests or pushes by default. Keep each project's existing CI, tests, and upgrade loop fast.

Guardian remains read-only. Automation around Guardian may publish or change repository settings, but only after the exact revision selected for publication has been verified and the responsible human or authorized operator has exercised publication authority.

## When to use Guardian

Use an on-demand Guardian run when one of these decisions is actually in scope:

- changing a private repository to public;
- publishing a release or public downloadable artifact;
- preparing a repository for an external handoff or public review;
- performing a targeted publication-hygiene check after a material change.

Do not add a Guardian run merely because a routine commit, pull request, dependency update, refactor, or internal iteration occurred. Those activities should continue through the repository's existing CI and engineering checks.

The `development` profile is available for an explicitly requested, targeted diagnostic. It is not a default development lane and is not required on every PR or push.

The Guardian repository itself retains normal CI on its own pull requests and main-branch changes to test Guardian's code. That self-validation does **not** mean consumer repositories must adopt Guardian in their everyday CI.

## On-demand pre-publication run

The caller template in [`examples/github/guardian.yml`](../examples/github/guardian.yml) deliberately has:

- `workflow_dispatch` for a manually selected pre-publication run;
- `public` for a post-visibility-change audit;
- `release.published` for a post-release audit;
- **no** `pull_request` or `push` trigger.

Choose the profile that matches the artifact:

| Profile | Required tracked files | Intended use |
| --- | --- | --- |
| `development` | none | Explicit, targeted diagnostic only |
| `static-web` | index.html | Minimal static web publication |
| `baseline` | README, LICENSE, SECURITY | General public repository |
| `release` | baseline + CONTRIBUTING + CHANGELOG | Public/released product |
| `python` | release + pyproject.toml | Python package and Guardian itself |

All profiles retain the same identity, environment, secret-pattern, and Git provenance checks. `static-web` is intentionally orthogonal to the software-document hierarchy: it is strict about the web artifact without forcing package-oriented publication documents into a minimal site.

## Exact-revision publication contract

When Guardian is selected as the pre-publication gate:

1. identify the intended target repository and full commit SHA;
2. dispatch the caller workflow against a ref that resolves to that intended revision;
3. choose the appropriate publication profile;
4. require the workflow to succeed;
5. require receipt result `VERIFIED`;
6. require receipt revision to equal the intended full commit SHA;
7. retain the receipt with the publication record;
8. only then allow the separately authorized human or operator to publish;
9. independently verify the resulting public or release state.

If Guardian returns `ACTION REQUIRED` or `INDETERMINATE`, do not treat the result as permission to publish.

GitHub's `public` event fires **after** a private-to-public transition. It cannot prevent the initial disclosure. The post-event audit is defense in depth, not a substitute for the on-demand pre-publication run. A manual Guardian workflow is evidence generation; it does not technically lock GitHub's visibility control or grant publication authority.

## Reusable workflow version pin

The `v1.0.0` reusable-workflow tag predates caller-input shell hardening and is superseded. Do not use that tag as the reusable-workflow reference. Pin callers to a reviewed, immutable commit SHA from the current `main` history until a superseding release is published.

The example intentionally uses `<PINNED_GUARDIAN_SHA>` so an adopter must review and record the exact 40-character commit it intends to trust. Replace the placeholder before enabling the workflow.

## Manual pre-publication invocation

For a caller workflow installed in a target repository:

```bash
gh workflow run guardian.yml -R OWNER/REPO --ref TARGET_BRANCH -f profile=release
```

Use `profile=static-web`, `baseline`, or `python` when appropriate. The `development` profile is reserved for deliberate spot-checks. Inspect the resulting run's `head_sha`, job conclusion, and receipt before any publication operation.

## Post-publication audit

The caller template listens for:

- `public` — audits the default-branch revision after a private-to-public transition, using the `baseline` profile;
- `release.published` — audits the published release revision using the `release` profile.

These events are useful for detection and evidence after publication. They do not block the event that triggered them and do not retroactively prevent disclosure.

## Efficiency rules

Guardian should reduce uncertainty without creating routine ceremony:

- leave normal PR/push CI to each project's existing test and quality workflows;
- do not install Guardian globally or make it a universal required status check;
- invoke the strict profiles only when a publication decision is actually being prepared;
- use the light `development` profile only for a deliberate diagnostic;
- cancel stale runs when a newer revision supersedes them;
- keep checks read-only and network-minimal;
- retain receipts for publication decisions, not every development commit;
- never duplicate an authoritative test merely to create another green badge;
- do not add dashboards, services, or automated publication authority when GitHub already provides the needed operational surface.

## Why Guardian does not publish by itself

Combining verification and administrative mutation in the default verifier would collapse the trust boundary. Guardian therefore remains:

```text
Sensor + Verifier + Evidence Generator
```

The surrounding human or authorized operator owns publication authority.
