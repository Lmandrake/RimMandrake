# BOUNDARY: a launch never starts a unit in a clone that cannot start one, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`clone_can_start`, the note in `_launch`). Item
`RIMMANDRAKE_GUARD_HELPER_LAUNCH_ON_MISSING_CLONE_TWO_RUNS_DIED_UNSTARTED`, written 2026-11-22. The ruling:
`design/RimMandrake/standing_rulings.md` §A fault of form is repaired where it is found. Each promise has a test of its
name in `src/RimMandrake/rimflow/selftest_detached_helper.py`.

Why: on 2026-11-22 two runs were launched with `--clone <path>` after the pool had taken that clone back. Each unit died
in one second (`FileNotFoundError: .../claude_bounded.sh` from spend_watchdog.py) while the launch printed DETACHED.

## ACCEPTS (the only inputs this is built for)

- **a-given-clone-path.** The `--clone` argument of `launch`: a path that is missing, or a directory with no
  `src/RimMandrake/Utils/claude_bounded.sh`.

## DOES NOT SURVIVE (not promised)

- **a-clone-with-the-script-but-otherwise-broken.** A clone that holds claude_bounded.sh is taken as given.

## PROMISES (each one is owed a test of the same name)

- **a-launch-on-a-missing-clone-takes-a-pool-clone-instead.** When `--clone` names a path that cannot start a unit, the
  launch takes the pool clone for the item, as a launch without `--clone` does, never creates the given path, and ends
  its text with one `NOTE (form, repaired): ` line that names the given path. Red on the base: DETACHED for a unit that
  dies unstarted.
