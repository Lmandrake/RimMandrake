# BOUNDARY: the pager's triggers (`pager_triggers.py`), Design Version 0.1.0

Code: `src/RimMandrake/Utils/pager_triggers.py`. Design: `design.md` §8 beside this page. The pager itself: `boundary.md`.
Each promise has a test of its own name in `src/RimMandrake/Utils/selftest_pager_triggers.py`; `--plants` there plants
the faults that the tests must catch.

## ACCEPTS (the only inputs the triggers are built for)

- **readings.** Under the RM data root: `ops_watch/status.json` (points with `v`, `m`, `x.observed_at`),
  `testq/fault_state.json` (`at`, `phase`), `switching_plan/state.json` (`stopped`), `switching_plan/markers/*.json`
  (`at` with a zone, `phase`).
- **callers.** `status` from anyone. `run` from the Conductor window or an Operations run (`pager.send` decides).
  `on` and `off` from the Conductor window.

## PROMISES

- **each-trigger-fires-on-its-line.** Each of the seven triggers is CLEAR on a quiet estate and FIRES on its line in
  `design.md` §8. A failed switch is CLEAR after a later good switch, or when the plan has not retried it for 6 h.
- **could-not-look-is-never-clear.** A missing, torn, wrong-shaped, stale (over 45 min) or unmeasured reading is
  COULD_NOT_LOOK. It never pages and never reads CLEAR. A PASSIVE fault monitor is COULD_NOT_LOOK: it never sets STUCK.
- **off-until-switched-on.** With no switch file, `run` reads nothing, pages nothing and exits 4. `run` pages only for a
  trigger that is ON.
- **only-the-conductor-switches.** `on` and `off` refuse every caller but the Conductor window, an unknown trigger, and a
  why under four words. Each switch is a Conductor log line.
- **torn-switch-file-is-not-all-off.** A switch file that cannot be read exits 3, reads nothing and pages nothing.
- **run-exits-tell-outcomes-apart.** 0 all read, and each page needed was sent or a repeat; 1 a needed page did not
  leave; 3 an ON trigger could not be read; 4 none is on; 5 the tool broke.
- **a-fired-page-passes-the-pager.** Every trigger's class, cause, reading and why passes `pager.py`'s own checks.

## DOES NOT SURVIVE (not promised)

- **nobody-runs-it.** The triggers page only when an Operations run or the Conductor window calls `run`. While the fleet
  is stopped neither can run, so `fleet_stop` does not ring at the time of the stop.
- **between-runs.** A fault that starts and ends between two runs does not page.
- **state-json-without-a-time.** `switching_plan/state.json` has no write time of its own; a dead switching plan leaves
  its last answer.

## LIMITS (each with the danger it guards)

- **MAX_AGE_MIN 45**: a frozen `ops_watch` reads CLEAR for hours, or pages for a fault that ended. The same line as
  `alarm_routes.json` `status_max_age_min`.
- **FAILED_FRESH_H 6**: a one-time failed switch that a reset made moot pages him for days. The plan writes the marker's
  time again at each retry, so a failure that lasts stays fresh.
- **DISK_FLOOR_GB 50**: `design.md` §8.
