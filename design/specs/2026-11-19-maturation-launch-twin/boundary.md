# BOUNDARY: maturation.py launch_mod's twin-run guard, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py` (`launch_mod`, `live_twins`, `_twins_reader`). **This page covers only the
guard that item `RIMMANDRAKE_GUARD_HAND_LAUNCH_AGAINST_DISPATCHER_TWIN_RUN` adds.** On 2026-11-16 a hand launch of
GimmeSomeSlack's blind cycle 6 ran beside the Dispatch step's launch of the same cycle: `launch_mod` checked only that
the cycle had no record yet, and a run that has just started has written none. The rest of `launch_mod` has no page
yet. Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_maturation_launch_twin.py`, each watched
failing on the base `c64672d310`.

## ACCEPTS (the only inputs this guard is built for)

- **one-record-per-detached-run.** `<RM_DISPATCHER_STATE>/detached/<unit>.json`, written by `detached_helper.py`
  before it starts the unit (status `launching`, then `running`, then an ended status). A run that `launch_mod`
  starts carries `RM_CONTROL_MOD` and `RM_CONTROL_STAGE` in the record's `env`.
- **a-run-is-live-by-its-unit.** `detached_helper.live_status` decides live: `launching` or `running` whose systemd
  unit is not inactive, failed or gone.

## DOES NOT SURVIVE (not handled)

- **two-launches-inside-one-record-write.** Two launches that both read the records before either one's
  `detached_helper.py launch` writes its `launching` record both go ahead. The window is the time between this read
  and that write (the brief write and one process start); the 2026-11-16 twin was a minute apart.
- **a-run-started-outside-launch-mod.** A detached run started by hand with `detached_helper.py launch` and no
  `RM_CONTROL_MOD` is a twin only when its item is the same item.
- **a-record-that-is-not-json.** A single record that cannot be read is skipped (`detached_helper.read_record`);
  only a folder that cannot be listed refuses.

## PROMISES (each one is owed a test of the same name)

- **launch-refuses-a-live-twin.** `launch_mod` refuses (2), before it writes a brief or launches, when a live detached
  run is on the same mod and stage, or on the same item; the refusal names the unit, its stage and its item.
- **launch-ignores-ended-and-other-runs.** A finished or dead run, or a live run on another mod or another stage with
  another item, refuses nothing. A mod with no live run reads `[]` (looked, none found).
- **launch-refuses-when-runs-unreadable.** When the detached-record folder cannot be listed, `live_twins` returns
  `None` with the cause, and `launch_mod` refuses (2) naming it: a twin that could not be ruled out is not "no twin".
- **live-twins-reads-the-records.** `live_twins(mod, stage, item)` reads every record in
  `<RM_DISPATCHER_STATE>/detached/` and returns the live ones whose `env` names the mod and stage, or whose `item` is
  the item.
- **stand-in-runner-reads-no-records.** A launch through a stand-in `runner` starts no unit, so it reads no records
  unless a `twins` reader is passed; the real `subprocess.run` reads `live_twins`. (The selftests that launch through
  a stand-in do not point `RM_DISPATCHER_STATE` at a temp folder, so the live records would make them depend on what
  runs today.)

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
