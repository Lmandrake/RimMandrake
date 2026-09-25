# Sea dive maps — design spec

Item: `SEA_DIVE_MAPS_BUILD_1`. Owner ruling (question card, 2026-09-25): **Build dive maps** —
diving opens a small underwater map where each sea's floor cast (the BiomeDef's `<wildAnimals>`)
actually spawns, one per sea, shared machinery across the four terminal seas (`RM_TheScald`,
`RM_GreySea`, `RM_TwilightSea`, `RM_PropaneLake`, all in `src/RimMandrake/TerminalBiomes`).

Status: RULED design, 2026-09-25 (§7), with the Scald floor worked in full (§7a rulings, §8
design, §8.8 open choices). Nothing built. Engine claims are labelled **MEASURED** (read in the
1.6 decompiled source via RimSage this sitting, symbol cited) or **UNMEASURED**.

## 0. Read first — what already exists (do not re-invent)

| already built | where | what it gives this spec |
|---|---|---|
| **A pocket map, in this repo, live-tested** | `src/RimUtinni/LanternDeeps/` — `RUT_LanternDeepGenerator.xml` (MapGeneratorDef with `pocketMapProperties`), `RUT_LanternDeepMineshaft.xml` (a `thingClass MapPortal` building), `Patch_PocketMapGrowthRate.cs`, `DeepFloraPlanter.cs` | the whole entry/exit/generator shape, plus two MEASURED pocket-map crashes and their fixes (§2.4) |
| Shore dive jobs | `src/RimMandrake/DivingInteraction/` (`RM_JobDriver_DiveBase/Hunt/Commune`, `RM_FloatMenuOptionProvider_Dive`, `RM_MapComponent_DiveSites`, `RM_DiveUtility.DiveEligibleTag`) | **the entry**: the float menu gets a third option, the job driver base is the descent, the map component owns the floor maps |
| Settings gate seam | `RM_MechanicGates` / `RM_MechanicGateExtension` (`EnvironmentalHazards`) — TerminalBiomes already registers `Scald.S1…S6` in `RM_TerminalBiomesMod.cs:192-196` | per-sea and per-mechanic toggles with zero new plumbing |
| Generic floor painters | `RM_GenStep_TerrainChannels` (random-walk channels of any TerrainDef), `RM_GenStep_ScatterPools` (3–6 spaced pools), `RM_GenStep_PlacedSetPieces` + `RM_SetPieceElement_AnchoredPawn`, `RM_ScattererValidator_NearThingDef` | Twilight's underwater rivers, Grey's brine pools, Scald's vents + sail clusters, statuary set-pieces |
| Weather forcing | `RM_GameCondition_WeatherPulse` / `GameCondition_EnvironmentalWeather` (override `GameCondition.ForcedWeather()`) | one held "murk" weather per floor |
| A dive clock | `HediffCompProperties_EnvironmentalExposure` — accrues while unroofed during listed weathers, heals otherwise, apparel stat slows it | the breath/exposure budget with no new hediff comp |
| Sea terrains | `RUT_ScaldWater*` (burnDamage 1/2), `RM_PropaneLakeDeep`/`RM_SolidPropane`, `RM_WastelandBrine*` (Wasteland mod — a brine pair already exists) | floor and hazard terrain per sea |
| The cast, already on the defs | 14 `RM_` floor residents in `Defs/ThingDefs_Races/RM_*Fauna.xml`, wired in each sea's `<wildAnimals>`; `fishTypes` on all four defs; `RM_ScaldWalkerChitin` (DivingInteraction) as the walker's drop | the shared machinery authors no creature; the Scald's four new residents (walker, swirl, guardian, swarm) are §8.2 |

## 1. The experience

**Shared shape (all four seas).** On the shore, right-click any `RM_DiveEligible` shallow cell:
beside today's "Dive to hunt" / "Dive to commune" is **"Dive down"**. No building. The colonist
walks there, holds position (the same wait toil the shore jobs use), and goes **under**: the first
descent generates that sea's floor map (100×100) and it **persists** — animals live on, harvest
regrows, wrecks stay chiselled; every later dive from any shallow cell of that sea on that map
lands on the same floor. Below, a **surface line** — a rope trailing up into the murk, the exit —
is the only way up, and its glow is the only light you did not bring; going up returns you to the
cell you last dived from. The floor is fully roofed by the water column ("the sea is the roof"):
permanently dim, no sky, no flyers, no drop pods, no raids (pocket maps are outside the
storyteller's target list — MEASURED, `StorytellerUtility.DefaultThreatPointsNow` redirects a
pocket map to its `sourceMap`). The map edge is open floor running off into murk; the floor cast
**walks in from the edges** exactly as surface wildlife does, so each sea's `<wildAnimals>`
populate by vanilla rules and keep repopulating. What you carry down is what is on you (apparel,
inventory); what comes up rides the surface line's vanilla load dialog (haul-to-portal).

Every dive is on a clock: **deep exposure** (§4) rises while a diver stands in the open on the
floor and heals only under a roof-in-the-roof (an air-bell: any built or natural sub-roof cell,
or the surface) or back on land. The player's job on a dive is to get in, take what the sea gives,
and get out before the clock says otherwise. Bringing something back means carrying it to the
surface line — the vanilla portal load/unload flow, unchanged.

**Per sea — what you see, what you take, what it costs.** Each respects its FROZEN sheet's bans.

| sea | the floor you walk | what is down there | the clock | bans honoured |
|---|---|---|---|---|
| **Scald** (`the_scald.md`, worked in §8) | a dark, unlit plain ringed by **chimney fields** of boiling cloud (three heat zones, §8.1); **bottom-walker** herds grazing the field edges and laying **Crowncarpet** (Deepfire's mat) behind them, lit by the **swirl** that feeds on them; **guardians** at the herds, **scalding swarms** at the chimneys; **shulla** shoals, **noohm** drifting; **wreckage** scattered on every floor and, on one hex, the mineral-crusted **Rakatan vessel** with dormant droids around it (§8.4) | Crowncarpet → Deepfire, walker chitin, **nodules** (gold, silver, uranium, Chimney Iron, magnetite, uraninite, Seep Salt, Pyrinth), **Mother-of-Scaldpearl** on the chimney flanks, wreck salvage; the one place the shoal-fish are *seen* not just caught | **heat as zones**: 55 °C ambient everywhere, `burnDamage` 0 / 3 / 8 by zone terrain (`HediffGiver_Terrain`, the shore jobs' own mechanism); the suit's heat armour is the gate (§8.1, §8.6) | ban 3 (crossing scald water always costs — heat + burn, no immunity item); ban 4 (the floor is "merely hot", nothing swims the boil: the map IS the depth, the surface never becomes walkable); ban 1 (nothing potable — no water source down here); ban 5 (nothing cools or drains it) |
| **Grey Sea** (`the_grey_deep.md`) | grey-green murk, a **pillar forest** (pale mineable pillar stone), **brine pools** with shores, the **statuary** (encased dead as mineable/chisel objects) | soluble minerals dip-harvested at pool **shores**, pillar stone, jacketed salvage, the giant's shed crust; **fessk** watching, **otheska/sorruth** grazing | **cold + brine**: 4 °C; pool water is `RM_WastelandBrineDeep` (impassable, so ban 1 is structural) ringed by `…BrineShallow` (`dangerous`, the harvest cell) | ban 1 (no survivable pool entry: deep brine is Impassable — engine-enforced, not a rule); ban 2 (no schools: `wildGroupSize 1` on every Grey kind); ban 4 (no glow: no glowing flora, the only light is the surface line and what you carry); ban 5 (statuary never rots: they are Buildings, not corpses) |
| **Twilight Sea** (`the_twilight_deep.md`) | green dusk under the **mat-roof**, **skylight** columns (a few unroofed light-well cells — the one place a flyer could enter, and the *only* natural light), **mud-channel rivers** (impassable "sinking water" channels with rich banks), kelp towers, and **lit Compact dwellings** on the banks (v1: a set-piece of 2–3 huts + lamps, uninhabited by pawns; the inhabited town is the sheet's v2) | bank harvest (the richest gathering ground), kelp, **noolim** shoals in the light columns, **loohn** hanging in the dark between | **mild**: 14 °C, the longest clock of the four — the comfortable sea, by ruling | ban 3 (no swimmable river: channels are Impassable); ban 4 (Compact never hostile: no pawns spawn, nothing attacks from the huts); ban 5 (no permanent skylight: regenerated per map, never a building); ban 1 (nothing this map does touches the surface roster) |
| **Propane Lake** (`the_propane_lakes.md`) | black **solid-propane floor** (`RM_SolidPropane`) under liquid fuel; **tholin dust** fallout, the Blue Desert's arrived dead as salvage, and the **war lab's** outer wall as a locked set-piece (a sealed ancient door — nothing inside in v1) | **oovanam** sifting the dust, **heemin** shimmer in the fuel layer above (rendered as the map's weather, not a pawn: they are the catch, `fishTypes`), the **vaunoom** as a rare arrival that hunts pipe-and-pawn | **cold**: **−79 °C** map temperature; hypothermia is the whole clock and it is short. Fuel above: any fire/explosion on the floor is a map-wide ignition (§4) | ban 4 (no ignition without a source: the map ignites only from a heat or spark event); ban 8 (lab guardians stay mechanoid/ancient — a door, no fauna); ban 3 (no standing visibility penalty: the murk here is dark, not fog); ban 6 (nothing native leaves — the surface line's `CanEnterPortal` check refuses tamed natives, §4) |

Hoolen (surface skimmer) and the two `AA_` flyers stay surface `wildAnimals` and are excluded
from the floor spawn (§3.3).

## 2. Engine route

### 2.1 Pocket map lifecycle (MEASURED)

- **`PocketMapUtility.GeneratePocketMap(size, generatorDef, extraGenSteps, sourceMap)` is a
  public static** that needs no building: it makes a `PocketMapParent` world object (`sourceMap`,
  `mapGenerator`), runs `MapGenerator.GenerateMap(..., isPocketMap: true)`, adds it to
  `Find.World.pocketMaps`. `DestroyPocketMap` removes it and `DeinitAndRemoveMap`s. The only
  building-coupled piece in vanilla is the **exit**: `GenStep_PlaceCaveExit` hard-spawns
  `ThingDefOf.CaveExit`, and `PocketMapExit.SpawnSetup` binds to
  `PocketMapUtility.currentlyGeneratingPortal` (logs "could not find map portal" and leaves
  `entrance` null if none). ⇒ the floor generator **omits `PlaceCaveExit`** and spawns its own
  exit class (§2.3), which is a `MapPortal` but not a `PocketMapExit`.
- `MapPortal : Building, IThingHolder` (`RimWorld/MapPortal.cs`) — `GetOtherMap()` /
  `GetDestinationLocation()` / `EnterString` are `virtual`; `Dialog_EnterPortal`,
  `JobDriver_EnterPortal`, `WorkGiver_HaulToPortal` and `JobGiver_ExitMap`'s pocket branch all go
  through those virtuals or `ThingRequestGroup.MapPortal`, which `Includes` **any
  `MapPortal` subclass** (`ThingListGroupHelper.Includes`: `typeof(MapPortal).IsAssignableFrom`).
  So a surface-line exit that answers "other map = the surface map, destination = the dive cell"
  gets the whole up-flow (load dialog, hauling, fleeing pawns head for it) for free.
- A `Map` is `Scribe_References`-able (`MapPortal.ExposeData` does exactly that with
  `pocketMap`), so a `MapComponent` can own floor maps across save/load.
- `MapGenerator.GenerateMap` (isPocketMap branch, lines ~128-137): `map.info.isPocketMap = true`;
  `map.pocketTileInfo = new Tile { PrimaryBiome = pocketMapProperties.biome }`; the properties'
  `tileMutators` are added to that tile. `map.TileInfo` returns `pocketTileInfo` for pocket maps
  (`Map.cs:394`). **So the floor map's biome IS the sea BiomeDef**, and its `<wildAnimals>` are what
  `WildAnimalSpawner` reads (`map.BiomeAt(loc).AllWildAnimals`).
- `PocketMapProperties`: `biome`, `tileMutators`, `temperature`, `destroyOnParentMapAbandoned`
  (default true), `preventPrisonerEscape`, `canLaunchGravship`, `canBeCleaned`.
- The transfer itself is nine lines in `JobDriver_EnterPortal`'s last toil (`DeSpawnOrDeselect`,
  `GenSpawn.Spawn` on the other map at a `StandableCellNear` the destination, `UnloadEverything =
  !otherMap.IsPocketMap`, clear queued work, `Lord.Notify_PawnLost`) — the descent job copies that
  shape; the ascent IS that driver, via the surface line. `JobGiver_ExitMap` on a pocket map sends
  fleeing/leaving pawns to any reachable `MapPortal` instead of the map edge.
- Teardown: `PocketMapUtility.DestroyPocketMap(map)` directly (vanilla `CompSealable` casts its
  parent to the *entrance* portal's `PocketMap`, which we do not have). Floors persist by ruling;
  destruction happens only on the persist-off setting or map abandonment
  (`destroyOnParentMapAbandoned`).
- Temperature: `MapTemperature.OutdoorTemp`/`SeasonalTemp` return
  `generatorDef.pocketMapProperties.temperature` on a pocket map (before any world lookup) — so
  the per-sea clock temperature is one XML number and needs no world tile.
- Pocket-map exemptions the engine grants (MEASURED via `IsPocketMap` call sites): no exit grid
  (`ExitMapGrid.MapUsesExitGridNow`), threat points redirect to `sourceMap`, prisoner/slave escape
  suppressed by property, `disableCallAid` on the generator, growing zones/plans disallowed unless
  flagged, verbs/abilities with `useableInPocketMaps=false` refused.

### 2.2 Wild animals on a pocket map (MEASURED — this is the ruling's crux)

- `Map.MapPostTick` calls `wildAnimalSpawner.WildAnimalSpawnerTick()` on **every** map, pocket or
  not — there is no pocket-map gate in `WildAnimalSpawner`.
- `DesiredAnimalDensity` = `map.TileInfo.AnimalDensity` (`Tile.cs:159` — `biome.animalDensity ×
  each mutator's animalDensityFactor`) × commonality/season factors. **The four sea defs carry
  `animalDensity` 0.15 / 0.1 / 0.1 / 0.1** — at that value a 100×100 floor's whole ecosystem budget
  is ≈0.10–0.15 weight (`Area / (10000 / density)`), i.e. nothing spawns. ⇒ the generator's `tileMutators` list carries a new
  `TileMutatorDef RM_SeaFloorHabitat` with `animalDensityFactor` (≈30, tune) and a wide
  `animalDensityRange`. This keeps the surface defs untouched (their density is a GravTide/coastal
  number, not ours to change here).
- Ongoing spawns need an **edge entry cell**: `RCellFinder.TryFindRandomPawnEntryCell` requires
  `(map.TileInfo.AllowRoofedEdgeWalkIn || !roofed) && CanReachColony && district.TouchesMapEdge`.
  A fully roofed floor therefore needs `allowRoofedEdgeWalkIn=true` on the same
  `RM_SeaFloorHabitat` mutator (`Tile.AllowRoofedEdgeWalkIn` reads it from mutators, `Tile.cs:198`;
  Odyssey's own `TileMutators_Natural.xml:255` uses the flag) **and** open walkable floor at the
  map edge (no rock ring). `CanReachColony` (`CanReachFactionBase`) during play is satisfied by any
  reachable player pawn, then by `CanReachBiggestMapEdgeDistrict` — open edges satisfy it even
  with no colonist below.
- Initial population: vanilla pocket generators (Undercave, InsectLair) omit the `Animals`
  GenStep; ours **includes `GenStepDef Animals`** (`GenStep_Animals` loops
  `SpawnRandomWildAnimalAt` until the ecosystem is full, using
  `RCellFinder.RandomAnimalSpawnCell_MapGen`, which also wants an edge-touching district — open
  edges satisfy it).
- `SeasonAcceptableFor` gates each kind on `ComfyTemperatureMin/Max` against the pocket
  temperature → each sea's residents must have comfy ranges spanning that sea's clock
  temperature (Propane's −79 °C especially) — an XML check on the 14 race defs, §6 step 3.
- Flyers: `SpawnRandomWildAnimalAt` fly-in needs an unroofed cell; on a roofed floor a
  `canFlyIntoMap` kind simply walks in. Hoolen/`AA_` flyers are removed from the floor list by
  `RM_DiveMapExtension.excludeFromFloor` (§3.3) — no engine work.

### 2.3 What is reused vs new (C#)

| piece | status |
|---|---|
| `MapPortal` (as the exit's base), `PocketMapUtility`, `Dialog_EnterPortal`, `JobDriver_EnterPortal`, `WorkGiver_HaulToPortal`, `JobGiver_ExitMap` pocket branch, `Animals`, `Fog` GenSteps, `HediffGiver_Terrain` burn | vanilla, reused as-is |
| `RM_GenStep_TerrainChannels`, `RM_GenStep_ScatterPools`, `RM_GenStep_PlacedSetPieces`, `RM_ScattererValidator_NearThingDef`, `GameCondition_EnvironmentalWeather` (held weather), `HediffCompProperties_EnvironmentalExposure`, `RM_MechanicGates` | ours, reused as-is (EnvironmentalHazards) |
| `Patch_PocketMapGrowthRate` (Harmony prefix on `MapPlantGrowthRateCalculator.BuildFor`) and `DeepFloraPlanter`/`MapComponent_DeepFloraRegrowth` | ours but `RUT_`-tier in LanternDeeps; **lift to `RM_` in the new mod** (§2.4) — the LanternDeeps copies then delete in favour of the shared one, or stay until its own sitting |
| **NEW** `RM_JobDriver_DiveDown : RM_JobDriver_DiveBase` — `ResolveOutcome` = get-or-generate the sea's floor from `RM_MapComponent_DiveSites`, record this cell as the return cell, transfer the pawn (the `JobDriver_EnterPortal` shape) | new, small |
| **EXTEND** `RM_MapComponent_DiveSites` — adds `Dictionary<BiomeDef, Map> floorMaps` + `Dictionary<BiomeDef, IntVec3> returnCells` (`Scribe_References` / `Scribe_Values`); `GetOrGenerateFloor(sea)` calls `PocketMapUtility.GeneratePocketMap` with a static `currentlyGeneratingDive` context (the `currentlyGeneratingPortal` pattern) so the exit GenStep can bind | small edit |
| **NEW** `RM_SurfaceLine : MapPortal` (the exit; `exitDef`-style ThingDef, Standable, glower, `CompProperties_Effecter` lightshafts as `CaveExit` has) — overrides `GetOtherMap` → surface map, `GetDestinationLocation` → the sea's return cell, `EnterString` "Surface"; ignores `def.portal.pocketMapGenerator` | new, small |
| **NEW** `RM_GenStep_PlaceSurfaceLine` — replaces `PlaceCaveExit`: centre-ish standable cell, clears radius 4.5, spawns `RM_SurfaceLine`, binds it from `currentlyGeneratingDive`, sets `MapGenerator.PlayerStartSpot` | new, tiny |
| **NEW** `RM_DiveMapExtension : DefModExtension` (on the sea BiomeDef): `generator`, `entryTerrains`, `floorTerrain`, `murkWeather`, `excludeFromFloor`, `exposureDays` | new, XML surface only |
| **NEW** `RM_GenStep_SeaFloorBase` — paints the whole map with the sea's `floorTerrain`, no rock ring, reading the extension | new, tiny (vanilla `Terrain` GenStep would lay the sea's `terrainsByFertility`, i.e. impassable deep water everywhere — skipped by omission) |
| **NEW** `RM_MapComponent_SeaFloor` — on `MapGenerated`: starts the held murk `GameCondition` and applies `RM_DeepExposure` bookkeeping; refuses map-wide fire if the sea is not flammable (Propane ignition, §4) | new, small |
| DivingInteraction float-menu third option "Dive down" (`RM_Job_DiveDown`), shown only when the cell's terrain is in some sea's `entryTerrains` | small edit to `RM_FloatMenuOptionProvider_Dive` |

### 2.4 Two MEASURED pocket-map crashes the Lantern Deeps already paid for

1. **Plant growth-rate calculator throws on a tile-less map** when the biome has pasture-edible
   wild plants (`Patch_PocketMapGrowthRate.cs` header, Player.log ref E6BB2EFD, 2026-09-18):
   `MapPlantGrowthRateCalculator.BuildFor` → `TileTemperaturesComp.OutdoorTemperatureAt(invalid)`.
   The Scald's Crowncarpet (`RM_DeepfireMat`, today still `RM_WelcomeBlanket` in TerminalBiomes)
   and any kelp make our floors liable. The prefix substitutes the
   source map's tile. **Required, day one.**
2. **Under natural roof `WildPlantSpawner` ignores the biome's `wildPlants`** and draws only from
   the planet-wide `cavePlant` set (`DeepFloraPlanter.cs` header). A roofed floor gets no mats/kelp
   without the planter GenStep + regrowth component. Reuse both with the biome name parameterised
   (they currently hard-code `RUT_LanternDeeps`).

### 2.5 UNMEASURED — test on the Desktop before building past step 2 of §6

- A `MapPortal` subclass used as an exit with **no entrance building**: the code paths it needs
  (`Dialog_EnterPortal` → `JobDriver_EnterPortal` → `GetOtherMap`/`GetDestinationLocation`;
  `JobGiver_ExitMap`; hauling) are read and go through virtuals/the request group, but no vanilla
  def does this — a live ascent with a hauled item is the proof. `MapPortal.GetGizmos` reads
  `def.portal.pocketMapGenerator.label` only when its own `pocketMap != null` (never, for the
  exit), so `portal` may be an empty block.
- `PocketMapParent.sourceMap` on a floor whose surface map is later abandoned:
  `destroyOnParentMapAbandoned` is the vanilla answer; whether our component's `Map` reference
  survives that cleanly (null on load) needs a save/abandon/load test.
- Whether `GameCondition.ForcedWeather()` holds against `WeatherDecider` on a pocket map exactly
  as on a surface map (`RUT_ScaldSteamLock` proves it on the surface only).
- Whether `GenStep_Fog` + `PlaceCaveExit` unfog a sensible radius on an all-open floor (vanilla
  cave maps are corridors).
- Live proof that animals arrive from a roofed edge — the whole reason the mutator exists. This
  is the falsification test of the ruling; it is a `rimworld-debug-testing` quicktest, not a cold
  load.

## 3. Map generation

### 3.1 One generator per sea, one floor per sea per surface map

Four `MapGeneratorDef`s (`RM_ScaldFloorGenerator`, `RM_GreySeaFloorGenerator`,
`RM_TwilightSeaFloorGenerator`, `RM_PropaneLakeFloorGenerator`), each: `isUnderground true`
(every cell roofed — the sea is the roof; `roofDef` a new unmineable `RM_RoofWaterColumn` so
nobody "mines" the ceiling), `pocketMapProperties { biome = that sea; temperature = its clock;
tileMutators = [RM_SeaFloorHabitat] }`, `disableCallAid true`, `ignoreAreaRevealedLetter true`,
`customMapComponents = [RM_MapComponent_SeaFloor, RM_MapComponent_DeepFloraRegrowth]`.

**Anchoring.** The dive job resolves its sea from the clicked cell's terrain: `RM_DiveMapExtension`
on each sea BiomeDef lists `entryTerrains` (that sea's `RM_DiveEligible` shallows); the one sea
claiming the terrain supplies the `generator`. The persistent floor is owned by the **surface
map's `RM_MapComponent_DiveSites`**, keyed by sea BiomeDef — so a shore with two hundred dive
cells still has exactly **one** floor per sea, and a surface map bordering two seas has two. The
floor's `PocketMapParent.sourceMap` is that surface map (vanilla abandonment cleanup applies).
The surface line's return cell is the cell of the **most recent** descent (updated per dive), so
a colony that dives from its own jetty comes up at its own jetty. Size: `100×100` (vanilla's
`pocketMapSize` default; 10,000 cells) — four persistent floors on one coastal map tick like four
extra small maps (each runs `WildAnimalSpawner`/plants/weather every tick); the persist-off
setting (§5) is the relief valve, and per-floor `animalDensity` stays bounded by the ecosystem
weight budget, which scales with area. Grey and Twilight today have
**no own shallow terrain** (they fall back to the vanilla ocean pair in SeaShores' resolution
order) — tagging vanilla `WaterOceanShallow` would open diving on every ocean, so step 1 authors
`RM_GreySeaShallow`/`RM_GreySeaDeep` and `RM_TwilightSeaShallow`/`RM_TwilightSeaDeep` (SeaShores
prefers a sea's own pair automatically) and tags the shallows. Propane's `RM_PropaneShallow`
already exists; the Scald's three tagged shallows already exist.

### 3.2 GenStep list (shared skeleton, per-sea additions in **bold**)

```
RM_SeaFloorBase          (order 100)  whole map = floorTerrain; edges stay open floor
RM_SeaFloorFeatures      (per sea, 200-300):
  Scald    chimney fields: RM_GenStep_ScatterPools with terrain swap (core RM_ScaldFloorScalding,
             ring RM_ScaldFloorHot, centre RM_ScaldChimney buildings) — §8.1
           + nodule/crystal scatter per zone, Scaldpearl on core cells, Seep Salt + Pyrinth
             (MayRequire) — §8.3
           + RUT_ScaldWreck* scatter on the plain (stock GenStep_ScatterThings, tag) — §8.4
           + Rakatan vessel set-piece + droids + debris fan IF sourceMap tile carries
             RUT_RakatanWreckBelow (Utinni mod, patch-added) — §8.4
  Grey     RM_GenStep_ScatterPools (brine: deep=RM_WastelandBrineDeep, shore=…BrineShallow)
           + pillar forest: GenStep_ScatterGroup of a mineable RM_PillarStone
           + statuary: RM_GenStep_PlacedSetPieces with a new RM_SetPieceElement_Building
  Twilight RM_GenStep_TerrainChannels (RM_SinkingWater, Impassable) for the mud rivers
           + bank terrain (RM_RiverBankMud, fertile) painted 1-2 cells either side
           + skylights: 3-5 unroofed discs (roof removed) with a glow-less "lightwell" effecter
           + Compact huts set-piece (buildings + lamps, no pawns)
  Propane  tholin dust filth band (RM_GenStep_EdgeBandFilth exists) + lab wall set-piece
RM_GenStep_PlaceSurfaceLine (ours; spawns RM_SurfaceLine — vanilla PlaceCaveExit is omitted, §2.1)
RM_DeepFloraGate         (lifted planter: plants from the sea's wildPlants under roof)
Animals                  (vanilla GenStep_Animals — the cast, from <wildAnimals>)
Fog                      (vanilla)
```

### 3.3 Where the cast and the catch come from

- **Floor residents** = the sea BiomeDef's `<wildAnimals>` (already wired: Scald noohm/shulla;
  Grey fessk/sorruth/essarn/otheska; Twilight noolim/loohn/weloon/lunoowa; Propane
  vaunoom/heemin/oovanam/hoolen + `AA_*`). `RM_DiveMapExtension.excludeFromFloor` names kinds that
  are surface-only (hoolen, `AA_AuroraSylph`, `AA_Skyeel`, `AA_Aerofleet`); `RM_MapComponent_
  SeaFloor` zeroes their commonality on that map by despawning any that arrive (cheapest; a
  Harmony postfix on `BiomeDef.CommonalityOfAnimal` keyed on `map.IsPocketMap` is the clean
  alternative if the despawn shows).
- **Catch** stays on `<fishTypes>` (Odyssey fishing from the shore, already live on all four).
  Nothing is fished *on* the floor: the sea-law's two defs per species are the floor pawn
  (`RM_Shulla`) and the catch item (`RM_ShullaCatch`), and both already exist. A diver may hunt
  the floor pawn — hunting the shoal fish is the "seen, not just caught" payoff.
- **Harvest** on the floor: Scald Crowncarpet (`RM_DeepfireMat` → `RM_DeepfireMatFresh`, the
  Deepfire spec's defs; laid by walkers, §8.2–8.3) plus the nodules of §8.3, Grey pool shores (a new `RM_BrineCrust` gatherable via the existing `RM_CompGatherableGas`/
  worked-lottery shapes), Twilight banks (new `RM_BankKelp` plant), Propane tholin (filth →
  `RM_TholinDust` item via a gather job). Each is one def + one existing comp; none is engine
  work.

## 4. Survival and cost

**No breath system exists to reuse (MEASURED):** searching the 1.6 source for drowning yields only
two flavour strings; Odyssey's swimming is a joy job (`JobDriver_GoSwimming`, `SwimPathFinder`)
and a render state (`job.swimming`, `swimmingGraphicData`) — there is no breath stat, no
underwater hediff, no pressure. So the clock is built from three existing mechanisms, no new
hediff comp:

1. **Deep exposure** — one new `HediffDef RM_DeepExposure` carrying
   `HediffCompProperties_EnvironmentalExposure` with `onlyDuringWeathers` = the four murk
   WeatherDefs (one per sea, new, held by the floor's `GameCondition_EnvironmentalWeather`).
   Accrues while unroofed-in-the-murk, heals on the surface or under an air-bell (any sub-roof
   cell). Stages: pressure headache → nausea/consciousness → collapse; severity per day from
   `RM_DiveMapExtension.exposureDays` so the Twilight is long and the Propane short. The comp's
   apparel-stat slowdown already exists: a **dive suit** apparel (one def, RM-tier, no franchise)
   carries it — the only gear item this spec adds. ⛔ No item ever zeroes it (Scald ban 3, Grey
   ban 1 spirit).
2. **Temperature** — the pocket map's own `temperature` (§2.1): Scald 55 °C, Grey 4 °C, Twilight
   14 °C, Propane −79 °C. Heatstroke/hypothermia are vanilla and already scale with apparel.
3. **Terrain** — Scald heat zones (`RM_ScaldFloorHot` 3 / `RM_ScaldFloorScalding` 8, §8.1) via
   vanilla `HediffGiver_Terrain` (the exact mechanism `SCALD_DIVING_MOD_1` live-verified
   2026-09-20; the engine floors any authored value at 3 — MEASURED); Grey pool shores `dangerous` brine
   shallows; Twilight channels and Grey deep brine `Impassable`, so the sheet's "no entry" bans
   are structural, not rules.

**Propane ignition (sheet ban 4, lake §3 "ignition has an engine").** `RM_MapComponent_SeaFloor`
listens for any `Fire` spawn or explosion on the Propane floor and, if the source is thermal or
electrical, transitions the map's held weather to `RM_PropaneBurn` (a reskinned firestorm-class
weather with `HediffCompProperties_EnvironmentalExposure` damage rate ×10) for a fixed span, then
back. No fiat ignition; a diver with a torch is the player's own fault. Whether this should also
touch the surface lake map is an owner question (§7 Q3).

**Leaving with things.** Vanilla portal load flow on the surface line. A `ThingComp.CanEnterPortal`
on `RM_SurfaceLine` refuses a *tamed Propane native* going up (sheet ban 6, R-H10) — the one
custom acceptance rule; everything else may come up. Going down carries only what is on the pawn.

**Death down there.** A downed diver is carried to the surface line by a colonist (vanilla
`FloatMenuOptionProvider_CarryPawnToExit` is pocket-map aware — MEASURED). A corpse left on the
Grey floor is the statuary's next member: `RM_MapComponent_SeaFloor` jackets any corpse older
than N days into an `RM_Statuary` building (Grey only; sheet §5 "the statuary only grows").

## 5. Mod Settings

All gates go through `RM_MechanicGates` (unregistered = enabled; a `RM_MechanicGateExtension` on
each gated def). Registered by the **DivingInteraction** mod constructor next to its existing
settings (`RM_DivingSettings`), because the descent is its job; TerminalBiomes' existing
per-sea toggles (`scaldEnabled` … `greySeaEnabled`) are honoured by ANDing, same as `Scald.S*`.

| setting | default | gate key / effect |
|---|---|---|
| Dive maps enabled (master) | on | `Dive.Maps` — off: "Dive down" absent from the float menu; existing floors persist and can still be surfaced from |
| Per sea: Scald / Grey / Twilight / Propane floor | on | `Dive.Floor.<Sea>` — off hides that sea's "Dive down" |
| Floor map size | 100 | side length passed to `GeneratePocketMap` for floors generated after the change (60–150) |
| Deep exposure rate | 1.0× | multiplies `exposureDays` (0 = clock off — labelled "makes diving free; not the shipped game") |
| Floor animal density | 1.0× | multiplies `RM_SeaFloorHabitat.animalDensityFactor` (0 = empty floors) |
| Propane ignition | on | `Dive.PropaneIgnite` on the burn transition |
| Statuary from corpses (Grey) | on | `Dive.GreyStatuary` |
| Floors persist between dives | on | off = `DestroyPocketMap` when the last colonist surfaces (cheap saves; loses harvest state) — labelled |

All-off degrades to today's shore-job-only diving. No worldgen-affecting toggle exists here
(nothing touches the planet).

## 6. Build order — small, each step shippable

1. **Terrain + tags (XML only, TerminalBiomes + DivingInteraction).** `RM_GreySeaShallow/Deep`,
   `RM_TwilightSeaShallow/Deep`; tag all four seas' shallows `RM_DiveEligible` (one patch file
   per sea, `MayRequire="mandrake.rm.terminalbiomes"`, the existing Scald patch is the shape).
   Ships: the shore hunt/commune jobs now work on all four seas. Verify with `validate_patch.py
   --live --defs`.
2. **The Scald floor, bare (falsification test).** `RM_DiveMapExtension`, `RM_JobDriver_DiveDown`
   + float-menu option, the `RM_MapComponent_DiveSites` extension, `RM_SurfaceLine`,
   `RM_GenStep_PlaceSurfaceLine`, `RM_ScaldFloorGenerator` with only
   `RM_SeaFloorBase → RM_GenStep_PlaceSurfaceLine → Animals → Fog`, `RM_SeaFloorHabitat` mutator, the lifted
   growth-rate patch, the comfy-temperature pass on the 14 race defs. **Quicktest on the minimal
   list + TerminalBiomes + DivingInteraction: do noohm and shulla spawn at gen and walk in from
   the roofed edge?** If no, §2.5 is wrong and the mutator flag is the first suspect. Ships: a
   walkable, populated Scald floor. Same test proves the ascent: surface with a hauled item.
3. **The clock.** `RM_DeepExposure`, four murk weathers + held condition (the Scald's carries
   no visibility fields — §8.5), the dive suit (on the Scald the steam ladder's
   `RM_ScaldProtection` is the suit stat — §8.6), per-sea temperatures. Ships: diving costs
   something.
4. **Scald dressing** — expanded into **§8.7 S1–S9** (zones + chimneys, walkers + Crowncarpet
   trail, nodules, guardians + swarms, sando passage, wreckage, the Rakatan vessel, settings,
   art), plus the lifted flora planter for the mats. Ships: the Scald as §7a rules it.
5. **Grey.** Own generator: pools, pillars, statuary set-piece, corpse jacketing, brine shore
   harvest.
6. **Twilight.** Channels + banks, skylights, kelp, Compact huts set-piece.
7. **Propane.** Solid-propane floor, tholin band, lab wall, ignition transition, native-export
   refusal.
8. **Mod Settings pass** (can ride with 2 for the master gate; the rest land with their step).

Steps 5–7 are independent of each other; each is one `rimworld-live-review` sitting with the owner
looking at the floor before the next. Art owed per step is filed as it appears — check
`infrastructure/artpipe/done/` first (CLAUDE.md rule).

## 7. Rulings — owner, 2026-09-25 (decisions taken by question card)

1. **Persistence:** a sea floor stays generated between dives.
2. **Entry:** right-click "Dive down" on shallow water only — no player-built building
   (§2.1/§2.3).
3. **Propane ignition:** contained to the dive map; the surface lake never burns from a dive.
4. **Floor size:** 100×100.
5. **Twilight Compact huts in v1** — not asked; the spec **assumes** empty lit dwellings as
   scenery (the inhabited town stays the sheet's v2). Raise at the Twilight sitting (§6 step 6).

### 7a. The Scald floor — owner, 2026-09-25 (typed notes + card decisions, `SEA_DIVE_MAPS_BUILD_1`)

6. **Brine pools are the Grey Sea's**, not the Scald's (typed).
7. **Centrepiece = the bottom-walkers** as real floor pawns (typed): huge, sea-urchin-like, very
   alien, living off extreme temperature gradients; swirls of smaller life feed on what they
   excrete; **as they pass slowly over the floor they PRODUCE the bacterial mats that make
   Deepfire**. They **never attack** (typed). This supersedes `scald_kit_spec.md` S5's
   Message-only surfacing incident as the walkers' only presence — the incident may stay as the
   surface-side tell, but the walker is now a pawn.
8. **Threats** (typed): *scalding swarms* and *walker guardians* — *"big leggy things like
   brittlestars gone wild. They think they're defending the Walker."*
9. **Sando giants** (`RSW_SandoAquaMonster`/`RSW_ElderSando`, already on the Scald via the Utinni
   patch) are a **passing wonder** (card): they pass overhead, their shadow dims the floor, they are
   never hostile unless attacked.
10. **Chimney fields** (typed): large fields of boiling cloudy water, rich in life and ore, at
    temperatures that threaten even protected divers.
11. **Ore is NODULES you simply gather** (typed) — not rock walls to mine.
12. **Minerals** (typed + cards): gold, silver, uranium; **Mother-of-Scaldpearl** (grows along the
    chimneys, very valuable) and **Chimney Iron** nodules — both IN; magnetite + uraninite crystals;
    our own **Seep Salt** (`RM_SeepSalt`, exists) and **Pyrinth** (`DV_Pyrinth`, exists) — chosen
    over gem clusters and Star Wars gas seeps (card 16:01).
13. **Heat = zones gated by suit rating** (card). **Visibility = light-based only** (card).
14. **The Scald Wrecked Rakatan Vessel** (typed: *"I love the idea of a crashed ancient Rakatan
    vessel, encrusted in minerals, with a few goodies still left."*): an official location in
    **ONE Scald hex only**; goodies = a powerful turret salvageable and fittable onto the gravship,
    batteries, more TBD; none of the offered extras were picked (card 15:36). **Dormant ancient
    droids ARE in — lying on the sea floor, NOT inside the ship** (typed: *"The dormant droids are a
    great idea, but it's just on the sea floor, NOT in the ship."*). **Other wreckage scattered
    around is a must** (typed).
15. **Plasteel is renamed Durasteel** in the Star Wars/Utinni layer (card; free `RM_` mods keep
    plasteel). `KOTOR_AlloyDurasteel` already exists, so the owner asked which canon metals
    (Beskar, Doonium, Duranium) exist before choosing — **open**, and it belongs to
    `MINERALS_WHERE_THEY_BELONG_1`, not this spec.

Open questions for the owner are in §8.8; everything else in this spec is ruled.

## 8. The Scald floor — the worked design

Everything below is Scald-only. Rulings are §7a; engine claims carry the §2 MEASURED/UNMEASURED
labels; names of new defs are **proposed** (invented words in the noohm/shulla register — free to
live in the `RM_` tier by Q11a) and numbers are INVENTED until a live sitting tunes them. Tier
line: the walker, its swirl, the guardians, the swarms, the chimneys, the nodules and every
mineral name here are **invented → `RM_` (TerminalBiomes / the Scald's own mod)**. The Rakatan
vessel, its turret and batteries, and the dormant droids are **canon IP → `RUT_` in a Utinni
mod**, added to the floor by patch exactly as `WildAnimals_TheScald.xml` adds the sando today.
The free Scald floor must read as complete without them (Q11a: *"rich enough to stand alone"*).

### 8.1 Floor layout and heat zones

The 100×100 floor is **three heat zones**, painted as terrain so every gate is structural (no
rules code decides who may enter). The pocket map's single `temperature` (§2.1) stays **55 °C**
for the whole floor — heatstroke is the ambient cost everywhere — and the zones add burn on top.

| zone | terrain (new, `RM_`) | where | what is there | the cost |
|---|---|---|---|---|
| **1 — the plain** | `RM_ScaldFloorPlain` (dark mat-floored basalt; `burnDamage` 0; tag `RUT_ScaldMarginMat` so Crowncarpet can grow on it) | the outer ~55% of the floor, every map edge, the surface line | walker herds and their swirl, Crowncarpet trails, shulla shoals, noohm drifting between, scattered wreckage (§8.4), loose Seep Salt and gold/silver nodules | ambient 55 °C only; nothing burns |
| **2 — the chimney fields** | `RM_ScaldFloorHot` (`burnDamage` **3** — the engine floor, MEASURED `Mathf.Max(burnDamage,3)`; cloudy overlay) | 3–5 discs, radius 9–14, each around a chimney cluster; never touching a map edge | the chimneys, Chimney Iron and uranium nodules, magnetite/uraninite crystals, Pyrinth, guardians on patrol, swarm nests | burn every tick standing; `ArmorRating_Heat` (the ladder's, §8.6) is what makes a crossing survivable |
| **3 — the chimney cores** | `RM_ScaldFloorScalding` (`burnDamage` **8**, INVENTED; brighter cloud) | the inner radius 3–4 of each disc, hugging the chimneys | **Mother-of-Scaldpearl** growing on the chimney flanks, the richest crystals, the wreck's stern (wreck hex only) | *"threatens even protected divers"*: at the boil-suit's 0.55 heat armour a diver still takes ~half of 8 per tick-burst — a raid on the core is seconds, not a stroll |

**Chimneys.** `RM_ScaldChimney` — a 1×1 impassable `Building` (new def, `RM_` tier), a tall dark
smoker column, `CompGlower` orange (r 6, the zone's light, §8.5), `CompProperties_Effecter`
steady white plume, `fillPercent 1`. Placed by the existing `RM_GenStep_ScatterPools` shape with
the disc centre painted `RM_ScaldFloorScalding` and the ring `RM_ScaldFloorHot` — the same
generator the Grey uses for brine, with terrains swapped, so the "pool" is a heat disc. 4–9
chimneys per field, spaced ≥2. `RUT_ScaldVent` (the shore vent, `Building_SteamGeyser`) is
**not** reused down here: its point is the condenser hook-up, which no diver builds on the floor.

**Gradients are the walker's food (§7a-7).** A walker's grazing target is the **boundary** of a
heat disc: `RM_ThinkNode_SeekHeatEdge` (new, small) picks a random `RM_ScaldFloorHot` cell
adjacent to a Plain cell and wanders there; the herds therefore ring the fields, which is where
the mats appear and where the guardians are. Nothing walks the cores but swarms.

**How the zones gate on the suit (§7a-13, the card).** The gate is the numbers already ruled in
`scald_steam_and_hazards_spec.md` §5: burn is vanilla `Burn` damage, `Burn` has `armorCategory
Heat`, so **`ArmorRating_Heat` on worn apparel is the suit rating** — wrap 0.30 opens zone 2 as
a dash, boil-suit 0.55 / vacsuit makes zone 2 workable and zone 3 a dash, Royal Rind sits between.
No item zeroes it (Ban 3: the 8-damage core burns through everything). A hard wall ("cannot
enter without rating ≥ X") is **not** built — it would be a rule where the terrain already is
one — but see §8.8 Q2 if the owner meant a hard gate.

**Layout rule of thumb** (SOMA/"quiet dark seabed", `references.md` #25): the plain is mostly
empty and dark; fields are rare, bright and loud. The surface line always lands on the plain,
never inside a field (`RM_GenStep_PlaceSurfaceLine` already picks a centre-ish standable cell —
add "terrain is Plain" to its validator).

### 8.2 Cast

Existing residents stay as §1/§3.3 lists them (noohm, shulla, plus the Utinni-patched sando, faa,
mee). New, all proposed names, all `RM_` unless marked:

| creature | proposed def | role | behaviour (mechanism) | tier | art |
|---|---|---|---|---|---|
| **Bottom-walker** — the centrepiece | `RM_Ullum` (*ullum*), `bodySize` 6+, `wildGroupSize` 2–4, herd, `MoveSpeed` ~0.9 (slow by ruling) | grazes the heat gradient; never attacks; **produces Crowncarpet** as it passes; the hunt drop is the already-shipped `RM_ScaldWalkerChitin` (DivingInteraction) | `RM_ThinkNode_SeekHeatEdge` (§8.1) for wandering; **`RM_CompMatLayer`** (new comp): every N ticks while moving, if the cell it just left is Plain and mat-free, spawn `RM_DeepfireMat` (Deepfire's Crowncarpet plant, §8.3) at low growth — the trail IS the mat source, so mats are found *behind herds*, not carpeting the floor. `manhunterOnDamageChance 0` and no attack verbs: a wounded walker walks away (ruling: never attacks; its guardians answer). `RM_OrganicScaldNative` hediffGiverSet so zone 2 does not burn it. Comfy range spans 55 °C (§2.2) | `RM_` | **owed** — nothing in `infrastructure/artpipe/done/` or `_artsrc/` (MEASURED 2026-09-25: only `gorewalker_*`, a different creature). Brief: a house-sized, spined, urchin-domed bottom-walker on many thick tube-legs, mat-fuzz on the spines, bands of temperature colour; 3 facings, `drawSize` ~5 |
| **The swirl** | `RM_Tillik` (*tillik*), tiny, `wildGroupSize` 6–12, not huntable-worth (meat 1) | the "swirls of smaller life" feeding on walker excretion; pure spectacle, harmless | spawn only as **followers**: `RM_CompMatLayer` also spawns 1–3 tillik per herd at gen (`RM_SetPieceElement_AnchoredPawn` exists for anchoring); `ThinkNode` follow-nearest-walker within 4 cells; `CompGlower` faint cyan r 2 — the herd is lit by its own swirl | `RM_` | owed; brief: a fleck-cloud creature drawn as 5–7 glowing motes, 1 facing reused, `drawSize` 1.2 |
| **Walker guardian** | `RM_Skerrak` (*skerrak*), `bodySize` 1.6, `wildGroupSize` 2–3 per herd, predator-class melee (serrated arm tips) | *"big leggy things like brittlestars gone wild. They think they're defending the Walker"* — hostile to any pawn within ~7 cells of a walker; otherwise ignore you | anchored to a herd at gen (`AnchoredPawn`); **`RM_ThinkNode_GuardAnchor`** (new): attack non-native pawns inside the guard radius of the nearest walker, break off when they leave it, return to the herd. Never hostile away from walkers (so the plain is safe if you keep your distance — the player learns the radius). Immune via `RM_OrganicScaldNative` | `RM_` | owed; brief: five to seven whip-thin armoured arms on a small central disc, arms as long as a man, pale and banded, one raised; 3 facings, `drawSize` 2.4 |
| **Scalding swarm** | `RM_Feen` (*feen*), `bodySize` 0.15, `wildGroupSize` 8–16, insectoid-class, `manhunterOnTameFailChance` n/a — **always hostile** as a swarm | the MORE THREATENING creature of the fields: a boiling cloud of tiny stinging things that lives *in* zones 2–3 and pours out at whatever crosses | vanilla predator herd is wrong (they would hunt shulla); use `RM_ThinkNode_GuardAnchor` anchored to a **chimney** instead of a walker — swarms defend their chimney the way skerrak defend a herd. Damage = `Burn`-type stings (`RM_ScaldSting`, small, `armorCategory Heat`), so **the same suit that beats the zone beats the swarm** — one ladder. Nest = `RM_FeenNest` (1×1 building on a Scalding cell, `CompSpawner`-like respawn every ~2 days, destroyable) so a field can be *cleared* for a while — the loop that makes nodule runs a plan rather than a coin flip | `RM_` | owed; brief: a dense cloud of glowing orange-white sparks with a few visible barbed bodies; 1 facing, `drawSize` 1.6 (the swarm is one pawn each, drawn as a puff) |
| **Sando passage** | reuse `RSW_SandoAquaMonster`/`RSW_ElderSando` **race**, new `PawnKindDef RSW_SandoAquaMonster_Passing` whose graphic is a **shadow silhouette** | the wonder (§8.5): a giant passes overhead, its shadow slides across the floor, it leaves | **`RUT_ScaldSandoPassage`** IncidentDef (Utinni mod, MayRequire swbestiary) on the floor map only, `IncidentWorker_HerdMigration` shape (MEASURED: it spawns a herd at one edge with a `LordJob` that crosses to the far edge and exits) with group size 1, rare (`baseChance` low). `drawSize` ~14, `AltitudeLayer` left at pawn (it draws over floor things — that is the dimming). Real pawn ⇒ attackable ⇒ vanilla animal retaliation (`manhunterOnDamageChance`) gives "never hostile unless attacked" for free. **Removed from floor `<wildAnimals>` spawn** by `excludeFromFloor` (§3.3) so it is only ever seen passing. Surface `wildAnimals` row untouched | `RSW_` race, `RUT_` incident | one shadow texture per race (2), top-down black silhouette with soft edge — check `SWBestiary` `_south.png` as the silhouette source before regenerating |

Comfy-temperature pass (§2.2) covers the four new races. Faa/mee (Utinni-patched) are unaffected.
`RUT_WalkerSurfacing` (the shore Message incident, built) stays as the surface tell and now has a
referent.

### 8.3 Minerals and nodules — the first worked example for `MINERALS_WHERE_THEY_BELONG_1`

This section allocates minerals to **one** biome. The planet-wide allocation (which biome gets
which ore, the plasteel→Durasteel rename, canon-metal collisions) belongs to
`MINERALS_WHERE_THEY_BELONG_1`; the Scald is its **first worked example** and that item should
copy this table's columns (mineral · form · where on the floor · tier · def status) for every
other biome rather than re-deriving them.

**Nodules are items, not rock (§7a-11).** A nodule is a haulable `ThingDef` stack lying on the
floor (`GenStep_ScatterThings` at gen, vanilla, `terrainValidationAllowed` per zone), brought up
via the surface line's load flow. No mining skill, no rock wall, no `Mineable` — you walk to it
and pick it up; the cost is the zone it lies in. Persistence + one-shot scatter means a floor
*empties*: `RM_MapComponent_SeaFloor` re-scatters a few nodules per in-game quadrum on cells no
colonist can currently see (setting `noduleRegrowth`, default on) so a return dive finds
something, never a full reset (Raft's drift, `references.md` #28).

| mineral | form on the floor | zone | def | tier |
|---|---|---|---|---|
| Gold | `RM_NoduleGold` — an item stack with a dark-lump `Graphic_Random`, `smeltProducts` → vanilla `Gold` at the smelter (nodules are crusted; cracking them is the smelter's job, same as Chimney Iron). Scattering raw `Gold` stacks is the fallback if the smelt step reads as friction in the sitting | 1 (rare), 2 | new `RM_NoduleGold` | `RM_` |
| Silver | as gold, more common | 1, 2 | `RM_NoduleSilver` | `RM_` |
| Uranium | as gold; only in the fields | 2 | `RM_NoduleUranium` | `RM_` |
| **Chimney Iron** | `RM_ChimneyIronNodule` — dark, rust-crusted lump; picked up whole, **smelts** at the smelter to `Steel` ×N (a real reason to carry a smelter); also usable directly as a Stony-category **stuff** for ugly, heat-proof floors (INVENTED — §8.8 Q4) | 2 | new item + smelt recipe | `RM_` |
| **Mother-of-Scaldpearl** | `RM_ScaldpearlGrowth` — a **`Plant`-class** def (grows, harvests, regrows) that spawns only on `RM_ScaldFloorScalding` cells adjacent to a chimney (`wildTerrainTags`), `harvestedThingDef RM_Scaldpearl`, `growDays` ~20, `harvestWork` high; `RM_Scaldpearl` MarketValue ~40 (INVENTED, "very valuable"), Beauty on display, a luxury stuff for jewellery if the jewellery mod is present (`MayRequire kikohi.jewelry`) | 3 only | new plant + item | `RM_` |
| Magnetite crystal | `RM_MagnetiteCrystal` item stack (nodule rule, not a formation): a black faceted crystal, `smeltProducts` → small `Steel`, MarketValue above the steel it holds so keeping it is a choice | 2 | new item | `RM_` |
| Uraninite crystal | `RM_UraniniteCrystal` item, yields `Uranium` + value; **glows faintly green** (`CompGlower` r 1.5 — the fields' second light) | 2–3 | new item | `RM_` |
| Seep Salt | **`RM_SeepSalt` exists** (WeepingStones, *"scraped from the rim of a steamfrond vent"*) — scatter its stacks on the plain near field edges. Cross-mod: TerminalBiomes does not depend on WeepingStones, so the scatter is a `PatchOperationAdd` **`MayRequire="mandrake.rm.weepingstones"`** (check the packageId in its `About.xml` before writing) into the Scald generator's GenStep list | 1 | exists | `RM_` |
| Pyrinth | **`DV_Pyrinth` exists** (Pyrinth mod, self-heating orange crystal) — as Seep Salt, `MayRequire` the Pyrinth mod's packageId; lies in the fields where its own glow is lost among the chimneys until you carry it out | 2 | exists | `RM_` |

**Not on the Scald floor (ruled or by tier):** gem clusters (mineralssparkle's `*Crystal`
formations — declined, card 16:01; our magnetite/uraninite are **our own items**, not the donor's
defs, so the free mod has no Workshop dependency), Star Wars gas seeps (declined), jade, plasteel
(the Durasteel question is the minerals item's), Beskar/Cortosis/Rhydonium/Kyber (IP and
off-theme). Brine crust is the Grey's.

**Deepfire's Crowncarpet.** The mat is `RM_DeepfireMat` (Deepfire spec §2.1 — the def moves out
of TerminalBiomes into LuminousPigment and the plant's common name is **Crowncarpet**, owner
card 16:16), harvesting `RM_DeepfireMatFresh` with its one-day clock. On the floor it grows
**only where walkers have passed** (§8.2 `RM_CompMatLayer`) plus the shore margins the Deepfire
spec already gives it; the Scald's `wildPlants` row for it is therefore **low** on the floor (the
trail is the density) — the biome-side wiring stays the Deepfire spec's. Fresh mat is heavier
than pigment and dies in a day, so a Crowncarpet dive is a *sprint*: walk the trail behind a
herd, harvest, surface, press — the dive map gives the Deepfire chain its intended pressure.

### 8.4 The Scald Wrecked Rakatan Vessel, the scattered wreckage, the dormant droids

**Tier and placement.** Rakatan is canon IP (Q11) → everything named here is `RUT_` in a Utinni
mod (proposed folder `src/RimUtinni/ScaldRakatanWreck/`, packageId `mandrake.rut.scaldrakatanwreck`,
`loadAfter` TerminalBiomes + WreckedMachines; or fold into `UtinniPatches` if it stays small).
**One Scald hex only (§7a-14):** the floor is generated per **surface** map (§3.1), so "the hex"
is a designated coastal tile whose Scald floor carries the wreck. Mechanism: a `TileMutatorDef
RUT_RakatanWreckBelow` (no gameplay effect of its own) placed on that one tile; `RM_GenStep_
SeaFloorFeatures` checks `sourceMap.Tile` mutators and, if present, runs the wreck set-piece.
**The tile is chosen at the final painting pass** (CLAUDE.md: the planet is painted once, at the
end) — so this spec's deliverable is a **paint-list entry** (`BIOME_PAINT_ONCE_AT_THE_END_1`):
*"`RUT_RakatanWreckBelow` on exactly one Scald-shore tile; prefer a tile the Ash'karr settlement
map already names as a pilgrim shore"* — never a worldgen step, never a seed sweep. Whether the
hex is marked on the world map before anyone dives is §8.8 Q6.

**The vessel.** A `RM_GenStep_PlacedSetPieces` layout (~18×30 footprint, straddling a field's
edge so the stern lies in zone 2–3 and the bow on the plain):
- **Encrusted hull** — `RUT_RakatanHullCrust`, a `RockBase`-class mineable blob (the
  `RUT_GreatboleHeartwood` shape) forming the ship's outline; `mineableThing` a 60/30/10 roll of
  `RM_ChimneyIronNodule` / `RM_Scaldpearl` / `RUT_RakatanHullShard` (a new high-value alien alloy
  fragment, MarketValue ~25). *Encrusted in minerals* is literal: you dig the crust to reach the
  hold, and the crust is the ore.
- **Inside:** `RUT_RakatanTurret` — a `Building_TurretGun`, minifiable, huge, slow, very long
  range, **installable on gravship substructure** like any minifiable building (Odyssey moves
  whatever sits on the substructure — no special flag; `MayRequire Ludeon.RimWorld.Odyssey` only
  for the description line). Ships **degraded** per `RAKATAN_ARCHOTECH_MACHINES_1` (*robust,
  survives, degrades gracefully*): starts at 30% HP with a `RUT_RakatanDecay` hediff-like
  `CompProperties` halving fire rate until refurbished through WreckedMachines' in-place repair
  — the refurbished turret **exceeds** a modern one (that item's stated trait). One per game.
- **Inside:** `RUT_RakatanBattery` ×3–5 — a `Building_Battery` with 2–3× vanilla capacity that
  has **lost most of it** (`storedEnergyMax` scaled by a `RUT_RakatanDecay` comp; refurbish
  restores and then exceeds). Minifiable; that is the "batteries".
- **More TBD:** none of the offered extras were picked (card 15:36). Nothing else is placed in
  v1; §8.8 Q7 asks what else.
- The hold interior is `RM_ScaldFloorPlain` under the ship's own roof (`RoofDef` thin metal —
  an **air-bell**: the one place on the floor where deep exposure heals, §4). That is a design
  gift, not an accident: reaching the hold is the reward.

**The dormant droids — on the floor, not in the ship (§7a-14).** `RUT_DormantRakatanDroid`, a
`Building` (not a pawn) lying on the plain and field edges of the **wreck hex's floor only**
(they fell with the ship — default; §8.8 Q5 asks whether the free tier should get an unbranded
"ancient machine" on every floor). 4–7 per floor, `GenStep_ScatterThings`, never inside the hull
footprint. Each is a WreckedMachines-style **study/refurbish** object (that mod's in-place repair
+ `RAKATAN_ARCHOTECH_MACHINES_1`'s *"study the MACHINE itself as part of the research"*):
studying one advances a `RUT_RakatanSalvage` research project that the turret and batteries'
refurbish bills require. They do **not** wake hostile — the floor's threats are the swarm and the
skerrak, and a droid ambush would be the vanilla dormant-mech cliché (§8.8 Q5 offers the
alternative if he wants it). Deconstructing one instead yields components + `RUT_RakatanHullShard`.

**Scattered wreckage — a must (§7a-14).** On **every** Scald floor, not only the wreck hex:
the three shipped `RUT_ScaldWreck{Hull,Tank,Frame}` (`ShipChunkBase` salvage buildings, real art
2026-09-25) scattered on the plain by stock `GenStep_ScatterThings` with the shared shallow tag
the inventory notes as owed — this spec adds `RM_ScaldFloorPlain` to that tag list. Note these
are `RUT_`-prefixed but franchise-free in content; they ship in TerminalBiomes today and are
legal on the free floor. On the wreck hex, the density triples within 25 cells of the vessel (a
debris fan), plus `RUT_RakatanHullShard` items among them.

### 8.5 Wonder moments

Each is one mechanism already named above; listed so FOUNDRY builds the *moment*, not just the def.

1. **The dark.** The floor is roofed and unlit (§7a-13: visibility is light-based only). The
   Scald's held weather (`RM_ScaldMurk`, §4) carries the exposure clock and **nothing else** — no
   `accuracyMultiplier`, no fog overlay; vanilla darkness (work speed, shooting, the "in darkness"
   mood for those who mind) is the whole visibility system. Light comes only from: **Deepfire-coated
   gear** (Deepfire spec §3.4 — a worn item is a moving light and a target), **Crowncarpet**
   (`CompGlower` on the plant; if the Deepfire spec gives the mat none, add it here for the floor
   variant only), **chimneys** (orange, r 6), **uraninite** (green, r 1.5), and **glowing creatures**
   (tillik cyan, feen orange-white, noohm's bubble line). A first dive with no Deepfire is a
   torch-lit stumble along a rope; a Deepfire-lit dive sees the herd before the herd's guardians
   see you. Visibility is the progression reward (`references.md` #24).
2. **The herd.** A walker herd is lit by its own swirl and trails a fresh rainbow behind it. Seen
   from the surface line as a slow constellation moving along a field's edge.
3. **The passage.** The sando shadow (§8.2): a letter *"Something vast passes overhead"*, a
   silhouette wider than the field sliding across, the floor darker under it for a minute, gone.
   Never fights unless you start it.
4. **The fields.** From the plain, an orange glow on the horizon and the swarm-sparks around it;
   inside, plumes, pearl on the flanks, and the clock. The one place that is bright.
5. **The vessel.** A mineral-crusted hull the size of a house, a bow on the plain and a stern in
   the boil, and the floor around it strewn with the fallen. Once per world.

Not built: brine pools (the Grey's), any pure-visual shimmer band or marine-snow particle layer
(desirable, `references.md` #7/#10, but a new weather-overlay class each — §8.8 Q8).

### 8.6 Gear dependencies

The Scald floor introduces **no new gear**. It depends on, and gives purpose to:

| gear | source | what it does on the floor |
|---|---|---|
| `RM_Apparel_ScaldWrap` (Neolithic, 12 `RM_ScaldWalkerChitin`) | `scald_steam_and_hazards_spec.md` §5, unbuilt | `ArmorRating_Heat 0.30`: opens zone 2 as a dash; its chitin cost is paid by hunting the walker — **the first walker hunt is the first suit** |
| Royal Rind gear (Neolithic) | same, §5a; waits on the Greentide fruit item | `ArmorRating_Heat 0.45` + extreme insulation: the mid rung, and the one that makes the 55 °C ambient comfortable |
| `RM_Apparel_BoilSuit` (Industrial, `RM_ScaldWorking`) | same, §5, unbuilt | `0.55`: zone 2 workable, zone 3 a dash, swarm stings blunted |
| Odyssey vacsuit + helmet | same, §5 patch | the Spacer rung, same numbers as ruled there |
| The dive suit (§4, `RM_DeepExposure` slowdown) | this spec | **collapse it into the ladder**: the deep-exposure comp's `protectionStat` is `RM_ScaldProtection` on the Scald floor, so the wrap/boil-suit/vacsuit slow the dive clock too and no separate "dive suit" def is needed for this sea (§8.8 Q3 for the other three seas) |
| Deepfire-coated apparel/weapon | Deepfire spec §3.4 | the light you bring; also a target for skerrak/feen at range |
| A smelter (or a colony with one) | vanilla | Chimney Iron → steel |

Nothing here reaches immunity; the 8-burn core and the 8% exposure floor hold Ban 3.

### 8.7 Build steps for FOUNDRY (Scald floor only — these replace §6 step 4), each with its proof

Prerequisite: §6 steps 1–3 (bare floor, surface line, clock) proven on the quicktest list.
Every step is XML-first and shippable alone; C# is named where it is unavoidable.

| # | step | new C# | proof |
|---|---|---|---|
| S1 | **Zones + chimneys.** `RM_ScaldFloorPlain/Hot/Scalding` terrains, `RM_ScaldChimney` building, Scald `RM_GenStep_SeaFloorFeatures` using `RM_GenStep_ScatterPools` with the terrain swap; surface-line validator "Plain only"; `RM_ScaldMurk` weather with **no** accuracy/fog fields | none | quicktest (minimal + TerminalBiomes + DivingInteraction): `jawa/list_things` counts 3–5 chimney clusters; `terrain_at` on a ring cell reads `RM_ScaldFloorHot`; a naked pawn placed on Hot takes `Burn` within 60 ticks (`HediffGiver_Terrain`), on Plain takes none; `GroundGlowAt` > 0 beside a chimney and 0 on the open plain |
| S2 | **Walker + swirl + mat trail.** `RM_Ullum`, `RM_Tillik` races/kinds, `RM_CompMatLayer`, `RM_ThinkNode_SeekHeatEdge`, `RM_OrganicScaldNative` on both; comfy ranges; `<wildAnimals>` rows (ullum 0.15, tillik 0 — followers only) | `RM_CompMatLayer`, `RM_ThinkNode_SeekHeatEdge` (both small) | quicktest: spawn 3 ullum on the plain, `step_game_ticks` 5000: ≥1 `RM_DeepfireMat` exists on a cell an ullum occupied (compare `list_things` before/after); ullum positions cluster within 3 cells of a Hot/Plain boundary; damage one — it moves away, no attack job |
| S3 | **Nodules.** `RM_NoduleGold/Silver/Uranium`, `RM_ChimneyIronNodule` + smelt recipe, `RM_MagnetiteCrystal`, `RM_UraniniteCrystal` (glower), `RM_ScaldpearlGrowth` + `RM_Scaldpearl`; scatter GenSteps per zone; Seep Salt + Pyrinth `MayRequire` patches; `noduleRegrowth` in `RM_MapComponent_SeaFloor` | none (regrowth is ~20 lines in an existing component) | `validate_patch.py --live --defs` clean; quicktest: `list_things` shows every nodule def present, none on the wrong zone (`terrain_at` sample of 20); haul one gold nodule to the surface line and load → it is on the surface map; `refresh.py` + `measure count ThingDef` shows the 9 new defs |
| S4 | **Guardians + swarms.** `RM_Skerrak`, `RM_Feen`, `RM_FeenNest`, `RM_ScaldSting` damage, `RM_ThinkNode_GuardAnchor`; anchored spawning of skerrak with herds and feen with chimneys | `RM_ThinkNode_GuardAnchor` (one class, two anchor kinds) | quicktest: a colonist 12 cells from a herd is ignored for 2000 ticks; at 5 cells a skerrak attacks within 300 ticks; step away to 12 — it disengages and returns; a colonist entering a field draws feen; destroy the nest — no feen respawn in 2 days; a boil-suited pawn takes measurably less sting damage than a naked one (same `hit` count) |
| S5 | **Sando passage.** `RSW_SandoAquaMonster_Passing` kind + shadow textures, `RUT_ScaldSandoPassage` incident (Utinni, `MayRequire` swbestiary), `excludeFromFloor` for the sando races | none (vanilla `IncidentWorker_HerdMigration`) | quicktest with SWBestiary loaded: fire the incident via `debug/incident`: one passing kind spawns at an edge, crosses, exits (`list_things` count 1 → 0); it is never in a floor `Animals` GenStep spawn over 5 regenerations; shoot it once — it turns hostile (manhunter) |
| S6 | **Wreckage everywhere.** Add `RM_ScaldFloorPlain` to the `RUT_ScaldWreck*` `terrainValidationAllowed` tag; scatter GenStep on the floor | none | quicktest: ≥6 wreck pieces on a fresh floor; deconstruct one — vanilla yield |
| S7 | **The Rakatan vessel (Utinni).** New mod folder, `RUT_RakatanWreckBelow` mutator, hull crust `RockBase` blob layout, `RUT_RakatanTurret`, `RUT_RakatanBattery`, `RUT_RakatanDecay` comp, `RUT_RakatanHullShard`, `RUT_DormantRakatanDroid` + `RUT_RakatanSalvage` research hooked to WreckedMachines' study/repair; debris fan; **paint-list entry** filed on `BIOME_PAINT_ONCE_AT_THE_END_1` | `RUT_RakatanDecay` (small), the mutator check in the feature GenStep (3 lines) | quicktest with the mutator forced on the source tile (`jawa/world_*` set mutator, then dive): the hull outline is there, mining a crust cell yields from the 60/30/10 table, the turret is minifiable and reinstalls on a gravship substructure cell and fires; battery `storedEnergyMax` reads degraded; a droid is studyable and advances `RUT_RakatanSalvage`; **without** the mutator, 5 regenerations show no Rakatan def at all (the free floor stands alone) |
| S8 | **Settings.** Add to §5's table: `Dive.Scald.Swarms`, `Dive.Scald.Guardians`, `Dive.Scald.SandoPassage`, `noduleRegrowth`, `Dive.Scald.Zone3Burn` (number) — all default shipped | none | toggle each off in a quicktest and confirm the absence (no feen spawn; no skerrak; incident refused; no regrowth after a quadrum) |
| S9 | **Art** (may run in parallel from S2 on): ullum ×3 facings, skerrak ×3, feen ×1, tillik ×1, sando shadow ×2, chimney, 6 nodule/crystal items, Scaldpearl plant + item, 3 zone terrains, Rakatan hull crust, turret, battery, droid, hull shard | — | `fill_queue.py` only after the `done/` + `_artsrc/` search in each brief; `generating-rimworld-sprites` validator passes; then the live **bedazzle sitting** with the owner (`SCALD_REVIEW.rws` is staged for exactly this) |

The bedazzle sitting is the acceptance test for S1–S6 together; S7 has its own sitting because it
is a Utinni mod with a research chain.

### 8.8 Open questions for the owner (choices, not rulings)

1. **Names.** Ullum (walker) · tillik (swirl) · skerrak (guardian) · feen (swarm) — keep, or
   rename in the same register? (Defs are cheap to rename before S2; expensive after art.)
2. **Heat gate shape.** (a) *Soft* — zones burn, the suit's heat armour decides how long you last
   (this spec's default; zero rules code, Ban 3 by construction). (b) *Hard* — a zone refuses
   entry below a rating, with a message. (c) Both: soft burn plus a hard wall on zone 3 only.
3. **The dive suit across seas.** (a) On the Scald, the ladder IS the dive suit (§8.6) and the
   generic dive suit def is not built until another sea needs it. (b) Build the generic suit now
   and let the Scald ladder stack on it.
4. **Chimney Iron.** (a) Smelts to steel only. (b) Also a stuff (heat-proof, ugly floors and
   walls, cheap). (c) Its own metal with its own stats (more work, more identity).
5. **Dormant droids.** (a) Wreck hex only, Rakatan, study/refurbish, never hostile (default).
   (b) Also an unbranded "ancient machine" on every free-tier floor. (c) Some wake hostile when
   disturbed (the vanilla dormant-mech shape) — more threat, less wonder.
6. **The wreck hex on the world map.** (a) Unmarked until first dive, then a named landmark.
   (b) Marked from the start as a rumour ("pilgrims say something lies under the shore here").
   (c) Never marked; the floor is the only tell.
7. **More Rakatan goodies.** Turret + batteries are in; nothing else was picked. Candidates if he
   wants a third: a degraded shield emitter for the gravship (`ShipShields` exists), a navigation
   core that reveals one world region, a sealed archive (Anomaly-free lore item). Or nothing.
8. **Pure-visual layers.** A thermocline shimmer band at each field's edge and a marine-snow
   drift over the plain — each is a new weather-overlay class and two textures. Worth it for v1,
   or later?
9. **Scaldpearl's use.** (a) Sell/beauty only. (b) Jewellery stuff via `kikohi.jewelry` when
   present. (c) A Deepfire press catalyst (ties the two Scald exports together). Nothing else is
   assumed.
