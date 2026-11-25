# Ticks, clocks and Verse.Rand: references for the next run (2026-11-24)

Item `RIMMANDRAKE_FIND_RAND_DRAWS_PARTING_RUNS_EVEN_STEP`. This page goes beside `play_vs_step_rand_draws.md`, which
holds the measurements. Its job is to help the next run find and remove the Rand draws that do not repeat, and to say
how time advances in RimWorld 1.6.

Tags:
- `[source read]`: I read it in the decompiled 1.6 tree `D:\ClaudeWork\rimmandrake\decomp\rw16\all`. Its
  `Assembly-CSharp.dll` md5 `bf39a6f68f2deda9b09d66f6ceffecf3` matches the DLL of the live game.
- `[online, unverified for 1.6]`: a web source says it, and I did not check it in the 1.6 code.
- `[guess ~N%]`: my estimate.
- `[measured]`: from `play_vs_step_rand_draws.md`.

The file paths below are relative to the decomp tree. No game was run for this page.

## 1. How time advances

### The frame loop
Each Unity frame runs `Root.Update` `[source read]`. In order:
1. `RealTime.Update`, then `LongEventsUpdate`.
2. `Rand.EnsureStateStackEmpty`.
3. The static caches and updates: portraits, attack targets, `Pawn_MeleeVerbs.PawnMeleeVerbsStaticUpdate`,
   `Storyteller.StorytellerStaticUpdate`.
4. `uiRoot.UIRootUpdate` (every window, the inspect pane, the gizmos and the tooltips).
5. `soundRoot.Update`.

`Root_Play.Update` adds `Game.UpdatePlay` and `musicManagerPlay.MusicUpdate` `[source read]`. `Game.UpdatePlay` runs
these in order `[source read]`:
1. `LetterStack.OpenAutomaticLetters`.
2. `tickManager.TickManagerUpdate` (the ticks).
3. `LetterStackUpdate`, `WorldUpdate`.
4. `Map.MapUpdate` for each map.
5. `GameComponentUpdate`, `SignalManagerUpdate`.

`Map.MapUpdate` runs once per frame, not once per tick `[source read]`. It runs:
- the sky, the power nets and `regionGrid.UpdateClean`;
- `regionAndRoomUpdater.TryRebuildDirtyRegionsAndRooms`;
- the glow grid and `lordManager.LordManagerUpdate`;
- `postTickVisuals.ProcessPostTickVisuals`;
- the drawing, the weather and `flecks.FleckManagerUpdate`;
- `MapComponentUpdate`.

### TickManagerUpdate: frames to ticks (`Verse/TickManager.cs`) `[source read]`
- If `Paused`, it sets `ticksThisFrame = 0` and returns.
- It adds time to `realTimeToTickThrough`. It adds `CurTimePerTick = 1/(60 x TickRateMultiplier)` when `deltaTime` is
  within 10% of that value. Otherwise it adds the real `deltaTime`.
- It calls `DoSingleTick` while `realTimeToTickThrough > 0` and `ticksThisFrame < TickRateMultiplier x 2`.
- It stops early if the game pauses or the frame has used more than 45.454544 ms (1000/22, `WorstAllowedFPS = 22`).
  It sets a positive balance that is left over to 0. The game drops that time and does not make it up later.

These two caps explain the measured rates. Speed 3 (target 360) gave about 255 ticks per second. Ultrafast (target 900)
gave about 510 `[measured]`.

### Speeds and their tick rates (`TickRateMultiplier`) `[source read]`

| Speed | Multiplier | Ticks per second, target |
|---|---|---|
| Paused | 0 | 0 |
| Normal (speed 1) | 1 | 60 |
| Fast (speed 2) | 3 | 180 |
| Superfast (speed 3) | 6; 12 when `NothingHappeningInGame`; 18 with no maps | 360 |
| Ultrafast | 15; 150 with no maps or the `UltraSpeedBoost` tweak | 900 |

`ForcedNormalSpeed` (the `TimeSlower`) caps the multiplier at 1. The wiki agrees: 60 ticks per second at speed 1, x3, x6
and x15 `[online, unverified for 1.6]`.

### DoSingleTick order `[source read]`
1. `MapPreTick` for each map. This holds `pathFinder.PathFinderTick`.
2. `ticksGameInt++`. Under `fastEcology` it adds 2000.
3. `Shader.SetGlobalFloat(GameSeconds)`.
4. `tickListNormal.Tick`, then `tickListRare.Tick`, then `tickListLong.Tick`.
5. The date notifier, the scenario, `WorldTick`, the story watcher, the game ender and the storyteller.
6. The tales, the quests, `WorldPostTick` and `MapPostTick` for each map.
7. The history, `GameComponentTick`, `LetterStackTick`, `AutosaverTick` and the filth monitor.
8. `TransportShipManager`.

### What ticks when (`Verse/TickList.cs`, `Verse/Thing.cs`) `[source read]`
- The game keeps three lists, with intervals 1 (Normal), 250 (Rare) and 2000 (Long).
- A thing's bucket is `|thing.GetHashCode()| % interval`. `Thing.GetHashCode()` returns `thingIDNumber` (the base hash
  only while the id is -1). So a Rare thing ticks when `TicksGame % 250 == thingIDNumber % 250`.
- `RegisterThing` and `DeregisterThing` take effect at the start of the list's next `Tick()`.
- Under `DebugSettings.fastEcology`, every plant runs `TickLong` on every tick.
- `IsHashIntervalTick(t, n)` is `t.HashOffsetTicks() % n == 0`. `HashOffset(int)` is `HashCombineInt(id, 169495093)`.
- **New in 1.6: the interval tick depends on the camera.** `Thing.DoTick` calls `Tick()` on every tick. It calls
  `TickInterval(tickDelta)` when `tickDelta >= rate` or `GenTicks.IsTickInterval(UpdateRateTickOffset, rate)`. The rate
  is `Min(Max(UpdateRateTicks, 1), 15)`.
  - `Thing.UpdateRateTicks` is `GenTicks.GetCameraUpdateRate(this)`. It returns 15 when the map is not drawn, when the
    thing is not on `Find.CurrentMap`, or when `CameraDriver.InViewOf(thing)` is false. Otherwise it returns
    `(int)CameraDriver.CurrentZoom + 1`, that is 1 (Closest) to 5 (Furthest).
  - `Pawn.UpdateRateTicks` is 15 for animals and the camera rate for every other pawn. `Fire` is 15. `PawnFlyer` is 1.
    `Projectile` overrides it too.
  - So in a colonist's view, the camera decides on which ticks `TickInterval` runs, and with what `delta`. See suspect 1.
- 1.6 pathfinding runs on Unity jobs. `PathFinderTick` (in `MapPreTick`) finishes all the jobs from the last tick first
  (`ForceCompleteScheduledJobs`, `JobHandle.CompleteAll`). Then it schedules this tick's work. A path is ready one tick
  later, at the same tick in every run. Wall time does not move it.

### What STEP does, and what it must imitate
Our STEP (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSceneTick.cs`, `StepFrame`) does three things:
1. It sets `CurTimeSpeed = Paused`.
2. It returns if `LongEventHandler.AnyEventNowOrWaiting`.
3. It calls `tm.DoSingleTick()` in a loop until 40 ms of wall time have passed (`StepFrameMs = 40`) `[source read]`.

That gives these differences from PLAY `[source read]`:

| | PLAY | STEP |
|---|---|---|
| `TicksThisFrame` | 1 or more | 0, because `TickManagerUpdate` returns at Paused. So `ProcessPostTickVisuals` returns at once (no breath puffs, footprints or wiggler). |
| Ticks per frame | about 1 at speed 1 | about 19 (480 ticks per second at 25 frames per second `[measured]`). Each tick gets 1/19 of the per-frame work: region rebuild, lord update, flecks, map and game components, mods' `Update` hooks. |
| Frame boundaries | depend on frame timing | depend on a wall-clock budget, so they fall on different ticks in each run. This is our own rule, not a bar. |
| `ForcePaused` | stops the clock | ignored. STEP checks it only at the start (`Refuse()`). |
| `CurTimeSpeed` inside a tick | the speed | `Paused` (0). `SubSoundDef.gameSpeedRange` defaults to 0..999, so sound still plays. Other tick code that reads the speed acts differently `[guess ~30% that one matters here]`. |

To imitate PLAY, STEP would need to:
- run `ProcessPostTickVisuals` with a `ticksThisFrame` equal to PLAY's;
- run per-frame work at PLAY's ratio;
- obey a forced pause.

A cheaper target is repeatability, not imitation. A fixed number of ticks per frame puts the frame boundaries on the
same ticks in each run. See section 4.

### The clocks and how to read each
| Clock | What it is | How to read it |
|---|---|---|
| `TickManager.TicksGame` (`ticksGameInt`) | ticks since the game began; saved | `Find.TickManager.TicksGame`, or `GenTicks.TicksGame` `[source read]` |
| `TicksAbs` | `ticksGameInt + gameStartAbsTick`; drives the date | `GenTicks.TicksAbs` `[source read]` |
| `TicksThisFrame` | ticks run in this frame (0 in STEP) | `Find.TickManager.TicksThisFrame` `[source read]` |
| `CurTimeSpeed`, `Paused`, `ForcePaused`, `TickRateMultiplier` | the speed and pause state | `TickManager` properties `[source read]` |
| `RealTime.deltaTime`, `realDeltaTime`, `frameCount`, `LastRealTime`, `UnpausedRealTime` | frame clocks | static fields and properties on `Verse.RealTime` `[source read]` |
| `Time.realtimeSinceStartup` | Unity wall clock. The sound slot gates read it. | Unity `[source read]` (the game's use of it) |
| `Time.time` | Unity frame time. The music reads it. | Unity `[source read]` |
| `Rand` `seed`, `iterations` | the global random stream | the private static fields; the plan reads `static:Verse.Rand.iterations` |

The calendar: 2500 ticks per hour, 60000 per day, 900000 per quadrum and 3600000 per year
`[online, unverified for 1.6]`. `GenTicks.TicksPerRealSecond = 60` `[source read]`.

## 2. Verse.Rand in one paragraph `[source read]`
`Verse.Rand` is one global static stream: `MurmurHash(seed, iterations++)`. Only the `Value` and `Int` getters increment
`iterations`, so a Harmony postfix on those two getters counts every draw. `StateCompressed` is private and packs
`seed | iterations << 32`. The `Seed` setter resets `iterations` to 0. `PushState()` saves `StateCompressed`.
`PushState(int)` saves it, then sets `Seed`. `PopState` restores it. The `*Seeded` helpers wrap their draw this way, so
they do not move the global stream. `Rand.EnsureStateStackEmpty` runs once per frame. The static constructor seeds from
`DateTime.Now`, but a save load and our `WriteRand` replace that seed.

## 3. Suspects for the extra draws in the first 22 ticks, ranked

What any suspect must explain `[measured]`:
- Both PLAY and STEP part.
- Most ticks draw the same count.
- A run that parts has drawn a few more: +6 by tick 1, +12 by tick 3.

One instrument tells all of them apart. It is the ticket's counter:
- a postfix on `Rand.Value` and `Rand.Int` that records the tick, whether `JawaBenchVitals.TickPre` has run without
  its `TickPost` (a static flag; it is cheaper than the `StackTrace` that `JawaBenchCalm.InTick` uses), and the
  caller's method (one `StackTrace` frame 2, or the deferred tracing of the Multiplayer mod);
- for ticks 0 to 30 of two STEP runs, then a diff of the counts per (tick, phase, caller).

The observations below are cheaper still, or they confirm one suspect after the counter.

| # | Suspect | Phase | Fits PLAY and STEP? | Confidence | Cheapest telling observation |
|---|---|---|---|---|---|
| 1 | **Camera-rate interval ticks (new in 1.6).** A colonist in view runs `TickInterval` every `CurrentZoom+1` ticks; one out of view runs it every 15. The view and the zoom come from the camera, which moves on real time: the dolly and zoom smoothing after a load, and the view rect at the window size. If the camera differs between runs, or a pawn crosses the edge of the view at a different moment, a pawn runs `TickInterval` on another tick, and its need, mood and MTB draws move. | in tick | yes | `[guess ~35%]` | Record each colonist's `UpdateRateTicks` and `Find.CameraDriver.CurrentZoom` as tracks (getters; they draw nothing) for ticks 0 to 30. Differing rates at the parting tick confirm it. To prove it, move the camera to the world view or off the colonists, so every rate reads 15. Then run the 3-run STEP oracle again. |
| 2 | **Sound draws behind real-time gates, with grain history kept on the def.** Each played sample draws its grain choice (`RandomizedResolvedGrain`, a rejection loop: `NeverTwice` and `NeverLastHalf` draw again until the grain differs from the history), the volume and the pitch: 3 or more draws, so two samples are about 6. Whether it plays depends on `SoundSlotManager.CanPlayNow` (`Time.realtimeSinceStartup`) and `SampleOneShotManager.CanAddPlayingOneShot` (same-def samples younger than 0.05 s of real time). The history (`recentlyPlayedResolvedGrains`, `lastPlayedResolvedGrain`) lives on the `SubSoundDef`, so it survives a save load and carries one run into the next. Sustainers draw on real-time schedules (`SubSustainer.SubSustainerUpdate`, `StartSample`, `SoundParamSource_Random`). Volume 0 does not skip a draw: no volume gate stands before the grain draw (`volumeMaster` is 0 in Prefs.xml). In STEP, about 19 ticks share 40 ms, so the 0.05 s window drops more samples. | in tick (one-shots from tick code) and per frame (sustainers) | yes | `[guess ~30%]` | A prefix and postfix on `SubSoundDef.TryPlay` that read `iterations` before and after, with the tick. Any count other than 0 at the parting tick confirms it. To prove it, wrap `TryPlay`, `SubSustainer.StartSample` and `SoundParamSource_Random` in `Rand.PushState()`/`PopState()`. Sound never feeds game state, so this is safe. |
| 3 | **Our own bridge, between `WriteRand` and tick 1, and the recorder.** `WriteRand` sets the state in the middle of a frame. The rest of that frame (UI, sound, music) and every later frame before tick 1 draw from the written stream. The track recorder reads pawn state from outside a tick, which can fill caches early (the class of fault that the Multiplayer mod patches: `SituationalThoughtHandler`, `PawnCapacitiesHandler.GetLevel`, `StatWorker.GetValue`). The calm profile runs `FramePre` on `Root_Play.Update` every frame. | between ticks | yes | `[guess ~15%]` | Read `iterations` in `TickPre` of tick 1 and compare it with the value written. A difference means draws ran outside a tick before tick 1. The per-phase column of the counter also shows it. |
| 4 | **UI and per-frame draws.** Inspect strings and gizmos of the selected thing (for example `GrowthUtility.GetInspectString`, `CompScanner`), `Pawn_MeleeVerbs.TryGetMeleeVerb` (it draws `Rand.Chance(0.04)`, and the Multiplayer mod patches it because UI calls it), tooltips under the mouse, `CompShield.Draw` (3 draws, not wrapped), `SnowGrid.CheckVisualOrPathCostChange`. The count changes with the number of frames per tick, the selection and the mouse. Weak fit: draws on every frame would part most ticks, and most ticks agree. | between ticks | yes | `[guess ~8%]` | The counter's between-ticks rows. To prove it, clear the selection (`Find.Selector.ClearSelection`) and close the windows before arming, then A/B. |
| 5 | **Post-tick visuals (PLAY only).** `ProcessPostTickVisuals` runs for pawns in the camera view. A breath puff (`FleckMaker.ThrowBreathPuff`) makes exactly 6 global draws. It needs a humanlike pawn standing at an ambient temperature below 0 and `(TicksGame + HashOffset) % 320` to fall in the frame's ticks. The downed wiggler and the water splashes draw too. It cannot explain STEP, which skips the whole method. | per frame | PLAY only | `[guess ~5%]` for the shared signature; higher for PLAY's extra parting | The map temperature (below 0 or not). The counter's caller column (`PawnBreathMoteMaker`). To prove it, wrap `Pawn.ProcessPostTickVisuals` in Push and Pop, as the Multiplayer mod does. |
| 6 | **Frame-boundary placement in STEP, with per-frame work that feeds ticks.** Region and room rebuild, `LordManagerUpdate`, the weather and fleck updates, and mods' `MapComponentUpdate` run between groups of about 19 ticks. The 40 ms budget puts those groups on different ticks in each run. | between ticks, felt in tick | STEP; PLAY has its own jitter | `[guess ~4%]` | Change STEP to a fixed number of ticks per frame. If the parting tick moves or goes away, this is the cause. |
| 7 | **Music and mods on the minimal list.** `MusicUpdate` draws a song interval and a song choice on `Time.time`. Its only gate is `disabled`, not the volume. The 26 mods may add their own Update or Draw draws. | per frame | yes | `[guess ~3%]` | The counter's caller column, filtered by assembly. |

The first two together are `[guess ~65%]`. Suspect 1 is the one that I did not expect before I read the 1.6 code.

## 4. What can stop the clock from outside (PLAY only, 3 of 21 runs)

STEP calls `DoSingleTick` directly, so it ignores `ForcePaused` and the speed. A PLAY clock stops for one of two
reasons `[source read]`:
- `curTimeSpeed` becomes `Paused`: `TickManager.Pause()`, `TogglePaused`, or our `Host.Pause`;
- `ForcePaused` is true: `WindowStack.WindowsForcePause` (any open window with `forcePause`),
  `LongEventHandler.ForcePause` (`AnyEventNowOrWaiting`), `TilePicker.Active`, the gravship cutscene or landing
  confirmation, or `MapGenerator.debugMode`.

Ranked for our case: the reference run and one speed-1 run stopped on tick 771, one speed-3 run on tick 1071, all with
the calm profile on.

| # | Cause | Confidence | The one read that confirms it |
|---|---|---|---|
| 1 | **A window with `forcePause` opens.** There are 54 such window classes. Some open with no click: `LetterStack.OpenAutomaticLetters` opens letters with `ShouldAutomaticallyOpenLetter` (`ChoiceLetter_BabyBirth`, growth moments); the Faction tick opens `Dialog_NamePlayerFaction` or `Dialog_NamePlayerFactionAndSettlement` (a `Dialog_GiveName`) at `TicksGame % 1000 == 200`; a mod can open a `Dialog_MessageBox`. The calm profile holds incidents, not windows. | `[guess ~45%]` | At the stall, read the list of `Find.WindowStack.Windows` with each window's type and `forcePause`. A naming dialog fits at most one of the two stop ticks (771 and 1071 are 300 apart, not 1000), so check `TicksGame % 1000` at the stall. |
| 2 | **Our own harness or bridge pauses it.** Another bridge call runs `Host.Pause`, the calm profile restores at the end of the lease, or `s.run`'s own pause path runs. The STEP loop sets `Paused` each frame anyway, so STEP would not show it. | `[guess ~25%]` | A Harmony prefix on `TickManager.TogglePaused` and the `CurTimeSpeed` setter that logs the tick and the stack. The stack names the caller in one run. |
| 3 | **`TickManager.Pause()` from a letter or game code.** `LetterStack.ReceiveLetter` pauses when `Prefs.AutomaticPauseMode >= letter.def.pauseMode`. Prefs.xml reads `MajorThreat`, and in Core only `ThreatBig` sets a pause mode that low, but a mod's LetterDef can. Other callers: `CompCerebrexCore`, `CompVoidNode`, `WorldRoutePlanner` (not on this map). | `[guess ~15%]` | The same `TogglePaused` prefix, or `Find.LetterStack.LettersListForReading` at the stall: the newest letter, its def, and its `def.pauseMode`. |
| 4 | **A long event.** `LongEventHandler.ForcePause` is `AnyEventNowOrWaiting`. Autosave queues one only after `AutosaveIntervalDays x 60000` ticks, and `ticksSinceSave` is not saved, so it is 0 after a load. Autosave cannot fire inside 1200 ticks. Another long event from a mod or a bridge call can. | `[guess ~8%]` | `LongEventHandler.AnyEventNowOrWaiting` at the stall. |
| 5 | **Pause on error.** `Log.Error` pauses when `DebugSettings.pauseOnError`. Prefs.xml reads `pauseOnError` False, so it is ruled out unless that setting changes at run time. | `[guess ~2%]` | `DebugSettings.pauseOnError` and the Player.log line at the stall tick. |

**The one instrument for all five:** when `s.run` first sees a still clock (before the 60 s cancel), read these:
- `CurTimeSpeed`, `Paused` and `ForcePaused`;
- each window type with its `forcePause`;
- `LongEventHandler.AnyEventNowOrWaiting`;
- the newest letter;
- the `TogglePaused` log.

## 5. How the Multiplayer mod got determinism, and what we can copy

The Multiplayer mod (rwmt/Multiplayer) runs lockstep. Every client runs the same ticks and compares random state.
`[online, unverified for 1.6]` for the whole section:
- **A random stream for each map.** `randState = HashCombineInt(map.uniqueID, World.ConstantRandSeed)`.
  `AsyncTimeComp.PreContext` runs `Rand.PushState()` and sets `Rand.StateCompressed = randState`. `PostContext` saves
  `randState = Rand.StateCompressed` and runs `Rand.PopState()`. The map's ticks draw only from their own stream, so
  any frame work (UI, sound, visuals) that draws from the global stream cannot reach them.
- **Its own tick driver.** `TickPatch` replaces `TickManager.TickManagerUpdate` (a prefix that returns false) and runs
  the ticks itself. `TickRatePatch` sets the rate.
- **A list of determinism patches** (`Source/Client/Patches/Determinism.cs`). It stops UI, camera and frame state from
  leaking into ticks:
  - `MoteMaker.MakeStaticMote` makeOffscreen and `MoteCounter.Saturated`;
  - `MapBrightnessTracker.Tick` deltaTime and `PawnTweener.TweenedPos`;
  - `Pawn_MeleeVerbs.TryGetMeleeVerb` and `Pawn.ProcessPostTickVisuals`;
  - `SituationalThoughtHandler`, `PawnCapacitiesHandler.GetLevel` and `StatWorker.GetValue` (UI fills the caches);
  - `DangerWatcher.DangerRating`, `WealthWatcher.ForceRecount`, `Zone.Cells`/`Plan.Cells`, `FastTileFinder.Query` and
    `UndercaveMapComponent`.
  
  I did not confirm whether it patches the 1.6 camera rate (`GetCameraUpdateRate`). The Multiplayer mod would need to.
- **Finding desyncs.** `DeferredStackTracing` postfixes the `Rand.Value` and `Rand.Int` getters and records the stack
  of each draw. `SyncCoordinator` compares the random state, the upper 32 bits, per tick between clients. Its wiki says
  that most desyncs come from interface actions that are not synced.

**What we can copy cheaply:**
1. **A tick-private stream** (about 20 lines in the companion). In `TickPre`, save the frame's `StateCompressed`, then
   write the tick stream's state. In `TickPost`, save the tick stream's state, then restore the frame's.
   - The scene arms the tick stream, not the global one.
   - This removes suspects 3, 4, 5 (in PLAY) and 7.
   - It does not remove draws made inside a tick whose count depends on real time or the camera (suspects 1 and 2).
2. **Wrap the sound draws** in `PushState`/`PopState`: `SubSoundDef.TryPlay`, `SubSustainer.StartSample` and
   `SoundParamSource_Random`. Sound never changes game state. This removes suspect 2.
3. **Pin the camera rate.** Patch `GenTicks.GetCameraUpdateRate` to return 15 (the off-screen rate), or keep the
   camera off the scene's pawns. This removes suspect 1.
   - It changes what PLAY at speed 1 would do with the camera on the pawns.
   - So the same pin must be on in the reference arm too. Whether a pinned reference still counts for a bar is a
     question for the owner, not ours to decide.
4. **A fixed number of ticks per STEP frame**, in place of the 40 ms budget. This removes suspect 6.
5. **The Multiplayer mod's draw tracer**, as the instrument: the ticket's experiment.

**Affordability:**
- **Full determinism is not affordable** `[guess ~80%]`. That means every run of every scene alike on every tick, in
  every arm, with the owner's mod list.
  - The Multiplayer mod spent years on it.
  - It patches dozens of vanilla sites.
  - It still meets desyncs from other mods.
  - Our full list has hundreds of mods.
- **"Repeatable on the minimal list, for one scene"** looks affordable `[guess ~60%]`: copy items 1 to 4 and see the
  ticket's oracle (three STEP runs with equal `iterations` on every tick) go green.
- **A weaker property that would serve a test bar:**
  - **Same outcome class:** for each run, a verdict in a small set, such as "colonists finished the job, no error,
    no death". Every run must land in the expected class. It needs no determinism and fits kind B scenes.
  - **Statistical equivalence:** n runs of each arm, with one number per run (for example ticks to finish the job).
    The arms must agree within a stated band by a two-sample test, such as a permutation test, at a stated n and
    power. That is the honest bar for "STEP stands in for PLAY at speed 1", because PLAY at speed 1 does not repeat
    either.
  - I would use the outcome class as the bar now, and statistical equivalence for the faster-driver question.

## 6. Sources

Code, read in the decompiled 1.6 tree (`D:\ClaudeWork\rimmandrake\decomp\rw16\all`):
- `Verse/TickManager.cs`: the multipliers, `TickManagerUpdate`, `DoSingleTick`, `Pause`, `ForcePaused`. It is the
  reference for how time advances.
- `Verse/TickList.cs`, `Verse/Thing.cs` (`DoTick`, `GetHashCode`, `UpdateRateTicks`), `Verse/GenTicks.cs`
  (`GetCameraUpdateRate`), `Verse/Gen.cs` (`IsHashIntervalTick`, `HashOffset`), `Verse/Pawn.cs`, `Verse/CameraDriver.cs`
  (`CurrentZoom`, `InViewOf`): what ticks when.
- `Verse/Rand.cs`: the stream, `StateCompressed`, Push and Pop, `EnsureStateStackEmpty`.
- `Verse/Root.cs`, `Verse/Root_Play.cs`, `Verse/Game.cs` (`UpdatePlay`), `Verse/Map.cs` (`MapUpdate`, `MapPreTick`): the
  frame order.
- `Verse/PostTickVisuals.cs`, `RimWorld/PawnBreathMoteMaker.cs`, `RimWorld/FleckMaker.cs`, `Verse/GenView.cs`: the visuals
  in PLAY only.
- `Verse.Sound/SubSoundDef.cs`, `Verse.Sound/Sample.cs`, `Verse.Sound/SoundStarter.cs`, `Verse.Sound/SoundSlotManager.cs`,
  `Verse.Sound/SampleOneShotManager.cs`, `Verse.Sound/SubSustainer.cs`: the sound draws and their real-time gates.
- `RimWorld/MusicManagerPlay.cs`: the music draws.
- `Verse/PathFinder.cs`, `Verse/PathRequest.cs`, `Verse.AI/Pawn_PathFollower.cs`: 1.6 pathfinding, one tick of latency.
- `Verse/LetterStack.cs`, `Verse/LetterDef.cs`, `Verse/WindowStack.cs`, `Verse/LongEventHandler.cs`,
  `RimWorld/Autosaver.cs`, `Verse/Log.cs`, `RimWorld/Faction.cs`, `Verse/DebugSettings.cs`, `Verse/PrefsData.cs`: what
  pauses the clock.
- Game data `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\Misc\LetterDefs\StandardLetters.xml`:
  which letters set a pause mode.
- The game's `Prefs.xml` (`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Prefs.xml`),
  read only: the volumes, `runInBackground`, `pauseOnLoad`, `automaticPauseMode`, `pauseOnError`, `devMode`.
- Ours: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSceneTick.cs` (STEP, `WriteRand`, `Refuse`) and
  `JawaBenchCalm.cs` (the calm profile's patches).

Online `[online, unverified for 1.6]`:
- https://github.com/rwmt/Multiplayer: the Multiplayer mod's repository; start here.
- https://raw.githubusercontent.com/rwmt/Multiplayer/master/Source/Client/AsyncTime/AsyncTimeComp.cs: the per-map
  random stream (`PreContext` and `PostContext`). This is the pattern for a tick-private stream.
- https://raw.githubusercontent.com/rwmt/Multiplayer/master/Source/Client/Patches/Determinism.cs: the list of vanilla
  sites that leak frame state into ticks. Use it as a checklist.
- https://raw.githubusercontent.com/rwmt/Multiplayer/master/Source/Client/Patches/TickPatch.cs and
  https://raw.githubusercontent.com/rwmt/Multiplayer/master/Source/Client/AsyncTime/TickRatePatch.cs: how it replaces
  the tick driver.
- https://raw.githubusercontent.com/rwmt/Multiplayer/master/Source/Client/Desyncs/DeferredStackTracing.cs and
  https://raw.githubusercontent.com/rwmt/Multiplayer/master/Source/Client/Desyncs/SyncCoordinator.cs: the draw tracer
  and the per-tick comparison. They are the model for the ticket's counter.
- https://github.com/rwmt/Multiplayer/wiki/Desyncs and https://github.com/rwmt/Multiplayer/wiki/Async-time: why
  desyncs happen (mostly interface actions), and the time model for each map.
- https://rimworldwiki.com/wiki/Time: ticks per second, ticks per hour, day, quadrum and year, and the speed multipliers.

These sites failed to fetch, so I used none of them: the rimworldwiki `Options`, `Game_speed` and
`Modding_Tutorials/Things` pages (404 with Retry-After), the ludeon.com forums (403), rwmt.github.io/Multiplayer (404)
and rimworldmodding.github.io (404).

## 7. What this page could not verify
- That the Multiplayer mod's code above is its 1.6 code. I read the master branch through a fetch agent, and I did not
  check the date of each file.
- Whether a fixture save restores the camera to the same position and zoom on each load, and how long the smoothing
  takes to settle. That decides how strong suspect 1 is. Recording the camera as a track answers it.
- Which tick code reads `CurTimeSpeed` or `Paused` (STEP runs its ticks with `Paused`). I did not sweep for it.
- The exact draw count of each `SubSustainer.StartSample`, and which sound defs use `NeverTwice` or `NeverLastHalf`.
- The ambient temperature of the fixture map (the breath-puff condition).
- Every cause in sections 3 and 4 needs the live game to confirm. Each row names the read.
