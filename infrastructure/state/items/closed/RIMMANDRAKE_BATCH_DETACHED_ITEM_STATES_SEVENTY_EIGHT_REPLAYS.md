# RIMMANDRAKE_BATCH_DETACHED_ITEM_STATES_SEVENTY_EIGHT_REPLAYS

## spec

`rm-running.service` (the RELENTLESS_NOW page, every minute, `TimeoutStartSec=90`) timed out on every run from about
13:15 PST 2026-11-16 (journal: 76 `Failed with result 'timeout'` from 13:00 to 15:10), which opened incident
timers-20261116223622 (`timers.failed_units`). Profiled 15:13 PST: 151 s per run, 140 s of it in
`fleet_mods.detached_done`, which ran `python3 src/RimMandrake/rimflow/cli.py show <item>` (a full ledger replay, about
1.8 s) once per finished detached helper since local midnight (78 rows). The cost grows with the day's helper count
and crossed 90 s in the early afternoon.

Fix: the default item-state reader in `detached_done` replays the ledger once per call (`_ledger_states`, lazily, only
when a row needs it) and looks each item up in that one table.

## verify

`python3 src/RimMandrake/Utils/selftest_fleet_mods.py` ends `ALL PASS`; its check "detached_done: default item states
come from one ledger replay, no per-item subprocess" FAILED on base dc4b56f7ec (watched) and passes with the fix.
Live: `fleet_mods.detached_done(24)` over 139 rows took 12.1 s and `gather` 3.6 s (was 140 s), measured 15:16 PST.

## criteria

Acceptance test: `python3 src/RimMandrake/Utils/selftest_fleet_mods.py` exits 0 with every line PASS (it was 1 FAIL
on the base). Live: `systemctl --user --failed` lists no `rm-running.service` once the dispatch checkout carries
the fix.
