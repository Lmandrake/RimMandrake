## spec

Design Version: FlowWorks 0.1.0 (current, a Problem against the locked bars). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks liquid rules: five old defects (shut sluice seals its whole square, deep sand reads as fresh water, bottle refuses a small pond, fuel sap never ignites, colonists ignore liquid spill filth).

## merged tickets

- `RIMMANDRAKE_SEAL_SLUICE_AT_ITS_PANEL_NOT_ITS_SQUARE` (proposed): A shut sluice gate keeps its own square dry (water 0.0) inside a full pit
  - sweep reading: A shut sluice seals its whole cell (RM_FlowKernel.IsSealed/sealedCell), so its square stays at 0 inside a full pit or keeps old water when one side drains; seen again on his walk 2026-11-20 stations 7-9; kernel untouched since except film sink commits
  - files: `src/RimMandrake/FlowWorks/Source/RM_FlowKernel.cs`, `src/RimMandrake/FlowWorks/Source/Superdeep/RM_FlowDoors.cs`
- `DEEP_SAND_FIX_READS_AS_FRESHWATER` (built): [MAJOR] Deep sand’s fishing tag also makes it a freshwater reservoir
  - sweep reading: drink half fixed (bd36286c47); source half still open: RM_MapComponent_Excavation.IsNaturalLiquid (Excavation.cs:1340-1350) returns baseTerrain.IsWater with no RM_DeepSand exclusion, so a pit dug beside deep sand fills with fresh water (GPT review FD_defs_xml_1.3, MAJOR, verified)
  - its check: a selftest row: IsNaturalLiquid/IsSourceCell false on RM_DeepSand, true on a water terrain; RM_LiquidStock gives deep sand no water fluid
  - files: `src/RimMandrake/FlowWorks/Source/RM_MapComponent_Excavation.cs`, `src/RimMandrake/FlowWorks/Source/RM_LiquidStock.cs`, `src/RimMandrake/FlowWorks/Defs/ManyWaters/TerrainDefs/RM_DeepSand.xml`
- `BOTTLE_FILL_FIX_SMALL_POND_TOO` (proposed): [MINOR] Bottle-fill search refuses a limited pond under one level (1000 L) though a bottle costs a fraction; RM_LiquidBottleUtility.cs search uses ex.Stock.CanSupply — switch to CanDebitTerrain(map,c,units) as TERRAIN_DRINK_FIX_SMALL_POND_REFUSED did
  - sweep reading: HEAD RM_LiquidBottleUtility.cs:353 bottle search still gates on ex.Stock.CanSupply (whole level) while thirst search was moved to CanDebitTerrain
  - files: `src/RimMandrake/FlowWorks/Source/LiquidTypes/RM_LiquidBottleUtility.cs`
- `RIMMANDRAKE_LIGHT_FUEL_SAP_TERRAIN_FIRES_STARTED_ZERO` (proposed): FlowWorks liquid ignition ON never lights fuel sap terrain (firesStarted=0): vanilla FireUtility refuses 0-flammability terrain
  - sweep reading: a failure happened: testq J20261113T071831Z-eaaeff, liquid_ignition_on FAIL, firesStarted=0. Unfixed at HEAD: LiquidIgnition.cs:125 still calls FireUtility.TryStartFireIn, which refuses 0-Flammability terrain. liquidIgnition ships ON by default (8b1312b0d5), so ordinary play reaches it: fuel sap never burns
  - files: `src/RimMandrake/FlowWorks/Source/LiquidTypes/LiquidIgnition.cs`
- `SPILL_CLEAN_FIX_COLONISTS_IGNORE_FILTH` (proposed): liquid_checks L5_colonists_clean_spill FAIL on flowworks tier 2026-10-29: 6 RM_Filth_LiquidSpill pieces untouched after 3000 ticks with a Cleaning-enabled spawned colonist in a Home-painted rect (passed 20261018: 9->0 in 750 ticks). MOD presumed, unproven: check the cleaner's job/readBack and filth cleanability. Evidence D:\ClaudeWork\rimmandrake\foundry_pipe\liquid_checks_A6.json
  - sweep reading: a failure happened: liquid_checks L5_colonists_clean_spill FAIL 2026-10-29 (6 RM_Filth_LiquidSpill untouched 3000 ticks; passed 2026-10-18); MOD vs SITE never settled, no later run
  - files: `src/RimMandrake/FlowWorks/Defs/Canals/FluidDefs/FlowWorks_Fluids.xml`

## his words (as recorded on the merged tickets)

- on `RIMMANDRAKE_SEAL_SLUICE_AT_ITS_PANEL_NOT_ITS_SQUARE`: "where the Sluice Gate stands, it kept it at water level 0.0 nonsensically." (live look 2026-11-14, his 11)

## verify

Acceptance test: none as one command, five causes; each fix writes its own red-first case (each merged ticket above names its check where it had one).

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: RIMMANDRAKE_SEAL_SLUICE_AT_ITS_PANEL_NOT_ITS_SQUARE
item: DEEP_SAND_FIX_READS_AS_FRESHWATER
item: BOTTLE_FILL_FIX_SMALL_POND_TOO
item: RIMMANDRAKE_LIGHT_FUEL_SAP_TERRAIN_FIRES_STARTED_ZERO
item: SPILL_CLEAN_FIX_COLONISTS_IGNORE_FILTH
