# SCALD_MECHANICS_1 — C# mechanics kit spec (engine mapping)

Drafted 2026-09-11 against the FROZEN lore sheet
`design/Jawa/worldbuilding/biomes/the_scald.md` (§0, §4, §5, §6 hard bans, §7,
§8, Owed). This spec maps the sheet's mechanics onto the engine — it invents
no lore. Anything marked **INVENTED** is a tuning parameter this spec had to
pick a starting value for; anything marked ❓ is an engine claim not verified
against source and must be checked before build.

**Source verification basis**: claims marked *(verified)* were read from the
RimSage source index this session (`mcp__rimsage__search_source` /
`read_csharp_symbol`). ⚠️ The index is nominally 1.5-era, so every "vanilla
has no X" claim carries an implicit ❓ against the live 1.6 assembly — though
note this session found the full Odyssey fishing/water-body machinery IN the
index (`WaterBody`, `FishingUtility`, `Zone_Fishing`, `JoyGiver_GoSwimming`
Odyssey-gated), so the fishing anchors below are stronger than the caveat
suggests. Anchors marked *(verified, greentide)* were verified at that spec's
drafting: `BiomeDef.biomeMapConditions`, `GameCondition.ForcedWeather()`,
WeatherDef `accuracyMultiplier`/`moveSpeedMultiplier`,
`WeatherOverlay_Fog : WeatherOverlayDualPanner`.

**Already built and RULED — this kit consumes, never re-authors:**

- Six `RUT_ScaldWater*` TerrainDefs
  (`src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_ScaldWater.xml`, shipped
  2026-09-06): burn 1/300 shallow · 2/240 deep, `traversedThought HotSpring`,
  `avoidWander true`, cyan glow (2,154,229), `dbh_water` thirst tag — the
  boiling-lift spec's ruled values (`design/Jawa/mods/REGROWTH_BOILING_LIFT_SPEC.md`
  R-B4a). The R-B weather set (boiling rain family) is ruled to the rain-canon
  biomes and rides **`FORGE_MECHANICS_1`**, not this kit.
- `RUT_TheScald` BiomeDef (`…/Defs/BiomeDefs/RUT_TheScald.xml`) with
  `wildAnimals` deliberately empty — the roster pass owns the four sorts.
- **Liquid typing**: `design/RimMandrake/RM_liquid_types_mod.md` (2026-09-11)
  owns what scald water IS (`RM_WaterBoiling*` family, §7 row "boiling water";
  its §8 sets the `RUT_TheScald` biome terrain overrides and patches
  `RM_LiquidProperties` onto the shipped terrains). This kit consumes those
  defs; it rules nothing about the liquid.

**Naming**: generic mechanisms `RM_` (`RimMandrake.*`); Scald content defs
`RUT_` (`RimMandrake.Utinni.*`). One C# implementation per mechanic, tuned
per-biome by XML; RM_ classes live in the ruled kit home
(`src/RimMandrake/EnvironmentalHazards/`) or a sibling RM_ mod.

**Hard-ban compliance (sheet §6, linter-checkable)** — how each ban binds:

| Ban | Where it binds |
|---|---|
| 1. Never potable | The steam-catch (S2) yields water AT the condenser, never a "purify scald water" recipe; no bill, def or tech in this kit takes scald water as an ingredient. `dbh_water` on the shipped terrains is the thirst-mod's contact tag, not potability — ❓ verify at build that the thirst mod does not let pawns DRINK from `dbh_water`-tagged burn terrain; if it does, the tag moves to the margin terrain only (S3) and the linter checks the six boil defs carry no drink route. |
| 2. Never the terminator seas' biome | Every def this kit ships is `RUT_Scald*`-prefixed and referenced only from `RUT_TheScald`; no shared roster/weather/terrain with `RUT_TwilightSea`/`RUT_GreySea`. |
| 3. No boiling-immune traversal for free | The shipped burn values stand — S3's bath margin is a NEW ring terrain at the cool edge, it repaints no boil cell; S6's wrecks are priced in burns precisely because no def removes them. No apparel/hediff in this kit grants burn immunity. |
| 4. No macro-life in the boil itself | Bottom-walkers ship as a surfacing set-piece (S5), never a pawn swimming the surface layer; bubble-sailors are the ban's own carve-out ("nothing swims the roiling surface layer but bubbles and sails"). No wild-spawn commonality puts any kind IN boil cells. |
| 5. No drained, cooled, or tamed Scald | No mechanic writes boil terrain to anything else — S4's geysers add; nothing subtracts. The margin ring (S3) is authored at gen, not player-extendable (no floor/terraform recipe over boil cells ships from this kit). |
| 6. No vanilla-Earth flora/fauna | Fish tables (S3) point only at `FISH_BESTIARY_COMMISSION_1`'s thermophile defs; vanilla `Fish_*` never enters `RUT_TheScald.fishTypes`. |

Scoreboard: **6 mechanics** · heavy reuse (1 ruled comp + 2 miasma-kit
generics + vanilla 1.6 fishing/geyser machinery) · **3 new RM_/RUT_ classes**
(0 L, 1 M, 2 S) · XML-only content on top.

---

## S1. The boil layer — boiling-lift integration + standing steam (§5, §9)

**Player experience.** The lake burns to touch and comforts as it burns
(shipped). The sky is the boil's breath: white steam standing over cyan water,
light diffused, sound the endless exhale. The boil never stops.

**Engine route.** Mostly landed already; this kit finishes the sky:

- Terrain: shipped (`RUT_ScaldWater*`); biome water-terrain overrides ride
  `RM_liquid_types_mod.md` §8. Nothing to build here.
- `RUT_ScaldSteam` WeatherDef — the default sky: zero rain/snow rates
  (steam, not weather-rain; the R-B rain family is the Forge's), accuracy
  (**INVENTED**: 0.9), move 1.0, white steam overlay reusing the greentide's
  `RM_WeatherOverlay_GroundFog` class with white/steam textures *(class
  verified, greentide)* — share the class, ship new art. Ambient: the boil's
  breath (`soundsAmbient`).
- **The lock**: ruled `RM_GameCondition_EnvironmentalWeather`
  (`ALPHA_MECHANICS_KIT_1`) as a permanent `biomeMapConditions` entry *(both
  hooks verified, greentide)* — forced `RUT_ScaldSteam` with configured clear
  spells (§9's "still day" that shows the wrecks). No damage fields — the
  steam is clean; the WATER burns. ⚠️ The shipped BiomeDef already carries
  `baseWeatherCommonalities` to silence the zero-commonality log line — keep
  them consistent with the lock (commonalities become the fallback set).

**Effort**: **S** (one WeatherDef + art; lock is ruled kit). **v1: ships.**

## S2. The steam-catch (§7 ⭐ "the tap of the world")

**Player experience.** Condensers raised at the rim's lower vents drink the
clean breath: free, endless distilled water — below the Contagion's line —
if you can hold the ground and pay the shore's burns to build there. Whoever
holds catch-rights holds the monopoly's source (story register; the Deepwater
dossier owns the politics).

**Engine route.** `RUT_SteamCatch` building, placement-locked to vents the
way geothermal locks to geysers — crib `CompPowerPlantSteam` *(class
verified, `Source/RimWorld/CompPowerPlantSteam.cs`)* and vanilla geothermal's
geyser place-worker (❓ exact PlaceWorker class name — read the geothermal
ThingDef at build). Production: `RM_CompResourceCondenser : ThingComp`
(generic — props: output ThingDef, stack per cycle, cycle ticks, requires
being on a named vent/geyser def) — **INVENTED**: 25 water units/day
equivalent. Output FORM is **owner card 2** (item water vs thirst-mod pipe
network vs both); v1 default drafted as item-water so the comp has no
cross-mod dependency, with the DBH-network variant behind the card.

🔴 Ban 1 patrol: the condenser sits on a VENT and yields clean water from
steam; it has no input, no bill, and cannot be placed on water terrain.

**Effort**: **S/M** (one generic comp + building def + art). **v1: ships**
(item-water form).

## S3. Margin fishing + the baths (§7 "the silver harvest", "the baths"; §8 the two-faith shore)

**Player experience.** At the cool margins you can fish water that burns and
comforts in the same step — and bathe in the one ring where it only
comforts: the planet's sacred spa. The silver shoals are the catch; the
rainbow mats band the shallows around you.

**Engine route.** Almost entirely vanilla 1.6 (Odyssey) machinery, verified
in-index this session:

- **Fishing**: `BiomeDef.fishTypes` *(verified, `Source/RimWorld/BiomeDef.cs:143`,
  class `BiomeFishTypes`: freshwater/saltwater common+uncommon lists +
  `rareCatchesSetMaker`)*. Fish buckets bind by `TerrainDef.waterBodyType`
  *(verified, `Source/Verse/TerrainDef.cs:232`)* via flood-filled
  `WaterBody` regions — and ⚠️ **`WaterBody.SetFishTypes` switches ONLY on
  `Freshwater`/`Saltwater`** *(verified, `Source/RimWorld/WaterBody.cs:178`)*:
  a terrain typed `Other` or `None` yields NO fish, ever. So whether the
  Scald fishes at all hangs on the salinity ruling — **that card is already
  open and owned at `RM_liquid_types_mod.md` §9 CARD-1** (fouled mineral
  broth: `Saltwater`, `Other`+extension, or a modded bucket). This kit takes
  the ruling as input and wires `RUT_TheScald.fishTypes` accordingly; it does
  not pre-empt it. Fish defs themselves (the thermophile silver shoal — "the
  strangest entry the fish roster will ever take") are
  `FISH_BESTIARY_COMMISSION_1`'s; ban 6 keeps vanilla `Fish_*` out.
  Pollution→toxfish and population curves come free (`FishingUtility`,
  *verified*).
- **The baths**: `RUT_ScaldMargin` TerrainDef — the authored cool ring:
  burn **0/0**, `traversedThought HotSpring` (the comfort without the hurt),
  swimmable, NOT `avoidWander`. Recreation is vanilla:
  `JoyGiver_GoSwimming` *(read in full this session — Odyssey-gated
  (`ModLister.CheckOdyssey`), cell validator requires `IsWater` +
  `toxicBuildupFactor == 0` + standable + not `KnownDangerAt`, outdoor temp
  ≥ 10 °C — trivially met in the Anvil band)*. ❓ verify at build that the
  burn terrains' `avoidWander`/danger reads as `KnownDangerAt` so pawns
  never pick a swim path THROUGH boil cells to reach the margin; if not, the
  margin ring must be pathable without crossing boil (authoring constraint,
  not code). Placement of the ring on THE map is map-authoring (bridge), not
  worldgen. Sacredness/pilgrimage/two-faith shore: story + sacred pass
  (sheet Owed "canon sitting"), zero code here.

**Effort**: **S** (one TerrainDef + one fishTypes block; everything else is
engine). **v1: ships** — fishTypes lands when CARD-1 and the bestiary do.

## S4. Geyser fields (§8 "the vapor law's second densest ground")

**Player experience.** The shore is geysered ground: steam columns on their
own rhythm, percussion under the boil's breath — free power for whoever
builds among them, burns for whoever walks carelessly.

**Engine route.** Vanilla owns geysers end-to-end: `SteamGeyser` ThingDef,
`SteamGeysers` GenStepDef, and the `SteamGeysers_Increased` TileMutatorDef
("high geothermal activity") *(all three verified via `search_defs`)*.
Route: apply the mutator (or hand-place geyser density) on the Scald's shore
tiles of THE fixed map — map/world authoring via the bridge on the frozen
planet, **not worldgen** (❓ verify at build that a TileMutatorDef applied
post-hoc to an existing tile runs its map-side worker on next map-gen of that
tile; else hand-scatter `SteamGeyser` things at map author time). Geothermal
power on them is vanilla (`CompPowerPlantSteam`, *verified*). S2's vents are
these geysers' rim-side siblings (one def family, **INVENTED**: `RUT_ScaldVent`
as a non-buildable spawned variant that S2's condenser and S5's bubble lines
both key on).

**Effort**: **S** (defs + map authoring; no new C# unless the mutator route
fails). **v1: ships.**

## S5. Bubble-sailor and bottom-walker set-pieces (§4 ⭐, §9)

**Player experience.** Flotillas of bubble-sailors tack up the vent columns
and drift back down — the biome's signature silhouette, readable traffic.
And rarely, at the deep center, an enormous back breaks the surface and is
gone: the herds are down there, mowing.

**Engine route.** Reuses the miasma kit's two generics (their build is that
kit's; this kit is their second customer — the reason they're RM_):

- **Bubble-sailors**: placed at gen by `RM_GenStep_PlacedSetPieces`
  (miasma M6's scatterer) keyed to `RUT_ScaldVent` sites — each vent gets a
  sail cluster (kinds are roster content; `wildAnimals` stays the roster
  pass's). Tethering: `RM_CompTerritorialAnchor` (miasma M6) anchored to the
  vent — sails never leave their bubble line (**INVENTED**: radius 8),
  ignore everything, flee nothing (they're the kindest resident; combat
  stats near-nil in XML). Vertical tack/drift is presentation: ❓ whether a
  float/hover render (fleck or `Graphic` bob) beats a swimming pawn — decide
  at build; ban 4's carve-out allows them ON the surface either way.
- **Bottom-walkers**: v1 is a **surfacing set-piece, not a resident pawn**
  (ban 4: the walkers live at depth; nothing swims the surface but bubbles
  and sails). `RUT_WalkerSurfacing` IncidentDef (weighted only into this
  biome, cooldown days **INVENTED**: 8–20) + `RUT_IncidentWorker_WalkerSurfacing`:
  picks a deep-water cell far from shore, plays an effecter sequence (spray,
  wake, the back — art/effecter, no pawn spawned), Message not Letter after
  the first sighting. Whether walkers ever become real huntable pawnkinds at
  depth is **owner card 3**; the roster's "four sorts" can still assign
  walker KINDS as flavor-census entries without map presence.

**Effort**: **M** (incident worker S–M; scatterer/anchor are miasma builds;
art/effecters are the real cost). **v1: ships** — sails at vents + the
surfacing incident.

## S6. Burning-shallows wreck salvage (§8 "wrecks in the shallows")

**Player experience.** Through cyan glow on a still day: what the pan
swallowed, cooked clean. Salvage it if you want — the price is posted in
burns per trip, by the water itself.

**Engine route.** `RUT_ScaldWreck*` building defs (2–3 silhouettes, art
pass) scattered at map-gen in shallow scald water —
`GenStep_ScatterThings` *(verified, `Source/Verse/GenStep_ScatterThings.cs`,
subclass of `GenStep_Scatterer`)* with a terrain validator for
`RUT_ScaldWaterShallow`/`OceanShallow` (❓ whether the stock scatterer takes
a terrain predicate in XML or needs a 10-line subclass — read
`GenStep_Scatterer.CanScatterAt` at build; worst case reuse
`RM_GenStep_PlacedSetPieces` with a terrain-band validator). Salvage is
vanilla deconstruct/smash yields (`costList`-derived returns + a small
`RUT_ScaldSalvage` loot ThingSetMaker ❓ crib the wreck/ancient-danger loot
shape); the burn-pricing needs zero code — the shipped terrains charge per
tick standing in them (ban 3 holds because nothing waives it). Cooked clean:
no rot, no corpses, no hostiles — hostile salvage is `SCALD_DARK_TOWER_1`'s
dungeon, a different item; the linter can check no pawn spawner rides these
defs. Loot REGISTER (what the pan swallowed — which eras, which goods) is
the items pass's, per sheet economy convention.

**Effort**: **S** (defs + scatter wiring + loot maker). **v1: ships.**

---

## XML-only ledger (no C#, listed so nothing gets re-invented)

- Biome figures, `baseWeatherCommonalities`, empty `wildAnimals` — shipped
  BiomeDef; roster pass fills fauna; mats/rainbow pigment flora are
  roster/art + items passes (§7 pigment economy is NOT this kit's).
- `RUT_ScaldWater*` terrains + their `RM_LiquidProperties` rows —
  shipped / `LIQUID_TYPES_MOD_1`.
- Thermophile fish defs — `FISH_BESTIARY_COMMISSION_1`.
- The two-faith shore, witness-trail, Compact catch-rights — story/sacred
  registers, no defs here.
- The dark tower dungeon — `SCALD_DARK_TOWER_1` (already in build:
  `StructureLayoutDefs_DarkTower.xml`).

## New-C# roster (beyond reuses)

| Class | For | Effort |
|---|---|---|
| `RM_CompResourceCondenser` | S2 | S |
| `RUT_IncidentWorker_WalkerSurfacing` | S5 | S–M |
| terrain-validated scatter (subclass ONLY if stock scatterer can't) | S6 | S |

Reused: `RM_GameCondition_EnvironmentalWeather` (ruled, `ALPHA_MECHANICS_KIT_1`) ·
`RM_WeatherOverlay_GroundFog` (greentide) · `RM_GenStep_PlacedSetPieces` +
`RM_CompTerritorialAnchor` (miasma kit) · vanilla 1.6 fishing, swimming,
geysers, geothermal.

## Build order

1. **External dependencies land first**: `ALPHA_MECHANICS_KIT_1` (S1 lock);
   miasma kit's scatterer/anchor generics (S5); `LIQUID_TYPES_MOD_1` +
   its §9 CARD-1 ruling (S3 fishing bucket); `FISH_BESTIARY_COMMISSION_1`
   (S3 fish defs).
2. **S1 steam sky** — biome instantly feels right; every later test happens
   under it.
3. **S4 geyser/vent field** — S2 and S5 both key on the vent defs.
4. **S2 steam-catch** — after S4; card 2 decides output form before art.
5. **S3 margin terrain + baths** — independent; fishing block waits on its
   two dependencies.
6. **S6 wrecks** — independent, any time after terrain overrides land.
7. **S5 set-pieces** — after S4 (vents) and the miasma generics; incident
   last (pure presentation).

## Open owner cards

*(Card 1 is deliberately NOT here: **the Scald salinity/fishing-bucket card
is already open at `design/RimMandrake/RM_liquid_types_mod.md` §9 CARD-1**
— this kit consumes its ruling.)*

2. **RULED 2026-09-12 — (c) BOTH, behind a Mod Settings toggle.** Item
   water is the default; the `dbh_water` pipe-network source enables in
   settings when the thirst mod is present (MOD_OPTIONS_RETROFIT_1
   doctrine).
3. **RULED 2026-09-12 — diving interaction, AND IT IS V1.** Owner verbatim:
   "Diving interaction, and make the diving mod v1 content now!!" ⇒ The
   bottom-walkers do not stay a visual: a diving mechanic (hunt/commune at
   the deep center, priced in burns) ships as v1 content, as its own
   RimMandrake-tier mod — filed as SCALD_DIVING_MOD_1. Ban 4's "out of the
   boil" reading is superseded exactly this far: the DEEP interaction
   exists; the boil surface remains no-swim.
   (Card 1, the basin's salinity, is ruled at RM_liquid_types_mod.md §9:
   FRESHWATER — and the rivers flow OUT of the Scald.)
