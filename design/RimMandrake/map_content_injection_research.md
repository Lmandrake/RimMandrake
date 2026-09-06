<!-- status: live ; planning discussion, owner + Fable, opened 2026-09-06 -->
# Map content injection — the research path

**Owner's brief, 2026-09-06 (planning mode, nothing built yet).** We need to inject
a huge amount of coherent, high-quality content into the procedurally generated
tile maps at the moment the gravship lands. Four content classes:

| class | examples |
|---|---|
| **natural** | interesting craters, biological formations, terrain + plant communities with complex relationships |
| **unnatural past** | ruins, crashed vessels, old camps |
| **current residents** | functional homes, factories, quarries, garrisons — complete with denizens |
| **micro-dungeons** | living caverns, customised beast populations with nests and lairs |

Three questions the plan must answer:

1. **Improving natural maps with natural elements.**
2. **Injecting plot/flavour into natural maps** so the world feels alive and inhabited.
3. **Large complex maps** — settlements that function, have guards in place, etc.
   (Samuel Streamer's newest series has guards at a doorway the player must sneak
   past, so scripted interactions of this kind are possible.)

Tools on the table: procedural Python, the bridge for live injection via Lua
(no reload to try a design), and a small amount of Claude access. Open questions
the owner posed verbatim:

- *Do we really want to code this into their procedural map generation?* (Landforms
  and mutators might teach us how.)
- *Do we keep the current Lua template injection and write many last-minute
  adjustable templates?* Some other way?
- *How do we generate all that content meaningfully and at high quality?*

Biome sheets (`design/Jawa/worldbuilding/biomes/`) are being written now and will
guide the decisions; meanwhile the repertoire of injectables must grow.

## 1. Inspiration the owner supplied

Saved under `research/RimMandrake/inspiration/map_injection_2026-09-06/`:

| file | what it shows | why it matters |
|---|---|---|
| `01_crater_lake_tile_terrain.jpeg` | crater-lake tile: an annular lake with a central island, radial cliff spurs, marsh fringe | pure terrain coherence — one landform organises the whole tile |
| `02_estuary_delta_tile.png` | braided estuary delta with islands and scattered points of interest | water network as the tile's skeleton; POIs sit on the islands |
| `03_circular_ship_city_base.png` | circular ship/city with satellite rings | a settlement with a single geometric idea |
| `04_riverside_organic_city.png` | organic riverside city, districts, bridges, a walled palace | district grammar; roads and water shape the blocks |
| `05_crescent_island_settlement.jpeg` | crescent island settlement with piers, gardens, walkways over water | a settlement composed AROUND a landform |
| `06_timelapse_symmetric_base.png` | symmetric fortified base (day 542 timelapse) | player-built order as a contrast to ruins |

Links from the brief:

- Google image search "rimworld map ruins" and "rimworld crater" (owner's searches, 2026-09-06)
- https://www.reddit.com/r/RimWorld/comments/1etvph4/for_those_who_were_curious_about_my_450/ (450-tile-wide map showcase)
- Mods to study: Geological Landforms, Ancient Urban Ruins, Gravship Crashes, vanilla ancient dangers / ruins / landforms / tile mutators.

Already in the repo and directly relevant:

- `research/RimMandrake/hand_authored_maps/` — 41 entries, 44 `.rws` hand-authored maps (UnknwnBuilds Worlds 25-61, Grapes, SickBoyWi), plus `research/RimMandrake/reference/rimworld_handcrafted_map_atlas.md` (the census) and `research/RimMandrake/samuel_streamer_study/02_TECHNIQUE_ANALYSIS.md`.
- `design/RimMandrake/map_authoring_decision.md` — bridge over save-editing, ruled 2026-08-12 (bridge call 0.002 s). Save-writing is DEAD (`save_authoring_pipeline.md`).
- `design/RimMandrake/beautiful_tilemap.md` — the image-in-the-loop concept, v2, nothing built.
- `skills/rimworld-scene-composition/SKILL.md` — the five composition metrics and the critical-reviewer pass.

## 2. What exists today (capability inventory)

*Filled from the repo audit — see §5 for the verbatim findings.*

| piece | what it does | runs where |
|---|---|---|
| `src/RimMandrake/Utils/rimplace/` | Lua template → `BuildPlan` IR → lint/render/verify offline; compiles to `jawa/*` bridge calls | offline, ms |
| `src/RimMandrake/StructureInjections/` | `GenStep_RimplacePlan` applies a baked flat plan (`Templates/*.txt`) at mapgen; a debug action applies one to a live map | mapgen time + live |
| `src/RimMandrake/Inhabited/` | inhabited settlements: cast rosters, duties, security profiles, `GenStep_ComposeSettlementDistrict`, lord routines | mapgen time |
| `src/RimMandrake/Utils/rimbench/` | live formations (crater, wreck, cavern, outpost, geyser field), scatter maths, terrain paint/capture | live via bridge |
| `src/RimStarWars/StructureInjectionsSW/`, `src/RimUtinni/StructureInjectionsRUT/` | 7 + 12 baked templates (graveyards, waystation, homestead, monument, toll gap …) | data |

## 3. Candidate architectures (prior to findings — tradeoffs as I see them)

The key structural fact: **a gravship landing creates a NEW map for that tile**, so
"the moment we land" IS map-generation time. Mapgen hooks fire exactly then; a
live-bridge pass fires a moment after. Both moments are available.

### A. Engine-native mapgen hooks (GenStep / TileMutator / Landform in C#)
Content is generated inside the game's own pipeline, before fog, roofs and
regions are finalised.
- **+** Terrain-level coherence (elevation, water, fertility) is only reachable here; the engine handles fog/roof/region/pathing refresh; ships as a plain mod; fires for every map including ones the player never sees us drive.
- **−** C# iteration needs a game restart (22 s minimal list / ~25 min full) unless the logic is data-driven; debugging blind inside a GenStep that swallows exceptions.
- **Mitigation already in hand:** `GenStep_RimplacePlan` is data-driven — a new plan file needs no rebuild, only a ~90 s quicktest map.

### B. Post-generation live injection (bridge + Python + Lua) — the current route
Python decides, the bridge writes, the game is already running.
- **+** Iterate in milliseconds; see the result instantly; LLM can sit in the loop; every rimbench formation already works this way.
- **−** The player's game must run the driver: fine on the owner's machine, impossible as a shipped self-contained mod; terrain/elevation rewrites after generation fight the engine (roofs, regions, fog, thick-roof mountains); ~40 bridge setters lie (`rimworld-bridge-silent-failures`).
- **Question for the owner:** is the runtime audience only your machine, or must this ever run without Python present?

### C. Hybrid — author offline, apply at mapgen (the plan file is the contract)
Python/Lua/LLM produce PLANS (data); one C# executor applies them at mapgen, and the same executor's debug action applies them live for iteration.
- **+** Best of A and B: ms iteration through the live debug action, self-contained at ship time, no Python at runtime; one verified executor.
- **−** Plans are flat (baked variants, not runtime randomness) unless the executor grows parametric ops; siting logic (where on the map, which orientation, how it meets terrain) must live in C# or be pre-decided.
- **This is what StructureInjections already is.** The question is whether to grow it into a small map-DSL (site selectors, terrain-conditioned ops, scatter) or keep it flat and bake many variants.

### D. Ride engine-native content formats (KCSG layouts, PrefabDef, TileMutatorDef, Landform graphs)
Author in the formats the game and the big mods already consume; export from live-built scenes with their exporters.
- **+** The engine sites, rotates, fogs and furnishes for free; vanilla settlements/quests/sites can consume our structures; the Vanilla Expanded and Odyssey toolchains already exist.
- **−** Each format has its own ceiling (KCSG is structure-only; PrefabDef is thing-only; mutators are terrain-first); mixed scenes need several formats stitched; dependency on VE Framework.

### E. Corpus mining (Real Ruins pattern over our 44 hand-authored saves + real bases)
Decode `.rws` maps into chunks (rooms, ruin fragments, terrain patches) and quilt them in.
- **+** Human-authored quality by construction; huge repertoire for free; a real training/reference set for the LLM route.
- **−** Chunks carry their source's mod defs (must be remapped or filtered); coherence between chunks is still ours to solve; savemap reads terrain grids today — the thing layer is the open probe.

### F. LLM-in-the-loop composition (Claude writes Lua templates / plans from the biome sheet; screenshot-graded)
- **+** Turns prose biome sheets into content directly; the scene-composition metrics give it a grader; ms render loop.
- **−** Quality is only as good as the ctx API and the critic; must never be a runtime dependency (the game is whole with the LLM absent).

**Working hypothesis (to be tested, not adopted):** C as the spine, D for whatever
the engine already does well (structures via KCSG/Prefab, terrain via mutators),
B as the iteration loop, E and F as the content FACTORIES feeding C. A is entered
only for terrain-level work that nothing post-generation can do.

## 4. Research probes — each cheap, each kills or confirms an assumption

| # | assumption | probe | cost |
|---|---|---|---|
| P1 | A gravship landing runs the standard `MapGenerator` with the tile's mutators/landmarks, so GenStep hooks fire at landing | read `GravshipLanding`/`MapGenerator` in decompiled source | 10 min |
| P2 | `PrefabUtility` / KCSG can spawn a structure on a LIVE map at a chosen cell | read signatures; one bridge call on a quicktest map | 30 min |
| P3 | `GenStep_RimplacePlan`'s live debug action is bridge-reachable and fast enough for a 100×100 plan | time it on a quicktest | 20 min |
| P4 | The 44-save corpus can be decoded to a THING layer (not just terrain) offline | extend/inspect `savemap.py` on one World_58 save | 1 h |
| P5 | Claude can turn one biome sheet paragraph into a rimplace Lua template that renders and lints | one `claude -p` run, `rimplace render`, human look | 30 min |
| P6 | Geological Landforms' graph format is authorable by us (XML, not editor-only) | read the mod's Defs + one landform file | 20 min |
| P7 | Real Ruins is 1.6-compatible and its blueprint format is readable | web + mod folder | 20 min |
| P8 | A pawn can be made to HOLD A POST (guard at a door) through an existing LordJob, reachable from the bridge | one live test on Inhabited pawns | 30 min |
| P9 | Terrain rewrite after generation (crater into an existing map) leaves fog/roof/regions sane | rimbench `crater.py` on a quicktest, then `region`/fog read-back | 30 min |

## 5. Findings

*Each line CONFIRMED (read in code/on disk/primary source) or UNCERTAIN. Where the
disk and the web disagree, the disk wins.*

### 5.1 The engine's own extension points (decompiled source, 2026-09-06)

Source root: `D:\Luke\dev\reference\rimworld-decompiled\`.

- CONFIRMED **A gravship landing runs the standard map generator.** `GravshipUtility.cs:540` calls `GetOrGenerateMap(destinationTile, size, mapParent.def, GetGenSteps(gravship))`; `GetGenSteps` (line 660) only PREPENDS `ReserveGravshipArea` and `GravshipMarker`. `MapGenerator.cs:141` runs every tile mutator's `Init(map)` before the gen steps. So every GenStep/mutator hook fires at the landing moment, and `MapGenerator.GetOrGenerateVar<List<CellRect>>("UsedRects")` already carries the ship's footprint — anything we inject at mapgen must respect it.
- CONFIRMED **The GenStep order table** (96 GenStepDefs across Core + DLCs, `Data/*/Defs/MapGeneration/`) is the timeline any injection must slot into:

  | order | step | what it fixes |
  |---|---|---|
  | 10-20 | ElevationFertility → MutatorPostElevationFertility | the heightfield (mountains, lakes, craters get their shape HERE) |
  | 200-240 | RocksFromGrid → Terrain → MutatorPostTerrain → RemoveTinyIslands | rock vs open ground; terrain types |
  | 390-401 | Roads → Settlement → SettlementPower | faction bases (vanilla settlements go here) |
  | 500 | MutatorCriticalStructures | mutator-owned structures (ancient quarry, uplink, abandoned colony) |
  | **600** | **ReserveGravshipArea** | the ship's footprint is reserved AFTER settlements and critical structures, so those are sited first and the ship lands around them |
  | 700-750 | MutatorNonCriticalStructures → AncientRuins → ScatterRuinsSimple/Shrines | ruins |
  | 850-875 | FindPlayerStartSpot → ScenParts | |
  | 900-970 | Plants → scatter groups (junk clusters, craters, debris, fences, mechs) → RockChunks | dressing |
  | 1120-1200 | CaveHives → Animals | fauna |
  | 1500 | Fog | everything enclosed is fogged from here |
  | 1600-1700 | MutatorFinal → GravshipMarker | |

  Below 600 an injected structure is something the ship lands AROUND; above 600 it must avoid `UsedRects`. `GenStep_ScatterGroup` / `GenStep_ScatterGroupPrefabs` (order 900-960) are pure-XML scatter of thing groups and prefabs — vanilla "junk clusters" are made with no C# at all.
- CONFIRMED **GenStep ordering and failure mode.** Steps sort by `def.order, def.index`; each `Generate()` is wrapped in a try/catch that logs `Error in GenStep` and continues with the NEXT step (`MapGenerator.cs:309-345`). A throwing step loses only its own remaining work, silently for the player.
- CONFIRMED **`GenStepParams` is `{sitePart, gravship, layout}`** — a GenStep knows whether it is running for a landing.
- CONFIRMED **TileMutatorWorker hooks:** `Init`, `Tick`, `GeneratePostElevationFertility`, `GeneratePostTerrain`, `GenerateCriticalStructures`, `GenerateNonCriticalStructures`, `GeneratePostFog` (`TileMutatorWorker.cs:25-61`), each invoked by a dedicated `GenStep_Mutator*`. ~50 Odyssey workers exist: Lake, LakeWithIsland(s), Cliffs, Dunes, Fjord, Bay, Cove, Archipelago, Basin, Wetland, HotSprings, IceCaves, Lava*, Oasis, Valley, Plateau, AncientQuarry/Ruins/Vents/Uplink, AbandonedColony*, InsectMegahive… (`Data/Odyssey/Defs/TileMutators/`). **This is the vanilla "landform" system and the crater-lake in image 01 is the shape it makes.** Mutators are terrain-first and gen-time only — no runtime API re-applies one to a live map (UNCERTAIN: absence not exhaustively proven).
- CONFIRMED **Landmarks are a WORLD-gen step** (`WorldGenStep_Landmarks`), assigning `LandmarkDef`s to tiles, which then weight mutators. Our frozen world already fixes which tile gets which landmark; per-tile mutators are the lever we hold.
- CONFIRMED **Layouts** (`LayoutWorker*`: Complex, Complex_Ancient, Mechanitor, AncientStockpile, Labyrinth, OrbitalPlatform, SimpleRuin, Structure) compose rooms from `LayoutRoomDef`s furnished by `RoomContentsWorker` and `RoomPart_*` (Crate, InsectHive, DormantMechCluster, SentryDrone, Barricades, Corpse, ConnectConduits…). `LayoutWorker.GenerateStructureSketch` reads `MapGenerator.mapBeingGenerated?.NextGenSeed` — gen-time coupled.
- CONFIRMED 🔑 **PrefabDef is the engine's structure format, and it works on a LIVE map.** `PrefabUtility.SpawnPrefab(PrefabDef, Map, IntVec3 pos, Rot4 rot, Faction, List<Thing> spawned, Func overrideSpawnData, Action onSpawned, bool blueprint)` (`PrefabUtility.cs:46`) is a plain static using `SetTerrain`/`GenSpawn.Spawn`; no gen-time state. `CanSpawnPrefab` (line 15) pre-checks. Vanilla ships `DebugActionsPrefabs` with `SpawnPrefab`/`SpawnPlayerPrefab` at the mouse cell on a playing map.
- CONFIRMED 🔑 **Vanilla has a prefab EXPORTER.** `DebugActionsPrefabs.CreatePrefab` → `PrefabUtility.CreatePrefab(rect, copyAllThings, copyTerrain)` and prints ready-to-paste `<PrefabDef>` XML. Build a scene live through the bridge, export it as data, ship it.
- CONFIRMED **PrefabDef vocabulary** (`PrefabThingData`, `PrefabTerrainData`, `SubPrefabData`): per-thing `stuff`, `colorDef`/`color`, `stackCountRange`, `hp`, `chance`, `quality`, `position`/`positions`/`rects`, `relativeRotation`; terrain by `rects` with `chance`; nested sub-prefabs with `chance`; whole-prefab `rotations`. Probabilistic variation is native (every stool at 0.66 chance in `AncientPrefabs.xml`). What it lacks: pawns, roofs, filth/damage passes, siting logic.
- CONFIRMED **Scatter family:** `GenStep_Scatterer` base (`count`, spacing, edge/pollution/faction filters, abstract `ScatterAt`), concrete `ScatterRuinsSimple`, `AncientComplex`, `ScatterAncientMechs/Turret/LandingPad`, `ScatterShrines`, `ScatterLayout`, `GenStep_ScatterGroupPrefabs`. No separate ScatterableDef type.
- CONFIRMED **Guards and posts exist in vanilla lords:** `LordJob_DefendBase` (toils DefendBase/AssaultColony), `LordJob_DefendPoint` (`LordToil_DefendPoint` with `wanderRadius`/`defendRadius`), `LordToil_Sleep`. `SitePartWorker.PostMapGenerate(Map)` is a sanctioned post-generation hook for site-specific setup.
- CONFIRMED **Refresh APIs after bulk live injection:** `RegionAndRoomUpdater.RebuildAllRegionsAndRooms()`, `FloodFillerFog.FloodUnfog(root, map)`, roof grid `SetRoof`, power-net rebuild (bodies not traced).

### 5.2 What this repo already has (audit, 2026-09-06)

- CONFIRMED **rimplace** ctx API (`luaenv.py:222-812`): `role, has_role, in_bounds, buildable, occupied, sizes, footprint_of, place, can_place, place_role_fit, place_role, place_overlay, wall_attach, floor, floor_rect, paint, floor_color, roof, roof_rect, wall_rect, door, window, wall_mount, clear, run, pawn, ruin, room, note, refuse`. Sandbox proven by negative-control selftests. **37 Lua templates** in `design/Jawa/templates/`, several already "site dressing, no walls" (krayt/bantha graveyard, podracer wreck, waste camp).
- CONFIRMED **flat plan directives** (`RimplacePlan.cs`): `FOOTPRINT, CLEAR(all|soft), FOUNDATION, TERRAIN, THING, RUN, ROOF, PAINT, FLOORCOLOR, PAWN`. Siting is `centerOnMap` or a fixed offset — **no terrain-aware siting exists**. PAINT/FLOORCOLOR are unimplemented at mapgen. The debug action applying a plan at the mouse cell on the current map is bridge-reachable (`StructureInjectionsDebugActions.cs`).
- CONFIRMED **Inhabited** is a resident cast with a one-toil-forever Lord (`RouteStance {AtWork, AtRest, Defending}`), a forced night-sleep job giver, and a `SecurityProfileDef` that is a stub. `GenStep_ComposeSettlementDistrict` composes `districts[0]` only. Two recorded gaps say nothing reaches it from either intended entry (`INHABITED_SETTLEMENT_MAPPARENT_GAP_1`, `INHABITED_TILEMUTATOR_NO_ENTRY_1`). **Not proven live end to end.**
- CONFIRMED **rimbench**: `scatter.py` pure geometry (`noise, fbm, elliptical_radius, lobes, radial_field, dither, pick, clumps, ring, rim_band, walk, blob, zones`); `formations.py` live (`crater, wreck, cavern, outpost, geyser_field`); `terrain.py` batches `jawa/set_terrain_batch`; open question whether painting terrain clears plants.
- CONFIRMED **savemap.py decodes terrain, under-terrain, foundation, roof and pollution grids only** — things and pawns are NOT decoded. Corpus mining of structures (approach E) needs a thing-layer reader; the `.rws` thing XML is plain and greppable (`rimworld-savegame` skill).
- CONFIRMED **rimplace gaps** (`rimplace-gaps.md`): no power/pipe/conduit layer in the IR; no door→room reachability; `buildable()` vacuous; roof-support check approximate; `door()`/`wall_mount()` delete what they overwrite; `calls` output not replayable.
- CONFIRMED **biome grammar** field 8 *"Inhabited objects — what structures, ruins and wrecks occur, and why here"* is where a sheet specifies map content; field 6 *"Never true"* is a hard-ban list a linter can read.
- CONFIRMED **queue items in flight that overlap this work**: `TILE_STRUCTURE_DESIGNS_1` (doing), `INHABITED_STOCK_ONTO_MAP_AND_FATE_1` (doing), `INHABITED_AUGMENTATION_BUILD_1` (doing), `SETTLEMENT_VISIT_LOOP_1`, `SETTLEMENT_VERBS_WAVE_1` (ready), `LIGHTFALL_CHASM_AUTHORING_1` (proposed); item files also exist for `BRIDGE_KCSG_VGE_TOOLS_1`, `WORLD_MUTATOR_LANDMARK_IMPORTERS_1`, `ISHKO_DARK_LANDMARKS_1`, `TILE_STRUCTURE_REVIEW_SAVE_1` (state UNCERTAIN). This plan must not fork those; it should name which it absorbs.

### 5.3 What is on THIS machine (disk inventory against `ModsConfig.FULL.LATEST.xml`, 2026-09-06)

Workshop root `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\<id>`.

**ACTIVE on the owner's full list and directly relevant:**

| mod | packageId | mechanism (from its def folders) | id |
|---|---|---|---|
| Vanilla Expanded Framework | OskarPotocki.VanillaFactionsExpanded.Core | KCSG: `CustomStructureGeneration/SymbolDef`, structure layouts, exporter | 2023507013 |
| Geological Landforms | m00nl1ght.GeologicalLandforms | `Landforms-v1/` XML graphs; replaces terrain/elevation gen (UNCERTAIN how it coexists with Odyssey mutators on a tile — P14) | 2773943594 |
| Biome Transitions | m00nl1ght.GeologicalLandforms.BiomeTransitions | data-only landform pack, ecotones at biome borders | 2814391846 |
| Biomes! Caverns | BiomesTeam.BiomesCaverns | `Landforms/` + C#: cavern map generation | 2969748433 |
| Alpha Biomes | sarg.alphabiomes | Odyssey `LayoutDefs`, `PrefabDefs`, `TileMutators` for its biomes | 1841354677 |
| **Vanilla Landmarks Expanded** | VanillaExpanded.VExplorationE | `PrefabDefs` + `TileMutators` — **a shipped example of exactly the L1+L2 pattern in §6.2** | 3656316229 |
| Gravship Raids | sk.gravshipraids | `PrefabDefs` (base + VGE) for wreck/raid structures | 3767338163 |
| Vanilla Gravship Expanded Ch1 | vanillaexpanded.gravship | `LayoutDefs`, `PrefabDefs` | 3609835606 |
| Gravship Crashes | Arcjc007.GravshipCrashes | no XML defs — Harmony/C# only (UNCERTAIN internals; source on GitHub per author) | 3578515873 |
| **Ancient Urban Ruins** | XMB.AncientUrbanrUins.MO | `AncientMarket_Library.CustomMapDataDef` + QuestScriptDefs — **a saved-map-data format spawned by quest**: the "import floor plans" system | 3316062206 |
| Go Explore! | Albion.GoExplore | own `GenStepDefs` | 1814100216 |
| Minerals Framework | zacharyfoster.mineralsframework | own `GenStepDef` | 3562390384 |
| Dark Ages: Beasts and Monsters | Van.Beasts | `TileMutators` for beast lairs (UNCERTAIN) | 3472275628 |
| VOE: Additional Outposts | MrHydralisk.VOEAdditionalOutposts | `StructureLayoutDefs` (KCSG) | 2873841790 |
| Outer Rim Furniture & Decor | Neronix17.OuterRim.FurnitureAndDecor | `SymbolDefs` (KCSG) | 2919553599 |
| VQE Cryptoforge / VQE Ancients / [SR] Factional War / [BTD] Gravship Blueprints | — | `SitePartDefs` — quest-site maps | 3461526070 / 3618306875 / 3423264477 / 3575162262 |
| Map Designer, Map Preview | zylle.MapDesigner, m00nl1ght.MapPreview | C# tools (blockout knobs; pre-landing preview) | 2111424996 / 2800857642 |
| Inhabited (ours) | mandrake.rm.inhabited | `GenStepDefs`, `TileMutatorDefs` | local |

**On disk but INACTIVE:** Vanilla Base Generation Expanded (3209927822, `LayoutDefs`),
Real Ruins (1552146295), Dungeon Core (3064597982, `QuestEditor_Library.CustomMapDataDef`
— same map-data idea as Ancient Urban Ruins), VFE Deserters / The Profaned / VOE Power
Grid (KCSG `StructureLayoutDefs`), VFE Settlers (C# GenSteps), GravTide (3779600989,
`TileMutatorDefs` + `WorldGenStepDefs`).

**Not on disk:** Map Reroll, Save Maps, Roads of the Rim, Better Ancient Complex (base).

Disk beats web where they differed: Real Ruins is present (inactive), not merely
"available"; Ancient Urban Ruins' mechanism is a `CustomMapDataDef` (the web could
not see this); Gravship Crashes has no XML at all.

### 5.4 Published mods and corpora (web, 2026-09-06)

- CONFIRMED **Real Ruins** uploads player-base snapshots to a server (author cites 3M+ blueprints) and replays pieces as ruins; blueprints are static XML; a public viewer exists at woolstrand.art/view; repo github.com/dieworld/RealRuins has a 1.6 folder (UNCERTAIN it is fully 1.6-working). Steam id 1552146295.
- CONFIRMED **KCSG** (Vanilla Expanded Framework): dev-mode exporter ("Export" ≤51×51, "Export from area" irregular) writes `StructureLayoutDef` (`layouts` grid, `roofGrid`, `terrainGrid`, `modRequirements`) plus `SymbolDef`s; runtime use via `KCSG.CustomGenOption` mod extension on a WorldObjectDef (`chooseFromlayouts`, `tryFindFreeArea`, `symbolResolvers` like `kcsg_randomdamage`, `kcsg_scatterstuffaround`). UNCERTAIN: no documented static call for third-party runtime spawning of a layout. Wiki: github.com/Vanilla-Expanded/VanillaExpandedFramework/wiki.
- CONFIRMED **Geological Landforms** is a node-graph (Seneral Node Editor Framework) terrain layer with an in-game editor and live preview; landforms are plain shareable XML; companion **Map Preview** shows the tile's map before settling. UNCERTAIN whether landforms place things (README describes terrain/temperature/rainfall only). github.com/m00nl1ght-dev/GeologicalLandforms.
- CONFIRMED **Ancient Urban Ruins** (Steam 3316062206) generates street/block city maps, underground elevators, and has "a system for importing floor plans and generating quest maps"; UNCERTAIN internals (no public source found).
- CONFIRMED **Gravship Crashes** (Steam 3578515873): a POI with a crashed gravship, damaged things/pawns, defenders scaled to beds/seats/ship size, dismantleable broken engine; source on GitHub per author.
- UNCERTAIN **PrefabDef modding docs**: none published; the decompiled source above is our documentation.
- UNKNOWN **The Samuel Streamer sneak-past-guards mechanism**: no source ties the episode to a mod; the vanilla lord toils in §5.1 can produce it regardless.
- CONFIRMED **Save Maps (Continued)** (Steam 2916523481, github.com/emipa606/SaveMaps) exports/imports a full tile as a blueprint under `Config\SavedMapPresets`. CONFIRMED **MapRenderer** (github.com/AaronCRobinson/MapRenderer) renders a live map to a high-res PNG (map→image; nothing goes image→map).

### 5.5 Composition rules already written down in this repo

22 rules extracted (source: `skills/rimworld-scene-composition/SKILL.md`, the map atlas §7-8, `beautiful_tilemap.md`, the streamer study). The ones that bind a generator:

1. Terrain boundaries jagged, staggered 1-2 cells; biome transitions are ecotone bands, never rectangles.
2. One dominant readable landmark IS the geography; authored content sits at compositional anchors (valley end, ring centre, island, below the dam).
3. Hydrology must look like a process with a cause (estuary, dry riverbed, former reservoir).
4. Topography defines rooms without walls; preserve negative space so the feature reads at map scale.
5. Seed environmental history: old roads, abandoned farms, former lakebeds, broken infrastructure.
6. Props inside an implied shape (ring, cluster, directional sprawl), never even scatter; a bone pile is ONE body with a skull at one end.
7. Ground-plane change (one-tile rise, shallow pit, stair) precedes prop placement; a linear feature needs bulk (several rows) or it reads as a fence rail.
8. Playability gates VETO (buildable flat area, pathing, geothermal), they do not average into beauty.
9. Build order foundation → terrain → things; substructure orphans are a state the game never produces.
10. A theme is defined by what is deleted as much as what is added.

Creator workflow (atlas §7, seven stages): macro-landform → reroll → hand-sculpt silhouette → texture geology/ecology → one focal landmark → seed history → package. The corpus: 44 saves, sizes 250² (17) … 500² (2), 11-44 distinct terrains per map (median 19); no terrain-mix percentages measured yet. NONE FOUND on scripted guard/patrol scenes in any of these sources.

## 6. Synthesis after the first research pass

### 6.1 What the findings change about §3

1. **The engine already has the contract we were about to invent.** `PrefabDef` is a
   data format for a structure with per-thing stuff/quality/hp/chance, terrain rects,
   nested sub-prefabs, and rotations; it spawns on a LIVE map from a static call; and
   the game ships an exporter from a live rect to XML. Approach C's "plan file" and
   approach D's "engine format" collapse into one thing: **author with rimplace (Lua)
   or by building live, store as PrefabDef, spawn at mapgen through a siting GenStep,
   spawn live through the bridge for iteration.** The flat plan executor stays only for
   what PrefabDef lacks: roofs, pawns, clears, paint.
2. **Landing time IS mapgen time, and the order table gives us slots.** Terrain-level
   work (question 1) belongs at order 10-240 as a `TileMutatorWorker`; structures at
   400-750; dressing at 900-970; denizens after 700 or in `PostMapGenerate`. Nothing
   post-generation can move the heightfield without fighting fog/roof/region state
   (P9 still to measure).
3. **Vanilla mutators ARE the landform system** for question 1: ~50 workers, terrain
   first, gen-time only. A crater-lake tile is `LakeWithIsland` + `Cliffs`. Our lever
   on the frozen world is which mutators each tile carries (`WORLD_MUTATOR_LANDMARK_IMPORTERS_1`
   already exists as an item) plus our own workers for shapes vanilla lacks.
4. **Guards at doors need no new mechanism**: `LordJob_DefendPoint` with a small
   radius at the door cell, or `LordToil_Sleep`; Inhabited's routine toil already
   switches between AtWork/AtRest/Defending. What is missing is the AUTHORING of a
   post (a cell + a stance + a pawn) inside a scene, and proof it holds live (P8).
5. **Quality has a grader already**: the five scene-composition metrics and the 22
   rules in §5.5. What is missing is anything that applies them BEFORE a human looks —
   playability gates (rule 8) and implied-shape checks (rule 6) are computable.

### 6.2 The layered shape this suggests (hypothesis, not a ruling)

| layer | gen order | shipped mechanism | authoring / iteration | content factory |
|---|---|---|---|---|
| **L0 world** | worldgen | landmark + mutator assignment on the frozen tiles | `rimworld-world-editing` bridge tools | biome sheet field 8 |
| **L1 landform** | 10-240 | vanilla `TileMutatorDef`s + ONE data-driven worker of ours that stamps a terrain/height mask from a file | rimbench `crater.py`/`terrain.py` live paint on a quicktest; masks from Python (`scatter.py`) or from an image | procedural Python; image-conditioned generation (`beautiful_tilemap.md`) |
| **L2 structure** | 400-750 | `PrefabDef` + a siting GenStep of ours (anchor selection: near water, on plateau, against cliff, off `UsedRects`) + aging passes (hp, ruin, filth) | rimplace Lua → PrefabDef; build live → `CreatePrefab` export; `SpawnPrefab` live via bridge | LLM from biome sheet; corpus mining of the 44 saves; hand |
| **L3 residents** | 700+ / `PostMapGenerate` | Inhabited cast + `LordJob_DefendPoint`/`DefendBase`; nests as prefab + pawnkind + lord | bridge spawn + lord assignment on a quicktest | cast rosters (Inhabited) |
| **L4 dressing** | 900-970 | `GenStep_ScatterGroup(Prefabs)` defs — pure XML | live scatter via rimbench | scatter maths |
| **L5 reveal** | 1500 | vanilla fog; dungeons are enclosed rock + roof | — | — |

A **scene** = a bundle across layers (prefab + roof rects + terrain mask + cast + posts
+ dressing) with a siting rule. That bundle is the unit the biome sheet's field 8
names, the unit the LLM authors, and the unit the review save shows.

### 6.3 Where each of the owner's three questions lands

1. **Natural elements** → L1 (mutators, our mask-stamping worker) + L4 (plant
   communities as scatter groups keyed to terrain). The image-in-the-loop idea is a
   MASK generator for L1, never a runtime dependency.
2. **Plot and flavour** → L2 scenes with aging passes + L3 small casts + L4 debris
   trails; history rules (§5.5 #5) as a checklist the generator must satisfy.
3. **Functioning settlements with guards** → L2 composed from district prefabs
   (KCSG/VBGE do this for vanilla factions; Inhabited's `districts[0]` is our start)
   + L3 posts and routines + power/pipe layers (the `rimplace-gaps.md` list is the
   work).

### 6.4 The research path, in order

| # | probe | status |
|---|---|---|
| P1 | landing runs standard mapgen with mutators | **CONFIRMED** (`GravshipUtility.cs:540,660`; `MapGenerator.cs:141`) |
| P2 | `SpawnPrefab` on a live map at a cell | source CONFIRMED; **live call pending** — expose `jawa/spawn_prefab` + `jawa/export_prefab` in JawaBench, one quicktest |
| P3 | live plan apply timing for 100×100 | pending |
| P4 | corpus `.rws` thing-layer decode | pending — extend `savemap.py` or a new reader; one World_58 save |
| P5 | Claude → Lua template from one biome-sheet paragraph | pending |
| P6 | Geological Landforms XML authorable / active? | see §5.3: ACTIVE, `Landforms-v1/` XML — format read pending |
| P7 | Real Ruins 1.6 + blueprint format | web CONFIRMED; on disk, INACTIVE (§5.3) — format read pending |
| P8 | a pawn holds a post through `LordJob_DefendPoint`, from the bridge | pending |
| P9 | post-hoc terrain rewrite leaves fog/roof/regions sane | pending |
| P10 | a data-driven `TileMutatorWorker` that stamps a mask file, proven on a quicktest | new — decides whether L1 is authorable without per-shape C# |
| P11 | `GenStep_ScatterGroup` defs of our own (pure XML) place a plant community keyed to terrain | new — decides whether L4 needs any C# |
| P12 | playability gates (rule 8) computable from the bridge read-back on a quicktest | new — the grader's floor |
| P13 | Ancient Urban Ruins' `CustomMapDataDef`: can it carry OUR whole authored maps (question 3) and spawn them by quest? read the def + one shipped instance | new — a possible shipped route for large maps |
| P14 | Geological Landforms vs Odyssey mutators on one tile: which runs, in what order, and is `Landforms-v1` XML hand-authorable | new — decides L1's authoring format |
| P15 | Vanilla Landmarks Expanded: read one landmark's `TileMutator` + `PrefabDef` pair as the worked example of L1+L2 | new — cheapest study, pure XML |

Each probe is under an hour on the minimal mod list and a quicktest map; none needs
the full list. The first three that CHANGE the architecture if they fail: P2 (the
prefab spine), P10 (natural content without C# per shape), P8 (guards).

## 7. Questions for the owner

**Owner, mid-session 2026-09-06:** *"we had assumed previously the unfavorable but
necessary 'player lands in a boring map, then clicks GO! and the map improves around
them through Bridge'. I'd take that, even though it's clumsy."* — so the runtime
audience is this machine, and a Python driver at runtime is acceptable. Findings say
the click is not necessary for structures and terrain (§6.1 #2); it remains available
as a second, LLM-flavoured pass.

Asked as cards, answers recorded below when given:

| # | question | options | answer |
|---|---|---|---|
| Q1 | When does content enter the map? | mapgen-time by default, bridge pass optional · GO-click bridge pass only · both always | — |
| Q2 | What is the stored unit of a structure? | `PrefabDef` (engine format; rimplace compiles to it) · keep the flat rimplace plan · KCSG `StructureLayoutDef` | — |
| Q3 | How is natural terrain shaped? | vanilla mutators + Geological Landforms + one mask-stamping worker of ours · Python terrain gen applied live through the bridge · both | — |
| Q4 | Which content factories first? (multi) | LLM from biome sheets · corpus mining of the 44 saves · live-build-and-export · hand-authored Lua | — |

Open, not yet carded: whether large authored maps (question 3) ship through Ancient
Urban Ruins' `CustomMapDataDef` route or through district composition — P13 decides
what is even possible.

## 8. Decisions

*None yet. Nothing in this document is ruled.*
