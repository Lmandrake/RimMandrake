# FlowWorks code review pass 1 (2026-10-05)

Scope: Source/*.cs (25) + Drilling, Superdeep, Swale, Debug.

## Reachability

## Per-file

## Build/selftest

## Marked clean
All 35 files are in RimMandrake_FlowWorks.csproj <Compile Include>. Live callers checked by grepping each file's type names across FlowWorks *.cs/*.xml: every file has an external referrer (defs XML thingClass/workerClass/driverClass, DefOf, other C#) except FlowWorksDebugActions.cs ([DebugAction] attribute-registered) and RM_PitDepthDraw.cs ([HarmonyPatch] attribute) — both live via attribute discovery. Pure-math files also compiled into Source/SelfTest. No dead files.

Review fanned out read-only to 4 opus reviewers (groups A-D); fixes applied by this agent.

Already CLEAN before this pass (8): JobDriver_DigCanal, JobDriver_FillInCanal, RM_ExcavationDepth, WorkGiver_DigCanal, WorkGiver_FillInCanal (b32878458), Drilling/RM_LiquidDrillExtension, RM_MapComponent_SubsurfaceLiquid, RM_SubsurfaceLiquidBiomeExtension (fd63f4e21). Still re-read this pass. 27 DIRTY.

### Group B (Mod, DefOf, FluidDef, Flood_FlowWorks, StockMath, FluidIdentity)
No significant findings except RM_StockMath.CollectComponent: when a component hits maxCells, cells still queued are already in visitedExcavated and never seeded -> permanently starved on huge networks. Fix: un-mark leftover queued excavated cells after the loop.

### Group A (Excavation, ExcavationDepth, designators, workgivers, jobdrivers)
- Designator_DigCanal + WorkGiver_DigCanal: read c.GetTerrain (temp layer = the liquid) so a wet channel read "Already water" -> could never be deepened, and the WorkGiver silently DELETED the designation once a channel got wet. FIXED: BaseTerrainAt (matches JobDriver_DigCanal).
- WorkGiver_FillInCanal: pawn-in-cell rule only checked at designation. FIXED: skip (keep designation) while a pawn is in the cell.
- Others: no significant findings.

### Group C (LiquidStock, LiquidBody, LiquidFire, FireMath, FillEffectMath, PitFillEffects, Debug, Drilling)
- RM_LiquidStock.FormBody: body truncated at MaxBodyCells leaves far cells unindexed -> later contact re-flooded owned cells into overlapping duplicate bodies (save bloat, double recede). FIXED: join the owned body on contact.
- Building_LiquidDrill: OutletCell = Position+FacingCell is INSIDE the 2x2 RM_LiquidDrill footprint in every rotation. FIXED: OutletFor() past the facing edge (same cell for 1x1), used by building and PlaceWorker.
- RM_MapComponent_SubsurfaceLiquid: removed LiquidDef -> yieldedLiquid null with hasYield true -> StatusReport NRE on every inspect. FIXED: HasYield and StatusReport guard null.
- Others: no significant findings.

### Group D (Superdeep/*, Swale, SuperdeepShooting, PitDrawMath, PitExposure*, PitTrapMath)
- RM_Swale.TryStep: BaseTerrainAt reads the ground under a player floor; SetTerrain of a rung then destroyed the floor. FIXED: skip cells with UnderTerrainAt != null.
- RM_SuperdeepTrap.EngineOf: uncached GetComponent under CanReach/PawnCanOpen/TryEnterNextPathCell hooks ahead of the early-out. FIXED: RM_SuperdeepShooting.EngineFor cache. Jumpers pruned of destroyed pawns on save.
- RM_PitExposure: copied whole room into a new List every 120 ticks before the 400 cap. FIXED: CellCount gate + iterate.
- Group A follow-up: BaseTerrainAt in the dig designator would have let a floored cell be dug; switched to FoundationAt ?? TopTerrainAt (TerrainAt minus temp layer).
- Not changed: SuperdeepTrapState.Tick walks spawned pawns every tick while superdeep cells exist (descent detector by design, no alloc). PitDepthDraw DrawPos also feeds projectile origin (minor).
Build 0 err after all fixes.

## Marked clean (pass 1, at c984c264f): 26 files with zero significant findings (all except the 10 fixed). Fixed 10 get a fresh full re-read before marking.

## Pass 2: fresh full re-read of the 10 fixed files (opus) -> no significant findings; all 10 marked clean. Low-severity note left: RM_LiquidStock FormBody join checks owner on any neighbour (incl. receded cells); joined cells are indexed but not in body.cells (re-joined after load). 36/36 scoped files CLEAN.
