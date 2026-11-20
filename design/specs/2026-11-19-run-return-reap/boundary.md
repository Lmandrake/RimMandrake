# BOUNDARY: a run's clone at its return and its reuse, Design Version 0.1.0

Code: `detached_helper.reap_leftovers` and its call in `detached_helper.return_clone`
(`src/RimMandrake/rimflow/detached_helper.py`); the marker scan is `role_launch.scan_marked`. Item:
`RIMMANDRAKE_REAP_SELFTEST_CHILD_ENDED_RUN_LEFT_HOLDING_CLONE`, written 2026-11-19. Twice on 2026-11-18 (5:18 PM and
6:55 PM PST) a detached run ended while a selftest it started (`run_selftests.py --_harness-child`,
`selftest_second_game_mutants.py`) still ran. `run_selftests.py` puts each test in its own scope in `rm-harness.slice`,
outside the run's cgroup, so finish's `stop_scope` did not reach it; the return step then kept the clone ("a process
is working in it") and the next launch on the item was refused until a person killed the child. Every process of a
run inherits `RM_ROLE_UNIT=<unit>` from its unit, whatever cgroup it lands in. The run's brief already says that a
command still running when the run ends is killed. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_detached_reap.py`.

## ACCEPTS (the only inputs this is built for)

- **a-finished-run-record.** A record with `status` finished, `unit`, `at` and a pool clone it owns (`owns_clone`).
- **marked-processes.** Processes of this uid whose environ holds `RM_ROLE_UNIT=<unit>` exactly.

## DOES NOT SURVIVE (not promised)

- **a-child-that-cleared-its-environment.** A process started with an empty or rewritten environment carries no
  marker; it is not reaped, and the clone is kept as before when its cwd is inside.
- **a-windows-process.** A Windows process the run started (python.exe, RimWorld) is not in /proc and is not touched.

## PROMISES (each one is owed a test of the same name)

- **a-leftover-child-is-ended-and-the-clone-returned.** A finished run whose marked child still runs with its cwd in
  the clone: the return step ends the child (TERM, then KILL) and gives the clone back; its steps name the pids.
- **an-unmarked-process-in-the-clone-keeps-it.** A process in the clone that does not carry the run's marker is never
  signalled, and the clone is kept with "a process is working in it".
- **another-units-marker-is-not-this-runs.** A process marked with another unit (a prefix of this unit's name or one
  that starts with it) is never signalled.
- **a-blind-scan-kills-nothing.** When the marker scan is blind, nothing is signalled, the step says the scan was blind
  and why, and the busy check decides as before.

- **a-reused-det-clone-takes-the-seat-identity.** `take_clone` on a standing `<ITEM>.det` clone gives it the seat clone's
  repo-local `user.email` (`scratch_clone.set_identity`), as a newly made clone gets
  (`RIMMANDRAKE_SET_HELPER_CLONE_NOREPLY_GMAIL_SLIPS_ONTO_PUBLIC`: RimMandrake is public).
- **role-launch-scan-rules-out-zombies.** `role_launch.scan_marked` rules out a process whose `/proc/<pid>/stat` state
  is `Z` (a zombie: its environ is never readable and it runs nothing) or that exited, as it rules out another uid's.
  A same-uid live process whose environ cannot be read, or whose state cannot be read, still makes the scan blind
  (`RIMMANDRAKE_SKIP_ZOMBIES_IN_MARKER_SCAN_ONE_DEFUNCT_BLINDS`: one `[python3] <defunct>` blinded every scan,
  2026-11-19).

Later lists beside this page: `polish.md` (none yet).
