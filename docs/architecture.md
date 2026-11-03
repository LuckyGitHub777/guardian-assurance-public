# Architecture

Guardian follows a deliberately small pipeline:

```text
Policy -> Engine -> Checks -> Evidence -> Decision
```

Checks are independent and return `PASS`, `FAIL`, or `INDETERMINATE`. The engine maps them to a top-level result:

- any `FAIL` -> `ACTION_REQUIRED`;
- otherwise any `INDETERMINATE` -> `INDETERMINATE`;
- otherwise -> `VERIFIED`.

This rule prevents uncertainty from becoming success.

The default verification path performs no network activity and no target-repository mutation.
