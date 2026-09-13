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
| 1. Never potable | **RESOLVED — SCALD_MECHANICS_1 spike, 2026-09-13.** CONFIRMED `dbh_water` does enable DBH thirst drinking (`BadHygiene.dll`, workshop/294100/836308268, 1.6 Assemblies, carries the literal alongside its own drink-tracking strings; `RUT_ScaldWater.xml`'s own prior header already stated the tag was placed there SO pawns could drink the boil, per R-B4a). That conflicted with this sheet's Ban 1, so the remedial action this row itself pre-ruled was taken: the tag is removed from all six `RUT_ScaldWater*` boil terrains and moved to the new `RUT_ScaldMargin` terrain (S3) — the boil now carries no drink route at all; the margin ring is the Scald's sole drink/draw source. |
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
verified, `RimWorld/CompPowerPlantSteam.cs`, decompile)* and vanilla
geothermal's geyser place-worker — **RESOLVED**: `PlaceWorker_OnSteamGeyser`
(`RimWorld/PlaceWorker_OnSteamGeyser.cs`, confirmed via the real 1.6
decompile this pass): checks `map.thingGrid.ThingAt(loc, ThingDefOf.SteamGeyser)
!= null`, a two-line pattern the S4 vent def's PlaceWorker crib follows
directly. Production: `RM_CompResourceCondenser : ThingComp` — **BUILT AND
COMPILING** this pass (`src/RimMandrake/EnvironmentalHazards/Source/
RM_CompResourceCondenser.cs`), cribbing `CompPowerPlantSteam`'s own
"re-check `ThingAt(parent.Position, requiredDef)` every tick, never cache"
shape so a deconstructed vent silently stops production rather than erroring
(generic — props: output ThingDef, stack per cycle, cycle ticks, requires
being on a named vent/geyser def, defaulting to vanilla `SteamGeyser` until
S4's `RUT_ScaldVent` exists) — **INVENTED**: 25 water units/day equivalent.
Output FORM is **owner card 2** (item water vs thirst-mod pipe network vs
both); v1 default drafted as item-water so the comp has no cross-mod
dependency, with the DBH-network variant behind the card.

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
- **The baths**: `RUT_ScaldMargin` TerrainDef — **BUILT** this pass
  (`src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_ScaldMargin.xml`), the
  authored cool ring: burn **0/0**, `traversedThought HotSpring` (the
  comfort without the hurt), swimmable, NOT `avoidWander`, and (per ban 1's
  now-RESOLVED row above) the sole carrier of `dbh_water`. Recreation is
  vanilla: `JoyGiver_GoSwimming` *(read in full this session — Odyssey-gated
  (`ModLister.CheckOdyssey`), cell validator requires `IsWater` +
  `toxicBuildupFactor == 0` + standable + not `KnownDangerAt`, outdoor temp
  ≥ 10 °C — trivially met in the Anvil band)*. **RESOLVED, and NOT the
  answer hoped for**: `PawnUtility.KnownDangerAt` (`RimWorld/PawnUtility.cs:619`,
  decompile) is `c.GetEdifice(map)?.IsDangerousFor(forPawn) ?? false` —
  edifice-only (traps/turrets), it never reads terrain `burnDamage` or
  `avoidWander` at all. Neither `JoyGiver_GoSwimming`'s cell validator nor
  `SwimPathFinder.TryFindSwimPath` (both read this session) check burn
  damage by any other route either, so nothing in vanilla stops a swim path
  from crossing open boil cells to reach the margin. **This is a real
  map-authoring constraint, not fixable in code** (documented in
  `RUT_ScaldMargin.xml`'s own header): the ring must be sited as a
  geometrically isolated cove/inlet cut off from open boil water by land,
  never a plain strip along an open shore. Placement of the ring on THE map
  is map-authoring (bridge), not worldgen. Sacredness/pilgrimage/two-faith
  shore: story + sacred pass (sheet Owed "canon sitting"), zero code here.

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
planet, **not worldgen**. **RESOLVED, decompile this pass**:
`GenStep_ScatterGeysers.CalculateFinalCount` (`RimWorld/GenStep_ScatterGeysers.cs`)
multiplies its base geyser count by `map.Biome.geyserCountFactor` and then
`foreach (TileMutatorDef mutator in map.TileInfo.Mutators) num *=
mutator.geyserCountFactor` — read LIVE at map-gen time from the tile's own
`Mutators` list (`TileMutatorDef.geyserCountFactor`, confirmed field). No
`TileMutatorWorker_SteamGeysers`-shaped class exists anywhere in the
decompile's ~65 `TileMutatorWorker_*` files — this mutator is data-only, not
worker-driven, so applying it to a tile's `Mutators` list BEFORE that tile's
map generates is sufficient; no post-hoc worker re-run is needed or possible.
⚠️ Timing constraint this resolves INTO, not out of: the mutator must land
before the Scald's map is (re)generated — if the map already exists, a
regen is required for the density bump to take effect; this is a
sequencing note for whoever does the world-authoring pass, not a code
question. Geothermal power on them is vanilla (`CompPowerPlantSteam`,
*verified*). S2's vents are these geysers' rim-side siblings (one def
family, **INVENTED**: `RUT_ScaldVent` as a non-buildable spawned variant
that S2's condenser and S5's bubble lines both key on).

**Effort**: **S** (defs + map authoring; no new C# unless the mutator route
fails). **v1: ships.**

## S5. Bubble-sailor and bottom-walker set-pieces (§4 ⭐, §9)

**Player experience.** Flotillas of bubble-sailors tack up the vent columns
and drift back down — the biome's signature silhouette, readable traffic.
And rarely, at the deep center, an enormous back breaks the surface and is
gone: the herds are down there, mowing.

**Engine route.** Partly reuses the miasma kit's generics (their build is
that kit's; this kit is their second customer — the reason they're RM_).
⚠️ **CORRECTION this pass**: only ONE of the two miasma generics actually
exists yet. `RM_CompTerritorialAnchor` shipped for real
(`MIASMA_MECHANICS_1`'s spike, `src/RimMandrake/EnvironmentalHazards/Source/
RM_CompTerritorialAnchor.cs`) and is usable now. `RM_GenStep_PlacedSetPieces`
does **not** exist — miasma's own item file lists it under its Spike 5
"Owed, not done" line explicitly. The bubble-sailor placement route below is
therefore blocked on that scatterer landing (miasma's own future work, not
this kit's), not safely spikeable for real placement yet — only the anchor
half is provably available today.

- **Bubble-sailors**: placed at gen by `RM_GenStep_PlacedSetPieces`
  (miasma M6's scatterer — **not yet built**, see correction above) keyed to
  `RUT_ScaldVent` sites — each vent gets a sail cluster (kinds are roster
  content; `wildAnimals` stays the roster pass's). Tethering:
  `RM_CompTerritorialAnchor` (miasma M6, **built and available now**)
  anchored to the vent — sails never leave their bubble line (**INVENTED**:
  radius 8), ignore everything, flee nothing (they're the kindest resident;
  combat stats near-nil in XML). Vertical tack/drift is presentation: ❓
  whether a float/hover render (fleck or `Graphic` bob) beats a swimming
  pawn — decide at build; ban 4's carve-out allows them ON the surface
  either way.
- **Bottom-walkers**: v1 is a **surfacing set-piece, not a resident pawn**
  (ban 4: the walkers live at depth; nothing swims the surface but bubbles
  and sails). `RUT_WalkerSurfacing` IncidentDef (weighted only into this
  biome, cooldown days **INVENTED**: 8–20) + `RUT_IncidentWorker_WalkerSurfacing`
  — **BUILT AND COMPILING this pass**
  (`src/RimMandrake/EnvironmentalHazards/Source/
  RUT_IncidentWorker_WalkerSurfacing.cs`): samples deep boil-water cells
  (`terrain.IsWater && terrain.burnDamage > 0`, which excludes the margin
  ring without needing to name it) and keeps the one furthest from a map
  edge as a "deep center" stand-in, fires `Messages.Message` (not a Letter)
  with no pawn spawned. Effecter choreography (spray, wake, the back) is
  art content, explicitly left for the full build; so is the actual
  `RUT_WalkerSurfacing` IncidentDef XML and its cooldown tuning. Whether
  walkers ever become real huntable pawnkinds at depth is **owner card 3**;
  the roster's "four sorts" can still assign walker KINDS as flavor-census
  entries without map presence.

**Effort**: **M** (incident worker S–M; scatterer/anchor are miasma builds;
art/effecters are the real cost). **v1: ships** — sails at vents + the
surfacing incident.

## S6. Burning-shallows wreck salvage (§8 "wrecks in the shallows")

**Player experience.** Through cyan glow on a still day: what the pan
swallowed, cooked clean. Salvage it if you want — the price is posted in
burns per trip, by the water itself.

**Engine route.** `RUT_ScaldWreck*` building defs (2–3 silhouettes, art
pass) scattered at map-gen in shallow scald water —
`GenStep_ScatterThings` *(verified, `Verse/GenStep_ScatterThings.cs`,
subclass of `GenStep_Scatterer`)* with a terrain validator for
`RUT_ScaldWaterShallow`/`OceanShallow`. **RESOLVED, decompile this pass, and
NO C# needed**: `GenStep_ScatterThings` carries stock XML-settable
`terrainValidationRadius`/`terrainValidationAllowed`/`terrainValidationDisallowed`
fields; its `CanScatterAt` override (read in full) walks
`GenRadial.RadialCellsAround(loc, terrainValidationRadius)` and checks
`terrain.HasTag(tag)` for each listed tag — **TAG-based, not defName-based**.
So the wreck scatter needs no subclass, only a shared tag on the shallow
Scald terrains (e.g. an `RUT_ScaldShallow` tag added to
`RUT_ScaldWaterShallow`/`RUT_ScaldWaterOceanShallow`/`RUT_ScaldWaterMovingShallow`
at build, since none of the three currently carry a tag that distinguishes
shallow from deep) fed into `terrainValidationAllowed`. This drops the S6
class ledger row below from "S, subclass ONLY if stock can't" to **zero new
C#** — confirmed possible, not guessed. Salvage is
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

| Class | For | Effort | Status |
|---|---|---|---|
| `RM_CompResourceCondenser` | S2 | S | **Built, compiling** (SCALD_MECHANICS_1 spike) |
| `RUT_IncidentWorker_WalkerSurfacing` | S5 | S–M | **Built, compiling** (SCALD_MECHANICS_1 spike) |
| ~~terrain-validated scatter subclass~~ | S6 | — | **RESOLVED: not needed.** Stock `GenStep_ScatterThings` handles it via `terrainValidationAllowed` tags. |

Scoreboard correction (this pass): **2 new classes**, both built and
compiling — down from the drafted 3, since S6 needs none.

Reused: `RM_GameCondition_EnvironmentalWeather` (ruled, `ALPHA_MECHANICS_KIT_1`) ·
`RM_WeatherOverlay_GroundFog` (greentide) · `RM_CompTerritorialAnchor`
(miasma kit, built and available) · `RM_GenStep_PlacedSetPieces` (miasma
kit, **drafted only, not yet built** — blocks real bubble-sailor placement,
see S5's correction above) · vanilla 1.6 fishing, swimming, geysers,
geothermal.

## Build order

1. **External dependencies land first**: `ALPHA_MECHANICS_KIT_1` (S1 lock,
   closed) — closed; miasma kit's scatterer/anchor generics (S5) — the
   anchor half is built, the scatterer half is not (see S5's correction);
   `LIQUID_TYPES_MOD_1` + its §9 CARD-1 ruling (S3 fishing bucket) — closed
   tonight; `FISH_BESTIARY_COMMISSION_1` (S3 fish defs) — **checked this
   pass, still `doing`**: it is a design/roster proposal awaiting owner
   rulings on 8 cardable questions, no build item filed yet. This blocks
   only `RUT_TheScald.fishTypes`' actual fish content (S3's fishing HALF);
   it does not block S3's `RUT_ScaldMargin` terrain (built this pass, zero
   dependency on the fish roster) or any other mechanic in this kit.
2. **S1 steam sky** — biome instantly feels right; every later test happens
   under it.
3. **S4 geyser/vent field** — S2 and S5 both key on the vent defs.
4. **S2 steam-catch** — after S4; card 2 decides output form before art.
5. **S3 margin terrain + baths** — independent; fishing block waits on its
   two dependencies.
6. **S6 wrecks** — independent, any time after terrain overrides land.
7. **S5 set-pieces** — after S4 (vents) and the miasma generics; incident
   last (pure presentation).

## Owner cards — RULED, sitting 2026-09-12

*(Card 1 is deliberately NOT here: **the Scald salinity/fishing-bucket card
lived at `design/RimMandrake/RM_liquid_types_mod.md` §9 CARD-1** — this kit
consumes its ruling, restated below alongside cards 2/3. All three cards are
settled; nothing here still blocks the Scald kit.)*

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
