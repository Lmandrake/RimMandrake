---
state: proposed
needs: bridge
---

# HOSE_PLUMP_FIX_SAME_LENGTH_AS_FLAT

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks hose H6: plump hose is wider than flat but its poseLen equals flat (23.7132 = 23.7132), so H6 fails

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show HOSE_PLUMP_FIX_SAME_LENGTH_AS_FLAT` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_PLUMP_FIX_SAME_LENGTH_AS_FLAT --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_PLUMP_FIX_SAME_LENGTH_AS_FLAT` first: another commit may already do it.
