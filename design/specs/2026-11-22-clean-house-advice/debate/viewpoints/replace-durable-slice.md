# Viewpoint `replace-durable-slice`

Debate on the clean-house advice, 2026-11-22. Named by: GPT Round 0.

**Thesis given to the advocate:** Stop extending bespoke recovery and spend the fortnight testing and replacing one bounded orchestration slice with an outside durable runtime.

**Suggested first act:** Identify an actual interrupted-run failure, freeze its current behaviour, and build a competing implementation using the same adapters and acceptance evidence.

Each round was one fresh `gpt-6.1-sol` call at high effort through `src/RimMandrake/Utils/gpt_consult.py`. Round 1
saw `../context_pack.md`, its eight inlined files and only this viewpoint. Round 2 saw the same pack plus all eight
Round 1 arguments. Some Round 1 advocates saw the pack before one date was corrected (the "slow the work" control act
is of 2026-11-18, not 2026-11-22); Round 2 was told. GPT's words are kept below as it wrote them.

## Round 1: the argument

**1. THE CASE**

Spend the fortnight replacing **one interrupted-worker lifecycle**, subject to evidence that the replacement earns its place. Stop extending bespoke recovery within that boundary.

The strongest evidence is the study’s admission that Core’s difficult part is “what happens when a run is killed, cancelled or done twice,” and that its estimate may underprice that work (`advice.md` §4, Core). Yet the recommendation starts consolidating launchers and building Core while the outside runtime gets a scratch trial with fake workers. That commits integration effort before testing whether the project should own recovery at all.

The investment already warrants a competing implementation: at least **517 M weighted tokens** of machinery runs over nine days (`advice.md` §4). That is historical spend, not recoverable savings. The **33 standing voids in nine days** and **71 of 96 hand acts involving decisions also made by the tick** identify places to investigate; neither figure measures failures caused by missing durability (`advice.md` §2; single-source sweep, candidate 1).

An important limit: **the pack does not identify an individual interrupted-run incident with enough evidence to reproduce it.** Its identity, current reachability and repair cost are UNMEASURED. Finding one is the first act, not a premise we may invent.

Freeze that incident’s inputs, build identity, effects and required outcome. Implement its worker lifecycle on one outside durable runtime, using the existing launcher, workspace, result-validation and landing adapters. Compare both implementations against the same evidence and interruptions. Keep the stage policy, creative judgement and human walk intact.

This could reduce the recovery machinery the project must maintain [guess ~60%]. It will not automatically remove hooks, prose, duplicated status readers or unsafe external effects.

I therefore sharpen the thesis: **replacement is the fortnight’s primary machinery experiment, with a real cutover as its intended result; adoption remains conditional.** If no current failure can be reproduced, or the runtime cannot safely use the real adapters, stop.

That is a bounded experiment consistent with both purposes in `PURPOSE.md`: keep building a game while learning which factory mechanisms deserve to remain ours. It also answers `gpt_review.md` §4 with an operational comparison, rather than another architecture argument.

**2. THE FIRST TWO WEEKS**

Day 0 is **November 22**; day 14 is **December 6, 2026**. Dates are checkpoints, not claims about measured implementation speed.

| Act and date | Who | What “done” means |
|---|---|---|
| Day 0, Nov 22: establish the boundary | Conductor window; owner sets the fortnight’s priority | One worker lifecycle is the maximum scope: accepted request → launch → interrupted execution → result acceptance → existing stage-write interface. Other mod work continues under existing holds and readiness rules. |
| Days 1–2, Nov 23–24: find the incident | Helper run | One identifiable interrupted run has its launch record, relevant state, effects, intervention and expected outcome captured. The current implementation reproduces the recovery defect. If none qualifies, stop the replacement effort and report that result. |
| Day 2, Nov 24: freeze the comparison | Helper run; Conductor window | Pin the current revision, inputs and adapters. State independent invariants: holds survive; stale workers cannot commit; evidence names the build; no duplicate accepted result or stage move. Preserve observed behaviour as evidence, including its defect—not as the definition of correctness. |
| Day 3, Nov 25: select one runtime | Helper run | Verify a pinned version against primary documentation and a local executable check. Record its persistence, restart and deployment requirements. Choose one candidate; do not build several competing prototypes. |
| Days 3–6, Nov 25–28: implement the competing slice | Helper run | It invokes the same adapters and produces the same accepted-result contract. Each external effect has an explicit retry/reconciliation rule. No stage ladder, ledger migration or replacement judge system enters scope. |
| Days 6–7, Nov 28–29: compare interruptions | Helper run; Conductor window reads results | Both implementations face the recorded incident and the study’s five faults: controller kill, worker kill, duplicate result, worker hang and machine restart. Capture effects, interventions, elapsed time and weighted tokens. |
| Days 8–10, Nov 30–Dec 2: exercise real boundaries | Helper run | Repeat faults around actual launch and commit boundaries, including an effect completed before its acknowledgement. Test holds and stale results after restart. Resolve discrepancies against the invariants. Stop if safe recovery requires a second bespoke recovery controller. |
| Days 11–13, Dec 3–5: cut over one eligible workflow | Conductor window; helper run | Disable the old scheduling/recovery route for that workflow before enabling the new one. Run one permitted real stage act on FlowWorks or Pyrelands, whichever fits. Reconcile in-flight work before rollback. Retire the displaced live recovery path after acceptance; Git retains history. |
| Day 14, Dec 6: deliver the verdict | Conductor window; owner | One page reports success **or failure**, total measured spend and omissions, interventions, remaining maintenance, and the disposition of both implementations. Continue, roll back or stop expansion. |

The pack says GPT reviews of pipeline code remain stopped pending a calibrated brief (`CLAUDE.md`, “Code is clean…”). This plan does not quietly restart those reviews. GPT’s present role is this debate; any later implementation review must satisfy that existing condition.

**3. COSTS**

The available calibration is **12.2 M across seven consolidation runs**, each **1.2–2.1 M** (`advice.md` §4). Those were smaller changes; they do not establish a runtime-integration price.

| Work | Proposed weighted-token allowance |
|---|---:|
| Incident reconstruction and comparison fixtures | 4–6 M [guess ~50%] |
| Runtime implementation and adapter integration | 10–18 M [guess ~35%] |
| Fault comparison, real cutover, rollback proof and retirement | 8–14 M [guess ~40%] |
| Independent helper challenge and final evidence page | 3–5 M [guess ~50%] |
| **Detached-run total** | **25–43 M [guess ~40%]** |

Conductor-window spend is **UNMEASURED**. Thus **25–43 M is not an all-in total**. Record available figures from day 0 and expose missing coverage.

Owner attention: **30–50 minutes [guess ~50%]** for setting the priority and reading the final result. His gameplay walk and any other reserved acts are additional; their duration is **UNMEASURED**.

What slows:

- Broad launcher, lease and state-store consolidation waits.
- Repository-wide parking and rule compression wait.
- Within the selected slice, recovery faults feed the replacement experiment rather than successive bespoke extensions. Necessary fixes that unblock unrelated mod work continue.

The risks are integration cost, another persistent dependency, interruption during cutover, and retaining two controllers indefinitely. The plan takes those risks deliberately and requires one active controller, reconciliation before rollback, and retirement of the displaced route.

No savings figure is justified yet. Maintenance savings and payback time are **UNMEASURED**.

**4. WHAT IT KEEPS AND WHAT IT DROPS FROM `advice.md` §5**

| Recommendation item | Treatment |
|---|---|
| **Freeze** | **Keep, narrowed.** Freeze new recovery mechanisms in the selected slice. Drop the new repository-wide filename gate this fortnight; it does not prove recovery correctness. The Conductor owns the boundary without creating another standing seat. |
| **Observe** | **Keep targeted observation.** Trace the chosen workflow, adapter calls, effects and interventions. Defer the whole-tree recorder and seven-day parking exercise. Lack of use elsewhere does not establish what this replacement needs. |
| **Thin line** | **Keep.** Advance one eligible real mod act through the replacement. Preserve bars, evidence requirements and the owner’s five acts. A blocked or failed canary is a reported result. |
| **Strangle toward Core** | **Keep the replacement method; change the destination.** Retain interfaces, classified differences and retirement. Defer broad launcher/list/page merges and the full decision inventory. Test whether the runtime should own this recovery boundary before improving its bespoke equivalent. |
| **Typed worker output** | **Keep the contract.** Validate structured results and build identity within this slice. Defer an independent SDK adoption: changing transport and orchestration together would complicate attribution. Structured shape alone never establishes completed effects. |
| **Three-day outside-engine Trial** | **Replace it with the main experiment.** Use the actual failure and real adapters. Drop the requirements that the tick fail two tests and replacement code be under one-tenth its size. A single consequential failure can justify replacement; code size cannot establish safety or operating cost. |
| **Do not rebuild** | **Keep.** No archive-and-restart, new stage ladder, ledger replacement or factory-wide migration. |
| **Measure on day 14** | **Keep and strengthen.** Include integration and recovery spend, failed attempts and interventions. Lines, token share and ticket counts remain supporting evidence. |

**5. HOW IT COULD BE PROVED WRONG**

These thresholds are proposed decision rules, not measured baselines.

| Falsifier | Threshold and date | How it could mislead |
|---|---|---|
| **There is no demonstrated present problem for this slice to replace.** | If **fewer than one actual interrupted-run failure** is reproduced on the frozen current implementation by **day 2, Nov 24**, this viewpoint loses its immediate justification. | Missing records or difficult reproduction could conceal a real defect. Report that uncertainty; do not substitute a hypothetical failure. |
| **The replacement cannot recover safely.** | By **day 10, Dec 2**, the final candidate must complete **10 repetitions of each of the five fault scenarios** with **zero invariant violations and zero recovery interventions**. Any remaining violation or intervention rejects cutover. | Fifty trials cover only chosen interruption points. A harness may miss a real effect or accidentally make it safe. Include interruptions after effects and before acknowledgement. |
| **Integration consumes the fortnight without earning an operational result.** | If detached implementation spend exceeds **43 M**, or **zero real stage transitions** have been accepted through the replacement by **day 14, Dec 6**, reject further rollout under this plan. | An unrelated mod defect or owner availability could prevent a transition. Name the cause separately, but do not present synthetic success as completed adoption. |

Passing these thresholds permits continued use of **this slice**. It does not prove that replacing the whole orchestrator would pay.

**6. THE OWNER’S DECISIONS**

**One priority decision:** give this bounded replacement the fortnight’s machinery allocation, using the proposed **43 M detached-run ceiling [guess ~40%]**, while broader consolidation waits.

The Conductor chooses the incident, runtime, eligible mod and technical disposition under existing delegated authority. The owner receives the full day-14 result without needing to answer architecture cards.

His five reserved acts remain his. A final gameplay pass still requires his walk.

## Round 2: the rebuttal and concessions

**1. REBUTTALS**

**repair-current-runtime**

You propose: “Three-day engine Trial — Defer for fourteen days,” while allowing “four to eight small repair jobs.”

That ordering gives bespoke recovery another exclusive investment period before testing whether it should remain ours. The pack identifies interruption, cancellation and duplicate completion as Core’s difficult, potentially underpriced work (`advice.md` §4). Small reader-consolidation runs do not price those repairs; your cost section correctly admits this.

Your strongest answer is that current blockers remain UNMEASURED. I accept that. It supports reconstructing a current incident before spending, rather than automatically postponing comparison for the entire fortnight. My replacement effort stops on November 24 if no current recovery defect reproduces.

Your runtime-cost falsifier needs pipeline defects to occupy “more than 50% of at least 24 combined eligible mod-hours.” A consequential recovery defect could warrant comparison without reaching that threshold. The threshold tests overall operational burden; it cannot determine whether one recovery mechanism deserves replacement.

**freeze-strangle-core**

You schedule “Land the first launcher replacement” on day 6 and consolidation of “result acceptance and stage commitment” on days 10–12. Meanwhile, the outside runtime gets a three-day trial.

Those are overlapping investments. The trial should inform who owns recovery before substantial changes to that boundary. The measured six consolidation groups establish that inconsistent readers can be repaired; they do not establish the price or benefit of changing launch and commit ownership.

Your adoption falsifier requires the library to pass all five scenarios, the tick to fail at least two, and bespoke code to fall below one tenth of the comparable slice. You acknowledge counting problems, but the substantive hurdle remains wrong: one duplicate accepted effect could justify replacement; two harmless failures might not. The decision needs consequence, adapter obligations and operating cost.

I accept your correction that legitimate Conductor judgment must survive. “Sole executor” is defensible for routine effects only if the authority contract preserves that judgment.

**rebuild-small-core**

You propose to “switch all orchestration authority together” after building a replacement, while dropping the engine trial to spend attention “proving this core’s recovery boundary.”

That assumes the project should implement the very mechanism under dispute. A new pure decision function does not itself solve interrupted external effects. Your own day-2 requirement—reconciling a launch completed before its receipt was recorded—is exactly the boundary my smaller experiment tests.

Your proposed 8,000-line ceiling includes adapters, but retained dependencies remain outside it. You disclose that limitation honestly. It still means the ceiling cannot establish that the operating system became small or cheaper to maintain.

The proposed 100–180 M weighted-token allowance is explicitly a guess. The objection is scope: replacing all orchestration exposes every held and advancing mod to a handover before one recovery slice has earned replacement. Preserve your contract and rollback rehearsal; narrow the authority transfer.

**Remaining rivals**

- **supervised-mod-sprint:** “Automate nothing new” buys product focus, but leaves a reproduced recovery defect’s ownership unanswered; supervised routing is an acceptable fallback, with its Conductor cost exposed.
- **consolidate-facts-only:** “Preserve … storage boundaries” is a sound default, but consistent readers cannot reconcile a launch completed before its acknowledgement; whether that failure currently exists remains UNMEASURED.
- **controlled-live-research:** Comparing “execution modes” answers a useful question, but matched creative tasks and complete session accounting introduce uncertainties beyond the narrower recovery question.
- **shrink-the-fleet:** “One concurrent helper” changes capacity before concurrency’s contribution is measured; it can also serialize mod progress behind this experiment without making interrupted effects safe.

**2. CONCESSIONS**

The rivals correctly distinguish maintenance exposure from demonstrated need. Neither 517 M weighted tokens nor 33 standing voids establishes a present durability defect. I retain my incident gate and withdraw any implication that replacement deserves the fortnight’s machinery allocation before that gate passes.

Repair-current-runtime and consolidate-facts-only are right to inspect today’s landed changes first. Incident reconstruction must establish that the frozen current implementation still fails. A historical failure already repaired does not qualify.

Supervised-mod-sprint and controlled-live-research correctly treat supervision as potentially useful. I retain Conductor stewardship and classify interventions before calling them defects. A required judgment is different from manual recovery.

I change three specific Round 1 commitments:

- **“Stop extending bespoke recovery within that boundary”** becomes a pause on discretionary extensions. A necessary repair must not wait for the replacement experiment; record it and reassess the comparison.
- **Ten repetitions of every fault scenario** loses its status as a sufficient acceptance threshold. Repeating the same interruption point cannot establish boundary coverage. Require explicit effect/write boundaries, real-adapter evidence and classified failures; repetitions provide supporting evidence.
- **Zero real stage transitions automatically rejects further rollout** becomes two separate outcomes: unsafe or unproved cutover is rejected; lack of eligible work leaves operational benefit UNMEASURED and earns no expansion.

My 25–43 M detached-run estimate remains an uncalibrated planning allowance, not a comparative cost advantage. Conductor spend and maintenance payback remain UNMEASURED.

The corrected November 18 control-act date supplies no new November 22 instruction to stop advancing mods.

**3. YOUR REVISED POSITION**

For November 22–December 6, keep authorized mod work moving and make one recovery slice the only prospective replacement experiment.

First inspect existing investigations and today’s consolidations. By November 24, reproduce one current interrupted-worker defect using identifiable inputs and effects. If none qualifies, stop replacement work and follow targeted runtime repair.

If one qualifies, compare the smallest adequate current repair with one outside-runtime implementation using the same adapters and acceptance contract. Preserve stage policy, holds, judgments and existing records. Include integration, reconciliation and retirement costs.

Cut over only the selected workflow after real-boundary recovery proof and an eligible mod act. Require one active controller and rehearsed reconciliation before rollback. No eligible act means no earned production adoption. Report failures and accounting gaps on December 6; permit no automatic expansion.

**4. THE COMBINED PLAN YOU COULD ACCEPT**

I could combine:

- **repair-current-runtime’s** reconstruction of FlowWorks and Pyrelands, continued authorized progress, and completion of relevant existing cutovers.
- **consolidate-facts-only’s** landed-change inventory and verification of actual callers.
- **freeze-strangle-core’s** substantive growth restraint, explicit authority contracts and removal of displaced execution paths.
- **rebuild-small-core’s** independently specified invariants, stale-worker tests and handover rehearsal, applied to one workflow.
- **supervised-mod-sprint’s** supervised delivery fallback and unchanged acceptance standards.
- **controlled-live-research’s** accounting for failed attempts, Conductor work and contamination.
- **shrink-the-fleet’s** restraint on new discretionary requests and safe accounting for in-flight work, without adopting its unmeasured capacity caps.

I could not accept simultaneous production ownership by two controllers, a factory-wide cutover bundled into this slice, or accepting a pass without substantive evidence. Those combinations defeat the boundary’s safety and attribution.

I also could not accept delaying a necessary mod-path repair to protect experimental purity. Finish the repair, disclose the changed baseline, and stop the comparison if its justification disappears.

**5. THE ONE QUESTION**

**Does the current worker lifecycle still require manual recovery after an actual interrupted run on an authorized mod path?**

By November 24, reuse existing investigations to select one identifiable incident. Capture its launch, build, effects, intervention and required outcome. Replay it on the current revision in a disposable workspace, using the existing launcher and result boundary. Inspect actual effects as well as recorded status.

If recovery succeeds without a hand, this replacement proposal loses its immediate justification. If it fails, the missing recovery obligation becomes the comparison contract. If records or tools cannot establish the result cheaply, report **UNMEASURED** and proceed with mod delivery rather than inventing the case.
