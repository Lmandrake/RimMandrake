**Use two AI roles and two service programs.**

- **Operator:** combines Conductor, Producer, Operations, Innovator, and FOUNDRY.
- **GPT Judge:** combines the interim GPT reviewer, Arbiter, and Auditor.
- **Controller:** owns durable work, priorities, permissions, scheduling, acceptance, and local monitoring.
- **Steve worker:** executes remote tests and independently watches the primary machine.

Keep the owner’s conversation responsive through a foreground Operator context while background work continues. That means **up to three AI contexts while the owner is present: conversation, work, and judgment**. Two role names do not mean only two running contexts.

The important separation is between **making a change and accepting it**. Planning, operations, and building can share one AI role when a program enforces their boundaries.

This is a proposed replacement design. The supplied documents do not establish that its guarantees work today.

The function inventory follows. I use the later response as the latest snapshot: it reports the idle-loop and helper-policy fixes, but their operational proof remains incomplete. “Operating” below means described as operating in the supplied evidence, not independently inspected here.

| Function | Current part | Does it work today? |
|---|---|---|
| Understand owner intent and maintain goals | Interactive Conductor; `CONDUCTOR_GOALS.md` | Operating; interpretation and application depend on the AI. |
| Provide a responsive conversation with the owner | BENCH/Conductor | Operating. The light interface is an explicit owner requirement. |
| Read, combine, and present owner questions and proposals | Conductor; delegated digest; question cards | Operating; questions lack consistent deadlines and blocking-cost visibility. |
| Record rulings, permissions, promises, and goodbye handoff | Conductor; ledger owner-said records | Partial. Recording exists; goodbye restart is unbuilt. |
| Deliver routine briefs, logs, and urgent notifications | Conductor; pulse programs; steward escalations | Partial. Routine delivery exists; some urgent paths depend on failed machinery or inactive destinations. |
| Preserve owner authority over reserved decisions | Delegation policy; grants; cut decisions; innovation probation | Partial. Rules exist; enforcement varies. |
| Make a weekly plan | Producer | Operating as a role duty. Executability and downstream application are incompletely demonstrated. |
| Order daily work and prepare ready work | Producer | Operating; readiness failures still produce bounced attempts. |
| Track progress, replan, detect running dry, and report major slips | Producer; Operations requests; proposed tracker | Partial. Daily/event runs exist; the owner-chosen tracking design is not applied. |
| Define acceptance criteria before raising work | Producer | Role rule, rather than a demonstrated mechanical prerequisite. |
| Limit unfinished work and prioritize it | Producer WIP output; queue ordering | Partial. No demonstrated limit across build, testing, review, and rework. |
| Propose cuts, obtain approval, and apply the approved cuts | Producer → Conductor → owner | Defined workflow; application depends on AI follow-through. |
| Choose which mods and scenarios receive test capacity | Producer; Conductor; testq environment | Broken handoff: decisions do not reach the services; defaults select FlowWorks. |
| Build and repair all assigned mod and workflow components | FOUNDRY | Operating; useful output and completion truth are unreliable. |
| Test a fresh build, repair failures, and repeat validation | FOUNDRY; game harness; testq | Partial. Tools exist; a mandatory complete loop is not enforced. |
| Delegate bounded work and select stronger or cheaper models | Seats; helper hooks; model policy | Operating capability. The later response reports unified helper limits; effective values are not supplied. |
| Produce and judge art, cosmetics, and provisional tuning | FOUNDRY; helpers/judges; art programs | Operating capability described; acceptance and resource integration remain partial. |
| Claim work, maintain ownership, and recover expired claims | Ledger; leases; `rimflow next` | Operating. Renewed ownership does not prove progress. |
| Wake an available builder and detect stalled delivery | Dispatcher; doorbell | Operating but imperfect. The later response reports revised retries; live proof is still owed. |
| Keep working usefully while tests or permissions are pending | FOUNDRY; Dispatcher | Reported fixed in instructions/re-ring logic; end-to-end proof remains owed. |
| Refresh context and recover interrupted workers | `seat_restart`; seat loop; restart requests | Unproved. The documents disagree on live/dry state; the later response says dry. |
| Protect the owner’s game and serialize live-game actions | Idle probe; bridge lock; companion grant | Partial. Locks and refusals exist; grant readiness is checked too late. |
| Submit, prioritize, execute, and reconcile remote tests | testq; SteveDesktop runner | Operating. Admission and recovery semantics have known defects. |
| Return remote results and ingest them into work records | Outbox; testq; ingest | Operating; exact-build association and delivery guarantees are incomplete. |
| Detect invalid environments, quarantine them, and prove recovery | Canary checks; testq; steward | Broken in important cases: one red retries by design; RUNNING ends incidents. |
| Automatically supply regression work and full-suite coverage | Filler; nightly sweep | Operating; allocation favors activity and old chains rather than demonstrated production need. |
| Keep Steve productively assigned and recover lane faults | Steward; ops_watch; headless BENCH incident run | Partial. Fault handling exists, but some destinations are obsolete and recovery means the wrong thing. |
| Preserve an optional second local test lane | Archmagi support; bridge lock | Built but OFF in the described service configuration. |
| Fold repeated findings without losing their occurrences | Proposed findings sorter | Planned, not operating. |
| Judge new findings and assign actionable failures | Intended FOUNDRY curation duty | No dependable live consumer; findings accumulate. |
| Retire resolved failure classes and reopen recurrences | Proposed standing-failures table | Planned; requires correct build/scenario/environment scope. |
| Track criterion evidence and invalidate contradicted assurance | Verify state machine | Broken: stale-build passes can count; current failures do not demote validation. |
| Record truthful completion, including legitimate no-code work | `close`; `implemented`; verify ladder | Broken: implicit HEAD, unmet criteria allowed, no enforceable independent acceptance. |
| Independently judge each claimed finished component | Interim GPT reviewer; advisory Arbiter | GPT consultation is a maker-invoked ritual; enforcement is absent. |
| Screen every close for mechanically detectable defects | Auditor prescreen; proposed hard-flag filer | Partial. Prescreen exists; automatic disposition is incomplete and a known gate defect remains open. |
| Independently recheck disputed check/environment judgments | Auditor; interim reviewer | Defined, but delivery, timing, and binding effects are incomplete. |
| Sample accepted work and assess reviewer accuracy | Auditor | Operating role duty; limited evidence, capacity constraints, and misplaced verdict files weaken it. |
| Turn defects and escapes into repaired, verified regressions | Arbiter/Auditor → builder tickets | Partial. Filing does not guarantee repair or removal of exposure. |
| Curate lessons into useful memory, rules, and skills | Auditor weekly fold; lessons corpus | Failing as a queue: 626 arrivals versus two deletions in the reported week. |
| Trim documentation, inspect codebase health, and improve rules | Arbiter weekly duty; Auditor; health programs | Mixed: some instrumentation operates; some duties are designed or unverified. |
| Propose better workflows, agent arrangements, and game concepts | Innovator | Operating proposal capability; owner authorization remains required. |
| Run bounded innovation trials and expire/revert them | Innovator; proposed watchdog | OFF/unbuilt. Trials lack their required expiry mechanism. |
| Measure accounts, consumption, runway, and available capacity | ops_watch; account capture/usage programs | Operating, with estimates and unknowns; stale readings can block all roles. |
| Recommend account selection while respecting account permission | `account_pick` | Operating recommendations; no automatic switching and currently no blocking holds. |
| Enforce shared concurrency, runtime, memory, and spending limits | Allocator; helper hooks; role launcher; OS slices | Partial. Helper fix reported; token allowances are not hard runtime ceilings. |
| Observe disk, memory, game performance, services, timers, and production flow | ops_watch; telemetry; memory/TPS/health programs | Operating instruments; collection does not guarantee corrective action. |
| Own incidents through acknowledgment, containment, repair, and recovery | Operations; steward; Dispatcher alarms | Incomplete. Claims, caps, suppression, and incorrect recovery conditions can stop effective escalation. |
| Detect failure of the monitoring and scheduling machinery | Dead-man; timer guards; steward-watch | Partial. Important paths share the failed delivery dependencies. |
| Schedule duties, supervise processes, pause activity, and retain owed work | Dispatcher; role launcher; systemd | Partial. Process supervision exists; missed slots/events can lose obligations. |
| Publish code/state and mirror the owner’s working copy | `publish`; git; mirror timer | Operating with observed failures; delivery acknowledgment is insufficient. |
| Preserve artifacts and telemetry; store objects; safely reclaim scratch | Telemetry/object-store/reaper programs | Operating as described; protection of referenced evidence is not proved. |
| Run unattended selftests and detect regressions in the machinery | Nightly selftests; codebase-health programs | Operating capability; integrated guarantees remain unproved. |
| Measure owner interventions, failure signals, and attention burden | Proposed health/message tagging | Mostly unmeasured; tagging and gold-baseline validation are planned. |
| Measure accepted production, rework, waiting, and useful test contribution | ops_watch; proposed output tracing/health page | Partial or absent. Accepted production lacks an adequate event. |
| Compare v3 with v2 on quality, cost, production, and owner burden | `v3_vs_v2`; Operations; Auditor | Scorer OFF; missing inputs prevent a defensible verdict. |
| Fit separate v2/v3 process models and refresh the v3 fit daily | Proposed process-model program | Designed/ready, not operating. |
| Publish a daily health assessment and independently challenge it | Proposed health page; Operations; Auditor | Designed, not operating. |
| Introduce outside faults, conceal live plants, reveal them, and correct statistics | Proposed drill machinery | Designed and explicitly OFF. |
| Review the finished integrated system with GPT | No systematic release gate shown | Owed by the current request; not demonstrated in v3. |
| Keep routing, authority, configuration, and migrations consistent | Cutover program; schedule; charters; overrides | Partial. Historical migration ran; future producers and effective configuration still disagree. |

Every row needs a home in the replacement. Removing a role does not remove its rows.

The system should enforce these **eight invariants**.

1. **Acceptance requires the actual result.** An accepted component has an explicit artifact identity, versioned criteria, valid passing evidence for every required criterion, and a GPT judgment from a non-maker context. Applicable unresolved failures block acceptance. No implicit HEAD, ledger-only substitute for a product change, or maker override. Legitimate no-code work has a named deliverable and appropriate evidence.

2. **Fresh work stays the current focus through validation and repair.** Building, testing, review, and rework all count as unfinished work. Normally there is one component in flight. One additional component is allowed only while the focus is genuinely blocked on an external dependency and no useful focus action remains. There can never be a third unfinished component.

3. **Every obligation has executable ownership until its outcome is verified.** Findings, incidents, review requests, plan failures, and mandatory duties persist until disposition. Each has an owner, next action, deadline, and escalation destination. A claim acknowledges receipt; it neither proves progress nor stops the impact clock. An available worker must take an eligible action or record a checkable reason it cannot.

4. **Test execution must produce usable, relevant evidence.** Every job identifies its build, scenario, fixture, environment, and purpose. An invalid canary stops ordinary admissions for that environment immediately. Recovery requires a valid recovery check. CPU time and RUNNING never establish usefulness or recovery.

5. **Actions stay inside current authority and resource ownership.** Live-game permission, owner presence, locks, account permissions, and execution capacity are checked at admission and at the affected action. Unknown permission blocks that action. Recovery and unrelated offline work remain possible. Only the owner can expand reserved authority.

6. **Interruptions and redelivery cannot lose work or duplicate its effects.** Jobs and results have durable identities. Replacement workers are fenced from old attempts; delivery is acknowledged; repeated ingestion has one effect. Publication failure cannot erase obligations. Referenced evidence survives cleanup.

7. **Monitoring failure cannot silence recovery.** Missing measurements create a recovery obligation; they do not prohibit its execution. Steve detects loss of the primary Controller and sends an owner-visible notification without using the primary machine.

8. **The system must expose whether it is helping.** Daily health and comparison obligations remain owed until produced or explicitly marked unavailable. Accepted output, owner interventions, rework, waiting, test contribution, and overhead have frozen definitions. Missing evidence cannot become “healthy,” “superior,” or a reason to postpone the decision indefinitely.

A WIP limit can deliberately leave a worker idle when both permitted components are blocked. That is an explicit capacity decision. It must not conceal an unexplained wait while eligible work within the limit exists.

Here is how the two AI roles cover the inventory.

| Merge | Result | Independence or capability lost | Replacement or reason it is acceptable |
|---|---|---|---|
| Conductor + Producer + Operations + Innovator + FOUNDRY | **Operator** | Separate managerial opinions; a planner who is distinct from the builder; separate cost-aware supervision | The Controller enforces WIP, authority, priorities, budgets, and acceptance. GPT independently examines outputs and system performance. Separate management personalities are unnecessary for one owner and one builder. |
| Arbiter + Auditor + interim reviewer | **GPT Judge** | A permanently separate AI auditor of the first reviewer | Rechecks use a fresh context that makes its initial judgment without seeing the earlier verdict. Calibration measures false acceptance and false rejection. Correlated GPT errors remain a real risk. |
| Scheduled Conductor + interactive BENCH identity | **Owner conversation with the Operator** | A separate chief-of-staff session owning its own operational state | The conversation reads the same durable state and files background work. It stays light and responsive. An open window never suppresses owed background duties. |
| Specialized helper seats and role-specific helper policies | **Optional bounded Operator invocations** | Default parallelism and separate helper identities | Keep delegation/model escalation available, but OFF initially. Any later helper uses the same global capacity reservation and cannot accept work. |

The Operator can know costs. **The GPT Judge does not receive cost pressure as part of its acceptance decision.** Resource limits can postpone a review; they cannot lower its bar.

The foreground conversation answers the owner, reads outstanding owner matters first, records decisions, and submits work. Long builds, investigations, and planning exercises run in the background. Goodbye records promises and a resumable checkpoint. There is no autonomous BENCH work queue.

The GPT Judge has three kinds of assignment under one charter:

- Judge a candidate component.
- Independently recheck selected accepted work, judgments, and health claims.
- Judge an integrated release of RimFlow or a mod.

These are assignments, not three scheduled AI roles.

“Blind” means the Judge receives the requirements, immutable artifact, raw evidence, and relevant limitations, without the maker’s self-grade or persuasive completion narrative. It can enumerate evidence and select additional checks itself. **Known failures are never hidden to manufacture blindness.**

For a recheck, the previous verdict stays hidden until the new initial assessment is recorded. The Judge then reconciles disagreements before disposition.

The two service programs have these responsibilities.

| Program | Responsibilities |
|---|---|
| **Controller, on the primary machine** | Durable work and incident state; dispatch; leases and fencing; AI process supervision; acceptance gate; testq’s local queue/admission/ingestion; monitoring collection; findings fold; planning checks; daily health/comparison/model jobs; artifact delivery; briefs; maintenance scheduling. |
| **Steve worker, on SteveDesktop** | Receive and acknowledge immutable jobs; verify artifact/environment identities; run bounded test processes; retain results until acknowledged; perform recovery checks; independently watch the primary Controller and notify the owner directly when it disappears. |

Both use the existing OS supervisor. AI sessions, game processes, fits, renders, and maintenance commands are bounded child jobs. **This is two maintained services, not a claim that the computer runs only two executables.**

Reuse the existing harnesses, collectors, and useful testq code. Consolidate their control state and scheduling. Merely launching the existing independent timers from a new wrapper would leave most of the complexity intact.

The Controller needs one authoritative transactional work store, retaining the append-only history and existing CLI concepts. Code travels through git. **Queue delivery must not depend on successfully committing and pushing a dirty clone.** Git exports and mirrors become acknowledged delivery jobs.

The Operator can edit its worktree and propose changes to the workflow. OS permissions prevent it from directly editing live acceptance records, Judge records, or the installed Controller. Changes to those components go through the same reviewed release path.

This creates a larger Controller, which is a risk, but removes several independent queues, schedules, freshness gates, and handoffs.

The build loop should be explicit:

1. **Select one component and freeze its contract.** Record its criteria, required scenarios, artifact paths, permissions, and test allocation before implementation. A discovered bad criterion becomes a visible contract revision; the maker cannot quietly weaken it.

2. **Build and test it.** Compile, run targeted checks, reproduce the relevant defect, and run the required integration/game scenarios against the exact candidate.

3. **Repair failures and repeat the required checks.** Retain failed results. A deterministic failure calls for a repair, rather than repeated unchanged runs hoping for green. Unexplained intermittent failures remain unresolved. Repeated testing uses a declared acceptance rule.

4. **Have the Controller request GPT review.** The maker does not decide whether consultation occurs. The Judge receives the candidate and evidence directly and can request additional tests.

5. **Return rejection to the same current focus.** Fix, retest, and obtain a fresh GPT assessment of the revised candidate. No new breadth displaces that repair.

6. **Accept mechanically.** The Controller verifies the artifact, criteria, evidence, outstanding failures, Judge receipt, and any required owner validation. Only then does it append the acceptance event.

An applicable later failure removes the affected current assurance and creates blocking regression work. Historical passes remain recorded, but cannot keep the current summary green.

Repeated unsuccessful repair consumes a bounded work allowance, then produces an owned diagnosis/blocking obligation. It never produces acceptance, unlimited blind retries, or an excuse to quietly abandon the component.

**Every finished component goes to GPT.** That includes workflow code, prompts, configuration, acceptance machinery, test infrastructure, and product components. Routine status messages and review receipts are records, rather than newly built components requiring recursive reviews.

**The assembled system also goes to GPT.** Component approval cannot substitute for an integrated review of the release manifest, installed configuration, actual handoffs, recovery behavior, and end-to-end evidence. A revised workflow release needs renewed system approval. Each assembled mod release likewise needs integration judgment.

The Controller enforces current focus as follows:

- Continue the focus’s runnable tests, repairs, evidence work, and review first.
- If a remote job or owner decision genuinely blocks all further focus work, record that dependency and permit one small independent component.
- On the dependency’s completion, return to the original focus at the next safe checkpoint.
- Count both components through testing, review, and rework. Never start a third.
- A defect in acceptance or containment machinery suspends reliance on the affected machinery and becomes the focus.

This preserves useful work during long waits without turning every waiting test into permission to start several more products.

The remaining functions fit into that architecture without new roles or services:

| Function | Minimal implementation |
|---|---|
| **Producer cadence** | Daily plan at 09:00. At 12:00 and 18:00, the Controller checks measured progress and invokes the Operator only for a meaningful deviation or dry queue. Major slips trigger immediately. Unsatisfied requests persist; no one-event-per-day disposal rule. |
| **Planning progress** | Distinguish relevant product commits, valid no-code deliverables, and accepted output. A very short completion is a suspicion flag, not an automatic rejection. |
| **Cuts and owner decisions** | One decision record contains exact proposed action, age, blocked work, and reserved authority. No response does not grant permission. Applied cuts must match the recorded decision. |
| **Test allocation** | The plan contains a versioned allocation. The worker acknowledges the applied version. Required focus proof comes first, then repair verification and useful regression coverage. |
| **Automatic test filling** | Preserve it as coverage-based selection. Queue useful missing or expired assurance. When coverage is satisfied, Steve may legitimately idle. Eliminate the demand to fill CPU time. |
| **Findings fold** | Run immediately after ingestion. Preserve every occurrence, group likely repeats with build/scenario/environment scope, and create one owned obligation for each new class. Route environment faults to recovery work. Flag done-but-failing contradictions immediately. |
| **Failure retirement** | Comparable passing evidence can establish resolution; unrelated pass streaks cannot. A recurrence reopens the obligation. |
| **Lessons and skills** | Keep searchable source records. Consolidate duplicates; promote important novel lessons immediately and recurring classes into tested rules or skills. The weekly Judge assignment checks new and older candidates. Do not make every raw lesson file a separate debt. |
| **Daily health** | Controller generates the factual page and traces. Operator explains exceptions and actions in the daily pass. Judge independently samples the claims and their consequences. |
| **Owner-message tagging** | Classify new messages within existing work, using the approved gold baseline and measured classification accuracy. No separate hourly Haiku role. Report estimated attention measures honestly. |
| **v3 versus v2** | One comparison module in the daily batch, using frozen definitions, comparable work classes, quality checks, and explicit missing data. Preserve the formal settled-week superiority rule; remove its separate timer. |
| **Process model** | One bounded daily computation: v2 fitted only to the specified historical v2 data; v3 updated from ongoing v3 data. Preserve shared-core/recounted comparisons, held-out validation, and visible stale/failed fits. Owner-habit changes inform the summary, not direct alarms. |
| **Innovation** | Operator brings proposals in the weekly planning pass or when a concrete opportunity arises. Preserve owner approval for new concepts and trials. Trial activation requires an expiry and proved rollback. |
| **Machine maintenance** | Collect health on the Controller’s reconciliation pass. Run mirroring, storage, cleanup, selftests, and art jobs as bounded obligations with deadlines and protected evidence references. |
| **Seat restart** | Delete the interactive-seat lifecycle. Work runs in bounded processes with durable checkpoints. After termination is confirmed, fence the old attempt and resume in a fresh context. Remote tests continue under durable job identities. |
| **Outside plants** | Retain an owner-authorized external injection harness and sealed register. Only the permitted owner-facing context sees live plants; evaluators see ended plants after initial assessment. Reveal, cleanup, and corrected statistics are mandatory. Keep automatic planting OFF initially. |

Retain **one effective policy document and one PAUSE control**. Policy contains the actual concurrency, resource, permission, and scheduling rules. Overrides have scope and expiry. Prompts reference that policy instead of repeating numbers.

PAUSE stops ordinary admissions. Monitoring, result preservation, safe termination, and urgent owner notification continue.

A normal day becomes much shorter:

| Time/event | What happens |
|---|---|
| Continuously | Controller handles results, obligations, dispatch, and containment. Steve executes eligible tests and watches the primary machine. Each service reconciles at least once a minute. |
| 09:00 daily bundle | Produce measurements, health page, comparison, and—when enabled—the daily fit. Operator makes or updates the plan and resolves new exceptions. Judge performs the daily independent sample. |
| 12:00 / 18:00 | Cheap progress checks. Invoke the Operator only when action is needed. |
| Component becomes test-ready | Tests run immediately. Failures stay with the focus. |
| Component passes maker validation | Controller requests GPT judgment immediately; there is no 11:00/17:00 wait. |
| Owner arrives | Foreground Operator answers immediately from current state; background work continues. |
| Monday’s daily bundle | Add weekly planning, memory/rule curation, reviewer calibration, and improvement proposals. |
| Integrated release ready | Run system validation and fresh GPT system review before release acceptance. |
| Owner says goodbye | Record decisions, promises, and checkpoint. No special restart ceremony. |

The recurring schedule is one reconciliation pulse, one daily bundle, and two gated progress checkpoints. Weekly work extends the daily bundle. Existing fixed-time maintenance becomes deadline-based work; there is no independent sweep, audit, innovation, or restart clock.

The handoff list reduces to five contracts:

1. **Owner ↔ Operator:** intent, decisions, explanations, and questions.
2. **Operator ↔ Controller:** proposed actions, durable work, checkpoints, and observed state.
3. **Controller ↔ Steve:** immutable jobs, acknowledgments, results, and recovery evidence.
4. **Controller ↔ GPT Judge:** candidate/evidence, additional checks, and signed judgment.
5. **Steve → owner:** independent notification when the primary service disappears.

Plans, operations requests, findings, audit defects, and lessons become different records in the same owned workflow. They no longer travel through a chain of named AI offices.

I would delete outright:

- Separate Producer, Operations, Innovator, Arbiter, and Auditor launches, schedules, budgets, logs, and OFF files.
- Autonomous BENCH identity and every producer that routes work to it.
- Doorbell arming, rings, wake counters, wake cooldowns, and interactive seat-restart machinery.
- Advisory duplicate verdict streams and the maker-invoked interim-review ritual.
- Clock-slot expiry and short event lookbacks for obligations that remain owed.
- The universal fresh-ops gate.
- RUNNING-as-recovery and indefinitely paused incident clocks.
- Fixed automatic retries for invalid canaries.
- Oldest-chain filler and duplicate sweeps whose purpose is simply utilization.
- The raw-lessons fold quota and expectation that each source file requires an individual fold.
- Helper borrowing/payback, competing limits, and quota-burning modes.
- Duplicated schedule and authority facts in role prose.
- Git publication as the transport for operational work.
- Process-commit share as an automatic freeze rule. Keep measuring it, but prioritize acceptance defects by exposure and judge improvement through actual production benefit.

I would keep these **OFF until the core passes its failure tests and an unattended proving period**:

- Extra autonomous helpers and the Archmagi lane.
- Automatic fault plants and role-disable experiments.
- Innovation trials without demonstrated expiry and rollback.
- Automatic account switching or model-driven staffing/throttling.
- Automatic permission renewal; explicit consent remains required.
- Broad cleanup or service-repair actions beyond tested, narrow operations.
- The daily process fit until its inputs and forward validation are trustworthy.

The daily fit remains part of the finished design; deferring activation does not delete its function. Measurement needed to judge the system starts immediately. A model is not a prerequisite for counting accepted output or detecting lost work.

Set the first keep/kill checkpoint **14 days after integrated acceptance**, without moving it because measurements are missing. That is an early operational decision. A formal claim of superiority still requires the stipulated comparable settled weeks.

The minimal design has risks. The following forced failures should be release tests, with expected outcomes recorded before execution.

| Invariant / principal risk | Forced failure | Required proof |
|---|---|---|
| **1 — False acceptance; GPT can also be wrong** | Attempt completion with missing review, unrelated SHA, stale-build pass, partial result, invalid canary, and an unresolved current failure. Include a plausible defective candidate. | Each invalid acceptance is refused. A genuine candidate succeeds. Blind calibration records false accepts and rejects; a faulty Judge cannot override mechanical evidence checks. |
| **2 — Operator goes wide or waits unnecessarily** | Hold two slow tests while a small independent offline item is ready; then deliver a focus failure. Attempt a third component. | One bounded alternate starts; the third is refused; the original focus resumes on the result. Repairs precede further breadth. |
| **3 — Combined Operator neglects duties or manufactures progress** | Generate a finding, disk alarm, reviewer defect, plan slip, and owner request. Claim an incident and renew its lease without progress. Restore after a seven-hour outage. | All obligations retain owners and age. Impact escalation continues after claim. Nothing disappears through a cap, cursor, old destination, or missed slot. |
| **4 — Steve stays busy producing invalid evidence** | Supply a dead colony and pending ordinary jobs; attempt manual resume. Also request a different mod from the old default. | First invalidity contains expenditure. Resume requires proved recovery. Applied allocation matches the plan. Required green regression evidence counts as assurance. |
| **5 — Authority or capacity races** | Expire a grant, have the owner return during live work, submit simultaneous capacity requests, and supply unknown account permission. | Affected actions refuse or yield safely; reservations cannot exceed the effective limit; unrelated recovery remains available. No grant silently renews. |
| **6 — Restart, delivery, or cleanup corrupts work** | Kill a worker with local edits, a held lock, and a pending remote job in separate cases. Duplicate results; break git publication; run cleanup. Replay across midnight and the repeated DST hour. | Old attempts cannot mutate accepted state; jobs reconcile once; edits/evidence remain recoverable; obligations survive; daily work is neither duplicated nor lost. |
| **7 — Consolidated Controller becomes the single point of silence** | Stop collection, then the Controller, then the primary machine. Hang a game process on Steve. | Local recovery works without fresh metrics. Steve’s owner notification bypasses the primary. A hung game does not stop Steve’s watchdog. |
| **8 — Reports flatter the system; learning loses important exceptions** | Remove metric inputs, mislabel owner messages, submit many duplicate lessons plus one unique severe lesson, and provide a poor model fit. | Unknown stays visible; tagging error is measured; the severe lesson receives disposition; the fit is rejected; missing data cannot produce superiority or postpone the checkpoint. |

Two additional limits remain explicit. Fresh GPT contexts reduce contamination but do not eliminate shared model blind spots; use representative blind calibration and independent executable checks. The two-machine design also cannot notify reliably if both machines and their notification connectivity fail together. An external heartbeat service would be the next addition only if that coverage is required.

Build this **one proved slice at a time**: acceptance and durable ownership first; remote testing and recovery second; planning, findings, and measurement next. Each slice goes through repeated validation and GPT review before the next expands the system. Then prove the assembled workflow under controlled failures and an unattended run.

That gives the owner depth before breadth—and makes the workflow itself the first product required to meet that standard.