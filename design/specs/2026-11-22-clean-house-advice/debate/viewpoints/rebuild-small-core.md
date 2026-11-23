# Viewpoint `rebuild-small-core`

Debate on the clean-house advice, 2026-11-22. Named by: added after Round 0 (see ../round0.md).

**Thesis given to the advocate:** Write a new, small factory core from zero (a few thousand lines) behind the existing mods, game driver and ledger history, and prove it with the old system as the oracle; retire the old orchestration in one cut-over.

**Suggested first act:** Write the architecture contract for the core from the work (not from the code), then build its decide-launch-read-move loop with the recorded history and fault tests as the oracle.

Each round was one fresh `gpt-6.1-sol` call at high effort through `src/RimMandrake/Utils/gpt_consult.py`. Round 1
saw `../context_pack.md`, its eight inlined files and only this viewpoint. Round 2 saw the same pack plus all eight
Round 1 arguments. Some Round 1 advocates saw the pack before one date was corrected (the "slow the work" control act
is of 2026-11-18, not 2026-11-22); Round 2 was told. GPT's words are kept below as it wrote them.

## Round 1: the argument

## 1. THE CASE

**Build a new orchestration core while the existing factory keeps serving mods, then replace the old orchestration in one guarded cut-over.** Keep the Maturation stages, mod code, game driver, working resource tools and ledger history.

The strongest evidence is competing authority. The single-source sweep’s candidate 1 found three different answers for LeaningScrub: held, automatically advancing, and awaiting an exam. It also counted 71 of 96 hand acts as decisions overlapping the tick’s responsibilities—although it explicitly leaves their cause uncertain. Consolidating readers helps; a core with one decision function and one transition writer would make competing authority harder to introduce [guess ~75%].

The present core contains 99,617 production lines, and reaching its current state consumed at least 517 M weighted tokens in nine days (`advice.md` §§2, 4). Those figures establish substantial maintenance exposure, not that every line is unnecessary. Today’s six completed consolidations show that recorded inputs and classified differences can support replacement proofs (`context_pack.md`, single-source sweep).

The study itself supplies the opening: §4 acknowledges that previous rebuilds were unbounded and lacked an oracle; §5 names bounded tick replacement as the next option if incremental repair fails. My disagreement is timing. Spending another fortnight rearranging launchers, lists and pages risks investing further in orchestration we may then replace [guess ~60%].

**I sharpen the thesis:** “a few thousand lines” is a design constraint to test, not a demonstrated size. The old system is a comparison oracle, not the authority on correct behaviour. Every disagreement must be resolved against the owner’s work contract; known bugs must become regression cases.

That contract must preserve creative judgement. The owner’s Maturation specification keeps blind judges, fix-in-place cycles, Conductor stewardship and the human walk. `PURPOSE.md` makes the factory experiment part of the product. A small core should route these judgements reliably, without pretending to make them.

This is a bounded experiment with a deletion obligation. It earns cut-over through recovery tests and real mod work. Failure leaves the existing factory operating.

## 2. THE FIRST TWO WEEKS

Day 0 is November 22; day 14 is December 6. Dates are proposed checkpoints, not measured delivery predictions.

| Day | Act | Who | “Done” means |
|---|---|---|---|
| 0 — Nov 22 | Write the contract from the work, before designing modules | Conductor window; helper run | Inputs, decisions, effects and authority are explicit. Preserve stages, holds, OFF controls, readiness blockers, ceilings, selective rechecking, fresh judges, Conductor decisions and the owner’s five acts. |
| 1 — Nov 23 | Fix scope and establish baselines | Conductor window; helper run | List everything being replaced and every retained dependency. Freeze a stratified corpus of **100 decision points**—a proposed sampling target—from recorded history. Start recording elapsed time, weighted tokens, interventions and owner minutes for eligible mod moves. |
| 2 — Nov 24 | Prove the persistence and effect boundary | Helper run | Demonstrate an intent/result/transition protocol using existing recording facilities. A restart can reconcile a launch that happened before its receipt was recorded. No second authoritative queue or stage store appears. |
| 3–4 — Nov 25–26 | Build replay and classify disagreements | Helper run; GPT challenges the proof | Each corpus case produces an expected decision, its provenance and a comparison with old behaviour. Missing inputs remain UNMEASURED. Synthetic cases supplement history and are labelled separately. |
| 5–6 — Nov 27–28 | Build decide → launch → read → move | Helper run | A pure decision function emits typed commands. One effect executor invokes retained tools. One writer accepts results and moves stages. Workers cannot advance stages themselves. |
| 7 — Nov 29 | Complete result and authority handling | Helper run; Conductor window | Interrupted, malformed, duplicate, cancelled and wrong-build results cannot create a false pass. Owner and Conductor acts retain their distinct authority. Stage 7 remains a brief with no veto. |
| 8–9 — Nov 30–Dec 1 | Attack recovery | Helper run | Run the study’s five fault families at relevant write/effect boundaries: tick kill, worker kill, duplicate result, hung worker and machine restart. Also test stale workers, competing resources and unreadable state. |
| 10 — Dec 2 | Read-only shadow operation | Conductor window; helper run | Old orchestration remains the sole actor. The new core records proposed decisions. Every substantive difference is explained; none is silently waived. |
| 11 — Dec 3 | Rehearse the actual handover and rollback | Conductor window; helper run | Old launchers and writers stop; in-flight work is drained or explicitly adopted; the new core reconciles state. Rollback rehearses reconciliation rather than restarting an old writer against unfamiliar events. |
| 12 — Dec 4 | Conditional single cut-over | Conductor window | Only after proof passes: switch all orchestration authority together. Every mod retains its existing hold/OFF/readiness state. Pyrelands or FlowWorks supplies the first eligible real move; the owner’s walk stays his. |
| 13 — Dec 5 | Recover a planned worker interruption during real work | Conductor window; helper run | The new core completes an eligible agent-controlled stage move without an outside launch or state repair. Evidence remains tied to the actual build. |
| 14 — Dec 6 | Retire old orchestration and deliver the verdict | Conductor window; helper run; owner reads | Remove replaced executable paths, timers and routing instructions. Git retains the oracle. Deliver results directly in the requesting conversation. If acceptance failed, retain the old factory and end the replacement attempt. |

The core’s proposed production-code ceiling is **8,000 lines**, including new adapters. This is a scope guard against recreating the measured 99,617-line core, not evidence that 8,000 lines will suffice. Retained dependencies and their responsibilities must be reported separately; moving decisions into an “adapter” does not satisfy the ceiling.

GPT’s role is to challenge the contract, fixtures and evidence. Any pipeline-code review must respect the existing requirement for a calibrated review brief (`CLAUDE.md`, “Code is clean when its promises are tested”).

## 3. COSTS

Measured anchors:

- Seven recent consolidation runs cost **12.2 M**, individually **1.2–2.1 M**.
- The current pipeline consumed **at least 517 M** of machinery runs over nine days.
- Conductor-window spend and cost per accepted stage move are **UNMEASURED**.

Neither anchor directly prices this replacement.

| Work | Proposed weighted-token allowance |
|---|---:|
| Contract and dependency boundary | 8–15 M [guess ~40%] |
| Historical corpus and comparison harness | 12–20 M [guess ~35%] |
| Core and retained-tool integration | 30–55 M [guess ~30%] |
| Recovery tests and resulting repairs | 25–45 M [guess ~30%] |
| Shadow operation, cut-over and retirement | 15–25 M [guess ~35%] |
| Independent challenges and measurement | 10–20 M [guess ~35%] |
| **Recorded helper/GPT work combined** | **100–180 M [guess ~30%]** |

Conductor-window tokens remain additional and **UNMEASURED** until instrumented. Real mod implementation and acceptance work must be shown separately.

Use **180 M as a proposed stop ceiling**, not an expected bill. Reaching it without acceptance ends the attempt; it does not justify another allocation automatically.

Owner attention: **40–60 minutes [guess ~50%]** for the initial choice and reading checkpoint/final results. His gameplay walks and other reserved acts are additional and **UNMEASURED**.

What slows:

- Unrelated factory experiments, broad consolidation and backlog cleanup wait.
- Existing mod work continues through the old factory, subject to current readiness and holds.
- Cut-over requires a deliberate pause in orchestration writes; its duration is **UNMEASURED**.
- Builders may compete with mod work for accounts, clones and attention.

The principal risk is discovering that hidden policy and recovery obligations exceed the small-core boundary. Other risks are incomplete history, a faulty oracle, stale workers producing effects after cancellation, and a rollback that cannot interpret new records. Keeping old operation available limits interruption; it does not make replacement cheap.

## 4. WHAT IT KEEPS AND DROPS FROM `advice.md` §5

| Recommendation | Position |
|---|---|
| **Freeze** | **Keep, with a named replacement exception.** Old operation receives necessary repairs; unrelated machinery waits. The new core is temporary duplication with a day-14 disposition. Do not promise negative line counts during construction. |
| **Observe** | **Keep observation; defer broad parking.** Record actual launches, writes, dependencies and interventions needed to establish the replacement boundary. Seven unused days cannot establish that an unrelated tool is disposable. |
| **Thin line** | **Keep.** Use eligible Pyrelands or FlowWorks work, including interruption recovery. Charge exposed factory repairs to machinery. Do not lift holds to manufacture a demonstration. |
| **Strangle toward Core** | **Drop sequential production migration.** Build and prove the replacement separately; transfer authority once. Small internal implementation steps remain useful. |
| **Core** | **Keep the destination; change construction.** Write new decision and transition code from the contract instead of progressively reshaping existing orchestration. |
| **Typed worker output** | **Keep the requirement.** Initially validate results behind the existing launch interface. Defer SDK migration unless the retained launcher demonstrably prevents the contract. Typed output alone never proves completed effects. |
| **Three-day outside-engine Trial** | **Drop from this fortnight.** Spend that attention proving this core’s recovery boundary. Failure of the boundary is a reason to stop and reconsider an engine. |
| **Do not rebuild** | **Reject for orchestration only.** Preserve mods, stable execution tools, acceptance policy and history. No archive-and-restart of the project. |
| **Measure on day 14** | **Keep, with earlier failure checkpoints.** Report failed attempts and machinery costs alongside accepted moves. Lines and ticket counts remain secondary. |

Also keep §5’s bans on speculative slice studies, duplicate mechanisms and prose compression as a substitute for executable decisions. Keep meaningful self-repair, but place each repair in its contracted home. Defer broad lease generalisation, page consolidation and idle-ticket parking unless required for replacement correctness.

## 5. HOW IT COULD BE PROVED WRONG

These are proposed thresholds, not existing measurements.

| Measurement and deadline | Falsifier | How it could mislead |
|---|---|---|
| Historical input completeness, **day 4 — Nov 26** | More than **10%** of the frozen 100 decision points require guessed critical inputs to determine the permitted act. The proposed history-based proof is too weak for this timetable. | Sampling easy recent records flatters completeness. Older missing records can make a feasible replacement look worse. Publish the selection method and missing branches. |
| Recovery correctness, **day 10 — Dec 2** | More than **zero unresolved safety failures** across the five fault families and contract boundaries: duplicate irreversible effects, stale-worker effects after authority loss, false passes or lost accepted transitions. | A fake executor may acknowledge effects more cleanly than systemd, git or the game. Include retained-tool integration tests; passing a simulation alone is insufficient. |
| Useful real operation, **day 14 — Dec 6** | Fewer than **one accepted agent-controlled mod stage move**, including planned worker interruption, with **zero outside launches or state repairs**, despite at least **48 hours of eligible work**. | Mod difficulty and unavailable resources can dominate. If no eligible work exists, the result is inconclusive and cut-over remains unearned. One easy successful move also gives limited confidence. |

Separately, crossing the **180 M stop ceiling** without acceptance ends this attempt even if no technical falsifier has fired.

## 6. THE OWNER’S DECISIONS

**One decision is necessary:** authorise—or decline—a bounded replacement attempt with the stated scope, stop ceiling, failure checkpoints and conditional single cut-over.

The Conductor can own the architecture contract, choose helpers, settle implementation details and execute a proven handover under existing delegated authority. SDK choice, engine choice, idle-ticket treatment and a new standing architecture seat need no owner decision now.

His five reserved acts remain his. This proposal requires no new decision about them.

## Round 2: the rebuttal and concessions

**1. REBUTTALS**

**Repair-current-runtime.** Your strongest point is that today’s consolidations deserve observation before another migration. But “Do not initiate unrelated resilience work” leaves an important distinction unresolved: recovery at the active launch/result/stage boundary is directly related to dependable operation, even before another production failure occurs.

The study identifies killed, cancelled and duplicate runs as Core’s difficult part; its recovery tests have not been run (`advice.md` §§4–5). Waiting for a repaired cause to require “more than one further manual recovery intervention” tests recurrence, not whether an interrupted commit can lose a transition or accept a result twice. Successful ordinary passage cannot establish that property.

This supports testing a replacement boundary now, **not** my original factory-wide cutover timetable. Your reconstruction should precede implementation, but it should supply an interruption experiment rather than postpone that evidence until December 6.

**Freeze-strangle-core.** You propose to “give the existing tick progressively more control of routine execution.” Yet the evidence establishes conflicting answers, not that the existing tick is the right place to accumulate authority. The sweep explicitly leaves the causes of overlapping hand acts uncertain.

Your fortnight changes the launcher, worker output, views, result acceptance and stage commitment while also conducting observation and an engine trial. Those are several interacting semantic changes. The measured 1.2–2.1 M consolidation runs do not price their integration; your answer acknowledges that limitation. Incremental construction deserves no automatic exemption from the fifth-pipeline risk you correctly identify in mine.

Your engine decision rule also requires the current tick to fail at least two fault scenarios and the alternative’s bespoke code to occupy less than one tenth of the comparable slice. Neither threshold measures the consequence of a failure or total maintenance responsibility. One serious recovery failure could justify replacement. Conversely, short code delegating complexity elsewhere could satisfy the size condition without reducing operating burden. Compare independently specified outcomes and exposed responsibilities instead.

**Replace-durable-slice.** Your demand for a real incident and real adapters improves my proposal. But “Stop extending bespoke recovery within that boundary” risks freezing the repair competitor before comparison. Test the smallest adequate current-runtime repair alongside the replacement; beating an unrepaired defect does not establish adoption’s advantage.

Also, the boundary ending at the “existing stage-write interface” needs scrutiny. The study explicitly says several programs write results and stages across three stores (`advice.md` §3). A durable worker lifecycle cannot establish correct stage commitment merely by successfully calling that interface. The comparison must include the result-to-transition gap and identify its sole writer.

You already require stale-worker rejection and effect reconciliation. Those obligations are precisely why a small, explicit control protocol remains necessary regardless of runtime choice. Your evidence could reject a bespoke implementation; it does not eliminate the architectural question my proposal addresses.

**Supervised-mod-sprint:** “Automate nothing new” can establish supervised throughput, but a completed mod cannot establish dependable unattended recovery; increased Conductor work remains a historically UNMEASURED cost.

**Consolidate-facts-only:** “Preserve … the storage boundaries now in force” leaves the study’s split result/stage commitment untouched; consistent readers can accurately describe inconsistent writes.

**Controlled-live-research:** “Aim for two matched pairs” depends on suitable work and attributable Conductor spend that the pack does not establish; your feasibility stop is sound, but an inconclusive comparison would leave recovery ownership undecided.

**Shrink-the-fleet:** “One concurrent helper” tests reduced demand, but actual concurrency and its contribution to failures are UNMEASURED; serialization alone does not remove competing readers or transition writers.

**2. CONCESSIONS**

I accept these corrections to my Round 1 position:

- **Repair-current-runtime and consolidate-facts-only:** establish what landed and reconstruct active paths first. I withdraw my implication that six reported consolidations establish completed replacement proofs. The pack supplies neither their completed proofs nor a definitive landed manifest.
- **Controlled-live-research and supervised-mod-sprint:** overlapping hand acts do not establish wasted supervision. I withdraw treating competing status answers as sufficient evidence of competing execution authority. Trace the actual launchers and writers; distinguish deliberate stewardship, slow dispatch and recovery.
- **Replace-durable-slice:** test actual launch and commit boundaries, including an effect completed before acknowledgement. I withdraw excluding an outside runtime until a bespoke core fails. A runtime may implement the replacement if the same contract and adapters support it.
- **Freeze-strangle-core:** my all-orchestration handover creates a larger exposure than the evidence justifies. I withdraw the scheduled day-12 global cutover and day-14 retirement. Cutover must follow proof of a bounded ownership transfer.
- **All narrower plans:** I withdraw **100–180 M weighted tokens** as the recommended fortnight allocation. It was an uncertain construction allowance, not evidence of value. Replacement cost and all-in operating cost remain **UNMEASURED**.
- My proposed **100-case corpus and 10% missing-input threshold** cannot establish branch coverage. They cease to be acceptance gates. Missing critical branches must remain explicit.
- The **8,000-line ceiling** remains only an experimental scope limit. It cannot demonstrate lower maintenance when retained dependencies carry substantial responsibility.

The corrected slowdown act is dated **November 18**. It supplies continuing controls, not evidence of a new slowdown instruction on debate day.

**3. YOUR REVISED POSITION**

For the next two weeks, keep existing mod work operating and test a bounded replacement core separately. First inventory the landed repairs and actual launch/result/stage writers on an advancing mod’s path. Then specify one coherent decide → launch → accept → commit contract, preserving all existing authority and acceptance rules.

Use the same fixtures and retained adapters to compare a new implementation with the smallest adequate repair of the current path. Include interruption after an effect but before its acknowledgement. Runtime choice remains open.

Old orchestration stays the sole production actor during replay and shadow operation. Transfer one bounded responsibility only after recovery, reconciliation and rollback proofs pass; otherwise end the fortnight without cutover. Do not schedule factory-wide replacement, broad parking or unrelated mergers. Report machinery spend separately, including missing Conductor accounting.

**4. THE COMBINED PLAN YOU COULD ACCEPT**

I could accept:

- **Repair-current-runtime’s** reconstruction and completion of demonstrated caller migrations as the opening work.
- **Consolidate-facts-only’s** independent expected answers, same-state comparisons and verification of landed changes.
- **Replace-durable-slice’s** real adapters, effect reconciliation and conditional retirement, with a minimally repaired current implementation as competitor.
- **Freeze-strangle-core’s** growth restraint, explicit contracts and removal of displaced instructions after executable ownership is proved.
- **Supervised-mod-sprint’s** supervised mod progress while the replacement remains isolated, with every intervention and its cost visible.
- **Controlled-live-research’s** accounting and contamination discipline, without requiring a matched-task experiment before testing recovery.
- **Shrink-the-fleet’s** reduced admissions where unfinished work is demonstrably accumulating, without assuming one helper is the correct capacity.

I could not accept, in any combination:

- Two production controllers authorized to launch or commit the same work.
- A deadline, code-size target or successful replay overriding unresolved holds, stale-worker effects, false passes or lost transitions.
- Retirement inferred from non-use during deliberately restricted traffic.
- A “small core” that hides its decisions and maintenance obligations in retained adapters.
- A durable-runtime victory declared against a known broken baseline without considering its smallest adequate repair.

These would invalidate the comparison or undermine the dependability being sought.

**5. THE ONE QUESTION**

**Can the current active launch → result → stage boundary recover correctly when an effect succeeds but its acknowledgement is lost, using a bounded repair in its existing home?**

This week, reconstruct one recent eligible run and reproduce that interruption in a disposable integration setup using the real retained launcher and recording interfaces. Check for duplicate launches, duplicate accepted results, lost transitions and acceptance of stale authority. Preserve holds and build identity. Compare the unmodified path, its smallest adequate repair and—only if needed—a minimal replacement implementation against identical expectations.

Record weighted tokens, interventions and which components require changes. Existing fixtures should be reused; the cost is **UNMEASURED**.

A correct local repair weakens my immediate replacement case. A repair requiring coordinated changes across competing writers strengthens it. If the necessary state or effects cannot be observed, the answer is **UNMEASURED**, and cutover remains unearned.
