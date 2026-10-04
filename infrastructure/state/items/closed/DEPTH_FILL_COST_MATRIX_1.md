# DEPTH_FILL_COST_MATRIX_1 — Path cost as a depth × fill-tier matrix so flooded is always slower than dry

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
[E]: each fluid's fill terrains become a depth × tier matrix (4 → 12 terrains per fluid, generated, not hand-written) so that, at every depth 1-3, any fill costs strictly more than the same depth dry. Fixes the MEASURED contradiction `RM_Fill_Water_Half` 42 vs dry `RM_Channel_Mid` 45. Superdeep stays Standable/300 dry and flooded alike (ruling 26).

## verify
A def census asserts, for every fluid and depth 1-3, cost(fill) > cost(dry same depth); the generator re-run is idempotent.

## criteria
No fill terrain is cheaper to cross than the dry cut beneath it.

## depends
Nothing; defs only. Does not wait on the oscillation fix.

## northstar
O1 def census row: the inequality over all generated terrains, with the old 42 < 45 case as its named regression.
