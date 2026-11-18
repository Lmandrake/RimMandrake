# RIMMANDRAKE_FIX_CONTROL_KILL_SURVIVOR_BOOKS_INIT_CODEX_CAUGHT

## spec
Three defects in `src/RimMandrake/rimflow/control.py` named by Codex's review of slice 1 (2026-11-18): (1) `pipe stop
--kill` and the write-now escalation recorded a run `killed` and started its clone return even when the kill left a
survivor or could not verify death; (2) a stopped run was voided in the control store only, so the dispatch books
(`run_void.py` voids.jsonl) still counted it toward trials and the stage ceiling; (3) `pipe init` used `RM_CONTROL_DB`
or the live path directly, so a test process without `RM_CONTROL_DB` initialised the live store.

## verify
`python3 src/RimMandrake/rimflow/selftest_control.py` (t_stop_review_fixes).

## criteria
The three checks of `t_stop_review_fixes` fail on 5dfb7ed767 (watched) and pass after the fix.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py
