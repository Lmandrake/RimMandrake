---
state: proposed
needs: offline
---

# FLOWWORKS_CLIMBERS_REWIRE_NAMES_THAT_LEFT

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks_LadderClimbers.xml still names RSW_ creatures that moved to the RM tier as RM_ (batch 3: RSW_Diplocaulus/Holcorobeus/Platyhystrix/Protosolpuga -> RM_; more follow as SWB_RM_FAUNA_DECIDE_HOME_LIKE_CHIKKA batches land). Repoint the defName= list; BENCH owns FlowWorks so FOUNDRY's mover skipped it. Old names now match nothing (silent no-op).

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_CLIMBERS_REWIRE_NAMES_THAT_LEFT` history before building.

## latest ledger notes

- 2026-10-24: Add RSW_Karrask -> RM_Karrask (moved a59b728a73); FlowWorks_LadderClimbers.xml still names RSW_Karrask.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_CLIMBERS_REWIRE_NAMES_THAT_LEFT --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_CLIMBERS_REWIRE_NAMES_THAT_LEFT` first: another commit may already do it.
