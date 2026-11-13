# A geyser in a pit: it sinks, it bubbles, it is a hot tub

Item: `RIMMANDRAKE_SINK_GEYSER_INTO_PIT_BUBBLING_HOT_TUB` · mod: FlowWorks (`mandrake.rimmandrake.flowworks`) · written
2026-11-12 19:00 PST by a detached BENCH helper of the Conductor · status: DESIGN, nothing built.
Open owner choices: `D:\ClaudeWork\rimmandrake\conductor\underliquid_20261112_evening\geyser\QUESTIONS.md`
(three; this spec carries the recommended answer for each, marked **[Q1]**, **[Q2]**, **[Q3]**, so it can be built
as written if he accepts the recommendations).

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
- **Drawn** at the seat: the print is lowered by the same sink pawns use (`pitSinkPerLevel` × seat notches) and kept
  inside the pit's outline (the lip occlusion pawns get). Harmony on `Building_SteamGeyser`'s print (it is a
  `Graphic_Single` map-mesh thing), and the map mesh is dirtied for its 2x2 when any of its cells' depth changes.
- **Under liquid** by `RM_UnderLiquid`: a thing standing on the floor, `GeyserMetres = 0.4` (a low vent mound).
  `Share(level, 0, 0.4)` of it is under; the drowned part draws at `Seen(clarity, metresOver)`: tinted in clear water,
  hidden in an opaque liquid (tar, oil, blood). Added to `SubmergeDrawChecks`' caller table.
- **Its puffs** rise from the seat while it is dry (the puff origin lowered by the same sink), so steam visibly comes
  out of the bottom of the pit.
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
- **Cost:** the plume is emitted only while the geyser's cells are in view (the same in-view rule as
  `RM_LiquidSurface.Bubbles`), from a per-map list of sunk geysers (rebuilt on spawn and on depth change, never a map
  scan per tick). Cosmetic RNG isolated (`Rand.PushState`), as the existing emitter does.

### 3.3 Heat

- **One kind of heat.** The geyser keeps its vanilla `PushHeat(40)` every 20 ticks while spraying, dry or covered.
  An open pit is outdoors, so it warms nothing (vanilla: an outdoor room takes no heat); a roofed pit room **cooks**,
  exactly as vanilla says of any room over a geyser. That is the trade of a roofed bathhouse; the soak hediff's
  ComfyTemperatureMax +50 is what makes the soak bearable in it, as in the mod.
- **The liquid is not made hot.** No `RM_HotLiquid` patch, no scald, no change of FluidDef. Water over a geyser stays
  water. Boiling water poured in is still boiling water and still burns through its own terrain (SCALD rule: no
  burn immunity for free).
- **It does not freeze:** the footprint and the tub reach never freeze while the geyser is uncovered by a generator,
  like vanilla's `HotSpring` (`canFreeze false`). The builder finds FlowWorks' pit-water freeze path
  (`RM_WaterBodyFreeze*`, the freeze selftests) and adds the exemption there; no new freezing rule.

### 3.4 The hot tub

- **Where:** liquid cells within `hotTubReach` (default 2.5 cells) of the geyser's centre, i.e. the 2x2 footprint and
  the ring around it, while the geyser is covered and uncapped. The bubbles are the sign; nothing else is built.
- **Which liquids [Q1, recommended]:** a positive flag on the liquid, `FluidDef.bathable` (default false), set only
  on plain water (`RM_Fluid_Water`, the freshwater ladder rain and rivers fill pits with). Every other shipped FluidDef
  (acid water, poison, reaction liquor, boiling water, icy water, tar, oil, chemfuel, propane, astrofuel, blood and
  the four slimes) **bubbles but is not a tub**; a new liquid opts in by its own def. Not read from terrain harm: the
  fill terrains of tar, oil, chemfuel, propane, astrofuel, blood and the slimes carry no `dangerous`,
  `toxicBuildupFactor` or `burnDamage` (their harm is fire, slip or poison-per-day), so a terrain gate would make a
  tar pit a spa [measured, 16 FluidDefs' brim terrains, 2026-11-12]. Icy water is excluded too: the geyser does not
  heat the liquid (3.3), so it stays a cold plunge.
- **Who:** any pawn with a joy need (colonists, slaves, guests), as recreation; prisoners soak but gain no joy (as the
  mod); a player-faction humanlike can be ordered in ("Soak in the hot pool"), which is how a sick pawn is sent. Not
  downed pawns, not animals, not a pawn who cannot reach the cell. Up to 6 at once per geyser (the mod's
  `joyMaxParticipants`).
- **Getting in:** ordinary FlowWorks pathing into the pit (a ramp, a ladder or a shallow side). A pit no pawn can
  enter is a tub nobody uses; that is the player's build, not a defect. In liquid deeper than wading the pawn soaks
  swimming, head up (`RM_Swim`), so a deep pool works; a pawn that cannot swim there is not given the job.
- **The job** `RM_SoakInGeyserPool` (`JoyGiverDef` + `JobDef`, Meditative, joyDuration 4000, baseChance 5): go to a free
  cell in reach, soak 3000 ticks, every tick comfort from the cell, rest at 1.111, joy at the mod's rate with
  JoyGainFactor 1.4; sleep Z and healing-cross motes every 100 ticks as the mod does.
- **While soaking:** hediff `RM_HotPoolSoak` ("hot pool"): ComfyTemperatureMin −50, ComfyTemperatureMax +50,
  BloodFiltration +0.08, naturalHealingFactor ×1.25 (the mod's "Healing waters", numbers unchanged).
- **After:** hediff `RM_HotPoolAfterglow` ("after the hot pool"): BloodFiltration +0.08, naturalHealingFactor ×1.25,
  severity 0.5 falling 0.4/day (1.25 days); a new soak replaces it (the mod's "Residual rejuvenation").
- **Mood [Q3, recommended]:** also vanilla Odyssey's own `HotSpring` thought (+2 for 0.1 day) when a soak ends, so it
  reads in the mood list like a real hot spring. Every DLC is assumed, so the def is always there.
- **Clothes:** set aside while soaking, look only (the mod's two render postfixes, our own), never in portraits; no
  nudity thought.
- **Capped vent [Q2, recommended]:** a geothermal generator on the geyser stops the sprayer in vanilla (`harvester`
  set), so it also stops the plume and the tub. A generator may be built on a **dry** sunk geyser (the `Heavy`
  affordance waived on the geyser's own footprint: the vent is bedrock); it is refused while liquid stands over the
  seat. Liquid later poured over a capped geyser just sits there: no plume, no tub. So it is power or a tub, never both.
- **Ascetic and other ideoligion quirks:** none added; vanilla precepts that read joy kinds see Meditative.

### 3.5 Mod Settings (FlowWorks, new section "Geysers in pits")

| setting | default | off means |
|---|---|---|
| `geyserSinksEnabled`: "A geyser sinks with the pit dug on it" (master) | on | today's behaviour: the geyser stays at the surface, no plume, no tub |
| `geyserPlumeEnabled`: "A sunk geyser bubbles through liquid over it" | on | covered geysers neither puff nor bubble |
| `geyserPlumeDensity` slider x0.2–x3 | x1 | |
| `geyserPoolEnabled`: "Pawns soak in a bubbling geyser pool" | on | bubbles only, no job, no hediffs |
| `geyserPoolReach` 1.5–4.5 cells | 2.5 | |
| `geyserPoolHealing` x1.0–x2.0 natural healing | x1.25 | x1.0 keeps the joy and comfort but no healing |
| `geyserPoolAfterglowEnabled` | on | no after-soak hediff |
| `geyserPoolMoodEnabled` (vanilla `HotSpring` thought) | on | no mood memory |
| `geyserPoolHidesClothes` | on | bathers stay drawn clothed |

Defaults are the shipped behaviour; all off is today's game. None affects worldgen. Each is scribed, reset by
`RM_SettingsReset`, and indexed by `RM_SettingsSearchIndex` (the FlowWorks settings pattern).

### 3.6 Rejected routes (recorded so nobody retries them)

- **Turning the cells over the geyser into vanilla `HotSpring` terrain.** FlowWorks owns a dug cell's terrain through
  its ladder and volume accounting; writing a foreign terrain there breaks both, and `HotSpring` gives only +2 mood.
- **Depending on Standalone Hot Spring** or spawning its 8x4 building: an 8x4 stone building does not belong at the
  bottom of a pit under water, and the ruling says *like* the mod.
- **Marking the pool `RM_HotLiquid`:** that is the scald path; a tub must not burn.

## 4. Acceptance tests

Each one fails on today's code (origin/main at c11e9e9d0e): the classes, defs, settings and proof do not exist, and
the behaviour each reads is today's opposite (geyser drawn at the surface, puffs out of liquid, no bubbles over plain
water, no soak job). Watched failing at filing: `test -f src/RimMandrake/FlowWorks/Source/Superdeep/RM_GeyserTubMath.cs`
exits 1 and `grep -rl "RM_HotPoolSoak" src/RimMandrake/FlowWorks` finds nothing [measured 2026-11-12 19:05 PST].

### 4.1 Offline (no game)

**O1, C#: `SelfTest/GeyserTubChecks.cs`**, registered in `SelfTest/Program.cs`, compiling the Verse-free
`Superdeep/RM_GeyserTubMath.cs` through the existing `RimMandrakeFlowWorks.SelfTest.csproj`. Expected 24 cases:

- `SeatNotches(int[] depths)`: {4,4,4,4}→4 · {4,4,4,2}→2 · {0,4,4,4}→0 · {}→0 · null→0 · {−1,4,4,4}→0 · {16,16,16,16}→16
  (7 cases; a mutant using the deepest cell must fail {4,4,4,2}).
- `Covered(levelMetresOverSeat)`: 0→false · 0.39→false · 0.41→true · 2.0→true (4).
- `PoolSafe(bathable, covered, capped)`: true only for (true, true, false); false for each of not bathable, not
  covered, capped alone; false for a null fluid (5).
- `InReach(dx, dz, reach)` from the 2x2 centre: (0.5,0.5,2.5)→true · (2.5,0.5,2.5)→false at 2.5 exclusive (2)
- `AfterglowDays(0.5, 0.4)` = 1.25 ± 1e−4 (1).
- `PlumeRate`: covered-spraying > covered-between > 0 for every viscosity; thick (`ticksPerTile` ≥ 120) gives fewer
  but larger bubbles than thin; density x0 gives 0 (5).

**O2, Python: `src/RimMandrake/FlowWorks/selftest_flowworks_geyser_tub.py`** (reads defs and comment-blanked source,
with named mutants that must go red, in the shape of `selftest_flowworks_hot_wet_terrain.py`). Expected 12 checks:

1. `HediffDef RM_HotPoolSoak` exists with ComfyTemperatureMin −50, ComfyTemperatureMax 50, BloodFiltration +0.08,
   naturalHealingFactor 1.25.
2. `HediffDef RM_HotPoolAfterglow`: maxSeverity 0.5, `HediffCompProperties_SeverityPerDay` −0.4, same healing.
3. `JobDef RM_SoakInGeyserPool`: joyKind Meditative, joyDuration 4000, joyMaxParticipants 6.
4. `JoyGiverDef RM_SoakInGeyserPool`: baseChance 5, joyKind Meditative, giverClass in `RimMandrake.FlowWorks`.
5. The nine settings of 3.5 are declared, scribed with the listed defaults, and named in a settings section.
6. No file under `src\RimMandrake\FlowWorks` names `StandaloneHotSpring`, `balistafreak` or `BathStandaloneHotSpring`,
   and `About.xml` has no new dependency.
7. A Harmony patch targets `Building_SteamGeyser` (print) and `IntermittentSteamSprayer.SteamSprayerTick` (or
   `Building_SteamGeyser.Tick`), each gated by `geyserSinksEnabled`.
8. The puff suppression keeps `GenTemperature.PushHeat` (the heat call is not skipped when covered).
9. `FluidDef` has `bathable` defaulting false; exactly `RM_Fluid_Water` sets it true; the pool gate calls
   `RM_GeyserTubMath.PoolSafe` with the cell fluid's `bathable` (mutants: default true, or tar set true, go red).
10. `RM_HotLiquid` is not called from the geyser code.
11. `SubmergeDrawChecks` has a geyser row (`GeyserMetres` 0.4).
12. The sunk-geyser list is rebuilt on depth change, not scanned per tick (no `AllThings`/`listerThings` call inside a
    tick method of the new map component).

Run: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_flowworks_geyser_tub.py` plus the FlowWorks C#
selftest lane. Pass = 24 + 12.

### 4.2 Live state reads (quicktest map, bridge; a proof `RM_GeyserPoolProof.Read <geyserThingID>` in
`RM_NorthstarProofs`, read by `jawa/static_call`)

The proof returns: `spawned`, `thingId`, `seatNotches`, `drawDz` (the patched print's z minus the cell centre),
`covered`, `fluid`, `plumeBubbles` and `dryPuffs` (counters since reset), `soakers`, `capped`.

| # | stage | pass reads | today |
|---|---|---|---|
| L1 | spawn a SteamGeyser on open soil; dig its four cells to 2 m | same `thingId`, `spawned` true, `seatNotches` 4, `drawDz` < 0, puff origin below the surface | proof absent; geyser drawn at the surface |
| L2 | dig only three cells | `seatNotches` 0, `drawDz` 0 | — |
| L3 | fill the 2 m pit with fresh water to 1 m | `covered` true, `fluid` Water; over 5000 ticks `plumeBubbles` > 0 and `dryPuffs` 0 | water throws no bubbles; puffs rise through it |
| L4 | a colonist with joy 0.2 ordered "Soak in the hot pool" | within 3000 ticks has `RM_HotPoolSoak`, ComfyTemperatureMax raised by 50; after the soak: `RM_HotPoolAfterglow` at 0.5, joy higher than at start, the `HotSpring` thought present [Q3] | no such job |
| L5 | drain; refill with acid water | `plumeBubbles` > 0 in acid's colour; no soak job given, no float-menu option | — |
| L6 | drain dry; place a geothermal generator [Q2] | allowed dry; `capped` true; then fill: `plumeBubbles` 0, no soak job | generator refused on a dug cell [guess ~70%] |
| L7 | save, reload | same `seatNotches`, `drawDz`; no new errors in `Player.log` | — |
| L8 | `geyserSinksEnabled` off | `drawDz` 0, `plumeBubbles` 0, no soak job (today's game) | — |

L1–L8 run as one `stage_proof_site.py`-style sitting on the minimal list (all five DLC). No flyer is involved. The
bubbles' look (tint, size, the wisp) is judged once by an Opus art judge from a zoomed capture, not by the maker.

## 5. Build order (for Relentless)

1. `RM_GeyserTubMath` + O1 (Verse-free; red first).
2. Seat depth, sunk print and sunk puffs + the `SubmergeDrawChecks` row; settings master.
3. Plume emitter + puff suppression (heat kept).
4. Pool: defs, job driver, joy giver, float menu, hediffs, clothes postfixes, freeze exemption; O2.
5. Generator rule [Q2].
6. Live proof L1–L8, then the art judge on the plume.
