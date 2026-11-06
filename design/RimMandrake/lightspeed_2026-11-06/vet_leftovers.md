# LIGHTSPEED_VET_LEFTOVERS_FOR_BRIDGE_TOOLS: which Northstar leftovers a bridge capability drains

Date: 2026-11-06. Seat: BENCH. Evidence: `vet_leftovers.json` beside this file (one row per unit, with `cls`, `mod`, `id`, `q1`, `code`, `bucket`, `q2`, `capability` and `home`).
Inputs: the census `design/RimMandrake/lightspeed_2026-11-06.md` and its data at `D:\ClaudeWork\rimmandrake\scratch\lightspeed_census_2026-11-06\`. Capability spec: `design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md`.

The owner said: *"Anything that's in [Northstar] that can't be translated to the LLM-free testing lane should get a required assessment, "Would it have been translatable with a new Bridge-equipped in game testing capability?" If so, file a ticket right away to do that, adapt the [Northstar] test into the LLM-free lane, and make it blocked on the new capability being accepted. Let's see how much of [Northstar] we can drain out!"*

## 1. Totals

There are 1,114 units: B 736 and C 378.

| Bucket | B | C | Total |
|---|---|---|---|
| yes-with-capability (a T-ticket in the spec makes it a script verdict) | 16 | 36 | **52** |
| yes-with-missing-capability (needs a capability the spec does not have) | 0 | 9 | **9** |
| route-only (no new capability; routing, config or a script written with today's tools) | 720 | 118 | **838** |
| no (a look; no honest measurable restatement) | 0 | 215 | **215** |

The 838 route-only units go to these homes. None of them are new tickets.

| Home | Units | Q1 reason |
|---|---|---|
| rollout #2: the Relentless round becomes a testq client | 313 | route missing: a B live-proof line that no testq client runs |
| rollout #3: Steve's missing mods | 289 | mod list: the mod is steve_missing on the minimal list |
| rollout #4: ROWS_JSON contract for standalone scripts | 77 | script owed: all 77 decide their own verdict (scan in scratch `scripts_scan.tsv`), so a ROWS_JSON wrapper routes them |
| rollout #5: proof lines for owed criteria | 118 | needs judgement as written, but the bar restates as a state that today's reads decide at a chosen moment |
| rollout #6: stubs, plus suites for mods that have none | 26 + 2 | script owed: the stub replies "no tool". The tool now exists (comp_read, pawn_health, pawn_need, fire_quest/quest_lifecycle, inhabited_settlement_create, world_tile_map_generate, seabed_layer_probe, execute_gizmo, damage_log) or needs only a site fixture or mod list |
| LIGHTSPEED_WIRE_GSS_FIRST_NO_LLM_PATH (filed) | 13 | route missing: GSS proof_all-only rows |

The 61 "yes" units become 14 grouped tickets (section 3), plus 2 capability items for the missing capabilities (section 4). That makes 16 proposed items.

So about 92% of the B+C pool (899 of 1,114 units) drains into the LLM-free lane. The 215 "no" units are 211 walk bars plus 4 look stubs. They stay with Northstar for judgement.

## 2. Method

1. **Enumeration.** Units were re-derived with the census classifier (`final.py`), not copied from its totals:
   - B_route, B_unwritten and C_stub come from cov.json probes × rows.json rows × stubs.json, using the census LOOK regex.
   - B_nosuite covers mods whose state is "load".
   - B_script is scripts.json.
   - B_lp is the lp.json lines with class B.
   - C_bar is the 374 bars parsed from the 95 walks (scratch `bars.json`, file order).

   The generator is `D:\ClaudeWork\rimmandrake\scratch\vet_leftovers_2026-11-06\assess.py`. The codes are in `bar_codes_a.py` and `bar_codes_b.py` (bars) and `stub_codes.py` (all 46 stubs), in the same folder.
2. **Q1 (why Lightspeed can't run it today)** follows from the census class:
   - route missing: B_lp, GSS rows
   - mod list: B_route
   - script owed: stubs, scripts, no-suite mods
   - needs judgement: C units
3. **Q2 (would a capability give a script verdict?)** I read every bar and stub one at a time and gave it one code:
   - **R**: today's reads, taken at moments the script chooses (before or after a step, at the end of a span), decide it. This includes "count == 0 over a span", which is read afterwards from damage_log, drain_log, incident_journal or letter_list.
   - **T2**: needs a v1 probe that today's tools lack: `thing.field("DrawPos")` (a property) or `cell.temp`.
   - **T3**: needs an exact stop at a state moment (`until(...)`, `hitTick`, "within N days", "stops", "never lit before the deadline").
   - **T5**: an invariant, sequence or per-tick sample over a span (alarm watcher, `stays`, `changed`).
   - **T6**: a stop on a ring event at an unknown tick (letter, incident).
   - **M1-M4**: needs a capability that is not in the spec (section 4).
   - **N**: a look.

   A judgement bar is a "yes" only when its bar, as written, names a state. "Reads as one family", "feels", "legible at a glance" and "looks right" are N even when a proxy measure exists. Bars that overlap D (flyer flight, for example bar `dustflutter` burst) are N. Two bars have a measurable half and a look half (`portable_ladder_live`, bar 313). They are N, because half a bar is not its verdict.
4. **Blocker** is the last capability the ticket needs, in build order T1, T2|T4, T3, T5, T6, T8, T10. T5 and T6 both build only on T3, but the spec orders T5 before T6. So a ticket that needs both is blocked on T6.

**Sanity probes** (all were run; `assess.py` asserts the first one):
- Class totals re-derive the census exactly: B = 736 and C = 378. Inside B: route missing 326 (313 + 13), mod list 289, script owed 121 (42 + 77 + 2). The stubs dict holds 46 = 42 B + 4 C.
- Index spot checks: bar 308 is `raiders_never_shelter_in_a_cage` (FlowWorks), bar 53 is `pmech_rite_harvests_behind_front` (PyrelandsMechanics) and bar 136 is `pyre_burrowers_dive`. Each matches the code I gave it while reading.
- The default code can see: unlisted bars default to N, and 211 bars came out N. That is not near 0 or 374. 163 bars were coded explicitly, and the R/T/M share is spread across 43 walks rather than collapsing onto one.
- Codes cover disjoint index ranges: codes_a covers 0-189 and codes_b covers 190-373, asserted non-overlapping. Every stub key resolves; a missing key would raise.

## 3. Proposed tickets (grouped; every name passes `rimflow namecheck`)

Every adapt ticket has the same done-when: its units run on Lightspeed (testq, warm game) with no LLM, and each one returns a script verdict.

| # | Name | Units | Blocked on (last in build order) | Also blocked on (missing capability) |
|---|---|---|---|---|
| 1 | FLOWSTUBS_DRAIN_SIXTEEN_TO_SCRIPTS | 16 B | RINGPROBES_WIRE_EVENT_CURSORS (T6) | - |
| 2 | FLOWWALK_DRAIN_BARS_TO_WATCHERS | 15 C | CONDWATCH_BUILD_OWNED_RINGS (T5) | - |
| 3 | PMECHWALK_DRAIN_BARS_TO_RINGS | 7 C | RINGPROBES_WIRE_EVENT_CURSORS (T6) | CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER, RINGPROBES_WIDEN_MESSAGES_RING |
| 4 | PYREWALK_DRAIN_BARS_TO_WATCHERS | 5 C | CONDWATCH_BUILD_OWNED_RINGS (T5) | CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER |
| 5 | ATMOWALK_DRAIN_BARS_TO_WATCHERS | 5 C | CONDWATCH_BUILD_OWNED_RINGS (T5) | - |
| 6 | SEASWALK_DRAIN_BARS_TO_WATCHERS | 3 C | CONDWATCH_BUILD_OWNED_RINGS (T5) | - |
| 7 | FIREECOWALK_DRAIN_BARS_TO_WATCHERS | 2 C | CONDWATCH_BUILD_OWNED_RINGS (T5) | CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER |
| 8 | SCRUBWALK_DRAIN_BARS_TO_WATCHERS | 2 C | CONDWATCH_BUILD_OWNED_RINGS (T5) | CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER |
| 9 | LIVESTOCKWALK_DRAIN_BAR_TO_WATCHER | 1 C | CONDWATCH_BUILD_OWNED_RINGS (T5) | - |
| 10 | CUISINEWALK_DRAIN_BAR_TO_UNTIL | 1 C | ADVANCEUNTIL_WIRE_PER_TICK_STOP (T3) | - |
| 11 | ANTIQWALK_DRAIN_BAR_TO_UNTIL | 1 C | ADVANCEUNTIL_WIRE_PER_TICK_STOP (T3) | - |
| 12 | GRAFFITIWALK_DRAIN_BAR_TO_UNTIL | 1 C | ADVANCEUNTIL_WIRE_PER_TICK_STOP (T3) | - |
| 13 | CAULDRONWALK_DRAIN_BAR_TO_WEATHER | 1 C | CONDWATCH_BUILD_OWNED_RINGS (T5) | CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER |
| 14 | SWPATCHWALK_DRAIN_BAR_TO_WEATHER | 1 C | CONDWATCH_BUILD_OWNED_RINGS (T5) | CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER |

The total is 61 units.

### Ticket titles

1. **FLOWSTUBS_DRAIN_SIXTEEN_TO_SCRIPTS**
   - **Adapt:** the 16 FlowWorks proof_all stub rows into Lightspeed scripts.
   - **Units by capability:**
     - 10 T3 `until` stops: weir_joined_wall, pond_empty_stops_flow, recession_off, refill_on, superdeep_capture_off, fire_torch_advances_pending, fire_reach_capped_at_source, chemfuel_inferno_off_smoulders, astrofuel_detonation_off_burns, propane_vanilla_fire_lights_inferno.
     - 2 T2 `cell.temp` reads: liquid_heat_warms_and_chills, liquid_heat_off_is_inert.
     - 3 T5 watchers or sequences: ladder_wall_live, trench_cage_live, container_styles_live.
     - 1 T6 letter-ring stop: first_find_sends_letter.
   - **Blocked on:** RINGPROBES_WIRE_EVENT_CURSORS.
   - **Done when:** all 16 run on Lightspeed with no LLM and give verdicts.
2. **FLOWWALK_DRAIN_BARS_TO_WATCHERS**
   - **Adapt:** 15 FlowWorks walk bars into proof lines. One of them is the duplicate `pit_occupant_below_floor` bar from north_star_validation_spec.
   - **Units by capability:**
     - 5 T2 DrawPos-by-depth reads via `thing.field`: pawn_height_ladder_legible, lowers, rises, pit occupant ×2.
     - 8 T3 stops: reservoir empty, canal fire, hose resumes, climbs out, scales wall, walks under deck, crushed ice melts, digging takes hours.
     - 2 T5 alarm watchers: raiders_never_shelter_in_a_cage, never_liquid_on_open_ground.
   - **Blocked on:** CONDWATCH_BUILD_OWNED_RINGS.
   - **Done when:** all 15 run on Lightspeed with no LLM and give verdicts.
3. **PMECHWALK_DRAIN_BARS_TO_RINGS**
   - **Adapt:** 7 PyrelandsMechanics walk bars.
   - **Units by capability:**
     - 3 T6 incident/letter stops: rite party walks in, visit picks and leaves, attack brings raids.
     - 1 T5 fire-front watcher: rite lights line.
     - 1 T3 until-leaves: leaves with fruit.
     - 1 M2: harvests behind the front, which needs `cell.fire` at each pawn's cell.
     - 1 M4: fruit defence warns, if the warning is a Message rather than a letter. Verify which; if it is a letter, it is T6.
   - **Blocked on:** RINGPROBES_WIRE_EVENT_CURSORS for 5 units. The M2 and M4 units are also blocked on the two section 4 items.
   - **Done when:** all 7 run on Lightspeed with no LLM and give verdicts.
4. **PYREWALK_DRAIN_BARS_TO_WATCHERS**
   - **Adapt:** 5 Pyrelands walk bars.
   - **Units by capability:**
     - 1 T3: scorchfruit_spoils_fast, where `hitTick` of the rot is compared with four days and one day.
     - 1 T5: firehawk_carries_ember.
     - 1 M1: burrowers_dive, where the burrowed state is a hediff.
     - 2 M3 weather/condition invariants: ashfall_darkens_drifts, cannot_ordinary_rain.
   - **Blocked on:** CONDWATCH_BUILD_OWNED_RINGS, plus CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER for 3 units.
   - **Done when:** all 5 run on Lightspeed with no LLM and give verdicts.
5. **ATMOWALK_DRAIN_BARS_TO_WATCHERS**
   - **Adapt:** 5 AtmosphericBase walk bars.
   - **Units by capability:**
     - 4 T5 per-tick samples or watchers over `cell.glow`, fixture colour and claimant: territory_boundary_moves, dark_is_never_still, never_white_but_the_narrator, never_dims_a_god.
     - 1 T3: never_an_uninterruptible_alarm (until the narrator is active).
   - **Blocked on:** CONDWATCH_BUILD_OWNED_RINGS.
   - **Done when:** all 5 run on Lightspeed with no LLM and give verdicts.
6. **SEASWALK_DRAIN_BARS_TO_WATCHERS**
   - **Adapt:** 3 SeasWaterline walk bars.
   - **Units by capability:**
     - 2 T3: until the waterline cast count is ≥ 1, with a visit-length deadline (positive and negative).
     - 1 T5: sample cast `pawn.pos` over the visit and check the share near water.
   - **Blocked on:** CONDWATCH_BUILD_OWNED_RINGS.
   - **Done when:** all 3 run on Lightspeed with no LLM and give verdicts.
7. **FIREECOWALK_DRAIN_BARS_TO_WATCHERS**
   - **Adapt:** 2 FireEcology walk bars.
   - **Units by capability:**
     - 1 T5: firebreak_reads_as_strip, as a watcher that `cell.fire` beyond the strip is never true.
     - 1 M3: ash_fertile_when_watered, where "black rain waters it" needs a weather/condition read.
   - **Blocked on:** CONDWATCH_BUILD_OWNED_RINGS, plus CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER.
   - **Done when:** both run on Lightspeed with no LLM and give verdicts.
8. **SCRUBWALK_DRAIN_BARS_TO_WATCHERS**
   - **Adapt:** 2 LeaningScrub walk bars.
   - **Units by capability:**
     - 1 T5: scrub_stall_reads_still, where `stays`/`changed` on `pawn.pos` under RM_Stall depends on body size.
     - 1 M3: scrub_never_windless, a weather invariant.
   - **Blocked on:** CONDWATCH_BUILD_OWNED_RINGS, plus CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER.
   - **Done when:** both run on Lightspeed with no LLM and give verdicts.
9. **LIVESTOCKWALK_DRAIN_BAR_TO_WATCHER**
   - **Adapt:** 1 Livestock bar, skarnix_leaves_the_light (T5).
   - **Method:** sample the animal's `pawn.pos` against `glow_at` over the span, and check that it ends in darkness.
   - **Blocked on:** CONDWATCH_BUILD_OWNED_RINGS.
   - **Done when:** it runs on Lightspeed with no LLM and gives a verdict.
10. **CUISINEWALK_DRAIN_BAR_TO_UNTIL**
    - **Adapt:** 1 Cuisine bar, cooked_at_campfire (T3).
    - **Method:** `until(pawn.job` is the stick-meal bill), then read the bill's workbench def.
    - **Blocked on:** ADVANCEUNTIL_WIRE_PER_TICK_STOP.
    - **Done when:** it runs on Lightspeed with no LLM and gives a verdict.
11. **ANTIQWALK_DRAIN_BAR_TO_UNTIL**
    - **Adapt:** 1 Antiquities bar, reader_at_station (T3).
    - **Method:** `until(pawn.job` is the read job), then read the antiquity's position and `thing.exists` after the job.
    - **Blocked on:** ADVANCEUNTIL_WIRE_PER_TICK_STOP.
    - **Done when:** it runs on Lightspeed with no LLM and gives a verdict.
12. **GRAFFITIWALK_DRAIN_BAR_TO_UNTIL**
    - **Adapt:** 1 Graffiti bar, mark_actually_appears (T3).
    - **Method:** `until` the paint job ends, then check that `map.count(mark, wall cell)` is ≥ 1.
    - **Blocked on:** ADVANCEUNTIL_WIRE_PER_TICK_STOP.
    - **Done when:** it runs on Lightspeed with no LLM and gives a verdict.
13. **CAULDRONWALK_DRAIN_BAR_TO_WEATHER**
    - **Adapt:** 1 Cauldron bar, no_rain_or_snow (M3, with a T5 watcher).
    - **Method:** a watcher that the map's weather is never a rain or snow def over the span.
    - **Blocked on:** CONDWATCH_BUILD_OWNED_RINGS, plus CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER.
    - **Done when:** it runs on Lightspeed with no LLM and gives a verdict.
14. **SWPATCHWALK_DRAIN_BAR_TO_WEATHER**
    - **Adapt:** 1 StarWarsPatches bar, desert_sandstorms (M3, with a T5 watcher).
    - **Method:** a watcher that the Star Wars sandstorm weather or condition occurs on a desert map over a stretch.
    - **Blocked on:** CONDWATCH_BUILD_OWNED_RINGS, plus CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER.
    - **Done when:** it runs on Lightspeed with no LLM and gives a verdict.

## 4. Missing capabilities (findings: not in the bridge-conditions spec)

The T2 probe set has fixed-cell spatial probes and `pawn.state` limited to downed/dead/mental/drafted. It has no hediff, weather or condition read. T6's ring covers letters only, not Messages. That leaves four gaps, grouped into two proposed capability items.

| Gap | Units | Proposed item | Builds on |
|---|---|---|---|
| M1: `pawn.hediff(def)` (has, severity) | 1 (pyre_burrowers_dive) | **CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER** | CONDPROBES_WIRE_ENGINE_READS (T2) |
| M2: a pawn-relative cell (`cell.*` at `pawn.pos`, evaluated per tick) | 1 (pmech_rite_harvests_behind_front) | the same item | T2 |
| M3: `map.weather` / `map.condition(def)` | 6 (Pyrelands ×2, FireEcology, LeaningScrub, Cauldron, StarWarsPatches) | the same item | T2 |
| M4: a Messages ring (`ring.count(messages, ...)`) | 1 (pmech_fruit_defence_warns_then_drives) | **RINGPROBES_WIDEN_MESSAGES_RING** | RINGPROBES_WIRE_EVENT_CURSORS (T6) |

**CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER**
- **What:** add three read-only probes to the T2 probe registry, with the same three-valued Unknown semantics:
  - `pawn.hediff(def)`
  - cell probes whose cell argument may be a pawn reference
  - `map.weather` / `map.condition(def)`
- **Unblocks:** 8 walk units across 6 tickets.
- **Done when:** each probe has a selftest and one live read on a warm game agrees with the engine state.

**RINGPROBES_WIDEN_MESSAGES_RING**
- **What:** add a Messages source to the T6 owned-cursor rings.
- **Unblocks:** 1 unit, but only if the warning is shown to be a Message. Verify that before building, or drop the item.
- **Done when:** `ring.count(messages, ...)` stops a T3 advance on a live warning.

## 5. Owed filings (the brief forbade the ledger here)

The owner's ruling says to file "right away". This doc only proposes; the Conductor or a seat with ledger rights owes these:

1. The 14 adapt tickets in section 3. Each one is blocked on the item named in its "Blocked on" column and, where listed, on the section 4 item.
2. The 2 capability items in section 4.
3. The Lightspeed rollout steps #2 through #6 of the census are **not filed**. Only LIGHTSPEED_WIDEN_112_MODS_NEVER_QUEUED and LIGHTSPEED_WIRE_GSS_FIRST_NO_LLM_PATH exist in the BENCH queue. 825 of the 838 route-only units have no item to land in until they are filed.
4. A lesson: the 42 B stub replies say "no tool exists" for reads that the bridge now has: comp_read, pawn_health, pawn_need, fire_quest/quest_lifecycle, inhabited_settlement_create, world_tile_map_generate (layer), seabed_layer_probe and execute_gizmo. The stub text is stale. Rollout #6 should rewrite these stubs as scripts, not wait on tools. One check is owed first: does world_tile_map_generate's `layer` parameter reach the seabed layer that the three DivingInteraction stubs need?
