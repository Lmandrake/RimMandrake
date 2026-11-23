# Viewpoint `controlled-live-research`

Debate on the clean-house advice, 2026-11-22. Named by: GPT Round 0.

**Thesis given to the advocate:** Treat the next fortnight as a bounded experiment comparing existing automation with supervised agent work on real mod tasks.

**Suggested first act:** State one research question, hold acceptance criteria fixed, and compare execution traces, weighted tokens and owner involvement under the two modes.

Each round was one fresh `gpt-6.1-sol` call at high effort through `src/RimMandrake/Utils/gpt_consult.py`. Round 1
saw `../context_pack.md`, its eight inlined files and only this viewpoint. Round 2 saw the same pack plus all eight
Round 1 arguments. Some Round 1 advocates saw the pack before one date was corrected (the "slow the work" control act
is of 2026-11-18, not 2026-11-22); Round 2 was told. GPT's words are kept below as it wrote them.

## Round 1: the argument

**1. THE CASE**

The next fortnight should answer one question:

> For fixed real mod work, does existing automation or Conductor-supervised agent work reach the same acceptance standard with fewer weighted tokens and fewer owner minutes, without worse recovery or elapsed time?

I sharpen the thesis: compare **execution modes**, using the existing tools and acceptance ladder. Building a new supervisor or experimental pipeline would change the subject.

This serves both declared purposes. `PURPOSE.md`, “The declaration” and “What is actually being experimented on,” explicitly make agent research part of the project, with the game providing visible evidence of agent mistakes. The Maturation specification, §2 item 10, also records the original approach: do the work by hand first; automate what proves boring.

The strongest evidence for comparison is uncertainty about the supposed remedy. The single-source sweep, candidate 1, counted **71 of 96 hand acts** as decisions overlapping the tick. But it assigned only `[guess ~40%]` confidence that one module would remove those acts: slow ticks could also explain them. The evidence establishes repeated intervention, not that more automation will outperform supervised work.

Meanwhile, `advice.md` §5 identifies the deciding measures—tokens, elapsed time, owner minutes and reversals per accepted stage move—and reports their baselines as **UNMEASURED**. Its recommended architectural direction therefore precedes its strongest outcome measurements.

The experiment has real work available: the supplied `pipe show` places FlowWorks and Pyrelands in in-game acceptance. Their readiness still needs checking; held and OFF mods supply no automatic permission to experiment. The OFF control act is from **November 18**, not the debate request today (`context_pack.md`, correction).

Finally, another open-ended redesign carries a demonstrated opportunity cost: at least **517 M weighted tokens** of machinery runs over nine days (`advice.md` §4). A bounded comparison could replace architectural preference with operational evidence `[guess ~70%]`.

This fortnight should produce accepted mod work and a decision about execution—not a fifth pipeline.

**2. THE FIRST TWO WEEKS**

Day 0 is November 22; day 14 is December 6. The following is a proposed protocol, not a claim about available task counts.

| Day/date | Act | Who | Done means |
|---|---|---|---|
| 0 — Nov 22 | State the question and register the comparison | Conductor window; owner accepts or changes the proposed envelope | One page fixes modes, acceptance criteria, accounting, stopping conditions and return date. |
| 1 — Nov 23 | Select real work | Conductor window; helper run inventories evidence | Aim for two matched pairs of remaining tasks within advancing mod versions. Record scope, readiness, expected difficulty and required game before assignment. Exclude held, OFF or BLOCKS paths. |
| 1–2 — Nov 23–24 | Establish accounting and isolation | Helper run; Conductor window | Every attempt has a build identity, execution trace, token reading or explicit missing reading, and owner-attention timer. Conductor sessions, subagents and GPT are included. |
| 2 — Nov 24 | Freeze the comparison | Conductor window | A uses current automatic routing. B uses the Conductor to choose and launch agent acts through existing tools. Both retain the same bars, relevant checks, independent judging, authority boundaries and landing rules. |
| 3–6 — Nov 25–28 | Execute first pair | Existing automation; Conductor window; helper runs | Both assigned tasks produce evidence or a recorded failure. Count retries, machinery repairs, waiting and manual state edits. Nobody quietly rescues A and calls it automatic. |
| 7 — Nov 29 | Check feasibility and contamination | GPT reviews protocol and outcome records; Conductor window reports | One short interim result names missing accounting, unequal work and repairs affecting either mode. Continue only within the registered envelope. |
| 8–11 — Nov 30–Dec 3 | Execute second pair, reversing mode order | Existing automation; Conductor window; helper runs | Both modes encounter another real task. Existing workers and judges remain independent where required. A supervised maker does not become its own judge. |
| 8–12 — Nov 30–Dec 4 | Compare interruption recovery | Conductor window; helper runs | One controlled worker interruption per mode in a disposable workspace, with no canonical-save or production-state risk. Record recovery cost and duplicate effects. Omit it if existing tools cannot isolate it safely; report UNMEASURED. |
| 12–13 — Dec 4–5 | Finish acceptance and audit costs | Fresh helper runs; owner for his reserved acts; GPT for the comparison | Results pass the unchanged applicable criteria. Only the owner grants his walk pass. All failed and unfinished attempts remain in the cost table. |
| 14 — Dec 6 | Return the result and choose the next default | Conductor window presents; owner decides any change he wants | Owner receives the comparison, accepted work, unresolved defects and a recommendation: automatic, supervised, task-dependent or inconclusive. Experiment machinery ends. |

Prefer identical tasks from the same starting build in isolated workspaces **only if existing automation supports that safely**. Otherwise use distinct matched tasks, assign modes before execution, and acknowledge the weaker comparison. Do not build a duplicate production controller to obtain experimental purity.

Keep fixed:

- Locked Design Versions and bars; divergent ideas wait for a later version.
- Worker models, starting evidence and judging procedure within each pair, where practical.
- Existing holds, readiness checks, game locks and the owner’s five reserved acts.
- The distinction between candidate evidence, accepted task completion and an actual production stage move.

An acceptance change invalidates that pair’s comparison. A shared machinery repair is recorded as contamination; its cost remains visible.

**3. COSTS**

The pack supplies a calibration point, not a measured experimental budget: seven consolidation runs cost **12.2 M**, with individual runs between **1.2 and 2.1 M** (`advice.md` §4). These were machinery runs, not a representative sample of live mod work.

| Cost | Proposed allowance or estimate |
|---|---|
| Twelve helper runs: two setup, four executions, four independent judgments, two accounting/analysis | **14.4–25.2 M weighted tokens** using the measured consolidation range as a rough proxy `[guess ~30%]`. Retries can exceed this. |
| Conductor window and GPT | Historical baseline: **UNMEASURED**. Planning reserve: **6–15 M** `[guess ~20%]`. Measure during the experiment. |
| Whole experiment | Approximately **20–40 M** `[guess ~30%]`; includes productive mod work as well as research overhead. |
| Owner’s protocol and decision time | Approximately **30 minutes** `[guess ~60%]`. |
| Owner’s required live looks | **UNMEASURED**. Planning reserve: **20–40 minutes** `[guess ~25%]`. |
| Total owner time | Approximately **50–70 minutes** `[guess ~30%]`; research administration and gameplay acceptance reported separately. |

Use **40 M** as a proposed experimental spending ceiling `[guess ~40% that it is sufficient]`, enforced outside worker briefs. Incomplete accounting cannot be treated as remaining capacity. Unfinished work and missing figures appear beside the ceiling.

What slows: broad consolidation, engine adoption, rule compression, bulk parking and new process studies. Necessary fixes on active mod paths continue, but consume time and tokens and can invalidate a comparison.

The principal risks are uneven task difficulty, Conductor learning between attempts, shared repairs improving the second mode, game availability, and research overhead displacing building. A small sample can support a provisional operating choice; it cannot establish a universal winner.

**4. WHAT IT KEEPS AND WHAT IT DROPS FROM `advice.md` §5**

| Recommendation | Treatment |
|---|---|
| **Freeze** | **Keep, narrower.** Hold execution policy and interfaces steady. Defer discretionary machinery additions. Use the existing Conductor’s review; do not build the proposed new publish gate for this fortnight. |
| **Observe** | **Keep targeted observation.** Trace the actual experimental work, including loaded paths where existing instruments expose them. Defer the repository-wide census and subsequent parking. Seven days of non-use remains insufficient proof of deadness. |
| **Thin line** | **Keep real mod progress.** Broaden from one compulsory core path to a comparison of automatic and supervised execution. Preserve whole-version acceptance; task slices are experimental observations, not invented stages. |
| **Strangle** | **Keep demonstrated repairs.** Consolidate a duplicate when it causes a concrete fault on the selected path. Defer the scheduled launcher, list, page and lease campaigns. |
| **Toward Core** | **Defer the destination decision.** Preserve the current decider and its existing improvements. Do not assume beforehand that moving every routing decision into code is the best next investment. |
| **Typed worker output** | **Keep existing structured results.** Defer the SDK pilot. Adding transport or authentication changes during the comparison introduces another variable. Validate result substance as well as shape. |
| **Three-day outside-engine Trial** | **Defer.** This fortnight compares the two execution modes already available. An engine trial becomes a possible next experiment if traces identify durability as the dominant cost. |
| **Do not rebuild** | **Keep.** No archive-and-restart, replacement controller or revived retired loop. |
| **Measure on day 14** | **Keep and strengthen.** Register measurements before work; include failures, owner attention, Conductor spend and accounting gaps. |
| **Stop new slice studies** | **Keep.** Only the interim check and final experimental result are commissioned. |
| **Treat every hand act as a core defect** | **Drop that presumption.** Trace it first. A mindful supervisory decision may be useful; an avoidable state repair is a different result. |
| **No study-generated tickets before owner reaction** | **Keep for this study’s architectural proposals.** Existing authority for necessary operational repairs remains. |
| **Reduce prose only when code absorbs its decision** | **Keep as a cleanup principle; defer the line target.** No 5,000-line milestone during the comparison. |
| **Architecture page before another generic mechanism** | **Keep the lookup discipline.** Do not require the owner to approve the nine-system destination before gathering outcome evidence. |
| **Counts that warn** | **Keep as context.** No bulk ticket parking, deletion or relabeling to improve the experimental result. |

**5. HOW IT COULD BE PROVED WRONG**

These are proposed stopping thresholds, not measured natural boundaries.

| Falsifier | Threshold and date | How the measurement could mislead |
|---|---|---|
| The comparison cannot be measured cheaply enough | By **day 2, November 24**, either no runnable matched pair exists, or more than **5% of recorded agent sessions** lack attributable weighted-token readings. Stop commissioning comparative runs. | Session counts can conceal one enormous missing Conductor session. Audit missing session duration and activity too; do not infer token completeness from session coverage alone. |
| Research displaces the work it promised to advance | By **day 10, December 2**, no selected task has met its fixed acceptance criteria despite at least two being recorded READY on day 2. This fortnight’s design has failed. | A genuinely difficult mod defect or owner absence can explain delay. Report the cause; the throughput promise still failed. |
| The experiment exceeds its bounded cost without a usable result | Before **day 14, December 6**, total spend reaches **40 M**, or experimental administration consumes **30 owner minutes**, with neither a completed pair nor an accepted task. End the experiment and return an inconclusive result. | Setup work may have lasting value; productive mod work may dominate token spend. Report both separately, but do not extend the experiment by renaming overhead. |

A supervised loss would **not** prove that running the comparison was mistaken. It would falsify extending supervised execution: if B costs more tokens **and** more owner minutes in both completed pairs, with no acceptance or recovery advantage by **December 6**, recommend A for the measured task class. Small samples, imperfect matching and learning effects limit that conclusion.

**6. THE OWNER’S DECISIONS**

Only two:

1. **Accept or change the experimental envelope:** the question, fixed acceptance standard, proposed 40 M ceiling, administration allowance and December 6 end date.
2. **At the end, accept or change the operating recommendation** supported by the result.

The Conductor selects ready tasks, assigns modes, coordinates helpers and handles ordinary delegated decisions. The owner’s five reserved acts remain his; live walks are acceptance work, not additional architecture decisions.

## Round 2: the rebuttal and concessions

## 1. REBUTTALS

**Supervised-mod-sprint**

“**Manual routing may substitute for automation**” is a legitimate hypothesis. Your sprint tests whether supervised execution can finish Pyrelands, but cannot establish whether that substitution helps. Both supervised success and supervised failure are compatible with existing automation being cheaper or dearer.

Your most important hidden cost is already acknowledged: “**Conductor routing, reading and reporting — UNMEASURED**.” Moving routing into that window could reduce recorded machinery work while increasing unrecorded work. The pack excludes Conductor spend; the 98 hand acts do not price supervision. A supervised pass would demonstrate feasibility, not an efficiency gain.

Your pass-tag falsifier also depends on readiness by November 24 and an offered walk completed by December 5. If either condition fails, the fortnight can end without testing its principal completion claim. That is understandable attribution, but it needs an explicit inconclusive outcome.

I accept your focus on finishing real work. I retain a comparison only where existing tools and suitable work make it cheap.

**Repair-current-runtime**

“**Much changed today … Their effect on actual mod progress has not yet been measured**” is the strongest objection to my original timetable. It supports observing the repaired runtime before assigning comparative work.

But “**execute the next permitted acts through the existing runtime**” alone cannot distinguish useful automation from expensive automation that supervision could replace. Stable operation supplies a baseline; it does not establish the best execution mode.

Your cost falsifier has a specific escape: repairs must exceed 30 M “**before both mods have crossed one accepted machine-controlled stage boundary**.” Once both cross, subsequent repair spend cannot trigger that test, however large. The ceiling should apply independently of reaching those milestones.

The corrected November 18 date also matters. The OFF instruction is neither a fresh November 22 suspension nor permission to resume those mods. Current controls bind; FlowWorks and Pyrelands remain the available candidates.

**Freeze-strangle-core**

“**The tick should become the sole executor of routine routing and stage transitions**” goes beyond the demonstrated fault. Conflicting next-step answers justify canonical readers. They do not establish that transferring execution authority will outperform explicit Conductor routing. The sweep itself gives only `[guess ~40%]` confidence that one next-step module would remove the overlapping hand acts; slow ticks remain an alternative explanation.

Your proposed launcher, output and transition changes also alter the system whose operational improvement you intend to measure. A lower second-week intervention rate could reflect easier work or learning; a higher rate could reflect migration disruption. Classified traces help, but cannot supply the missing comparison.

Your **34–66 M incremental machinery estimate**, with mod work and Conductor tokens additional, makes this uncertainty consequential. Small reader consolidations do not calibrate recovery or authority migration. Establish the current runtime’s actual limiting failure before buying that scope.

**Remaining rivals**

- **Consolidate-facts-only:** “**across at least three distinct incidents**” can postpone your scope-escalation test after one dominant lifecycle failure; otherwise, completing demonstrated caller migrations fits my plan.
- **Rebuild-small-core:** “**transfer authority once**” concentrates the handover risk across orchestration before the pack establishes that reader repairs or supervised execution are insufficient.
- **Replace-durable-slice:** “**the pack does not identify an individual interrupted-run incident**” makes your incident gate essential; I accept reconstruction now, replacement only if its evidence earns priority.
- **Shrink-the-fleet:** “**one concurrent helper**” tests serialization, but concurrency is UNMEASURED; changing admissions, roles and workload together cannot isolate which change helped.

## 2. CONCESSIONS

Repair-current-runtime and consolidate-facts-only are right that today’s changes deserve verification before another experiment changes their operating conditions. I change my opening acts to reuse the in-flight investigations and verify the callers serving active work.

Supervised-mod-sprint is right that finishing a version matters more than assembling balanced experimental samples. I withdraw the scheduled second pair and the twelve-run planning model. Suitable matched work is UNMEASURED; I will not duplicate substantial acceptance work merely to obtain a comparison.

I withdraw my **20–40 M total forecast** and **50–70 owner-minute forecast**. Consolidation runs do not adequately price live acceptance, and Conductor accounting remains unproved. Total cost is **UNMEASURED** until coverage is established.

I also withdraw the **5% missing-session threshold**. Session counts cannot bound missing weighted tokens. Missing material Conductor accounting prevents a token-efficiency verdict.

My own stopping rule had the same loophole I identified in repair-current-runtime: reaching an accepted task could disable its cost stop. I change the proposed **40 M ceiling** to stop further comparative work regardless of partial success. It is enforceable as a total ceiling only with adequate accounting; otherwise comparative commissioning stops.

Replace-durable-slice is right that recovery proof must exercise actual effect boundaries. A disposable-workspace worker interruption alone cannot establish production transition recovery. Unsupported recovery comparisons remain **UNMEASURED**.

Finally, supervised routing needs an explicit temporary exception where it would otherwise violate the standing prohibition on hand workarounds without permanent fixes. My Round 1 operating envelope did not state that clearly enough.

## 3. YOUR REVISED POSITION

For the fortnight ending December 6, advance FlowWorks and Pyrelands through the current runtime, preserve GimmeSomeSlack’s walk, and defer discretionary architecture changes. First collect existing investigation results and verify today’s consolidations on those paths.

Observe actual execution, including Conductor work, failed attempts, waiting and repairs. Attempt a small automatic-versus-supervised comparison only if suitable ready work, existing isolation and adequate accounting are available by November 24. Otherwise continue productive work and return an inconclusive comparison.

Preserve bars, fresh judges, holds, readiness and the owner’s five acts. Repair demonstrated blockers in their existing homes. Do not presume every intervention is a defect.

Stop comparative work at the proposed 40 M ceiling or when measurement feasibility fails. Deliver accepted work, failures and the operating recommendation directly on December 6.

## 4. THE COMBINED PLAN YOU COULD ACCEPT

I could combine:

- **Repair-current-runtime’s** reconstruction of both advancing mods and verification of relevant unfinished cutovers.
- **Consolidate-facts-only’s** caller audit and independently justified expected answers, limited to active paths and demonstrated disagreements.
- **Supervised-mod-sprint’s** supervised completion route as a conditional comparison or recovery option, with its temporary operating exception stated explicitly.
- **Freeze-strangle-core’s** restraint on speculative additions and separation of legitimate judgment from routine recovery.
- **Replace-durable-slice’s** incident reconstruction and effect-boundary tests if interruption recovery emerges as the material obstacle.
- **Shrink-the-fleet’s** restraint on new study admissions and direct return of results, without imposing an unmeasured global concurrency cap.

I cannot combine a stable execution-mode comparison with simultaneous launcher migration, SDK adoption, replacement orchestration and fleet reduction. Those changes destroy attribution. They could follow the evidence as separate experiments.

Under any combination, I reject unsupported passes, weakened bars counted as progress, concurrent controllers for the same workflow, and efficiency claims that omit material Conductor work. Those invalidate the result itself.

## 5. THE ONE QUESTION

**After today’s consolidations, what avoidable machinery burden remains on the next authorized acceptance work?**

This week, follow the next ready work on FlowWorks and Pyrelands using existing launch records, control acts, helper results and timestamped Conductor notes. For each obstruction or intervention, identify its cause, elapsed delay, weighted tokens, owner minutes and whether supervision could legally bypass it without weakening evidence.

Reuse the investigations already running. Do not build a recorder. Mark missing accounting **UNMEASURED**.

Reader disagreement favors completing consolidation; recovery failure favors the durable-slice investigation; repeated routine routing delays justify the supervised comparison. If machinery scarcely obstructs acceptance, finish the mods.
