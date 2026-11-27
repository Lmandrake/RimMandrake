# BOUNDARY: DefDump db tick

Code: `src/RimMandrake/Utils/defdump_db_tick.py`, run by `src/RimMandrake/Utils/systemd/rm-defdump-db.timer`.
Item: `SELFTEST_UNMEASURED_FOUR_REBUILD_DEFDUMP_DB`. Tests: `src/RimMandrake/Utils/selftest_defdump_db_tick.py`.

## WHY

`defs.sqlite` is derived from the newest DefDump capture. Each game load with RimDefDump writes a new capture, and the
producer keeps the newest three. Nothing rebuilt the db after a capture. So every reader that goes through
`dump_manifest.dump_db` read the db as stale and answered UNMEASURED. Measured 2026-11-26: the db was built from capture
2026-11-12T08-10-06Z, which was pruned; four newer captures existed; `ecosystem_pyramid_check` and
`label_collision_check` read UNMEASURED. One `measure build` took 28.7 s and 173 MB, and both checks then measured. A
newer capture landed one hour later, and the db read stale again.

## ACCEPTS

`tick` looks once at the live dump root (`game_paths.DUMP_ROOT`). When the db is absent or stale against the newest
capture, it runs `measure build` once. It writes one reading. `check` answers whether the db is kept current. `show`
prints the last reading. `--root` and `RM_DEFDUMP_DB_DIR` (where the reading goes) exist for tests.

## LIMITS

- **A build is cut at 900 s.** The danger is a hung build that holds the timer for good (systemd starts no second run).
  Measured 2026-11-26: two builds, 28.7 s and 68.7 s wall (the second was the first tick). 900 s is more than ten
  times the longer.
- **A reading is fresh for 7200 s.** The danger is a dead timer that reads alive. The timer beats each 30 minutes. Ends no
  work: `check` answers 1.
- **A stale db is allowed for 7200 s after its newest capture.** The danger is a false red in the gap between a capture
  and the next tick. Ends no work: `check` answers 1 past it.

## PROMISES

- **a-stale-db-is-rebuilt.** A db that is absent, or stale against the newest capture, is rebuilt by one `measure build`
  in the same tick. The reading names the capture it was built from.
- **a-current-db-is-left-alone.** A db that is current is not rebuilt.
- **no-capture-builds-nothing.** A dump root with no capture builds nothing, and the reading says so.
- **a-failed-build-is-named.** A build that exits non-zero, prints no `MEASURED` line, or is cut by its limit writes its
  cause in the reading, and `tick` exits 1. The old db stays (the build swaps the db in atomically).
- **check-tells-the-cases-apart.** Exit 0: the reading is fresh and the db is current, or stale for less than the
  grace. Exit 1: no reading, a stale reading, an absent db, or a db stale past the grace; the line names which. Exit 2:
  the dump root, the measure skill or the reading cannot be read.

## DOES NOT SURVIVE

- **a-capture-from-another-mod-set.** The tick builds from the newest capture, whatever mod list made it. A capture from a
  list without the defs a checker reads makes that checker read UNMEASURED with its own cause.
- **a-game-load-that-writes-no-capture.** The db then stays built from the newest capture that exists, which is current
  by the producer's own rule.
