# Teardown: GPT's attack on the synthesis, and what changed

One call, `gpt-6.1-sol` at high effort, 2026-11-22 about 4:37 PM PST. It saw `context_pack.md` with its eight files,
`round0.md`, the eight `viewpoints/*.md` files and the draft `plan.md` (430,916 characters). The prompt asked for
misrepresentation, weak points, omissions, a check of the new void measurement, the owner's decisions, the top
screen, and three ranked required changes. The draft was not committed; GPT quotes each part that it attacks. There is no
third pass.

## What the revision took, and what it did not

| GPT's point | judgement | what changed in `plan.md` |
|---|---|---|
| The draft made a full history table a gate before mod work; repair-current-runtime had withdrawn exactly that ("Neither mod should wait for a complete retrospective") | Correct. This was the most important error | Act 1 is now: find each mod's next legal act and do it. The history table is built beside the work and gates nothing |
| "Before any new build" was claimed as all eight advocates' view; rebuild-small-core still wants a separate bounded replacement test now | Correct | §2 states the convergence without it; the preventive-test disagreement stays in §5 |
| "Most of the duplication is migrations left half done" turned GPT's `[guess ~70%]` into a fact | Correct | The top screen now says "much of", tagged as GPT's guess |
| "Every advocate withdrew its cost forecast" is false: replace-durable-slice kept 25 to 43 M as a qualified allowance; freeze-strangle-core kept a 60 M outer stop | Correct | §2 says so |
| The recurrence threshold was kept after repair-current-runtime changed its meaning | Correct | A recurrence now stops and reopens that one repair; it does not falsify the plan |
| "No rebuild: Kept" overstates the rebuild advocate's concession | Correct | Row now reads: no factory-wide cut-over; a separate bounded replacement test is still argued (§5) |
| "The other seven: no cap" overstates; several accept a reduction when traces show contention | Correct | §5 restated |
| §8 said the debate did not test study delivery; consolidate-facts-only rejected "no tickets before the owner reacts", and the first review addressed delivery | Correct | The plan drops "no tickets before you react" (known repairs keep the same-run rule) and the limit line is restated |
| The branch table mixes symptoms, causes and authority; one class per stop hides chains; "ready" as an entry condition hides machinery that prevents readiness; a release is not automatically good judgement; account stops are not automatically contention; a lost run does not automatically earn an outside runtime | Correct on each | The table allows a chain of classes; pipeline-caused readiness blocks count; a delegated act is classed "necessary" or "avoidable rescue" row by row; contention needs a named competing obligation; the smallest repair always goes first |
| The freeze forbids an "engine build" while a branch allows an outside-runtime comparison | Correct | One explicit, bounded exception, outside the live pipeline, never a second live controller |
| Dropped safeguards: independent expected answers; reconciliation before any handover; a legal form of hand routing; an inconclusive outcome | Correct | All four are now in §4 |
| The void count shows stop reasons, not recovery correctness, cost, rate or whether fewer helpers would reduce account stops; the raw lines were not supplied | Correct | The claim is cut down to the stop reasons. The raw listing is now committed (`evidence/voids_2026-11-22.txt`). The three lifecycle leads in it (two relaunches onto a reclaimed clone, one launch systemd never answered) become the first incidents to inspect |
| Two owner decisions is not evidence-based: the first bundles delegated work; the second is an admission policy the Conductor can run | Mostly correct | The fortnight and any cap on unfinished agent work are the Conductor's to enact. One decision is left, because it turns on the project's purpose, which is his: whether new pipeline experiments wait outside the live pipeline until 12-06 |
| Rewrite the top screen; put executing the next legal act first | Correct | Rewritten on GPT's suggested lines, in this project's plain style |
| Repeated requests may be retries; group them by concern before any request cap | Correct | No request cap is proposed |

Not taken: GPT's suggestion that a missing operating decision (when hand routing would break the permanent-fix rule)
should be settled as a new exception. The revision avoids the conflict instead: the Conductor routes by hand only
with acts it may already do, and a pipeline defect found that way still gets its permanent fix under the existing
rule. No rule changes.

## GPT's answer, verbatim

The synthesis is not ready to become the operating plan. It turns partial agreement into unanimity, restores a delay that an advocate explicitly withdrew, and uses counts of stop reasons to answer questions about recovery and workload that those counts cannot answer.

Its strongest practical correction should be: **establish each mod’s next legal act and execute it promptly; investigate the wider history alongside that work.**

**1. The synthesis misrepresents several Round 2 positions.**

- **It invents agreement that reconstruction must precede building.**

  `plan.md` §2 says all eight accept:

  > “reconstruct the advancing mods' next legal acts and what blocks them, from existing records, before any new build”

  But repair-current-runtime’s Round 2 concession says:

  > “My days 1–4 were too sequential. Reconstruct each mod’s immediate next act first; execute it as soon as readiness permits. Continue deeper investigation alongside useful work. Neither mod should wait for a complete retrospective.”

  This matters operationally. The synthesis restores the sequence the advocate rejected.

- **It presents the rebuild advocate as accepting an incident prerequisite that it still disputes.**

  The same claimed convergence includes:

  > “start a replacement only for a reproduced, current failure”

  Rebuild-small-core’s revised position instead says:

  > “keep existing mod work operating and test a bounded replacement core separately.”

  Its final question proposes reproducing an interruption at the current launch/result/stage boundary, including an effect completed before acknowledgement. It does not require a previously observed production incident before that investigation.

  The synthesis may choose incident-first replacement. It cannot call that unanimous agreement or confuse replacement construction with preventive testing.

- **It converts a hypothesis about duplication into a measured diagnosis.**

  The top screen says:

  > “Most of the duplication is migrations left half done, not new copies.”

  Round 0 actually says:

  > “incomplete cutovers explain much of the observed duplication. … `[guess ~70%]`”

  No supplied census establishes “most,” and the investigation did not establish the origin of every duplicate. The synthesis’s own §3 preserves the uncertainty; its top screen removes it.

- **It falsely says every advocate withdrew its cost forecast.**

  `plan.md` §2:

  > “Every advocate withdrew its own cost forecast as uncalibrated.”

  Replace-durable-slice’s Round 2:

  > “My 25–43 M detached-run estimate remains an uncalibrated planning allowance, not a comparative cost advantage.”

  That allowance was qualified, not withdrawn. Freeze-strangle-core also retained its proposed 60 M outer stop. Neither figure establishes affordability, but the record must distinguish withdrawal from qualification.

- **It restores a recurrence threshold after the advocate changed its meaning.**

  `plan.md` §4:

  > “a cause called repaired needs more than one further manual recovery on either mod.”

  Repair-current-runtime’s Round 2:

  > “A verified recurrence disproves the particular repair’s claimed completeness; it does not alone establish that the whole runtime needs replacement.”

  The synthesis retains the older threshold and places it under “How the plan could be shown wrong.” One verified recurrence already challenges that repair. It does not establish that the whole strategy failed.

- **“No rebuild” overstates the rebuild advocate’s concession.**

  The synthesis says:

  > “No rebuild | Kept”

  Its justification is withdrawal of the whole-core cutover and allocation. But the advocate retained:

  > “test a bounded replacement core separately”

  What converged was opposition to a scheduled factory-wide cutover, not rejection of every bounded replacement experiment.

- **It overstates the rejection of a helper cap.**

  `plan.md` §5:

  > “The other seven: no cap whose need is unmeasured.”

  Repair-current-runtime’s actual combined position permits:

  > “reduce concurrency when traces demonstrate contention.”

  Several advocates reject mandatory blanket serialization while accepting conditional reductions. That is narrower than seven advocates rejecting any unmeasured default setting.

- **Its last limit understates scrutiny of study delivery.**

  `plan.md` §8 says:

  > “No GPT advocate argued the study's §8 … The debate did not test it.”

  Consolidate-facts-only explicitly addressed one central provision:

  > “‘No tickets before the owner reacts to a study’ | Do not introduce this restriction. Known defects retain the existing same-run repair rule.”

  The first GPT review also challenged delivery directly. A defensible statement is that the debate did not conduct a dedicated evaluation of the complete proposed delivery mechanism.

**2. The blocking table is useful as a working record; making it a prerequisite is the likely failure.**

The plan asks one helper to reconstruct **every stop, hand act and void since November 13**, classify them, establish start and end times, attach spend, and commit the table. It then schedules reading the table and taking branches the following day.

The evidence does not establish that this reconstruction is cheap or complete. The original study could not measure elapsed time or spend per stage move. The sweep did not open the tick readings. Conductor accounting is absent. Existing records are sources to investigate, not proof that the required history can be recovered.

An exhaustive retrospective could consume the opening days while acceptance work waits. `[guess ~75%]` That is precisely the risk repair-current-runtime withdrew in Round 2.

The table should therefore begin with **the current next act for each mod**, not the complete history. Historical gaps remain UNMEASURED and do not prevent an otherwise authorized act.

The branch design also needs correction:

- **It mixes symptoms, causes and authority.** A lost result may follow an account stop; a Conductor release may rescue slow dispatch; a wrong check may itself be pipeline machinery. Assigning exactly one class can conceal that chain.
- **“Ready” cannot be an entry requirement for measuring pipeline obstruction.** Otherwise machinery that prevents readiness disappears from the assessment. Repair-current-runtime explicitly required pipeline-caused readiness blocks to count.
- **A release or clear is not automatically useful judgment.** The rules establish who may perform it. They do not establish whether this particular act was necessary stewardship or avoidable rescue.
- **Account pressure is not automatically contention from other admitted work.** The latter requires identifying the competing obligation and occupied resource.
- **Every reproduced lost or doubled run does not automatically earn an outside-runtime build.** The smallest adequate repair may resolve it. The advocates retained comparison as a conditional investment, not an obligatory second implementation.

The plan also contradicts itself. Its branch table permits an outside-runtime comparison, while its freeze says no “engine build” and defines success as “Nothing in that list lands.” It needs an explicit, bounded exception.

“A repair goes into the home that already exists” is a useful default. It cannot prohibit reconsidering a demonstrated defect spanning competing writers or result/stage stores. Several Round 2 concessions expressly kept that possibility open.

**3. The synthesis drops safeguards that matter more than its schedule.**

The strongest omissions are:

- **Independent expected answers.** The scheduled caller audit says to “compare old and new answers.” Round 0 and multiple advocates insist that old behavior is evidence, not correctness. Each difference must be judged against the intended rule and captured state.
- **Reconciliation before handover and rollback.** The synthesis retains “never two live controllers,” but drops explicit treatment of in-flight workers, stale authority and effects completed before acknowledgement. Any replacement branch needs these conditions.
- **A legal supervised contingency.** The plan says the Conductor may route by hand until dispatch is repaired. Supervised-mod-sprint and controlled-live-research explicitly conceded that some such work requires a temporary exception to the permanent-fix rule. The synthesis neither states that exception nor confines supervision to acts already permitted.
- **A complete return obligation.** The owner’s original complaint included studies not returning. The synthesis promises delivery for this fortnight, but restores “no tickets before you react” without separating completed requested work, returned findings, optional acknowledgement and implementation. It leaves known repairs vulnerable to an unnecessary owner wait.
- **An inconclusive outcome.** Limited late-stage work cannot establish the best architecture for Designer admission, building and blind-review cycles. The December 6 page must be allowed to say that the broader question remains unanswered.
- **Repeated requests may be retries.** This survives as a caveat, but loses force when the synthesis recommends a request cap without first grouping requests by the unresolved concern they repeat.

The principal disagreement resolved without adequate evidence is **whether to test the effect-before-acknowledgement boundary now**. Rebuild-small-core argues for that test even without a previously reproduced incident. The synthesis chooses against it partly by citing void counts. Those counts do not establish the safety of that boundary.

There is also a contradiction between the top screen’s “Nothing else gets built” and §4’s promised “bounded replacement study” after a threshold. The plan needs a clear rule for reopening scope, not simultaneous prohibitions and promises.

**4. The void measurement supports a narrow description, not the causal conclusion.**

Accepting the synthesis’s classification as reported, it establishes:

> Of 36 listed void entries, 15 named owner-ordered stops, 14 named account-level stops or switches, two named Conductor stops, and five were grouped as system failures or never started.

The raw entries are not supplied. The classification therefore cannot be independently checked from this pack. The plan also needs to explain which entry is no longer standing and whether its totals count entries, distinct runs or distinct incidents.

“Crash recovery is not where most voids come from” is defensible **only as a description of the assigned stop reasons in this list**.

It does **not** show:

- How much blocked time, weighted-token loss or recovery work each category caused.
- Whether owner-, Conductor- or account-stopped workers recovered correctly afterward.
- Whether deliberate stops exposed stale results, stranded work, lost transitions or duplicate effects.
- Whether recovery failures appear outside the void list.
- The failure rate, because total runs and exposure to each condition are not given.
- Whether fewer concurrent helpers would reduce account stops.

“Account pressure is a large source” should become:

> “Fourteen entries name account-level stops or switches; their causes and operational cost are not yet established.”

Account switching may be normal policy, a response to accumulated usage, interference from other admitted work, or faulty accounting. This measurement does not distinguish those explanations.

It also contains **concrete lifecycle leads** that the synthesis minimizes: two relaunches named clones already reclaimed by the pool, and one launch received no answer from systemd. These warrant inspecting effects and records before classifying the problem as absent or irrelevant. They do not, by themselves, establish that an outside runtime is needed.

Most importantly, **the reason a worker stopped and the correctness of recovery after it stopped are different measurements**.

**5. Two is not an evidence-based number of owner decisions.**

The first—“Take this fortnight as written”—bundles ordinary delegated work with unresolved policy choices. The supplied rules already let the Conductor prioritize authorized mods, investigate blockers, repair known faults and defer discretionary work. None is among the owner’s five reserved acts.

There is evidence of real tradeoffs: experimental work is part of the project’s purpose, and a restriction may delay it. That can justify presenting a concrete choice. It does not justify making the entire opening depend on blanket approval. Indeed, the top screen says its first acts need no owner decision.

The second decision is ambiguous:

- **A cap on unfinished agent work and undelivered results** is an admission policy the Conductor can manage under delegated authority.
- **A rule restricting what the owner may request** is a different proposition. “It limits you” does not establish its necessity.
- Shrink-the-fleet’s revised rule excluded owner walks and optional reactions from consuming admission slots. The top screen’s “open study and process requests” needs that precision.

The missing decision is primarily **an operating decision**, not necessarily another owner card: what happens when supervision would violate the same-run permanent-fix rule, or when a consequential recovery boundary warrants testing before another incident?

The Conductor should settle that scope explicitly, recording its authority and reason. Ask the owner only if concrete evidence makes the obvious delegated answer contested. His eventual walk pass remains his; it is not an additional cleanup-policy decision.

**6. The top screen needs substantial replacement.**

Specific edits:

- **Line 1:** add “when current holds, stops and readiness permit.” An advancing status is not proof that the next act is ready.
- **Line 2:** replace the complete retrospective with identifying each mod’s immediate next legal act. State that deeper reconstruction proceeds alongside execution.
- **Line 3:** remove automatic remedies. Slow dispatch needs diagnosis; an outside-runtime comparison needs justification; contention needs evidence of competing work.
- **Line 4:** replace “Nothing else gets built” with a default deferral and an explicit route for a demonstrated exception.
- **Line 5:** promise a recommendation and an inconclusive outcome where necessary. Do not imply that all next steps require the owner.
- **“Most of the duplication…”:** cut “Most,” preserve the hypothesis and its uncertainty.
- **“The studies also came back incomplete…”:** say “Some requested work was incomplete.” The pack does not establish a universal completion failure.
- **“Most voided runs…”:** name the sample and distinguish stop reasons from recovery correctness.
- **“Your decisions: two”:** remove until the actual undecided policy choices are separated from delegated execution.
- **The first three acts:** put executing the next permitted mod act first; make the audit supporting work.

A replacement top screen could read:

> Through December 6, advance FlowWorks and Pyrelands using the current pipeline and preserve GimmeSomeSlack’s walk. Identify each mod’s next legal act from current records and execute it as soon as permitted. Reconstruct older failures alongside that work.
>
> Verify the relevant consolidations and repair demonstrated wrong answers or execution faults. Keep acceptance bars, holds and independent judgment unchanged. Record pipeline-caused readiness blocks, failed attempts and interventions; distinguish necessary judgment from avoidable rescue.
>
> Defer broad mergers, parking and new instrumentation. A reproduced recovery defect may justify comparing a local repair with one bounded replacement. Necessary repairs do not wait for that experiment.
>
> Return progress, failures, attributable costs and measurement gaps on November 29 and December 6. These results may justify a next investment; they may leave the broader architecture question unanswered.

**7. My three required changes, ranked.**

1. **Remove the retrospective as a gate to mod work.** Start with each immediate legal act, execute promptly, and investigate alongside it. Count pipeline-caused readiness blocks. State the supervision exception and preserve necessary same-run repairs.

2. **Repair the claims about agreement and evidence.** Quote revised positions accurately, retain the preventive-testing disagreement, restore uncertainty about incomplete migrations, and restrict the void conclusion to recorded stop reasons.

3. **Give each permitted change a concrete proof and stopping rule.** Require independent expected outcomes, before/after evidence, visible accounting gaps, and reconciliation for any ownership transfer. Stop or reconsider the particular failed repair or experiment; do not turn an arbitrary aggregate threshold into another study by default.