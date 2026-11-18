# RIMMANDRAKE_CHARGE_NOTHING_FOR_JUDGE_STOPPED_RUN

## spec
When the Designer's stage-5 pre-launch judge (`role_launch.py stage5-judge` -> `coverage_judge.py`) stops a concept
(`coverage_judge.hold`: status blocked + `coverage_stop`, exit STOP_EXIT=3), the unit exits before any model starts.
The role_done harvest in `role_launch.py` (~1136-1216) has a no-model branch only for `program_closed` (the
stage5_program PRE_DONE_EXIT close); a judge stop falls through to the model path, so:

1. the run is charged its whole budget: "UNMEASURED (counted at its budget)" (400,000 for rm-role-designer-1794938276);
2. `close_concept` judges an absent result.json, the stage machine rejects it, `rejection_cause` reads "unknown", and
   the run is re-chained: the next launch on the blocked concept is refused (`role:Designer:stage_refused`, 18:12:44Z),
   a second, redundant alarm about a designed stop.

Evidence (incident roles-20261117113849): `D:\ClaudeWork\rimmandrake\dispatcher\journal.jsonl` lines 15435 (launch
17:57:56Z), 15459-15463 (role_done failed, stage_rejected, rejection cause unknown, role:Designer:failed, 18:05:52Z);
`D:\ClaudeWork\rimmandrake\dispatcher\roles\rm-role-designer-1794938276.err` (the judge's stop, no claude start);
`design/concepts/Pyrelands/stage.json` coverage_stop.at 18:05:37Z, inside the run window.

Fix shape (no new rule or judging machinery, Relentless freeze): beside the `program_closed` branch, read the
concept's stage.json; when there is no result and `coverage_stop.at` falls in [run.at, now], record the run with
tokens 0 / raw 0 (no model started) and route it as the judge's designed stop: one alarm naming the stop and the
`coverage_judge.py release <dir> --why ...` that lifts it, no re-chain.

## verify
A selftest in `selftest_role_launch.py`: a concept run with no result, no transcript and a stage.json whose
coverage_stop.at is inside the run window harvests with tokens 0 and launches no re-chain; the same run with
coverage_stop.at before run.at still harvests as today (failed, counted at its budget). Watch it fail first.

## criteria
- a judge-stopped run is charged 0 tokens, not its budget
- a judge-stopped run is not re-chained and raises no stage_refused on the next tick
- a run with no result and no judge stop in its window is harvested exactly as before

## refs
file: src/RimMandrake/rimflow/role_launch.py
file: src/RimMandrake/rimflow/selftest_role_launch.py
