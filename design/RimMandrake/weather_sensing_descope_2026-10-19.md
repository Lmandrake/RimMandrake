# Weather sensing descope — inventory and options (2026-10-19)

**Owner, 2026-10-19:** *"I would like to defer the concept of weather sensing technology,
planetary map observation of weather systems, and that entire line of inquiry, technology,
and development. Downscope this. Please assess what we already have in the game and give me
question cards on what to descope at this time."*

**Outcome (owner cards 2026-10-19):** D1 → delete the mast and its comp; D3 → Tiers 2-4 and the
main-map tier cut permanently. Done offline in `WEATHER_MAST_DELETE_BAROMETER_GOES_QUIET`
(deploy owed). D2, D4, D5, D6 were not asked.

Precedent already in the ledger, verbatim, from `LEANINGSCRUB_MECHANICS_BUILD_1`'s trim law:
*"Too much focus on constant advanced warning... Players arent that into it."* That item
already builds "the systems, not the instruments: no alarm buildings, no radar features, no
warning-UI". This descope applies the same direction to the whole weather line.

## Headline

| group | what it is | pieces | live in game today |
|---|---|---|---|
| **1. Sensing / forecast / observation** (being deferred) | the forecast ladder, built and planned | **4 built** (instrument building, its forecast comp, the forecast arithmetic and its fuzz tests, the folk-sign text) + **4 planned only** (Tier 2 station, Tier 3 radar-analog, Tier 4 orbital layer, the owner's "seen on the main map" second tier) + **2 reference docs** | **1**: the instrument mast is buildable now (`mandrake.rm.weathersuite` is active). The folk signs are deployed but their mod is **not** in the active list. |
| **2. Weather itself** (stays) | storms, auroras, weather defs, gales, plumes, weather effects on senses | ~20 mods carry weather defs; WeatherSuite's own terminator front and nightside aurora | yes, per mod |
| **3. Hazard tells** (stay unless you say otherwise) | readable signs that warn of a hazard; the standing rule is *no animal or pawn ever vanishes without a readable sign* | ~20 tell mechanisms across 15 mods (table below), each with its own Mod Settings row | yes, per mod |

**Nothing in group 1 is wired to a research project, a quest, an incident, a world-map layer or
another mod.** There is no weather research def and no world-map weather overlay anywhere in
`src/`. The "planetary map observation" line exists only as prose.

## Group 1: sensing, forecast and observation (the deferred line)

### 1a. `RM_WS_WeatherInstrument`, the weather instrument mast (BUILT, LIVE)

- **Path:** `src/RimMandrake/WeatherSuite/Defs/ThingDefs_Buildings/ThingDefs_WeatherInstrument.xml`
- **Plain words:** a 20-steel mast in the Misc build menu. When you select it, its inspect pane shows
  "Instrument reading — likely next: X (~N%), then Y (~M%)", or "front-forced weather incoming —
  X" when a game condition forces the weather. It borrows vanilla's drop-beacon art. **No research
  gate**: it is buildable from day one.
- **Shipped/loaded:** deployed to `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WeatherSuite\`
  (byte-identical to the repo); `mandrake.rm.weathersuite` **is** in the live `ModsConfig.xml`
  (535 active, parsed 2026-10-19; ModsConfig describes the next load).
- **What depends on it:**
  - `src/RimMandrake/WeatherSuite/validation.py`, the `weather_instrument_reports_a_live_forecast_reading` chain (spawns it by defName).
  - `design/validation_walks/RimStarWars/WeatherSuite.md`, steps 8 and 9.
  - Savegames: the defName appears in **68 of 345 saves** (grep, 2026-10-19), including
    `CANONICAL_ASHKARR_START_2026-09-12.rws`, only inside Vanilla Trading Expanded's price-history table
    (`TradingManager/priceHistoryRecorders`) or CaravanAdventures' `packUpFilter/allowedDefs`. No save has one built.
  - Docs that only name it: `design/RimMandrake/flowworks_map_controls_design_2026-10-16.md` (one table row),
    the mod-audit registry under `design/RimMandrake/mod_audit/`, `infrastructure/state/art/def_history.json`.
- **What removing it would break:** deleting the def gives every one of those saves one
  "could not load reference" warning when VTE reloads its price table. That is harmless, but it is
  noise in exactly the saves we use most. The validation chain and walk steps 8–9 would need deleting
  in the same change. Making it unbuildable while keeping the def breaks nothing.

### 1b. `CompForecaster` / `CompProperties_Forecaster`, the instrument's brain (BUILT, LIVE)

- **Path:** `src/RimMandrake/WeatherSuite/Source/WeatherSuiteHook.cs` (the last ~100 lines), compiled into
  `src/RimMandrake/WeatherSuite/Assemblies/WeatherSuiteHook.dll`.
- **Plain words:** a read-only copy of vanilla's weather-choice odds. It touches no RNG and does nothing per
  tick. It runs only when the mast is selected.
- **Depends on it:** only 1a. The **same DLL** also holds the terminator front, the nightside aurora
  and `WeatherGeometryUtility.ArcFromSubstellar`, which **`mandrake.rut.patches` (UtinniPatches) hard-depends on**
  (`src/RimUtinni/UtinniPatches/About/About.xml` lines 31 and 43; `GeothermalDensityField.cs` calls it).
- **What removing it would break:** removing the class means rebuilding the DLL, a new `.srchash`, re-dirtying
  `WeatherSuiteHook.cs` for code review, and the steps in 1c. The mod as a whole **cannot leave the mod
  list**, because UtinniPatches needs the DLL.
- **Mod Settings:** none. `WeatherSuiteSettings.cs` says so on purpose: *"nothing to turn off that isn't already
  'don't build the building'"*.

### 1c. The forecast arithmetic and its tests (BUILT, offline only)

- **Paths:** `RM_WeatherKernel.TopShares` in `src/RimMandrake/WeatherSuite/Source/Kernel/RM_WeatherKernel.cs`;
  the `forecast` fuzz family in `src/RimMandrake/WeatherSuite/Source/SelfTest/WeatherFuzz.cs` and `Program.cs`;
  6 forecast mutants in `src/RimMandrake/Utils/mutate_weathersuite_fuzz.py`; the "hand copy of the forecast sort"
  lint in `src/RimMandrake/Utils/lint_weathersuite_defs.py`; runner `src/RimMandrake/Utils/selftest_weathersuite_fuzz.py`.
- **Plain words:** the top-two percentage maths and the tests that keep it honest.
- **What removing it would break:** nothing in game. Removal would have to edit four test files at once, or the
  mutation run would report mutants that no longer apply. If 1a/1b stay dormant, these stay too.

### 1d. Folk signs, `AshkarrWeather_FolkSigns.xml` (BUILT, DEPLOYED, NOT LOADED)

- **Path:** `src/RimUtinni/AshkarrWeatherSuite/Patches/AshkarrWeather_FolkSigns.xml` (Tier 0 of the ladder).
- **Plain words:** it rewrites the description of five vanilla weathers (Clear, Fog, DryThunderstorm, SnowGentle,
  SnowHard), adding a sentence such as *"count the gap between flash and crack…"*. It is text only, with no mechanic.
- **Shipped/loaded:** deployed to `…\Mods\AshkarrWeatherSuite\`, but **`mandrake.rut.weathersuite` is NOT in the
  live ModsConfig** (the mod audit lists it as `OURS_ABSENT_INSTALLED`). So players see none of this text today.
- **Depends on it:** `design/validation_walks/RimUtinni/AshkarrWeatherSuite.md` steps 3–8 and
  `src/RimUtinni/AshkarrWeatherSuite/validation.py`.
- **Entanglement:** the same mod also ships **`WeatherGeometryDefs_Ashkarr.xml`, the planet's only
  `PlanetGeometryDef`**. That is weather itself, not sensing. Dropping the whole mod would be wrong; only the one
  patch file is group 1.
- **Is it a tell?** No. It is flavour on weathers that are not hazards. It is the "Tier 0 observation" rung, so it belongs
  with this descope. (It is also arguably harmless lore. Hence a card.)

### 1e–1h. Planned only (NOT BUILT, NOT FILED)

| id | where | plain words |
|---|---|---|
| 1e Tier 2 weather station | `design/Jawa/proposals/weather_suite_deep_design.md` §8 table, Build-ladder "v2" | a powered building giving a short local forecast and reading the pressure tide |
| 1f Tier 3 radar-analog | same, §8 and "v2" | a grounding-mast array that tracks the terminator front and gives glass-storm arrival windows |
| 1g Tier 4 orbital/high-altitude layer | same, §8 and "Dream" | a gravship-borne whole-planet weather layer |
| 1h owner's "second tier: seen on the main map" | same, ruled table line 43 (`wea:forecasting-ladder`, v1); frozen source `design/Jawa/worldbuilding/review/proposal_suite_review.decisions.json` | *"just have one or maybe two tiers only… The first one might just give advanced warning. The second allows them to be seen on the main map"* |

**No ledger item, code, def, texture or world layer exists for any of these four.**

### 1i. Reference documents (prose only)

- `research/Jawa/rimworld_weather_mod_concepts.md`: §1 Planetary Weather Layer, §2 hurricane world-map presentation,
  §4 Forecasting as Technology (Tiers 0–4), §13 Smoke Forecasting. It is cited by `weather_suite_deep_design.md`,
  `fire_ecology_deep_design.md` and `ship_shields_deep_design.md`. Research notes are history; this descope does not
  require editing them.
- `design/Jawa/proposals/weather_suite_deep_design.md` §8 plus its Build-ladder paragraph: this is **live design**
  that still says Tier 2–3 is v2 and Tier 4 is Dream. It needs a "deferred, owner 2026-10-19" mark once you decide.
- `src/RimMandrake/WeatherSuite/About/About.xml` description: still advertises "a Tier-1 forecast-instrument" and "Tier 2-4
  forecasting… awaiting PROPOSAL_SUITE_REVIEW_1". It must be corrected to match whatever you decide.

### Ledger state of group 1

| item | state | note |
|---|---|---|
| `WEATHER_SUITE_SLICE_1` | superseded (2026-09-02) | built Tier 0–1; superseded by the item below |
| `WEATHER_SUITE_V1_PROMOTIONS_1` | dropped | glass storms / static seasons / spore blooms. That is **weather itself**, not sensing, so this descope does not touch it |
| any Tier 2–4 / main-map item | **none filed** | nothing to drop |

So **there is no live ledger item to drop.** The only ledger actions are optional (see the end).

## Group 2: weather itself (stays, listed for clarity)

- WeatherSuite's `RM_WS_TerminatorFront` (a permanent storm wall) and `RM_WS_DarkAurora` (incident, condition and thought),
  plus their three Mod Settings rows.
- Weather defs in Abyss, BlueDesert, Cauldron, Contagion, CrackedLands, LanternDeeps, Miasma, SolarMirrors,
  Stillsand (dune gale), Greentide, FeverWood, Wasteland, EnvironmentalHazards (scald steam, vent flash) and others.
- `RM_WeatherSenseExtension` (`src/RimMandrake/CreatureBehaviors/Source/RM_WeatherSenseExtension.cs`): despite the
  name, this is **weather acting on creatures' senses** (sun factor, sand-swimmer sensing, rumble drowned out). It is
  group 2, not sensing tech.
- `RM_Geophone` (Stillsand) senses **creatures** under sand, not weather. Out of scope.

## Group 3: hazard tells (a readable sign is REQUIRED; not descoped unless you say so)

Every one of these is a warning tied to a hazard, and each has its own Mod Settings row:

| mod | tell (Mod Settings label) |
|---|---|
| WeatherSuite | terminator-crossing letter (`MapComponent_TerminatorBand`, sent once) |
| Contagion | rattlegrope / gawpsack tells before a Burn (*"the tells are the forecast"*, ruled at its sitting) |
| Wasteland | "Named storm warnings" plus warning length |
| TheForge | "Warning letters" (cycle telegraph); "White plume fronts" |
| Cauldron | "...and warn me when it does" / "...when the vents go quiet" |
| Stillsand | "Singing-dune warning"; "Tell me when the dust settles"; dune gale |
| LanternDeeps | "A failing roof warns before it falls"; the aurora storm |
| DivingInteraction | "The Scald: Sail Forecast (sailors warn before a vent discharges)" (`RM_MapComponent_ScaldVentForecast`) |
| BlueDesert | "Crack warning before flora detonates" |
| NightsideIce | breach "Warnings"; thermal-signature alert |
| Scarlands | "Tetchik jar warnings" |
| LongShade / LeaningScrub / TerminalBiomes / Sarlacc | clean-patch tell; venomvine "rears and tells"; channel first-entry warning, scrape-sign; "Swallows leave a sign" |

The **Sail Forecast** and the **Contagion tells** use the word "forecast", but both are creatures
behaving before a hazard, which is exactly the readable sign the standing rule demands. Gene `RM_Gene_B6_PetrichorGland`
(UtinniPatches) already had its forecast stripped (`[SIMPLIFIED]`, now a flat trade). **Recommendation: none of
group 3 is touched by this descope.**

## Side finding (weather itself, not sensing; reported, not acted on)

`mandrake.rut.weathersuite` is absent from the live ModsConfig, so **no `PlanetGeometryDef` loads**. By the code
(`WeatherGeometryUtility.ActiveGeometry`), this means the terminator front and the nightside aurora never trigger, and
UtinniPatches' `GeothermalDensityField` fails open (vanilla density planet-wide, no nightside zero). This is INFERRED from
ModsConfig plus the source; the warning line was not found in today's `Player.log` / `Player-prev.log`, and it fires lazily.
Whether this is deliberate is not recorded. Candidate item name (namecheck OK): `ASHKARR_GEOMETRY_WIRE_SUN_STILL_UNPINNED`.

## Decisions for question cards

**D1. The weather instrument mast (`RM_WS_WeatherInstrument`), the only live sensing content.**
- (a) Keep it as it is. It costs nothing and works today, but it contradicts the deferral.
- (b) **Make it unbuildable** (remove `designationCategory`; def, comp and tests stay). One XML line, no rebuild, saves stay
  clean, easy to revive. The validation chain still spawns it by name.
- (c) Delete the building and its comp. The cleanest result, but it needs a DLL rebuild and code review, deleting the
  validation chain and walk steps, deleting the forecast fuzz and mutants, and it adds a load warning in the saves that name it.
- (d) Hide it behind a new Mod Setting, off by default. It needs new C# plus a rebuild, and it adds a switch for a feature
  nobody uses.

**D2. The folk-sign text (Tier 0, deployed, not loaded).**
- (a) Leave it. It is invisible while its mod is off the list, and it is harmless lore if the mod is switched back on.
- (b) Delete the one patch file, plus walk steps 3–8. Keep the mod for its planet geometry.
- (c) Keep it but relabel it as plain lore, so it is not "Tier 0 of a ladder", and strip the ladder wording from its header.

**D3. The planned Tier 2 / 3 / 4 and the "seen on the main map" tier.**
- (a) **Defer: mark §8 and the Build ladder "deferred by owner 2026-10-19"**, keeping the prose for a later return.
- (b) Cut permanently: delete §8's Tier 2–4 rows and the main-map line from the live design doc. The frozen decisions
  file stays as history.
- (c) Park as one v2 ledger item so the idea has a single home (`FORECAST_LADDER_DESIGN_SKY_KEEPS_SECRETS`).

**D4. The hazard tells (group 3).**
- (a) **Untouched**: they are hazard signs, required by the standing rule.
- (b) Review them case by case at a later sitting (the Leaning Scrub trim law suggests some may be too much warning).
- (c) Trim only the letter-style warnings (Forge, Cauldron, Wasteland), keeping the creature tells.

**D5. The About.xml text and the deep-design doc wording.**
- (a) Correct both to match D1–D3 in the same change (recommended; the standing rule is to correct false text on sight).
- (b) Leave them until a docs pass.

**D6 (side finding). The Ash'karr geometry mod is off the active list.**
- (a) File `ASHKARR_GEOMETRY_WIRE_SUN_STILL_UNPINNED` to find out whether that is deliberate.
- (b) It is deliberate: record why and close the question.
- (c) Ignore it for now.

## Ledger commands (NOT run)

No live item covers sensing, so nothing needs dropping. These commands would apply after the cards; fill `--by-card` with the
real question and pick:

| purpose | command |
|---|---|
| D1(b)/(c) work item | `rimflow file WEATHER_MAST_RETIRE_BAROMETER_GOES_QUIET --for FOUNDRY --target-field v1 --needs offline --title "Make RM_WS_WeatherInstrument unbuildable (or delete) per weather-sensing descope" --spec design/RimMandrake/weather_sensing_descope_2026-10-19.md --by-card "<D1 question → pick>"` |
| D2(b) work item | `rimflow file FOLKSIGNS_RETIRE_GOSSIP_HUSHED --for FOUNDRY --target-field v1 --needs offline --title "Remove AshkarrWeather_FolkSigns.xml; keep the geometry def" --spec design/RimMandrake/weather_sensing_descope_2026-10-19.md --by-card "<D2 question → pick>"` |
| D3(c) park | `rimflow file FORECAST_LADDER_DESIGN_SKY_KEEPS_SECRETS --for BENCH --target-field v2 --needs owner --title "Weather forecast ladder Tier 2-4 + main-map observation: deferred by owner 2026-10-19" --spec design/RimMandrake/weather_sensing_descope_2026-10-19.md --owner-said "I would like to defer the concept of weather sensing technology, planetary map observation of weather systems, and that entire line of inquiry, technology, and development."` |
| D6(a) | `rimflow file ASHKARR_GEOMETRY_WIRE_SUN_STILL_UNPINNED --for FOUNDRY --target-field v1 --needs offline --title "mandrake.rut.weathersuite inactive: no PlanetGeometryDef, terminator front/aurora/geothermal gate inert" --why "found during the weather-sensing descope assessment"` |
| historical items | none. `WEATHER_SUITE_SLICE_1` is already superseded and `WEATHER_SUITE_V1_PROMOTIONS_1` is already dropped (and covers weather, not sensing). |

Before filing, check each flag against `rimflow file --help` and the `using-rimflow` skill (`--target-field` vs `--target`).
