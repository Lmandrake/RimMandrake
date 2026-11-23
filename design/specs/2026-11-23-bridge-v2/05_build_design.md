# BRIDGE v2.0, pass 2: how to build it (the build design)

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_REBUILD_OR_IMPROVE_CODE_READ`. Written 2026-11-23.
The needs are `02_needs_design.md` (pass one). The build order is `06_build_order.md`. The owner's page is
`07_for_the_owner.md`. The GPT review of this file and what it changed are at the end, and its two rounds are kept in
`census_sources/gpt_pass2_round1_answer.md` and `census_sources/gpt_pass2_round2_answer.md`.

Every claim carries a tag. **READ**: I read the named code in this run (the RimWorld 1.6 source through RimSage, or a
file of this repo). **MEASURED**: a record on disk holds the number, and the record is named. **GUESS n%**: not read,
not measured. Nothing in this file was measured in a game: this run touched no game.

The owner's aim (2026-11-23): "Force the situation ALWAYS if possible, there are too many variables to control
otherwise." and "let's get VERY creative in trying to remove them to preserve sanity and not burn all our tokens on
repeating large expensive test suites with low yields even if the mod is 100% correct."

## The answer

**Improve, by joining what exists. Do not rebuild.**

Pass one did not read the bridge's code, and wrote its needs as if a new core were owed. The code already holds most of
that core, as parts that were built one at a time and never joined. The build is therefore one small new part, the
**scene kernel**, which joins them, plus one part outside the game, the **scene judge**.

Three ideas carry the design. Each one answers the owner's aim directly.

1. **Record inside the game, judge outside the game.** The game side does only what must be exact to the tick: it
   stages the scene, does each act step on its tick or condition, evaluates the stop condition after every tick, and
   records every value that the contract names. The seven-outcome verdict is then computed by a Python program from the
   recorded trace. So when a check is found wrong, the repaired check **judges the kept trace again and no game runs**.
   Today a wrong check costs a full rerun. (The present condition evaluator already exists twice, in C# and in Python,
   and the two must give byte-identical output on shared vectors `[READ: JawaBenchCondCore.cs header]`. That twin is
   what makes this safe.)
2. **A stage with no bystanders.** Scenes run on a stage map that holds only the cast. The standing test colony lives on
   a second small map. So there is no fence to build, no path cost to distort, and census ranks 4 and 7 (a bystander
   dies, starves, hauls, drinks, reserves) cannot happen on the stage.
3. **One store in the game for every deviation from shipped play.** The calm controls, the force used on each actor, the
   live-tuning overlay of `04_live_tuning.md`, a pinned update rate and a planted fault are all the same kind of thing:
   a declared change that the game process holds, stamps on every receipt, and puts back. They share one store, one
   restore and one stamp. A planted fault is an overlay entry, so "shown both ways" needs no rebuild and no restart.

## What the present bridge is

READ in this run: `src/RimMandrake/bridgetools/` (177 C# files, 81,638 lines, 427 distinct `jawa/` tool names; counted
with `wc` and `grep` on 2026-11-23), `HOOKS.md`, the csproj, and the headers and key bodies of the files named below.

**The transport is not ours.** RimBridgeServer is a Workshop mod (id 3727949765). Its source is not in this repo
`[READ: csproj comment]`. It loads our companion DLL from the game's `BridgeTools` folder and calls each `[Tool]` method
off the main thread; our code hops to the main thread with `ctx.MainThread.InvokeAsync` `[READ: rimbridge-companion
skill §2]`. A hop is not a frame boundary `[READ: JawaBenchSceneRunnerTools.cs header]`. Its argument binder drops
unknown parameters; our Harmony guard refuses them for our tools `[READ: JawaBenchArgGuard.cs]`. It binds Windows
loopback, so callers run under `python.exe`.

**What exists, and what each part gives the v2 design.**

| part (file) | what it does today `[READ]` | role in v2 |
|---|---|---|
| Scene runner (`JawaBenchSceneRunnerCore.cs`, `JawaBenchSceneRunnerTools.cs`, tool `jawa/run_scenes`, built 2026-11-18) | One call runs a suite: each scene on its own plot, staged, ticked in process, judged; rows are PASS, FAIL or UNMEASURED with a cause. A scene is a C# method `[RMTest]` in the mod's PROOF build, found by reflection. The rules are unit-tested offline in a plain .NET harness. | The frame-slice loop, the deadline-bounded dispatch and the "game changed under the run" guard are kept as the kernel's time driver. C# scenes stay as plug-ins (below). |
| FlowWorks playtest runner (`JawaBenchFlowWorksPlaytest.cs`, 2026-10-06) | Scenarios as C# iterators that yield "N ticks" or "until predicate"; a journal line written when each scenario ends; two tick modes: the game's own loop at Ultrafast, or a paused step loop. | The proof that both tick modes already work in one driver. Its scenes migrate; the runner retires. |
| Condition evaluator (`JawaBenchCondCore.cs`, 1,578 lines; `JawaBenchCondProbes.cs`; Python twin `src/RimMandrake/Utils/conds.py`) | JSON condition trees, three-valued (true, false, unknown), with `changed`, `edge`, `stays`; a run object `CondRun` with `Arm` and an end-of-tick `Step`, watchers, samples, snapshots, coverage and cost. Probes read cells, pawns, things, and **any field or property path, private ones included** (`thing.field`, bound once to a getter; a method is refused). A reading that cannot be made is `gone`, `oob`, `unbound` or `error`, never 0. | This is pass one's "value paths" and "conditions", already built and unit-tested. **`CondRun` was never wired into a tick**: its item `ADVANCEUNTIL_WIRE_PER_TICK_STOP` is still proposed. Wiring it is the keystone. |
| End-of-tick dispatcher (`JawaBenchVitals.cs` `TickPre`/`TickPost`) | A guarded prefix and postfix on `TickManager.DoSingleTick`, installed at the first arm, with reentry, skip and orphan guards. | The one end-of-tick hook. It serves the game's own loop and the step loops alike, because both call `DoSingleTick`. |
| Awareness (`JawaBenchAwareness.cs`, `JawaBenchAwarenessCore.cs`) | Hooks on `IncidentWorker.TryExecute`, `PawnGenerator.GeneratePawn`, `Pawn.SpawnSetup`, the wild animal spawner, hives, hatching and birth; an incident journal that tells "called" from "fired"; where each pawn came from; a block on wild animal spawning. | The incident tap, the arrival watch and the wild-animal control. |
| Damage and lineage rings (`JawaBenchSituationalTools.cs`) | Postfixes on `Thing.TakeDamage` (not virtual, so one hook sees all damage), `Pawn.Kill`, `Thing.Destroy`, stack absorb, split and ingest. | The damage, death and destruction taps. |
| Vitals and the safe advance (`JawaBenchVitals.cs`, `JawaBenchVitalsCore.cs`, tool `jawa/safe_advance`) | Every 60 ticks a diff of the map's pawns gives triggers: arrival, downed, hurt, hostile, starving, mental state, departed. A latch stops an advance. A clock ledger catches a clock jump. | The cast watch and the game watch start here. The 60-tick diff becomes a per-tick track for cast members. |
| Safety (`JawaBenchSafetyCore.cs`, `JawaBenchCompanionSafety.cs`, tool `jawa/companion_handshake`) | Two profiles: CAMPAIGN (the default) and TEST, granted only by a file on the machine, never by a caller. A gate prefix on every tool. Game epochs, so a call aimed at an old game is refused. A handshake that says what loaded. | Pass one's "sitting mode" and "never destructive on his game" are this gate. The scene kernel is a TEST-only family. |
| Disk writer (`JawaBenchTpsWriter.cs`) | Hooks copy numbers and strings on the main thread and enqueue; a writer thread serialises in order, bounded, counts drops, and never blocks the game. | The trace writer. Pass one's "written out while running, bounded, survives a crash" exists. |
| Hook discipline (`HOOKS.md`, `JawaBenchHookGuard.cs`, `selftest_bridge_hooks.py`) | Every Harmony patch site is on one table with its rules (contained, takes `__runOriginal`, checks the thread, safe as an orphan, void finalizer). A selftest fails when a new site is missing from the table. | Every new tap joins this table. |
| Pictures (`JawaBenchArtboardTools.cs`, `JawaBenchShotSettleTools.cs`, `JawaBenchHudLease.cs`) | An off-screen capture of a map rectangle: the main camera is pointed at the rectangle, rendered to a texture and put back inside one step after `Update`, with a postfix that makes the game submit the draws for that view. A tool that snaps drawn pawn positions to their cells while paused. A lease that turns screenshot mode off again. | Pass one's "pixels" exist in the "move and restore" form. |
| Forcing (`jawa/ordered_job`, `jawa/order_pawn`, `jawa/lord_*`, `jawa/pawn_flight`, `jawa/pen_pin`, `jawa/set_draft`) | Orders through the float menu or the work giver, lords and duties, pins. | Levels 2 to 7 of the Minimum Force ladder exist as tools. |
| Calm, as separate tools (`jawa/weather_set`, `jawa/rain_suppress`, `jawa/wild_spawner_block`, `jawa/incident_queue_*`, `jawa/quiet_site`, `src/RimMandrake/Utils/modcheck/quiet_site.py`) | Each control is one call. None reports a breach. Most are lost on a load. | The mechanisms of the calm profile. The sibling run joins them into one call now. |

**Three faults of the present bridge that the design must repair** `[READ]`:
1. **A C# scene runs on a build that is not the shipped build.** `jawa/run_scenes` needs the mod's PROOF build
   (`RM_PROOFS`); `scene_runner.py` says "deploy it, run this, then put the release build back". A verdict made on the
   PROOF DLL is not a verdict about the release DLL (policy §8: the record names the build that the game had loaded).
2. **Every time driver steps while the game is paused.** `jawa/run_scenes`, `jawa/safe_advance` and the playtest
   runner's default mode call `DoSingleTick` in a loop with `CurTimeSpeed = Paused`. Whether a paused step loop gives
   the verdicts of ordinary play was designed as an experiment on 2026-11-06
   (`design/RimMandrake/tickburst_2026-11-06/final.md`) and never run: the item is BLOCKED on a path fault of its
   measuring tool. So no run on record shows that the paused step loop agrees with play.
3. **The parts do not know each other.** The scene runner does not arm the awareness taps, does not use the condition
   evaluator, writes no trace, and returns rows that its own C# judge made. The condition evaluator is reachable only by
   `jawa/cond_eval`, which reads once and advances nothing.

## Engine facts settled in this pass

The fourteen guesses of `03_open_questions.md`, each read in the RimWorld 1.6 source through RimSage on 2026-11-23.

| guess of pass one | status now | what I read |
|---|---|---|
| A path request's result is set only inside `PathFinderTick` (80%) | **READ, true** for queued requests | `PathRequest.found` is written only by `Resolve` (called from `PathFinder.FinalizeRecyclePathJobData`) and by `Validate` (called from `ComputeWorkThisTick`); both run only inside `PathFinderTick`, which first calls `ForceCompleteScheduledJobs`. A second route exists and is synchronous: `PathFinder.FindPathNow` (about ten vanilla callers: exit map, melee approach, prison break, breaching). Neither route depends on frames. |
| The global random state is not in the savegame (85%) | **READ, true** | A search of the whole source for a save site of `Rand`'s seed or iterations finds none. A reload is a new sample. |
| Thing ids survive a save and load (disputed) | **READ, true** | `Thing.ExposeData` saves `"id"`; `UniqueIDsManager.ExposeData` saves `nextThingID`. The census record "ids shifted by 1000" is explained by `UniqueIDsManager`'s constructor, which starts a NEW game's counter at `Rand.Range(0, 1000)`: that record compared two games, not one game across a load `[GUESS 75% for the explanation]`. The kernel still binds an alias to the object, and to the id only across a load. |
| Every mental state starts through `TryStartMentalState` (85%) | **READ, true** | `MentalStateHandler.curStateInt` has one write site that sets a state (inside `TryStartMentalState`) and one that clears it. About 40 callers reach it. A load restores a saved state without it. |
| Inspirations have one entry (75%) | **READ, true** | `InspirationHandler.curState` is set only in `TryStartInspiration`. |
| Quest offers arrive as incidents (70%) | **READ, FALSE** | `QuestUtility.GenerateQuestAndMakeAvailable` has at least nine callers that are not incidents (a quest part, the orbital scanner, a hacked thing, a ritual outcome, the comms dialog twice, a book, a royal title, a bestowing ceremony). The one choke point is `QuestManager.Add`, called from `QuestUtility` only (apart from debug and old-save code). The gate goes there. |
| Orbital traders are incidents (70%) | **READ, true** | `PassingShipManager.AddShip` has one caller, `IncidentWorker_OrbitalTraderArrival`. |
| One point overrides the outdoor temperature of a map (60%) | **READ, true, and better than guessed** | `MapTemperature.OutdoorTemp` is the one getter that reads the tile's temperature. It returns first `map.Biome.constantOutdoorTemperature` when the biome sets one, then, for a pocket map, `map.generatorDef.pocketMapProperties.temperature`. **So a pocket map, or a test biome, holds its temperature by data, with no patch.** |
| Plant growth and wild plant spawning can be held per station (60%) | **READ, half true** | Wild plant spawning is one method per map, `WildPlantSpawner.WildPlantSpawnerTick`: it can be held for a whole map. Growth is each plant's own `TickLong`: no per-station hold exists. Growth is WATCHED, and a stage map with bare ground has nothing to grow. |
| A spawn tap sees every route by which a pawn appears (80%) | **READ, true** | `GenSpawn.Spawn` is the only caller of `SpawnSetup` outside the overrides, and every override calls its base. The present `Pawn.SpawnSetup` postfix sees every arrival, loads included (flag `respawningAfterLoad`). |
| The UI has no stored widget tree (90%) | **READ by structure, 95%** | Windows draw through static immediate-mode calls each frame (`Window.DoWindowContents`, `Widgets.*`). The present settings smoke test already draws each mod's settings page inside a hidden window to catch its exceptions `[READ: JawaBenchProofHookTools.cs]`. |
| Projectiles compute their position from their own tick count (80%) | **READ, true** | `Projectile.ExactPosition` is computed from `DistanceCoveredFraction`, which is `1 - ticksToImpact / StartingTicksToImpact`. |
| How a flying animal's flip-book frame is chosen (not read) | **READ** | `AnimationDefGenerator_Flying` makes one keyframe per picture at tick `i * ticksPerFrame`, each with its own `GraphicStateDef` whose `texPath` is that picture. `AnimationWorker_Keyframes.GraphicStateAtTick` returns the keyframe for `PawnRenderTree.AnimationTick`, which is game ticks minus `animationStartTick`, wrapped. The frame is a pure function of game ticks. The probe calls `PawnRenderNode.TryGetAnimationGraphicState` and records the state's name and `texPath`. **Layer 2 of the flapping test is a small build, not a hard one.** |
| The engine exposes one log channel for errors that never reach `Verse.Log` (85%) | **READ, true** | `Root` subscribes `Log.Notify_MessageReceivedThreadedInternal` to Unity's `Application.logMessageReceivedThreaded`. A tap subscribes to the same event. It is called on any thread. |
| A pocket map with an empty generator is cheap to make and remove (unknown) | **READ for the route, cost UNMEASURED** | `PocketMapUtility.GeneratePocketMap` is `MapGenerator.GenerateMap` with a pocket parent; `DestroyPocketMap` removes it. The present tool `jawa/map_seed_foil` already generates a second map, reads it and drops it inside one call on the full list (commit `d5e3400df2`), so the route works in practice. Its time is not on record. GUESS 70%: under 3 s for a 75 x 75 map on the full list. |
| Static state of mods survives a load (90%) | **READ by structure, 97%** | `GameDataSaveLoader.LoadGame` builds a new `Game`; no assembly is unloaded. |

Three more facts that decide choices below, read in this pass:
- **Ordinary play can stop on an exact tick.** `TickManager.TickManagerUpdate` breaks its loop right after a
  `DoSingleTick` when `Paused` is true. A postfix on `DoSingleTick` that sets `CurTimeSpeed = Paused` therefore ends the
  game's own loop on that tick. The exact stop needs no stepper of ours.
- **The camera-dependent update rate has one source.** `GenTicks.GetCameraUpdateRate(Thing)` returns 15 when the thing
  is not on the shown map or not in the camera's view, and zoom level + 1 (1 to 5) when it is.
- **The queued incidents fire by absolute tick.** `IncidentQueue.IncidentQueueTick` fires an entry when its `FireTick`
  has passed, and drops an entry whose retry time has passed. A queue that is only frozen fires everything late at
  once when it is released. A frozen queue must have its fire ticks moved by the time it was held, or be saved aside.

Still GUESS after this pass: the replay rate (50% on a test list, 20% on the full list: pass one's figures stand); the
cost of a pocket map; whether Mono keeps a method inlined in callers that were compiled before a patch (GUESS 60% that
it can happen for small methods; the canary rite below tests it instead of trusting it).

## Three ways to build, and the pick

### Way A: join in place (the pick)

A scene kernel is added to the present companion as a few new files. It reuses the frame-slice loop, the end-of-tick
dispatcher, the condition evaluator, the taps and the disk writer. A scene is **data**: a scene file is compiled by
Python into a **run plan** (JSON), and one new tool, `jawa/run_plan`, runs it. The judge is Python.

- **Cost** `[GUESS 65%]`: about 1,500 lines of new C# (the plan interpreter, the staging ops that call the bodies of
  present tools, the per-tick wiring, the new taps), about 2,500 lines of Python (the compiler, the lint, the judge, the
  verdict ledger). Twelve tickets reach the first full scene with a verdict; see `06_build_order.md`.
- **Risk.** The companion is one flat partial class of 177 files; a fault in a new file can break tool registration
  for all (a duplicate tool name kills the whole provider `[READ: rimbridge-companion skill §1]`). Guard: kernel logic
  lives in pure `*Core.cs` files with offline harnesses, as the present cores do, and in a class of its own (the
  scene runner already had to leave the partial class for a loader reason `[READ: SRL comment]`).
- **Risk.** The transport is a third party's. Guard: the kernel needs only "start a run" and "read a result file"; the
  trace and the receipt go to disk through our own writer, so a long run does not hold a connection (below).

### Way B: a new core as a mod of its own, with the present bridge kept for exploring

A new dev-only RimWorld mod (a real mod with a `GameComponent`) holds the kernel, its own transport (a file drop or a
named pipe) and its own taps. The present companion stays as the exploring layer.

- **Buys:** independence from RimBridgeServer; a tick hook with no Harmony (a `GameComponent` ticks inside the game's
  tick); it is loaded before the first map; it can run where the bridge is absent.
- **Costs** `[GUESS 60%]`: a second transport, a second deploy path, a second identity check, and the cores twice or a
  reference between the two assemblies: about twice Way A before the first scene runs. A dev mod in the mod list
  changes the list that the test claims to prove, and it must be kept out of every shipped list. The calm controls and
  forcing tools would be called across an assembly edge or copied.
- **Risk:** two bodies that both patch `DoSingleTick` and `TryExecute`. The hook table of today has one owner.
- **When it would be right:** if RimBridgeServer breaks on a game update and its author does not repair it. The pick
  keeps this door open cheaply: the kernel's pure cores do not reference the bridge's SDK, so they can move into a mod.

### Way C: every scene is C# inside its mod, and the bridge only dispatches

This is where the code was heading on 2026-11-18: `[RMTest]` scenes in each mod's PROOF build, one runner.

- **Buys:** the fastest scene; full access to the mod's internals; no interpreter; it works today for one suite.
- **Costs:** a scene edit is a C# edit, a build, a deploy and a game restart (22 s on 13 mods, 14 to 25 minutes on the
  full list `[MEASURED: 01_census.md]`). The verdict is made on the PROOF build, not the shipped one (fault 1 above).
  The judge is code of the mod under test and shares its blind spots; the runner already carries an "outside read" to
  limit that `[READ: SceneRunnerCore header]`. A contract that is C# cannot be linted, hashed or judged again offline.
  No scene of this kind can cover two mods without a hard reference.
- **Risk:** the 110 proof classes of today were this way without a shared shape `[MEASURED:
  live_test_speed_assessment_2026-11-12.md]`; the cost showed as reruns, not as build effort.

### Why A

1. **The evidence is in the tree.** The parts that pass one ranks 2, 3, 4 and 6 of its first ten (taps, tracks, a
   runner, a calm call) exist and are unit-tested. A rebuild would write them again and meet again the traps that
   they record (`skills/rimbridge/references/silent-failures.md`, the six faults of `HOOKS.md`).
2. **Way C's build identity fault cannot be repaired inside Way C.** A data scene runs on the release DLL.
3. **Only A and B allow the judge outside the game**, and B pays twice for the same result.
4. **A keeps both older rulings true at once.** 2026-11-06: proofs stay in Python and the game gains generic
   primitives. 2026-11-12: one shared in-game runner, prioritized by the owner. A data scene is a generic primitive that
   runs in the game, and its verdict is made in Python.

What A gives up: independence from RimBridgeServer (kept as a door, above), and the raw speed of a compiled scene for
very long scenes. A C# plug-in covers the second where it is measured to matter.

## The scene kernel

### The parts

```
scene file (YAML, in the mod)                      OUTSIDE THE GAME (Python, our repo)
   | scene_compile.py: lint against the frozen def dump, expand defaults, hash
   v
run plan (JSON)  ---- jawa/run_plan ---->          INSIDE THE GAME (companion, TEST profile only)
                                                     admit -> calm -> stage -> arm -> act and run -> settle -> leave
                                                     writes: trace (JSONL, by the disk writer), receipt core (JSON)
   <---- handle, then the two file paths ----
scene_judge.py: trace + plan -> one of the seven outcomes, the first failed condition
scene_verdicts.py: the runs of one claim on one build -> the scene's verdict (the policy's rules)
```

### What runs inside the game, and only that

| phase | what the kernel does | built from |
|---|---|---|
| admit | The profile is TEST; the driver lock of this game is held by the caller's run id; the handshake's assembly hashes and mod list equal the plan's; no other run is live. | the gate, the handshake, the sibling run's receipt tool |
| calm | Arms the plan's calm profile and writes each control's status. | the sibling run's calm tool, then the breach log ticket |
| stage | Takes a station on the stage map; cleans it; builds terrain, things and the cast from the plan; reads each write back; binds each alias to its object; runs the capability asserts. | the bodies of `jawa/build_batch`, `jawa/set_terrain_batch`, `jawa/spawn_pawn`, `jawa/destroy_batch` and the pawn kit tools; new: aliases, asserts |
| arm | Compiles every condition of the plan with the present compiler (a name that does not resolve is refused here, by name). Adds one track for every probe that any condition names, so the trace holds what the judge needs by construction. Runs the canary rite (below). Records the random state, the camera rate and a start digest. | `CondRun.Arm`; new: the canary |
| act and run | After every tick, in `TickPost`: sample the tracks (written only on change), step the conditions, fire each act step whose tick or condition is due, test the end. An act step is one of a closed list of ops (order through a giver, raw job, place, explosion, fire an incident, set weather, start flying, apply an overlay entry, save and load). | `CondRun.Step`, the present forcing tools' bodies |
| settle | Reconciles the trace against state read directly (every alias: bound, spawned, alive, position, holder). Closes the trace. | new, small |
| leave | Pauses the game. Cleans the station, or keeps it when the plan says so. Repays the deviation store. | the store (below) |

The kernel **does not** compute SUCCESS or MOD FAILURE. It reports facts with two exceptions that must end a run early
and so must be evaluated inside: the end condition, and a "stop now" list (an exception storm, the game left the map,
the run's deadline). Everything else is the judge's.

### Decision 1 in detail: judge outside, from the trace

Pass one put the deciding inside the game, to remove the round trip from the deciding window. The round trip is removed
here too: nothing is read or decided between the act and the end. What moves outside is only the arithmetic of the
verdict, after the game is paused. This buys four things that an in-game judge cannot give.

- **A repaired check costs no game time.** The trace is kept. `scene_judge.py --rejudge <trace>` gives the new outcome.
  The repo's rule "repair a wrong check in the sitting, and show it FAIL on a planted fault and PASS on the real build"
  becomes two re-judgements of two kept traces.
- **The judge is testable with no game.** Its fixtures are recorded and hand-made traces, one for each row of the
  classifier. A mutation run over the judge is an offline selftest.
- **A change of the judge needs no companion build and no game restart.**
- **The checker cannot share the mod's process state.** It sees only what the taps and tracks wrote.

What it costs: the trace must hold everything a condition reads. The arm phase guarantees that for value conditions.
For event conditions the tap must be armed; a condition that names a tap that is not armed is refused at compile time.
A condition that needs a value at an instant inside a tick (not at its end) is served only by a tap; the lint says so.

**One semantics, two homes.** Conditions inside the game (act triggers, the end) and conditions in the judge are the
same tree language, compiled by the same rules: the C# evaluator and its Python twin already share vectors
(`src/RimMandrake/Utils/conds_vectors.json`). The cut nodes of the first version (`count`, `seq`, `before`, `after`)
are added on the Python side first, because the judge needs them and the game does not.

### Decision 2: ordinary execution first, and what "ordinary" means here

The kernel has three time modes. Each receipt names the one used.

| mode | how ticks run | evidence it gives | status |
|---|---|---|---|
| **PLAY** | The game's own loop, unpaused, at a named speed. `TickPost` evaluates and pauses on the end tick (exact, by the fact read above). | Ordinary play. The default for every acceptance scene. | New, small: the playtest runner's `speed` mode already does it without the exact stop. |
| **STEP** | Paused, `DoSingleTick` in slices, one slice per Unity frame inside a wall budget. | A model of play: the per-frame work runs once per slice, `Paused` reads true, the tick rate multiplier reads 0. | Exists (`run_scenes`, `safe_advance`). It is today's only mode. |
| **BURST** | STEP with a large budget and a pinned update rate. | The fastest; the furthest from play. | Later, and only if PLAY at the game's top speed is measured too slow. |

- **The end-of-tick hook** is the present `TickPost` on `DoSingleTick`. No second hook is added.
- **STEP is not thrown away, and it is not trusted.** The first measurement ticket runs the 2026-11-06 experiment at
  last: one scene, PLAY against STEP, traces compared tick by tick. Until a scene has that comparison on record, a STEP
  verdict reads "STEP, not compared" on its receipt, and the verdict ledger does not count it for a bar.
- **The camera.** In a test game the camera is the kernel's. At arm it is placed so that every station of the run is in
  view, and the zoom is recorded; the update rate that the cast had (zoom level + 1) goes on the receipt. When the
  stations do not fit in one view, the plan must pin the rate: a prefix on `GenTicks.GetCameraUpdateRate` returns the
  declared value for the run. A pinned rate is an entry in the deviation store, and the receipt says so.
- **Staying alive.** PLAY needs nothing. STEP yields every frame already and reports "no new frame in 15 s" as a
  stall `[READ: SceneFrameStallMs]`.
- **Long scenes.** `jawa/run_plan` returns a handle at once when the plan's tick limit is over a threshold. The run
  goes on inside the game (driven per frame by a hidden `MonoBehaviour`, the playtest runner's pattern). The receipt
  core and the trace are files; `jawa/run_status` reads the state. A caller that dies loses nothing.
- **The comparison that proves a faster mode** is the trace itself: the two runs start from one save (both reloaded),
  and the judge's inputs (tracks and taps of the cast) must be equal tick by tick up to the first random draw that
  differs; the first difference is reported, as pass one's divergence finder.

### Decision 3: value paths

They exist: the probe `thing.field` with a path, and the pawn, cell and map probes `[READ: JawaBenchCondProbes.cs]`.
The path is resolved once at arm, type by type, to a chain of field and property getters; private members are allowed
(`BindingFlags.NonPublic`); a method is refused; a link that is null reads as its named state. What the kernel adds:

- **A root that is an alias**, and roots for a thing's comp (`comp(TypeName)`), a map component, a hediff of a pawn by
  def, and a mod's settings object. Today a path starts at a thing id.
- **A reviewed list of pure methods** that a path may call (`Pawn.Downed` is a property and needs none; the list is
  for getters such as `GetStatValue` and the FlowWorks depth getters that are already allowed by name). A method not
  on the list is refused by name. Properties stay allowed, because the engine's own UI calls them every frame; a
  property known to have a side effect goes on a deny list (none is known today).
- **Rebinding.** A track re-resolves from its root every tick when any link is a replaceable object (a job, a comp
  list); the cost is measured per run and shown (`cost` exists in the result today).
- **The flight probes** `pawn.flight.*` and `pawn.anim.*`, which the first version refused by name pending the flight
  ticket: state, lerp tick, the graphic state's name and `texPath`, facing.

### Decision 4: taps, and the canary rite

**Tracks first, taps only where a tick's end cannot see.** Many of pass one's taps are a change of state that is still
there at the end of the tick: a job changed, a toil index changed, a cell changed, a hediff appeared, a mental state
began, the weather changed. A track written on change records these with no Harmony patch, so it cannot be blind by
inlining, by an override, or by another mod's prefix. Its limit is stated on the receipt: end-of-tick resolution.
A Harmony tap is added only for a fact that does not survive to the end of the tick, or whose cause is known only at
the call.

| fact | how it is caught | hook point | state |
|---|---|---|---|
| damage (asked and dealt, instigator, part) | tap | `Thing.TakeDamage` postfix | exists |
| death, destruction | tap | `Pawn.Kill`, `Thing.Destroy` | exists |
| a pawn appears; where it came from | tap | `Pawn.SpawnSetup` postfix, `PawnGenerator.GeneratePawn` | exists |
| incident attempt, with caller, held or run | tap | `IncidentWorker.TryExecute` | exists; the allow list is new |
| error, warning, exception | tap | `Verse.Log` prefixes exist; add the Unity event | the sibling run builds the first-exception tap |
| job start and end, with who gave it and the end condition | tap | `Pawn_JobTracker.StartJob`, `EndCurrentJob` | new |
| toil, position, facing, health summary, mental state, carried thing, holder | track, per tick, cast only | none | new, cheap |
| reservation refused | tap | `ReservationManager.Reserve` (result false) | new |
| mental state attempt that did not start | tap | `MentalStateHandler.TryStartMentalState` | new |
| quest offered | tap and gate | `QuestManager.Add` | new |
| fire started, with instigator; explosion, with instigator | tap | `FireUtility.TryStartFireIn`, `GenExplosion.DoExplosion` (names to confirm at build) | new |
| letter, message | tap | `LetterStack.ReceiveLetter`, `Messages.Message` | new |
| window opened | track of the window stack per frame while a run is live | none | vitals reads the stack today |
| weather, game condition, temperature, hour | track | none | new, cheap |
| sound asked, effect asked | tap, off by default | `SoundStarter.PlayOneShot` | later |

**The arm-time test: the canary rite.** A synthetic event sent into our own recorder proves only our recorder. So at
arm the kernel performs the real engine acts on a **canary**: a thing and a pawn of a vanilla kind that it spawns in a
quarantine cell of the stage map. It spawns them (arrival tap), damages the thing by 1 (damage tap), gives the pawn a
wait job and ends it (job taps), reserves and releases a cell (reservation tap), logs one marker warning (log tap),
then destroys both (destroy tap). Each armed tap must hold the canary's record with the canary's id. A tap that does
not is COULD NOT ARM, and the run does not start. The rite also lists, for each tap, every other mod's prefix on the
same method (from Harmony's patch info, which `jawa/harmony_patches` reads today), because a foreign prefix can skip
the original: such a tap is armed with the note "can be skipped by <mod>".

The canary proves the route that the canary took. It does not prove every route. Two more guards stay from pass one:
each tap states the routes it covers, and the settle phase reconciles the trace against state. An unexplained
difference is COULD NOT LOOK. Fires and explosions have no harmless canary; their taps are proven by a fixture scene
in the kernel's own selftest suite, once per build of the companion, not at every arm.

### Decision 5: sent programs

No script engine is added. The exploring layer keeps what it has: the 427 tools, `jawa/static_call` (TEST only), and
`jawa/cond_eval`. A test pilot who needs new logic in the game writes a public static method in a C# file of the
mod's PROOF build or of the companion, as today.

**A script becomes a plug-in by an attribute.** A probe plug-in is a public static method with an attribute whose
type name is `RMProbeAttribute` (name, version), found by reflection exactly as `RMTestAttribute` is found today, so no
mod references the bridge. A plan may name a plug-in as a track (`plugin:<name>@<version>`); the receipt lists it. A
plug-in that lives in a PROOF build is refused for an acceptance run (fault 1); a plug-in for acceptance ships in the
companion, or in the mod's release DLL behind the trace interface of decision 8.

`[RMTest]` scenes stay valid as an exploring tool and for a fixture too complex for data. Their rows are never a bar's
evidence while they need the PROOF build.

### Decision 6: pixels without his camera

**Keep "move and restore inside one step"; build no second camera.** The present off-screen capture already points the
main camera at the rectangle after `Update`, renders to a texture, and restores it before the frame is shown, with the
view-rectangle postfix that makes the game submit the draws `[READ: JawaBenchArtboardTools.cs lines 10 to 20]`.

- On a test game the camera belongs to the kernel, so nothing is owed.
- On ArchBig the capture is allowed only while his hold is off and the profile allows it. He would notice nothing on
  screen, because the swap happens between the update and the present of one frame `[GUESS 80%: no visible flicker;
  the map's section meshes for the other view are regenerated in that frame, which can cost a frame-time spike that he
  could feel as one hitch]`. In sitting mode it is refused.
- A true second camera would also need a second cull and draw submission for dynamic things, which the engine does per
  frame for one view only `[READ: the same header]`. That is a large build for no gain on test games.

### Decision 7: the station fence

**There is no fence, because there are no bystanders on the stage.**

- A test game runs with two maps. The **green room** is the map where the standing test colony lives: fed, rested,
  drafted, needs held. It exists so that the game has free colonists (the engine starts its game-over countdown when the
  player has none: `GameEnder.gameEnding` `[READ: the field, in JawaBenchVitals.cs; the exact rule: GUESS 85%]`). The **stage map** holds stations and cast, and nothing else: no
  colonist, no animal, no wild spawn (the spawner is held for that map), bare ground of one terrain, no roof, no plant.
- A scene that needs a colonist casts one. A cast colonist is built for the scene and removed at clean.
- One trap, read in the code: an incident whose def requires colonists on the target map "succeeds" without running
  when the map has no free colonist `[READ: JawaBenchAwareness.cs header, IncidentWorker.TryExecute]`. A raid scene
  therefore casts its defenders, and the incident tap's "called, not fired" record catches the miss.
- The stage map is a pocket map when its cost allows (its temperature is then held by data, a fact read above), else a
  second settlement map on a temperate tile. Which one is decided by the first measurement of the cost.
- **Scenes on his full-list colony** (the walks) cannot move the colony. There the bystanders are held by means that
  are per pawn and so do not touch the cast: an allowed area that excludes the stations for each colony pawn and
  animal, and the scene's things set forbidden, so that no bystander hauls or uses them. Wild and visiting pawns are watched,
  and removed between scenes. This is weaker than the stage, and the receipt says "shared map".

### Decision 8: reset hooks and trace points in our mods

No shipped mod references dev tooling. The pattern is the one that `RMTestAttribute` uses today: a small shared source
file compiled into each mod, and discovery by name through reflection.

- **Shared file** `src/RimMandrake/_Shared/TestHooks/RMTestHooks.cs`, compiled into each mod as `internal`:
  - `RMTrace.Emit(string name, ...)`: a static method whose body is `var s = Sink; if (s != null) s(...)`. `Sink` is a
    static delegate field, null in play. The cost in play is one field read and one branch.
  - An attribute `RMResetAttribute` on a public static method `string Reset(string scope)`, which clears the mod's
    per-scene state (caches, counters, pending callbacks) and answers what it cleared.
  - An attribute `RMDigestAttribute` on a public static method `string Digest(string scope)`, which answers a digest of
    the same state. Reset verification compares it.
- **The kernel finds them** in every loaded assembly whose name starts with `RimMandrake`, by attribute type name. It
  sets each `Sink` at arm and clears it at leave. A mod with no hook is listed on the receipt as "no reset hook".
- A "mod says" record is evidence of a branch only. The compiler refuses a success condition that stands on it alone
  (pass one's rule).

This adds test-only code to shipped mods. Pass one sent that to the Conductor (allow, recommended). I agree: the code
is inert when no kernel is present, and it is the only way to see why a giver refused.

### Decision 9: where the receipt, the trace and the keeper saves live

Under the agent storage root (on Archmagi `D:\ClaudeWork`), never in the repo:

```
<root>\rimmandrake\scenes\<game name>\<yyyymmdd>\<run id>\
    plan.json            the run plan as sent (its hash is the scene's identity)
    receipt.json         written by the kernel (facts) and completed by the judge (outcome); schema versioned
    trace.jsonl          the tracks, taps and marks, in order, with ticks
    keeper.rws.txt       the name of the keeper save, when one was written (the save stays in the game's Saves folder)
```

- The in-game writer writes into the game's own JawaBench folder, as the TPS record does today; the Python driver
  moves the run's files to the storage root when the run ends (one game may be on SteveDesktop).
- **Kept:** receipts for the life of the mod version (they are small). Traces 14 days, or until the hunt that uses
  them closes, or for as long as the run is the standing evidence of a bar. Keeper saves until their hunt closes.
- **In the repo:** only the scene's verdict line in the mod's version folder (the verdict ledger, decision 12), with
  the run id and the receipt's hash. A committed file never cites a path under the storage root as its only evidence;
  it cites the run id.
- The receipt schema is the contract with the pipeline. It is a boundary page of its own
  (`design/specs/2026-11-23-bridge-v2/boundary.md`, written with the first ticket).

### Decision 10: migration

First the scene that exists in both forms, so that the two can be compared: **Explosive Knockback's storeroom pair**,
which is an `[RMTest]` suite today, and its spared-carrier scene (pass one's worked example 1). Then **FlowWorks'
ordered rescue** (worked example 2), because the census gives 1 success in 18 free runs against 2 of 2 when ordered.
Then the three scenes whose opportunity never arose (`sc_moat_raid`, `sc_islands`, `sc_pit_trap_raid`), which need the
raid allow list. The full-list walks last: they need the shared-map holds and ArchBig.

A mod converts its scenes when it next advances, as a planned change of its next version; no current bar moves
(pass one's item for the Conductor, kept).

### Decision 11: the two disputed points

- **The general window transcript: later, behind adapters.** The first UI needs are named windows of ours (the trade
  window, a Mod Settings page). For those, an adapter reads the window's own state object, and the settings smoke
  window already draws every settings page. A general transcript means a patch on each `Widgets` entry that draws text
  or a control, active for one frame of one window; it is feasible `[GUESS 70%]` and it is not in the first twenty
  tickets. GPT's cut is taken for now; pass one's need stands as a later ticket.
- **The general before-sweep: it is a query over tools that exist.** `jawa/pawn_census`, `jawa/incident_queue_peek`,
  the window stack, `jawa/weather_get`, the handshake and the log scan give the first five finding classes with no new
  C#. On the stage map most classes are empty by construction (no bystander, no reservation, no plant). The sweep is
  therefore a short Python function in the driver, grown one class at a time when a run names one. No ticket of its own.

### Decision 12: the scene verdict ledger

**In the Maturation Pipeline, beside the test table, in Python.** It is policy, not transport: it must change when
the policy changes, with no companion build. One append-only file per mod version,
`design/concepts/<Mod>/version/scene_runs.jsonl` (a line per run: scene, plan hash, build, outcome, mode, overlay
stamp, run id, receipt hash), and one program, `src/RimMandrake/rimflow/scene_verdicts.py`, that applies the rules of
the three kinds, holds a pass on an UNRESOLVED run, counts a kind B budget, and writes the hunt notice. A run with an
overlay stamp other than `none`, a STEP run that was not compared, or a PROOF build can never count for a bar.

### Decision 13: who chooses a plant

**The mod keeps a list of mutants; the program draws; the overlay applies.**

- Each mod has `design/concepts/<Mod>/version/mutants.json`. A mutant names the bar it should break and an overlay
  entry that breaks it: a tuning value set to a wrong number, a formula slot replaced, one of our Harmony patches taken
  off, a settings switch flipped. The builder writes the first mutants with the bars; the coverage judge adds more.
- "Shown both ways" for a scene is one sitting in one process: the green run first (overlay `none`), then, for a
  mutant that the program draws for this scene by a seeded choice that the scene's author does not control, the red
  run under the mutant's overlay, then the revert. The red run's receipt carries the stamp, so it can never be counted
  as a pass. Its outcome must be MOD FAILURE on the condition that the mutant names.
- A fault that no live value can express (a wrong branch in compiled code) needs a mutant build. Those are few, cost a
  restart each, and are batched.
- A mutant that only switches the whole feature off is refused by the list's lint (pass one's warning).

## Where live tuning sits (`04_live_tuning.md` folded in)

The overlay is not a separate tool beside the kernel. It is one of four kinds of entry in the **deviation store**, the
one in-game record of everything that is not shipped play:

| kind of entry | examples | who writes it |
|---|---|---|
| calm control | incidents held, wild spawn held, weather forced, needs of the green room held | the calm phase |
| force | "rescuer: order through the giver (level 3)", "carrier: pinned" | the stage and act phases |
| overlay entry | a def field, a tuning point, a settings field, a formula slot, a patch switch | a plan's `overlay:` block, a sweep, a mutant |
| time and rate | mode PLAY, STEP or BURST; a pinned update rate; a named time compression | the arm phase |

One store gives all four what `04_live_tuning.md` asks for the overlay alone:
- **The game owns the truth.** One call lists every live entry with its before value. A crashed script leaves a
  known game.
- **Every receipt carries the whole store**, filled by the game. A scene cannot leave it out.
- **Restore is one mechanism**: reverse order, read back, a debt file written before the first write and repaid at
  leave, at lease end and at the next start of the companion (pass one §10).
- **The stamp and the taint mark** are properties of the store: a receipt reads `overlay: none` only when no overlay
  entry is live, and `tainted: true` from the first overlay write until the process restarts.
- **A sweep is a list of run plans** that differ in their `overlay:` block. The kernel needs only "run this list";
  the repeated baseline, the shuffled order and the cold confirmation of the winner are the driver's.
- **The verdict ledger enforces the three rungs.** A stamped run is TUNED, never PASS.
- **ArchBig never arms.** Overlay entries are refused in the CAMPAIGN profile, as `jawa/mod_settings_field set` is
  today `[READ: 04_live_tuning.md, JawaBenchSafetyCore.cs]`.

The build order of `04_live_tuning.md` is kept inside the kernel's order: first `jawa/mod_settings_field` joins the
store (our settings are pokeable today), then def-field writes with recipes, then the sweep on the run plan, then
export and the absorbed check, then tuning classes in the mods as each advances, then formula slots and patch
switches, then the load-time overlay. Mutants need only the first step for a settings switch, and the patch switch
for a patch.

## Creative removals: what else is forced or removed, and by what

The owner asked for creativity in removing variables. Beyond the three ideas at the top:

| variable | removed by | cost |
|---|---|---|
| Bystanders, haulers, drinkers, their deaths in long runs | the stage map holds only cast | one more map in a test game |
| Outdoor temperature drift, heat waves on the cast | a pocket stage map holds its temperature by data | none, if the pocket map's cost is acceptable |
| Wild plants, regrowth, animals arriving | bare stage, wild plant and animal spawners held for that map | none |
| Rain on a scene | the stage map's weather is forced; a pocket map has its own weather manager `[GUESS 70%]` | none |
| The raid that will not come | the scene fires the incident through its own worker with exact parms (`fire_incident` exists), the gate allows that one incident only, and the tap proves "fired", not only "called" | none |
| The raider that will not choose | two scenes: the ordered act (kind A), and the choice as a budgeted kind B in side-by-side copies | pass one §5; unchanged |
| A wrong check | re-judge the kept trace | zero game time |
| A flaky scene that needs "the same moment again" | the keeper save and the random state, only for scenes in a hunt | half a second per run in a hunt |
| The camera | held by the kernel on a test game; the rate is recorded or pinned | none |
| A stale build | the receipt's loaded-build hashes, checked in admit before a tick is spent | the sibling run builds it |
| Another mod's ticker | scenes run on the smallest mod list that holds the claim; the full list is a named, separate check | the tiers exist |
| An unknown influence | every run that ends UNRESOLVED keeps its trace and its keeper save, so the next step is a read, not a rerun | disk |

**What is deliberately not forced.** The decision that a scene claims to test stays with the mod (Minimum Force). The
kernel records the force level per actor on the receipt, and the lint refuses a scene whose entry line steps past its
own claim.

## What this design does not settle

- Whether STEP agrees with PLAY for our scenes. Nobody has measured it. The first measurement ticket does.
- The cost of the stage map as a pocket map, and whether mods' map components behave on a pocket map as on a
  settlement map `[GUESS 75% yes for ours]`. If not, the stage is a second settlement map.
- The replay rate. The keeper save and the divergence finder measure it when the first hunt needs it.
- The general window transcript and draw-submitted probes: later tickets, not designed further here.
- Droids, sound heard, taste: pass one's testing horizon stands.

## What GPT changed

(Filled after the two review rounds.)
