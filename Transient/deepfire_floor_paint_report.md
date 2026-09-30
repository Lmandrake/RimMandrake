# DEEPFIRE_FLOOR_PAINT_1 report

## Status
Built, compiled clean, NOT deployed, NOT live-tested. The coordinator runs the proof.

## Harmony targets (RimSage, decompiled 1.6)
- `Verse.TerrainGrid.SetTerrainColor(IntVec3 c, ColorDef color)` — public; writes colorGrid then calls DoTerrainChangedEffects(c, same, same).
- `Verse.TerrainGrid.DoTerrainChangedEffects(IntVec3 c, TerrainDef oldTerr, TerrainDef newTerr, TerrainDef oldFoundation = null)` — PRIVATE, single overload; `map` is a private field (`___map`).
  Callers: SetTerrain, RemoveTopLayer, SetFoundation, RemoveFoundation, SetTempTerrain, RemoveTempTerrain, SetTerrainColor.
  NOT called by `RemoveGravshipTerrainUnsafe` (gravship lift) — coats there are not cleared by this hook.
- `RimWorld.BeautyUtility.CellBeauty(IntVec3 c, Map map, HashSet<Thing> countedThings = null)` — public static, NOT inlined-shaped (loops, ~40 lines); postfixed directly, the spec's AverageBeautyPerceptible fallback is not needed.
  Early-returns the Fillage.Full thing's beauty (walls) without terrain — the postfix mirrors that (no floor bonus under a full-fillage edifice).
- `RimWorld.RoomStatWorker_Beauty.GetScore(Room room)` — sums CellBeauty over cells then divides by `CellCountCurve.Evaluate(n)` (0→20, 40→40, linear).
- `Verse.Room.Notify_TerrainChanged()` — public; sets statsAndRoleDirty (used to refresh the room readout after a coat change).

## Built (all under src/RimMandrake/LuminousPigment/)
- `Source/MapComponent_DeepfireLights.Clusters.cs` (new; class made `partial`): Scribed byte grid
  `floorCoats` (`rmDeepfireFloorCoats`), floor API (AddFloorCoat / ClearFloorCoats / FloorCoatsAt /
  Notify_FloorColorChanged), fixed 3x3 block clustering keyed block x kind(floor|1x1 building) x coats x
  colour -> one proxy per group at the cell nearest its centroid, radius = coat radius + 1 for 2+ cells.
  FinalizeInit rebuilds floor lights from the grid (drops coats on cells whose floor vanished).
- `MapComponent_DeepfireLights.cs`: 1x1 Buildings (walls, small furniture) now join the clusters instead of
  one proxy each; multi-cell things keep one proxy per Thing. `Get(map)` got a one-entry cache (CellBeauty
  is hot).
- `Source/DeepfireFloorPatches.cs` (new): postfixes on SetTerrainColor (relight), DoTerrainChangedEffects
  (floor removed/replaced -> coats zeroed, no refund; temp terrain over a surviving floor keeps them),
  CellBeauty (+0.5 per coated cell, skipped under a full-fillage edifice, as vanilla skips terrain there),
  `RM_RoomStatPart_DeepfireFloor` on RoomStatWorker_Beauty.GetScore (+2 per 10 coated room cells, cap 10).
- `Source/DeepfireFloorJobs.cs` (new): floor-cell branch of the player path — WorkGiver_ApplyDeepfireFloor
  (cell scanner, Floor reservation layer, vanilla WorkGiver_PaintFloor shape) + JobDriver_ApplyDeepfireFloor.
  Defs: `RM_ApplyDeepfireFloorDesignation` (targetType Cell), JobDef `RM_ApplyDeepfireFloor`, WorkGiverDef
  `RM_ApplyDeepfireFloorWorkGiver` (Construction, priorityInType 400). Designator_Deepfire / RemoveDeepfire
  now accept floor cells.
- `Source/DeepfireFloorDebugActions.cs` (new): dev actions under Actions\Deepfire (coat / designate /
  vanilla-paint red / strip / remove floor / report, each on the 6x6 rect SW-cornered at the clicked cell;
  each logs one `[DeepfireFloor] {json}` line).
- Constants (no settings wiring): `DeepfirePaintDefaults.ClusterBlock 3, ClusterRadiusBonus 1, CostFloorCell 1,
  FloorBeautyPerCell 0.5, FloorRoomBonusPer10 2, FloorRoomBonusCap 10`.
- Defect fixed in passing: `RM_DeepfireLightProxy` was saveable, so a save/load kept every proxy AND
  CompDeepfire.PostSpawnSetup spawned a fresh twin — lights doubled per load. Now `isSaveable false`
  (spec §3.6 "Lights are never saved").

## Findings worth knowing
- The spec's proof arithmetic is wrong: RoomStatWorker_Beauty.GetScore divides the per-cell sum by
  CellCountCurve (38 for a 36-cell room), so the rise is 18/38 + 6 ≈ 6.47, not "36 x 0.5 + 6". The proof
  script asserts the engine formula.
- The "4 proxies" row only holds when the 6x6 sits on the 3-cell block grid (SW corner multiple of 3);
  unaligned it is 9. The script defaults to (60,60).
- The real designation -> WorkGiver -> JobDriver floor path is built but NOT exercised by the proof script
  (it uses the dev coat action); a "Floor: designate 6x6" dev action exists for a live check of it.
- Not handled: gravship lift (`RemoveGravshipTerrainUnsafe` bypasses DoTerrainChangedEffects), Dub's Paint
  Shop floor colours (§8), the room line as its own readout row (the bonus is folded into the score).

## Verification
- dotnet build: 0 errors, 0 warnings; DLL 56,320 -> larger (new types compiled; csproj lists all 4 new files).
- XML parse: every Defs/ and Patches/ file parses.
- run_selftests.py: 77/79, 1 unmeasured, 1 FAILED — `selftest_deployed_biome_refs.py` (19 dangling
  deployed biome refs, RUT_TheRot/RUT_WeepingStones; unrelated to this mod).

## Proof script
`python.exe src\RimMandrake\bridgetools\prove_deepfire_floor.py [--start] [--x 60 --z 60]` from the repo root,
after deploying this build. Builds an 8x8 walled roofed room (6x6 WoodPlankFloor interior), then asserts:
36 coated / exactly 4 floor proxies / centre glow up / CellBeauty +0.5 / room line +6 / room Beauty rise
= 18/curve(n)+6; red paint -> Structure_Red, still 4 proxies, red-dominant glow; strip -> 0 coats, 0 proxies,
Beauty back to baseline; re-coat + RemoveTopLayer -> grid zero, 0 proxies; no Deepfire errors in the log.
Exit 0 pass / 1 fail / 2 could not run.
