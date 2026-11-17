**Part A should not ship as specified.** It changes retry and escalation decisions using a classifier that mistakes some serious mod defects for infrastructure failures. Changes one and two could preserve useful context, but neither yet specifies how that context prevents another investigation or changes a repair decision. Part B is explicitly deferred; its proposed routing benefit cannot be credited to this version.

Findings, most severe first:

1. **“The game never reached a loaded map” does not establish a pipeline fault.**

   A mod can prevent loading through malformed definitions, initialization exceptions, dependency errors, broken patches or save incompatibility. Failure to reach a map can be the strongest observation of its defect. Part A instead excludes that failure from the mod’s visits and streak.

   The other signatures also confuse symptoms with ownership:

   - A missing test might be a builder’s omitted deliverable, contrary to PROCESS §4, Stage 3.
   - A wrong mod list might reflect an incomplete dependency declaration.
   - Previous-run state might expose a genuine persistence or cleanup defect in the mod.
   - A silent engine call provides insufficient evidence; it does not establish which component failed.

   Classify **whether a measurement was valid** separately from **which component caused the failure**. Preserve any valid failed observations even when the run also suffered infrastructure trouble. Require causal evidence before assigning ownership; do not turn “not observed” into “pipeline caused it.”

   The proposal’s claimed asymmetric risk is also wrong: excluding a genuine mod failure does not directly make it green. With `verdict_for()` unchanged, it primarily delays diagnosis and escalation. Conversely, counting an infrastructure failure does not itself make a mod green either (`status.py:415–450`).

   The seven signature tests would certify these mistakes. They need counterexamples, particularly a candidate mod that prevents loading while a control build loads successfully.

2. **Changing `retriable()` is insufficient to preserve the visit or remove the failure from escalation.**

   Consumption here is partly an eligibility decision, not a visible decrement:

   - `retriable()` excludes ordinary started-and-ended failures from automatic retry (`maturation_dispatch.py:1270–1300`).
   - **`decide_ingame()` checks terminal states before consulting that retry predicate.** `exit not met` returns immediately. An unfinished record also stops unless the specifically recognized killed-run resume applies (`maturation_dispatch.py:1520–1548`).
   - **`testpilot_route.judge()` independently selects runs** by note position and `NOT_A_TEST`, then calls `streaks()`. It has no fault-classification filter (`testpilot_route.py:115–130`).

   Part A must integrate with all three functions, the upstream calculation of `owed`, run-book eligibility, and the corresponding blind-stage path. The supplied excerpts do not show the actual visit-number writer; claiming to have traced that mutation would exceed the evidence.

   A new classifier and recorder checks alone will not achieve “does not consume a visit.” Nor does the proposal identify who classifies a crashed run, unavailable provider or absent footer after the agent has stopped.

   Required acceptance: a started run suffers an infrastructure failure, ends, is classified once, remains eligible for the same visit, and contributes nothing to either applicable streak. Test the existing terminal-record paths, not just `classify()`.

3. **`discriminated: true` overstates what was checked. As specified, that signal is a net negative.**

   One alternative plus an existing reference establishes that the reporter **recorded an alternative**. It does not establish that the reference supports its rejection, that the claimed cause was isolated, or that the failing assertion concerned that cause.

   Worse, the cited precedent does not actually resolve arbitrary run references. `cmd_spawn()` accepts a syntactically matching run name through `model.RUN_RE.match(...)`, without checking that the run exists (`cli.py:3205–3218`). Copying that behavior would violate the promised nonexistent-run rejection.

   Keep the explanation, but use a literal label such as `alternatives_recorded`. Track reference resolution separately. Do not present either as proof of discrimination. `--red-at` is also an assertion by the reporter until linked to the recorded failure.

   Typed references are useful navigation. They need immutable provenance—run identity or commit-pinned content—not merely a path that exists today. The supplied CODE does not include the cited `modledger` resolver, so its actual resolution guarantees remain unverified.

4. **The new fields do not survive the current RimFlow write/read path—but the proposal correctly identifies this.**

   The current trace is explicit:

   - `cmd_finding()` emits only the existing finding arguments (`cli.py:3185–3200`).
   - The event schema permits no optional finding fields (`model.py:517`).
   - Replay reconstructs `world.findings[name]` using only `from`, `type`, `severity` and `at` (`model.py:2763`).

   Adding argparse flags alone therefore stores nothing new. Adding emission and schema support still leaves replay silently discarding the fields.

   Change one explicitly names `_apply`, strict writes, tolerant reads and a replay acceptance test. **That part of the proposal is right; it is not an overlooked defect.** No implementation is supplied to establish that it has been done.

   Change two remains underspecified because its canonical store is undecided. Its acceptance tests also lack the explicit replay requirement. All new fields need end-to-end persistence tests through the chosen store and renderer.

   One smaller implementation trap: lifted `_pairs()` rejects an empty list (`relentless_explain.py:59–70`). The optional flag path must bypass that requirement or adapt the helper.

5. **“Third occurrence of the same cause” is not implementable safely without defining identity and lifetime.**

   The obvious comparisons each fail:

   | Comparison | Failure |
   |---|---|
   | Exact explanation text | Run IDs, paths, timestamps and paraphrases evade the limit. |
   | Broad category, such as `bridge_unreachable` | Unrelated incidents accumulate into a false stop. |
   | Finding name | Newly minted names turn every recurrence into a first occurrence. |
   | `findings_fold.signature()` | It hashes the supplied tuple; it does not discover semantic equivalence. |

   The existing tuple includes mod, chain, row, normalized text and sometimes name (`findings_fold.py:98–118`). It may split one shared infrastructure cause across checks or merge repeated symptoms with different causes.

   Use a structured incident identity: affected component, stable failure code and evidence supporting the cause. Count distinct attempts, not repeated ingestion of one run. Specify scope, recovery/reset rules, treatment after a repair, and behavior across pipeline versions. Unknowns need bounded escalation even when their explanations vary.

   The advertised `(kind, why)` function also lacks the state needed to count repeats, emit findings and set alarms. Separate classification from the orchestration that performs those actions.

6. **Automatic self-repair in one working tree and index threatens the evidence itself.**

   Several agents can edit the same pipeline files, stage one another’s changes, or run tests against a mixture that never existed in a commit. A red/fix comparison can become invalid between its two executions. Patch reversal can undo another agent’s work.

   Mod-specific leases do not serialize shared infrastructure edits or protect the shared git index. The existing ITEMS already show failures from duplicate leases and stale readers:

   - `RIMMANDRAKE_UNFENCE_LIVE_HOLDER_WHEN_RIVAL_NEVER_STARTED`
   - `RIMMANDRAKE_HOLD_TICK_LAUNCHES_ON_STALE_CLONE_GHOST_STEWARD`

   Part A adds concurrent finding creation, counter updates and repair attempts without defining atomicity or idempotency. Two classifiers can duplicate one incident or miss the threshold through stale reads.

   Use isolated worktrees/indexes for repairs, or exclusive ownership covering edit, test, staging and publication. Bind evidence to the tested commit. Classification, finding creation and repeat accounting need stable event identities so retries cannot multiply them.

7. **Changes one and two have no specified operational consumer. More records are not yet less work.**

   Their concrete decision changes are currently narrow:

   | Change | Decision actually changed |
   |---|---|
   | One | Refuse malformed optional explanations or unresolved references. No repair, routing or investigation decision is specified. |
   | Two | Refuse incomplete optional dispositions. A digest counts outcomes. No subsequent candidate lookup or reuse decision is specified. |
   | Three A | Retry eligibility, streak eligibility and third-repeat escalation—substantial changes, inadequately integrated. |

   Change two claims to prevent repeated investigation, but does not specify a candidate identity, retrieval step, expiry rule or reconsideration trigger. A recorded rejection cannot save the next investigator effort unless the next investigator receives it. A later code change may also invalidate a previous rejection.

   The likely consumer is the existing surprise/explain-away mechanism: it already remembers explained or non-bug observations, retires recurring contexts and revives real bugs (`testpilot_route.py:1–50`). Extend that path before creating a parallel rejection archive.

   “No agent is told any of these fields” also needs narrowing. Reporters need instructions to populate them; later investigators need the useful content. Hiding a continuation metric is different from hiding diagnostic context.

8. **The migration and UNMEASURED refusal do not match the represented data.**

   `step4_live()` **derives** UNMEASURED when a step-4 record is absent or lacks PASS/FAIL. There need not be an UNMEASURED write to refuse (`status.py:615–632`). Putting validation inside `record_run()` cannot guarantee that every displayed UNMEASURED has a reason.

   Historical absence does not prove a historical infrastructure failure. The 659 rows need distinctions such as never attempted, incomplete attempt, missing record and unknown provenance. Do not manufacture causal classifications from missing evidence.

   Define:

   - Strict requirements for new completed attempts, with tolerant historical reads.
   - Explicit reasons for derived missing-record states.
   - Append-only corrections with evidence and classifier version.
   - Rendering of missing, unresolved, rejected and unverified states.
   - Denominators that distinguish runs, checks and findings.

   The quoted counts account for 988 of 1,363 rows; identify the remaining 375 before publishing revised quality percentages.

   Build identity is already missing from existing live rows according to `RIMMANDRAKE_RECORD_BUILD_IDENTITY_IN_LIVE_ROWS`. Complete that instrumentation before relying on list/build mismatch as a classification input. Avoid turning migration into an automatic replay of every historical check.

9. **The proposal changes policy while claiming only to change records, and its vocabularies overlap.**

   PROCESS §5, Dispatch gives blind and in-game visits one automatic run and sends ended visits to the Conductor. Part A authorizes additional automatic attempts. That is a policy change, even if stage numbers and budgets stay unchanged.

   Removing infrastructure failures from the streak also changes the population underlying the existing calibration. Part B acknowledges that calibration risk for its future predicate; Part A needs the same acknowledgment.

   Change two permits rejecting candidates for `harness_limit` or `environment`, while Part A requires pipeline failures to become findings and known defects to be fixed. Those can coexist only with an explicit distinction: **reject the suspected mod attribution while retaining the infrastructure incident**. Otherwise one change encourages discarding what the other requires repairing.

   No existing validity gate becomes redundant: annotations cannot replace build match, red-first evidence or the verdict ladder. But automatic classification-based retries could bypass the existing Conductor decision, while the terminal checks in `decide_ingame()` could make those retries unreachable.

   Also reconcile Change two’s four named dispositions plus absence, “five values,” and six rejection reasons. Its acceptance oracle should have one unambiguous vocabulary.

10. **Build a corrected Part A first; defer standalone Change two. Cheaper existing mechanisms should precede both.**

   If restricted to one proposal change, choose **Part A after correcting its ownership model and integration**. It alone directly changes an expensive decision: whether to spend another attempt and when to escalate. Begin with positively evidenced infrastructure failures; retain ambiguous mod observations and existing escalation rather than suppressing them.

   Change one is worth a small implementation as diagnostic context, with an honest label and a visible consumer. **Change two is not worth building as a separate subsystem in its present form**; extend the existing rejection memory and settle its relationship to `modledger` statuses first.

   Existing work should take priority where it makes this evidence trustworthy:

   - Repair stale-clone decisions, live-holder fencing and blind-judge write permissions—the corresponding ITEMS document lost or false records already.
   - Complete build-identity capture before classification depends on it.
   - Fix the known red coverage selftest before making changes that its publication checks block.
   - Resolve Stage 3’s missing “behavior built” signal; preventing unbuilt behavior from reaching live testing saves more than annotating the resulting failure.

   The cheapest immediate loop intervention is **`RC.submit` wiring**, already specified in `RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS`: existing refusals are checked but never counted. For a defect already needing live diagnosis, **`TESTPILOT_WANTED` already routes directly to a sitting**, without waiting for another three failures (`testpilot_route.py:115–130`). Those change decisions using machinery already present.
