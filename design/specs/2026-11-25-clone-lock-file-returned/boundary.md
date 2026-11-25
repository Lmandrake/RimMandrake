# BOUNDARY: a returned pool clone takes its lock file with it, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`clone_lock`, `drop_clone_lock`, the lock step in `return_clone`).
Item `RIMMANDRAKE_CLEAN_STALE_LOCKS_AND_LEFTOVERS_OF_RETIRED_ERAS`, written 2026-11-25. Each promise has a test of its
name in `src/RimMandrake/rimflow/selftest_detached_helper.py`.

Why: every detached launch locks `<pool>/clones/<ITEM>.det.lock`, and nothing removed that file. On 2026-11-25 the
Archmagi pool held 915 lock files with no clone beside them. A reader took them as the locks of live runs.

## ACCEPTS (the only inputs this is built for)

- **a-pool-clone-lock-file.** `<clone>.lock`, made by `clone_lock`: absent, free, or held by a launch.

## DOES NOT SURVIVE (not promised)

- **a-lock-file-on-a-filesystem-without-flock.** On a mount where `flock` does nothing, two launches can both hold it.
- **lock-files-left-before-this-change.** They stay until a sweep removes them.

## PROMISES (each one is owed a test of the same name)

- **a-returned-clone-takes-its-lock-file-with-it.** A return that gives the clone back (bundled, parked or removed)
  removes `<clone>.lock`. A return that keeps the clone keeps it. A lock file that a launch holds is never removed.
  A lock file that is already gone is a removal, not a failure. Red on the base: the lock file stays.
- **a-launch-never-holds-an-unlinked-lock-file.** When the lock file was unlinked while a launch waited on it, the
  launch lets that file go and takes the lock on the file that stands at the path now. Red on a mutant that skips the
  inode check.
