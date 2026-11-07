# BRIDGE_CONDITIONS — composable wait / watch / sample primitives for live tests (draft, 2026-11-06)

Status: DRAFT (first-stage designer, BENCH). Offline design only: no game, bridge, ledger or deploy was touched.
GPT enrichment: `gpt_enriched.md` beside this file.

## 0. Owner ask and decided direction

Owner, 2026-11-06, verbatim: *"Please design and ticket up the capabilities that you suggested for additional in-game
tool testing: advance until this is true, N ticks, watch this and report when it happens. We might even be able to test
Flyers this way finally: return the series of images that are iterated between while it flies around. We were always
supposed to implement more in-game testing built into Bridge to leverage from Python... let's get back into that! Do a
full design pass now on all the testing needs we've experienced, or the things that go really slowly now, and muse on
what else we could build into the testing suite associated in Bridge/Python scripts to supercharge what we can do!
Attack the polling problem directly and aggressively with many potential options to use like lego building blocks to
assemble the tests and conditions we need. "Wait until there's water in this cell." "Report when this cell turns dry."
"Alert when light(dark) reaches this location." Spec this out richly, both evidence-based as well as proactively."*

Decided direction (Conductor, owner authority): **proofs stay in Python** (flexible, legible, changeable without a game
restart). The game side gains a **small set of generic, composable primitives** that Python calls — an evaluator for a
condition tree, a watcher registry, a sampler — never per-mod test suites in C#. Many-ticks-per-frame is a separate item
(`TICKBURST_PROVE_MANY_TICKS_ONE_FRAME`) and is referenced, not designed, here.

The one-sentence design: **move the `if` into the tick loop.** Today Python advances K ticks, reads, decides, repeats;
the game is paused between, the read resolution is K, and every iteration is 2+ bridge round trips. Instead Python
sends the condition once, the companion evaluates it after every tick (or every k ticks, declared) inside the existing
`jawa/safe_advance` stepper, and returns the exact tick it became true plus the values that made it true.

## 1. Inventory: what already exists (this project keeps having already built it)

Method: `grep -A2 '\[Tool(' src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs | grep -oE '"jawa/[^"]+"'` → **418
distinct `jawa/*` tools in 138 .cs files** (426 `[Tool(` attributes). Filtered by name for wait/watch/event/flight/
advance/cell/light/log, then read the Description of each candidate.

### 1.1 The stepper we should extend, not replace — `jawa/safe_advance`
`JawaBenchVitalsTools.cs:149-238` (tool) + `JawaBenchVitals.cs:699-735` (`SA.Frame`, the per-frame driver).
- Game paused; per frame, `DoSingleTick()` in chunks of ≤60 (`V.MaxChunk`, `JawaBenchVitalsCore.cs:43`) inside a
  per-frame wall budget (`frameBudgetMs`, default 40 ms), so it already runs **many ticks per frame**. (Factual note
  for the TICKBURST item: its premise "today stepping is one tick per frame" is true of `rimworld/step_game_ticks`, not
  of `jawa/safe_advance`. TICKBURST should measure safe_advance's achieved ticks/s before building a new stepper.)
- After every chunk it calls `V.FirstStop(Latch.Since(r.StartSeq), r.Stop)` — **a latch with a sequence cursor and a
  `stopOn` kind filter. This is exactly the hook a condition needs**: a watcher that becomes true emits a latch trigger
  of a new kind `cond`, and the existing loop stops on it. No new stepper.
- Already safe: refuses > budgetTicks (30000) on a populated map without `timeException`, refuses > 1.2 M ticks,
  aborts on game change / map gone, `action=status|cancel`, returns `state=running` after `timeoutMs` so a caller can
  re-poll (the pattern a long `advance_until` reuses to stay under the 540 s command limit).
- Gap: the latch is checked **per chunk** (≤60 ticks), so a condition stop would have 60-tick resolution unless the
  condition is evaluated per tick inside the inner `for (i<n) DoSingleTick()` loop (§3.5).

### 1.2 The monitor — `jawa/vitals` (`JawaBenchVitalsTools.cs:21`)
Pawn vitals over time, tombstones for deaths, hostile structures, clock ledger (discontinuity detection), blocking
windows, new letters incl. GameEnded, required actors/specimens, coverage heartbeat. Rows go to the TPS record.
**Reusable**: it is already a per-chunk watcher with a typed trigger vocabulary (`V.DefaultStopKinds`). The condition
engine is a generalisation of it: vitals = a built-in watcher set; `cond` = user-supplied watchers on the same latch.

### 1.3 Event rings already recorded in game (event-source predicates read these by cursor)
| tool | file:line | records |
|---|---|---|
| `jawa/damage_log` | JawaBenchSituationalTools.cs:1043 | every TakeDamage + real Kill, victim, def, amount, instigator, part, tick, cell |
| `jawa/incident_journal` | JawaBenchAwarenessTools.cs:154 | every IncidentWorker.TryExecute call with honest outcome fields, seq + epoch |
| `jawa/heat_events` | JawaBenchHeatEventTools.cs:16 | RM_HeatEvents (beskararmorer) events oldest first |
| `jawa/drain_log` | JawaBenchTerrainTools.cs:1934 | recent log messages incl. those logged during step_game_ticks (bridge `effects.logs` is blind there) |
| `jawa/letter_list`, `rimworld/list_messages` | — | letters, messages |
All are rings with a seq/oldestRetained cursor. **Reusable directly** as `ring.*` probes ("a new damage row matching X
since arm").

### 1.4 Point reads that become probes (each already has the engine call we need)
| tool | file:line | engine read |
|---|---|---|
| `jawa/glow_at` | JawaBenchNorthstarTools.cs:483 | `GlowGrid.GroundGlowAt`, `PsychGlowAt`, `CurSkyGlow`, roofed, hour; refuses OOB by name |
| `jawa/shade_probe` | JawaBenchShadeProbeTools.cs:78 | shade/mirror-light stack by reflection |
| `jawa/get_terrain_batch`, `get_terrain_layers` | JawaBenchTerrainTools.cs:418 | terrain top/under/foundation |
| `jawa/canal_cell_report`, `flowworks_engine_state`, `flowworks_excavation_rect` | JawaBenchFlowWorksTools.cs:82, JawaBenchFlowWorksNorthstarTools.cs:191 | FlowWorks depth, fill f, isSource, nextPulseTick, pulse interval |
| `jawa/cell_temperature`, `thing_ambient_temp`, `room_get` | JawaBenchSimTools.cs:91 | temperature, room |
| `jawa/map_fire` (event) / `list_things` | JawaBenchEventTools.cs:835 | fire |
| `jawa/site_state` | JawaBenchNorthstarTools.cs:572 | weather, snow over rect, pawns' jobs, conditions, storyteller |
| `jawa/pawn_get`, `pawn_census`, `pawn_stats`, `pawn_need`, `list_pawns`, `thing_stats`, `stat_explain` | — | pawn/thing state |
| `jawa/time_clock` | — | ticksAbs / ticksGame |
| `jawa/static_call` | — | a mod's own `Proof*` static method (the proof-hook pattern used by GSS, FlowWorks, Titanoslime, Scarlands hospice) |
| `jawa/workgiver_probe`, `flowworks_job_probe` | JawaBenchWorkGiverProbeTools.cs:32 | why a pawn would/would not take work |

### 1.5 Flight — `jawa/pawn_flight` (`JawaBenchFlightTools.cs:260`)
Reads Pawn.Flying and the whole Pawn_FlightTracker (flightState, canEverFly, canFlyNow, maxFlightTicks, flyingTicks,
flightCooldownTicks, lerpTick, current JobDef + tryStartFlying). Actions report/start/hold/land with `maintainTicks`.
**Reusable** as the field source for `pawn.flight.*` probes. Has no per-tick series and no render-frame read (§4).

### 1.6 Python side
| what | where | reusable? |
|---|---|---|
| `_BridgeBase.ticks(n)` | src/RimMandrake/Utils/validation_core.py:147 | yes: the place to add `until/watch/sample`; already does site_recover on benign governor stops |
| `_BridgeBase.probe_of` sleep-poll handshake | validation_core.py:~125-140 | replace: it `time.sleep(poll_s)`-polls a mod-settings serial for a frame to service a probe |
| `clockgate.advance_chunk`, `SAFE_CHUNK_MAX = 2500`, `GovernorStop`, `is_benign_stop`, governor_stops.jsonl | src/RimMandrake/Utils/modcheck/clockgate.py:131 | yes: until-stops must NOT be GovernorStops; a new `CondStop` result type |
| `modcheck.watch.Watch` (bland map, chunked wait, detector sweep after every chunk, surprise evidence, visitor rule) | src/RimMandrake/Utils/modcheck/watch.py:55 (DEFAULT_CHUNK 600) | yes: its detector sweep is a Python-side invariant monitor at 600-tick resolution; its detectors are candidates to move into the in-game watcher set |
| `modcheck.suite.wait_ticks` (feeds colonists before each chunk) | Utils/modcheck/suite.py:433-467 | yes, wrap |
| `northstar_driver/` (session, transport, bars, lint_calls, bridge_utilization, tool_schemas.json) | src/RimMandrake/Utils/northstar_driver/ | `lint_calls.py` can lint for the poll-loop anti-pattern once the primitive exists; `tool_schemas.json` must learn the new tools |
| NORTHSTAR_MOTION_FRAMES_1 (ordered frame sequence judged, not last screenshot) | Utils/modcheck/selftest_motion_frames.py | the judging side exists; it lacks a deterministic frame SOURCE — §4 supplies one for flyers (paths, not screenshots) |
| `Utils/logwait.py` | Utils/logwait.py:44 | Player.log poll; superseded for in-session log conditions by a `log.*` probe |

**Verdict.** We already own: a safe many-ticks-per-frame stepper with a stop latch, a typed trigger vocabulary, five
event rings with cursors, and a point read for nearly every predicate the owner named. **What is missing is only the
glue: a condition tree evaluated inside the stepper, a persistent watcher registry, and a sampler.** That is the build.

## 2. Evidence: polling and slowness we have suffered

### 2.1 Census of poll loops (method stated)
Method (script kept in seat scratch, re-runnable): `ast`-walk every `.py` under `src/RimMandrake/` except
`selftest*`/`test_*` (**1,594 files parsed, 0 skipped**). A loop counts when it is the **innermost** `for`/`while` whose
body contains (a) an advance call (`wait_ticks`, `.ticks(`, `step_game_ticks`, `safe_advance`, `advance_chunk`,
`clockgate.step`) **or** a `time.sleep(` **and** (b) a bridge read (`.call(`, `jawa/`, `rimworld/`, `.probe(`).
- **157 loops**: **75 advance-read loops in 54 files**, **82 sleep-read loops**.
- Precision, hand-checked: of the first 28 advance loops, **16 are true advance-read-decide polls** (57%); the rest are
  plain chunking (`suite.py:467`, `governor.py:251`), per-case setup loops (`l1_donor_off_round.py:758`), or mocks
  (`TheRot/validation.py:1590`). Estimate **~40-45 true advance-until polls** in live proofs.
- Of the 82 sleep loops, **57 wait on game lifecycle** (`get_ui_state` programState == Playing, bridge status,
  map_info) after a load — the same 5-line loop copy-pasted into ~50 scripts. The rest are wall-clock watches of game
  state (`perf/game_comp_stall_hunt.py:167`, `bridgetools/prove_biome_timelapse.py:71` sleeps 20 s between reads) or
  probe handshakes (`validation_core.py` `probe_of`, `FlowWorks/validation_hose.py:82`).
- The count is a lower bound for advance polls written as straight-line `ticks(); read(); ticks(); read()` without a
  loop (not counted) and for polls inside helpers called from loops.

### 2.2 Concrete cases (path:line → what a primitive replaces)
| # | case | path:line | what hurt | primitive that replaces it |
|---|---|---|---|---|
| E1 | **FlowWorks validation_v2 run 4**: 1,301 bridge calls for 63 rows, 269 s; `P_pits` alone 8,607 ticks in 142.9 s (**60 ticks/s**, pit-fill waits), `X_promoted` 4,771 ticks 55.9 s | FlowWorks/northstar/validation_v2_result_20261025T0152_run4.json:27,123 | wall is tick waits at step_game_ticks speed plus read round trips | `advance_until(any cell in pit rect fill ≥ f, max)` inside safe_advance (many ticks/frame, 1 call) |
| E2 | v2 pulse loop: step PULSE_PIN, read engine, read 3 cells, decide, repeat; `stalled<3` guard | FlowWorks/northstar/validation_v2.py:2930-2948 | ≥5 calls per chunk; resolution = PULSE_PIN | `until(all(cell(E8).depth==1, cell(E7a).depth==0, cell(E7b).depth==0) and rainNeg measurable)` + `sample(engine.nextPulseTick)` |
| E3 | **glasswalk speed**: 750 calls of `step_game_ticks(2)` to time a walk between two x lines, because `S.run(10)` sampled every ~80 ticks and produced a FALSE 0.65 speed ratio (SUMP_GLASSWALK_SPEED_RATIO_1) | Utils/scenes/l2_glasswalk_20261010.py:18-26 | wrong number from coarse sampling, then 750 round trips to fix it | `watch(edge(pawn.x ≥ x0))`, `watch(edge(pawn.x ≥ x1))` → two exact ticks, 1 advance call |
| E4 | gravel wait_depth: step 250, read depth, until changed, limit 6000 | FlowWorks/northstar/gravel_live.py:313-321 | 24 iterations × 2 calls; 250-tick resolution | `until(changed(cell.depth))` |
| E5 | sprinkler `until_pulse` first version waited on a MAP-GLOBAL Pulses counter, returned on ANOTHER head's pulse, read this head 60-130 ticks early (T21, T22, acid arm stale) | FlowWorks/northstar/sprinkler_live.py:229-234 | wrong-subject trigger; workaround = wait a whole interval blind | `until(changed(reflect(head.lastPulseTick, thing=id)))` — per-subject watch |
| E6 | lacquer job: step 150, read selected pawn's job, until RM_LacquerWornItem seen then gone (30 tries) | LuminousPigment/live_probes/lp_lacquer_press_rightclick.py:102-111 | a short job can start and end inside one 150-tick gap: missed event | `watch(pawn.job == X)` edge events (start tick, end tick, duration) |
| E7 | Cauldron vexxiss: re-lay water under a WANDERING pawn and wait 120 ticks for a 60-tick poison tick, 3 attempts, else UNMEASURED | Cauldron/validation.py:1818-1834 | the subject moved between reads; UNMEASURED by design | `until(any cell in rect(follow pawn A, r=3) terrain == Toxic, within 180)`; `follow:` targets move with the pawn |
| E8 | pit_superdeep swim: step WARN_STEP, read exhaustion via static_call, pawn_get, ProofSwim headUp, until exhaustion ≥ warn | FlowWorks/northstar/pit_superdeep_walk.py:1285-1295 | 4 calls per step | `sample([exhaustion, pos, headUp], every=k)` + `until(exhaustion ≥ warn)` |
| E9 | owner_review_stage: loop time_clock + ticks(2000) until hour 10-14; stage_review.py "RimWorld has no cheap hour read here; step a bounded amount and stop" | FlowWorks/northstar/owner_review_stage.py:993-1001; Utils/stage_review.py:280-286 | blind time-of-day hunting in 2000-tick hops | `until(game.hour in [10,14])` — or better, the light predicate the review really wants: `until(cell.glow ≥ 0.7)` |
| E10 | Titanoslime digest: 50× ticks(120) and read every pair, track held/heldClock | GelatinousSlime/northstar/titanoslime_gates.py:397-411 | 50 × (1+pairs) calls | multi-watch: one `watch(edge(held==0))` per pair, one advance |
| E11 | Graffiti v1: `while not done(read)`: step STEP, read | Graffiti/graffiti_v1_live_proof.py:286-289 | generic advance-until written by hand | `advance_until(reflect(...))` |
| E12 | Webwork harvest: step, re-read clock (it "stopped answering mid-walk"), read ProofHarvestRead | Webwork/webwork_harvest_live_proof.py:141-150 | clock re-read each step to know how far it went | until result carries `tickFrom/tickTo/executed` |
| E13 | Scarlands hospice: safe_advance ADVANCE_STEP then static_call WalkInRead until PASS or gone | Scarlands/hospice_live_proof.py:111-118 | already on safe_advance — shows authors WANT until; they hand-roll it | `advance_until(reflect.call("WalkInRead") startswith PASS ∨ thing gone)` |
| E14 | LuminousPigment glowtank: 12× step 500 + list_things in rect until a cultured crop appears | LuminousPigment/live_probes/lp_glowtank_seed_sow.py:49-54 | 500-tick resolution; 24 calls | `until(count(thing def X in rect) ≥ 1)` (spawned predicate) |
| E15 | l1 donor-off: 20× ticks(250) + set_current_map + list pawns until the colonist is back on the home map | Utils/modcheck/l1_donor_off_round.py:1043-1050 | map switching inside the poll | `until(pawn(id).map == home)` |
| E16 | BlueDesert cold wax: 9× set room heat 35, wait 500, count RM_ColdWax until 0 | BlueDesert/validation.py:1285-1292 | heat re-applied by hand each step | `until(count==0)` with an `each_tick` hold action (`hold: room_heat=35`) |
| E17 | **flat wait budgets that ignore the pawn's stat**: fill_in_on waited 2,500 ticks; a Mining-0 pawn needs 16,000 → FAIL; the earlier PASS just drew a skilled pawn | lesson skills/live-debugging-proof-harness/references/sites-and-timing.md | the wait was a guess, not a condition | `until(cell filled, max = budget)` — a condition, not a guessed duration; the budget is only a ceiling |
| E18 | tick-keyed mod cache: a census 4 ticks after building a tank still read 'no port' (CompHoseReel.Port(), 60-tick cache) | lesson skills/rimbridge/references/traps.md | read too early by wall-time reasoning | `until(stays(port != null, 1))` or `settle(probe, quiet=60)` |
| E19 | **river-flooded pit**: the 05 PIT_ACCESS deep pit had a cell beside river sources and filled by gravity to f=1, spoiling the ladder-refusal demo | lesson skills/live-debugging-proof-harness/references/sites-and-timing.md | nobody watched the pit while staging | an **invariant watcher** armed at staging: `alarm(any cell in pit rect fill > 0)` — reports the tick it flooded and which neighbour fed it |
| E20 | step_game_ticks ~50 ticks/s on the 325-mod list (506 of 2000 in 10 s): an 8-day plant run ≈ 2.6 h | lesson skills/rimbridge/references/traps.md | wall time | use safe_advance (many ticks/frame) + TICKBURST; and `until` so we stop at the event, not at the guessed end |
| E21 | screenshot after step_game_ticks shows STALE tween positions (cost 5 identical wrong shots); PawnTweener lags ~0.85 cell | lessons skills/rimworld-live-review/references/traps.md, skills/rimworld-live-review/references/traps.md | visual evidence of a moving thing is unreliable while paused | state reads (`pawn.pos`, `pawn.drawPos`) recorded by the sampler instead of screenshots — the same argument as §4 flyers |
| E22 | **Relentless live lane**: 912 rows, **54% UNMEASURED**, top cause "the proof exited 2: it did not measure" / proof-or-site defect **231 rows** | design/RimMandrake/fast_testing_2026-11-05/ideas_inside.md §1.1 (from /home/mandrake/rm/relentless/live/runs.jsonl) | hand-rolled polls are where proofs break: a wrong chunk, a moved subject, a missed window, a site spoiled unseen | shared, tested primitives with three-valued results (true / false / UNKNOWN-and-why) |
| E23 | 57 copies of "loop get_ui_state until Playing, sleep" | e.g. bridgetools/prove_gravship.py:73, BlueDesert/prove_carbon_garden.py:78, FlowWorks/northstar/validation_v2.py:4916 | duplicated, each with its own budget and failure text | one `await_lifecycle(state="map_ready")` Python helper over a bridge-side readiness probe |
| E24 | `FIREHAWK_FLIGHT_BEHAVIOR_1`: ~35 min, ~25 screenshots, dozens of movement checks, caught nothing | skills/rimworld-modding/references/flight.md:22-30 | visual hunt of a short state | §4 flight state + frame-path recorder (joint session) |

### 2.3 What the evidence says, in four lines
1. **Resolution bugs** (E3, E5, E6, E7, E18): coarse advance-then-read gives a wrong answer or misses the event.
2. **Round-trip cost** (E1, E2, E8, E10, E14): 2-5 calls per poll iteration, 60 ticks/s stepping.
3. **Guessed durations** (E17, E9, E16): a wait expressed as ticks instead of as a condition.
4. **Unwatched sites** (E19, E22): nothing was watching the thing that spoiled the test.

## 3. The lego set

Three layers, each small: **probes** (read one value), **predicates & combinators** (turn values into true/false over
time), **runners** (decide when to evaluate and what to do on a hit). Everything is data (JSON); Python builds it,
the companion evaluates it. No mod-specific C#.

### 3.1 Values are three-valued, never silently zero
Every probe returns `{v, ok}` where `ok` is `true` or a reason: `gone` (pawn/thing despawned or dead), `oob` (cell off
map), `unbound` (type/field/mod not loaded), `error:<Type>` (exception, message kept). Predicates over a not-ok value are
**UNKNOWN**, not false. `until` never fires on UNKNOWN unless the tree says so (`is_unknown(p)` / `on_unknown: "stop"`,
default `stop` with `state=unknown` naming the probe). This is the instrument-trap rule (a 0 is a query bug until a
sanity probe proves the instrument can see) built into the wire format. Every arm evaluates once **at arm time** and
returns the initial values (`atArm`): the caller sees the instrument can see before a single tick runs, and a condition
already true at arm is reported as `trueAtArm` (level) and does not count as an edge.

### 3.2 Probes (value sources) — catalogue
Targets: `cell:[x,z]`, `rect:[x,z,w,h]`, `cells:[[x,z],...]`, `pawn:<id>`, `thing:<id>`, `kind:<PawnKindDef>`,
`def:<ThingDef>`, `follow:{pawn:<id>, r:<n>}` (a rect re-centred on a moving pawn each evaluation — E7), `map` (current
or `mapId`). Rect targets take a **reducer**: `max|min|sum|mean|count_where(pred)|any(pred)|all(pred)|frac(pred)|
argmax|cells_where(pred)` (the last returns the cell list — used by the light-front and flood cases).

| id | probe | returns | engine read (reuse) | cost class |
|---|---|---|---|---|
| P1 | `cell.terrain` (layer top/under/foundation) | defName | TerrainGrid (get_terrain_layers) | C0 |
| P2 | `cell.is_water` | bool (TerrainDef.IsWater) | TerrainGrid | C0 |
| P3 | `cell.fluid` (FlowWorks: depth level, fill f, fluid def, isSource) | number/def | FlowWorks map comp (canal_cell_report, excavation_rect) via a registered **field adapter** (§3.7) | C0 |
| P4 | `cell.glow` | 0..1 GroundGlowAt | GlowGrid (glow_at) | C0 |
| P5 | `cell.psych_glow` | Dark/Lit/Overlit | GlowGrid | C0 |
| P6 | `map.sky_glow` | 0..1 CurSkyGlow | SkyManager | C0 |
| P7 | `cell.roofed` / `cell.roof` | bool / defName | RoofGrid | C0 |
| P8 | `cell.temp` / `room.temp` | °C | GenTemperature / Room | C0 |
| P9 | `cell.fire` / `cell.fire_size` | bool / max Fire.fireSize | ThingGrid filtered by Fire | C1 |
| P10 | `cell.snow` / `cell.sand` | depth | SnowGrid | C0 |
| P11 | `cell.things` (def/category filter) | count / ids | ThingGrid | C1 |
| P12 | `cell.pollution`, `cell.fog`, `cell.zone`, `cell.home` | bool/def | grids | C0 |
| P13 | `cell.pathcost` / `cell.walkable` / `cell.standable` | number/bool | PathGrid | C0 |
| P14 | `reach(from pawn/cell, to cell, traverse)` | bool | Reachability (cached by region) | C2 |
| P15 | `pawn.pos` / `pawn.drawpos` / `pawn.rot` / `pawn.map` | cell / vec / Rot4 / mapId | Pawn | C0 |
| P16 | `pawn.dist(cell|pawn|thing)` | cells | — | C0 |
| P17 | `pawn.job` / `pawn.jobdriver_toil` / `pawn.lord_job` / `pawn.duty` | defName / index | jobs.curJob | C0 |
| P18 | `pawn.need(def)` / `pawn.mood` / `pawn.break_threshold` | 0..1 | needs | C0 |
| P19 | `pawn.hediff(def)` (present/severity/part) | bool/number | health.hediffSet | C1 |
| P20 | `pawn.state` (downed/dead/mental/drafted/hostile/asleep) | enum/bool | Pawn | C0 |
| P21 | `pawn.stat(def)` / `thing.stat(def)` | number (cached stat, `bust` opt-in) | StatWorker | C2 |
| P22 | `pawn.flight.*` (state, flying, flyingTicks, cooldown, lerpTick, canFlyNow) | enum/number | Pawn_FlightTracker (pawn_flight fields) | C0 |
| P23 | `pawn.anim.*` (CurAnimation defName, AnimationTick, keyframe index, frame texPath) | §4 | PawnRenderTree | C1 |
| P24 | `thing.exists` / `thing.spawned` / `thing.hp` / `thing.pos` / `thing.def` | — | Thing | C0 |
| P25 | `thing.comp(type).field(path)` / `thing.field(path)` | any | reflection, compiled once to a getter delegate | C1 |
| P26 | `map.count(def or kind, rect?, faction?)` | number | listerThings / mapPawns | C1-C2 |
| P27 | `map.condition(def)` / `map.weather` / `map.rain_rate` / `game.hour` / `game.tick` / `game.season` | — | — | C0 |
| P28 | `static.field(type, field)` | any | reflection (adapter: FlowWorks engine nextPulseTick, GSS settings) | C0 |
| P29 | `static.call(type, method, args)` | string/number | a mod's own `Proof*` hook (jawa/static_call), **opt-in, `every ≥ 10` enforced, per-call ms reported** | C3 |
| P30 | `ring.count(source, filter)` since arm | number | damage_log, incident_journal, heat_events, letters, messages, vitals triggers | C0 (cursor diff) |
| P31 | `log.count(level, regex)` since arm | number + first matching text | the drain_log capture (a Verse.Log postfix already installed) | C0 |
| P32 | `room.role` / `room.cells` / `room.openroof` | — | Room | C1 |
| P33 | `power.net(thing).stored/produced` / `fuel(thing)` / `refuel` | number | CompPowerTrader/Battery/Refuelable | C1 |
| P34 | `wall.ms` / `tps` | number (NON-deterministic, for perf conditions only; flagged) | Stopwatch / tps sampler | C0 |

Cost classes (to be MEASURED in the first build, not assumed): C0 a field read (target < 1 µs); C1 small list scan
(< 10 µs); C2 cache-dependent (< 100 µs typical, unbounded worst case); C3 arbitrary mod code (unbounded: measured per
call, auto-throttled).

### 3.3 Predicates over values
| id | predicate | meaning |
|---|---|---|
| Q1 | `cmp(p, op, v)` | `== != < <= > >=`, `in [a,b]`, `in {set}`, `matches /re/` |
| Q2 | `changed(p)` | value differs from its value at arm (or at last hit, `rearm`) |
| Q3 | `delta(p, op, d)` | v − v_atArm compares to d ("rose by 0.3") |
| Q4 | `rate(p, op, r, window=N)` | slope over the last N evaluations ("draining faster than 0.01/tick") |
| Q5 | `settled(p, quiet=N)` | unchanged for N ticks (the cache / settling case E18) |
| Q6 | `is_unknown(p, reason?)` | the probe could not see (explicit, e.g. "until the pawn is gone") |
| Q7 | `crosses(p, v, dir=up|down|either)` | sugar for `edge(cmp(...))` with hysteresis `band` to stop flicker at a threshold |

### 3.4 Combinators (time-aware)
| id | combinator | semantics |
|---|---|---|
| K1 | `all[...]`, `any[...]`, `not` | Kleene three-valued logic (UNKNOWN propagates: `any[true, unknown]` = true, `all[true, unknown]` = unknown) |
| K2 | `edge(c, rise|fall|both)` | true only on the evaluation where c changes; carries `lastOtherTick` so the real transition is bracketed in `(lastOtherTick, tick]` |
| K3 | `level(c)` | the default: true whenever c is true |
| K4 | `stays(c, N)` | c has been true for N consecutive ticks (debounce; "stays dry for 600 ticks") |
| K5 | `within(c, N)` | c becomes true within N ticks of arm, else the node resolves FALSE at N (a deadline — "fills within 2500 or FAIL") |
| K6 | `seq[a, b, ...] within N` | a, then b after a, ... (ordering; "job starts, then cell changes, then job ends") |
| K7 | `count(edge(c), n)` | the n-th occurrence ("third pulse") |
| K8 | `after(c, N)` | true N ticks after c first became true (delayed check: "60 ticks after the fire starts, is the cell still wet?") |
| K9 | `while(guard, c)` | c is only evaluated while guard holds; guard false = UNKNOWN (scope a watch to "while the pawn is on this map") |
| K10 | `for_each(targets, c)` | instantiate c per target; result lists which targets hit (multi-plot; one watcher per pit/pair, E10) |
| K11 | `never(c)` | an invariant: true until c is ever true; a hit is a violation (E19 river flood) |

### 3.5 Runners (the calls Python makes)
| id | tool | does |
|---|---|---|
| R1 | `jawa/cond_eval {tree}` | evaluate once now, no tick; returns value tree with every probe's `{v, ok}`. For writing and debugging trees, and for the `atArm` sanity read. |
| R2 | `jawa/advance_until {until, max_ticks, every=1, stopOn, actions, sample?}` | safe_advance with a stop condition: runs until `until` is true, or max_ticks, or a vitals stop, or UNKNOWN (policy). Returns `state: hit | max | stopped | unknown | aborted | running`, `hitTick`, `bracket`, `values` at hit, `executed`, `tickFrom/To`, and the sample series if requested. Implemented INSIDE `SA.Frame` — evaluation after every `DoSingleTick` when `every=1` (moves the latch check inside the inner loop for cond runs). |
| R3 | `jawa/watch_arm {name, tree, mode: event|alarm|stop, every, max_events, actions}` → id | a persistent watcher evaluated after every tick of ANY advance (safe_advance, step_game_ticks, normal-speed play — via a postfix on `TickManager.DoSingleTick`, the seam JawaBenchAllocProbe already patches). Emits events into a ring; `mode=stop` also emits a latch trigger so safe_advance stops on it; `alarm` = invariant (K11). |
| R4 | `jawa/watch_read {since_seq}` / `watch_list` / `watch_clear {id|all}` | events with `tick`, `bracket`, `watcher`, `values`, `seq`; status per watcher (evals, ms used, last value, achieved resolution, disarmed-why) |
| R5 | `jawa/sample_arm {name, probes, every, max_rows, on_change_only}` / `sample_read {since_seq}` | time series rows `[tick, v1, v2, ...]`, ring buffer; `on_change_only` makes it a change log (flight frames §4, light fronts) |
| R6 | `jawa/field_snapshot {name, probe, rect}` / `field_diff {a, b}` | a whole-rect value grid at a moment (glow, fluid, terrain, temp) and a cell-wise diff — before/after evidence in one call (§5) |

`advance_until` = arm a `mode=stop` watcher + `safe_advance` + read + clear, done atomically in one call so nothing leaks.

### 3.6 Actions on trigger (all optional; default `stop`)
`stop` (end the advance, pause), `pause_only` (pause, leave the run resumable — `action=resume`), `event` (record and
keep going), `snapshot` (attach `values` of named extra probes to the event — "when it floods, also read the 8 neighbours'
isSource"), `field_snapshot` (R6), `dump` (a screenshot-free state dump: the vitals row + named probes + pawn jobs within
r), `screenshot` (**opt-in only, never for flyers**, never on the tick thread — queued to the next frame after pause),
`hold` (per-tick re-assertions while armed: `room_heat`, `need level`, `pawn_flight hold` — for the BlueDesert E16
pattern; a hold is listed in the result, never invisible), `rearm` (count repeated events). No action runs mod code
except an explicit `static.call`.

### 3.7 Field adapters (generic, data-registered — how mod fields become probes without per-mod C#)
A probe `adapter:<name>` maps to a reflection recipe in a JSON file deployed with the companion
(`bridgetools/cond_adapters.json`): `{"flowworks.cell": {"type": "RimMandrake.FlowWorks.MapComponent_Depth",
"getter": "FillAt(IntVec3)", "fields": ...}}`. Compiled to delegates once per map load; `unbound` (not error) when the
mod is absent. Names in the adapter file are verified by `measure`/def dumps at authoring time, never guessed. This
keeps FlowWorks water (owner's "water in this cell"), GSS cord tension, Titanoslime held mass, etc. in data.
(⚠ the FlowWorks type/method names above are PLACEHOLDERS in this draft, to be read from source before build.)

### 3.8 Wire format (JSON)
```json
{"until": {"all": [
    {"cmp": [{"p": "cell.fluid", "cell": [106,103], "f": "fill"}, ">=", 0.5]},
    {"not": {"cmp": [{"p": "pawn.state", "pawn": "Human123", "f": "downed"}, "==", true]}}
  ]},
 "max_ticks": 6000, "every": 1, "on_unknown": "stop",
 "watch": [{"name": "dry", "tree": {"edge": {"cmp": [{"p": "cell.is_water", "cell": [110,90]}, "==", false]}, "dir": "rise"}, "mode": "event"},
           {"name": "light_front", "tree": {"crosses": [{"p": "cell.glow", "cell": [40,40]}, 0.3], "dir": "up", "band": 0.02}, "mode": "event"}],
 "sample": {"every": 60, "probes": {"sky": {"p": "map.sky_glow"}, "lit": {"p": "cell.glow", "rect": [30,30,20,20], "reduce": "frac", "where": [">=", 0.3]}}},
 "actions": {"on_hit": ["stop", {"snapshot": {"n8": {"p": "cell.fluid", "rect": [105,102,3,3], "reduce": "cells_where", "where": ["isSource", "==", true]}}}]}}
```
Rules: every node has an optional `"id"` (echoed in results); unknown keys are refused by name (ArgGuard pattern,
JawaBenchArgGuard.cs); the parsed tree is echoed back canonicalised so Python can diff what the game understood; trees
are compiled once at arm (defs resolved, delegates built) — a defName that does not resolve is a refusal at arm, never
a silent false at tick 4000. Size cap (e.g. 256 nodes, 4096 cells per rect probe) refused by name.

### 3.9 Evaluation cost and the per-tick budget
- Budget: total watcher + until evaluation **≤ 0.5 ms per tick by default** (`evalBudgetMs`), measured with a
  Stopwatch around evaluation and reported per watcher (`msTotal`, `msMaxPerEval`, `evals`).
- Each node declares `every` (default 1 for C0/C1, 10 for C2, 60 for C3). Rect reducers on > 400 cells default to
  `every = 10`.
- Over budget: the engine does NOT silently thin evaluations. It reports `overBudget` with the achieved resolution and,
  per policy (`budget_policy: "stop" | "degrade"`), either stops with state `budget` or doubles `every` for the most
  expensive watcher and records that in the result (`resolutionTicks` per watcher is always in the result).
- Edge bracketing makes coarse evaluation honest: an event at `every=10` reports `bracket: [t-10, t]`.
- The evaluator itself must be cheap: compiled delegate tree, no LINQ/allocation per tick (the AllocProbe tool can prove
  0 GC per eval — a selftest bar).

### 3.10 Determinism and timestamps
- `tick` = `Find.TickManager.TicksGame` read **after** the DoSingleTick that produced the state (evaluation point =
  end of tick, after all map/game component ticks). Documented as "state as of end of tick t".
- With `every=1` the hit tick is exact and the bracket is `(t-1, t]`. Two runs from the same save + same tree give
  the same hit tick where the simulation is deterministic (RNG seeded from the save); any difference is itself a
  finding (the determinism probe GSS already runs).
- Clock discontinuities (`time_set_ticks`, load) are seen by the vitals clock ledger: events after one carry
  `epoch+1` and K4/K5/K8 timers are refused across an epoch rather than computed across a jump.
- Wall time (`wallMs`) is reported alongside but never used in a predicate except P34 (flagged non-deterministic).
- Normal-speed play (joint sessions): watchers still evaluate per tick through the DoSingleTick postfix; timestamps are
  still ticks.

### 3.11 Safety
- **Vitals latch stays in charge.** `advance_until` is safe_advance: every default stop kind still stops it, the 30000
  budget / timeException / 1.2 M refusals still apply, game-change/map-gone still abort. A condition can only END an
  advance earlier, never extend one.
- **Threat interrupts**: default `stopOn` kept; add `log_error` as an optional stop kind (P31) and `cond_unknown`.
- **Command limits**: one `advance_until` call waits at most `timeoutMs` (default 300 000, Python passes ≤ 480 000 so
  the Bash call fits in 540 s); after that it returns `state=running` and the run CONTINUES in game; Python re-attaches
  with `action=status` in a new call (the existing safe_advance pattern). Python helpers write a progress line on every
  return (the 600 s silence rule).
- **Watcher hygiene**: watchers are scoped to a game + map (cleared on load/menu, like SA.Run); `watch_list` is part of
  `site_state`; a harness `finally` calls `watch_clear(all)`; an orphan watcher older than N minutes with no reader logs
  one warning. Exceptions inside a probe disarm that watcher with `disarmedWhy` (never swallowed, never kill the tick).
- **No writes from conditions.** Only `hold` actions write, they are explicit, listed, and refused unless the run is
  armed as a test (`FTestOnly` safety flag, JawaBenchSafetyCore.cs:102).
- **Flyers**: `pawn_flight hold/start` as a `hold` action is refused unless `jointSession=true` is passed (§4 gate).

### 3.12 Python wrapping (validation_core API)
New module `src/RimMandrake/Utils/conds.py` (builders) + methods on `_BridgeBase`:
```python
from conds import cell, pawn, rect, thing, ring, log, game, all_, any_, not_, edge, stays, within, seq
r = B.until(cell(106, 103).fluid("fill") >= 0.5, max_ticks=6000)            # -> Hit(state, tick, bracket, values)
if r.state == "max": row("PIT_FILLS", "FAIL", "no fill in 6000 ticks", r)       # the condition IS the verdict
with B.watch("dry", edge(cell(110, 90).is_water == False)) as w:               # context manager clears on exit
    B.ticks(2500)                                                              # any advance; watcher sees every tick
for ev in w.events: ...                                                        # ev.tick, ev.bracket, ev.values
s = B.sample({"x": pawn(pid).pos.x, "ex": thing(pid).field("swimExhaustion")}, every=10, ticks=1200)
B.cond_eval(tree)                                                              # debug a tree without ticking
```
- Operator overloading builds JSON (`>=` returns a Q1 node); `.json()` prints it; names are checked offline against
  `tool_schemas.json`.
- `B.until` returns a typed result; `state == "unknown"` maps to UNMEASURED with the probe's reason; `stopped` maps
  through clockgate's existing GovernorStop / site_recover path; `max` is the caller's FAIL/UNMEASURED decision.
- **Offline twin**: `conds.evaluate(tree, series)` evaluates the same semantics over a recorded series in Python. One
  JSON vector file `conds_vectors.json` (tree, series, expected hits) is run by the Python selftest AND by a C# selftest
  through `cond_eval` on a fake series — the two evaluators cannot drift.
- Migration: `northstar_driver/lint_calls.py` gains a rule flagging the advance-read loop pattern of §2.1 (same AST
  heuristic) as a warning with "use B.until"; `await_lifecycle()` replaces the 57 copy-pasted ready loops.

## 4. Flyer frame recording (state, not pictures) — joint-session gated

Standing rulings: *"NEVER live-test a flyer's flight without the owner present"* and *"Don't try to capture images of
flight. It doesn't work."* The owner's ask ("return the series of images that are iterated between while it flies
around") is met by recording WHICH texture the engine selects on each tick, then assembling the picture offline from
the PNGs on disk. No screenshot is taken at any point.

### 4.1 Why this is a deterministic state read (decomp, rw16)
- `AnimationDefGenerator_Flying.CreateAnimFromFrames` builds one AnimationDef per facing (east/north/south; west
  mirrors east): one Keyframe per frame at `tick = i*ticksPerFrame`, `durationTicks = (count+1)*ticksPerFrame` (so a
  last-frame dwell or a gap slot exists — the recording settles which), keyframes on the "Body" tag node with
  `AnimationWorker_Keyframes`; each frame carries a GraphicStateDef `<defName>Fly<Dir>_<i>` whose
  `defaultGraphicData.texPath = prefix + i + "_dir"`.
- `Pawn_FlightTracker.CheckFlyAnimation()` picks `GetBestFlyAnimation(pawn)` and calls
  `pawn.Drawer.renderer.SetAnimation`.
- `PawnRenderTree.AnimationTick = TicksGame − animationStartTick` (looped or clamped); each node takes
  `AnimationWorker.GraphicStateAtTick(AnimationTick, ...)`.
- So the frame on screen is a pure function of game state. It can be read on every tick without drawing anything,
  identically while paused.

### 4.2 Probe P23 and the recorder
`pawn.anim` returns `{anim: defName|null, animTick, loop, keyIndex, graphicState, texPath, facing, mirrored}`. With
`pawn.flight` (P22: state, flying, flyingTicks, lerpTick, cooldown) and `pawn.pos/drawpos/rot`, a `sample_arm` with
`on_change_only` over `[flight.state, anim.anim, anim.keyIndex, rot]` produces the flip-book as data:
`tick, state, facing, keyIndex, texPath, drawPos`. Tool sugar is `jawa/flight_frames {pawn, ticks}`, a sample_arm
preset; that is the only flyer-specific code.

### 4.3 What the offline check proves (Python, no game)
- Every recorded texPath resolves to a PNG on disk (via reading-rimworld-graphics), for every facing.
- The cycle order is 0..n−1 with the expected per-frame dwell (`ticksPerFrame`), and the last-frame or gap behaviour
  is measured, not assumed.
- Facing follows movement: rot against the drawPos delta, and west is mirrored from east.
- Takeoff, flying, landing: the animation is set on takeoff and cleared on landing, and `flyingTicks` is bounded.
- Output is a flip-book sheet built from the disk PNGs in recorded order, at true scale beside a vanilla human
  (review-sheet rule), with an animated GIF of the recorded sequence. This is "the series of images", produced
  without a camera.
- An offline-only precheck needs no game at all: the frame set and its texPaths can be computed from the def plus the
  decomp rules, so missing frames fail before any session.

### 4.4 The gate
- **The first live run of flight recording is a joint session with the owner present.** The spec ships with the
  recorder built and selftested offline (fake series through the C# evaluator via `cond_eval`, and the generated
  AnimationDefs read with flight never started). It is not run on a flying pawn until that session.
- `pawn_flight start/hold` as an action or hold requires `jointSession=true`, and the tool refuses it otherwise. No
  unattended script may pass that flag. The lint rule flags it.
- No screenshot action is accepted in a tree that includes P22 or P23.

## 5. Proactive muse (ranked by value per effort)

1. **Invariant monitors on every advance (K11 `never` + R3 alarm).** A default watcher pack that harnesses arm once:
   no new red log line, no pawn of ours downed, no fire in the plot rect, no water outside the plot (E19), and no
   thing of ours destroyed. Every proof then gets "nothing else went wrong" for free, at the exact tick it happened.
2. **`await_lifecycle()` and a readiness probe** (`game.ready`: program state, map loaded, LongEvent idle, and the
   bridge tool count). This removes 57 copy-pasted load loops (E23) and the most common source of harness flake.
3. **Log-error trigger (P31) as a stop kind.** Stop at the tick of the first red error with a state dump. This turns
   "the log has 40 errors after 8000 ticks" into "error at tick t, during job J, at cell c".
4. **Field snapshot and diff (R6).** One call gives a before/after grid of fluid, glow, terrain or temperature. It
   proves "water spread exactly to these cells", "light reached here" and "nothing else changed" without per-cell
   loops (E3, E5).
5. **Settle or quiescence detector (Q5 over a rect aggregate).** "Advance until the flow field stops changing for 300
   ticks." This replaces the guessed fill-wait durations (E17, E8).
6. **Per-plot `for_each` (K10).** One advance drives N plots, each with its own hit tick, which is the FlowWorks v2
   pattern (E1, E2). Combined with TICKBURST, the 269 s run4 becomes a few calls.
7. **Job-refusal trace.** A probe over `workgiver_probe` returning *why* a pawn will not take a job, so it can be
   sampled ("why is it still idle at tick t?") (E6, E7).
8. **Path and reachability probes (P13, P14).** "Until the pawn can reach X" and "never unreachable": canal crossings,
   bridges and Glasswalk lanes.
9. **Determinism replay.** Run the same tree twice from the same save and compare hit ticks and series. Drift is a
   finding, and this generalises the GSS determinism probe.
10. **Perf conditions (P34, flagged).** "Stop if TPS stays under 30 for 600 ticks." Perf rows then carry the tick of
    the slowdown instead of an average.
11. **Recorded series as fixtures.** Any sample series can be saved as a JSON fixture and replayed through
    `conds.evaluate` for offline regression of predicate logic (offline twin, §3.12).
12. **Light and dark fronts.** `cells_where(glow >= x)` sampled every 60 ticks over a day gives the light map as a
    function of time: "alert when light reaches this location" for glowtank (E14), plus dark-spawn conditions.
13. **Incident and letter cursor conditions.** "Until the incident fires" and "never a raid": quest and incident mods
    can prove timing without reading letters by hand.

## 6. Leftovers: not polling or condition primitives

- **TICKBURST_PROVE_MANY_TICKS_ONE_FRAME** is a separate item and is not designed here. Its premise is factually wrong
  for safe_advance: safe_advance already runs up to 60 ticks per chunk, chunked by `frameBudgetMs`. Its premise is true
  of `rimworld/step_game_ticks`. The real gain is raising the per-frame tick budget while paused. advance_until
  composes with it, because the condition is checked per tick whatever the chunking.
- Cold-load cost (25 min on the full list) belongs to the load-round and minimal-list work, not here.
- Bridge round-trip latency (about 50 ms per call; L_preflight made 371 calls in 19.8 s) needs batch read tools
  (`get_terrain_batch` exists; extend the pattern). §3 reduces the call count but does not fix per-call cost.
- Site staging and recovery (proof-or-site defects, 231 rows in runs.jsonl) concerns prepare_site and the fixtures, and
  is only partly helped by invariant monitors.
- PawnTweener lag in screenshots (E21) matters only for owner looks; state reads avoid it.

## 7. Proposed tickets (not filed; every name passed `rimflow namecheck` 2026-11-06)

| name | scope |
|---|---|
| CONDEVAL_BUILD_COMPILED_TREES | C# tree parser, compiler, three-valued evaluator, cond_eval, P1-P34 C0/C1 probes, ArgGuard, vectors selftest |
| ADVANCEUNTIL_BUILD_PER_TICK_STOP | advance_until inside SA.Frame per tick, latch kind `cond`, bracket and resolution, status resume |
| WATCHRINGS_BUILD_EVERY_TICK_EVENTS | watch_arm/read/clear, sample_arm/read, the DoSingleTick postfix, budget accounting, scoping and hygiene |
| CONDSDSL_WIRE_PYTHON_BUILDERS | conds.py builders, `_BridgeBase.until/watch/sample`, CondStop, offline twin, shared vectors |
| CONDADAPTERS_WIRE_FLOWWORKS_FIELDS | cond_adapters.json, FlowWorks/GSS adapters with names read from source |
| POLLLOOPS_MIGRATE_TO_UNTIL | lint_calls rule, migration of the top 10 cases (E1-E10), await_lifecycle |
| INVARIANTPACK_BUILD_NEVER_WATCHERS | the default `never` watcher pack (§5.1) and log_error stop kind |
| FIELDSNAPSHOT_BUILD_GRID_DIFF | R6 grids and diff |
| FLYERFRAMES_PROVE_JOINT_SESSION | P23, flight_frames preset, offline checker and flip-book sheet; first live run only with the owner present |

Build order: core, then advance_until, then the Python DSL (usable at that point), then watch/sample, then adapters,
lint and invariants, then the flyer item last, at a joint session.
