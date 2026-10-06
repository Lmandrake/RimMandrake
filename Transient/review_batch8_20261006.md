# Review batch 8 (2026-10-06)

Full-file reviews at 99b61e39b (SolarMirrors light hook) and e2edd5cc3 (ledge refuge). Engine facts checked with RimSage
(GlowGrid.GroundGlowAt signature + private `map` field, Building_WorkTable.UsableForBillsAfterFueling,
Pawn_JobTracker job expiry).

## FIXED — `src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs` (uncommitted, DLL rebuilt)

1. **Stale light buffer doubled light.** `BuildLightLayer` zeroed `lightLayer` only when the last build had
   `anyLight`. Toggling Solar Mirrors' `shadeEffect` off made `AddLight` return false (anyLight=false over a filled
   buffer); toggling it back on added the new light on top of the old. Same for unregister-all then re-register.
   Fix: always clear the buffer when sources exist (one Array.Clear per Recompute).
2. **Exposure let a beam override shade gear; ShadeAt did not.** `RebuildHeatLayers` applied light AFTER the gear
   cover, so a shade tent in a beam read full exposure (heat, sun path cost, patch graph) while `ShadeAt` and the
   interface doc say gear still shades inside a beam. Fix: roof/cast exposure, then light, then gear cover, then
   glare floor. With no light the result is identical to before (zero-change claim preserved).

Hook otherwise OK: GridVersion bumps once per Recompute after light is built; buffer re-sized on cell-count change;
MirrorLight unregisters in MapRemoved and the grid clears its list; everything runs on the main thread in
MapComponentTick/FinalizeInit; no subscriber = no reads of lightLayer. Note (not a defect): with SolarMirrors loaded
every map subscribes and its first empty pass triggers one extra Recompute.

## CLEAN (marked)

- SolarMirrors/Source: RM_CompLightReceiver.cs, RM_CompMirror.cs, RM_MapComponent_MirrorLight.cs, RM_MirrorMath.cs,
  RM_MirrorPatches.cs, RM_ReAimMirror.cs, RM_SolarMirrorsMod.cs
- CreatureBehaviors/Source/RM_SunHeatMath.cs (selftest 48/48)
- FloodedCanyon/Source/RM_LedgeRefuge.cs — 250-tick sweep, Goto/Wait pushes (Wait expiry confirmed in
  JobTrackerTickInterval), seeker selection, save/load (debugCells null-guarded; cells rebuilt on FinalizeInit) all sound.
