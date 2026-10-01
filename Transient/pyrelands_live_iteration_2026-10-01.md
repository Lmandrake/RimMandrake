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

### Run 2 — stopped: one-tick-per-frame waits

`t.wait_ticks` drives `rimworld/step_game_ticks`, one tick per Unity frame: MEASURED ~53
ticks/s (3,170 ticks per wall minute). The suite needs ~760k ticks (7-day regrow, 4.5-day
rot), i.e. ~4 hours. Added `_wait()`: waits > 5,000 ticks run at Ultrafast and poll the real
clock (`Session._ticks`), pause ~400 ticks short and finish exactly with `step_game_ticks`;
a 60 s clock stall raises. MEASURED ~400 ticks/s. Also added a per-component `[pyre]`
progress line on stderr (the driver prints only at the very end).

### Run 3 — REFUSED by pre-flight `no_modal`

`Dialog_NamePlayerSettlement` (the site settlement's own naming prompt) was open. Answered
it the same way (Randomize + OK): settlement "Pandale". `_on_site()` now closes any
`NamePlayer*` dialog.

### Run 4 — first end-to-end run (results `Transient/northstar/Pyrelands_20261001T184744Z.json`)

Driver: NOT GREEN, PASS=0 FAIL=9 UNMEASURED=11. State-PASS bars are reported UNMEASURED by
the driver until `judge_cli.py` grades their screenshots (by design).

| bar | state verdict | reason |
|---|---|---|
| mapgen_log_clean | PASS | Player.log scan clean |
| plant_distribution_correct | **FAIL (finding)** | `Plant_TreeAnima` x1 on the site; wildPlants == manifest; probe saw Plant_Grass |
| animal_distribution_correct | UNMEASURED | census clean (17 wild, 5 kinds, none foreign); `wildAnimals` read-back not serialisable |
| grass_chokes_ground | PASS | |
| ruins_scorched | UNMEASURED | no RM_FE_ScorchRuins on this site; no tool forces the genstep |
| burn_line_present | UNMEASURED | 0 fires; site recipe holds burnLine OFF through gen |
| fulgurite_armed_only / biome_def_wiring (toggle floor) | PASS | |
| ground_ash_ladder | FAIL — **harness** | extinguished at 3,000 ticks; `Fire.TryBurnFloor` needs a fire alive 7,500 ticks (decompiled `RimWorld.Fire.TicksToBurnFloor`). Now waits 8,000 |
| ash_dusting / ashfall_accumulates (toggle floor) | PASS | |
| scorch_fruit_seed (toggle floor) | FAIL — likely finding | 0 ScorchFruit in a 24x24 fully-grassed burn: the postfix takes its ONE roll on the fire's first tick and needs a plant-free standable cell in 3x3, but the burning grass still stands then. Evidence (rect vs whole-map count, cap 40) added |
| ashfall_darkens_drifts, cinderfall_distinct, blackrain_reads, cannot_ordinary_rain | PASS | |
| scorchfruit_fire_born | FAIL — **harness** | "gen" ScorchFruit = 9 were fruit from runs 1-2's burns. Now: a ScorchFruit at the census outside every suite fire pad is on unburned land (the site's only fires are the pads) |
| scorchfruit_produces | FAIL — **harness** | harvest made yield; food read 0.200 -> 0.200 because the game is paused (no ticks ran for the ingest). Now polls food every 150 ticks for 1,500 |
| scorchfruit_spoils_fast | UNMEASURED | yield stack gone by day 0.5 (eaten/hauled?). Per-sample whole-map + nearby yield readings added |
| firehawk_carries_ember, burrowers_dive | FAIL — **harness** | `map_fire` refused all cells: the pads sat on deep ash from run 2's burns (non-flammable). Pads are now re-laid to RM_FE_Ground_Soil first |
| furnacebeast_warmth | FAIL — **harness** | colonist at 3 cells; an uncharged beast's aura is 4.9 x 0.35 = 1.7 cells (`CompFurnaceWarmthAura`). Colonist now adjacent |
| furnacebeast_heats_room | PASS | matched rooms set to 10 C |
| embergrass_regrows | FAIL -> now UNMEASURED | 0 of 256 regrew in 7 days, but the plan marks this threshold CALIBRATING (never gates), so the gate I had added is removed; the numbers are reported |
| fulgurite_after_lightning | FAIL | 0 fulgurite after 20,000 ticks of DryThunderstorm (301 fires: strikes landed). Sand-cell count now recorded to tell probability from defect |

Also: the results JSON keeps only ~300 chars of each component's evidence, so `_note()` now
echoes every evidence record to stderr (`[pyre-note]`).

### Run 5 (`Transient/northstar/Pyrelands_20261001T192754Z.json`) — the fixture was destroyed by run 4

🔴 **Run 4's fulgurite chain (locked DryThunderstorm, 20,000 ticks, no containment) let the
lightning fires burn the WHOLE site**: run 5's terrain census reads 49,263 cells of
`RM_FE_Ash_Deep`, 16 cells of sand, and the site's three colonists are gone (no player pawns,
no human corpse). This was a harness defect of mine, not the mod. Consequences: every
fresh-map census bar is now meaningless on this fixture, and the site needs a reload
(`northstar_site.py`) before those bars can be measured — I am not permitted to load saves.
Changes: the lightning chain now extinguishes the map every 1,000 ticks; a `_fresh_site()`
gate makes every fresh-map census component UNMEASURED when > 100 deep-ash cells lie outside
the suite's own fire pads (deep ash only comes from burning); the harvest bar spawns its own
colonist (spec 1b) instead of borrowing the site's.

Other run-5 evidence and fixes:
- scorch_fruit_seed FAIL again: 0 in the 24x24 burn, 4 on the whole map. scorchfruit_fire_born
  FAIL: 0 in its burned cohort. The 12 ScorchFruit the census found all sit on the LADDER pad,
  i.e. they came from run 4's three-cycle burn, so the postfix can fire; a single burn of a
  freshly grassed patch yields none. Consistent finding across two pads and two runs.
- scorchfruit_spoils_fast: inspect text read "spoils in 3.5 / 3 / 2.5 days" at day 0.5 / 1 /
  1.5 (i.e. daysToRotStart 4 confirmed), then the stack vanished at day 2 — eaten by a wild
  grazer. Now walled in with steel (plan 2.3a "fenced cell").
- firehawk_carries_ember: 20 job samples, never `RM_FireHawkCarryEmber` (wander, one Flee).
  Fire-alive count now recorded per sample so "no fire" reads UNMEASURED, not FAIL.
- furnacebeast_warmth: no hediff; `spawn_pawn` SCATTERS near the cell, so the distance was
  unknown. Now walks the colonist to the beast each sample and records the distance.
- furnacebeast_heats_room: both rooms read exactly 49.71 C (same as outdoors 49.67) 2,500
  ticks after `room_heat set 10`. Now: `room_get` proves both are rooms, checks the scattered
  beast actually landed inside room A, samples every 250 ticks, gates on the mean delta while
  the control is below the pusher's 24 C cap, UNMEASURED if it never is.
- burrowers_dive: PASS (`RM_Burrow` job, `RM_Burrowed` seen, grazer intact).
- embergrass_regrows: pre 256 / day3 0 / day7 0 at 46 C (on a burned-out map); UNMEASURED
  (calibrating).
- fulgurite: 16 sand cells on the map, 8 fires: an expected fulgurite count of ~0.0006 cannot
  test the bar. Now UNMEASURED with that arithmetic when expect < 1.

## Findings about the mod

(filled at the end)
