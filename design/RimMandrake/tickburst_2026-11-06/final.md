# TICKBURST_PROVE_MANY_TICKS_ONE_FRAME: final (reframed after skeptical review)

Status: final design, 2026-11-06, BENCH designer (fresh Opus). Inputs: `expansion.md` and `gpt_review.md` beside this file,
and `design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md` §4. Nothing here is built or live-tested.

## 0. Verified before writing (and one correction to the brief)

- `JawaBenchVitals.cs:719-730` (`JawaBenchSafeAdvance.Frame`): once per Unity frame, while ticks remain, it checks the
  vitals latch and the frame budget, then runs a chunk of `DoSingleTick` calls, and repeats. `V.MaxChunk = 60`
  (`JawaBenchVitalsCore.cs:43`); `frameBudgetMs` defaults to 40, clamped 5-200 (`JawaBenchVitalsTools.cs:172,208`).
  **Correction:** 60 is the chunk, not the per-frame cap. Ticks per frame are about budget / tick-ms, plus one
  unchecked chunk of overshoot (the budget is read only between chunks).
- Only `rimworld/step_game_ticks` is one tick per frame. Census 2026-11-06, a lower bound counting lines, not live
  calls: 259 lines in 139 `.py` files under `src/` call it; 153 lines call `safe_advance`. `_BridgeBase.ticks` already
  goes through `clockgate.advance_chunk`, which prefers safe_advance.
- Vanilla Ultrafast **targets 900 ticks/s** (9,000 with `UltraSpeedBoost`). 30 and 300 ticks per frame are catch-up
  ceilings, not targets. Public RimBridgeServer docs say it enables `UltraSpeedBoost` at startup. That is UNVERIFIED
  for the installed version, so every arm reads the flag back.
- Trap carried in: `rimworld/set_time_speed` has left the game PAUSED before (MODCHECK_ULTRAFAST_CLOCK_STALL_1,
  `BlueDesert/validation.py:439`). An unpaused arm counts only if ticksGame is seen to move.

## 1. Reframed goal

We already have a many-ticks-per-frame stepper: `jawa/safe_advance`. **Measure it, then adopt it.** First, measure its
ticks/s against `step_game_ticks` and vanilla's own loop. Second, prove on three existing proofs that it gives the
same verdicts as **unpaused normal-speed play**. Third, move direct `step_game_ticks` callers onto it, but only for
proofs whose verdicts stay equal. No new stepper tool. The claim we are allowed to make is "no divergence observed in
N trials on these proofs", never "equivalent".

## 2. The experiment

### 2.1 Arms

| arm | stepping | role |
|---|---|---|
| R | unpaused Normal speed, vanilla `TickManagerUpdate`, `UltraSpeedBoost` set false and read back; pause at the target tick and record the overshoot | **reference**: the native loop with no Paused flag. Without it, every other arm is a paused stepper and they could all agree while sharing one defect |
| A | `step_game_ticks`, paused, 1 tick per frame | today's direct callers |
| B | `safe_advance`, chunk 60, budget 40 ms (default) | the adoption candidate |
| C | `safe_advance`, budget 200 ms (maximum N per frame) | stress |
| U / U+ | unpaused Ultrafast with `UltraSpeedBoost` false, then true (each set and read back) | throughput only: no exact tick count, so not in the equivalence comparison |

The speed setter for R, U and U+ is named at build time from its source, never guessed, and
`TickManager.CurTimeSpeed` is read back.

### 2.2 Throughput (ticks/s)

- Sites: a quicktest colony on the **minimal list**, and the same fixture with a FlowWorks pit plus hoses (expensive
  ticks). Then the **owner's full list** as the big list, riding a load that is already scheduled. No special cold load.
- Matched starts. Every trial reloads the same fixture, waits for a settle barrier (GameReady, no long event, 3
  frames), discards a 600-tick warm-up, then measures 20,000 ticks. That gives enough burst frames for a p99.
  Arm order is randomized in balanced blocks; 3 repeats per arm count as a pilot.
- Controlled and recorded: VSync and FPS cap, window focus, camera position and zoom (1.6 update rates depend on the
  view), autosave (off), logging, profiler patches.
- Readings, kept in separate clock domains:
  - ticks: ticksGame re-read from the game, never inferred from "executed";
  - frames, plus a per-frame tick histogram (raw samples, not means);
  - server stepping ms per frame and the worst frame;
  - client end-to-end wall time and bridge round trips;
  - `GarbageCollector.isIncremental` and heap growth. These are recorded only, not ruled on.
- Sanity probe first: 60 requested ticks must move ticksGame by exactly 60 in A, B and C. R must be seen to reach its
  target. A rate read off a clock that did not move is a query bug.

### 2.3 Verdict equivalence: three named existing proofs, both ways

Each proof gets one `--step {play,step,safe}` switch in its own step helper, so the same rows run under R, A and B/C.

1. **FlowWorks v2 `P_pits`** (`src/RimMandrake/FlowWorks/northstar/validation_v2.py`, step `P_pits`): fluid and pit
   occupancy. `P_pits` itself advances time through `jawa/order_pawn` waits; v2's direct `step_game_ticks` calls sit in
   `J_jobs_scheduler` (E4 off window, E1b pulse loop) and in the X rows (`_x8b_cover_occupant`, `_x10_canal_fire`), and
   all of them go through the `--step` switch (`_direct_step`). Throughput-bound in run4 (8,607 ticks, 143 s). `X_promoted` rides the same pass.
   The `P_forced` / `ProofForcedFlyer` landing step (:3247, `FLYER_LAND_TICKS`) is **excluded** and stays on
   `step_game_ticks`. Flyers stay out (standing ruling), although build_spec §4 had listed it for migration.
2. **LINES** (`src/RimMandrake/FlowWorks/northstar/lines_proof.py`, step helper :225): pipe poles and GSS power cord,
   which exercises power-net connect **and** disconnect (G1).
3. **Glowtank seed-sow** (`src/RimMandrake/LuminousPigment/live_probes/lp_glowtank_seed_sow.py:50,59`): glow plus plant
   growth (Plant ticks only `TickLong`). Run once at midday and once from a dusk start (G3, G4).

The oracle is stronger than PASS/FAIL:
- Per-row verdicts and reasons.
- Checkpoints at matched ticks. Discrete invariants must match exactly: power-net membership, thing counts by def,
  `glowOnInt`, established, pit occupants, descentCount.
- Continuous values must stay inside bounds: fluid totals, stored energy. The bounds file is committed before the
  first trial. No NaN is allowed.
- Logged ticking exceptions are counted per arm.
- The first divergent checkpoint and both digests are kept.

Trials: 5 fixture reloads per arm per proof, plus 1 fresh-process trial per arm (a 22 s minimal-list load). Stated
limit: zero mismatches in 5 trials still leaves a one-sided 95% upper bound of about 45% on the mismatch rate. That is
a reason to adopt per proof, not a general license.

N sweep (needs `perFrameTickCap`, §3): run LINES and glowtank-at-dusk at N per frame in {1, 30, 60, 61, max}. A
result that changes with N is a **scheduling incompatibility to investigate**. It is filed, not assumed to be a mod
defect, and that caller stays on `step_game_ticks`.

Adoption rule: a proof's direct calls move to `_BridgeBase.ticks` / `clockgate.advance_chunk` only if B matches R
(and C, where it was run) in every trial. If A and B both diverge from R, that is a finding about paused stepping,
filed against the harness.

### 2.4 Per-frame effect guard list (an audit with file:line, then a targeted check)

Each guard row is read in the 1.6 decompile, DLC and our mods, and classed **sim** or **visual**. Every sim row gets a
check in §2.3.

| G | per-frame work | check |
|---|---|---|
| G1 | power-net registration (`UpdatePowerNetsAndConnections_First`): a stale topology both delays a new link and keeps an obsolete one | LINES connect and disconnect rows |
| G2 | `TryRebuildDirtyRegionsAndRooms` **and `RegionGrid.UpdateClean`**: trace every room and temperature consumer, not just the lazy ones | P_pits room rows; audit list |
| G3 | glow grid recompute (job-based): a stale value can be too bright or too dark | glowtank with the lamp toggled |
| G4 | `SkyManagerUpdate`: `CurSkyGlow` is **read by the sim** (plant growth, darkness) | glowtank from dusk; the audit lists `CurSkyGlow` consumers |
| G5 | world dissolution: `CompDissolutionEffect_Goodwill` and `_Pollution` run in `WorldUpdate` (relations and pollution) | census of every `WorldUpdate` / `MapComponentUpdate` / `GameComponentUpdate` / `WorldComponentUpdate` override in Assembly-CSharp, DLC and loaded mods. Sanity probe: both Dissolution classes must appear |
| G6 | background path and glow jobs: completion barriers and worker-visible state | read where 1.6 completes scheduled path jobs relative to `DoSingleTick` |
| G7 | `Pawn_JobTracker.StartJob` loop guard on `Paused` and `lastJobGivenAtFrame == RealTime.frameCount` | verify it in 1.6; count job-loop errors per arm in P_pits (pawn churn) |
| G8 | ticking while `Paused` is true (`TickRateMultiplier` 0): direct `Paused`, `RealTime` and frame-counter readers, not only `TickRateMultiplier` | grep the decompile and our 36 frame-hook files; RM_WallReach is precedent |
| G9 | 1.6 variable tick rates (`GenTicks` camera update rate, projectile and world-object rates) | camera pinned and recorded in provenance |
| G10 | autosave and long events mid-burst; latch read per chunk | autosave off and recorded; a trial with any latch or long event is flagged, not compared, until per-tick stops land (L-c) |
| G11 | `DrawPos` / tweener consumers, sound and effecter callbacks that use shared RNG | audit list only; screenshots go to L-e |

## 3. Small builds inside this item

- `safe_advance`: add `perFrameTickCap` (default 0, meaning unlimited) and a `stepMs` status field (summed in-frame
  stepping ms). The second also keeps the conditions evaluator budget meaningful (build_spec §1.6). Small C# change,
  with a selftest.
- `src/RimMandrake/Utils/tickburst_bench.py`, with `--mock`. It writes JSON with provenance (mod-list hash, fixture
  hash, DLL hashes, arm, N per frame, camera, autosave state) to `D:\ClaudeWork\rimmandrake\tickburst\`. It checks run
  status, then cancels on exit, so no orphan run outlives its 540 s caller. It appends the first rows of the
  throughput ledger.
- The `--step` switch in the three proofs, and the adoption of each proof that passes.

## 4. Cut, and why

- "N ≤ 30 is vanilla-equivalent apart from F7": deleted. A tick-count ceiling does not establish equivalence (GPT 1).
- A new `jawa/tick_burst` tool: it would duplicate `SA.Frame`.
- Adaptive chunk (O3): bounding overshoot from the last chunk's mean does not work (GPT 14). Replaced by per-tick
  stop checks (L-c).
- Frame-boundary flush (O4): a different execution model, not a fix (GPT 16). Not filed. The name
  `FRAMEFLUSH_PROBE_SECOND_BACKEND` passes namecheck and is filed only if G1-G4 block an adoption.
- A private-RNG determinism runner (GPT 19): this item tests ordinary-play compatibility, not determinism.
- Comparing against the Smart Speed, TimeControl, RimThreaded and Performance Fish mods: none establishes
  paused-burst equivalence (GPT 5).
- The full adversarial fixture zoo (GPT 23): reduced to the three proofs, the dusk start and the N sweep.
- `GC.CollectionCount(0..2)`: Boehm is non-generational. Replaced by `isIncremental` and heap growth.
- Flyer rows, including `FLYER_LAND_TICKS`: excluded by standing ruling.

## 5. Leftovers: (a) part of this item, (b) a separate item

| id | leftover | home |
|---|---|---|
| L-a | Measure safe_advance on the minimal list and the full list before building (build_spec §4; L1) | (a) §2.2 |
| L-b | Move FlowWorks v2 `P_pits` / `X_promoted` off `step_game_ticks` (build_spec §4) | (a) §2.3 proof 1, flyer step excluded |
| L-c | Check stop requests, the deadline and long events after **every** tick (GPT 13-14) | **neither**: this is the inner-loop break that `ADVANCEUNTIL_WIRE_PER_TICK_STOP` (build_spec T3) already puts in `SA.Frame`. Its acceptance should name the deadline and long-event checks; not duplicated here |
| L-d | Bridge round trips cost about 53 ms per call; build batch reads | (b) **`BATCHREADS_BUILD_ROUND_TRIP_CUT`**: batch read tools in the `get_terrain_batch` pattern (things-in-rect, pawn-state, fluid-cells, power-nets), each proved by reading the same cells as the single-call tools and counting the round trips saved on one existing proof |
| L-e | PawnTweener lag and stale `DrawPos` after bulk stepping (E21) | (b) **`SHOTSETTLE_BUILD_PAUSED_BARRIER`**: a screenshot helper that settles tweened positions to the root while paused, advancing no ticks (GPT 12), proved by a ticksGame read before and after the capture |
| L-f | `scenelib.run` plays unpaused at speed 4 (`play_for`, at least 200 ms per call) | (b) **`SCENERUN_MIGRATE_OFF_UNPAUSED_PLAY`**: move `scenelib.run` (`Utils/scenes/scenelib.py:44`) to paused `_BridgeBase.ticks`, judged by unchanged scene verdicts and an exact ticksGame delta |
| L-g | The long tail of about 255 direct `step_game_ticks` lines | (b) **`STEPCALLS_MIGRATE_WHERE_VERDICTS_HOLD`**: migrate the remaining direct callers in batches, each batch adopted only if it passes this item's §2.3 rule. Frame-sensitive callers stay. The lint that refuses new direct calls is a rule added to `POLLLOOPS_MIGRATE_TO_UNTIL`'s lint, not a second lint |
| L-h | Clock domains, save/load policy, provenance, throughput ledger, failure evidence, 540 s orphans (expansion L6-L11) | (a) §2.2, §2.3, §3 |
| L-i | Per-frame stepping ms for the conditions budget (build_spec §4) | (a) `stepMs`, §3 |
| L-j | Cold load (25 min on the full list), site staging (L2, L4) | owned by load-round and site/fixture work; recorded only |
| L-k | Flyer frames (L12) | excluded |

All four (b) names passed `python3 src/RimMandrake/rimflow/cli.py namecheck` on 2026-11-06. None is filed; the
Conductor files them.
