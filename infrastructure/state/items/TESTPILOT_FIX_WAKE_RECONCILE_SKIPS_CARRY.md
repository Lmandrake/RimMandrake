# TESTPILOT_FIX_WAKE_RECONCILE_SKIPS_CARRY

Found by BENCH's independent check of e73abe40ab (F5 fix, `Pilot._reconcile`).

**Defect.** `wake()` now runs `_reconcile()`, which calls `_resolve(c)` for every queued/testing candidate.
`_resolve` reads `scenario_status`, which matches evidence by item + fingerprint + scn_hash, not by candidate id. So a
same-fingerprint rebuild that was enqueued while no pilot was running (the normal case: one item per pass, then a
handoff, and the next pilot wakes) is resolved inside `wake()` using its parent's evidence. It never reaches
`decide() -> carry`, so the L9a audit trail is missing: there is no `carry` decision, no carried records under the new
candidate id, and no `_supersede_older`. The verdict is correct, but nothing in the record explains it.

**Repro** (fake driver, offline): `D:\ClaudeWork\rimmandrake\testpilot_fixes\check\myprobes.py`, `p_wake_resolves_samefp`:
`child=resolved/pass carry_decisions=0 carried_ev=0`.

**Fix direction.** Limit `_reconcile` to candidates that have evidence recorded under their OWN cand id (the crash
window F5 targets). Rebuilds with no evidence of their own should go to `decide`/`carry`. Write the test red first.

## verify
A new selftest: run a pass, hand off, enqueue a same-fp rebuild, then wake a fresh pilot. The rebuild must resolve through a
`carry` decision that has carried records under its own cand. The test must be red on e73abe40ab, and the F5 tests must stay green.
