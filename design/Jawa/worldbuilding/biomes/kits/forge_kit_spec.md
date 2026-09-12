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
❓ The sheet's three donor biomes (`Volcano`, `LavaField`,
`AB_PyroclasticConflagration`) — confirm at build which mod/DLC owns each and
whether 1.6 lava terrain damages standing pawns natively (nothing verified
here assumes it does).

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
in `rosters/the_forge.json`, MEASURED "floats") — ❓ read the Alpha Animals
def + any comp/class behind its float at build and crib the draw route.
This kit adds the pasture-binding:

- `RM_MapComponent_VaporColumns` — builds a column field from emitter
  positions (steam geysers, vents, lava-adjacent cells) at map init +
  on-change; public `InColumn(IntVec3)`. The vent props themselves are the
  ruled **`RM_CompActiveGasEmitter`** reuse (miasma/greentide precedent —
  harmless white gas, pure atmosphere) — zero new emitter C#.
- `RM_CompVaporDrifter : ThingComp` on sky kinds: constrains wander/graze
  destinations to column cells (❓ cleanest seam — wander-root override vs a
  small ThinkTree subtree; same open question the miasma's
  `RM_CompTerritorialAnchor` carries, resolve both against the same source
  read at build), grants the kit's ground-hazard immunities (scald bursts do
  not touch drifters — they live in the steam), and drives the float-draw
  offset if the Aerofleet route turns out to be class-side rather than
  def-side.
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
  `MapPortal` down (portal-in-pocket-map chaining) — nothing in the indexed
  source forbids it, nothing proves it; PROVE in a quicktest before
  committing the multi-floor design. Fallback that loses little: one deep
  floor per tower, tower count from the set-piece scatterer (card 1 rules
  which).
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
  it can never establish (the sheet's physics as def structure; linter:
  no `plant.reproduces` on it ❓ exact field name — read `PlantProperties`
  at build, never guess it into XML).
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

## Open owner cards (unruled — next card sitting)

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
