# Explosive growth: the ruled spec (2026-10-16)

**Authority:** `design/RimMandrake/explosive_growth_rulings_2026-10-16.md` (the owner's words, five rounds plus the typed
light ruling). Where this spec and the rulings disagree, the rulings win and this file is wrong. Inputs it supersedes
where they conflict: `explosive_growth_consensus_2026-10-16.md` (C), `explosive_growth_bench_design_pass_2026-10-16.md`
(B), `explosive_growth_gpt_review_2026-10-16.md` (G).

**Retired by the rulings, do not build:** the settled-wet state and its ×4 (W3: *"It always counts as fresh as long
as it's there. It's continuous."*); re-arm timers and the pulse exploit arithmetic (moot without a settle state); the
flat everyday ×4 band; the ×10 wet-jungle band (C1: ×4); a moisture overlay or wet-soil terrain (GM1); new desert rain
or flash floods in Utinni (WP1); the riverbank radius (W2: the water and mud cells only); the 300-plant rain cap (PF1).

Code claims are tagged **MEASURED (file:line)** against the bench clone at `9143b48cb3`, or **UNMEASURED**. Every
number not in the rulings is **PROPOSED**. Paths below are relative to `/home/mandrake/rm/bench`
(`D:\Luke\dev\RimMandrake` mirror).

---

## 1. The rule in six sentences

1. A cell is **wet** while a qualifying water source is present on it; wet ground is always fresh, continuously.
2. A plant grows by its **archetype's** rate for the cell's state, and only while it has light.
3. **Dry natives** (our plants of the dry biomes) run ×10 wet and ×0.1 dry; at maturity on wet, lit ground they
   cycle forever: fruit and many sprouts, or (1 in 3 by default) rupture.
4. **Wet natives** (our plants of the wet biomes) run ×4 at home always; at maturity they fruit prolifically, then
   wither, leaving a few sprouts.
5. Anything that yields wood grows at the slower tree rate; a plant below ×1 also ages at its slowed rate.
6. A crop that fruits by itself drops a full harvest and **uses up the water on its cell**; water, not yield, is the
   price.

---

## 2. Cell state machine

### 2.1 States

Per cell, computed on read from sources (no per-cell ticking):

| state | condition | who it matters to |
|---|---|---|
| **WET** | at least one live water source (§3) accepted by the plant standing there (§2.4) | every archetype |
| **DRY** | no accepted source | every archetype |
| **ASH-FRESH** | the cell burnt within `ashFlushDays` (C5: *"A burnt cell counts as fresh"*) | fire-adapted plants only; reads as WET for them |
| **SEALED** | the plant stands in a `Building_PlantGrower` (basin, pot, hydroponics) | every archetype: vanilla speed, no bonus, no cycle (H1) |

There is no "settled", no "fresh event" and no re-arm. GPT's critical finding G-1 (incomplete `wetSince` machine)
is dissolved, not patched: the only transitions are source-appears and source-gone.

### 2.2 Transitions

| from | event | to | note |
|---|---|---|---|
| DRY | a source appears (flood reaches it, hose spill lands, water poured, rain starts on an unroofed cell, channel fills) | WET | immediate; the next `GrowthRate` read sees it |
| WET | the last source on the cell goes (filth consumed or gone, flood recedes, rain stops*, channel drains, roof built*) | DRY | immediate |
| WET | a **crop** on it completes a self-fruit (§4.4) | DRY, unless the source is natural (river/mud) or a running flood | the consuming source is removed: spill filth destroyed, poured mark cleared, channel cell drawn down by `cropDrawLitres` |
| any | fire burns the cell | + ASH-FRESH for `ashFlushDays` | independent of water; the two OR together |
| any | suppression (grazing M10, dry-air blower M2) | as today: refuses new player water and dries the cell for its window | MEASURED API `Source/ExplosiveGrowthAPI.cs:40-43`; callers `EnvironmentalHazards/Source/RM_Patch_GrazingSuppressionHook.cs:91`, `RM_CompDryFieldEmitter.cs:163` |

\* rain: see open question OQ-9 (does ground stay wet after rain stops). Roof built over a WET-by-rain cell ends that
source; building a roof never ends a hose, poured or channel source.

### 2.3 Light gating (12:28 ruling)

*"the plants ONLY grow like this while there is light. On the Utinni world, this is always or never true. On other
worlds it will cycle."*

- Our rate multiplies vanilla's composite `GrowthRate`, which already contains `GrowthRateFactor_Light`
  (MEASURED RimSage `RimWorld/Plant.cs:301`); a dark cell is 0 and stays 0. The existing postfixes already return
  early on `__result <= 0` (MEASURED `Source/RM_ExplosiveGrowthPatches.cs:63,92`). Keep that contract: our factor
  never lifts a zero.
- The cycle clock (charge) holds in the dark: `StepCharge` advances only when `wet && growing`, holds when wet and
  not growing (MEASURED `Source/Kernel/RM_ExplosiveGrowthKernel.cs:64-69`). Keep.
- **The trap:** vanilla also rests every plant by the CLOCK, not the light: `Resting` is `DayPercent < 0.25 ||
  > 0.8` (MEASURED RimSage `RimWorld/Plant.cs:277-284`), and `GrowthPerTick` is 0 while resting (`Plant.cs:334`).
  On a tidally locked Ash'karr a permanently lit cell would still rest 45% of every day, so "always" is not true
  unless resting is overridden there. Whether Ash'karr's local clock is already pinned: UNMEASURED (the pinned sun is
  a shadow extension, MEASURED `CreatureBehaviors/Source/RM_PinnedSunExtension.cs:31-43`; nothing in `src/` patches
  `GenLocalDate` or `GenCelestial`, MEASURED by grep). Card OQ-7.
- Dark-side cells never get the show: no arming without light, already true via the composite.

### 2.4 Liquid adaptation (T2: *Only for adapted plants*)

- **Clean water** (`RM_Fluid_Water`, vanilla fresh water terrain, rain) waters every archetype.
- **Any other liquid** (the four slimes, red water, Greentide/Miasma/FeverWood fluids, boiling water, sheen) waters
  only a plant whose profile lists it in `adaptedLiquids`. Declared per biome at its review sheet (§9).
- Today the accepted set is one global list (MEASURED `Defs/ExplosiveGrowth/RM_ExplosiveGrowthRoster.xml:194-` lists
  `RM_Fluid_Water`, four slimes and three jungle fluids; read into `RM_ExplosiveGrowthRegistry.IrrigationFluids`,
  `Source/RM_ExplosiveGrowthRegistry.cs:139,232`) and the check is per cell, not per plant (MEASURED
  `Source/RM_SoakSources.cs:109`). Acceptance must move to the (cell source, plant) pair.

### 2.5 Rate table

`r` multiplies vanilla's composite `GrowthRate` and REPLACES every band of today (never stacks). In scope only (§6).

| archetype | WET (lit) | DRY (lit) | SEALED | notes |
|---|---|---|---|---|
| dry native | **×10** | **×0.1** (C6) | ×1 | trees ×0.625 of these (§5) |
| wet native, home biome | **×4, always** (C1), wet or dry | ×4 | ×1 | away from home: OQ-12 |
| fire-adapted (Pyrelands natives) | ×10 on WET or ASH-FRESH | ×0.1 | ×1 | a dry native with an ash source |
| stunted (terminator biomes) | today's ×0.4, unchanged | ×0.4 | ×1 | the rulings did not touch it; MEASURED setting `ExplosiveGrowthMod.cs:39` |
| exempt (anima, Gauranlen, ambrosia, growDays < 1, cave plants) | ×1 | ×1 | ×1 | MEASURED `RM_ExplosiveGrowthRegistry.cs:29-32,199-208` |
| vanilla crop / vanilla plant | ×1 if water nearby, else **×0** (DEFAULT) or ×1 (setting "normal") | | ×1 | §6 setting A |

Vanilla Odyssey drought (`GrowthRateFactor_Drought`, MEASURED in the composite, `Plant.cs:301`) still multiplies:
drought on dry ground gives ×0.03. PROPOSED: leave it (it is an event); G's "patch the drought factor directly"
stays open as a perf-free follow-up.

---

## 3. Water sources

| source | ruling | becomes WET | consumed by crop self-fruit | today | status |
|---|---|---|---|---|---|
| **river / water / mud terrain cells** | W2 *"(1) and the plants continuously grow and writhe there"* | the cell itself only, permanently | never | natural liquid is deliberately NOT a soak (MEASURED `Source/RM_SoakSources.cs:20-22`) | build: a per-`TerrainDef` "natural fresh water" bool array |
| **FloodedCanyon flood** | WP1 (the only natural flood in Utinni) | every cell the flood wets, while the water is there | never while it runs | pushed through `ExplosiveGrowthAPI.SoakCells` (MEASURED `FloodedCanyon/Source/RM_MapComponent_CanyonFlood.cs:499`) | keep; the soak duration becomes "while flooded" |
| **hose spill** | W4/HW1 *"Hose + carried + sprinklers"* | a cell holding spill filth of an accepted liquid | yes: the filth is destroyed | `RM_LiquidSpill.Spill` makes filth only, no soak (MEASURED `FlowWorks/Source/Machinery/RM_LiquidSpill.cs:176-204`) | build: read the filth, no FlowWorks edit needed |
| **carried water** | same | a cell a pawn pours on; PROPOSED representation: the same spill filth, so GM1's "obvious reason" is visible | yes | not built | build: job + work giver (§8 D8) |
| **dug channel holding accepted liquid** | GM1 names "channel" as a visible reason | the channel cell and its 8 neighbours (today's rule) | yes: draws `cropDrawLitres` from the cell | MEASURED `Source/RM_SoakSources.cs:98-112`, rule in `_Shared/FlowWorksIrrigation/FlowWorksIrrigationRead.cs:104` | keep; switch from timed soak to presence |
| **rain** | WP1, round-2 C3 (*"A rare flood or rainstorm is transformative and crisis-driving"*) | unroofed cells, while a water rain runs (OQ-9 for after) | yes (OQ-8 for wild plants) | random scatter of ≥20 cells per pulse (MEASURED `Source/RM_SoakSources.cs:134-150`); `soakWeathers` empty by default | build: rain is map-wide on unroofed ground; Utinni adds no rain anywhere it is not today |
| **ash flush** | C5 | ASH-FRESH for fire-adapted plants | no | Pyrelands already saves a per-cell last-fire tick (MEASURED header `Pyrelands/Source/PyrelandsAshField.cs`) | build: read it (OQ-11 duration) |
| **basins / pots** | H1 *Watered, normal vanilla speed* | SEALED | n/a | nothing reads the grower (B §0.2) | build |
| **sprinklers** | SP1 | deferred | — | — | **deferred to `SPRINKLERS_DESIGN_PIPES_THEN_PANACHE`** (ours: heads on FlowWorks pipes, rudimentary; VFE: bold automation; adapted together) |
| **miasma surge** (salt line) | not addressed | as today | — | MEASURED `Source/RM_SoakSources.cs:114-132` | keep unchanged; flagged OQ-13 |
| **Soak Zone / timer switch** | not a player source (B §0) | dev map-maker only | — | MEASURED `FloodedCanyon/Source/MapControls/Building_RM_SoakZone.cs:83` | keep as a dev tool |

Twilight Sea is a sea floor and rains in error (`TWILIGHT_SEA_FIX_IT_RAINS_UNDERWATER`); rain there is a defect,
not a source.

---

## 4. The two archetypes

### 4.1 Dry natives

Default archetype for every plant def our tiers ship that is not native to a wet biome and not exempt or stunted.

- Growth: ×10 wet, ×0.1 dry, light-gated.
- **Churn, endlessly while wet and lit** (round 4 card): ×10 to maturity, then the cycle outcome, then again.
- **Cycle outcome** at maturity (C2, C3), rolled once per maturity:
  - with probability `ruptureChance` (default **1/3**; per-plant override, `1` for some, `0` for groundcover and
    others): **rupture** = die impressively, using the plant's violent top (Burst, Tinder, Slime or the contaminated
    Rupture, whichever the plant declares; Burst when it declares none). See OQ-5 on the name;
  - otherwise: **fruit** (its harvest product × `produceFactor`; wood never, §5) and **many sprouts**
    (PROPOSED 4–7 in radius 2.9, respecting built ground). Whether the parent lives (growth reset) or dies is
    OQ-6; PROPOSED: lives, reset to growth 0.5 so the cycle repeats on the cell.
- **Pyrelands grass:** `ruptureChance 0`, `sproutCount` high (PROPOSED 6–9) and the dry-native ×10 on ASH-FRESH:
  *"does not rupture but does grow violently quickly and spread itself super-fast."*
- The tell ladder (ground, swell, hue, tremble, creak, silence) stays as the visible run-up to each outcome
  (MEASURED `Source/Kernel/RM_ExplosiveGrowthKernel.cs:11,53-61`).

### 4.2 Wet natives

Plants native to Greentide, Miasma, Fever Wood (the ruled jungles) and Webwork, Contagion (WP3 *"Answer is (1)"*).

- Growth: ×4 at home, always (C1).
- **Cycle at maturity:** fruit **prolifically** (PROPOSED `produceFactor` default 2.0), then **wither** (die
  quietly: rot to a dead plant, no blast), leaving **a few sprouts** (PROPOSED 1–2, respecting built ground).
- Never rupture (no violent top), unless a plant's sheet row says otherwise.
- Fever Wood giants keep `Flush` (survive their top; MEASURED `Source/RM_TopResolver.cs:289-296`): a sheet-row
  exception to "wither".

### 4.3 Archetype assignment

- Default from data, not from a biome at runtime: a plant listed in the `wildPlants` of a wet biome (or its RUT_
  twin) is a wet native; otherwise a dry native. Computed once at `Rebuild` (MEASURED loop
  `Source/RM_ExplosiveGrowthRegistry.cs:171-214`).
- A plant in both a wet and a dry biome's roster: the biome review sheet's row decides (§9). Until then, PROPOSED:
  wet native (the conservative rate). This answers G's WP3 objection: the biome list seeds, the plant row decides.
- Every plant ever reaches a sheet row; the seed is never the final word.

### 4.4 Crop self-fruit (EC3)

*"A full harvest but the water gets used up. That's the cost."*

- A **crop** = a plant sown in a growing zone (vanilla `Plant.IsCrop`/sown by a pawn). Which crops self-fruit:
  OQ-15 (PROPOSED: our native plants sown as crops; vanilla crops never self-fruit, they only obey setting A).
- At maturity on WET ground the crop drops its **full** `YieldNow()` harvest, and that IS its harvest: the plant is
  treated as harvested (dies, or for a repeat-harvest def resets to `harvestAfterGrowth` exactly as vanilla
  harvesting does). No second pawn harvest of the same growth (closes G critical finding 2's double spend).
- The water on the cell is consumed (§2.2). Natural river/mud and a running flood are not consumed.
- The jackpot and last-swing gamble (MEASURED `Source/RM_ExplosiveGrowthPatches.cs:183-232`) interact with this:
  OQ-14.

---

## 5. Wood, dormancy, and the economy item

### 5.1 Wood at tree rate (EC1 *"(1) but we need to renormalize EVERYTHING anyway"*)

- **Woody** = `def.plant.IsTree` OR `harvestedThingDef == WoodLog`. Today only `IsTree` (MEASURED
  `Source/RM_ExplosiveGrowthRegistry.cs:207`), which misses six wood yielders (B §0.5).
- Tree ratio stays today's 2.5 / 4 = **0.625** (MEASURED `ExplosiveGrowthMod.cs:37-38`): dry-native trees ×6.25
  wet, ×0.0625 dry; wet-native trees ×2.5 at home.
- Wood is never a cycle drop.
- Yields and grow days are NOT tuned here: `PLANT_ECONOMY_TUNE_EVERY_NUMBER_AT_ONCE` owns the planet-wide
  renormalization (incl. `RM_SicklyGlowMushroom`'s 25 logs in 2 days).

### 5.2 Dormancy (WP2 *"Yes, age at the slowed rate"*; G: age before mortality)

- A plant whose **moisture factor** (the §2.5 `r`, not the composite `GrowthRate`) is below 1 ages at `r`.
- Implementation shape: a **prefix** on `Plant.TickLong` that removes `(1 − r) × 2000` from the coming age step,
  because vanilla adds `ageInt += 2000` and checks `Dying` in the same call, after growth (MEASURED RimSage
  `RimWorld/Plant.cs:810-868`, age at the `ageInt += 2000` line, mortality right after). A postfix would let vanilla
  kill the plant first (G High finding 3).
- Fractional remainder kept per plant (or `GenMath.RoundRandom`); age clamped ≥ 0.
- Darkness, blight, temperature and drought never slow ageing: only our moisture factor does.
- `r = 0` (vanilla crop, default setting, no water nearby) means the crop neither grows nor ages: OQ-16.

---

## 6. Scope and Mod Settings (C4)

*"Settable in options. Vanilla crops may function normally, or (default) they simply don't grow unless there's
water nearby. But the local plants blow past them in this biome. Our plants should have similar settings: either
they simply grow normally in other biomes, or they do the same x10 when watered or x0.1 when dry elsewhere too."*

| setting | options | default | replaces |
|---|---|---|---|
| **A. Vanilla crops in our biomes** | `normal` (vanilla speed) · `need water nearby` (×0 unless an accepted source within `nearbyRadius`, then ×1) | **need water nearby** (ruled) | the everyday ×4 band, which today also speeds vanilla crops (MEASURED setting comment `ExplosiveGrowthMod.cs:37`) |
| **B. Our plants outside our biomes** | `vanilla` (×1, no cycle) · `same rule` (§2.5 rates and cycles) | UNRULED; PROPOSED `vanilla`, labelled unsupported (CLAUDE.md 2026-10-15: *"We can't guarantee they will work in other biomes beyond our framework"*) | `applyInOtherBiomes` (MEASURED `ExplosiveGrowthMod.cs:62`), which today extends BOTH tiers to ALL plants, vanilla included; B touches our plants only (OQ-10) |

- Scope otherwise unchanged: our biomes (MEASURED `BiomeInScope`, `Source/RM_ExplosiveGrowthRegistry.cs:62-64`);
  the Utinni roster's `scopeAllBiomes` puts every biome in scope (MEASURED
  `src/RimUtinni/UtinniPatches/Defs/ExplosiveGrowth/RUT_ExplosiveGrowthRoster.xml:29`).
- "Our natives always outgrow them here": with A at default, a native at ×10 beside a crop at ×1 is the ruled
  picture; nothing extra to build.
- Remaining settings (PROPOSED, every number a slider, defaults = the ruled numbers): dry-native wet ×10, dry ×0.1;
  wet-native home ×4; tree ratio 0.625; default `ruptureChance` 1/3; `ashFlushDays`; `nearbyRadius`;
  `cropDrawLitres`; one toggle per source (§3); wave stagger on/off (§7); tells, hue, sounds, suppression and the
  per-top switches as today (MEASURED `ExplosiveGrowthMod.cs:64-104`). Remove `defaultMultiplier`,
  `wetAmbientMultiplier`, `wetAmbientTreeMultiplier`, `soakMultiplier`, `defaultSoakHours` (MEASURED
  `ExplosiveGrowthMod.cs:37-54`).
- All-off degrades to vanilla growth everywhere (the "superb Mod Settings" rule).

---

## 7. The full-map wave (PF1 *"Try (2) then fallback to (3) if we have to"*)

- **First build (2):** every grown, lit plant on newly WET ground arms, swells and takes its outcome. No cap, no
  "nearest the colony" sample.
- **Fallback (3), only if §11's perf bar fails:** stagger arming over about one in-game day: a cell's arm delay is a
  deterministic hash of the cell index into [0, 60000) ticks, so the wave rolls across the map and a reload replays
  it identically.
- **Brakes that ship either way** (they change no behaviour):
  - re-mesh a plant only when its tell stage or size step changes; today the pass dirties every soaked immature
    plant and every charging plant on each reprint (MEASURED `Source/Kernel/RM_ExplosiveGrowthKernel.cs:253,312`;
    reprint every `reprintIntervalTicks` = 250, `ExplosiveGrowthMod.cs:76`);
  - batch dirty cells per map section per pass;
  - `GrowthRate` stays pure (no allocation, no writes), including inspect-pane reads.
- **Two steady-state cases are new and are the bigger load:** a wet-jungle map where every wet native cycles forever
  at ×4, and a riverside strip of dry natives churning at ×10. Both are in §11.

---

## 8. Delta: today's code → this spec

Sizes: **S** under half a day, **M** half a day to two days, **L** more (INFERRED estimates).

| # | file / class | change | size |
|---|---|---|---|
| D1 | `Kernel/RM_ExplosiveGrowthKernel.cs` `AmbientBand` (MEASURED :133-140) | → `RateFor(archetype, state, woody, settings)`: one rate, replaces, never stacks; fuzz self-test updated | S |
| D2 | `RM_ExplosiveGrowthPatches.cs` `RM_Patch_Plant_GrowthRate_Bands` + `_Soak` (MEASURED :56-99) | merge into one postfix reading D1; vanilla-crop rule A; SEALED short-circuit | M |
| D3 | `RM_MapComponent_ExplosiveGrowth` + `RM_EgLedger` (`soakUntil` timed dict, MEASURED kernel :146-193, comp :112-127) | presence model: WET = any live source; timed entries kept only for flood/rain; `TrySoak` "extends, never shortens" semantics retired for player water | M |
| D4 | new: natural-water terrain table | per-TerrainDef bool (river, shallow/deep fresh water, mud); cell itself only | S |
| D5 | `RM_SoakSources.PulseIrrigation` (MEASURED :98-112) | channel = presence, per (cell, plant) liquid acceptance; crop draw-down hook into FlowWorks' fill | M (cross-mod) |
| D6 | new: spill-filth reader | WET while accepted spill filth lies on the cell; consume = destroy filth | S |
| D7 | `RM_SoakSources.PulseWeather` (MEASURED :134-150) | random scatter → unroofed cells WET while a listed water rain runs; roof-change ends it | S |
| D8 | new: carried-water job (WorkGiver + JobDriver, FlowWorks container read) | pawns pour water on a zone; leaves spill filth | M (cross-mod) |
| D9 | `RM_PlantProfile` / `RM_ExplosiveGrowthRosterEntry` / extension (MEASURED `RM_ExplosiveGrowthRegistry.cs:8-19`, `RM_GrowthTop.cs:63-87`) | add `archetype`, `ruptureChance`, `sproutCount`, `adaptedLiquids`, `fireAdapted`, `woody`; registry seeds archetype from wet biomes' `wildPlants` | M |
| D10 | `RM_TopResolver.Churn` (MEASURED :105-115) + `Fire` (:77-93) | dry cycle: roll `ruptureChance` → violent top, else fruit + many sprouts + growth reset; wet cycle: prolific fruit, wither, few sprouts | M |
| D11 | `Sink.OnArmed` (MEASURED `RM_MapComponent_ExplosiveGrowth.cs:277-287`) | drop the arming sprout (sprouts belong to the outcome) | S |
| D12 | new: crop self-fruit | full `YieldNow` drop = the harvest; plant harvested; consume cell water | M |
| D13 | new: `Plant.TickLong` prefix | dormancy by moisture factor, before vanilla's age step and `Dying` check | S |
| D14 | new: tidal-lock resting | if OQ-7 says so, `Resting` false on lit cells of a tidally locked world | S |
| D15 | Pyrelands fire hook → ExplosiveGrowth | ASH-FRESH from the ash field's saved last-fire tick | S |
| D16 | new: SEALED growers | `Building_PlantGrower` → ×1, no cycle | S |
| D17 | `RM_ExplosiveGrowthRegistry` `p.tree` (MEASURED :207) | woody = IsTree OR WoodLog yield | S |
| D18 | `ExplosiveGrowthMod.cs` settings + UI (MEASURED :22-104, :158-273) | §6 settings A and B, slider set, remove band/soak sliders, save migration of old keys | M |
| D19 | `RM_ExplosiveGrowthRoster.xml` (MEASURED `wetAmbientBiomes` :212, `irrigationFluids` :194) + `RUT_ExplosiveGrowthRoster.xml` (:89,:93) | biome lists → archetype seeds incl. Webwork, Contagion; global fluid list → per-plant `adaptedLiquids` | S |
| D20 | `Kernel` `Pass` (MEASURED :240-315) | stage-change-only re-mesh; section batching; stagger hook (off) | S |
| D21 | `ExposeData` (MEASURED comp :357-375) | save migration: old `soakUntil` / `charges` load into the new model without throwing | S |
| D22 | `validation.py`, `northstar_plan.py`, `selftest_explosivegrowth_fuzz.py`, `lint_explosivegrowth_defs.py` | chains rewritten to the ruled rates (×10/×0.1/×4, replace not stack), cycle, crop consumption, light hold, dormancy, settings A/B | M |
| D23 | biome review sheet tooling (generator UNMEASURED; `Utils/biome_sheet_stats.py` exists) | §9 columns | M |
| D24 | perf harness | §11 cases | M |

**Total: 24 rows, 13 S + 11 M + 0 L ≈ L overall** (INFERRED ~9–13 builder days). Nothing is a rewrite: the ledger,
tell ladder, tops, suppression, settings framework and suite harness stay.

---

## 9. Per-biome review sheet columns

Every plant row on a biome's review sheet gains (decisions stored as data, `review-sheets` contract):

| column | values | default before he rules | ruling |
|---|---|---|---|
| **archetype** | dry native · wet native · fire-adapted · stunted · exempt | seeded (§4.3) | C2, WP3 |
| **rupture odds** | 0 · 1 in 3 · 1 in 1 · other fraction | 1 in 3 for dry natives, 0 for groundcover and wet natives | C3 *"exceptions will be declared as we go forward. That's why we need this on for each biome review."* |
| **violent top** | Burst · Tinder · Slime · Rupture (contaminated) · none | today's roster top (MEASURED counts in `RM_ExplosiveGrowthRoster.xml`: 75 None, 22 Rupture, 9 Slime, 6 Churn, 3 Tinder, 1 Burst, 1 Flush) | C3 |
| **liquid adaptation** | list: water (always), slimes, red water, jungle fluids, sheen, boiling | water only | T2 |
| **sprouts** | few · many · super-fast (count) | dry many, wet few | C2, Pyrelands grass |
| **woody** | yes / no | computed (§5.1), shown for confirmation | EC1 |

Multi-homed species (a plant in two biomes' rosters) appear as a row on each sheet; archetype conflicts are surfaced,
never silently resolved (CLAUDE.md: evictions are stopped; this is review work).

---

## 10. GPT critical and high findings: resolved by the rulings?

| # | G finding (severity) | status |
|---|---|---|
| 1 | Moisture state machine incomplete (Critical) | **Resolved**: W3 makes state = presence; no fresh-event window exists to be wrong |
| 2 | Fruit and harvest spend the crop twice (Critical) | **Resolved for crops** by EC3 + §4.4 (self-fruit is the harvest, water consumed). Open: jackpot interaction (OQ-14); wild plants' fruit has no water cost (OQ-8) |
| 3 | Dormancy postfix unsafe (High) | **Resolved**: WP2 + §5.2 prefix before mortality, moisture factor only |
| 4 | Ageing evidence overstated (High) | **Moot**: dormancy adopted regardless |
| 5 | Pulse arithmetic wrong (High) | **Moot**: no settle state, no re-arm |
| 6 | Hydroponics ×4 an economy decision (High) | **Resolved**: H1 ×1 |
| 7 | No water budget (High) | **Partly**: crops consume their cell's water; channels draw litres (§2.2). Open: dry-native churn on player water is free forever (OQ-8) |
| 8 | Rain waves a gameplay hazard (High) | **Partly**: Utinni adds no rain (WP1); rain stays on biomes that have it, whose natives are wet (no rupture). Residual: rupture at 1 in 3 is higher than C's 15%, so a flood is more dangerous; pawn-harm ceiling stays (MEASURED `burstHurtsPawns`, `ExplosiveGrowthMod.cs:86`) |
| 9 | WP3 replaces plant identity with biome (High) | **Mitigated**: biome seeds, sheet row decides (§4.3) |
| 10 | Per-plant vs cell event identity (High) | **Moot**: cycles are per plant per maturity; no event identity |
| 11 | Rain history and roofs (High) | **Simplified**: WET while raining on unroofed ground; after-rain persistence OQ-9 |
| 12 | Perf costs remain (High) | **Open**: §7 brakes + §11 test |
| 13 | Permanent-water cache holes (High) | **Mostly moot**: the cell itself only, terrain-def lookup, no radius cache |
| 14 | Fire flush expires on empty ground (High) | **Open**: OQ-11 |
| 15 | Wood classification (High) | **Resolved** (EC1, §5.1); yields go to `PLANT_ECONOMY_TUNE_EVERY_NUMBER_AT_ONCE` |
| 16–22 | Medium/low (vanilla claims, crop XML attribution, flood survival `destroyedByFlooding`, labour figures, density classes, chemistry precedence, small engineering) | chemistry resolved by T2; flood survival: a flood-killed plant has nothing to accelerate, accepted; density classes stay open (C7); the rest are build-time care |

---

## 11. Perf test the full-map wave needs

Bar (ruled S0-6): **≥ 90% of mechanic-off TPS**. Everything else PROPOSED.

- **Method:** paired A/B on the same save, mechanic on vs `enabled = false`, 3 runs each, fixed seed, one in-game
  day at max speed, game unpaused, no pawns drafted. Report median TPS ratio, p99 frame time, mesh rebuilds per
  second, things spawned per day (fruit stacks, sprouts), save size and save/load time before and after the day.
- **Maps:** 250×250 and 325×325, dense ground (Webwork-density live values from the dump, not the XML), lit.
- **Cases:**
  1. **Wave, flood:** Flooded Canyon flood over a fully grown valley of dry natives (rupture 1 in 3).
  2. **Wave, rainstorm:** outside Utinni, a water rain over a fully grown, unroofed map of dry natives.
  3. **Steady, wet jungle:** a Greentide map at equilibrium, every wet native cycling at ×4.
  4. **Steady, riverside:** a river map, dry natives on mud cells churning at ×10.
  5. **Dormant desert:** a dry map at ×0.1 with the dormancy prefix: cost of the `TickLong` prefix alone.
- **Decision rule:** case 1 or 2 below 90% → turn on the §7 stagger and re-run; still below → card to the owner.
  Case 3, 4 or 5 below 90% → a build defect (no stagger applies), fix before shipping.
- **Instrument checks first** (instrument traps): prove the off run really has the mechanic off (startup line), and
  that the on run armed (count of charging plants > 0 at hour 1).

---

## 12. Open questions (card-ready, one line each)

- **OQ-1 (BC1) Should each biome also carry a water label?** (1) Yes, seven labels that seed archetypes and rain;
  one more label per biome, ~60 with twins · (2) No, plant rows only; WP3 seeds from wet biomes' rosters already ·
  (3) Yes, but descriptive only (validates content, decides nothing).
- **OQ-2 (BC2) Where do biome class numbers live?** (1) In each biome file, checked by a test against one table;
  nothing rewrites at runtime · (2) Written at game start from the table; fights Map Designer · (3) Leave as
  authored, no table.
- **OQ-3 (GM2) Does snow count as water?** (1) Melting snow waters like rain (Wasteland, Sump only) · (2) No, only
  liquid water; snowy wastes stay dry · (3) Only in Utinni's two snowy biomes, never elsewhere.
- **OQ-4 (C7) Shared density classes for biomes?** (1) Yes, five classes, new biomes only at first · (2) Yes, and
  move existing biomes on review rows · (3) No, tune each biome by hand.
- **OQ-5 "Rupture" names two things: which is the 1-in-3?** (1) Any violent death (burst, tinder, slime, or the
  contaminated rupture, per plant) · (2) Only the contaminated rupture; others never die violently · (3) Burst only;
  contaminated rupture keeps its own odds.
- **OQ-6 After fruit and sprouts, does a dry native live?** (1) Lives, shrinks back, cycles on the same cell ·
  (2) Dies, sprouts replace it (today's churn) · (3) Lives, but each cycle costs it health until it dies.
- **OQ-7 On the tidally locked world, do lit plants rest at "night"?** (1) No: always lit means always growing
  (about 1.8× more growth than vanilla's clock) · (2) Yes, keep vanilla's clock rest · (3) No rest, but only on
  Ash'karr's sunlit tiles.
- **OQ-8 Does a wild plant's cycle use up water too, or only crops?** (1) Only crops (ruled case); wild churn on
  player water is free · (2) Every fruiting plant consumes it; player water is always spent · (3) Player water also
  evaporates after a few hours whatever grows.
- **OQ-9 After rain stops, how long is open ground wet?** (1) Not at all; wet only while it rains · (2) A few hours,
  shown by puddle filth · (3) Until a plant fruits there.
- **OQ-10 Our plants outside our biomes: default?** (1) Vanilla, labelled unsupported (matches 2026-10-15) ·
  (2) Same rule, labelled unsupported · (3) Same rule only in Utinni.
- **OQ-11 How long does a burn count as fresh, and what if nothing is growing?** (1) 3 days from the fire ·
  (2) Until the first plant there matures once · (3) 3 days, restarted when a sprout appears.
- **OQ-12 A wet native away from home, or a dry native in a wet biome?** (1) Each keeps its archetype rate everywhere
  in scope · (2) Plants take the archetype of the biome they stand in · (3) Wet natives off home act as dry natives.
- **OQ-13 Does the miasma salt-line surge stay a water source?** (1) Yes, as today (fresh side waters) · (2) No, it
  is not water · (3) Only for plants adapted to miasma.
- **OQ-14 Keep the harvest jackpot and last-swing gamble?** (1) Keep both on wild plants, off for crops ·
  (2) Keep both everywhere · (3) Cut both; water is the only lever.
- **OQ-15 Which crops self-fruit?** (1) Only our natives sown as crops · (2) Every crop on wet ground, vanilla
  included · (3) None; crops are harvested by pawns only.
- **OQ-16 A vanilla crop with no water nearby: does it age?** (1) No, frozen until watered · (2) Yes, normally, so
  it dies if never watered · (3) Ages slowly (×0.1).
- **OQ-17 What is "water nearby" for vanilla crops?** (1) Within 2 cells of a source · (2) Within 6 cells · (3) The
  cell itself only, like our plants.
