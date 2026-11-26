# Work bundle WB-mod-ExplosiveKnockback-20261126-011752 (mod:ExplosiveKnockback)

Updated 2026-11-25 PST. One member, one group (the ledger readiness repair).

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
