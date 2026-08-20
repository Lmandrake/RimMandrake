# The worldmap bridge surface — every element, and read/write/validate for each

**CHECK owns this.** Owner's order, 2026-08-19: enumerate everything a WORLDMAP contains,
then build read / write / validate capability for all of it, grouped sensibly, tested
against a minimal mod list so reloads are cheap.

Source of truth for every type and signature below is the RimWorld 1.6 (Odyssey) source
read through RimSage, not model memory. Facts marked ⚠️ are inferred and must be proven
live before anything depends on them.

---

## 0. The four facts that shape the whole design

**1. Tile storage is per-LAYER, not on `WorldGrid`.** `WorldGrid` delegates to
`PlanetLayer`; `PlanetLayer.tiles` is the real `List<Tile>`. `WorldGrid[int]` is the
SURFACE indexer and returns `SurfaceTile`; `WorldGrid[PlanetTile]` is layer-qualified.
`TilesCount` is surface-only. 1.6 has 3 `PlanetLayerDef`s: Surface, Orbit, Orbit2.

**2. There is no per-tile visual invalidation except pollution.** Every other change
forces a whole `WorldDrawLayer` mesh regeneration. There is no `Notify_TileChanged`,
no dirty flag, no `Notify_BiomeChanged`. This is why bulk-then-regenerate is the only
sane shape for a writer.

**3. 🔴 `Tile`'s own private caches are NEVER invalidated by anything in the codebase.**
`hillinessLabelCached`, `cachedMaxTemp`, `cachedMinTemp`, `tmpHasSecondaryBiome`,
`tmpSecondaryBiome` are set lazily on first read and have **no reset method anywhere**.
If anything has already read `HillinessLabel`, `MinTemperature`, `MaxTemperature` or
`Biomes` on a tile, changing `hilliness` / `temperature` / `PrimaryBiome` afterwards
leaves the stale value for the rest of the session.
⇒ **Write before anything reads, or reload.** Our validators must therefore read back
the RAW FIELDS, never the cached properties — a validator built on `HillinessLabel`
would confirm its own writes while the planet stayed wrong.

**4. `OverlayRoad` / `OverlayRiver` cannot REMOVE.** Passing null logs `ErrorOnce`.
Lower-priority overlays are silently refused (`road.priority`, `river.degradeThreshold`).
Removal and downgrade require editing `SurfaceTile.potentialRoads` / `potentialRivers`
directly, on BOTH endpoints. That is a capability we must build, not one we inherit.

---

## 1. PER-TILE SCALARS — `RimWorld.Planet.Tile`

All public settable fields unless noted.

| element | member | type | notes |
|---|---|---|---|
| biome | `PrimaryBiome` | `BiomeDef` | **property, get/set**, wraps private `biome`. 80 defs |
| elevation | `elevation` | `float` | default 100. `WaterCovered => elevation <= 0` on SurfaceTile |
| hilliness | `hilliness` | `Hilliness` | **enum, not a def**. Read back raw — `HillinessLabel` is cached |
| temperature | `temperature` | `float` | default 20 |
| rainfall | `rainfall` | `float` | |
| swampiness | `swampiness` | `float` | |
| pollution | `pollution` | `float` | ⭐ the ONE element with an incremental renderer path |
| feature | `feature` | `WorldFeature` | the named region this tile belongs to |
| tile id | `tile` | `PlanetTile` | readonly struct: `tileId` + `layerId`; implicit to/from int |
| mutators | `mutatorsNullable` | `List<TileMutatorDef>` | use `AddMutator`/`RemoveMutator`, not the list |

**Derived, read-only, and all of them lie after an edit** (see fact 3): `Biomes`,
`Layer`, `Landmark`, `Mutators`, `OnSurface`, `WaterCovered`, `IsCoastal`,
`HillinessLabel`, `HillinessForElevationGen`, `HillinessForOreGeneration`,
`AnimalDensity`, `PlantDensityFactor`, `FishPopulationFactor`, `AllowRoofedEdgeWalkIn`,
`MaxTemperature`, `MinTemperature`, `MaxFishPopulation`.

## 2. PER-TILE LINKS — `RimWorld.Planet.SurfaceTile : Tile`

```csharp
public struct RoadLink  { public PlanetTile neighbor; public RoadDef  road;  }
public struct RiverLink { public PlanetTile neighbor; public RiverDef river; }
public List<RoadLink>  potentialRoads;    // settable field
public List<RiverLink> potentialRivers;   // settable field
public int riverDist;                     // settable field
public List<RoadLink>  Roads  => PrimaryBiome.allowRoads  ? potentialRoads  : null;
public List<RiverLink> Rivers => PrimaryBiome.allowRivers ? potentialRivers : null;
```

🔴 **`Roads` and `Rivers` are FILTERED VIEWS.** A biome with `allowRoads=false` HIDES
existing links without deleting them. A validator reading `Rivers` will report a river
missing when it is present but suppressed by the biome we just painted underneath it.
**Read `potentialRivers` / `potentialRoads` to validate; read `Rivers` / `Roads` to
answer "what does the player see".** These are different questions and we need both.

Writers: `WorldGrid.OverlayRiver(from,to,def)` / `OverlayRoad(from,to,def)` write BOTH
endpoints symmetrically and no-op silently if either tile is not a `SurfaceTile`.
`OverlayRiver` also maintains `riverDist = max(riverDist, other.riverDist + 1)`.
Rivers must be laid **mouth first, then upstream** (§12).
Defs: 4 `RiverDef` (Creek/River/LargeRiver/HugeRiver), 5 `RoadDef`.

## 3. LANDMARKS — 1.6, Odyssey-gated

```csharp
class Landmark { public LandmarkDef def; public string name; public bool isComboLandmark; }
class WorldLandmarks { public Dictionary<PlanetTile, Landmark> landmarks;
                       Landmark this[PlanetTile] { get; set; }        // get returns null if absent
                       void AddLandmark(LandmarkDef, PlanetTile, PlanetLayer=null, bool forced=false);
                       void RemoveLandmark(PlanetTile); }
```
Reached at `Find.World.landmarks`. `Tile.Landmark` returns **null when
`!ModsConfig.OdysseyActive`** — so a minimal mod list that drops Odyssey silently
removes every landmark. 113 `LandmarkDef`. `AddLandmark` also rolls the def's
`mutatorChances` / `comboLandmarkMutators` onto the tile, so adding a landmark is
ALSO a mutator write.

## 4. TILE MUTATORS — 336 defs, the largest surface

`Tile.AddMutator(def)` resolves category conflicts, sorts by `genOrder`, and calls
`def.Worker?.OnAddedToTile(tile)`. `Tile.RemoveMutator(def)`. Never write
`mutatorsNullable` directly — the worker callback is where the side effects live.

## 5. RENDERER — what makes an edit visible

Vanilla's own debug tools, verbatim:
```csharp
// after biome change   (DebugToolsMisc.SetBiome)
Find.World.renderer.GetLayer<WorldDrawLayer_Terrain>(PlanetLayer.Selected).RegenerateNow();
// after landmark add   (DebugToolsMisc / DebugActionsMisc)
Find.World.renderer.GetLayer<WorldDrawLayer_Terrain>  (tile.Layer)           .RegenerateNow();
Find.World.renderer.GetLayer<WorldDrawLayer_Landmarks>(Find.WorldGrid.Surface).RegenerateNow();
Find.World.renderer.GetLayer<WorldDrawLayer_Hills>    (Find.WorldGrid.Surface).RegenerateNow();
// pollution only, incremental
Find.World.renderer.Notify_TilePollutionChanged(planetTile);
```
Whole-planet rewrite: `SetAllLayersDirty()` (async next frame) or
`RegenerateAllLayersNow()` (synchronous).
⚠️ `WorldDrawLayer_Roads` / `_Rivers` follow the same pattern but **no vanilla call site
exists** — inferred from `WorldDrawLayer_Paths` subclassing. PROVE THIS LIVE.

Non-visual caches that must also be cleared after a bulk write:
* `layer.FastTileFinder.DirtyCache()` / `.DirtyTile(tile)` — else site and settlement
  tile queries keep the old biome and landmark.
* `Find.WorldPathGrid.RecalculateLayerPerceivedPathCosts(layer)` — movement difficulty
  is a cached `float[]` built from `PrimaryBiome.impassable` / `movementDifficulty` and
  `hilliness`. Self-clears `Find.WorldReachability.ClearCache()` when passability flips.

---

## 6. NAMED REGIONS — `WorldFeatures` / `WorldFeature`

```csharp
class WorldFeatures { public List<WorldFeature> features; public bool textsCreated;
                      WorldFeature GetFeatureWithID(int); void UpdateFeatures(); }
class WorldFeature { int uniqueID; FeatureDef def; PlanetLayer layer; string name;
                     Vector3 drawCenter; float drawAngle; float maxDrawSizeInTiles; float alpha;
                     IEnumerable<int> Tiles;   // SCANS every tile for tile.feature == this
                     ctor(FeatureDef, PlanetLayer) }
```
🔑 **Tile membership is stored ON THE TILE (`Tile.feature`), not in the feature.** So
assigning a region = writing `feature` on each member tile. `WorldFeature.Tiles` is a
full-grid scan, i.e. O(n) per feature — do not call it in a loop over 24 regions.

`drawCenter` and `maxDrawSizeInTiles` are computed by `FeatureWorker.AssignBestDrawPos`
(flood-fill inward from edge tiles, deepest tile nearest the centroid,
`maxDrawSizeInTiles = bestTileDist * 2 * 1.2`). **`drawAngle` is never set by the
generator** — it stays 0 and is applied as `Quaternion.Euler(Vector3.forward * (90 - drawAngle))`.
⇒ We get label placement control vanilla never uses. 36 `FeatureDef`.

## 7. WORLD OBJECTS — settlements and everything else on the globe

`Find.WorldObjects` (`WorldObjectsHolder`): `Add` / `Remove` / `Contains`;
`AllWorldObjects`; typed lists `Settlements`, `SettlementBases`, `Sites`, `Caravans`,
`MapParents`, `DestroyedSettlements`, `PeaceTalks`; `ObjectsAt(PlanetTile)`,
`WorldObjectAt<T>(PlanetTile)`, `SettlementAt(...)`, `AllSettlementsOnLayer(layer)`.

Creation is two steps:
```csharp
var wo = WorldObjectMaker.MakeWorldObject(def);   // sets def, ID, creationGameTicks, PostMake()
wo.Tile = tile;  wo.SetFaction(faction);  ((Settlement)wo).Name = "...";
Find.WorldObjects.Add(wo);                         // placement is separate
```
`Settlement : MapParent, ITrader, INameableWorldObject` — `Name` get/set (backing
`nameInt`), `namedByPlayer`, `trader`, `previouslyGeneratedInhabitants`.
🔴 **A `Settlement` whose faction is null on load is DESTROYED with a warning.** Our 72
holdings must each carry a live faction before the owner saves, or they vanish on reload.
132 `WorldObjectDef`.

## 8. WORLD INFO — `Find.World.info`

`name`, `planetCoverage`, `seedString`, `persistentRandomValue`, `overallRainfall`,
`overallTemperature`, `overallPopulation`, `landmarkDensity`, `initialMapSize`,
`List<FactionDef> factions`, `pollution`. `Seed => GenText.StableStringHash(seedString)`.

🔴 **`overallPopulation` and `landmarkDensity` are NOT scribed** — they do not survive
save/load. Anything we set there is lost the moment the owner reloads. Do not build a
capability that depends on them persisting.

## 9. LAYERS — and where they come from

🔴 **Planet layers are created from the SCENARIO, not from worldgen parameters.**
`WorldGrid.CreateRequiredLayers()` walks `Find.Scenario.AllParts` for
`ScenPart_PlanetLayer`. `Find.Scenario.surfaceLayer` becomes the root surface.
⇒ A minimal mod list must not disturb the scenario, or the layer set changes underneath us.
3 `PlanetLayerDef` (Surface, Orbit, Orbit2). Surface genSteps in order: Terrain, Lakes,
Rivers, Mutators, Landmarks, AncientSites, AncientRoads, Pollution, Factions, Roads, Features.

## 10. ORDERING CONSTRAINTS discovered in source

1. **Landmarks before settlements — but NOTHING ENFORCES IT.**
   🔴 **CORRECTED 2026-08-19 by live measurement.** `LandmarkDef.IsValidTile` does reject a
   tile holding a settlement (also impassable biome/hilliness, an existing landmark, and
   `TileMutatorDef.preventsLandmarks`) — but **`WorldLandmarks.AddLandmark` never calls it.**
   Measured: on settlement tile 63540, `IsValidTile` returned **False** with
   `settlementAtOrAdjacent True`, and `AddLandmark` **added the Oasis anyway**.
   ⇒ `IsValidTile` is the GENERATOR's placement rule, not a guard on the setter. The
   ordering constraint is real but it is **ours to enforce**; nothing will stop us
   stacking a landmark on a settlement, and there is no error when we do.
   `jawa/world_landmarks_set` therefore reports the verdict in `validity[]` and leaves
   the decision to the caller.
2. **Biome before links.** `Roads`/`Rivers` are filtered by `PrimaryBiome.allowRoads` /
   `allowRivers`; painting a biome after laying a river can hide the river.
3. **Rivers mouth-first**, so `riverDist` accumulates correctly.
4. **Everything before anything reads a cached property** (fact 3).
5. **Roads cost nothing to the path grid** — the road multiplier is computed live in
   `GetRoadMovementDifficultyMultiplier`, not cached in `layerMovementDifficulty`. Only
   `WorldReachability` and the draw layers need clearing after a road change.

---

## 11. THE TOOL GROUPS — read · write · validate

| # | group | tools | notes |
|---|---|---|---|
| G1 | tile scalars | `world_tile_get` · `world_tile_set` · `world_tile_import` · `world_tile_validate` | the 21,872-tile core |
| G2 | links | `world_links_get` · `world_links_set` · `world_links_clear` · `world_links_import` · `world_links_validate` | ⭐ `_clear` is capability vanilla LACKS |
| G3 | mutators + landmarks | `world_mutators_get/set` · `world_landmarks_get/set` | 336 + 113 defs |
| G4 | features | `world_features_get` · `world_features_set` | incl. `drawAngle`, which vanilla never sets |
| G5 | world objects | `world_objects_get` · `world_objects_set` · `world_objects_add/remove` · `world_settlements_import` | faction must be non-null |
| G6 | info + layers | `world_info_get/set` · `world_layers` | 2 fields do not persist |
| G7 | **commit** | `world_commit` | the invalidation recipe from §5. Without it every write is invisible |
| G8 | lint | `world_lint` | the owner's sanity pass, run in-engine |

**Design decisions, and the reasons:**
* **Import tools take a FILE PATH, not an ops string.** The existing batch convention is a
  semicolon-separated `string ops` capped at `MaxOps = 4096`; 21,872 tiles would need ~6
  calls and a multi-megabyte socket payload. The file already writes CSVs
  (`world_tile_export`) — reading one back is symmetric. ⚠️ There is **no CSV-reading
  code anywhere in the companion today**; this is new capability, deliberately.
* **Every group gets a validate that reads RAW FIELDS**, never cached properties, and for
  links reads `potentialRivers`/`potentialRoads` rather than the biome-filtered views.
* **`world_commit` is separate from every writer.** Regenerating a draw layer per write
  would be pathological over 21,872 tiles; and it is the one place the renderer recipe
  lives, so it can be fixed once.

---

## 12. MEASURED LIVE, 2026-08-19 — what the source read did not tell us

Everything above came from source. These came from the running game and are the facts
that source alone would have got wrong.

* ✅ **The renderer recipe is confirmed end to end.** All 8 commit steps succeed,
  including `WorldDrawLayer_Roads.RegenerateNow` and `_Rivers` — which the source read
  could only mark ⚠️ UNCERTAIN because vanilla has no call site for them. Proven.
* ⚡ **Writing all 21,872 tiles takes 0.1 seconds** and reading them back to validate takes
  about as long. Bulk world editing is not expensive; the expensive part was always the load.
* 🔴 **`BiomeDef.allowRivers` / `allowRoads` do not exist in the offline def dump.** All 80
  biomes report neither field, yet live they are `False` on `Ocean`, `IceSheet` and
  `GlacialPlain`. **This question cannot be answered offline.**
* 🔴 **Biome-hiding is common, not theoretical.** An untouched quicktest world carries 20+
  tiles whose rivers or roads exist in `potential*` and are invisible because the biome
  forbids them. Paint water over a river and the river is still there, silently.
* 🔴 **A contiguous tile-ID range is NOT a contiguous region on the globe.** Painting ids
  20000–23999 produced scattered rosettes; importing ids 0–21871 into a 119,904-tile grid
  produced a hard diagonal seam. Anything geographic must go through the neighbour graph,
  never id arithmetic.
* ⚠️ **`CameraJumper.TryShowWorld()` returns false unless `ProgramState == Playing`**, and
  `start_debug_game_ready` at `readiness=mapData` does not guarantee that. Wait for Playing.
* ⚠️ **The debug log has Auto-open ON and reopens on any warning**, obscuring screenshots.
  Close-and-recheck in a loop immediately before every capture.
* ⚠️ **`rimworld/search_debug_actions` timed out at 30s even on the 13-mod list.** The
  documented debug-discovery hang is not only a heavy-modlist problem. Do not call it.
* 🔑 **`build.py --apply` without `--gm` silently drops `jawa/fire_incident` and
  `jawa/send_letter`.** It refuses and names them, but the flag must be `--gm --apply`.
