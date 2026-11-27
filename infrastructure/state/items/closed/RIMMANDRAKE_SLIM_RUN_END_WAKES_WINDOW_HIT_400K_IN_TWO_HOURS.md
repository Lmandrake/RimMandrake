# RIMMANDRAKE_SLIM_RUN_END_WAKES_WINDOW_HIT_400K_IN_TWO_HOURS

## spec

The Conductor window c95f9ab4 (started 2026-11-25 6:38 PM PST) reached its hard context limit at 9:00 PM PST.
Measured over its transcript on Archmagi (`measure_tx.py`, 2026-11-26):

- 19 run-end wakes carried 129,090 characters. 73,415 of them were the state block (29 rows each wake). Most rows
  (held mods, switches, accounts) did not change from one wake to the next.
- The first turn printed the Conductor log tail (12.9k characters) twice, the owed list twice, and the old window's
  last reply and the top lines of his words twice. `seat_restart.py wake` printed them, then `handoff.py --wake`
  and the Start of turn steps (`queue CONDUCTOR --owed`, `tail -n 40 log.md`) printed them again.

Cut the repeats:
1. A run-end wake to the same window prints only the state rows that changed since its last wake. The unchanged
   rows become one counted line. A new window, or a window that compacted since its last wake, gets the whole block.
2. The first turn prints the log tail, the owed list, the last reply and his words once. A second wake read in the
   same window prints one line that names the command that prints them again. The Start of turn steps no longer
   run the owed list or the log tail again.

## verify

- `python3 src/RimMandrake/rimflow/selftest_run_end_wake_slim.py` (two wakes in a row with the same state print the
  unchanged rows once; red on the parent).
- `python3 src/RimMandrake/rimflow/selftest_wake_reads_once.py` (the first-turn reads print once per window; red on
  the parent).
- The byte size of a first-turn wake, before and after, in a note on this item.

## criteria

- [ ] a second run-end wake with the same state prints no unchanged state row again
- [ ] the first turn prints the log tail and the owed list once

## refs

file: src/RimMandrake/rimflow/run_end_wake.py
file: src/RimMandrake/rimflow/seat_restart.py
file: src/RimMandrake/Utils/handoff.py
file: src/RimMandrake/rimflow/roles/conductor.md
