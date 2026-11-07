# Guardian

**Publication Assurance Infrastructure**

Verify before publishing. Evidence before claims.

**GitHub Pages:** [Selected Public Works](https://luckygithub777.github.io/guardian-assurance-public/) is a separate static gallery served from this repository. It is not the Guardian CLI, a security certification, or an endorsement of the linked projects.

Guardian is a local-first, read-only publication assurance tool that verifies a repository before release and produces evidence bound to the exact revision examined.

## What you can do with it

- **Inspect a release candidate:** check tracked content, common secret patterns, publication identity, and repository provenance without modifying the target.
- **Understand the result:** distinguish `VERIFIED`, `ACTION REQUIRED`, and `INDETERMINATE` instead of treating an incomplete check as a pass.
- **Keep evidence tied to the source:** write an optional receipt outside the repository so the verification does not change the revision it describes.

See the [example receipt](examples/receipt.example.json) for the result format. Guardian checks only its configured policy and cannot grant rights, validate full Git history for publication, or certify security.

## Quick start

From the repository root:

```bash
python -m pip install .
guardian-pa verify .
```

A successful verification is intentionally narrow: it means the exact repository revision satisfied the configured Guardian policy at verification time. Guardian does **not** claim that software is universally secure, bug-free, compliant, or safe against unknown future threats.

Before changing a repository's visibility or shipping public artifacts, separately review identity, full Git history, PR revisions, non-text media, third-party rights, and live UX. These are **outside** a narrow Guardian `VERIFIED` result. See [Publication boundary](docs/publication-boundary.md).

## Automation

Guardian is an **optional publication-boundary tool**, not a required dependency for everyday development and not a global control plane for every repository.

Keep each project's existing CI, tests, and normal upgrade loop moving. Do **not** add Guardian to every pull request or push by default. Invoke it when a real publication decision or targeted assurance need justifies the additional check.

The recommended model is:

```text
routine development
    ↓
project's existing CI and tests
    ↓
no Guardian dependency by default

actual publication decision
    ↓
optional manual Guardian run on the intended revision
    ↓
revision-bound receipt
    ↓
authorized publish operation
    ↓
optional post-publication / release audit
```

The example caller is deliberately on-demand: it has a manual pre-publication run and optional post-publication/release audit events, with **no pull-request or push trigger**. A `public` event happens after a private-to-public transition; it is an audit signal, not a preventive gate.

**Version note:** the `v1.0.0` reusable-workflow tag predates caller-input shell hardening and is superseded. Pin callers to a reviewed, immutable commit SHA from current `main` until a superseding release is published. See [automation guidance](docs/automation.md).

See [`docs/automation.md`](docs/automation.md) and [`examples/github/guardian.yml`](examples/github/guardian.yml).

When Guardian is selected as a pre-publication gate, a human or authorized automation layer must wait for an exact-revision `VERIFIED` result before publishing. Guardian itself never changes visibility or publishes.

## Results

Guardian has three top-level outcomes:

- `VERIFIED` — every required check completed and passed.
- `ACTION REQUIRED` — at least one required check completed and found a policy violation.
- `INDETERMINATE` — Guardian could not reliably complete at least one required check.

Unknown never becomes green.

## What Guardian checks

- **Identity** — the publication identity is not an obvious local/test placeholder.
- **Environment** — common machine-specific files and absolute local paths are absent.
- **Secrets** — common credential formats and private-key material are not present in tracked text files.
- **Repository** — required public-facing files are present **and tracked in the attested revision**, while forbidden local artifacts are not tracked.
- **Provenance** — the target is a Git repository with a resolvable revision and clean tracked worktree.

## Read-only boundary

A normal Guardian verification does not:

- modify the target repository;
- repair files;
- commit or push changes;
- change GitHub permissions;
- publish releases;
- upload repository contents;
- make network requests.

Evidence is generated in memory. To persist a receipt, provide an explicit path **outside** the repository:

```bash
guardian-pa verify . --receipt ../guardian-receipt.json
```

Guardian rejects in-repository receipt output by default so verification does not mutate the artifact being judged.

## CLI

```text
guardian-pa verify [TARGET] [--policy FILE] [--receipt FILE] [--json] [--verbose]
```

Exit codes:

```text
0  VERIFIED
1  ACTION_REQUIRED
2  INDETERMINATE / EXECUTION_ERROR
```

## Policy

The built-in Python policy is stored at [`policies/default.yaml`](policies/default.yaml). In v1.0, policy files use JSON syntax, which is valid YAML 1.2, so the runtime remains dependency-free.

Reusable automation also provides [`development`](policies/development.yaml), [`static-web`](policies/static-web.yaml), [`baseline`](policies/baseline.yaml), and [`release`](policies/release.yaml) profiles. The development profile is available for an explicitly requested, targeted diagnostic; it is not a default CI lane.

## Evidence

Receipts use [`guardian-receipt-v1`](schemas/guardian-receipt-v1.schema.json) and bind verification to:

- Guardian version;
- full Git commit SHA;
- Git tree SHA;
- policy version and SHA-256 digest;
- the checks executed and their outcomes.

Receipts do not include secret values, usernames, hostnames, home directories, or absolute local paths.

Release evidence should be attached to the GitHub release or CI run for the exact tagged commit, not committed back into `main`; committing a receipt would change the commit it claims to describe.

## Security and privacy

Guardian is deliberately conservative. Required-check failure produces `ACTION REQUIRED`; inability to determine a required condition produces `INDETERMINATE`.

See [`SECURITY.md`](SECURITY.md), [`docs/security-model.md`](docs/security-model.md), [`docs/threat-model.md`](docs/threat-model.md), and [`docs/privacy.md`](docs/privacy.md).

## Development

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
guardian-pa verify . --receipt ../guardian-receipt.json
```

The release gate requires executable tests, adversarial negative cases, privacy/redaction checks, Guardian self-verification, and CI reproduction on the exact release commit.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
