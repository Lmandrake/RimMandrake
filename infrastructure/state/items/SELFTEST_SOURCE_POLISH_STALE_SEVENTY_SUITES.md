---
state: proposed
needs: deploy
---

# SELFTEST_SOURCE_POLISH_STALE_SEVENTY_SUITES

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

SelfTest source tidy (C#, needs a rebuild with a .srchash): Program.cs header says ~70 suites (about 110 run); dead locals pumped/tank/held in Liquid_unit_contract_roundtrip_conserves; HoseSelfTest.cs lines 643-648 orphan HOSE_ENDS_FIX doc comment attached to nothing

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show SELFTEST_SOURCE_POLISH_STALE_SEVENTY_SUITES` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify SELFTEST_SOURCE_POLISH_STALE_SEVENTY_SUITES --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=SELFTEST_SOURCE_POLISH_STALE_SEVENTY_SUITES` first: another commit may already do it.
