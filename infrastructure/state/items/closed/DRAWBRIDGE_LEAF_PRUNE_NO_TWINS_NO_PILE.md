---
state: proposed
needs: offline
---

# DRAWBRIDGE_LEAF_PRUNE_NO_TWINS_NO_PILE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Drawbridge build spec 2026-11-04, part 2: remove two-leaf drawbridges (SplitLeaves to one leaf; a span over the max leaf is not a drawbridge, ordinary bridges still allowed), cut the plank stack (RM_DrawbridgeArt.DrawPlanks, its art and pad; raid planks untouched), retire the no-longer-drawn LeafUp Edge/Underside art and RM_DrawbridgeCableMath.LeafEdgeBody (DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED stopped drawing them).

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show DRAWBRIDGE_LEAF_PRUNE_NO_TWINS_NO_PILE` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify DRAWBRIDGE_LEAF_PRUNE_NO_TWINS_NO_PILE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=DRAWBRIDGE_LEAF_PRUNE_NO_TWINS_NO_PILE` first: another commit may already do it.
