---
state: proposed
needs: offline
---

# FLOWWORKS_SELFTEST_FIX_FOUR_RED_AT_BASE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Four FlowWorks stock checks red, none from wrecked links: three stale source greps, one 50 ms timing bar

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_SELFTEST_FIX_FOUR_RED_AT_BASE` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_SELFTEST_FIX_FOUR_RED_AT_BASE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_SELFTEST_FIX_FOUR_RED_AT_BASE` first: another commit may already do it.
