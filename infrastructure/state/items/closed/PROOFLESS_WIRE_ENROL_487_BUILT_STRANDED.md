# PROOFLESS_WIRE_ENROL_487_BUILT_STRANDED

## spec

Split from `LIVE_PROOF_LINES_FILL_FOR_BUILT` (built items owing live criteria with no live-proof line wait forever).
Measured 2026-11-06 on 9172db627d: 487 built/validated items, 858 owed live criteria (L2 547, L1 204, GREEN-MIN 99,
GREEN-FULL 8) have no `live-proof <crit>:` line in `infrastructure/state/live_proofs/<ID>.txt`; 21 of them have a file
missing only some lines. `relentless_live_round.py eligible` counts them only as `skipped["no proof"]`.

Why nobody writes them: `relentless.eligible()` admits only `proposed`/`ready`, and the live round never turns a missing
line into work (by design: a guessed proof would pass criteria nobody proved). `rimflow start` on a built item moves it
to `doing` and loses `built_sha`, so the normal lease path cannot be reused as is.

Shape: the supervisor enrols such an item as a proof-lines job (store flag, no ledger start/close): the worker writes
the missing lines (and `.criteria` where needed), lints them through `relentless_live.refused_proof`, commits, finishes;
on a checked PASS the store marks it done and leaves the ledger built, so the live round picks the lines up on the next
round. A per-tick cap (rules) keeps 487 items from flooding the pool. A criterion no honest line can prove (an owner
look, a stale criterion) is put down with its reason on the ledger, never a guessed line.

## criteria

- A1 L0: a selftest shows `eligible()` (or its sibling) admits a built item owing a live criterion with no line, and refuses one whose lines are all present.
- A2 L0: a selftest shows the lease of such an item issues no `rimflow start` and its checked PASS issues no `close`/`implemented`.
- A3 L0: a selftest shows the per-tick cap from relentless_rules.json bounds how many such items enrol in one tick.
