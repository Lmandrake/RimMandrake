## spec
Found 2026-11-11 by CLAUDE_ARCHMAGI_FWLIVE while proving `GSS_WATER_STUB_FIX_PASSED_LAST_WEEK` (broaden step, GPT's
"messy real water" suggestion), live on Archmagi, fw_gss_sitting list, GSS DLL c16983bc (= .srchash).

**What a player sees:** a waterproof conduit laid across FlowWorks' own pit/canal water `RM_Fill_Water_Superdeep`
("deep water (2 m or more)") is drawn by Gimme Some Slack as ONE cord lying on the water surface, battery to consumer.
The same crossing over vanilla `WaterDeep` dives: two water stubs at the banks. Deep swim on or off makes no difference.

**Why:** `SnapshotBlock.Of` (GSS `Source/Core/SnapshotBlock.cs`) buries only water whose TerrainDef is Impassable.
`RM_Fill_Water_Superdeep` inherits WaterShallow: passability Standable, affordance WaterproofConduitable (so a player CAN
lay waterproof conduit on it, unlike vanilla WaterDeep, where `jawa/build_check` refuses it). FlowWorks decides
"deep" itself in `RM_Swim.IsDeepSwimIndex` (swim terrain OR the excavation map component's dug depth, not decked),
which GSS cannot see without a cross-mod contract.

**Live readings** (matrix F60 canal scene with the water terrain swapped, `run_live.py --scenes full --only XW`):
- XW1 RM_Fill_Water_Superdeep: stubs 0, cord_edges 1 (cord on the water) — swim on AND off
- XW2 RM_Fill_Water_Brim (1.5 m, wadeable): stubs 0, cord_edges 1 — consistent with GSS's "walkable = ground" rule
- XW3 WaterMovingChestDeep (vanilla river, wadeable): stubs 0, cord_edges 1 — same
- XW4 WaterDeep: stubs 2, cord_edges 2 (PASS)
Evidence: `whittle/gss_water_stub_fix_passed_last_week/evidence/sibling_water_variants_swimON.json`,
`…/sibling_water_variants_swimOFF.json`, `…/sibling_XW1_fw_superdeep_cord_on_water.png`, `…/sibling_XW4_waterdeep_two_stubs.png`.

**To decide (Designer):** should a cord dive under swim-depth water that is def-Standable? If yes, the contract: e.g. a
terrain tag or DefModExtension FlowWorks puts on its swim-depth terrains that GSS reads by name (no assembly reference),
plus what to do about dug-depth cells that are swim-deep only through the excavation component. Brim (1.5 m) and vanilla
chest-deep river stay wadeable ground. A matrix scene with `RM_Fill_Water_Superdeep` would guard it.
