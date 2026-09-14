# FORGE_MECHANICS_1 — C# mechanics kit spec (engine mapping)

Drafted 2026-09-11 against the FROZEN lore sheet
`design/Jawa/worldbuilding/biomes/the_forge.md` (§0, §3, §4, §5, §6 hard bans,
§7, §8, Owed) and the RULED comp kit in
`design/Jawa/worldbuilding/alpha_family_source_review.md` §4 (owner, 2026-09-11:
all six RM_ comps IN; build item `ALPHA_MECHANICS_KIT_1`). This spec maps the
sheet's mechanics onto the engine — it invents no lore. Anything marked
**INVENTED** is a tuning parameter this spec had to pick a starting value for;
anything marked ❓ is an engine claim not verified against source and must be
checked before build.

**Source verification basis**: claims marked *(verified)* were read from the
RimSage source index this session (`mcp__rimsage__search_source` /
`read_csharp_symbol`). ⚠️ Unlike the greentide/miasma drafting sessions, this
session's index DOES show Odyssey-era symbols (`ModsConfig.OdysseyActive`,
`GrowthRateFactor_Drought` in `Source/RimWorld/Plant.cs`), so it is newer than
the "1.5-era" caveat those specs carry — but the standing discipline holds:
every "vanilla has no X" claim is "no X **in the indexed source**" with an
implicit ❓ against the live 1.6 assembly. Anchors marked *(verified,
greentide)* / *(verified, miasma)* were verified at those specs' drafting.
**RESOLVED — FORGE_MECHANICS_1 spike, 2026-09-13.** The sheet's own donor line
("vanilla Volcano/LavaField") is half wrong: `LavaField` is CONFIRMED vanilla
— Odyssey DLC content (`Defs/Odyssey/BiomeDefs/LavaField.xml`,
`Defs/Odyssey/FeatureDefs/Features.xml`'s `LavaField` FeatureDef, workerClass
`BiomeWorker_LavaField` in the core `RimWorld` namespace; the BiomeDef itself
carries no `MayRequire`, only a few sub-elements do). `Volcano` is NOT
vanilla — CONFIRMED absent from vanilla's own `LandmarkDefOf` roster (no
`Volcano` field; `LavaFlow` is the nearest vanilla landmark) and absent
everywhere in the 1.6/Odyssey decompile — it is **Advanced Biomes**
(`emipa606/AdvancedBiomes`, WS 3541022508; `biome_terrain_palette.md` §A3,
already correctly attributed there: "Advanced Biomes uses unprefixed
defNames... `Volcano`... lava + obsidian terrain, ActiveTerrain lava
dynamics"). `AB_PyroclasticConflagration` is CONFIRMED Alpha Biomes (the
`AB_` naming convention this repo uses consistently for that mod;
`rosters/the_forge.json` records "Alpha pyroclastic donor family" /
"Alpha Biomes' own pyroclastic-donor tree"). Note the naming collision this
surfaces: Advanced Biomes' own terrain (`AB_LiquidLava`/`AB_Obsidian`/
`AB_VolcanicGravel`, per `biome_terrain_palette.md` §3) ALSO carries an `AB_`
prefix — a different mod reusing the same two letters, already flagged as a
legibility hazard at §4 item 2 of that same doc, not new here.

Whether 1.6 lava terrain damages standing pawns natively — CONFIRMED yes, via
the same native mechanism the Scald spike found for boil terrain:
`TerrainDef.burnDamage`/`burnIntervalTicks` (`Verse/TerrainDef.cs:212`),
read every tick by `Verse/HediffGiver_Terrain.cs:17` (`if (terrain.burnDamage
> 0 && Rand.MTBEventOccurs(terrain.burnIntervalTicks, ...))`, dealing
`DamageDefOf.Burn`). The concrete vanilla terrain, though, tells against F4's
"open melt" framing: `LavaShallow` (merged def) carries `burnDamage=3`,
`burnIntervalTicks=120`, `dangerous=true`, `avoidWander=true`,
`ignitePawnsIntervalTicks=240` and IS walkable (`affordances: Walkable`) —
a real, native burn hazard a pawn can cross. `LavaDeep`, by contrast, is
`passability=Impassable` (`pathCost 300`) with no burn fields of its own on
the raw def — nothing can stand on it at all, native or otherwise, so
"open melt as the wall" (F4) reads correctly only for LavaDeep-as-obstacle;
any walkable melt/scald surface in the tower floors should crib
LavaShallow's own field values rather than inventing new ones. No C# needed
for either behaviour — it is stock TerrainDef data + the stock HediffGiver.

**Naming**: generic mechanisms are `RM_` (`RimMandrake.*` namespaces); Forge
content defs exposing them are `RUT_` (`RimMandrake.Utinni.*`). Per the ruled
§4 resolution, one C# implementation per mechanic, tuned per-biome by XML only.
RM_ classes live in the ruled kit's home (`src/RimMandrake/EnvironmentalHazards/`,
packageId `mandrake.rm.environmentalhazards`) or a sibling RM_ mod if FOUNDRY
splits by weight.

**Hard-ban compliance (sheet §6, linter-checkable)** — how each ban binds this kit:

| Ban | Where it binds |
|---|---|
| 1. Nothing lives in the lava | No kind this kit places is lava-native; the tower tenders (F4) are mechanoid-family machines. Linter: no PawnKindDef spawns on lava terrain. |
| 2. Lava-machines never revealed | F4 ships a dungeon SHELL only — no def, label, desc, letter or quest string in this kit says what the tenders run. String linter over the kit's defs. |
| 3. No furred/chilled/lush fauna | This kit ships mechanisms, not kinds; the roster pass owns admission. F3's drifter comp attaches only to sky kinds the roster names. |
| 4. No taking of Forge fire (Tribes canon) | No item def in this kit is "captured Forge fire"; F6's heat is used in place, never bottled. Lore text is the canon sitting's, not this kit's. |
| 5. No tibanna source but the beldons | `RUT_TibannaGas` is produced ONLY by F2's gatherer comp on beldon kinds. Linter: no RecipeDef products and no other def's butcher/kill yield contain it. |
| 6. No ordinary rain | F1 locks the weather rotation (ruled-comp shape); the only rain-rendering weather reachable is the scalding burst. Vanilla rain is structurally unreachable. |
| 7. No vanilla-Earth flora/fauna | Roster pass owns eviction; nothing here spawns Earth defs. |

Scoreboard: **6 mechanics** · **3 ruled/kit reuses** (EnvironmentalWeather
shape, ActiveGasEmitter, PlacedSetPieces + the greentide's `RUT_Scald`) ·
**6 new RM_ classes** (1 L, 3 M, 2 S) · F6 is XML-only.

---

## F1. The closed boiling rain — flash cycle + flash-interval growth (§3, §4, ban #6)

**Player experience.** The mountain rains on itself: no drizzle, ever — long
still heat, then a sudden violent burst of boiling rain that scalds anyone in
the open and flashes back to steam off the rock in seconds. In the burst
window and the minutes after, the flash-flora visibly surges — fireweed grows
almost while you watch, then stalls until the next fall. Farming here means
learning the mountain's breathing.

**Engine route.** Three pieces:

- **The lock + the pulse**: `RM_GameCondition_WeatherPulse : GameCondition`
  (generic — base weather, burst weather, burst MTB/duration, burst damage all
  props), attached via `BiomeDef.biomeMapConditions` *(verified, greentide,
  `Source/RimWorld/BiomeDef.cs:131`)*. Forces `RUT_ForgeStill` (hot haze,
  vent-steam ambient, zero rain) via `ForcedWeather()` *(verified, greentide,
  `Source/RimWorld/GameCondition.cs:345`)*; on MTB (**INVENTED**: mean 10
  in-game hours, never scheduled) switches its forced weather to
  `RUT_BoilingRain` for a short burst (**INVENTED**: 20–40 min in-game).
  `WeatherDef.rainRate` is a native field *(verified,
  `Source/Verse/WeatherDef.cs:37`)* — the burst renders as real driving rain;
  the "flash back to steam" is overlay art + a ground-steam fleck pass at
  burst end, not a water/wetness system.
- **The scald**: during bursts only, the condition damages unroofed pawns on
  interval — exactly the ruled `RM_GameCondition_EnvironmentalWeather` damage
  shape, reparameterized — using **`RUT_Scald`** (the greentide kit M3's
  DamageDef with its `RM_ScaldArmor` armor category; cross-kit reuse — if the
  greentide build slips, the def is XML and ships here first). Scald severity
  gated by the wet-kit armor stat, so fireweed-fiber gear (§7) is literally
  the admission ticket. **INVENTED**: burst damage ~4 scald per 60-tick
  interval unroofed, unarmored — brutal to stand in, survivable to sprint
  through (card 2 rules the ceiling).
- **Flash-interval growth**: `RUT_Plant_FlashFlora : Plant` overriding
  `Plant.GrowthRate` — `public virtual` *(verified,
  `Source/RimWorld/Plant.cs:289`)* — multiplying the vanilla factors by the
  flash window: ×**INVENTED** 8.0 from burst start until 2 in-game hours
  after, ×0.05 outside it. Window state lives in
  `RM_MapComponent_FlashCycle` (records burst start/end ticks; Scribe-saved;
  also the public API `InFlashWindow()` any future consumer reads). Net
  growth over a mean day roughly matches a normal crop — the RHYTHM is the
  mechanic. Native flash-flora and fireweed use the subclass; pawns/animals
  ignore the window.

*Why not a ruled comp unmodified*: `RM_GameCondition_EnvironmentalWeather`
forces ONE weather and damages continuously; the Forge's identity is the
pulse. One new condition class, honest; the damage half is the ruled shape
verbatim.

**Effort**: **M** (condition + map component; plant subclass S). **v1: ships**
— §5 "the rain boils, falls, and flashes; the flora lives between" is the
biome's thesis.

## F2. Beldon herds + the tibanna harvest (§4, §7, ban #5)

**Player experience.** Vast placid gas-grazers drift the vapor columns. A
beldon in reach can be harvested — tibanna gas taps out of the living animal
on a cycle, like shearing — and there is no other tibanna on the planet. Which
is why the Empire's station sits here metering it (§8; the clock itself is
`TIBANNA_EMBARGO_PLOT_1`, not this kit).

**Engine route.** Vanilla gathering machinery, one honest subclass:

- **The tap**: `RM_CompGatherableGas : CompHasGatherableBodyResource`
  *(abstract base verified, `Source/RimWorld/CompHasGatherableBodyResource.cs:6`;
  `CompMilkable`/`CompShearable` are the stock concrete cribs — verified,
  props shape `CompProperties_Milkable { milkIntervalDays, milkAmount,
  milkDef, milkFemaleOnly }`)*. Subclassing rather than raw CompMilkable buys
  correct strings (inspect line "tibanna pressure", gather job label
  "tap tibanna") and a sex-independent gate. Attached by XML to the beldon
  kinds. **INVENTED**: interval 2 days, amount 12 `RUT_TibannaGas`.
- **The beldon**: a def named `Beldon` already ships in the mod set — the
  Forge roster JSON records it MEASURED with a predator flag the sheet
  contradicts (`rosters/the_forge.json`: "def as shipped hunts"); the roster
  pass owns stripping it to placid and any rename. This kit attaches the comp
  to whatever kind the roster lands; it ships no PawnKindDef.
- **The monopoly (ban #5)**: `RUT_TibannaGas` ThingDef ships here, produced by
  this comp alone — no recipe, no mineral, no butcher yield, no trader-stock
  tag outside Imperial hands (trade wiring rides `TIBANNA_EMBARGO_PLOT_1`).
  The linter check is a product scan over all RecipeDefs.

*Why not a ruled comp*: nothing ruled gathers body resources; vanilla already
owns the whole job/gizmo pipeline — smallest possible subclass.

**Effort**: **S**. **v1: ships** (the campaign clock stands on it).

## F3. The vapor-column flight layer (§3, §4)

**Player experience.** The sky fauna — beldons, fumeriders, fleet fliers —
drift above vents and melt where nothing else can go, visibly floating. They
never wander off across the ash like ground animals; the columns are their
pasture, and hunting them means going where the columns are.

**Engine route.** There is no z-axis; "flight" is the Aerofleet posture —
a ground pawn that floats visually and paths where others can't. The mod set
already proves it: `AA_Aerofleet` / `AA_ColossalAerofleet` (defNames verified
in `rosters/the_forge.json`, MEASURED "floats") — **RESOLVED — FORGE_MECHANICS_1
spike, 2026-09-13.** CONFIRMED the float is not Alpha Animals' own code at
all: `AA_Aerofleet`'s `<comps>` block
(`.../workshop/content/294100/1541721856/1.6/Defs/ThingDefs_Races/Races_Aerofleet.xml`)
carries `<li Class="VEF.AnimalBehaviours.CompProperties_Floating">` — a
**Vanilla Expanded Framework** comp (WS 2023507013, `VEF.dll`,
`1.6/Assemblies/`), not `AlphaBehavioursAndEvents.dll`. Binary-string read of
`VEF.dll` (`MEASURE_ALLOW_SCAN=1`, same technique the Scald spike used on
`BadHygiene.dll`) turns up the real seam: `CompFloating` maintains a shared
static roster (`floating_animals`, `AddFloatingAnimalToList`/
`RemoveFloatingAnimalFromList` — added/removed on spawn/despawn, not
per-tick lookup) consumed by exactly ONE Harmony postfix,
`VanillaExpandedFramework_Pawn_DrawTracker_DrawPos_Patch` — a patch on
`Verse.Pawn_DrawTracker.DrawPos`'s getter, applying a `FloatingOffset` to any
pawn currently in that list. A second string,
`DisablePathCostForFloatingCreatures`, confirms the "ignore terrain movement
costs" line in Aerofleet's own flavor text is the same comp's doing (a
pathing-cost patch, not a terrain-affordance trick). **Consequence for
`RM_CompVaporDrifter`**: crib the same seam — a `ThingComp` that registers
itself into a shared list on spawn/despawn, consumed by ONE Harmony postfix
on `Pawn_DrawTracker.DrawPos` — rather than a PawnRenderer draw node or a
def-side float property; this mod's `.csproj` already references
`0Harmony.dll` (for the biome-glow patch), so no new dependency is needed.
This kit adds the pasture-binding:

- `RM_MapComponent_VaporColumns` — builds a column field from emitter
  positions (steam geysers, vents, lava-adjacent cells) at map init +
  on-change; public `InColumn(IntVec3)`. The vent props themselves are the
  ruled **`RM_CompActiveGasEmitter`** reuse (miasma/greentide precedent —
  harmless white gas, pure atmosphere) — zero new emitter C#.
- `RM_CompVaporDrifter : ThingComp` on sky kinds: constrains wander/graze
  destinations to column cells — **RESOLVED — FORGE_MECHANICS_1 spike,
  2026-09-13, against the same source read MIASMA_MECHANICS_1's own spike
  already did for `RM_CompTerritorialAnchor`
  (`src/RimMandrake/EnvironmentalHazards/Source/RM_CompTerritorialAnchor.cs`).**
  That spike found the real seam is neither a raw wander-root override nor a
  bespoke ThinkTree subtree in isolation: vanilla's own hive defenders use
  `Verse.AI.PawnDuty` (focus + radius) read by two `protected virtual`
  JobGiver overrides — `RimWorld/JobGiver_HiveDefense.cs`'s
  `GetFlagPosition`/`GetFlagRadius` (on the abstract base
  `RimWorld/JobGiver_AIFightEnemy.cs:42,47`) and `RimWorld/
  JobGiver_WanderHive.cs`'s `GetWanderRoot` (on `JobGiver_Wander`, a real
  overridable method, not a Func field). `RM_CompTerritorialAnchor`
  reproduces this pattern generically via `RM_JobGiver_AnchorWander :
  JobGiver_Wander` overriding `GetWanderRoot(Pawn pawn)`. F3's
  pasture-binding is the SAME seam, already proven to compile in this
  assembly: a sibling `RM_JobGiver_ColumnWander : JobGiver_Wander`
  overriding `GetWanderRoot` to return the nearest cell
  `RM_MapComponent_VaporColumns.InColumn` accepts, wired into the sky
  kind's ThinkTreeDef the same way `RM_JobGiver_AnchorWander` is (a
  PawnKindDef/ThinkTreeDef content decision, XML, owed to the full build —
  not a further engine question). No new C# class is needed to prove this
  seam; it already compiles as `RM_CompTerritorialAnchor`'s own JobGivers.
  Grants the kit's ground-hazard immunities (scald bursts do
  not touch drifters — they live in the steam). No float-draw offset of its
  own is needed: the Aerofleet float route is CONFIRMED class-side (the VEF
  `CompFloating`/`Pawn_DrawTracker.DrawPos` Harmony postfix above), so any
  sky kind wearing VEF's own `CompProperties_Floating` already floats
  without this comp touching draw code at all.
- **Fleet fliers** ("race in, eat fireweed, retreat"): diet XML (fireweed in
  the food filter) + the drifter comp with a looser leash (**INVENTED**:
  forage radius 12 beyond columns) — no bespoke AI in v1; the darting read is
  speed stats, roster-owned.

**Effort**: **M** (component + comp; unknowns are seams, not systems).
**v1: ships** — §5 "the herds drift the columns" and F2's harvest both stand
on the kinds actually staying over the melt.

## F4. The foundry tower dungeon shell (§7, §8, bans #1–2)

**Player experience.** A dark tower's door at the base of a cone. Inside is
not a room on your map — it is floor after floor of forge-works over open
melt, heat as the wall, the glowing tenders as the garrison, forge-tech
salvage as the prize. You leave the way you came, richer or cooked.

**Engine route.** The engine's pocket-map machinery, stock since Anomaly and
richly present in the indexed source:

- **The door**: `RUT_FoundryTowerEntrance` ThingDef with a `MapPortal`-family
  building class — `MapPortal` holds the pocket map, generates it on first
  entry via `def.portal.pocketMapGenerator` / `pocketMapSize` *(verified,
  `Source/RimWorld/MapPortal.cs:324–333`,
  `Source/RimWorld/MapPortalProperties.cs`)*; `PocketMapExit` is the stock
  way back *(verified, `Source/RimWorld/PocketMapExit.cs:8`)*.
- **The floor**: `RUT_FoundryFloor` MapGeneratorDef with
  `pocketMapProperties` — per-generator ambient temperature is native
  *(verified, `Source/Verse/MapTemperature.cs:33–36` reads
  `pocketMapProperties.temperature`)*: **INVENTED** 70 °C — "heat as the
  wall" is a def field, no C#. GenSteps lay forge-works rooms, melt channels
  (impassable), salvage caches, tender spawns. Tender kinds are
  mechanoid-family, roster/faction pass; their strings reveal nothing
  (ban #2).
- **Floor after floor**: ❓ whether a pocket map can host a further
  `MapPortal` down (portal-in-pocket-map chaining) — **narrowed but NOT
  resolved, FORGE_MECHANICS_1 spike, 2026-09-13 (this needs a live
  quicktest, per the item's own instructions this pass did not attempt
  one).** Full-body reads of `RimWorld/MapPortal.cs` (`GeneratePocketMapInt`
  → `PocketMapUtility.GeneratePocketMap`), `Verse/PocketMapUtility.cs`,
  `Verse/MapGenerator.cs`'s `GenerateMap(..., isPocketMap: true)`, and
  `RimWorld/MapPortalProperties.cs` turn up **no guard anywhere** that
  checks whether `sourceMap` (the map a new pocket map is generated FROM) is
  itself already a pocket map — `PocketMapParent.sourceMap` is untyped as
  to "must be a real map," and `Find.World.pocketMaps` is a flat
  `List<PocketMapParent>` with no nesting/depth field. So the source
  code neither explicitly forbids chaining NOR explicitly handles it — it is
  genuinely untested engine territory, not "probably fine": nothing in
  `Verse/Map.cs`'s `IsPocketMap`/`PocketMapParent` properties, nor any of
  the ~30 call sites `search_source` found for `IsPocketMap` (world
  rendering, `CameraJumper`, caravan-exit, psychic rituals, prisoner escape,
  etc.), was written with "a pocket map whose OWN Parent is a
  PocketMapParent" in mind — several of those call sites walk exactly one
  level up (e.g. `RimWorld/GenStep_InsectLairCave.cs:130`'s
  `(map.Parent as PocketMapParent)?.sourceMap`) and would silently stop at
  the first level in a chain. This raises, not lowers, the risk that a
  second-level pocket map would generate without error but break something
  UI/traversal-side one level removed — PROVE in a quicktest before
  committing the multi-floor design; do not treat "no forbidding code" as
  "safe." Fallback that loses little: one deep floor per tower, tower count
  from the set-piece scatterer (card 1 rules which).
- **Placement**: towers on the map are set-pieces — reuse the miasma kit's
  **`RM_GenStep_PlacedSetPieces`** *(miasma M6; base
  `GenStep_Scatterer` verified there)* with a Forge def-list entry
  (**INVENTED**: 0–2 tower entrances per Volcano/LavaField-zone map, 0–1 on
  Pyroclastic skirts). The tower EXTERIOR (the vertical skyline) is art/def
  work on the entrance building, not this kit's C#.

*Why not a ruled comp*: nothing ruled owns maps; vanilla `MapPortal` does.
The kit's C# here is GenStep content for the floor generator, not new
machinery.

**Effort**: **L** (floor GenSteps + content wiring; the portal shell itself
is nearly free). **v1: ships one-floor towers**; multi-floor rides the ❓
chaining proof (flagged at build, never silent).

## F5. The Contagion die-off ring (§4, §5)

**Player experience.** At the ash skirts a ring of dead red creep, always
fresh: every so often the Contagion pushes a tongue of red up the slope, it
blackens and dies within hours, and the ring is renewed. The one ground the
weapon cannot take, marked by its own failed invasions. You can watch it
lose.

**Engine route.** Self-contained ambience, deliberately small:

- **Gen-time ring**: a scatter pass in the biome's terrain GenStep painting
  `RUT_DeadCreep` filth/ground-cover along the map-edge band on Pyroclastic
  maps (**INVENTED**: band 8–15 cells in from the edge, patchy).
- **The probe**: `RUT_ContagionProbe` IncidentDef (weighted only into Forge
  biomes, MTB-ish commonality — **INVENTED**: ~1 per 8 days) spawning a
  cluster of `RUT_DyingCreep` plant-things at a map edge carrying
  `RM_CompScriptedDieOff : ThingComp` (generic: spread N cells over M hours,
  then die, leaving `RUT_DeadCreep`; all props). **INVENTED**: spread 6–10
  cells over 4 hours, dead by hour 8. Letter on arrival, quiet death.
- **The ban edge**: `RUT_DyingCreep` carries no reproduction/harvest fields —
  it can never establish (the sheet's physics as def structure). **RESOLVED
  — FORGE_MECHANICS_1 spike, 2026-09-13.** `plant.reproduces` does not exist
  as a field on `RimWorld/PlantProperties.cs` at all — CONFIRMED by a full
  class read against the live 1.6/Odyssey decompile (every field of the
  class enumerated; no `reproduces`/`spreads`/`multiplies` boolean anywhere).
  RimWorld has no such per-plant flag. The REAL mechanism, also confirmed by
  source: `RimWorld/WildPlantSpawner.cs`'s `GetCommonalityOfPlant` returns
  `cachedPlantCommonalities.GetValueOrDefault(plant, 0f)`, and those cached
  commonalities come from `RimWorld/BiomeDef.cs:419`'s own
  `CommonalityOfPlant(ThingDef)`, which reads the BiomeDef's own `wildPlants`
  dict — a plant absent from every active BiomeDef's `wildPlants` entry gets
  commonality exactly 0 and `WildPlantSpawner` never spreads it on its own,
  full stop. So the linter check is not "no `plant.reproduces` field" (that
  field doesn't exist to check) — it is **"`RUT_DyingCreep` appears in no
  BiomeDef's `wildPlants` dict, anywhere"**; the only spread route left is
  this kit's own scripted `RM_CompScriptedDieOff`, exactly the "physics as
  def structure" the sheet already calls for. (`RM_CompScriptedDieOff` also
  ships this pass — see FORGE_MECHANICS_1's own spike-pass write-up.)
- Cross-flow: `the_contagion.md`'s own kit owns real creep mechanics; this
  kit's die-off pieces are standalone so the Forge never waits on it — if a
  shared creep system lands later, `RUT_DyingCreep` becomes its client
  (noted for that kit's drafting).

**Effort**: **S**. **v1: ships** (§5 "always fresh" is a standing-truth line).

## F6. Geothermal industry — XML only (§7)

**Player experience.** The one place fire costs nothing: smelters, kilns and
forges built directly over vents run with no fuel and no power line, and the
vanilla geothermal generator has the planet's densest geyser field to sit on.

**Engine route.** Zero C#:

- `RUT_VentSmelter` / `RUT_VentKiln` / `RUT_VentForge` — workbench ThingDefs
  with **no** fuel or power comp, gated onto geysers by
  **`PlaceWorker_OnSteamGeyser`** *(verified,
  `Source/RimWorld/PlaceWorker_OnSteamGeyser.cs`; `Building_SteamGeyser` and
  `CompPowerPlantSteam` show the whole stock pattern)*. Recipes mirror the
  fueled vanilla equivalents (**INVENTED**: +20% work speed — free heat is
  also good heat; card 3 can strike it).
- Power: vanilla `GeothermalGenerator` needs nothing from us; geyser density
  is `VAPOR_EMITTER_PLACEMENT_1`'s law (epicenter here).
- Obsidian/volcanic-glass materials (§7): the §B3 terrain family — items
  pass, not this kit.

**Effort**: **XML S**. **v1: ships.**

---

## XML-only ledger (no C#, listed so nothing gets re-invented)

- Biome figures (temps 42–56 °C, animalDensity low per heat-adapted-and-few,
  the three-zone BiomeDefs) — biome XML per sheet §0; donor merge rides the
  biome consolidation work, not this kit.
- Fireweed fiber, the heat-gear apparel tree, tibanna trade pricing — items
  pass + `TIBANNA_EMBARGO_PLOT_1`. Ban #4 patrols the fire side.
- All creature/flora kinds (beldon adjust, Aerofleet→Fumerider rename, fleet
  fliers, flash-flora) — roster pass (`rosters/the_forge.json`).
- Imperial gas station set-piece content — `TIBANNA_EMBARGO_PLOT_1` (placement
  capability = the same `RM_GenStep_PlacedSetPieces` reuse, listed there).

## New-C# roster (beyond the ruled/kit reuses)

| Class | For | Effort |
|---|---|---|
| `RM_GameCondition_WeatherPulse` + `RM_MapComponent_FlashCycle` | F1 | M |
| `RUT_Plant_FlashFlora` (Plant subclass) | F1 | S |
| `RM_CompGatherableGas` | F2 | S |
| `RM_MapComponent_VaporColumns` + `RM_CompVaporDrifter` | F3 | M |
| Foundry floor GenSteps + entrance/exit content (`MapPortal` family) | F4 | L |
| `RM_CompScriptedDieOff` (+ probe incident worker if needed) | F5 | S |

Total: 1 L, 2 M, 3 S; reuses: `RUT_Scald` + scald armor category (greentide
M3), `RM_CompActiveGasEmitter` (ruled kit), `RM_GenStep_PlacedSetPieces`
(miasma M6), the EnvironmentalWeather damage shape (ruled kit).

## Build order

1. **`ALPHA_MECHANICS_KIT_1` lands first** (external dependency): the
   EnvironmentalWeather condition shape F1 reparameterizes, ActiveGasEmitter
   for vents.
2. **F1 weather pulse + scald** — the biome instantly feels right; every
   later live test happens under the breathing sky. Take `RUT_Scald` from the
   greentide build if landed, else ship the XML here.
3. **F6 vent industry** — pure XML, any time after biome defs exist.
4. **F2 tibanna tap** — small, unblocks `TIBANNA_EMBARGO_PLOT_1` design.
5. **F5 die-off ring** — small, independent.
6. **F3 vapor columns + drifters** — after F1 (immunity reads the burst
   state); coordinate the wander-seam source read with the miasma kit's
   anchor comp.
7. **F4 foundry towers** — the L item, last; run the portal-chaining
   quicktest FIRST and let card 1's ruling pick the shape.

Cross-item dependencies restated: `ALPHA_MECHANICS_KIT_1` (F1, F3),
greentide kit M3 (`RUT_Scald`, F1), miasma kit M6 scatterer (F4), roster pass
(beldon/sky kinds for F2/F3, flash-flora defs for F1), items pass (§7
economy), `VAPOR_EMITTER_PLACEMENT_1` (geyser density law — consumer, no
blocker), `TIBANNA_EMBARGO_PLOT_1` (consumes F2; owns station, clock, trade).

## Owner cards — RULED, sitting 2026-09-12

1. **RULED 2026-09-12 — one large deep floor per tower in v1.** As
   drafted; portal-chained multi-floor lands later only if a quicktest
   proves the seam clean.
2. **RULED 2026-09-12 — boiling rain is survivable once.** Downed-and-
   scarred teaches the lesson; fireweed gear turns the biome on. Never
   instant death from one burst.
3. **RULED 2026-09-12 — beldon taming is brutal-but-possible.** As drafted:
   breaking the monopoly is a campaign act, not a pen. Ruled as one package
   with the tibanna embargo (T1 cut + T2 two-ended clock — see
   tibanna_embargo_plot_spec.md, same sitting).
