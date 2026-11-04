## Problem
`scratch_clone.py clone_unlanded()` (scratch_stranded, helper clones under rm/scratch and session scratchpads) counts every dirty ledger or code_review shard as unlanded work. The residue fix CLONE_POOL_FIX_TRANSCRIPT_RESIDUE put `noise_on_origin()` only on the POOL path (`dirty_beyond_origin`). So a Conductor helper clone whose shard lines all reached origin/main still reads stranded after an hour and raises disk.pool_breach. 2026-11-03 08:30Z: 4 of 5 stranded rows (rm/scratch/BENCH booksjam, gamehold, livefix-20261102-193930, relentless-waste) held only BENCH.jsonl shard lines, every one already on origin/main (checked line by line after a fetch). This is the 5th outage of OPS_WORKER_CLONE_POOL_RESTORE_HMOQ.

Second cause: a Relentless pool clone in its game phase (VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL, live lease gen 9) held a one-line clean-mark commit (9995a7b894, code_review shard) through the wait for the bridge and read stranded after an hour. Relentless should land shard-only commits at once rather than carry them through a game wait, or a live lease should excuse the clone.

## Fix
1. In `clone_unlanded`, skip POOL_NOISE paths whose lines origin already holds, judged against the MIRROR tips or a fresh fetch, never the clone's own origin/main ref (a `--shared` scratch clone's ref is stale).
2. Relentless lands a shard-only commit before a game wait (or pool `stranded` excuses a clone under a live lease).
3. Selftest cases in selftest_scratch_clone.py for both.

## Done when
scratch_stranded ignores landed shard dirt; pool_breach stays 0 through a day of Conductor helper clones; close with `--live "unit=rm-ops-watch.timer reading=/mnt/d/ClaudeWork/rimmandrake/ops_watch/status.json max_age=2h"`.
