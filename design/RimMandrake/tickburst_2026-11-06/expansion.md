# TICKBURST_PROVE_MANY_TICKS_ONE_FRAME: expansion

Status: design expansion, 2026-11-06, BENCH builder. Nothing here is built or live-tested. Next step: GPT skeptical
review (`gpt_review.md` beside this file), then a reframe into tickets.

Owner's words that started it: "6) weird, but cool... let's do the experiment". Then: "Anything I left out, capture
those in TICKBURST_PROVE_MANY_TICKS_ONE_FRAME ... after you do a similar expansion out followed by a
reframe/enhancement/skeptical review". The "left out" items are the leftovers of the bridge-conditions design
(`design/RimMandrake/bridge_conditions_2026-11-06/draft.md` §6 and `gpt_enriched.md`). They are in §8 here. The
condition primitives themselves belong to that spec and are not redesigned here.

## 0. Headline correction: most of the burst already exists

The item as filed says "today bridge stepping is one tick per frame, 60-280 ticks/s". That is true of
`rimworld/step_game_ticks` (RimBridgeServer.dll's own description says "Each requested tick is executed on a separate
Unity update frame"; `fast_testing_2026-11-05/scored.md:33`). It is **not** true of `jawa/safe_advance`:

- `JawaBenchVitals.cs:675-737` (`JawaBenchSafeAdvance.Frame`). Once per Unity frame, while the run has ticks left,
  it loops `for (i < chunk) tm.DoSingleTick()`. Chunks are ≤60 ticks (`V.MaxChunk = 60`,
  `JawaBenchVitalsCore.cs:43`). It checks the vitals latch between chunks and stops when the stopwatch passes
  `frameBudgetMs` (default 40 ms, clamped to 5-200; `JawaBenchVitalsTools.cs:171-208`). A frame can therefore run many
  chunks: up to roughly 40 ms divided by the tick cost, in ticks.
- `JawaBenchFlowWorksPlaytest.cs:84-114,512` has its own "batch" driver: pause, then `DoSingleTick` inside a per-frame
  budget (default 50 ms).
- The Python side already prefers it. `_BridgeBase.ticks` (`validation_core.py:147`) calls `clockgate.advance_chunk`,
  which calls `jawa/safe_advance` when the companion has it and falls back to `step_game_ticks` otherwise
  (`modcheck/clockgate.py:289-300`). Calls go in chunks of `SAFE_CHUNK_MAX = 2500` (`clockgate.py:131`).
- Vanilla also runs many ticks in one frame. `TickManager.TickManagerUpdate` (decompiled `Verse/TickManager.cs:318-355`)
  runs ticks while `ticksThisFrame < TickRateMultiplier * 2` and the frame has spent less than 45.45 ms. Ultrafast is
  multiplier 15, so up to 30 ticks per frame. With `UltraSpeedBoost` or no maps it is 150, so up to 300 ticks per
  frame. Superfast is 6, or 12 when "nothing happening", so up to 12 or 24.

So the experiment the owner approved has two parts. Part one is a **measurement**: what ticks/s does safe_advance
actually reach, against step_game_ticks and against vanilla Ultrafast, on the minimal list and on the full list? Part
two is a **trust proof**: do proofs give the same verdict whichever way they are stepped? A new stepper is not
justified until those numbers exist. The design question is how far to raise the per-frame budget, and how to guard
the per-frame differences that grow with it.

Census, which is a lower bound because it counts lines, not live calls: 259 `step_game_ticks` lines in 139 Python files
under `src/`, against 153 `safe_advance` lines. Some of the 259 are fallback branches (clockgate). The rest are direct
callers that run at about 60 ticks/s and are the real migration target (§6).

## 1. Mechanics: what one burst frame is

The Unity frame order, as far as we know it. `Root_Play.Update` calls `Game.UpdatePlay` (decompiled `Verse/Game.cs:660`):

1. `LetterStack.OpenAutomaticLetters`
2. `TickManager.TickManagerUpdate`. This does nothing while Paused. safe_advance keeps the game Paused, so vanilla
   ticks nothing here.
3. `LetterStackUpdate`, `World.WorldUpdate`, each `Map.MapUpdate`, `GameInfoUpdate`, `GameComponentUpdate`,
   `SignalManagerUpdate`, `GlobalTextureAtlasManagerUpdate`.

The JawaBench burst runs in a separate MonoBehaviour `Update()` (`JawaBenchVitals.cs:46`, calling `JawaBenchVitals.Frame`
and then `JawaBenchSafeAdvance.Frame`). Unity does not define the order of two MonoBehaviours' `Update` unless script
execution order is set. So the burst runs either just before or just after `UpdatePlay` within the same frame. That
order is UNMEASURED. It matters for §2: it decides whether the first tick of a burst sees per-frame state cleaned by
this frame's MapUpdate or by the last one's.

Inside the burst, each `DoSingleTick` (decompiled `TickManager.cs:357+`) runs the full simulation: MapPreTick,
`ticksGameInt++`, the shader GameSeconds global, the three tick lists, DateNotifier, Scenario, WorldTick,
StoryWatcher, GameEnder, Storyteller, TaleManager, QuestManager, WorldPostTick, MapPostTick, History,
GameComponentTick, LetterStack, and so on. Nothing in the tick is skipped. What a burst skips is everything that runs
**once per frame**: with N ticks per frame, it runs once per N ticks instead of once per tick.

## 2. What runs per frame, not per tick (the divergence surface)

Each entry gives the evidence, what N>1 changes, and whether vanilla Ultrafast already exercises it (up to 30 ticks
per frame). A "yes" there means the risk is already accepted in normal play at that N. The new exposure is
N ≫ 30 (safe_advance on a cheap map) and ticking while the Paused flag is set.

| # | per-frame work | evidence | effect of N ticks per frame | vanilla at 30/frame? |
|---|---|---|---|---|
| F1 | **Power net registration** `powerNetManager.UpdatePowerNetsAndConnections_First` (delayed RegisterTransmitter/Connector actions) | `Map.cs:1156`, `PowerNetManager.cs:114` | A conduit or building spawned mid-burst joins its net only at the next frame. For N-1 ticks it is unpowered: a proof that builds and then ticks sees later power. | yes, ≤30 ticks |
| F2 | **Region and room rebuild** `regionAndRoomUpdater.TryRebuildDirtyRegionsAndRooms` | `Map.cs:1158`; also called lazily from `RegionGrid.cs:40,85,129` | Mostly safe, because queries rebuild lazily. Room stats and temperature room groups may lag. | yes |
| F3 | **Glow grid recompute** `glowGrid.GlowGridUpdate_First` (dirty light, job-based) | `Map.cs:1159`, `GlowGrid.cs:370` | A light toggled mid-burst is stale for up to N ticks. Plant growth, the darkness mood and our glow conditions (bridge-conditions leftover 12) read stale light. | yes |
| F4 | `skyManager.SkyManagerUpdate`, `weatherManager.WeatherManagerUpdate` (ambience volume only), `postTickVisuals`, drawing | `Map.cs:1155,1161,1193` | Render and sound only. Sky colour interpolation jumps. | yes |
| F5 | `lordManager.LordManagerUpdate`, `areaManager.AreaManagerUpdate`, `GameComponentUpdate`, `WorldUpdate`, `SignalManagerUpdate` | `Map.cs:1160,1187`, `Game.cs:671-679` | UNREAD for sim effects; read each before ruling. | yes |
| F6 | **Our own mods' per-frame hooks**: 36 files under `src/RimMandrake` (excluding bridgetools) use `MapComponentUpdate`, `GameComponentUpdate`, `Update()`, `OnGUI`, `Time.deltaTime`, `Time.frameCount` or `RealTime.*` (list: scratch `frame_hooks.txt`; includes FlowWorks LiquidSurface, Hoses, Excavation, SuspensionBridges, GSS CordGraph/Aerial/ConduitRuns, SolarMirrors, AcousticScanner, AtmosphericBase, ExplosiveGrowth, Stillsand) | grep 2026-11-06 | Throttles keyed to frames or wall time misbehave either way. Known instance: RM_WallReach treated `Paused` as "no tick passes" and rebuilt about once per tick in a stepped soak (lesson `20261022T154849Z-FOUNDRY-...`, WALL_REACH_TUNE_REBUILDS_TENFOLD). | partly (not the Paused case) |
| F7 | **Ticking while `Paused` is true**: `TickRateMultiplier` reads 0 and `CurTimePerTick` 0 during every burst tick | `TickManager.cs:74-127` | Vanilla readers of `TickRateMultiplier` are all visual (CameraMapConfig, PawnTweener, PawnRenderUtility, TexturePanner, WeatherOverlayDualPanner, Sound Sample, RealTime, GlobalControlsUtility; grep of decompiled), so vanilla sim is unaffected. A mod that divides by the multiplier, or skips work when Paused, diverges. This is **new** relative to vanilla play. | **no** |
| F8 | **Autosave**: `AutosaverTick` queues a long event mid-tick (`LongEventHandler.QueueLongEvent(DoAutosave)`) | `RimWorld/Autosaver.cs:31-39` | safe_advance checks `LongEventHandler.AnyEventNowOrWaiting` only at frame start, so it keeps ticking the rest of the frame with a save queued. The save then runs between frames, mid-run. Effect on verdicts: probably none (vanilla also ticks out its frame), but it costs wall time and a burst crosses the autosave interval more often per call. Option: make TimeException policy suppress autosave during a run. | yes |
| F9 | **Long events and modals** raised mid-burst (letters with pause, `Find.WindowStack` dialogs, quest choices) | safe_advance re-checks only at frame start; vitals latch covers modals per chunk | Up to one chunk (60 ticks) runs past a modal that would have paused play. | n/a: vanilla pauses on its own |
| F10 | **Frame-budget overshoot**: the budget is checked between chunks, so the worst frame costs about 60 × the worst tick. One measured `DoSingleTick` took 2,368 ms (HoseTickWatch.cs:9, live round 9 T2). | `JawaBenchVitals.cs:725-727` | A long frame stalls the bridge, the UI and screenshots; the 540 s command limit applies per call. | vanilla checks per tick against 45 ms |
| F11 | **GC and allocation pressure**: a 40-200 ms frame of pure ticking produces garbage at tick rate, while Unity's incremental GC (if enabled) gets fewer frames to spread work | UNMEASURED | Possible longer GC spikes. These are wall-time effects only, not verdict effects. | partly |
| F12 | **UI and input**: OnGUI, letters, camera, PawnTweener (E21 in bridge-conditions) | `Game.cs`, PawnTweener reads TickRateMultiplier | Screenshots taken right after a burst show tweened positions lagging. State reads are fine. Only owner looks are affected. | yes |
| F13 | **Sound**: one-shots fire per tick inside the burst; sustainers update per frame | Sound Sample reads TickRateMultiplier | Many sounds in one frame. Cosmetic, but loud. | yes |

Rule that follows: **N ≤ 30 per frame is vanilla-equivalent apart from F7** (ticking while Paused). Above 30 per frame,
F1, F3 and F6 become longer lags than any vanilla player sees. Above 300 per frame, nothing in vanilla has exercised
them.

## 3. Design options

- **O1: Measure first, no new tool.** Benchmark safe_advance (chunk 60, budget 40) against `step_game_ticks` and vanilla
  Ultrafast, on the same save, on the minimal list. This is the cheapest answer to the owner's experiment. Cost: one
  bridge sitting, plus a small script.
- **O2: Tune safe_advance knobs.** Raise `frameBudgetMs` toward its 200 ms clamp, keep the chunk ≤60, and add a
  `perFrameTickCap` (default 0 = unlimited; 30 = "vanilla-equivalent"). The cap turns F1, F3 and F6 into a dial
  instead of a property of the map's tick cost. Cost: a small C# change and a selftest.
- **O3: Adaptive chunk.** Shrink the chunk when one tick costs more than budget/60 (from the last chunk's mean). This
  bounds F10's overshoot to about one tick. Cost: small.
- **O4: Frame-boundary flush (risky).** Every K ticks inside a burst, call the per-frame sim maintenance by hand:
  `powerNetManager.UpdatePowerNetsAndConnections_First`, `glowGrid.GlowGridUpdate_First`,
  `TryRebuildDirtyRegionsAndRooms`. This closes F1-F3 without real frames. Risk: calling `_First` methods twice in one
  frame, and the glow job's lifetime. Needs reading each body first. Cost: medium, with a high trust burden.
- **O5: A new `jawa/tick_burst` tool, as the item names it.** It duplicates safe_advance minus the vitals latch, so
  it is not justified unless O1 shows safe_advance's overhead (latch checks, `V.FirstStop` per chunk) matters. The
  default is **not to build it**. If it is built, it must reuse `SA.Run`.
- **O6: Speed-mode route.** Unpause at Ultrafast with `UltraSpeedBoost` (static private, multiplier 150, so up to 300
  ticks per frame within 45 ms). This uses vanilla's own loop, so F7 disappears. Cost: we lose exact tick counts
  (overshoot within a frame) and the per-chunk latch. FlowWorks playtest "speed" mode is precedent.

## 4. Measurement plan (answers "how fast")

Instrument: one script, `Utils/tickburst_bench.py` (proposed), writing JSON to `D:\ClaudeWork\rimmandrake\tickburst\`.

- **Sites**: (a) a quicktest colony on the minimal list (22 s load), empty-ish; (b) the same map after placing a
  FlowWorks pit plus hoses (expensive ticks); (c) one run on the owner's full list only if a load is happening anyway
  (no special cold load; BENCH takes only live looks, so it rides a scheduled one).
- **Modes**, each for 6,000 ticks, 3 repeats, interleaved A/B/A to cancel thermal and GC drift:
  M1 `step_game_ticks`; M2 safe_advance chunk 60 at budgets 20, 40, 100, 200 ms; M3 Ultrafast unpaused (wall time
  until ticksGame moves 6,000); M4 Ultrafast + UltraSpeedBoost; M5 safe_advance with `perFrameTickCap=30` (after O2).
- **Readings per run**: ticksGame before and after (**re-read from the game, never inferred from "executed"**),
  wall seconds measured on the Python side and in `StartMono/EndMono`, frames (`r.Frames`), ticks per frame (mean and
  p99), the worst frame in ms, mean tick ms (JawaBench TPS sampler, `JawaBenchTpsProfiler.cs`), bridge round trips per
  run, and GC count deltas (`GC.CollectionCount(0..2)`, read through `jawa/static_call` or a status field).
- **Sanity probe (instrument trap)**: first run 60 ticks and require ticksGame to move by exactly 60. A rate measured by
  a clock that did not move is a query bug, not a result.
- **Expected shape, as a hypothesis to falsify**: M1 about 60 ticks/s (frame-bound, E1/E20). M2 at 40 ms is about 40 /
  tick-ms × fps-share. On the minimal list (tick ≈ 0.1-0.5 ms, unmeasured) that would be several thousand ticks/s.
  M3 is at most 30 × fps (about 1,800 ticks/s at 60 fps). If M2 is not well above M1, the bottleneck is the Python
  poll or round trip, not the frame. That would be a finding.

## 5. Verdict-equivalence plan (answers "can we trust it")

- **Proofs**: the three precedent in-proof loops make poor subjects, because they already burst inside a static call.
  Use three bridge-driven proofs that call `_BridgeBase.ticks` and run on the minimal list. Proposed: FlowWorks P_pits
  pit-fill (E1, power and fluid), one GSS cord or aerial line (power nets, which exercise F1), and one plant or light
  proof (glow, F3; Plant ticks only `TickLong`). Names to be picked from `live_proofs/` by reading them, not guessed.
- **Arms**: A = `step_game_ticks` (1 tick per frame); B = safe_advance at its default; C = safe_advance at 200 ms and
  no cap (maximum N per frame); D = cap 30.
- **Same start**: load the same save fixture for each arm (a mid-proof save if the proof supports it). Fix the RNG
  where the proof allows (`Rand.PushState(seed)` is not possible across ticks, so equality is of **verdicts and
  coarse state**, not bit-identical worlds; note it).
- **Compare**: the verdict row by row (PASS/FAIL/UNMEASURED with reasons), plus a state digest at the end: per-cell
  fluid totals, power net count, stored energy, pawn positions and jobs, thing counts by def, ticksGame. A verdict
  difference is a defect to classify (MOD, SITE or HARNESS). A digest difference within RNG noise needs a tolerance
  written **before** the runs.
- **Repeat**: two runs of the same arm give the noise floor. Equivalence means the A-vs-C difference is no larger than
  A-vs-A.
- **Guard to ship with it**: GPT's "sweep clock domains and tick phases" (`scored.md:116`). Run each proof with N per
  frame in {1, 30, max}. Any mod whose verdict changes with N has a per-frame dependency, and it is filed against
  the mod.

## 6. Interplay with the conditions runner and migration

- `advance_until` (bridge-conditions R2) is safe_advance with a condition evaluated after **every** `DoSingleTick`,
  inside the same inner loop (`draft.md:246`). Burst size does not change its tick resolution. It changes only how
  many ticks pass between frame-level effects (F1-F3). A condition that reads light or power can be true later than
  in vanilla play by up to N ticks. Its report must carry `ticksPerFrame` so a reader can judge a hit against F1-F3.
- "Burst until condition" is therefore not a new feature. It is `advance_until` with `frameBudgetMs` and
  `perFrameTickCap` passed through.
- Migration: the direct `step_game_ticks` callers (about 259 lines, §0) move to `_BridgeBase.ticks` or
  `clockgate.advance_chunk`. A `lint_calls` rule refuses new direct calls (bridge-conditions ticket
  POLLLOOPS_MIGRATE_TO_UNTIL already proposes the lint, so add the rule there instead of opening a second lint).
- The 2,500-tick Python chunk cap exists so that a refusal stays local, not for speed. At several thousand ticks/s
  (if measured), one call is under 1 s, and round trips (about 50 ms each) become a visible share. Raise the cap only
  if the measurement shows that share above about 10%.

## 7. Value, cost, evidence summary (burst itself)

| idea | value | cost | evidence |
|---|---|---|---|
| O1 measure | the owner's experiment, answered; sets every soak estimate | S | precedent loops; E1/E20 rates |
| O2 cap + budget knobs | makes per-frame lag a dial; enables equivalence arms | S | `JawaBenchVitalsTools.cs:171-208` |
| O3 adaptive chunk | bounds a frame-stall from one slow tick | S | HoseTickWatch 2,368 ms tick |
| O4 frame-boundary flush | removes F1-F3 lag at high N | M, high trust | `Map.cs:1155-1160` |
| O5 new tick_burst tool | none beyond O2 unless O1 shows latch overhead | M | duplicate of SA.Frame |
| O6 Ultrafast+boost route | vanilla-native, no F7 | S | `TickManager.cs:104-110` |
| equivalence suite | trust for every future stepped proof | M | §5 |
| step_game_ticks migration | the bulk of the real speed-up for legacy proofs | M | 259 lines / 139 files |

## 8. Leftovers from the bridge-conditions design (owner: "anything I left out")

From `bridge_conditions_2026-11-06/draft.md` §6 and the non-primitive parts of `gpt_enriched.md`.

| # | leftover | value | cost | evidence | home |
|---|---|---|---|---|---|
| L1 | **Tick burst premise**: correct it to "true of step_game_ticks, false of safe_advance"; the gain is the paused per-frame budget | sets the item's real scope | S (this doc) | draft §6; `JawaBenchVitals.cs:718-731` | this item (§0) |
| L2 | **Cold-load cost** (about 25 min on the full list against 22 s on the minimal list) | biggest single wall cost per round | owned elsewhere | draft §6; rimworld-load-round skill | load-round / minimal-list work; not here, recorded so it is not lost |
| L3 | **Bridge round-trip latency**: about 50 ms per call; L_preflight made 371 calls in 19.8 s. Needs batch read tools (`get_terrain_batch` exists; extend the pattern to things-in-rect, pawn-state-batch, fluid-cells-batch, power-nets-batch) | at burst speed the round trip becomes the bottleneck (§6) | M per batch tool | draft §6 | this item, as a follow-up ticket: BATCHREADS_BUILD_ROUND_TRIP_CUT (namecheck OK 2026-11-06, not filed) |
| L4 | **Site staging and recovery** (proof-or-site defects: 231 rows in runs.jsonl) concerns `prepare_site` and fixtures; invariant monitors only partly help | most UNMEASURED rows | M-L | draft §6; `scored.md:110` | site/fixture work; recorded, not designed here |
| L5 | **PawnTweener lag in screenshots** (E21) after a burst: let the tweener settle (a few real frames at Normal, or `PawnTweener.ResetTweenedPosToRoot`) before a capture | only owner looks | S | draft §6; F12 | screenshot helpers |
| L6 | **540 s command limit vs long bursts** (`gpt_enriched.md` §6.5): a resumable run id, status polling and cancel, which safe_advance already has; make sure a burst run cannot outlive its caller unnoticed (orphan run refuses later advances, night review 2026-10-13) | robustness | S | `JawaBenchVitalsCore.cs:340`; gpt_enriched §6.5 | this item: a status check in the bench script |
| L7 | **Clock domains** (`gpt_enriched.md` §2.4): simulation ticks, frames and wall time are reported separately in every result | prevents "ticks/s" being computed from the wrong clock | S | gpt_enriched §2.4 | this item: §4 readings |
| L8 | **Save/load policy mid-run** (`gpt_enriched.md` §6.2): a burst must end on game change or map loss (it already does, `AdvanceGameGate`) and must not span an autosave without saying so (F8) | evidence integrity | S | gpt_enriched §6.2; F8 | this item |
| L9 | **Determinism provenance** (`gpt_enriched.md` §7.4): record mod list hash, save fixture hash, seed, stepping mode and N per frame with every verdict | lets a later reader see that a verdict came from a burst | S | gpt_enriched §7.4 | this item (§5) |
| L10 | **Cost budget and throughput ledger** (`gpt_enriched.md` §7.1-7.2; `scored.md` "Proof cost ledger"): ticks/s, calls per row, wall per row per proof run | tells whether any speed-up worked | S-M | scored.md:120 | this item's bench writes the first rows |
| L11 | **Preserve failure evidence** (`gpt_enriched.md` §7.5): on an equivalence mismatch, keep both digests and the last N per-tick samples | debuggability | S | gpt_enriched §7.5 | §5 |
| L12 | **Flyer frames joint session** (`gpt_enriched.md` §8): never live-test a flyer's flight (standing ruling). A burst makes flyer frames even less representative. **Excluded**: no flyer proof is in the equivalence set | ruling compliance | 0 | standing ruling | excluded |

## 9. Open questions (for the review)

1. Unity Update order of the JawaBench MonoBehaviour relative to `Root_Play.Update`: does a burst see this frame's
   MapUpdate or the last one's?
2. Is `UltraSpeedBoost` settable (static private; who sets it, dev mode only?), and does it beat safe_advance?
3. Is the incremental GC enabled in RimWorld 1.6's Unity build (F11)?
4. Which three proofs: pick by reading `live_proofs/` for ones that use `_BridgeBase.ticks` and run on the minimal
   list.
5. Is there external prior art: TickManager "ultrafast", the dev "tick once" key (`TimeControls.cs:155-158`, one tick
   per keypress), mods such as Smart Speed / TimeControl / RimThreaded (multithreaded ticks) / Performance Fish, and
   what did they learn about per-frame divergence?
