# WB-pipeline-operations-20261126-104834

Member: OPS_SCRATCH_OUTSIDE_READING_RESTORE_WLTC: CLOSED at 13eca2af33fc (restart 1, 2026-11-26 03:45 PST).

- Step A done: keep 1. The live cause was a slow reap run (137 min seen) against the 150 min stale line of disk.scratch_outside_blind, with the sanity record stamped only at a run's start and end.
- Step B done: check `cmd:python3 src/RimMandrake/Utils/selftest_scratch_outside_heartbeat.py`, red on the parent (3 fails).
- Step C done: fix 533ada697a52 (scratch_reap.sanity_beat + ops_watch.scratch_outside reads `beat`). Fresh reader (restart run): nothing significant. Class guard: the selftest's `--against <rev>` replay, shown red on 533ada697a52^ with `rimflow guard`, landed 13eca2af33fc.
- Live: the reap run started 11:30:13Z on the new code beat at 11:36:27Z and 11:44:07Z; ops_watch reads blind=0. Closed with `--live unit=rm-scratch-reap.timer reading=~/.local/state/rm-scratch-reap/sanity.json max_age=3h`.

Next: none. The bundle is finished.
