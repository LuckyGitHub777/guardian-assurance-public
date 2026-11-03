# Evidence Contract

`guardian-receipt-v1` is a revision-bound statement of what Guardian observed.

A receipt binds to Guardian version, policy version and digest, full Git commit SHA, Git tree SHA, check outcomes, and the overall result.

Release receipts belong in CI artifacts or GitHub Release assets associated with the exact tagged commit. They should not be committed back into the verified source branch because doing so would change the revision they describe.
