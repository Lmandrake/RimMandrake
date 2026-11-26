# Boundary: a mod ledger follows its Design Version's bars and its set-aside evidence

Code: `sync_bars` in `src/RimMandrake/rimflow/modledger_backfill.py` (and its `bars` verb); `reduce` (its `bar.*` and
`live.run` branches) and `cited_file_exists` in `src/RimMandrake/rimflow/modledger.py`; `lock_bars` and
`ledger_bars_sync` in `src/RimMandrake/rimflow/maturation.py`. Tests: each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_modledger_version_bars.py`. Item: `RIMMANDRAKE_REPAIR_KNOCKBACK_LEDGER_READINESS_STOPS_TICK_HOLDER`.

The failure, 2026-11-25 at 4:20 PM PST: Explosive Knockback's readiness test (`acceptance/modledger_backfill_accept.py`)
failed 2 of 7, so `pilot_ledger` refused the mod and the tick launched no holder on its road back. Two causes:

- `maturation.py lock-bars` wrote 0.2.0's 73 ids to `version/locked_bars.json`. Nothing wrote the 14 new ids to the mod
  ledger, which still held 0.1.0's 59 bars. FlowWorks had the same drift inside one version (his card moved 3 bars to
  0.2.0 and added 1: ledger 57, record 55). In Gimme Some Slack, `lock-bars --add` locked 59 bars and VERSION.json
  `bars_total` still read 57.
- `maturation.py next-version` moved 0.1.0's numbered evidence into `version/previous/0.1.0/`. 105 BACKFILL events cite
  the old paths.

## How the ledger learns a lock (the choice)

`version/locked_bars.json` stays the one record of a version's bars, and `lock_bars` stays its one writer. Each write of
that record also brings the mod ledger level with it, as BACKFILL events that cite the record. The ledger's events are
append-only, so the cited paths are not rewritten: the reader of a citation also looks in `version/previous/*/`.

## ACCEPTS (the only inputs this is built for)

- **a-lock-record.** `version/locked_bars.json` as `lock_bars` writes it: `version`, `ids` (a list of bar ids),
  `history` (each entry with `at`).
- **a-mod-ledger.** The shards of `design/concepts/<Mod>/ledger/`, read by `modledger.read`.
- **a-cited-path.** An event's evidence ref: `path:<repo path>`, with an optional `#locator` or `:line`.

## DOES NOT SURVIVE (not promised)

- **a-lock-written-by-hand.** A `locked_bars.json` written without `lock_bars` reaches the ledger only when someone runs
  `modledger_backfill.py bars --mod <Mod>`.
- **a-bar-renamed-in-place.** A renamed bar is one bar deferred and one bar locked. The ledger keeps no link between the
  two names.
- **two-previous-versions-holding-the-same-path.** A set-aside path resolves when any `version/previous/<v>/` holds it.
  The resolver does not check that `<v>` is the event's own version.

## LIMITS

None.

## PROMISES (each one is owed a test of the same name)

- **a-deferred-bar-leaves-the-version.** In `reduce`, a bar whose last bar event is `bar.deferred` leaves `bars` and is
  kept in `bars_deferred`. A later `bar.locked` or `bar.added` brings it back. A `live.run` on a deferred bar sets its
  verdict there and does not bring it back. A ledger with no deferred bar has no `bars_deferred` key, so its views read
  byte for byte as before.
- **a-set-aside-citation-resolves.** `cited_file_exists` finds a `design/concepts/<Mod>/version/<rest>` path that is
  missing at that path in `version/previous/<v>/<rest>`. A path missing from both places stays missing. A path outside a
  mod's `version/` folder is never looked up in `previous/`.
- **sync-bars-levels-the-ledger-with-the-lock.** `sync_bars` appends a BACKFILL `bar.locked` for each id of the record
  that the ledger lacks, and a `bar.deferred` for each ledger bar that the record does not hold. Each event cites the
  record. It says which ids it locked and deferred. A second run writes nothing. A bar that a later record locks again
  comes back.
- **sync-bars-writes-nothing-it-cannot-read.** A mod with no ledger returns None. A record that is absent, cannot be
  parsed, or names a version other than the ledger's: nothing is written, and the result is not ok and says why.
- **lock-bars-syncs-the-ledger.** `lock_bars` syncs the mod ledger after it writes the record, and returns the sync's
  result as `ledger` (None for a mod with no ledger). A ledger that does not take the record never rolls the lock back.
  The CLI prints `LEDGER NOT LEVEL` and exits 3.
- **lock-bars-keeps-bars-total-level.** When VERSION.json holds an integer `bars_total` that differs from the number of
  recorded ids, `lock_bars` sets it to that number, names the record in `measured_from.bars_total`, and returns
  `bars_total` {was, now}. A count that is already level is not rewritten.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
