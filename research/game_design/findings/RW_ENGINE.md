# RW_ENGINE — base game + DLC dungeon machinery

Written 2026-09-11. Scope: **what vanilla RimWorld 1.6 (Core + Ideology +
Biotech + Anomaly + Odyssey) can actually do for dungeon-shaped content, and
the exact XML/C# knobs an author turns** — not third-party mods (that's
LOCAL_MODS.md) and not this repo's own design decisions (that's
REPO_PRIOR.md), except where this repo's own prior sessions already did the
primary-source verification I need and I am citing that verification.

**Machine-access fact, same as the sibling findings:** this Mac has no
`/mnt/c`, no Windows share, no local Steam install, and no `defs.sqlite` —
`measure count <Type>` returns `UNMEASURED dumpdb` for everything
(`~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py`), and
`src/RimMandrake/Utils/ilprobe/` targets a hardcoded Windows path to
`Assembly-CSharp.dll` that does not exist here. Every finding below is
therefore either (a) read directly, byte-for-byte, from a repo-committed
document that a *prior* session wrote after reading the decompiled 1.6 source
at `D:\Luke\dev\reference\rimworld-decompiled\` or the live def dump on the
owner's Windows machine, with the exact file+line citation preserved, or (b)
a def-name/mechanism I looked up independently this session and mark
accordingly. CONFIRMED means primary-source-verified (by this session or a
cited prior one); UNCERTAIN means inferred or secondhand — I say what would
close the gap.

---

## 1. The map-generation pipeline — where any dungeon content must slot in

CONFIRMED (`design/RimMandrake/map_content_injection_research.md` §5.1,
decompiled source `D:\Luke\dev\reference\rimworld-decompiled\`):

- Every map — a travel-to Site, a colony tile, a gravship landing — runs the
  **same `MapGenerator`**, which runs every active tile's `TileMutatorWorker.Init`
  then a sorted list of **96 `GenStepDef`s across Core + DLCs**
  (`Data/*/Defs/MapGeneration/`), each `Generate()` wrapped in its own
  try/catch (`MapGenerator.cs:309-345` — a throwing step loses only its own
  work, **silently**, and the run continues).
- **The order table that matters for dungeon authoring:**

  | order | step | what it fixes |
  |---|---|---|
  | 10-20 | `ElevationFertility` → `MutatorPostElevationFertility` | heightfield (mountains, lakes, craters) |
  | 200-240 | `RocksFromGrid` → `Terrain` → `MutatorPostTerrain` → `RemoveTinyIslands` | rock vs open ground |
  | 390-401 | `Roads` → `Settlement` → `SettlementPower` | faction bases |
  | **500** | `MutatorCriticalStructures` | mutator-owned structures — **Ancient Quarry, Ancient Uplink, Abandoned Colony** (Odyssey) |
  | 600 | `ReserveGravshipArea` | gravship footprint reserved AFTER settlements/critical structures |
  | 700-750 | `MutatorNonCriticalStructures` → `AncientRuins` → `ScatterRuinsSimple`/`Shrines` | ruins |
  | 850-875 | `FindPlayerStartSpot` → `ScenParts` | |
  | 900-970 | `Plants` → scatter groups (junk clusters, craters, debris, fences, mechs) → `RockChunks` | dressing |
  | 1120-1200 | `CaveHives` → `Animals` | fauna |
  | 1500 | `Fog` | everything enclosed fogs from here — **this is the vanilla "sealed until discovered" mechanism**, free, for any enclosed room with no path to a revealed cell |
  | 1600-1700 | `MutatorFinal` → `GravshipMarker` | |

  A structure sited **below 500** is something later steps must build around
  (`UsedRects`); above 600 it must itself avoid `UsedRects`.
- CONFIRMED **`GenStepParams` is `{sitePart, gravship, layout}`** — a GenStep
  knows whether it is running for a quest Site, a gravship landing, or neither.
- CONFIRMED **`TileMutatorWorker` hooks**: `Init`, `Tick`,
  `GeneratePostElevationFertility`, `GeneratePostTerrain`,
  `GenerateCriticalStructures`, `GenerateNonCriticalStructures`,
  `GeneratePostFog` (`TileMutatorWorker.cs:25-61`). ~50 Odyssey workers exist
  (`Data/Odyssey/Defs/TileMutators/`): `Lake*`, `Cliffs`, `Dunes`, `Fjord`,
  `Bay`, `Cove`, `Archipelago`, `Basin`, `Wetland`, `HotSprings`, `IceCaves`,
  `Lava*`, `Oasis`, `Valley`, `Plateau`, **`AncientQuarry`/`AncientRuins`/
  `AncientVents`/`AncientUplink`**, **`AbandonedColony*`**, `InsectMegahive` —
  these are Odyssey's "landform" system, and several are themselves
  dungeon-shaped (a whole tile's critical structure).
- CONFIRMED **refresh APIs** for any post-hoc structural edit:
  `RegionAndRoomUpdater.RebuildAllRegionsAndRooms()`,
  `FloodFillerFog.FloodUnfog(root, map)`, roof grid `SetRoof`, power-net
  rebuild. This is how a live-injected structure (or, offline, a mod that
  breaches a sealed vault) re-syncs regions/fog/power after the fact.

---

## 2. `PrefabDef` — vanilla's own **hand-authored fixed layout** format

CONFIRMED, decompiled source (`map_content_injection_research.md` §5.1):

- 🔑 **`PrefabDef` is the answer to "can an author place a specific fixed
  layout by hand."** `PrefabUtility.SpawnPrefab(PrefabDef, Map, IntVec3 pos,
  Rot4 rot, Faction, List<Thing> spawned, Func overrideSpawnData, Action
  onSpawned, bool blueprint)` (`PrefabUtility.cs:46`) is a plain static call —
  no gen-time coupling, works on an **already-running map**.
  `CanSpawnPrefab` (line 15) pre-checks fit. Vanilla ships
  `DebugActionsPrefabs` with `SpawnPrefab`/`SpawnPlayerPrefab` at the mouse
  cell.
- 🔑 **Vanilla ships an EXPORTER.** `DebugActionsPrefabs.CreatePrefab` →
  `PrefabUtility.CreatePrefab(rect, copyAllThings, copyTerrain)` prints
  ready-to-paste `<PrefabDef>` XML from a live-built rect. Build a scene
  through the bridge/dev tools, export it, ship it as data.
- CONFIRMED **PrefabDef vocabulary**: `PrefabThingData` (per-thing `stuff`,
  `colorDef`/`color`, `stackCountRange`, `hp`, `chance`, `quality`,
  `position`/`positions`/`rects`, `relativeRotation`), `PrefabTerrainData`
  (terrain by `rects`, `chance`), `SubPrefabData` (nested sub-prefabs with
  `chance`), whole-prefab `rotations`. Probabilistic variation is native
  (every stool at 0.66 chance in vanilla's `AncientPrefabs.xml`).
  **What it lacks: pawns, roofs, a filth/damage-aging pass, and any siting
  logic** (where on the map, near what) — a prefab is placed by a caller that
  already decided the cell.
- CONFIRMED **a live prefab census on the owner's real mod list** (bridge
  probe, `map_content_injection_research.md` §5.7): 47+ shipped prefabs
  enumerable via the generic debug-action executor, e.g.
  `AncientSystemRacks_Rows`, `Exterior_CrashedCrane`, `CrashedShuttle`,
  `Exterior_AncientBunker` — real defNames, present and spawnable.
- **This is the single strongest "author a specific room by hand" primitive
  vanilla ships.** It is thing-and-terrain-only; it composes with the Layout
  system (§3) for room-scale content and with `SitePartDef`/`GenStepDef`
  (§4) for siting on a travel-to map.

---

## 3. The `LayoutDef`/`LayoutWorker` system — vanilla's *procedural* dungeon generator

CONFIRMED, decompiled source (`map_content_injection_research.md` §5.1) plus a
second confirmation via a mod's own decompiled reference to the vanilla
classes it wraps (`design/Jawa/worldbuilding/complexlayoutdef_acm_reference.md`):

- **`LayoutWorker*` subclasses that ship in vanilla**: `Complex`,
  `Complex_Ancient`, `Mechanitor`, `AncientStockpile`, `Labyrinth`,
  `OrbitalPlatform`, `SimpleRuin`, `Structure`. `LayoutWorkerComplex_AncientComplex`
  is the one behind the vanilla **Ancient Complex** — confirmed by name from
  a third-party mod's own `LayoutWorkerComplex` class explicitly written to
  NOT be this vanilla one, and by `LayoutDefOf.AncientComplex` /
  `LayoutDefOf.AncientComplex.Worker.GenerateStructureSketch` being called as
  vanilla's own fallback generator (`complexlayoutdef_acm_reference.md` point 1).
  ⇒ **`LayoutDef AncientComplex` is CONFIRMED to exist** (via `LayoutDefOf`
  member); its full field list is UNCERTAIN pending a direct dump/decompile
  read on this machine.
- **The composition mechanism**: a `LayoutWorker` runs
  `RoomLayoutGenerator.GenerateRandomLayout` (a shared `BaseGen` utility —
  the SAME generator vanilla's Ancient Complex uses; a mod's decompiled
  comment names **Biotech's "Sanguophage vaults"** as another consumer of
  this exact utility — **UNCERTAIN**, secondhand from a mod dev's comment,
  not independently verified this session; confirm via `LayoutDefOf` census
  or `grep RoomLayoutGenerator` in the decompiled source) to produce a
  `LayoutSketch` of rooms, then furnishes each room via `LayoutRoomDef`s
  (`RoomContentsWorker` + `RoomPart_*`: **`Crate`, `InsectHive`,
  `DormantMechCluster`, `SentryDrone`, `Barricades`, `Corpse`,
  `ConnectConduits`** — confirmed names, `map_content_injection_research.md`
  §5.1).
- 🔑 **This is genuinely a different axis of authoring from a fixed
  `PrefabDef`/hand-placed template: a `LayoutRoomDef` names a *pool* of room
  content and the C# only orchestrates picking + a threat/loot budget — it
  never hardcodes what a room contains.** (This exact pattern, read from a
  mod's decompile of `LayoutWorkerComplex`/`GenStep_RandomAncientComplex`,
  is explicitly the SAME shape vanilla's own Ancient Complex generator uses,
  per `complexlayoutdef_acm_reference.md`.) So vanilla's dungeon generator is
  **weighted-room-pool + weighted-threat-budget**, not a fixed map: an author
  can write new `LayoutRoomDef`s/`RoomPart_*` content into the existing pool,
  but cannot pin an exact room-by-room floor plan through `LayoutDef` alone.
  For an exact floor plan, use `PrefabDef` (§2) or a `CustomMapDataDef`-style
  whole-map format (§8).
- ⚠️ **`LayoutWorker.GenerateStructureSketch` reads
  `MapGenerator.mapBeingGenerated?.NextGenSeed`** — it is **gen-time coupled**;
  it cannot be re-run against an arbitrary live map the way `PrefabDef` can.
- UNCERTAIN, flagged as a real gap this session did not close: the exact
  field list of `LayoutRoomDef`, `LayoutPartDef` (from the user's original
  lead list — **not independently confirmed to exist as a distinct def type
  this session**; `LayoutRoomDef` is confirmed by name, `LayoutPartDef` is
  not — it may be folded into `RoomPart_*` C# classes rather than a separate
  Def type). Confirm with `measure count LayoutPartDef` once run against a
  live dump.

---

## 4. `SitePartDef` → `GenStepDef` → map — the travel-to dungeon shape

CONFIRMED, both from decompiled-source citations and from this campaign's own
built, offline-validated quest family
(`design/Jawa/worldbuilding/vault_thaw_quest_family.md`,
`design/validation_walks/RimUtinni/VaultDungeons.md`):

- A travel-to Site is a **world object** (a `Site : MapParent` on the world
  map) built of one or more `SitePartDef`s. `SiteMaker.MakeSite` **never
  calls `SitePartDef.FactionCanOwn`**, so a hidden/custom faction can own a
  quest site (CONFIRMED, `vault_thaw_quest_family.md`).
- Each `SitePartDef` carries `minMapSize`, `wantsThreatPoints` and other
  siting fields; a paired `GenStepDef` with `linkWithSite` runs at mapgen and
  reads `GenStepParams.sitePart` to place that part's content.
- **`SitePartWorker.PostMapGenerate(Map)` is a sanctioned post-generation
  hook** for site-specific setup (spawning the quest-specific state after the
  standard pipeline finishes) — CONFIRMED,
  `map_content_injection_research.md` §5.1.
- **A concrete, real worked example, built and validated in this repo**
  (`VaultDungeons.md`): `SitePartDef RUT_VaultSite_Type1` (`minMapSize
  325×1×325`, `wantsThreatPoints=false`) pairs with `GenStepDef
  RUT_GenStep_VaultSite_Type1` (`linkWithSite = RUT_VaultSite_Type1`) whose
  `genStep` class cites a `StructureLayoutDef` by defName. The layout format
  used there (`KCSG.GenStep_CustomStructureGen`) is a **third-party** (VE
  Framework) fixed-template consumer, not vanilla — vanilla's own equivalent
  for "one exact hand-authored floor plan, sited by a SitePartDef" is
  `PrefabDef` (§2) or the whole-map format in §8, either spawned from a
  `GenStepDef`/`SitePartWorker.PostMapGenerate`.
- **Threats are budgeted, not placed 1:1**: `wantsThreatPoints` feeds a points
  budget the site's `GenStepDef`/`LayoutWorker` (§3) spends on threat
  defs, each with `chancePerComplex`/`selectionWeight`/`maxPerComplex`/
  `maxPerRoom` caps (CONFIRMED shape, `complexlayoutdef_acm_reference.md`,
  describing the same budget mechanism vanilla's Ancient Complex threat list
  uses).

---

## 5. Pocket maps and `MapPortal` — vanilla's **sealed sub-structure** primitive

This is the closest vanilla shape to shape (b) from the brief — *a sealed
sub-structure opened by breaching/entering something on the surface map* —
and it is a **first-class Anomaly mechanism**, reused successfully by this
campaign for two different builds. CONFIRMED, cross-checked across three
independent repo documents plus one real shipped-XML worked example:

- **`Verse/PocketMapProperties.cs`**: `biome`, `temperature`, `tileMutators`,
  `destroyOnParentMapAbandoned` — the fields that fix a pocket map's
  character regardless of the parent map it is entered from.
- **`PocketMapUtility.GeneratePocketMap`** builds the pocket map; entry is
  through a **`MapPortal` building** on the parent map. This is exactly the
  Anomaly **Labyrinth** pattern:
  `Anomaly/Defs/MapGeneration/LabyrinthMapGenerator.xml`
  (`design/Jawa/worldbuilding/aquatic_movement_routes.md`).
- **The Labyrinth's only door, confirmed by name**: `ThingDef
  WarpedObelisk_Abductor` is **the sole route into the Labyrinth pocket
  map** — removing it orphans `LayoutRoomDef LabyrinthObelisk`
  (`design/Jawa/worldbuilding/cherrypick_inbox.md`,
  `cherrypick_resolved.md`). Note the def-name collision trap here too: an
  `IncidentDef` of the identical name `WarpedObelisk_Abductor` also exists —
  a real, previously-hit "same name, different type" hazard worth carrying
  into any dungeon-key design that names its own defs after in-fiction props.
- **Anomaly's `PitGate` (ThingDef + IncidentDef) is `PitGate : MapPortal`,
  fully self-contained** (own lifecycle; `portal/pocketMapGenerator=Undercave`,
  `portal/exitDef=CaveExit` per `design/V2_DREAMS.md` §"THE SARLACC", verified
  from the live def dump 2026-08-31). `Undercave` is **both a
  `MapGeneratorDef` and a `BiomeDef`** — "the place you arrive." Its own
  gen-step chain, confirmed by name: `Fleshbulbs, RockChunks, PlaceCaveExit,
  Dreadmeld, Fleshmass, FleshSacks, UndercaveInterest, Plants`.
  **`FleshmassHeart` is confirmed SURFACE-ONLY** — its `IncidentDef` targets
  `Map_PlayerHome` only, and nothing in `UndercaveMapComponent` or that
  gen-step chain references it, so an author wanting a fleshmass-heart-style
  climax at the bottom of an Undercave-shaped pocket map must place it
  themselves.
- 🔑 **Pocket-map nesting is UNENFORCED by the engine.**
  `MapPortal.GeneratePocketMapInt` never checks `base.Map.IsPocketMap` —
  CONFIRMED (`design/Jawa/worldbuilding/sarlacc_spec.md` §"the portal", a
  RimSage-sourced measurement). **This means chained/nested dungeons (shape
  (c) in the brief) are legal today with zero new C#: a `MapPortal` placed
  ON a pocket map opens a second pocket map beneath it, arbitrarily deep.**
  The one real soft risk carried in this repo's build: transport/quest
  helpers (`ShipJob_Arrive`, `QuestGen_TransportShip`) resolve "the real map"
  only one level up, so no shuttle/quest logic may target a level below the
  first.
- **Sealing/collapse mechanics, both confirmed on a real shipped comp and a
  real vanilla timer:**
  - `CompProperties_Sealable` with `destroyPortal=true` **permanently
    destroys the portal** on sealing; paired with
    `CompProperties_LeaveFilthOnDestroyed` it drops filth and — per the
    comp's own confirm text — **anyone left below is lost**. This is a real,
    lint-clean, built ThingDef in this repo
    (`design/validation_walks/RimUtinni/LanternDeeps.md`), i.e. it is a
    genuine vanilla-comp composition, not invented.
  - Vanilla's own **collapse timer**: `BeginCollapsing()` arms a ~25,000-tick
    countdown with staged rumble/roof-drop warnings, then the map dies,
    killing everyone left on it (`sarlacc_spec.md` §"the collapse is the exit
    bell" — read from vanilla PitGate/Undercave behavior). **This is a real,
    reusable "the dungeon has a clock, leave or die" primitive**, not custom
    work.
- **A complete, real worked XML example of a hand-authored pocket-map
  dungeon**, built and (partially) validated in this repo
  (`design/validation_walks/RimUtinni/LanternDeeps.md`):
  ```xml
  <!-- the door: -->
  <ThingDef>
    <defName>RUT_LanternDeepEmergence</defName>
    <thingClass>MapPortal</thingClass>
    <size>(6,6)</size>
    <passability>Impassable</passability>
    <holdsRoof>true</holdsRoof>
    <destroyable>false</destroyable>
    <portal>
      <pocketMapGenerator>RUT_LanternDeepGenerator</pocketMapGenerator>
      <exitDef>CaveExit</exitDef>
      <pocketMapSize>66</pocketMapSize>
    </portal>
  </ThingDef>
  <!-- the room beyond it: -->
  <MapGeneratorDef>
    <defName>RUT_LanternDeepGenerator</defName>
    <isUnderground>true</isUnderground>
    <forceCaves>true</forceCaves>
    <ignoreAreaRevealedLetter>true</ignoreAreaRevealedLetter>
    <disableCallAid>true</disableCallAid>
    <pocketMapProperties>
      <biome>BMT_CrystalCaverns</biome>
      <temperature>17</temperature>
    </pocketMapProperties>
    <genSteps>
      <li>BMT_CrystalsGenerator</li>
      <!-- + the standard underground terrain/rock/plant/fog steps -->
    </genSteps>
  </MapGeneratorDef>
  ```
  This confirms every field name above is real and load-bearing (the file's
  own validation walk checks each one against a live def read-back), and it
  confirms a **biome-gated, low-probability natural-emergence scatter**
  pattern too: `GenStep_ScatterCavePortal` (custom C#, extends vanilla
  `GenStep_ScatterGroup`) rolls `Rand.Chance(chancePerMap)` and checks
  `map.Biome.defName` against a hardcoded allow-set before placing the door
  — because **`GenStepDef` has no biome field of its own**, so a biome gate
  on a scatterer is always author-written logic, never a vanilla XML field.
- **`SpaceMapParent`** (Odyssey) is the third sealed-structure shape:
  a `WorldObjectDef` subclassing `SpaceMapParent` picks its `MapGeneratorDef`
  via `def.mapGenerator`, and a `MapGeneratorDef` family can be built by
  `ParentName` inheritance off Odyssey's own `Space`→`Asteroid` pair
  (CONFIRMED, `design/Jawa/worldbuilding/depths_build_spec_v1.md`). This is
  Odyssey's own vocabulary for "a place in space you fly a shuttle to and
  land inside," structurally parallel to a pocket map but reached via the
  world map / orbit layer rather than a portal building.

---

## 6. Scatter family — how loot and set-pieces actually get placed

CONFIRMED (`map_content_injection_research.md` §5.1, §Jawa
`tile_augmentation_catalogue.md`):

- **301 live `GenStepDef`s** on the owner's real mod list; the vanilla
  scatter vocabulary: `GenStep_Scatterer` (abstract base: `count`, spacing,
  edge/pollution/faction filters, abstract `ScatterAt`) →
  `ScatterRuinsSimple`, `AncientComplex`, `ScatterAncientMechs`,
  `ScatterAncientTurret`, `ScatterAncientUtilityBuilding`,
  `ScatterAncientLandingPad`, `ScatterShrines`, `ScatterLayout`,
  `GenStep_ScatterThings`, `GenStep_ScatterGroup`, `GenStep_Outpost`,
  `GenStep_ScatterGroupPrefabs`. **There is no separate `ScatterableDef`
  type** — scatterers are plain `GenStepDef`s with a workerClass.
- **`GenStep_ScatterGroup`/`GenStep_ScatterGroupPrefabs` are pure XML** —
  vanilla's own "junk clusters" need zero C#.
- 🔑 **Can loot be placed by hand at a coordinate?** Two confirmed vanilla
  routes: (a) inside a `PrefabDef`, every thing carries an explicit
  `position`/`positions`/`rects` (§2) — this is literal hand-placement; (b)
  inside a Layout-generated room, loot is a `ThingSetMakerDef` output resolved
  through `LayoutWorker.FindBestSpawnLocation` (a heuristic "somewhere
  sensible in this room," not an exact cell) — CONFIRMED by name from
  `complexlayoutdef_acm_reference.md`'s read of the vanilla-shaped
  `SpawnThings`/`FindBestSpawnLocation` pattern.  A real, first-discovery
  "letter on finding loot" mechanism exists too: an optional `RectTrigger` +
  `SignalAction_Message` per room firing a `thingDiscoveredMessage`
  (same source).

---

## 7. What each DLC actually adds, dungeon-wise

| DLC | dungeon-shaped content, CONFIRMED | mechanism |
|---|---|---|
| **Core** | Ancient Complex, ancient ruins/shrines, ancient danger (locked door + mechanoid guard — the original vanilla "one-room dungeon") | `LayoutWorkerComplex_AncientComplex` (§3), `GenStep_ScatterRuinsSimple`/`AncientComplex`, `PrefabDef` ancient prefabs |
| **Ideology** | **none found.** Checked explicitly this session (grep across every repo doc that reads Ideology content for dungeon/layout/site terms) — Ideology's own content is ideoligions/rituals/relics, not map structures. Mark this a real, checked-and-absent finding, not an omission. | — |
| **Biotech** | Mechanitor-related layout (`LayoutWorker Mechanitor`, confirmed by name, §3); "Sanguophage vault" content reusing `RoomLayoutGenerator` — **UNCERTAIN**, secondhand from a mod dev's decompiled comment, not independently confirmed against vanilla Biotech defs this session | `LayoutWorker*`, `RoomLayoutGenerator.GenerateRandomLayout` |
| **Anomaly** | The deepest vanilla analogue to an authored dungeon: **PitGate → Undercave** (pocket-map descent, gen-step chain, surface-only heart, collapse timer) and **Warped Obelisk → Labyrinth** (the other pocket map, one obelisk = one door, `LabyrinthMapGenerator.xml`). Plus the **monolith research-gate** (`minMonolithLevel > Find.Anomaly.HighestLevelReached`, only live when `AnomalyPlaystyleDef.generateMonolith=true`) and `EntityCodex`/`HiddenItemsManager` reveal machinery (§9). | `MapPortal`, `PocketMapUtility`, `Anomaly/Defs/MapGeneration/*`, `Find.Anomaly` |
| **Odyssey** | ~50 terrain-and-structure `TileMutatorWorker`s including **critical structures at gen order 500** (`AncientQuarry`, `AncientUplink`, `AncientVents`, `AbandonedColony*`) — a whole tile's dungeon-shaped centerpiece, assigned by `LandmarkDef`/world-gen; `SpaceMapParent` (§5) for orbit/space POIs; the live `PrefabDef` exporter (`DebugActionsPrefabs`) and `requireInspectedGravEngine` build-gate; gravship landing itself running the standard mapgen pipeline (`GravshipUtility.cs:540,660`). | `TileMutatorDef`, `SpaceMapParent`, `PrefabUtility` |

---

## 8. Whole-map-as-data — the format vanilla does NOT ship, but a sibling class exists

CONFIRMED (`map_content_injection_research.md` §5.6, P13): vanilla ships **no**
def type for "a whole fixed map as flat data" — `LayoutDef` is a room-pool
generator (§3), `PrefabDef` is thing/terrain-only (§2). The closest thing
to shape (a)/(c) "one big fixed handmade dungeon map" in the *engine's own
vocabulary* is composing many `PrefabDef`s across a `SitePartDef`'s
`GenStepDef`, OR reusing the pocket-map primitive (§5) at whatever size is
wanted (`pocketMapSize` is a plain field, `LanternDeeps`'s example uses 66;
this campaign's vault dungeons use 325×325 fixed-tile Sites, §4). A true
"paste a full 200×200 map verbatim" format (`CustomMapDataDef`) is a
**third-party** mod format (Ancient Urban Ruins / Dungeon Core), not vanilla
— out of this file's scope, see LOCAL_MODS.md.

---

## 9. Gating — the real mechanisms, enumerated

CONFIRMED, primary-source read in a prior session and preserved with line
citations (`design/Jawa/anomaly_exception_access_spec.md` §1, decompiled
source):

The full chain `Designator_Build.Visible` walks, **in order**, before a
building is even offerable — every one of these is a real gate an author can
pull:

1. faction tech level (`minTechLevelToBuild`/`maxTechLevelToBuild`)
2. **research**: `entDef.IsResearchFinished` — every listed
   `researchPrerequisites[i].IsFinished` (`BuildableDef.cs:172`)
3. **Anomaly monolith level**: `minMonolithLevel > Find.Anomaly.HighestLevelReached`,
   but only when `AnomalyPlaystyleDef.generateMonolith` is true for the active
   playstyle (same guard on the Anomaly architect category and on
   `CompHoldingPlatformTarget.CanBeCaptured`)
4. `difficulty.AllowedToBuild`
5. any custom `PlaceWorker.IsBuildDesignatorVisible(def)`
6. `buildingPrerequisites` (colonists must already own building X)
7. 🔑 **`discoveryPrerequisites`** — a `List<ThingDef>` on `BuildableDef`
   (line 56); hidden while `Find.HiddenItemsManager.Hidden(thingDef)` is true
   for any listed def. **This is a vanilla "reveal gate independent of the
   research tree," saved automatically, flipped by one call
   (`Find.HiddenItemsManager.SetDiscovered(def)`)** — the cleanest primitive
   for "this dungeon/building is invisible until an event says otherwise."
8. Odyssey `requireInspectedGravEngine`

Other confirmed gates, same source:
- **`EntityCodex.Hidden(def)`**: a `ResearchProjectDef` can be hidden from the
  research tab only if it is listed in some `EntityCodexEntryDef.discoveredResearchProjects`
  of an undiscovered entity (`EntityCodex.cs:61-80`) — narrower than
  `discoveryPrerequisites` and entangled with the Anomaly codex UI.
- **`ResearchManager.FinishProject`** is a public API that can finish a
  research project from code with no player action (`ResearchManager.cs:403-507`,
  fires `Notify_UnlockedByResearch` + the `ResearchCompleted` signal) — a
  quest/event can grant a tech tree unlock outright.
- **Fog** (`Fog` genstep, order 1500, §1) is the free, structural version of
  "sealed until discovered" for any enclosed, unreached room — no extra
  authoring needed if the room is simply enclosed with no path to a revealed
  cell.
- **Doors are NOT one-way and vanilla has no native "locked until X" door
  comp** (CONFIRMED, `skills/rimworld-layout-layers/references/layer-mechanics.md`:
  `TraverseMode` = `ByPawn, PassDoors, NoPassClosedDoors, PassAllDestroyableThings,
  …` — a closed door either blocks a given traverse mode or doesn't; there is
  no directional/keyed variant in the enumerated modes). A "locked until you
  have the key" door is therefore always a custom `ThingComp` (pattern:
  `CompProperties_Sealable` from §5, which is a real, cheap, composable
  building block for exactly this) or a forbidden-area/power gate, never a
  bare vanilla field on `Building_Door`.
- **Quest signals** (`skills/rimworld-quests/SKILL.md` §1, §6): a
  `QuestScriptDef`'s node tree runs ONCE at generation and leaves `QuestPart`s
  that talk only by signal string — the standard vanilla way to arm "open
  this once event X fires," and the standard vanilla way for it to fail
  silently (a renamed `storeAs` kills every listener on it with no error).

---

## 10. The story layer — how a place tells the player something

CONFIRMED mechanisms actually available, cross-referenced against the quest
skill and the pocket-map examples above:
- **Letters/messages**: `SignalAction_Message`, a `thingDiscoveredMessage` per
  room on first find (§6) — the vanilla "you found something" beat, no quest
  needed.
- **Quest text**: `questNameRules`/`questDescriptionRules` grammar rules,
  resolved once at generation (`rimworld-quests` SKILL.md §3) — the standard
  vanilla channel for "why this place matters," but generated once and frozen;
  it cannot react to what the player does inside the dungeon without a
  signal-driven follow-up quest part.
- **Inspect strings / descriptions**: plain `ThingDef.description` /
  `LayoutRoomDef` flavor — static, authored per def, no runtime logic.
- **HistoryEventDef + signals**: this campaign's own build
  (`VaultDungeons.md`) uses exactly this for outcome tracking — 8
  `HistoryEventDef`s (`RUT_VaultSleepersWoken`, `RUT_HelixSidedWithTheWoken`,
  etc.) as the "memory substrate" a quest's signal listeners react to. This
  is a real, generalizable pattern for "the dungeon remembers what you did."
- **Custom `ThingComp`s** are the escape hatch for anything reactive inside
  the dungeon itself (a console that reacts to being interacted with, a
  socket that checks for a specific item) — vanilla ships the comp framework
  but no "puzzle comp" of its own; every interactive object beyond a
  fixed-description prefab is author-written C#.

---

## 11. What CANNOT be done — the hard walls

1. **No vanilla def type stores a whole fixed map as flat per-cell data.**
   (§8) `LayoutDef` procedurally generates room arrangements from a pool;
   `PrefabDef` places things+terrain but has no pawns, no roofs, no siting
   logic, and is capped in practice by whatever rect you export
   (`DebugActionsPrefabs`'s own dev-mode exporter is documented elsewhere as
   size-limited when driven through the third-party KCSG exporter, ≤51×51 —
   **UNCERTAIN** whether that cap is KCSG's own or shared with vanilla's
   `CreatePrefab`; not confirmed against vanilla source this session).
2. **`LayoutWorker.GenerateStructureSketch` is gen-time seed-coupled**
   (§3) — a Layout-based room arrangement cannot be regenerated deterministically
   against a live, already-generated map; only `PrefabDef` and pocket-map
   spawners (§2, §5) can be invoked live.
3. **No vanilla field puts a biome gate on a `GenStepDef`.** (§5, the
   `LanternDeeps` finding) — any "only scatter this dungeon door in cold
   biomes" logic is always hand-written C#, string-compared against
   `map.Biome.defName`.
4. **No vanilla door is one-way or natively lockable by a key/item/hediff.**
   (§9) `TraverseMode` only distinguishes "can pass a closed door at all," not
   direction or ownership of a key. A keyed door is always a custom
   `ThingComp` layered on `Building_Door`.
5. **`SitePartDef`/`WorldObjectDef` have no goodwill field**
   (CONFIRMED, `design/Jawa/worldbuilding/the_forgotten_war.md:293`) — a
   dungeon site cannot itself carry a faction-relations consequence; that has
   to be modeled as a quest reward/outcome instead.
6. **A GenStep that throws fails silently** (§1) — there is no vanilla
   "did my dungeon actually finish generating" signal; a broken GenStep
   produces a map that loads clean and is simply missing content, discoverable
   only by a human noticing or a quicktest read-back.
7. **No worldgen/second-planet capability is in scope for this campaign
   regardless of what the engine can do** — this is a standing project
   ruling (`CLAUDE.md`), not an engine limit, but it forecloses using any
   vanilla mechanism (world-gen landmarks, `WorldGenStep_Landmarks`) to
   *generate* dungeon placement; every site must be hand-assigned to the one
   frozen world.

---

## 12. Sources, for re-verification

Everything above traces to one of these; none is a fabricated defName —
where a name could not be pinned to a primary source this session, it is
flagged UNCERTAIN inline with what would confirm it (a live `measure count`,
a live def read-back, or an `ilprobe`/decompile pass, none of which this Mac
can run today).

- `design/RimMandrake/map_content_injection_research.md` §5.1, §5.6, §5.7 —
  decompiled-source pass, `D:\Luke\dev\reference\rimworld-decompiled\`
- `design/Jawa/anomaly_exception_access_spec.md` §1 — decompiled-source pass
  with exact file+line citations (`Designator_Build.cs`, `BuildableDef.cs`,
  `HiddenItemsManager`, `EntityCodex.cs`, `ResearchManager.cs`)
- `design/Jawa/worldbuilding/complexlayoutdef_acm_reference.md` — `ilspycmd`
  decompile of a third-party mod's own read of vanilla `LayoutWorkerComplex_AncientComplex`/`LayoutDefOf.AncientComplex`
- `design/Jawa/worldbuilding/sarlacc_spec.md`, `design/V2_DREAMS.md`
  ("THE SARLACC") — RimSage-sourced live-dump measurements of `PitGate`,
  `Undercave`, `FleshmassHeart`
- `design/Jawa/worldbuilding/aquatic_movement_routes.md`,
  `design/Jawa/worldbuilding/cherrypick_inbox.md`/`cherrypick_resolved.md` —
  `Anomaly/Defs/MapGeneration/LabyrinthMapGenerator.xml`,
  `WarpedObelisk_Abductor`/`LabyrinthObelisk`
- `design/validation_walks/RimUtinni/LanternDeeps.md`,
  `.../VaultDungeons.md` — real, lint-checked, partially def-read-back-verified
  shipped XML in this repo
- `design/Jawa/worldbuilding/vault_thaw_quest_family.md`,
  `design/Jawa/worldbuilding/dungeons_arc_spec.md` — `SitePartDef`/`GenStepDef`
  mechanics and this campaign's own built quest layer
- `skills/rimworld-layout-layers/references/layer-mechanics.md` — room/region/
  door mechanics, `Source/Verse/Room.cs` et al.
- `skills/rimworld-quests/SKILL.md` — quest/signal model
- `design/Jawa/worldbuilding/the_forgotten_war.md:293` — `SitePartDef` goodwill gap
