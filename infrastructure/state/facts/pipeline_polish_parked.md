# Pipeline polish, parked

One line per finding that was judged not worth the touch, for a component with no boundary page folder. This is a
record. Nobody fixes from it (CLAUDE.md §Touching code has a cost). Several runs append here: append one line, never
rewrite another line.

- 2026-11-19 `RIMMANDRAKE_BATCH_SCRATCH_ARCHIVE_QUEUE_GROWS_HOURLY` (scratch_reap.py): the 28 KB selftest-clone burst drains by itself (ARCHIVE 608 at 4:31 PM, 535, 267 at 6:10 PM; deferred 659 -> 329; disk 523 GB free); one walk of 224 s per tiny clone is slow, not harmful. Refile if three runs in a row do not shrink `deferred` in `~/.local/state/rm-scratch-reap/last_run.json`.
- 2026-11-19 `RIMMANDRAKE_RETAIN_SAVES_BACKUPS_NOTHING_REAPS_THEM` (saves_prune.py, backups, Transient): no reaper for Saves (5.8 GB, 428 files), Saves copies (backups 68 GB) or Transient; C: has 2.1 TB free and D: 1.5 TB free, so no disk is near full. A new deleter of saves could delete a canonical save. A hand cleanup pass does the 2026-11-15 "no trash piling up" ask without new code.
- 2026-11-19 `RIMMANDRAKE_RENAME_FLEET_STATES_READER_STILL_NAMED_FOR_TICK` (fleet_mods.py): `relentless_states` is live code with a retired name; nothing misreads it, and selftest_retired_era_gone.py passes with it.
- 2026-11-19 `RIMMANDRAKE_RENAME_SEVEN_WORK_DIRS_STILL_NAMED_FOR_LOOPS` (seed_trust.py, run_rules.json, running_now.py, mod code): seven `D:\ClaudeWork\rimmandrake` dirs keep era names; live readers find them, and the retired-trees MANIFEST.md says why they stayed. A move would touch a held mod (Graffiti), GSS mod code and the Pyrelands proof inputs for a name only.
- 2026-11-19 `RIMMANDRAKE_RETIRE_JAM_CLASS_DETECTORS_NAMING_REMOVED_TARGETS` (jam_classes.json): the dead detector rows fire nothing; `jam_classes.py lint` names them (24 problems) but no selftest or publish check runs that lint, and evidence_metrics reads the retired belt journal as UNMEASURED, never 0.
