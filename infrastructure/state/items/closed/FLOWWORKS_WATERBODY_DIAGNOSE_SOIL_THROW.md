# FLOWWORKS_WATERBODY_DIAGNOSE_SOIL_THROW

**Outcome (2026-10-16, FOUNDRY, live on donor_off_phase0):** a VANILLA 1.6 Odyssey bug, not FlowWorks. FlowWorks'
`RM_Patch_LiquidHeatTerrainChanged` postfix was only *listed* on the Harmony stack of the patched
`TerrainGrid.DoTerrainChangedEffects`; it never ran (the original threw first).

**Stack** (from `Transient/modcheck/Contagion_20261016T081229Z.json`, chain `genome`, `set_terrain_batch Soil`):
`Enumerable.First` <- `WaterBodyTracker.RemoveCellFromExistingBody` <- `WaterBodyTracker.Notify_TerrainChanged`
<- `TerrainGrid.DoTerrainChangedEffects` <- `TerrainGrid.SetTerrain`. Message: `Sequence contains no matching element`.

**Mechanism (decompiled 1.6):** when a water cell changes between two non-None `waterBodyType`s (fresh <-> salt, or
water <-> one of our liquids of another type), `Notify_TerrainChanged` only calls `TryCreateBodyOrAddToExisting`.
The cell joins the new-type body; the OLD body keeps it in `CellCount` (never decremented) while its
`bodiesByCell` entry is overwritten. Turning the old body's remaining cells to land later finds `CellCount > 0` with
no cell left in `bodiesByCell`, and the `rootCell` reassignment's `First(...)` throws. A save/load heals it
(`ConstructBodies` refloods).

**Repro (vanilla terrain only, quicktest, deterministic):** `WaterShallow` 3x3, one cell `WaterOceanShallow`
(optionally back to `WaterShallow`), then `Soil` over the 3x3 -> throw. Control without the flip -> clean.

**Fix:** `src/RimMandrake/FlowWorks/Source/RM_WaterBodyTypeFlipFix.cs` - a prefix on
`WaterBodyTracker.Notify_TerrainChanged` that detaches the cell from its old-type body (as vanilla's own remove
does) before vanilla adds it to the new one. Setting `waterBodyTypeFlipFixEnabled` (default on; off = vanilla).
Commit `f7f2a6d30`. **Verified live** after redeploy: all three repros (flip, flip-and-back, 4x1 strip) apply clean,
0 `WaterBodyTracker` lines in Player.log.

**Open:** which step flipped a water type on the Contagion modcheck map was not traced (tick 824016 map, tile
55631); any type flip triggers it, and the fix covers every route.
