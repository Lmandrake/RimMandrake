# BOUNDARY: an apply run of the scratch reap waits out a dry run that holds its lock, Design Version 0.1.0

Code: `take_lock` and `release_lock` in `src/RimMandrake/Utils/scratch_reap.py`, called from its `main`. Item:
`LIVE_RESTORE_RM_SCRATCH_REAP`, written Fri 2026-11-27. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_scratch_reap_lock_wait.py`.

## Why

On Archmagi on 2026-11-27 a helper ran two dry runs of `scratch_reap.py` by hand, 6:47 to 6:54 PM and 6:59 to 7:05 PM
PST (`runs.jsonl` rows with `apply: false`). The 7:03 PM run of `rm-scratch-reap.service` found `run.lock` held,
printed "another reaper run holds the lock" and exited 0. A dry run writes `last_dry_run.json`, never `last_run.json`.
So `last_run.json` stayed at the 6:24 PM run until the 8:00 PM run ended, and three live promises on that reading
(2 h line) broke at 8:33 PM.

## The design

- The holder of `run.lock` writes its mode and pid into the file (`apply <pid>` or `dry <pid>`), and erases them when
  it ends. A contender opens the file without truncating it, so it reads the holder's name.
- An apply run that finds a dry run holding the lock waits for the lock, then runs. An apply run stands down for an
  apply run. A dry run stands down for any run. A holder that names no mode is read as an apply run.
- systemd starts no second run of the unit while one waits, so at most one timer run waits.

## The danger the limits guard

- **No new limit.** The wait has no bound of its own. A hung dry run makes the apply run wait until the unit's
  `TimeoutStartSec` (39,600 s, its danger named in the unit file) ends it. Meanwhile `last_run.json` ages and the live
  promises alarm, as for a hung apply run.
- **`QUICK_S` (120 s) in the selftest** is a hang guard. An empty-fixture run takes about 2 s.

## ACCEPTS (the only inputs this is built for)

- **a-run-of-the-reaper.** `scratch_reap.py` with or without `--apply`, on one state dir (`SCRATCH_REAP_STATE`, default
  `~/.local/state/rm-scratch-reap`).

## DOES NOT SURVIVE (not promised)

- **a-holder-in-its-first-instant.** Between its `flock` and the write of its name, a holder reads as the run before it
  (or as unnamed). A contender then stands down or waits by that reading. The window is microseconds.
- **an-older-reaper-holding-the-lock.** A reaper from before this page names no mode, so an apply run stands down for it.

## PROMISES (each one is owed a test of the same name)

- **an-apply-run-waits-out-a-dry-run.** While a dry run holds the lock, an apply run waits; when the dry run ends, the
  apply run runs and writes `last_run.json`.
- **an-apply-run-stands-down-for-an-apply-run.** It exits 0 at once and writes no record.
- **a-dry-run-stands-down-for-any-run.** Held by an apply run or a dry run, a dry run exits 0 at once.
- **an-unnamed-holder-reads-as-an-apply-run.** An apply run stands down for a holder that names no mode.
- **the-holder-names-itself-until-it-ends.** The holder writes `<mode> <pid>`, a contender's open leaves it in place,
  and the name is gone when the holder ends.
