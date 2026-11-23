# BRIDGE v2.0, pass 2: the build order

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_REBUILD_OR_IMPROVE_CODE_READ`. Written 2026-11-23.
The design is `05_build_design.md`. **None of these tickets is filed.** The list is for the Conductor.

## How to read a ticket

- Each ticket is one run of one builder.
- **Offline test**: a selftest file that does not exist today, so its command is red today (the runner reports the
  missing file as a failure). The count is the number of checks that the file must print as passed. Each offline test
  also carries its planted faults: the builder shows the test red on each plant before the fix is called done.
- **Live test**: a `prove_*.py` script run under `python.exe` on a test game (ArchSmall by default) by whoever holds
  that game. A live test that did not run is recorded UNRUN with its command, never as passed.
- Every new Harmony patch site joins `src/RimMandrake/bridgetools/HOOKS.md` in the same ticket
  (`selftest_bridge_hooks.py` is red otherwise).
- Every new file of pipeline machinery gets its promises on `design/specs/2026-11-23-bridge-v2/boundary.md` first
  (the repo's rule: a boundary page before pipeline code). The first ticket creates that page.
- All paths below are relative to the repo root. `SELF` means `python3 src/RimMandrake/Utils/run_selftests.py --only`.

## The work already running

`RIMMANDRAKE_BUILD_BRIDGE_RECEIPT_CALM_AND_TAP_EITHER_WAY` builds three tools on the present bridge now. This design
**keeps all three and builds on them**; none is replaced.

| the sibling's tool | what it becomes in the kernel | what the kernel needs from it |
|---|---|---|
| loaded-build receipt | the `loaded` block of every scene receipt, and the check of the admit phase | the hash of each assembly **as loaded**, the active mod list in order, the DLC, the game version, as one internal C# function that a tool and the kernel both call |
| one-call calm map | version 0 of the calm profile, called by the calm phase | one internal function that returns a status per control (HELD, WATCHED, COULD NOT ARM), and a matching restore |
| first-exception tap | the `error` tap of the trace, and the "stop now" signal for an exception storm | each record goes through the present disk writer with the tick and the phase; the tap also subscribes to Unity's `Application.logMessageReceivedThreaded` (read in this pass: the game's own log listens there) |

If the sibling built any of the three as a tool body only, the second ticket below lifts that body into an internal
function. That is a move of code, not a redesign.

## The tickets, in dependency order

### `RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE`
- **Builds:** `design/specs/2026-11-23-bridge-v2/boundary.md` (the trace schema, the receipt schema, the judge's
  promises). `src/RimMandrake/rimflow/scene_judge.py`: plan + trace + receipt facts -> one of the seven outcomes, the
  classifier row, the first failed condition with its observed values. Flag `--rejudge <run folder>`. The Python
  condition evaluator gains `count`, `seq`, `before`, `after` over tap records. One exit code per outcome.
- **Needs:** nothing. No game.
- **Offline test:** `SELF src/RimMandrake/rimflow/selftest_scene_judge.py`, 27 checks: one hand-made trace for each
  of the nine classifier rows of `02_needs_design.md` §7 (9); the four "could not look" shapes kept apart: a tap not
  armed, records dropped in the needed span, an empty trace, a trace that ends before the end mark (4); a success
  that was already true before the act is refused (1); a success with no exposure is refused (1); a "mod says" record
  alone decides nothing (1); a mod bug that walks its own actor into a hazard is UNRESOLVED, not ENVIRONMENT FAULT (1);
  a giver's refusal is MOD FAILURE, not APPARATUS FAULT (1); `--rejudge` gives a byte-identical receipt for an
  unchanged plan (1); each exit code (7); an unknown key in a plan is refused by name (1).
- **Planted faults that must turn it red:** swap classifier rows 4 and 5; treat a dropped span as an empty span; let
  an empty trace read as "no forbidden effect".
- **Why first:** it fixes the two schemas that every later ticket writes to; it needs no game, so it can be built
  while every game is busy; and it is the part that lets a repaired check judge a kept trace again.

### `RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED`
- **Builds:** in `JawaBenchVitals.cs` `TickPost`, an optional per-run evaluator: `CondRun.Step` after every tick,
  tracks written on change through `JawaBenchTpsWriter.Enqueue` as kind `scene`, an exact stop (the inner loops of
  `jawa/run_scenes` and `jawa/safe_advance` break after the tick that hit; in PLAY mode `CurTimeSpeed = Paused` is set
  in the postfix). Alias roots for `thing.field`. Closes the intent of `ADVANCEUNTIL_WIRE_PER_TICK_STOP`, which the
  Conductor then drops as superseded by this ticket.
- **Needs:** `RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE`'s trace schema.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_scene_tick_wiring.py`, 12 checks on a .NET harness
  that compiles the pure files (the pattern of `SceneRunnerSelfTest`): a hit on tick T stops with `executed == T`; a
  condition true at arm gives `executed == 0`; a safety stop and a hit on one tick report both; a track writes one row
  per change and none when nothing changed; a probe that goes `gone` writes `gone`, never 0; an unknown under
  `on_unknown: stop` ends the run as unknown; the budget stop names the costliest node; an epoch change ends the run;
  two runs cannot be armed at once; a skipped original (`__runOriginal` false) records nothing; a dropped row is
  counted; the source check of `selftest_bridge_hooks.py` still passes.
- **Live test (UNRUN until a game is held):** `python.exe src\RimMandrake\bridgetools\prove_scene_tick_wiring.py`,
  5 rows: `until(game.tick >= T0+137)` gives `hitTick == T0+137` in STEP; the same in PLAY, with the game paused on
  that tick; a 1-tick event (a thing spawned and destroyed inside one tick by the script) is in the trace by its taps;
  a private field path reads the same value as `jawa/pawn_get`; steady-state allocation is 0 (`jawa/alloc_probe`).
- **Why second:** `CondRun` is built and unit-tested and has never run in a tick. This is the smallest change that
  removes the gap between calls, which is the cause behind census ranks 2, 5 and 9.

### `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`
- **Builds:** `JawaBenchSceneKernelCore.cs` (pure: the plan parser, phase order, the closed list of act ops, the
  settle reconciliation rules) and `JawaBenchSceneKernel.cs` (the tool `jawa/run_plan`, `jawa/run_status`; TEST profile
  only). Phases admit, stage, arm, act and run, settle, leave, on the present plot grid. Staging ops call the bodies of
  `jawa/build_batch`, `jawa/set_terrain_batch`, `jawa/spawn_pawn`, `jawa/destroy_batch`. Aliases. The receipt facts.
  `src/RimMandrake/Utils/scene.py run <plan.json>` drives it and calls the judge. First scene as data: Explosive
  Knockback's spared carrier (worked example 1 of `02_needs_design.md`).
- **Needs:** `RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE`, `RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED`; the sibling's receipt function.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_scene_kernel_core.py`, 16 checks: each phase's
  refusal by name (6); an act step that cannot be delivered ends as an apparatus fact, not a verdict (1); a plan whose
  build hash differs from the loaded one is refused in admit before staging (1); an alias bound twice is refused (1);
  the settle reconciliation flags a cast thing that vanished with no event (1) and passes a clean run (1); a run over
  the tick threshold returns a handle and a later status (2); unknown plan keys are refused (1); the game is left
  paused in every ending, including a thrown tick (1); the release build is enough: no type of a PROOF build is named
  by the kernel (1).
- **Live test (UNRUN until a game is held):** `python.exe src\RimMandrake\bridgetools\prove_run_plan_spared_carrier.py`,
  4 rows: the data scene gives SUCCESS on the release build; the same plan under the mutant "the carried pawn is not
  spared" (a build flag in this first ticket, an overlay entry after `RIMMANDRAKE_BUILD_MUTANTS_BY_OVERLAY_AUTHOR_DOES_NOT_CHOOSE`) gives MOD FAILURE on the named
  condition; the existing `[RMTest]` pair gives the same two results on the same save; the whole run is one bridge
  call plus one status read.
- **Why third:** it is the first scene that runs end to end as data on the shipped DLL, and its comparison with the
  existing C# scene shows whether the kernel sees what the old judge saw.

**The first three pay first because** together they turn "a script of hundreds of calls with a judge in the mod's
PROOF build" into "one call, a trace on disk, a verdict from a program that can be run again", and they do it with
about one new C# file, on code that already exists and is already unit-tested. Nothing after them is useful without
them, and each of them is useful alone: the judge to re-judge, the wiring to every present proof that waits on a
condition, the plan to every new scene.

### `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED`
- **Builds:** the PLAY mode's exact stop in the kernel (if `RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED` left any part), and the measurement that the
  2026-11-06 tick burst design asked for and never got: one plan run in PLAY and in STEP from one save (both
  reloaded), 5 times each, traces compared tick by tick; ticks per second of each mode on the 13-mod list and, riding
  a load that is already scheduled, on the full list. Fixes the path fault of `tickburst_bench.py` or replaces that
  tool by `scene.py compare`. The receipt field `mode` and the ledger rule "STEP, not compared, counts for no bar".
- **Needs:** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`.
- **Offline test:** `SELF src/RimMandrake/Utils/selftest_scene_compare.py`, 6 checks: two equal traces compare
  equal; a difference in a track names the tick and the value; a difference only in wall time is not a difference; a
  missing tick range is "could not compare", not "equal"; a replay is never counted as a sample; the comparison
  refuses two runs that did not start from one save.
- **Live test (UNRUN):** `python.exe src\RimMandrake\Utils\scene.py compare --plan <spared carrier> --modes play,step --n 5`,
  expected: a table of 10 runs and one line, "no divergence observed in 5 pairs" or the first diverging tick.
- **This is the first of pass one's six first-week measurements.** Its result decides whether STEP may be used for
  acceptance at all, and whether BURST is ever built.

### `RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS`
- **Builds:** the stage map and the green room for a test game: make (a pocket map first; a second settlement map as
  the fallback), keep as a fixture save per mod list, the station allocator with margins, clean with read-back, retire
  on a failed clean. Measures the cost of making the stage and of a clean and build of a 400-cell station.
- **Needs:** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_stage_stations.py`, 10 checks (pure allocator): no
  two stations overlap, margins included; a request that cannot fit says why; a retired station is never given again;
  a station near the edge is refused when the plan asks for distance from the edge; the same plan built twice gives
  equal read-back digests (on a recorded read-back); 5 more on the clean list (things, filth, fire, designations,
  reservations each named when left behind).
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_stage_map.py`, 6 rows: the stage holds zero
  pawns after make; the green room's colonists are alive and fed after 60,000 ticks of an idle stage; a scene run after
  a deliberately dirty scene (corpses, a reservation, a fire) gives the result of a fresh stage; the outdoor
  temperature of the stage does not move in 60,000 ticks; the make and the clean-and-build times are printed; a raid
  incident aimed at a stage with no free colonist is reported "called, not fired".

### `RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER`
- **Builds:** capability asserts in the stage phase (can do a work type, has a ranged attack, can reach, is hostile,
  is awake); the act op "order through the giver" on the body of `jawa/ordered_job` with the giver's refusal returned
  as a fact; the act op "motive" (a lord and duty, from the `jawa/lord_*` bodies); the force level per actor in the
  deviation record. Second scene as data: FlowWorks' ordered rescue.
- **Needs:** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`, `RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS`.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_scene_force.py`, 9 checks: each of the eight force
  levels is written on the receipt as declared (8, on a fake game); a plan whose entry line steps past its own claim is
  refused by the lint (1).
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_ordered_rescue.py`, 4 rows: the rescue
  completes (SUCCESS); a rescuer whose work type is disabled fails its assert before a tick is spent (an apparatus
  fact); a giver made to refuse by the mutant gives MOD FAILURE; a hostile with no lord is refused at stage with the
  reason.

### `RIMMANDRAKE_BUILD_CANARY_RITE_PROVES_TAPS_NOT_BLIND`
- **Builds:** the new taps of `05_build_design.md` decision 4 (job start and end, reservation refused, mental state
  attempt, quest offered, letter, message, fire and explosion with instigator); the canary rite at arm; the list of
  foreign prefixes per tap; the per-tick cast tracks (toil, position, health summary, mental state, holder).
- **Needs:** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_scene_taps.py`, 14 checks on the pure recorder: each
  of the seven new taps keeps the six hook rules of `HOOKS.md` (7); a canary record that is missing gives COULD NOT ARM
  for that tap only (1); a tap with a foreign prefix is armed with the note (1); a blind tap (the hook removed in the
  harness) is caught by the canary (1); a record outside any run is dropped and counted (1); the settle reconciliation
  catches a death with no kill record (1); two job starts in one tick keep their order (1); `selftest_bridge_hooks.py`
  passes with the new sites on the table (1).
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_canary_rite.py`, 4 rows: every tap holds the
  canary's record on the 13-mod list; the same on the full list, with each foreign prefix named; the rite's time is
  printed; one tap unpatched by hand is reported COULD NOT ARM and the run does not start.

### `RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE`
- **Builds:** on the sibling's calm tool: named, versioned profiles; HELD only after a planted breach was seen
  stopped on this mod list, else ARMED UNPROVEN; the breach log (every held attempt and watched event, in the trace);
  the incident allow list at `IncidentWorker.TryExecute`; the quest gate at `QuestManager.Add`; the mental state gate;
  the queued incidents saved aside and given back with their fire ticks moved by the time held; re-arm after a load;
  the lease and the debt file; refusal of destructive controls in the CAMPAIGN profile.
- **Needs:** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`; the sibling's calm tool.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_calm_profile.py`, 12 checks on the pure store: a
  control reads HELD only after its planted breach (1); the allow list lets one named incident through once (1); a
  held queue gives back each entry with its fire tick moved (1); restore in reverse order with read-back (1); a debt
  written before the first write and repaid by a later start (2); a lease that ran out restores (1); a restore that
  could not put a value back says which (1); a destructive control in CAMPAIGN is refused by name (1); an attempt
  count and a "scheduling switched off" count are kept apart (1); a second driver's call is a breach of class
  APPARATUS (1); unknown profile keys are refused (1).
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_calm_profile.py`, 5 rows: a planted incident,
  a planted wild animal at the stage edge and a planted weather change each give one breach record that names them (3);
  a load in the middle changes no status (1); a killed driver leaves no control on after the lease (1).

### `RIMMANDRAKE_BUILD_SCENE_VERDICT_LEDGER_RECEIPT_IS_NOT_VERDICT`
- **Builds:** `src/RimMandrake/rimflow/scene_verdicts.py` and the file `scene_runs.jsonl` in a mod's version folder:
  the rules of kinds A, B and C over the runs of one claim on one build; a pass held by an UNRESOLVED run; a kind B
  budget and INCONCLUSIVE; a reclassification added, never overwritten; the hunt notice to the Conductor; a stamped
  run, an uncompared STEP run and a PROOF build run count for no bar. The Stage 6 exit reads it.
- **Needs:** `RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE`'s receipt schema. No game.
- **Offline test:** `SELF src/RimMandrake/rimflow/selftest_scene_verdicts.py`, 15 checks: kind A decides on one
  valid run (2: pass, fail); kind B passes on one SUCCESS only with no MOD FAILURE and no UNRESOLVED (3); a budget
  spent gives INCONCLUSIVE (1); X of Y for a result random by design (1); one UNRESOLVED holds the pass until classed
  (1); a reclassification keeps the history (1); a replay is not a sample (1); a cluster counts as one cluster (1); a
  run with an overlay stamp reads TUNED and counts for nothing (1); a STEP run with no comparison counts for nothing
  (1); a change that does not touch what the scene reads keeps the verdict (1); a serious single UNRESOLVED opens a
  hunt notice with the four parts the policy names (1); the four answers zero, none, could not look and failed are
  kept apart in the summary (1).

### `RIMMANDRAKE_BUILD_SCENE_FILE_COMPILER_AND_LINT_NO_GAME`
- **Builds:** `src/RimMandrake/Utils/scene_compile.py`: the scene file of `02_needs_design.md` §11 -> a run plan;
  defaults expanded and printed; the hash of the expanded contract; lint against the frozen def dump
  (`observed/inventory/DefDump_OFFICIAL/`); fixtures by name. The three worked examples as real files in their mods.
- **Needs:** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`'s plan format.
- **Offline test:** `SELF src/RimMandrake/Utils/selftest_scene_compile.py`, 13 checks: the three worked examples
  compile (3); a misspelt def is refused by name (1); a path whose first step is not an alias is refused (1); a
  success on "mod says" alone is refused (1); a success already true before the act is refused (1); a kind B scene
  with no budget is refused (1); a kind A scene with an allowed miss is refused (1); a "throughout" condition that the
  success must break is refused (1); a condition on a tap that the plan does not arm is refused (1); the expanded
  contract's hash changes when a default changes (1); the same file compiles to the same bytes twice (1).

### `RIMMANDRAKE_BUILD_DEVIATION_STORE_SETTINGS_FIELD_JOINS_FIRST`
- **Builds:** the deviation store of `05_build_design.md` (calm, force, overlay, time and rate: one record, one
  restore, one stamp); `jawa/mod_settings_field set` writes only through it; the `WriteSettings` block while a
  settings entry is live; the journal written before the first poke; the taint mark; the on-screen line
  `OVERLAY <name> <hash>`; the plan's `overlay:` block. This is step 1 of `04_live_tuning.md`.
- **Needs:** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`, `RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE` (the debt file).
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_deviation_store.py`, 12 checks: apply in order and
  stop at the first failure with the earlier entries reverted (1); a failed revert marks the game SPOILED (1); the
  taint mark stays after a revert (1); `overlay: none` with the taint set is not clean (1); a receipt lists every live
  entry of all four kinds (1); a `const` and a `static readonly` target are refused by name (2); CAMPAIGN refuses an
  overlay entry (1); a second holder cannot apply (1); the journal exists before the first write (1); a settings write
  to disk is blocked while an entry is live (1); a value changed by another hand is listed as differing from its
  default (1).
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_overlay_settings.py`: experiments E1 and E2
  of `04_live_tuning.md` (the FlowWorks fall multiplier doubles the injury and returns; the config file's hash never
  changes; the time for one point of the Knockback sweep is printed).

### `RIMMANDRAKE_BUILD_MUTANTS_BY_OVERLAY_AUTHOR_DOES_NOT_CHOOSE`
- **Builds:** `mutants.json` per mod with its lint; the seeded draw; `scene.py both-ways <scene>`: the green run,
  the drawn mutant's red run under its overlay, the revert, both receipts recorded in the scene's history; the live
  switch of one of our Harmony patches (off and on, with a call counter that proves it).
- **Needs:** `RIMMANDRAKE_BUILD_SCENE_VERDICT_LEDGER_RECEIPT_IS_NOT_VERDICT`, `RIMMANDRAKE_BUILD_SCENE_FILE_COMPILER_AND_LINT_NO_GAME`, `RIMMANDRAKE_BUILD_DEVIATION_STORE_SETTINGS_FIELD_JOINS_FIRST`.
- **Offline test:** `SELF src/RimMandrake/Utils/selftest_scene_mutants.py`, 9 checks: a mutant that only switches
  the feature off is refused (1); a mutant must name a bar (1); the draw is the same for the same scene and build and
  cannot be set by the scene file (2); the red run's receipt can never count as a pass (1); a red run that ends
  SUCCESS marks the scene "cannot fail" (1); a red run that fails on another condition than the mutant names is
  reported as such (1); the green run is always first (1); a mutant that needs a build is listed as "needs build" and
  not run live (1).

### `RIMMANDRAKE_BUILD_STAMP_AGAIN_REPEATS_WITH_RESET_DIGEST`
- **Builds:** repeats of one plan on fresh stamps; N copies side by side as one cluster; the reset digest of the
  station and of each mod's `RMDigest` hook, compared with the first stamp; the periodic fresh-process comparison;
  launches, valid opportunities and exposures counted apart.
- **Needs:** `RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS`, `RIMMANDRAKE_BUILD_SCENE_VERDICT_LEDGER_RECEIPT_IS_NOT_VERDICT`; `RIMMANDRAKE_BUILD_MOD_TRACE_AND_RESET_HOOKS_BY_REFLECTION` for the mod digests.
- **Offline test:** `SELF src/RimMandrake/Utils/selftest_scene_repeats.py`, 8 checks.
- **Live test (UNRUN):** 20 stamped copies of the chosen-rescue scene finish in less wall time than 3 single runs
  take today; a planted cross-talk between two copies is a breach.

### `RIMMANDRAKE_BUILD_FLIGHT_PROBES_STATE_AND_FRAME_NO_PICTURES`
- **Builds:** the probes `pawn.flight.*` and `pawn.anim.*` (the graphic state's name and `texPath` from
  `PawnRenderNode.TryGetAnimationGraphicState`), the offline audit that every frame's texture exists for every
  facing, the flapping scene of worked example 3 as a file. Takes over the build half of
  `FLYERFRAMES_PROVE_JOINT_SESSION`.
- **Needs:** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`, `RIMMANDRAKE_BUILD_SCENE_FILE_COMPILER_AND_LINT_NO_GAME`.
- **Offline test:** `SELF src/RimMandrake/Utils/selftest_flight_frames.py`, 8 checks on recorded and hand-made
  series: a full flight sequence passes; a skipped state fails; a flip-book that repeats one frame fails; a frame held
  for the wrong number of ticks fails; a landing that keeps a flying picture fails; a bird still in the air at the
  limit is not judged; no bird took off is an allowed miss; the asset audit names a missing texture.
- **Live test:** **the owner's act.** The first live run is with him present (the standing rule). See
  `07_for_the_owner.md`, choice 1.

### `RIMMANDRAKE_BUILD_MOD_TRACE_AND_RESET_HOOKS_BY_REFLECTION`
- **Builds:** `src/RimMandrake/_Shared/TestHooks/RMTestHooks.cs` (`RMTrace`, `RMResetAttribute`, `RMDigestAttribute`,
  `RMProbeAttribute`); the kernel's discovery; the "mod says" record type; first use in Explosive Knockback and
  FlowWorks when each next advances.
- **Needs:** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_test_hooks.py`, 7 checks: a mod with no hook is
  listed as such; a hook of the wrong shape is a named problem, never skipped in silence; `Emit` with a null sink
  allocates nothing; the sink is cleared at leave, also after a thrown tick; two mods' hooks do not collide; a probe
  plug-in from a PROOF build is refused for an acceptance run; the release DLL of a mod with hooks names no type of
  the companion.

### `RIMMANDRAKE_BUILD_DEF_FIELD_OVERLAY_WITH_WRITE_RECIPES`
Step 2 of `04_live_tuning.md`: def-field writes through the store, the first recipes from that file's table, the
UNVERIFIED state, the fingerprint before and after. **Needs** `RIMMANDRAKE_BUILD_DEVIATION_STORE_SETTINGS_FIELD_JOINS_FIRST`. **Offline test:**
`SELF src/RimMandrake/bridgetools/selftest_overlay_recipes.py`, 10 checks. **Live test (UNRUN):** experiments E3, E4,
E5 and E7 of `04_live_tuning.md`.

### `RIMMANDRAKE_BUILD_SWEEP_RUNNER_ON_RUN_PLAN_LIST`
Steps 3 and 4 of `04_live_tuning.md`: `scene.py sweep` (a list of plans that differ in their overlay; the repeated
baseline; the shuffled order; the "cannot rank" answer), export, and the absorbed check. **Needs** `RIMMANDRAKE_BUILD_STAMP_AGAIN_REPEATS_WITH_RESET_DIGEST`, `RIMMANDRAKE_BUILD_DEF_FIELD_OVERLAY_WITH_WRITE_RECIPES`.
**Offline test:** `SELF src/RimMandrake/Utils/selftest_scene_sweep.py`, 9 checks.

### `RIMMANDRAKE_BUILD_KEEPER_SAVE_RAND_STATE_DIVERGENCE_FINDER`
For scenes in a hunt: a save and the random state at arm, the replay procedure (both runs reloaded), the trajectory
fingerprint, "diverged at tick T, first difference". It measures the replay rate. **Needs** `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED`. **Offline test:**
`SELF src/RimMandrake/Utils/selftest_scene_replay.py`, 7 checks. **Built when the first hunt needs it.**

### `RIMMANDRAKE_BUILD_LOAD_CROSSING_ACT_REBINDS_ALIASES`
The act op "save and load in the middle": settle after the load, bind each alias by its saved id (read in this pass:
ids are saved), re-arm the store and the probes, continue the timeline. **Needs** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`, `RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE`. **Offline test:**
`SELF src/RimMandrake/bridgetools/selftest_scene_load_crossing.py`, 6 checks.

### `RIMMANDRAKE_BUILD_GAME_WATCHER_NAMES_THE_BROKEN_STATE`
The watcher outside the game on the heartbeat that the disk writer already gives: ticking, paused, frames stopped,
an exception on every frame, stuck in a load, at the menu, no map, process gone; a run never starts on a game whose
last state was broken; a test game is stopped, ArchBig is reported (see `07_for_the_owner.md`, choice 2). It builds
on `crash_watch.sh`, the stall dump and `game_health_check.py`. **Needs** nothing new. **Offline test:**
`SELF src/RimMandrake/Utils/selftest_game_watcher.py`, 9 checks (one per state, and the "never start on a broken
game" rule).

### `RIMMANDRAKE_BUILD_WINDOW_ADAPTERS_TRADE_AND_SETTINGS_FIRST`
Window content as data for named windows: the trade window and a Mod Settings page, on the present trade probe and
settings smoke window. The general transcript is a later ticket and is filed only if an adapter cannot serve a need.
**Needs** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`. **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_window_adapters.py`, 6 checks.

### `RIMMANDRAKE_BUILD_FLIGHT_FILMSTRIP_FOR_HIS_EYE_ONLY`
**Only on the owner's yes** (`07_for_the_owner.md`, choice 1). One image that tiles N consecutive ticks of a flight,
made by the off-screen capture that exists, after `RIMMANDRAKE_BUILD_FLIGHT_PROBES_STATE_AND_FRAME_NO_PICTURES` passes; never a pass condition; first proven on a vanilla
bird. **Needs** `RIMMANDRAKE_BUILD_FLIGHT_PROBES_STATE_AND_FRAME_NO_PICTURES`.

## The order at a glance

Each arrow reads "is needed by". Names are shortened here to their subject words; the full names are the headings above.

```
now, on the present bridge:  the sibling run (receipt, calm, first exception)

SCENE_JUDGE ──┬─ COND_RUN_INTO_TICK ── RUN_PLAN ──┬─ PLAY_AGAINST_PAUSED_STEP (measure)
              │                                   ├─ STAGE_MAP ── CAST_ASSERTS_AND_ORDER ── STAMP_AGAIN_REPEATS
              └─ SCENE_VERDICT_LEDGER             ├─ CANARY_RITE (taps)
                                                  ├─ CALM_PROFILE ── DEVIATION_STORE ── MUTANTS_BY_OVERLAY
                                                  │                        └─ DEF_FIELD_OVERLAY ── SWEEP_RUNNER
                                                  ├─ SCENE_FILE_COMPILER ── FLIGHT_PROBES ── (FLIGHT_FILMSTRIP, his yes)
                                                  ├─ MOD_TRACE_AND_RESET_HOOKS
                                                  └─ LOAD_CROSSING_ACT, WINDOW_ADAPTERS
any time: GAME_WATCHER            when a hunt needs it: KEEPER_SAVE ... DIVERGENCE_FINDER
```

## Old items that this order absorbs

For the Conductor to drop as superseded, each with this file as the reason, once the absorbing ticket is filed:

| old item | absorbed by |
|---|---|
| `ADVANCEUNTIL_WIRE_PER_TICK_STOP` (bridge conditions, per-tick stop) | `RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED` |
| `CONDWATCH_BUILD_OWNED_RINGS` (watchers outside an advance) | `RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED`, `RIMMANDRAKE_BUILD_CANARY_RITE_PROVES_TAPS_NOT_BLIND`: tracks and taps of a run |
| `RINGPROBES_WIRE_EVENT_CURSORS` (conditions over event rings) | `RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE`, `RIMMANDRAKE_BUILD_CANARY_RITE_PROVES_TAPS_NOT_BLIND`: the judge counts tap records |
| `TICKBURST_PROVE_MANY_TICKS_ONE_FRAME` (many ticks per frame, with its comparison) | `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED` |
| `FLYERFRAMES_PROVE_JOINT_SESSION` (flight as state) | `RIMMANDRAKE_BUILD_FLIGHT_PROBES_STATE_AND_FRAME_NO_PICTURES` for the build; the joint session stays his |

## What is measured first

Pass one listed six things to measure in the first week. Their homes: ticks per second by mode, and whether the
camera rate changes results: `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED`. The cost of the calm profile and of a reassert: `RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE`'s live test. The cost
of clean and build, and of the stage map: `RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS`'s live test. The overhead of the taps: `RIMMANDRAKE_BUILD_CANARY_RITE_PROVES_TAPS_NOT_BLIND`'s live test. The
replay rate: `RIMMANDRAKE_BUILD_KEEPER_SAVE_RAND_STATE_DIVERGENCE_FINDER`.
