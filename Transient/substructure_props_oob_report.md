# SUBSTRUCTURE_PROPS_LAYER_OOB_1 — investigation report

Status: IN PROGRESS

## Task
21x `Could not regenerate layer RimWorld.SectionLayer_SubstructureProps: System.IndexOutOfRangeException`
during sea-dive proof tonight. Trace:
`Verse.EdificeGrid.get_Item(IntVec3)` ← `GridsUtility.GetEdifice` ←
`RimWorld.SectionLayer_GravshipHull.ShouldDrawCornerPiece` (TRANSPILER gravtide.mod
`GravTide.SectionLayer_GravshipHull_ShouldDrawCornerPiece_Patch`) ←
`SectionLayer_SubstructureProps.Regenerate` (TRANSPILER vanillaexpanded.gravship)

## Sections
- [ ] Evidence gathered from the two logs
- [ ] Our dive-map generation reviewed (DivingInteraction, RM_SeaDiveGenerators.xml, GenStep_SeaFloorTerrain, hatch placement)
- [ ] Substructure/hull terrain def semantics (RimSage)
- [ ] SectionLayer_SubstructureProps / SectionLayer_GravshipHull decompiled logic (RimSage)
- [ ] Root cause determination: ours vs donor (GravTide/VEF)
- [ ] Fix applied (if ours) or donor verdict written (if not)
- [ ] Build + selftest verification
- [ ] Commit + push

## Findings
(pending)

## Verdict
(pending)
