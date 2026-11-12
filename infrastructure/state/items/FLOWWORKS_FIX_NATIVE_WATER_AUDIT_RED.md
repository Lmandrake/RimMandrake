---
state: proposed
needs: offline
---

# FLOWWORKS_FIX_NATIVE_WATER_AUDIT_RED

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Natives-drink-own-water audit is red: RM_Miasma brackish deep and shallow (NotDrinkable), RM_TheChill RM_PropaneDeep (Propane) read BLOCKED

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_FIX_NATIVE_WATER_AUDIT_RED` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_FIX_NATIVE_WATER_AUDIT_RED --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_FIX_NATIVE_WATER_AUDIT_RED` first: another commit may already do it.
