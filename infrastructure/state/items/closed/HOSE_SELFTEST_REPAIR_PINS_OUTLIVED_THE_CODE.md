---
state: proposed
needs: offline
---

# HOSE_SELFTEST_REPAIR_PINS_OUTLIVED_THE_CODE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

HoseSelfTest.cs:713/714 pin 'if (!MarkDirty(...)) MapChanged();' but RM_MapComponent_Hoses.cs now calls MarkDirty unconditionally (lines 393/437): 2 FlowWorks SelfTest hose assertions red on 8ba36d342c (436/438 with --only Hose*); re-pin to the current no-overflow shape

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show HOSE_SELFTEST_REPAIR_PINS_OUTLIVED_THE_CODE` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_SELFTEST_REPAIR_PINS_OUTLIVED_THE_CODE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_SELFTEST_REPAIR_PINS_OUTLIVED_THE_CODE` first: another commit may already do it.
