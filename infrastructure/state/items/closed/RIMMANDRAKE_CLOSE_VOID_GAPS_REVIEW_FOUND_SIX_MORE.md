## spec
Codex full-file review of RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS (2026-11-18; the findings are restated here in full) found six more places where a system failure still spends a counter or a void cannot be told apart. The owner, 2026-11-18: "I will not accept ANY system that pointlessly expends such statistical measurements based on failed system calls or behavior."
1. `run_void.sync_system`/`heal_system`: a finished record whose `result` is "unknown" is marked `void_seen[unit]="counted"` (final) and heals an existing void, though "unknown" is UNMEASURED, not a run that counted. Fix: unknown neither finalises `counted` nor heals a void.
2. `run_void.resolve`: `--mod MOD --since TIME` searches only live books and stage entries, so a run already moved to `voided` by sync_system cannot be hand-voided that way ("no run on MOD"). Fix: include moved entries, by their saved `at`.
3. `run_void.SYSTEM_BOOKS` leaves out `pilot_launches`, `ledger_runs`, `cert_rerun`, `cert_red`: a timed-out unit held only there is never classed void_system and its ceiling release stays spent. Fix: scan them (single-entry books apart from lists). The census says the cert rerun has no detached record: check whether its unit has one before scanning.
4. `role_launch.close_concept` (this item's own change): when `stage_void` raises (a transient stage.json read/write), the rejection counts and is routed, and nothing retries the void marking. Fix: persist an owed void mark and retry it before the rejection is counted or routed.
5. `role_launch.chain_ask`: the chain count is charged at the request; a run-now that never launched (stage_open raised, refuse_now) keeps its chain spent. Fix: give the chain back on a request consumed without a launch (the request carries chain_key/chain_stage now).
6. `designer_stage` loop ceiling (`loop_spend`, `ceiling_crossed_at`, `loop_start`): a void run's charge (and a void judge round) still counts toward the loop ceiling that parks the concept. Fix: exclude void units (stage `voided.spend_refs`, void_system rounds and rejections) from the loop's start, spend and crossing; keep the true spend shown apart.

## verify
Acceptance test: drafted, NOT yet watched failing (the filing run was ending its ticket): one check per point in `src/RimMandrake/rimflow/selftest_run_void.py` (points 1-3, 6) and `selftest_role_launch_reject_routes.py` (points 4-5), each built from the scenario above, watched failing on origin/main first; expected 6 new checks, all PASS after the fix.

## criteria
Each of the six either spends nothing for a void_system run (or an UNMEASURED record) or names why it cannot, in `design/RimMandrake/pipeline_trial_counters_census_2026-11-18.md`.

## refs
file: src/RimMandrake/rimflow/run_void.py
file: src/RimMandrake/rimflow/role_launch.py
file: src/RimMandrake/rimflow/designer_stage.py
