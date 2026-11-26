# RIMMANDRAKE_FIX_STEWARD_FORECAST_KEEPS_CHAIN_FILLER_DROPS

## spec

`src/RimMandrake/Utils/testq/testq.py` `fill_plan` says it is the one plan that `cmd_fill` and the steward share.
`fill_once` ran one more step after `fill_plan`: it dropped each chain that modcheck no longer declares
(`bad_selection`, `unknown_chains`) and ranked again. The steward (`steward.py` `lane_state`) called only `fill_plan`,
so the steward kept a chain that the filler dropped.

Failure that happened, 2026-11-26 10:27Z: the filler logged `filler: FlowWorks no longer declares proofs; not ranked`,
then `FlowWorks: no owed work; no fill` (verdict exhausted, a settled state). The steward read verdict `pick` with
`["proofs"]`, raised `IDLE_EMPTY: fill would queue FlowWorks: proofs but nothing is pending (the fill failed?)`,
escalated two levels (`STEVE_LANE_UNSTICK_IDLE_UNOWNED_IDLEEMPTY_MWRPSP`) and started one paid wake session. The lane
had no owed work and no fault.

Fix: the drop of undeclared chains moves into the path that `fill_plan` returns. The filler and the steward then read
one plan. `fill_once` keeps its log line.

## refs

file: src/RimMandrake/Utils/testq/testq.py
file: src/RimMandrake/Utils/testq/selftest_testq.py
file: src/RimMandrake/Utils/testq/selftest_testq_steward.py

## verify

`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_testq,selftest_testq_steward`

The two new tests fail on the base commit `badfdaeb24` and pass on the fix:
`t_fill_plan_drops_undeclared_chain_like_the_filler` and
`t_steward_does_not_cry_idle_empty_on_a_chain_the_filler_drops`.

## criteria

- `fill_plan` never returns verdict `pick` with a chain that modcheck refuses as unknown or as offline only.
- With history whose only pickable chain is undeclared, `lane_state` does not read `IDLE_EMPTY` with a reason that
  starts `fill would queue`.
- With no undeclared chain, the plan is the same as before the fix.
- On the live lane, after the dispatch clone pulls the fix, `/mnt/d/ClaudeWork/rimmandrake/testq/steward.json` no
  longer reads `IDLE_EMPTY` for FlowWorks `proofs`.
