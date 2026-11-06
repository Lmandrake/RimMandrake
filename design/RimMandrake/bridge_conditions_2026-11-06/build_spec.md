# BRIDGE_CONDITIONS: build spec (2026-11-06)

Status: BUILD SPEC (third stage, BENCH, Opus 5.5). Offline. It condenses `draft.md` (first designer) and
`gpt_enriched.md` (GPT critique) after checking the claims it relies on against the code. Where this spec and
an input disagree, this spec governs.

Owner ask (2026-11-06): composable in-game bridge primitives called from Python: "advance until this is true, N
ticks, watch this and report when it happens", "Wait until there's water in this cell.", "Report when this cell
turns dry.", "Alert when light(dark) reaches this location." Attack polling aggressively. Record flyers as the
sequence of flight-animation frame texture paths (STATE, never screenshots). The first live flight run is a joint
session with the owner. Proofs stay in Python, and the game gains generic primitives, not C# test suites.
Many ticks per frame belongs to `TICKBURST_PROVE_MANY_TICKS_ONE_FRAME`. This spec references that item and does
not specify it.

## 0. What was verified, and what the inputs got wrong

| claim | verdict | evidence |
|---|---|---|
| safe_advance already runs many ticks per frame | TRUE | `JawaBenchVitals.cs:699-735` `SA.Frame`: `DoSingleTick` in chunks of `V.MaxChunk = 60` (`JawaBenchVitalsCore.cs:43`) inside `frameBudgetMs` (default 40). |
| the stop latch is checked per chunk, so a condition stop would have 60-tick resolution | TRUE | `SA.Frame` calls `V.FirstStop(Latch.Since(r.StartSeq), r.Stop)` once per chunk, before each inner `for (i<n) DoSingleTick()`. |
| a new DoSingleTick postfix is needed for watchers (the draft's R3, "the seam AllocProbe patches") | WRONG, and it would double-evaluate | Vitals already owns a guarded prefix and postfix pair, `TickPre`/`TickPost` (`JawaBenchVitals.cs:~235-268`, with reentrancy and skip guards and active only while armed). That pair is the single dispatcher, which answers GPT §2.3. |
| E1: FlowWorks v2 P_pits (143 s) is a poll problem | MOSTLY WRONG | `validation_v2_result_20261025T0152_run4.json`: P_pits made 96 calls for 8,607 ticks. Its wall time is tick throughput (`rimworld/step_game_ticks`, for example `FLYER_LAND_TICKS` at `validation_v2.py:3247`). That cost belongs to TICKBURST, and conditions fix little of it. The 371 calls in L_preflight are reads with 0 ticks, which is a batching problem. |
| FlowWorks "water in this cell" needs placeholder names | RESOLVED | `RimMandrake.FlowWorks.RM_MapComponent_Excavation` has `DepthAt(IntVec3)` and `FillAt(IntVec3)` returning `byte` (`FlowWorks/Source/RM_MapComponent_Excavation.cs:1400,1461`), plus `IsSourceCell`. The companion already reflects these at `JawaBenchFlowWorksTools.cs:436-440`. |
| the companion's pure logic can be unit-tested offline | TRUE | Pure `*Core.cs` files are compiled into console selftests (`bridgetools/AwarenessSelfTest/*.csproj` includes `JawaBenchVitalsCore.cs`), and Python selftests run them. The condition evaluator follows that pattern. |
| sampling per tick misses sub-tick changes (GPT) | TRUE, accepted | A state read once per tick at end of tick misses a job that starts and ends within one tick. When occurrence matters, the claim goes to an event ring (§1.3, P-ring). The result always states its coverage. |
| mutating actions must be recorded with results (GPT) | ACCEPTED | v1 has no in-game write actions (§1.7 OUT). Every mutation the Python wrapper makes while a run is armed, including `site_recover`, is appended to `result.mutations[]`. |
| "the work is only glue" (draft) | WRONG (GPT) | The contract (temporal semantics, coverage, ownership, retained results) is the work, and it is ticketed as such (CONDCORE first). |

## 1. The minimal core

### 1.1 Shape
Python sends a JSON condition tree once. The companion evaluates it at the end of every tick inside the vitals
`TickPost` hook. It is the same code path in `safe_advance`, in `step_game_ticks` and in normal-speed play. The
companion returns the exact tick the condition became true, together with the values that made it true. The stepper
is not replaced: `advance_until` is `safe_advance` with one extra stop source.

### 1.2 Wire format (v1)
```json
{"until": {"all": [
   {"cmp": [{"p": "fw.fill", "cell": [106,103]}, ">=", 1]},
   {"not": {"cmp": [{"p": "pawn.state", "pawn": "Human123", "f": "downed"}, "==", true]}}]},
 "max_ticks": 6000, "every": 1, "on_unknown": "stop", "runKey": "v2-P3-a1b2",
 "watch": [{"name": "dry", "tree": {"edge": {"cmp": [{"p": "cell.is_water", "cell": [110,90]}, "==", false]}, "dir": "rise"}}],
 "sample": {"every": 60, "on_change_only": false, "probes": {"sky": {"p": "map.sky_glow"}}},
 "snapshot_on_hit": {"n8": {"p": "fw.fill", "rect": [105,102,3,3], "reduce": "max"}}}
```
Rules:
- Unknown keys are refused by name (the `JawaBenchArgGuard.cs` pattern).
- The tree is compiled once at arm: defs are resolved, getters are bound, and the canonical form is echoed back. A
  defName that does not resolve is a refusal at arm, never a silent false at tick 4000.
- Caps are refused by name: 64 nodes, 1,024 cells in total across rect probes, 16 watchers per owner, 4,096 sample rows.
- Every node may carry an `"id"`, which is echoed back in the results.
- Spatial probes are pinned to an explicit `mapId` (default: the current map at arm). A UI map switch never retargets them.
- Rects are inclusive. An out-of-bounds cell is refused at arm.

### 1.3 Probe set (v1). Every read returns `{v, status}`
`status`: `ok` | `gone` (the thing or pawn is despawned, destroyed or dead; `detail` says which) | `oob` | `unbound`
(the type or mod is not loaded) | `error` (an exception, with its message kept). A non-ok value is UNKNOWN, never 0 or
false. Arm evaluates every probe once and returns `atArm`, so the caller sees that the instrument can see before
any tick runs.

| probe | read (all verified read-only) | serves |
|---|---|---|
| `cell.terrain`, `cell.is_water` | TerrainGrid (top layer, `TerrainDef.IsWater`) | "turns dry" for vanilla water |
| `fw.depth`, `fw.fill`, `fw.source` | `RM_MapComponent_Excavation.DepthAt/FillAt/IsSourceCell` (`unbound` without FlowWorks) | "water in this cell" (FlowWorks) |
| `cell.glow`, `map.sky_glow` | `GlowGrid.GroundGlowAt`, `SkyManager.CurSkyGlow` (the `jawa/glow_at` reads) | "light (dark) reaches this location" |
| `cell.roofed`, `cell.temp`, `cell.fire` | RoofGrid, GenTemperature, ThingGrid filtered by Fire | common site conditions |
| `game.tick`, `game.hour` | TickManager, GenLocalDate | time-of-day staging (E9) |
| `pawn.pos`, `pawn.map`, `pawn.job` (def and job id), `pawn.state` (downed, dead, mental, drafted) | Pawn | walks (E3), jobs (E6), map return (E15) |
| `thing.exists`, `thing.spawned`, `thing.pos` | Thing | lifecycle |
| `thing.field(path)` | fields and properties only, compiled to a getter delegate once; a method call is refused | per-subject mod state (E5) |
| `map.count(def, rect?)` | listerThings | spawn conditions (E14) |
| `ring.count(source, filter)` since arm | cursor diff over `jawa/damage_log`, `incident_journal`, `drain_log` (log errors), letters | event-complete occurrence and `log_error` |
| `pawn.flight.*`, `pawn.anim.*` | ticket FLYERFRAMES only | flyer frames |

Rect reducers: `any | all | count_where | max | min`. `all` and `any` over an empty set is refused at arm
(`require_nonempty` is the default). `static.call` (arbitrary mod code) is not admitted in v1 (§1.8).

### 1.4 Predicates and combinators (v1, a small bounded set)
| node | semantics (resolves GPT §3.3 for this subset) |
|---|---|
| `cmp(p, op, v)` | `== != < <= > >=`, `in [a,b]`, and circular `hour_in [a,b]` across midnight. Numbers are compared with an optional `tol`. |
| `all`, `any`, `not` | Strong Kleene logic. Every child is evaluated on every due tick (no short-circuit), so stateful children never skip updates. |
| `changed(p)` | The value differs from the previous ok observation. An UNKNOWN in between resets the baseline. |
| `edge(c, rise\|fall)` | True on the evaluation where `c` flips. A condition already true at arm does not count as an edge (`trueAtArm` is reported instead). An UNKNOWN gap resets the baseline. |
| `stays(c, N)` | `c` has been true on every evaluation over an elapsed span of N ticks. An UNKNOWN breaks the streak. This also covers "settled", as `stays(not changed(p), N)`. |
| deadline | `max_ticks` on the run. A hit exactly on the deadline tick counts as a hit. `max_ticks=0` evaluates at arm only. |
| `alarm` (watcher mode) | An invariant: the first true is a violation event. Never used as an `until` root. |

Cut from v1: `rate`, `delta`, `seq`, `count(edge)`, `after`, `while`, `for_each`, hysteresis, MTL `responds_to`.
Python composes these from watch events when it needs them (§3). For `for_each`, Python arms one watcher per subject.

### 1.5 Runners (bridge tools)
| tool | does |
|---|---|
| `jawa/cond_eval {tree}` | Evaluates now with no tick. Returns the canonical tree, per-node `{v, status}`, and cost. It doubles as a dry run. |
| `jawa/safe_advance` + `until`, `watch`, `sample`, `snapshot_on_hit`, `runKey` | Existing tool, extended. A `cond` hit sets a per-run flag in `TickPost`, and the `SA.Frame` inner `for` breaks after the tick that set it, so the stop is exact. `state` adds `hit`, `unknown` and `budget`. The existing `done` means max_ticks with no hit. A start with a `runKey` already seen returns the existing run, never a second one. The last 8 terminal results are retained and readable by `runKey`. |
| `jawa/cond_watch {action: arm\|read\|clear\|list, owner, ttlMin}` | Persistent watchers and samplers outside any advance, for normal-speed play or a caller's own stepping. One ring per owner, read with a `since_seq` cursor. Overflow returns `gap` with the lost seq range. `clear` acts on the owner's watchers only, and there is no global clear-all for harnesses. |

Result (one shape for every runner):
`{runKey, state, hitTick, values, atArm, trueAtArm, executed, tickFrom, tickTo, epoch, triggers[], coverage:
{every, evals, resolutionTicks, gaps[], complete}, cost: {evalMsTotal, evalMsMax}, watch[], sample[], snapshot,
mutations[]}`. When safety and a hit land on the same tick, `triggers[]` lists both. `state` is `stopped` (safety
takes precedence), and `hitTick` is still reported. A condition hit is evidence. Python makes the PASS, FAIL or
UNMEASURED call; the draft's "the condition IS the verdict" is withdrawn.

### 1.6 Budget
- The evaluator cost is measured, not assumed. CONDCORE and ADVANCEUNTIL report `evalMsTotal/evalMsMax` per run, and
  AllocProbe checks for 0 GC allocation on the steady-state path, excluding hit and serialisation.
- Default limit: evaluation ≤ 5% of stepping time per frame, plus a hard 0.2 ms per tick. Over the limit, the run
  stops with `state=budget` and names the costliest node. There is no silent degradation of `every` (GPT §7.2). A
  `sample` may opt into `degrade:true` because it is exploratory.
- The limit is relative to stepping time, so it scales when TICKBURST raises ticks per frame.

### 1.7 Safety and interrupts
- The vitals latch stays in charge. Every default stop kind, the 30,000 budget, `timeException` and the 1.2 M
  refusal still apply. A condition can only end an advance earlier.
- `on_unknown: stop` (the default) ends the run with `state=unknown`, naming the probe and its status. `ignore` is
  allowed per node via `"optional": true`.
- Load, menu, game change or map gone ends the run (the existing `AdvanceGameGate`) and clears every watcher scoped to
  that game. Watchers carry a ttl lease (like vitals `ttlMin`) and expire without a reader.
- An exception in a probe disarms that watcher with `disarmedWhy`. It never kills the tick.
- A run is armed only while the game is paused, or the game is paused by arm. Python's stimulus, issued before the call
  while paused, is therefore race-free without an atomic stimulate action.
- **OUT of v1**: `hold` and intervention actions (BlueDesert E16), `screenshot` actions, `static.call` probes,
  `field_snapshot/diff`, `pawn_flight start/hold` from any tree, monitor persistence across save/load, `rate/seq/...`
  (§1.4), and the job start/end Harmony event seam. Each is a later item, filed only if a USE case proves it is needed.

### 1.8 Determinism
- `tick` is `TicksGame` read in `TickPost` after the tick ran, meaning state as of the end of tick t. With `every=1` the
  hit tick is the first qualifying end-of-tick observation. It does not claim the intra-tick instant.
- Every event carries the vitals `epoch` (from `EnsureEpoch`). `stays` and the deadline are refused across an epoch
  change.
- Probes are read-only by construction: field and property getters plus the listed engine reads, with no RNG.
  `thing.field` refuses methods. Wall time appears only in `cost`, never in a predicate.
- Determinism replay (the same save and tree, run twice) is a later use, not a v1 bar.

### 1.9 Python API (`src/RimMandrake/Utils/conds.py` + `_BridgeBase` in `validation_core.py`)
```python
from conds import cell, fw, pawn, game, ring, all_, any_, not_, edge, stays, changed
r = B.until(fw(106, 103).fill >= 1, max_ticks=6000)          # CondResult(state, hit_tick, values, coverage, ...)
with B.watch("dry", edge(cell(110, 90).is_water == False), owner=RUN) as w:
    B.ticks(2500)                                              # any advance; the watcher sees every tick
    for ev in w.events(): ...                                  # ev.tick, ev.values, ev.seq
B.cond_eval(tree)                                              # debug a tree without ticking
```
- Operator overloading builds the JSON. Names are checked offline against `northstar_driver/tool_schemas.json`.
- `B.until` chunks under the 540 s command limit with `timeoutMs` ≤ 480,000, then re-attaches by `runKey`. The
  cumulative tick budget is preserved, and a progress line is printed on each return.
- `state=stopped` goes through clockgate's existing `GovernorStop` / `is_benign_stop` path. On a benign stop,
  `site_recover` runs, the mutation is appended to `result.mutations[]`, and the run resumes. Level conditions carry on.
  Edge and stays monitors restart their baseline and `coverage.gaps[]` records the hole. A `hit` is never a
  `GovernorStop`; it is a new `CondResult`.
- `unknown` maps to UNMEASURED with the probe's reason. Mapping `done` (no hit by max) to FAIL or UNMEASURED is the
  caller's choice.
- `scenelib` gets the same `until` and `watch` functions over its `call()`, because `TheSump/prove_glasswalk_speed.py`
  uses scenelib, not `validation_core`. The builders are shared.
- Offline twin: `conds.evaluate(tree, series)`. It is the same semantics in Python, run on the same
  `conds_vectors.json` as the C# core (§2 CONDCORE).

## 2. Tickets

Acceptance is a selftest (offline) unless marked live. "Live" means a minimal-list check through the bridge, run
by whoever holds the bridge, never this designer. Every name passed `rimflow namecheck` on 2026-11-06. None is filed
yet.

| # | name | one buildable unit | acceptance | depends | needs |
|---|---|---|---|---|---|
| T1 | `CONDCORE_BUILD_THREE_VALUED_TREES` | Pure C# `JawaBenchCondCore.cs` (parse, refuse, canonicalise, compile, Kleene logic, the nodes of §1.4, coverage and cost accounting, behind an `IProbeSource` interface), the `CondSelfTest` console project (AwarenessSelfTest pattern), the Python `conds.evaluate` twin, and `conds_vectors.json` | `selftest_conds_vectors.py` runs the vectors through both evaluators with byte-identical outputs. The vectors include: true at arm, `max_ticks=0`, a hit exactly on the deadline, UNKNOWN mid-streak, an UNKNOWN gap before an edge, an empty rect refused, a stateful child under `any[true, ...]`, a shared probe with independent baselines, an epoch change under `stays`, and every refusal by name | none | none |
| T2 | `CONDPROBES_WIRE_ENGINE_READS` | The Verse-side `IProbeSource` for the probe set of §1.3 (not ring, not flight), map pinning, `atArm`, and the `jawa/cond_eval` tool | Live: on a quicktest map, `cond_eval` values equal `jawa/glow_at`, `get_terrain_layers`, `canal_cell_report`/`flowworks_excavation_rect` and `pawn_get` for the same cells and pawns. A bad defName, an OOB cell and a missing FlowWorks each return their named status. | T1 | none |
| T3 | `ADVANCEUNTIL_WIRE_PER_TICK_STOP` | Evaluation in vitals `TickPost`, the per-run flag, the inner-loop break in `SA.Frame`, the `hit/unknown/budget` states, `runKey` idempotency, 8 retained results, the result shape of §1.5, and the budget of §1.6 | Offline: unit tests for stop arbitration (safety and hit on the same tick, cancel racing completion). Live: `until(game.tick >= T0+137)` gives `executed == 137` and `hitTick == T0+137`; true at arm gives `executed == 0`; a repeated `runKey` start creates one run; AllocProbe shows 0 steady-state allocation; cost is reported | T1, T2 | none |
| T4 | `CONDSDSL_WIRE_PYTHON_BUILDERS` | `conds.py` builders, `B.until`, `B.watch`, `B.cond_eval`, `CondResult`, the clockgate integration (resume, `mutations[]`, `gaps[]`), scenelib functions, `tool_schemas.json` | `selftest_conds_dsl.py` against a fake bridge: the JSON shapes, state to verdict mapping, a 540 s re-attach by `runKey`, the benign-stop resume recording its mutation, and an edge baseline reset after a recovery | T1 (fakes T3) | none |
| T5 | `CONDWATCH_BUILD_OWNED_RINGS` | `jawa/cond_watch` (arm, read, clear, list), per-owner rings and ttl leases, `sample` (with `on_change_only`), clearing on load and menu, overflow gaps | Offline: unit tests for ring overflow, gap ranges, lease expiry and owner-scoped clear. Live: one edge watcher on `cell.is_water` sees the same single event under `step_game_ticks`, `safe_advance` and normal-speed play, with no double count | T3 | none |
| T6 | `RINGPROBES_WIRE_EVENT_CURSORS` | `ring.count` over damage_log, incident_journal, drain_log and letters since arm, plus `log_error` as an opt-in stop kind | Live: a stimulus from an existing tool, named at build time from its source, raises one row. `until(ring.count(...) >= 1)` stops on that tick, and ring overflow reports `gap` | T3 | none |
| T7 | `GLASSWALK_MIGRATE_EXACT_EDGES` | **The USE ticket** (§3) | Before and after on the same load, with identical verdicts and the counts of §3 | T3, T4 | none |
| T8 | `READYWAITS_UNIFY_ONE_HELPER` | The Python `await_lifecycle(state, deadline_s)` over `get_ui_state` (frame and wall clock, not ticks), migration of 5 of the about 57 copy-pasted ready loops, and a `lint_calls.py` warning for new copies | A selftest with a fake bridge covers loading, menu, missing map and timeout. The 5 migrated scripts still pass their own selftests | none | none |
| T9 | `POLLLOOPS_MIGRATE_TO_UNTIL` | A `lint_calls.py` rule for the advance, read and decide loop (draft §2.1 AST heuristic), plus 3 migrations that test distinct guarantees: gravel `wait_depth` (E4, level), sprinkler `until_pulse` per head via `thing.field` (E5, subject identity) and a staging `alarm` on pit fill (E19, invariant) | Each migration produces identical verdicts before and after, with calls and wall time recorded as in §3. The lint selftest flags the 3 old forms and passes the new ones | T5, T7 | none |
| T10 | `FLYERFRAMES_PROVE_JOINT_SESSION` | First, verify the seam against the deployed decomp (`AnimationDefGenerator_Flying`, `Pawn_FlightTracker.CheckFlyAnimation`, `PawnRenderTree.AnimationTick`, the graphic state to texPath mapping). Then build the probes `pawn.flight.*` and `pawn.anim.*` (`anim`, `animTick`, `keyIndex`, `graphicState`, `texPath`, `facing`, `mirrored`), a `flight_frames` sample preset (an on-change channel for state, keyIndex, texPath and facing; a separate periodic channel for position), an offline asset audit (every texPath resolves to a PNG for every facing), and a reconstructed flip-book with its limit stated: it shows the selected graphic state, not rendered pixels | Offline: the seam is documented with file:line in the decomp; the asset audit runs from defs; a fake series through T1 decodes; `cond_eval` reads `pawn.anim` on a generated AnimationDef without starting flight. Live: **only at a joint session with the owner present**. No tree can start or hold flight, and screenshots are refused when `pawn.anim` is in the tree | T2, T5 | **needs=owner** (live run) |

Build order: T1, then T2 with T4 in parallel, then T3, then T7 (USE: the first end-to-end proof), then T5 and T6,
then T8 (independent, any time), then T9, then T10 last, at the joint session.

## 3. USE ticket: `GLASSWALK_MIGRATE_EXACT_EDGES`

**Pick:** `src/RimMandrake/TheSump/prove_glasswalk_speed.py` (SUMP_GLASSWALK_SPEED_RATIO_1/A1). Why it benefits most:
- It is the densest poll in the tree. `walk_exact` (lines 143-191) advances `rimworld/step_game_ticks(2)` and then
  reads `time_clock`, `pawn_get` and `time_clock` again: 4 bridge calls per 2 ticks.
- Its history is a list of instrument failures that a per-tick edge removes:
  - `S.run(10)` sampling gave a false 0.65 ratio (E3).
  - Live on 2026-11-04 the clock ran between calls, so walks read 2 and 26 ticks: `granite=1.17 ticks/cell` FAIL
    (`/home/mandrake/rm/relentless/live/SUMP_GLASSWALK_SPEED_RATIO_1-A1-20261104T015948Z.log`).
  - The exact-clock guards added after that make it correct, but slow.
- Its verdict is one comparable RESULT line.

**Baseline (read from code; no clean measured run exists).** The three latest Relentless runs are UNMEASURED (no
13 ticks/cell pawn), the harness FAIL above, and a crash with `No BiomeDef named 'RM_GreySea'` (environment)
(`/home/mandrake/rm/relentless/live/SUMP_GLASSWALK_SPEED_RATIO_1-A1-2026110{3,4,5}*.log`).

Per walk:
- Approach loop: up to 80 × (`step(20)` + `pawn_get`).
- Timing loop: about 15 cells × T ≈ 13.6 ticks, so about 205 ticks on granite and about 250 on glass. At 2 ticks per
  step that is about 100-125 steps × 4 calls, or about 400-500 calls.

Four walks therefore take about 1,700-2,100 bridge calls, with a 2-tick crossing resolution (per-cell error ≤ 0.17).
At the measured ~53 ms per call (run4 L_preflight: 371 calls in 19.8 s) that is about 90-110 s of walk wall time.
On a 19-mod tier `step_game_ticks` itself ran at 5-14 ticks/s (scenelib.py:45), so the real figure may be higher.

**After.** Each walk becomes:
- `ordered_job`
- one `until(pawn.pos.x <= x+1)`
- `ordered_job`
- one `safe_advance` with `watch: [edge(pawn.pos.x >= x+X0), edge(pawn.pos.x >= x+X1)]`, `until` = the second
  edge, and `max_ticks` 1,200

That is about 5 calls per walk, about 20 calls for all walks, with 1-tick resolution and no free-running clock
(safe_advance is paused). The unpaused-clock failure class disappears by construction. Expected compression: ≥ 80×
fewer walk calls and ≥ 10× less walk wall time (bounded below by safe_advance tick throughput).

**Measurement, before and after.**
1. Add a call counter to `scenelib.call` (module counter, printed as `CALLS n WALL_S w` per walk and in total). This is
   part of T7.
2. On one minimal-list load that has `RM_GreySea` (fix the environment first; it is not a product defect), run the
   old proof, then the new one, back to back, on the same build.
3. Pass when:
   - both RESULT lines carry the same verdict (PASS/FAIL/UNMEASURED and the same clause);
   - granite and glass ticks/cell agree within 2/12 ticks/cell, the old resolution;
   - the counter shows the compression above.
4. A verdict difference is a finding to diagnose, never averaged away.
5. Evidence goes to `D:\ClaudeWork\rimmandrake\bridge_conditions\use_glasswalk\` (`old.log`, `new.log`, `counts.json`).

## 4. Leftovers for TICKBURST_PROVE_MANY_TICKS_ONE_FRAME (not condition primitives)

- Measure first: safe_advance already does ≤ 60 ticks per chunk inside a 40 ms frame budget. TICKBURST's premise
  ("one tick per frame") holds for `rimworld/step_game_ticks`, not for safe_advance. Measure the ticks/s safe_advance
  achieves on the minimal list and on the full list before building anything.
- FlowWorks v2 run4: P_pits (8,607 ticks, 143 s, 96 calls) and X_promoted (4,771 ticks, 56 s) are throughput-bound.
  Move the `step_game_ticks` calls there (`FLYER_LAND_TICKS`, `validation_v2.py:3247`) to safe_advance.
- `scenelib.run` uses `play_for` at speed 4, which plays at least 200 ms per call and is unpaused. Scenes need a paused
  bulk stepper.
- The evaluator budget (§1.6) is relative to stepping time, so TICKBURST must report per-frame stepping ms for the
  budget to stay meaningful.
- Per-call bridge latency (~53 ms; L_preflight made 371 read-only calls) needs batch read tools in the
  `get_terrain_batch` pattern. It is a round-trip cost, not polling.
- PawnTweener lag and stale draw positions after bulk stepping (E21) matter for owner looks only. State reads avoid them.
- Cold load (25 min on the full list) belongs to load-round and minimal-list work.
