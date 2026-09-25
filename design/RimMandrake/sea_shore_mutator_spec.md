# Sea shore tile mutator — design spec

Item: `SEA_SHORE_TILE_MUTATOR_1`. Written 2026-09-25 by a design subagent; owner ruling that
started it, verbatim: *"It sounds like a tile mutator would be the true fix so long as no tile
had two different kinds of sea touching it, correct? If so, that's our path."*

Binding context (from `CLAUDE.md`): there is no worldgen feature; the planet is hand-authored,
frozen and painted ONCE at the end; a biome on zero tiles is not a defect; mutator assignment to
tiles is an authoring step at that final painting pass, never generation.

Related: `design/RimMandrake/sea_dive_maps_spec.md` (the sea-floor maps themselves — this spec is
only about the LAND map's coast). Sibling item: `SEA_FLOOR_AND_CATCH_PASS_1`.

Every engine claim below is marked **MEASURED** (read from the decompiled 1.6 source via RimSage on
2026-09-25, file:line cited) or **UNMEASURED**.

## 0. Read first — the mutator ALREADY EXISTS

🔴 **`SEA_SHORE_TILE_MUTATOR_1` (filed 2026-09-25) asks for a thing that was built on 2026-09-23.**
`src/RimMandrake/SeaShores/` is `mandrake.rm.seashores`, commit `fb352d7c6`, recorded in
`SEA_FLOOR_AND_CATCH_PASS_1` under *"(a)–(c) BUILT"*. It is exactly the owner's path: one
`TileMutatorDef` `RM_SeaCoast` whose worker subclasses vanilla `TileMutatorWorker_Coast` and lays the
neighbouring SEA's water instead of the land biome's. This spec therefore does not design a second
mutator; it (1) records the engine facts that justify the existing one, (2) states how it reaches
tiles on a frozen planet, (3) answers the two-seas question with a measurement, and (4) lists the
gaps that are genuinely still open.

| what | state (2026-09-25) |
|---|---|
| `src/RimMandrake/SeaShores/Defs/TileMutatorDefs/RM_SeaCoast.xml` | authored |
| `src/RimMandrake/SeaShores/Source/RM_TileMutatorWorker_SeaCoast.cs` | authored, builds clean, selftest 8/8 (per the sibling item) |
| `src/RimMandrake/SeaShores/Source/RM_WorldComponent_SeaShoreHealer.cs` | authored — the frozen-planet assignment path |
| `src/RimMandrake/SeaShores/Source/RM_SeaShoresHarmony.cs` | `CoastDirectionAt` postfix, `TryAddMutator` prefix, two catch patches |
| DLL in `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\SeaShores\Assemblies\RimMandrakeSeaShores.dll` | deployed 2026-09-23 18:08 |
| `mandrake.rm.seashores` in the LIVE `ModsConfig.xml` | **ABSENT** (parsed 2026-09-25: 627 active; `mandrake.rm.terminalbiomes` present, seashores not) |
| live proof on a map beside a sea | **NONE** — never loaded in the game |

⇒ The item's premise *"today a map beside the Scald gets vanilla ocean"* is true for two reasons at
once: the engine fact in §1, AND the fix is not in the active list. Nothing here is proven live.

## 1. How 1.6 tile mutators work (MEASURED unless marked)

**The def.** `TileMutatorDef : Def` (`Source/RimWorld/TileMutatorDef.cs`). Fields that matter here:
`workerClass` (instantiated once per def via `Activator.CreateInstance(workerClass, this)` — the
`Worker` property caches it, so **one worker instance serves every map**, `TileMutatorDef.cs`
`Worker` getter), `categories`/`overrideCategories`/`priority` (conflict resolution, below),
`genOrder` (sort key on the tile), `chanceOnNonLandmarkTile` (the random roll at worldgen),
`overrideCoastalBeachTerrain` / `overrideLakeBeachTerrain` / `overrideRiverbankTerrain` /
`overrideMudTerrain` (terrain overrides read by `MapGenUtility.BeachTerrainAt` etc.,
`MapGenUtility.cs:210-250`), `biomeWhitelist`/`biomeBlacklist`, `coastSidesRange`, and the density
factors (`animalDensityFactor`, `plantDensityFactor`, `fishPopulationFactor` — multiplied in
`Tile.AnimalDensity` / `Tile.PlantDensityFactor` / `Tile.FishPopulationFactor`, `Tile.cs`).

**The worker.** `TileMutatorWorker` (`Source/RimWorld/TileMutatorWorker.cs`) is abstract with
virtual hooks: `IsValidTile(tile, layer)`, `OnAddedToTile(tile)`, `Init(map)`, `Tick(map)`,
`GetLabel`/`GetDescription`, and the map-generation phases `GeneratePostElevationFertility(map)`,
`GeneratePostTerrain(map)`, `GenerateCriticalStructures(map)`, `GenerateNonCriticalStructures(map)`,
`GeneratePostFog(map)`, plus `MutateWeatherCommonalityFor`, `AnimalCommonalityFactorFor`,
`PlantCommonalityFactorFor`, `AdditionalWildPlants`. Map generation calls these on every mutator
in `map.TileInfo.Mutators` at the matching genstep (the genstep-to-hook wiring itself is
**UNMEASURED** in this pass; the sibling item and `sea_dive_maps_spec.md` §2 rely on the same
assumption and it is the documented 1.6 contract).

**Vanilla's coast.** `TileMutatorWorker_Coast` (`Source/RimWorld/TileMutatorWorker_Coast.cs`):
- `Init(map)`: `coastAngle = GetCoastAngle(map.Tile)`; builds `coastNoise =
  MapNoiseUtility.FalloffAtAngle(angle, CoastOffset 0.1–0.2, map)` plus two displacement layers
  (0.006/30 and 0.015/25).
- `GetCoastAngle(tile)` = `Find.World.CoastAngleAt(tile, BiomeDefOf.Ocean).GetValueOrDefault()` —
  **the vanilla Ocean def by reference, hardcoded**; `protected virtual`.
- `GeneratePostElevationFertility`: every cell with noise `< MaxForDeepWater (0.4)` gets elevation 0.
- `GeneratePostTerrain`: `CoastTerrainAt(cell)` → noise `< 0.4` deep, `< 0.5` shallow, `< 0.6` and
  `ShouldGenerateBeachSand` → beach; written unless the cell is stone (or stone with no edifice and
  the target is water).
- `DeepWaterTerrainAt` / `ShallowWaterTerrainAt` / `BeachTerrainAt` are `protected virtual` and
  delegate to `MapGenUtility.DeepOceanWaterTerrainAt` = `map.BiomeAt(cell).oceanDeepTerrain ??
  WaterOceanDeep`, `ShallowOceanWaterTerrainAt` = `…oceanShallowTerrain ?? WaterOceanShallow`,
  `BeachTerrainAt` = first mutator `overrideCoastalBeachTerrain` else
  `map.BiomeAt(cell).coastalBeachTerrain ?? Sand` (`MapGenUtility.cs:200-220`).
  🔑 **`map.BiomeAt(cell)` is the LAND map's biome** — this is the engine fact behind the item: a
  map beside the Scald lays the land biome's (i.e. vanilla) ocean water, never the Scald's.

**Coast direction and `IsCoastal`.** `World.CoastDirectionAt(tile)` (`World.cs:316-346`) returns
`Rot4.Invalid` unless the tile's `PrimaryBiome.canBuildBase` and at least one neighbour has
`PrimaryBiome == BiomeDefOf.Ocean`; `LakeDirectionAt` is the same shape against `BiomeDefOf.Lake`.
`World.CoastAngleAt(tile, waterBiome)` (`World.cs:303-314`) takes the biome as a parameter — mean
heading of the neighbours whose `PrimaryBiome == waterBiome`, `null` if none — which is why the
override in §1a needs no Harmony. All four of our seas are `impassable`, `canBuildBase false`
(`RM_TheScald.xml`, `RM_GreySea.xml`, `RM_TwilightSea.xml`, `RM_PropaneLake.xml`), so no map is ever
generated ON a sea tile.

**How mutators get onto a tile.** `WorldGenStep_Mutators.AddMutatorsFromTile(layer)`
(`Source/RimWorld/Planet/WorldGenStep_Mutators.cs`) runs once per planet at worldgen (also from
`World.cs:160` and the 1.5 back-compat converter): Mountain for Mountainous/Impassable; Lakeshore if
`LakeDirectionAt` valid (Odyssey) else Coast if `CoastDirectionAt` valid; the river family; Caves by
chance; every def with `chanceOnNonLandmarkTile > 0` by roll; MixedBiome 20 % (Odyssey). Each goes
through private static `TryAddMutator(tile, layer, def)` → `def.IsValidTile` → `tile.AddMutator`.

**`Tile.AddMutator` conflict rule** (`Tile.cs:248-283`): for every existing mutator sharing a
`category` with the incoming one, the existing is **removed if `incoming.priority >=
existing.priority`**, else `Log.Error("Detected mutator conflict…")` and both stay; anything in the
incoming `overrideCategories` is removed unconditionally; the list is re-sorted by `genOrder`;
`Worker.OnAddedToTile` fires. Vanilla `Coast` is category `Coast`, genOrder 100, priority 0
(`Defs/Core/MapGeneration/TileMutators.xml:35-41`); `RM_SeaCoast` copies all three, so adding it to a
tile that carries vanilla `Coast` **replaces it silently** — the property the healer fix in §6
relies on.

**Persistence.** Mutators are saved with the world: per tile as `mutatorDefs` (`Tile.ExposeData`,
`Tile.cs:370`, `LookMode.Def`) and, on the surface layer, as two packed arrays `tileMutatorTiles`
(int) + `tileMutatorDefs` (ushort **shortHash**) (`SurfaceLayer.cs:92,124,247-268`;
`DeserializeMutators` resolves via `DefDatabase<TileMutatorDef>.GetByShortHash` and silently drops an
unknown hash). ⇒ A frozen planet keeps the mutators it had when generated and never re-rolls them;
reading them offline from a `.rws` needs a shortHash table from a dump of the SAME mod set
(`rimworld-savegame` skill).

**`coastSidesRange` and `IsValidTile`** (`TileMutatorDef.cs`, `IsValidTile`): the neighbour count
is taken only over `BiomeDefOf.Ocean`/`BiomeDefOf.Lake`, so any value would refuse a tile beside
our seas; `RM_SeaCoast.xml` leaves it unset and gates in the worker instead. `biomeWhitelist`/
`Blacklist` and the density/temperature/hilliness ranges are read ONLY here, i.e. only at the
moment of adding — the 2026-09-07 freeze note measured the same thing: repainting a biome under an
already-placed mutator is safe.

**Per-edge alternative the item mentions.** `TileMutatorWorker_MixedBiome.Init`
(`TileMutatorWorker_MixedBiome.cs:9-104`) picks ONE neighbour of another whitelisted biome
(tile-seeded shuffle), computes the mean heading of all neighbours of that biome, and splits the
map with a rotated axis plus displacement noise into a `MixedBiomeMapComponent.biomeGrid`. It is a
two-biome split, not an N-sea one, and it is Odyssey-gated — relevant only if §4 ever finds a
two-sea tile.

### 1a. What `RM_SeaCoast` does with the above (read from our source, not the engine)

`RM_TileMutatorWorker_SeaCoast : TileMutatorWorker_Coast` overrides exactly the virtuals that were
wrong: `GetCoastAngle` → `Find.World.CoastAngleAt(tile, thatSea)`; `DeepWaterTerrainAt` /
`ShallowWaterTerrainAt` → the sea's terrain (resolution order in §3); `BeachTerrainAt` → the land's
unless the sea's extension overrides it; `IsValidTile` additionally requires `canBuildBase` and a
sea neighbour. The sea a tile "faces" is `RM_SeaShoreUtility.PrimarySeaFor(tile)`: **the sea biome
holding the most of the tile's neighbours, ties broken by ordinal `defName`** — deterministic, so
two loads lay the same shore. A sea is any BiomeDef carrying `RM_SeaShoreExtension` (fields
`deepTerrain`, `shallowTerrain`, `beachTerrain`, `countsAsCoast`, `providesCatch`, `generateShore`).

## 2. How the mutator gets onto tiles — authoring, never worldgen

The planet is hand-authored, frozen, and will be painted once at the end after a world remake
(`CLAUDE.md`; memory *"World remake is the last step"*). Three routes exist; only the last two apply
to the shipped save.

1. **Fresh worldgen** (`RM_Patch_TryAddMutator` prefix): when `WorldGenStep_Mutators` asks for
   vanilla `Coast` on a tile with no vanilla-Ocean neighbour but a sea of ours, `RM_SeaCoast` is
   substituted. ⚠️ This only fires for seas that are ALREADY on the tiles at generation time. The
   final remake generates a vanilla planet and the seas are painted on afterwards
   (`jawa/world_tile_set` + `world_commit`), so at that moment this route places nothing useful and
   may place vanilla `Coast` beside vanilla oceans that are then painted into our seas. **Do not
   rely on it for the shipped world.**
2. **The painting pass writes the mutator** — `jawa/world_mutators_set` per tile, then
   `jawa/world_commit`, as part of the terminal paint script. This is the authoring step the item
   asks for. Inputs: the painted biome grid + the adjacency graph (§4). Rule: every land tile
   (`canBuildBase`) with ≥ 1 sea neighbour gets `RM_SeaCoast`, and any vanilla `Coast`/`Lakeshore`
   it carries is removed (`AddMutator` does the removal for `Coast` by the priority rule; `Lakeshore`
   is also category `Coast` — **UNMEASURED**: check `Lakeshore`'s category in
   `Defs/Odyssey` before assuming). `jawa/world_mutators_audit` reads back the raw list.
3. **The healer on load** (`RM_WorldComponent_SeaShoreHealer.FinalizeInit`): adds `RM_SeaCoast` to
   every `canBuildBase` tile with a sea neighbour that carries **no Coast-category mutator**,
   logs one line, is idempotent, settings-gated. This is the safety net for any save made before
   route 2 ran — including today's `CANONICAL_ASHKARR_START_2026-09-12.rws`.

🔴 **Defect in route 3 as written, measured against the records.** The current planet was
generated with vanilla oceans/lakes and then repainted into `RUT_*` seas (freeze stamp,
2026-09-07). The 2026-08-24 mutators RECORD (`world/ASHKARR_DRAFT_2026-08-24_mutators.csv`) shows
**99 of the 577 sea-coastal land tiles still carrying vanilla `Coast`** (0 `Lakeshore`; 99 `Coast`
on the whole planet). The healer skips those 99 as *"already coastal"*, `TileMutatorWorker_Coast`
then asks `CoastAngleAt(tile, Ocean)` → `null` → angle **0**, and lays **vanilla ocean water on an
arbitrary side** of the map. That is a RECORD of 2026-08-24 (the 2026-09-07 stamp says the mutator
set was unchanged by that day's writes, but nothing after that is recorded); the live number needs
`jawa/world_mutators_get`. Fix is one line in the healer (§6 step 2): treat a vanilla `Coast` with
no vanilla-Ocean neighbour as replaceable, which `AddMutator`'s priority rule already permits.

Ordering note for route 2: the mutator must be written AFTER the biome paint (it reads neighbours),
and the paint must first strip stale `Coast` where no vanilla Ocean remains (there is none on the
planet today: Ocean 0, Lake 0 on the 2026-09-12 record).

## 3. Per-sea terrain mapping (from the defs in `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/`)

Resolution order in `RM_SeaShoreUtility.DeepTerrainOf/ShallowTerrainOf`: extension field → the
sea's `oceanDeep/ShallowTerrain` → its `waterDeep/ShallowTerrain` → vanilla `WaterOceanDeep/Shallow`.
None of the four sets `ocean*Terrain`.

| sea (RM_ def; RUT_ frozen twin identical) | extension `deepTerrain` / `shallowTerrain` | sea's own `waterDeep` / `waterShallow` (NOT used by the shore) | what the shore lays (deep / shallow) | beach |
|---|---|---|---|---|
| `RM_TheScald` | `RUT_ScaldWaterOceanDeep` / `RUT_ScaldWaterOceanShallow` (`RUT_ScaldWater.xml`) | `RUT_ScaldWaterDeep` / `RUT_ScaldWaterShallow` (+ moving pair) | boiling ocean deep / boiling ocean shallow | land biome's `coastalBeachTerrain ?? Sand` |
| `RM_GreySea` | (empty extension) | none | **vanilla `WaterOceanDeep` / `WaterOceanShallow`** | land's |
| `RM_TwilightSea` | (empty extension) | none | **vanilla `WaterOceanDeep` / `WaterOceanShallow`** | land's |
| `RM_PropaneLake` | `RM_PropaneDeep` / `RM_PropaneShallow` (FlowWorks, `FlowWorks/Defs/LiquidTypes/TerrainDefs/RM_Propane.xml`) | `RM_PropaneLakeDeep` / `RM_SolidPropane` (`RM_PropaneLakeTerrains.xml`) | liquid propane deep / shallow | land's |

Consequences:
- Grey and Twilight shores are **indistinguishable from a vanilla coast** today. `sea_dive_maps_spec.md`
  §3.1 already owes `RM_GreySeaDeep/Shallow` and `RM_TwilightSeaDeep/Shallow` (none exist under
  `src/` yet, checked 2026-09-25) — authoring them and naming them in the extension is what gives
  those two seas a visible identity on the shore. Until then `SeaForCell` also cannot key their
  water by terrain (both resolve to the ambiguous vanilla pair) and falls back to the tile's primary
  sea.
- The Scald has TWO water families on purpose: `RUT_ScaldWater*` (fresh pair, moving pair) for
  rivers/inland and `RUT_ScaldWaterOcean*` for the shore; the extension exists precisely because the
  BiomeDef's `water*` fields name the wrong pair.
- The Propane Lake's `waterShallowTerrain` is a solid crust (`RM_SolidPropane`), while its shore
  lays FlowWorks' liquid `RM_PropaneShallow`. Whether the shore should be crust-then-liquid is a
  design question for the Propane Lake's own sitting, not this spec.
- `TerminalBiomes/About.xml` lists `loadAfter` flowworks/divinginteraction/environmentalhazards but
  **not `mandrake.rm.seashores`**; the extension `<li>` carries `MayRequire="mandrake.rm.seashores"`
  so load order only matters for the `MayRequire` resolution — **UNMEASURED** whether a `MayRequire`
  on a modExtension `<li>` needs the named mod loaded EARLIER; add seashores to `loadAfter` (§6).

## 4. The two-seas rule: the check, and what happens if a tile fails it

**Premise (owner):** no land tile touches two different sea kinds. **Measured on the record: it
holds — 0 tiles.**

Instrument, and what it is evidence for:
- **Adjacency** is `world/world_neighbors_sub7b.csv` (21,872 rows, dumped by `jawa/world_neighbors`
  2026-08-18). The neighbour graph is planet GEOMETRY (seed + subdivisions), not painting; it stays
  valid until the world is remade, and after the remake it must be re-dumped once (same tool).
- **Biome per tile** is the decaying column. `world/ASHKARR_WORLDMAP_tiles.csv` is a RECORD exported
  2026-09-12; per its freeze stamp and `CLAUDE.md` it says what the planet looked like THEN, never
  now. So: a check on the CSV is evidence about the planet **as of 2026-09-12**; the only instrument
  for "now" is the live world (`jawa/world_tile_get` — 100-row cap, so batch — or a fresh export via
  `src/RimMandrake/Utils/ashkarr_rebase_from_save.py` from a fresh save), and at the final painting
  pass the check runs against the painted grid in memory before `world_commit`.

Result on the 2026-09-12 record (python over both CSVs, parsed not grepped; sanity probe: sea tile
counts Scald 312 / Grey 472 / Twilight 607 / Propane 57 — the Scald's 312 matches the 2026-09-07
stamp; Ocean 0, Lake 0):

| | count |
|---|---:|
| land tiles with ≥ 1 sea neighbour | **577** (Twilight 224, Grey 221, Scald 79, Propane 53) |
| land tiles touching **≥ 2 different sea kinds** | **0** |

⚠️ 577 equals the estimate in `SEA_FLOOR_AND_CATCH_PASS_1` because it is the same record and the
same method — agreement, not corroboration. The check script is six lines and belongs in the
terminal paint tooling as a gate, not as a one-off (§6 step 4).

**If a tile ever does touch two seas** (a later repaint could create one): the shipped code does
not fail — `PrimarySeaFor` picks the sea with more neighbours, ties by defName — so the tile gets
ONE sea's water on the mean heading of that sea's neighbours, and the other sea is simply absent
from the map. That is the "majority neighbour" rule the item names. The per-edge alternative
(MixedBiome-style angle split, two waters on one map) would be new C# (`GeneratePostTerrain`
resolving terrain per cell by which sea's falloff it is inside) and is worth nothing while the
count is 0.

**Question for the owner (yes/no):** *If the final painting ever produces a land tile touching two
different seas, is "the sea with more neighbouring tiles wins, the other sea does not appear on that
map" acceptable — so the paint tooling simply REPORTS such tiles and we repaint one neighbour by
hand rather than building a two-water shore?* — Yes ⇒ keep the shipped majority rule, add the
gate; No ⇒ file the per-edge worker as its own item, gated on the first real occurrence.

## 5. Mod Settings (already built, `RM_SeaShoresSettings`)

Four instance-field toggles, defaults = shipped behaviour, each labelled world/map-affecting where
it is:

| setting | default | off means |
|---|---|---|
| `seasCountAsCoast` — *Modded seas count as coastline* | on | only vanilla Ocean makes a tile coastal (no coastal animals, no emerge-from-water, no delta) |
| `generateSeaShores` — *Generate shores on maps beside a modded sea* | on | tile may read coastal but the map lays no water/beach (`ShoreSuppressed` also skips the elevation flatten). Labelled "Affects world and map generation." |
| `seaCatchTables` — *Fish the sea's catch table* | on | land biome's fish, as vanilla |
| `healFrozenWorldOnLoad` — *Repair existing worlds on load* | on | the healer does nothing. Labelled "Affects an existing saved world." |

Nothing to add for this item except the §6 step-2 behaviour, which rides `healFrozenWorldOnLoad`
(no new toggle: replacing a stale vanilla `Coast` is the same repair, not a new mechanic). Per-sea
opt-outs are on the extension (`generateShore`, `countsAsCoast`, `providesCatch`), which is the
right place — a sea that should be scenery only says so on its own def.

## 6. Build steps (each shippable; smallest first)

1. **Put it in the list and prove it.** Add `mandrake.rm.seashores` to the live `ModsConfig.xml`
   (game-down window; DLL already deployed 2026-09-23 — re-deploy with
   `deploy_custom_mods.py --mod SeaShores` if the source moved since) and add it to
   `TerminalBiomes/About.xml` `loadAfter`. Live proof on a land tile beside the Scald
   (`jawa/world_tile_map_generate`): the healer's log line, boiling water at the map edge on the
   Scald's side, a fishing zone accepted, a Scald catch. This is the owed line already in
   `SEA_FLOOR_AND_CATCH_PASS_1`; it closes the "authored, not live-proven" gap.
2. **Healer: replace a stale vanilla `Coast`.** In `RM_WorldComponent_SeaShoreHealer.FinalizeInit`,
   a tile whose Coast-category mutator is vanilla `Coast` AND that has no `BiomeDefOf.Ocean`
   neighbour (`RM_Patch_TryAddMutator.HasVanillaOceanNeighbour`, already public) is healed, not
   skipped — `AddMutator(RM_SeaCoast)` removes the old one by the priority rule. Log the replaced
   count separately. Verify live with `jawa/world_mutators_get` on one of the 99 record tiles.
3. **Grey/Twilight own water.** Author `RM_GreySeaDeep/Shallow`, `RM_TwilightSeaDeep/Shallow`
   (already owed by `sea_dive_maps_spec.md` §3.1) and name them in the two extensions; then
   `SeaForCell` keys their water by terrain and the shore is visibly theirs.
4. **Terminal paint gate.** In the painting-pass tooling: after the biome grid is final and before
   `world_commit`, (i) assert every land tile has ≤ 1 sea kind among its neighbours and print the
   offenders, (ii) write `RM_SeaCoast` via `jawa/world_mutators_set` to every land tile with a sea
   neighbour, (iii) `jawa/world_mutators_audit` the result and diff the count against (ii). Route 3
   then has nothing to do on the shipped save, and its log line reads `healed 0`.
5. **Re-dump adjacency after the remake** (`jawa/world_neighbors path=…`) and re-run the gate.

Not in scope: a two-water shore (§4, only if the owner says No), the Propane crust-vs-liquid shore
question (Propane Lake sitting), the floor/diving half (`sea_dive_maps_spec.md`).

## 7. Open questions for the owner

1. §4 — the yes/no on the majority rule for a hypothetical two-sea tile (today: 0 such tiles).
2. Does step 1 (enable + live-prove SeaShores) happen now, or ride the next cold load? It is the
   only step that needs the game.
