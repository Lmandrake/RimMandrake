# world_tile_map_generate no longer returns a map with a stale render

## spec
`jawa/world_tile_map_generate` (`JawaBenchSocietyTools.cs`, method `WorldTileMapGenerate`)
used to return as soon as `GetOrGenerateMapUtility.GetOrGenerateMap` handed back a `Map`,
on BOTH the fresh-generation branch and the `wasAlreadyGenerated=true` idempotent-reuse
branch. Nothing in that path guaranteed `regionAndRoomUpdater.Enabled`, region/room state,
or the draw meshes were consistent with the map's actual current contents — so destroyed
plants and converted terrain (done by an EARLIER caller, via a different tool, before this
call reused the same map) could keep rendering as alive/unconverted. Any visual verdict
(a screenshot, an "does this look right" check) taken on a bridge-generated map without a
prior `jawa/map_commit {redraw:true, full:true}` was unreliable.

## fix
Extracted `jawa/map_commit`'s finalize sequence into a shared private helper,
`RunMapFinalizeSteps(map, regions, pathing, power, redraw, full)`, in
`JawaBenchMapTools.cs` (same partial class, `JawaBenchTerrainTools`, same namespace
`JawaBench.BridgeTools`). `MapCommit` now calls it with its own tool parameters —
behaviour unchanged, same steps in the same order. `WorldTileMapGenerate` now calls the
same helper — unconditionally, on both branches, right before it returns — with
`regions=true, pathing=true, power=true, redraw=true, full=true` (matching the exact
sequence named in the defect: enable the updater, `RebuildAllRegionsAndRooms`,
`RegenerateEverythingNow`). Result now carries `mapFinalize{failedSteps, steps[]}` so a
caller can see it ran and whether any step failed, the same shape `map_commit` already
returns.

Ran unconditionally on the reuse branch too, not only fresh generation: that is exactly
the path a stale render was proven possible on, since a fresh `MapGenerator.GenerateMap`
already calls `Map.FinalizeInit()` (confirmed via RimSage read of `Verse/Map.cs` —
`FinalizeInit` sets `regionAndRoomUpdater.Enabled = true` and calls
`RebuildAllRegionsAndRooms()` itself), but the idempotent-reuse branch
(`Current.Game.FindMap(tile)` already non-null) skips `GenerateMap`/`FinalizeInit`
entirely and hands back whatever state an earlier edit left behind.

Shared code, not duplicated: the two call sites' preconditions differ only in which
sub-steps they expose as caller-tunable (`map_commit` exposes all five knobs to the
caller; `world_tile_map_generate` always wants the full sequence), which is exactly the
shape a shared helper with boolean parameters covers cleanly — no need for two independent
step lists that could drift apart.

`RegionAndRoomUpdater.Enabled` semantics confirmed via RimSage before touching it:
default `true`; vanilla itself toggles it `false` during bulk/rock/space gen steps and
sets it back `true` afterward (`GenStep_RocksFromGrid`, `GenStep_Space`,
`GenStep_ReserveGravshipArea`, `Map.FinalizeInit`, `Map.cs:1240` on map removal). Setting
it `true` unconditionally here matches every one of those call sites' "finished editing,
turn it back on" pattern — never toggled off by this change.

## verify
`python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py` (plan-only, no
`--apply` — the game's up/down state was not checked further since this pass never
deploys): **Build succeeded, 0 Warning(s), 0 Error(s)**.

Deploy + live proof still owed (companion DLL cannot be written while RimWorld is
running; this pass is build-only by design). At the next natural shutdown window:
1. `taskkill.exe /F /IM RimWorldWin64.exe`
2. `python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py --apply`
3. Launch, generate a world-tile map via `jawa/world_tile_map_generate`, destroy a plant
   or convert terrain on it via an existing tool, call `jawa/world_tile_map_generate`
   again on the SAME tile (hits the `wasAlreadyGenerated=true` branch) with no
   intervening `jawa/map_commit` call, screenshot, and confirm the destroyed
   plant/converted terrain now RENDERS correctly — i.e. that this call alone did the job
   `map_commit` used to have to be called separately for.

## criteria
- [x] both methods' real implementations read in full (not guessed)
- [x] `RegionAndRoomUpdater` enable/disable semantics confirmed via RimSage before editing
- [x] shared finalize sequence extracted, `map_commit` behaviour unchanged
- [x] `world_tile_map_generate` runs the same sequence unconditionally before returning
- [x] build: 0 warnings, 0 errors
- [ ] deployed to the live game
- [ ] live-proven: destroy/convert + re-call + screenshot with no separate map_commit
