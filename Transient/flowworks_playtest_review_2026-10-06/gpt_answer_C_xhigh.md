**I recommend moving the main playtest into the running game: a small C# scenario runner that exercises production behavior, reports failures directly, and prepares one compact review save.** Keep the existing pure C# selftests. Use a player agent later, for a bounded experiment in usability.

The deliverable should be a **ranked defect report plus a “walk this” save**, not another green scoreboard or comprehensive feature catalogue.

Everything below uses the supplied bundle. I have not run the game. Costs are estimates; proposed new files are identified as such.

**1. Diagnosis.** The process rewards maintaining its model of testing more reliably than improving the player’s experience.

The measured evidence is:

| Evidence | What it establishes |
|---|---|
| `northstar_time_ledger_extract.md`, §2: **84.7 minutes** setup-invalid, **64.0 minutes** lost/voided, **16.4 minutes** productive out of 210 | Historically, invalid experiments consumed most live time. This is a multi-mod pass, not FlowWorks’ present runtime. |
| `flowworks_size_table.md`: **87 tooling-touching commits versus 74 mod-touching commits** | Tooling is a major workstream. Overlapping commits prevent interpreting this as a labor percentage. Its Python total also includes the production liquid generator. |
| `latest_results_trimmed.md`: current core **251.1 seconds, 872 calls, 59 PASS** | The core has already become reasonably fast. |
| Same result: `P_pits` + `X_promoted` = **184.99 seconds**, **10,480 of 11,510 ticks** | These phases now consume **74% of wall time and 91% of ticks**. Eliminating RPCs alone cannot eliminate most runtime. |
| `review_map_visuals.py:station_ops()` | The 34-station visual board generates **700 bridge calls**, before verification and labels—derived from the supplied code. |
| `debug_process.md`, §§0, 2–3; `northstar_densification_lessons.md`, rule 1 | Every discovery tends to acquire a permanent check, and removal requires an exceptionally strong implication claim. This structurally favors accumulation. |

My inference: agents have a clear, mechanically achievable objective—make declarations, mocks, mappings, fixtures and statuses agree. “Make this moat useful and this pit convincing” has weaker completion criteria. Consequently, discrepancies become harness projects before becoming game improvements.

The machinery has found real defects: `validation_v2.py` documents the oscillation and shared-source fixes. The problem is what its success now means.

I would **contradict this morning’s review’s priority order**. Durable evidence remains necessary, but fixing the repository-wide scoreboard should not lead this week. The latest FlowWorks run already records matching loaded/repository DLL hashes and MVID agreement. The supplied walk now declares a checkout/result route that the report supposedly reads; its actual ingestion remains unverified. Build one direct report for this mod first.

Several game-facing problems deserve immediate reproductions:

- **Natural liquid identity:** `RM_LiquidStock.FormBody()` expands through any neighboring `owner.IsSourceCell(n)`. It does not require the neighbor to have the seed’s liquid identity, yet assigns the resulting body one fluid. Adjacent water and tar can therefore enter one classification walk. This is a source finding; demonstrate the runtime consequence before calling it a confirmed live defect.
- **Colonist falls:** `RM_SuperdeepTrapState.Tick()` requires `RM_SuperdeepTrap.Captures(p)` before invoking fall damage and spikes. Ordinary player colonists are excluded by default. That conflicts with the key sheet’s station 19: the colonist supposedly takes fall damage and climbs out.
- **Visible flow:** the measured vectors fill the far end first—`[0,0,0,1]`—as the v2 docstring explicitly describes. Oracle agreement does not establish the walk’s requirement for a continuous wet reach extending from the inlet.
- **Sluice intent:** the review says opening a shut sluice admits liquid. The unified model says sluices pass liquid while closed; `Flood_FlowWorks.CanFloodInto()` expressly permits flow doors. The main pulse donor picker has no door-state gate. Choose the intended behavior before writing another passing test.
- **Persistence:** the supplied 59-row core has no save/load or performance row. Furthermore, component service order is documented as changing after load, and `RM_LiquidFire.carriedAcc` deliberately is not saved. Both deserve continuation tests.

Those are better next objectives than increasing the number of declared checks.

**2. Three different approaches.**

**Approach A: execute scenarios inside the real game. This is my preference.**

Add a separate development-only assembly, with proposed files such as:

- `bridgetools/FlowWorks.Playtest/ScenarioRunner.cs`
- `bridgetools/FlowWorks.Playtest/Scenarios.cs`
- `bridgetools/FlowWorks.Playtest/ReviewController.cs`

It references the real FlowWorks and game assemblies. It introduces no test `MapComponent` or `GameComponent` into saves.

A launch file or one bridge “start” call selects the batch. After that, C# owns execution. RimBridge remains useful for launching, navigation and emergency inspection; Python no longer constructs the experiment through hundreds of individual commands.

Concretely:

1. **Verify the selected build and fixture.** Reuse the current loaded-DLL comparison, active-list check, custom-def sentinel, pause check and config backup.
2. **Build small scenes locally.** Call the real terrain, building and excavation methods. Verify their resulting state using primitive snapshots.
3. **Test calculations through production entry points.** Invoke the existing pulse implementation for transition tests; retain a short real scheduler test.
4. **Test integration through actual gameplay paths.** Create designations, enable the appropriate work priorities and let an undrafted pawn obtain and finish work. For construction, use blueprints and materials with god mode off.
5. **Observe at bounded intervals inside the game.** Record job starts, completion effects, movement, room membership and damage. A tick observer must not recursively drive ticks. Yield setup and capture work across ordinary frames.
6. **Write each result immediately.** Send primitive snapshots to a JSONL journal. A crash preserves earlier observations.
7. **Perform a persistence checkpoint/reload**, then build the final owner gallery and save it.

The important separation is **setup shortcuts versus evidence routes**. Instant digging is excellent for building a fluid fixture. It cannot prove `Designator_DigCanal → WorkGiver_DigCanal → JobDriver_DigCanal`.

Likewise, `RM_NorthstarProofs.ProofLip()` proves the lip helper accepts a job. The acceptance test must actually feed, tend, capture or convert the target and observe the outcome. Redirecting `StartPath` does not, by itself, establish that every vanilla toil accepts the changed destination.

Reuse:

- Production `RM_*Math` files and `Source/SelfTest/Program.cs`.
- Existing scene geometries and known regression cases from v2.
- Useful setup operations from `extensions.py`.
- `RM_RiverWorksProof`/`RM_RiverWorksProofWorks` as diagnostic helpers.
- Labels, verified save writing and config recovery from the current review machinery.

Retire after their requirements have executable replacements:

- The live `validation_v2.py`/`extensions.py` orchestration.
- Golden-site preparation and its cell-by-cell sidecar contracts.
- Duplicate fake transports for that orchestration.
- The capability-sheet dependency of the review map.

Keep `validation.py` as a small compatibility adapter if the existing registry needs it. It should read one result, not orchestrate a second checkout.

**Failure modes:** direct calls bypassing gameplay, contaminated scenarios, a main-thread runner that hangs, and test code becoming a second implementation of the mod. Control these with explicit action routes, small independent fixtures, bounded execution, and assertions outside the production predicates being tested. Do not build a general scenario language.

**Approach B: run the production liquid algorithm outside Unity, with generated action sequences.**

This abandons Northstar and bridge-driven testing entirely for the core algorithm.

There is already a good starting point: `RM_StockMath.cs`, `RM_PitTrapMath.cs`, `RM_FireMath.cs`, `RM_RiverMath.cs` and other pure arithmetic files are compiled into standalone selftests.

However, **the complete pulse is not presently offline**. Recipient ordering, donor selection, displacement and terrain application remain in `RM_MapComponent_Excavation.cs`; body formation remains in `RM_LiquidStock.cs`.

For broad offline coverage, introduce a proposed production file, `Source/RM_FlowKernel.cs`, and extract the grid transition calculation into it. Use integer cell indices, arrays and explicit inputs. The game adapter retains terrain writes, weather/season reads, bodies, jobs, rendering and Scribe.

Test action sequences such as:

> dig → deepen → supply → pump → join another fluid → rain → fill in → exhaust → refill

Assert design properties rather than exact agreement with a copied algorithm:

- `0 ≤ F ≤ D ≤ 4`.
- No transfer into a wet cell carrying another fluid.
- No unaffordable source debit.
- Displacement returns liquid where capacity exists.
- Original terrain survives dig/fill cycles.
- Refill stays within capacity.
- Pending work and collections remain bounded.

Accounting must use **per-fluid volume**, including stocks, excavation levels, tanks and containers. The current pulse ledger counts levels and observes only one part of the system. Include explicit external input, sink, burn, overflow and conversion terms; do not require equal volumes across an intentionally unequal conversion recipe.

Generate thousands of small cases, save failing seeds, and shrink them by removing cells and actions. Replay selected failures in the real game.

Do **not** assert arbitrary rotation or insertion-order equivalence: the code intentionally uses directional and ordering tie-breaks. Use symmetric cases with an unambiguous expected outcome, and test persistence against a declared ordering policy.

Reuse the existing pure production files, selftest executable and known failing examples. Retire duplicated Python arithmetic once equivalent production-code tests exist; keep a small independent specification model where it adds genuine disagreement.

**Failure modes:** spending weeks extracting the engine, introducing regressions during extraction, and constructing a fake Verse that agrees with itself. Time-box the kernel feasibility spike to two agent-days. If extraction requires mocking rooms, pawns or terrain caches, stop.

This is attractive for long action sequences and boundary cases, but **it cannot produce a convincing pit, prove a warden job, or validate a shader**.

**Approach C: a bounded player agent completing missions.**

Use an agent to play a supplied colony through the existing Architect/designator, selection, gizmo and menu surfaces.

Three initial missions:

1. Build and fill a defensive canal from a limited pond.
2. Trap an enemy, capture from the lip, service the prisoner and release appropriately.
3. Move liquid through a pump/tank/container chain and cross a river safely.

Prepare resources, research, healthy workers and objectives before the mission. During the mission:

- No instant excavation, direct fill writes, forced jobs or state repairs.
- Use actual player commands; verify their postconditions.
- Record failed placements, repeated searches, abandoned work, unclear feedback and unintended consequences.
- Permit state reads for diagnosis, while distinguishing what the agent learned from what the player could see.
- Reproduce a suspected defect with a short deterministic scenario before filing it as a mod failure.

Use a thin proposed `northstar/player_missions.py`; do not create a general RimWorld-playing platform. Prefer semantic game commands to pixel clicking where they represent the same player action.

Reuse the bridge client, existing UI semantics, snapshots and mission save. Remove the requirement to translate every observation into a new northstar visual bar or component.

**Failure modes:** agent incompetence presented as friction, agents using internal knowledge a player lacks, nondeterminism, and long live sessions spent navigating menus. A useful report needs the action trace and a reproducible example, not “the mod felt confusing.”

Its strength is discovering problems nobody thought to specify. Its weakness is reliable coverage.

Estimated economics:

| Approach | Agent-days to first useful result / broad coverage | Warm live-game time per run | Main expansion risk |
|---|---:|---:|---|
| **A: in-process scenarios** | **2 / 6–9** | **6–10 min**, including focused captures, gallery and persistence; target 8 | A universal scenario framework |
| **B: offline production kernel** | **1–2** for existing math; **6–10** for broad extraction | **0** offline; roughly **5–10 min** for selected engine replays and review staging | Reimplementing Unity/Verse |
| **C: player missions** | **2–4** for a thin pilot | **20–35 min** for three bounded missions; retries add cost | Building a general game-playing agent |

These exclude human review and compilation. Budget approximately **1.9 additional minutes** for a minimal cold launch plus the supplied 90-second quicktest estimate. The latest run’s 10.2-second map creation is one observation, not a dependable general budget. Full-list startup adds roughly **15 minutes**.

The following is the coverage contract to implement, **not a claim that these tests exist today**. “Sampled” under C means mission coverage, not exhaustive assurance.

| Owner requirement | A: automatically establish | B: automatically establish | C: discover through play | Human judgment |
|---|---|---|---|---|
| Flooding and canal flow | Scheduled flow; confinement; legacy `Flood_FlowWorks` spread, expiry and recovery | Extracted grid transitions and sequence invariants | Sampled canal/flood behavior | Front readability and usefulness |
| Liquid types and two fluids interacting | Adjacent natural bodies; meeting fronts; refusal; drain/reclaim; rain on foreign liquid | Identity and no-mix invariants | Confusing or surprising joins | Substance distinction |
| Pumps, pipes, tanks, containers | Actual transfers, power loss, capacity, refusal, completed container jobs | Available pump/conversion/net arithmetic | Construction and operation friction | Affordances and practical usefulness |
| Designating, digging, building and filling in | Designator → autonomous worker → completion; blueprint construction; terrain restoration/displacement | Work/cost arithmetic | Ordinary construction loop | Discoverability and labor balance |
| Quarry and sluice | Actual dig completion, local yield, repeat-cut exploit guard; door behavior after resolving intent | Discovery arithmetic | Yield and operation friction | Reward balance |
| Sluice box and panning | Report unavailable/dependency-blocked until built | Rules when available | No present coverage | Future experience review |
| Different creation/embedding terrains | Allowed/refused soil, rock, floors, foundations, water, edifices; original-layer restoration | Explicit terrain classifications where extracted | Placement problems | Material appearance |
| Varying depth and fill | All legal D/F states, capacity and movement behavior | Exhaustive small-state transitions | Sampled crossings | Depth/fill legibility |
| Refill and recession | Correct source fluid, weather/season adapter, restoration and scheduler | Rate/clamp/boundary arithmetic | Sampled exhaustion/recovery | Refill pacing |
| Pits and prisoner behavior | Actual exit attempts, width, jump, covers, ladder permissions, capture and completed lip service | Trap/width/permission arithmetic | Prison mission | Confinement cues and cruelty/balance |
| Flame ignition and fluid effects | Real Fire and explosion triggers; nonflammable controls; drowning/poison/burn effects; foam/rain branches | Rates, thresholds, front bounds | Sampled defense consequences | Flame appearance and threat |
| Differing viscosities | Real cadence plus fluid-transfer tests | Stride/rate boundaries | Timing surprises | Water/tar/slime feel |
| River force and works | Scheduled shove, exemptions, ford/ferry, flood surge, edge wash/return, weir/breach | Direction/cadence/size arithmetic | Crossing and routing friction | Force readability and fairness |
| Art, perspective, layering/clipping | Render-contract checks and approved-image regression checks | Pure geometry where available | Visible anomalies | Overall appearance |
| Shallow/deep appearance and pawn-edge clipping | Correct materials, sink/occlusion state, movement frames, actual inability to escape | Sink/face arithmetic | Sampled crossings | Convincing shallow/deep read |
| Saving/loading | Real Scribe round trip and continuation | Kernel checkpoint continuation only | Load/continue mission | Rare visible reconstruction anomalies |
| Performance | Engine/render timings and scaling in real scenes | Algorithm scaling | Experienced hitching | Acceptable feel |

Optional dependencies need named scope. DBH being absent cannot yield a thirst-integration PASS. VE adapters require a tier containing their actual dependency. Ordinary shipped mechanics should not disappear from coverage because their settings are optional.

**3. Evaluate the four outputs.** An output does not catch defects by itself; its value depends on the experiment producing it.

| Output | What it catches or communicates | Cost and required approach | Worth it here? |
|---|---|---|---|
| **(a) Ranked breakages + one prepared review save** | Machine-settleable failures, plus concentrated visual/feel/balance questions | A supplies real behavior and staging; B contributes generated failures. Around **0.5–1 agent-day** to simplify existing report/navigation/decision plumbing; **1–3 warm minutes** presentation work within the broad-run estimate; **12–15 human minutes** | **Yes. Make this the mandatory output.** |
| **(b) Player agent reporting friction** | Missing affordances, awkward sequences, bad feedback and emergent interaction | C; **20–35 live minutes** per mission batch, plus reproduction of suspected defects | **Later, experimentally.** It cannot replace assertions or the owner. |
| **(c) Pass/fail on every build** | Repeatable arithmetic, loading and known behavioral regressions | B/existing selftests every build; a small A smoke after deployment. Full live coverage on every intermediate DLL multiplies restart cost | **Yes for a narrow gate. No for full certification on every build.** |
| **(d) All three layered** | Regression safety, focused judgment and exploratory discovery | Cheap gate every build; A packet per review candidate; C periodically. Running all three every time costs at least **26–45 warm game minutes**, before review/startup | **Worth it only at different frequencies.** |

For **(a)**, rank failures by consequence and evidence:

1. Save corruption, crashes, liquid creation/loss, wrong liquid identity.
2. Broken player loops: workers cannot complete work, prisoners cannot be serviced, trapping fails.
3. Incorrect behavior or performance.
4. Visual defects and unresolved balance questions.

Group cascading failures under their cause. The report should distinguish **observed defect**, **source concern awaiting reproduction**, **invalid experiment**, and **feature unavailable**. The owner should receive at most five leading findings, with the rest expandable.

Each defect needs expected/actual behavior, a reproduction, evidence and the production files likely involved. Agents fix machine-settleable failures autonomously. The gallery contains questions needing judgment—not stations asking the owner to verify conservation or watch a job eventually finish.

For **(b)**, stop the pilot unless three runs totaling at most **60 live minutes** produce at least one useful, reproducible finding that the deterministic scenarios missed.

For **(c)**, label the narrow gate honestly: “functional smoke passed on this build/tier.” It must not become “FlowWorks works” while machinery, rivers, persistence or experience remain untested.

**4. Visual checks.** Separate render correctness from whether the result communicates the intended thing.

Machines can decide explicit render contracts:

- A graphic is `BaseContent.BadGraphic`; a texture/shader is missing.
- `RM_LiquidLooks` selected the intended material family and tier parameters.
- Water retains its intended depth pass; thick-liquid Flow materials omit it.
- `RM_PitDepthDraw` applies the expected sink, skips fliers and respects its toggle.
- Expected wall geometry exists, has finite coordinates and valid triangles.
- A supported mutation invalidates the visible section.
- Shadow suppression and lip-occlusion commands occur in the appropriate cases.

Machines can also decide **bounded screenshot regressions**, once the owner approves a reference:

- A large unintended patch appears outside the subject.
- A previously visible pawn or spike disappears.
- A covered pit’s crop differs beyond an approved tolerance.
- A depth or fill comparison becomes effectively identical.
- A new rectangular occlusion strip appears during crossing.

Those are comparisons against an approved presentation, not universal rules for “good art.” Render queues and geometry alone cannot establish final visibility through shaders, transparency and other mods.

A visual model can screen for likely defects—flat pits, road-like trenches, tinted-water slime—but its YES should not automatically settle perspective, convincing depth or balance. Start with approved/rejected examples and measure agreement with the owner.

Two changes are essential.

First, **observe without repairing**. `RM_NorthstarProofs.ProofWallFaces()` calls `layer.Regenerate()` before counting vertices. That establishes that regeneration can build geometry; it cannot prove normal invalidation works. Keep the camera fixed, mutate through the real action, capture after normal rendering, and only then force regeneration as a diagnostic comparison.

Second, record **game tick, pulse count, Unity frame and real time** separately. `RM_LiquidSurface` animates using real time even while simulation is paused; wakes require pawn movement ticks. Scrubbing the clock a day forward cannot prove a fire survived a simulated day.

The current gallery also has concrete defects:

- `review_map_visuals.fill_level()` couples depth to fill. It does not cover the complete legal depth/fill set.
- Key-sheet station 35 promises dry/trace/half/brim at **D2**. With integer fill and `FillTier()`, D2 has dry, half and brim; **trace is impossible**.
- The granite scenes use `Deepen()` directly, while `Designator_DigCanal` accepts soil. They demonstrate rendering, not player-accessible stone excavation.
- Bottom visual plots lie in the sink band; gallery cells reach near the opposite edge. These need explicit intentional-sink designation or relocation.
- `RM_PitLipOcclusion` records a known trade: it can cover a pawn or item standing on the lip. Stage **two pawns**, one below and one above, plus a dropped item. The current single-pawn setup misses this.

Build one compact **15-state board**: undug ground plus every legal `(D,F)` for D1–D4. Add matched dirt/stone render comparisons, a vanilla shallow-water reference and movement clips across north/south/east/west edges. Include a representative larger pawn.

The human decides whether those states read correctly at play zoom, whether the walls convincingly exceed the occupant, whether tar looks wet, whether slime looks thick, and whether the transition clips naturally.

**5. Human review sitting.** Hand over a loaded, framed map and a short key—not commands to paste.

The packet contains:

- One versioned keeper save.
- A concise ranked defect report.
- A numbered route with approximately **eight stops**.
- Pre-recorded short motion clips where replay would consume time or destroy the staged state.
- An in-game review control with next/previous, replay, reset and verdict entry.

Suggested route:

| Stop | Adjacent comparisons | Judgment requested |
|---|---|---|
| 1 | Complete depth/fill board; dirt/stone; vanilla water reference | Can depth and fill be read separately? |
| 2 | Water, tar, oil, slime at matched depth/fill | Do they communicate distinct substances? |
| 3 | Pawn below lip, pawn above lip, item; crossing clips | Are sinking, clipping and visibility convincing? |
| 4 | Covered/uncovered pit, spikes, raised/lowered ladder, doors | Are the important states visible at play zoom? |
| 5 | Fill front, drawdown and refill sequence | Does the behavior look understandable and well paced? |
| 6 | Burning, fed-burning and spent liquid | Does fire read correctly and feel threatening? |
| 7 | Serviced prisoner pit and bounded release interaction | Does this feel like workable confinement? |
| 8 | Pump/container loop, river/ford/ferry; stocked free area | Are operation, crossings and force understandable? |

Aim for **8–10 minutes comparing**, **3–5 minutes interacting**, with loading completed beforehand. This covers many questions per stop without requiring the owner to remember a scene across a large map.

Every stop states one plain question and one optional action. Use **Accept / Reject / Unclear**, plus a short note. No prefilled verdicts.

The development-only UI writes decisions immediately to a sidecar keyed by build, station and question. Existing `serve_sheet.py` decision handling can be reused if helpful, but the owner’s primary surface remains the game. Labels and review state remain outside the save’s serialized classes.

On rejection, automatically retain the frame/clip, action trace and note, then create or update the relevant work item. Record clicked choices as decisions, not fabricated verbatim owner quotations. Acceptance retires that question for the same evidence; reopen it when relevant appearance or behavior changes.

`RM_LiquidLookProof.Tune()` is useful during review. Record accepted values back into the generator data, then restart and reproduce them. A tuned in-memory material is not a deployed fix, and a save does not preserve that tuning.

The existing 51-feature tour plus 34 visual plots is too much for routine review. Keep it as an inventory. The recurring route should contain only changed, rejected or unresolved judgments, with shared comparisons covering several questions.

**6. First week for Approach A.** This week should produce game fixes and a useful sitting. It should not extract the full offline kernel or generalize testing across all mods.

| Day | Work | Falsifiable success test |
|---|---|---|
| **1** | Add the smallest runner: existing build identity, three scenes, incremental results. Reuse a fixed scratch fixture. | Canal, actual worker dig and pit exit tests run twice. An injected final exception preserves prior results and reports incomplete. Each run finishes within **6 warm minutes**. |
| **2** | Test adjoining natural fluids, meeting fronts, rain on foreign fluid, pump/displacement accounting and shared sources. Fix observed production failures. | Side-adjacent and diagonal water/tar bodies retain correct identities. A removed no-mix guard fails. The shared-source regression remains caught. |
| **3** | Exercise actual pawn behavior: ordinary colonist fall, hostile trap, jump, ladder permissions, capture and one completed lip-service job. Produce the first small review save. | A real worker completes the service from outside D4. A forced exit cannot pass because the pawn died/downed. The keeper reloads and exposes at least **eight judgment questions**. |
| **4** | Cover terrain designation/embedding, actual construction and container work, quarry exploit guard, ignition triggers, and legacy flood recovery. Add representative machinery/rivers using existing tests. | Disabling a completion effect fails its scenario. Real Fire ignites appropriate fluid; nonflammable control stays unlit. Dig/fill restores the original terrain layers. Missing dependencies remain explicit. |
| **5** | Replace the large recurring gallery with the compact route. Add stationary-camera render checks and edge-crossing clips. | The board contains every legal D/F state. Suppressed mesh invalidation is detected before forced regeneration. Two-pawn lip scenes show both subjects clearly enough to judge. |
| **6** | Persistence continuation and performance. Test competing source outlets, viscosity phase, pending fire, jumper state, tank/container state and an interrupted job. | Save/load/continue matches an uninterrupted branch under declared normalization. Dropping a saved field fails. Performance samples measure production work separately from RPC/report time. |
| **7** | Run the broad batch, then one full-list scratch smoke and the owner sitting. Apply the highest-priority resulting fixes. | Three minimal-tier batches have **no unexplained setup failures**, median **≤8 warm minutes** including packet production. The owner completes **≥10 distinct judgments in ≤15 minutes**. Full-list results and remaining coverage gaps are explicitly reported. |

For performance, measure empty/control and populated scenes, pulse duration, allocations where obtainable, and render frame cost with the camera stationary. Include a targeted large-component/cap-boundary test. Establish a baseline on this machine; a throughput number dominated by observers is not mod performance evidence.

Long burn/refill rates can be checked through production rate arithmetic plus direct production transitions and a short scheduler test. Keep a longer natural-duration soak periodic. Do not label accelerated-method evidence as “survived a day of gameplay.”

**Kill rule:** allow at most **two agent-days of initial runner infrastructure**. Starting day 3, count active work time and game ownership time—not commits or emitted rows.

Freeze tooling development if either:

- Across three days, infrastructure consumes **over 30% of agent work**, without closing at least two game-facing findings or owner decisions; or
- Two successive batches spend **over 20% of game ownership time** recovering invalid experiments; or
- The review save is still unusable at the end of day 3.

Then use the existing v2 plus a few selected, batched extension scenarios to finish the highest-priority mod fixes and stage the review manually through existing helpers. Preserve the unfinished runner; stop expanding it. Do not respond by adding an observatory, another mock layer or a new documentation program.

Passing the week’s speed target is insufficient if the owner still mostly receives status explanations.

**7. What to stop doing now.**

- **Stop treating `shows=` as proof of appearance.** `validation.py:ROW_SHOWS` maps state and def checks to visual claims. That is useful routing metadata, not visual evidence. `L3_defs_live` path costs cannot establish that a trench looks obstructive.
- **Stop reporting “Works in game” from a mapped mechanism PASS.** `human_review.py` derives that label from behavior rows. Use “behavior tested” and show appearance acceptance separately.
- **Stop using timestamp-newest evidence for current review status.** The capability sheet describes newest-result selection; the supplied extract does not establish identity filtering. Pass an explicit current result to the packet builder.
- **Stop making ordinary features disappear into “extensions.”** Pumps, prisoner service, bottles and rivers are normal functionality. Run them at appropriate frequencies and expose absent coverage; the core’s 59/59 is a scoped result.
- **Stop asking the human to manufacture stimuli.** “Spawn fire,” “start a flood” and “unpause for days” in `KEYSHEET.md` are unfinished staging tasks.
- **Stop resurrecting subjects across scenarios as routine cleanup.** The latest extension result records 18 restoration actions, including resurrections. Preserve the death as evidence and rebuild a valid fixture before dependent tests.
- **Stop forced refreshes before testing normal refresh.** Change `ProofWallFaces()` into a diagnostic repair operation plus a non-mutating observation.
- **Stop maintaining multiple full default/settings/capability copies.** `BOOL_DEFAULTS`, `site_spec.SETTINGS`, extension defaults and the capability table create reconciliation work. Keep one executable requirement inventory; batch-read runtime settings.
- **Stop requiring a permanent executable guard for every discarded theory.** Retain the note. Add a guard when recurrence would be consequential and the test can detect it cheaply.
- **Stop defending obsolete orchestration through `debug_process.md` §2’s “no parallel system” rule.** Replace that method constraint for this experiment. Preserve the owner’s design authority and hash-bound experience rulings.
- **Stop generalizing before FlowWorks benefits.** No shared all-mod framework, universal dependency cache, general fake RimWorld or skill-rewrite campaign this week.
- **Keep the proven prohibitions:** retired hot reload, broad debug-action search, stale sockets after timeouts, guessed parameters, and uncontrolled concurrent deploy/config changes. These prevent known expensive failures.

The governing work item should be concrete: **“Fix these ranked game failures; prepare these unresolved judgments for a fifteen-minute sitting.”** That gives the agents an outcome whose value the owner can see immediately.