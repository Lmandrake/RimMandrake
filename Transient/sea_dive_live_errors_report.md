# SEA_DIVE_LIVE_ERRORS_1 report — 2026-09-30

Inputs: `Transient/sea_dive_floor_live_2026-09-30.txt`, `Transient/sea_dive_player_log_2026-09-30.txt`.
All offline; no game or bridge touched.

## 1. Proof reported "no pocket map generated" x4 — instrument bug (ours, fixed)

Player.log shows maps 2, 3, 4 and 5 generated with `pocket=True`, one per sea.
`prove_sea_dive_floor.py`'s `loaded_maps()` read `r["loadedMaps"]`, but
`jawa/set_current_map` refuses an unknown id through `Fail(message, extra)`, which
returns `{success, message, details}`. The list is at `details.loadedMaps`
(`JawaBenchMapInfoTools.cs` + `JawaBenchTerrainTools.cs:7007`). So the top-level read
was `{}` every time, and "no new map" was guaranteed.

Fix: read `details.loadedMaps`, and raise if the listing is empty. An empty listing
means the instrument is broken; it never means there are no maps. The census now also
records the exit count and the terrain under the exit, and it fails the sea unless
there is exactly one exit and it is not standing on brine pool.

## 2. "Tried to destroy non-destroyable thing RM_SeaDiveExit" x9 — ours (fixed)

The errors fall between the Grey Sea's map-gen context line and its
`FinalizeInit: map 3`. Only the Grey Sea generator lists `RM_GreySeaFloorDressing`
(order 880), which runs after `RM_PlaceSeaDiveExit` (order 400). The dressing called
`c.GetEdifice(map)?.Destroy()` in its basin carve, Elder footprint and brine channels.
The exit counts as an edifice (`BuildingProperties.isEdifice = true` by default) and is
`destroyable=false`. `Thing.Destroy` logs this exact error (`Thing.cs:1047`) and refuses,
once per cell of the 3x3. RimSage confirmed both facts. Side effect: the exit was left
standing, but the terrain under it was repainted as brine pool.

Fix, in `GenStep_GreySeaFloorDressing.cs`:
- The keep-out zone is the exit footprint expanded by 2 cells.
- The basin is placed at the lowest cell whose jacket ring (11.5) clears the keep-out:
  first with the strict margin, then with a margin relaxed to the pool's own edge. If
  neither fits, the step takes the candidate farthest from the exit.
- The basin, channels, aprons and jacket ring all skip keep-out cells.
- Only `destroyable` edifices are destroyed.
- The Elder is skipped (with a warning) if its footprint would overlap the exit or an
  indestructible edifice, because `GenSpawn` would wipe it.

`BrineEncasementUtility` had the same unguarded `Destroy()` (a pawn encased on the
exit's cell). It now refuses to encase on an indestructible edifice.

## 3. RealFoW IndexOutOfRangeException — donor-side (not ours; documented)

Stack: `MapComponentSeenFog.IsShown(faction,x,z)` ← `CompFieldOfViewWatcher.livePawnHear`
← `CompTick`. Decompiled from the installed
`workshop/294100/3391128917/1.6/Assemblies/rimworld-mod-real-fow.dll`
(Mlie.NWNRealFogOfWar) with ilspycmd:

- `IsShown` returns `GetFactionShownCells(f)[z * mapSizeX + x]` with no bounds check.
- `livePawnHear` calls `IsShown(faction, item.Position)` for every moving non-faction pawn
  in `nearByPawn`, a cached list.
- `PostSpawnSetup` switches `mapCompSeenFog` to the NEW map and resets
  `lastHearTick = lastHearUpdateTick = now`, but never clears `nearByPawn`. So after
  +100 ticks, the hearing pass indexes the new 50x50 pocket map's grid with the old
  home-map pawns' positions, and `z*50+x` goes past 2500.
- `CompTick` runs the hear check before the list refresh (`ticksGame - lastHearUpdateTick == 200`,
  exact equality). The exception aborts the tick before the refresh can run, so the
  refresh tick is missed and never fires again. The error then repeats every 100 ticks
  for as long as the pawn stays on that map, and the rest of that pawn's FoV tick is
  skipped too.

Our side is clean. The pocket map is a normal 50x50 map from
`PocketMapUtility.GeneratePocketMap`, and RealFoW sized its grids from `map.Size` at
construction. Fannie's positions ((27,6), (32,4), (29,5), (23,3)) are all in bounds.
The bad index comes from OTHER pawns' positions on the map she left. Any pawn that
travels from a larger map to a smaller one hits this if a moving non-player pawn was in
its hearing range before it left. That covers any pocket map: Anomaly undercave,
gravship, ours. Only Fannie threw because only she had moving animals near her on the
home map.

Not fixed here. A compat Harmony postfix on `CompFieldOfViewWatcher.PostSpawnSetup`
that clears `nearByPawn` would be enough, but it belongs in a compat mod, not
DivingInteraction. It could be filed as `REALFOW_STALE_HEARING_LIST_1` if wanted.

## Live command

Deploy DivingInteraction, then (python.exe, repo root, throwaway quicktest map):

    python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod DivingInteraction --apply
    python.exe src/RimMandrake/bridgetools/prove_sea_dive_floor.py

The DLL can only be written while the game is down, and the proof needs a fresh
quicktest. Expected: four verdicts with a census each, zero `non-destroyable` lines in
Player.log, and the Grey Sea exit on non-pool terrain. RealFoW errors can still appear
on a diver that had moving animals nearby before it dived; that is donor-side.
