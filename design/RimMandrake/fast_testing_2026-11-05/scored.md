# Fast testing: scored (phase 3 of 3), 2026-11-05

Scorer: a fresh Opus that wrote none of the ideas. Inputs: `ideas_inside.md` (40 concepts + Jev), `ideas_outside.md`
(42 concepts, sourced), `ideas_gpt.md` (38 concepts, sourced), all in this folder. 120 ideas merge into **29 distinct
mechanisms** (merge map at the end; every source idea is listed under exactly one mechanism, with its title).

## Verdict in one paragraph

The game is not the bottleneck; **the plumbing around it is**. The bridge is held 637-850 min a day and driven 31-79 min
of it (5-10%), the deterministic no-LLM lane (testq, SteveDesktop) already makes ~1,700 rows/day while Relentless makes
~65 measured rows/day, and the top three causes of wasted live time are an LLM doing deploy-and-restart, a 30-minute
6-proof pacing clock, and proof/criterion defects found only at run time. So the best bets are boring: move every
needs-bridge proof onto a no-LLM lane, make staging a Python state machine, drop the pacing clock, and lint at
authoring time. Those four are days of work and plausibly lift Relentless from 2.7 to 15-30 measured rows/hour
(INFERRED, not measured: see the plan for the measurement that settles it). The "go faster than real time" family is
real but has a hard ceiling found in this pass: **our bridge's `step_game_ticks` runs one tick per Unity frame**, so
exact stepping is frame-bound (measured 60-280 ticks/s); breaking that needs an in-frame tick-burst tool, which the
repo already does inside individual proofs. Learned players, world models and headless engines are moonshots whose
value is mostly hype at this project's scale.

## Measurements re-checked (2026-11-05)

| claim (source) | verdict | evidence |
|---|---|---|
| Relentless 912 rows, 230 PASS+FAIL in 84.6 h = 2.7/h (inside §1.1) | **CONFIRMED** | `/home/mandrake/rm/relentless/live/runs.jsonl`: UNMEASURED 495, REFUSED 146, PASS 134, FAIL 96, none 41; first 2026-11-02T04:14Z, last 2026-11-06T03:01Z |
| "72 rows refused by the 160-char limit" on proof lines (inside §1.1, concept "Proof lint pre-flight") | **MISREAD — corrected** | The 160-char refusals are about the **criterion text truncated at 160 chars on the ledger** ("A1 is cut at 160 chars on the ledger and no prose holds the rest: a proof cannot be judged against a criterion"), not proof-line length. 97 such rows on 7 items (72 on `GRAFFITI_NORTHSTAR_GREEN_FULL_1`, 9 `SEABED_DESCENT_ASCENT_1`, 5 `FIREFOAM_DIAGNOSE_CANNOT_AIM_AT_FIRE`), all between 2026-11-02T13:53Z and 2026-11-03T05:07Z — none since. The helper finding "no 160-char proof-line limit" is consistent: the fix is "every criterion's full text lives in prose", and the gate retried the same item 72 times without learning, which is the real defect. |
| REFUSED "`$` builds command at run time" 33, flyer refusals 6 (inside) | CONFIRMED (33; flyer 13 across three wordings) | same file |
| Round pacing `round_max` 6, `round_every_s` 1800, `unmeasured_retry_s` 6 h | **CONFIRMED** | `src/RimMandrake/rimflow/relentless_live_round.py` line 89 `DEFAULTS` |
| Staging is an LLM session holding the bridge | **CONFIRMED** | `src/RimMandrake/rimflow/relentless_game.py`: `bridge_take("relentless staging %s: deploy and restart…")` then `fx.launch(…, stage_prompt(…), r["pilot_agent"], …)` |
| testq PASS 11,712 / UNMEASURED 5,439 / NOT_RUN 897 / FAIL 190 over 748 jobs | **CONFIRMED** | `D:\ClaudeWork\rimmandrake\testq\done\*.json` (748 files) |
| GSS not wired into testq | **CONFIRMED** | `src/RimMandrake/Utils/testq/wired_mods.json` `wired`: FlowWorks, Stillsand, Contagion, TerminalBiomes, FeverWood, EnvironmentalHazards |
| 70 GSS commits since 2026-10-17; last `proof_all` 119 rows 2026-10-16 | CONFIRMED (70; 119 rows) | `git log --since=2026-10-17 -- src/RimMandrake/GimmeSomeSlack`; `src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261016T192502.json` |
| GPT: public README says `step_game_ticks` = one tick per Unity update frame | **CONFIRMED for our deployed bridge** | The tool description inside `D:\ClaudeWork\rimmandrake\build\RimBridgeServer.dll` (literal-string read, `MEASURE_ALLOW_SCAN=1`): "Advance the paused game by an exact number of ticks, one tick per Unity update frame … Each requested tick is executed on a separate Unity update frame." Matches the measured ~600-2,800 ticks per ~10 s call (`skills/rimbridge/references/silent-failures.md`), i.e. **60-280 ticks/s**, an in-game day (60,000 ticks) in 3.5-17 min. |
| "No TPS benchmark on file" (inside §1.3) | PARTLY FALSE | the 60-280 ticks/s above is on file (dated 2026-09-12 and 09-21); a controlled benchmark (minimal vs full list, empty vs busy map) is still owed |
| In-process proofs are novel (inside "In-process C# test runner DLL", outside "In-process test runner") | **FALSE — precedent exists** | `RM_WebworkProof.cs`, `RM_WebworkSiegeProof.cs`, `RM_Building_TractionLance.cs` loop `Find.TickManager.DoSingleTick()` in-process; `RM_FirefoamAimProof.ProofAim` is called by one `jawa/static_call` from a proof line. The pattern works here; what is missing is a shared runner and result table. |
| Bridge utilization 4.9 / 10.1 / 5.6% | not re-run (read-only tool output cited by the inside helper) | `src/RimMandrake/Utils/northstar_driver/bridge_utilization.py --day` |
| Jev latency, cost, image support | not re-checked (no score above rank 20 depends on it) | `~/dev/Dispatch/providers/jev/docs/FINDINGS.md` |

One more hype check on the headline comparison: testq's 1,700 rows/day and Relentless's 65/day are **not the same
unit**. A testq row is one assertion of a mod suite (720 of 748 jobs are FlowWorks, 30% UNMEASURED); a Relentless row
is one acceptance criterion of one item. The 25x gap is real in plumbing terms but overstated as "value".

## Weights and scale

Each mechanism is scored 1-5 (5 = best) on:

| axis | weight | 5 means |
|---|---|---|
| speed-up potential (S) | 0.30 | multiplies measured rows/hour several-fold on its own |
| feasibility here (F) | 0.20 | Unity Mono, our bridge, our mods already show it works |
| effort (E) | 0.15 | ≤ 2 agent-builder days |
| scalability (Sc) | 0.10 | more mods and SteveDesktop gain with no per-mod work |
| risk/trust (R) | 0.15 | no new false-pass or flake path; no LLM required; never touches flyer flight |
| time to first value (T) | 0.10 | a measured gain within a week |

Composite = weighted sum (max 5). Speed gets the largest weight because it is the owner's ask; trust is weighted
equal to effort because a fast false PASS is worse than a slow true one.

## Ranked table

| rank | mechanism | S | F | E | Sc | R | T | composite |
|---|---|---|---|---|---|---|---|---|
| 1 | One no-LLM lane: route needs-bridge items to testq, GSS wired | 5 | 5 | 4 | 5 | 4 | 5 | **4.70** |
| 2 | Deterministic staging daemon | 5 | 5 | 4 | 4 | 4 | 5 | **4.60** |
| 3 | Continuous rounds, no 30-min pacing | 4 | 5 | 5 | 3 | 4 | 5 | **4.35** |
| 4 | Authoring-time lint and generated proof lines | 3 | 5 | 5 | 4 | 5 | 5 | **4.30** |
| 5 | Coded UNMEASURED routes | 4 | 5 | 4 | 4 | 4 | 4 | **4.20** |
| 6 | In-frame tick burst tool | 4 | 4 | 5 | 4 | 3 | 5 | **4.10** |
| 7 | In-process test runner | 4 | 5 | 3 | 5 | 4 | 3 | **4.05** |
| 8 | Proof cost ledger and throughput benchmark | 2 | 5 | 5 | 4 | 5 | 5 | **4.00** |
| 9 | Invariant monitors, log oracle, sometimes-assertions | 3 | 5 | 4 | 5 | 4 | 4 | **4.00** |
| 10 | Def-driven generated tests, wrapped vanilla Autotests | 4 | 4 | 4 | 5 | 3 | 4 | **3.95** |
| 11 | Commit-triggered suites with dependency-based reuse | 4 | 4 | 3 | 5 | 3 | 4 | **3.80** |
| 12 | Test plots: many proofs per map | 5 | 3 | 3 | 5 | 3 | 3 | **3.80** |
| 13 | Golden-state digests and save round-trips | 3 | 4 | 4 | 5 | 3 | 4 | **3.65** |
| 14 | Several windowed game instances per machine | 4 | 3 | 3 | 5 | 3 | 3 | **3.50** |
| 15 | Save-fork fixtures and in-memory rewind | 3 | 4 | 3 | 4 | 3 | 3 | **3.30** |
| 16 | Bisection and minimisation bots | 2 | 4 | 3 | 4 | 4 | 3 | **3.15** |
| 17 | Oracles: Python models and metamorphic relations | 2 | 4 | 3 | 3 | 4 | 3 | **3.05** |
| 18 | Mutation testing of proofs | 1 | 4 | 3 | 4 | 5 | 3 | **3.00** |
| 19 | Property-based and search-based scenario generation | 3 | 3 | 2 | 4 | 4 | 2 | **3.00** |
| 20 | Scripted autopilot colony and overnight soak | 3 | 3 | 2 | 4 | 3 | 2 | **2.85** |
| 21 | Clock jump instead of simulate | 3 | 3 | 3 | 3 | 2 | 3 | **2.85** |
| 22 | Jev small judgments in the loop | 2 | 3 | 4 | 4 | 2 | 3 | **2.80** |
| 23 | Retrospective queries over recorded telemetry | 2 | 3 | 3 | 4 | 3 | 3 | **2.80** |
| 24 | Headless game, containers, process checkpoint, game-as-library | 5 | 1 | 1 | 5 | 2 | 1 | **2.75** |
| 25 | Seeded determinism, replay and trace diff | 3 | 2 | 2 | 4 | 3 | 2 | **2.65** |
| 26 | Semantic UI assertions | 1 | 3 | 3 | 3 | 4 | 3 | **2.55** |
| 27 | Hot-reload of defs | 3 | 2 | 2 | 3 | 2 | 3 | **2.50** |
| 28 | Carved unit tests from live runs | 2 | 2 | 2 | 3 | 3 | 2 | **2.25** |
| 29 | Learned small player and world-model surrogates | 2 | 2 | 1 | 3 | 2 | 1 | **1.85** |

### Why each top-ranked mechanism scores as it does

- **One no-LLM lane.** testq already holds a warm game (load median 1 s), deploys in ~30 s and runs suites without an
  LLM. Relentless runs a parallel, slower lane for the same game. Routing every needs-bridge criterion with a proof
  line to testq (or making Relentless's round a testq client), and wiring GSS (whose `proof_all` is 119 rows in 7 min),
  is mostly configuration plus an adapter. SteveDesktop as the exact-mod-list host is the natural home. Risk: testq's
  own 30% UNMEASURED comes along; the lane must keep its verdict semantics.
- **Deterministic staging daemon.** Every step `stage_prompt()` asks an LLM to do is already a script
  (`deploy_custom_mods.py`, `modlist_swap.py`, `./game`). The measured idle gaps are dominated by 9-20 min staging holds.
  An LLM stays only for the state the machine has no rule for.
- **Continuous rounds.** A config change with a cap of 12 proofs/hour removed. Scored lower on scale because alone it
  only moves the ceiling: staging still limits it.
- **Authoring-time lint** (corrected scope): refuse at `file`/`close` time a criterion whose full text is not in prose,
  a proof line that builds its command with `$`, a flyer-flight criterion, a missing script, a mod not in the declared
  load; and generate the missing `live_proofs/<ID>.txt` for built items from the mod's suite (five built GSS items have
  none, so no lane can ever run them). Also: a refusal reason seen twice on the same item must stop the retry; 72
  identical refusals on one item is a loop, not a test.
- **Coded UNMEASURED routes.** "not deployed" (85) → deploy and retry now; "changed since built" (47) → rebuild queue;
  "not in running load" (30+) → park for that list; "proof exited 2" (231) → harness fixer with stderr. Today all wait
  6 h or go to an LLM worker.
- **In-frame tick burst.** A JawaBench tool that calls `Find.TickManager.DoSingleTick()` N times inside one frame
  (with a wall-time budget per frame and the real `ticksGame` re-read after) breaks the one-tick-per-frame ceiling.
  Already done ad hoc inside Webwork and TractionLance proofs. Trust cost: anything keyed to Unity `Update` or render
  frames (weather overlays read `TickRateMultiplier`, some mods animate per frame) behaves differently; GPT's "Sweep
  clock domains and tick phases" is the guard and must ship with it. Speed-up size is UNMEASURED: the first step is
  measuring it.
- **In-process test runner.** Generalise the `static_call` proof pattern into one runner with a result table, so a
  suite is one bridge call. High feasibility (precedent in our own tree and in RimTest Redux), moderate effort.
- **Proof cost ledger and throughput benchmark.** Not a speed-up itself; it is the instrument that tells whether the
  others worked, so it ranks high on trust and time to value.

## Groups

**Quick wins (days, each ≤ 2-3 builder days):** One no-LLM lane (GSS wiring is the first half-day); Deterministic
staging daemon; Continuous rounds; Authoring-time lint and generated proof lines; Coded UNMEASURED routes; In-frame
tick burst tool; Proof cost ledger and throughput benchmark; Invariant monitors (start with "no new red error from our
packageIds" as a free assertion on every run).

**Foundational bets (weeks):** In-process test runner; Test plots (many proofs per map, Minecraft GameTest style);
Commit-triggered suites with dependency-based reuse; Def-driven generated tests and wrapped vanilla Autotests; Golden
digests and save round-trips; Save-fork fixtures; Several windowed instances per machine (Steam, GPU memory and
`-savedatafolder` isolation must be proved first); Bisection and minimisation bots; Mutation testing of proofs.

**Moonshots (months, mostly research):** Headless/containerised RimWorld, process checkpoint (CRIU) and
game-as-library; seeded determinism with replay and trace diff (RimWorld is not deterministic without
Multiplayer-mod-level work); learned small players, world models, DAgger/HER/MAP-Elites/curriculum generators;
autopilot colonies driven by Jev; carved unit tests.

## Combinations that multiply

1. **Staging daemon × continuous rounds × authoring lint × coded routes.** Each alone is capped by the others (a
   continuous round with an LLM stager still waits 9-20 min; a fast stager still waits 30 min for the clock; both
   still burn rounds on refused or undeployable lines). Together they turn the 5-10% utilization into the real
   constraint, which is proof wall time.
2. **Test plots × in-process runner × tick burst × invariant monitors.** One load runs many proofs at once, each a
   single bridge call, ticking faster than frame rate, and every tick also checks every invariant. This is the only
   combination that changes the unit cost of a proof by an order of magnitude, and the only one that needs the
   isolation check (GPT's "Deliberately hunt contamination between tests").
3. **Commit-triggered suites × golden digests × bisection bot.** A regression is detected on the commit that caused
   it, pinned to a field diff, and bisected to a sha with no LLM in between; the builder receives a sha and a diff.
4. **One no-LLM lane × SteveDesktop exact-list host × windowed instances / load pools.** Two machines, each holding
   warm loads, fed from one queue: throughput scales by machines before any code gets faster.
5. **Def-driven generated tests × mutation testing.** Generated rows are cheap and shallow; mutation testing is what
   stops them inflating row counts without catching anything.

## Sequenced plan (top 8)

Order is chosen so each step's measurement is readable on the instrument the first step builds.

1. **Proof cost ledger and throughput benchmark.** First step: add `wall_s`, `ticks`, `stage_s` and `lane` to every
   Relentless and testq row, and run one benchmark of `step_game_ticks` ticks/s on the minimal and full list, empty
   and busy map. Proves it worked: a daily table of measured rows/hour per lane and ticks/s per list, reproduced on two
   days.
2. **Authoring-time lint and generated proof lines.** First step: run the existing round's refusal checks at
   `rimflow file`/`close` time, plus "a refusal repeated twice on one item stops retrying". Proves it: REFUSED rows per
   day drop to near zero (from 146 in 3.5 days) with no rise in UNMEASURED.
3. **Continuous rounds.** First step: set `round_every_s` to 0-60 and `round_max` to "until the eligible set is empty
   or the load changes", behind the existing supervisor. Proves it: proofs per bridge-held hour rise; no new bridge
   collisions in the journal.
4. **Deterministic staging daemon.** First step: replace `fx.launch(stage_prompt(...))` with a Python function that
   runs deploy plan → apply → `modlist_swap.py` → restart → wait-up, calling an LLM only on an unhandled exit. Proves
   it: median staging hold falls from 9-20 min to cold-load time (22-54 s minimal list), and bridge active/held rises
   from 5-10% toward the 31% pre-Relentless figure or above.
5. **One no-LLM lane, GSS first.** First step: add GimmeSomeSlack to `wired_mods.json` with its minimal list and run
   `proof_all` on the current build on SteveDesktop. Proves it: a dated GSS `proof_all` result on the current sha
   (none since 2026-10-16), then one per GSS commit.
6. **Coded UNMEASURED routes.** First step: map the four largest `why` buckets to routes and log each route taken.
   Proves it: UNMEASURED share of Relentless rows falls from 54%, and the median time from UNMEASURED to the next
   measured row on that item falls from hours to minutes.
7. **In-frame tick burst tool.** First step: a `jawa/tick_burst` tool with a per-frame wall budget, benchmarked
   against `step_game_ticks` on the same map, plus a same-scenario comparison (burst vs stepped) on three existing
   proofs. Proves it: ticks/s multiple measured, and the three proofs give identical verdicts both ways.
8. **In-process test runner.** First step: lift the `RM_FirefoamAimProof`/Webwork pattern into one `[RMTest]` runner
   returning a row table, and port one mod's suite. Proves it: that suite's wall time and bridge-call count before
   and after, same verdicts.

Next after these: Test plots, Invariant monitors, Commit-triggered suites. Estimated combined effect of steps 2-6:
Relentless from 2.7 to 15-30 measured rows/hour (INFERRED from the removed waits; step 1 measures the truth).

## Hype check

- **Row counts are not value.** Generated and def-driven tests can make a counter go up 100x while finding nothing;
  pair every row-count gain with a found-defect count and mutation scores.
- **"Faster than real time" is frame-bound today.** One tick per frame is confirmed in our bridge DLL. Every soak,
  clock-jump and autopilot estimate must use 60-280 ticks/s until the burst tool measures better. An 8-hour night is
  then 1.7-8 million ticks, 29-134 in-game days per instance: useful, not "years".
- **Jev is not a test oracle.** Its own findings: confidence runs backwards, it cannot count or compare numbers, and the
  shadow log meant to calibrate it never accumulated. It fits routing and triage after code has decided the verdict.
- **Learned players are the Doom result transplanted to a game of indirect control.** RimWorld's own job AI already
  plays the colony; a scripted policy over a handful of menus captures most of the testing value at a fraction of the
  cost. Score kept lowest.
- **Headless and determinism are other people's multi-year projects.** HeadlessRim and RimWorld Multiplayer exist, but
  adopting either across 300 mods is a research programme, and both change the thing under test.
- Owner rules hold throughout: no mechanism here live-tests a flyer's flight, and none needs an LLM in the loop.

## Merge map (120 source ideas → 29 mechanisms)

Sources: **in** = `ideas_inside.md` §3, **out** = `ideas_outside.md` §2 (links in its §3), **gpt** = `ideas_gpt.md`
(links inline there). Source numbers are cited with their titles.

- **One no-LLM lane:** in C08 (Wire GSS into testq), in C28 (Two machines, both used), in C27 (Load-list pools),
  out 4 (The always-on test colony; Gauntlet, Factorio test server), out 6 (Mod-list tiers as test sizes).
- **Deterministic staging daemon:** in C01 (Deterministic staging daemon), in C06 (LLMs only at the edges), out 37
  (Main-thread heartbeat and hang watchdog; RimDevTools), out 38 (Transactional environment edits; RimDevTools).
- **Continuous rounds:** in C02 (Continuous rounds instead of a 30-minute, 6-proof cadence), in C03 (Resident proof
  server).
- **Authoring-time lint and generated proof lines:** in C04 (Proof lint pre-flight; scope corrected above), in C09
  (Auto-generated proof lines for built items), in C34 (SDE cascade for proof authoring), out 3 (A Python spec DSL,
  compiled not authored; Rimworld-Pickle, RimWorldTestHarness), gpt 20 (Test bridge client contracts without reserving
  RimWorld; Schemathesis).
- **Coded UNMEASURED routes:** in C05 (UNMEASURED auto-triage with fixed routes), gpt 07 (Solve fixture feasibility
  before touching the game; Scenic, Z3), gpt 21 (Plan setup repairs from preconditions; GOAP).
- **In-frame tick burst tool:** in C11 (TPS benchmark, then a tick budget per proof; benchmark half moved to the cost
  ledger), in C13 (Headless or render-off ticking), out 35 (Uncapped tick speed for tests; ML-Agents time_scale),
  gpt 24 (Sweep clock domains and tick phases; the trust guard).
- **In-process test runner:** in C20 (In-process C# test runner DLL), out 36 (In-process test runner, Python only
  orchestrates; RimTest Redux, DFHack, Unreal functional tests).
- **Proof cost ledger and throughput benchmark:** in C39 (Proof cost ledger), in C11 (benchmark half), gpt 33 (Find the
  throughput limit without hiding overload; k6 open models).
- **Invariant monitors, log oracle, sometimes-assertions:** in C21 (Invariant monitors that run every tick), in C38
  (Perf budget gate), in C35 (Test the owner's own play), out 14 (Always-on invariant monitor; TigerBeetle,
  Antithesis), out 15 ("Sometimes" assertions as coverage; Antithesis), out 18 (Log as oracle, budgeted), gpt 19
  (Reconcile transactions rather than final totals; cocotb scoreboards), gpt 34 (Amplify lifetime leaks through rapid
  teardown cycles).
- **Def-driven generated tests:** in C25 (Def-driven test generation), out 17 (Def-derived expectations), out 20 (Def
  fuzzing), out 21 (Wrap the vanilla Autotests; Dev mode Make Colony), out 41 (Specs from the def files themselves).
- **Commit-triggered suites with dependency reuse:** in C07 (Commit-triggered suite), out 34 (Containerised test image;
  CI half), gpt 17 (Reuse evidence according to actual dependencies; Ekstazi), gpt 01 (Stop stochastic tests when the
  evidence is sufficient; Fishtest SPRT).
- **Test plots:** in C17 (Many scenarios per map, many maps per game), in C14 (Minimal map per proof), out 1 (Test
  plots on one map; Minecraft GameTest), out 2 (Proof structures as saved blueprints), gpt 15 (Deliberately hunt
  contamination between tests; pytest-randomly — the isolation guard).
- **Golden-state digests and save round-trips:** in C19 (Golden-state diffs), out 10 (Golden state snapshots; Verify,
  insta), out 23 (Save/load round-trip on everything), gpt 35 (Test historical save migrations as versioned edges).
- **Several windowed instances:** in C26 (Several game instances on one machine), out 33 (Headless RimWorld instances,
  many at once; windowed half).
- **Save-fork fixtures and rewind:** in C15 (Save-fork fixtures), in C16 (In-memory snapshot and rewind), out 8
  (Snapshot and fork; Antithesis, stable-retro), gpt 04 (Clone trajectories as they approach rare failures; adaptive
  multilevel splitting).
- **Bisection and minimisation bots:** in C10 (Bisection bot), gpt 13 (Minimize the offending mod set; weighted delta
  debugging), gpt 14 (Test competing Harmony patches as critical pairs), gpt 16 (Localize faults from passing and
  failing coverage; GZoltar).
- **Oracles:** in C22 (Oracle per mod), out 13 (Metamorphic relations for mods), out 16 (Python shadow model), gpt 03
  (Use a surrogate as a statistical control variate; multifidelity Monte Carlo), gpt 32 (Identify behavior with
  designed input pulses; SIPPY).
- **Mutation testing of proofs:** in C24 (Mutation tests for the proofs themselves), out 26 (Mutation testing for our
  proofs; Stryker.NET), gpt 36 (Check that test shortcuts preserve the gameplay path).
- **Property-based and search-based generation:** in C23 (Property-based fuzzing of our mods), out 19 (Stateful PBT
  over the bridge; Hypothesis), out 24 (Curiosity explorer; EA SEED), out 25 (Coverage via Harmony call counters; CA2),
  out 22 (Chaos storyteller; Jepsen), gpt 05 (Oversample dangerous conditions and correct their weights), gpt 06
  (Search for the smallest safety margin; PSY-TaLiRo, RTAMT), gpt 08 (Feed comparison operands back into the fuzzer;
  AFL++ CmpLog), gpt 09 (Cover interactions without enumerating every configuration; NIST ACTS), gpt 10 (Skip
  equivalent action orderings; SPIN POR), gpt 11 (Deduplicate equivalent network shapes; SPORE), gpt 12 (Turn abstract
  counterexamples into live scenarios; SPIN), gpt 38 (Search for the most plausible failure sequence; adaptive stress
  testing).
- **Scripted autopilot colony and overnight soak:** in C29 (Jev autopilot colony), in C36 (Overnight soak farm), out 39
  (Test-the-tests mode: the game plays itself overnight; Paradox, Ubisoft), out 31 (Persona bots for playtesting).
- **Clock jump:** in C12 (Clock-jump instead of simulate), out 12 (Time-skip with checkpoints).
- **Jev small judgments:** in C30 (Jev failure triage), in C31 (Jev frame check), in C32 (Jev stuck detector), in C33
  (Jev picks which fuzz runs a reasoner reads), out 30 (Small judge models for "does it look right").
- **Retrospective telemetry queries:** gpt 18 (Ask new questions of old executions; NASA F´ history search).
- **Headless, containers, checkpoint, game-as-library:** in C40 (The game as a library), out 33 (headless half;
  HeadlessRim), out 34 (Containerised test image; image half), gpt 22 (Restore a booted process instead of loading a
  save; CRIU).
- **Seeded determinism, replay, trace diff:** in C18 (Record and replay), in C37 (Differential testing across builds),
  out 7 (Seeded deterministic runs; FoundationDB, rwmt), out 9 (Desync-style trace diff), out 11 (Input-log replay of
  owner playtests), gpt 02 (Pair builds with independent streams for external events).
- **Semantic UI assertions:** gpt 37 (Assert UI meaning instead of matching whole screenshots; AltTester, Poco).
- **Hot-reload of defs:** out 5 (Hot-reload instead of reload).
- **Carved unit tests:** gpt 23 (Carve fast unit tests out of live executions).
- **Learned small player and world models:** out 27 (RimWorld gym over the bridge; RLE), out 28 (Tiny policy trained on
  our own runs; Doom 1.3M), out 29 (Skill library, LLM only at the edges; Voyager), out 32 (World-model surrogate for
  triage; GameNGen), out 40 (Benchmark our harness on RLE), out 42 (Diffusion "what should it look like" oracle), gpt 25
  (DAgger), gpt 26 (Hindsight relabelling), gpt 27 (MAP-Elites repertoire), gpt 28 (Scenarios by disagreement between
  players), gpt 29 (Compile a learned player into a decision tree; VIPER), gpt 30 (Learn the owner's preferences
  between play sequences), gpt 31 (Train in a cheap approximation, then transfer).

Count check: inside 40 + outside 42 + GPT 38 = 120; inside C11, outside 33 and outside 34 are split across two
mechanisms each, so 123 placements.
