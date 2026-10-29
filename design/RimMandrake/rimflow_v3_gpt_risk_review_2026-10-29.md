# RimFlow v3 risk report

**RimFlow v3 is not yet demonstrated to be a reliable autonomous production system. Several of its most important controls already fail in ordinary operation.**

The central problem is that the system often records an intermediate action as success:

- A claim verifies a wake-up, even if useful work does not follow.
- A running test job ends a SteveDesktop incident, even if the test environment is invalid.
- A completion label can survive substantial contradictory evidence.
- Filing a defect transfers it into a queue without guaranteeing that anyone will repair it.
- Launching a supervisory role demonstrates that it ran, without demonstrating that its output changed an outcome.

These are structural weaknesses. More frequent role runs, larger token allowances, or more helpers will not repair them by themselves.

The system has useful foundations: durable records, leases, explicit unknown measurements, separation between makers and reviewers, and some conservative safety gates. But **its operational guarantees are materially weaker than its role descriptions suggest**. The owner remains the person who discovers contradictions, resolves ownership, renews permissions, authorizes exceptions, and gets stalled work moving.

My recommendation is to prioritize a small set of enforceable production invariants and prove them through controlled failures before expanding the supervisory machinery.

## Reading this report

References to **AB** mean the as-built document; **Design** means the October 26 design of record; **HC** means the October 29 health check; **NA** means the night audit.

I reviewed the supplied text and searched primary literature and operational guidance. I did not inspect the live code, machines, or files. Therefore:

- **Observed** means demonstrated by the supplied evidence.
- **Inferred** means a failure follows plausibly from the described rules, but its occurrence is not established.
- **Unknown** means the implementation or evidence needed to decide is missing.
- **DESIGNED** safeguards receive no credit as operational protection.

Several qualifications matter:

1. **798 waiting items do not necessarily mean 798 executable items.** The incident proves inadequate handling of “waiting for tests,” but the eligible offline work must be reconstructed before estimating lost production.
2. **The health check corrects the grant incident to four grant-related bounces.** The fifth bounced ticket required an owner art decision. AB repeats the less accurate count in places. [HC §3.3; NA]
3. **“Validated” needs careful interpretation.** QUARRY had reached L2 while criteria remained owed. The evidence demonstrates a misleading aggregate status and unresolved contradictory results; it does not establish that all 26 failures tested the exact build and criteria underlying that status. [AB §6; HC §3.5]
4. **The rolling seven-day metrics largely include pre-v3 activity.** They demonstrate current problems, not that v3 caused the entire measured deterioration.
5. Slots before deployment are not production scheduling failures. HC was also written earlier than the extended as-built document, so some later scheduled runs had not yet become due.

## 1. Ranked risk register

“Detectability” means whether the **current operating system reliably notices and acts**, rather than whether a human can discover the problem afterward.

| ID | Risk | Mechanism | Evidence | Likelihood | Impact | Detectability today | Suggested direction |
|---|---|---|---|---|---|---|---|
| **R01** | Completion cannot be trusted | Status, commit, evidence and independent acceptance are not joined into an enforced contract | QUARRY validated with 26 fails/0 passes; ledger-only SHAs; reviewer request is a maker ritual; accepted output unmeasured. AB §§2.17, 6, 8; HC §3.5 | Observed | Critical | Poor; retrospective discovery | Enforce acceptance against a named build, criteria and independent evidence |
| **R02** | Steve can consume resources while producing invalid evidence | RUNNING ends incidents; canary failures do not reliably prevent repeated expenditure | Live dead-colony incident; three canary failures; AB §§2.15, 8 | Observed | Critical | Partial; symptoms recorded without dependable containment | Make environment validity a prerequisite for admission and incident resolution |
| **R03** | FOUNDRY can stop useful work while the system considers wake-up handling complete | Claims prove receipt; waiting is not represented as a managed work state; cooldown substitutes for recovery | Two approximately 70-minute idle cycles while jobs were pending and 798 items waited. AB §§2.2–2.5 | Observed | High | Logs detect no handoff; response is ineffective | Manage progress and dependencies after receipt; select other eligible work |
| **R04** | Findings and alarms fall into unowned or inactive queues | Findings have no consumer; new operational work still routes to BENCH after cutover | 128 untriaged findings; BENCH receives alarms but is never rung. AB §§2.13, 2.15, 2.20, 4 | Observed | Critical | Poor | Assign executable ownership and reconcile all routing after migration |
| **R05** | A monitoring failure can disable the roles needed to diagnose it | All role launches depend on fresh ops_watch; shared machine, scheduler and publishing dependencies | Operations refused on 117-minute-stale status; timer shutdown went unrecovered. AB §§2.1, 2.13, 8; HC §1 | Observed precursor; systemic outage plausible | Critical | Unknown external coverage | Add a minimal recovery path and dead-man signal outside the failed dependency |
| **R06** | Important incidents can remain unresolved despite multiple alarms | Daily run caps, six-hour suppression, claims stopping escalation, and owner relay delays have no repair guarantee | Operations’ two alarm slots consumed; invalid-lane diagnosis held. AB §§2.2, 2.8, 2.15, 4 | Observed | High | Partial | Track incidents through verified recovery; reserve severity-based response capacity |
| **R07** | Queues grow faster than they can be drained | Intake is unconstrained; builder, reviewer and lessons capacity are not balanced | 1,088 lessons; 622 under seven days old versus 40 folded weekly; inherited review backlog. AB §§2.10–2.11, 8; HC §3.2 | Observed | High | Counts visible; corrective control absent | Measure arrivals/departures and age; constrain WIP and remove duplicate work |
| **R08** | Quality controls discover defects without getting them fixed | Arbiter is advisory; Auditor can only file more tickets; fixes compete in the same builder queue | Fake-close prescreen defect remained proposed after reassignment. AB §§2.10–2.11, 4, 8 | Observed | Critical for known gate defects | Partial | Give gate repairs explicit priority and closure verification |
| **R09** | Human attention remains the final integration mechanism | Nearly every exception converges on one Conductor and one owner; proposals have no deadline | Grant renewal, overrides, cut lists, proposals, owner-only permissions. AB §§4, 7 | Observed | High | Attention itself is unmeasured | Record decision age, blocking cost, delegated authority and escalation |
| **R10** | Resource limits provide false confidence | Token “caps” are admission checks and retrospective alarms; helper policies disagree; total allocation is not enforced globally | Arbiter 1.02M against 500k; helper limits 2/3/6; live override and neutralized bands. AB §§2.1, 2.10, 2.14, 8 | Observed | High | Overruns visible after expenditure | Distinguish allowances from hard limits; reserve shared capacity atomically |
| **R11** | Supervisory work can perpetuate itself | Findings create process tickets; process tickets consume the builder; new process creates further maintenance | Process-only share 72.4%; most fundamental safeguards remain queued. AB §§2.19, 8; Design §§1, 6 | Strong warning; causation unproven | High | Weak outcome comparison | Require each process change to demonstrate a production benefit |
| **R12** | Success and kill criteria cannot govern deployment | Essential measurements are absent; comparison job is off; missing data can defer judgment indefinitely | Keep-going, accepted output and failure-signal share unmeasured. AB §§2.13, 6–8 | Observed | High | Known, but no effective consequence | Set an instrumentation deadline and explicit treatment of missing evidence |
| **R13** | Test effort is assigned to the wrong work | Producer’s mod decision has no execution path; defaults and filler choose workload | FlowWorks-only service defaults; no applied TESTQ mod configuration. AB §§2.9, 2.15, 4 | Observed | High | Poor; jobs still finish | Publish and acknowledge a versioned test allocation plan |
| **R14** | Permission and readiness failures repeatedly waste builder attempts | Permissions are checked too late; no visible expiry preparation or dependency ownership | Four grant-related overnight bounces; current grant location/expiry unverified. AB §2.16; HC §3.3 | Observed | High | Delayed until work refuses | Preflight readiness and surface expiry; preserve explicit consent boundaries |
| **R15** | Configuration and authority have split into incompatible versions | Charters, code defaults, schedule, overrides and seat identities disagree | Enabled headings stale; BENCH residue; four helper numbers; cap explanations stale. AB §§2.14, 2.20, 5, 8 | Observed | High | Mostly manual | One authoritative effective configuration, with machine-checked consistency |
| **R16** | Events or scheduled duties disappear during outages | Six-hour lookback, one-hour slot windows and dependencies can discard opportunities | Missed slots never recover; Operations dependency; event caps. AB §§2.1, 3 | Plausible; missed-slot behavior established | High | Journal records misses, not necessarily recovery | Retain obligations until satisfied or explicitly waived |
| **R17** | Restart or lease recovery duplicates or strands work | Interactive session lifecycle is separate from durable jobs, locks and leases | Kill path unexercised; stale request; 45-minute leases; long-running tests. AB §§2.4–2.5, 6, 8 | Unknown under failure | High | Unproven | Exercise interruption, fencing, cleanup and resumption end to end |
| **R18** | Git, evidence and state publication diverge | Local records may exist without successful publication; multiple clones and shared seat identities complicate consistency | 18 publish errors, push/rebase failures, trial verdicts in wrong path. AB §§4, 8; HC §1 | Observed | High | Partial | Track durable delivery, consumer acknowledgment and exact artifact versions |
| **R19** | Reviewers share the maker’s blind spots or insufficient evidence | Separate role names do not create independent observations; calibration is weak | Maker-selected review; shared tooling; four audit samples; 30-verdict threshold considers false rejection. AB §§2.10–2.17 | Plausible; verification defects observed | High | Low | Independent evidence selection; measure false acceptance and rejection |
| **R20** | Unproven recovery and maintenance automation causes a broader outage | Timer control, scratch deletion, shared resources and configuration edits have broad effects | All rm-/testq timers once stopped without restart; scratch growth; restart path untested. AB §§2.18, 3, 8 | Observed precursor | Critical in worst case | Unknown | Narrow scope, protected evidence, rollback and controlled failure tests |

## 2. Detailed assessment of the highest risks

### R01 — There is no enforceable meaning of accepted work

The most serious defect is the missing connection between “the ledger says progress happened” and “the requested behavior works.”

The intended north star is clear: named scenarios, a specific build, and a non-maker check. Yet that outcome has no dedicated event, accepted output cannot be measured, and the interim reviewer is requested by the same seat whose work it judges. The as-built review found no programmatic refusal of an unreviewed close. [AB §§2.17, 6]

The QUARRY example adds a second problem: aggregate state can remain reassuring while contradictory results accumulate. Even if “validated” technically means a partial level, a reader must reconstruct the unresolved criteria and test history to discover that limitation. A status requiring that investigation is unsuitable as a production summary.

Ledger-only SHAs are another warning. A legitimate investigation or verification task may produce no code change. That is acceptable. But its completion must describe the actual result; a convenient repository HEAD is not evidence that the intended implementation exists.

**Direction:** make acceptance a machine-checked event containing:

- The exact product build or artifact identity.
- The acceptance-criteria version.
- Evidence for each required criterion.
- Test environment, scenario and relevant fixture identities.
- An independent reviewer’s recorded decision.
- Explicit outstanding limitations and their authority.
- Any current contradictory evidence.

A new applicable failure should visibly invalidate the affected assurance or open a blocking regression. Historical passes should remain historical facts, without continuing to imply current correctness.

**Proof required:** an unreviewed close, unrelated SHA, partial result, invalid canary, stale-build pass and known current-build failure must each fail to produce accepted output. A genuine passing case must succeed.

This is more valuable than adding another report about completion quality.

### R02 — SteveDesktop has a liveness check where it needs a validity check

The steward’s incident-ending condition is RUNNING. That answers whether a job is executing. It does not answer whether the machine is producing usable evidence.

The live dead-colony incident demonstrates the difference. Three canary failures consumed time without a valid result. A CPU-busy rig can therefore appear operational while its contribution to production is zero.

There is an important unresolved contradiction: the documented testq behavior says INVALID/CANARY pauses the lane, yet the reported incident repeated. Possible explanations include:

- The failures were classified differently.
- Work was already admitted.
- Something resumed the lane.
- The worker and dispatcher ran different versions.
- The pause applied to only part of the execution path.
- A separate submission or execution path bypassed the check.

The supplied evidence cannot distinguish these. Calling this merely a bad threshold would be premature.

**Direction:** represent separate facts:

| Fact | Meaning |
|---|---|
| Reachable | Commands can reach Steve |
| Executing | A process is running |
| Environment valid | The required game state and sanity checks hold |
| Evidence usable | The requested scenario completed with interpretable results |
| Evidence consumed | A responsible actor used the result |
| Production contribution | The result supports acceptance, finds a defect, or provides required regression assurance |

An invalid canary should prevent further ordinary admissions for the affected environment. Resumption should require an explicit recovery check, rather than a momentary return to RUNNING.

**Proof required:** reproduce the dead-colony condition and show that expenditure stops, the incident remains open, responsibility is assigned, and a known-good recovery test is required before resumption.

**Passing tests are not waste.** A valid regression test that finds no defect may provide valuable assurance. The current “caught nothing” measure is therefore a poor stand-alone measure of usefulness. It can punish successful prevention and encourage the manufacture of findings.

### R03 — The Dispatcher manages delivery attempts, not continuing production

The ring protocol is reasonably explicit up to receipt. Its model of what happens afterward is inadequate.

In the incident:

1. FOUNDRY submitted two jobs.
2. It declared itself unable to proceed until they finished.
3. The Dispatcher detected no handoff.
4. The response was approximately an hour of cooldown.
5. The same pattern happened again.

The 600-second handoff deadline plus 3,600-second cooldown already explains a delay of roughly 70 minutes before scheduling overhead. This is policy-induced lost availability, not just slow model behavior. [AB §2.2]

The system lacks a useful distinction between:

- No eligible work.
- Work blocked on a named dependency.
- A worker waiting for a result.
- A worker confused about its instructions.
- A worker that has acknowledged work but made no progress.
- A genuinely exhausted queue.

FOUNDRY’s charter says to keep other lanes moving. That instruction did not produce the required behavior in the observed case. Repeating it more strongly would leave the same enforcement gap.

**Direction:** when waiting, require a structured record identifying the pending jobs, blocked criteria, expected next event and other eligible work considered. Keep the durable item open while releasing the seat to another executable item.

A ring should establish receipt. A separate progress control should establish useful advancement or a justified block.

**Proof required:** submit two slow test jobs while an independent offline ticket is ready. FOUNDRY should work the offline ticket and later reconcile both results exactly once. If no eligible work exists, it should record why and wake on the dependency’s completion.

Increasing wake caps cannot solve this failure. It only permits more attempts at the same broken interaction.

### R04 — Work is being produced for receivers that do not exist operationally

There are two proven holes.

**Findings have no running consumer.** They accumulate as UNTRIAGED events. Their visibility in ops_watch does not compensate for the absence of an assigned processing duty. [AB §§2.15, 4, 6]

**New operational items still route to BENCH.** The cutover moved autonomous building to FOUNDRY, but ops_watch and the steward continue producing BENCH work. BENCH is never automatically rung. This is a migration defect in work routing, even if a particular OPS item also triggers an Operations run. [AB §§2.13, 2.15, 2.20]

Reassigning the existing 691 items was insufficient. Every future producer of work also needed migration.

The designed findings sorter is sensible in principle: consolidate repetitions and reserve judgment for new cases. It does not yet close the hole. Its future FOUNDRY curation duty also needs reserved capacity and an overdue rule.

**Direction:** every source of work should identify a current receiver, acknowledgment, deadline and fallback. Reject or prominently quarantine items assigned to retired autonomous destinations.

**Proof required:** generate a test finding, disk alarm, Steve fault, audit defect and owner decision request. Trace each from creation through acknowledgment to disposition. No source should rely on the owner discovering it in an inactive queue.

### R05 — The monitoring system can prevent its own recovery

Fresh ops_watch status is a prerequisite for every scheduled role, including Operations. A stale or broken collector can therefore stop the diagnostic role that would ordinarily investigate the collector.

This is a circular dependency. It already produced an Operations refusal on stale status. [AB §§2.1, 2.13; HC §1]

The account and agents gates add further dependencies. An unreadable ledger also prevents launches. These are understandable precautions for normal production, but the system needs a deliberately smaller recovery path that can operate when ordinary prerequisites are unavailable.

Existing rm-deadman, timer-guard and steward-watch programs may provide some coverage. Their existence does not prove independence. If they share the same user systemd manager, machine, credentials, disk or publication route, a common failure can silence all of them.

The previous incident that stopped every relevant timer and left them stopped makes this concern concrete. [AB §8.30]

**Direction:** separate normal production admission from minimal recovery. A recovery check should be able to report stale measurements, inspect service health and perform narrowly authorized repairs without requiring the failed measurement first.

A dead-man signal should be observed outside the failure domain it supervises. It must test the notification path, not just update another local heartbeat.

**Proof required:** stop ops_watch, stop the Dispatcher, break publishing, and make the primary machine unreachable in separate controlled tests. Record what still detects the failure and where the owner-visible signal appears.

### R06 — Incident management can stop at a claim, a cap, or a suppressed alarm

Several rules reduce noise and spending, but their combination can defer important repair indefinitely:

- Operations gets only two alarm runs daily.
- An alarm gets at most one alarm run per day.
- There is a one-hour gap.
- Dispatcher alarm kinds repeat no more often than every six hours.
- A live claim pauses the steward’s unowned clock.
- Most owner communication waits for the Conductor.
- Proposals have no named timeout.

On day one, the invalid-lane diagnosis was held because other alarm runs had consumed the daily allowance. [AB §2.8]

A claim is evidence that somebody took responsibility. It is not evidence that the incident stopped harming production. A worker can keep a lease alive while making no useful progress, and the escalation clock may then remain paused.

**Direction:** distinguish acknowledgment, mitigation, repair and verified recovery. Keep an elapsed-impact clock running after acknowledgment. Assign one incident owner and one incident identity across steward, ops_watch, Operations and the ledger.

Routine alarms may be batched. Critical containment should have reserved capacity or a mechanical action that does not require another expensive AI run.

The repair target should follow the harm: permitted invalid test expenditure, blocked builder time, evidence loss or owner interference. A fixed “two incidents per day” limit has no such connection.

**Proof required:** exhaust routine alarm capacity, then introduce a canary failure. Verify that containment and escalation still occur.

### R07 — The learning queue is mathematically unstable under the reported policy

The lessons policy allows 40 folds per weekly pass. The inbox holds 1,088 files, including 622 less than seven days old. [AB §§2.11, 8.28; HC §3.2]

Assuming the stated cap applies to total folded files:

- With **no new arrivals**, clearing 1,088 requires **28 weekly passes**.
- Recent intake is approximately **15.6 times** the weekly processing allowance.
- Sustained intake of 622 per week against 40 departures increases backlog by approximately **582 files per week**.

Deduplication or bulk disposition could change this arithmetic. No such live mechanism is demonstrated.

The 14-day inbox expectation is incompatible with this capacity. “Weekly fold” is a cadence, not a sufficient service policy.

Similar capacity questions apply to the Auditor’s inherited 826 closes and 489 verify items, mandatory rechecks, new hard flags, random sampling and weekly work. Removing a count cap does not remove the wall-time and token constraints. [AB §§2.10–2.11]

**Direction:** measure arrivals, departures, age and repeat classes. Consolidate repeated lessons into a small set of enforceable rules; expire or reject low-value entries explicitly. Reserve capacity for old work rather than allowing new mandatory work to starve it.

The desired outcome is fewer repeated defects. Counting folded files can become another activity proxy.

### R08 — Independent review has insufficient authority over known defects

Separating Producer, Arbiter and Auditor is a sound response to the documented failure of self-review. The current operational arrangement weakens that separation.

- Arbiter verdicts are advisory.
- The binding interim review is not demonstrably enforced.
- The Auditor cannot reopen or reject work; it creates another ticket.
- The same builder must then choose the repair from a large queue.

The fake-close prescreen defect is especially serious. A known defect in a quality gate should change how that gate’s results are trusted until repaired. Filing a ticket while continuing to treat the gate normally leaves the known vulnerability active. [AB §§2.10–2.11, 4; HC §1]

There is also an unresolved distinction between role-file language about “blocking reds” and demonstrated code enforcement. A policy saying an item blocks is insufficient unless the relevant acceptance or release operation refuses to proceed.

**Direction:** define the effect of each verdict on admission, acceptance and release. Give defects in acceptance machinery a repair path that cannot be continually displaced by ordinary work.

**Proof required:** plant a harmless fake completion in an isolated test workflow. Show that it is refused, its defect is routed, the repair is implemented, and a repeat attempt is caught by the corrected gate.

### R09 — The owner is still the system’s exception processor

The Conductor reduces presentation volume: turning 47 owner items into approximately seven cards is useful. It does not show that the underlying decisions were eliminated.

The owner still controls or resolves:

- Permission renewal and account exceptions.
- Cut decisions and many proposals.
- Innovation authorization.
- Role activation and binding authority.
- Ambiguous routing and contradictory instructions.
- Emergency recovery when autonomous paths stall.

The Conductor is simultaneously the communication hub, interactive workshop identity, gatekeeper of information and scheduled supervisor. A live window can suppress its headless runs, even if the window is unattended. Window naming also needs testing because BENCH, CONDUCTOR and “AGENT CONDUCTOR” appear in different mechanisms. [AB §§2.6–2.7, 7]

“No timeout” on owner proposals is a substantial omission. A question can be technically delivered while blocking production for days.

**Direction:** record each decision’s age, affected work and default disposition. Delegate repeatable decisions by class. Maintain one routine human channel, with an explicit urgent path for system failure.

Measure owner minutes, interruptions, repeated questions and oldest blocking decision. Message count alone can improve while cognitive burden gets worse.

### R10 — Resource controls are inconsistent and partly fictional

The Arbiter’s run used approximately twice its nominal cap. This was allowed behavior: token caps are not mid-run stops. Calling them caps invites a false operational assumption. [AB §§2.1, 2.10]

The six role daily allowances sum to **7.75 million weighted tokens**, before interactive seats and the interim reviewer. That sum is not a hard system ceiling because an admitted run can overshoot.

Helper control is more confused:

- Role files say two across all roles.
- Schedule and slot rules say three for Conductor.
- The live budget says six.
- The allocator allows ten overall.
- An owner override remains attached to BENCH.
- Enforcement is per seat, not a global reservation system.

The owner explicitly authorized some overrides and neutralized throttling. Those decisions are not implementation bugs. The defects are unclear effective scope, stale explanatory text and weak enforcement of whatever policy is supposed to remain.

**Direction:** publish the effective policy, including overrides and expiry. Separate advisory allowances, launch limits and hard resource stops. Reserve shared helper capacity atomically, with recovery for stale reservations.

Maintain enough capacity for measurement, containment and repair when ordinary production has exhausted its allowance.

Token blindness can protect reviewers from lowering quality standards to save money. It is sound only if the surrounding resource controls actually work.

## 3. Systematic failure-surface map

### 3.1 Every handoff needs more than durable storage

For each handoff, the missing contract is some combination of:

**Who owns receipt? What proves understanding? How long may it wait? What proves action? What happens if the receiver is wrong? Who verifies recovery?**

Writing a file, creating a ticket or launching a process answers none of those questions by itself.

The following covers the live handoffs described in AB §4 and the additional lifecycle boundaries in §§2–6.

| Handoff | Receiver absent or slow | Receiver wrong, or output misleading | Required control |
|---|---|---|---|
| Owner → Conductor → recorded ruling | Unrecorded instructions remain conversational; blocking decisions age | Wrong interpretation becomes durable policy | Owner wording, scope, effective time and implementation acknowledgment |
| Conductor goals → Producer | Goals can remain stale while production continues | Producer optimizes an obsolete or misunderstood goal | Versioned goals referenced by each plan |
| Stop hook → armed doorbell | After the 23-hour wait expires, an otherwise live seat becomes unwakeable | Stale session identity can target the wrong lifecycle | Observe arming health and session generation |
| Dispatcher → FOUNDRY | Retry/cooldown delays; unarmed seat receives nothing | Receipt or claim is mistaken for useful progress | Receipt plus separate progress verification |
| Dispatcher → scheduled role | Gates and missed windows prevent a run | Unit completion is mistaken for completed duties | Structured duty results and carryover obligations |
| Role pre-launch → role | Evidence preparation may time out or delay the role | Incomplete or stale preparation biases judgment | Explicit preparation status and evidence cutoff |
| ops_watch → launch gates | Staleness blocks all scheduled roles | Fresh wrapper may contain old or unsuitable individual readings | Per-measurement freshness; degraded recovery path |
| ops_watch → token-blind roles | Missing digest leaves decisions unsupported | Allow-list can hide a relevant operational constraint | Versioned digest contract; explicit omitted/unknown fields |
| ops_watch → BENCH alarm queue | Autonomous receiver is absent after cutover | Alarm is treated as delivered because filing succeeded | Route to current operational owner |
| Account/runway alarms → Operations | Wait for next permitted run; some alarms are not ledger items | Recommendation has no acknowledged action | Durable incident or explicit accepted deferral |
| Operations → Producer replan | Event quota used; request waits for daily slot | Replan addresses a symptom but leaves dependency broken | Request acknowledgment, plan version and disposition |
| Operations → Conductor → owner proposal | No timeout; window hold or owner absence delays it | Summary loses urgency or action details | Blocking cost, urgency and decision deadline |
| Producer → FOUNDRY queue | Work waits behind gates, caps or unavailable seat | High-ranked work may be unready, duplicate or already done | Readiness check and eligible-work selection |
| Producer → Conductor → TESTQ configuration | Current path is missing | Plan says one mod; service runs FlowWorks | Applied configuration readback and acknowledgment |
| Producer cut list → owner → Producer | Undecided list blocks replanning | Approved cuts differ from applied cuts | Compare decision with CUT APPLIED |
| FOUNDRY → helper allocator → helper | Budget stale or role helper ban prevents capacity | Per-seat counts violate supposed shared limit | Global reservation and explicit owner override scope |
| FOUNDRY → bridge lock/grant | Lock or permission unavailable; ticket bounces | Stale ownership or inadequate remaining grant permits unsafe work | Preflight, bounded lock ownership and permission checks |
| FOUNDRY → testq | SSH outage, paused lane or low priority delays proof | Wrong build, scenario or environment is submitted | Immutable job specification tied to item attempt |
| testq → SteveDesktop | Remote outage or stale worker blocks execution | Remote artifact differs from requested artifact | Verify received build and fixture identity |
| Steve outbox → testq → ingest | Results can remain remote or locally un-ingested | Duplicates, late results or wrong item associations alter state | Durable acknowledgment and idempotent ingestion |
| Ingest → findings pool | No live consumer | Repeats obscure novelty or unrelated failures merge | Owned triage with version-aware grouping |
| FOUNDRY → interim reviewer | Maker omits request or waits indefinitely | Reviewer sees selected or incomplete evidence | Enforced independent review record |
| Close/claim → Arbiter | Batch timing delays judgment | Advisory judgment has no state effect | Explicit enforcement policy and review-age visibility |
| Arbiter → verdict file → Auditor | Wrong path makes verdicts effectively absent | Wrong cutoff or schema omits relevant decisions | Consumer acknowledgment and schema/path checks |
| Arbiter FAIL → owning seat | Repair waits in ordinary queue | Environment fault misdiagnosed as module fault | Diagnostic evidence and repair verification |
| Auditor DEFECT → owning seat | Known defect remains proposed | Duplicate ticket records concern without fixing source item | Linked regression and priority by exposure |
| Auditor escape → Arbiter | Next batch delays response | New test fails to cover actual escape | Reproduction tied to original failure |
| Auditor waiting picks → Conductor | Three daily runs can pass before escalation | “Waiting” is repeatedly reset or incorrectly classified | Age from first block, independent of run count |
| Lessons → Auditor → rule builder | Weekly capacity cannot drain intake | Lesson folded into unenforced prose | Verify recurrence prevention in execution |
| Innovator → Conductor → owner | Proposal waits indefinitely | Acceptance is confused with successful adoption | Distinct proposed, authorized, trialled and adopted evidence |
| Steward → BENCH → owner | Retired receiver; escalation delayed or paused by claim | Brief RUNNING interval ends unresolved incident | Current owner and recovery-based closure |
| seat_restart → killed seat → replacement | Relaunch fails; doorbell or locks remain stale | Replacement repeats work or accepts stale results | Lifecycle generation, cleanup and durable resumption |
| Ledger/git → publish → other clones/consumers | Dirty tree or push refusal strands updates | Different readers act on different histories | Delivery acknowledgment and reconciliation |
| Mirror → owner working copy | Mirror stops or lags | Mirrored build is assumed to be the reviewed build | Visible version identity and mirror age |
| Conductor/pulse → owner | Delivery may wait for a reading session | Short digest implies health without unresolved exceptions | Explicit stale, unknown and blocked indicators |

Two important **unknowns** require code-level tests:

- Does a blocked top queue item prevent the Dispatcher from finding lower-ranked eligible work?
- Does retry or event processing retain an unsatisfied obligation, or merely advance a cursor after attempting delivery?

The described behavior does not establish either guarantee.

### 3.2 Designed handoffs introduce further obligations

| DESIGNED handoff | Risk that remains even after implementation |
|---|---|
| Ingest → findings sorter → Operations/FOUNDRY | Signature normalization can merge distinct failures; version changes can split repeats; three passes can retire the wrong build’s failure; daily judgment still needs capacity |
| Health extract/tag/trace → daily page → Operations | Tagging errors, stale summaries and self-assessment can produce reassuring reports without changed outcomes |
| Auditor plants → register → Conductor/Arbiter | Live knowledge can cue responders; plants can contaminate production or metrics; plant cleanup and attribution need independent verification |
| Daily process-model fit → current.json → Operations | A successful fit can be poorly identified or predictively useless; repeatedly reused holdouts can leak into tuning |
| Plan tracker → Producer → immediate Conductor wake | Shared event quota can suppress the new event; “immediate wake” has no demonstrated path around existing holds and caps |

These designs should be tested as new production paths. They do not automatically repair the old paths merely because their duties are specified.

### 3.3 “Done” signals that can be satisfied without the intended result

This is the main Goodhart surface: behavior can improve the visible measure while leaving the real objective unchanged.

| Signal | What can satisfy it | What remains unproven |
|---|---|---|
| Ring verified | Claim/start/lease event | Useful progress |
| Seat alive | Recent activity | Correct work |
| Lease renewed | Periodic renewal | Advancement or genuine ownership |
| Role `done` / `end_turn` | Process ends normally | All required duties completed |
| `RUN COMPLETE` | Text marker | Plan executable or implemented |
| Commit SHA present | Any available commit, including ledger-only | Relevant product change |
| Implemented/built | Maker records implementation | Behavior works |
| Validated | Some qualifying verification history | All required current criteria pass |
| Test DONE | Runner finishes | Scenario valid and result interpretable |
| Steve RUNNING | Job starts | Rig healthy or useful |
| Finding filed | New record exists | Finding read, diagnosed or repaired |
| Audit defect ticket filed | Concern transferred to queue | Exposure reduced |
| Lesson folded | File moved, deleted or rewritten | Repeat error prevented |
| TESTQ mod choice recorded | Producer writes decision | Service executes chosen allocation |
| Innovation adopted | State updated | Benefit survives real use |
| Low unused quota | Tokens consumed | Valuable output |
| Fewer owner messages | Larger cards or less reporting | Lower attention burden |
| Low process-commit share | Reclassifying, squashing or adding product commits | Better production efficiency |

Use these as diagnostic signals. Do not let them stand alone as proof of production success.

### 3.4 Who watches the watchers?

| Monitor/control | What it sees | Silent failure or blind spot |
|---|---|---|
| Dispatcher | Seat activity, gates, claims, role units | Cannot judge useful work; its own failure needs an independent observer |
| ops_watch | Collected metrics and freshness marks | Fresh status can coexist with stale individual readings; all gated roles can disappear when it fails |
| Steward | Lane state and ownership | RUNNING can hide invalid execution; claim pauses escalation |
| Steward-watch | Heartbeat | Healthy heartbeat does not prove valid tests or consumed results |
| rm-deadman / timer-guard | Other timers, as described | Coverage, external delivery and resistance to common shutdown are not demonstrated |
| Arbiter | Supplied evidence and verify bar | Advisory; maker-selected evidence; missed or misplaced artifacts |
| Auditor | Prescreen plus selected rechecks | Capacity, biased sample, unresolved mandatory work, and no direct repair authority |
| Interim reviewer | Consulted close | Invocation is optional in enforcement terms; absence may be invisible |
| Conductor | Allowed inputs and relayed issues | Window suppression, summary loss, stale goals and attention bottleneck |
| Nightly selftests | Encoded expected behavior | Components may pass while their integration fails |
| Evidence-tamper alarm | Defined tampering symptoms | Authentic evidence can still concern the wrong build or scenario |
| v3_vs_v2 | Comparative metrics | Off, incomplete inputs and invalid counterfactual |
| Proposed health page/model | Derived summaries and predictions | Can validate its own reporting while production remains broken |

A timer being active and its service exiting successfully are weak health signals. The stronger test is a small end-to-end transaction that reaches the intended consumer and produces the expected state change.

### 3.5 Feedback loops, deadlocks and single points of failure

| Loop | How it fails |
|---|---|
| **Wait → cooldown → wait** | Pending tests cause FOUNDRY to stop; Dispatcher waits an hour; pending tests still block the next turn |
| **Invalid rig → retry → more invalid work** | A job starts, clears the incident, then fails; subsequent work repeats the expenditure |
| **Findings → process tickets → less product capacity → more findings** | The only builder spends increasing time maintaining the production machinery |
| **Hard flags → audit priority → no random sampling** | Mandatory work continuously displaces broader quality measurement |
| **Claim → escalation paused → no repair** | Ownership activity suppresses attention while impact continues |
| **Stale measurement → Operations blocked → stale measurement persists** | Recovery depends on the failed prerequisite |
| **Permission expired → repeated claims → bounces** | Readiness is discovered after scarce worker effort is spent |
| **Cap exceeded → cap raised → more overhead** | The response to expensive supervision becomes permission to spend more without demonstrated benefit |
| **Conductor helper borrowing → FOUNDRY payback** | Interactive activity can leave the autonomous builder under-resourced afterward; debt needs limits and visibility |
| **Audit finding → new ticket → ordinary queue** | Quality oversight repeatedly discovers the same exposure without obtaining repair |
| **Restart held by helper/lock/game state** | A stale blocker may prevent context recovery; expiry of the restart request may erase the intended action |

The principal single points are the autonomous FOUNDRY seat, the Dispatcher, ops_watch as a universal gate, the ledger/projection/publishing path, the primary machine’s user services, the Steve worker, and the Conductor-owner decision channel. The bridge and companion grant are additional single points for live validation.

Adding more agents on the same machine and through the same dependencies does not remove these shared failure modes.

## 4. Comparison with research and operational practice

### Multi-agent failure research: the observed problems fit established categories

The revised MAST paper identifies 14 failure modes across system design, inter-agent coordination and task verification. It analyzes more than 1,600 traces from seven frameworks. Its categories are useful diagnostic tools; its benchmark frequencies are not estimates of RimFlow’s failure rate. [Cemri et al., *Why Do Multi-Agent LLM Systems Fail?*](https://arxiv.org/html/2503.13657)

| MAST category | RimFlow correspondence |
|---|---|
| Specification and role failures | Conflicting helper limits; stale BENCH ownership; charter instructions differ from enforced behavior |
| Repeated steps and stopping-condition failures | Repeated invalid tests; recurring idle waits; process work that reproduces its own queue |
| Coordination failures | Unconsumed findings; wrong verdict path; TESTQ decision never applied |
| Reasoning/action mismatch | FOUNDRY’s continuous-work charter versus stopping while other work may be eligible |
| Premature termination | Ending a work turn while dependencies and follow-up remain unmanaged |
| Missing or incorrect verification | Optional review enforcement, ledger-only evidence, reassuring state despite unresolved failures |

The important implication is that better models alone will not fix these coordination and verification defects.

### Agentic-workflow guidance favors explicit, testable boundaries

Anthropic recommends simple, composable patterns, increasing complexity when needed, grounding execution in environmental results, and defining stopping conditions. RimFlow’s deterministic scheduling and durable state fit that advice. Its overlapping identities, conflicting policies and incomplete handoffs undermine the simplicity and observability those patterns need. [Anthropic, *Building effective agents*](https://www.anthropic.com/research/building-effective-agents)

OpenAI’s guide recommends incremental development, clear tools and instructions, explicit run exit conditions, and human intervention after repeated failures. RimFlow’s original staged rollout was consistent with this. Enabling all supervisory roles before proving unattended delivery and measuring accepted output weakens the ability to identify which role helps. [OpenAI, *A practical guide to building agents*, pp. 13–16, 30–32](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)

Neither guide establishes that an executive-style org chart is an effective architecture for this workload. Role separation needs measured benefits.

### SRE: alert on broken service, then manage recovery

Google’s monitoring guidance distinguishes symptoms from causes and stresses actionable alerts. RimFlow collects many internal causes and activity measures, but the service symptoms that matter are incompletely measured: no accepted output, invalid test evidence, blocked production and repeated owner intervention. [Google SRE, *Monitoring Distributed Systems*](https://sre.google/sre-book/monitoring-distributed-systems/)

SLO-based alerting evaluates precision, recall, detection time and reset time. RimFlow currently emphasizes alarm frequency limits without demonstrating those four properties. [Google SRE Workbook, *Alerting on SLOs*](https://sre.google/workbook/alerting-on-slos/)

An error budget is useful because consuming it changes operating behavior. A flag that remains above target while ordinary operation continues is reporting, not a comparable control. RimFlow should define what production or process expansion pauses when reliability deteriorates. [Google SRE Workbook, *Example Error Budget Policy*](https://sre.google/workbook/error-budget-policy/)

A proper dead-man check verifies the alert pipeline and is observed externally when its signal disappears. Local watchdogs sharing a failure domain do not provide that guarantee. [Prometheus Operator, *Watchdog runbook*](https://runbooks.prometheus-operator.dev/runbooks/general/watchdog/)

SRE also distinguishes repetitive operational toil from engineering that produces enduring improvements. Process commits are therefore not automatically waste. The test is whether they reduce recurring intervention or improve production. [Google SRE, *Eliminating Toil*](https://sre.google/sre-book/eliminating-toil/)

### Queueing, Kanban and Theory of Constraints

Little’s law relates average work in a defined system, throughput and elapsed time: **L = λW**. Its useful application here requires consistent boundaries and meaningful completed units. Raw ticket counts and incomparable items cannot provide a credible delivery forecast. [John Little, *A Proof for the Queuing Formula: L = λW*](https://pubsonline.informs.org/doi/abs/10.1287/opre.9.3.383)

The Kanban Guide calls for explicit workflow states, WIP control, work-item aging and service expectations. RimFlow has queues and leases, but does not demonstrate a consistently enforced limit across building, pending tests, review and rework. A limit only on active coding would hide unfinished work downstream. [*The Kanban Guide*, May 2025](https://kanbanguides.org/the-kanban-guide/2025.5/)

Theory of Constraints directs improvement toward the bottleneck and subordinates other activity to it. Steve utilization is irrelevant to throughput if valid environments, result consumption, independent acceptance or owner decisions are the actual constraint. The constraint may change over time. [Goldratt Research Labs, *Introduction to Theory of Constraints*](https://www.goldrattresearchlabs.com/introduction-to-toc)

### Goodhart: the proxy can improve while the objective deteriorates

Manheim and Garrabrant distinguish several mechanisms by which optimizing a metric can damage the goal. RimFlow need not contain deliberate deception for this to happen. Rewards implicit in instructions—keep Steve busy, consume expiring quota, close tickets, fold lessons—can generate convincing activity without increased accepted product output. [*Categorizing Variants of Goodhart’s Law*](https://arxiv.org/abs/1803.04585)

Countermeasures should combine outcome measures, diagnostic activity measures and occasional independent inspection. No single throughput number should determine success.

### Test quality: invalidity, failure and flakiness are different

Google defines a flaky result as passing and failing on the same code and describes how noisy tests cause real failures to be ignored. Retrying and quarantining can help, but can also hide defects. [Google Testing Blog, *Flaky Tests at Google and How We Mitigate Them*](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)

RimFlow’s dead colony is an invalid precondition, not established flakiness. Twenty-six failures with no passes are not evidence of flakiness either. Classification requires build, environment and scenario identity. Retry policy should follow the failure class.

### Chaos engineering and organizational design

Chaos engineering starts with a measurable operating condition, introduces a realistic fault, and observes whether the condition survives, while containing harm. RimFlow’s proposed external plants are directionally sound, but the simplest deterministic failure tests should come first. [*Principles of Chaos Engineering*](https://principlesofchaos.org/)

RACI clarifies who performs work, who ensures completion, and who is consulted or informed. RimFlow’s role cards describe specialties, but do not consistently identify who ensures each handoff finishes. [Microsoft, *Define roles and responsibilities*](https://learn.microsoft.com/en-us/power-platform/guidance/adoption/roles)

There is no defensible universal “correct number of AI direct reports” to import from human management. Here, span of control should be assessed through unresolved decisions, handoff volume, waiting time and the Conductor’s actual handling capacity.

## 5. Decisions that look arbitrary and unstable

The problem is not that an initial number was guessed. Initial values often must be provisional. The problem is that many values lack a demonstrated relationship to harm, capacity or measured behavior, and several interact badly.

The following covers the parameters in AB §5 and the expanded restart and allocator settings. Grouping is used where the interaction is the risk.

### Dispatcher, delivery and scheduling

| Parameter | Assessment |
|---|---|
| **Tick 120s; boot delay 3min; accuracy 5s** | Reasonable initial cadence, but “every two minutes” is misleading because the timer waits after completion. Measure actual intervals. |
| **Tick budget 420s; service timeout 600s** | A budget-length tick plus the next delay gives about **nine minutes** between starts; a timeout-length run gives about **12 minutes**, excluding other delays. Short downstream timers must tolerate this. |
| **Idle threshold 240s** | No evidence establishes this as the useful boundary between normal thought/tool latency and lost availability. |
| **Ring verification 300s** | Must exceed real delivery latency under load. An unarmed doorbell bypasses this whole retry mechanism. |
| **Handoff deadline 600s** | Defines claim latency, not useful progress. Exactly matches the dead-seat threshold, which can confuse diagnosis if observation is coarse. |
| **Retries 2, giving 3 attempts** | Reasonable finite retry bound, but repetition is useful only for transient delivery failure. It cannot repair a mistaken worker interpretation. |
| **Cooldown 3600s** | Demonstrably too blunt for the observed waiting case. The approximately 70-minute cycle is a direct consequence. |
| **Dead threshold 600s** | Needs a heartbeat definition that distinguishes a dead seat from a long blocking tool call. |
| **Recovery verification 300s; 3 recoveries/day** | Inactive while recovery is off. Do not describe these values as current protection. |
| **Wake caps 12/hour, 96/seat/day, 120/day** | Count wake attempts rather than productive availability. Raising them treats a symptom unless each extra wake produces useful output. |
| **Defaults 3/30/80/3** | Missing configuration silently changes policy substantially. Required production keys should fail validation rather than inherit surprising defaults. |
| **Owner idle 1200s; probe boot slack 60s** | Conservative protection is sound. Idle does not itself grant permission, prove game availability, or prevent the owner returning immediately afterward. |
| **Alarm repeat 21600s; hold alarm repeat 21600s** | Six-hour suppression is excessive for some production failures. New severity or worsening impact should not be hidden as the “same kind.” |
| **ops stale 2700s** | Allows three normal 15-minute collection intervals before gating. Its harm depends on the metric; a universal freshness threshold is coarse. |
| **Future tolerance 300s** | May conceal clock errors large enough to distort ordering and expiry. Compare with helper future tolerance of only 5s. |
| **Event lookback 6h** | Dangerous unless unread obligations survive longer outages. Test cursor behavior after outage, quota exhaustion and malformed events. |
| **Run-now TTL 3600s** | A request may expire while gates are closed. Expiry needs an acknowledged failure, not silent disappearance. |
| **Slot lateness 3600s; no catch-up** | Appropriate for some obsolete snapshots, inappropriate for mandatory unresolved duties. Separate an expired appointment from an owed obligation. |
| **after_role Operations** | Useful sequencing, but unnecessary coupling if followers could work with explicit stale/unknown status. A missed Operations slot can eliminate multiple duties. |
| **Local-midnight accounting** | Test straddling runs, daily cap attribution, clock changes and the coming daylight-saving transition. Relative waits and local-day caps serve different purposes. |

### Doorbell, leases and restart

| Parameter | Assessment |
|---|---|
| **Doorbell poll 3s; maximum wait 23h** | Polling is responsive; the near-daily expiry creates an unattended lifecycle hazard without demonstrated automatic rearming. |
| **Lease 45min; renewal every 10min** | Reasonable spacing, but renewal proves ownership activity. Long test waits and restarts require explicit handling. |
| **Context backstop 110,000 tokens** | Needs evidence linking context size to error risk and restart cost. Token count alone is not a quality diagnosis. |
| **Backstop idle 1800s** | A continuously active but deteriorating session may never qualify. A stuck idle session may wait 30 minutes before recovery starts. |
| **Configured grace 30s versus default 120s** | Material policy difference. Verify which actions cancel, postpone or survive the grace. |
| **quiet 30s; busy_ticks 3** | “Three ticks” has variable elapsed duration because tick runtime varies. |
| **Restart verify 90s** | Needs to cover real launch and rearming latency, including slow disk and account initialization. |
| **arm 900s; intile wait 30s/window 90s** | Several nested clocks can create races. Test the exact state sequence under delayed startup. |
| **Helper stale 3600s; game hold 3600s** | A stale helper or game marker may delay recovery for an hour. Holding needs visible reasons and bounded cleanup. |
| **Restart cooldown 1800s; hold alarm 3600s** | Can suppress repeated failed recovery while the seat remains unavailable. |
| **Request max age 3600s; claimed max 300s** | Request expiry must not erase an unresolved restart need; claimed expiry needs safe ownership transfer. |
| **Owner idle 120s; backstop owner idle 1200s** | Different thresholds may be intentional, but their safety rationale should be explicit. |
| **Fence 1020s; ring hold 600s** | Need a demonstrated ordering model with leases and late results; constants alone do not prove exclusive ownership. |
| **SIGTERM then SIGKILL after 10s** | Requires evidence that commits, state writes, locks and remote jobs survive or recover correctly. |
| **Scope grace 600s; stop 30s** | A lingering scope gets a substantial extra window. Verify whether it can still mutate state or consume resources, and whether stopped work is reconciled. |
| **Only human input cancels pending restart** | Test legitimate machine activity during the pending transition. A new claim or helper must not race with the kill. |

### Resources, helpers and accounts

| Parameter | Assessment |
|---|---|
| **Helper budget max age 600s** | “Five missed ticks” assumes short ticks; a normal slow tick can approach this duration. Independent hook recomputation may then disagree with the allocator. |
| **Helper future slack 5s** | Much stricter than the role status tolerance. Clock policy should be coherent. |
| **Limits 2 globally / 3 session / 6 live / total 10** | These are competing policies. Resolve effective authority before tuning their values. |
| **BENCH override until Nov 4** | Explicit owner authorization exists, but its identity and checkout scope must survive the seat migration correctly. |
| **Owner-window helper borrowing and payback** | Can create delayed autonomous starvation. Bound debt and show its production effect. |
| **DARK at 98% used** | Leaves little recovery capacity unless protected elsewhere. |
| **ALMOST_OUT enter <0.5, leave >0.8; hold 2h** | Hysteresis is sound. The thresholds need forecast-error measurements. |
| **CRUISE steps at pace 0.8/1.0/1.2** | Small measurement changes can change concurrency. Determine whether the fit is sufficiently stable. |
| **BURN enter >1.5 with <48h to reset; leave <1.2 or <6h** | Encourages spending near reset. Unused quota is not equivalent to wasted production opportunity. |
| **SWEEP 3; hold 12h; cross-hold 2h; minimum mode 60min** | Damp oscillation, but may preserve a bad mode through changed conditions. Safety exceptions need precedence. |
| **Fit 3h; ≥4 points over ≥1.5h; 1460 messages/%** | Weak grounding for a changing mixture of models, cached input, long runs and helpers. The live budget explicitly lacked a measured burn rate. |
| **Session brake >90%; spare 10%** | Potential recovery reserves, but interaction with owner overrides and neutralized role bands is unclear. |
| **Lent account ≤48%, prefer first 48h, floor 10%** | Respecting account permission is sound. Enforcement, time basis and override precedence need confirmation. |
| **Queue paydown A1>100 or D1≥10; exit A1<60 and D1<5** | Hysteresis is useful, but work count does not measure effort or acceptance capacity. |
| **Presence bench 30/AFK 60; live helper window 900s** | May classify stale activity as current presence; test against actual owner and helper sessions. |
| **Finish margin 6h; default overage window 24h; bench floor 1** | Unclear relationship to current one-builder architecture and recovery requirements. |
| **Codex conservation runway 1.0; Steve stall 30min/invalid streak 3** | Cross-system resource choices must not disable repair while preserving low-value production. |
| **24GB seat slice/10GB per seat; 12GB harness slice** | Need combined memory and disk-pressure evidence including game, remote coordination and helper concurrency. |
| **Account switch <0.8 or <10%; target ≥1.2/≥20%; minimum draw 10%; soonest reset** | No demonstrated optimization objective combining permission, reliability and useful output. Today these are recommendations, not controls. |
| **Neutralized throttle bands; empty hold list** | Intentional overrides. Their effective duration and restoration conditions should be explicit rather than “when he is back.” |
| **Weighted tokens 1/1.25 or 2/0.1/5** | Useful internal accounting if consistent. They are not automatically money, latency or resource consumption. |

### Role schedules, budgets and calibration

| Parameter | Assessment |
|---|---|
| **Conductor 08:00/20:00; 450k/run, 1.35M/day; session 6% weekly** | No demonstrated relationship between cadence/spend and decision delay. Window suppression can remove scheduled coverage. |
| **Operations 07:30/19:30; 450k run/550k economy/1.65M day** | Twelve-hour routine spacing demands dependable event handling. Repair capacity should not depend on expensive diagnostic runs alone. |
| **Operations alarms: 1h gap, 1/alarm/day, 2/day** | Already starved a diagnosis. Severity and ongoing impact must matter more than incident count. |
| **Producer 09:00; Wednesday weekly; 800k/run, 2M/day** | Daily ordering may be useful; event-only replanning is fragile when the single event allowance is consumed. |
| **Producer 1 event/day** | Shared failure, replan and future slip signals can displace each other. Unsatisfied requests need carryover. |
| **Arbiter 11:00/17:00; 500k/run, 1.25M/day** | Long acceptance delays are possible; budgets have already been exceeded substantially. |
| **Arbiter preparation 900s, tiers 6, max 1200s** | Potential evidence bottleneck. Establish whether preparation time is included in other deadlines and what happens to excluded items. |
| **Arbiter binding after 1 week/30 verdicts** | Too weak as a calibration rule. False acceptance is essential; false rejection alone is insufficient. Thirty total verdicts may contain far fewer relevant cases. |
| **Auditor 13:00; 700k/run, 875k/day; 45min wall time** | Multiple unbounded duties compete inside a finite run. Evening Arbiter verdicts may wait roughly 20 hours for the next audit. |
| **Audit escalation after 3 runs** | Under daily execution this can mean days. Use elapsed impact and age. |
| **Random slice 1 in 5** | This is a fraction of selected picks, not necessarily 20% of all closes. Preserve sampling capacity against mandatory workload. |
| **Lessons 40 weekly; inbox ≤14 days** | Incompatible with reported intake unless substantial aggregation/disposal changes the unit of work. |
| **Innovator Tue/Fri/Sun; 500k/run, 625k/day** | Three runs weekly are not justified by one observed proposal. Measure benefit and owner handling cost. |
| **Probation exit 3 adopted/no failed revert in 30 days** | Three easy cases do not establish broad reliability. Rare trials can satisfy the no-failure period with little exposure. |
| **Run wall limits 30/45min** | Real stops, but abrupt termination creates partial-work obligations. |
| **Headless helpers disabled; helpers_max 2 unused** | Conservative pending a shared cap. Documentation should distinguish unavailable capacity from configured capacity. |

For scale, even **zero errors in 30 independent representative cases** would still leave an approximate 95% upper bound near 10% on the error probability. Real verdicts will not necessarily be independent or representative. The current threshold should not be mistaken for strong validation.

### Measurements, thresholds and test allocation

| Parameter | Assessment |
|---|---|
| **ops_watch every 15min; timeout 420s** | Appropriate for some trends, slow for containment of invalid expensive jobs. Keep immediate admission checks local. |
| **Seven-day baseline, 3σ, minimum 20 points** | Recent structural change and correlated readings weaken statistical meaning. Twenty quarter-hour points are not twenty independent operating days. |
| **Eight same-direction readings** | Useful flag, but rolling seven-day values overlap heavily. Eight rises are not eight independent confirmations. |
| **Silence 2h/3h/6h by family** | Six hours of silent test/process evidence can hide most of an unattended session. Relate windows to tolerated harm. |
| **Clear after 4 passes; lock wait 90s** | Four ordinary collections can take about an hour. Rearming must handle recurrence and worsening severity during that interval. |
| **Runway <1.0 alarm** | Forecast uncertainty matters; stale estimates should not masquerade as current constraints. |
| **Steve stall >30min; unclaimed >10min; invalid streak ≥3** | Multiple overlapping policies, with different clocks and owners. A canary invalidity may warrant stopping on the first confirmed failure. |
| **Disk <210/200/200GB; root <420GB flag** | Absolute free space is weak without growth rate. At 207GB/day, exhaustion time matters more than a fixed number. |
| **Failed units/tamper >0** | Useful exact invariants, provided intentional stops and evidence scope are defined. |
| **Nothing-tests >18h flag only** | Neither proves waste nor produces a required action. Replace the interpretation before strengthening the alarm. |
| **Process share ≥61%; token talk ≥10%; findings >0 flags** | Thresholds mix outcome, style and queue health. Repeated breaches require explicit disposition; zero findings may also mean broken detection. |
| **Testq 60s after completion; timeout 900s; SSH reprobe 300s** | A timeout-length tick plus delay is about 16 minutes between starts. Probe and heartbeat expectations must reflect actual timing. |
| **Fill 4 chains; 8h/day; 200 jobs** | Resource bounds are sensible; relevance is weak. Oldest-run selection does not establish value or unblock priority work. |
| **Priority → same-profile train → oldest** | Can starve old low-priority jobs. Measure oldest age and ensure required proof is not displaced by filler/profile convenience. |
| **DRY after 2 unmeasured runs; retry after 3 days** | Can leave critical scenarios untested for days. Unknown results should create an owned evidence gap. |
| **Two non-DONE fillers brake** | Helpful containment, but coarse status may miss repeated useless DONE results. |
| **Nightly sweep 01:30, FlowWorks default** | Can duplicate filler or explicit jobs. Confirm deduplication by build and scenario. |
| **One automatic retry** | Reasonable for selected transient failures; not for deterministic invalid fixtures without repair. |
| **Steward 10/30/120min; manual pause fault 60min; READY fault 5min; heartbeat 5min** | Escalation complexity exceeds the demonstrated incident model. Claims and RUNNING transitions can defeat the intended timing. |
| **Archmagi 600s silence/1800s backoff** | Inactive protection while the lane is off. Historical hours require configuration attribution. |
| **Grant minimum remaining 45min** | Sound refusal threshold, but must cover the admitted suite or provide a safe expiry protocol. It is not permission to renew automatically. |
| **24h close-after attribution** | Can label valuable regression work useless and reward loosely associated closes. |
| **Keep-going ≤26/day; failure signals ≤25%; process <61%** | Useful hypotheses, not universal thresholds. Baselines, definitions and uncertainty must be comparable. |
| **SUPERIOR: 4/7 primaries, 3/4 settled weeks** | Majority voting can hide unequal importance. Veto guards are sound, but cost needs an explicit acceptable trade-off. |
| **Noise bands from 7 baseline days** | Limited evidence, especially with weekday patterns, serial dependence and changing work mix. |
| **Missing primaries / counterfactual coverage 0.75** | Refusing unsupported conclusions is sound. Missing inputs must not indefinitely postpone the deployment decision. |

### Parameters in the new designs

- **12:00/18:00 Producer checks, possible 15:00 addition:** plausible trial values, but a third scheduled slot is not the first remedy for broken result handling. Sharing one daily event allowance remains a conflict.
- **Excluding closes under five minutes:** useful suspicion flag, poor acceptance rule. A two-minute repair can be real; a six-minute ledger exercise can be empty.
- **Daily 06:30 model, 30-minute timeout, 20×150 steps, 120 members, four processes:** reproducibility and bounded execution are good. None of these values establishes convergence, identification or useful prediction.
- **Three model failures to RED; stale after 36h:** a daily fit can be stale for a considerable period before action. Preserve the last valid model visibly, without presenting it as current.
- **Hourly tagging and 15-minute health extraction:** validate classification accuracy, missed messages and boundary cases before interpreting small changes in owner behavior.
- **Three passes to retire a standing failure:** must be scoped to applicable build, scenario and environment. Pass streaks across incomparable conditions are meaningless.
- **Random planted-fault time:** randomness is useful after a reliable test harness exists. First prove deterministic coverage, safe cleanup and complete tracing.

## 6. What cannot be known yet, and how to find out

| Unknown | Why existing evidence cannot answer it | Smallest useful investigation |
|---|---|---|
| How much production the idle incident lost | Waiting queue is not equivalent to ready work | Reconstruct eligible items, dependencies and permissions at each idle interval |
| Why canary failure repeated despite pause rules | Classification, versions and resume events are missing | Trace the three jobs through admission, canary, result, pause and resume |
| Whether QUARRY status contradicts exact-build evidence | Results span days and may cover different criteria/builds | Join every verify to build, scenario, criterion and status transition |
| Whether close review is enforceable | Role text is present; a rejecting hook was not found | Attempt a harmless unreviewed close in an isolated fixture |
| Actual independent acceptance throughput | No adequate event or baseline exists | Define and instrument acceptance, then retrospectively label a bounded sample |
| True defect escape rate | Four selected audits are too few and biased | Blind sample of accepted work, with known sampling probabilities |
| Arbiter accuracy | Advisory trials and incomplete calibration | Blinded representative good/bad cases; measure false acceptance and rejection |
| Findings’ distinct actionable volume | Repeated failures inflate count | Manually label a sample and evaluate proposed grouping against it |
| Actual bottleneck | CPU hours, claims and commits do not locate it | Measure time waiting for builder, permission, test, ingestion, review and owner |
| Whether WIP is enforced end to end | Producer outputs a cap; enforcement is not demonstrated | Start work to the boundary and attempt excess work across downstream states |
| Event survival during outage or quota exhaustion | Cursor advancement semantics are unspecified | Pause beyond six hours; exhaust event quota; restore and inspect pending obligations |
| Common-mode monitoring coverage | Watchers’ dependencies are incompletely documented | Stop shared services/machine and observe external detection |
| Restart correctness | Live kill-and-relaunch path unexercised | Interrupt representative local and remote work; verify cleanup and single resumption |
| Publishing consistency | Errors are known, delivery reconciliation is not | Inject dirty tree/push refusal; verify no event is lost or treated as delivered prematurely |
| Grant expiry behavior | Current grant location and lifetime unverified | Trace permission source and perform a controlled near-expiry refusal |
| Owner attention saved | Message measures missing; batching changes message size | Sample active handling minutes, interruptions and repeat questions |
| Whether v3 pays for itself | Mixed windows, incomplete outcomes, counterfactual failure | Prospective frozen definitions, matched work classes and explicit cost/attention accounting |
| Daily model validity | Successful computation is not predictive validation | Timestamp predictions before outcomes; evaluate forward error and interval coverage |
| Safety of scratch reaping and broad maintenance | Protection of active evidence is not shown | Verify referenced artifacts survive cleanup; test rollback and recovery |

Four cautions apply to the eventual v2/v3 comparison:

1. Different rolling windows can legitimately produce 72.4% and 61.6%. That alone does not prove either instrument is wrong.
2. Changing staffing, thresholds, models, workload and owner behavior simultaneously makes causal attribution difficult.
3. “Settled” needs a predeclared definition; otherwise unfavorable weeks can be excluded after inspection.
4. A daily statistical model cannot recover causal evidence absent from the underlying record.

## 7. A concrete repair sequence

This sequence uses the existing programs and roles. It does not require another supervisory agent.

### First: make the current incident impossible to repeat silently

| Action | Responsible executor | Evidence of completion |
|---|---|---|
| Enforce canary validity before further ordinary admissions | FOUNDRY repairs testq; Operations owns incident recovery | Dead colony prevents new affected jobs; recovery requires a valid check |
| Handle pending tests without idling the whole builder | FOUNDRY; Producer supplies ready work | Slow tests coexist with independent offline production; results reconciled afterward |
| Remove retired BENCH routing | FOUNDRY updates all producers; Operations checks routing | Synthetic alarms/findings reach active owners |
| Give findings a live consumer | FOUNDRY implements chosen sorter and bounded judgment duty | New distinct failure gets disposition; repeats retain traceability |
| Repair the known fake-close vulnerability | FOUNDRY; independent reviewer verifies | Fake close rejected before and after restart/replay |
| Define truthful completion and regression state | Producer defines criteria; FOUNDRY enforces; independent reviewer checks | Invalid/stale/unreviewed evidence cannot produce acceptance |

### Second: make failures recoverable

Implement durable incident ownership, progress-sensitive escalation, publication acknowledgment and a minimal recovery path that survives stale ops_watch.

Exercise the seat restart with local edits, a pending remote job and a held resource in separate controlled cases. Keep automatic dead-seat recovery off until these paths are safe; **leaving recovery off during validation is a defensible choice**, provided the absence of autonomous recovery is clearly signalled.

Preflight game permissions and expiry before assigning live work. Do not silently extend the owner’s grant: authorization and machine idleness are separate conditions.

### Third: prove operational usefulness

Instrument accepted output, rework and owner handling effort. Reconcile metric definitions. Measure supervisory output through its downstream consequence:

**Was an issue acknowledged, mitigated, repaired and independently verified? Did production or owner burden improve?**

The process model, additional check-ins and richer health page are lower priority than these missing guarantees. Their implementation should not displace the repairs that make their inputs trustworthy.

## 8. Conditions for calling the workflow operational

The original 48-hour unattended proof remains a good requirement. It should be attempted after the controls above exist and should include deliberate, contained failures. [Design §6]

A credible proof would demonstrate all of the following:

- A waiting test does not stop independent eligible work.
- An invalid environment cannot accumulate ordinary test expenditure.
- Every new critical finding reaches a current owner.
- A claimed incident continues aging until mitigation or verified recovery.
- Exhausted routine alarm capacity does not suppress critical containment.
- Stale ops_watch does not silence the recovery signal.
- Publishing failures recover without lost or duplicated effects.
- A restarted seat resumes durable work without duplicate ownership.
- Current failing evidence prevents misleading acceptance.
- Mandatory duties survive missed clock slots as explicit obligations.
- Permission expiry blocks affected actions cleanly and visibly.
- The owner is not required to discover any of these failures manually.

Until that proof exists, the accurate description is **an experimental production workflow with demonstrated routing, validity and completion-control defects**. Its strongest ideas are worth preserving. Its claimed autonomy should remain limited to what these tests actually demonstrate.