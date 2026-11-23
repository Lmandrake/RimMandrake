---
state: built
needs: bridge
---

# DRAWBRIDGE_ROPES_FIX_DEAD_SINGLE_FACING

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

RM_DrawbridgeCableMath.RopesFor falls back to Art[key] with no bare key; a single-facing anchor would throw KeyNotFound

Built at `87e27b3e966c` (origin/main); code is in, what is owed is below.

## what is left

- A2

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify DRAWBRIDGE_ROPES_FIX_DEAD_SINGLE_FACING --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=DRAWBRIDGE_ROPES_FIX_DEAD_SINGLE_FACING` first: another commit may already do it.
