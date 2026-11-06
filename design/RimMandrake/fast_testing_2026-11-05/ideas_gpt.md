**38 additional concepts**, checked against both supplied lists. I excluded the existing staging, batching, headless, replay, snapshot, invariant, generic fuzzing, and small-policy proposals. Where a concept extends one of those foundations, the additional mechanism is explicit.

These are proposed RimWorld adaptations; linked sources establish precedents, not demonstrated compatibility or speedups in this project. “Attacks” refers to measurements in `ideas_inside.md`.

One fresh implementation finding: the **current public RimBridgeServer README describes `step_game_ticks` as advancing one tick per Unity update frame**. If that matches the deployed version, exact stepping can be frame-limited independently of bridge latency. Unity documents `-batchmode`/`-nographics`, but those flags alone do not establish that RimWorld initializes correctly without graphics or that `Time.timeScale` accelerates its tick scheduler. These are investigation findings, not additional concepts counted below. Sources: [RimBridgeServer](https://github.com/pardeike/RimBridgeServer), [Unity Player arguments](https://docs.unity3d.com/2022.3/Documentation/Manual/PlayerCommandLineArguments.html), [Unity time management](https://docs.unity3d.com/cn/2022.3/Manual/TimeFrameManagement.html).

**01. Stop stochastic tests when the evidence is sufficient**

Declare two failure-rate hypotheses and acceptable error probabilities before starting a campaign.  
After each independent episode, update a sequential probability ratio test; stop when either boundary is crossed.  
This replaces “always run 100 seeds” with an evidence-dependent stopping rule; inconclusive campaigns remain inconclusive.  
Source: Stockfish’s [Fishtest](https://github.com/official-stockfish/fishtest) and [SPRT testing workflow](https://official-stockfish.github.io/docs/fishtest-wiki/Creating-my-first-test.html).  
Attacks: §1.2b’s **4,870 run-minutes** and the earlier **32% of chain-minutes spent retesting known-good chains**.

**02. Pair builds with independent streams for external events**

Generate separate deterministic streams for weather, incidents, initial pawn attributes, and other controlled disturbances.  
Feed identical external events to both builds, rather than relying on one global RNG seed that diverges after an extra random call.  
Compare paired outcome differences; reduced environmental variance can mean fewer episodes for a balance conclusion.  
Source: [NumPy’s reproducible parallel RNG streams](https://numpy.org/doc/2.0/reference/random/parallel.html); the paired-experiment adaptation is proposed here.  
Attacks: §1.2b’s run-minutes and §1.6’s regression investigations; adds **variance reduction** beyond existing seeded differential replay.

**03. Use a surrogate as a statistical control variate**

Run thousands of cheap model evaluations and a smaller, randomly selected set of paired real-game evaluations.  
Estimate the real-game mean by correcting the cheap model’s estimate with measured game–model residuals.  
Allocate samples using observed correlation and cost; retain uncertainty bounds instead of treating surrogate predictions as PASS results.  
Source: [Multifidelity Monte Carlo](https://kiwi.oden.utexas.edu/research/multi-fidelity-uncertainty-quantification.php).  
Attacks: §1.2b’s **4,870 run-minutes**; differs from existing surrogate anomaly detection by reducing the real runs needed to estimate aggregate outcomes.

**04. Clone trajectories as they approach rare failures**

Define intermediate danger levels: declining power reserve, insufficient food, overloaded junction, then actual failure.  
Maintain a population of runs; replace unpromising trajectories with branches from runs that reached the next danger level.  
Spend subsequent simulation around precursors instead of repeatedly simulating uneventful colony beginnings; track ancestry because branches are correlated.  
Source: [Adaptive multilevel splitting](https://pmc.ncbi.nlm.nih.gov/articles/PMC4440697/).  
Attacks: §1.2b’s run-minutes and §1.6’s owner-discovered edge cases; the new mechanism is **adaptive trajectory replication**, beyond ordinary save forking.

**05. Oversample dangerous conditions and correct their weights**

Deliberately sample more severe temperatures, resource shortages, or incident combinations than normal play produces.  
Where the normal and sampling distributions are known, weight each result by their likelihood ratio to estimate normal-play risk.  
Without valid probabilities, retain the campaign as bug hunting and report no natural failure-rate estimate.  
Source: Art Owen’s [importance sampling chapter](https://artowen.su.domains/mc/Ch-var-is.pdf).  
Attacks: §1.2b’s expensive run phase; exposes rare conditions without requiring proportionally long ordinary soaks.

**06. Search for the smallest safety margin**

Express requirements over time: “after reconnection, power returns within 250 ticks” or “temperature remains below the damage threshold.”  
Compute a numerical robustness margin for each trace, then let an optimizer search inputs that drive that margin toward violation.  
A nearly failing run becomes useful search feedback even when it produces no exception or novel code coverage.  
Sources: [PSY-TaLiRo](https://arxiv.org/abs/2106.02200), [RTAMT](https://github.com/nickovic/rtamt).  
Attacks: §1.2b’s run-minutes and §1.6’s repeated edge-case discovery; adds **specification-directed falsification**, rather than generic random exploration.

**07. Solve fixture feasibility before touching the game**

Describe setup requirements as constraints: reachable workstation, legal placement, required roof, valid power connection, available ingredients.  
Use a solver to construct a satisfying layout; materialize it through the bridge and verify its actual preconditions before starting the proof.  
Impossible setups return an explanation before consuming a live slot; incomplete abstractions are caught by the live precondition check.  
Sources: [Scenic scenario generation](https://docs.scenic-lang.org/en/3.x/api.html), [Z3’s Python interface](https://github.com/microsoft/z3guide/blob/main/website/docs-programming/02%20-%20Z3%20Python/01%20-%20Introduction.md).  
Attacks: §1.1’s **231 proof-or-site UNMEASURED rows** and testq’s **30% UNMEASURED**.

**08. Feed comparison operands back into the fuzzer**

Instrument selected comparisons in test assemblies to record values on both sides of failed branches.  
When code checks a threshold or special identifier, generate inputs around that observed value instead of waiting for random mutation to discover it.  
For RimWorld, adapt the instrumentation to managed IL or explicit test hooks; AFL++ instrumentation itself is not a drop-in Mono solution.  
Source: AFL++ [CmpLog and Redqueen](https://github.com/AFLplusplus/AFLplusplus/blob/stable/instrumentation/README.cmplog.md).  
Attacks: §1.2b’s run-minutes and §1.6’s missed edge cases; goes beyond existing method counters by using **comparison data to construct inputs**.

**09. Cover interactions without enumerating every configuration**

Model DLC flags, mod settings, dependencies, biome, quality, and relevant companion mods as factors with constraints.  
Generate a covering array guaranteeing chosen two-way or three-way combinations rather than trying the Cartesian product or arbitrary random subsets.  
Record interaction coverage separately from test count so missing combinations remain visible.  
Source: NIST’s [ACTS explanation](https://csrc.nist.gov/projects/automated-combinatorial-testing-for-software/faqs).  
Attacks: §1.1’s **10 full-list sessions**, §1.4’s **15–25-minute loads**, and §1.6’s unresolved interaction regression.

**10. Skip equivalent action orderings**

Give test actions conservative read/write footprints: which pawn, network, map component, RNG stream, or global state they affect.  
Explore both orders when actions interact; retain one representative ordering when independence has been established.  
An uncertain footprint means “explore both,” preventing an optimization from silently excluding shared-state bugs.  
Source: SPIN’s [partial-order reduction](https://spinroot.com/spin/Man/Quick.html).  
Attacks: §1.2b’s run-minutes; adds **state-space reduction** to stateful testing instead of merely generating more sequences.

**11. Deduplicate equivalent network shapes**

Canonicalize generated wire or pipe graphs so permutations of interchangeable node IDs produce the same representation.  
Reject already-tested graph classes before constructing them in-game; preserve spatial attributes wherever distance, orientation, or terrain matters.  
This removes duplicate scenarios rather than running transformed scenarios to assert a metamorphic relation.  
Source: the distinction between symmetry and ordering reduction in [SPORE](https://plv.mpi-sws.org/genmc/pldi2024-spore-full.pdf).  
Attacks: §1.2b’s repeated run work and the earlier **32% known-good retesting**.

**12. Turn abstract counterexamples into live scenarios**

Build a small finite-state abstraction of one subsystem: connected/disconnected, reserved/unreserved, powered/unpowered, destroyed/alive.  
Model-check temporal requirements and translate counterexample paths into concrete bridge actions.  
When a counterexample cannot occur in-game, refine the abstraction; the game confirms findings rather than executing the entire abstract search.  
Source: [SPIN model-checking tutorial](https://www.spinroot.com/spin/Doc/course/mc-tutorial.pdf).  
Attacks: §1.6’s manual discovery and isolation loop, with expensive live execution reserved for candidate counterexamples.

**13. Minimize the offending mod set**

Starting from a reproducibly failing configuration, remove dependency-valid groups of mods and rerun the same scenario.  
Use delta debugging that can handle interacting groups; do not assume one bad mod or monotonic failure behavior.  
Produce a small conflict set, preserving the original failure signature and distinguishing failed loads from behavioral failures.  
Source: [Weighted Delta Debugging](https://arxiv.org/abs/2411.19410).  
Attacks: §1.6’s WATER_STUB regression with **three candidate causes**; differs from existing commit bisection by minimizing a **configuration**, including multi-mod interactions.

**14. Test competing Harmony patches as critical pairs**

Collect patches targeting the same methods, including priorities and before/after constraints.  
For overlapping patches, exercise representative inputs under alternative permitted relative orders in disposable test instances.  
Compare return values, skipped originals, exceptions, and side effects; report a concrete order-sensitive witness.  
Source: [Harmony 2 patch ordering](https://harmony.pardeike.net/v2/articles/priorities.html).  
Attacks: §1.4’s expensive full-list investigation and §1.6’s unisolated interaction failures; mod-list order alone does not specify patch execution order.

**15. Deliberately hunt contamination between tests**

Run selected proofs alone, in reverse order, and in reproducibly shuffled orders within a warm process.  
When a result changes, minimize the preceding tests to identify the polluter: static cache, subscription, settings mutation, or leftover fixture.  
This makes persistent-game execution safer by testing its isolation assumptions directly.  
Source: [pytest-randomly](https://github.com/pytest-dev/pytest-randomly).  
Attacks: testq’s **30% UNMEASURED**, **787 partial groups**, and the warm-game lane’s potential for accumulating hidden state.

**16. Localize faults from passing and failing coverage**

Collect a compact method-or-branch coverage vector alongside each verdict.  
Compare execution spectra across passing and failing scenarios to identify code disproportionately associated with failures.  
Hand the builder implicated methods and distinguishing scenarios; this consumes existing runs rather than requiring a fresh diagnostic sitting.  
Source: [GZoltar](https://github.com/GZoltar/gzoltar), an automatic-debugging precedent whose mechanism would need a C# implementation.  
Attacks: §1.6’s unresolved regressions and §1.1’s **96 FAIL rows** routed into investigation.

**17. Reuse evidence according to actual dependencies**

Record which assemblies, defs, settings, patch chains, and fixture versions each test depends on.  
Hash that dependency set and reuse unchanged evidence; changes to shared initialization or unknown dependencies invalidate conservatively.  
Periodically run the complete suite to audit the dependency approximation.  
Source: [Ekstazi’s dynamic dependency selection](https://github.com/gliga/ekstazi).  
Attacks: the earlier **32% known-good retesting** and §1.6’s suite target moving across **70 GSS commits**; finer-grained than mapping changed paths to a mod suite.

**18. Ask new questions of old executions**

Keep timestamped event and telemetry histories sufficient for declared observation classes.  
When a new requirement appears, run its temporal query over those histories without replaying commands or loading RimWorld.  
Report “insufficient observations” when required fields were not recorded; old traces cannot establish behavior of a newer build.  
Sources: NASA F´ [history-search test API](https://fprime.jpl.nasa.gov/latest/docs/user-manual/gds/gds-test-api-guide/), [RTAMT](https://github.com/nickovic/rtamt).  
Attacks: §1.6’s reopening acceptance criteria and §1.2b’s run-minutes; adds **retrospective checking**, beyond game replay.

**19. Reconcile transactions rather than final totals**

Observe accepted operations and their outcomes using correlation IDs: ingredients reserved, work completed, output emitted, cancellation acknowledged.  
Maintain a scoreboard of outstanding obligations and match completions, including permitted cancellation paths and deadlines.  
Detect duplicate outputs, dropped work, and misattribution even when aggregate totals happen to balance.  
Source: hardware verification’s driver/monitor/scoreboard architecture, exemplified by [cocotb testbench tools](https://docs.cocotb.org/en/v1.5.1/testbench_tools.html).  
Attacks: §1.1’s costly FAIL diagnosis and §1.6’s wrong-victim class of acceptance work; adds **causal transaction matching** beyond state invariants.

**20. Test bridge client contracts without reserving RimWorld**

Generate protocol tests from capability schemas and captured responses: omitted fields, unknown arguments, pagination, terminal errors, and response types.  
Run Python parsing, routing, and verdict logic against a protocol simulator before a proof enters the live queue.  
Use occasional real-server conformance checks to ensure the simulator still represents the deployed bridge.  
Sources: [Schemathesis](https://github.com/schemathesis/schemathesis), [RimBridgeServer response conventions](https://github.com/pardeike/RimBridgeServer).  
Attacks: §1.1’s **231 proof-or-site defects**; extends beyond proof-line lint to executable **client/server contract verification**.

**21. Plan setup repairs from preconditions**

Represent fixture operations with preconditions, effects, and costs: clear cell, provide ingredient, connect power, assign worker, remove roof.  
When a setup precondition fails, a deterministic planner constructs a short legal repair sequence and verifies each effect.  
Stop before the behavioral test begins; repairs must not manufacture the outcome the proof is supposed to observe.  
Source: the Python [GOAP planner](https://github.com/agoose77/GOAP).  
Attacks: §1.1’s **231 proof-or-site UNMEASURED rows** and testq’s partial groups; adds synthesized multi-step repair beyond fixed error routes.

**22. Restore a booted process instead of loading a save**

Experiment with checkpointing a headless Linux process after assemblies and defs initialize, with external connections quiesced.  
Restore isolated copies that reconnect their bridge endpoints, retaining initialized process memory and static state.  
Unlike a map snapshot, this targets startup itself; Unity resources, sockets, and process identity make feasibility an explicit experiment.  
Sources: [CRIU checkpoint/restore](https://criu.org/Checkpoint/Restore), [external GPU-state limitations](https://www.criu.org/GPU_Checkpointing).  
Attacks: §1.1’s **42 cold starts** and §1.4’s **15–25-minute full loads**.

**23. Carve fast unit tests out of live executions**

Capture selected mod-method arguments and the relevant dependency state during a real scenario.  
Generate direct-call tests that mutate those captured inputs outside the full scenario, extracting small adapters where Unity objects prevent isolation.  
Lift discovered failures back into the live fixture before treating them as game bugs.  
Sources: [Carving Parameterized Unit Tests](https://arxiv.org/abs/1812.07932), executable examples in [The Fuzzing Book](https://www.fuzzingbook.org/html/Carver.html).  
Attacks: §1.2b’s run-minutes; differs from “game as a library” by extracting **small observed execution contexts**, not reproducing the whole engine.

**24. Sweep clock domains and tick phases**

Run targeted scenarios at different tick offsets, render cadences, pause transitions, and supported speed settings.  
Instrument whether behavior depends on simulation ticks, Unity scaled time, unscaled time, or Update calls; perturb one clock relationship at a time.  
Use this to identify which tests remain valid under accelerated execution and catch interval-boundary bugs ordinary fixed-start fixtures miss.  
Sources: [Unity time management](https://docs.unity3d.com/cn/2022.3/Manual/TimeFrameManagement.html), [bridge stepping semantics](https://github.com/pardeike/RimBridgeServer).  
Attacks: §1.3’s **missing TPS characterization** and §1.2b’s run costs; qualifies acceleration rather than assuming it preserves behavior.

**25. Correct a small player on the states it actually visits**

Train an initial policy, let it operate, and collect expert action labels on the states produced by its own mistakes.  
Aggregate those labels and retrain, instead of repeatedly training on clean demonstrations it no longer resembles.  
The teacher can be validated code or reviewed judgments; Jev could propose labels, with correctness established separately from confidence.  
Source: [DAgger](https://arxiv.org/abs/1011.0686).  
Attacks: §1.6’s owner-dependent edge discovery and testq’s unproductive partial runs; adds **on-policy corrective data collection** beyond ordinary imitation learning.

**26. Learn useful goals from failed attempts**

For goal-conditioned training, relabel an unsuccessful episode with a goal it actually achieved: reaching a room, completing one segment, obtaining an ingredient.  
Reuse the trajectory as training evidence for that goal while preserving the original test’s failure verdict.  
This gives sparse-reward bridge tasks useful learning signal without another game episode.  
Source: [Hindsight Experience Replay](https://arxiv.org/abs/1707.01495).  
Attacks: §1.2b’s run-minutes and discarded partial-run effort; the new mechanism is **training-data relabeling**, not another player architecture.

**27. Preserve a repertoire of different play styles automatically**

Define behavioral dimensions such as colony density, resource slack, network fragmentation, and reliance on hauling.  
Maintain a MAP-Elites archive containing effective policies or scenarios in different cells, and mutate representatives from across the archive.  
This retains unusual but productive behaviors that optimizing one survival score would eliminate.  
Source: [pyribs quality-diversity algorithms](https://docs.pyribs.org/en/stable/supported-algorithms.html).  
Attacks: §1.2b’s **720 of 748 jobs concentrated on FlowWorks** and §1.6’s narrow manually discovered coverage; adds an explicit **diversity-preserving archive** beyond fixed personas or curiosity.

**28. Generate scenarios by disagreement between players**

Train a scenario designer to construct situations an established player can solve but a weaker player cannot.  
Use that performance gap as curriculum feedback, avoiding both trivial maps and universally impossible ones.  
As players improve, the generated scenarios change; retain discovered scenarios as deterministic regression fixtures.  
Sources: [Dual Curriculum Design](https://github.com/facebookresearch/dcd), [minimax](https://github.com/facebookresearch/minimax/blob/main/README.md).  
Attacks: §1.2b’s run-minutes and §1.6’s owner-driven scenario invention; adds **regret-based environment generation**.

**29. Compile a learned player into a decision tree**

Use a trained policy to label compact states, then fit a decision tree that approximates its actions.  
Execute the tree as ordinary local code and inspect its branches; use value-aware extraction when the teacher supplies suitable action values.  
Measure disagreement and task performance on held-out real-game episodes before replacing the teacher.  
Source: [VIPER policy extraction](https://proceedings.neurips.cc/paper/2018/hash/e6d8545daa42d5ced125a4bf747b3688-Abstract.html).  
Attacks: §1.0’s low active utilization and §1.3’s hot-loop latency; converts learned behavior into **inspectable deterministic execution**, rather than retaining a model call per decision.

**30. Learn the owner’s preferences between play sequences**

Show the owner pairs of short, comparable play segments: understandable versus confusing, engaging versus tedious, recoverable versus frustrating.  
Train a small trajectory-preference model and use it to find future segments that merit review or guide player training.  
Keep preference judgments separate from correctness assertions; a learned preference is evidence about taste, not proof that a mod works.  
Source: [Deep reinforcement learning from human preferences](https://arxiv.org/abs/1706.03741).  
Attacks: §1.6’s repeated designer sittings and reopening design targets; extends small judges from screenshot defects to **learned experiential preferences**.

**31. Train in a cheap approximation, then transfer**

Build only enough of a subsystem’s environment to train a player: needs, movement costs, jobs, and a small action vocabulary.  
Randomize approximation parameters so the policy cannot depend on one overly convenient model, then measure transfer into real bridge episodes.  
Spend real-game training chiefly on transfer failures; correctness verdicts continue to come from RimWorld.  
Sources: [Domain randomization](https://arxiv.org/abs/1703.06907), [analysis of sim-to-real transfer](https://arxiv.org/abs/2110.03239).  
Attacks: §1.2b’s run-minutes; differs from a predictive surrogate by using the approximation to produce a **transferable controller**.

**32. Identify behavior with designed input pulses**

Apply controlled power, demand, temperature, or input-rate changes while recording the subsystem response.  
Fit delays, gains, settling times, or oscillation characteristics and compare those identified parameters across builds.  
A short diagnostic excitation can expose a wrong time constant or feedback loop that a long steady-state run hides.  
Source: [SIPPY system identification](https://github.com/CPCLAB-UNIPI/SIPPY).  
Attacks: §1.2b’s run-minutes and §1.6’s repeated manual diagnosis; adds **experimental system identification** beyond predicting individual next states.

**33. Find the throughput limit without hiding overload**

Offer bridge work at controlled arrival rates independent of response completion, then increase load in stages.  
Measure queue depth, latency distribution, tick progress, and dropped or rejected work; locate the point where the queue grows persistently.  
This avoids a request–wait–request benchmark automatically reducing pressure whenever the system slows.  
Source: k6’s [open versus closed workload models](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/?pg=blog&plcmt=body-txt).  
Attacks: §1.3’s gap between **4–21 ms main-thread calls** and **0.21–0.72 s logged means**; determines usable harness capacity, beyond a per-mod timing gate.

**34. Amplify lifetime leaks through rapid teardown cycles**

Repeatedly create, use, destroy, and reload the same mod objects while tracking retained instances, event subscribers, and cache entries.  
After warm-up, look for growth per lifecycle rather than waiting for an overnight session to exhaust memory.  
Use mod-owned counters or weak references first; detailed heap tooling depends on what the shipped Mono player supports.  
Source: Unity’s [snapshot-comparison memory workflow](https://unity.com/blog/engine-platform/everything-you-need-to-know-about-memory-profiler).  
Attacks: §1.2b’s warm-game run time and §1.1’s cold-start churn; the measurements do **not** establish leaks already exist—this targets failures that could undermine long-lived test instances.

**35. Test historical save migrations as versioned edges**

Keep small saves produced by released mod versions, including awkward intermediate states.  
Load each into the candidate build, assert migration-specific requirements, save again, and reload to check that migration is idempotent.  
Represent supported upgrades explicitly, so testing focuses on actual compatibility promises rather than every possible version pair.  
Source: original proposal here, extending the supplied save/load work to **cross-version migration**.  
Attacks: §1.6’s **70-commit moving codebase** and expensive late regression reproduction; ordinary same-version round trips cannot cover this.

**36. Check that test shortcuts preserve the gameplay path**

For selected actions, reach the same intended outcome through a debug/helper operation and through normal designation, reservation, work, and completion.  
Compare which lifecycle hooks and side effects actually occur, then label helper operations with the behaviors they bypass.  
Use shortcuts for valid setup while requiring the natural path for acceptance criteria involving those omitted behaviors.  
Source: original harness-fidelity proposal; [RimBridgeServer](https://github.com/pardeike/RimBridgeServer) exposes both debug actions and gameplay/UI control.  
Attacks: §1.1’s proof/site defects and §1.6’s late regressions; adds **validation of the test stimulus itself**, beyond mutating the mod to test assertions.

**37. Assert UI meaning instead of matching whole screenshots**

Expose stable semantic identities and properties for relevant controls: enabled state, selected style, tooltip, displayed value, and action binding.  
Drive and assert those properties directly, reserving images for appearance questions; add an adapter for RimWorld’s UI where Unity hierarchy inspection is insufficient.  
This catches a wrong or disabled control without requiring a vision judgment of the entire screen.  
Sources: [AltTester Unity SDK](https://github.com/alttester/AltTester-Unity-SDK), [Poco](https://github.com/airtestproject/poco), existing [bridge UI-layout support](https://github.com/pardeike/RimBridgeServer).  
Attacks: §1.1’s proof/site failures and §1.6’s owner-look dependence; adds **semantic UI assertions**, beyond recording clicks or checking screenshot usability.

**38. Search for the most plausible failure sequence**

Let a search controller choose environmental disturbances while the ordinary player continues trying to succeed.  
Reward reaching a failure while penalizing unlikely disturbance sequences, producing a plausible explanatory path rather than only maximal destruction.  
Use tree search over disturbance choices and replay the resulting sequence as a deterministic repro; likelihood claims require a defined disturbance model.  
Source: the open-source [AdaptiveStressTesting implementation](https://github.com/maxiaoba/AdaptiveStressTesting).  
Attacks: §1.2b’s run-minutes and §1.6’s owner-led edge discovery; differs from the existing chaos storyteller through **likelihood-aware trajectory search**.

The five I find most non-obvious, without ordering them by merit:

- **03 — Surrogate control variates:** use approximation errors to reduce required real-game samples.
- **04 — Rare-failure trajectory cloning:** multiply promising histories instead of starting more ordinary colonies.
- **18 — New assertions over old telemetry:** answer some new questions without running the game again.
- **23 — Unit tests carved from live play:** turn expensive executions into cheap, realistic test contexts.
- **28 — Scenarios generated by player disagreement:** automatically seek situations that are difficult but demonstrably solvable.
