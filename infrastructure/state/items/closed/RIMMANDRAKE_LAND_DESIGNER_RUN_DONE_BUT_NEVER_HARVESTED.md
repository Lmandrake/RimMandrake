# RIMMANDRAKE_LAND_DESIGNER_RUN_DONE_BUT_NEVER_HARVESTED

## spec

DesignerCodex run `rm-role-designercodex-1794846919` (Cauldron stage 3, launched 2026-11-16T16:35:19Z) finished
cleanly at ~08:43 PST: `dispatcher/roles/rm-role-designercodex-1794846919.json` has `subtype: done`, `is_error: False`,
and `stage.json` advanced to stage 4 ready. But the Dispatcher journal holds only its `role_launch` line: no
`role_done`, no `role_stage`, so `designer_stage.land_state` never ran. Its 12 concept files and the amended item prose
`CAULDRON_ACCEPTANCE_SCENES_ASSERT_CONTROL_RECOVER.md` sat dirty in the seat clone until `disk.seat_dirt` rang
(incident work_belt-20261116175716). Landed by hand 2026-11-16 10:35 PST: a02d9093cb (concept) and 22eb78c5b7 (item).

The orphan sweep saw "Cauldron stage 4 ready but NOT chained" at 16:58Z (chain_cap 8) and did nothing about the
unlanded state. Root cause UNKNOWN: the run's record was not in `state.json`/`runs.json` when looked at, so it
fell out of tracking without a done. Neighbouring evidence: journal line at 16:50:29Z, "unit inactive, scope
inactive, its process check UNMEASURED; kept as running" (a different run, same tick window).

Fix wanted: (1) find the path where a role run leaves tracking without `role_done`; (2) the orphan sweep lands any
concept whose last result file is newer than origin's copy (`designer_stage.py land <dir>` is idempotent), so a lost
done never strands work again.


## verify

Acceptance test: a selftest that writes a done role record for a unit absent from the Dispatcher's running set,
with a dirty concept folder in a temp clone, runs one orphan-sweep tick, and asserts land_state was called once
(fails on base: the sweep only alarms chain_cap). Not yet written; the fixer writes it first.

## criteria

- A done role run whose unit left tracking without `role_done` gets its concept state landed within one Dispatcher tick.
- The selftest above passes; `seat_dirt.py report` reads stale 0 after a lost-done run.

## refs

file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/dispatcher.py
