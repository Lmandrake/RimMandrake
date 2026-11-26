# RIMMANDRAKE_TRACE_DESIGNER_TWIN_COMMIT_LAND_SAID_LEVEL

## spec

Measured Sat 2026-11-21 5:59 AM PST (incident `work_belt-20261121132228`, `disk.seat_dirt` = 3).

The Designer role clone `/home/mandrake/rm/roles/Designer` was ahead 1 and behind 82 of origin/main.

- The local commit `36562a6e2a` ("ledger: BENCH role run (role clone Designer)") came from the 03:22 PST land unit
  `rm-role-designer-1795260155-land`. That unit's JSON said `shard: PUBLISHED 175293dc5f`, `level: level`, `ok: true`.
  The 3 BENCH lines of the commit were already on origin (a twin).
- Staged in the clone: 5 DISPATCHER lines and 1 RUNNER line (all on origin), and
  `design/concepts/Pyrelands/stage.json` (MM; row for row equal to origin, 313 rows).
- Later land units (for example `rm-role-designer-1795262630-land` at 04:04 PST) also said `level` and `ok` while
  HEAD was ahead.

Repair by hand: `git restore` of the 3 twin paths, then `seat_sync.py --superseded 36562a6e2a` (SYNCED to
`dee81d290`; backup branch `backup/Designer-pre-sync-20261121_055936-36562a6`).

The fix is unknown. Two questions stay open:

1. Why did `./publish` leave the local commit in place after it printed PUBLISHED?
2. Why did `role_clones.level()` read `level` while HEAD was ahead of origin/main?

Component: `src/RimMandrake/rimflow/role_clones.py` (`land`, `level`).

## verify

`python3 src/RimMandrake/Utils/seat_dirt.py report --clone /home/mandrake/rm/roles/Designer` reads `stale: 0` after
each Designer run, and `git -C /home/mandrake/rm/roles/Designer rev-list origin/main..HEAD` is empty after its land
unit ends.

## criteria

Acceptance test: none, the cause is not yet reproduced. The oracle to write: a `land()` run on a clone where
`./publish` lands a cherry-picked twin and leaves the local commit. That run must not report `level`, and must level
the clone or report `stranded` with its fix line.

## refs

file: src/RimMandrake/rimflow/role_clones.py
