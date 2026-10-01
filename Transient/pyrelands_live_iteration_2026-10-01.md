# Pyrelands north-star suite — live iteration, 2026-10-01

Suite: `src/RimMandrake/Pyrelands/validation.py`, plan `src/RimMandrake/Pyrelands/northstar_plan.py`.
Site: Pyrelands fixture, map id 1, tile 3, `pyrelands` tier. Driver:
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py`.

Rules followed: a FAIL that reflects the mod is a FINDING and stays; a predicate is changed only
where plan §2 / §2.3a says what it measures; the grader is never edited; UNMEASURED is not green.

## Pre-run: static check of every bridge call against the live tool schemas

Parsed `rimbridge_client.py --list-tools` (479 tools) and checked every `bridge_call` in the
suite with an AST walk. **22 call sites were broken** before any run: undeclared params on
`list_things` (`thingRequestGroup`, `note`, `rotStage`, pseudo-"note" calls), `set_plants`
(`defName`/`rect` x4), `destroy_batch` (`defName`), `list_pawns` (`animalsOnly`),
`get_terrain_batch` (`whole_map`, `plantableOnly`, `footprintOf`), and six tools that do not
exist (`log_since_mark`, `map_component_state`, `designate`, `list_jobs`, `get_pawn_hediffs` x2,
`room_temperature_pair`). Live probes then measured the result shapes (recorded in the suite
docstring). Fixes, each to what plan §2 / §2.3a says the bar measures:

| was | now | why |
|---|---|---|
| `get_def ... wildPlants/wildAnimals/baseWeatherCommonalities` | `get_defs fields=...` | `get_def` does not return them; `get_defs` reads wildPlants + weather table. `wildAnimals` is a non-public List the bridge cannot serialise -> that read-back is UNMEASURED |
| `get_def` `terrainPatchMakers` top-level | `extra.terrainPatchMakers` | measured shape |
| whole-map census via `isCompleteList` | `perDef` table, refused unless it sums to `countMatched` | `isCompleteList` is false whenever `limit` truncates rows |
| `log_since_mark` | Player.log scan with pre-flight row 3.8.7's `scan_log` | `drain_log` keeps 1000 lines and cannot reach mapgen |
| fulgurite "armed" via `drain_log` | `jawa/harmony_patches` on `WeatherEvent_LightningStrike.DoStrike` | load-time line has rolled out of the buffer; the patch itself is the proof |
| `map_component_state` (BurnLine) | free-standing `Fire` count | what `MapComponent_BurnLine.Measure()` counts |
| `list_jobs jobDef=RUT_FireHawkCarryEmber` | `site_state` job of the spawned hawk, `RM_FireHawkCarryEmber` | tool absent; JobDef was renamed RUT_ -> RM_ (the old name could never match) |
| `get_pawn_hediffs` | `list_pawns includeHealth` | tool absent |
| `room_temperature_pair` | two `make_empty_room`s + `room_heat set` + `cell_temperature` | tool absent; plan: matched rooms at one start temperature |
| `designate` | `designate_batch` + forced `ordered_job Harvest`, then forced `Ingest` with `pawn_need` read across it | plan 2.3a attributable harvest + ingest (food half was never measured) |
| rot via `allRotted` | `inspect_string` samples every half day + Meat_Human reference | plan 2.3a: rot by CompRottable, reference beside it |
| ScorchFruit fire-born burned bare ground | grass planted first | fuel-less fire never reaches TryBurnFloor (2026-09-13 lesson) |
| one chain per area | one chain per independent bar | a FAIL turns every later component of its chain UNMEASURED |
| fires spread freely | each fire on its own pad ringed by `RM_FE_FirebreakLine`, map extinguished after | an unbounded grass fire would contaminate every later census |
| census after the fire chains | census chains first | plan: census before any tick or fire |
| — | `_unmeasured()` helper | a component that cannot measure records UNMEASURED with its reason, never PASS |

## Runs

### Run 1 — aborted (fixture defect, not the suite)

~1,700 ticks in, `Find.CurrentMap` hopped to the colony map 0 and stayed there through a
manual `set_current_map 1`. Cause, read from decompiled `Faction`/
`NamePlayerFactionAndSettlementUtility`: the player faction has NO NAME, and once 4.3 days
have passed the game re-opens `Dialog_NamePlayerFactionAndSettlement` periodically; that
dialog (and closing it) moves the current map. Closing it only defers it. Run 1 was stopped
(its reads after the hop were on the wrong map, so it produced no usable verdicts).
Fixed for the session by answering the dialog (Randomize x2 + OK through
`rimworld/click_ui_target`): faction is now "Vererabum Common League". The suite also gained
`_on_site()` before every pad/component: if the current map is not the RM_Pyrelands site it
closes that dialog and restores the site map, recording that it did. Both maps checked for
fire (none) and all seven isolation toggles restored to their shipped ON before run 2.
**Site recipe gap for whoever owns `northstar_site.py`: name the player faction at site
creation, or every run past day 4.3 will hop maps.**

## Findings about the mod

(filled at the end)
