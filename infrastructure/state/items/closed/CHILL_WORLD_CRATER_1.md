# CHILL_WORLD_CRATER_1 — the live world-tile crater

## what

Card ruling (2026-09-27): when the sarlacc-guts route fires
(CHILL_WARLAB_ROUTES_1's apocalyptic tier), **the lake's world tiles swap to a
new crater biome in-save** — the planet is visibly wounded from orbit,
forever.

Deliverables:
1. A crater BiomeDef (dead glass, no life, its own world-map color).
2. A live tile-swap mechanism: on the detonation event, the Chill's world
   tiles change biome in the running save (plus whatever regeneration/cleanup
   the affected maps need).

## doctrine guards, so this never gets mis-filed

- **A crater BiomeDef with 0 tiles is the EXPECTED state** — it only ever
  gains tiles by the in-game event. Never a finding.
- **This is not worldgen and produces no alternative planets** — it is a
  scripted in-save consequence on THE map, same planet, one wound. The
  no-worldgen law is untouched.
- First bar is **feasibility**: prove a live biome swap on world tiles is
  save-safe (the bridge's world tools do live biome writes + world_commit at
  authoring time; the open question is doing it from game code mid-save,
  and what happens to generated maps, roads and settlements on the swapped
  tiles). Report before building the full event.

## provenance

Decision taken by question card 2026-09-27 (live tile change chosen over
maps-only and defer options). Filed by BENCH out of the Chill concept sitting.

## deliverable 1 — the crater BiomeDef (built 2026-09-28, FOUNDRY)

`RM_ChillCrater` in `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_ChillCrater.xml`,
floor terrain `RM_ChillCraterGlass` (`Defs/TerrainDefs/RM_ChillCraterTerrains.xml`),
placeholder world texture `Textures/World/Biomes/RM_ChillCrater.png`. It is kept out of
worldgen with `generatesNaturally=false` and nothing else. Every flag that affects
neighbours, pathing or links copies the Chill (`impassable`, `canBuildBase=false`,
`allowRoads=true`/`allowRivers=false`, `isBackgroundBiome`). So the swap changes the look
and the life, and nothing else. The header comment gives the engine reason for each flag.
Paint list row added as NO PAINT. Not deployed.

## deliverable 2 — feasibility verdict (desk research, RimSage, 2026-09-28)

**The core swap is already PROVEN live, by another item.** `WAR_LAB_CRATER_HOOK_1`
(`src/RimUtinni/StructureInjectionsRUT/Source/WarLab/WarLabCraterMutation.cs`, 2026-09-11)
does this exact thing from game code: it sets `SurfaceTile.PrimaryBiome` (a public setter)
and then makes the same engine calls `jawa/world_commit` makes, in-process. The 2026-09-24
ledger note on that item records a live run on the real campaign world: 57 of 57
`RUT_PropaneLake` tiles flipped, 0 other tiles touched, and the change survived a
save and reload into a separate test save. `world_commit` is not a bridge-only concept.
Every step in it is an ordinary public engine call.

**What source reading adds (not live-tested):**
- A SURFACE map on a swapped tile changes biome at once. `Map.Biome => TileInfo.PrimaryBiome`,
  and `TileInfo` is `Find.WorldGrid[Tile]` for any map that is not a pocket map, so they
  cannot diverge. Existing terrain, plants, pawns and water bodies stay as they are. New
  wild spawns, weather picks and fishing rare-catches read the new biome. Null `fishTypes`
  would NRE `FishingUtility.GetCatchesFor`, so the crater carries an empty one.
  ⚠️ `jawa/map_info`'s description says tile biome and map biome "diverge after a live
  world_tile_set". Vanilla source says they cannot, unless some mod patches `Map.Biome`,
  which is unmeasured.
- POCKET maps (the dive floors) are untouched. Their biome is `pocketTileInfo`, saved
  per map. But `destroyOnParentMapAbandoned=false`, so a cached Chill floor outlives
  takeoff. The follow-up must `PocketMapUtility.DestroyPocketMap` it. `MapPortal.PocketMap`
  clears itself afterwards.
- Roads and rivers: no change, because the link filters match. Settlements: `canBuildBase=false`
  on the Chill means the engine places none. Sites are UNMEASURED; read `jawa/world_objects_get`
  on the 57 tiles before building. Tile's uncacheable fields (temperature, hilliness label,
  secondary biome) do not depend on the biome. Loading a save without TerminalBiomes falls
  back to the layer's default biome (`PlanetLayer` load) rather than crashing.

**Owed by the follow-up once the Route 1 trigger exists:**
1. Retarget `WarLabCraterMutation.CraterBiomeDefName` from `RUT_Wasteland` to `RM_ChillCrater`.
2. ⛔ `RUT_WarLabReactorCore` + `CompIgniteCraterOnDestroy` fire on ANY destruction of an object
   staged in the war lab layout. That contradicts the spec's no-accidents law. Replace it with the
   deliberate Route 1 arming.
3. Destroy the Chill floor pocket map(s), deciding what happens to pawns inside, and gate the
   swap on `RM_TerminalBiomesSettings.chillEnabled`.
4. Decide how the player reaches the "ripped-open lab" afterwards. The crater is
   `canBuildBase=false`, not a water biome, and impassable, so today nothing can land there.
5. Live checks: swap with a surface map open on the tile, then save and reload, then check
   Player.log and fishing. Also rename the lake's WorldFeature label if the owner wants that.
