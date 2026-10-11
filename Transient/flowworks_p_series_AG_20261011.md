# FlowWorks P-series — picker AG, 2026-10-11 (FOUNDRY)

Takes the HIGHEST unclaimed offline-provable P item (AF takes the lowest). P14 and P10 were done earlier; P4 is with AF.

## P11 STATION_REACH_CENTRE_RETHINK_FOOTPRINT
**Defect (verified):** `src/RimMandrake/FlowWorks/Source/LiquidTypes/Building_LiquidPump.cs` `ReachCells()` took a
circle of `reach + rect.Width/2` about `Position`. On the 3×2 pumping station (reach 4) that reached 5 cells off the
bottom edge and 4 off the top, and the footprint's height was never used.

**Fix:** `RM_PumpMath.FootprintDistSq` / `InFootprintReach` (Verse-free) measure from the footprint's nearest cell;
`ReachCells` scans `rect.ExpandedBy(ceil(reach))`, keeps cells within reach, nearest first. Touching-cell pumps
(reach ≤ 1.5) unchanged.

**Proof (offline):** `PrePortFixChecks.cs` case `P11_station_reach_is_measured_from_the_footprint` (4 off every side
in, 5 out, footprint excluded, corner bound) plus a can-fail: the old circle reaches (10,5), the new rule does not.
`selftest_flowworks_stock.py` 160/160; rivers/swale/cover_breaks/looks_round pass; `winbuild.py FlowWorks` 0 errors.
Owed live: a station drawing from water 4 off its long side in game. Not deployed.

## P9b NATURAL_HEAT_CACHE_PROVE_STALE_DAYS

**Defect (verified by reading):** `src/RimMandrake/FlowWorks/Source/RM_LiquidHeat.cs` caches the natural hot/cold cell
list and rebuilds it only every `RescanTicks` = 15,000 ticks. Nothing invalidated it on a terrain change except the dev
proof `ProofRescan`, so a drained or painted hot spring kept (or failed to start) heating its room for up to 60
intervals.

**Hook (RimSage, decompiled 1.6):** every vanilla terrain write (SetTerrain, RemoveTopLayer, Set/RemoveFoundation,
Set/RemoveTempTerrain, SetTerrainColor) ends in private `TerrainGrid.DoTerrainChangedEffects(c, oldTerr, newTerr,
oldFoundation)`; `TerrainGrid.map` is a private field (`___map`). Not covered: `SetUnderTerrain` (under layer, not
`TerrainAt`) and `RemoveGravshipTerrainUnsafe` (gravship moves; the 15,000-tick rescan still catches those).

**Fix:** postfix `RM_Patch_LiquidHeatTerrainChanged` (PatchFeature on `liquidHeatPushEnabled`) marks the list stale via
`NotifyNaturalStale()` when `RM_LiquidHeatMath.TerrainChangeStalesNatural(oldKind, newKind, excavated)`: a
non-excavated cell whose hot/cold kind changed. Same-kind writes and excavated cells (read live) force nothing, so the
engine's own channel writes do not trigger rescans. At most one full rescan per 250-tick interval.

**Proof (offline):** `PrePortFixChecks.cs` case `P9b_...` (truth table, wiring regexes on the patch target, decompiled
parameter names and the notice, a can-fail probe that the binding check rejects a mis-named parameter, and the old
60-interval staleness). `selftest_flowworks_stock.py` 161/161; other FlowWorks selftests pass; `lint_harmony_targets.py`
missing 0; `winbuild.py FlowWorks` 0 errors. Owed live: drain a roofed hot pool and see the room stop warming within an
interval. Not deployed.
