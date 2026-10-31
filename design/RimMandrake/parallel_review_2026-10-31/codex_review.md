The reports identify serious problems, but overstate both the safety of immediate expansion and what the replay can establish. **The proposed add-on has the right ingredients; it is not yet a fair comparison.**

This review uses only the inlined reports. “Reproduced” below retains their stated scope; it does not mean I independently exercised the code.

## Ranked findings

1. **Critical — the proposed fan-out prerequisites leave known work-corruption and false-check risks open.**

   `handoff_context.md` makes Requirements 1–3 sufficient before expansion, postponing helper ownership and path controls. Yet its Finding 5 already says concurrent edits can contaminate commits **and test results**. `use_now.md` nevertheless recommends starting six helpers.

   A publish lock protects cooperating publishers. It does not stop peer edits, direct commits, pulls, or other worktree changes. A HEAD comparison followed by reset remains vulnerable unless every relevant mutator follows the locking protocol. Declared paths help prevent overlapping edits, but disjoint files can still share build outputs or affect the same tests.

   Expansion needs a demonstrated way to test and accept an exact, stable candidate—not merely explicit-path commits and one designated publisher. This does not by itself establish that worktrees are required.

   **Cites:** `handoff_context.md`, Findings 1 and 5; “Worktrees,” Recommendation; Requirements 1–6. `use_now.md`, opening and §3.

2. **Critical — the existing replay’s validity is less secure than `arms.md` admits.**

   `arms.md` calls serial acceptance and token costs “honest.” But `use_now.md` reports that the runner executes from a dirty, mutable FOUNDRY tree without a recorded code-tree hash.

   Restricting *commits* to mod source/design does not freeze uncommitted edits. A pre-pull check does not establish an immutable runtime, and an AST import closure does not exhaust configuration, hooks, subprocesses, dynamic imports or generated inputs.

   This establishes a **contamination risk**, not proof that contamination occurred. Until executable code and inputs are reconstructed, even the narrower serial verdict needs qualification.

   **Cites:** `arms.md`, §C, “What the verdict still supports.” `use_now.md`, §2.

3. **High — lease recovery and claim coordination can duplicate work or let obsolete workers publish.**

   Two gaps are missing from the proposed safety gate:

   - A clone-local `next` lock does not establish exclusion across BENCH and FOUNDRY’s separate clones. “One clone per seat” is insufficient unless ownership namespaces are disjoint or claims are centrally arbitrated. Union-merging events preserves conflicting claims; it does not prevent them.
   - Auto-reclaiming on a finished or stale transcript does not prove all work stopped or its result was delivered. The reports themselves show long silent helpers. A reassigned item needs a fencing generation that prevents the old holder from later renewing, closing or publishing it.

   Durable ownership, completion receipts and recovery should precede increased fan-out. A dead parent’s unread final notification is also a lost-result channel even when the code survives.

   **Cites:** `handoff_context.md`, Findings 4 and 8; attack-table “Clone-local lease lock” and lease rows; Requirements 4–5; “Evidence and gaps.”

4. **High — neither the capacity recommendation nor pooled-budget safety is established.**

   Quiet CPU samples and historical aggregate memory do not bound simultaneous suite, helper, Windows-build and game peaks. The reports explicitly missed spikes and have not measured combined-load peaks.

   Both memory conclusions overreach: a cache-heavy slice at its cap establishes neither “None to spare” nor “the cap is not the limit today.” Reclaim and cache churn can reduce throughput without an OOM.

   More seriously, “do not switch by hand” does not prevent the reported **automatic** account failover from closing every Claude window. Stale five-hour usage, unknown arm burn and conflicting burn estimates defeat the pooled-runway assurance. Concurrent admissions also need to account for outstanding spend: several workers can pass the same floor check before their calls are charged.

   **Cites:** `use_now.md`, §1, capacity table, Budget and Stop lines. `arms.md`, limits 16–18 and UNMEASURED.

5. **High — append safety is being mistaken for execution safety.**

   Flocked appends and file-position ordering do not make `require_tested → brief → build → test` transitions atomic. They also do not prove which candidate a test checked.

   Narrowing arm locks requires explicit task/attempt/build identities, per-stream state transitions, crash recovery and idempotent completion. Otherwise duplicate dispatch, stale test receipts or an abandoned untested build can remain correctness failures or permanent blockers.

   File position orders **recording**, not necessarily execution or causality. Separate tester identities do not establish checks of immutable artifacts. Consequently, “fair checking … holds” is unsupported.

   **Cites:** `arms.md`, §B; limits 4–8; “Smallest fix,” Checking unchanged.

6. **High — the add-on cannot attribute differences to parallelism as proposed.**

   It changes helper permissions, prompts, writable delegation, stream scoping and integration, then compares against an earlier replay. “Any drop” in acceptance is therefore **not automatically the reliability price of parallelism**.

   Equal stream/helper allowances are useful, but may omit critic, tester, merger and controller capacity. Conversely, forcing identical role arrangements can erase architecture differences.

   The trial needs a contemporaneous N=1 control under the same pinned harness and acceptance procedure, plus a defined resource envelope covering every role. Report modified variants as modified variants.

   **Cites:** `arms.md`, limits 10–12; “Smallest fix,” Required and Checking unchanged.

7. **High — fan-in and spend attribution are necessary but underspecified.**

   **Fan-in:** the reports do not establish that historical tasks across eras form one compatible cumulative workload. Define starting revisions and dependency relationships before landing everything onto one main. Completion order must respect those dependencies. Clean textual rebases can still create semantic regressions; final acceptance must cover the integrated result. Apply the same integration treatment to N=1.

   **Spend:** a session’s clone is a useful attribution input, not a demonstrated per-call execution key. Controllers, retries, children and shared services need attribution too. Near-zero ambiguity is insufficient if calls are omitted or counted twice. Reconcile attributed and shared overhead against total observed spend.

   **Cites:** `arms.md`, limits 1–2, 13 and 22; “Smallest fix,” Same tasks, Per-call task key and Fan-in step.

8. **High — completion capacity can silently cap concurrency even after builder limits disappear.**

   The reports mention queues without designing admission around them: independent review, judging, heavy tests, Windows builds, landing, live proof and recovery.

   Full-belt spawning can fill every slot with builders while checkers or integration wait. Cross-lane review swaps can also stall when everyone is holding unfinished work. Overlay-private suite locks already undermine the assumed heavy-test exclusion.

   Measure these service rates and queue lengths; give verification and recovery sufficient priority or capacity. Otherwise more helpers merely increase work in progress—or pressure reviewers to weaken checks. Small tests cannot substitute for required checks just to preserve apparent throughput.

   **Cites:** `handoff_context.md`, Findings 2–3 and 7; Requirements 7. `use_now.md`, §§2–3. `arms.md`, limit 18.

9. **Medium — several headline explanations and numbers are unsupported or wrong.**

   - **“Structurally anti-parallel” is too categorical.** Token efficiency gives speed no credit, but helpers can improve acceptance or reduce total rework and tokens.
   - **Observed mean is not a ceiling.** FOUNDRY averaging 2–2.7 helpers does not establish its “real ceiling.”
   - **Alarm counts are not causal attribution.** Neither 218 unwakeable alarms nor the proposed-item inventory establishes the dominant cause of underuse.
   - **The lane arithmetic fails.** Mandatory lanes require 7–8 helpers; optional F makes 8–9. The stated six-helper start cannot staff that plan.
   - **The output forecast exceeds its assumptions.** Three builders × eight hours, at 1.5–2 hours/item with roughly 25% rework, supports about 9–13 items—not 15–25 or 20–30.
   - **“Found nothing” is not automatically wasted testing.** Regression coverage can be useful; Steve’s proposed half-share and “best value” claim lack the necessary outcome evidence.

   **Cites:** `arms.md`, §C.2. `handoff_context.md`, Measured concurrency. `use_now.md`, §§3–5.

10. **Medium — “every limit must defend itself” was applied selectively.**

   Retry caps are dismissed because they are “not concurrency,” although they limit productivity and occupy slots. Cruise 6, nesting prohibition, fallback 3, ceilings 4/10, context thresholds and fixed test allocations remain provisional choices rather than demonstrated requirements.

   Some retained choices conflict: a fails-open spawn hook weakens reliance on slot enforcement; “never kill mid-turn” needs reconciliation with a watchdog intended to kill silent helpers. A helper-free restart boundary may be necessary today, but its necessity after durable ownership and reattachment remains untested.

   Owner authority explains who may change a rule; it does not supply empirical evidence for its value. Each limit needs a failure it prevents, an observable trigger and a condition for reconsideration.

   **Cites:** `arms.md`, limits 11–12 and 21. `handoff_context.md`, attack table, especially restart, fallback, fails-open, nesting and watchdog rows.

## Is the add-on fair?

**Not yet.** Equal allowance, execution keys, fan-in and accepted-per-hour are sound requirements, but need these additions:

1. **Pin the experiment:** runner, dirty patch, prompts, configuration, task inputs, tools and initial revisions.
2. **Add a fresh N=1 control:** same helper permissions and final acceptance process as N>1. Separate L1 delegation changes from L2 changes when claiming their individual effects.
3. **Define the resource envelope:** count every role and shared service. Control cross-arm contention through fair allocation or randomized repeated blocks.
4. **Define a valid cumulative workload:** dependency-aware bases, integration and final checks. Count rejected work, semantic conflicts, rework and abandoned attempts.
5. **Define accepted-per-hour end to end:** include scheduling, checks, integration and drain. Report waits separately without silently subtracting them. Predeclare treatment of unfinished work at the cutoff.
6. **Reconcile spend completely:** propagated execution identities, child attribution, shared overhead and account-total reconciliation.
7. **Predeclare the decision rule:** reliability margin, uncertainty, throughput/cost tradeoff and an adaptive escalation rule. Testing only N=2/4 does not defend a ceiling.

The strongest surviving findings are the credible publish-loss mechanism, the quiet-boundary/full-belt contradiction, the replay’s enforced L2 serialization and its failure to measure throughput. The publish reproduction demonstrates a possible loss, **not an observed production incident**. The reports do not yet establish safe six-to-ten-helper operation, a concurrency ceiling, or a production-switch winner.