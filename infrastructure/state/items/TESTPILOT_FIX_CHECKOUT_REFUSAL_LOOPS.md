# TESTPILOT_FIX_CHECKOUT_REFUSAL_LOOPS

Filed (BENCH): testpilot: a PilotRefused mid-act (e.g. an `_at_rev` checkout failure in reload) bypasses the abort
requeue budget: the candidate stays queued forever, every pass aborts, 0 evidence, never parked (probe: 4 passes, 4
reload decisions, state queued). Evidence `D:\ClaudeWork\rimmandrake\arena_testpilot\indep6\probe_defects.txt`.
Blocks ARENA_TESTPILOT_BUILD_RELOAD_SCALED_BY_COST.

## verify
- L0: the probe re-run: a candidate whose checkout always refuses is parked once the abort budget is spent, never
  queued forever; a selftest for it is red when the fix is reverted.
- Stopping point: finish.

## criteria
- A1 L0: refused-checkout candidate parks after the budget; forced-failure test red on revert
