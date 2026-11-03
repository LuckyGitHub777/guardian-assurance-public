# Publication boundary: what automated checks do not prove

A successful repository-policy check is evidence about a particular configuration and revision, not proof that public release is free of personal information, confidential material, or legal claims.

## Must be independently reviewed before changing visibility or deploying

1. **Identity and intent:** accountable rights holder, repository owner, target SHA, audience, domain, public purpose and disclosure authorization.
2. **Complete Git footprint:** commits, branch and tag refs, PR/issue texts and revisions, logs, CI artifacts and releases. Changing the current working tree cannot retract historic public content.
3. **Personal information:** names, affiliations, addresses, email, phone, usernames, personal stories, screenshots, transcripts, private AI-session links and re-identifying combinations. Preserve required authorship and attribution rather than falsifying provenance.
4. **Non-text assets:** images, video, PDFs, archives, packaged binaries and previews. Inspect embedded metadata, source paths, overlays, EXIF/XMP, hidden layers, external links and redistribution rights.
5. **Runtime privacy and security:** user-controlled fields, browser storage origins, outbound network destinations, consent, third-party libraries, secret use, access boundaries, branch protection, tests and preview/deploy parity.
6. **Public messaging:** claims align with evidence, attribution and license grants are authorized, errors are understandable, and the public site is verified signed out on mobile and desktop.

## Decision contract

If any gate remains **unverified**, the publication decision is **HOLD**. Do not convert a successful narrow scan into a 100% OPSEC assurance. If historical sensitive material is already public, avoid an impulsive force-push or deletion; inventory dependents and coordinate remediation separately. Retain detailed evidence in private storage, not public PR bodies or generated artifacts.

Current verification code does not exhaustively inspect all history, all files in all refs, all binary metadata, all public PR revisions, or off-platform caches. A passing outcome must disclose these limitations.

## Optional private contextual identity screen

For a specific authorized pre-publication verification, the operator may
provide a private newline-separated set of context terms **at runtime** using
`GUARDIAN_OPSEC_DENYLIST` and enable `GUARDIAN_REQUIRE_CONTEXT=1`. Do not
commit, print, store in public CI inputs, or include actual terms in PRs.

The verification engine includes a `contextual_identity` check **only** when
either setting is present. If required input is missing, malformed, or exceeds
supported limits, the check returns `INDETERMINATE` rather than a green receipt.
A detected filename or file-content match returns `ACTION_REQUIRED` with
generic finding codes; it never emits the term or matching filename.

Scope remains deliberately narrow: **current tracked text tree** only.
Binary metadata, Git history, issues, releases, websites, archives, aliases
and personal combinations are not certified by this check. The absence of a
configured private list means **no contextual coverage was performed**; normal
development CI remains unaffected.

An authorized local operator may run:

```bash
GUARDIAN_REQUIRE_CONTEXT=1 GUARDIAN_OPSEC_DENYLIST="$PRIVATE_RUNTIME_TERMS" guardian-pa verify . --receipt ../guardian-private-receipt.json
```

Use a secure local environment or approved secret manager for the terms.
Review the private receipt and complete all other publication gates before
publishing any artifact. A green bounded scan is not blanket sanitation.
