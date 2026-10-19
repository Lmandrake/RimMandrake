# 04 — Scope cuts: what to stop building so v1 can ship (2026-10-19)

*Final after GPT enrichment (§9). The numbers in §1, §3 and §6 include the GPT finds that were verified against the repo.*

FOUNDRY, offline, read-only on the ledger, the game and the bridge. The owner asked (2026-10-19) for a second deep
pass entirely about **scope cuts**: *we were very ambitious, and building is much slower than expected because every
feature needs so much testing.* Nothing in this file is decided. Every cut that touches something he ruled IN needs
his word, and his ruling is quoted next to it.

Labels: **MEASURED** = read today with the named instrument. **RECORDED** = another doc says it (cited).
**ESTIMATED** = a judgement. **UNMEASURED** = nobody has measured it.

---

## 1. Executive summary

- **The queue is not converging.** MEASURED (ledger shards, 2026-10-06 → 10-19): **992 items filed, 323 closed,
  43 dropped**. We file three items for every one we close.
- **874 items are open, and 872 of them say v1.** One says v2. MEASURED (`model.replay`, as-of 2026-10-19T17:08Z).
  The v2 bucket is effectively unused, so everything competes for v1.
- **Testing is the bottleneck, not code.** 438 open items are already **built or validated** and wait only for live
  rows. They owe 919 of the **922 owed live rows**; the other 3 sit on `doing` items. All 922 by level: L1 152 · L2 518 · GREEN-MIN 105 · GREEN-FULL 10 · L3 52 · L4 85. MEASURED. The
  last 7 ledger days recorded 187 `verify` events of any result. That is a count of verify events, not of rows
  discharged. Read it as: the existing debt alone is on the order of weeks of pure verification, before anything new is
  filed. ESTIMATED.
- **One system is most of the weight.** FlowWorks is 93,455 lines of C#, 51,016 lines of Python (40,140 of it test
  harness, 519 required checks), and 86 open items owing 127 live rows. MEASURED (`wc -l`, census). Its finish board
  put the narrow finish at 9–13 agent-days and the "everything filed" scope at **+25 to 40 agent-days**. RECORDED,
  `design/RimMandrake/flowworks_finish_board_2026-10-18.md` §4–5.
- **39 of our mods are built but not in the game.** They are neither active in the live `ModsConfig.xml` (536 mods,
  parsed) nor composed into Baroque Biomes. Together they hold 42,062 lines of C#. MEASURED. They still carry open
  items (about 27 that name them directly, 46 live rows).
- **The proposed cuts in §3 remove 268 open items (31%) and 356 owed live rows (39%)** from v1. That includes C15, 26 items
  and 85 rows that GPT found and that were verified against the repo (§9). A testing-regime change (§3, T) converts another **173 rows** from live
  proof to offline selftest plus owner play. Together that is **about 529 of 922 live rows (57%)**. MEASURED by an id-pattern script over the census (§8); the patterns are a
  judgement, so treat the counts as ±10%.
- **The game's own design argues for most of these cuts.** The campaign is *"Land → … temporary camp → … decide what
  to leave behind → launch → repeat. The permanent colony lives aboard; planetary camps are disposable."*
  (`design/Jawa/reconciled_lore/01_campaign.md`). Deep base-building on the ground (bridges, sprinklers, tall tanks,
  trench warfare, canopy shade simulation) serves a colony that, by design, leaves.
- **Weather.** The descope the brief describes as "the planetary weather system was descoped completely" is
  **narrower than that** in the ruling. The owner cut weather **sensing** (forecast mast, forecast Tiers 2–4,
  planetary-map observation). The same day he ruled weather itself **ON**: *"Not deliberate, turn it on"*. Details,
  residue and the contradiction are in §2.

**Top recommendations, in order:** (1) change the testing regime, (2) move FlowWorks' full-scope extras to v2,
(3) retarget every open item of the 39 inactive mods to v2, (4) move world/lore extras and Warscar extras to v2,
(5) move the optional biome side-systems GPT found to v2 (light/pigment, Stillsand side activities, the Cathedral
exposure arc, Greentide extras, vaults, Bacta, kinetic weapons), (6) keep the sea at its ruled minimum, (7) drop the
telemetry stack, (8) move the Bazaar and in-game LLM work to v2.

---

## 2. The weather descope: what was ruled, what is still in the tree and queue, and a contradiction

**The ruling.** Owner, 2026-10-19, verbatim: *"I would like to defer the concept of weather sensing technology,
planetary map observation of weather systems, and that entire line of inquiry, technology, and development.
Downscope this."* Then, by card (`WEATHER_MAST_DELETE_BAROMETER_GOES_QUIET`, 2026-10-19T12:12Z): *"Weather sensing:
what happens to the instrument mast? → Delete it; Tiers 2-4 and the main-map tier → Cut them permanently"*.
Assessment doc: `design/RimMandrake/weather_sensing_descope_2026-10-19.md`.

**What it covers.** It covers only group 1 of that doc:
- the forecast mast `RM_WS_WeatherInstrument`;
- its comp `CompForecaster`;
- the forecast maths, fuzz family and mutants;
- the planned Tier 2 station, Tier 3 radar-analog and Tier 4 orbital layer;
- the "seen on the main map" tier.

It explicitly **does not** cover:
- group 2, weather itself: `RM_WS_TerminatorFront`, `RM_WS_DarkAurora`, every biome's weather defs, and
  `RUT_WS_AshkarrGeometry`;
- group 3, the hazard tells.

**Same day, the opposite direction for weather itself.** By card (`ASHKARR_WEATHER_INSTALL_THE_SLEEPING_STORMS`,
2026-10-19T12:34Z): *"Weather Suite mod inactive, storms/aurora off - deliberate? → Not deliberate, turn it on"*.

**State today (MEASURED 2026-10-19):**

| piece | in the tree | deployed / loaded | ledger |
|---|---|---|---|
| Mast def, `CompForecaster`, forecast maths/tests | **deleted** (`src/RimMandrake/WeatherSuite/Defs/` has no `ThingDefs_Buildings`; DLL rebuilt c89d78695) | deployed copy's `ThingDefs_Buildings` folder is empty; the deployed `WeatherSuiteHook.dll` is byte-identical to the repo (`cmp`) | `WEATHER_MAST_DELETE_BAROMETER_GOES_QUIET` done; **`WEATHERSUITE_DEPLOY_MAST_LEAVES_THE_BUILDING` still `proposed`, although the deploy has landed** (stale) |
| Tiers 2–4, main-map tier | prose only, struck in `design/Jawa/proposals/weather_suite_deep_design.md` (lines 43, 320) | — | no items (never filed) |
| `WeatherSuite` (terminator front, dark aurora, `PlanetGeometryDef` type, `WeatherGeometryUtility.ArcFromSubstellar`) | present, 734 C# lines | `mandrake.rm.weathersuite` active | stays; `PLANET_GEOMETRY_WIDEN_SUN_STANDS_STILL` (proposed) **builds on it**, and Sun & Shade reads the sun angle from it |
| `AshkarrWeatherSuite` (`RUT_WS_AshkarrGeometry`, the planet's only `PlanetGeometryDef`) | present | **`mandrake.rut.weathersuite` is now active** (536-mod list) | `ASHKARR_WEATHER_INSTALL_THE_SLEEPING_STORMS` still `proposed` (the install happened at the 13:03Z relaunch; its live check is owed) |
| Folk-sign text `AshkarrWeather_FolkSigns.xml` (Tier 0 of the cut ladder) | **still present** (D2 was never asked) | **now loaded**, because its mod was switched on for the geometry | no item |
| `UtinniPatches` hard dependency on the WeatherSuite DLL (`GeothermalDensityField`) | present | — | the DLL cannot leave the list |

**Contradictions to report:**
1. **The brief vs the ruling.** "Planetary weather system descoped completely" is not what was ruled. Only the
   sensing line was cut. Weather itself was turned **on**. If the owner now means all of weather, that is a **new**
   ruling, and §3 row W2 sizes it.
2. **The ladder's bottom rung is now live.** The folk signs are "Tier 0 of the forecast ladder" per the descope doc.
   They were **not** themselves cut: D2 was never asked. Still, they became visible to players today as a side effect
   of turning the geometry mod on, which is new exposure nobody chose. Cheapest fix: delete the one patch file and walk steps 3–8 (D2(b) of the descope doc). That needs one card.
3. **Two stale ledger states**, both listed in the table above.
4. **Hazard "warnings" vs the Leaning Scrub trim law.** *"Too much focus on constant advanced warning... Players arent
   that into it."* (2026-09-29, `LEANINGSCRUB_BEDAZZLE_SITTING_1`). The descope kept ~20 letter-style warnings across
   15 mods (D4 was not asked). The "readable sign" rule requires a sign. It does not require every warning **letter**, so
   D4 is still open. The letter-style ones (Forge, Cauldron, Wasteland) are worth one card.

---

## 3. Candidate cuts, ranked

Ranking = live rows and items saved × how little the cut costs the player experience. Counts are MEASURED from the
census (§8). "Rows" = owed live criteria (L1/L2/GREEN/L3/L4) on open items in the group. Recommendations:
**REMOVE** (drop the items, delete or leave dead code), **V2** (`rimflow retarget … v2`; nothing is deleted),
**KEEP-SIMPLIFIED** (ship a named minimal version), **KEEP**.

| # | candidate | what it adds for the player | cost to finish | test load | recommendation | minimal v1 version | what depends on it |
|---|---|---|---|---|---|---|---|
| T | **Testing regime**: per-mod "first north-star script" rows, review-finding fix rows (titles `Mod: …`), settings-toggle proof rows | nothing directly; confidence | each row needs a staged live run; the queue shows 32 first-script items, 89 finding items and 32 toggle items not already in a cut below | **173 rows** (L2 70, GREEN-MIN 56, L1 38, L4 8, L3 1) | KEEP-SIMPLIFIED (process) | a finding fix closes at L0 (selftest/fuzz/mutant) plus the owner playing; GREEN-MIN only for mods in the spine; toggle proofs only at shipped defaults, all-off, and genuinely distinct runtime paths (FlowWorks alone has 157 toggles, finish board F2); no combinatorial matrix | `NORTHSTAR_EVERYWHERE_PROGRAM_1` (owner 2026-10-01) must be re-scoped; FOUNDRY.md already says *"the owner playing is the default validation"* |
| C2 | **FlowWorks full-scope extras**: 7 suspension-bridge builds, trench cover, raider trench, big-creature walls and slots, thirst/bottles/containers/tall tanks/four-style tank looks, sprinklers, river toggle proofs, dev map controls, quarry digging, liquid industry set-pieces, lava, pit access extras (carryable ladder, climbing gear, wall scaling), guardrails, pit temperature, art polish | real but secondary: ground infrastructure for a camp the design says you leave | +25 to 40 agent-days (RECORDED, finish board §4) | **51 items, 98 rows** (L2 67) | **V2** (needs his word) | the "one big dig": exactly-level water, metres/litres, canals, pumps, hoses, wells, superdeep pit + wall ladder + fall damage; thirst left to Dubs (his own card: *"Dubs' runs, ours steps aside"*) | `SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT` (validated) stays as a refactor; `TITAN_TRENCHES_WIRE_MIND_THE_GAP` falls with big creatures; `LIQUID_THIRST_CHAIN_1` and `LIQUID_BOTTLE_LOOP_1` go together |
| C5 | **39 built-but-inactive mods** (SolarMirrors 5,680 C#, Watchers 3,426, KeelHoist 2,915, UnfinishedLine 2,892, TheBazaar 2,179, AtmosphericBase, LoreStages, Sarlacc, RaidRedesigner, Warcasket, Atlas, ShipShields, OasisMaker, PropaneLakeMechanics, AcousticScanner, SithLine, BrainWorms, …) | none today: the player never loads them | their open items | **27 items, 46 rows** | **V2** (Sarlacc needs his word: he named its four kinds, *"Seeker digger dreamer devourer"*, 2026-09-26, `SARLACC_HABITAT_BUILD_1`) | none in v1; code stays on disk | Warcasket↔WasteRun; KeelHoist↔`FORGE_KEELWORK_REMAINDER_1`; AssailantSalvage↔`GELATINOUSSLIME_VAULT_SEAL_BREACH_1` (*"seal does not exist"*) and the war lab; Bazaar → C4 |
| C14 | **World and lore extras**: the war lab (specimens, garrison, crater hook), fall-zone lost-cargo quests, feral survivor pawnkind, minerals-where-they-belong, event-trace props library, Rakatan archotech machines, map landform mutators design, Force-disturbance reflavour, scrapnest theft, Wyyyschokk pendant, throat cask, mindstone | flavour and set-pieces | design and build each | **16 items, 26 rows** | **V2** (scrapnest theft needs his word: *"Yes they steal everything, and there are also stealing raids."*, 2026-10-10) | — | not here, on purpose: `HORRORS_RAIDING_FACTION_1` (a faction absent at the freeze is absent forever), `GM_BLACKBOARD_SHADOW_M4_1` (the Empire clock is a spine pressure), `WARLAB_CRATER_ACCIDENTAL_TRIGGER_1` (a live bug: fix it, or delete the reactor core with the war lab) |
| C9 | **Warscar extras**: old tongue, pilgrim journals and camps, hospice deserters, Open Boast rite, rainbow pools, totchak, turret tracking, chotrix signs, aerosol screen | flavour depth in one biome | high (several are C#) | **12 items, 24 rows** (L2 17) | **V2** | Warscar ships as roster + terrain + weather + ruins | chotrix signs need `FOOTPRINT_TRACK_GRID_1` (also V2) |
| C10 | **Titans and slime extras**: titan wake/roof/breakthrough fixes, corpse-site safety, titanoslime, slime chunk bomb, vault seal breach, Joining Water rite | spectacle | medium | **13 items, 16 rows** | **V2** | slime as a liquid and terrain; titans spawn and walk | big-creature walls are counted in C2 |
| C6 | **Sea depth beyond the ruled minimum**: per-sea floor biomes, 32-species fish bestiary, Twilight bottom cast, useless-artifact plot, Brine Elder trade, garden escalation, specimen cabinet, tow line, alloy forge, twilight wells | wonder, in a side layer | high | **17 items, 13 rows** | **KEEP-SIMPLIFIED** | the ship flies to `RM_SeabedLayer` and back (`SEABED_DESCENT_ASCENT_1`); **one** shared floor biome; fishables alive on it (ruled) | `SEA_DIVE_HATCH_REMOVE_1` waits on descent, so keep descent |
| C12 | **Graffiti remainder**: north-star trial chain, imperial graffiti, designator choice, punk art review, sigil frames | flavour | low to medium | **10 items, 11 rows** | **V2** (needs his word: forks F1–F10 were ruled by card 2026-10-09) | the two build waves already landed (RECORDED, `design/RM_GRAFFITI_SCOPE_WIDENING.md`) | `GraffitiImperial` is inactive |
| C3 | **Telemetry, health metrics, TPS dashboards** (VictoriaMetrics + SQLite + Grafana, colony vitals, away dashboard, health bands) | none for the player | medium | **14 items, 9 rows** | **REMOVE** | keep the existing TPS record as it is | his own words: *"Minimal is good, add functionality as needed by debugging."* (2026-10-11) |
| C4 | **The Bazaar trade window + in-game LLM** (grid, price engine, haggle duel, broker tab, banter, displacement of Trade UI Revised/VTE; kyber plot; LLM raid redesigner; Oracle) | a nicer trade screen; voices | 5 slices, 4 of them blocked | **13 items, 4 rows** (mostly unbuilt) | **V2** (needs his word) | vanilla trade window plus the trade-UI mods already loaded | `BAZAAR_DISPLACEMENT_PASS_1` would retire VTE; without it VTE stays |
| C7 | **Tree-crown shade model, canopy zoom layer, shadecraft lessons, tree burst, own tree graphics** | correct shade in forests | about 4.5 agent-days for the crown model (RECORDED, `tree_shade_model_2026-10-19.md` §5) | **11 items, 4 rows** | **KEEP-SIMPLIFIED** (needs his word) | Direct Sun by geometry everywhere, **off on tree-heavy maps** (option (d), ~0.5 day, same doc) | his ruling calls (d) *"an inferior option"*; Direct Sun's live rows need the choice |
| C8 | **Explosive growth beyond the owner's original idea**: terminal moments, charge/burst kernel fixes, flood-witness event | spectacle he did not ask for | 12 open items; 5,004 C# lines | **12 items, 3 rows** | **KEEP-SIMPLIFIED** (needs his word for tree bursts: *"Every tree that hits a water-driven death bursts."*, 2026-10-17) | his original rule: *"barely grow at all until they get access to water, then they grow x10"* (2026-10-16) | `TREE_BURST_*` (in C7) and `FLOOD_WITNESS_EVENT_1` fall with it |
| C11 | **Art polish**: icon outline repaint (~141), 63 desiccated corpses, pack overlays, canon drain, statue expansion, facings redraws, flyer variants and flip-books, sheet tooling | looks | artpipe time, owner review time | **28 items, 0 rows** | **V2** | art already accepted as-is (ruled 2026-10-18/19) | none in code |
| C13 | **Process programmes**: north-star everywhere/partial gaps/adversarial review/skill/retro, validation retrofit, human exploration pass, art-override family script, materials review, macro generator v0, discovery achievements, loadscreen renders | none for the player | open-ended | **14 items, 4 rows** | **REMOVE or V2** | — | the testing regime T replaces the north-star programme |
| W1 | **Weather folk signs** (now live by accident, §2) | lore text | one file + walk steps | 0 rows | **REMOVE** (one card) | — | none |
| W2 | *If* the owner now means **all** planetary weather: terminator front, dark aurora | the dayside/nightside storm wall | small; built | 0 items open | **KEEP** (built, cheap) | as is | Sun & Shade and UtinniPatches need the WeatherSuite DLL and `PlanetGeometryDef`, so the mod cannot leave the list either way |
| B | **Secondary mechanics of the not-yet-ready biomes** (Stillsand 30 open/38 L2, Rust Cathedral 19/27 L2, Sea 29, Leaning Scrub 24, FeverWood 15/16 L2, Greentide 10/16 L2, Sump 14, Forge 11, Scald 10, Rot 9) | each biome's signature | high in sum | 200+ items. The split into signature vs secondary is **UNMEASURED** | **KEEP-SIMPLIFIED**, biome by biome | per biome: roster + terrain + weather + **one** signature mechanic + its hazard sign ("Everything ships THIN except the gravship", `infrastructure/state/V1.md`) | he prefers *"carefully handle biome by biome"* (2026-09-22): one short card per biome, not a sweep |
| C15 | **Optional biome side-systems (found by GPT, verified §9)**: LuminousPigment light/deepfire system and the light ledger; Stillsand precious caves, cave-as-place, sand sieve, sun lance, geophone; the Rust Cathedral exposure/regard/hum arc and hull bolts; Greentide stellock lace, thurrock herd, humming grove, greatbole crossovers; kinetic-blast weapons; the six Forsaken vaults and their thaw quests; Bacta tank and revival; FeverWood brood ransom and Kurreth columns; orphans of other cuts (footprint grid, spore screen, egg broker, cradle strike, waste-run stubs) | optional depth, one biome at a time | each is its own subsystem | **26 items, 85 rows** (L2 60) | **V2** (needs his word for kinetic weapons: *"fully build the Thump weaponry and the Explosive Kick mods start to finish"*, 2026-10-07; and for Bacta revival, ruled IN in its title) | each biome keeps its signature (B) | orphans follow their parents (C4, C9, C14) |
| C16 | **GimmeSomeSlack leftovers**: MessyConduit-era items (`MESSY_CONDUIT_MOD_1`, cable-pile look, review round 1), power theft, the mixed-style probe | polish on a validated mod | small | **5 items, 13 rows** | **V2**, or close as superseded by *"GimmeSomeSlack all looks great! Verified."* (2026-10-16), after one read of each | GSS as validated | none |

**KEEP (the spine, §4):** factions, ideoligions, xenotypes and pawnkinds; the gravship; the world map and the
paint-once; Pyrelands (validated, 20/20 bars); the sprint biomes (Leaning Scrub, Cauldron, Contagion); GimmeSomeSlack
(validated 2026-10-16); FlowWorks core; Direct Sun (geometry); Creature Behaviors core; droids; donor retirement
and Cherry Picker (these *reduce* load time and test load); Mod Settings (the screens that exist, and the switches the 2026-09-12 ruling requires per major feature; **freeze additions**).

---

## 4. The v1 spine: the smallest set that is still the game

Measured against the campaign brief (`design/Jawa/reconciled_lore/01_campaign.md`) and the v1 gate
(`infrastructure/state/V1.md`: *"the eight rows seen working in the game once, plus the full faction roster, plus one
playable session"*; gate row 3 was deleted 2026-08-15, so the gate is now **seven** rows):

1. **The start**: the canonical save on a donor-free list; the gravship (ships DEEP); the founders; Zeddo's Yard.
2. **The freeze-critical content** (cannot be added after the world is saved): the faction roster, ideoligions,
   xenotypes, pawnkinds, settlement and landmark names.
3. **The planet**: Ash'karr as authored, painted once at the end with every Baroque biome's BiomeDef present.
4. **The three pressures that force motion**: Empire pursuit, Hutt ledger, Ta'Baa's clock. These already exist as
   rules and lore. Their *mechanics* coverage is UNMEASURED here. Keep at least one pressure → departure loop that
   has been **observed** working: `EMPIRE_ESCALATION_LADDER_1` (validated, owes L2 5 + L4 1). `GM_BLACKBOARD_SHADOW_M4_1`
   (Imperial heat + orbital timer) is a Python shadow, not a mod; it is kept out of the cuts.
5. **Water as the master resource**: FlowWorks core (level water, depth in metres, canals, pumps, hoses, wells,
   tanks), with thirst from Dubs Bad Hygiene Lite.
6. **Baroque biomes, thin**: every biome's roster, terrain, weather, one signature mechanic and its readable hazard
   sign. Pyrelands is accepted (*"Ok, I'm approving this whole sheet."*, 2026-10-16). The current sprint is Leaning
   Scrub, Cauldron and Contagion, at the depth he approved by card on 2026-10-16. The Rot is next in line.
7. **Direct Sun** by geometry, with parasols and roofs as shade.
8. **Cords and power**: GimmeSomeSlack as validated.
9. **Pits** as superdeep cells with one wall ladder and fall damage.
10. **The sea**, at its ruled minimum: ship down to one seabed layer and back, fishables alive there.
11. **One playable session** by the owner: the gate.

Everything else in §3 is either v2 or simplified.

---

## 5. Cuts and their dependency effects

- **C2 (FlowWorks extras) → v2.**
  - The suspension base-class lift (`SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT`, validated) stays: it is a behaviour-
    neutral refactor already proven.
  - The seven `SUSPENSION_*` builds, `TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT` and
    `RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP` leave.
  - **This reverses an owner card from 2026-10-18** (*what counts as finished → everything filed*). The owner's own
    words on that card: *"(3) but simply accept all of your art the first time so as not to block. I can review in
    parallel."*
  - `BIG_CREATURES_DESIGN_WALLS_AND_SLOTS` was answered by card on 2026-10-19 (*"package yes; break through now…
    step over trenches < B/4…"*). Moving it to v2 takes `TITAN_TRENCHES_WIRE_MIND_THE_GAP` with it.
  - Thirst: his card *"OQ-1 whose thirst under Dubs → Dubs' runs, ours steps aside"* (2026-10-17) means our own thirst
    need only matters without Dubs. The spine has Dubs, so `THIRST_*`, `LIQUID_THIRST_CHAIN_1` and
    `LIQUID_BOTTLE_LOOP_1` can wait.
  - `HOSE_REALFLOW_DIAGNOSE_SHORT_POUR_DRY_TANK` and the level-water work stay. They are core.
- **C5 (inactive mods) → v2.** No code changes, because nothing loads them. Three couplings:
  - `GELATINOUSSLIME_VAULT_SEAL_BREACH_1` needs an Assailant seal that *"does not exist"*, so it goes too.
  - `FORGE_KEELWORK_REMAINDER_1` touches KeelHoist.
  - `STILLSAND_SOLAR_STILL_1` is a Stillsand item, not a SolarMirrors one. It is kept in B.
- **C4 (Bazaar + LLM) → v2.**
  - Without `BAZAAR_DISPLACEMENT_PASS_1`, Trade UI Revised, Utility Columns and VTE stay on the list.
  - The 2026-08-15 ruling *"all in-game LLM generation is v2"* (`design/V2_DREAMS.md`) and the 2026-09-05 transport
    ruling (*"Claude Code in non-interactive mode… can be called from a shell script without any API key"*) do not
    conflict on scope. The transport ruling says **how**; the earlier one says **when**. That reading is mine. He should
    confirm it.
- **C7 (tree crowns) → fallback (d).** Direct Sun's live rows (`DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME`) then run on
  three non-forest maps. The forest biomes (Greentide, Webwork, Long Shade) get Direct Sun off. His words:
  *"If we do not go that route, we may choose to turn it off on tree-heavy maps (this would be an inferior option)."*
  (2026-10-19).
- **C8 (explosive growth) → the owner's original idea.** The tree-burst items (in C7) and `FLOOD_WITNESS_EVENT_1`
  depend on burst behaviour and leave with it. `EXPLOSIVE_GROWTH_MERGE_COMES_HOME` (fold into Baroque Biomes) stays.
- **C6 (sea) → minimum.**
  - `SEABED_DESCENT_ASCENT_1` stays, because `SEA_DIVE_HATCH_REMOVE_1` is blocked on it.
  - `SEABED_PER_SEA_FLOORS_1` collapses to one floor biome.
  - The fish bestiary reuses existing creatures. *"All the fishables should also be alive and moving around in the
    depths (this is true for ALL seas)."* (2026-09-26) still holds; it is the minimum, not an extra.
- **T (testing regime).**
  - `NORTHSTAR_EVERYWHERE_PROGRAM_1` (*"Ticket writing basic northstar scripts for all mods… I really do mean stop and
    start working a new way."*, 2026-10-01) is narrowed to the spine.
  - The 33 open first-script items outside the cuts close at L0 plus owner play.
  - `modcheck floor` keeps reading DRAFT for the rest. That is honest: it is not a defect.
- **C3 (telemetry) → remove.** The bridge's TPS record stays (`BRIDGE_TPS_*` fixes can be dropped or kept as L0).
- **W1 (folk signs) → remove one patch file.** `AshkarrWeatherSuite` stays for its geometry def.

---

## 6. Savings estimate

| | items | owed live rows | other |
|---|---|---|---|
| all open today | 874 | 922 | — |
| scope cuts C2–C16 (union, no double count) | **268** | **356** (L2 214, L1 42, L4 39, GREEN-MIN 35, L3 24, GREEN-FULL 2) | FlowWorks extras alone: +25 to 40 agent-days avoided (RECORDED estimate) |
| testing regime T (rows on items not already cut) | 0 removed; 153 items close faster | **173** converted to L0 + owner play | — |
| **total** | **268 (31%)** | **≈529 of 922 (57%)** | — |
| tree crowns → fallback (d) | — | — | ≈4 agent-days (RECORDED: 4.5 vs 0.5) |
| inactive mods | — | — | 42,062 C# lines leave the code-review loop and the selftest sweep |

Not counted: the rest of the biome-by-biome trim (B), because the split is UNMEASURED. C15 is the part of B that GPT
found and that has been verified. At the queue's measured filing rate,
**these cuts only hold if new filings into the cut areas go straight to v2** (§7, Q3).

---

## 7. What I would want the owner to rule on

1. **Testing regime (T).** May a review-finding fix, or a first north-star script outside the spine, close on
   offline selftests plus your play, without a staged live run?
2. **FlowWorks finish line (C2).** Keep "everything filed", or finish the one big dig and move suspension bridges,
   trench cover and raiders, big-creature walls, thirst/bottles, sprinklers and the dev map controls to v2?
3. **New ideas default to v2.** From today, does a newly filed feature item land in v2 unless you say v1?
4. **The 39 inactive mods (C5).** Retarget all their open items to v2? Name any you want back in v1.
5. **Trade and voices (C4).** Bazaar and in-game LLM to v2, with vanilla trade plus the loaded trade-UI mods for v1?
6. **Direct Sun on forest maps (C7).** Ship with option (d) now and build the crown model in v2?
7. **Weather.** Did you mean the whole weather system, or only sensing as ruled this morning? Also, the folk signs
   went live today by accident: delete them?
8. **Biomes thin (B, C15).** One short card per biome: which ONE signature mechanic ships in v1? The side-systems in
   C15 go to v2 unless you name them.
9. **Testing caps (§9.3).** Adopt the six caps as standing process: live proof only at defaults, all-off and distinct
   paths; one final full-list batch; frozen shared tooling; a fixture preflight; one keeper-save load per cut; new
   discoveries default to v2.

---

## 8. Instruments, method and caveats

- Ledger projection: `src/RimMandrake/rimflow/model.py` `replay()`, 10,901 events in `infrastructure/state/ledger/events/{BENCH,FOUNDRY,OWNER}.jsonl`, as-of 2026-10-19T17:08Z. This is the same function `rimflow next` uses.
- Item → mod mapping is a heuristic: the title prefix `Mod:`, then the id prefix alias, then the most-mentioned mod folder in the item prose. 80 of 874 open items stayed unmapped ("OTHER"). Per-mod counts are therefore approximate. The cut-group counts in §3/§6 use explicit id patterns instead (script: FOUNDRY scratchpad `cutgroups.py`; the patterns are listed in the appendix).
- Lines: `wc -l` over each mod folder, excluding `obj/` and `bin/`. "Harness" lines and required checks: `src/RimMandrake/Utils/modcheck/required_checks.json` plus mod-local validation, proof and selftest files.
- Activity: the live `ModsConfig.xml`, parsed with `ET.find("activeMods")`: 536 active, of which 61 are ours. 32 more are composed into `mandrake.rm.biomes`.
- North-star state: `modcheck floor --all`. Only Pyrelands and GimmeSomeSlack are VALIDATED; every other mod is DRAFT.
- Verify history: 657 `verify` events (485 pass, 60 fail, 112 partial). 20 items went fail → pass on one criterion. The ledger does not separate a fix from flakiness. A keyword proxy puts ~27% of fail/partial events on harness, site or instrument causes (UNMEASURED beyond the proxy).
- Not measured: player-experience value. That column is a judgement against the campaign brief and is labelled as such.

---

## 9. GPT enrichment

**How.** `python3 src/RimMandrake/Utils/gpt_consult.py` (default model, effort high), 2026-10-19. GPT was given:
- the draft;
- every open item grouped by mod;
- the per-mod line and row tables;
- the cut id lists;
- the owner-rulings census;
- the testing-load census;
- `01_campaign.md`, the FlowWorks finish board, and the weather descope doc.

It was asked to find missed cuts, challenge every KEEP, flag testing-load traps, and find errors.

**Verification.** Every item id GPT named was checked against the ledger projection; all 45 exist. Owed rows were
re-read from the census, not taken from GPT's text. Legend: **ACCEPTED** (verified, now in the body),
**REJECTED** (reason given), **UNVERIFIED** (not checkable today).

### 9.1 Cuts I missed

| # | GPT's find | verdict |
|---|---|---|
| 1 | LuminousPigment/deepfire light system + `LIGHT_LEDGER_ONE_1` + `DEEPFIRE_WORLD_LIGHT_1` (19 rows) | **ACCEPTED** → C15. Ten items exist with 19 owed rows. Mostly GPT-review finding fixes on an optional system. |
| 2 | Stillsand side activities: precious caves, cave as place, sand sieve, sun lance, geophone (17 rows) | **ACCEPTED** → C15. All five are `validated` and owe L2/L3/L4. |
| 3 | Rust Cathedral exposure/regard/hum arc + hull bolts (17 rows) | **ACCEPTED** → C15. The megastructure stays. |
| 4 | Greentide stellock lace, thurrock herd, humming grove, greatbole crossovers (15 rows) | **ACCEPTED** → C15 |
| 5 | `KINETIC_BLAST_WEAPONS_1` (10 rows) | **ACCEPTED, needs his word.** He said *"fully build the Thump weaponry and the Explosive Kick mods start to finish"* (2026-10-07). |
| 6 | Six Forsaken vaults + thaw quests (9 rows) | **ACCEPTED** → C15 |
| 7 | Bacta tank and revival (8 rows) | **ACCEPTED, needs his word.** The revival item's own title cites an owner ruling. |
| 8 | FeverWood brood ransom, Kurreth columns, promised gift (8 rows) | **ACCEPTED** → C15 |
| 9 | Orphans of cuts: `FOOTPRINT_TRACK_GRID_1`, `SCREEN_STOPS_SPORES_1`, `WEBWORK_EGG_BROKER_CHANNEL_1`, `CRADLE_STRIKE_RECONCILE_WITH_LAB_DIVE`, `WASTE_RUN_STUBS_1` | **ACCEPTED** → C15. The draft called the footprint grid v2 but had left it out of the id list. That error is fixed. |

### 9.2 Challenges to each KEEP

| keep | GPT's challenge | verdict |
|---|---|---|
| gravship/start/world | merge `BIOME_WORLD_SWITCH_WAVE_1`, `BIOME_PAINT_ONCE_AT_THE_END_1`, `WORLD_REMAKE_FINAL_STEP_1` into one final act; keep `GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1` | **ACCEPTED** as a recommendation. This agrees with `03_ticket_impact.md`. |
| factions/xenotypes | keep the roster and text; defer `TECHPRINT_FACTION_GATING_1`, `XENOTYPE_CANON_CORRECTION_1` beyond what the roster needs | **UNVERIFIED.** Not read in depth today; it goes to the owner as a question, not a cut. |
| three pressures | keep one observed pressure → departure loop (`EMPIRE_ESCALATION_LADDER_1`) | **ACCEPTED** → §4 |
| FlowWorks core | bound it to one water/fuel logistics loop; `HOSE_REALFLOW_DIAGNOSE_SHORT_POUR_DRY_TANK` stays | **ACCEPTED** in spirit. That is already the C2 minimal version. The tanker loop is ruled a pillar (2026-09-13). |
| Direct Sun | disabling it globally is cheaper than a forest exception | **REJECTED as a recommendation, kept as an option.** *"no biome-specific heat, no biome-specific sun"* (2026-10-19) is a fresh, firm ruling. Q6 offers it. |
| GimmeSomeSlack | keep the accepted graphics; defer power theft and style probes | **ACCEPTED** → C16 |
| pits | defer pit-prison use | **REJECTED.** *"Should 3-deep pits work as prisons → Superdeep only, as designed"* (2026-10-16) and the item `PIT_SUPERDEEP_COLLAPSE_1` is the authority; the prison is the superdeep cell itself. `PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER` (newer card, 2026-10-18) stays. |
| sea minimum | defer diving entirely; keep surface fishing | **REJECTED as a recommendation.** *"It's ship or nothing"* (2026-09-26) and *"All the fishables should also be alive and moving around in the depths"* (2026-09-26) are ruled. Listed only as the deepest possible cut, which needs his reversal. |
| Creature Behaviors | 24,727 C# lines, 107 required checks, 5 first-script failures; keep only the cast-essential behaviours | **ACCEPTED in part.** The numbers match the census and `testload.md`. Wound link, alarm share and vermin breeding are already T2 finding rows, so T covers them. |
| Mod Settings | keep the existing screens and required switches, freeze additions; master-only reverses the 2026-09-12 ruling | **ACCEPTED.** The draft's "master switch plus tuning" is replaced (§3 KEEP line). |
| donor retirement | keep dependency severance; defer cosmetic equivalence (`DONOR_CODE_SHAPE_REBUILD_1`, `DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO`) | **ACCEPTED** as a recommendation. *"Just put in placeholder art for now or donor copies and retire these mods!!! Just get it done."* (2026-10-19) |
| droids | challenge the primitive tier and wipe severity | **REJECTED for now.** The primitive tier is IN by card (2026-10-12). It goes to the owner only if he wants deeper cuts. |
| sprint biomes / Rot | one signature each; defer the Rot sprint | **Not adopted.** The sprint depth was approved by card (2026-10-16), and the Rot is *"First biome of next sprint"*. It is listed in Q8 as his choice. |
| Pyrelands | defer `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1` | **ACCEPTED** as a recommendation: it is a proposed new build on an accepted biome. |
| expansion hooks | challenge `NORTHSTAR_PARTIAL_GAPS_FILL_1`, `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, `TREE_BURST_BUILD_LITRES_BUY_YEARS`, `PLANET_GEOMETRY_WIDEN_SUN_STANDS_STILL` | **ACCEPTED** for the first three, which are already in C13, C14 and C7. **REJECTED** for the planet geometry item: Direct Sun reads its sun angle from it. |

### 9.3 Testing-load traps, and the caps GPT proposed (all ACCEPTED; they go to the owner as Q9)

1. **Settings multiplication.** FlowWorks has 157 toggles (VERIFIED, finish board F2). Prove live only at shipped
   defaults, all-off and genuinely distinct runtime paths. Offline-test wiring, bounds and persistence.
2. **Repeated certification.** Parent trials and child GREEN items reuse one receipt. Run one final full-list batch,
   then re-test only the affected mechanisms.
3. **Harness recursion.** Freeze shared tooling (28,488 lines of modcheck plus driver, VERIFIED in `testload.md`)
   except for defects that block a kept observation. Allow one bounded repair, then change the fixture or the method.
4. **Invalid sites.** Run a short fixture preflight. Classify a setup failure apart from a product failure and abort
   at once. This matches the `TESTENV_*` family and `SPRINT_SITES_DIAGNOSE_VENOMVINE_SCRATCHES`.
5. **Couplings and save residue.** Every cut gets one def-reference audit and one keeper-save load. Keep inert defs
   where saves name them (the precedent is the mast's 68 saves in the weather descope).
6. **Expanding work.** New discoveries default to v2. A v1 filing needs a demonstrated blocker plus a named removal.
   Parents close when their kept acceptance is met, whatever their deferred children still owe.

### 9.4 Errors GPT found in the draft

| # | error | verdict |
|---|---|---|
| 1 | Savings counted `SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT`, which the draft keeps | **ACCEPTED.** It had already been excluded before the reply arrived (with `GM_BLACKBOARD_SHADOW_M4_1` and `WARLAB_CRATER_ACCIDENTAL_TRIGGER_1`, a live bug). |
| 2 | Three MessyConduit items (10 rows) sat in the FlowWorks cut, but they are GimmeSomeSlack's | **ACCEPTED** → moved to C16 |
| 3 | 922 rows are not all on built/validated items, and "five weeks" was verify-event arithmetic | **ACCEPTED.** 919 rows are on built/validated items, and §1 now says this. |
| 4 | The gate is seven rows, not eight; the sprint is three biomes and the Rot is next | **ACCEPTED** → §4 |
| 5 | Several cuts lacked an adjacent owner quote (tree bursts, graffiti, scrapnest, Sarlacc, the sea, settings) | **ACCEPTED** → quotes added in §3. For Sarlacc, the owner named its kinds (*"Seeker digger dreamer devourer"*, 2026-09-26); that is not an explicit "accepted", so it is flagged rather than overstated. |
| 6 | The folk signs were never specifically cut (D2 not asked), and the no-vanishing rule does not require every warning letter | **ACCEPTED** → §2 reworded |

---

## 10. Appendix: the exact item ids in each cut group

Generated by the cut script over the census (as-of 2026-10-19T17:08Z). Owed rows per group are in §3.

**C2 FlowWorks full-scope extras** (51): `AQUATIC_WATER_BREATHING_GENE_1`, `BIG_CREATURES_DESIGN_WALLS_AND_SLOTS`, `CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES`, `EXCAVATION_WALL_ART_1`, `FALLEN_WIRE_SHOCK_1`, `FALL_GUARDRAILS_BUILD_REAL_OBJECT`, `FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS`, `FLOWWORKS_CONTAINER_MATERIALS_1`, `FLOWWORKS_PLAYTEST_CAMPAIGN_1`, `FLOWWORKS_QUARRY_DIGGING_1`, `FLOWWORKS_REVIEW_LOOKS_ROUND_1`, `FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES`, `FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS`, `HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY`, `HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME`, `LAVA_LIQUID_BUILD_PROMISED_BY_CARD`, `LIQUID_BOTTLE_LOOP_1`, `LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS`, `LIQUID_INDUSTRY_SETPIECES_1`, `LIQUID_THIRST_CHAIN_1`, `PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS`, `PIT_LADDER_REDRAW_HUNG_ON_THE_WALL`, `PIT_SPIKES_SHRINK_HALF_A_MAN`, `PIT_TEMPERATURE_SOFTENING_1`, `PROPANE_CANAL_WIRE_STILL_NO_FLUID`, `PUMP_ART_RESKIN_LESS_GARDEN_HOSE`, `RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP`, `RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS`, `RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED`, `RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS`, `SLIME_CROSSING_BUILD_SLIPPERY_SLOPE`, `SPRINKLER_HEADS_BUILD_PUMP_REQUIRED`, `SUSPENSION_ART_RESKIN_HE_SEES_FIRST`, `SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS`, `SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP`, `SUSPENSION_JETTY_BUILD_WALK_THE_PLANK`, `SUSPENSION_LIVE_DIAGNOSE_FIRST_REAL_RUN`, `SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD`, `SUSPENSION_WATERS_BUILD_MAY_BACKTRACK`, `SWALE_CANAL_ART_REFERENCE_1`, `TAKEN_BY_LAND_SERVICE_1`, `TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH`, `TANK_TALL_BUILD_TWICE_THE_DRINK`, `THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY`, `THIRST_DESIGN_SLIME_IS_THE_LAST_RESORT`, `THIRST_RULES_BUILD_SALT_OFF_THE_MENU`, `TITAN_TRENCHES_WIRE_MIND_THE_GAP`, `TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT`, `VEXXITH_USES_1`, `WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS`, `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST`

**C3 Telemetry / health / TPS / dashboards** (14): `AWAY_DASHBOARD_BUILD_1`, `BRIDGE_TPS_CAPTURE_FIXES_1`, `BRIDGE_TPS_REGULAR_REPORT_1`, `BRIDGE_TPS_REVIEW2_FIXES_1`, `HEALTH_BANDS_WIRE_QUEUED_BEHIND_OVERHEAD`, `HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME`, `HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP`, `HEALTH_METRICS_PROVE_EIGHT_WRITTEN_UNTESTED`, `TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED`, `TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO`, `TELEMETRY_DUPLICATES_RETIRE_AFTER_QUIET_WEEK`, `TELEMETRY_STACK_BUILD_AFTER_THE_MOVE`, `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS`, `TPS_VERDICT_FIX_SIX_SECONDS_NOT_THIRTY`

**C4 Bazaar + in-game LLM** (13): `BAZAAR_BANTER_LINES_1`, `BAZAAR_BROKER_TAB_1`, `BAZAAR_DISPLACEMENT_PASS_1`, `BAZAAR_HAGGLE_DUEL_1`, `BAZAAR_PRICE_ENGINE_1`, `BAZAAR_STOLEN_GOODS_PROPERTY_1`, `BAZAAR_WINDOW_GRID_1`, `ECONOMY_TRADE_SWEEP_1`, `KYBER_TRADE_PLOT_1`, `KYBER_TRADE_PLOT_FIRST_SCRIPT_1`, `MOOKEE_TRADE_ANIMAL_IDENTIFY_1`, `PLOT_MECHANISM_MODS_WAVE_1`, `THE_BAZAAR_FIRST_SCRIPT_1`

**C5 Built-but-inactive mods** (27): `ASSAILANT_DUNGEON_BUILD_1`, `ASSAILANT_SALVAGE_FIRST_SCRIPT_1`, `ASSAILANT_WARLAB_BUILD_MERGE`, `ATMOSPHERIC_BASE_BUILD_PROGRAM_1`, `BRAIN_WORMS_FIRST_SCRIPT_1`, `FLAME_STATUES_MOD_BUILD_1`, `FORGE_KEELWORK_REMAINDER_1`, `GRAVSHIP_ACOUSTIC_SCANNER_1`, `HOSTILE_FLORA_FIRST_SCRIPT_1`, `LORE_STAGES_FIRST_SCRIPT_1`, `NORTH_STAR_ATMOSPHERIC_TBD_1`, `OASIS_MAKER_FIRST_SCRIPT_1`, `PROPANE_LAKE_MECHANICS_FIRST_SCRIPT_1`, `PYRINTH_FIRST_SCRIPT_1`, `SARLACC_FIRST_SCRIPT_1`, `SARLACC_HABITAT_BUILD_1`, `SARLACC_PIT_WIDEN_THE_BIG_ONES`, `SARLACC_SEEKER_ROOTING_1`, `SHIELD_MODS_LEVERAGE_1`, `SOLAR_MIRRORS_BUILD_1`, `UNFINISHED_LINE_SITE_BEATS_1`, `UNFINISHED_LINE_SITE_CHOICE_1`, `UNFINISHED_LINE_TITHE_BEAT_1`, `UNFINISHED_LINE_WORLD_FOUNDRY_1`, `WARCASKET_FIRST_SCRIPT_1`, `WARCASKET_JUNKER_KINDS_BUILD_1`, `WARCASKET_WASTE_RUN_REMAINDER_1`

**C6 Sea depth beyond the ruled minimum** (17): `CHILL_AURORA_UNATTENDED_SOURCE_1`, `CHILL_SUIT_SHELTER_RULE_1`, `ELDER_DISCHARGE_STUN_LIVING_1`, `ELDER_TRADE_TRANSACTIONAL_PAYOUT_1`, `FISH_BESTIARY_BUILD_1`, `GARDEN_ESCALATION_PROGRESS_FIX_1`, `GREYSEA_USELESS_ARTIFACT_PLOT_1`, `SEABED_PER_SEA_FLOORS_1`, `SHIP_ALLOY_FORGE_1`, `SHIP_TOW_LINE_1`, `SPECIMEN_CABINET_DISPLAY_1`, `TWILIGHTSEA_FLOOR_PASS_1`, `TWILIGHTSEA_FLORA_PASS_1`, `TWILIGHT_BOTTOM_CAST_1`, `TWILIGHT_SEABED_WELLS_MISSING_1`, `TWILIGHT_WELL_AVOIDS_CURRENT_1`, `TWILIGHT_WELL_LIGHT_STATE_1`

**C7 Tree shade / canopy / tree burst** (11): `CANOPY_LAYER_BUILD_ROOF_OF_THE_WORLD`, `CANOPY_SHADE_DESIGN_BIG_DARK_PATCHES`, `DECOY_SHADE_TARP_1`, `SHADECRAFT_LESSONS_DESIGN_1`, `SUNSHADE_EXTRACT_DECIDE_WHEN_CLOCK_TICKS`, `TREE_BURST_BUILD_LITRES_BUY_YEARS`, `TREE_BURST_DESIGN_SWEETLINE_TAKES_ITS_TIME`, `TREE_CROWN_MEASURE_FROM_THE_ART`, `TREE_GRAPHICS_OWNERSHIP_1`, `TREE_SHADE_BUILD_CROWNS_ON_STILTS`, `TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE`

**C8 Explosive growth beyond the original idea** (12): `EGROWTH_BURST_FIX_NEVERDOWNS_AVERAGES`, `EGROWTH_DISABLE_FIX_BLOATED_PLANTS_STAY`, `EGROWTH_MASTER_FIX_SPARES_THE_BANDS`, `EGROWTH_RELOAD_FIX_FREE_CHARGE_PASS`, `EGROWTH_SAVELOAD_PROVE_DICT_SCRIBE_SHARE`, `EGROWTH_SCOPE_FIX_FROZEN_CHARGES_GAMBLE`, `EGROWTH_SUPPRESS_FIX_OFF_STILL_SUPPRESSES`, `EGROWTH_TELL_FIX_STAGE_RATCHET_STUCK`, `EXPLOSIVE_GROWTH_FIRST_SCRIPT_1`, `EXPLOSIVE_PLANT_GROWTH_1`, `EXPLOSIVE_SCOPE_ROW_PROVE_NEEDS_QUIET_LIST`, `FLOOD_WITNESS_EVENT_1`

**C9 Warscar extras** (12): `WARSCAR_AEROSOL_SCREEN_1`, `WARSCAR_CHOTRIX_SIGNS_1`, `WARSCAR_HOSPICE_DESERTERS_1`, `WARSCAR_OLD_TONGUE_1`, `WARSCAR_OPEN_BOAST_RITE_1`, `WARSCAR_PILGRIM_CAMP_SITES_1`, `WARSCAR_PILGRIM_JOURNAL_ANTIQUITY_1`, `WARSCAR_RAINBOW_POOLS_1`, `WARSCAR_SHEET_DONOR_PORT_1`, `WARSCAR_TOTCHAK_WAKES_1`, `WARSCAR_TURRETS_TRACK_1`, `WARSCAR_VALIDATION_FIDELITY_1`

**C10 Titans / slime extras** (13): `CORPSE_SITE_SAFETY_1`, `GELATINOUSSLIME_JOINING_WATER_RITE_1`, `GELATINOUSSLIME_PIT_SOLVENT_1`, `GELATINOUSSLIME_TITAN_CHUNK_BOMB_1`, `GELATINOUSSLIME_VAULT_SEAL_BREACH_1`, `TITANIC_BODYSIZE_TEST_RACE_1`, `TITANIC_CREATURES_FIRST_SCRIPT_1`, `TITANOSLIME_SLIME_BIOME_1`, `TITAN_BREAKTHROUGH_CLEARING_1`, `TITAN_CAMPS_SCAVENGERS_EVENTS_1`, `TITAN_ROOF_AVOIDANCE_1`, `TITAN_TRENCHES_WIRE_MIND_THE_GAP`, `TITAN_WAKE_FIXES_1`

**C11 Art polish (art never blocks)** (28): `ART_SHEETS_SCALE_CELLS_WIDEN_TOO_LATE`, `ART_SHEETS_TAIL_1`, `ART_SHEET_REDESIGN_FRESH_OR_REFUSE`, `ART_SIZES_AUDIT_AFTER_DONORS_LEAVE`, `ART_SUBJECT_RESOLVER_1`, `ART_VERSION_WRANGLING_1`, `CANON_DRAIN_1`, `CANON_FAUNA_FLORA_GPT_REVIEW_1`, `CANON_HERD_LORE_ARBITRATION_1`, `DESICCATED_LOOKALIKE_FAMILIES_1`, `DESSICATED_CORPSES_INSTALL_AFTER_PICKS`, `DESSICATED_CORPSES_REDRAW_ONE_BY_ONE`, `EXTRA_ART_PER_BIOME_COMMISSION_1`, `FACINGS_REDRAW_NORTHS_ABOUT_FACE`, `FASCINATING_WORLD_JUNK_1`, `FLYER_VARIANTS_INSTALL_MORE_FACES_PLEASE`, `GUARDRAIL_ART_RESKIN_BORROWED_FENCE`, `ICON_OUTLINE_REPAINT_1`, `INSITU_ART_JUDGE_SAVES_KEPT_WARM`, `JOSSUR_FLIGHT_FRAMES_1`, `LIVINGBOLT_CORPSE_ART_1`, `MYNOCK_FLIPBOOK_FRAMES_1`, `OLD_ART_SHEETS_REBUILD_WITH_SCALE_PANELS`, `PACK_OVERLAYS_BUILD_SHARED_SADDLEBAGS`, `SHEET_NOTES_FINISH_SEVENTEEN_DEF_HALVES`, `SPRINT_KIT_ART_SKETCH_BEFORE_THE_VETO`, `STATUE_ART_EXPANSION_1`, `TEXREGEN_UNPROVEN_ASK_THE_SHEETS`

**C12 Graffiti remainder** (10): `GRAFFITI_DESIGNATOR_MARK_CHOICE_1`, `GRAFFITI_IMPERIAL_FIRST_SCRIPT_1`, `GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1`, `GRAFFITI_NORTHSTAR_GREEN_FULL_1`, `GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1`, `GRAFFITI_NORTHSTAR_SHIP_1`, `GRAFFITI_NORTHSTAR_TRIAL_1`, `GRAFFITI_PUNK_ART_REVIEW_1`, `GRAFFITI_SIGIL_FRAMES_ART_1`, `GRAFFITI_V1_LIVE_PROOF_1`

**C13 Process/tooling programmes** (14): `ART_OVERRIDE_FAMILY_SCRIPT_1`, `DESIGN_MATERIALS_REVIEW_1`, `MACRO_GENERATOR_V0_1`, `MODCHECK_DONOR_ENVIRONMENTS_1`, `MOD_HUMAN_EXPLORATION_PASS_1`, `MOD_VALIDATION_RETROFIT_1`, `NORTHSTAR_ADVERSARIAL_REVIEW_1`, `NORTHSTAR_EVERYWHERE_PROGRAM_1`, `NORTHSTAR_PARTIAL_GAPS_FILL_1`, `NORTHSTAR_PROCESS_RETRO_1`, `NORTHSTAR_SITUATIONAL_ROLLOUT_1`, `NORTHSTAR_VALIDATION_SKILL_1`, `PLANETARY_LOADSCREEN_RENDERS_2`, `UTINNI_DISCOVERY_ACHIEVEMENTS_1`

**C14 World/lore extras** (16): `ANCIENT_WAR_LAB_1`, `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, `EVENT_TRACE_PROPS_LIBRARY_1`, `FALLZONE_LOST_CARGO_QUESTS_1`, `FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1`, `FORCE_DISTURBANCE_REFLAVOR_1`, `MAP_LANDFORM_MUTATORS_DESIGN_1`, `MINDSTONE_MATRIX_KINDLED_BUILD_1`, `MINERALS_WHERE_THEY_BELONG_1`, `RAKATAN_ARCHOTECH_MACHINES_1`, `SCRAPNEST_BIRD_BASE_THEFT_1`, `THROAT_CASK_ITEM_1`, `WARLAB_GARRISON_DESIGN_EARLY_BLAST`, `WARLAB_SPECIMENS_DESIGN_BREAKOUT_CHOICE`, `WAR_LAB_CRATER_HOOK_1`, `WYYYSCHOKK_FANG_PENDANT_1`

**C15 GPT-found: light/pigment, Stillsand side activities, Cathedral arc, Greentide extras, kinetic weapons, vaults, Bacta, FeverWood ransom, orphans** (26): `BACTA_FIRST_SCRIPT_1`, `BACTA_REVIVAL_MECHANIC_1`, `BACTA_TANK_CORE_1`, `CATHEDRAL_EXPOSURE_COMPLETION_1`, `CATHEDRAL_REGARD_BLACKBOARD_1`, `CRADLE_STRIKE_RECONCILE_WITH_LAB_DIVE`, `FEVERWOOD_BROOD_RANSOM_1`, `FOOTPRINT_TRACK_GRID_1`, `GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1`, `GREENTIDE_HUMMING_GROVE_1`, `GREENTIDE_STELLOCK_LACE_BUILD_1`, `GREENTIDE_THURROCK_HERD_BUILD_1`, `KINETIC_BLAST_WEAPONS_1`, `LIGHT_LEDGER_ONE_1`, `PROMISED_GIFT_NEVER_LOST_1`, `RUSTCATHEDRAL_HULL_BOLTS_BUILD_1`, `SCREEN_STOPS_SPORES_1`, `STILLSAND_CAVE_AS_PLACE_1`, `STILLSAND_GEOPHONE_1`, `STILLSAND_PRECIOUS_CAVES_LIVE_1`, `STILLSAND_SAND_SIEVE_CHORE_1`, `STILLSAND_SUN_LANCE_1`, `VAULT_DUNGEON_BUILD_1`, `VAULT_THAW_QUEST_FAMILY_1`, `WASTE_RUN_STUBS_1`, `WEBWORK_EGG_BROKER_CHANNEL_1`

**C16 GimmeSomeSlack leftovers (MessyConduit-era items, GSS validated 2026-10-16)** (5): `GSS_STYLE_RUN_PROVE_MIXED_LOOKS_SUSPECTED`, `MESSYCONDUIT_CABLE_PILE_LOOK_1`, `MESSYCONDUIT_REVIEW_ROUND1_1`, `MESSY_CONDUIT_MOD_1`, `POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK`
