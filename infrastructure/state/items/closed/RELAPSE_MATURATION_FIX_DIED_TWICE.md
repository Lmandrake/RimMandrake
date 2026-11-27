# RELAPSE_MATURATION_FIX_DIED_TWICE

## spec

The incident `maturation-20261121225203` was tamed on 2026-11-26 21:55Z after two relapses in 24 h. Both relapses
carried `maturation.list_gate_blind_passes` (the Workshop Pipeline's ticket lane held ready work on a check that could
not look). Read from Archmagi `D:\ClaudeWork\rimmandrake\ops_watch\told.jsonl` and `series\maturation.jsonl`, the metric
rang in at least six episodes on 2026-11-26 and 27, each with a new sub-cause, and each fixed one at a time:

- a shape event not yet landed (exit 2, self-cleared, judged not worth the touch);
- no `python.exe` on the tick's PATH (exit 3 and exit 127; cce50b77fd, 8bfe14ac0e);
- a check shaped onto a selftest that is not yet on origin/main (exit 2; 45782d4084 refuses it at shape);
- a live bundle run that works the item (exit 2; 854af661ad: a live run outranks an unmeasured check);
- a live check with no game that runs its mods (exit 2; b200cceda8: it takes a free game or reads waits_game);
- a live check that the bridge refused in the CAMPAIGN profile (exit 2, 06:43Z 11-27, cleared by itself).

The other two metrics of the first relapse (`clone_behind_min`, `hand_acts_overdue`) have their own fixed items
(RIMMANDRAKE_UNSTICK_TICK_CLONE_TWO_LINES_BLOCK_EVERY_PULL, RIMMANDRAKE_FIX_HAND_ACT_CLOCK_LOCAL_TIME_READ_AS_UTC).

The structural fault: a check that cannot look, on an item with no live run, reads `blind` on every tick, for ever.
Nothing in the pipeline repairs the check. Only the alarm moves it, and each ring buys an Operations read that fixes one
sub-cause. The fix: when one item's check reads blind for `blind_repair_passes` applied ticks in a row (list_dispatch.json,
under the alarm's line of more than 3), the lane sends the item through every launch gate as a Work run whose brief says
that the check cannot look and that the run repairs the check (or its runner) first, then does the work. That run is
counted like any Work run, so a check that still cannot look after `max_runs_per_item` runs reads `stopped` on the
Conductor's owed view, with its reason, instead of blind. A hold that is not one item's check (an unreadable ledger, the
games, the load, the run records) stays blind and is told by the alarm as before.

## verify

`python3 src/RimMandrake/rimflow/selftest_list_dispatch.py` (the test `t_a_check_that_stays_blind_gets_a_repair_run`).

## criteria

- One item whose check stays unmeasured (no live run, not a game wait) reads `blind` for its first
  `blind_repair_passes - 1` applied ticks and then a Work run is launched on it, with `repair_check` on the row.
- The Work brief of that run names the check's output and tells the run to repair the check or its runner.
- The streak is per item; it ends when the check reads anything else; a dry or run-now tick neither counts nor ends it.
- After the repair run ends and the check still cannot look, the item reads `stopped` by the Work-run count, not blind.
- `blind_hold` does not count a row that launched its repair run.

## refs

file: src/RimMandrake/rimflow/list_dispatch.py
file: src/RimMandrake/rimflow/list_dispatch.json
file: src/RimMandrake/rimflow/selftest_list_dispatch.py
file: design/specs/2026-11-23-list-dispatch/boundary.md
