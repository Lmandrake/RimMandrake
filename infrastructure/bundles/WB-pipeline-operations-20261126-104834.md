# WB-pipeline-operations-20261126-104834

Member: OPS_SCRATCH_OUTSIDE_READING_RESTORE_WLTC (claimed, BENCH).

- Step A done: keep 1. Past causes all have closed fixes; the live cause is a slow reap run (137 min seen) against the 150 min stale line of disk.scratch_outside_blind, with the sanity record stamped only at a run's start and end.
- Step B done: check `cmd:python3 src/RimMandrake/Utils/selftest_scratch_outside_heartbeat.py`, red on the parent (3 fails).
- Step C, the fix: published 533ada697a52 (scratch_reap.sanity_beat + ops_watch.scratch_outside reads `beat`). 7/7 touched selftests green; mutant `seen = at` caught (2 fails).
- Stopped by the account-end stop order (ct_000209) after the publish.

Next:
1. One fresh reader (not this run) reads only the diff of 533ada697a52, once.
2. Live proof: once /home/mandrake/rm/dispatch holds 533ada697a52, a reap run started after that writes a top-level `beat` in ~/.local/state/rm-scratch-reap/sanity.json. Read it while the run is in progress.
3. Close with `--sha 533ada697a52 --live "unit=rm-scratch-reap.timer reading=/home/mandrake/.local/state/rm-scratch-reap/sanity.json max_age=3h"`.
The reap run that started 2026-11-26 01:23 PST runs the old code and does not beat. If it goes past 150 min, it can raise the alarm once more. That is expected and is not a new fault.
