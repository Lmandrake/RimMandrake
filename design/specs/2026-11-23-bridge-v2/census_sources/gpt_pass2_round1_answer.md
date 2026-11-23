I have not independently verified the RimWorld 1.6 source. **RECALLED** marks engine claims drawn from memory; details I cannot establish remain **UNPROVEN**.

1. **RISKY — reuse is reasonable; the comparison is loaded.**

   B need not copy the cores or introduce another transport immediately. C need not put tests inside the mod under test: compiled fixtures can live in the companion, discover targets through reflection, emit traces, and use an outside judge. C# contracts can be hashed; constrained contracts can be linted. “Way C’s identity fault cannot be repaired” is false.

   A understates integration costs: competing tick drivers, cancellation, shared static state, patch ordering, writer failure, schema migration, lifecycle ownership, and preventing the other 427 tools from mutating an active run. Existing unit tests do not establish compatible lifecycle assumptions.

   **Failure:** an exploratory tool replaces an actor’s job during a run. Admission succeeded, the trace is coherent, and the judge reports MOD FAILURE.

   **Smallest repair:** establish exclusive mutation ownership across every entry point before joining runners.

   A fourth candidate is a transport-neutral harness library, an existing-bridge adapter, compiled fixture plug-ins, and declarative observation contracts. It avoids rebuilding transport and modifying shipped mod binaries. Whether it beats A requires one measured vertical slice, not line-count guesses.

2. **RISKY — a trace is sufficient only for explicitly bounded questions.**

   Compared with an appropriately placed in-game observer, trace-only judgment can lose: unnamed state; pre-act values; intermediate writes; arguments and causal context; alias incarnations after replacement, split, merge or load; precision/types during serialization; temporal evaluator state; asynchronous event ordering; duplicate, dropped, reordered or unflushed rows; and distinctions between tap time, sample time and act time. C#/Python semantic drift adds another failure route.

   **Failure:** TickPost samples health, an act damages the actor, then the run stops that tick. The trace contains the old health; settle does not reconcile health. The outside invariant passes.

   Automatic tracks cover named probe values at the chosen sampling points. They do not establish exposure, causality, transient absence, atomic snapshots or complete event coverage. A shared evaluator cannot reconstruct missing observations.

   **Smallest repair:** specify initial samples, phase boundaries, event sequence numbers, immutable object identities, event-time snapshots, coverage intervals and a durable completion footer. Require completeness before classification.

   Rejudging is valid only when retained evidence supports the repaired question. Preserve the original contract and checker version. Repairs to staging, observation, exposure, triggers or stopping require reruns; otherwise rejudging can conceal apparatus faults and hindsight-driven contract changes.

3. **UNPROVEN — several source observations become unjustified universal claims.**

   **(a)** The quoted pause check would support exact stopping in that loop. I cannot independently certify it. **RECALLED:** later postfixes and frame work can still execute. Test an actual multi-tick frame and final tick count.

   **(b)** The cited vanilla call graph may establish queued-result publication sites. It does not establish modded routes or that asynchronous completion timing cannot affect outcomes.

   **(c) RECALLED:** outdoor temperature differs from room temperature. Even accepting the quoted getter, biome precedence and room/heater/game-condition behavior defeat “the stage holds its temperature” as a general guarantee.

   **(d) RECALLED:** animation selection depends on animation identity/start state and render-tree state. “Pure function of game ticks” suppresses those inputs; selected graphic state also does not prove submitted pixels.

   **(e)** “Only caller” is, at most, a vanilla-source claim. **RECALLED:** mod overrides can omit base calls. A base-method postfix cannot certify universal arrivals.

   **(f) RECALLED:** quest registration and a player-visible offer are different events. Blocking `Add` also needs caller-side consistency testing.

   **(g) RECALLED:** persisted things retain serialized IDs. That does not guarantee object-reference continuity, survival, or uniqueness across games.

   **Smallest repair:** replace universal facts with scoped guarantees and executable counterexample tests.

4. **RISKY — the stage removes interference by changing the system being tested.**

   **RECALLED:** incidents can depend on target eligibility, player-home status, colonists, map geometry, wealth and threat parameters. Providing defenders does not establish valid raid arrival, reachable entry cells or ordinary storyteller behavior.

   **Failure:** a pocket-map raid cannot select a valid arrival route. The harness reports RANDOM MISS, or substitutes forced spawning and reports SUCCESS. Neither establishes the colony-map claim.

   **RECALLED:** map components and mods can branch on map type, parent, tile and home status. Sun, weather, temperature, world connections and map-wide networks therefore need separate validation. The green room also remains a source of ticking and shared state; it is not free isolation.

   Choosing pocket versus settlement primarily by generation cost is backwards. Choose by required semantics, then measure cost.

   **Smallest repair:** classify scene capabilities and map requirements. Default colony claims to representative settlement maps; allow pocket maps only for narrower claims with transfer evidence.

   Shared-map holds are acceptable as declared precautions, not isolation. **RECALLED:** allowed areas and forbidden flags do not universally constrain combat, mental states, forced jobs or mod behavior. Detect interference during the scene and invalidate affected evidence.

5. **RISKY — PLAY removes one known distortion; it does not establish determinism.**

   **RECALLED:** higher speeds change the relationship between simulation ticks and rendered frames. Frame callbacks, real-time timers, coroutines, rendering-dependent caches and asynchronous work can consequently interleave differently. Mods can also inspect speed or pause state.

   **Failure:** a mod updates a targeting cache once per frame. At speed 1 it refreshes before each relevant decision; at Ultrafast several decisions consume stale data. Both runs use PLAY, but only one passes.

   Kind A should mean a controlled, decisive opportunity, not an assertion that execution is inherently deterministic. Establish a named reference configuration and validate faster configurations per relevant mechanism.

   The camera policy is incomplete. **RECALLED:** view and zoom can affect update cadence. Recording them once does not prove they stayed fixed; pinning one getter does not neutralize every camera-dependent behavior. A global prefix can also alter the green room.

   **Smallest repair:** compare PLAY speed 1, speed 3 and Ultrafast before STEP. Monitor camera state throughout, scope rate overrides to the cast, and treat overridden execution as a separate configuration requiring transfer evidence.

6. **WRONG — the proposed canary does not even exercise all its promised records.**

   **Failure:** the reservation tap records `Reserve == false`; the canary merely reserves and releases a cell successfully. A correct tap produces no refusal record, so the rite rejects it. Conversely, synthetic recorder tests can pass while the actual refusal hook is absent.

   The rite also does not exercise mental-state attempts, quest offers, letters, messages or necessarily death. Destroying a pawn is not a demonstrated death-route test. One warning does not certify exception capture.

   It cannot prove coverage of other definitions, subclasses, callers, skipped originals, argument fidelity, event ordering, serialization or durable delivery. Settle cannot recover an intermediate event whose final state was restored.

   **RECALLED:** spawning and job execution can consume IDs, randomness and persistent state. Cleanup does not establish their reversal. Thus the rite can alter the scene it supposedly certifies.

   **Smallest repair:** run positive and negative route fixtures in disposable certification sessions for the exact build/mod list. Acceptance starts from a cold fixture. Arm-time checks should validate bindings, patch inventory, writer acknowledgement and coverage declarations without gameplay acts. Explicitly report remaining coverage limits.

7. **RISKY — unify the audit envelope, not the rollback semantics.**

   A setting assignment, an issued job, elapsed time, a suppressed incident and an uninstalled patch are not one reversible operation.

   **Failure:** restore a multiplier after the mutant created injuries and cached derived values. Read-back says “restored,” but the next baseline still differs.

   **Smallest repair:** use typed entries with separate persistence, compensation and invalidation rules. Irreversible effects require fixture reload or process restart. A debt file cannot undo elapsed simulation or arbitrary side effects.

   Green-then-red proves sensitivity only if both runs had comparable opportunities and the mutant reached its target. Otherwise deterioration or contamination can manufacture the red result. Red SUCCESS means “this mutant was not killed,” not “the scene cannot fail.”

   Overlay mutation misses compiled control flow, wrong targets, ordering, serialization, stale caches, lifecycle faults and timing defects unless purpose-built switches exist. Calling these “few” has no evidence. This biases trust toward conveniently tunable faults.

   Use independent fixture starts, target-reached evidence and a mutation matrix including compiled mutants. Also reject persistent **taint** explicitly in the ledger: checking only the current overlay stamp permits later contaminated baselines.

8. **RISKY — “the first three pay first” is not demonstrated.**

   The judge has no existing conforming traces to rejudge. The first scene needs observation and cleanup guarantees scheduled later. The third ticket combines parsing, lifecycle, staging, operations, asynchronous handles, reconciliation and migration; it is not credibly one builder run.

   **Concrete acceptance holes:**

   - A force executor always uses raw jobs but copies the declared force level into receipts. All eight declaration tests pass.
   - A reset implementation returns a constant digest. Comparing repeated recorded read-backs passes without proving live cleanup.
   - A recorder harness manufactures valid events while actual Harmony hooks remain disconnected.
   - A compiler rejects only one syntactic “already true” example. It passes while runtime pre-existing success remains accepted.

   Several checks simply repeat requirements: “seven outcomes,” “each phase refuses,” “restore reverses,” and numeric check counts provide no independent oracle.

   **Smallest repair:** first build a narrow lifecycle-and-observation spike: multi-tick PLAY stopping, initial/final sampling, writer drain, dropped-row invalidation, cancellation and exception cleanup. Move watchdog and minimum restoration ahead of destructive staging. Split the canary/taps ticket by event family.

   Fix dependencies: repeats precede their reset-hook dependency in the listed order. Add early replay-state handling; comparing independently reloaded saves does not control randomness by itself.

9. **WRONG — the page presents unmeasured promises as settled behavior.**

   “No game runs again for a wrong check” excludes missing evidence and wrong stopping. “Every run” records what happened exaggerates sampled coverage. “The stage holds its temperature and weather by itself,” “one small part,” “tuning takes seconds,” and universal restart-free mutation are unsupported.

   **Failure:** a repaired checker requires an unrecorded value. The owner expects free rejudgment; the team needs another expensive session.

   ArchBig policy contradicts itself: overlays are prohibited in CAMPAIGN, yet tuning on his game is offered. Full-list checks supposedly use disposable copies, yet destructive changes to his saves are offered. Camera movement is both prohibited and conditionally permitted.

   **Smallest repair:** distinguish the original save, disposable copy, running process, profile and current owner hold in one explicit permission matrix.

   Flight consent remains his choice. **RECALLED:** selected animation state is not proof of rendered appearance; the first joint session must establish that distinction.

   Missing owner decisions include expenditure/time caps, acceptable claim restrictions from forced scenes, retention/privacy, and automation on his process. Ticket order can be delegated. The page cannot itself declare product hooks and standard destructive controls outside his authority.

10. **RISKY overall — make these three changes, in this order.**

   **First, establish an evidence-completeness contract.** The current sampling/act ordering can produce SUCCESS from stale observations. Specify phase ordering, initial samples, event identity/order, loss detection, durable closure and checker-version history. Rejudging must refuse questions the recording cannot answer.

   **Second, certify execution and isolation before building the general interpreter.** Pocket-map semantics, camera changes and speed-dependent execution can silently narrow the claim. Start with one representative settlement-map scene; compare PLAY speeds, inject observation failures, and prove cleanup using independent reads and cold starts. Admit other configurations by capability and transfer evidence.

   **Third, replace “one restore” and “both ways” with explicit contamination rules.** A reverted value does not revert consequences. Separate reversible assignments from irreversible acts; enforce taint in the verdict ledger; run baseline and mutant from independent matched fixtures; prove mutant activation; include compiled faults. Bring cancellation, watchdog and failed-restore handling forward.

   These changes address false confidence first. More scenes, faster repeats and additional overlay features otherwise make an unsound verdict pipeline produce answers faster.