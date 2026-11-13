# A geyser in a pit: it sinks, it bubbles, it is a hot tub

Item: `RIMMANDRAKE_SINK_GEYSER_INTO_PIT_BUBBLING_HOT_TUB` · mod: FlowWorks (`mandrake.rimmandrake.flowworks`) · written
2026-11-12 19:00 PST by a detached BENCH helper of the Conductor · status: BUILT offline (2026-11-12 evening), live
proof owed (4.2). The three owner choices (`D:\ClaudeWork\rimmandrake\conductor\underliquid_20261112_evening\geyser\QUESTIONS.md`)
were answered **by card, 2026-11-12 ~7:5x PM PST**:

- **[Q1] Bathing: "Water plus harmless liquids (tar, oil, blood, slimes bathable, each with a cost)"** — not the
  water-only recommendation. Section 3.4 carries it.
- **[Q2] Generator: "Allowed in a dry pit, caps it (no bubbles, no tub after)"** — as recommended.
- **[Q3] Mood: "Vanilla's small bonus (Odyssey hot-spring memory, +2 for about 2.4 h)"** — as recommended; the brief adds
  that a setting may raise it (`geyserPoolMoodFactor`).

## The ruling

Owner, 2026-11-12 ~18:40 PST, verbatim:

> *"Digging a pit on a Geyser allows the Geyser to descend to the bottom of the pit (it remains and descends). Filling
> the pit with water or any fluid still works and generates distinctive bubbles where the geyser is. When pawns are
> near those bubbles, they will treat it like a hot tub and gain benefits like the Hot Springs mod currently supports
> (see mod)."*

## 1. Which "Hot Springs mod"

**Standalone Hot Spring** by balistafreak, packageId `balistafreak.StandaloneHotSpring`, Steam workshop 2205980094
(`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2205980094`). [guess ~85%] Why:

- It is the only installed candidate **built on a steam geyser** (`PlaceWorker_OnSteamGeyser`; its description:
  *"Built on top of a naturally occuring steam geyser"*). The ruling is about geysers.
- It is in **52 of the 96** saved mod lists under `deployed/config/` (the full-list snapshots of August 2026), so it
  was on his list [measured]. None of the hot-spring mods is active in today's `ModsConfig.xml` [measured, parsed].
- The other five: *Hospitality: Spa* (2971831654, guests' spa buildings; in none of the 96 lists), *Dubs Bad Hygiene -
  Spring Water Patch* (3531641684, a drink-source patch), *Better Hot Springs* (3532108439: patches vanilla Odyssey's
  `HotSpring` thought from +2 mood for 0.1 day to +6 for 0.25 day; in none of the lists), *Nature's Pretty Sweet*
  (3542949511, deprecated terrain pack), *ReGrowth: Boiling* (3565675704, a biome; in 26 lists, but it has no tub).
- Vanilla 1.6 Odyssey also has hot springs: the `HotSpring` water terrain (`traversedThought HotSpring`, +2 mood for
  0.1 day, `heatPerTick 0.01`, `canFreeze false`, steam `AirPuff` flecks) on the `HotSprings` landmark. That is not a
  mod, so it is not what "the Hot Springs mod" means, but its thought is reused in **[Q3]**.

### What Standalone Hot Spring gives (read from its 1.6 defs and its shipped C# source)

| part | value |
|---|---|
| the building | `StandaloneHotSpring`, 8x4, on a geyser, 18000 work, Construction 8, 500 stone. Beauty 200, Comfort 1.0, JoyGainFactor 1.4, BedRestEffectiveness 1.111, `ai_chillDestination`, joy kind Meditative |
| joy | `JoyGiverDef BathStandaloneHotSpring`: baseChance 5, Meditative; `JobDef`: joyDuration 4000, joyMaxParticipants 6 |
| the job (`JobDriver_bathStandaloneHotSpring`) | walk to a free one of 6 fixed slots; soak 3000 ticks (1.2 h) lying face up; every tick: comfort from the cell, rest (`TickResting` at 1.111), joy `1.4 × joyGainRate × 0.36 / 2500` per tick (no joy for prisoners); every 100 ticks a sleep Z or a healing-cross mote |
| while soaking | hediff **Healing waters** (`IntheStandaloneHotSpring`): ComfyTemperatureMin −50, ComfyTemperatureMax +50, BloodFiltration +0.08, naturalHealingFactor ×1.25 |
| after | hediff **Residual rejuvenation** (`BathedInStandaloneHotspring`): BloodFiltration +0.08, naturalHealingFactor ×1.25; severity 0.5 falling 0.4 a day, so it lasts 1.25 days ("slightly over 24 hours"; one visit a day is enough); a new soak replaces it |
| who | anyone with a joy need picks it as recreation; a player-faction humanlike can be ordered in ("Use hot spring" float menu), which is how a sick pawn is sent; downed pawns cannot use it (drowning risk, by its own text) |
| look | Harmony postfixes on `PawnRenderNodeWorker_Apparel_Body.CanDrawNow` and `..._Head.HeadgearVisible` hide a bather's clothes (not in portraits) |
| not given | no mood thought, no cleanliness/hygiene, no temperature change of the air, no scalding |

## 2. What happens today when a pit is dug on a steam geyser

- **The dig is allowed.** Vanilla `SteamGeyser` is 2x2, `altitudeLayer Floor`, `isEdifice false`, `destroyable false`.
  `Designator_DigCanal.CanDigCell` refuses only an edifice (`"Must designate open ground."`), so all four geyser cells
  can be dug to any depth [measured, code read].
- **The geyser survives but does not descend.** Nothing in FlowWorks names `SteamGeyser` or `Building_SteamGeyser`
  [measured, grep of `src\RimMandrake\FlowWorks`], and vanilla `TerrainGrid.DoTerrainChangedEffects` only destroys
  plants, filth, blueprints and frames [measured, decompile]. So the geyser keeps its map-mesh print at its old Floor
  altitude, flat over the cut, and keeps puffing: `IntermittentSteamSprayer` throws `AirPuff` at `TrueCenter()` (the
  surface) for 200–500 ticks every 500–2000 ticks and `GenTemperature.PushHeat(geyser, 40)` every 20 ticks while it
  sprays, unless a harvester (a geothermal generator) sits on it [measured, decompile]. [guess ~75%] that it draws over
  the pit's wall faces and over any liquid poured in; nobody has looked live.
- **Filled with liquid:** the liquid's own bubbles only (`RM_LiquidSurface.Bubbles`, per-fluid `surfaceLook.bubbles`;
  plain water has none), and the dry puffs keep rising out of it.
- **Geothermal generator:** needs `PlaceWorker_OnSteamGeyser` (the geyser at its exact centre) and `Heavy` affordance.
  The dug-cell terrains in `FlowWorks\Defs\Canals` carry Diggable/Light/Soil/Walkable/Water affordances and no `Heavy`,
  so [guess ~70%] a generator is refused on a dug geyser today. A geyser that already has a generator cannot be dug (the
  generator is an edifice).

### What already exists and is reused (searched before designing)

| need | existing | reuse |
|---|---|---|
| how deep a cell is dug | `RM_MapComponent_Excavation.ExcavatedDepthAt` | the geyser's seat depth |
| draw a thing sunk in a cut | `RM_PitDepthDraw` (`RM_Patch_PitDepthDrawOffset.SinkOf`, `pitSinkPerLevel` 0.3/notch) | the same sink for the geyser print and its puffs |
| liquid covering a thing | `RM_UnderLiquid.Share` / `Seen` (the one under-liquid law, RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL) | the geyser is one more caller: a thing standing on the floor, `GeyserMetres` tall |
| bubbles per liquid | `RM_LiquidSurface` + `RM_Fleck_LiquidBubble` (Biotech vat bubble, tinted by `surfaceLook.bubbleColor`), `RM_LiquidLookMath.BubblesThisTick`, settings `liquidBubblesEnabled`/`liquidBubbleDensity` | the plume uses the same fleck and colour, its own rate |
| hot liquid harm | `RM_HotLiquid` (scald patches for hot releases, Burn by heat) | **not used**: a tub is not a scald. Boiling water poured in still scalds through its own terrain |
| room heat from liquid | `RM_LiquidHeat` (FluidDef `hot`/`cold` push vanilla room heat) | unchanged; the geyser's own vanilla `PushHeat` is the only extra heat |
| bathing in the Scald | `RUT_ScaldMargin` (SCALD_MECHANICS_1 S3): vanilla `HotSpring` thought plus vanilla `JoyGiver_GoSwimming` | the precedent for "comfort without the hurt" and for the `HotSpring` thought; it has no tub job |
| standing in water is cold | `RM_WetCosts` raises ComfyTemperatureMin in water | the soak hediff's −50 cancels it while soaking, as the mod's does |

## 3. Design

All of it lives in FlowWorks (pits and liquids are FlowWorks'), namespace `RimMandrake.FlowWorks`, defs `RM_`.
**No dependency on Standalone Hot Spring**: none of its defNames, classes, textures or packageId; the numbers are copied
as our own defaults. If a player also runs that mod, both work: its building is a different thing on an undug geyser.

### 3.1 The geyser descends

- **Seat depth** = the **shallowest** dug depth of the geyser's four cells (`RM_GeyserTubMath.SeatNotches`). It sits on
  ground that is there, so it never floats: one undug corner keeps it at the surface, four cells dug to 2 m seat it at
  2 m. Derived from the excavation grid every time it is asked; **no new saved field**, so old saves load as they are,
  and filling a pit back in raises the geyser with it.
- **Drawn** on its own squares, at the seat: the print, the puffs, the plume and the heated water share one anchor,
  `RM_GeyserPit.VentCentre` (owner 2026-11-13: *"the geyser itself is outside the hot tub dark blue region ... you can
  see the dark geyser beneath, the bubbles north of that, and the hot tub dark blue square north of that too"*;
  RIMMANDRAKE_ALIGN_HOT_TUB_VENT_BUBBLES_AND_WATER_SQUARE). The first build lowered the print by the pawns' sink; the
  `PrintPlane` prefix applied that shift again on every plane the under-liquid split re-printed, so the vent drew about
  four squares south of its water and the plume two: removed. Every 250 ticks a geyser whose seat moved re-meshes its
  squares. The geyser casts no pit floor shadow (it is a vent).
- **Under liquid** by `RM_UnderLiquid`: a thing standing on the floor, `GeyserMetres = 0.4` (a low vent mound), its
  depth the seat. `Share(level, 0, 0.4)` of it is under; the drowned part draws at `Seen(clarity, metresOver)`: tinted in
  clear water, hidden in an opaque liquid (tar, oil, blood). The row is `RM_SubmergeDraw.BuildingMetres`.
- **Its puffs** rise from the vent while it is dry, where vanilla puts them.
- The geyser **never vanishes** (no despawn, no destroy, same ThingID throughout dig, fill, drain and refill).

### 3.2 Filling: the plume of bubbles

- **Covered** = the liquid's true level over the seat exceeds `GeyserMetres` (the vent mouth is under). In shallower
  liquid it still puffs.
- **Covered and spraying** (the vanilla sprayer still runs its timer): no dry `AirPuff` from the vent; instead a
  **plume**: `RM_Fleck_LiquidBubble` thrown over the geyser's 2x2 footprint at the liquid's surface, larger (scale 1.5–3
  against the ambient 0.8–1.8), clustered toward the vent centre, with a `WaterRipple` ring on most bursts. Between
  sprays a gentle stream keeps going (about a fifth of the spray rate), so a sunk geyser is always findable by eye.
- **Distinctive per liquid:** the bubble tint is the liquid's own `bubbleColor` (each FluidDef's surface look); a
  liquid with no colour of its own uses white-blue. Thick liquids (tar, slimes, oil: slow `ticksPerTile`) throw fewer,
  bigger, slower bubbles ("blorps") and no ripple ring; thin ones a fast fizz. A water-like liquid also gives off a
  faint steam wisp at the surface during a spray (vanilla `AirPuff`, from the surface, not the vent).
- **Cost:** the plume is emitted only while the geyser is in view (the same in-view rule as
  `RM_LiquidSurface.Bubbles`), from a per-map list of the map's geysers (`RM_MapComponent_GeyserPits`, filled at map
  init and by a `SpawnSetup` postfix; the seat is read from the grid per use, so no depth-change hook is needed; never a
  map scan per tick). Cosmetic RNG isolated (`Rand.PushState`), as the existing emitter does.
- **Art:** the plume uses the existing surface bubble (`RM_Fleck_LiquidBubble`, Biotech's vat bubble tinted per
  liquid) as its placeholder; real plume art is its own art item, filed through the art ledger
  (`RIMMANDRAKE_DRAW_GEYSER_PLUME_BUBBLE_ART_PLACEHOLDER_IN_USE`).

### 3.3 Heat

- **One kind of heat.** The geyser keeps its vanilla `PushHeat(40)` every 20 ticks while spraying, dry or covered.
  An open pit is outdoors, so it warms nothing (vanilla: an outdoor room takes no heat); a roofed pit room **cooks**,
  exactly as vanilla says of any room over a geyser. That is the trade of a roofed bathhouse; the soak hediff's
  ComfyTemperatureMax +50 is what makes the soak bearable in it, as in the mod.
- **The liquid is not made hot.** No `RM_HotLiquid` patch, no scald, no change of FluidDef. Water over a geyser stays
  water. Boiling water poured in is still boiling water and still burns through its own terrain (SCALD rule: no
  burn immunity for free).
- **It does not freeze:** the heated water (3.4 Where) never freezes while the geyser is uncapped, like vanilla's
  `HotSpring` (`canFreeze false`): a postfix on vanilla `FreezeManager.CanFreeze` (the gate every freeze roll and spread
  reads) answers false on those squares; no new freezing rule.

### 3.4 The hot tub

- **Where:** the liquid the vent is BENEATH: cells within `geyserPoolReach` (default 2.5 cells) of the geyser's centre
  that are dug, wet with the vent's own liquid and joined edge to edge through it to the vent's own squares
  (`RM_GeyserTubMath.PoolRegion`), while the geyser is covered and uncapped. Water in another pit or a lake beside the
  vent is never heated, however near (owner 2026-11-13: *"I had intended that the Geyser must itself be beneath the pit
  water itself, not just adjacent as shown here. There's no way for the heat to get from the hole into the pit water in
  this configuration."*; RIMMANDRAKE_RESTRICT_HEAT_TO_GEYSER_BENEATH_PIT_WATER_ONLY). The bubbles are the sign; nothing
  else is built.
- **Which liquids [Q1, owner by card: "Water plus harmless liquids"]:** a positive field on the liquid,
  `FluidDef.bathGroup` (`RM_GeyserTubMath.BathGroup`, default `None`): `Water` on `RM_Fluid_Water` (the freshwater ladder
  rain and rivers fill pits with), `Tar`, `Oil`, `Blood`, and `Slime` on the four slimes. Water always bathes; each other
  group follows its own setting. `None` (acid water, poison, reaction liquor, boiling water, icy water, chemfuel, propane,
  astrofuel) **bubbles but is never a tub**: liquids that harm by themselves and the fuels, as he ruled; reaction liquor
  was not named on the card and stays out. A new liquid opts in by its own def. Not read from terrain harm: the fill
  terrains of tar, oil, chemfuel, propane, astrofuel, blood and the slimes carry no `dangerous`, `toxicBuildupFactor` or
  `burnDamage` (their harm is fire, slip or poison-per-day), so a terrain gate would let the fuels in [measured, 16
  FluidDefs' brim terrains, 2026-11-12]. Icy water stays out: the geyser does not heat the liquid (3.3).
- **What a strange bath costs** (`FluidDef.bathCost`, data on the liquid; each kind of cost behind its own setting;
  paid by any soak that began, whether or not it was cut short):

  | liquid | filth where the bather climbs out | memory | slip |
  |---|---|---|---|
  | water | none | none | none |
  | tar | 3 `RM_Filth_Tar` | `RM_BathedInTar` "tar bath" −2 for 0.5 day | none |
  | oil | 3 `RM_Filth_LiquidSpill` | none | none |
  | blood | 3 `Filth_Blood` | `RM_BathedInBlood` "bathed in blood" −4 for 1 day (nullified by Psychopath, Bloodlust) | none |
  | the four slimes | 2 `RM_Filth_LiquidSpill` | none | 2 s stun (120 ticks) climbing out |

  Small and legible: a tar or blood bath is still a net gain for a pawn who needs joy and healing, never a trap. Slime
  is already nearly impossible to wade (`RM_SlimeSlip`), so a slime pool is mostly a deliberate build.
- **Who:** any pawn with a joy need (colonists, slaves, guests), as recreation; prisoners soak but gain no joy (as the
  mod); a player-faction humanlike can be ordered in ("Soak in the hot pool"), which is how a sick pawn is sent. Not
  downed pawns, not animals, not a pawn who cannot reach the cell. Up to 6 at once per geyser (the mod's
  `joyMaxParticipants`).
- **Getting in:** ordinary FlowWorks pathing into the pit (a ramp, a ladder or a shallow side). A pit no pawn can
  enter is a tub nobody uses; that is the player's build, not a defect. In liquid deeper than wading the pawn soaks
  swimming, head up (`RM_Swim`), so a deep pool works; a pawn that cannot swim there is not given the job.
- **The job** `RM_SoakInGeyserPool` (`JoyGiverDef` + `JobDef`, Meditative, joyDuration 4000, baseChance 5): go to a free
  cell in reach, soak 3000 ticks, every tick comfort from the cell, rest at 1.111, joy at the mod's rate with
  JoyGainFactor 1.4; every 100 ticks a healing cross (healing injuries) or a sleep Z (tired) mote. **The bather sits
  up** (standing posture), not face up as in the mod: FlowWorks drowning reads a lying pawn by its lying height
  (`RM_Drowning.Lying`), so a lying soak would drown pawns in a pool they can stand in. A soak at least half done
  earns the afterglow and the memory.
- **While soaking:** hediff `RM_HotPoolSoak` ("hot pool"): ComfyTemperatureMin −50, ComfyTemperatureMax +50,
  BloodFiltration +0.08, naturalHealingFactor ×1.25 (the mod's "Healing waters", numbers unchanged).
- **After:** hediff `RM_HotPoolAfterglow` ("after the hot pool"): BloodFiltration +0.08, naturalHealingFactor ×1.25,
  severity 0.5 falling 0.4/day (1.25 days); a new soak replaces it (the mod's "Residual rejuvenation").
- **Mood [Q3, owner by card]:** also vanilla Odyssey's own `HotSpring` thought (+2 for 0.1 day) when a soak ends, so it
  reads in the mood list like a real hot spring, its strength scaled by `geyserPoolMoodFactor` (x1–x3, the memory's
  `moodPowerFactor`). Every DLC is assumed, so the def is always there.
- **Clothes:** set aside while soaking, look only (the mod's two render postfixes, our own), never in portraits; no
  nudity thought.
- **Capped vent [Q2, owner by card]:** a geothermal generator on the geyser stops the sprayer in vanilla (`harvester`
  set), so it also stops the plume and the tub. A generator may be built on a **dry** sunk geyser (the `Heavy`
  affordance waived on the geyser's own footprint: the vent is bedrock); it is refused while liquid stands over the
  seat. Liquid later poured over a capped geyser just sits there: no plume, no tub. So it is power or a tub, never both.
- **Ascetic and other ideoligion quirks:** none added; vanilla precepts that read joy kinds see Meditative.

### 3.5 Mod Settings (FlowWorks, screen "Geysers in pits", `RM_GeyserPitSettings`)

| setting | default | off means |
|---|---|---|
| `geyserSinksEnabled`: "A geyser sinks with the pit dug on it" (master) | on | today's behaviour: the geyser stays at the surface, puffs through liquid, no plume, no tub |
| `geyserPlumeEnabled`: "A sunk geyser bubbles through liquid over it" | on | covered geysers neither puff nor bubble |
| `geyserPlumeDensity` slider x0.2–x3 | x1 | |
| `geyserPoolEnabled`: "Pawns soak in a bubbling geyser pool" | on | bubbles only, no job, no hediffs |
| `geyserPoolReach` 1.5–4.5 cells | 2.5 | |
| `geyserPoolHealing` x1.0–x2.0 natural healing | x1.25 | x1.0 keeps the joy and comfort but no healing |
| `geyserPoolAfterglowEnabled` | on | no after-soak hediff |
| `geyserPoolMoodEnabled` (vanilla `HotSpring` thought) | on | no mood memory |
| `geyserPoolMoodFactor` x1–x3 (the memory's strength) | x1 | |
| `geyserPoolHidesClothes` | on | bathers stay drawn clothed |
| `geyserBathTarEnabled` / `geyserBathOilEnabled` / `geyserBathBloodEnabled` / `geyserBathSlimeEnabled` | on | that liquid bubbles but is no pool (water always is) |
| `geyserBathFilthEnabled` (filth cost) | on | strange baths leave no filth |
| `geyserBathMoodCostEnabled` (tar and blood memories) | on | no bad memory |
| `geyserBathSlipEnabled` (slime slip) | on | no slip climbing out of slime |
| `geyserGeneratorOnSunkEnabled` | on | a sunk geyser takes no generator (vanilla's Heavy affordance refuses the dug floor) |

Defaults are the shipped behaviour; all off is today's game. None affects worldgen. Each is scribed, reset by
`RM_SettingsReset` (the screen's Reset button) and found by the settings search (`Block(list, "Geysers in pits", ...)`).

### 3.6 Rejected routes (recorded so nobody retries them)

- **Turning the cells over the geyser into vanilla `HotSpring` terrain.** FlowWorks owns a dug cell's terrain through
  its ladder and volume accounting; writing a foreign terrain there breaks both, and `HotSpring` gives only +2 mood.
- **Depending on Standalone Hot Spring** or spawning its 8x4 building: an 8x4 stone building does not belong at the
  bottom of a pit under water, and the ruling says *like* the mod.
- **Marking the pool `RM_HotLiquid`:** that is the scald path; a tub must not burn.

## 4. Acceptance tests

Both offline tests were watched failing on the base (origin/main e6c3749f36, 2026-11-12 evening): the C# SelfTest does
not build without `RM_GeyserTubMath.cs`, and the Python check stops on the missing source files; both are green on the
build [measured].

### 4.1 Offline (no game)

**O1, C#: `SelfTest/GeyserTubChecks.cs`**, registered in `SelfTest/Program.cs`, compiling the Verse-free
`Superdeep/RM_GeyserTubMath.cs` through `RimMandrakeFlowWorks.SelfTest.csproj`: 9 cases, 44 assertions (seat = the
shallowest cell, 7; covered past 0.4 m, 4; the pool gate, 5; reach, 2; afterglow 1.25 days, 1; plume rates and sizes,
8; bubbles per tick average the rate, 2; bath groups follow their settings, 6; heat only through the water over the
vent, 9).
Run: `python3 src/RimMandrake/Utils/selftest_flowworks_stock.py --only 'GeyserTub_*'` (9/9).

**O2, Python: `src/RimMandrake/FlowWorks/selftest_flowworks_geyser_tub.py`**: 15 checks over the shipped defs and the
comment-blanked C# (its docstring lists them: the hediffs, job and joy giver numbers; the 18 settings declared, scribed,
drawn and registered; no Standalone Hot Spring name or dependency; the spawn, sprayer and puff patches gated by the
master; the heat push never skipped; `bathGroup` default None and exactly water, tar, oil, blood and the four slimes
bathing, gated through `PoolSafe`; no `RM_HotLiquid`; the under-liquid geyser row at 0.4 m; no map scan in the tick;
each strange bath's cost and its defs; the bather never lies down; the generator waiver dry-only and on the vent's own squares), and 21 named mutants of the real text, each of which
must turn a check red. Run: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_flowworks_geyser_tub.py`.

### 4.2 Live state reads (quicktest map, bridge; `RimMandrake.FlowWorks.RM_GeyserPoolProof.Read "<geyserThingID>"`
by `jawa/static_call`, `"reset"` zeroes the counters) — NOT RUN; the staging and what right looks like:
`D:\ClaudeWork\rimmandrake\conductor\underliquid_20261112_evening\geyser_build\LIVE_LOOK_CHECKLIST.md`

The proof returns: `spawned`, `thingId`, `seatNotches`, `vent` (the anchor of print, puffs, plume and heated water: x,z), `heated` (squares of heated water), `levelMetres`, `covered`,
`fluid`, `bathable`, `pool`, `spraying`, `plumeBubbles`, `dryPuffs` and `coveredPuffsStopped` (counters since reset),
`soakers`, `capped`.

| # | stage | pass reads | today |
|---|---|---|---|
| L1 | spawn a SteamGeyser on open soil; dig its four cells and two rows south of it to 2 m | same `thingId`, `spawned` true, `seatNotches` 4, `vent` the footprint's centre, `dryPuffs` rising | proof absent; geyser drawn at the surface |
| L2 | dig only three cells | `seatNotches` 0, `heated` 0 | — |
| L3 | fill the 2 m pit with fresh water to 1 m | `covered` true, `fluid` Water; over 5000 ticks `plumeBubbles` > 0 and `dryPuffs` 0 | water throws no bubbles; puffs rise through it |
| L4 | a colonist with joy 0.2 ordered "Soak in the hot pool" | within 3000 ticks has `RM_HotPoolSoak`, ComfyTemperatureMax raised by 50; after the soak: `RM_HotPoolAfterglow` at 0.5, joy higher than at start, the `HotSpring` thought present [Q3] | no such job |
| L5 | drain; refill with acid water | `plumeBubbles` > 0 in acid's colour; `bathable` false; no soak job given, no float-menu option | — |
| L5b | one pit each of tar, oil, blood and a slime | `bathable` true, `pool` true; a soak ends with that liquid's cost (spec 3.4 table) | — |
| L6 | drain dry; place a geothermal generator [Q2] | allowed dry; `capped` true; then fill: `plumeBubbles` 0, no soak job | generator refused on a dug cell [guess ~70%] |
| L7 | save, reload | same `seatNotches`, `vent`, `heated`; no new errors in `Player.log` | — |
| L8 | `geyserSinksEnabled` off | `heated` 0, `plumeBubbles` 0, no soak job (today's game) | — |

L1–L8 run as one `stage_proof_site.py`-style sitting on the minimal list (all five DLC). No flyer is involved. The
bubbles' look (tint, size, the wisp) is judged once by an Opus art judge from a zoomed capture, not by the maker.

## 5. Build order (for Relentless)

1–5 built offline on 2026-11-12 evening (math + O1, seat/print/puffs and the under-liquid row, plume and puff
suppression with the heat kept, pool defs/job/joy giver/float menu/hediffs/clothes/freeze exemption + O2, the generator
rule). Left: 6, the live proof L1–L8 + L5b, then the art judge on the plume, then the real plume art.
