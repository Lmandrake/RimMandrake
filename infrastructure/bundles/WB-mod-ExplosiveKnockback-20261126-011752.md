# Work bundle WB-mod-ExplosiveKnockback-20261126-011752 (mod:ExplosiveKnockback)

Updated 2026-11-25 6:25 PM PST. One member, one group (the ledger readiness repair). Done.

## Classes
| ticket | class | evidence |
|---|---|---|
| RIMMANDRAKE_REPAIR_KNOCKBACK_LEDGER_READINESS_STOPS_TICK_HOLDER | REAL (pipeline) | `modledger_backfill_accept.py ExplosiveKnockback` FAIL 2 of 7 on e04ed7fe07: 59 bars against 73; 105 BACKFILL events cite 0.1.0 paths that next-version set aside in `version/previous/0.1.0/` |

## Causes (measured)
- `maturation.py lock-bars` writes `version/locked_bars.json` and never the mod ledger: Explosive Knockback 0.2.0's 14 new bars stayed out. The same cause hit FlowWorks (57 against 55: his card moved 3 bars, added 1) and Gimme Some Slack (11 bars missing; its VERSION.json `bars_total` read 57 against the 59 locked).
- The ledger's cited paths are append-only; `next-version` moves the evidence they cite.

## Fix
- `modledger_backfill.sync_bars` (verb `bars`): BACKFILL `bar.locked` / `bar.deferred` that cite locked_bars.json; `lock_bars` calls it and keeps VERSION.json `bars_total` level.
- `reduce`: a deferred bar leaves `bars` (`bars_deferred`, key present only when one is deferred).
- `cited_file_exists`: a `version/` path also resolves in `version/previous/<v>/`.
- Page `design/specs/2026-11-25-ledger-follows-version-bars/boundary.md`, test `selftest_modledger_version_bars.py` (6 of 6 promises; red on the parent, red on each planted fault).
- Explosive Knockback's ledger synced: 14 bars locked; acceptance PASS 7/7.

## Polish
- The brief's 20 polish lines of `design/concepts/ExplosiveKnockback/version/polish.md` name mod files that this run did not change: none taken.
- Polish lines beside `maturation.py`'s other pages (raid pause, live kinds) name functions this run did not touch and that its tests do not cover: left.

## Landed
- Code, page, test, `maturation_advance` recalibrated alone: 47f3903c84 (218 pipeline checks green).
- Explosive Knockback ledger: 17c7d84297. Readiness PASS 7/7 on origin/main; `pilot_refusal` reads "ready". Run recorded 3cca8b5020.
- FlowWorks ledger (+1 locked, 3 deferred): readiness 7/7. Gimme Some Slack ledger (+11 locked): 59 = its lock, 5ab3125787.
- Filed: RIMMANDRAKE_SETTLE_SLACK_PASSED_WITH_TWO_LOCKED_BARS_UNTABLED (its test table and bars_total read 57, its lock 59), 01c56d4fcf.

## Fresh reader
- One Opus reader: nothing significant. Its nits, done in this run: an eased deferred bar stays deferred; `_status_of` reads a deferred bar; the packet lists deferred ids; `sync_bars` writes views also after a partial append; the `bars` verb says a ledger refusal; `bars_total` provenance written when `measured_from` is absent.
- Left: a rewrite of a VERSION.json not in indent 1 (FlowWorks) reformats the whole file. The diff is noisy, and no data is lost.
