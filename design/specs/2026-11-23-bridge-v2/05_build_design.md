# BRIDGE v2.0, pass 2: how to build it (the build design)

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_REBUILD_OR_IMPROVE_CODE_READ`. Written 2026-11-23.
The needs are `02_needs_design.md` (pass one). The build order is `06_build_order.md`. The owner's page is
`07_for_the_owner.md`. The GPT review of this file and what it changed are at the end, and its two rounds are kept in
`census_sources/gpt_pass2_round1_answer.md` and `census_sources/gpt_pass2_round2_answer.md`.

**Corrected 2026-11-23 after pass three** (`11_design.md` is the design; the Conductor enacted its pick). A scene is a
Python script on the scene library, not a scene file, and no plan interpreter is built unless experiment A asks for
one. The lines of this file that described a scene file, its compiler, a run plan and the plug-in attributes are
corrected below, each in its place. What this file says about the trace, the judge outside the game, the evidence
contract, the taps and their certificate, the stage with no bystanders, the deviation record, the mod hooks and the
verdict ledger stands. Where this file says "the kernel" for a run of several phases, read "the session of
`scene.open` and the hands it calls": the phases are the same, and Python calls them one at a time.

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
   recorded trace. So when a check is found wrong, the repaired check **judges the kept trace again and no game runs**,
   whenever the trace holds what the repaired check reads (the judge says so itself; see "The evidence contract").
   Today a wrong check always costs a full rerun. (The present condition evaluator already exists twice, in C# and in Python,
   and the two must give byte-identical output on shared vectors `[READ: JawaBenchCondCore.cs header]`. That twin is
   what makes this safe.)
2. **A stage with no bystanders.** Scenes run on a stage map that holds only the cast. The standing test colony lives on
   a second map. So there is no fence to build, no path cost to distort, and census ranks 4 and 7 (a bystander
   dies, starves, hauls, drinks, reserves) cannot happen on the stage.
3. **One store in the game for every deviation from shipped play.** The calm controls, the force used on each actor, the
   live-tuning overlay of `04_live_tuning.md`, a pinned update rate and a planted fault are all the same kind of thing:
   a declared change that the game process holds and stamps on every receipt. They share one record and one stamp.
   Each kind has its own rule for being put back, and the record says which changes cannot be put back. A planted
   fault is an overlay entry, so most "shown both ways" runs need no rebuild.

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
| Safety (`JawaBenchSafetyCore.cs`, `JawaBenchCompanionSafety.cs`, tool `jawa/companion_handshake`) | Two profiles: CAMPAIGN, which guards a loaded canonical world save and nothing else, and TEST. A file on the machine lists the canonical saves; a caller cannot change the profile. A gate prefix on every tool. Game epochs, so a call aimed at an old game is refused. A handshake that says what loaded. | The scene kernel is a TEST-only family: it does not run while a canonical world save is loaded. His looks are guarded by his hold and the driver lock, not by this gate. |
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

**Scope of every row.** READ means: true of the vanilla 1.6 source. A mod can add a route that the vanilla source does
not have (a subclass that does not call its base, a second caller, a patch). So no tap or gate is trusted because of a
row here. Each fact that a tap or a gate stands on is tested on the real mod list by the tap certificate (decision 4).

| guess of pass one | status now | what I read |
|---|---|---|
| A path request's result is set only inside `PathFinderTick` (80%) | **READ, true** for queued requests | `PathRequest.found` is written only by `Resolve` (called from `PathFinder.FinalizeRecyclePathJobData`) and by `Validate` (called from `ComputeWorkThisTick`); both run only inside `PathFinderTick`, which first calls `ForceCompleteScheduledJobs`. A second route exists and is synchronous: `PathFinder.FindPathNow` (about ten vanilla callers: exit map, melee approach, prison break, breaching). Neither route depends on frames. |
| The global random state is not in the savegame (85%) | **READ, true** | A search of the whole source for a save site of `Rand`'s seed or iterations finds none. A reload is a new sample. |
| Thing ids survive a save and load (disputed) | **READ, true** | `Thing.ExposeData` saves `"id"`; `UniqueIDsManager.ExposeData` saves `nextThingID`. The census record "ids shifted by 1000" is explained by `UniqueIDsManager`'s constructor, which starts a NEW game's counter at `Rand.Range(0, 1000)`: that record compared two games, not one game across a load `[GUESS 75% for the explanation]`. The kernel still binds an alias to the object, and to the id only across a load. |
| Every mental state starts through `TryStartMentalState` (85%) | **READ, true** | `MentalStateHandler.curStateInt` has one write site that sets a state (inside `TryStartMentalState`) and one that clears it. About 40 callers reach it. A load restores a saved state without it. |
| Inspirations have one entry (75%) | **READ, true** | `InspirationHandler.curState` is set only in `TryStartInspiration`. |
| Quest offers arrive as incidents (70%) | **READ, FALSE** | `QuestUtility.GenerateQuestAndMakeAvailable` has at least nine callers that are not incidents (a quest part, the orbital scanner, a hacked thing, a ritual outcome, the comms dialog twice, a book, a royal title, a bestowing ceremony). The one choke point for a quest being registered is `QuestManager.Add`, called from `QuestUtility` only (apart from debug and old-save code). The gate goes there. The letter that shows an offer to the player is a separate event, caught by the letter tap. |
| Orbital traders are incidents (70%) | **READ, true** | `PassingShipManager.AddShip` has one caller, `IncidentWorker_OrbitalTraderArrival`. |
| One point overrides the outdoor temperature of a map (60%) | **READ, true, and better than guessed** | `MapTemperature.OutdoorTemp` is the one getter that reads the tile's temperature. It returns first `map.Biome.constantOutdoorTemperature` when the biome sets one, then, for a pocket map, `map.generatorDef.pocketMapProperties.temperature`. So a pocket map, or a test biome, fixes its OUTDOOR temperature by data, with no patch. Room temperature, heaters, fires and game conditions still act. |
| Plant growth and wild plant spawning can be held per station (60%) | **READ, half true** | Wild plant spawning is one method per map, `WildPlantSpawner.WildPlantSpawnerTick`: it can be held for a whole map. Growth is each plant's own `TickLong`: no per-station hold exists. Growth is WATCHED, and a stage map with bare ground has nothing to grow. |
| A spawn tap sees every route by which a pawn appears (80%) | **READ, true** | `GenSpawn.Spawn` is the only caller of `SpawnSetup` outside the overrides, and every override calls its base. The present `Pawn.SpawnSetup` postfix sees every vanilla arrival, loads included (flag `respawningAfterLoad`). A mod's pawn class that overrides `SpawnSetup` without calling its base would be missed; the settle reconciliation (a census of the map's pawns against the trace) is the guard. |
| The UI has no stored widget tree (90%) | **READ by structure, 95%** | Windows draw through static immediate-mode calls each frame (`Window.DoWindowContents`, `Widgets.*`). The present settings smoke test already draws each mod's settings page inside a hidden window to catch its exceptions `[READ: JawaBenchProofHookTools.cs]`. |
| Projectiles compute their position from their own tick count (80%) | **READ, true** | `Projectile.ExactPosition` is computed from `DistanceCoveredFraction`, which is `1 - ticksToImpact / StartingTicksToImpact`. |
| How a flying animal's flip-book frame is chosen (not read) | **READ** | `AnimationDefGenerator_Flying` makes one keyframe per picture at tick `i * ticksPerFrame`, each with its own `GraphicStateDef` whose `texPath` is that picture. `AnimationWorker_Keyframes.GraphicStateAtTick` returns the keyframe for `PawnRenderTree.AnimationTick`, which is game ticks minus `animationStartTick`, wrapped. Given the tree's current animation and its start tick, the frame is a pure function of game ticks. It is the picture that the game selects, not proof of what reached the screen. The probe calls `PawnRenderNode.TryGetAnimationGraphicState` and records the state's name and `texPath`. **Layer 2 of the flapping test is a small build, not a hard one.** |
| The engine exposes one log channel for errors that never reach `Verse.Log` (85%) | **READ, true** | `Root` subscribes `Log.Notify_MessageReceivedThreadedInternal` to Unity's `Application.logMessageReceivedThreaded`. A tap subscribes to the same event. It is called on any thread. |
| A pocket map with an empty generator is cheap to make and remove (unknown) | **READ for the route, cost UNMEASURED** | `PocketMapUtility.GeneratePocketMap` is `MapGenerator.GenerateMap` with a pocket parent; `DestroyPocketMap` removes it. The present tool `jawa/map_seed_foil` already generates a second map, reads it and drops it inside one call on the full list (commit `d5e3400df2`), so the route works in practice. Its time is not on record. GUESS 70%: under 3 s for a 75 x 75 map on the full list. |
| Static state of mods survives a load (90%) | **READ by structure, 97%** | `GameDataSaveLoader.LoadGame` builds a new `Game`; no assembly is unloaded. |

Three more facts that decide choices below, read in this pass:
- **Ordinary play can stop on an exact tick, with one trap.** `TickManager.TickManagerUpdate` breaks its loop right
  after a `DoSingleTick` when `Paused` is true. A pause made in a postfix on `DoSingleTick` therefore ends the game's
  own loop on that tick. The trap (found by GPT, then read): the setter of `CurTimeSpeed` **refuses** the write when
  the player has no control (`PlayerCanControl`: a gravship landing confirmation, or `Game.PlayerHasControl` false). So
  the kernel refuses to start a run in that state, reads the speed back after it pauses, and treats a run that ticked
  past its end as a fault of the apparatus. Other postfixes on the same method and the frame's own work still run after
  the pause; the live test checks the final tick count on a frame that ran several ticks.
- **The camera-dependent update rate has one source.** `GenTicks.GetCameraUpdateRate(Thing)` returns 15 when the thing
  is not on the shown map or not in the camera's view, and zoom level + 1 (1 to 5) when it is.
- **The queued incidents fire by absolute tick.** `IncidentQueue.IncidentQueueTick` fires an entry when its `FireTick`
  has passed, and drops an entry whose retry time has passed. A queue that is only frozen fires everything late at
  once when it is released. A frozen queue must have its fire ticks moved by the time it was held, or be saved aside.

Still GUESS after this pass: the replay rate (50% on a test list, 20% on the full list: pass one's figures stand); the
cost of a pocket map; whether Mono keeps a method inlined in callers that were compiled before a patch (GUESS 60% that
it can happen for small methods; the tap certificate of decision 4 tests it instead of trusting it).

## Three ways to build, and the pick

### Way A: join in place (the pick)

A scene kernel is added to the present companion as a few new files. It reuses the frame-slice loop, the end-of-tick
dispatcher, the condition evaluator, the taps and the disk writer. A scene is a **Python script** on the scene library
(`11_design.md`); the new tools are generic hands (`jawa/run_until`, `jawa/act_batch`, `jawa/read_paths`). The judge is
Python.

- **Cost** `[GUESS 65%]`: about 1,500 lines of new C# (the per-tick wiring, the session, the act batch, the path
  reads, the new taps), about 2,500 lines of Python (the scene library, the judge, the verdict ledger). This guess was
  made for the plan interpreter and the compiler; it has not been made again for the library `[GUESS 50%]`. The tickets are in `06_build_order.md`; the first three give one scene with a recorded trace and a verdict.
- **Risk.** The companion is one flat partial class of 177 files; a fault in a new file can break tool registration
  for all (a duplicate tool name kills the whole provider `[READ: rimbridge-companion skill §1]`). Guard: kernel logic
  lives in pure `*Core.cs` files with offline harnesses, as the present cores do, and in a class of its own (the
  scene runner already had to leave the partial class for a loader reason `[READ: SRL comment]`).
- **Risk, understated in my first draft (GPT).** Joining parts that were built apart means joining their life
  cycles: two tick drivers, cancellation, static state, patch order, a writer that falls behind, and 427 tools that
  can change the game while a run is live. Unit tests of each part say nothing about that. Guards: a **run lock**
  (while a run is live, the gate that already sits on every tool refuses every tool of a changing family, by the run's
  id; reads are allowed and counted on the receipt), one driver per run, and the first ticket is a narrow slice that
  proves the life cycle on one scene before the general interpreter is written.
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
- **A fairer form of C (GPT).** Compiled fixtures can live in the companion and not in the mod, reach the mod by
  reflection, write a trace and leave the verdict to an outside judge. That repairs the build identity fault and the
  shared blind spot. What stays: each scene edit is a companion build and a restart of the game, and a duplicate tool
  or type breaks every tool. Way A keeps this form as its plug-in route (decision 5) for the scenes that data cannot
  express.

### Why A

1. **The evidence is in the tree.** The parts that pass one ranks 2, 3, 4 and 6 of its first ten (taps, tracks, a
   runner, a calm call) exist and are unit-tested. A rebuild would write them again and meet again the traps that
   they record (`skills/rimbridge/references/silent-failures.md`, the six faults of `HOOKS.md`).
2. **A data scene runs on the release DLL and is edited with no build and no restart.** Way C can repair its build
   identity fault only by moving fixtures into the companion, and then every scene edit restarts the game.
3. **A, B and the companion-fixture form of C all allow the judge outside the game** (GPT corrected my first claim
   that only A and B do). A is the only one of the three in which a scene edit needs no build and no restart, and B
   pays twice for the same result.
4. **A keeps both older rulings true at once.** 2026-11-06: proofs stay in Python and the game gains generic
   primitives. 2026-11-12: one shared in-game runner, prioritized by the owner. A data scene is a generic primitive that
   runs in the game, and its verdict is made in Python.

What A gives up: independence from RimBridgeServer (kept as a door, above), and the raw speed of a compiled scene for
very long scenes. A C# plug-in covers the second where it is measured to matter.

**The cost figures above are guesses from line counts.** GPT's objection holds: the pick is confirmed or refuted by one
measured slice, not by an estimate. The first ticket of `06_build_order.md` is that slice: one scene, the game's own
loop, a trace, an exact stop; the ticket after the judge kills, cancels and throws in the middle of a run. If the slice shows that the parts cannot share one life cycle,
Way B is reopened with the pure cores moved into a mod.

## The scene kernel

### The parts

```
scene script (Python, in the mod)                  OUTSIDE THE GAME (Python, our repo)
   | scene.contract: lint against the frozen def dump, hash; scene.open, s.stage, s.run, s.act, s.read
   v
one call for each step ---- the hands ---->        INSIDE THE GAME (companion, TEST profile only)
                                                     admit -> calm -> stage -> arm -> act and run -> settle -> leave
                                                     writes: trace (JSONL, by the disk writer), receipt core (JSON)
   <---- each reply with its receipt ----
scene.judge: trace + contract -> one of the seven outcomes, the first failed condition
scene_verdicts.py: the runs of one claim on one build -> the scene's verdict (the policy's rules)
```

### What runs inside the game, and only that

The phases below are the duties of the game side. Under pass three, Python asks for each phase by a call of the scene
library, and "the plan" in a row means "what the script asked for in that call". The order of the acts is the script's.

| phase | what the kernel does | built from |
|---|---|---|
| admit | The profile is TEST; the driver lock of this game is held by the caller's run id; the handshake's assembly hashes and mod list equal the plan's; no other run is live; the player has control (the pause can be written). The run lock goes on. | the gate, the handshake, the sibling run's receipt tool |
| calm | Arms the plan's calm profile and writes each control's status. | the sibling run's calm tool, then the breach log ticket |
| stage | Takes a station on the stage map; cleans it; builds terrain, things and the cast from the plan; reads each write back; binds each alias to its object; runs the capability asserts. | the bodies of `jawa/build_batch`, `jawa/set_terrain_batch`, `jawa/spawn_pawn`, `jawa/destroy_batch` and the pawn kit tools; new: aliases, asserts |
| arm | Compiles every condition of the plan with the present compiler (a name that does not resolve is refused here, by name). Adds one track for every probe that any condition names, and the standard cast tracks. Checks the tap certificate against the loaded build (decision 4). Writes the first sample of every track, before any act. Records the random state, the camera state and a start digest. | `CondRun.Arm`; new: the certificate check |
| act and run | After every tick, in `TickPost`, in this fixed order: sample the tracks (written only on change), step the conditions, test the end, then fire each act step that is due. A run never ends on a tick in which an act step fired. An act step is one of a closed list of ops (order through a giver, raw job, place, explosion, fire an incident, set weather, start flying, apply an overlay entry, save and load). | `CondRun.Step`, the present forcing tools' bodies |
| settle | Pauses and reads the speed back. Writes the last sample of every track. Reconciles the trace against state read directly (every alias: bound, spawned, alive, health, position, holder; a census of the stage's pawns). Waits for the writer to drain, then writes the closing record with the counts of rows written and dropped. | new, small |
| leave | Cleans the station, or keeps it when the plan says so. Puts back what the deviation record says can be put back, and names what cannot. Takes the run lock off. | the record (below) |

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

### The evidence contract (added after GPT's review)

A judge that reads only a trace is wrong whenever the trace is wrong or thin. GPT's failing case was exact: a sample
is taken, an act step then damages the actor, and the run stops on that tick; the trace holds the old health and the
judge passes. The contract below is what the trace must be before any verdict is allowed. The judge checks each point
and answers COULD NOT LOOK when one fails.

1. **Order inside a tick is fixed** (the table above): sample, conditions, end test, then act steps. A value changed by
   an act step is therefore sampled on the next tick at the latest, and a run cannot end before that sample.
2. **A first sample before any act, and a last sample after the pause.** Every track has both, each under a phase mark.
3. **Every record has a sequence number, its tick, and its phase** (in a tick, at end of tick, between ticks). Taps and
   tracks share one sequence. An act step writes its own record, so "the health changed after the act" is readable.
   **A tap record carries two sequence numbers: the one taken when the call was entered and the one taken when it
   completed, and the entry number of the call that enclosed it.** GPT's case: damage kills a pawn; the postfix of
   `Pawn.Kill` runs before the postfix of the enclosing `Thing.TakeDamage`, so records written at completion show the
   death before the damage. `before` and `after` in the judge compare entry numbers. A tap that has only a postfix
   today (`Thing.TakeDamage`) gets a prefix that takes the entry number.
4. **An alias names one object for the whole run.** Each record carries the alias and the object's own identity. When
   the object is replaced (a stack split, a pawn turned into a corpse, a load), the record of that event links old to
   new, and the alias does not move by itself.
5. **Loss is counted.** The closing record holds rows written and rows dropped per kind. A trace with no closing record
   is incomplete. A condition whose span holds a dropped row is not judged.
6. **A sampled value is an end-of-tick value, and says so.** A value that changes twice inside one tick shows only its
   last state. A condition that needs the middle of a tick is refused at compile time unless a tap serves it.
7. **The plan, the checker and their versions are part of the run.** A re-judgement adds a line to the run's history
   with the checker's version and what changed; it never replaces the first outcome. A re-judgement compares the
   staging, the act steps, the end and the observation list of the two plans, and refuses when any of them differs.
8. **Looking must not change the run.** A track that calls a property can fill a cache, draw a random number or
   change state, and the trace would then describe a run that the observer repaired (GPT's case: a lazy cache that
   ordinary play leaves stale). So: an acceptance track reads **fields**. A property or a method is read only from a
   reviewed, versioned list of readers. The kernel compares the random state before and after its sample phase on every
   tick; a draw inside the sample phase is a fault of the apparatus. The certification session runs one reference
   scene with the full tracks and with none, and the two outcomes and tap records must agree.

**What a re-judgement may and may not replace.** A repaired check judges a kept trace again when the repair changed only
how recorded facts are read: a comparison, a tolerance, a window, a count, the classifier. A repair to the staging, to
an act step, to the end condition, or to what is observed needs a new run, and the judge refuses the re-judgement by
naming the track or tap that the trace lacks. To make the first case common, every cast member gets the standard cast
tracks whether or not a condition names them: position, facing, job, toil, health summary with each injury, downed,
dead, mental state, carried thing, holder, faction, drafted. Storage is cheap; a rerun is not.

### Decision 2: ordinary execution first, and what "ordinary" means here

The kernel has three time modes. Each receipt names the one used.

| mode | how ticks run | evidence it gives | status |
|---|---|---|---|
| **PLAY** | The game's own loop, unpaused, at a named speed. `TickPost` evaluates and pauses on the end tick (exact, by the fact read above). | Ordinary play at that speed. The default for every acceptance scene. | New, small: the playtest runner's `speed` mode already does it without the exact stop. |
| **STEP** | Paused, `DoSingleTick` in slices, one slice per Unity frame inside a wall budget. | A model of play: the per-frame work runs once per slice, `Paused` reads true, the tick rate multiplier reads 0. | Exists (`run_scenes`, `safe_advance`). It is today's only mode. |
| **BURST** | STEP with a large budget and a pinned update rate. | The fastest; the furthest from play. | Later, and only if PLAY at the game's top speed is measured too slow. |

- **The end-of-tick hook** is the present `TickPost` on `DoSingleTick`. No second hook is added.
- **STEP is not thrown away, and it is not trusted.** The first measurement ticket runs the 2026-11-06 experiment at
  last: one scene, PLAY against STEP, traces compared tick by tick. Until a scene has that comparison on record, a STEP
  verdict reads "STEP, not compared" on its receipt, and the verdict ledger does not count it for a bar.
- **PLAY is not one thing, and it is not determinism (GPT).** Speed 1, speed 3 and Ultrafast put a different number of
  ticks between two frames, so anything that a mod does once per frame (a cache refresh, a draw-time update) meets the
  ticks differently. Kind A means a decisive opportunity under a named configuration, not a promise that every
  configuration agrees. So the **reference configuration** is PLAY at speed 1 with the camera on the station. A faster
  speed, and STEP, count for a bar only for a scene whose traces were compared with the reference and agreed. A
  comparison is valid for one key: the plan's hash, the loaded hashes of the mods that the scene touches, the
  companion's hash, the mod list and the arm. When any part of the key changes, the comparison is owed again. The
  measurement ticket compares speed 1, speed 3, Ultrafast and STEP, in that order of trust.
- **The camera.** In a test game the camera is the kernel's. At arm it is placed so that every station of the run is in
  view. The view rectangle and the zoom are a track for the whole run, so a camera that moved is a breach on the
  record and not an assumption. The update rate that the cast had (zoom level + 1) goes on the receipt. When the
  stations do not fit in one view, the plan may pin the rate: a prefix on `GenTicks.GetCameraUpdateRate` returns the
  declared value **for cast things only** and leaves every other thing, the green room included, as the game computes
  it. A pinned rate is a deviation on the receipt, and a run with a pinned rate is a configuration of its own: it
  counts for a bar only after the same comparison with the reference. The pin covers this one function; other code
  that reads the camera is not covered, and the receipt says so.
- **Staying alive.** PLAY needs nothing. STEP yields every frame already and reports "no new frame in 15 s" as a
  stall `[READ: SceneFrameStallMs]`.
- **Long scenes.** `jawa/run_until` returns a request id at once when the tick limit is over a threshold. The run
  goes on inside the game (driven per frame by a hidden `MonoBehaviour`, the playtest runner's pattern). The receipt
  core and the trace are files; the session's status reads the state. A caller that dies leaves a paused game and a
  session that `scene.attach` takes over.
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
  on the list is refused by name. A property is treated as a method: in an acceptance run it is read only when it is on the list (point 8 of the
  evidence contract). In the exploring layer, any property may be read, as today.
- **Rebinding.** A track re-resolves from its root every tick when any link is a replaceable object (a job, a comp
  list); the cost is measured per run and shown (`cost` exists in the result today).
- **The flight probes** `pawn.flight.*` and `pawn.anim.*`, which the first version refused by name pending the flight
  ticket: state, lerp tick, the graphic state's name and `texPath`, facing.

### Decision 4: taps, and the tap certificate

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
| reservation made and refused | tap | `ReservationManager.Reserve` (both results) | new |
| mental state attempt, started or not | tap | `MentalStateHandler.TryStartMentalState` | new |
| quest registered | tap and gate | `QuestManager.Add` | new |
| fire started, with instigator; explosion, with instigator | tap | `FireUtility.TryStartFireIn`, `GenExplosion.DoExplosion` (names to confirm at build) | new |
| letter, message | tap | `LetterStack.ReceiveLetter`, `Messages.Message` | new |
| window opened | track of the window stack per frame while a run is live | none | vitals reads the stack today |
| weather, game condition, temperature, hour, camera | track | none | new, cheap |
| sound asked, effect asked | tap, off by default | `SoundStarter.PlayOneShot` | later |

**The proof that a tap is not blind: a certificate made off the stage.** My first draft ran a "canary rite" at every
arm: real engine acts on a canary thing and pawn, inside the scene's own game. GPT showed three faults in it. It did
not exercise what it claimed (it reserved a cell successfully while the tap must also see a refusal; it never touched
the mental, quest, letter, message, fire or explosion taps). A route that the canary took proves that route only. And
the rite itself spends thing ids and random numbers and gives a pawn a job in the game that the scene is about to use,
so it disturbs the very run that it certifies. The repair:

- **A certification session**, in a disposable game, once for each pair of (companion build, mod list). A fixed suite
  of route fixtures performs every tapped act by its real engine routes, with a positive and a negative case each
  (a reservation made and one refused; a mental state started and one refused; an incident fired and one held; a quest
  registered; a letter; a message; a fire lit by a pawn and one by a thing; an explosion; a death by damage and one by
  a hediff; a pawn that arrives by spawn, by drop pod and by a load). The suite also plants a blind tap (one hook
  taken off) and must report it. Its result is a **tap certificate**: for each tap, the routes shown, the routes not
  shown, and every other mod's patch on the same method (from Harmony's patch info, which `jawa/harmony_patches`
  reads today), because a foreign prefix can skip the original. The certificate is keyed by the companion's hash, the
  mod list's fingerprint, the hash of that patch inventory, and a hash of the settings of every mod that has a patch
  on a tapped method (GPT: a foreign prefix can skip the original only when one of its settings says so; the patch
  list does not change).
- **At arm, no gameplay act.** The kernel checks only: the certificate's key equals the loaded identity; our patch is
  on each tapped method and the foreign patches are the certified ones; the routes that the scene's conditions need
  are on the certificate's "shown" list; one marker row goes through the writer and comes back acknowledged. A tap
  with no valid certificate is COULD NOT ARM for a scene that needs it.
- **A witness during the run.** Where a tap has a prefix, the prefix counts entries and the postfix counts records. An
  entry with no record (the original was skipped, or the postfix did not run) is counted on the receipt, and it voids
  that tap's coverage for the run.
- **The limit, stated.** No check at arm can prove that another mod's prefix will act in this run as it did in the
  certification session. Where a scene's verdict rests on "this event did not happen" and the tapped method has a
  foreign prefix, the receipt marks the absence as "not provable here", and the judge does not use it to excuse or to
  convict.
- **Silence is still not proof.** Each tap states the routes it covers. The settle phase reconciles the trace against
  state. An unexplained difference is COULD NOT LOOK. "No event" means "nothing happened" only on certified routes with
  a clean reconciliation; an event that came and went inside one tick on an uncertified route stays invisible, and the
  receipt's coverage lines say which routes those are.

### Decision 5: sent programs

No script engine is added. The exploring layer keeps what it has: the 427 tools, `jawa/static_call` (TEST only), and
`jawa/cond_eval`. A test pilot who needs new logic in the game writes a public static method in a C# file of the
mod's PROOF build or of the companion, as today.

**No plug-in attribute is built.** A probe is a field path (private fields and statics included) or a property from
the reviewed list (`contracts/read.md`). A fixture is Python (`s.stage`, or a fixture save). A value that no path
reaches gets a trace point in the mod (decision 8). A call of a PROOF-build method goes through `s.raw` and marks the
run EXPLORED, so it cannot be evidence for a bar.

`[RMTest]` scenes stay valid as an exploring tool. Their rows are never a bar's
evidence while they need the PROOF build.

### Decision 6: pixels without his camera

**Keep "move and restore inside one step"; build no second camera.** The present off-screen capture already points the
main camera at the rectangle after `Update`, renders to a texture, and restores it before the frame is shown, with the
view-rectangle postfix that makes the game submit the draws `[READ: JawaBenchArtboardTools.cs lines 10 to 20]`.

- On a test game the camera belongs to the kernel, so nothing is owed.
- On ArchBig the capture is allowed only while his hold is off (the hold guards a look). He would notice nothing on
  screen, because the swap happens between the update and the present of one frame `[GUESS 80%: no visible flicker;
  the map's section meshes for the other view are regenerated in that frame, which can cost a frame-time spike that he
  could feel as one hitch]`. In sitting mode it is refused.
- A true second camera would also need a second cull and draw submission for dynamic things, which the engine does per
  frame for one view only `[READ: the same header]`. That is a large build for no gain on test games.

### Decision 7: the station fence

**There is no fence, because there are no bystanders on the stage.**

- A test game runs with two maps. The **green room** is the map where the standing test colony lives: fed, rested,
  drafted, needs held. It exists so that the game has free colonists (the engine starts its game-over countdown when the
  player has none: `GameEnder.gameEnding` `[READ: the field, in JawaBenchVitals.cs; the exact rule: GUESS 85%]`). The
  **stage map** holds stations and cast, and nothing else: no colonist, no animal, no wild spawn (the spawners are held
  for that map), bare ground of one terrain, no roof, no plant.
- A scene that needs a colonist casts one. A cast colonist is built for the scene and removed at clean.
- **The stage is chosen by what the claim needs, not by what is cheap (GPT; my first draft chose a pocket map first, by
  cost).** A scene states `needs["map"]` in `scene.open`:
  - `settlement` (the default): the stage is an ordinary settlement map of the player's on a temperate tile, with map
    edges, a home status and normal incident targets. A raid arrives at an edge as it does in play.
  - `pocket`: allowed only for a claim that needs no map edge, no home status, no incident and no sun or weather of a
    tile. It buys a fixed outdoor temperature and a cheap fresh map per scene.
  - `colony`: the scene runs in a real colony (the full-list walks; below).
  The receipt names the map kind. **A result on a stage is evidence for the claim as staged.** Whether it carries to a
  real colony is shown, per bar, by at least one scene of that bar on a `colony` map (the walk), not assumed. The
  colony scene must reach the same exposure as the staged one; a colony scene about something else transfers nothing
  (GPT's case: a branch taken only above five free colonists). A bar whose behaviour can depend on colony size, wealth
  or a map-wide state either has such a scene or says in its text that the claim is the staged one only.
- The stage is not free isolation. The green room still ticks, and the world, the storyteller and the one random
  stream are shared. The calm profile holds or watches those; the stage removes only what stands on the same map.
- One trap, read in the code: an incident whose def requires colonists on the target map "succeeds" without running
  when the map has no free colonist `[READ: JawaBenchAwareness.cs header, IncidentWorker.TryExecute]`, and the incident
  journal's row (`returned`, `outerBodyRan`, `pawnsSpawnedDuring`) tells "called, not fired" from "fired". RaidEnemy is
  not such an incident: at a stage with no colonist it fires, and its raiders arrive `[MEASURED 2026-11-24, ArchBig,
  prove_stage_map.py R4: 6 raiders, the journal row agreed]`. A raid scene casts its defenders because the claim is about
  a defended colony, not to make the raid fire. A raid left to the worker draws its strategy (StageThenAttack stands
  under a Defend duty first `[MEASURED, the same run]`), so the scene fixes the strategy and the arrival mode
  (`jawa/fire_raid strategy= arrivalMode=`) and the points; the opportunity conditions name "raiders spawned at an edge
  and hold an assault duty". A raid whose raiders find no way in is a failed opportunity on the record.
- **Scenes on his full-list colony** (the walks) cannot move the colony. There the bystanders are held by means that
  are per pawn: an allowed area that excludes the stations for each colony pawn and animal, and the scene's things set
  forbidden. These are precautions and not isolation: an area does not bind a pawn in a mental state, in combat or
  under a forced job, nor a mod's own movement. So the watchers run, any non-cast thing that touches a station makes
  the affected run UNRESOLVED or ENVIRONMENT FAULT by the classifier, and the receipt says "shared map".

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
- A "mod says" record is evidence of a branch only. `scene.contract` refuses a success condition that stands on it alone
  (pass one's rule).

This adds test-only code to shipped mods. Pass one sent that to the Conductor (allow, recommended). I agree: the code
is inert when no kernel is present, and it is the only way to see why a giver refused.

### Decision 9: where the receipt, the trace and the keeper saves live

Under the agent storage root (on Archmagi `D:\ClaudeWork`), never in the repo:

```
<root>\rimmandrake\scenes\<game name>\<yyyymmdd>\<run id>\
    contract.json        the scene's contract, with its hash; beside it the commit hash of the script's clean tree
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

**The mod keeps a list of mutants; the program draws; an overlay or a build applies.**

- Each mod has `design/concepts/<Mod>/version/mutants.json`. A mutant names the bar it should break and how it is
  applied. A **live mutant** is an overlay entry: a tuning value set to a wrong number, a formula slot replaced, one of
  our Harmony patches taken off, a settings switch flipped. A **compiled mutant** is a build flag in the mod's source
  that changes a branch, an order or a target. The builder writes the first mutants with the bars; the coverage judge
  adds more.
- **Both kinds are needed, and how many of each is unknown.** Live values cannot express a wrong branch, a wrong
  target, a wrong order, a stale cache, a life-cycle fault or a timing fault unless the mod has a switch for it. A
  list that holds only live mutants would make the scenes that guard tunable numbers look better tested than the rest.
  So each bar's mutants carry their kind, and a bar whose only killed mutants are value changes says so in the scene's
  history. Compiled mutants cost one restart each and are run in batches.
- "Shown both ways" for a scene:
  - the green run and the red run each start from **the same fixture state, loaded fresh** (the save that the scene
    driver already takes before a run), with the random state written back and each mod's reset digest equal, so wear
    from the first run cannot make the second one red;
  - the mutant is drawn for this scene by a seeded choice that the scene's author does not control;
  - the red run must show that the mutant **was used**, not only set: each mutant names its witness, which is a
    recorded fact that differs because of the mutant (the changed number in a damage record, a trace point at the place
    that reads the value, a call counter of the patch taken off). A read-back alone does not count: the mod may act on a
    value that it cached earlier (GPT's case). The scene's exposure condition must also hold as in the green run;
  - a bar's mutant list is reviewed by an agent that did not write the scene, and holds at least two mutants, so that
    the draw is a draw;
  - the red run's outcome must be MOD FAILURE on the condition that the mutant names. A red run that ends SUCCESS
    means "this mutant was not killed by this scene". It does not mean that the scene cannot fail;
  - the red run's receipt carries the stamp, so it can never be counted as a pass.
- **A process that ran a live mutant is tainted until it restarts** (the taint rule of `04_live_tuning.md`). The verdict
  ledger refuses, for a bar, any run whose receipt has the taint mark, not only a run with a live overlay. So mutant
  runs go at the end of a sitting, after every green run, or in a session of their own.
- A mutant that only switches the whole feature off is refused by the list's lint (pass one's warning).

## Where live tuning sits (`04_live_tuning.md` folded in)

The overlay is not a separate tool beside the kernel. It is one of four kinds of entry in the **deviation record**, the
one in-game record of everything that is not shipped play:

| kind of entry | examples | who writes it |
|---|---|---|
| calm control | incidents held, wild spawn held, weather forced, needs of the green room held | the calm phase |
| force | "rescuer: order through the giver (level 3)", "carrier: pinned" | the stage and act phases |
| overlay entry | a def field, a tuning point, a settings field, a formula slot, a patch switch | a plan's `overlay:` block, a sweep, a mutant |
| time and rate | mode PLAY, STEP or BURST; a pinned update rate; a named time compression | the arm phase |

What the four kinds share is the **record and the stamp**, not the way back (GPT: "unify the audit envelope, not the
rollback"). My first draft said "one restore". That was wrong: setting a number back does not undo the injuries that
the number caused, and a removed animal does not return. So every entry carries one of three classes:

| class | meaning | examples | how the game gets clean again |
|---|---|---|---|
| **PUT BACK** | a value was assigned; the old value is written back and read back | a settings field, a def field with a recipe, the weather lock, a switch, a pinned rate | the write-back, checked |
| **GIVEN BACK** | something was held aside and is returned with a stated correction | queued incidents (every absolute tick of an entry is moved by the time held: its fire tick and its retry window, or the entry would expire on return) | the return, checked; the correction is on the record |
| **NOT UNDONE** | an act with consequences | a job given, a pawn placed, ticks that ran, an animal removed, the hunger and the mental breaks that did not happen while needs were held, things made while an overlay was live, a patch that already acted on state | by how far it reached (below) |

A NOT UNDONE entry names how far it reached, because the way to get clean differs:
- **the station**: clean the station, or retire it;
- **the save** (the map, the world, the pawns): load the fixture save again;
- **the process** (a mod's static cache or counter, a patch taken off and put on, a def field): a load does not clear
  it. Only the mod's reset hook with an equal digest, or a restart of the game, does. The taint mark is the overlay's
  case of this; a non-overlay act that reached a mod's statics sets "process dirty" on the same footing.

A hold on needs is two entries: the hold itself (PUT BACK when released) and what did not happen meanwhile (NOT
UNDONE, the save).

- **The game owns the truth.** One call lists every live entry with its class and its before value. A crashed script
  leaves a known game.
- **Every receipt carries the whole record**, filled by the game. A scene cannot leave it out.
- **Leaving a run**: PUT BACK and GIVEN BACK entries are returned in reverse order and read back; a debt file is
  written before the first write and repaid at leave, at lease end and at the next start of the companion
  (pass one §10). A NOT UNDONE entry is handled by its reach, as above.
- **The stamp and the taint mark** are properties of the record: a receipt reads `overlay: none` only when no overlay
  entry is live, and `tainted: true` from the first overlay write until the process restarts.
- **A sweep is a Python loop over one script** with a different `s.act.tune` value in each pass; the repeated
  baseline, the shuffled order and the cold confirmation of the winner are the loop's.
- **The verdict ledger enforces the three rungs.** A stamped run is TUNED, never PASS.
- **Overlay entries arm on any game.** They are refused only while a canonical world save is loaded (the CAMPAIGN
  profile, as for `jawa/mod_settings_field set`), and while his hold guards a look `[READ: JawaBenchSafetyCore.cs]`.

The build order of `04_live_tuning.md` is kept inside the kernel's order: first `jawa/mod_settings_field` joins the
store (our settings are pokeable today), then def-field writes with recipes, then the sweep as a Python loop, then
export and the absorbed check, then tuning classes in the mods as each advances, then formula slots and patch
switches, then the load-time overlay. Mutants need only the first step for a settings switch, and the patch switch
for a patch.

## Creative removals: what else is forced or removed, and by what

The owner asked for creativity in removing variables. Beyond the three ideas at the top:

| variable | removed by | cost |
|---|---|---|
| Bystanders, haulers, drinkers, their deaths in long runs | the stage map holds only cast | one more map in a test game |
| Outdoor temperature drift | a pocket stage fixes its outdoor temperature by data, for claims that may use a pocket map; else the temperature is watched and the hour set | the claim is narrower on a pocket map |
| Wild plants, regrowth, animals arriving | bare stage, wild plant and animal spawners held for that map | none |
| Rain on a scene | the stage map's weather is forced by the engine's own forced-weather route and read back | none |
| The raid that will not come | the scene fires the incident through its own worker with exact parms (`fire_incident` exists), the gate allows that one incident only, and the tap proves "fired", not only "called" | none |
| The raider that will not choose | two scenes: the ordered act (kind A), and the choice as a budgeted kind B in side-by-side copies | pass one §5; unchanged |
| A wrong check | re-judge the kept trace, when the trace holds what the repaired check reads | zero game time in that case |
| A flaky scene that needs "the same moment again" | the keeper save and the random state, only for scenes in a hunt. These two do not give the same moment: runs from one save with the random state written back drifted within 51 ticks, in STEP as in PLAY (`experiments/play_vs_step_rand_draws.md`, 2026-11-24) | half a second per run in a hunt |
| The camera | held by the kernel on a test game; the rate is recorded or pinned | none |
| A stale build | the receipt's loaded-build hashes, checked in admit before a tick is spent | the sibling run builds it |
| Another mod's ticker | scenes run on the smallest mod list that holds the claim; the full list is a named, separate check | the tiers exist |
| An unknown influence | every run that ends UNRESOLVED keeps its trace and its keeper save, so the next step is a read, not a rerun | disk |

**What is deliberately not forced.** The decision that a scene claims to test stays with the mod (Minimum Force). The
kernel records the force level per actor on the receipt, and the lint refuses a scene whose entry line steps past its
own claim.

## What this design does not settle

- Whether STEP, or a fast PLAY speed, agrees with PLAY at speed 1 for our scenes. Measured on one scene on 2026-11-24
  (`experiments/play_vs_step_result.md`): no arm agrees, and PLAY at speed 1 does not agree with itself. Runs from one
  save with the random state written back draw differently within the first 22 ticks
  (`experiments/play_vs_step_rand_draws.md`).
- Whether the joined parts hold one life cycle under a kill, a cancel and a thrown tick. The first ticket's slice
  shows it.
- The cost of a second settlement map in a test game, and whether our mods' map components behave on a pocket map as
  on a settlement map `[GUESS 75% yes for ours]`.
- How many of each mod's faults a live mutant can express. Unknown; each mod's mutant list will show it.
- The replay rate. The keeper save and the divergence finder measure it when the first hunt needs it.
- The general window transcript and draw-submitted probes: later tickets, not designed further here.
- Droids, sound heard, taste: pass one's testing horizon stands.

## What GPT changed

Two rounds, both kept in `census_sources/`: `gpt_pass2_round1_prompt.md`, `gpt_pass2_round1_answer.md` (the first
attempt with web search ran out of time; its notes are `gpt_pass2_round1_partial_log.txt`), and
`gpt_pass2_round2_prompt.md`, `gpt_pass2_round2_answer.md`. GPT answered round 1 from the text and from recall, with
no web access; where it named an engine fact, I read the fact in the 1.6 source before I used it.

### Round 1: folded in

- **A stale sample could pass a broken run.** The first draft sampled, then fired act steps, and could stop on the same
  tick. Added: the fixed order inside a tick, the first and last samples, sequence numbers and phases, the closing
  record, and the rule that a run never ends on a tick in which an act step fired ("The evidence contract").
- **"No rerun for a wrong check" was an overclaim.** A re-judgement is sound only when the trace holds what the
  repaired check reads, and never for a repair of staging, acts, the end or the observation. The judge now refuses a
  re-judgement by naming what the trace lacks, the first outcome is never replaced, and every cast member gets the
  standard tracks so that more repairs can be re-judged.
- **The pause can be refused.** GPT found, from the public source, that the speed setter refuses the write when the
  player has no control. I read it (`TickManager.CurTimeSpeed`, `PlayerCanControl`). The admit phase and the settle
  phase now check it.
- **The canary rite was wrong.** It did not exercise the taps that it claimed to prove, and it disturbed the game that
  the scene was about to use. Replaced by a tap certificate made in a disposable session per companion build and mod
  list, with a check at arm that performs no gameplay act (decision 4).
- **"One restore" was wrong.** A value put back does not undo its consequences. The deviation record now has three
  classes (PUT BACK, GIVEN BACK, NOT UNDONE), and the taint mark is enforced by the verdict ledger.
- **"Shown both ways" needed more.** Green and red now start from the same fixture state loaded fresh; the red run must
  show that the mutant was reached; a red SUCCESS reads "this mutant was not killed"; compiled mutants are a kind of
  their own, and I withdrew "those are few", which had no evidence.
- **The stage map was chosen by cost.** Now by what the claim needs: a settlement map by default, a pocket map only
  for a narrow claim, and a result on a stage is evidence for the claim as staged, carried to a colony by a walk scene.
- **PLAY is not one configuration.** A reference configuration (speed 1, camera on the station); faster speeds and STEP
  count only after a comparison per scene; the camera is tracked for the whole run; the rate pin is scoped to the cast.
- **Way A's joining cost was understated, and Way C was painted worse than it is.** Added the run lock, the life-cycle
  risk, the fairer form of C, and the statement that the pick stands on one measured slice. The build order now starts
  with that slice.
- **The engine table read vanilla facts as universal.** Each row is now scoped to the vanilla source, and the taps and
  gates stand on the certificate, not on the table.
- **The build order** (see `06_build_order.md`): the first ticket became the life-cycle slice; the run plan was split
  from the staging ops; the taps were split by family; the game watcher and the minimum put-back moved before the
  staging ops; the mod hooks moved before the repeats; four acceptance tests that wrong code could pass were repaired.
- **The owner's page** (see `07_for_the_owner.md`): the overclaims were cut.

### Round 1: not taken, with the reason

- **"A fourth way (a transport-neutral library, an adapter for the present bridge, compiled fixtures, declared
  observation) may beat all three."** That is Way A as designed, said in other words: the kernel's cores do not
  reference the bridge's SDK, the present bridge is the adapter, and compiled fixtures are the plug-in route. I took
  its one new demand, the measured slice first.
- **"Missing owner decisions: spend and time caps, retention, the claim restrictions of forced scenes, test hooks in
  the product."** By the standing rule of this repo only five acts stay his (a live flight test, art he kept, his
  walk, a money spend, publication). None of these is one. No money is asked for. The Conductor decides them and
  tells him after; the page says so.
- **"Default every colony claim to a representative settlement map and admit other maps only with transfer
  evidence."** Taken for the map kind (settlement by default). Not taken for the cast-only stage: the census shows
  bystanders and leftovers as the cause of at least 23 spoiled records, and a claim about competition with bystanders
  can still ask for a `colony` map.

### Round 2: folded in

GPT judged five of the twelve round-1 repairs sufficient and seven partial. What I took from round 2:

- **Looking can change the run.** A property read every tick can repair a stale cache, and the trace would be
  perfect and wrong. Added point 8 of the evidence contract: fields by default, a reviewed list for anything else, a
  random-state check round the sample phase, and a with-and-without comparison in the certification session.
- **Record order of nested hooks.** A death was recorded before the damage that caused it. Tap records now carry the
  entry number, the completion number and the enclosing call; the judge's `before` and `after` use entry numbers.
- **The certificate named patches, not what they do.** Its key now holds the settings of every mod with a patch on a
  tapped method; the scene's needed routes are checked against the certificate; a run-time witness counts entries
  against records; and the design states what no check at arm can prove.
- **A red run did not prove that the mutant was used.** Each mutant now names a witness that differs because of it; a
  bar's list is reviewed by another agent and holds at least two.
- **A fresh load is not a full reset.** A NOT UNDONE entry names its reach (station, save, process); a held queue
  entry has every absolute tick moved, not only the fire tick; a hold on needs is two entries.
- **A comparison of arms had no expiry.** It now has a key and is owed again when the key changes.
- **"Only A and B allow the judge outside" was still false.** Corrected, and a compiled fixture now has a stated life
  cycle with no verdict of its own.
- **Transfer from the stage to a colony.** The colony scene must reach the same exposure, or the bar says that its
  claim is the staged one.
- **The build order:** the first ticket was still too big and is split into the slice and the life-cycle hardening;
  the gates are built before the certificate, and the calm profile after; the game watcher is before the first plan
  that changes a map; a bootstrap mode marks every run made before the certificate exists as counting for nothing; two
  planted faults that their tests could not catch got fixtures that do.
- **The owner's page:** the camera choice is withdrawn; "no bystander can die" was narrowed; the
  filmstrip choice asks only what is his (whether pictures of flight may be made), not whether to build it.

### Round 2: not taken, with the reason

- **"Split persistence from restoration into two separate fields on every entry."** Taken in substance as the reach of
  a NOT UNDONE entry. Not taken as a second axis on PUT BACK and GIVEN BACK entries: for those the reach is the value
  itself, and a second field would be filled with the same word every time.
- **"Choices 2 and 3 reserve 'his own game' beyond the five acts and need an authority."** The review was right. Nobody
  plays (owner, 2026-11-23), so both choices are deleted: a broken game is stopped at once on any game, and a test may
  remove things on any save that is not canonical.
