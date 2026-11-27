# BOUNDARY: the tick keeps its own clone level, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_dispatch.py`, the functions `sync_clone`, `seat_sync`,
`unlanded_ledger_mods`, and the not-a-prefix retry in `land_ledger`. Tests:
`src/RimMandrake/rimflow/selftest_dispatch_clone_sync.py` (real git against a local bare origin, with the real
`land.sh` and `seat_sync.py`). Item: `RIMMANDRAKE_UNSTICK_TICK_CLONE_TWO_LINES_BLOCK_EVERY_PULL`.

The tick's clone is `/home/mandrake/rm/dispatch`. Every pipeline timer runs from that clone. Before this page, two
routes moved it: the `git pull --ff-only` in `testq-tick.service`'s ExecStartPre, and the `seat_sync.py` that
`land.sh` runs after each landing from the clone. The ff-only pull refuses when a dirty file is also changed by an
incoming commit. So a DISPATCH line that a landing left behind blocked the pull each time origin appended to the same
shard, and the clone moved only when some other landing from it happened to run.

## ACCEPTS (the only inputs this is built for)

- **one-tick-at-a-time.** The applying tick runs under its state lock, so no second tick appends to the clone's
  DISPATCH shards while `sync_clone` runs. Other writers in the clone (ops_watch, ingest) land their own ledger shards
  through `land.sh`. `seat_sync` carries each dirty shard under a flock on that file, so an append that runs at the
  same time lands before or after the carry and is not lost.
- **shards-are-append-only.** `design/concepts/*/ledger/*.jsonl` is `merge=union` in `.gitattributes`, and every
  writer only appends. The views (`ledger/views/**`) are derived (`rm-derived`): a dirty view takes origin's bytes.

## DOES NOT SURVIVE (not handled)

- **a-real-overlap.** A dirty file that is not an append and that origin also changed: `seat_sync` refuses, says so,
  and the clone stays behind. The reading's `clone_sync` names the refusal, the journal prints it, and the
  `OPS_DISPATCH_CLONE_BEHIND_UNSTICK` alarm fires after 15 minutes.
- **a-landing-that-always-refuses.** A landing that origin refuses every time (a lint) is tried again on each tick, and
  each try says why in the reading. Nothing stops the retries.

## PROMISES (each one is owed a test of the same name)

- **land-ledger-lands-beside-a-peer-append.** A peer clone appended to a mod's DISPATCH shard on origin, and the tick's
  clone appended a line of its own without the peer's line. `land_ledger` brings the clone level (`seat_sync`), then
  lands. Both lines are on origin, and the clone is level with origin/main and clean after.
- **sync-clone-lands-unlanded-lines-and-moves.** The clone holds a DISPATCH line that no landing carried, and origin
  appended another line to the same file, so `git pull --ff-only` refuses. `sync_clone` keeps both lines in the clone,
  lands the clone's line, and leaves the clone level with origin/main and clean.
- **sync-clone-moves-past-a-dirty-view.** Nothing is unlanded, but a derived view in the clone is dirty and origin
  rewrites it, so `git pull --ff-only` refuses. `sync_clone` still moves the clone level with origin/main.

- **sync-clone-holds-before-it-fetches.** Before its `seat_sync` fetches, `sync_clone` writes `gc.auto=0` and
  `maintenance.auto=false` into the clone's own config (`clone_pack.hold`), so no git command of the tick starts
  git's automatic packing inside the tick's 1 GB unit. The packing runs in `rm-clone-pack.timer`
  (`design/specs/2026-11-27-timer-clone-packing/boundary.md`).

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
