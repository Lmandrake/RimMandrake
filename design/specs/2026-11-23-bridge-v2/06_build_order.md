# BRIDGE v2.0, pass 2: the build order

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_REBUILD_OR_IMPROVE_CODE_READ`. Written 2026-11-23, repaired after two GPT review rounds.
The design is `05_build_design.md`. All the tickets are filed (2026-11-23, by
`RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`), each with its test, except `RIMMANDRAKE_BUILD_FLIGHT_FILMSTRIP_FOR_HIS_EYE_ONLY`,
which waits for the owner's choice 1b (`07_for_the_owner.md`).

## How to read a ticket

- Each ticket is one run of one builder. A ticket's name is its identity; the order of the headings is the build order.
- **Offline test**: a selftest file that does not exist today. Its command is red today: `run_selftests.py --only` on a
  missing file exits 1 `[MEASURED 2026-11-23, on selftest_scene_judge.py]`. The count is the number of checks the file
  must print as passed. `SELF` below means `python3 src/RimMandrake/Utils/run_selftests.py --only`.
- **Wrong code that must go red**: planted faults. The builder shows the test red on each plant before the ticket
  closes. A check count alone is not an oracle (GPT's objection, taken); the plants are.
- **An offline test proves rules, never hooks.** A recorder harness can pass while the real Harmony hook is not
  connected. For every tap and gate the oracle is live: the tap certificate
  (`RIMMANDRAKE_BUILD_TAP_CERTIFICATE_CANARY_RUNS_OFF_STAGE`).
- **Live test**: a `prove_*.py` script under `python.exe` on a test game (ArchSmall by default), run by whoever holds
  that game. A live test that did not run is recorded UNRUN with its command, never as passed.
- Every new Harmony patch site joins `src/RimMandrake/bridgetools/HOOKS.md` in its ticket (`selftest_bridge_hooks.py`
  is red otherwise). Every new file of pipeline machinery has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
- All paths are relative to the repo root.

## The work already running

`RIMMANDRAKE_BUILD_BRIDGE_RECEIPT_CALM_AND_TAP_EITHER_WAY` builds three tools on the present bridge now. This design
**keeps all three and builds on them**; none is replaced.

| the sibling's tool | what it becomes in the kernel | what the kernel needs from it |
|---|---|---|
| loaded-build receipt | the `loaded` block of every scene receipt, and the check of the admit phase | the hash of each assembly **as loaded**, the active mod list in order, the DLC and the game version, as one internal C# function that a tool and the kernel both call |
| one-call calm map | version 0 of the calm profile, called by the calm phase | one internal function that returns a status per control, and a matching put-back |
| first-exception tap | the `error` tap of the trace, and the "stop now" signal for an exception storm | each record goes through the present disk writer with the tick and the phase; the tap also listens to Unity's `Application.logMessageReceivedThreaded` (the game's own log listens there; read in this pass) |

If the sibling built any of the three as a tool body only, the run-plan ticket lifts that body into an internal
function. That is a move of code, not a redesign.

## The first three that pay, and why

1. **`RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED`**: the slice. One hand-written scene in the game's own
   loop: one probe, one act, the condition evaluator stepped in the tick, a trace on disk that meets the evidence
   contract, an exact stop.
2. **`RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE`**: the judge, on the slice's real traces and on
   hand-made ones.
3. **`RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`**: the first scene as data on the release DLL.

Two small guard tickets are built between the second and the third, because the run plan is the first thing that
changes a map on its own: `RIMMANDRAKE_BUILD_GAME_WATCHER_NAMES_THE_BROKEN_STATE` and
`RIMMANDRAKE_HARDEN_RUN_LIFE_CYCLE_KILL_CANCEL_THROWN_TICK`.

**Why these.** The condition evaluator's run object is built and unit-tested and has never run in a tick; wiring it is
the smallest change that removes the gap between calls (census ranks 2, 5 and 9). The slice is also the measurement
that confirms or refutes the pick "join, do not rebuild": if the parts cannot share one life cycle, that shows here,
before the interpreter is written. The judge makes a kept trace judgeable again and needs no game. The run plan turns
the two into a scene that a mod builder can write. **That they pay first is a GUESS (70%) until the slice is run**; my
first draft stated it as a fact, and GPT was right that nothing had shown it.

**Bootstrap mode.** Until the tap certificate exists, every run of `jawa/run_plan` is marked BOOTSTRAP on its receipt,
and the verdict ledger counts it for no bar. The first scenes are built and compared in that mode.

## The tickets, in build order

### `RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED`
- **Builds:** `design/specs/2026-11-23-bridge-v2/boundary.md` (the trace schema and the evidence contract of
  `05_build_design.md`). In `JawaBenchVitals.cs` `TickPost`, an optional per-run evaluator for **PLAY only**: the fixed
  order (sample, conditions, end test, act steps), `CondRun.Step` after every tick, tracks written on change through
  `JawaBenchTpsWriter.Enqueue` as kind `scene`, the first and last samples, sequence numbers and phases, the random
  state compared round the sample phase, the closing record after the writer drained, the pause in the postfix read
  back. One hand-written scene: one probe on one pawn, one act (a damage), one end condition. Closes the intent of
  `ADVANCEUNTIL_WIRE_PER_TICK_STOP`.
- **Needs:** nothing.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_scene_tick_wiring.py`, 11 checks on a .NET harness
  that compiles the pure files (the pattern of `SceneRunnerSelfTest`): a hit on tick T gives `executed == T`; true at
  arm gives `executed == 0`; a track writes one row per change and none without a change; a probe that goes `gone`
  writes `gone`, never 0; an unknown under `on_unknown: stop` ends the run as unknown; a skipped original records
  nothing; a dropped row is counted in the closing record; **inside one tick the sample record's sequence number is
  lower than the act record's**; an act step and the end cannot fall on one tick; the first and the last sample exist
  for every track; a random draw inside the sample phase is reported.
- **Wrong code that must go red:** sampling after the act steps (caught by the sequence check); a closing record
  written before the writer drained; a stop that lets one more tick run.
- **Live test (UNRUN until a game is held):** `python.exe src\RimMandrake\bridgetools\prove_scene_tick_wiring.py`,
  5 rows: `until(game.tick >= T0+137)` gives `hitTick == T0+137` at speed 1 and at Ultrafast, with the game paused on
  that tick and the tick count read after the frame ended; a private field path reads the same value as
  `jawa/pawn_get`; an actor damaged by the act step shows the new health in the trace before the run ends; the trace's
  closing record counts zero dropped rows; steady-state allocation is 0 (`jawa/alloc_probe`).

### `RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE`
- **Builds:** `src/RimMandrake/rimflow/scene_judge.py`: plan + trace + receipt facts -> one of the seven outcomes,
  the classifier row, the first failed condition with its observed values. It checks the evidence contract first and
  answers COULD NOT LOOK when a point fails. `--rejudge <run folder>` adds a line to the run's history and refuses, by
  naming the missing track or tap, a question that the trace cannot answer. The Python condition evaluator gains
  `count`, `seq`, `before`, `after` over tap records. One exit code per outcome.
- **Needs:** the trace schema of the ticket above. No game. Its fixtures are the slice's recorded traces and hand-made
  ones.
- **Offline test:** `SELF src/RimMandrake/rimflow/selftest_scene_judge.py`, 31 checks: one trace for each of the
  nine classifier rows of `02_needs_design.md` §7 (9); the evidence contract: no closing record, a dropped row in the
  needed span, a missing first sample, a missing last sample, a tap that a condition needs and the plan did not arm
  (5); a success already true at the first sample is refused at run time (1); a success with no exposure is refused
  (1); a "mod says" record alone decides nothing (1); a mod bug that walks its own actor into a hazard is UNRESOLVED,
  not ENVIRONMENT FAULT (1); a giver's refusal is MOD FAILURE, not APPARATUS FAULT (1); `--rejudge` with an unchanged
  checker gives the same outcome and adds one history line (1); `--rejudge` with a condition on an unrecorded value is
  refused by name (1); the first outcome is never overwritten (1); an alias whose object was replaced with no link
  record is COULD NOT LOOK (1); each exit code (7); an unknown key in a plan is refused by name (1).
- **Wrong code that must go red:** classifier rows 4 and 5 swapped; a dropped span read as an empty span; an empty
  trace read as "no forbidden effect"; a re-judgement that overwrites the first outcome.

### `RIMMANDRAKE_BUILD_GAME_WATCHER_NAMES_THE_BROKEN_STATE`
- **Builds:** the watcher outside the game, on the heartbeat that the disk writer already gives: ticking, paused,
  frames stopped, an exception on every frame, stuck in a load, at the menu, no map, process gone. A run never starts
  on a game whose last state was broken. A broken game is stopped at once, on any game, and the stop is reported. It
  builds on `crash_watch.sh`, the stall dump and `game_health_check.py`. It comes before the run plan, which is the first ticket that changes a map by itself.
- **Needs:** nothing.
- **Offline test:** `SELF src/RimMandrake/Utils/selftest_game_watcher.py`, 10 checks: one per state (8); "never
  start on a broken game" (1); "could not read the heartbeat" is its own answer, never "ticking" (1).
- **Wrong code that must go red:** a stale heartbeat file read as "paused"; an unreadable file read as "ticking".

### `RIMMANDRAKE_HARDEN_RUN_LIFE_CYCLE_KILL_CANCEL_THROWN_TICK`
- **Builds:** the run's life cycle under faults: the run lock (while a run is live, the gate on every tool refuses the
  changing families, by the run's id; reads are counted); one driver per run; a clean end on cancel, on a thrown tick,
  on a changed game or map, on a driver that died; the same per-tick evaluator in the two step loops
  (`jawa/run_scenes`, `jawa/safe_advance`) with their exact stop; the epoch check; the refusal to start when the
  player has no control.
- **Needs:** the slice.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_run_life_cycle.py`, 10 checks: a safety stop and a
  hit on one tick report both; the budget stop names the costliest node; an epoch change ends the run; two runs cannot
  be armed at once; a run that ends on a thrown tick still writes its closing record; a changing tool called during a
  run is refused with the run's id; a read tool called during a run is allowed and counted; a cancelled run leaves the
  game paused; a run refused for "no player control" changes nothing; the hook table check still passes.
- **Wrong code that must go red:** a run lock that covers `jawa/` tools of one family only; a cancel that leaves the
  evaluator armed.
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_run_life_cycle.py`, 4 rows: the driver
  killed in the middle leaves a closing record and a paused game; `jawa/spawn_pawn` from a second caller during a run
  is refused and is a breach on the receipt; the STEP loops stop on the exact tick; a thing spawned and destroyed
  inside one tick is in the trace by its taps.

### `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`

**Held on 2026-11-23, not built** (the last section of this file): it waits on experiment A.
- **Builds:** `JawaBenchSceneKernelCore.cs` (pure: the plan parser, the phase order, the closed list of act ops) and
  `JawaBenchSceneKernel.cs` (the tools `jawa/run_plan` and `jawa/run_status`, TEST profile only). The phases admit,
  arm, act and run, settle, leave on the present plot grid, with a small set of stage ops only (spawn a thing, spawn a
  pawn, set a cell's terrain, by the bodies of the present tools) and aliases. The receipt facts. The minimum put-back:
  the debt file written before the first change and repaid at the next start. `src/RimMandrake/Utils/scene.py run
  <plan.json>` drives it and calls the judge. First scene as data: Explosive Knockback's spared carrier (worked
  example 1 of `02_needs_design.md`).
- **Needs:** the slice, the judge, the game watcher and the life-cycle ticket; the sibling's receipt function. Runs in bootstrap mode.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_scene_kernel_core.py`, 17 checks: each phase's
  refusal by name (5); an act step that cannot be delivered is an apparatus fact, not a verdict (1); a plan whose
  build hash differs from the loaded one is refused in admit, before any change (1); an alias bound twice is refused
  (1); the settle reconciliation flags a cast thing that vanished with no event (1), flags an actor that is still
  there with a health that differs from the trace (1), and passes a clean run (1); a run over the tick threshold
  returns a handle and a later status (2); unknown plan keys are refused (1); the game is left paused in every ending
  (1); the kernel names no type of a PROOF build (1); a receipt made with no certificate reads BOOTSTRAP (1).
- **Wrong code that must go red:** admit that checks the build after staging; a settle that skips the health
  reconciliation; a leave that does not repay the debt file after a thrown tick.
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_run_plan_spared_carrier.py`, 4 rows: the data
  scene gives SUCCESS on the release build; the existing `[RMTest]` pair gives the same result on the same save; the
  whole run is one bridge call and one status read; a red run under a compiled mutant ("the carried pawn is not
  spared") gives MOD FAILURE on the named condition. That red run is on another build, so the scene's "shown both
  ways" record reads PROVISIONAL until the mutant ticket gives a red run on the release DLL.

### `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED`
- **Builds:** `scene.py compare`: one plan, from one fixture save loaded fresh for every run, with the random state
  recorded at arm and written back before each run (two loads of one save do not start with equal random state; read
  in this pass: the state is not in the save). Arms, in order of trust: PLAY speed 1 (the reference), PLAY speed 3,
  PLAY Ultrafast, STEP. Five runs each; traces compared tick by tick; ticks per second of each arm on the 13-mod list
  and, riding a load that is already scheduled, on the full list. The receipt field `mode`, and the rule "an arm that
  was not compared with the reference counts for no bar". A comparison holds for one key (plan hash, loaded hashes of
  the mods the scene touches, companion hash, mod list, arm) and is owed again when the key changes. Replaces the stuck measuring tool of
  `TICKBURST_PROVE_MANY_TICKS_ONE_FRAME`.
- **Needs:** the run-plan ticket.
- **Offline test:** `SELF src/RimMandrake/Utils/selftest_scene_compare.py`, 8 checks: two equal traces compare equal;
  a difference in a track names the tick and the value; a difference only in wall time is no difference; a missing
  tick range is "could not compare", not "equal"; a replay is never counted as a sample; two runs that did not start
  from one save are refused; a run whose random state was not written back is refused; a comparison under another key
  is not used.
- **Wrong code that must go red:** a comparison that ignores taps; "could not compare" reported as equal.
- **Live test (UNRUN):** `python.exe src\RimMandrake\Utils\scene.py compare --plan <spared carrier> --arms play1,play3,ultra,step --n 5`:
  a table of 20 runs and, for each arm, "no divergence observed in 5 runs" or the first diverging tick and value.
- This is the first of pass one's six first-week measurements. Its result decides which arms may be used for
  acceptance, and whether a faster driver is ever built.

### `RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO`
- **Builds:** the full stage phase: terrain, structures with stuff and health, things with counts, a pawn with exact
  kind, faction, health (each injury and part), gear, skills, traits, work types, needs, position, facing; every
  write read back from the game; fixtures by name; clean with read-back.
- **Needs:** the run-plan ticket.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_stage_ops.py`, 10 checks on the pure plan-to-ops
  layer: each op's refusal by name (6); a reply is built from the read-back, never from the request (1); a pawn whose
  kind was replaced by the game is a staging fault (1); two builds of one plan give equal digests on recorded
  read-backs (1); a clean that left a thing behind names it (1).
- **Wrong code that must go red:** a reply that echoes the request; a clean that reports success with a corpse left.
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_stage_ops.py`, 5 rows: a 400-cell station
  with 10 pawns is cleaned and built, and the time is printed; the same plan built twice gives equal read-back
  digests; a spawn that the game answered with another kind is reported; a scene run after a deliberately dirty scene
  (corpses, a reservation, a fire) gives the result of a fresh station; a station that cannot be cleaned is retired.

### `RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS`
- **Builds:** the green room and the stage for a test game; the three map kinds of `needs.map` (`settlement` the
  default, `pocket`, `colony`); the stage kept as a fixture save per mod list; the station allocator with margins and
  retirement; the spawners held for the stage map; the per-pawn holds for a `colony` map.
- **Needs:** the staging ops ticket.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_stage_stations.py`, 8 checks (pure allocator): no two
  stations overlap, margins included; a request that cannot fit says why; a retired station is never given again; a
  station near the edge is refused when the plan asks for distance from it; a `pocket` request by a scene that fires
  an incident is refused; a `colony` request is marked "shared map"; two more on the allocator's edge cases.
- **Wrong code that must go red:** margins left out of the overlap test; a `pocket` stage given to a raid scene.
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_stage_map.py`, 6 rows: the stage holds zero
  pawns after make; the green room's colonists are alive and fed after 60,000 ticks of an idle stage; a raid fired at a
  `settlement` stage with cast defenders spawns raiders at an edge with an assault duty; the same raid at a stage with
  no free colonist: the incident journal's outcome agrees with the raiders on the stage (the game fires it; measured
  2026-11-24); the make time of each map kind is printed; a wild animal that
  appears on the stage is a breach.

### `RIMMANDRAKE_BUILD_CAST_TRACKS_AND_JOB_TAPS_FIRST_FAMILY`
- **Builds:** the standard cast tracks (position, facing, job, toil, health summary, downed, dead, mental state,
  carried thing, holder, faction, drafted); the taps for job start and end (with who gave the job and the end
  condition) and for a reservation made and refused.
- **Needs:** the run-plan ticket.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_cast_tracks.py`, 9 checks on the pure recorder: the
  six hook rules of `HOOKS.md` for each of the two taps (2); two job starts in one tick keep their order (1); a record
  outside any run is dropped and counted (1); an alias whose object is replaced writes a link record (1); a track on a
  replaced job re-binds (1); the settle reconciliation catches a death with no kill record (1); the hook table check
  passes (1); the per-tick cost of the tracks is in the result (1).
- **Wrong code that must go red:** a job tap that records the new job only; an alias that silently moves to a corpse.

### `RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER`
- **Builds:** the capability asserts of the stage phase (can do a work type, has a ranged attack, can reach, is
  hostile, is awake); the act op "order through the giver" on the body of `jawa/ordered_job`, with the giver's
  refusal returned as a fact; the act op "motive" (a lord and a duty, from the `jawa/lord_*` bodies); the force level
  of each actor on the deviation record. Second scene as data: FlowWorks' ordered rescue.
- **Needs:** the stage map ticket; the cast tracks ticket.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_scene_force.py`, 6 checks: a plan whose entry line
  steps past its own claim is refused (1); each assert's refusal by name (5).
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_ordered_rescue.py`, 5 rows: the rescue
  completes (SUCCESS); a rescuer whose work type is disabled fails its assert before a tick is spent; a hostile with no
  lord is refused at stage with the reason; **the force level on the receipt is checked against the game**: for an
  order declared "through the giver", the job tap's "given by" field names that giver, and for a raw order it does
  not; a giver made to refuse gives MOD FAILURE.
- **Wrong code that must go red (live):** an executor that always starts a raw job and copies the declared level onto
  the receipt. GPT named this: the offline checks of my first draft would have passed it.

### `RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY`
- **Builds:** the taps for a mental state attempt (started or not), a quest registered, a letter, a message, a fire
  started and an explosion (each with its instigator); the tracks for weather, game condition, temperature, hour, the
  camera and the window stack.
- **Needs:** the cast tracks ticket.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_world_taps.py`, 9 checks: the hook rules for each of
  the six taps (6); an attempt and a start are two records (1); a message is recorded before the rule that hides
  repeats (1); the hook table check passes (1).

### `RIMMANDRAKE_BUILD_INCIDENT_QUEST_MENTAL_GATES_BEFORE_CERTIFICATE`
- **Builds:** the three gates that the calm profile will use, as mechanisms with an allow list and an attempt count:
  incidents at `IncidentWorker.TryExecute` (on the present awareness hook), quests at `QuestManager.Add`, mental
  states at `MentalStateHandler.TryStartMentalState`; the queued incidents held aside and given back with every
  absolute tick moved by the time held (the fire tick and the retry window). They are built before the certificate so
  that the certificate can show a held route and a refused route for each.
- **Needs:** the world event taps ticket.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_scene_gates.py`, 9 checks: the allow list lets one
  named incident through once (1); a held attempt is counted and recorded with its caller (1); a gate that is off
  changes nothing and records nothing (1); a held queue entry comes back with its fire tick and its retry window both
  moved (2); an entry already past its retry window when held is reported, never dropped in silence (1); the hook
  rules for the two new gate sites (2); with a canonical save loaded (CAMPAIGN), every gate is refused (1).
- **Wrong code that must go red:** a queue return that moves the fire tick only (GPT's case: the entry expires at
  once).

### `RIMMANDRAKE_BUILD_TAP_CERTIFICATE_CANARY_RUNS_OFF_STAGE`
- **Builds:** the certification suite of `05_build_design.md` decision 4: for every tap, a positive and a negative
  route fixture by real engine acts, in a disposable game; a planted blind tap; the list of foreign patches per tapped
  method; the certificate file keyed by companion hash, mod list fingerprint, patch inventory hash and the settings hash of
  every mod with a patch on a tapped method; the check at arm, which performs no gameplay act and compares the scene's
  needed routes with the certificate; the run-time witness (entries against records); the reference scene run with
  and without tracks. From this ticket on, a run with a valid certificate is no longer BOOTSTRAP.
- **Needs:** both tap tickets and the gates ticket.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_tap_certificate.py`, 11 checks: a certificate for
  another companion hash is refused (1); for another mod list (1); a changed patch inventory is refused (1); a tap
  with a route not shown is listed as such, never as covered (1); a scene that needs an uncertified tap is COULD NOT
  ARM (1); the arm check calls no op of the act list (1); a foreign prefix is named on the receipt (1); a missing
  certificate is "could not look", never "covered" (1); a changed setting of a mod with a foreign patch voids the
  certificate (1); an entry with no record voids that tap's coverage for the run (1); an absence on a method with a
  foreign prefix reads "not provable here" (1).
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_tap_certificate.py`, 4 rows: every fixture
  leaves its record on the 13-mod list; the same on the full list, with each foreign patch named; one hook taken off
  by hand is reported blind; the suite's time is printed.
- **Wrong code that must go red (live):** a tap whose Harmony patch was never installed while the recorder's unit
  tests pass.

### `RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE`
- **Builds:** on the sibling's calm tool: named, versioned profiles; a control reads HELD only after a planted
  breach of its kind was seen stopped on this mod list (in the certification session), else ARMED UNPROVEN; the breach
  log in the trace; the three gates of the gates ticket joined into the profile with a scene's exceptions; the profile
  armed again after a load; the lease; destructive controls refused only while a canonical world save is loaded (CAMPAIGN).
- **Needs:** the run-plan ticket; the gates ticket; the tap certificate; the sibling's calm tool.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_calm_profile.py`, 11 checks on the pure part: a
  control reads HELD only with its certificate line (1); a scene's exception opens one gate for one named event and
  closes it at leave (1); a hold on needs is two entries, the hold and what did not happen (1); the put-back runs in
  reverse order with read-back (1);
  a lease that ran out puts back (1); a value that could not be put back is named (1); a destructive control with a
  canonical save loaded is refused by name, and runs on any other save (1); "attempts stopped" and "scheduling switched off" are two numbers (1); a second
  driver's call is a breach of class APPARATUS (1); unknown profile keys are refused (1); a control of class NOT
  UNDONE is listed as such (1).
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_calm_profile.py`, 5 rows: a planted incident,
  a planted wild animal at the stage edge and a planted weather change each give one breach record that names them (3);
  a load in the middle changes no status (1); a killed driver leaves no control on after the lease (1).

### `RIMMANDRAKE_BUILD_SCENE_VERDICT_LEDGER_RECEIPT_IS_NOT_VERDICT`
- **Builds:** `src/RimMandrake/rimflow/scene_verdicts.py` and `scene_runs.jsonl` in a mod's version folder: the
  rules of kinds A, B and C over the runs of one claim on one build; a pass held by an UNRESOLVED run; a kind B budget
  and INCONCLUSIVE; a reclassification added, never overwritten; the hunt notice. A run counts for no bar when its
  receipt has an overlay stamp, the taint mark, an arm that was not compared with the reference, a PROOF build, or a
  map kind that the bar does not accept. The Stage 6 exit reads it.
- **Needs:** the judge ticket. No game.
- **Offline test:** `SELF src/RimMandrake/rimflow/selftest_scene_verdicts.py`, 17 checks: kind A decides on one
  valid run (2); kind B passes on one SUCCESS only with no MOD FAILURE and no UNRESOLVED (3); a spent budget gives
  INCONCLUSIVE (1); X of Y for a result random by design, and one short of X held for the Conductor's call (1); one UNRESOLVED holds the pass until classed (1); a
  reclassification keeps the history (1); a replay is not a sample (1); a cluster counts as one cluster (1); a stamped
  run reads TUNED and counts for nothing (1); a run with the taint mark and `overlay: none` counts for nothing (1); an
  uncompared arm counts for nothing (1); a change that does not touch what the scene reads keeps the verdict (1); a
  serious single UNRESOLVED opens a hunt notice with the four parts that the policy names (1); zero, none, could not
  look and failed are four answers in the summary (1); a re-judged run shows both outcomes (1).
- **Wrong code that must go red:** a ledger that checks the overlay stamp and not the taint mark; a kind B pass with
  an UNRESOLVED run standing.

### `RIMMANDRAKE_BUILD_SCENE_FILE_COMPILER_AND_LINT_NO_GAME`

**Dropped on 2026-11-23** (the last section of this file). No scene file is built. The lint checks below now belong to
`scene.contract`, and `RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP` carries them.
- **Builds:** `src/RimMandrake/Utils/scene_compile.py`: the scene file of `02_needs_design.md` §11 -> a run plan;
  defaults expanded and printed; the hash of the expanded contract; lint against the frozen def dump
  (`observed/inventory/DefDump_OFFICIAL/`); `needs.map`; fixtures by name. The three worked examples as real files.
- **Needs:** the run-plan ticket's plan format.
- **Offline test:** `SELF src/RimMandrake/Utils/selftest_scene_compile.py`, 13 checks: the three worked examples
  compile (3); a misspelt def is refused by name (1); a path whose first step is not an alias is refused (1); a
  success on "mod says" alone is refused (1); a kind B scene with no budget is refused (1); a kind A scene with an
  allowed miss is refused (1); a "throughout" condition that the success must break is refused (1); a condition on a
  tap that the plan does not arm is refused (1); a condition on the middle of a tick with no tap is refused (1); the
  expanded contract's hash changes when a default changes (1); one file compiles to the same bytes twice (1).
- The lint cannot know whether a success is already true before the act; that is decided at run time by the judge on
  the first sample (the judge ticket's check). GPT named this hole in my first draft.

### `RIMMANDRAKE_BUILD_DEVIATION_RECORD_SETTINGS_FIELD_JOINS_FIRST`
- **Builds:** the deviation record of `05_build_design.md` (calm, force, overlay, time and rate; the classes PUT BACK,
  GIVEN BACK and NOT UNDONE with its reach: station, save or process; the stamp; the taint mark and "process dirty"); `jawa/mod_settings_field set` writes only through it; the
  block on `WriteSettings` while a settings entry is live; the journal written before the first poke; the on-screen
  line `OVERLAY <name> <hash>`; the plan's `overlay:` block. This is step 1 of `04_live_tuning.md`.
- **Needs:** the run-plan ticket; the calm profile ticket.
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_deviation_record.py`, 14 checks: entries applied in
  order, and a failure reverts the earlier ones (1); a failed revert marks the game SPOILED (1); the taint mark stays
  after a revert (1); `overlay: none` with the taint set is not clean (1); a receipt lists every live entry of all four
  kinds with its class (1); a NOT UNDONE entry of reach "save" marks the game state dirty until the fixture is loaded, and one of reach
  "process" stays dirty across a load (2); a
  `const` and a `static readonly` target are refused by name (2); an overlay entry is refused with a canonical save loaded (1); a second
  holder cannot apply (1); the journal exists before the first write (1); a settings write to disk is blocked while an
  entry is live (1); a value changed by another hand is listed as differing from its default (1).
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_overlay_settings.py`: experiments E1 and E2
  of `04_live_tuning.md`.

### `RIMMANDRAKE_BUILD_MOD_TRACE_AND_RESET_HOOKS_BY_REFLECTION`
- **Builds:** `src/RimMandrake/_Shared/TestHooks/RMTestHooks.cs` (`RMTrace`, `RMResetAttribute`, `RMDigestAttribute`;
  pass three builds no `RMProbe` plug-in); the kernel's discovery; the "mod says" record type; first use in Explosive Knockback and
  FlowWorks when each next advances.
- **Needs:** the instruments ticket (pass three moved the block off the held run-plan ticket).
- **Offline test:** `SELF src/RimMandrake/bridgetools/selftest_test_hooks.py`, 8 checks: a mod with no hook is
  listed as such; a hook of the wrong shape is a named problem; `Emit` with a null sink allocates nothing; the sink is
  cleared at leave, also after a thrown tick; two mods' hooks do not collide; a hook from a PROOF build is refused
  for an acceptance run; a mod's release DLL with hooks names no type of the companion; **a digest hook is accepted
  only after it was seen to differ between a clean state and a state dirtied on purpose**.
- **Wrong code that must go red:** a `Digest` that returns a constant (GPT's case).

### `RIMMANDRAKE_BUILD_MUTANTS_BY_OVERLAY_AUTHOR_DOES_NOT_CHOOSE`
- **Builds:** `mutants.json` per mod with its lint and the two kinds (live, compiled); the seeded draw;
  `scene.py both-ways <scene>`: the green run and the red run each from the fixture save loaded fresh, with the random
  state written back; each mutant's witness (a recorded fact that differs because of the mutant); a list of at least
  two mutants per bar, reviewed by an agent that did not write the scene; both receipts in the scene's history; the live switch of one of our Harmony patches (off and
  on, with a call counter that proves it).
- **Needs:** the verdict ledger, the compiler and the deviation record tickets.
- **Offline test:** `SELF src/RimMandrake/Utils/selftest_scene_mutants.py`, 13 checks: a mutant that only switches
  the feature off is refused (1); a mutant must name a bar (1); the draw is the same for one scene and build, and the
  scene file cannot set it (2); the red run's receipt can never count as a pass (1); a red run that ends SUCCESS reads
  "mutant not killed" (1); a red run with no exposure proves nothing and says so (1); a red run whose witness did not change reads "mutant not
  used" (1); a bar with one mutant is refused (1); a red run that fails on another
  condition than the mutant names is reported as such (1); both runs start from the same fixture hash (1); a compiled
  mutant is listed "needs build" and is not run live (1); a bar whose killed mutants are all value changes says so (1).

### `RIMMANDRAKE_BUILD_STAMP_AGAIN_REPEATS_WITH_RESET_DIGEST`
- **Builds:** repeats of one plan on fresh stamps; N copies side by side as one cluster; the reset digest of the
  station and of each mod's digest hook, compared with the first stamp; the periodic comparison with a fresh process;
  launches, valid opportunities and exposures counted apart.
- **Needs:** the stage map, the verdict ledger and the mod hooks tickets.
- **Offline test:** `SELF src/RimMandrake/Utils/selftest_scene_repeats.py`, 8 checks.
- **Live test (UNRUN):** 20 stamped copies of the chosen-rescue scene finish in less wall time than 3 single runs
  take today; a planted cross-talk between two copies is a breach; **a mod state left dirty on purpose changes the
  reset digest and stops the repeat**.

### `RIMMANDRAKE_BUILD_FLIGHT_PROBES_STATE_AND_FRAME_NO_PICTURES`
- **Builds:** the probes `pawn.flight.*` and `pawn.anim.*` (the graphic state's name and `texPath` from
  `PawnRenderNode.TryGetAnimationGraphicState`, the animation's name and start tick), the offline audit that every
  frame's texture exists for every facing, the flapping scene of worked example 3 as a file. Takes over the build
  half of `FLYERFRAMES_PROVE_JOINT_SESSION`.
- **Needs:** the run-plan and compiler tickets.
- **Offline test:** `SELF src/RimMandrake/Utils/selftest_flight_frames.py`, 8 checks on recorded and hand-made
  series: a full flight passes; a skipped state fails; a flip-book that repeats one frame fails; a frame held for the
  wrong number of ticks fails; a landing that keeps a flying picture fails; a bird still in the air at the limit is not
  judged; "no bird took off" is an allowed miss; the asset audit names a missing texture.
- **Live test:** **the owner's act.** The first live run is with him present (`07_for_the_owner.md`, choice 1).

### Later tickets, each when its need is measured

| ticket | what it builds | needs |
|---|---|---|
| `RIMMANDRAKE_BUILD_DEF_FIELD_OVERLAY_WITH_WRITE_RECIPES` | step 2 of `04_live_tuning.md`: def-field writes through the record, the first recipes, the UNVERIFIED state, the fingerprint before and after. Offline: `SELF src/RimMandrake/bridgetools/selftest_overlay_recipes.py`, 10 checks. Live (UNRUN): experiments E3, E4, E5, E7 of that file | dropped 2026-11-25, not worth the touch yet: no scene, proof or mod writes a def field live (every `s.act.tune` caller names a `setting:` target, which the deviation record already reaches), and the settings live test (E1, E2: the cost of one point against a reload) is UNRUN. File it again when a tuning need names a def value that is not a mod setting, after E1 and E2 have run |
| `RIMMANDRAKE_BUILD_SWEEP_RUNNER_ON_RUN_PLAN_LIST` | steps 3 and 4 of `04_live_tuning.md`: `scene.py sweep` (plans that differ in their overlay, the repeated baseline, the shuffled order, the "cannot rank" answer), export, the absorbed check. Offline: `SELF src/RimMandrake/Utils/selftest_scene_sweep.py`, 9 checks | the repeats and def-field tickets |
| `RIMMANDRAKE_BUILD_KEEPER_SAVE_RAND_STATE_DIVERGENCE_FINDER` | for scenes in a hunt: a save and the random state at arm, the replay procedure, the trajectory fingerprint, "diverged at tick T". It measures the replay rate. Offline: `SELF src/RimMandrake/Utils/selftest_scene_replay.py`, 7 checks | dropped 2026-11-24, not worth the touch yet: no hunt is open, and one save with its random state written back does not repeat a run (0 of 10 pairs, `experiments/play_vs_step_rand_draws.md`). `scene_compare.py` already writes the random state back at arm and names the first diverging tick. File it again when the first hunt needs it, after `RIMMANDRAKE_FIND_RAND_DRAWS_PARTING_RUNS_EVEN_STEP` names the draws that part the runs |
| `RIMMANDRAKE_BUILD_LOAD_CROSSING_ACT_REBINDS_ALIASES` | the act op "save and load in the middle": settle after the load, bind each alias by its saved id with a link record, arm the record and the probes again, continue the timeline. Offline: `SELF src/RimMandrake/bridgetools/selftest_scene_load_crossing.py`, 6 checks | the run-plan and calm tickets |
| `RIMMANDRAKE_BUILD_WINDOW_ADAPTERS_TRADE_AND_SETTINGS_FIRST` | window content as data for the trade window and a Mod Settings page, on the present trade probe and settings smoke window. Offline: `SELF src/RimMandrake/bridgetools/selftest_window_adapters.py`, 6 checks | the run-plan ticket |
| `RIMMANDRAKE_BUILD_FLIGHT_FILMSTRIP_FOR_HIS_EYE_ONLY` | **only on the owner's yes**: one image that tiles N ticks of a flight, by the off-screen capture that exists; never a pass condition; first proven on a vanilla bird | the flight probes |

## The order at a glance

Each arrow reads "is needed by". Names are shortened to their subject words; the full names are the headings above.

```
now, on the present bridge:  the sibling run (receipt, calm, first exception)

COND_RUN_INTO_TICK (the slice) ─┬─ SCENE_JUDGE ─────────────┐
                                └─ RUN_LIFE_CYCLE ──────────┤
GAME_WATCHER ───────────────────────────────────────────────┴─ RUN_PLAN (bootstrap mode)

RUN_PLAN ──┬─ PLAY_AGAINST_PAUSED_STEP (measure)
           ├─ STAGE_OPS ── STAGE_MAP ──────────────────┐
           ├─ CAST_TRACKS_AND_JOB_TAPS ────────────────┴─ CAST_ASSERTS_AND_ORDER
           │        └─ WORLD_EVENT_TAPS ── GATES ── TAP_CERTIFICATE ── CALM_PROFILE ── DEVIATION_RECORD
           ├─ SCENE_FILE_COMPILER ── FLIGHT_PROBES ── (FLIGHT_FILMSTRIP, on his yes)
           └─ MOD_TRACE_AND_RESET_HOOKS
SCENE_JUDGE ── SCENE_VERDICT_LEDGER
MUTANTS_BY_OVERLAY needs: SCENE_VERDICT_LEDGER, SCENE_FILE_COMPILER, DEVIATION_RECORD
STAMP_AGAIN_REPEATS needs: STAGE_MAP, SCENE_VERDICT_LEDGER, MOD_TRACE_AND_RESET_HOOKS
```

The judge, the verdict ledger, the compiler and the game watcher need no companion build. The tickets that change the
companion are built one after another, never two at one time: one game install has one companion DLL, and a duplicate
tool name stops every tool of the companion (`skills/rimbridge-companion/SKILL.md` §1).

## Old items that this order absorbs

For the Conductor to drop as superseded, each with this file as the reason, once the absorbing ticket is filed:

| old item | absorbed by |
|---|---|
| `ADVANCEUNTIL_WIRE_PER_TICK_STOP` (bridge conditions: an advance stops on the exact tick) | `RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED` |
| `CONDWATCH_BUILD_OWNED_RINGS` (bridge conditions: watchers outside an advance) | the tracks of the same ticket and the two tap tickets |
| `RINGPROBES_WIRE_EVENT_CURSORS` (bridge conditions: conditions over event rings) | `RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE` (the judge counts tap records) |
| `TICKBURST_PROVE_MANY_TICKS_ONE_FRAME` (many ticks per frame, with its comparison) | `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED` |
| `FLYERFRAMES_PROVE_JOINT_SESSION` (flight recorded as state) | `RIMMANDRAKE_BUILD_FLIGHT_PROBES_STATE_AND_FRAME_NO_PICTURES` for the build; the joint session stays his |

## What is measured first

Pass one listed six things to measure in the first week. Their homes:
- ticks per second by arm, and whether the camera rate changes results: the measurement ticket;
- the cost of the calm profile and of a reassert: the calm profile ticket's live test;
- the cost of clean and build: the staging ops ticket's live test; the cost of each stage map kind: the stage map
  ticket's live test;
- the overhead of the taps: the tap certificate's live test;
- the replay rate: the keeper save ticket.

## Decisions that the Conductor owes before or while these are built

They are not the owner's (only five acts stay his), and "not his" does not mean "no decision" (GPT). Each is small.

1. Test-only hooks in shipped mods (`RMTrace`, reset and digest hooks): allow or not. Recommended: allow.
2. How long traces and keeper saves are kept, and the disk limit for them, with the danger that the limit guards.
   Recommended: the terms of `05_build_design.md` decision 9, and the pool's existing disk floor.
3. The first content of the standard calm profile. Recommended: the controls marked READ in pass one's table.
4. Which bars may rest on a staged scene alone, and which need a colony scene. Recommended: decide per bar at the
   mod's next advance, with the rule of decision 7.
5. The reviewed list of readers (properties and methods that an acceptance track may call): who reviews an addition.
   Recommended: the code review role, as for any pipeline code.
6. The wording of the policy's sentence on a forbidden effect caused by another mod (pass one's item, still open).

## Pass three: the enacted order (2026-11-23)

The Conductor enacted the pick of pass three on 2026-11-23 (delegated; on the item
`RIMMANDRAKE_DESIGN_BRIDGE_TWO_PYTHON_TESTS_FEW_RICH_ENTRY_POINTS`). The design is `11_design.md`; the contracts are in
`contracts/`. A scene is a Python script on the scene library; the game holds generic hands; no scene file. This
section is the order. Where a section above speaks of a scene file, a compiler or a run plan as a thing to build, this
section is right. Each act below was made through `rimflow` on 2026-11-23 and is on the ledger.

### What was done to the tickets

| act | ticket | detail |
|---|---|---|
| **dropped** | `RIMMANDRAKE_BUILD_SCENE_FILE_COMPILER_AND_LINT_NO_GAME` | no scene file is built. Its lint duties live in `scene.contract`; the conversion ticket's test carries those four checks. Successor: `RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP` |
| **held, with a wait to 2026-12-07** | `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA` | waits on experiment A (`RIMMANDRAKE_RUN_BRIDGE_EXPERIMENT_PYTHON_ACT_AGAINST_IN_GAME_ACT`), scenes 1 and 3. Dropped when they agree; reopened in part (a batch schedule or a bounded rule, never a scene language) only for the scene shape that scene 3 shows to differ |
| **split** | `RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO` | keeps the C# duty: each staging tool replies from a read-back made in the same main-thread hop as the write. 6 checks. The Python part is `s.stage` |
| **split** | `RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER` | keeps the C# duty: the order through the game's own giver code, the motive act, the force level on the record. 4 checks. The Python part is `can=` of `s.stage` and `s.act.order` |
| **split** | `RIMMANDRAKE_BUILD_LOAD_CROSSING_ACT_REBINDS_ALIASES` | keeps the C# duty: the load barrier. 4 checks. The Python part is `s.act.reload` |
| **filed** | `RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH` | the instruments: `jawa/run_until` (exact stop, per-tick recorder of any value path, session), `jawa/read_paths` (hidden reads), `jawa/act_batch` with request ids. 18 checks |
| **filed** | `RIMMANDRAKE_BUILD_SCENE_LIBRARY_TEN_NAMES_FIVE_LAYERS_TODAY` | the skeleton of `scene.py`: receipts, refusals, the process mark, help from the contract pages, and the first two entry points `scene.open` and `s.run`, plus `s.raw`. 22 checks |
| **filed** | `RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP` | FlowWorks `sc_moat_raid`, Explosive Knockback's storeroom bomb pit, Gimme Some Slack `sc_wall_lamp_looks`, on the library; each remaining name is built when a scene needs it; old against new is measured. 17 checks |
| **blocks moved** | calm profile, cast tracks, deviation record, flight probes, load crossing, mod hooks, window adapters, the play-against-step measurement, staging ops | each was blocked on the plan ticket; each is now blocked on the instruments ticket |

Each acceptance test is in the ticket's prose (`infrastructure/state/items/<ID>.md`). Each of the six commands (three
new, three split) was seen red on 2026-11-23: exit 1, because its selftest file does not exist yet `[MEASURED]`.

### The order

```
buildable now, side by side (one is C#, one is Python):
  1. WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH     the instruments: per-tick recorder, exact stop, hidden read, act batch
  2. BUILD_SCENE_LIBRARY_TEN_NAMES                the skeleton, scene.open, s.run, s.raw
then:
  3. CONVERT_THREE_SCENES                         needs 1, 2 and SCENE_JUDGE; shows whether ten names help

beside them, no game needed:   SCENE_JUDGE (needs the slice), GAME_WATCHER (free now)
live, the Conductor's:         the slice's live proof, then experiment A (scene 1 needs only landed code; scene 3 needs 1)

after 1, one companion build at a time:
  RUN_LIFE_CYCLE (the session that outlives its driver; scene.attach)
  STAGE_OPS (C# duty) ── STAGE_MAP ──┬─ CAST_ASSERTS_AND_ORDER (C# duty)
  CAST_TRACKS_AND_JOB_TAPS ──────────┘  └─ WORLD_EVENT_TAPS ── GATES;  TAP_CERTIFICATE
  CALM_PROFILE;  MOD_TRACE_AND_RESET_HOOKS;  MEASURE_PLAY_AGAINST_PAUSED_STEP
  DEVIATION_RECORD ── DEF_FIELD_OVERLAY           (the hands behind s.act.tune)
  SCENE_JUDGE ── SCENE_VERDICT_LEDGER ── MUTANTS_BY_OVERLAY
  STAGE_MAP ── STAMP_AGAIN_REPEATS ── SWEEP_RUNNER (a Python loop over a script)
  FLIGHT_PROBES;  WINDOW_ADAPTERS;  LOAD_CROSSING (C# duty);  KEEPER_SAVE
held:    RUN_PLAN, until experiment A
dropped: SCENE_FILE_COMPILER
```

### What the Conductor still owes

- The slice and the filing item are closed: `prove_scene_tick_wiring.py` read 7 PASS of 7 on ArchSmall on 2026-11-23.
  `SCENE_JUDGE` is no longer blocked on the slice. Experiment A: `experiments/exp_a_result.md`.
- The tickets that stay keep their text, in which "plan" now means "what the script asked for in a call"
  (`05_build_design.md`, corrected at its top). `RMProbe` and `RMFixture` plug-ins are not built.
- The sweep ticket's name still says "run plan list". The name stays (a name states what was meant at filing); its work
  is a Python loop.
