**I would move FlowWorks playtesting into a small, in-process scenario runner, and make its main product a short failure report plus one prepared review save.** Keep the existing fast arithmetic tests. Use RimBridge to start runs, collect artifacts and navigate the review map. Give a player-like agent a separate, bounded exploration role later.

The decisive change is the unit of work: **a player episode with observable consequences**, such as “designate a trench, let a pawn dig it, admit tar, trap someone, ignite it, save, reload and continue.” Today the machinery is much better at certifying individual predicates than at establishing that those predicates compose into the intended game.

I reviewed the supplied snapshot only. Proposed build costs and future timings below are estimates, not measurements.

**1. Diagnosis**

The current method rewards completing its own declarations, fixtures and evidence plumbing. Those are necessary prerequisites, but they have become a large competing product.

| Measured evidence | What it establishes |
|---|---|
| `flowworks_size_table.md`: 87 commits touched harness/review tooling; 74 touched mod code/art, with overlap | Tooling changes are at least as frequent by this approximate measure. It does **not** establish an hours ratio. |
| Same table: 794 KB of Python, versus 843 KB of C# | The surrounding machinery is substantial. The Python total includes the production generator and art tools, so it is not all testing overhead. |
| `northstar_time_ledger_extract.md`, §2: 84.7 of 210 minutes failed setup gates; another 64 minutes were lost or voided | Historically, approximately 71% of that session bought no accepted behavior proof. |
| `latest_results_trimmed.md`: current core is 59/59 PASS, 251.1 seconds, 872 calls | The core has already become reasonably fast. The historical 21–35-minute FlowWorks run is no longer the current baseline. |
| Same result: `P_pits` 104 seconds; `X_promoted` 80.99 seconds | Together they consume approximately **74% of current wall time and 91% of ticks**. RPC batching alone cannot remove most of this run. |
| `validation.py` and `extensions.py` | Pumps, prison service, refill, bottles, machinery and river behavior are substantially outside the default core. “Every mechanism row” means every selected core row, not every shipped mechanic. |
| FOUNDRY’s GSS handoff: defects that round came from the owner looking | For that round, the human review exposed defects the automated checks missed. It does not prove automation is generally ineffective. |

**My inference:** agents can make reliable progress on bounded, self-authored checklists. Player experience is harder to specify and often absent from the default run, so effort flows toward the tractable tooling work. Every investigation also creates more permanent machinery: mock faults, guards for discarded theories, coverage mappings, status derivation and presentation rules.

I disagree with this morning’s review’s priority. Durable evidence matters, but **repairing the project-wide scoreboard should not be FlowWorks’ first experiment**. It could accurately count the current narrow proof while the owner still encounters a bad game. The latest core already records a loaded DLL SHA matching the repository DLL and `mvidMatchesFile=True`; the supplied walk now names a checkout/result integration path. Those newer facts limit the earlier diagnosis.

There are more valuable experiments directly in the supplied code:

- **Touching liquids:** `RM_LiquidStock.FormBody()` expands through any `owner.IsSourceCell(n)`. It contains no same-fluid or same-suite boundary test. If adjacent water and tar terrains both satisfy `IsWater`, they can become one body carrying the seed’s fluid. That is a source-level finding; the precise live consequence still needs reproduction.
- **Reload changes scarce allocation:** `RM_MapComponent_Excavation.DoPulse()` explicitly documents insertion/dig order during play and cell-index order after load. Two channels competing for the last units can therefore receive different allocations after reload.
- **Two representations of liquid:** `Flood_FlowWorks.PlaceFluid()` writes temporary terrain without updating excavation F or fluid identity. The grid-based flow, pump and fire paths can consequently disagree with the visible release. Test their composition.
- **Detonation consumption:** `RM_LiquidFire.AdvanceFront()` causes explosions, but the shown `BurnPulse()` applies the slow burn calculation to excavated cells regardless of fire kind. The shown code does not implement the design’s immediate consumption for detonating liquids.
- **A probe repairs its subject:** `RM_NorthstarProofs.ProofWallFaces()` calls `layer.Regenerate()` before observing geometry. It cannot establish that ordinary play invalidated the mesh correctly.

These are test targets, not claims of live-confirmed defects.

**2. Three different approaches**

**Approach A — In-process player episodes. My preference.**

Compile a dev-only scenario runner into the JawaBench companion assembly, with narrow internal hooks where necessary in FlowWorks. It runs after a disposable map has finished loading.

Use a **static controller**, not a new serializable `MapComponent`. It should cooperatively advance through phases on the main thread, allowing ordinary ticks and rendering between them. Do not put a long simulation loop inside one bridge call.

Its external interface can be tiny:

```text
Start(recipe, seed) → run ID, immediately
Status(run ID) → phase, completed results, last progress
Collect(run ID) → report and artifact paths
```

It can also auto-start from a local recipe at load, without a bridge client. RimBridge remains useful transport; Northstar’s Python chain/plot machinery ceases to be the execution structure.

Concrete reuse and changes:

- Reuse the production APIs on `RM_MapComponent_Excavation`, `RM_LiquidStock` and `RM_LiquidFire`.
- Reuse fixture knowledge from `site_spec.py`, `validation_v2.py` and the existing proof classes.
- Put scenario controllers in a proposed `JawaBenchFlowWorksScenarios.cs`.
- Give `RM_NorthstarProofs` a **read-only snapshot** operation. Keep `ProofResetRect` for setup, but distinguish it from observation.
- Turn `review_map.py` into a thin launcher/navigation helper. Reuse its labels, keeper-save verification and free-area setup.
- Replace migrated live orchestration in `validation_v2.py`, `extensions.py` and `extensions_rivers.py`. Keep their useful assertions until their replacement detects the relevant fault.

The first scenario catalogue should be episodes, not one scene per toggle:

| Episode | What executes through the real game |
|---|---|
| Dig and undo | Designate, autonomous work selection, dig, deepen a wet cut, fill in, restore original terrain |
| Pond and canal | Limited supply, branching channels, recession, refill, edge drainage |
| Two-fluid boundary | Touching bodies, opposing fronts, rain, pumping and displacement across the boundary |
| Liquid logistics | Construct and power a pump/tank connection; fill containers; convert liquid; exercise blocked output |
| Pit and prison | Walk/jump/fall in, hold, raise/lower ladder, capture down, feed/tend/convert from the lip |
| Fire defense | Real flame trigger, nonflammable control, travelling front, source ignition, foam/rain, replenishment, detonation |
| River crossing | Ordinary scheduled shoves, ford/ferry exemption, flood, weir catch/breach, levee gap |
| Persistence and load | Save these states mid-operation, reload, continue and compare |
| Appearance | Controlled depth/fill/material boards and short edge-crossing sequences |

The distinction from current proofs is **stimulus → actual outcome**. `ProofLip()` saying a lip can be found is insufficient: a real feeding job must deliver food while the warden stays outside. Calling `StepOne()` proves a shove operation; a scheduled crossing must additionally prove registration, timing and continued movement.

Direct invocation remains excellent for algorithm transitions and long-duration rate calculations. Pair it with a few scheduler checks. Never label clock scrubbing or shortened burn settings as a day of ordinary play.

**Coverage:** this approach can automatically cover every functional item in the owner’s list, subject to the scope table below. It screens appearance and balance for the human. It misses broad emergent colony behavior unless episodes deliberately include it.

**Estimated cost:** 1–2 agent-days for a falsifiable pilot; 5–8 for useful coverage of the owner’s list; further optional-mod integration is separate. Target **3–6 warmed live minutes**, including persistence and a small performance sample. That target must be measured: changing execution location does not make required game ticks disappear.

**Failure modes:** fixtures bypass player entry points; observers call the same predicates they supposedly verify; the controller becomes a generic scenario language; one scenario contaminates another.

**Containment:** ordinary C# methods, a fixed catalogue, setup-only shortcuts clearly marked, outcome assertions against actual game state, and no framework extraction in week one. Reset recipes must include bodies, fire queues and global settings—not merely D/F and terrain.

**Delete after replacement:** golden-trial preparation/preflight machinery from the default route, duplicate Python live phases and their redundant transport mocks. Preserve production regression cases and the owner’s vision.

---

**Approach B — Execute the production liquid core offline, with generated action sequences.**

This abandons live playtesting for the largest algorithmic surface.

The repository already has the right beginning: `Source/SelfTest/Program.cs` compiles production files such as `RM_StockMath.cs`, rather than testing a transcription. Extend that discipline.

Initially generate sequences against existing production helpers:

```text
dig → pour → pulse → pump → fill in → refill → burn → drain
```

Check independent requirements: bounds, compatible fluids, accounted transfers, restoration, progress under declared conditions. Keep failing seeds and reduce them to short cases.

For whole-engine coverage, make a **small production extraction** from:

- `RM_MapComponent_Excavation`: component resolution, flow ordering and donor selection;
- `RM_LiquidStock`: body traversal, bookkeeping and recession selection.

A proposed `RM_FlowStep.cs` should operate on arrays and explicit inputs, with Verse adapters supplying terrain identity, weather and cell indexing. Both game and tests execute that production implementation.

Do **not** build fake regions, fake pawns, fake Unity rendering or a headless RimWorld.

Reuse `PulseOracle` as a diagnostic comparator and preserve its known oscillation/shared-source examples. It is a port of the implementation; matching it is weaker evidence than satisfying an independently stated property.

**Coverage:** excellent for flow, stocks, depth/fill combinations, viscosity scheduling, no-mix arithmetic, refill and conservation. It tests pit-width, river-cadence, fire-rate and conversion arithmetic. It cannot prove that Harmony patches run, pawns finish jobs, rooms form, Unity renders correctly or Scribe restores state.

**Estimated cost:** 2–3 agent-days for generated tests over existing helpers; approximately 6–10 for a careful whole-flow extraction and adapter verification. **Zero live minutes per offline run.** Allow a 2–5-minute live adapter check after relevant changes, plus review-save preparation.

**Failure modes:** refactoring destabilizes the mod; the fake environment becomes the product; tests establish an invented physics model; properties accidentally demand symmetry the design does not promise.

For example, arbitrary construction-order invariance is currently false for scarce shared supply. Test conserved quantity and legal allocation; separately decide whether that ordering policy is acceptable. Mirror tests should use fixtures where the declared rules actually predict equivalent results.

**Reuse/delete:** extend the C# selftest project and reuse existing math. After adapter agreement, remove redundant per-pulse Python comparisons from routine live runs. Retain a few real engine checks. Do not enlarge `fakegame.py` into a gameplay simulator.

This approach is valuable, but I would not begin with the full extraction. The owner’s present pain includes art, jobs and prison behavior that it cannot settle.

---

**Approach C — A bounded agent plays ordinary FlowWorks goals.**

Give an agent a prepared colony and a goal, with no mechanism-changing privileges after setup:

- Build a defensive canal using ordinary designation and construction.
- Store and move liquid using the available UI.
- Capture and service a prisoner in a pit.
- Cross a river safely.
- Recover after a mistaken dig or fill operation.

Use RimBridge’s Architect, selection and gizmo surfaces, supplemented by screen interaction where necessary. Keep an action transcript and periodically collect authoritative state. Stop at the first meaningful obstacle and save a reproducible checkpoint.

The agent must encounter actual affordances. Calling `Deepen()`, setting tank stock or invoking `ProofIgnite()` would invalidate the player-like claim.

Keep the driver separate from `validation_v2.py`. Reuse `review_map.py`’s supplied materials and calm setup. The files primarily under test become `Designator_*`, `WorkGiver_*`, `JobDriver_*`, buildable gizmos, translations and refusal messages.

Measure friction concretely:

- failed or ambiguous placement attempts;
- actions and menu searches to accomplish a goal;
- jobs accepted but abandoned;
- unexpected state changes;
- recovery steps;
- missing explanation for a refusal.

**Coverage:** strongest for discoverability, designation, construction, work priorities, logistics and prison workflows. It can explore all the owner’s mechanics but cannot systematically certify them. It screens visual problems; it does not supply reliable taste or balance judgment.

**Estimated cost:** 1–2 agent-days for a pilot using existing capabilities; 3–5 for reliable transcripts and checkpoints. Budget **15–30 live minutes per bounded session**. Longer open-ended play could easily take an hour.

**Failure modes:** expert source knowledge hides discoverability problems; the agent blames its own input errors on the game; “friction” becomes verbose opinion; screen automation creates another harness.

**Containment:** fixed goals, a session deadline, no self-modifying driver, explicit attribution of automation failures, and replayable reports. A friction finding becomes a regression test only after reproduction.

**Reuse/delete:** reuse player-facing bridge tools and setup helpers. No need to delete Northstar to pilot this approach, but do not duplicate its functional gates inside the player agent.

**3. Coverage of the owner’s entire list**

This is the responsibility split for the preferred design. It also states the limits of the alternatives.

| Required area | A: automatic episode checks | B: offline coverage | C: player exploration / human question |
|---|---|---|---|
| Flooding and canal flow | Scheduled flow, confinement, legacy release expiry/restoration, branches and sinks | Flow transitions, bounds and progress | Is the front understandable and useful? |
| Pumps, pipes, tanks, converters | Real powered transfer; capacity, wrong-fluid and blocked-output cases | Transfer/conversion arithmetic | Placement, connection and operation friction |
| Liquid types and two-fluid interaction | Separate bodies; opposing fronts; drain/reclaim; rain and displacement | Compatibility and per-fluid accounting | Are substances distinguishable? |
| Differing viscosities | Matching channels under equal **actual ticks**, plus stride checks | Cadence/stride boundaries | Do speeds communicate different liquids? |
| Designating canals/pits, digging/building | Designator acceptance and refusal; autonomous worker; real construction | Depth/work arithmetic only | Orders, feedback and interruption feel |
| Filling back in | Occupied refusal, displacement, overflow disclosure, exact terrain restoration | Bounds and displacement arithmetic | Is the consequence clear? |
| Different terrains / embedding | Soil, sand, mud, natural rock, floor, foundation, wet cut and edifice acceptance table | Contract checks, limited adapter coverage | Material appearance and unexpected restrictions |
| Quarry, mining sluice/panning | Real dig completion; local finds; exploit guard; first-find letter | Discovery math and repeated-cut sequences | Reward pacing; panning/sluice-box experience when built |
| Trapping and prisoner behavior | Spawned/alive pawn; attempted exit; width, faction, jumper, cover, ladder, door, room/bed; actual lip jobs | Width/trap predicates only | Confinement readability, cruelty and usability |
| Ignition by appropriate flame | Real Fire/Flame stimulus, water control, source spread, extinguishing and detonation consumption | Eligibility, rates and front math | Fuse speed, burn appearance and threat |
| River force pushing | Real river flow grid, ordinary scheduler, current/flood strength, ford/ferry and washed-away continuation | Quantization/cadence/hazard arithmetic | Force, warning and safe-crossing feel |
| Refill | Stock gain, capacity clamp, reverse restoration, rain/season inputs | Rate integration | Does recovery time support the defense loop? |
| Varying fill and canal depth | Every legal D/F pair; path cost and applicable occupant effects | Exhaustive small-state arithmetic | Can depth and fill both be read? |
| Shallow/deep liquid behavior | Actual traversal, deep trapping/drowning distinctions | Movement/effect calculations | Shallow looks shallow; deep looks deep |
| Art, perspective, layering/clipping | Resource/material checks; geometry bounds; stationary-camera transitions | Geometry/math only | Perspective, coherence, readability |
| Pawn versus edge | All entry/exit directions; held exit attempts; lip bystanders; sinking/shadow checks | Draw/trap math | Clipping during motion and believable depth |
| Saving/loading | Actual Scribe round trip **and continuation** | Core-state serialization if extracted; not Scribe | Visible reconstruction |
| Performance | Flow pulse, ordinary tick, frame/render, save/load samples | Core cost/scaling | Noticeable hitching on the real stack |

Panning and the mining sluice box are dependency-blocked in `flowworks_remaining_2026-10-05.md`. Report them as **not available to test**, with the dependency. Do not construct empty review pads or claim coverage because `RM_Sluice` exists: that is the gate, a different feature.

**4. Evaluate the four proposed outputs**

| Output | What it catches | Cost and prerequisites | Worth it here? |
|---|---|---|---|
| **(a) Ranked failures + one prepared human-only review save** | Machine-detectable regressions; owner settles residual appearance, feel and balance | A supplies reproducible episodes and scenes. B can contribute seeds; C contributes friction checkpoints. Target 1–3 additional minutes to assemble from existing recipes, plus 10–15 human minutes | **Yes. Make this the primary deliverable.** |
| **(b) Player agent reporting friction** | Missing affordances, misleading feedback, awkward workflows and recovery | C; approximately 15–30 live minutes per session, then agent triage | **Yes, selectively.** Especially after functional episodes pass |
| **(c) Pass/fail on every build** | Fast regressions, build errors and known arithmetic faults | Existing C# tests/B every build. Selected A episodes on deployed builds | **Yes, with bounded claims.** No full-list checkout every build |
| **(d) All three layered** | Broadest coverage, with each instrument addressing a different uncertainty | Requires scheduling, not three duplicated full suites | **Eventually yes.** Do not build all three systems in week one |

For (a), rank **root causes**, not failing rows:

1. Lost/corrupted state, crash, duplication or unauthorized fluid conversion.
2. Broken player loop: jobs, imprisonment, flow or transfer.
3. Visual correctness: clipping, missing rendering, stale visible state.
4. Experience/tuning questions.
5. Coverage gaps and environmental failures, explicitly distinguished from mod defects.

Each failure needs expected/actual, build identity, shortest reproduction and evidence. Ten downstream failures caused by one missing prisoner are one finding.

The owner should receive the full ranked list, but the save should contain **only judgment scenes**. Agents handle mechanical debugging. A human station should not ask him to wait and discover whether a pump works.

For (c), distinguish:

- **Every build:** compile and fast production tests.
- **Each deployment candidate:** relevant player episodes and an ordinary scheduler sentinel.
- **Periodic complete episode run:** all required functional areas.
- **Release candidate:** the actual canonical list and its identified build.

A scoped green is useful. “Everything works” from a narrow green is harmful.

For (d), run the player agent when there is a question it can answer: after a workflow change, an owner friction report or a milestone. Running it on every arithmetic edit spends the scarce game instance poorly.

**5. Visual checks: what machines can actually decide**

Three levels of evidence should remain separate.

**Deterministic machine checks**

- Texture/shader resolves; no `BadGraphic`; intended terrain uses the intended material.
- Wall geometry is finite, bounded and present at the correct boundaries.
- Render depth/queue and shadow-suppression conditions match their contracts.
- Pawn draw offset changes continuously and returns to the expected position.
- Fill selects the correct terrain tier.
- Ordinary mutations dirty the relevant section.
- Capture identifies the correct map, camera, tick and rendered frame.

These establish render contracts. They do **not** establish a convincing pit.

**Screenshot checks with explicit uncertainty**

Controlled frames can detect gross regressions: missing subjects, magenta placeholders, unexpected overlays, visible spill outside a boundary, a stationary image where a declared transition should change it.

Use fixed camera and lighting, bounded regions and a known-good owner-approved reference. Mask UI and deliberately animated regions where appropriate. Image differences are a screening signal; they do not automatically mean “worse.”

If recurring clipping warrants it, add a small diagnostic capture using isolated pawn/lip silhouettes to measure pixels surviving outside a specified occlusion band. That can establish a narrowly defined overlap defect. Building a general segmentation system would be poor first-week work.

**Human judgments**

- Does the pit look deep rather than like a tile treatment?
- Does its perspective agree with RimWorld?
- Can the player distinguish depth from fullness?
- Does tar look wet and thick?
- Is the submerged pawn still findable?
- Does edge crossing look physically believable?
- Is the faint ghost from lip transparency acceptable?
- Do speed and danger feel right?

There are unusually specific high-risk cases in this code:

- `RM_PitLipOcclusion` documents that its band can hide a pawn/item standing **on the lip**. Stage a sunk pawn and a lip bystander together.
- It skips occlusion during some depth-changing movement. Capture entry/exit in every direction and at corners.
- `RM_LiquidSurface` uses real-time animation. A paused game can still animate; game tick alone does not identify animation phase.
- Camera movement can regenerate sections. Capture a mutation **without moving the camera or calling a refresh**, then reframe afterward. A defect repaired by reframing is a finding.

Also fix the review matrix:

`review_map_visuals.fill_level()` uses F=D−1, except at D1. Across D1–D4 it therefore shows brim, half, half and brim. That confounds depth and fill. The key’s “D2: empty, trace, half, brim” is impossible: at D2, F is only 0, 1 or 2, mapping to dry, half and brim.

Show all **14 legal excavated D/F pairs**, grouped into a few comparison boards. Compare depth at fixed F, and fill at fixed D. Add soil/stone neighbors, water/tar/slime controls and empty/occupied twins. The owner can judge many cells in one view without walking 34 individual stops.

**6. The human sitting**

Aim for **10–15 minutes**, with an optional five-minute free-play area.

The owner receives:

- a one-page ranked failure report, with at most five items expanded;
- one named keeper save, already verified by loading it;
- a plain key containing approximately **8–12 judgment stops**;
- short captured motion sequences for transitions that would otherwise require waiting;
- an automatically selected first stop and working in-game navigation.

Suggested stops:

1. Depth and legal fill comparison boards.
2. Soil/stone material and multi-cell perspective.
3. Water/tar/slime appearance and motion.
4. Pawn entry/exit, corner clipping and lip bystanders.
5. Empty/occupied/covered pit readability.
6. Ladder, spikes and door states.
7. Burning/spent/replenished moat appearance.
8. River force and safe-crossing feel.
9. Supplied free area for one short defense experiment.

A stop may contain many neighboring cases. It should ask one coherent judgment question.

Keep static scenes paused, clear and calm. Moving scenes need a bounded “play this sequence” control that pauses afterward. Exclude them from the static gallery’s uncontrolled ticking. Slow refill and multi-day burning should arrive as prepared comparisons with honest tick/configuration captions—not instructions to wait days.

Reuse `JawaBenchReviewLabels.cs`. Add navigation and **Accept / Needs change / Unclear** controls through its process-memory overlay. Do not serialize review-controller classes into the save. Restore labels/navigation automatically when the review save loads; the owner should not paste `--labels` commands.

Verdicts append a small record containing scene ID, build/art identity, decision and optional note. Reuse the existing decisions-as-data mechanism, but stop making the browser capability sheet the primary review medium.

Then:

- “Needs change” creates or updates one finding, with the scene evidence.
- “Unclear” returns to the agent for better staging.
- Acceptance remains attributable to that build/look.
- Changed materials or behavior reopen affected judgments.
- Clicked options are recorded as choices; typed notes alone are quoted as the owner’s words.

Live `RM_LiquidLookProof.Tune()` is useful here. It is an explicit tuning API, distinct from the retired general hot-reload tool. However, its overrides are memory state: accepted values must flow back into the generator, rebuild/deploy, and be rechecked. A saved gallery does not preserve unscribed global tuning.

The present key transfers far too much testing labor to the human: “unpause for days,” generate rain, trigger floods, inspect costs, discover whether a job works. Preparation should resolve those mechanics before the sitting.

**7. First week for Approach A**

An agent-day here means roughly eight focused hours of work. Parallel offline work does not create another game instance.

| Day | Deliverable | Falsifiable success test |
|---|---|---|
| **1** | Minimal in-process controller and the touching-fluid scenario. Retain current tooling unchanged | One invocation builds the fixture and produces a result without per-cell RPC. A deliberately removed fluid-boundary guard produces the expected failure. Fix or explicitly resolve the observed production behavior |
| **2** | Real designation → autonomous dig → fill-in episode, including terrain/foundation cases | A worker finishes without a forced JobDriver or instant dig. A no-op completion mutation fails. Original terrain is restored; wet deepening and forbidden floor cases get explicit outcomes |
| **3** | Pit/prison episode: entry, attempted escape, ladder, room/bed, capture and lip service | Actual capture and feeding complete, victim stays spawned/alive, and the worker never enters D4. Removing the movement veto or lip routing fails the corresponding outcome |
| **4** | Liquid logistics and fire episode | A constructed powered connection moves accounted liquid. Real flame ignites a burnable control and does not ignite water. Source spread, replenishment and detonation consumption receive explicit results |
| **5** | Real river episode; one save/load continuation; basic performance sampling | Scheduled shoves occur without `StepOne()` driving them. Ford/ferry controls differ. Reverse-dig-order scarce channels and pending fire survive the declared continuation comparison. Performance excludes bridge wait time |
| **6** | One human-only review save, compressed boards, navigation and verdict ingestion | Another agent opens it without instructions and reaches every stop. No stop requires a mechanical verification wait. A test rejection produces the right finding and survives regeneration |
| **7** | Three repeated minimal runs; owner sitting; canonical-list smoke on a disposable save | Repeats have consistent declared outcomes and no manual recovery. Complete warmed run meets a measured target of ≤6 minutes, or identifies why. Owner reviews in ≤15 minutes. Full-list results are reported separately |

Use fixed river fixtures for algorithm/scene repeatability, but include a genuinely generated river sentinel. Painting water terrain alone does not create `riverFlowMap`. DBH and VE adapters need their actual dependencies; a skipped absent-dependency test is not evidence those integrations work.

Performance should initially sample empty/control and populated cases: approximately 100, 1,000 and 6,000 excavated cells, a 200-cell burning run, and visible versus off-screen rendering. Measure pulse duration, ordinary tick cost, allocations and frame hitches separately. Use repeated control-relative measurements; absolute thresholds need a baseline.

The persistence comparison must include D/F/fluid, body stocks and footprints, original terrain, pulse phase, jumpers, pending fire, tanks and relevant jobs. Do not double-count natural source tiles as both full cells and body stock.

**Kill rule**

Allow the first two days as a capped experiment. Thereafter, stop expanding tooling if either condition holds:

- Over two consecutive days, **more than 30% of agent work goes into generic harness/report/mock/policy work**, while no production defect is fixed or previously unverified owner behavior becomes demonstrated.
- Two of three repeated runs require manual fixture recovery, or setup/instrument failures consume **more than 20% of live time**.

Count actual work and timed run phases. Do not use commits or row totals as substitutes.

When triggered:

1. Freeze runner features and abstraction work.
2. Keep the last reliable controller and review save.
3. Select one concrete mod defect.
4. Reproduce it with the existing narrow tools, fix it and retain one regression.
5. Resume runner work only when a measured obstacle prevents that specific task.

Week-one success is **working game behavior and productive judgments**, not a converted suite.

**8. Stop doing these things now**

1. **Stop treating coverage claims as experience proof.** `validation.py:ROW_SHOWS` explicitly maps state mechanisms to visual bars. “Claimed” is useful bookkeeping; it is not “looks right.” The current walk is **DRAFT**, despite older VALIDATED claims.

2. **Stop generating a comprehensive status museum for the owner.** Retire the 51-stop feature tour, S0/M status boards and unbuilt placeholder pads from routine review. Keep capability inventory privately if useful. Replace it with a judgment route.

3. **Stop imposing `prep_site.py` + the 24-row `preflight_flowworks.py` golden contract on ordinary functional runs.** Keep build identity, exact prerequisites and config restoration. Reserve exact camera/luma/environment contracts for captures that require them.

4. **Stop interpreting “on request” as “ordinary shipped behavior need not be covered.”** Pumping, refill, prisoner service and bottles are core player behavior. Optional third-party compatibility remains separately scoped.

5. **Stop repairing render state during verification.** `ProofWallFaces()`’s forced regeneration and camera-driven refresh establish reconstructed geometry, not correct player-visible updates.

6. **Stop keeping a runtime guard for every discarded theory.** `debug_process.md §2.4` makes that growth automatic. Retain informative notes; retain guards when they protect a real recurrence or cheap invariant. This review supplies the requested ablation rationale.

7. **Stop maintaining several authoritative defaults/layout/status copies.** `BOOL_DEFAULTS`, `site_spec.SETTINGS`, extension defaults and review derivations each create parity work. Use resolved runtime settings for the run, plus one explicit shipped-default check.

8. **Stop live-testing every build on the canonical list.** Minimal tests first; targeted dependency tiers when relevant; canonical smoke on candidates. A 15-minute load is worthwhile when it resolves an actual integration question.

9. **Stop broad sweeps that resurrect or heal test subjects.** The latest extension result says colonists were restored 18 times, including resurrection. Preserve deaths as outcomes. Calm-world maintenance must not repair the subject being measured.

10. **Stop promoting SKIP into PASS.** In the supplied `validation.py:_report_rows()`, a SKIP row leaves the component’s PASS verdict intact. Preserve it as inapplicable; never count it as observed behavior.

11. **Stop letting historical prose direct current experiments.** Concrete contradictions include:
    - `extensions_rivers.py` says unregistered; `validation.py` registers it.
    - The walk’s status hint describes the retired reservoir/drip model.
    - The key blames `liquidIgnitionEnabled=False` for canal fire, while the new `RM_LiquidFire` trigger uses `canalFireEnabled`.
    - The key promises foam persistence, while `RM_LiquidFire` documents that water-tagged fill terrain rejects foam filth.
    - Older design says a closed sluice holds liquid; the unified model and release code say it passes liquid. Do not stage “open gate to flood” until that hydraulic contract is settled.
    - “Cutting donor candidates cannot reintroduce oscillation” does not establish eventual progress. A conservative filter can still stall flow.

**The first investment should be two real episodes and one useful review save—not a new universal testing platform.** If that pilot exposes and helps fix game defects within two days, expand it. If it mainly produces runner repairs, kill the expansion immediately.