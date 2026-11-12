---
state: proposed
needs: offline
---

# HOSE_CALLSITE_FIX_PATTERNS_OUTRAN_CODE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Two hose call-site source checks fail in the FlowWorks SelfTest on clean hose code: GptA_hoses_off_never_retract_on_obstacles and A3 recycled world TickRecheck pattern

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show HOSE_CALLSITE_FIX_PATTERNS_OUTRAN_CODE` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_CALLSITE_FIX_PATTERNS_OUTRAN_CODE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_CALLSITE_FIX_PATTERNS_OUTRAN_CODE` first: another commit may already do it.
