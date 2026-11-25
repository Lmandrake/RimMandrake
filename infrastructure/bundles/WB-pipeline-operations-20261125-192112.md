# WB-pipeline-operations-20261125-192112 state

Worker on SteveDesktop; ops_watch and the alarms live on Archmagi (`ssh mandrake@archmagi-wsl`, store
`/mnt/d/ClaudeWork/rimmandrake/ops_watch/`). Scratch copies of item dumps: `/mnt/d/ClaudeWork/scratch/wb192112/` (SteveDesktop).

## Learned about the system
- Sense now runs apart (rm-metronome-sense, 120 s hang guard, 5a08fffc96). 24 h to 2026-11-25 19:22Z: 1295 sense beats, 0 non-zero
  exits; sense_kills.jsonl last kill 2026-11-23T05:27Z; sense.families_blind = 0.
- Alarm hosts that rang again owe a class guard (`rimflow guard <ID> --test selftest*.py --instance ...`), shown red before the close
  (model.guard_owed, repeat_guard.py). A correct alarm on an external outage has no fix to guard.
- Live readings 2026-11-25 19:2xZ: ringing MATURATION_HAND_ACT (2), SCRATCH_DIRTY_END (1: PermissionError on rename into
  /mnt/d/ClaudeWork/backups/leftovers/.../.incoming-*). All other member alarms read 0.

## Members (class, outcome, commit)
| member | class | outcome |
|---|---|---|
| RIMMANDRAKE_FIND_SENSE_SLOWDOWN_SEVEN_IN_TEN_KILLED | ALREADY FIXED (5a08fffc96 + 6e7ea2cae4..) | closed |
| RIMMANDRAKE_FIX_DISK_FAMILY_OVERRUNS_BEAT_STALE_READING | ALREADY FIXED (same cause) | closed |
| RIMMANDRAKE_WATCH_OPS_SENSE_OVERRUN_MOST_FAMILIES_BLIND | ALREADY FIXED (same cause) | closed |
| WRAPUP_SETTINGS_DEBT_RESTORE_TIDY_ELF | ALREADY FIXED: A1 PASS on SteveDesktop 2026-11-25T17:01Z | closed |
| OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ | REAL: archive rename refused by Windows (EACCES) | fixed 35c1d817ff, guard shown red; live owed |
| OPS_SCRATCH_DIRT_MEASURE_AT_START_SANF | REAL: count lines with no danger | fixed 35c1d817ff, guard shown red; live owed |
| OPS_WORKER_CLONE_POOL_RESTORE_HMOQ_PBAL | REAL: run-end landing race | fixed 55a0dde614, guard shown red; live owed |
| OPS_MATURATION_IDLE_ADVANCING_MOD_CBFQ | NOT WORTH THE TOUCH | dropped 3c0db874cc |
| OPS_MATURATION_MOD_PAUSED_FYEB | NOT WORTH THE TOUCH (designed pauses) | dropped 0e14e6142a |
| OPS_MATURATION_HAND_ACT_UNFOLDED_ZLWA | REFUSED: folds are the Conductor's | note d86a8216ad |
| RELAPSE_REFUSALS_FIX_DIED_TWICE | NOT WORTH THE TOUCH (cause gone 6 days) | dropped 63a866c26e |
| WRAPUP_SETTINGS_DEBT_RESTORE_TIDY_ELF | ALREADY FIXED | done 0b66b4ba91 |
| OPS_DESIGNER_UNSTICK_READY_AND_WAITING_GZKV | correct alarm, cause gone (Pyrelands locked 11-21 20:06Z); guard owed by Conductor ruling | to refuse |
| OPS_SEATS_READING_RESTORE_IMJA_YAKX, OPS_SEAT_CLONE_DIRT_RESTORE_VTLF, OPS_STEVE_SEATS_RESTORE_QTWK_RGFZ | correct alarms on real conditions | to class |
| RESOURCE_SIM_BUILD_WAITS_FOR_REAL_DATA | a build, not a fault | to refuse |

## Next, in order
1. Class the seats/steve hosts, refuse QUEUE_STALLED and RESOURCE_SIM.
2. Fresh reader of scratch_reap.py rename_retrying, scratch_reap_sanity.json, scratch_clone.py live_seen.
3. Live: next rm-scratch-reap run on Archmagi (runs from /home/mandrake/rm/dispatch) reads sanity.json end with no rename failure;
   disk.pool_breach reading; then close END, START, POOL with guard rerun green.

## Context size after each group
- after classing start: 114k of 1M
- after scratch, pool, maturation groups: 236k of 1M
