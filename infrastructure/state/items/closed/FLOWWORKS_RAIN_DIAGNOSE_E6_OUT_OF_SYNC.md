---
state: proposed
needs: offline
---

# FLOWWORKS_RAIN_DIAGNOSE_E6_OUT_OF_SYNC

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

SteveDesktop core_live_rows E6_rain_fills_unroofed FAILs 7x (10-28..10-31, latest 10-31T10:03Z, 0 passes since): rain leaves S4_band/S1_ladder/S1_deep/E6_open cells at 0 vs expected 1; earlier runs also 'pulse-0 vector != oracle (out of sync)'. Diagnose mod vs oracle. Evidence: findings_fold.md table, 7 findings FLOWWORKS_E6_RAIN_FILLS_UNROOFED_FAILS_*

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_RAIN_DIAGNOSE_E6_OUT_OF_SYNC` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_RAIN_DIAGNOSE_E6_OUT_OF_SYNC --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_RAIN_DIAGNOSE_E6_OUT_OF_SYNC` first: another commit may already do it.
