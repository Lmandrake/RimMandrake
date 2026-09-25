# Sea dive maps — design spec

Item: `SEA_DIVE_MAPS_BUILD_1`. Owner ruling (question card, 2026-09-25): **Build dive maps** —
diving opens a small underwater map where each sea's floor cast (the BiomeDef's `<wildAnimals>`)
actually spawns, one per sea, shared machinery across the four terminal seas (`RM_TheScald`,
`RM_GreySea`, `RM_TwilightSea`, `RM_PropaneLake`, all in `src/RimMandrake/TerminalBiomes`).

Status: RULED design, 2026-09-25 (§7). Nothing built. Engine claims are labelled **MEASURED**
(read in the 1.6 decompiled source via RimSage this sitting, symbol cited) or **UNMEASURED**.

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
| The cast, already on the defs | 14 `RM_` floor residents in `Defs/ThingDefs_Races/RM_*Fauna.xml`, wired in each sea's `<wildAnimals>`; `fishTypes` on all four defs | nothing in this spec authors a creature |

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
| **Scald** (`the_scald.md`) | dark mat-floored basin, rainbow **welcome blankets** on everything, **vents** (`RUT_ScaldVent`) with **bubble-sailors** (`RM_Noohm`) tethered to them, **shulla** shoals darting the dung-fall; the wrecks of §8 in the deep | rainbow pigment (mat harvest), walker chitin, vent-side salvage, the one place the shoal-fish are *seen* not just caught | **heat**: map temperature 55 °C (heatstroke, vanilla) + vent-adjacent floor cells carry `burnDamage 1` (`HediffGiver_Terrain`, the mechanism the shore jobs already pay with) | ban 3 (crossing scald water always costs — heat + burn, no immunity item); ban 4 (the floor is "merely hot", nothing swims the boil: the map IS the depth, the surface never becomes walkable); ban 1 (nothing potable — no water source down here); ban 5 (nothing cools or drains it) |
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
   The Scald's `RM_WelcomeBlanket` and any kelp make our floors liable. The prefix substitutes the
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
  Scald    RM_ScaldVentScatter (existing RUT_ScaldVent, reuse RUT_ScaldSailScatterer's validator)
           + burn ring (RM_ScaldFloorHot, burnDamage 1) painted around vents
           + RUT_ScaldWreckScatter (exists) for the deep wrecks
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
- **Harvest** on the floor: Scald mats (existing `RM_WelcomeBlanket` → `RM_RainbowPigment`),
  Grey pool shores (a new `RM_BrineCrust` gatherable via the existing `RM_CompGatherableGas`/
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
3. **Terrain** — Scald vent ring `burnDamage 1` via vanilla `HediffGiver_Terrain` (the exact
   mechanism `SCALD_DIVING_MOD_1` live-verified 2026-09-20); Grey pool shores `dangerous` brine
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
3. **The clock.** `RM_DeepExposure`, four murk weathers + held condition, the dive suit, per-sea
   temperatures. Ships: diving costs something.
4. **Scald dressing.** Vents + sails (existing scatterer), burn ring, wrecks, lifted flora planter
   for the mats. Ships: the Scald as the sheet describes it.
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

No open questions remain.
