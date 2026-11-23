## spec
Class MOD, found live 2026-11-20 by sc_ice (holder sub-run 5, design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_ice_20261120T224417.json).
A shoveled Mining-10 colonist cut a 5x5 dug pond (Soil ground, 1 m water) frozen over with vanilla ThinIce at -5.4 C; the cut landed (d 2 -> 3) with
ThinIce still on the square at the last poll, and no RM_CrushedIce appeared within 3 squares (list_things scanned 15,108 things, isCompleteList).

Cause (read): `RM_DigDiscovery.IceCut` reads `RM_DigSpoil.ClassAt` = `ClassOf(OriginalTerrainAt)`, the ground the pit was dug from (Soil), and
`RM_GroundClassMath.IceTerrains` lists Ice, RM_PackedIce, RM_ChillIceBedrock, RM_PackedSnow and VEE_DenseSnow_Rough, not vanilla's ThinIce.
So a frozen-over pit never yields crushed ice.

Instrument sane: the same scene with both ponds dug from Ice ground (evidence/exp/ice_ground_ice_sanity.json) reads the cut PASS (crushed 0 -> 1)
and the melt PASS (ledger 0 -> 10,000 dL, want 10,000).

Bar (design/concepts/FlowWorks/scenes.json sc_ice): "a frozen pond on a cold map (asserted ice)"; "cut a cell, then warm above freezing";
"crushed ice on the cut that melts back into the pond"; control "cut an unfrozen pond" -> "no crushed ice".

Design point for the fixer: the cut through a frozen-over pit should yield from its surface ice (top terrain ThinIce). Note that an open-water
cut on Ice ground also yields crushed ice under the ground rule (the sanity run's control read 0 -> 1); sc_ice stages Soil ground, so its
control is unaffected.

## verify
Stage 6: `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_ice --out <json>`; ICE_cut_leaves_crushed_ice and
ICE_melts_back_into_pond PASS, ICE_control_unfrozen_cut_no_crushed_ice stays PASS. Offline: a unit test on IceCut's class read (red now, green on the fix).

## criteria
- A cut through ThinIce over a dug pit leaves one crushed ice that melts back to 10,000 dL; a cut through open water on Soil leaves none.

## refs
file: src/RimMandrake/FlowWorks/Source/RM_DigDiscovery.cs
file: src/RimMandrake/FlowWorks/Source/RM_GroundClassMath.cs
def: ThingDef/RM_CrushedIce
