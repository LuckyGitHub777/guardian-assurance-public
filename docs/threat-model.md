# Threat Model

Guardian v1 focuses on accidental publication risk and bounded repository-integrity failures:

- committed credentials or private-key material;
- machine-specific local paths or local artifacts;
- missing public governance/security files;
- placeholder/local Git author identity;
- unresolved or dirty Git provenance;
- evidence that is not bound to a revision and policy.

Out of scope for v1:

- complete malware detection;
- dependency vulnerability intelligence;
- remote service compromise;
- malicious Git server behavior;
- compromised host/kernel/runtime;
- exhaustive secret detection;
- legal or regulatory certification.

Unknown or unavailable required evidence must produce `INDETERMINATE` rather than `VERIFIED`.
