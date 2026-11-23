---
state: built
needs: bridge
---

# PIPE_ADAPTER_REDRAW_FLANGE_FOR_A_WHALE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

RM_PipeAdapter_Chemfuel/Propane: flange ~0.56 and brass coupling ~0.37 cell vs hose 0.18; redraw smaller (inventory in items/PUMP_PORTS_REDRAW_SIZED_FOR_FAT_PIPES.md)

Built at `d025b96cb3e3` (origin/main); code is in, what is owed is below.

## what is left

- A1

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify PIPE_ADAPTER_REDRAW_FLANGE_FOR_A_WHALE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=PIPE_ADAPTER_REDRAW_FLANGE_FOR_A_WHALE` first: another commit may already do it.
