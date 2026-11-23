**The repairs close the original stale-sample case and narrow the re-judgement claim correctly. They still do not establish that a complete trace describes an undisturbed run, that a certified tap remains trustworthy in another session, or that a planted fault actually caused the red result.**

1. **The twelve “folded in” findings**

   | Finding | Judgement | Remaining failing case |
   |---|---|---|
   | Stale sample after an act | **SUFFICIENT** | The original case is closed by prohibiting termination on an act tick and requiring a final sample. |
   | No rerun for a wrong check | **SUFFICIENT** | The revised claim explicitly excludes changes to staging, acts, termination and observation. Implementation must compare those execution inputs; checking only for missing track names would not enforce the rule. |
   | Pause can be refused | **SUFFICIENT** | Admission, pause read-back and the check after the frame address the identified failure. |
   | Canary rite | **PARTIAL** | A foreign prefix can consult a mutable setting or static flag. Certification exercises its permissive branch; the scene exercises its suppressing branch. Companion hash, mod list and patch inventory remain identical. |
   | One restore | **PARTIAL** | Releasing frozen needs does not return the depletion or consequences suppressed during the hold. Also, loading a fixture does not undo process-static changes, although NOT UNDONE offers a fresh load as a recovery. |
   | Shown both ways | **PARTIAL** | A mutant setting reads back correctly at the act, but the mod uses a cached value established earlier. Exposure holds and the red run fails for another reason. The specified evidence establishes assignment, not consumption or causation. Fresh loads also do not equalize RNG or statics. |
   | Stage chosen by cost | **SUFFICIENT** | The map-kind choice now follows the claim. Whether a cast-only settlement represents a colony remains a separate, unresolved issue below. |
   | PLAY is not one configuration | **PARTIAL** | Qualification is “per scene,” without an explicit validity key. A later build changes per-frame behaviour while retaining the scene name; its old fast-mode comparison can remain eligible. Qualification must expire with relevant build, plan, settings and configuration changes. |
   | Joining cost and treatment of C | **PARTIAL** | The fairer C is described, but “Only A and B allow the judge outside the game” remains false. A compiled companion fixture that records facts for Python judgement is the document’s own counterexample. The supposedly narrow first ticket also remains large. |
   | Vanilla facts read as universal | **SUFFICIENT** | The scope qualification closes that particular overclaim. It does not make the certificate sufficient. |
   | Build order | **PARTIAL** | Certification needs held/refused routes whose gates are built later by the calm ticket; the calm ticket itself needs certification. Several listed mutation tests also lack a distinguishing fixture. |
   | Owner page | **PARTIAL** | The ArchBig table permits scenes where the TEST-only kernel cannot run under CAMPAIGN, and its camera prohibition conflicts with choice 4. Details below. |

2. **The three “not taken” reasons**

   - **Fourth architecture: substantially sound.** Transport-neutral cores, an adapter and compiled fixtures need not constitute another architecture. But decision 5 specifies probe discovery more clearly than it specifies an accepted compiled *fixture* lifecycle. Define how such fixtures stage, act and record through the kernel without supplying their own verdict. Delete the surviving “Only A and B” assertion.

   - **Missing owner decisions: sound under the stated standing rule.** Nothing supplied establishes that retention, ordinary compute time, hook policy or forced-scene restrictions require his decision. They still need explicit Conductor decisions and operational limits. “Not the owner’s decision” does not mean “no decision needed.”

   - **Cast-only stage instead of representative colony: insufficient reason.** Twenty-three spoiled records justify an isolation tier; they do not establish transfer. A bug can depend on colony population, wealth, reservation pressure or a map-wide cache without any bystander touching the station. For example, the mod takes a broken branch only above five free colonists. The cast-only scene passes; an unrelated colony scene for the same bar does not test that branch. Require relevant transfer evidence or restrict the claim.

3. **Wrong verdicts while satisfying all seven evidence points**

   **Wrong SUCCESS: an observing property repairs the behaviour.** A permitted property lazily initializes a cache that ordinary execution leaves stale. Sampling it every tick makes the mod work. The trace has correct values, identities, phases, counts and versions; nothing was lost. It faithfully records behaviour changed by the observer. “The UI calls properties” does not establish purity.

   **Wrong MOD FAILURE: nested postfix records reverse the intended event order.** Damage synchronously kills a pawn. The `Pawn.Kill` postfix records death before the enclosing `Thing.TakeDamage` postfix records damage. A checker requiring `before(damage, death)` fails correct behaviour. All seven points can hold: sequence numbers accurately describe **record emission order**, but the contract never distinguishes call entry, completion and causal order.

   Re-judgement cannot recover the missing call-entry or causal information. Changing the observation requires another run under the repaired rule. Likewise, re-judging an actively observed run cannot establish what would have happened without the probe.

4. **What can make the disposable-session certificate lie**

   The key can remain unchanged while these change:

   - Mod settings or game-component settings controlling a foreign prefix.
   - Static flags, caches, delayed initialization or conditional patch behaviour.
   - Pawn subclasses, comps, map kinds and other route-selecting state absent from the fixtures.
   - Method warm-up/JIT history, relevant to the document’s own inlining concern.

   **Cheapest useful check:** hash and compare effective settings, relevant loaded code and declared gate state at arm; verify the scene’s required routes against the certificate’s route list. Patch presence alone is insufficient.

   For state-dependent suppression, add passive per-run upstream-route and emitted-event counters where possible. An exercised route with no corresponding tap record invalidates coverage.

   There is **no universal passive arm check** that proves an arbitrary foreign prefix will behave as it did in another process. Where an absence claim depends on that uncertainty, downgrade coverage or require a targeted certification under the matching state.

5. **Deviation classes and taint**

   **“Needs released” is not adequately described as GIVEN BACK.** Releasing a hold returns control, not the hunger, exhaustion, mental-state opportunities or other consequences suppressed during elapsed time. Split the restored control flag from the NOT UNDONE history. GIVEN BACK fits only when an actual resource/state was held aside and its return has a defined correction.

   **Queued incidents have another concrete defect:** the engine-facts section names both firing and retry expiry. The restoration recipe shifts only fire ticks. An incident can return with a future fire tick and an already-expired retry deadline, then disappear. Preserve all relevant remaining durations.

   **NOT UNDONE has an invalid generic recovery:** loading a fixture cannot clear process statics. Distinguish station-, save- and process-persistent effects.

   The overlay taint rule is defensible for arbitrary writes. It blocks **green → live red → next green acceptance in the same process**. Therefore `both-ways` needs batching of all greens before reds, or restarts. It does **not** prevent exploratory sweeps: their later baselines can remain TUNED controls.

   Its larger weakness is scope: non-overlay acts can contaminate process statics too.

6. **The build order**

   **Still too large:** `WIRE_COND_RUN_INTO_TICK`. It combines both execution modes, changes to multiple drivers, recording and writer-drain correctness, condition policies, a lock across changing tool families, cancellation, thrown ticks, epoch changes and allocation verification. That is substantially more than one narrow integration experiment.

   Split out a hand-written PLAY slice with one probe, one act and one exact stop. Follow with lifecycle failure handling, global admission locking and other drivers.

   **Still-wrong dependencies:**

   - The certificate requires held/refused incident routes; the gates arrive in CALM_PROFILE, which requires the certificate. Build the gates first, then certify the assembled recorder-and-gate system.
   - GAME_WATCHER precedes full STAGE_OPS but not RUN_PLAN, which already spawns pawns and changes terrain. Its required admission protection must precede that first mutating plan.
   - Acceptance `run_plan` requires a certificate at arm, although certification is built much later. Specify a restricted, explicitly non-acceptance bootstrap mode.

   **A planted fault its tests need not catch:** RUN_PLAN’s “a settle that skips the health reconciliation.” Its reconciliation fixtures test a vanished object and a clean run. Neither distinguishes correct health reconciliation from one that checks identity but ignores health. Add a still-present actor whose direct health differs from the trace.

   The first ticket’s “sampling after the act steps” also lacks an explicit sequence assertion. Showing that new health appears before termination does not distinguish the two sampling orders.

7. **The owner page**

   **Remaining overclaim:** “No bystander can … starve or die in a long run.” The green room still ticks in the same world. Separation prevents entry onto the stage; it does not guarantee survival against disease, mod behaviour or other global effects. State the narrower guarantee.

   **ArchBig contradictions:**

   - Scenes are allowed on original and copied saves, but the kernel is TEST-only. Copying a save does not change the running process’s CAMPAIGN profile.
   - Destructive operations are allowed on the copy, while the design refuses destructive calm controls in CAMPAIGN.
   - The original-save camera cell says “never”; choice 4 authorizes a tool that moves that camera temporarily.
   - Ordinary scene arming places the camera on the station. Permission for an off-screen photograph does not define permission for that ongoing scene camera control.

   Permissions need to be expressed by **process profile, loaded-save category, hold state and operation**, with each allowed combination executable.

   **A choice that is not his:** commissioning and prioritizing the medium filmstrip build belongs to the Conductor under the stated rule. Waiving his screenshot restriction is his choice; combine neither decision with the other.

   Also, the page introduces “your own game and camera” as a reserved category beyond the enumerated five acts. Choices 2–4 need the actual authority for that reservation or an explicit request to amend the rule.

8. **The five most important remaining faults, ranked**

   1. **Observation can change the result.** Arbitrary properties and plug-ins can initialize caches, consume randomness or mutate state while producing a perfect trace. Smallest repair: default-deny unreviewed acceptance probes, including properties; use versioned, reviewed snapshot readers and fixtures that detect writes and RNG consumption.

   2. **The certificate identifies patches, not their effective behaviour.** Settings, static flags and route selection can change without changing its key. Smallest repair: bind certification to effective configuration and declared route requirements; add passive route witnesses. Refuse absence-based conclusions when the exercised route cannot be covered.

   3. **Record order is underspecified for temporal judgement.** Nested postfixes can record death before the damage that caused it. Smallest repair: define event timestamps explicitly and record entry/completion plus parent-call identifiers where causal ordering matters. Do not apply `before` to completion rows as though they were event-start times.

   4. **A red run does not prove the mutant was consumed.** Read-back plus exposure permits a cached value to bypass the mutant. The author can also supply a one-element mutant pool. Smallest repair: require a mutant-specific consumption/branch witness and independently reviewed mutant selection; control RNG and persistent state when attributing the failure.

   5. **“Fresh load” is treated as a stronger reset than it is.** Non-overlay acts can leave process statics dirty, while restoration also omits incident retry deadlines. Smallest repair: classify persistence separately from restoration, require restart or verified reset for process effects, and preserve every absolute deadline when returning held queue entries.