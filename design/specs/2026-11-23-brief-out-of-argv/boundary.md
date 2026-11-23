# BOUNDARY: a detached run's brief never rides in its processes' argv, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`_launch`, the brief file; `launch_argv`, `StandardInput=file:`).
Item `RIMMANDRAKE_STOP_KILLING_WORKING_JUDGE_AT_FORTY_FIVE_MIN`, written 2026-11-23. Each promise has a test of its name
in `src/RimMandrake/rimflow/selftest_detached_helper.py`.

Why: on 2026-11-23 at 5:10:34 AM PST the ExplosiveKnockback blind-cycle-6 judge ran
`kill -TERM $(pgrep -f 'lane2/plant_faults[.]py' | head -1)` to stop its own background job. Its brief named
`lane2/plant_faults.py`, and a brief under 100 KB went in as the `-p` argument, so it was in the argv of
`spend_watchdog.py` (the unit's main process), `claude_bounded.sh` and `claude`. pgrep matched `spend_watchdog.py`
(pid 3707891) first. The main process died of SIGTERM. `claude_bounded.sh` traps TERM, so the unit stayed in
`stop-sigterm` for its `TimeoutStopSec=600`, and at 5:20:35 AM systemd killed the judge while it worked. Spend:
UNMEASURED (empty result file).

## ACCEPTS (the only inputs this is built for)

- **a-launch-brief.** The brief that `detached_helper.py launch` (or `launch()` from Python) is given, of any length,
  with the footer that `_launch` adds.

## DOES NOT SURVIVE (not promised)

- **a-pattern-that-matches-the-run-name-or-item.** The argv still holds the item id (`--name DETACHED <SEAT> <ITEM>`),
  the clone path and the unit name. A `pgrep -f` on one of those still matches the run's own wrappers.
- **role-launches.** `role_launch.launch_argv` (rm-role-* units) still passes its brief as `-p`. No run of that kind was
  killed this way.

## PROMISES (each one is owed a test of the same name)

- **a-brief-never-rides-in-a-wrappers-argv.** A brief of any length goes to claude by file on stdin
  (`StandardInput=file:<state>/detached/<unit>.brief.md`). No argument of the systemd-run argv holds a phrase of it.
  Red on the base: a short brief went in as the `-p` argument.

## LIMITS

- none new. `ARG_BRIEF_MAX` stays as the bound that no launch argument may reach (Linux `MAX_ARG_STRLEN`, E2BIG,
  measured 2026-11-16).

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
