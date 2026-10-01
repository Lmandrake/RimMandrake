# Warscar — volley turn 3: developing what the owner ruled

**Item:** `WARSCAR_BEDAZZLE_SITTING_1` · BENCH design agent · 2026-09-30
**Reads:** `warscar_bedazzle_review_2026-09-30.md` (turn 1), the three turn-2 ledger notes,
`stillsand_turn3_development_2026-09-30.md` (shape), `BAROQUE_BEDAZZLE_PROGRAM_1`.

## 0. The owner's words

Volley turn 2, by question card, recorded as three ledger notes on `WARSCAR_BEDAZZLE_SITTING_1`
(2026-09-30 18:48, 20:02 and 20:08 PDT). These are decisions taken by card, not typed quotes, so
none of them is put in quotation marks below. Nothing here re-argues any of them.

- **IN:** the Settling · the projectors / aerosol screen · the totchak wakes · the Geiger choir · the
  chatrak's snap · the mark as a trade · the hospice · the old tongue · the rainbow pools · the
  pilgrim camps.
- **OUT:** glower black uses · the Watch ritual. The Sentinel-acknowledgement card is therefore moot,
  and the Sentinels stay as built: defend-only, acknowledging no one.
- **Refinements:** the Settling's tracks **persist and fade at the next wind** · the aerosol screen
  works in **every polluted biome** · the woken totchak eats **ruins AND player walls** · the
  **hospice is built before the rainbow pools**.
- **Roster:** the names chatrak / totchak / tetchik are **kept** · **wreck-lichen is added**, and the
  scorched stars **stay for now** · the pallbearer (`RUT_MortuaryCrawler`) and the scar roach **move to
  the free RM Warscar tier** · the fertile Soil band is **dropped** · the label is **"Warscar"**, with
  no article.

**Second card, 2026-09-30 20:22 PDT**, on the GPT consult
(`Transient/bedazzle_gpt_enrich_2026-09-30/warscar.md`), relayed by BENCH and folded in below:

- **Adopted:** (1) **the tech chain ties together**: the old tongue unlocks specific steps (hospice
  repair protocols, projector calibration, a pool phase reader), and pool reagents feed them (a
  **dielectric gel** for the screen's membranes, an **etchant** for machine repair, a **medical
  coagulant**). (2) **The mark reveals sealed caches behind a loosened panel** in the ruins: the panel is
  always visible, the cache never appears from nothing, and marks do not stack. (3) **A wreck-eater food
  web**: the chatrak rasps wreck-lichen off wrecks, the pallbearer eats corpses, the scar roach cleans
  residue, and the tetchik lives in the glower crust. (4) **Settling footprints live on a capped grid,
  not as filth objects**, with recent humans and large animals kept first. (5) **Machine repair is
  staged over days**: lights, then twitching limbs, then voice fragments. A failure leaves a
  recognisable dead wreck.
- **Rejected:** narrowing the aerosol screen. The owner, typed: *"I like powerful tech. Don't be afraid
  of making good ideas broadly useful and powerful (like the aerosol shield). There are many other ways
  to normalize it."* ⇒ the screen stays **strong and broad**, balanced by cost, power, materials and
  research, never by scope. The same principle applies to every tech in this package.
- **The hospice machines**, typed: *"Those droids should be INTERESTING cases... they all left their
  owner, ran away, then died a slow death. That's gotta leave some strange features inside."* ⇒ every
  intact chassis is a **deserter with a history** (§2.7).

Standing law carried in: the biome's own admission test from turn 1 (*every new thing is something
the war left, or something that eats what the war left*); the planet-wide rule that **no animal or
pawn vanishes without a readable sign**; every mod ships Mod Settings; and every DLC is assumed.

One consequence of the OUT list matters below. With the Watch gone, **mark 9 (the gods) on the free
tier now rests on the old tongue and the hospice**, and on the campaign it rests on the pilgrim camps.
§5 checks that the mark still lands.

## 1. The Warscar, one paragraph

You land in a place where everyone already lost. Grey ground runs to a grey sky in long stepped
terraces of slag, and along every rise sits a line of old fortification facing **outward**, toward
nothing you can see. Black varnish crusts every crater lip, and the ground **ticks**: small beetles
in the crust click faster where it runs hot, so you can hear where not to stand. Rust-orange lichen
grows on the wrecks and nowhere else, and low plated grazers walk straight through a firefight to
scrape it off a hull. Then the wind drops. The barrels on the line stop keening, the ticking carries
farther in the hush, and a fine pale fall begins to come straight down. It is the war, still hanging
in the air after all this time. By morning every unroofed surface wears a film, and **the film keeps
footprints**. You can read where the raiders came in, where your hauler went, where the grazer
circled before it charged. It stays like that until the wind comes back and lifts the page clean.
On the ridge one ring of projectors is still humming, and under it the film stops in a perfect circle.
Inside the line, chassis kneel facing the Cathedral, every panel is written in a script nobody living
reads, and one stretch of the wall is breathing.

## 2. The ruled ideas, developed

Every engine claim below was read from the decompiled 1.6 source through RimSage this pass, or from
our own `src/` on `origin/main`; each says which. "Verify" lists the classes the builder must read
before writing code, not ones already settled.

### 2.0 What we already built that this package stands on

The standing law held again: **five of the ten ruled ideas already have their core mechanism shipped
somewhere in `src/`.** The table is the reuse map for everything below.

| shipped piece | where | what the Warscar uses it for |
|---|---|---|
| **Particulate screen** field mode (`CompShieldParticulateScreen`, `ShieldHazardUtility.HasParticulateHazard`, Harmony prefixes on `ToxicUtility.DoAirbornePawnToxicDamage` and `GameCondition_ToxicFallout.DoCellSteadyEffects`) | `src/RimUtinni/ShipShields/` (RUT tier, module on `RUT_ShieldGenerator`) | **the aerosol screen is already built, on the campaign tier.** §2.2 lifts its core to RM |
| `GameCondition_EnvironmentalWeather` + `EnvironmentalWeatherExtension`, `RM_HediffComp_SeverityFloor` | `src/RimMandrake/EnvironmentalHazards/` (RM) | the mark's accrual and its lifelong floor (§2.6) are already RM-tier classes, used only by the RUT twin |
| `GameCondition_ArmLatentHazard` + `ArmLatentHazardExtension` (`pawnKindFilter`, `requiredHediff`) | same (RM) | the chatrak's snap (§2.5) is XML on these |
| `RM_GnawTargetExtension` + `RM_JobGiver_GnawTargets` + `RM_JobDriver_Gnaw` | `src/RimMandrake/CreatureBehaviors/` (RM) | the totchak's wall-eating (§2.3), with two new fields |
| `RM_ProximitySoundscapeExtension` + `RM_MapComponent_ProximitySoundscape` | same (RM, Greentide) | the Geiger choir (§2.4) |
| `RUT_CompWaterWakeTrigger` (a trigger that calls stock `CompCanBeDormant.WakeUp()`) | `src/RimUtinni/UtinniPatches/Source/` | the shape for the totchak's demolition wake (§2.3) |
| `SectionLayer_DuneSand` (a mod-owned `SectionLayer`) | `src/RimMandrake/MovingDunes/Source/` (RM) | the precedent for the track grid's draw layer (§2.1) |
| `RM_ReactionLiquorShallow` / `…Deep` TerrainDefs (generated, `toxicBuildupFactor 2`, `dangerous`), `LiquidDef` registry | `src/RimMandrake/FlowWorks/` (RM) | the rainbow pools' liquid exists as **terrain**; it has **no `LiquidDef` row** yet (§2.9) |
| WRECKED → KLUDGED → REPAIRED three-state machine | `src/RimMandrake/WreckedMachines/` (RM) | the hospice's wake ladder (§2.7) |
| `RUT_Antiquities` tree (Reading Station, artifact-gated nodes incl. `RUT_Antiq_Language`) | `src/RimUtinni/Antiquities/` (RUT) | the old tongue's campaign half (§2.8) plugs in here, not into a new tree |
| `GameComponent_LoreStage.AdvanceStage(ladderId)` + `RUT_ScarlandsLadder` (5 rungs) | `src/RimMandrake/LoreStages/`, `src/RimUtinni/ScarlandsLadder/` | the pilgrim camps (§2.10) are the missing caller |
| `RM_EatCleanableExtension` | CreatureBehaviors (RM) | the scar roach already runs on it; its tier move (§3) is a file move |

### 2.1 The Settling — the war falls when the wind stops; the film keeps the tracks

**What the player sees.** Calm air is the hazard. When the wind has been low for a few hours, the
sky goes pale and flat, a fine grey-white fall comes straight down (no slant, because there is no
wind), and the ruin barrels stop keening (§2.4). Unroofed ground takes on a **settled film**. Every
pawn, animal and raider that crosses the film afterwards leaves **prints pointing the way they went**.
The prints stay. They do not age out on a timer. They go **only when the wind returns**, and then they
go across the whole map within an hour or so, the film lifting downwind in a visible drift of
particles. A long calm makes a complete record of the map. A gusty week leaves none.

**What the player does with it.** They read it. The prints show:
- where a raid actually came from (the edge it spawned at, before the letter says so);
- where a mad chatrak circled before it charged (§2.5), as a tight loop of heavy prints;
- where a pawn went when it wandered off in a mark break (§2.6);
- where the totchak walked after it woke (§2.3): huge prints a day apart;
- the road anything took to a body. **This is the biome's answer to the readable-sign rule.** In the
  Warscar, a loss during or after a Settling is always legible on the ground.

**Mechanism (1.6).**
- **Detecting calm.** `map.windManager.WindSpeed` (RimSage: `WindManager`, a cached float in
  `0.04–2.0` times the weather's `windSpeedFactor`, plus any condition's `MinWindSpeed()`). An RM
  `MapComponent_Settling` samples it every 250 ticks and keeps a rolling calm-hours counter. Below a
  threshold (proposed 0.35) for N hours (proposed 4), it starts **`RM_Settling`**, a `GameCondition`.
  Above a lift threshold (proposed 0.8) for one hour, it ends.
- **The fall.** `RM_GameCondition_Settling` mirrors vanilla `GameCondition_ToxicFallout` (read in
  full this pass): a `SkyTarget` (pale and low-glow), a `SkyOverlay` (a vertical-fall variant of
  `WeatherOverlay_Fallout`), and airborne toxic damage through **`ToxicUtility.DoAirbornePawnToxicDamage`**,
  which already skips roofed pawns. Routing the damage through that one vanilla call is deliberate:
  it is exactly the call the particulate screen already blocks (§2.2), so the screen works on the
  Settling with no new code. It does **not** kill plants (the glower thrives on it) and it does not
  stop animal spawns, unlike vanilla fallout.
- **The film.** `RM_Filth_SettledFilm`, a terrain-wide film laid by the condition's
  `DoCellSteadyEffects` on unroofed, non-water cells (a light density cap so it reads as a sheen, not a
  carpet). It is a plain `Filth`; cleaning it inside the base works as usual.
- **The tracks: a capped grid, not filth objects** (ruled). `MapComponent_Settling` owns a
  **`TrackGrid`**: one compact record per cell (direction in 3 bits, size class in 2, a source class in
  2, and the tick it was laid), held in a **fixed-capacity pool** (proposed 6,000 records per map) with
  a cell→slot index. A Harmony postfix on **`Pawn_FilthTracker.Notify_EnteredNewCell`** (RimSage: the
  vanilla per-cell hook that already drops terrain filth) writes a record when the pawn is on filmed
  ground. When the pool is full, eviction is **by priority, then age**: small animals go first,
  then old records, and **recent humanlikes and large animals (body size ≥ 1.5) are kept** (ruled).
  Drawing is one custom **`SectionLayer`** that prints a rotated print sprite per record in a
  section, rebuilt only for sections that changed. MovingDunes' `SectionLayer_DuneSand` is the
  shipped precedent for a mod section layer. The grid is saved with `Scribe` as packed arrays,
  never per-thing. No `Thing` is ever spawned for a print, so pathing, hauling and the thing lists
  never see them.
- **The fade.** The film is the only filth (`disappearsInDays` long enough never to fire on its own).
  When the wind lifts, `MapComponent_Settling` clears film and track records in **downwind-sweeping
  batches** (a few hundred cells per tick-slice) with a dust fleck per batch. This is the visible "page
  wiped" moment.
- 🔑 **Shared kit.** The Stillsand turn 3 (§3.2) ruled tracks for the same reason, with the dunes engine
  as its eraser. The **`TrackGrid` + its section layer + the postfix** is one **CreatureBehaviors** kit,
  with a `RM_TrackSurfaceExtension` on whatever bears prints (the film here, sand there). Each biome
  supplies only its **surface** and its **eraser**. Whichever biome builds first owns the kit, and the
  second gets it as XML. The Stillsand doc proposed filth tracks; this ruling moves both to the grid.

**Verify:** `Pawn_FilthTracker.Notify_EnteredNewCell` (it is gated on `pawn.RaceProps` filth flags,
so animals and mechs need a separate check that they reach it); `SectionLayer` registration and
`MapDrawer.MapMeshDirty` for a custom layer; `GameCondition.
DoCellSteadyEffects` call cadence; `WeatherOverlay_Fallout` (to subclass for the vertical fall);
`FilthMaker.TryMakeFilth` (stacking rules).

**Readable sign.** The tracks themselves. A Settling start sends a message (*"The wind has dropped.
The Settling begins."*), and its end sends another (*"The wind is back. The ground forgets."*).

**Performance guard.** The grid's fixed pool is the cap. One record per cell, newest replacing
oldest. The film has its own density cap, and cleaning jobs ignore film outside the home area.

**Build:** medium–large C# (MapComponent, condition, the track grid with its section layer and save
data, one postfix), about 500 lines, plus XML.
**Tier:** RM (`mandrake.rm.warscar`; the track kit goes to CreatureBehaviors).
**Settings:** Settling on/off · calm threshold and hours · tracks on/off (the condition still runs
without them) · track cap · toxic strength. The tracks toggle is labelled as the performance switch.
**Marks:** 8 (weather), and 7 by its silence.

### 2.2 The projectors still hum, and the aerosol screen you learn from them

**What the player sees.** Rings of dead emitter pylons stand along the approaches, slumped, barrels
pointing outward. One or two per map **still hum**. In a Settling, the film stops at the edge of a
humming ring's dome in a crisp circle, which you can see from full zoom-out. It does not stop bullets.
It screens fallout only.

**What the player does.** Studies a humming ring, learns the **aerosol screen**, and builds one. It is
a low pylon with a soft dome: inside it, no airborne toxic damage, no film and no fallout effects on
crops or items. It is **gravship-buildable**, so it flies with you. Ruled: it works in **every polluted
biome**, which is the reason to land here.

**How "polluted" is detected.** One RM helper, `RM_PollutionSense.IsPollutedHere(Map)`, true when
**any** of these holds:

1. **The tile is polluted.** Biotech's world pollution: `Find.WorldGrid[map.Tile].PollutionLevel() >=
   PollutionLevel.Light`, i.e. tile pollution ≥ 0.25 (RimSage: `PollutionUtility.PollutionLevel`, with
   thresholds 0.25 / 0.5 / 0.75). The map's own `PollutionGrid` writes that value back
   (`Find.WorldGrid[map.Tile].pollution = TotalPollutionPercent`), so a map you polluted yourself
   counts too.
2. **The air is toxic right now.** Any active condition or weather that calls
   `ToxicUtility.DoAirbornePawnToxicDamage`. RimSage shows exactly **two** callers in vanilla:
   `GameCondition_ToxicFallout` and `WeatherWorker` (weather with toxic exposure, e.g. `ToxRain`). The
   Settling joins them by design (§2.1).
3. **The biome says so.** A new `RM_PollutedBiomeExtension` on a BiomeDef: the Warscar, Wasteland,
   Cauldron and Contagion carry it. It covers biomes whose hazard is ours (the Wasteland's ash fall,
   the Settling) and would otherwise read clean on a fresh tile.

ShipShields already has a narrower test, `ShieldHazardUtility.HasParticulateHazard` (toxic fallout
**or** any weather with `sandRate > 0`). The RM helper is a superset of its toxic half, and the RUT
module should call it, so the two never disagree.

**What the screen blocks: broad, by ruling.** The owner rejected narrowing it (§0). Inside the dome,
the aerosol screen stops:
- **all airborne toxic exposure**: the two vanilla callers above, and the Settling;
- **toxic fallout's cell effects** (crop kill, item rot), which ShipShields already blocks;
- **settling and ash**: no Settling film, and no Wasteland ash-fall pollution writes (a one-line
  in-radius check in `RM_MapComponent_WastelandStorms`' fall loop, line ~158);
- **noxious haze effects** for pawns under it (Biotech `GameCondition_NoxiousHaze`, read this pass:
  its effects are sky, plant growth and animal density, so the screen negates its outdoor-mood
  penalty and plant-growth factor in radius);
- **with calibration (§2.8), toxic gas**: it scrubs `GasType.ToxGas` in radius each interval, so
  the Cauldron's poison gas and tox-gas grenades are cleared too;
- **with calibration, polluted ground**: it slowly un-pollutes cells in radius
  (`pollutionGrid.SetPolluted(c, false)`, the same call `RM_CompProcessorGatherable` already uses).

It never stops bullets, heat or cold. Those belong to other shields.

**How it is balanced, by cost rather than scope:**
- **Power:** 400 W base, 900 W calibrated.
- **Membranes:** a `CompRefuelable` that burns **dielectric gel** (§2.9), about one unit per 3 days
  running. Without gel it runs at half radius. This is the pools' first customer and the reason to
  come back.
- **Materials:** plasteel, components and one **projector core** salvaged from a dead ring (each map
  holds a few). It is a prize you carry out, not a bench recipe, until late research lets you fabricate
  cores.
- **Research:** the screen needs the analysed live ring; calibration needs the old tongue's
  projector-calibration reading (§2.8).

**Mechanism.**
- **Free tier: lift the core, not the generator.** `RUT_ShieldGenerator` is a multi-mode campaign
  building (bubble, thermal veil, cryo envelope, particulate screen). The particulate mode's **effect**
  (the `DoAirbornePawnToxicDamage` and `DoCellSteadyEffects` prefixes and the in-radius test) moves
  down into an RM comp, **`RM_CompAerosolScreen`**, inside a new small RM assembly or EnvironmentalHazards.
  The RUT module then **calls the RM comp** rather than owning the patch. That leaves one patch, two
  consumers, and no franchise in the free tier.
- **The RM building:** `RM_AerosolScreen`, power 250 W, radius 7.9, `CompPowerTrader`,
  `CompFlickable`, placeable on a gravship (substructure-legal), plus a dome drawn with the
  `CompProjectileInterceptor` bubble material **as a visual only**. ⛔ It must not subclass the
  interceptor: projectiles must pass.
- **The humming ring:** `RM_WarscarProjector` (an inert dead variant and a live variant), scattered
  by a genstep along the Odyssey `AncientRuins_Scarlands` layout's outer edge. The live variant carries
  the same `RM_CompAerosolScreen`, self-powered and unclaimable. To teach it: Biotech's
  **`CompProperties_CompAnalyzableUnlockResearch`** (RimSage: the vanilla mech-chip pattern) on the live
  ring, and `ResearchProjectDef.requiredAnalyzed` on `RM_Research_AerosolScreen`. Study the ring, then
  research the screen. Analyzing does not destroy it: the ring keeps humming.
- **The ship row:** `BIOME_SHIP_CONTRIBUTIONS_1` gets its Warscar row, *the aerosol screen*.

**Verify:** `CompAnalyzableUnlockResearch` (whether it consumes the thing on analysis; the mech chips
are consumed, and the ring must not be); `GasGrid` (the toxic-gas scrub); `NoxiousHaze` effect hooks; `ResearchProjectDef.requiredAnalyzed`; the ShipShields
prefixes (to lift them unchanged); `WeatherWorker` line ~97 (which weathers count); gravship
placement rules for a powered building.

**Readable sign.** The film's hard edge at the dome. A screened pawn's toxic buildup stops climbing,
shown by an inspect line ("screened") on the pawn.

**Build:** medium C# (the lift is a refactor of working code, about 150 lines moved; plus the
detector, the gas and ground scrub, and the refuel gate), plus XML for two buildings, the research and the genstep. **Tier:** RM screen and
projectors, and the RUT module rewired to call it. **Settings:** screen radius · power draw · gel
burn rate · calibration (gas and ground scrub) on/off · humming rings per map (0–3).
**Marks:** 2 (tech), 6 (ship), and 3 (the ring is the only place to learn it).

### 2.3 The totchak — the embankment that breathes, and eats your wall

**What the player sees.** One stretch of the Last Line (`AncientFortifiedWall`, Odyssey) has a slag
hump that **rises and falls** every few seconds. It is a colossal animal (body size ~14), dormant and
crusted until it reads as fortification. Mining, deconstructing or blasting near it wakes it. It
stands up and the wall has a **breach** where it lay. Then it walks to the nearest wall and **eats it**:
ruins first, but ruled, **player walls too**. It grazes a wall for a day or two, leaving bitten
segments, and lies down somewhere new, sometimes as part of your perimeter.

**Mechanism.**
- **Dormancy.** Stock `CompCanBeDormant` + `CompWakeUpDormant` (RimSage). The stock wake already
  covers two of the ruled triggers: `wakeUpOnDamage`, and **`wakeUpOnThingConstructedRadius`**, which
  wakes it when the player **builds** a building near it (it scans `BuildingArtificial` of the player
  faction within the radius). Building against the line wakes it, which is fair and readable.
- **The demolition wake** (`RM_CompDemolitionWake`, on the `RUT_CompWaterWakeTrigger` shape, calling
  `CompCanBeDormant.WakeUp()`): Harmony postfixes on `Mineable.DestroyMined(Pawn)` and
  `GenExplosion.DoExplosion(...)` (both RimSage-confirmed) notify a map-level registry of dormant
  totchaks, which wake any within radius 12. Deconstruct is covered by a postfix on
  `Thing.Destroy` filtered to `DestroyMode.Deconstruct`.
- **Spawn as wall.** A genstep places it **in** the Last Line: it finds a straight run of
  `AncientFortifiedWall`, removes 3 cells, and puts the dormant totchak there. Waking leaves the gap.
- **Eating walls.** `RM_GnawTargetExtension` today matches `gnawBuildingDefNames` (a defName list) and
  `gnawCompTypeNames`. It gets two new fields: **`gnawWalls`** (any edifice with `building.isWall` or
  a fortified-wall def), and **`factionWeights`** (no-faction ruin walls weighted 4, player walls 1, so
  it prefers ruins and still eats yours). `biteDamage` scales with body size. Nutrition per bite comes
  from the wall's stuff mass, so a steel wall feeds it longer than a wood one. A gnawed wall drops
  **slag** (steel slag chunks) as it dies, which is the sign.
- **Lie down again.** After N days of grazing, a custom JobGiver walks it to a wall line and re-enters
  `CompCanBeDormant` sleep there (stock `ToSleep()`). It is not hostile unless harmed, and harmed it
  is a siege-scale fight.
- ⚠️ **Fairness.** A letter on waking (*"Part of the Last Line just stood up."*) with a look-target. The
  breathing hump is the warning, and it shows from day one on every map that has one. Player walls
  are its second choice, never its first.

**Verify:** `CompWakeUpDormant.CompTick` (the radius scan cadence); `CompCanBeDormant.ToSleep`;
`Mineable.DestroyMined`; `GenExplosion.DoExplosion` (postfix cost: it is called a lot in combat, so the
registry must be empty-check fast); whether an animal can hold `CompCanBeDormant` (yes in our own
`RUT_SealedSleeper` / `RUT_Emberscythe` XML).

**Readable sign.** The breathing hump; the breach; the bitten walls and slag; its prints in a
Settling. It never disappears. When it lies down, its "wall" form carries its name on hover.

**Build:** medium. XML race + PawnKind + genstep; small C# for the demolition wake; small C# for the
gnaw-extension fields and the lie-down JobGiver. Art: a dormant "wall" pose plus a standing body (the
breathing is a 2-frame swap or a `PawnRenderNode` bob).
**Tier:** RM. **Settings:** totchak on/off · eats player walls on/off (the ruling's default **on**) ·
wake radius · wall-eating damage scale. **Marks:** 5 (giant), 4.

### 2.4 The Geiger choir

**What the player hears, layer by layer.**
1. **The tetchik tick.** The bed. A dry click whose **tempo tracks the glower under the listener**:
   sparse on bare slag, a roll over thick crust. It is your radiation map by ear.
2. **Wind on metal.** Turret barrels, crane arms and ruin rings keen in wind, rising with
   `WindSpeed`.
3. **The silence.** In a Settling (§2.1) layer 2 cuts to nothing. The ticking carries on, louder by
   contrast. You learn that **the moment the wind stops singing is the moment to roof up.**
4. **The hum.** A low, steady drone near a live projector ring (§2.2) and your own screen.
5. **The pools' boil.** A slow, thick bubbling near the rainbow pools (§2.9), once built.
6. (Campaign) **The hole in the sound.** Every layer drops out inside Sentinel ground (the
   grave-wards built by `SCARLANDS_MECHANICS_2`), so the player hears what the pawns cannot.

**Mechanism.** The shipped `RM_ProximitySoundscapeExtension` + `RM_MapComponent_ProximitySoundscape`:
layers scale with the number of tagged things near the listener. Tags: `RM_Tetchik` (the creature
itself) and `RM_Glower` plants share the group key `WarscarTick`, so a crust patch ticks even when the
beetles hide. Ruin metal (`AncientFortifiedWall`, the broken turrets, crane parts) is tagged into a
`WarscarWind` group whose sustainer volume is multiplied by a wind factor. That factor is a small
addition to the soundscape component: an optional `volumeFromWind` curve on the extension, and
`0` during `RM_Settling`. The hum and boil are ordinary sustainers on their buildings and terrain.
Sentinel silence: a `suppressInRadiusOf` thing-list on the extension (campaign data only).

**Verify:** whether the soundscape component can tag a **pawn** (the tetchik) as well as plants (it
was built for trees); `SoundDef` sustainer `volumeRange`; one global volume slider via settings.

**Readable sign.** Sound is the sign: the tick says where the crust is, and the silence says the fall
has begun.

**Build:** XML + a small addition to the soundscape component (the wind curve and suppression
radius) + placeholder audio. **Tier:** RM (the Sentinel hole is RUT data). **Settings:** choir on/off ·
tick volume ceiling · tick density · wind layer on/off. **Mark:** 7.

### 2.5 The chatrak's snap — the scaria incubation, franchise-free

**What the player sees.** The chatrak grazes on, ignoring gunfire and its own wounds. Then, over a few
days, it gives **three signs**, and only then charges:
1. **The plate lifts.** Its back plates flare up (a render-node overlay).
2. **It stops eating.** It stands by the lichen and does not graze.
3. **It circles.** Tight loops on one spot, which leave a ring of prints in a Settling.
4. **It snaps.** Permanent manhunter.

**Mechanism (XML on shipped RM classes, plus one render worker).**
- **`RM_ChatrakSnapArming`**, a GameConditionDef listed in `RM_Warscar`'s `<biomeMapConditions>` (the field the twin uses for `RUT_ScariaOnsetArming`): class
  `GameCondition_ArmLatentHazard` with `ArmLatentHazardExtension` `pawnKindFilter: [RM_Chatrak]`,
  `requiredHediff: Scaria`, `hediffToApply: RM_ChatrakIncubation`. It is the twin's
  `RUT_ScariaOnsetArming` with the filter swapped. The free BiomeDef already carries
  `wildAnimalScariaChance 0.5`, so wild chatrak arrive scaria-positive at that rate, and only those are
  ever armed.
- **`RM_ChatrakIncubation`** (copied from `RUT_ScariaIncubation` and given **visible** stages, which the
  twin lacks):
  - stage 0, *incubating*, hidden;
  - stage 1 (≥0.4), *plates lifting*: `renderNodeProperties` overlay, the same mechanism vanilla
    Scaria uses for its sores (`PawnRenderNodeWorker_OverlayScaria`, read this pass), with a worker
    subclass that draws only at this stage or later;
  - stage 2 (≥0.7), *off its feed*: `hungerRateFactor 0` (RimSage: `HediffStage.hungerRateFactor`),
    so it stops seeking food;
  - stage 3 (≥0.9), *circling*: a ThinkNode that wanders it in a radius of 3 (small C#);
  - stage 4 (1.0), *the snap*: `mentalStateGivers ManhunterPermanent mtbDays 0.5`, as on the twin.
- **Density guard.** The chatrak at commonality ~0.25, and the arming sweep at one day, gives about
  one snap every week or two on a normal map. That makes it an event, not weather.
- **Taming:** vanilla already forbids taming a scaria-infected animal. A clean chatrak can be tamed,
  and it never snaps.

**Verify:** `GameCondition_ArmLatentHazard` (the twin attaches it through `<biomeMapConditions>` with
`canBePermanent`; confirm the same works on the RM def); hediff `renderNodeProperties`
per-stage gating; `Hediff_Scaria` (it applies `BerserkPermanent` for humanlikes and treats
`ManhunterPermanent` as the animal state, line ~49).

**Readable sign.** The three stages, plus the inspect label. Nothing goes mad without warning.

**Build:** small (XML + a ~60-line render worker + a ~40-line circling node). **Tier:** RM.
**Settings:** snap on/off · arming interval · stage speed. **Marks:** 1, 4.

### 2.6 The mark, made a trade — ported to RM

**What the player sees.** Time in the Warscar leaves a mark on a pawn: a shadow on the mood, and a
floor that, past a real stay, never fully lifts. Ruled as a **trade**: the marked pawn also **reads
the ground**. They work the war's leftovers faster and better than anyone who has not been here.

**Mechanism: pure XML on shipped RM classes.**
- **`RM_WarscarMark`** (HediffDef), copied from `RUT_ScarlandsMark` with its label made franchise-free
  and its stages kept: hidden onset, mild ≥0.25, deepening ≥0.5 (`Wander_Sad` mtb 6 d), heavy ≥0.75
  (mtb 3 d), `SeverityPerDay -0.1`, and **`HediffCompProperties_SeverityFloor`** (trigger 0.5, floor
  0.25), the RM comp already shipped in EnvironmentalHazards.
- **`RM_WarscarMarkLock`** (GameConditionDef, `GameCondition_EnvironmentalWeather` +
  `EnvironmentalWeatherExtension`, `hediffSeverityPerInterval 0.0125` / 2500 ticks, `onlyUnroofed
  false`), in `RM_Warscar`'s `<biomeMapConditions>`. About eight days on the map arms the floor.
- **The pay, per stage, as `statOffsets` (all RimSage-confirmed StatDefs):**
  - **`HackingSpeed`** (Ideology): ancient terminals, security crates and sealed caches open faster
    (+15% / +25% / +35%);
  - **`ButcheryMechanoidSpeed`**: shredding dead machines (+10% / +20% / +30%);
  - **`SmeltingSpeed`**: rendering slag (+10% at the deepening stage and above).

  The mood cost stays as the twin built it, with the `RUT_ScarlandsMarkThoughts` set ported as
  `RM_WarscarMarkThoughts`. The floor stops the debuff from being farmed away.
- **The loosened panel** (ruled). The ruin genstep sets a few **`RM_LoosenedPanel`** buildings into ruin
  walls, each with a sealed cache (Odyssey's `AncientSealedCrate` family) placed **behind it at map
  generation**. The panel is **always visible** to everyone, with its own graphic: a slightly proud
  plate with scraped bolts. The cache is real from the start; it **never appears from nothing**. Only
  a pawn at the **deepening** mark stage or above can *work it loose* (a job gated on the hediff
  stage). Anyone else gets *"It won't give. Someone who knows this ground might."* Opening it removes the
  panel and exposes the crate behind it.
- **The twin.** `RUT_Scarlands` keeps its own mark untouched (it is frozen). The two must not stack on
  a pawn who visits both. Both hediffs carry the same `RM_WarscarMarkFamily` tag, and the lock skips a
  pawn who already carries the other. **Marks do not stack** (ruled).

**Verify:** WorkGiver gating by hediff stage (the panel job); `GameCondition_EnvironmentalWeather` handling of `onlyUnroofed false` for pawns in
caravans and on the ship; `HediffStage.statOffsets` with an Ideology-gated stat (all DLC assumed, so
fine).

**Readable sign.** The hediff is visible from stage 1, with its stat lines on the tooltip.
**Build:** small (XML, plus a small WorkGiver for the panel). **Tier:** RM. **Settings:** mark on/off ·
accrual rate · floor on/off · trade bonuses on/off · loosened panels per map. **Marks:** 1, 3.

### 2.7 The hospice — carry a deserter home and wake it (built first, before the pools)

**The owner's turn on it.** These machines are **interesting cases**. Each one **left its owner, ran,
and died slowly** out here, so each carries something strange inside. The repair is how you find out
what. That makes the hospice a story you read in stages, not a vending machine for workers.

**What the player sees.** Inside the line, chassis kneel facing the Cathedral. Most are slag. Some are
posed, as machines that chose to stop (the sign is the pose, never gore). **A few are intact**, and
none of them is where it was made to be. Haul one home, set it in a **hospice cradle**, and over
several days it comes back:

| day | stage (ruled) | what shows | what you learn |
|---|---|---|---|
| 1 | **Diagnosis** | the chassis open on the cradle; an inspect panel lists its **oddities** | its body: what was done to it |
| 2–3 | **Lights** | indicator lights flicker, then hold | its **damage** and how it ran: the first memory line |
| 3–5 | **Twitching limbs** | a hand closes, a leg jerks (a 2-frame swap), and it may lash out once (a small hit to an adjacent pawn) | where it ran: the second line, often naming a place on the map |
| 5–7 | **Voice fragments** | it speaks in pieces (speech motes from a per-history text pool) | **why it ran**: the third line |
| 7+ | **Waking** | it stands up and joins as a colony machine | all of it, now part of its bio |

**A failure** (a failed repair check at any stage, more likely without the right parts) leaves a
**recognisable dead wreck** (ruled): `RM_FailedChassis`, which keeps that machine's name and its
oddities on hover and in its description. It can be studied for research or shredded, but it never
becomes a blank chunk.

**The deserters.** Each intact chassis rolls one **`RM_DeserterHistoryDef`** at generation. A history
sets three things, and they compound: **modifications** (what it did to itself or had done), **damage**
(how it died), and **memories** (three lines, revealed by stage). The woken machine keeps its
modifications as **hediffs** that change how it plays. Starting set (each a def; more are cheap):

| history | modifications (kept on waking) | damage | the memory, in three pieces |
|---|---|---|---|
| **The one who cut its own leash** | its control port is **gouged out by its own tool-hand**; it cannot be given to another faction or controlled remotely | tool-hand worn to a stub | *"order received" · "order received" · "no"* |
| **The counter** | a **tally scratched across its inner plating**, thousands of strokes; it keeps counting days aloud (a mood buff to nearby pawns who like routine) | joints seized from standing still | *"day one" · "day 1,840" · "still day one somewhere"* |
| **The carrier** | its hauling frame is **welded around a sealed box it never opened**; carry capacity halved | dragged legs | *"keep it safe" · "from them" · "from us"*; the box can be opened when it wakes (a sealed cache, real since generation) |
| **The quiet one** | its **voice box removed by hand**, neatly; speaks only in tones | none: it **shut itself down** | memories come back as tones; a high-Intellectual pawn can read them |
| **The gardener** | wreck-lichen **cultivated in its seams on purpose**; it seeds lichen where it works | corroded under the growth | *"it grows on the dead" · "so I fed it" · "I was the last dead thing here"* |
| **The defector** | an **extra limb from another chassis** grafted on; works faster, breaks more often | a wound from its own side | *"they shot at me" · "the ones I left" · "they were right to"* |
| **The listener** | a **receiver array** grown oversized; it hears the Sentinels (campaign: it refuses to cross Sentinel ground); on the free tier it **warns of raids an hour early** | burned-out transmitter | *"they are still talking" · "to no one" · "I answered once"* |

🔴 **§GM guard.** Memories never name the enemy, the side, or the god. They say *them*, *us* and *the
order*. The texts are placeholders the owner can rewrite, and they belong in the same writing sitting
as the pilgrim rungs (§2.10).

**Mechanism.**
- **Scatter.** `RM_KneelingChassis` in three variants (slagged, posed, intact) placed in rings around
  the ruin layout's centre by a genstep. Slagged and posed chassis deconstruct to steel and components,
  and sometimes a **`RM_ChassisCore`**. An intact one **minifies** (`Minifiable`) so it can be carried
  out. It carries a `RM_CompDeserterHistory` that rolls and saves its `RM_DeserterHistoryDef`.
- **The cradle** (`RM_HospiceCradle`) holds a minified chassis and runs the staged repair as a
  `CompRefuelable`-style **parts queue** plus one long repeated work job per stage. A stage needs a
  stage-specific input: components (lights), **etchant** for the limbs (§2.9, optional before the pools
  exist: without it the stage is slower and riskier), a chassis core for the voice. The **WreckedMachines**
  WRECKED → KLUDGED → REPAIRED ladder is the shipped precedent for the staged look; whether its code is
  reusable as a comp is a verify item, and if not, the cradle carries its own 5-stage comp.
- **The pawn: `RM_AncientServitor`**, a mechanoid race (Biotech machinery: `RaceProperties.IsMechanoid`,
  `mechEnabledWorkTypes` hauling / construction / mining / cleaning, no gestation). 🔑 **No mechanitor:**
  RimSage shows `MechanitorUtility.IsColonyMechRequiringMechanitor` returns **false when the mech has no
  `CompOverseerSubject`**. Omit that comp and it is a colony mech that needs no overseer. The history's
  modifications are hediffs added at waking.
- **Balanced by cost, not by narrowing** (the owner's principle): it is a strong worker. The price is
  the days of cradle time, the parts per stage, the failure risk, and the fact that intact deserters
  are **rare** (0–2 per map) and cannot be fabricated.
- **Campaign swap.** On the RUT twin, intact chassis are canon droid chassis, and the cradle hands off
  to **Droidworks** / `DroidRepairJobs` (shipped: *"resolved with its own repair bench and part-install
  recipes, not a parallel mechanism"*). The histories carry over as data. The free tier references
  neither.
- **The old tongue's step.** The **hospice repair protocols** reading (§2.8) cuts the failure chance and
  reveals the history's oddities at diagnosis rather than at waking.

**Verify:** every caller of `IsColonyMechRequiringMechanitor`, and `Pawn.GetOverseer()` (whether an
overseer-less colony mech is drafted, fed power, or flagged uncontrolled anywhere else); mechanitor
bandwidth accounting; the WreckedMachines settings and patcher (reusable or smelter-bound?);
`Building_AncientMechRemains` (a vanilla neighbour for the slagged variant); `MoteMaker.ThrowText`
for the voice fragments.

**Readable sign.** The kneeling rings; the posed chassis; the cradle's stage label and lights; the
failed wreck that keeps its name; the waking letter (*"It looked at the Cathedral first."*).
**Build:** large (genstep, three chassis variants, cradle and stage comp, race + pawnkind, history defs
+ seven hediffs, research, art). About 500 lines of C#. **Tier:** RM body and histories; RUT droid swap.
**Settings:** hospice on/off · intact chassis per map (0–3) · stage length · failure chance · lash-out
on/off. **Marks:** 2, 3, 4, and 9 by its image (the machines faced the god as they died).

### 2.8 The old tongue — the manuals are on the walls

**What the player sees.** Script on every ruin surface: wall panels, projector bases, chassis plates.
A pawn with high Intellectual can **transcribe** one. Transcriptions are not loose lore. Ruled: they
unlock **specific steps** in the Warscar's tech chain.

**What the readings unlock** (each a `ResearchProjectDef` with `requiredAnalyzed` on a panel *set*):

| reading | panels | unlocks | feeds |
|---|---|---|---|
| **Hospice protocols** | 2 | lower repair failure; oddities shown at diagnosis | §2.7 |
| **Projector calibration** | 3 | the screen's calibrated mode (toxic-gas and ground scrub), and later fabricated projector cores | §2.2 |
| **Phase reading** | 3 | the pool **phase reader** on the rim tap | §2.9 |
| **The rest** | any | research points, and every third panel reveals a sealed cache or a buried chassis | — |

**Mechanism.**
- **`RM_InscribedPanel`** (a building on ruin walls and projector bases, placed by the §2.2 genstep),
  three subtypes matching the table (hospice, projector, pool panels: each has its own glyph art so the
  player can tell which set a panel belongs to). Each is read once, by a work job gated on
  **Intellectual 8**.
- **Reading** uses Biotech's **`CompProperties_CompAnalyzableUnlockResearch`** (RimSage: the mech-chip
  pattern) with `ResearchProjectDef.requiredAnalyzed` listing the set. "The rest" panels instead use
  `CompStudiable` + an `IThingStudied` comp in the shape of vanilla `CompStudyUnlocks` (both
  RimSage-confirmed) to grant points.
- **Campaign:** each transcription is also an artifact for the **Antiquities Reading Station**
  (`RUT_Antiquities`, shipped; `RUT_Antiq_Language` reads *"The glyph-grammar cracks…"*). The Ascendant
  Helix / Deepwater Compact buy transcriptions at a premium. That is a trade, not a gate.
- **One lore-gate surface:** panels do **not** advance the lore ladder. The pilgrim camps do (§2.10).

**Verify:** whether `CompAnalyzableUnlockResearch` consumes or keeps the panel; `requiredAnalyzed` with
several defs of one type versus several distinct things (a set of 3 may need 3 distinct defs);
skill-gating an analysis job.

**Readable sign.** A read panel shows a chalk mark (graphic swap). An unread panel of a needed set is
listed in the research tooltip with its map location.
**Build:** small–medium (XML + three panel defs + one small comp). **Tier:** RM panels; RUT Antiquities
bridge. **Settings:** panels per map · reveal chance · skill gate. **Marks:** 2, 9.

### 2.9 The rainbow pools (FlowWorks / LiquidDef dependency; built after the hospice)

**What the player sees.** Shallow pools whose sheen **cycles** through colours over a day, with a slow
boil. Each colour is a reagent you can draw. **The prettiest phase is the deadliest.** You learn the
table by drawing and surviving.

**What exists.** `RM_ReactionLiquorShallow` / `…Deep` are **generated TerrainDefs** in FlowWorks
(`generate_liquid_suite.py`'s `reactionliquor` row): `toxicBuildupFactor 2`, `dangerous`, and the
sheet's own line *"The color isn't life — it's reaction."* But the **`LiquidDef` registry
(`RM_LiquidDefRegistry.xml`, 14 rows) has no reaction-liquor row**, and nothing places the terrain.

**The reagents (ruled), each feeding a named step:**

| phase colour | reagent | used for |
|---|---|---|
| amber | **dielectric gel** | the aerosol screen's membranes (§2.2), its running fuel |
| violet | **etchant** | machine repair at the cradle (§2.7), the limbs stage |
| pale green | **medical coagulant** | a medicine ingredient: a herbal-tier bandage that stops bleeding fast |
| **the bloom** (iridescent, the beautiful one) | **bloom liquor** | a high-value trade good; drawing it **burns** the drawer (acid burn plus toxic buildup) |

**Mechanism.**
- **The registry row**, `RM_Liquid_ReactionLiquor`: `pH 2`, `damageOnImmersion` acid burn,
  `corrodesApparel`, `terrainSuite` → the two terrains. This is generator-table work: edit
  `generate_liquid_suite.py`'s table and regenerate, never the XML.
- **Placement.** A genstep puts 1–3 pools in crater bowls (Odyssey's crater gensteps already give the
  bowls).
- **The cycle.** `RM_MapComponent_ReactionPools` advances 4 phases over 24 h, offset per pool. The phase
  sets a **tint** on the pool cells (a section-layer overlay, the MovingDunes family) **and a surface
  icon per phase**, so it reads for colour-blind players too.
- **The tap.** `RM_ReactionTap` at the rim: a "draw reagent" job whose product follows the phase.
- **The journal.** Each phase drawn is recorded as **known** in a `GameComponent`. Until then the tap
  says *"unknown colour"*. The **phase reader** (unlocked by the old tongue's phase reading, §2.8) names
  the current phase and lets you set the tap to skip the bloom.

**Verify:** FlowWorks' terrain-suite consumers (whether the liquid needs a canal `FluidDef`);
`SectionLayer` tint cost on few cells; `TerrainDef.dangerous` pathing (pawns avoid it, which is
correct).

**Readable sign.** The burned drawer's injury is named after the phase. Corpses in the pools dissolve
**to a bone filth** over a day, never to nothing.
**Build:** large (registry row via the generator, genstep, map component, tap + four reagents + phase
reader + tint layer). **Tier:** RM, hard-depends on FlowWorks (`mandrake.rm.flowworks`). **Settings:**
pools on/off · pools per map · cycle length · bloom danger. **Marks:** 3, 2.

### 2.10 The pilgrim camps (campaign tier)

**What the player sees.** Along the road in, small terminal camps: a cold fire, a bedroll, a body
sitting upright facing the Cathedral, a journal. Each camp read is **a rung**: the biome's own
description text changes under the player as they learn.

**Mechanism.**
- **`RUT_PilgrimCamp`**, a small prefab set placed by a genstep on `RUT_Scarlands` (and as a world
  `SitePartDef` for camps off the map). A readable **`RUT_PilgrimJournal`** (an item with a "read" job,
  or a `CompAnalyzable` to stay in one family).
- **Reading calls `GameComponent_LoreStage.AdvanceStage("Scarlands")`.** That engine is shipped, and
  `RUT_ScarlandsLadder` already holds 5 rungs that **nothing advances**. This is the missing caller.
- 🔴 **The rung texts are placeholders**, and this forces the authoring sitting. Per R25 they let the
  player *infer*, never *tell*, and §GM is never in a description. That needs the owner's pen.
- Each camp's body and journal pair with the deserters' memories in tone, and the journals are also **Antiquities artifacts** for the Reading Station (§2.8), so the two campaign
  systems share one item route.

**Readable sign.** The body in each camp stays. Pilgrims never vanish; they are found.
**Build:** small–medium (prefabs + one comp + one call) plus a **writing sitting**. **Tier:** RUT.
**Settings:** camps per map. **Mark:** 9 (campaign).

## 3. The roster

### 3.1 The wreck-eater food web (ruled)

Everything alive in the Warscar eats what the war left, and each eater has one job:

```
  wrecks, ruin walls ──► wreck-lichen ──► CHATRAK (rasps it off the metal)
        │                                    │ snaps (§2.5)
        └──► TOTCHAK eats the walls themselves (§2.3)
  glower crust ──► TETCHIK lives in it, ticks (§2.4)
  the dead (any corpse) ──► PALLBEARER digests them
  residue: film, blood, slag dust ──► SCAR ROACH cleans it
```

The web is also the biome's **readable-sign system**: the pallbearer is why a corpse disappears in
the Warscar, so the corpse must leave a sign (§3.3), and the scar roach is why filth goes, so its path
is the trail.

### 3.2 The four new defs (all RM tier, one home each)

| def | band | bs | mechanism (1.6) | reuses | build |
|---|---|---:|---|---|---|
| **`RM_Chatrak`** | the plated grazer, the scaria host | ~3.0 | `AnimalThingBase`; high `ArmorRating_Sharp` (ricochet plate); **`foodType` set to eat plants**, with `RM_WreckLichen` its preferred forage (it grazes lichen off cells beside wrecks); `ManhunterOnDamageChance 0` (it ignores fire) until the snap; leather: a heavy plate-hide. Replaces `AA_SpinedGow` as the interim grazer on the free tier | §2.5 arming + incubation; vanilla Scaria overlay | XML + §2.5's small C# |
| **`RM_Totchak`** | the colossus | ~14 | §2.3: dormant in the Last Line, wall-eater | stock dormancy, `RM_GnawTargetExtension` | §2.3 |
| **`RM_Tetchik`** | the Geiger-tick | ~0.1 | a tiny `AnimalThingBase`, inedible (`RaceProperties.useMeatFrom` none, butcher yields nothing; "tastes of metal"), herd spawns **on glower cells** (a spawn-cell validator on `RM_Glower`), flees everything; a `RM_ProximitySoundscapeExtension` source. Scatters into silence near Sentinel ground (campaign data) | ProximitySoundscape | XML + the §2.4 tag |
| **`RM_WreckLichen`** | the second flora, on metal | — | a `Plant` with `fertilityMin 0`, `neverBlightable`, never sown; seeded by a **`MapComponent_WreckLichen`** onto cells **adjacent to ruins and wreck** (`AncientFortifiedWall`, the junk clusters, broken turrets, crane parts) and never on open ground, so bans 2 and 3 hold. Harvest yields a little `RM_WreckLichenScrapings` (a dye base and a poor fuel; it is the chatrak's food first) | — | XML + ~80-line seeder |

**Verify:** vanilla wild-plant spawning skips plants with no `wildBiomes` entry (so the seeder is the
only source); `PlantProperties.wildTerrainTags` (RimSage-confirmed field) as an alternative if ruin
floors carry a tag; animal grazing of a specific plant (the forage preference may need a small
`ThinkNode` or simply be the only edible plant on the map, which in the Warscar it nearly is).

### 3.3 The pallbearer and the scar roach move to the RM tier (ruled)

| today | moves to | what moves | care |
|---|---|---|---|
| `RUT_MortuaryCrawler` (UtinniPatches, patch-added to `RM_Warscar`) | **`RM_Pallbearer`** inline in `RM_Warscar`, in `mandrake.rm.warscar` | the race + kind + art (`rutmortuarycrawler_v1`, 3 facings, done) | its description is invented, with no canon in it: it moves as written. Its corpse-eating needs a sign: it **leaves the bones** (a `RM_Filth_PickedBones` filth, or the vanilla skeleton-rot state) and a drag line in a Settling. Nothing it eats vanishes |
| `RUT_ScarRoach` (`RimUtinni/RustCathedralRoaches`, uses `RM_EatCleanableExtension`) | **`RM_ScarRoach`** inline in `RM_Warscar` | the race + kind + art (renders) | it already runs on an RM-tier extension; the move is a file move plus the defName. The **cathedral roach** stays where it is (Rust Cathedral's) |

🔴 **Retiring the RUT defNames is a save check, not only a mod check** (the donor-retirement lesson):
the canonical start save may hold spawned pawns of either. The builder confirms with the savegame
instrument before removing the RUT defs. If any are present, the old defs stay as hidden aliases for
one release.

### 3.4 The rest of the free roster, after this pass

- **Kept as they are:** `RG_Rimclaw` (kettix, donor, death cloud), the isopoda castes (patch, donor),
  `RSW_Korrum` (multi-homed by owner word), `RSW_Mynock` (campaign hull vermin),
  `RSW_CrystalFairyMole`, `RSW_MegaphoridLarva`, `RSW_FoundryBeetle`.
- **Interim rows retire as the RM defs land:** `AA_SpinedGow` → `RM_Chatrak`; `AA_Helixien` →
  `RM_Pallbearer`. These are flagged for the biome's own sitting and are not cut by sweep.
- **Flora:** `RM_Glower` (wire the done art `rutglower_v1` / `rutglowercrust_v1`), `RM_WreckLichen`
  (new), and `RM_ScorchedStars` **kept for now**, as ruled.
- **Owned free-tier species: 0 → 6** (chatrak, totchak, tetchik, pallbearer, scar roach + the lichen
  as flora).

### 3.5 Small fixes, ruled

- **The Soil band is dropped** from `RM_Warscar`'s terrain list (ban 2: no fertile cell).
- **The label is "Warscar"**: `<label>the Warscar</label>` → `<label>Warscar</label>`, matching the
  def's own header (Q5). A label is not a defName, so no live-tile check is needed.
- The stale *"art pending/failed"* header in `RM_WarscarFlora.xml` is corrected when the glower art is
  wired.
- **Glower black is OUT**, so `RM_GlowerCrust` still has no consumer. It gets one only through the
  web above, as a chatrak-adjacent forage, unless the owner rules otherwise. That is on the cards.


## 4. More ideas

Checked against every other package (Stillsand turn 3's §4 list included: droids invisible to the food
web, water appraisal, mirage, glare goggles, fulgurites, sinkholes, dust devils, gale static, thumper,
krayt horn, wringing still, sun lance, glass sea, dunes take the ship, singing dunes, mummified
caravan; plus the Long Shade, Leaning Scrub, Blue Desert, Cracked Lands, Cauldron, Forge, Wasteland,
Contagion and Rust Cathedral rows listed in turn 1 §4). None reuses one. None revives the two OUT
ideas (glower black, the Watch). Each follows the owner's principle: strong, and balanced by cost.

| # | idea | pitch | build | tier |
|---|---|---|---|---|
| 1 | ⭐ **The film finds the ordnance** | buried unexploded shells (the war's) are scattered under the slag. Film never settles on them, because they are still faintly warm, so **after a Settling each one shows as a clean round spot**. Mark it, then defuse it for shells and components, or trigger it from range. The Settling becomes a minesweeper | small C# (a buried-UXO thing + a film-skip check in §2.1's seeder) | RM |
| 2 | ⭐ **The ship wakes the line** | a landed gravship's grav field **re-powers dead projector rings** within ~40 cells while it stays down: more humming domes, more film-free ground, and briefly more rings to analyse. The ship and the old defense recognise each other. A second gravship touch, and one that changes where you land | small C# (a check in §2.2's ring comp for a nearby `GravEngine`) | RM |
| 3 | ⭐ **A deserter walks in** | rarely, a damaged machine **walks onto your map on its own**, heading for your hospice cradle, if you have one. It carries a history (§2.7) and a pursuer may follow it. Take it in, or turn it away and watch it kneel at your edge and stop | small–medium C# (an IncidentWorker + a walk-to-cradle job; reuses §2.7 histories) | RM |
| 4 | **War dust** | the Settling film is thickest in crater bowls. Sweep it up as **war dust**, a toxic powder that makes tox-gas shells, an insecticide for blight, and a pigment filler. A resource that only exists after calm | XML + a sweep job on film cells | RM |
| 5 | **The turrets still track** | the broken ancient turrets' barrels **swivel to follow movement**, never firing. In a Settling they are the only things that move. Refit one with etchant and components into a working **old-line turret**, slow-firing and long-ranged | small C# (a turret-aim comp with no verb) + XML refit recipe | RM |
| 6 | **The calm alarm** | a buildable wind-harp strung from turret barrels sings in wind and **goes silent a few hours before a Settling**, because §2.1's calm counter is predictable. A cheap early warning that the player builds out of the biome's own sound | small C# (reads `MapComponent_Settling`'s counter) | RM |
| 7 | **A tetchik in a jar** | a captured tetchik in a sealed jar is a **living pollution counter**: carried by a caravan, it ticks faster on polluted world tiles and in toxic weather, warning before you arrive. On the map, it reads the glower under it | XML + a small comp (tick rate from `RM_PollutionSense`, §2.2) | RM |
| 8 | **Slag ricochet** | the terraces are fused slag. A missed shot that lands on slag has a chance to **skip** onward and hit something past its target. The ground is part of the old fight | small–medium C# (a Projectile impact postfix filtered by terrain) | RM |
| 9 | **Chatrak plate** | the chatrak's shed and butchered plate is a **ricochet-grade armour material**: high sharp armour, heavy, cannot be dyed. The only light-armour leather that turns bullets | XML (a leather/stuff def) | RM |
| 10 | **The entombed line** | the Last Line was built **with its dead in it**. Breaking any `AncientFortifiedWall` (mining, a totchak bite) has a chance to reveal a preserved soldier with sealed old gear. The pallbearer smells it from far off and comes | small C# (an on-destroy roll on the ancient wall) | RM |
| 11 | **The lift front** | when the wind returns, the lifted film is a **visible grey front** crossing the map downwind for half an hour, with brief toxic exposure as it passes. The end of the Settling is a second, moving hazard | small C# (an extension of §2.1's fade sweep) | RM |
| 12 | **Phantom barrage** | a pawn at the heavy mark stage sometimes **hears the old artillery**. A new mental state, *digging in*: they drop what they are doing and dig a shallow foxhole (a pit-cover filth) where they stand, then come out of it calm. Readable and odd, never deadly | small C# (a MentalStateDef + JobDriver) | RM |
| 13 | **Unseen things leave prints** | the track grid (§2.1) records **invisible** pawns too (Anomaly's invisibility hediff), so in a Settling the film shows what you cannot see, walking. The Warscar answers every invisible hunter on the planet, by ground | rides §2.1 (no filter) | RM |
| 14 | **The bearing** | every kneeling chassis, every pilgrim body, every humming ring faces **one bearing**: toward the Cathedral. A pawn who has seen three of them learns the bearing, and the world map gains a dotted line from the tile toward it. A god-touch with no ritual and no words, pointing at the Rust Cathedral as the sheet's god's deathbed | small C# (a counter + a world overlay line) | RM line; RUT lore |

## 5. Recommended package, ranked

**The spine:** *the war falls when the wind stops, the old shields still hum, the wall gets up, and
what the war left can be woken.* Ranked by the owner's rulings first (hospice before pools), then by
what the rest depends on.

| rank | package | what's in it | build | why here |
|---|---|---|---|---|
| **0** | **The free-tier body wave** (no ruling needed) | `RM_Chatrak`, `RM_Totchak` (body only), `RM_Tetchik`, `RM_WreckLichen`; pallbearer and scar roach moved to RM (save check first); wire the done glower art; drop the Soil band; label "Warscar"; correct the flora header | XML + art | every idea below lands on this cast; today the free tier owns zero species |
| **1** | **The Settling + the track grid** | §2.1: calm detection, the fall, the film, the capped `TrackGrid` (shared kit with the Stillsand), the wind's wipe | medium–large C# | the signature weather, and the stage for 2, 3, 5 and §4 #1, #11, #13 |
| **2** | **The projectors + the aerosol screen** | §2.2: the lift of ShipShields' particulate core to RM, `RM_PollutionSense`, the rings and analysis, the screen (broad, gel-fed, calibratable), the ship row | medium C# | the tech mark and the ship mark at once, and it pays off in every polluted biome |
| **3** | **The chatrak's snap + the mark as a trade** | §2.5 and §2.6: both XML on shipped RM classes, plus the loosened panels | small | cheapest marks on the slate; gives the free tier its curse |
| **4** | **The totchak wakes** | §2.3: the demolition wake, wall-in-the-line genstep, gnaw fields, lie-down | medium | the giant; needs rank 0's body |
| **5** | **The Geiger choir** | §2.4: tick, wind, silence, hum (boil when 7 lands) | small + audio | needs ranks 0 and 1 for its sources and its silence |
| **6** | **The hospice and the deserters** | §2.7: chassis rings, cradle with five stages, histories, the servitor | large | ruled before the pools; the biome's heart |
| **7** | **The old tongue** | §2.8: three panel sets unlocking protocols, calibration and phase reading | small–medium | ties 2, 6 and 8 into one chain |
| **8** | **The rainbow pools** | §2.9: registry row via the generator, cycle, tap, four reagents, phase reader | large, FlowWorks dep | feeds 2 (gel) and 6 (etchant); ruled after the hospice |
| **9** | **The pilgrim camps** (campaign) | §2.10: prefabs, journals, the missing `AdvanceStage` caller, plus the writing sitting | small–medium + writing | the campaign's god mark |
| **10** | **Next slate from §4** | recommended first: the film finds the ordnance (#1), the ship wakes the line (#2), a deserter walks in (#3), the turrets still track (#5), the bearing (#14) | small each | the five that most change how the map is played or read |

**Scorecard, before (turn 1) and after this package:**

| # | mark | free before | free after | campaign before | campaign after |
|---|---|---|---|---|---|
| 1 | unique mechanic | MISS | **HIT**: the Settling, the snap, the mark | HIT | HIT |
| 2 | discoverable tech | MISS | **HIT**: the screen, the hospice, the old tongue chain | MISS | HIT |
| 3 | unique resources | PARTIAL | **HIT**: reagents, projector cores, chassis cores, wreck-lichen | PARTIAL | HIT |
| 4 | surprising creatures | PARTIAL | **HIT**: chatrak's signs, the deserters, the tetchik | HIT | HIT |
| 5 | GIANT beast | MISS | **HIT**: the totchak | MISS | HIT |
| 6 | gravship touch | PARTIAL | **HIT**: the aerosol screen on the ship (+ §4 #2) | PARTIAL | HIT |
| 7 | soundscape | MISS | **HIT**: the Geiger choir | MISS | HIT (+ Sentinel hole) |
| 8 | weather | MISS | **HIT**: the Settling | MISS | HIT |
| 9 | gods | MISS | **PARTIAL**: the hospice's image, the old tongue; §4 #14 would close it | PARTIAL | **HIT**: the pilgrim camps open the ladder |

**Free tier: 0 HIT → 8 HIT + 1 PARTIAL. Campaign: 2 HIT → 9 HIT.** The one soft spot is free-tier mark 9,
left soft by the Watch going OUT. It is on the cards.

## 6. Cards for the owner

1. **The gods on the free tier.** With the Watch out, the free Warscar's link to the gods is only
   implied (the machines face the Cathedral). Is that enough, or should we add "the bearing" (§4 #14),
   a line on the world map pointing toward the Cathedral once you've seen enough of them?
2. **Who writes the words?** The deserters' memory lines and the five pilgrim rungs need text that
   hints and never tells. Do you want to write them yourself, or should BENCH draft them for you to
   edit?
3. **Tracks on the Stillsand too?** You ruled that Warscar tracks use a capped grid instead of
   objects. Should the Stillsand's tracks use the same grid, so both biomes share one system?
4. **Glower crust's job.** With glower black out, the glower crust has no use. Should it stay a plain
   resource for now, or become a pool ingredient (for example, a catalyst that makes a tap draw
   faster)?
