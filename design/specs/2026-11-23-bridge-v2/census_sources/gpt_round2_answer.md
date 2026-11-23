1. **The six most serious holes**

- **Causal attribution is replaced by entity ownership.** Row 4 requires a cause that “names an entity that is neither cast nor a thing of the mod under test.” A FlowWorks bug routes its rescuer into a vanilla fire; the fire damages it and invalidates the rescue opportunity. Row 4 can excuse the mod. **Smallest fix:** require evidence that the spoiler arose independently of the tested behaviour, using a validated attribution rule. Otherwise UNRESOLVED, as the policy requires.

- **A broken eligibility check becomes an apparatus fault.** “APPARATUS FAULT if a step is refused” conflicts directly with the ordered-rescue claim, which leaves “the giver’s eligibility” under test. A regression making that giver reject every valid rescue escapes MOD FAILURE. **Smallest fix:** distinguish failure to deliver an order from the tested giver’s refusal. The contract decides whether refusal violates the claim.

- **Probe arming is mistaken for continuous observation.** “One synthetic event through each tap at arm time” cannot justify “‘No event’ then means that nothing happened.” A synthetic event can exercise one route while the real event uses an uninstrumented route; a tap can also stop after arming. Silent damage plus an unchanged cached health value can produce SUCCESS. **Smallest fix:** require coverage claims by event route, continuous observation-health records, and terminal reconciliation against independent state. Unproved coverage remains COULD NOT LOOK.

- **The execution model changes the subject without bounding the evidence.** “The driver must do that work between ticks as play does” does not specify frame-to-tick scheduling; pinning update rates additionally changes execution. **Verified in Multiplayer source:** it deliberately relocates manager updates into ticks and commands; that establishes a deterministic execution model, not equivalence to ordinary play. **Smallest fix:** distinguish ordinary-play execution from normalized execution, declare the latter’s evidence limits, and require comparison on timing-sensitive claims. [Multiplayer source](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/AsyncTime/AsyncTimeComp.cs)

- **Run receipts do not implement the policy’s verdict rules.** “The second passes on one SUCCESS among its copies” omits the policy’s veto from any MOD FAILURE or UNRESOLVED on the same claim/build. There is no specified durable aggregation, budget enforcement, reclassification history, or hunt-opening notification. **Smallest fix:** require a scene verdict ledger implementing policy §§3–5, including X/Y yield rules and explicit hunt notices.

- **Repair can erase the evidence.** Reassert “repairs what drifted”; “Only the third list stops a scene”; it is “safe to call at any time.” If called during a deciding window, it could extinguish fire or restore settings whose change was the failure. **Smallest fix:** prohibit undeclared repairs during observation. Record the original violation irreversibly before repair, preserve its verdict consequences, and distinguish preparation repairs from interventions.

2. **Classifier counterexamples and ordering**

Row 4’s “external” is **not causally decidable as written**. A program can match an external-kind list; matching does not prove external origin. Nor does temporal precedence prove causation.

Concrete wrong classifications:

- **Mod → ENVIRONMENT:** the mod removes protection, exposing its actor to vanilla heat. Heat precedes opportunity loss and matches an external category.
- **Environment → MOD FAILURE:** another mod destroys the subject. The default forbidden effect, “a cast thing destroyed,” triggers row 1. This actually follows the policy’s unconditional forbidden-effect rule. The design must expose that attribution consequence or obtain a policy amendment.
- **Apparatus → SUCCESS:** a destruction tap passes its synthetic test but misses the real destruction route; a stale alias still returns its last healthy state. No recorded blindness reaches row 2.
- **Mod → APPARATUS:** the tested giver wrongly refuses an eligible order.
- **Expected transition → UNRESOLVED:** an opportunity requires the victim to remain downed throughout, while successful rescue includes treatment. The language permits this contradictory contract.

Keep observed forbidden effects first because policy demands it. After that, rows 2 and 3 need cause-sensitive precedence: a known driver failure with resulting telemetry loss should identify APPARATUS FAULT; a crash without established cause remains COULD NOT LOOK.

Rows 6–9 also need explicit endpoint semantics and sufficient observed opportunities. Prevent kind A from declaring an allowed random miss. Kind C must inherit its underlying A/B judging rules, rather than receive a separate catch-all.

3. **Calm profile**

These HELD claims exceed their evidence:

- “Incidents from any other caller”: the stated choke point covers callers that use it, not every implementation of equivalent behaviour.
- “Visitors, traders, caravans, orbital traders”: a universal guarantee rests on a partly read classification.
- Quest offers, inspirations, temperature, plant growth, and mental-state completeness are admitted guesses. They cannot be promised profile guarantees before verification.
- “Needs of bystanders … none needed” omits verification that the hold remains effective.
- A disabled scheduler cannot count hypothetical incidents it never generated. Distinguish prevented scheduling opportunities from actual blocked attempts.

These engine routes were **not independently verified here**; the objection is that the design promotes its own partial evidence into guarantees.

“A fence … steps past nothing that the scene tests” is false for claims involving reservations, congestion, target selection, rescue competition, or resource availability. Held needs, incident suppression, weather locks, and pinned update rates can likewise change those decisions. Each needs an evidence-limit declaration, like force levels.

Missing watchers include mutations of existing objects, stack transfers, fuel/power/liquid changes, reservations and target changes outside the station, settings dependencies, and asynchronous replies. Ownership does not reveal the originating cause.

“No breach” establishes isolation only relative to demonstrated watcher coverage.

4. **Telemetry and the flapping bird**

“Declared probes + value paths + named plug-ins” needs a separate exploration lane. Keep versioned, validated observers for acceptance; retain constrained, recorded exploratory scripts on disposable games. A sent program can be hashed, versioned, and subsequently validated. Deployment form does not establish correctness.

“Resolves the path once … cost of a field read” overlooks changing jobs, replaced components, null intermediates, containers, and getters with computation or side effects. Require declared null semantics, rebinding, freshness, read-only guarantees, and measured observation cost. These are requirements, not implementation choices.

The three flight layers answer different questions. Draw intent still fails to prove submission, visibility, occlusion, texture contents, correct materials, or that consecutive rendered frames actually show motion. A resolver-generated filmstrip may bypass the defective ordinary rendering route.

“The west view is the mirrored east view” must be an asset-specific contract, not a universal expectation. Likewise, require every animation frame only when the observed flight lasts long enough.

The design’s clock and renderer claims were **not independently verified here**.

5. **Fast repeats**

“Stamp again” is suitable for verified local claims. Calling every stamp “an honest new sample” is unjustified. Persistent state can change successive opportunities, and side-by-side copies can alter one another’s targeting and resource competition. A cluster label acknowledges dependence without measuring or removing it.

Reset verification compares only declared state. It misses undeclared caches, event subscriptions, pending callbacks, world relationships, allocator-dependent behaviour, and cross-station references. Add periodic fresh-map/process comparisons and a growing reset-dependency inventory.

“When a fault shows … writes a save of … START” requires a checkpoint already captured at arm time. State its unconditional capture cost, retention budget, and coherent relationship to the recorded random state.

The trajectory fingerprint is a **divergence alarm, not sample identity**. Equal random-draw counts can hide different draw values or consumers; equal positions/jobs can hide different health, liquids, reservations, and animation. Different fingerprints can still belong to an attempted replay. Record sample/replay provenance explicitly; use claim-specific state/event fingerprints diagnostically, never to certify independence or deduplicate automatically.

6. **Scene language and examples**

The census demands “a save and load mid-span.” The language specifies neither a save/load action contract nor what survives it: timeline position, observer rearming, alias binding, clock continuity, settings, and completion readiness. A generic “do this” slot does not deliver that capability. The Bazaar’s asynchronous stubbed reply similarly lacks request matching, timeout, and late-reply semantics.

“Only `claim`, `cast`, `act`, `success` and `end` are always needed” conflicts with mandatory policy declarations of entry point and valid opportunity. Defaults must be explicit, inspectable contract expansions.

An always-passing scene can assert an initial fact—`carrier.alive`—and end before its scheduled explosion. It uses game state and defeats the “mod says” restriction. Require act execution, actual exposure, and claim-relevant change. “Shown both ways” needs independently selected mutants; an author-chosen disabling setting can produce a trivial red without validating the intended oracle.

Example defects:

- **Carrier:** damage to the carrier does not prove the carried victim was exposed to the relevant damage path. Its exposure oracle needs separate justification.
- **Rescue:** “not in pit.cells” allows an incorrect destination; “job !=” includes interruption or failure. Assert the intended destination and completion condition.
- **Flight:** define quantification over birds, partial flights at timeout, and non-takeoff versus broken-flight outcomes. Do not charge incomplete observation as a random miss.

Fifteen minutes is plausible for transcribing an established fixture. It is not credible for developing the contract, instrumentation, attribution, and mutation evidence.

7. **Reorder the first ten**

By stability per effort:

1. Truthful replies, instance locking, loaded identity.
2. First-error capture and external process watchdog.
3. Minimal tracks/taps, freshness, durable trace.
4. Small scene runner using ordinary execution.
5. Build/read-back/capability assertions.
6. Minimal calm profile, restore, and existing holds.
7. Through-giver orders with refusal semantics.
8. Durable verdict ledger, contract lint, mutation checks.
9. Reset-verified repeats.
10. Targeted draw/UI adapters.

Defer a custom normalized tick driver until ordinary execution shows a measured bottleneck. Universal sweeps and render transcripts have speculative effort estimates. Loaded DLL identity also requires load-time evidence; it cannot be reconstructed reliably from today’s disk file.

8. **Cuts and wrongly surrendered territory**

Cut universal “anything changed” attribution, generic UI transcription, and comprehensive pre-run prediction from the initial scope. Replace each with explicit supported coverage and targeted adapters.

“Natural scenes at force level 0 … policy already leaves these” misstates the policy. The policy permits an explicitly declared testing horizon; it does not categorically exclude natural acceptance scenes. Retain budgeted natural decision tests where forced orders bypass the important decision.

Finally, “the watchers catch what no suppressor holds” must go. Unknown influences remain unknown until coverage demonstrates otherwise. Sound taste can remain outside automation; missing audio, wrong sound routing, and gross timing defects need not.