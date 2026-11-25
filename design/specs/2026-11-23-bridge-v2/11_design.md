# BRIDGE v2.0: the design

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_PYTHON_TESTS_FEW_RICH_ENTRY_POINTS`. Written 2026-11-23. The Conductor enacted the
pick of pass three on 2026-11-23 (delegated; on the item). This file is the design. It points at three things and does
not repeat them: the argument and the counts (`08_where_tests_live.md`), the survey of today's tools
(`09_entry_points.md`), and the contract of each entry point (`contracts/`, start at `contracts/README.md`). The build
order is the last section of `06_build_order.md`. Tags: READ, MEASURED, GUESS n%.
**Design Version of the scene library and its hands: 0.1.0.** Nothing here has run in a game.

## The architecture, in six sentences

1. **A live test is a Python script on one library.** The library is `src/RimMandrake/Utils/scene.py`. It has ten
   names. The script decides the sequence, the moment to stop, and what to do next.
2. **The bridge is the hands.** The C# companion holds generic instruments and acts: stop on a condition at an exact
   tick, record values and events on every tick, read a value, write a value, stage, force, calm. A hand names no scene
   and gives no verdict.
3. **The verdict is made outside the game**, by `scene.judge`, from a kept trace. A trace can be judged again with no
   game.
4. **Every entry point returns a receipt**: what it did, on which game and loaded build, which hands it called, what it
   could not look at.
5. **Python is selected when the scene is built, not while it plays.** An agent writes or edits a script, and the script
   runs. No agent chooses tools during a run that counts.
6. **The list grows from use.** A thing becomes an entry point, a verb or a reader after two real scenes needed it. A
   struggle in Python becomes a ticket for a better hand.

The owner's words that fix this, all of 2026-11-23, on the item: "The 'Rich' entry point could be in the Python that
drives the bridge, and BRIDGE is just the underlying 'hands' functions"; "for PYTHON to select at build-time, not for
the agent to select during play-time"; "I don't think we need a YAML scene language"; "YES, Python entry point receipts
are excellent"; "I am willing to read one-page contracts".

## The ten names

`scene.contract`, `scene.open`, `s.stage`, `s.run`, `s.act`, `s.read`, `scene.judge`, `s.shot`, `scene.attach`, `s.raw`.
One page each in `contracts/`. Ten names are about twenty operations (`s.act` has ten verbs); the pages say so.

Three wanted capabilities, and the name that reaches each:

| capability (his words: "hidden variable reads, per-tick captures and actions") | name | hand behind it |
|---|---|---|
| read a hidden value once: a private field, a static of a mod, a def value | `s.read` | `jawa/read_paths` (new; read-only) |
| capture values on every tick, a hidden one included | `s.run(record=...)` | `jawa/run_until` (the landed slice, widened) |
| act on an exact tick; several acts with no frame between them | `s.run` to the tick, then `s.act` or `s.act.batch()` | `jawa/run_until`, `jawa/act_batch` (new) |
| write a live value, like RIMMSQoL ("modifying variables live, in-game") | `s.act.tune` | the overlay of `04_live_tuning.md` |

**A tuned run can never pass.** `s.act.tune` marks the game process from the first write until the game restarts. The
game holds the mark and writes the stamp TUNED into every later receipt, run and picture, in every session of that
process. A save written in a marked process carries the mark inside the file, and a game that loads it is marked, so a
restart does not clean a tuned world. A raw call that can change the game marks the process EXPLORED in the same way.
`scene.judge` sets `counts_for_bar = False`, and the verdict ledger records TUNED, never PASS (`contracts/act.md`). A
tuning target needs a write recipe; with none, the write is made only as UNVERIFIED. `04_live_tuning.md` stays the design of what can be
written and when a write acts; this file only fixes its door: one verb, no second tool beside it.

## The five questions of `00_owner_topics_interfaces.md`

### 1. The contract of each entry point
`contracts/<name>.md`, one page for each of the ten, each in the same seven parts: what it is for; what it accepts;
what it returns, with its receipt; its state changes; what it refuses, by name, with the repair; one example from a
real scene of ours; the check that turns red. Each has a last part, its limits. The pages are written before the code,
and the code is built to them.

### 2. Read the contract, not the internals
The pages live beside the code, in `src/RimMandrake/Utils/scene_contracts/` (moved 2026-11-23); `contracts/` here holds one
pointer line, and `contracts/<name>.md` in this folder's files means the page there. One step finds them:
`python3 src/RimMandrake/Utils/scene.py help` prints the README, and `help <name>` prints a page. The Tools block of the
root `CLAUDE.md` gets that one line when the library lands. An author reads at most the README and the pages of the
names the scene uses; the 563 tool schemas and the five older driver layers are not read.

### 3. Rigid interfaces and gates
Five gates, each red at once:
- **At the call.** Every name checks its arguments before any bridge call and raises `scene.Refused(NAME, repair)`.
  Nothing was changed when a refusal is raised.
- **One contract test for each refusal and each promise**, of the same name as on the page, in
  `src/RimMandrake/Utils/selftest_scene_library.py`, against a fake bridge that replays recorded replies. The tests run
  at `./publish`. They prove what the Python does.
- **A live proof for each promise about the game** (the stop tick, no frame inside a batch, a read-back, the mark). A
  fake reply cannot prove these. Each proof checks the hand's answer against a second, independent reading, is written
  by the ticket that builds the hand, and reads UNRUN until it has run.
- **Page against signature.** A selftest compares each page's Accepts table with the function's signature. A page that
  names an argument the function does not take is red, and so is the reverse.
- **At acceptance.** `scene.py accept <script>` refuses a tree that is not clean, and a script that imports an older
  driver layer or the bridge client (`IMPORTS_OLD_LAYER`). A stamped run does not count.
A fault of form in a call is returned to the same agent with its repair, in the same run; no refusal here stops a mod.

### 4. Brain and hands
| | decides | acts and records |
|---|---|---|
| the scene's sequence, its branches, when to try again | Python (the script) | |
| the verdict | Python (`scene.judge`, from the trace) | |
| the moment to stop a running game | Python gives the condition as data | the game evaluates it at the end of each tick and pauses |
| acts, reads, recording, staging, calm | Python asks | the game does, reads back, writes the trace and the receipt |

The stop condition is the one piece of test data that the game evaluates. It carries no verdict and names no scene. The
kept exception of pass three stands: when experiment A shows that an act from Python gives a different state, that act
is done in the game by a generic facility (a batch, a bounded rule), still not by a scene in C#.

### 5. The owner's part
He reads contracts, not code, and he does not write them: agents write a contract, and he reacts to a concrete page.
Before the build he reads `contracts/README.md`, then `run.md`, `act.md` and `read.md` (they hold the three capabilities
he asked for), then `judge.md`. The other five are for a second sitting or not at all. After the build, a change to
what a page accepts, returns or refuses is a change of the library's Design Version, and it reaches his daily digest
with the page's diff. None of this is one of his five acts; his word still changes any page.

## The Conductor's five challenge points

1. *Rich entry points and tests in Python conflict when the rich layer is C#.* Settled: the rich layer is Python.
2. *A rich entry point is a bigger instrument, so it needs a receipt.* Taken: the receipt is in every contract, and the
   game fills the build lines.
3. *A rigid contract can freeze a wrong abstraction.* Taken: `s.raw` keeps every tool reachable, the promotion rule is
   "needed twice by real scenes", and the first build is two names and three scenes, not ten names at once.
4. *He does not write interfaces.* Taken (question 5).
5. *"Few rich beats many" is unmeasured here.* True. The records class past failures by symptom (24 blind reads, 22
   harness or transport, 5 wrong build `[READ]`), not by "a wrong tool was chosen", so the count asked for is
   `UNMEASURED` from records. The conversion ticket measures it on three scenes: a fresh agent with only `scene.py help`,
   against the old scripts, by lines, calls, reruns and spoiled runs.

## The promotion rule, and the struggle rule

- **Promotion.** `scene.py raw-census` lists every `s.raw` call in the committed scenes, as a proposal that a reviewer
  decides. What is promoted is a typed operation that two scenes share, never a tool name: two calls of
  `jawa/static_call` into different methods share nothing. It becomes a verb of `s.act`, a reader of `s.read` or a
  helper of `scene.cond`, with its line on a contract page and its test. A helper for one scene stays in that scene.
  The same raw sequence in two scenes, with no limit of the bridge behind it, becomes a Python helper.
- **Struggle.** Three signs that Python has met a limit of the bridge, each of which files a hands ticket and not a C#
  test: a poll loop on a running game; a proof helper compiled into a mod for one scene; a value that no path reaches.
  Evidence that this happens: 59 mod C# proof files hold 19,607 lines, and `jawa/static_call`
  into such helpers is the most used tool, 844 call sites `[MEASURED, 08]`.
- **Removal.** The deletion test of the Pocock study: delete the thing in your head; if the complexity vanishes, the
  thing was a pass-through and goes; if the complexity comes back in several callers, the thing stays.

## The hands

### Kept (the instruments behind the names)
The tools that 20 or more live files name are 58 `[MEASURED, 09]`. They stay, each with its promise on a boundary page
when it is next touched: the batch stagers, `jawa/ordered_job`, the damage, explosion and incident tools, the calm and
gate tools, `jawa/get_defs`, `jawa/mod_settings_field` (it joins the overlay), the off-screen capture, `jawa/static_call`
(reachable only through `s.raw`), and `jawa/scene_slice` until `jawa/run_until` replaces it.

### Unused today, and what happens to each
172 of the 430 `jawa/` tools are named by no live script `[MEASURED 2026-11-23]`. A tool that an agent calls by hand
leaves no file, and the bridge's call journal has not been counted, so "unused" here means "no script names it".

| group | count | route |
|---|---|---|
| authoring tools (`world_*`, `faction_*`, `ideo_*`, pawn and colony editing, lore, prefabs) | 108 | not test tools. They stay as they are, for world and map authoring. This design does not touch them |
| read and health tools: `get_pawns_batch`, `list_things_batch`, `get_power_nets_batch`, `pipe_net_info`, `cond_watch`, `first_exception`, `health`, `vitals`, `load_stall_probe`, `savegame_mod_match`, `startup_types` | 11 | **published**: the batch reads through `s.read_many`, `cond_watch` through `s.run(record=)`, the rest as phases of `scene.open` and lines of its receipt |
| cost probes: `alloc_probe`, `heap_census`, `texture_memory`, `game_comp_timing`, `tps_test_block`, `tps_test_attribution`, `telemetry_tier`, `telemetry_mark` | 8 | **published** as the cost lines of the `s.run` receipt when a scene asks for them |
| picture helpers: `settle_tweens`, `frame_finish`, `refresh_rect`, `nulltex_probe` | 4 | **published** inside `s.shot` |
| calm helpers: `rain_suppress`, `time_pin_normal_speed`, `forecast_incidents` | 3 | **published** as controls of the calm profile |
| act tools: `raid_shape_fire`, `settlement_attack`, `spawn_mech_cluster`, `map_skyfaller`, `transporter_launch`, `roof_collapse`, `send_letter`, `letter_send_delayed`, `trade_execute`, `manhunter_preview` | 10 | exploring layer; each becomes a form of `s.act.incident` or `s.act.place` when two scenes need it. These are also the acts that Inhabited will want |
| `scene_slice` | 1 | kept until `jawa/run_until` replaces it |
| the other 27 (for example `wipe_cell`, `connect_cells`, `fix_floating_roofs`, `rebuild_dirty_regions`, `autosave_now`, `scenario_select`, `timetable`, `wealth_recount`, `type_visibility`) | 27 | **deletion candidates**, by the deletion test. No tool is deleted on today's evidence. First count the journal for 30 days; then delete, in one curation pass, each tool that has no call and no caller, with its name in the commit. The list is `D:\ClaudeWork\rimmandrake\scratch\bridge_v2_pass3b\unused_jawa.txt` and is made again from the tree at that pass |

`scene.tools(words)` is how an agent finds any of them, with one line each. That is the publishing route for a
capability that nobody used because nobody could find it.

### New hands wanted, each with the evidence that needs it

| hand | evidence | ticket |
|---|---|---|
| `jawa/run_until`: the exact stop, with recording of any value path on every tick, for a session | FlowWorks `sc_moat_raid` gave PASS, FAIL, PASS in three valid runs on visit 9, and "the cause is not read"; the scene now polls each raider every 60 ticks from Python `[READ: visit_9/SUMMARY.md]`. Census: 3 to 4 of 31 merged rows are timing between calls `[READ, 08]` | `RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH` |
| `jawa/read_paths`: a read of private fields and statics, read-only | 24 of the 51 old non-mod FAILs were blind reads `[READ, 08]`; FlowWorks reads `held=` by a text search of a C# proof helper's output `[READ: concept_scenes.py, RM_PromotionProofs.cs]` | the same ticket (the recorder and the read share the path evaluator) |
| `jawa/act_batch`, and request ids | FlowWorks `sc_fill_front` starts two fills that the design wants on one tick; a lost reply can do an act twice `[READ, 08]` | the same ticket |
| the session that outlives its driver, paused | 22 of the 51 were harness or transport faults `[READ]`; visit 9 `sc_pit_trap_raid` "an unfinished capture" | `RIMMANDRAKE_HARDEN_RUN_LIFE_CYCLE_KILL_CANCEL_THROWN_TICK` |
| the read-back in the same hop as the write | visit 9: two staging faults found only after their scenes failed `[READ]` | `RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO` (its C# duty) |
| the overlay for live writes, with the stamp | his ask; the test pilot sitting of 2026-11-23 switched the melee rule off through `jawa/mod_settings_field`, with no stamp on the result `[READ: selftest_flowworks_moat_rim_stabs.py]` | `RIMMANDRAKE_BUILD_DEVIATION_RECORD_SETTINGS_FIELD_JOINS_FIRST` (built); def fields: dropped until a def value that is not a setting needs a live write (`06_build_order.md`, Later tickets) |
| event taps (spawn, death, damage, job), the load barrier, the order through the game's giver | pass two's evidence stands (`05`, decisions 4 and 2) | the tap tickets; the C# duties of the two split tickets |

## What serves Inhabited later

Inhabited places settlements and casts by defs and flat plans; it holds no LLM code. The in-game LLM is the Oracle mod,
under two laws: LLM output is display text or a menu choice that C# validates, and the game is whole without the LLM
`[READ: the Conductor's scan on the item]`. His aim: "a live-game BRIDGE use function to inject ... 'improve the tile
map' capability, 'improve the raid' capability". **The bridge is not an in-game LLM host.** That stays Oracle's.

What this design does now for that later customer, at small cost:
- **Hands are generic acts with typed arguments and a refusal by name.** "Improve the raid" is `incident` and `place`
  with arguments from a closed set; that is Oracle's menu law in another form. `GUESS 70%` that the same hands serve.
- **Every act has a receipt and a record.** A feature that changes a player's game needs exactly that record.
- **A new hand is a plain C# method with a thin tool wrapper**, so that a mod can call the act in process, with no
  socket. This costs one rule for new hands and nothing for tests today: weak value now, strong value later, so it is
  in (his rule of 2026-11-23).

What is **not** decided: the companion is development tooling and no player has it. Which hands would ship inside a
mod is a question for Inhabited's own design, after the four current mods
(`RIMMANDRAKE_ADMIT_INHABITED_TO_PIPELINE_AFTER_FOUR_MODS_NEVER_SEEN_IT`).

## Deliberately not designed yet

| thing | why not now | what opens it |
|---|---|---|
| a scene language (YAML or other) | dead, by his word and the pick | nothing |
| the plan interpreter in the game (`RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`) | held | experiment A, scene 3: only when an act from Python gives a different state than the act in the game |
| a bounded rule in a run ("when this, do that, at most N times") | no scene of ours names the shape | the first scene with many reactions, after the benchmark of `08` |
| the sweep runner | a Python loop over a script may be enough | the first sweep that the loop cannot do |
| names 8 and 9 beyond their pages (`s.shot`, `scene.attach`), and the verbs no converted scene uses | built when one of the three scenes, or the next, needs it | the conversion ticket |
| conversion of the 436 live scripts | a script converts when its mod next advances | each mod's own advance |
| deletion of any tool | the call journal is not counted | the 30-day count |
| which hands ship to players for Inhabited | not this design's question | Inhabited's design |
| window content as data, the flight filmstrip | unchanged from pass two | their tickets |

## What this replaces

- `02_needs_design.md` §11 (the scene file) and the scene-file and run-plan parts of `05_build_design.md` are replaced
  by this file. `05` is corrected in place: its top says which parts stand.
- `09_entry_points.md` keeps its survey and counts. Where it and a contract page differ (the page's home, the stamp
  rule of `s.raw`, promotion after two scenes), the contract page is right.
- The parts of `05` that stand: the trace and the judge outside the game, the evidence contract, the taps and their
  certificate, the station fence, reset hooks and trace points in mods, the verdict ledger, who chooses a plant.

## What GPT changed (round 2, `census_sources/gpt_pass3_round2_answer.md`)

All 14 findings were taken. The five it called blockers: a restart did not clean a tuned world (the mark now lives in
saves and is inherited at load); a changing raw call marked only its session (now the process); a fake bridge cannot
prove a promise about the game (each such promise has a live proof with a second reading); a lost reply left no handle
(the request id is given before the call, and a repeat returns the first effect); an unreadable value in a stop
condition had no meaning (the run stops as `unknown`). Also: a group is frozen; accepted is not completed; the refusal
that waited on an experiment is out of version 0.1.0; promotion is of a typed operation, by review; three struggle
signs, not four.

## What I am not sure of

- Whether ten names help an agent is a hypothesis `[GUESS 75%]`. The conversion ticket is its test.
- `scene.open` may be too large for one name `[GUESS 35% that it is split]`.
- A hidden read by reflection can break on a field rename with no compile error. The guard is the state `error` with
  the list of fields; the cost is a rerun, not a wrong result `[GUESS 80%]`.
- The receipt adds text to every return. If agents stop reading it, the default print becomes the two lines `did` and
  `could_not_look`, and the rest stays in the file.
