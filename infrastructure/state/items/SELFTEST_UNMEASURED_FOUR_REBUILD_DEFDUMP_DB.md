## spec
Four selftests read UNMEASURED on 2026-10-27 because the live DefDump's `defs.sqlite` was absent or stale, and the dump
was blind to xenotypeSets. Measured 2026-11-26: `selftest_mandrakepatches.py` and `selftest_xenotype_cut_spawnsets.py`
pass; `selftest_ecosystem_pyramid_check.py` and `selftest_label_collision_check.py` read UNMEASURED, because the db was
built from capture 2026-11-12T08-10-06Z (pruned) and four newer captures existed. The cause: each game load with
RimDefDump writes a new capture, and nothing rebuilt the db after it. No game is needed: the db is derived from a
capture that is already on disk (`measure build`, 28.7 s).

The repair: rebuild the db now, and add `rm-defdump-db.timer` (`src/RimMandrake/Utils/defdump_db_tick.py`, page
`design/specs/2026-11-26-defdump-db-tick/boundary.md`), which rebuilds the db when it is stale against the newest
capture.

## criteria
- The four selftests exit 0 (they measure).
- `python3 src/RimMandrake/Utils/defdump_db_tick.py check` exits 0: the timer runs and the db is current with the newest
  capture, or stale for less than the grace.

## verify
`python3 src/RimMandrake/rimflow/list_shape.py holds SELFTEST_UNMEASURED_FOUR_REBUILD_DEFDUMP_DB` (the two shaped parts).

## refs
new: src/RimMandrake/Utils/defdump_db_tick.py
new: src/RimMandrake/Utils/systemd/rm-defdump-db.timer
file: src/RimMandrake/Utils/systemd/ops_clocks.json
