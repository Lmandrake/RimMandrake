# Polish beside design/specs/2026-11-19-failed-before-reads/boundary.md

- `src/RimMandrake/rimflow/selftest_failed_before_reads.py` `t_lane_launched_run_is_no_hand_run` does not test the
  "once" of the lane fold: call `MH._fold_tick_own(st, ...)` a second time on the readable lane state and check that
  each of `run-lane-old`, `run-lane-cleared` has one line in `hand_folds.jsonl`. Today the shared `a["id"] in folds`
  guard of `_fold_tick_own` keeps it, and `t_hand_run_the_books_now_own_is_folded` pins that guard.
