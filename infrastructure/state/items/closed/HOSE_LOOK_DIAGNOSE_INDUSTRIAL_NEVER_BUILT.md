---
state: proposed
needs: bridge
---

# HOSE_LOOK_DIAGNOSE_INDUSTRIAL_NEVER_BUILT

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks hose R2/R3/R5/R6: the Industrial-look reel at (117,120) never became a building, so four look rows fail on one missing reel

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show HOSE_LOOK_DIAGNOSE_INDUSTRIAL_NEVER_BUILT` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_LOOK_DIAGNOSE_INDUSTRIAL_NEVER_BUILT --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_LOOK_DIAGNOSE_INDUSTRIAL_NEVER_BUILT` first: another commit may already do it.
