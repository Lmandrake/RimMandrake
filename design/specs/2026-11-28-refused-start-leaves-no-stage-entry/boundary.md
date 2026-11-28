# BOUNDARY: a Designer stage run around its launch, Design Version 0.1.0

Code: the `role_launch` branch of `execute` in `src/RimMandrake/rimflow/dispatcher.py` (its stage open before
systemd-run and its drop after a launch that did not happen); `stage_open`, `stage_abort` and `stage_unopen` in
`src/RimMandrake/rimflow/role_launch.py`; `abort_run` and `unopen_run` in `src/RimMandrake/rimflow/designer_stage.py`.
This page covers only these parts of the files named. Item: `RIMMANDRAKE_FIX_ROLE_START_CHECK_RUNS_STALE_CLONE_CODE`,
written 2026-11-28. Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_designer_stage.py`.

## ACCEPTS (the only inputs this is built for)

- **a-designer-launch-with-a-concept.** A `role_launch` act of a stage-machine role that names a concept folder with a
  stage.json. The dispatcher opens the stage's run (`open_run`, commit) just before systemd-run, under the unit name
  that the launch uses. A unit name is used by one launch only (`rm-role-designer-<epoch>`).
- **a-launch-outcome.** `role_launch.launch` returns ok, or a refusal whose text starts `REFUSED by control:` (the
  control store refused it at admission or at the unit's start check), or starts `role_clones.MAKING` (the clone is
  being made), or another failure (systemd-run said no).

## DOES NOT SURVIVE (not promised)

- **a-concurrent-stage-write.** A write to the same stage.json by another program between the open and the drop is
  kept, but the drop reads and writes the whole file (`write_json`): a write that lands between that read and that
  write is lost. The window is one systemd-run call.
- **a-dispatcher-killed-between-open-and-drop.** The open run stays in stage.json; the next open charges it as a retry.

## PROMISES

- **a-refused-start-leaves-no-stage-entry.** A launch that the control store refused, at admission or at the unit's
  start check, leaves the concept's stage.json history as it was before the open: no `open` row and no `abort` row,
  no open run, nothing charged. What the open settled for an earlier run (a `retry` charge) stays. A launch that
  systemd-run itself refused still drops the open run uncharged and records an `abort` row. Added 2026-11-28: 22
  refused Designer starts on DirectSun left 44 rows in the Designer clone's stage.json. Tested by
  `t_a_refused_start_leaves_no_stage_entry`.
