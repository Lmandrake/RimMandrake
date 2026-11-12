---
state: proposed
needs: offline
---

# SELFTEST_FIX_FLOWWORKS_STOCK_ELFQ

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Ops alarm NIGHTLY_RED: 1 red since 2026-11-06, due 2026-11-09T11:00: G# locator: turn across the blend (outward vs heading after it) median NaN deg failing vs #

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show SELFTEST_FIX_FLOWWORKS_STOCK_ELFQ` history before building.

## latest ledger notes

- 2026-11-06: ops_watch: new at 2026-11-06T19:20:58Z: src/RimMandrake/Utils/selftest_flowworks_stock.py (due 2026-11-09T11:00:00Z)

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify SELFTEST_FIX_FLOWWORKS_STOCK_ELFQ --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=SELFTEST_FIX_FLOWWORKS_STOCK_ELFQ` first: another commit may already do it.
