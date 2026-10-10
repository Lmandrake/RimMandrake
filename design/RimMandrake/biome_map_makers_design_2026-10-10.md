# Per-biome map-makers + landform mutators — design draft (2026-10-10)

Items: `BIOME_MAP_GENERATORS_DESIGN_1` (thrust 2) and `MAP_LANDFORM_MUTATORS_DESIGN_1` (thrust 1).
Ruled by question card 2026-10-10 02:00 (decision taken by question card, no quote):
- **Landforms are OUR OWN tile mutators**, force-placed on a chosen tile at the final painting pass,
  copying `mandrake.rm.seashores`. Not third-party landform data files (not the GL-graph emitter route).
- **One map-maker per biome**: each biome gets its own hand-built landing-map logic, not a shared
  weighted kit.

Scope: the LOCAL map made when a gravship lands. Nothing here generates, varies or rolls the planet
(CLAUDE.md no-worldgen ruling). `chanceOnNonLandmarkTile` stays 0 on every def below, so nothing
is ever placed by chance. Tiles get a landform by hand at the one painting pass, the same way they get a biome.

## 1. What exists (MEASURED)

### 1.1 Engine (RimSage, decompiled 1.6, read 2026-10-10)
- **The map generator is picked by the world object, not by the biome.** `MapParent.MapGeneratorDef`
  is `def.mapGenerator ?? Encounter`. `Settlement` uses its own def's generator. `BiomeDef` has no
  generator field. Only pocket maps choose a generator directly (`pocketMapProperties.biome`). So
  "a MapGeneratorDef per biome" **is not available** for surface landings without patching
  `MapParent`. ⇒ The biome-level levers are the two lists below.
- `MapGenerator.GenerateMap` builds the step list as follows: `mapGenerator.genSteps`, plus each tile
  mutator's `extraGenSteps`, plus **`map.Biome.extraGenSteps`**. It then removes
  **`map.Biome.preventGenSteps`** and each mutator's `preventGenSteps`, appends the caller's extra
  steps (gravship landing adds `ReserveGravshipArea`), and runs `Distinct()`. It calls every
  mutator's `Worker.Init(map)` before any step runs.
- `TileMutatorDef` fields that matter here: `workerClass`, `genOrder`, `categories`,
  `overrideCategories`, `priority`, `chanceOnNonLandmarkTile`, `extraGenSteps`, `preventGenSteps`,
  `preventNaturalElevation`, `preventPatches`, `hillinessForElevationGen`,
  `biomeWhitelist`/`biomeBlacklist`, `terrainPatchMakers`, and the density factors. `IsValidTile`
  refuses a tile that already holds a mutator in the same category with priority >= this one.
- `TileMutatorWorker` hooks: `Init`, `GeneratePostElevationFertility`, `GeneratePostTerrain`,
  `GenerateCriticalStructures`, `GenerateNonCriticalStructures`, `GeneratePostFog`, `Tick`,
  `IsValidTile`, `OnAddedToTile`, and label, description, weather, animal and plant factors.
- GenStep order table: `map_content_injection_research.md` §5.1. Elevation is set at 10–20,
  terrain at 200–240, critical structures at 500, **`ReserveGravshipArea` at 600**, ruins at
  700–750, plants and scatter at 900–970, animals at 1200, fog at 1500. A throwing GenStep logs
  `Error in GenStep` and the next step runs anyway (§5.1).

### 1.2 The sea-shore mutator, the template (`src/RimMandrake/SeaShores/`, spec `design/RimMandrake/sea_shore_mutator_spec.md`)
- `Defs/TileMutatorDefs/RM_SeaCoast.xml`: a drop-in twin of vanilla `Coast` (same category, genOrder 100,
  priority 0). Worker `RM_TileMutatorWorker_SeaCoast : TileMutatorWorker_Coast` overrides only
  `IsValidTile`, `Init`, the coast angle, the deep/shallow/beach/coast terrains,
  `GeneratePostElevationFertility` and the label/description.
- Per-sea data sits on the BiomeDef as `RM_SeaShoreExtension`, not in the worker.
- **How it is forced onto a tile:** spec §4 route 2 says the painting pass writes it with
  `jawa/world_mutators_set` and then `jawa/world_commit`, and reads it back with
  `jawa/world_mutators_audit`. Route 3 is `RM_WorldComponent_SeaShoreHealer.FinalizeInit`, a
  settings-gated, idempotent repair for saves made before route 2. Route 1, the Harmony substitution
  at worldgen (`RM_Patch_TryAddMutator`), is not used for the shipped world.
- Shipped with `RM_SeaShoresSettings` (heal-on-load toggle), `validation.py`, a selftest and a
  fuzz harness. This is the shape every landform copies.
- Other own mutators exist as hand-placed flags: `RUT_FallLine` (chance 0, no gensteps, "placed by
  hand") and `RUT_LandmarkIconOnly`.

### 1.3 Per-biome map-gen hooks already in our biome mods (parsed from `Biomes.compose.json` members)
These are the seeds of each map-maker. None of them builds a biome's macro shape yet:
- **`extraGenSteps` in use:** Abyss (3), BlueDesert (1), Contagion (1), FloodedCanyon (1),
  LanternDeeps (1), LeaningScrub (1), LongShade (4), Miasma (1), NightsideIce (1), Pyrelands (1),
  Stillsand (1), TheRot (1), **Warscar (15**, including vanilla `CratersLarge/Medium/Small`),
  Wasteland (1). Most are the shared `RM_WreckField_<Biome>`.
- **GenStepDefs that some BiomeDef `extraGenSteps` does not list.** These are reached by another
  route (patch, C# or modExtension; UNMEASURED per file): FeverWood (4), FloodedCanyon
  `RM_FloodedCanyon_MercyLedges` and `_FossilStrata`, GelatinousSlime (3), Greentide (2),
  RustCathedral (4), TheSump (2), Webwork (2), Stillsand `RM_PreciousCaves`, TerminalBiomes (13).
- **C# that already touches the elevation, terrain or rock grids at gen time:**
  `FloodedCanyon/Source/RM_MercyLedges.cs` and `RM_FossilStrata.cs`,
  `Stillsand/Source/RM_PreciousCaves.cs` and `TerminalBiomes/Source/RM_GenStep_TwilightChannels.cs`.
  `EnvironmentalHazards/Source/RM_GenStep_GradientAxis.cs` (Miasma) does a gradient repaint.
- **No surface BiomeDef sets `preventGenSteps`.** Each one runs vanilla `ElevationFertility` and
  `Terrain` and then decorates on top. That is the gap this design closes.
- **MapGeneratorDefs we own are all pocket maps:** `LanternDeeps/RM_LanternDeepGenerator`,
  `DivingInteraction/RM_SeabedGenerators` and `RM_SeaDiveGenerators` (4 each). The seas' floor maps are
  therefore ALREADY one generator per sea.

### 1.4 Third-party landform mods
- The live `ModsConfig.xml` (565 active, parsed 2026-10-10) carries `m00nl1ght.geologicallandforms`,
  `…geologicallandforms.biometransitions`, `m00nl1ght.mappreview`, `zylle.mapdesigner`.
- GL Harmony-patches `TerrainPatchMaker`. On a tile with a GL landform, the landform's graph can
  overwrite the biome's terrain. See `src/RimUtinni/UtinniPatches/Patches/JawaTerrain_SaltPans.xml`
  header and research §5.8: a custom GL landform gets no TileMutatorDef, so it **cannot be forced
  per tile**. With Odyssey active, GL disables 14 of its own landforms.
- `RM_LanternDeeps.xml` deliberately carries no GL modExtension, because a donor type discards the
  whole def. **None of our BiomeDefs depends on GL.**
- Offline tools to keep: `src/RimMandrake/Utils/rimbench/{mapgen_v0,mapgen_paint,render_terrain,corpus_stats}.py`.
  `gl_emit.py` is now reference only, because the card ruled out the data-file route.

## 2. Architecture

### 2.1 Two layers, one contract
| layer | owns | runs at | lives in |
|---|---|---|---|
| **Landform** (thrust 1) | the macro heightfield: canyon cut, crater bowl, plateau and cliff line, sinkhole | `GeneratePostElevationFertility` (after vanilla elevation, before rock and terrain) | `TileMutatorDef` + worker, one per landform, in a new kit `RimMandrake.Landforms` composed into `mandrake.rm.biomes` like `SeaShores` |
| **Map-maker** (thrust 2) | everything that makes the biome read as itself: its elevation character where the biome owns one, its terrain language, its water, its set pieces | its own GenSteps, slotted around the vanilla order table | the biome's own folder: `src/RimMandrake/<Biome>/Defs/MapGeneration/RM_<Biome>_MapMaker.xml` + `Source/RM_<Biome>MapMaker.cs` |

**The contract:** a landform shapes the ground and stamps a read-only mask, `RM_LandformMask`, which
records the floor, the rim/wall and the interior. It holds it in a `MapGenerator` var such as
`GetOrGenerateVar<…>("RM_Landform")`, pending the RimSage check in §4. The map-maker reads
`map.TileInfo.Mutators` and that mask and **adapts to it**. A flooded-canyon map-maker on a Crater
tile floods the bowl and not a slot. Neither layer may write the other's cells after its own slot.

### 2.2 How "one map-maker per biome" is expressed
- The map generator is chosen per world object (§1.1), so **the per-biome entry point is the BiomeDef
  itself.** `extraGenSteps` lists the biome's own steps. `preventGenSteps` removes vanilla steps the
  biome replaces, for example `ElevationFertility` for a biome whose elevation is hand-built, or
  `Terrain`. This is pure XML, needs no Harmony and is already used by 14 biomes.
- **Each biome's logic is its own C#**, in its own assembly, with its own parameters. It is not a
  shared chooser with weights. The shared code is **utilities only**: noise and fbm, mask stamping,
  the `UsedRects` guard, "keep a flat buildable landing patch", and a terrain set-batch helper. It
  goes in a small static library in the Biomes shell assembly and makes no choices about any
  biome's shape.
- **Typical map-maker step set** (order numbers are proposals):
  - `RM_<Biome>_Shape`, order 12–19. A biome-owned elevation pass, or a modifier of vanilla's. It
    runs after a landform worker, so it sees the landform.
  - `RM_<Biome>_Ground`, 215–235. Terrain language beyond `terrainsByFertility` and
    `terrainPatchMakers`.
  - `RM_<Biome>_Pieces`, < 600 when the ship lands around them, > 600 when they must avoid
    `UsedRects`. These are the sheet's field-8 objects. The existing scatter GenSteps fold in here
    unchanged.
- **Gravship invariant:** a map-maker must leave a landable area. `ReserveGravshipArea` runs at 600
  and needs room. UNMEASURED: what it does when there is none. Every map-maker's first script checks
  this (§4).
- Pocket-map biomes (LanternDeeps, the four seabed floors) already have their own MapGeneratorDef.
  Their map-maker IS that generator, and no new entry point is needed.

### 2.3 Landform mutators, how they are authored and force-placed
- **One `TileMutatorDef` per landform.** Fields: `categories` = `RM_Landform`, so a tile holds at most
  one; `chanceOnNonLandmarkTile` = 0; `genOrder` before biome steps; `preventNaturalElevation` or
  `hillinessForElevationGen` where the shape needs it; `biomeWhitelist`/`biomeBlacklist` to stop a
  landform being painted where a biome sheet bans it (field 6). Worker:
  `RimMandrake.Landforms.RM_TileMutatorWorker_<Name>`. Parameters such as depth, width, wall
  steepness and rim height go in a `DefModExtension` on the def, as the sea data sits on
  `RM_SeaShoreExtension`. **Each landform is hand-written code. There is no generic "stamp a file"
  worker.**
- **Collisions:** Odyssey's own `Valley`, `Plateau`, `Cliffs`, `Basin` and similar use their own
  categories. Ours set `overrideCategories` for the vanilla terrain-shape categories they replace
  (UNMEASURED: the exact category strings, to be read from `Data/Odyssey/Defs/TileMutators/` before
  authoring). A tile painted with ours must not also roll a GL landform: §3 Q2.
- **Force-placing:** at the single painting pass (`BIOME_PAINT_ONCE_AT_THE_END_1`), a
  `world/landform_paint_list.csv` (tile, landform, reason) is applied by `jawa/world_mutators_set`,
  then `world_commit`, then `world_mutators_audit` to read it back. That file is data under git and is
  the source of truth, just as the biome paint list is. **No healer:** the world is remade at the end,
  so no existing save needs repair. If Q2 keeps GL, the paint script also strips any GL mutator from
  those tiles.
- **Landform vocabulary.** The 8 proven types are Canyon, Crater, Sinkhole, LoneMountain,
  DesertPlateau, Badlands, Rift and Gorge, with Cirque and SecludedValley as candidates. v1 is §3 Q1.

### 2.4 Mod Settings (every mod ships superb settings)
- **Per biome**, inside the existing `RM_BiomesSettings` (the `enabled[key]` dict, absent means on):
  - add `mapmaker.<Biome>` "Hand-built map for <Biome>", default on.
  - Off makes each `RM_<Biome>_*` step return at once. A `[StaticConstructorOnStartup]` then
    re-adds the vanilla steps the biome's `preventGenSteps` removed, because that list is def data
    and cannot change mid-game.
  - The label says "applies to newly generated maps; restart required".
- **Per landform**, on a Landforms settings page:
  - `landform.<Name>`, default on. Off makes the worker a no-op, and the tile generates with plain
    vanilla elevation. The def stays loaded, so saves are safe.
  - A master "Landforms on" switch.
  - Labelled as map-generation-affecting (it is not worldgen).
- **Feature-gating rule:** a landform is NOT gated to a biome. It is a kit, and any tile on any
  biome can carry it, so it works without our biomes. Map-maker steps are biome-bound by nature, but
  the shared utilities are not.
- Every toggle goes in the mod's `suite.toggles` (debug_process §2.3).

### 2.5 Tier split (Q11a, naming tiers)
- **`RM_` (franchise-free)** carries ALL map shape: every landform and every map-maker for an `RM_`
  biome. The free mod's maps must look identical to the campaign's. No "thin fallback".
- **Campaign (`RUT_`/`RSW_`)** adds only CONTENT: canon set pieces, faction ruins, Utinni structures.
  It does this by patching extra `GenStepDef`s onto a biome's `extraGenSteps` from
  `UtinniPatches`, as `RUT_FoundryTowerScatter` and others already do. It **never** changes terrain
  shape. The landform paint list is campaign data (it is THE world), but the defs it names are `RM_`.

## 3. Per-biome map-shape intent
Sources: each BiomeDef's own `<description>` (cited as `src/RimMandrake/<Biome>/Defs/…`), and its
sheet under `design/Jawa/worldbuilding/biomes/`. Where a sheet's name differs from the mod's name,
the sheet was matched by its field-1 text (shown as "≈"). An intent column marked "needs owner"
means the docs give no macro shape. A "likely landforms" entry is a suggestion, never a ruling.

| biome (def) | sheet | map-shape intent from its own docs | likely landforms |
|---|---|---|---|
| Abyss `RM_Abyss` | `abyss.md` | obsidian stone "twisted into shapes no wind carved"; pockets of clear air in the dark | needs owner |
| BlueDesert `RM_BlueDesert` | `the_blue_desert.md` | a plateau of old ice, wind-scoured bare, "almost empty" | DesertPlateau |
| Cauldron `RM_Cauldron` | `cauldron.md` | a low, wet-black forest over venting ground; flat, no shadows | needs owner |
| Contagion `RM_Contagion` | `the_contagion.md` | "a red valley on a scalded mountain" | SecludedValley |
| FeverWood `RM_FeverWood` | `the_fever_wood.md` | still backswamp: shallow pools over deep mud, trunks several tiles wide, raised wooden byways | none (flat) |
| FloodedCanyon `RM_FloodedCanyon` | ≈`the_cracked_lands.md` | canyon country: mesas, hoodoos, slot canyons, polygon clay pans; floods run wall to wall | Canyon, Gorge, Badlands |
| GelatinousSlime `RM_GelatinousSlime` | `the_slime.md` | a country-sized body "wearing a landscape as its skin" | needs owner |
| Greentide `RM_Greentide` | `the_greentide.md` | a gallery jungle a few tiles wide hugging steaming rivers; deep mud | Gorge? needs owner |
| LanternDeeps `RM_LanternDeeps` | `the_lantern_deeps.md` | crystal-grown voids under cold mountains (pocket map, own generator) | n/a (pocket) |
| LeaningScrub `RM_LeaningScrub` | ≈`arid_shrubland.md` | a flat, wind-scoured plain of even, leaning fuzz to every horizon | none (flat) |
| LongShade `RM_LongShade` | ≈`desert.md` | scattered rock and scarps throwing 4× shadows; shade islands with lethal gaps | Badlands? needs owner |
| Miasma `RM_Miasma` | `the_miasma.md` | a delta: brackish channels between a dying sea and its rivers | needs owner |
| NightsideIce `RM_NightsideIce` | `nightside_ice.md` | the highest ground of the night; ice that flows and fractures | Rift? needs owner |
| Pyrelands `RM_Pyrelands` | `the_pyrelands.md` | open grass savanna "to the horizon" with a moving burn | none (flat) |
| RustCathedral `RM_RustCathedral` | `the_rust_cathedral.md` | a flat plateau carrying a circuit-board maze of walls | DesertPlateau |
| Stillsand `RM_Stillsand` | ≈`dune_sea.md` + `deep_desert.md` | a corrugated plain; every dune runs the same way at the same spacing | none (dune field is map-maker) |
| TheForge `RM_TheForge` | `the_forge.md` | "one mountain, three zones": towers, red seams and flows, ash skirts | LoneMountain |
| TheRot `RM_TheRot` | `the_rot.md` | a fungal continent of bone and lilac towers, milky ponds | needs owner |
| TheSump `RM_TheSump` | `the_sump.md` | the lowest basin: flat black pools and glassy sheets | Crater/basin? needs owner |
| Warscar `RM_Warscar` | `the_scarlands.md` | crater fields and slag hills on shattered megastructure floors | Crater |
| Wasteland `RM_Wasteland` | `wasteland.md` | where rivers die into salt and brine; craters from old weapons | Crater? needs owner |
| Webwork `RM_Webwork` | `the_webwork.md` | a jungle that drank its river; high green shoulders, silk channels | needs owner |
| WeepingStones `RM_WeepingStones` | `weeping_stones.md` | high pale ridges and shoulders; seeps on shaded faces; pools | LoneMountain/ridge? needs owner |
| TheScald `RM_TheScald` | `the_scald.md` | a crater sea ringed by geysered shores (water tile; floor = pocket) | n/a: shore via SeaCoast |
| GreySea `RM_GreySea` | `the_grey_deep.md` | a shrinking salt sea; stranded terraces (floor = pocket) | n/a |
| TheChill `RM_TheChill` | ≈`the_propane_lakes.md` | a black mirror of fuel ringed by a frozen crust (floor = pocket) | n/a |
| ChillCrater `RM_ChillCrater` | none found | "a basin of black glass where a lake used to be" (BiomeDef only) | Crater |
| TwilightSea `RM_TwilightSea` | `the_twilight_deep.md` | a waveglass-lidded sea; the floor is a cavern with skylights (pocket) | n/a |

UNMEASURED: whether a sea tile can carry a landing. If it cannot, the four seas' map-makers are
their existing seabed generators and their shores come from `RM_SeaCoast` on neighbouring land.

## 4. Build order, risks, owner questions

### 4.1 Build order
1. **Landforms kit skeleton plus ONE landform (Canyon)**, copying SeaShores' layout: def, worker,
   extension, settings, `validation.py`, a walk under `design/validation_walks/RimMandrake/`, a
   selftest. **First-script bars** (debug_process §2):
   - the def is present with chance 0;
   - `world_mutators_set` on a quicktest tile succeeds and reads back;
   - the generated map's elevation and rock grids differ from a control tile in the landform's
     shape (a state read, not a screenshot);
   - a landable area remains;
   - toggle off gives the vanilla map.
   Before writing the worker, confirm three things with RimSage: the Odyssey mutator category strings
   (§2.3), the `MapGenerator` var API, and what `ReserveGravshipArea` does when it finds no room.
2. **Pilot map-maker.** The pilot biome is chosen by Q3. It gets its `RM_<Biome>_Shape/Ground/Pieces`
   steps, its existing GenSteps folded into the set, `preventGenSteps` where it replaces vanilla,
   its settings key, and a first script. That script reads the step list off a generated map
   (`map.generatorDef` plus the biome lists), checks the shape bars from its sheet, and checks the
   landable area.
3. **Pilot on a Canyon tile**, to prove the contract (§2.1) on one map.
4. **Owner review as a savegame** (owner ruling 2026-09-02): one review map per variant, with a grid
   key. Offline previews come from `mapgen_paint.py`/`render_terrain.py` between loads.
5. **Remaining biomes, one per sitting**, alongside each biome's sheet sitting. Order follows sheet
   completeness, and "needs owner" rows wait for their sitting.
6. **The paint list** is filled during the final painting pass, never before it.

### 4.2 Risks
- **GL and BiomeTransitions are active on the live list.** GL patches `TerrainPatchMaker` and can
  overwrite a map-maker's terrain on any tile where it rolls a landform (§1.4). Without a decision,
  the landform and the biome look of a tile depend on load order. That is Q2.
- **`preventGenSteps` is def data.** Turning a map-maker off needs the startup re-add and a restart
  (§2.4). The settings label must say so.
- **A silent GenStep failure.** A throwing step logs and generation continues, so a broken map-maker
  produces a vanilla-looking map that looks like success. Every first script must assert the
  biome's signature in the grids, not only "no errors".
- **Landing room.** A Canyon or Rift worker can leave no flat buildable patch. The utilities library
  must guarantee one, and the scripts must check it.
- **Existing steps.** Warscar's 15 `extraGenSteps`, and the GenSteps attached by routes not yet
  traced (§1.3), must keep running. Trace each one's attach route before folding it in.
- **Elevation hooks.** Odyssey mutators with `preventNaturalElevation` on the same tile can fight
  ours. Use categories and `overrideCategories`, and verify on a quicktest.

### 4.3 Questions for the owner (card-ready)
**Q1 — v1 landform vocabulary.**
- (a) Only what the sheets ask for: Canyon, Crater, DesertPlateau, LoneMountain. Smallest, and every
  landform has a home.
- (b) All 8 proven types. Broader painting palette, about twice the work, and some go unused.
- (c) Canyon only until the pilot is accepted. Fastest proof, but the painting palette stays empty longer.

**Q2 — Geological Landforms on our world.**
- (a) Keep GL, and the paint pass strips GL from every tile we give a landform or map-maker. GL
  still decorates vanilla-biome tiles, at the cost of a strip step plus an audit.
- (b) Retire GL and BiomeTransitions from the shipped list. One source of map shape and no
  conflicts, but vanilla-biome tiles lose GL variety.
- (c) Keep GL everywhere and accept that it sometimes wins. No work, but our maps stop being
  predictable.

**Q3 — Pilot biome.**
- (a) FloodedCanyon. Canyon is its whole identity, and it already has two elevation-touching GenSteps.
- (b) Warscar. Craters, and the richest existing step set (15), but much existing content to keep working.
- (c) RustCathedral. Flat plateau with a wall maze, which tests "map-maker without landform" first.

**Q4 — How deep each map-maker goes.**
- (a) Replace vanilla elevation and terrain per biome (`preventGenSteps`). Full control and the
  most work per biome.
- (b) Modify vanilla's output in place. Cheaper, but maps keep a vanilla feel underneath.
- (c) Decide per biome at its sitting. Flexible, but there is no uniform contract to test against.

**Q5 — Where landforms ship.**
- (a) Inside Baroque Biomes as a composed kit, like SeaShores. One mod and one settings page.
- (b) A standalone `RimMandrake: Landforms` mod. Usable without our biomes, but one more mod to keep
  in step.
