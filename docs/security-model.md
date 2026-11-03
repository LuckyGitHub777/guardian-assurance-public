# Security Model

Guardian is a **sensor + verifier + evidence generator**, not an administrator.

The v1 trust boundary assumes the local machine and Git executable are available to Guardian. Guardian verifies publication hygiene and provenance properties; it is not a tamper-resistant hardware root of trust and does not defend against an attacker that already fully controls both the verifier and its runtime.

Guardian therefore avoids universal claims. `VERIFIED` means the configured required checks completed successfully for the exact revision recorded in the receipt.

Policy files are validated against the complete v1 structure before checks run. Missing, mistyped, or unknown policy fields produce a policy error and an `INDETERMINATE` CLI outcome; they do not silently disable required checks.

Tracked symlinks are inspected as their stored link-target text. Guardian does not dereference a symlink to read an unrelated local file. Text reads are bounded to the policy limit plus one byte; known binary suffixes are not loaded into memory by the text scanner. Policy v1 caps that limit at 16 MiB.

Text-check coverage is explicit: tracked files that are not recognized as common binary formats and exceed the configured scan limit or cannot be decoded cause `INDETERMINATE`, not `VERIFIED`. Common binary suffixes are outside this text-scanning contract; binary metadata and embedded content require the separate media review in [Publication boundary](publication-boundary.md). Unknown or extensionless unreadable files fail closed.
