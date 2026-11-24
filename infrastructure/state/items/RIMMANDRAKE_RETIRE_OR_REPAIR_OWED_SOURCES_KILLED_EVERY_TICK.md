# RIMMANDRAKE_RETIRE_OR_REPAIR_OWED_SOURCES_KILLED_EVERY_TICK

## spec

The failure, measured 2026-11-23 from `/mnt/d/ClaudeWork/rimmandrake/dispatcher/journal.jsonl`: the Dispatcher step
`owed_sources` (`owed.py sync-sources`, every 300 s) was killed at its 6 to 10 s budget on 210 of 210 passes on 2026-11-22,
175 of 185 on 11-23 and 19 of 19 on 11-24 UTC to 02:14Z. A hand run needed more than 110 s (load 19). Cause [guess ~85%]: `owed.live_rows`
computes `maturation.next_step` for every versioned mod, and those reads grew. The last item it filed is of
2026-11-20T02:51Z; it filed 9 in all. So the step spends about 8 s of a tick and does nothing.

Two ways; the first is recommended:
1. Retire the step. What it did is done elsewhere now: the Needs Conductor list (`maturation_now.conductor_needs`) shows the
   Conductor's hand steps, and `left_open_continue.py` carries a run that left its item open. Check both against
   `owed.maturation_sources` and `owed.detached_sources` first.
2. Or read the rows from `dispatcher/maturation/reading.json` in place of `live_rows`.

In both cases delete the kill queue of `promise_scan.py` (`seat_restart.queue_untracked_promises`, `owed.promise_sources`,
`owed.read_promises`, `dispatcher/untracked_promises.jsonl`): 2 rows ever, both false ("After you read that, are you ready for
a question card?", "Tell me a little ahead and I will have it up."), none filed. The wake already reprints the dead
window's last reply. Keep the per-prompt note: 35 of 176 turns that showed it filed an owed item (20%), against 130 of 1,860
(7%) without it (design/specs/2026-11-23-streamline-review-state/state.md).

## verify

The item's outcome check (`--effect`): exit 0 when `owed_sources_every_s` is gone from `dispatcher_schedule.json`, or when at
least 15 of the last 20 `owed_sources` journal rows are not KILLED. Seen failing (exit 1) on 2026-11-23 before filing.

## criteria

- A1: the outcome check exits 0.
- A2: `grep -rn untracked_promises src .claude` finds nothing, and `selftest_promise_scan.py`, `selftest_owed_sources.py` and
  `selftest_seat_restart.py` pass.
