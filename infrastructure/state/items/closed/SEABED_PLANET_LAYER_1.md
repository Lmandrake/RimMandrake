# SEABED_PLANET_LAYER_1 — the sea floor as a real planet layer

Ash'karr's four seas get their floors as a **real `PlanetLayerDef`, a geometric twin of the
surface** — same origin, radius, view angle, subdivisions and tile count — instead of
generated `MapPortal` pocket maps. Owner ruling by question card, 2026-09-26.

**Why the old shape was wrong, measured:** `PocketMapProperties.destroyOnParentMapAbandoned`
defaults to `true`, so a gravship takeoff from an unanchored tile already destroyed the sea
floor. And one hatch can only ever hold one floor, because a pocket map has no address. A
layer tile has one, derived from where the ship is — the bug cannot be expressed in this
architecture.

Plan: `/home/mandrake/.claude/plans/glistening-tumbling-moore.md`.
Phase 1 report: `Transient/seabed_layer_phase1_2026-09-26.md`.

## spec

Phase 1 — the layer, offline-provable, no content:

- `RM_SeabedLayer` `PlanetLayerDef` on stock `SurfaceLayer` / `SurfaceTile`.
- Registration from a `GameSetupStepDef` (fresh world) **and** a `WorldComponent.FinalizeInit`
  (every load, so an existing save gains the layer).
- A worldgen step that **mirrors rather than generates**: one `SurfaceTile` per surface tile,
  each populated from the surface tile above it.
- Two-way connections at cost 0 plus zoom links, each set only if currently null.
- `RM_SeabedUnavailable` default biome, `RM_SeabedFloor` placeholder, `RM_SeabedSite` world
  object with `WorldObjectCompProperties_Abandon`.

Built 2026-09-26, in `src/RimMandrake/DivingInteraction/` (`mandrake.rm.divinginteraction`).

## Watch out

- 🔴 **Never build a dictionary or any other ledger pairing surface tiles to floor tiles.**
  Translation is arithmetic — `new PlanetTile(tileId, otherLayer)`. GravTide (the reference
  implementation we harvested technique from) wrote that ledger twice and deleted it twice.
- 🔴 **`PlanetLayer.subdivisions` is private with no accessor and must be READ, never guessed.**
  The `RegisterPlanetLayer` parameter defaults to `10`; a scenario may set anything. A mismatch
  does not fail — it silently pairs seabed tiles with *different places on the planet*. The
  `layer.TilesCount != surface.TilesCount` throw is the only thing that catches it.
- 🔴 **Connection work must be guarded on `Scribe.mode ∈ {Inactive, PostLoadInit}`.**
  `World.FinalizeInit` runs *before* Scribe resolves the saved connection dictionary.
- 🔴 **`MapPlantGrowthRateCalculator.BuildFor(Map)`** takes `map.Tile` to `OutdoorTemperatureAt`,
  which indexes an array by tile id, and throws out of `Map.FinalizeInit` **after** the map is
  in `Find.Maps` — the map never finishes and `MapDrawer` NREs every frame. `MapTemperature`
  and `TileTemperaturesComp` guard for this; that class does not. It is safe in vanilla only
  because Undercave/Space/etc. have zero wild plants between them. **Phase 1 sets
  `plantDensity 0` on both biomes partly for this reason. Phase 3 gives the floor real plants
  and must guard for it first.**
- ⚠️ **`WorldObjectCompProperties_Abandon.ConfigErrors` rejects the def unless
  `worldObjectClass` is a `MapParent`** — the default is plain `WorldObject`.
- ⚠️ Vanilla hardcodes `== PlanetLayerDefOf.Surface` / `== Orbit` in several places
  (`Settlement.cs:448`, `MapParent.cs:153`, `SitePartWorker.cs:73`, `TileFinder.cs:337`,
  `SettlementProximityGoodwillUtility`). Phase 1 touches none of them; later phases will.
- ⛔ `RM_SeaDiveHatch` and the four `RM_SeaDiveGenerator_*` defs are untouched and keep working.
  Phase 2 decides their fate.

## verify

- `dotnet build` of `RM_DivingInteraction.csproj` green, **and** the new type names present in
  the built DLL's metadata (the csproj sets `EnableDefaultCompileItems false`; a file without
  a `<Compile Include>` line compiles into nothing, silently).
- `validate_patch.py` on the new def XML, plus a duplicate-sibling-tag check with a sanity probe.
- **Not yet proven, and only a game load can prove it:** fresh-world registration, load-an-
  existing-save registration, the twin-guard firing or staying quiet against a real grid,
  the connection/zoom links surviving a save-reload round trip, and the two biomes and the
  world object passing `ConfigErrors` at def load.

## later phases

2. Descent and ascent (pilot console destination step, fuel per depth, arrival interception).
3. The floor as a habitable place (dry fertile terrain + water-fill MapComponent, plants,
   animal density, the two fishing fixes).
4. Biomes and content per sea — replaces `RM_SeabedFloor`; each sea's surface biome gains
   `RM_SeabedAccessExtension`.
5. The depth/geology worldgen step, taken with the world remake. Depth is `-elevation`;
   vanilla bottoms the ocean at −500 m, so a usable range needs reshaping at worldgen.
