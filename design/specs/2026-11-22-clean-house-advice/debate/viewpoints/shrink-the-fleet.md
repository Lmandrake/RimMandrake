# Viewpoint `shrink-the-fleet`

Debate on the clean-house advice, 2026-11-22. Named by: added after Round 0 (see ../round0.md).

**Thesis given to the advocate:** The volume comes from too many agents, seats, concurrent runs and owner requests; cut the process (fewer helpers, fewer seats, one lane, a slower pace) and let the code shrink because less is asked of it.

**Suggested first act:** Cap concurrent helper runs and open requests, retire seats and roles that the reduced flow does not need, and measure what machinery the smaller flow still touches.

Each round was one fresh `gpt-6.1-sol` call at high effort through `src/RimMandrake/Utils/gpt_consult.py`. Round 1
saw `../context_pack.md`, its eight inlined files and only this viewpoint. Round 2 saw the same pack plus all eight
Round 1 arguments. Some Round 1 advocates saw the pack before one date was corrected (the "slow the work" control act
is of 2026-11-18, not 2026-11-22); Round 2 was told. GPT's words are kept below as it wrote them.

## Round 1: the argument

## 1. THE CASE

**Reduce the work entering the factory before reorganizing the factory.** For fourteen days, use one Conductor window, one concurrent helper, one advancing mod, and at most two admitted requests awaiting completion or owner response.

The strongest evidence is the rate of work entering one human’s project. Thirteen of twenty-one owner study requests arrived in four days, alongside eleven to thirty-three owner items per day. Every study produced something, but twelve owner-requested studies had no ledger record of delivery. The transcript sample qualifies that finding: two were never named; three were named briefly. This supports reducing unfinished work before building another delivery mechanism (`advice.md` §1).

The machinery is consuming substantial effort: at least **517 M weighted tokens** over nine days to establish the current pipeline, with **98 hand acts** and **33 standing voids** during that period. Machinery-only commits exceeded mod-only commits **761 to 198** in the last week, although the machinery category includes useful mod and art tools (`advice.md` §§2, 4). That is sufficient reason to test a smaller operating burden.

There is also direct evidence of repeated services: competing next-step readers, launch routes, queues, status pages and judges (`single-source-sweep/report.md`, candidates 1–8; `advice.md` §2). Fewer simultaneous obligations may let whole operating roles disappear instead of requiring every route to be consolidated [guess ~65%].

**I sharpen the thesis:** the pack does not establish that concurrency caused this volume. Actual concurrency, owner reading capacity and cost per accepted stage move are UNMEASURED. Reducing the fleet is therefore a reversible experiment, not a proven diagnosis.

It respects both purposes of the project. `PURPOSE.md` makes agent research an explicit goal; testing whether fewer agents produce more dependable creative work is legitimate research. Keep independent judgment, the existing acceptance bars and the owner’s five reserved acts. Reduce how much runs at once.

## 2. THE FIRST TWO WEEKS

Day 0 is **2026-11-22**; day 14 is **2026-12-06**. The caps below are proposed experimental settings, not measured optimal capacities.

| Day / act | Who does it | What “done” means |
|---|---|---|
| **0: Admit less work** | Owner | Approves the fourteen-day experiment. Default lane: Pyrelands. One concurrent helper includes detached helpers, in-window subagents and independent GPT jobs; the Conductor window remains available. |
| **0: Drain existing work safely** | Conductor window | Stops new admissions. Accounts for every in-flight record, distinguishes live work from stale records, and preserves unfinished changes before stopping anything. No abandoned clones or silently lost results. |
| **0–1: Establish one lane** | Conductor window; one helper run if needed | FlowWorks waits. GimmeSomeSlack’s prepared walk remains available, but selecting it replaces the active lane. Existing owner holds and OFF acts remain binding. |
| **1: Limit requests** | Conductor window | At most two requests are admitted across mod work, repairs and studies, including results awaiting owner response. New requests wait or explicitly replace one. Existing backlog remains searchable history; it does not automatically launch work. |
| **1: Record the starting point** | One helper run | Records enabled AI schedules, live seats, launch routes and the selected mod’s unchanged acceptance scope. Existing traces supply launches, stops, edits, spend and elapsed time. Any missing measure reads UNMEASURED. |
| **1–7: Observe the smaller operation** | One helper run installs a temporary recorder; subsequent runs remain serial | Captures loaded project modules, fired hooks and started units. Recorder output has one temporary home and an expiry. Rare recovery paths are listed separately. |
| **1–6: Build the selected mod** | Serial helper runs; Conductor window; owner for reserved acts | Existing stages advance normally. Makers and fresh judges run separately. Only an observed defect blocking this lane justifies machinery repair. Repair effort is charged to machinery. |
| **2: Remove standing AI duties the lane does not need** | Conductor window | Disables verified unnecessary recurring AI work. Operations alarms remain supplied by existing programs; the Conductor handles actionable results. Designer and judge briefs remain available for serial use. No new architecture seat is created. |
| **7: Retire what reduced demand actually released** | One helper run | Removes unnecessary seat launch configurations, instructions and exclusive dependencies where references and rare-path checks permit. Every removal names its replacement responsibility and restoration path. Uncertain components stay dormant. |
| **8–11: Continue the same lane** | Conductor window; serial helper runs | No new architecture, SDK pilot, engine trial or backlog census. Reports distinguish useful mod work, blocking repairs and waiting for the owner. |
| **12: Test one interruption** | One helper run | Interrupts a worker at a safe, reversible point and observes recovery. No duplicate effects or false pass. Records every manual recovery act; fixes only a demonstrated blocker. |
| **13: Finish and return results** | Conductor window | Each admitted request has either its result returned to the requesting conversation or an explicit remaining blocker. No undelivered result disappears into another queue. |
| **14: Judge the experiment** | GPT, then owner | One page reports mod progress, machinery spend, interventions, owner minutes, retired duties and unresolved defects. GPT evaluates the measurements. The owner continues, changes or ends the experiment. |

A request waiting for the owner remains admitted: this prevents “finished helper work” from becoming an unlimited reading backlog. Owner emergencies and reserved acts can interrupt; the displaced work waits.

## 3. COSTS

| Cost | Amount and basis |
|---|---|
| **Setup, temporary recorder, retirement and recovery check** | **6–9 M weighted tokens [guess ~40%].** Planning basis: three small operational runs at today’s measured **1.2–2.1 M each**, plus the study’s **about 2 M** recorder estimate (`advice.md` §4). These are different tasks, so the transfer is uncertain. |
| **Reserve for up to two small blocking repairs** | **3–5 M [guess ~35%].** Larger defects invalidate this allowance rather than justify an unlimited repair campaign. |
| **Planned cleanup allowance including reserve** | **9–14 M [guess ~35%].** This is an allowance, not a predicted saving. |
| **Mod implementation and judgment** | **UNMEASURED.** The pack has no comparable per-stage cost. Serial execution does not guarantee fewer total runs. |
| **Conductor work and day-14 GPT review** | **UNMEASURED.** Conductor spend is absent from the supplied accounting. |
| **Owner administration** | **About 30 minutes [guess ~50%]:** 15 to start, 5 at day 7, 10 at day 14. Live walks and other reserved acts are additional and UNMEASURED. |

What slows: parallel mod progress, new studies, speculative repairs, biome design reads and factory experiments requiring implementation. Idle games and unused account capacity are acceptable during this test.

What risk it takes: serial work can delay an urgent repair; the Conductor can become overloaded; dormant roles may contain overlooked responsibilities. Fewer agents may merely execute the same expensive machinery more slowly. Independent judges, game locks, owner holds, build identity and existing substantive checks remain necessary even with one helper.

## 4. WHAT IT KEEPS AND WHAT IT DROPS

Item by item from `advice.md` §5:

| Recommendation | Keep, change or drop |
|---|---|
| **Freeze** | **Keep and tighten.** Freeze speculative machinery work and reduce admissions. An observed blocker may receive a bounded repair; a void does not automatically authorize another mechanism. Use existing controls before adding a gate. |
| **Observe** | **Keep, with narrower claims.** Measure what this smaller operation touches. Non-use demonstrates absence from this experiment, not universal deadness. Retire exclusive dependencies only after reference and rare-path checks. |
| **Thin line** | **Keep.** One mod advances. Pyrelands is already at in-game acceptance, so this tests its remaining passage, not the entire pipeline. |
| **Strangle toward Core for two weeks** | **Drop as a scheduled campaign.** No planned launcher, queue, status-page or lease mergers. Consolidate only when a demonstrated lane blocker requires it. |
| **Adopt typed worker output** | **Defer the pilot.** Keep existing structured results. Prose parsing earns attention if it produces a concrete failure on the selected lane. |
| **Three-day outside-engine Trial** | **Defer.** It adds another builder and another implementation before testing whether reduced demand changes the problem. |
| **Do not rebuild** | **Keep.** Preserve the current pipeline, mods and history. |
| **Measure on day 14 and decide again** | **Keep.** Judge unchanged acceptance work and total operating burden. Smaller queues and fewer files alone cannot establish success. |

Also drop the scheduled **5,000-line rule-file target** and the new architecture-owner seat. Retire instructions when their duties disappear; do not turn prose reduction into another production quota.

## 5. HOW IT COULD BE PROVED WRONG

These are proposed failure thresholds, not figures inferred from the pack. They test whether shrinking the fleet is sufficient for the next fortnight.

| Falsifier | Measurement, threshold and date | How it could mislead |
|---|---|---|
| **The cap obstructs useful work** | By **December 6**, more than **24 cumulative hours** of otherwise executable selected-lane work waited solely because the one-helper cap prevented its required repair or independent check. | Owner absence, unavailable evidence and game holds could be wrongly attributed to the cap. Record the actual blocking dependency. |
| **The smaller operation still needs too much repair** | By **December 6**, detached machinery work for setup, retirement, recovery and lane repairs exceeds **14 M weighted tokens**. | Missing records or work hidden inside the Conductor could undercount. An expensive recorder could also dominate the result. Report categories and missing coverage. |
| **Interventions remain routine** | For stage moves completed during **November 30–December 6**, more than **three unplanned launches, stops, releases or state edits per accepted move** occur outside the tick. Exclude the deliberately injected interruption. | One difficult stage can dominate a small sample; stopped recording can manufacture improvement. Count from execution/control traces. With no completed moves, this measure is UNMEASURED and there is no success claim. |

Crossing these thresholds would reject this plan’s adequacy. Staying below them would support continued testing, not prove that excessive concurrency originally caused the cruft.

## 6. THE OWNER’S DECISIONS

**One decision now:** authorize the fourteen-day reduction as a single experiment, with Pyrelands as the default lane, one concurrent helper, two admitted requests and reversible retirement of unnecessary operating duties. This explicitly changes the current expectations of opportunistic parallel work and immediate machinery repair.

The Conductor chooses implementation details and preserves the owner’s five reserved acts. The owner need not adjudicate tools, seats or individual backlog items.

**One decision on December 6:** continue, adjust or end the experiment after reading its measured result.

## Round 2: the rebuttal and concessions

**1. REBUTTALS**

**Supervised-mod-sprint.** Your strongest claim is: “manual routing may substitute for automation; manual assertion may never substitute for proof.” Agreed on proof. But you prescribe fourteen days of explicit Conductor routing before showing that the current routing prevents the next legal act. The supplied status lists Pyrelands and FlowWorks as “tick: live”; their actual blockers remain UNMEASURED.

The original instruction to pilot by hand concerned Explosive Knockback. It supports supervised experimentation, but does not establish that Pyrelands now needs a different dispatcher. Likewise, 98 hand acts establish intervention, not successful supervised throughput. The sweep expressly leaves their causes uncertain.

Your cost table correctly makes Conductor routing UNMEASURED. That is a material exposure when adding routing responsibility to the seat through which studies already failed to return. Shrinking admissions can be tested while retaining existing routing. Use supervision when a concrete routing failure requires it; do not make replacing routine routing the experiment’s starting condition.

**Repair-current-runtime.** You recommend: “Repair failures that demonstrably obstruct FlowWorks and Pyrelands.” This is stronger than speculative consolidation, and your reconstruction-first approach is sound. But it limits the kinds of repair without explicitly limiting the unfinished obligations competing for execution and attention.

The supplied status lists six named in-flight records plus six more. Their actual live concurrency is UNMEASURED. That makes draining and classifying them necessary before adding reconstruction jobs—even useful ones. Your instruction to reuse existing results helps, but does not establish which recurring AI duties should continue.

Your **9.6–25.2 M** helper allowance excludes mod work, Conductor windows and GPT. It therefore cannot establish that maintaining both advancing lanes has a lower operating burden than concentrating execution. Conversely, the evidence does not justify my original blanket instruction that FlowWorks wait. The defensible difference is admission and concurrency control, not withholding otherwise executable work when Pyrelands cannot proceed.

**Freeze-strangle-core.** Your proposed **34–66 M** machinery programme includes observation, launcher replacement, typed output, an engine trial, transition commitment and parking. You acknowledge that mod work and Conductor-window tokens are additional. This purchases several architectural experiments before establishing which current obligations can simply stop.

“The tick should become the sole executor of routine routing and stage transitions” is a coherent destination. The sweep proves conflicting answers, however, and gives only **[guess ~40%]** confidence that one next-step module would remove the classified hand acts. It does not establish that launcher and transition restructuring are this fortnight’s highest-value work.

Your intervention falsifier requires “at least two comparable completions in each week.” The pack establishes no such workload. You correctly call insufficient observations inconclusive, but the programme could consume its allowance without obtaining its deciding comparison. First reduce demand, classify actual interventions and complete the existing cutovers that demonstrably matter. A particular recovery failure can then earn a particular replacement.

For the remaining rivals:

- **Consolidate-facts-only:** “audit every group’s callers” needs an execution boundary; prioritize callers used by admitted work rather than commissioning another broad audit.
- **Controlled-live-research:** “two matched pairs” are an aspiration, not an available workload demonstrated by the pack; compare modes only if suitable work and accounting already exist.
- **Rebuild-small-core:** a “single cut-over” concentrates authority transfer across held and active mods before evidence identifies a factory-wide replacement need; its **100–180 M** allowance is substantial speculative machinery work.
- **Replace-durable-slice:** “If none qualifies, stop” is the right discipline; reproducing an interrupted-run defect earns investigation, but does not by itself establish replacement over a bounded repair.

**2. CONCESSIONS**

I accept these changes to my Round 1 position:

- **Repair-current-runtime is right about existing work.** Withdraw the blanket “FlowWorks waits.” Reuse current sweeps and unblocking results before commissioning anything. Pyrelands remains the priority; another authorized mod can use the serial lane when Pyrelands has no executable act.
- **Supervised-mod-sprint and controlled-live-research are right about supervision.** Withdraw the presumption behind my “more than three” outside interventions per accepted move falsifier. That threshold has no measured calibration. Record all interventions, then distinguish authorized judgment, slow dispatch, recovery and wrong decisions.
- **The rivals are right about observation and rare paths.** Withdraw the scheduled module recorder and day-seven retirement campaign. Narrow traffic cannot establish that standing responsibilities disappeared. Disable a recurring AI duty only after identifying its responsibility and verifying that it remains covered. Leave uncertain components dormant.
- **My two-request rule was too broad.** Change it to cover unfinished agent work and results not yet returned to the requesting conversation. Waiting for an owner walk or optional reaction must remain visible, but must not consume every admission slot.
- **My cost allowance was weakly transferred.** Withdraw **9–14 M** as a forecast. It extrapolated consolidation-run costs to different work. Total incremental cost remains UNMEASURED until Conductor work is included.
- **My cap falsifier reacted too late.** Withdraw waiting for **24 cumulative hours** of cap-only delay. Review a documented cap blockage when it occurs and explicitly reconsider the cap.
- The corrected control act is from **November 18**. It establishes persistent OFF decisions, not a fresh November 22 instruction to halt today’s advancing mods.

**3. YOUR REVISED POSITION**

For the next fourteen days, reduce admissions and standing AI duties before restructuring orchestration. Use one Conductor window and one concurrent helper by default, with Pyrelands first. Preserve independent judges through serial runs. Drain existing work safely and reuse its results.

Keep existing routing unless a demonstrated failure requires intervention. Allow other authorized mod work when the priority mod cannot proceed. Keep GimmeSomeSlack’s prepared walk available.

Admit at most two unfinished agent requests, including undelivered results; track owner waits separately through existing records. Repair demonstrated blockers in existing homes. Defer scheduled mergers, SDK adoption, engine implementation and retirement campaigns.

Measure accepted work, machinery and mod weighted tokens, Conductor coverage, blocked time and interventions. Reconsider the helper cap when it demonstrably prevents useful work. A smaller queue alone is no success.

**4. THE COMBINED PLAN YOU COULD ACCEPT**

I could combine:

- **Repair-current-runtime’s** reconstruction, reuse of existing results and completion of relevant unfinished cutovers.
- **Consolidate-facts-only’s** same-state comparisons and independently justified expectations for readers actually used.
- **Supervised-mod-sprint’s** evidence standards and temporary supervised routing where needed.
- **Controlled-live-research’s** accounting and conditional comparison, if suitable work exists without constructing experimental infrastructure.
- **Freeze-strangle-core’s** repair-in-the-existing-home discipline and removal of genuinely displaced paths.
- **Replace-durable-slice’s** requirement to reproduce a current incident before commissioning replacement.

I cannot accept stacking those into simultaneous machinery programmes: that defeats the admission experiment. The small-core build, scheduled launcher campaign and durable-runtime implementation cannot all accompany it.

Under any combination, I reject deletion justified only by fortnight non-use, success claimed from missing accounting, weakened acceptance bars, or competing live controllers without exclusive ownership. Those invalidate either dependable operation or the evidence used to judge it.

**5. THE ONE QUESTION**

**When the selected mod is authorized and ready, how much of its actual delay and machinery spend comes from other admitted work, rather than faults on its own path?**

Use existing launch records, control acts, completed sweep results and Conductor messages during this week’s real acceptance work. For each blocked interval, identify the required next act, occupied resource, competing obligation and attributable weighted tokens. Separate owner waits, mod defects and runtime failures. Missing timing or Conductor spend stays UNMEASURED.

That directly tests whether shrinking demand addresses the observed burden—or merely leaves the same broken runtime running more slowly.
