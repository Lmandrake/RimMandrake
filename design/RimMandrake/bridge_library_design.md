# rimdrive — the reusable Python bridge library (design)

Commissioned by the owner 2026-09-12 (BENCH sitting, same day as the modcheck
re-ruling): a library that "enables both rapid construction of test scripting
as well as supports injection of new content … a wise place to build up
sophisticated game interactions without needing DLL recompile." Design only;
no implementation in this document's commit.

Evidence base: `bridge_latency_bench.py` (MEASURED 2026-09-12, 593 mods:
~16 ms/main-thread call on a persistent connection, ~78 ms for a whole
fresh-process action, TCP+hello 0.8 ms); the driving-pattern census of
2026-09-12 (400+ one-shot throwaway scripts vs ~a dozen persistent-connection
tools); `skills/rimbridge` doctrine (silent failures, poisoned socket, pause
discipline, batching).

## 0. What already exists, and what this design actually adds

The census found the library half-built and scattered:

| capability | lives today in | state |
|---|---|---|
| framing, token discovery, param guard, retired-tool guard | `Utils/rimbridge_client.py` | done, keep unchanged |
| verified mutation (`mutate(what, do, verify)`), spawn/stuff/quality/pawn/gear verbs, step/play, screenshot discipline (clear_ui, unique filenames) | `Utils/rimbench/core.py` (`Session`) | done, extract |
| ordered gated step-run with ledger, census gate, settle wait, litter tracking, `FakeSession` offline selftest | `bridgetools/load_session.py` | prior art, extract patterns |
| offline plan lint/render/compile to batched `jawa/*` calls (rect coalescing, chunking) | `Utils/rimplace/plan.py` | done — but it has NO dispatcher; nothing applies its output |
| plan-JSON replay against one connection with commit + read-back | `sea_landmark_cleanup_apply.py`, `apply_floor_plan.py`, `repaint_hull.py` | idiom, each hand-rolled |
| reconnect after timeout with post-condition polling | only `w9_run.py`, `reload_check.py`, ad hoc | NOWHERE shared |

Genuinely new: the session hardening (reconnect + post-condition polling,
verified pause, focus preflight, bridge-lock integration), enforced teardown
(litter as a mechanism, not a convention), the runtime tool census, the
scenario layer (modcheck), and a dispatcher that applies rimplace plans.

## 1. Layered architecture

Strict discipline: a layer imports only the layer below it. A mod's
`validation.py` and every future one-shot script imports L3/L4 only — never
`RimBridge` directly, because L1/L2 is where the read-back, pause and teardown
discipline lives (modcheck spec §1).

**L0 transport — `rimbridge_client.py`, unchanged.** Framing, token discovery,
unknown-parameter guard, retired-tool guard. Stays dependency-free stdlib.

**L1 session — `rimdrive.session.Session`** (extraction of rimbench
`Session` lifecycle + new hardening):
- connect via `resolve_endpoint()`; **runtime tool census at connect** (§6.3);
  game-focus preflight (`game_focus.preflight()` — the runInBackground trap);
  optional `settle` gate for a fresh load (the ~40 s drivability window,
  owner-measured 2026-08-14, from `load_session.py`).
- **reconnect with post-condition polling**: a timeout poisons the socket by
  design (skill §1); the session drops it, reopens, and re-asserts the CALLER'S
  stated post-condition — it never blind-retries a call whose idempotence is
  undeclared. This is today hand-rolled in exactly two polling scripts.
- **pause discipline as code**: `paused()` context — re-pause on entry and at
  every exit, VERIFIED by reading `ticksGame` twice (skill §4b; the 2026-08-12
  two-pawn colony loss). Ticks advance only through explicit `step()`/`play()`.
- **litter registry**: every id the session spawns is recorded; `sweep()`
  destroys them and re-reads the area empty (modcheck spec §1b — build-up and
  tear-down are absolute); runs on context exit AND on abort.
- optional bridge-lock integration: `Session(lock="rimflow")` takes/releases
  the bridge through `rimflow bridge` so a script cannot forget the release.

**L2 verified ops — `rimdrive.verify`** (extraction of `mutate()` + the
read-back channels):
- `mutate(what, do, verify)` unchanged in shape; verifiers read INDEPENDENT
  channels (`get_cell_info`, `jawa/list_pawns`, save parse) — never the
  mutating call's own response.
- **Change from rimbench**: an unverifiable write (today `set_stuff` without
  `at` returns a silent `True`) is no longer silent — it lands in the evidence
  stream marked `UNVERIFIED`, and a scenario-layer component containing one
  cannot report PASS, only PASS(UNVERIFIED n). Silence was the bug class this
  module exists to kill; it should not host a quiet exemption.
- **Fix during extraction**: pawn verification via `list_colonists` only sees
  player pawns (rimbench's own docstring admits it). Hostile/other-faction
  spawns verify via `jawa/list_pawns` — modcheck's pit raider needs this on
  day one.

**L3 domain verbs — `rimdrive.things / pawns / map / world / events / camera /
time`**, families mirroring `capability-matrix.md`:
- `things`: spawn (verified), set_stuff/set_quality, destroy_batch.
- `pawns`: spawn by kind+faction (correct verify channel per faction), gear
  (wear/strip via `jawa/pawn_gear` + read-back), select, order with the
  engine-parity caveat (§2c), hediff read/write, prisoner/enslave recipes
  (the spawn-into-other-faction-first trap encoded, not documented).
- `map`: clear_area (footprint + exclusion zone), terrain/foundation batches
  (ordering law: foundation → terrain → things), `apply_plan(BuildPlan)` — the
  missing rimplace dispatcher: compile_calls() output applied chunked on one
  connection, `map_commit` last, then read-back of a sample of cells.
- `world`: `jawa/world_*` writes always paired with `world_commit` + read-back
  (the no-commit-no-visible-edit law), 100-row read pagination handled.
- `events`: weather_set, game_condition, fire_raid/fire_quest (GM-gated).
- `camera`: look/frame extracted verbatim from rimbench (clear_ui default ON,
  unique filenames — both are paid-for lessons).
- `time`: `step()` (deterministic, builds tests), `play()` (wall-clock,
  "eventually" only).

**L4a scenario — `modcheck`** (its own package, consumes L1–L3): `Suite`,
chains, components, `toggle=` floor enforcement, checkpoints (debug mode),
evidence bundle, UNMEASURED-downstream, verify-event + HTML sheet + registry.
All per `mod_validation_runner_spec.md`; nothing scenario-specific leaks down.

**L4b content-injection kits** (siblings of modcheck, same layer):
- `plans`: author in rimplace Lua or BuildPlan, lint/render offline,
  `apply_plan` live — structures without a game restart.
- `scenes`: stage_review_grid (the options-as-savegame ruling 2026-09-02: one
  map, grid pitch, grid key, save + stat the Saves folder), lineups
  (rimbridge_lineup extraction), populate (spawn-many doctrine — batch, never
  one pawn).

## 2. The C#/Python rule

**Default: Python composes existing tools. A C# companion tool
(`rimbridge-companion` skill) is written only for a new PRIMITIVE**, and a
primitive is established by exactly one of four tests:

- **(a) throughput**: the operation is per-item over N with no existing batch
  tool, and N × ~16 ms (MEASURED 2026-09-12, 593 mods, sequenced main-thread
  calls) exceeds ~10 s **in a run that recurs** (a modcheck smoke run, a wave
  tool). One-off authoring passes never qualify — 421 calls is 7 s once.
  The fix is a batch primitive (`set_terrain_batch`: 421 cells, 1 call, 14 ms).
- **(b) atomicity**: the invariant must hold within one tick — spawn + faction
  + draft before the AI thinks, multi-part state that must not interleave with
  the sim. Python round trips cannot promise tick-coherence even paused.
- **(c) engine-predicate parity**: the question is one the GAME also asks, and
  the answer must come from the engine's own call with its exact arguments
  (the `canReach` lesson: a real `CanReach` with `PathEndMode.OnCell` answered
  honestly and was still the wrong verdict). **This test says C# even when
  Python could limp there** — a plausible Python reproduction of an engine
  predicate is worse than no answer, because it lies fluently.
- **(d) reachability**: no tool and no debug action reaches the state at all.
  Check the debug-action tree before concluding (1,119 "apparel" matches on a
  3-mod list; browse with `list_debug_action_children`, never
  `search_debug_actions` on the full stack).

**The cost asymmetry that makes Python the default**: a Python verb ships by
commit — zero recompile, zero restart, testable the same minute on the live
game. A C# tool is ~1 min edit-build-deploy-test on the minimal list, **but
companions register only at RimBridgeServer startup**, so it costs a restart
(22 s minimal, ~15 min full list) and the deploy/census ceremony — and every
new C# tool is new surface for the silent-failure class that produced the ~40
lying calls. A bug in a Python verb fails loudly in the script that owns it.

Corollary: when a Python verb starts accumulating retry loops, sleeps, and
multi-call choreography to fake atomicity, that is test (b) failing slowly —
promote it to a primitive instead of hardening the workaround.

## 3. Content injection without recompile — and its hard limit

"Inject new content" means: any arrangement of EXISTING defs, staged live —
things with material/quality, pawns of any kind/faction with gear and
hediffs, whole structures from plans, weather, game conditions, raids,
quests. All of it is Python over existing primitives, reversible, and needs
no build. This is where "sophisticated game interactions" accumulate.

**The hard limit, stated plainly: a NEW Def cannot be injected.** A new
ThingDef/PawnKind/etc. is XML, deployed to the game dir, loaded at startup.
`jawa/hot_reload_defs` is RETIRED (owner 2026-09-03 — it hung a 589-mod game
and broke all pawn generation while every health flag read green). The
sanctioned path is deploy + restart on the minimal list (22 s, MEASURED
2026-09-07 era; the rimworld-load-round skill). Likewise a new C# tool needs
the shutdown window. The library's job is to make everything short of a new
Def free, so restarts are spent only on genuinely new defs.

## 4. API sketch (signatures for review, not implementation)

The pit-mod chain from the modcheck spec, annotated by layer:

```python
from modcheck import Suite                    # L4a
suite = Suite("RM_PitTraps")

@suite.chain("pit_capture")
def pit_capture(t):
    t.clear_area(size=40)                     # L3 map    (verified empty after)
    pits = t.spawn("RM_Pit", count=3, at="line")   # L3 things → L2 mutate → L1 litter
    raider = t.spawn_pawn("raider", hostile=True, beyond=pits)
                                              # L3 pawns — verify via jawa/list_pawns
    with t.component("falls_in", toggle="pitsEnabled"):
        t.walk_over(raider, pits)             # L3 pawns.order + poll post-condition
        t.wait_ticks(600)                     # L1 time: explicit ticks, else paused
        t.expect_in_cell_of(raider, "RM_Pit") # L2 read-back, lands in evidence
        t.screenshot()                        # L3 camera: clear_ui, unique name
        t.checkpoint("in_pit")                # L4a: no-op in smoke, dump in --debug
# chain end: L1 sweeps every spawned id, re-reads area empty, re-verifies pause
```

Non-test use, same layers (proves the library is not modcheck-shaped):

```python
from rimdrive import Session
from rimdrive.plans import load_plan, apply_plan
from rimdrive.scenes import stage_review_grid, save_for_review

with Session(lock="rimflow") as s:            # take/release the bridge itself
    plan = load_plan("design/.../junkyard_shack.lua")   # offline lint+render first
    apply_plan(s, plan, at=(120, 140))        # chunked, map_commit last, read-back
    grid = stage_review_grid(s, options=four_gate_variants, pitch=18)
    save_for_review(s, "GATE_OPTIONS_2026-09-12", grid_key=grid)
    # save_for_review backs up keepers first, stats the Saves folder after,
    # and confirms a NEW file appeared (the saveName trap, 2026-08-24)
```

## 5. Migration — what happens to the 400+ one-shot scripts

The fresh-process pattern is not the problem (78 ms MEASURED); the ad-hoc raw
`RimBridge` use with no read-back is. Migration is by attrition, not rewrite:

- New throwaway scripts import L3 verbs; they get read-backs, litter tracking
  and pause discipline for free and shrink to a few lines. `Transient/` stays
  their home; they stay disposable.
- Raw `RimBridge` remains legitimate for pure READS and for the library's own
  internals. A raw WRITE outside the library becomes a review flag (a
  convention first; a hook only if attrition fails — no ceremony up front).
- The dozen persistent-connection tools (`apply_floor_plan`, lineups, replay
  scripts) migrate opportunistically when next touched, each deleting its
  hand-rolled connection/verify boilerplate.
- `load_session.py` keeps its job (the cold-load run-sheet) but its `Session`,
  census, settle and litter internals become rimdrive imports.

## 6. Risks and open questions (each with a recommendation)

1. **Name and location.** Recommend `src/RimMandrake/Utils/rimdrive/` (dev
   tooling — tier-naming exempt), with `modcheck` as a separate consumer
   package per its spec. Alternative — grow `rimbench/` in place — rejected:
   rimbench mixes the general Session with bench-specific map-authoring
   experiments, and its name says bench. rimbench becomes rimdrive's first
   consumer; its `core.py` empties by extraction. (Owner may prefer another
   name; nothing below depends on it.)
2. **Do the world-authoring tools move in?** Recommend: the world FAMILY of
   verbs (commit-paired writes, paginated reads) yes — it is generic
   discipline; the Ash'karr authoring scripts themselves stay siblings, they
   are campaign artifacts that CONSUME the library.
3. **Tool-surface rot.** The jawa/ census rots by design (91 tools 2026-08-19,
   "count it, never quote it"). Recommend runtime assertion over documentation:
   at connect, the session reads `tools/list` (already fetched for the param
   guard, 16 ms) and each domain verb declares the tools it requires; a
   missing tool fails AT CONNECT with the deploy hint, not mid-run as a
   mystery. No version numbers, no pinned counts anywhere in the library.
4. **Testing the library itself.** Three tiers, wired into `run_selftests.py`:
   offline selftest with a `FakeSession` (pattern exists in `load_session.py`)
   asserting call shapes and call-count budgets (rimbench `selftest.py`
   already asserts batching budgets — keep that discipline); a live selftest
   chain on the minimal-list quicktest (spawn → verify → sweep → pause-verify,
   ~a minute end to end); and the modcheck pit pilot as the integration proof.
5. **Unverifiable writes.** Recommend the §L2 rule (explicit `UNVERIFIED` in
   evidence, no silent True) — it changes rimbench behaviour and a reviewer
   should sign off on that deliberately.
6. **Concurrency.** One session per process, one bridge driver per project
   (rimflow lock); the library refuses a second concurrent Session in-process.
   Parallel subagents queue on the lock — the 2026-08-15 two-driver stall is
   the reason; no pooling, ever.

## 7. Rollout

Item shape (for BENCH to file on the owner's yes): RIMDRIVE_LIBRARY_BUILD_1 —
L1/L2 extraction + hardening with selftests; then MOD_VALIDATION_RUNNER_1
consumes it (its item already describes the extraction); L3 families land
verb-by-verb as consumers need them, each with its FakeSession test; L4b kits
land with their first real use. No big-bang rewrite of anything that works.
