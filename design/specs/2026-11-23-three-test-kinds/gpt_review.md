The draft leaves three things dangerously interchangeable: evidence that a capability worked once, evidence that it is reliable, and permission to stop spending on an unresolved defect. Those need separate meanings even with A/B/C fixed.

**1. BREAKDOWN: the eight most serious failures**

The likelihoods below are subjective estimates of encountering each problem across several mods and repeated agent visits, not measured defect rates.

1. **A bug can destroy its own preconditions and then be excluded as an environment fault.**

   Scene: the spared carrier must be inside the blast. A knockback bug moves the carrier prematurely, before the harness records the explosion’s target set. Runs 1–4 find the carrier outside and record ENVIRONMENT FAULT. Run 5 happens to preserve the ordering and succeeds. The scene passes.

   Likewise, a rescue mod can corrupt a reservation, leaving “a valid reachable rescue target” false. The harness excludes precisely the runs containing the defect.

   **Wrong outcome:** a real bug passes through outcome-dependent exclusion. Calling the check a “precondition” does not make it external to the mod.

   **Likelihood: high, roughly 70%.** Pawn position, jobs, reservations, health and faction state are common things both the environment and mods change.

2. **Kind B certifies existence while its description implies reliability.**

   Scene: an intended 50% drop capability is broken and produces a drop only 1% of the time. The tester budgets 100 opportunities. Ninety-nine misses can all look like legitimate random outcomes; one drop passes the scene. The probability of at least one drop is about 63%.

   For a supposedly reliable capability, honest classification helps but does not solve this: a capability that works only 10% of the time still has a 10% chance of passing on its first valid opportunity.

   **Wrong outcome:** a broken frequency or intermittently broken capability receives an unqualified PASS.

   **Likelihood: high, roughly 80%,** if “traced success” is presented as proof of the whole feature.

3. **An unexplained failure can coexist with a passing verdict.**

   Scene: run 1 successfully lifts a pawn. Run 2 leaves the pawn missing; the agent cannot distinguish despawning, an observation gap and an invalid map reference. After one read it records an unclassed failure. There is no second occurrence, so no C hunt opens. There is one success and no run *classed* MOD FAILURE: PASS.

   Alternatively, the second incident has a different symptom and never counts as “the same” unexplained failure.

   **Wrong outcome:** ignorance is treated as favorable evidence. Agents can game the tag by declining to attribute failures.

   **Likelihood: high, roughly 75%.** Attribution is hardest exactly where the defects are most consequential.

4. **Forcing can bypass the feature while producing its expected final state.**

   Scene: FlowWorks’ job-selection patch never offers a rescue. Directly ordering the rescue job works twice. The tester calls the capability fixed because “rescue happened.” The broken selection path remains.

   Sequence: natural scene fails → direct job succeeds → natural scene is replaced → acceptance goes green.

   **Wrong outcome:** a real integration bug passes. Conversely, teleporting onto a pit may omit a normal movement notification and falsely fail correct code.

   **Likelihood: very high, roughly 85%.** The bridge is explicitly able to intervene at several different layers.

5. **“Traced success” can become a self-authored assertion that proves nothing.**

   Scene: the mod logs `RescueComplete` before moving the pawn, or the bridge reads a success flag the mod itself set. An exception prevents the actual transfer. The program accepts the flag.

   A quieter version: the carrier survives because no damaging blast reached it, yet a screenshot and a “protection applied” log produce a pass. The test never established that the protection had anything to prevent.

   **Wrong outcome:** a no-op, partial implementation or wrong actor passes. More runs repeat the same blind spot.

   **Likelihood: high, roughly 70%,** unless observation contracts are specified independently of the implementation.

6. **Persistent verdicts accumulate into a suite that no actual candidate satisfies.**

   Sequence: scene A passes on DLL 1. A shared job helper changes for scene B, but nobody identifies A as affected. B passes on DLL 2. The game process still has an older assembly loaded, or the full mod list has also changed. The ledger says both passed.

   Even with correct build tracking, an earlier scene may leave a reservation or global setting that changes a later scene. Per-scene persistence does not establish isolation.

   **Wrong outcome:** stale evidence certifies the final candidate, or contamination falsely blocks it.

   **Likelihood: high, roughly 70%.** “Touches what the scene reads or exercises” is substantially harder to determine than a source diff.

7. **Closing a C hunt can erase an unresolved defect.**

   Scene: a pit transfer duplicates a pawn once in 18 runs. The next hunt does not reproduce it. The hunt and tripwire are removed; one line says “rare transfer anomaly.” Later, another agent treats the absence of an acceptance failure as evidence of resolution.

   A related sequence: fix claimed → no reproduction → expensive regression retired because recurrence is not “proved likely” → the fix never actually addressed the cause.

   **Wrong outcome:** stopping investigation is laundered into fixing the defect; its evidence becomes unusable.

   **Likelihood: high, roughly 75%.** The draft explicitly provides deletion but barely specifies the surviving record.

8. **Environment removal can consume more than the reruns it was meant to save.**

   Sequence: one animal interrupts a scene → remove animals → suppress replenishment → discover a mod spawner → reduce the mod list and cold-load → rebuild dependencies → create a bridge suppression hook. The original scene could have run in a confined room using an existing command.

   The shared list then claims “animals removed,” although the implementation only removed currently spawned animals.

   **Wrong outcome:** tokens burn on infrastructure; a correct mod remains blocked; the reduced configuration conceals the compatibility bug that mattered.

   **Likelihood: very high, roughly 85%.** The proposed cost ordering is not generally a cost ordering, and “each time” has no stopping condition.

**2. DEFINITIONS: overlaps, gaps and deciding wording**

Classification needs to attach to **a stated claim under a stated procedure**, not to a feature name such as “rescue.”

1. **Uncontrolled setup versus unreliable implementation: A or B?**

   Boundary: an explosion is reliable once the carrier is exposed, but pawn movement often prevents exposure.

   Deciding wording:

   > “A applies when the declared procedure can reliably establish a valid opportunity and the expected result is non-random. B applies when obtaining that opportunity remains uncertain after proportionate control, or when the specified result is intentionally random.”

   Once a valid, non-random opportunity exists, an incorrect response is a failure in either kind.

2. **Deterministic procedure with intermittent results: A or C?**

   Boundary: replaying the same saved pit scene sometimes duplicates a pawn. The draft says C’s “test itself is deterministic,” which could disqualify the very hunt needed.

   Deciding wording:

   > “For C, deterministic means that the procedure and failure predicate are specified; repeatable outcomes are not required. C records an investigation into a suspected intermittent defect.”

   That preserves the owner’s distinction without asserting that the simulator repeats exactly.

3. **A stochastic scene investigating an intermittent bug: B or C?**

   Boundary: natural raids provide opportunities; a deterministic tripwire detects duplicate pawn ownership during those opportunities.

   Deciding wording:

   > “A C hunt may use A or B scenes to obtain exposure. Record the hunt separately from those scenes’ acceptance verdicts.”

   This keeps C temporary without requiring a fourth kind or silently replacing the acceptance question.

4. **A missed opportunity versus failed autonomous behavior.**

   Boundary: no raider rescues the pawn. Is rescue selection outside the test, or part of the promised capability?

   Deciding wording:

   > “An event required by the capability’s claim is an expected behavior, not an environmental precondition.”

   If the claim is “an ordered rescue completes,” selection is outside scope. If it is “eligible comrades initiate rescue,” selection is under test.

5. **A legitimate random miss has no outcome category.**

   Boundary: an eligible 20% drop rolls no drop. That is neither MOD FAILURE nor ENVIRONMENT FAULT, and observation succeeded.

   Add an outcome:

   > “EXPECTED RANDOM NON-SUCCESS: a valid opportunity with an allowed non-success result.”

   Keep its denominator. Do not put it under an environment tag.

6. **A single ambiguous incident: B or C, and what happens now?**

   Boundary: one pawn disappears, but no cause is known and no repetition occurs.

   Deciding wording:

   > “An observed violation may open C after one occurrence. Ambiguous evidence is recorded as unresolved; it does not count as success or as a demonstrated external exclusion.”

   Repetition should increase urgency, not be the prerequisite for acknowledging a potentially serious defect.

7. **An invalid A run contradicts “a failure is a real failure.”**

   Boundary: the bridge crashes before issuing the explosion command.

   Deciding wording:

   > “A has one valid observed run. Harness, setup and observation faults do not decide the mod verdict.”

   A remains the default. It does not acquire immunity to apparatus failure.

8. **Reliability and occurrence rate are different B claims.**

   Boundary: a rare rescue opportunity is hard to arrange, versus a rescue that intentionally succeeds only some of the time.

   Deciding wording:

   > “B states whether uncertainty concerns exposure, the specified outcome distribution, or both. Its acceptance claim states which of these was demonstrated.”

   “Too many variables” alone is not a deciding definition. It needs named residual influences and a bounded account of control attempts.

**3. KIND B JUDGING**

**One traced success is defensible as a narrow capability witness. It is not a reliability certificate.** No cheap counting rule can remove that distinction.

Three examples show where the present rule breaks:

- A 50% drop implemented as 1% can eventually produce the one success sought.
- A reliable effect that fails on one pawn race can pass on another. Repeating the favorable fixture never exercises the broken configuration.
- A rescue that completes once but corrupts state afterward can pass if observation ends at the first favorable event.

“No observed mod failure” means little unless valid opportunities, exclusions and observation duration are all explicit.

For scale: with a fixed sample of independent, identically distributed valid trials and zero failures, the one-sided 95% upper bound on failure probability is \(1-0.05^{1/n}\). It is 95% after one success, about 45% after five, and about 9.5% after thirty. These are illustrations, not recommended live quotas. Correlated replays and outcome-dependent exclusions invalidate that interpretation. [NIST’s exact binomial method](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm).

The cheapest honest rule is:

1. **Declare the claim before running.**

   For example:

   > “An eligible directly ordered rescue transfers this pawn safely across this pit boundary.”

   That is narrower than “raiders reliably rescue comrades.” The scene can provide the former witness without pretending to provide the latter.

2. **Declare opportunity, success, forbidden effects and observation end.**

   The endpoint must cover the meaningful aftermath: destination ownership, job completion and any required cleanup. It need not wait indefinitely for hypothetical consequences.

3. **Stop on the first sufficient witness for an existence claim.**

   Further favorable repetitions usually add less value than checking a different relevant configuration. Preserve every relevant adverse observation already obtained; stopping cannot erase it.

4. **Do not pass through unresolved adverse evidence concerning the same claim and candidate.**

   Resolve its classification, fix the defect, or record an explicit scope/risk disposition by the Conductor or owner. This is not a demand for endless reruns: budget exhaustion produces INCONCLUSIVE, not a fabricated PASS.

5. **For intentionally random behavior, separate occurrence from rate.**

   A live witness may establish that an eligible outcome can happen. The probability calculation, eligibility logic and boundary behavior should usually be checked cheaply offline. If the game’s actual output rate is the important claim, declare an acceptable rate range and a statistical decision procedure before collecting the sample. A budget may prove insufficient.

   For illustration, if the question is merely “would a correct 20% mechanism produce at least one result?”, fourteen independent opportunities give about a 95.6% chance. That does **not** verify a 20% rate.

6. **Treat X-of-Y as expenditure unless it actually defines a statistical claim.**

   Define whether Y counts launches, valid opportunities or exposures. Record all three when they differ. Changing the budget is allowed prospectively with a reason; it cannot rewrite the meaning of observations already collected.

For an agent-free “traced success,” the program needs a scene-specific observation contract. A log message alone is insufficient.

For an ordered rescue, the bridge could establish:

- A unique run ID, pawn IDs, map IDs and a baseline state.
- An eligible target and an accepted production job.
- Actual pickup/containment and transfer events through the normal execution path.
- The same pawn appearing at the permitted destination, with consistent ownership and no duplicate.
- Completion and required cleanup by a defined endpoint.
- Continuous enough observation to detect the declared forbidden effects.

For carrier protection, it needs the correct carrier, the actual explosion event and relevant exposure facts, the protection path exercised, and the specified final health/carrying state. It must rule out vacuous survival because no effective threat existed.

Use ordinary game state and boundary observations alongside internal decision events. The mod announcing “I protected it” is evidence of a branch, not evidence that protection worked. Validate each important checker once against a deliberately broken, disabled or known pre-fix case where practical; do not require expensive checker validation on every run.

A compact structured receipt should contain the predicates, observed values, tick/phase stamps, result and links to a bounded detailed trace. Agents read exceptions and ambiguities, not every successful trace.

For automatic ENVIRONMENT FAULT classification:

1. Declare the external preconditions before the run.
2. Observe them inside the game at the relevant operation boundary, on the simulation thread or another verified consistent snapshot.
3. Monitor interval conditions across the interval they must hold. A rescue has several boundaries; one “deciding moment” is insufficient.
4. Record a concrete failed predicate and its supporting state.
5. Exclude the run only when that failure invalidates this claim and is established as external to the behavior being tested.

The crucial limitation: **a program generally cannot infer causal independence from a failed predicate alone.** “Pawn outside blast” is not automatically external. If the mod could have moved it, either use earlier state/events to distinguish causes or return unresolved.

Also, independent failures survive invalid setup. An unrelated animal interruption does not excuse a duplicate-pawn invariant violation.

**4. KIND C LIFECYCLE**

The lifecycle needs separate records for **the investigation**, **the defect**, and **acceptance**.

**Open**

A hunt needs a suspected invariant violation or concrete symptom, its evidence, affected candidate/configuration and a responsible investigator. “One or twice” should not be a numeric gate. One well-observed duplication can justify more action than ten ambiguous screenshots.

Opening C must preserve the source scene’s existing verdict and adverse evidence. Notify the Conductor as proposed, but make the notification actionable: what happened, why it matters, the next discriminating action, and the proposed spending limit.

**Hunt**

Count exposure to the suspected trigger, not merely runs. Twenty scenes containing no rescue attempts say little about a rescue defect.

Each investigation step should answer a question:

- Does the duplicate arise before or after map transfer?
- Does it require simultaneous rescues?
- Does save/load preserve the bad state?
- Does it occur only with a named patch present?

A tripwire needs an activation check, bounded trace storage and a capture path that survives the suspected failure where possible. “No tripwire fired” is uninformative if it never armed or the crash destroyed its output.

**Budget**

Do not invent a universal run count or failure-rate threshold.

Instead:

- Set a real expenditure ceiling in the project’s scarce units: another cold load, a pilot sitting, bridge work or a token allowance.
- Choose the smallest next batch that could distinguish the current hypotheses.
- Continue while the next action has a plausible decision consequence.
- End when the ceiling is reached or available actions no longer justify their cost.
- Extend only for a named new hypothesis or newly cheaper method, with the reason recorded.

The ceiling is an allocation decision. It need not pretend to be statistical proof.

**End**

The draft’s first outcome conflates finding a trigger with fixing a bug. Finding a reproducer is a milestone; the defect can remain open.

Use distinct closure reasons:

- **Fixed and verified:** cause/fix evidence and suitable post-fix validation exist.
- **Disproved or apparatus defect:** explain what invalidated the report.
- **Unresolved, investigation stopped:** reproducibility or expected evidence value no longer justifies spending.
- **Handed off:** another investigation owns the unresolved work.

Turning C into a forced A scene does not itself close the defect. Nor does the absence of recurrence establish that a speculative fix worked.

**Retire**

The active hunt and acceptance tripwire can be removed without marking the defect fixed. A serious unresolved defect still needs a release disposition; stopping its hunt does not decide whether to ship.

The surviving record should contain:

- Symptom, violated invariant and practical severity.
- Original traces, relevant save/fixture and reproduction instructions where available.
- Game/build/mod-list/settings/harness identity.
- Runs **and actual exposures**, with exclusions.
- Controls and hypotheses tried, and what each established.
- Fix and verification evidence, if any.
- Closure reason, remaining uncertainty and responsible decision-maker.
- Concrete reopening triggers: recurrence, an affected refactor, a new report or cheaper instrumentation.

“One line” can be the index entry linking this record. It cannot substitute for it.

**5. ENVIRONMENT CONTROL IN RIMWORLD 1.6**

I checked the Multiplayer project’s implementation and 1.6 release material. I did not inspect this project’s bridge or exact game binary. The assessments below distinguish feasible control designs from verified existing commands. Exact hook names and interactions need checking against the installed 1.6 build.

1. **Storyteller incidents: ordinary scheduling can be suppressed; all external events cannot be assumed suppressed.**

   A calm fixture needs control over scheduled incidents, already queued incidents and relevant quest/script sources. Turning down threat or disabling the ordinary storyteller path is not a contract that no visitor or mod-spawned threat will appear.

   Prefer scene-scoped suppression with an allowlist for intentionally injected events and a record of blocked events. A blanket incident gate can otherwise suppress the very incident integration being tested.

   **Confidence: high, about 90%, in the distinction; medium, about 65%, in implementation effort without inspecting the bridge.**

2. **Weather: setting it once and keeping relevant conditions stable are different operations.**

   A bridge can plausibly select weather and inhibit ordinary transitions for a short scene. Existing game conditions and mod hooks must also be considered. Stable weather does not imply stable temperature, snow, lighting, wind or accumulated environmental effects.

   Specify the variable the scene needs: “no rain during ignition” is more useful than claiming “weather frozen.”

   **Confidence: about 85% in the control strategy; about 60% that one generic hook covers this mod list.**

3. **Hour and season: initialize them; usually do not freeze the global clock.**

   Pawn jobs need ticks to progress. Holding all clock-derived behavior fixed while simulation advances requires selective virtualization, which can change schedules, cooldowns and periodic checks.

   Start at a chosen date/time and keep the scene short enough to stay in its declared interval. A scene genuinely testing a daily boundary needs a different profile.

   **Confidence: high, about 95%.**

4. **Needs: selected needs can be initialized or maintained, but that changes behavior.**

   Maintaining food/rest/mood over a short fixture is plausible. It is not equivalent to preserving all health, pain, consciousness, genes, drugs, custom needs or work eligibility.

   Use good initial conditions and a short interval before adding continuous clamps. Do not suppress an entire pawn update path just to stop hunger.

   **Confidence: about 85% conceptually; about 60% for generic coverage of custom pawn systems.**

5. **Mental breaks: ordinary initiation can likely be gated; blanket immunity is not established.**

   High mood is not a universal “cannot enter a mental state” guarantee. Existing mental states, scripted starts and mod-specific mechanisms need separate treatment.

   A suppression hook should report attempted interventions. If the feature concerns mental states or job interruption, suppression changes the tested capability.

   **Confidence: about 80% in the distinction; about 60% in coverage without code inspection.**

6. **Wild animals: removing existing animals does not prevent new ones.**

   A calm fixture needs initial cleanup plus control of replenishment, entry and relevant spawners. Scope it to unwanted animals: scene animals and non-wild pawns may be essential.

   For many scenes, a small controlled enclosure will be cheaper and less invasive than global animal suppression.

   **Confidence: about 90% in the distinction; medium in the complete source inventory.**

7. **Rand: state control is possible; whole-game replay from a seed is not guaranteed.**

   Multiplayer’s code explicitly saves/restores `Rand.StateCompressed` and uses `Rand.PushState`/`PopState`. That supports scoped RNG control. It does not make the world-generation seed a complete simulation checkpoint, nor cover every mod’s independent random generator. [Multiplayer RNG context implementation](https://raw.githubusercontent.com/rwmt/Multiplayer/master/Source/Client/AsyncTime/AsyncTimeComp.cs).

   Even the same RNG state produces different relevant draws when unrelated calls consume the stream. Use seeds for particular diagnostic fixtures, record them, and distinguish replaying one trajectory from sampling different trajectories. Never reseed repeatedly until the desired outcome appears and call that a probability test.

   **Confidence: high, about 95%.**

8. **Tick order: tick stepping helps; it does not establish complete determinism.**

   The 1.6 Multiplayer project includes explicit handling of scheduled pathfinding work and a merged pathfinder race fix. Its determinism patches also address frame-time-dependent behavior. That is evidence against treating all relevant behavior as one automatically repeatable serial tick loop. [Pathfinder implementation](https://raw.githubusercontent.com/rwmt/Multiplayer/master/Source/Client/AsyncTime/AsyncTimeComp.cs), [race fix](https://github.com/rwmt/Multiplayer/pull/846), [determinism patches](https://raw.githubusercontent.com/rwmt/Multiplayer/master/Source/Client/Patches/Determinism.cs).

   With roughly 300 mods, fix versions, load order, configuration, fixtures and command timing. Do not promise identical replay across process starts or machines without demonstrating it. Conversely, 300 mods do not automatically make every scene irreducibly stochastic.

   **Confidence: high, about 95%, in the limitation; low in any prediction of this project’s actual replay rate.**

My expected bridge priorities, subject to measuring existing capabilities:

1. **Atomic scene operations and bounded execution.** Pause, prepare, verify, arm observations, issue a command, advance until a predicate or tick limit, return paused. This removes tool round-trip races and repeated screenshot narration.
2. **Structured event capture and verdict predicates.** Stable entity IDs, positions, ownership, damage events, jobs, reservations and exceptions, with tick/phase stamps. Observation stability often buys more than another environmental suppression.
3. **Reusable fixtures with reset verification.** Check that reservations, scene objects, jobs and modified settings are cleaned up. Save reload is useful but should not be assumed to clear process-static mod state.
4. **An executable calm profile.** Report which controls actually armed, their scope and detected breaches. Support per-scene exceptions and guaranteed restoration.
5. **Loaded-build and configuration receipts.** Distinguish the assembly actually running from the file most recently compiled.
6. **Scoped RNG replay tools.** Useful for diagnosis; lower priority than reliable observations and command timing.

This ordering is an engineering estimate, roughly 75% confidence. I would measure avoided agent turns and invalid scenes before funding broad determinism work.

**6. MINIMUM FORCE**

The ladder is an example of progressively preserving more behavior, not a general ordering of test quality or cost.

- **Teleportation** can isolate occupancy consequences but bypass movement, collision and entry notifications. It can falsely pass broken traversal integration or falsely fail code that correctly depends on normal movement events.
- **Assigning a path or job** can exercise execution while bypassing selection, eligibility checks or ordinary job acquisition. Its meaning depends on the exact bridge operation.
- **A baited corridor** preserves more selection behavior but changes reachability, danger assessment, congestion and target choice. It can conceal bugs involving alternative routes.
- **A natural raid** exercises broader integration, but the relevant opportunity may never happen. Its absence is not a feature failure unless the claim requires it to happen.

The key question is: **which production behavior remains between the intervention and the observed result?**

“Force the environment, never a decision our own mod’s code makes” is not decidable from the draft’s terms. A mod can patch vanilla job selection, path cost, reservation or incident eligibility. Ordering a vanilla job may therefore bypass the mod’s decision. Changing the environment can also predetermine that decision.

Replace the boundary with:

> “Declare the production entry point and the decisions this scene claims to test. Intervene before those decisions. Any bypassed behavior is outside this scene’s evidence.”

For FlowWorks, a direct rescue order could prove execution and cleanup. A separate, targeted eligibility/selection check is needed if autonomous rescue is promised. That selection check need not wait for an entire natural raid.

Also record fixture validity. A forced job that no supported gameplay state can legally initiate may expose a robustness defect, but it does not automatically refute the advertised behavior.

Finally, “why a lower-force step was not used” should not require trying every weaker intervention. An explained cost estimate is sufficient. Otherwise the ladder becomes another token-burning ritual.

**7. THE PRINCIPLE**

The wording can remain untouched. Its dangerous applications are operational:

- “Rare” is treated as “low value,” ignoring severity and frequency of exposure in real play.
- Lack of recurrence is treated as evidence of low recurrence after the tripwire is removed.
- The cost of keeping one check is assessed separately, while its diagnostic value across several features is ignored.
- The cost of a cold load is charged in full to every scene rather than considering the marginal cost of an already-running visit.
- Retirement improves the tester’s completion metric, so troublesome scenes disappear first.
- A test with an expensive current implementation is retired before considering a cheaper oracle or offline equivalent.
- “Likely to return” is interpreted as requiring proof about the future. Regression risk rarely supplies that proof.
- A slow or incomplete offline substitute is called “coverage moved offline” despite omitting the production integration.
- The owner’s walkthrough becomes an assumed substitute without evidence it will encounter the configuration.
- Periodic review itself becomes costly ceremony, or never happens because nobody owns it.

Two operating rules would prevent most of this:

1. **Retirement preserves both the claim and unresolved risk.** Record what decision the evidence informed, why its future marginal value no longer pays, what cheaper evidence replaces it if any, and what reopens it. The Conductor or owner makes scope/risk dispositions; a tester may propose them. Batch these decisions into existing milestone reviews.
2. **Judge marginal cost against expected decision value, including consequence.** Consider exposure, severity, uncertainty, diagnostic usefulness and alternatives. A rare pawn-loss defect may earn testing that a common cosmetic defect does not. Retiring a test does not resolve an observed defect.

**8. FIXES: concrete edits, most valuable first**

1. **MUST — Replace B’s pass sentence.**

   Replace:

   > “The test passes on evidence of success: at least one traced success, and no run classed MOD FAILURE.”

   With:

   > “For a declared capability-witness claim, B passes on at least one machine-checked success, with no unresolved adverse observation or mod failure relevant to that claim and candidate. This establishes the witnessed behavior, not its reliability or occurrence rate.”

2. **MUST — Replace automatic precondition exclusion.**

   Replace:

   > “A run whose preconditions did not hold is an ENVIRONMENT FAULT.”

   With:

   > “A run is ENVIRONMENT FAULT only when recorded evidence establishes that an external condition invalidated this observation. A condition that the tested behavior could have broken is unresolved until distinguished. Independent observed defects remain defects.”

3. **MUST — Add an executable scene contract.**

   > “Each scene declares its claim, production entry point, valid opportunity, required observations, success predicate, forbidden effects and observation endpoint. Predicates are versioned with the scene.”

4. **MUST — Add missing outcomes and an inconclusive scene verdict.**

   Add EXPECTED RANDOM NON-SUCCESS and unresolved adverse evidence to the run record. Add INCONCLUSIVE as a scene verdict when the budget ends without deciding evidence.

   Define APPARATUS FAULT as a demonstrated harness/control failure, and COULD NOT LOOK as insufficient observation. Neither is favorable mod evidence.

5. **MUST — Replace the random-rate sentence.**

   Replace:

   > “the test states the expected rate and the count that would show it”

   With:

   > “The test distinguishes demonstrating an outcome from checking its rate. A rate check declares an acceptable range, valid-opportunity denominator, sampling assumptions and decision rule. Exhausting its budget may leave the rate unverified.”

6. **MUST — Replace the A judgment.**

   > “A uses one valid, adequately observed run. Correct behavior passes; a demonstrated violation fails. Setup, apparatus and observation faults do not decide the mod verdict.”

7. **MUST — Strengthen persistent-verdict identity.**

   Replace the first bullet of section 4 with:

   > “Evidence records the loaded build, game/DLC/mod configuration, fixture, controls and checker version. Reuse requires an explicit unaffected judgment for relevant changes; uncertain dependencies invalidate only the affected evidence. A later relevant defect overrides an earlier success.”

   Include runtime state dependencies when scenes share a session.

8. **MUST — Separate hunt closure from defect resolution.**

   Replace C’s three endings with the closure reasons in section 4 above. Explicitly add:

   > “Finding a trigger, ending a hunt and removing an acceptance check do not by themselves fix or accept the defect.”

9. **MUST — Replace C’s one-line retention rule.**

   > “Retirement leaves a linked defect record containing original evidence, configuration, exposures, investigation results, closure reason, remaining risk and reopening triggers.”

10. **MUST — Replace the force boundary.**

    Replace:

    > “Force the environment. Do not force past a decision that our own mod’s code makes”

    With:

    > “Use the least force that makes the scene affordable and reliable while preserving the production decisions it claims to test. Record the entry point and bypassed behavior.”

11. **SHOULD — Replace the unexplained-failure escalation rule.**

    > “Record the first unexplained adverse observation and its effect on acceptance. Open C when investigation is warranted; one credible serious occurrence is sufficient. Repetition triggers Conductor review but is not required to open a hunt.”

    Preserve the explicit notification rule.

12. **SHOULD — Replace the mandatory environment-removal ordering.**

    > “After identifying a confounder, choose a proportionate control using expected total cost and preserved test meaning. Reuse existing controls first where suitable. Further infrastructure work is bounded; residual uncertainty may justify B.”

    Delete the claim that the existing five-step sequence is an “order of cost.”

13. **SHOULD — Make the shared control list executable and qualified.**

    > “A shared control records implementation, scope, verified configurations and known escapes. A scene checks that its required controls are active; a historical entry is not proof of current control.”

14. **SHOULD — Add hunt and scene spending limits.**

    > “Before spending, state the next decision the work may change and its expenditure ceiling. Extend for a recorded new reason. Budget exhaustion changes the evidence status, not the observed facts.”

15. **SHOULD — Replace “Nothing else gates the tag.”**

    > “The program checks that required evidence fields and referenced observations exist. The tag changes the procedure; it cannot erase observations, broaden the claim or decide release risk.”

    Non-empty text alone is almost no protection against a gamed tag.

16. **SHOULD — Add the two retirement operating rules from section 7.**

    Assign decisions to existing Conductor/owner milestone reviews. Do not create a separate recurring review meeting.

17. **NICE — Clarify the no-repeat exception.**

    Replace “unless that scene’s tag says why” with:

    > “Any required repetitions state the additional evidence sought and stopping rule. A remains a one-valid-run test.”

    This prevents a note on an A tag from reinstating consecutive-pass requirements.

18. **NICE — Replace the aspirational suite metric.**

    Replace:

    > “The aim is that a correct mod almost never fails a live suite.”

    With:

    > “Track demonstrated mod failures separately from invalid and inconclusive scenes, and reduce the cost of obtaining deciding evidence.”

    Otherwise relabeling failures can appear to achieve the objective.

**9. What to cut to halve the final rule text**

Cut explanation and duplication, not distinctions that affect verdicts.

- **Remove the drafting wrapper:** item history, timestamps, next steps and “working text” notices.
- **Remove the two historical examples from the rule.** Keep them in the rationale document.
- **Remove the verbatim owner transcript from the rule.** Preserve it in the design record.
- **Remove the open-points section.** Resolve those points into requirements or implementation tasks.
- **Move placement instructions out of the normative text.** Charter and skill destinations belong in the enactment task.
- **State tag authority once.** Tester proposes/assigns with evidence; Conductor and owner retain scope/risk authority. Eliminate repeated accounts of rescue involvement, while retaining mandatory hunt notification.
- **Use one shared scene contract.** A/B/C should state only their differences; do not repeat identity, observation, fault or budget rules.
- **Make run outcomes and scene verdicts one compact definition block.** Avoid repeatedly explaining that an invalid run needs no compensating pass.
- **Keep the minimum-force rule and one short ladder example.** Move the extended tradeoff discussion into the live-testing skills.
- **Move calm-environment implementation detail into a versioned bridge profile.** The policy should require scoped, verified controls and stated exceptions.
- **Combine C endings and retirement into one lifecycle paragraph**, with a pointer to the required surviving record.
- **Keep verdict reuse once**, including its identity and invalidation conditions.
- **Keep the Principle verbatim.** Delete corollaries already expressed by lifecycle and retirement rules.
- **Compress the horizon to one sentence:** “State the configurations and claims left to walkthrough or real play.”

The final rule should spend most of its words on what constitutes evidence, what a verdict means, and what survives when spending stops. Those are the parts agents otherwise improvise under pressure.