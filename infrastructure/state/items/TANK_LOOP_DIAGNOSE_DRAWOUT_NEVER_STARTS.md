---
state: proposed
needs: bridge
---

# TANK_LOOP_DIAGNOSE_DRAWOUT_NEVER_STARTS

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks toggle_tank_loop/tank_loop_on: a Store tank of 120000 fresh water never drawn down (WorkGiver_FillBottleFromTank never ran)

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show TANK_LOOP_DIAGNOSE_DRAWOUT_NEVER_STARTS` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify TANK_LOOP_DIAGNOSE_DRAWOUT_NEVER_STARTS --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=TANK_LOOP_DIAGNOSE_DRAWOUT_NEVER_STARTS` first: another commit may already do it.
