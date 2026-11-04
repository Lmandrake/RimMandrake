# Test tolerance: GPT's advice (2026-11-04)

Asked by the Conductor on the owner's words (standing_rulings.md, "Broken tests are expected"). Case file: `D:\ClaudeWork\rimmandrake\conductor\test_tolerance_consult\` (context.md, churn_census.txt, item_histories.txt). This is design input, not ruled; build items cite it by section.

**Build the attribution gate first: no failed validation should authorize product rework until the system has decided what failed and why.** Preserve the candidate while that decision is pending.

Relentless currently turns “the acceptance process did not succeed” into “the implementation needs another generation.” That transition explains much of the churn. Tonight’s fixes improve classification, but the decisive change belongs in the supervisor: **measurement, attribution, repair authorization, and closure need separate records and transitions.**

The evidence also argues against a blanket “these were broken tests” conclusion. Steve had inaccessible evidence and an inadequate replacement proof. LeaningScrub had a genuine contract mismatch, followed by non-reproduction and downtime. Titanic had a fixture whose expected reduction was mathematically absent at the chosen boundary. Each requires a different next action. (*item_histories.txt*, those three histories.)

### Build order, ranked by value per effort

| Rank | Build | Relative effort | Value |
|---|---|---:|---|
| 1 | Replace direct `fail() → new builder` with an enforced attribution transition | Small–medium | Stops expensive rework based on unknown causes |
| 2 | Instrument incidents, dependency waits, and event-based release | Small–medium | Repairs shared faults once; prevents waiting items being restaffed |
| 3 | Repeat detection plus a durable diagnostic handoff | Small | Stops recurrence of already-understood failures |
| 4 | Structured per-clause results and acceptance-binding repair | Medium | Removes ambiguous log interpretation and contract-lock loops |
| 5 | Replay fixtures, validator controls, and live canaries | Medium | Makes classifier and instrument repairs checkable |
| 6 | Independent closure audits and cohort metrics | Small initially; ongoing | Reveals whether improved throughput hides false closes |

Start with a narrow vertical slice: replay **STEVE_DISK**, **LEANINGSCRUB**, and a mixed Titanic result through the real supervisor transitions. Require that inaccessible evidence preserves the candidate, a repair dependency prevents staffing, and a genuine observed violation remains blocking. Do this before adding more general judging layers.

---

**Make the things being judged explicit.** A validation attempt depends on several independently versioned artifacts:

- Product implementation.
- Acceptance obligations: what must be true.
- Acceptance binding: scenario, oracle, threshold, evidence source.
- Proof implementation and fixtures.
- Runner, bridge, and checker sandbox.
- Deployment, loaded game, save, map, and other site state.
- Result parser and close logic.

“Introduced by this commit” and “a product defect” are separate facts. A commit can introduce a broken proof, an unrunnable contract, or missing deployment metadata. Those are real defects requiring repair; they do not automatically authorize rewriting the feature.

Record an attempt approximately as follows:

```json
{
  "attempt_id": "...",
  "candidate_sha": "...",
  "clause_id": "A2",
  "obligation_hash": "...",
  "binding_hash": "...",
  "proof_hash": "...",
  "runner_version": "...",
  "actual_site_manifest": "...",
  "evidence_ids": ["..."],

  "measurement": "VALID | PARTIAL | UNREACHED | INVALID",
  "finding": "SATISFIED | VIOLATED | NOT_REPRODUCED | UNKNOWN",

  "attribution": {
    "status": "PROVISIONAL | CONFIRMED | DISPUTED",
    "targets": ["PRODUCT", "PROOF", "HARNESS", "SITE", "CONTRACT"],
    "evidence_ids": ["..."],
    "next_discriminating_experiment": "..."
  },

  "authorized_action": "...",
  "waits_on": ["..."]
}
```

Allow multiple attributed faults. A proof can discover a genuine product violation in one row and lose access to another. Preserve the valid finding without pretending the remaining obligations were measured.

These fields need evidence behind them. The supervisor should compute identities, capture outputs, and check result completeness; an agent supplies the semantic interpretation.

**Give attribution an explicit decision owner.** Use a short, read-only diagnostic lease—an additional mode of the existing Judge/Help machinery, rather than another permanent organizational chair.

The flow should be:

1. **Runner records observations.** Commands, outputs, actual environment, expected and observed values, measurement stage reached.
2. **Supervisor handles mechanically established conditions.** Missing result document, mismatched run identity, or failed prerequisite means no product verdict yet.
3. **Diagnostician resolves ambiguous failures.** It reads the complete logs, relevant source, prior attempts and attributions, and instrument health. It may run bounded diagnostic experiments.
4. **Diagnostician records a signed attribution and authorized repair target.**
5. **Supervisor enforces that authorization.** A builder lease requires an actionable product finding; an instrument repair receives a separate lease.
6. **Disputed attribution goes to a fresh Judge/Conductor review.** The Conductor resolves routing and authority; it does not substitute its judgment for the final feature check.

A product-rework authorization should identify:

- The obligation allegedly violated.
- The actual setup and identities.
- What was successfully observed.
- Expected versus observed behavior.
- Why the failure implicates product behavior.
- Which alternative explanations remain unresolved.

Straightforward, trustworthy assertions can take a fast path. Ambiguous crashes and missing observations require diagnosis. The system need not launch an elaborate debate for every red test.

This would have interrupted Steve at the first unreachable SSH measurement, rather than sending builders through gens 3 and 5. It would also have preserved the legitimate concern at gen 7: grepping a worker-authored free-space number does not independently establish the cleanup. (*item_histories.txt*, STEVE_DISK, gens 1–9.)

---

**Repair the instrument as tracked work while the product item waits.** Add an instrument-incident entity:

```text
incident:
  affected component and version
  reproducing evidence
  affected attempts/items
  diagnostic hypotheses
  repair owner and lease
  acceptance fixtures
  release condition
```

The parent becomes `WAITING_ON_INSTRUMENT`, retaining its candidate SHA and valid clause receipts. It receives no product strike, redesign, or fresh builder. The incident owns the repair effort and its cost.

Use the same pattern for:

- `WAITING_ON_SITE`
- `WAITING_ON_DEPENDENCY`
- `CONTRACT_REVIEW`
- `INVESTIGATING_REPRODUCTION`

Keep worker lease fencing separate from product-generation counts. You still need to revoke a repair worker safely without implying that another product implementation was attempted.

**Release waits on evidence-bearing events.** An incident repair should wake affected items after its release checks pass. A predecessor completion should wake its dependents. A changed capability fingerprint can authorize a retry. A supervisor tick alone should not.

The repaint and Comb Holds cases already identify their unmet predecessors, yet were repeatedly staffed. These need executable dependency edges, not stronger reminders. (*churn_census.txt*, REPAINT_SAVES_RETIRE_THREE_GHOST_STARTS; COMB_HOLDS_DEF_RETIRE_AFTER_THE_REMAKE.)

For a shared outage, create one incident and link all affected items. Pause the affected validation lane, keep unrelated offline work moving, and use one recovery probe. Otherwise twenty items independently “debugging the bridge” become another source of overload.

Instrument repair must have an exit contract:

1. Reproduce the instrument failure.
2. Show the repaired instrument accepts a suitable known-good fixture.
3. Show it rejects a suitable known-bad fixture for the intended reason.
4. Show missing, stale, foreign, or incomplete evidence cannot become PASS.
5. Rerun the affected obligation against the preserved candidate.

**An instrument repair never closes its dependent product items.** It restores their ability to be judged.

For Steve, the adapter should capture machine identity, timestamp, command, and raw measurement. The cleanup obligation also needs evidence of the relevant actions or before/after state; current free space alone cannot establish everything that was cleared or preserved. If adequate historical evidence cannot be recovered, that clause remains unresolved. Repeating cleanup would not repair missing provenance.

---

**Separate acceptance obligations from their measurement bindings.** The current contract lock protects against moving the finish line, but it also traps workers behind broken measurement methods.

Create two versioned objects:

- **Obligation:** the required behavior and its scope.
- **Binding:** the scenario, proof, execution location, fixtures, and evidence freshness rules used to establish it.

Permit an independent Setter/Judge to approve a binding repair that preserves the obligation. Require a semantic comparison: what it measured before, what it measures afterward, and whether any acceptable behavior changed. Ambiguity remains blocking.

Examples:

- Moving an SSH measurement from the sandbox to a supervisor adapter changes execution location.
- Correcting an undiscoverable proof name changes invocation.
- Replacing an independent measurement with a worker-written number weakens evidence and requires rejection.
- Replacing “name the job during the move” with “the move did not occur” changes the obligation.

LeaningScrub’s initial Marker correctly detected that last mismatch. The subsequent build workers correctly reported that they could not repair the locked contract. The scheduler kept sending the wrong capability. (*item_histories.txt*, LEANINGSCRUB, gens 1–7.)

Likewise, tooling items explicitly reported finished work and an unrunnable or incorrectly named contract, but required redesign merely to change the measurement route. (*churn_census.txt*, TESTQ_WORKER_MIGRATE_PYDANTIC_CONTRACT; DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO; GUBBRA_GOURD_FIX_WONT_SELECT.)

The design’s instrument leaves and versioned contracts are useful foundations (§§3.2 and 4). Its rule that every edit defaults to an owner-approved loosening needs a delegated path for independently reviewed instrument repairs.

---

**Make loop breakers redirect work, rather than demand novelty.** Start with these rules:

| Signal | Required response |
|---|---|
| An attempt cannot reach required evidence | Diagnose capability or evidence routing before any product rework |
| Same failure signature after two relevant product changes | Suspend automatic rebuilding; compare product, proof, and binding hypotheses |
| Identical capability failure across several items | Open one shared incident; pause affected lane |
| Opposite outcomes on identical inputs and identities | Investigate instability; preserve contradictory runs |
| Known unmet predecessor | Wait on its event; issue no worker lease |
| Repeated “nothing left to build” with supporting evidence | Review attribution and routing immediately |
| Repeated investigation without a discriminating experiment | Escalate diagnosis to fresh help |

These thresholds are initial operating choices, not evidence that the second failure proves the test wrong.

“Same clause failed on two SHAs” is a useful suspicion trigger. It is weak causal evidence: neither SHA may have changed anything relevant, or both implementations may share the same defect. Track changes to the clause’s relevant product behavior, proof, binding, and environment.

The current `repeated_live()` tracks only clause labels and finish SHAs. It lacks those distinctions. The brief history also truncates explanations to 140–160 characters, which can discard the measurement and proposed next action. (*worker_brief_excerpt.py*, `repeated_live`, `ending_history`.)

Give every retry a **retry warrant**:

> What changed—or what transient hypothesis makes another attempt informative—and what result would change the decision?

A recognized persistent sandbox restriction does not merit another expensive blind check. A suspected transient interop failure may merit one controlled retry after a health probe.

Planet Atmosphere demonstrates why repeated wording cannot settle attribution: the history contains incompatible staging requirements, an actual sampling-validity defect, and later WSL interop failures. “Same cause … so a reload cannot help” overstates what the available classification established. (*item_histories.txt*, PLANET_ATMOSPHERE_CLOUD_COST_1.)

Measure progress within the active work type. Repairing a bridge or eliminating a hypothesis can advance an incident without making a feature clause green. The design’s clause-progress signal (§6) is useful for delivery, but cannot by itself decide whether an instrument investigation is productive.

---

**Replace log guessing with a measurement protocol, retaining regexes as a migration aid.** Each clause should produce structured observations and a final result tied to the supervisor’s run ID. Capture:

- Prerequisites checked and their actual values.
- Expected observations and observations received.
- Explicit measurements of absence.
- Expected/actual values, units and thresholds.
- Site, deployment and session identity.
- Completion status and raw evidence references.

Missing or malformed output yields `UNKNOWN` or `INVALID`. A final PASS line cannot overwrite an earlier valid violation. Required rows must be complete.

Several current classifier assumptions are unsafe:

- **`AssertionError` does not establish product failure.** Proofs assert their own setup and internal assumptions.
- **Other exceptions do not establish instrument failure.** Product execution can throw exceptions.
- **“No component,” `None`, and zero matching rows may be the defect.** If a valid query establishes that a required component is absent, absence is the measurement.
- **“Type not found” can implicate deployment, invocation, packaging, or the product.**
- **The last verdict line cannot reliably adjudicate mixed rows.**
- **An 8 KB tail and 25-line window can omit decisive evidence.**

These problems arise directly from `EXC_LINE`, `READ_NOTHING`, `BROKEN_CALL`, `VERDICT_LINE`, and the tail limits. (*live_classifier_excerpt.py*.)

Have adapters report **where execution stopped**: launch, transport, setup, stimulus, observation, evaluation, result delivery. Use that as evidence, while leaving causal attribution open.

Titanic especially requires row-level handling: the excerpt explicitly describes an unloaded-type SITE row beside two MOD failures. A broad inability pattern must not erase independently valid defects. (*live_classifier_excerpt.py*, `EXIT1_UNLOADED` comment.)

---

**Validate validators against both good and bad worlds.** Add a replay bank from tonight’s cases, with expected classifications, routing, and closure behavior.

| Fixture or injected fault | Required behavior |
|---|---|
| Good implementation, valid setup | SATISFIED |
| Known requirement violation, valid setup | VIOLATED with the intended observation |
| Bridge disconnect or sandbox denial | UNREACHED; no product strike |
| Stale result from another SHA/session | INVALID; cannot close |
| Required component genuinely absent | Valid observed violation |
| One valid defect plus another unreachable clause | Preserve defect and unresolved clause |
| Proof aborts before observation | INVALID/UNKNOWN; diagnose cause |
| Proof omits an assertion or forces PASS | Known-bad control exposes the validator defect |
| PASS text alongside structured failure | Failure remains blocking |
| Unexpectedly missing result rows | Incomplete evidence; cannot close |

Test the **supervisor transitions**, not merely the classifier function: no generation bump, incident created once, no restaffing while waiting, repaired incident wakes the correct candidate, incomplete evidence cannot close it.

Use two mutation streams:

- **Mutate the product:** verify the proof detects the intended violation.
- **Mutate the proof:** remove an assertion, change a threshold, substitute stale data, skip a row, swallow an exception, or force PASS. Verify controls expose the damaged proof.

A proof mutation that crashes is easy to detect. A proof mutation that returns plausible green is the essential false-close test.

For the live harness, run cheap canaries through the **actual supervisor service context**:

1. Windows/WSL interop works.
2. The bridge responds to a round trip.
3. Expected game, deployment and site identities are observable.
4. A disposable known observation can be produced and read.
5. An intentionally wrong expectation is rejected.

The PATH failure passed through precisely because the service environment could not perform reads that worked elsewhere. Canary execution from a developer shell would miss it. (*live_classifier_excerpt.py*, `windows_path`; *item_histories.txt*, TITANIC’s PATH-bug unhold.)

Cache canary health by relevant environment fingerprint and expiry. Cheap identity checks should precede scarce live slots; expensive controls can be sampled or triggered by relevant changes.

Planet Atmosphere additionally needs a **multi-session experiment plan**: separate with/without launches, compatible manifests, main-menu-state checks, and a join step. One generic staged game cannot satisfy both arms. (*item_histories.txt*, PLANET_ATMOSPHERE, gen 3.)

For diagnosis tasks, do not require the historical symptom to recur merely to prove the instrument works. LeaningScrub needs controls showing that its instrumentation identifies a deliberately produced move and job. A healthy run without the original symptom is `NOT_REPRODUCED`; it does not answer the original attribution question. (*item_histories.txt*, LEANINGSCRUB, gens 13–19.)

---

**Give each role the history needed for its decision.**

| Role | What it should see |
|---|---|
| Builder | Current obligations, candidate, valid findings, prior attempted fixes, confirmed attributions, repair dependencies and relevant raw evidence |
| Diagnostician | Full relevant attempt history, complete logs, product/proof/binding changes, site identities, prior attributions and contradictions |
| Instrument repairer | Incident reproduction, affected interfaces, controls, prior repairs and release criteria |
| Setter/binding reviewer | Original obligation, old/new bindings, measurement assumptions and evidence of the defect |
| Marker | Obligations, candidate, proof, actual execution identities, raw receipts and required coverage; retain protection from builder advocacy |
| Supervisor/Operations | Dependency graph, incidents, retry warrants, resource use and release conditions |
| Auditor | Closed cohorts, decision provenance, changed bindings and independent audit evidence |

Keep observations separate from interpretations. Preserve superseded attributions with the evidence that overturned them.

A cold redesign may omit speculative narratives. It should still receive established facts such as “this sandbox cannot SSH to Steve” and the incident blocking that route. Forgetting those facts recreates the failure.

**Use separate verdict vocabularies for separate decisions.**

- Measurement: `VALID`, `PARTIAL`, `UNREACHED`, `INVALID`.
- Clause finding: `SATISFIED`, `VIOLATED`, `NOT_REPRODUCED`, `UNKNOWN`.
- Attribution: `PRODUCT`, `PROOF`, `HARNESS`, `SITE`, `CONTRACT`, `CHECKER`, `DEPENDENCY`, with provisional/confirmed/disputed status.
- Workflow: `REWORK_PRODUCT`, `REPAIR_INSTRUMENT`, `RESTAGE`, `REVIEW_CONTRACT`, `WAIT`, `RECHECK`, `CLOSE`.

Keep PASS/WEAK/FAIL as summaries if useful. They should be derived from these records rather than directly selecting the next worker.

---

**Tonight’s changes are valuable containment, with several remaining holes.**

| Change | Assessment and next correction |
|---|---|
| Structured defects versus unreached evidence | Strong improvement. Add defect target and measurement validity: “red proof” is not sufficient attribution to product. |
| UNMEASURED preserves SHA and generation | Correct. Apply across offline, live, checker loss and staging paths. |
| Two blind checks then repair hold | Safe containment, but recognized persistent failures should create the incident immediately. Reserve retries for plausible recovery. |
| Supervisor-owned offbox adapters | Correct direction. Preserve raw provenance and explicit evidence freshness; keep the Marker judging sufficiency. |
| GAP:OTHER → PASS | Honor the ruling as churn containment. Apply only after all obligations are independently shown satisfied; retain the coverage finding for follow-up. |
| Wider proof-path patterns | Necessary hotfix. Replace filename inference over time with registered artifact roles and computed changes. |
| Live-row classifier | Useful bridge. Keep uncertain cases out of automatic product rework; migrate to structured observations. |
| History and instrument snag route | Necessary. Enforce their effect in supervisor state transitions. |

The Marker rule still says “a proof that runs and is red is FAIL” and counts “a red test, a crash” as defects. Those statements continue to combine product and instrument faults. (*marker_rule_excerpt.py*, `RULE`.)

The WEAK change also needs honest interpretation. The latest shadow has **175 of 211 WEAK verdicts** changing disposition—about 83%, or 25% of all 697 verdicts. That shows enormous policy impact; it does not establish that all 175 were unnecessary holds or safe closes. (*weak_shadow.txt*.)

A synthetic mutant can violate a named requirement, and an empty per-generation diff can conceal earlier substantive work. Preserve the original accepted baseline for causal comparisons. Do not let `GAP:DIFF` depend solely on the last housekeeping commit. Several histories report empty diffs after earlier implementation work. (*item_histories.txt*, STEVE_DISK and PLANET_ATMOSPHERE.)

Finally, broad unholds after “the harness is fixed” need replacement with incident-specific release tests. The histories show blanket releases followed by further distinct failures. Release the attempts whose recorded dependency was repaired, then remeasure them. (*item_histories.txt*, 2026-11-03 02:33 unholds.)

---

**Measure delivery, measurement availability, and false closes together.**

| Metric | Counting rule |
|---|---|
| Accepted delivery yield | Accepted obligations ÷ intake-accepted obligations, by fixed intake cohort; show waiting and unresolved work |
| End-to-end cost | All builder, diagnostic, repair, checker and live costs per accepted item, plus unfinished-cohort spend |
| Attributable rebuild waste | Product-worker effort spent before any supported product attribution |
| Instrument availability | Fraction of scheduled validations obtaining valid required measurements, by component |
| Repeat waste | Attempts repeating an established condition without a retry warrant |
| Diagnostic effectiveness | Time to actionable attribution; later reversal rate; predicted versus observed experiment results |
| Repair leverage | Dependent validations restored per incident, with recurrence rate |
| False rejection/nonclosure | Known-good controls wrongly rejected, and controls left unresolved; report separately |
| Validator sensitivity | Known-bad catch rate by fault class, with counts |
| Observed false closes | Independently audited closes violating their obligations, stratified by closure age |
| Unknown validation debt | Number, age and business priority of items awaiting evidence or repair |

Use random closure audits for an overall estimate and targeted audits for high-risk changes; report those populations separately. Keep seeded misses separate from production escape rates. “No later complaint” is weak evidence of correctness.

Instrument failures can be excluded from product-test accuracy denominators, but their time and cost must remain visible in delivery metrics. Otherwise the system can improve its reported accuracy by measuring less.

The existing TRUST design already contains several good pieces (§9). Extend it with measurement availability, attribution reversals, unresolved debt, and repair fan-out. Its own warning remains applicable: finite controls establish limited evidence, not universal reliability.

**What you are most likely getting wrong is the enforcement point.** Prompts now ask agents to diagnose, while the supervisor still has paths that interpret unsuccessful acceptance as permission to rebuild. Contract locks can block legitimate instrument repair; isolation can remove necessary evidence; novelty-driven redesign can discard correct work; and holding everything can look rigorous while delivering nothing.

The first shipping milestone should therefore be concrete: **an unresolved validation preserves the candidate, creates the right diagnostic or repair work, prevents automatic rebuilding, and remains unable to close until the original obligations have adequate evidence.** That is the common fix behind tonight’s cases.
