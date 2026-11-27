# Which Verse.Rand draws part runs from one save and one random state (2026-11-27)

Item `RIMMANDRAKE_FIND_RAND_DRAWS_PARTING_RUNS_EVEN_STEP`, after `play_vs_step_rand_draws.md`. Game ArchBig, on the
fixture's own 26-mod list (written from `rm_fixture_play_vs_step.rws` with `modsconfig_from_save.py`), companion of
`521f3e18da`. Plan `src/RimMandrake/Utils/scene_compare_plans/colony_drift_rand.py`, STEP arm, the save loaded fresh and
the arming run's random state written back before every run. Instrument: `jawa/rand_trace`
(`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchRandTrace.cs`), driver `src/RimMandrake/Utils/rand_trace.py`,
verdict `src/RimMandrake/Utils/rand_trace_verdict.py`.

## The instrument could see

In all nine runs, every traced tick read `seen`: the draws that the postfix counted at depth 0 equal the stream's
`iterations` delta of that tick, and no tick and no gap between ticks moved the stream past the hook `[measured]`. The
postfix on `Rand.Value` and `Rand.Int` covers every draw: these two getters are the only code that moves `iterations`
in 1.6 (`iterations++` appears in `Verse/Rand.cs` lines 35 and 51 only) `[source read]`. 0 faults, 0 draws from another
thread.

## What was measured

1. **No draw falls between ticks in STEP** `[measured]`. All depth-0 draws were inside `DoSingleTick` (phase `tick`);
   phases `pre` and `frame` drew 0. So UI, sound and visuals between ticks do not part STEP runs.
2. **The first parting draw is the fish shadow fleck** `[measured]` (`rand_trace_runs.json`: 3 runs, 40 ticks;
   `rand_trace_runs_300.json`: 3 runs, 300 ticks). In every pair, the first parting tick (9 and 13 in the first set, 3 in
   the second) holds exactly these rows, and every later difference follows from them:
   - `Verse.GenCollection.RandomElement < Verse.FishShadowComponent.FindFishFleckLocation < FishShadowComponent.MapComponentTick`: 1 draw
   - `Verse.FishShadowComponent.SpawnFishFleck < FishShadowComponent.MapComponentTick`: 4 draws
   - `Verse.FleckStatic.Setup < FleckThrown.Setup < FleckSystemBase.CreateFleck`: 1 draw

   That is 6 draws for each fleck, which matches the "+6 by tick 1" of `play_vs_step_rand_draws.md`.
3. **Why the fish fleck moves between loads** `[source read]`. `FishShadowComponent.MapComponentTick` (Odyssey) fires for a
   water body on `GenTicks.IsTickInterval(body.GetHashCode(), …)`. `WaterBody.GetHashCode()` folds in
   `base.GetHashCode()`, the object's identity hash, which the runtime assigns anew at every load. So the tick on which
   each body throws a fleck differs from load to load, and so do the draws. Nothing about frame timing decides it.
   The pawns' own hash ticks do not part: `Thing.GetHashCode()` returns `thingIDNumber`.
4. **The fix experiment, both ways** `[measured]` (`rand_trace_runs_isolated.json`, 3 runs, 300 ticks, with
   `isolate=Verse.FishShadowComponent:MapComponentTick`: the tracer wraps that method in `Rand.PushState`/`PopState`, so
   its draws leave the global stream still):
   - with it, the three runs draw the same count from the same callers, and `iterations` is equal, on ticks 3 to 52.
     Then all three part on tick 53 (see the next point);
   - without it (`rand_trace_runs_300.json`, the same build and session), the runs part on tick 3.
5. **A second cause parts the runs on tick 53, and it is not a draw** `[measured]`. On tick 53 the isolated runs differ in
   `RimWorld.Pawn_FilthTracker.Notify_EnteredNewCell < Pawn_PathFollower.TryEnterNextPathCell < PatherTick < Pawn.Tick`
   (18 draws against 15: one pawn enters a cell on another tick, 3 draws for each entry) and in
   `RimWorld.WildPlantSpawner.WildPlantSpawnerTickInternal` (7 against 8). Every draw before tick 53 was equal in count
   and caller, from one written-back state, so the values drawn were equal too. An input that is not a draw parts them.
   It is not yet found. Three theories were tested and are false:
   - the 1.6 asynchronous path jobs resolve on a tick that frame timing sets: false, because `PathFinder.PathFinderTick`
     calls `ForceCompleteScheduledJobs` and resolves each request on the next tick `[source read]`;
   - an identity hash on a pawn sets a tick interval (`PawnWaterRippleMaker`): false, because `Thing.GetHashCode()` is
     `thingIDNumber` `[source read]`;
   - the camera sets the rate of `TickInterval` (`GenTicks.GetCameraUpdateRate`, the lead suspect of
     `tick_and_rand_references.md`): the `world.camera` track is equal in all three runs `[measured]`, so the rate cannot
     part them, unless a frame-time read inside the rate does `[guess ~25%]`.

## Next theories for tick 53 (GPT, 2026-11-27; hypotheses, none tested)

From `gpt_consult.py` over this page. The plant draws may be downstream: `WildPlantSpawner` runs in `MapPostTick`, after the
pawn ticks.

1. **Live inputs race inside the path jobs.** `PathFinder.ScheduleBatchedPathJobs` schedules a managed
   `PathGridDoorsBlockedJob.Execute` that reads live pawn positions, jobs and doors on a worker thread while the tick goes
   on. Probe: run that job at once at scheduling time (the path still delivered on the next tick) and compare again.
2. **Random toils built before the write-back.** `JobDriver.ExposeData` (PostLoadInit) calls `SetupToils()`; some
   `MakeNewToils` draw a wait. Probe: at arm, compare (pawn ID, driver type, each toil's `defaultDuration`).
3. **Pawn tick order.** `TickList` appends `thingsToRegister`; the order inside a bucket may differ by load, and
   `PatherTick` collision checks see earlier pawns. Probe: the ordered pawn IDs entering `Pawn.Tick`, from tick 1.
4. **Path restoration at load.** `Pawn.PostMapInit → TryResumePathingAfterLoading → StartPath` rebuilds `curPath`. Probe:
   after load, compare each moving pawn's (Position, nextCell, nextCellCostLeft, nextCellCostTotal).
5. **Frame-counted job-loop guard while paused.** `Pawn_JobTracker.StartJob` counts `jobsGivenThisTick` by
   `RealTime.frameCount`. Probe: whether its over-10 branch runs before tick 53.

## What it decides

- **One save and one written-back random state cannot repeat a run on a map with fish water.** The fish fleck parts
  every STEP run within the first fleck interval; PLAY runs the same tick code, so it parts there too `[guess ~85%]`.
- **Holding the fish fleck off the global stream is a known, cheap part of the fix**: it moves the first parting from
  tick 3–13 to tick 53. It is not the whole fix. The cause on tick 53 is the next question, and until it is found a
  scene that needs "the same moment again" stays kind B in every arm, and no faster arm can be shown equal to PLAY
  speed 1.
- The tracer is the instrument for that next question: `jawa/rand_trace action=arm window=<ticks> isolate=<…>`,
  then the depth-0 rows of the first parting tick.

## Reading it again

```
python3 src/RimMandrake/Utils/rand_trace_verdict.py report design/specs/2026-11-23-bridge-v2/experiments/rand_trace_runs.json
python3 src/RimMandrake/Utils/rand_trace_verdict.py report design/specs/2026-11-23-bridge-v2/experiments/rand_trace_runs_isolated.json
python.exe src\RimMandrake\Utils\rand_trace.py --game ArchBig --arms step --n 3 --window 300 [--isolate Verse.FishShadowComponent:MapComponentTick] --out <json>
```

The game must load the fixture's own list: `rm_fixture_play_vs_step` records 26 mods, and a game that lacks one refuses
the load.
