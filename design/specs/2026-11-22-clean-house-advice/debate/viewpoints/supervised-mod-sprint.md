# Viewpoint `supervised-mod-sprint`

Debate on the clean-house advice, 2026-11-22. Named by: GPT Round 0, as `artisan-mod-sprint`; renamed because "Artisan" is a retired era name here (see `../round0.md`).

**Thesis given to the advocate:** Temporarily accept supervised orchestration so agents and the Conductor can finish mod work without first perfecting automation; stop machinery work except what blocks a mod today.

**Suggested first act:** Choose one advancing mod, retain its bars and independent judges, and have the Conductor explicitly route its next acts; automate nothing new.

Each round was one fresh `gpt-6.1-sol` call at high effort through `src/RimMandrake/Utils/gpt_consult.py`. Round 1
saw `../context_pack.md`, its eight inlined files and only this viewpoint. Round 2 saw the same pack plus all eight
Round 1 arguments. Some Round 1 advocates saw the pack before one date was corrected (the "slow the work" control act
is of 2026-11-18, not 2026-11-22); Round 2 was told. GPT's words are kept below as it wrote them.

## Round 1: the argument

## 1. THE CASE

**For fourteen days, let the Conductor explicitly route one mod through its remaining work. Automate nothing new. Repair machinery only when a concrete fault blocks that mod’s next act.**

This is supported by the pipeline’s original design. The Maturation specification §2 names the Conductor as steward, requires reading evidence at stage changes, and says the pilot is done by hand first: “Only what proved boring by hand gets automated.” Supervision preserves that design’s intelligence without restoring the retired Artisan loops.

The strongest reason is the opportunity cost already measured. The present pipeline consumed **at least 517 M weighted tokens of machinery runs in nine days** (`advice.md` §4). Last week had **761 machinery-only commits against 198 mod-only commits** (§2). Those commits do not measure value, and `Utils` includes mod tools, but they support the owner’s complaint that fixing has displaced building.

The proposed cleanup still gives week one a launcher merger, list merger, page merger, recorder, typed-output pilot and engine trial (`advice.md` §5). Each may be worthwhile. None is established as necessary to finish the currently advancing Pyrelands version.

Supervision is already substantial: **98 hand acts in nine days**, including **71 of the first 96 classified as decisions the tick also makes** (`advice.md` §2; sweep report, candidate 1). The sweep explicitly leaves their cause uncertain. These figures show dependence on supervision; they do not prove that another automation increment will remove it.

Choose **Pyrelands**, currently at in-game acceptance (`pipe_show_2026-11-22_1615.txt`). Preserve its locked version, bars, evidence requirements and fresh judges. A supervised completion would provide a useful reference workload for later automation [guess ~70%].

I sharpen the thesis: **manual routing may substitute for automation; manual assertion may never substitute for proof.** This needs an explicit temporary exception to `CLAUDE.md`’s prohibition on hand workarounds without permanent fixes. It must preserve readiness checks, holds, resource locks and the owner’s five reserved acts.

## 2. THE FIRST TWO WEEKS

Day 0 is **November 22**; day 14 is **December 6**. Dates are checkpoints, not permission to advance without evidence.

| Day / date | Act | Who does it | “Done” means |
|---|---|---|---|
| 0 · Nov 22 | Establish Pyrelands as the sprint’s priority. Review in-flight work before deferring other launches. | Conductor window | Existing controls express the priority. Current owner holds and OFF decisions remain respected. No retired machinery returns. |
| 0 | Read the locked version, bars, readiness list, current build and surviving evidence. | Conductor window; helper run if needed | Existing records identify the exact remaining acceptance work and actual blockers. Unknown readiness stays UNMEASURED. |
| 0 | Establish the supervised launch route. | Conductor window | Existing tools can launch and record the next authorized act without a competing tick launch. If they cannot, that is a concrete blocker—not grounds to bypass controls. |
| 1 · Nov 23 | Prepare the next unresolved in-game acceptance scenario. | Helper run | The scene, script, named game and build are ready; the required visible behavior comes from the existing bars. |
| 2 · Nov 24 | Run acceptance and classify failures. | Helper run | Each result distinguishes a mod fault, check fault, scene fault or inability to measure. Evidence names its build. |
| 3–5 · Nov 25–27 | Fix substantive gaps and repeat affected checks. | Helper runs; Conductor routes | Required checks pass. Changed deciding checks have bad-state and good-state proof. Mod fixes receive the required fresh review. Unaffected evidence remains valid. |
| Throughout | Repair only machinery blocking the next concrete mod act. | Helper run; Conductor selects scope | Failure is reproduced, repair stays in the existing home, related checks pass, and Pyrelands resumes. No general consolidation follows. |
| 6 · Nov 28 | Complete any required independent review of changed mod work. | Fresh helper; GPT may fill an existing independent-reader role | The reader did not make the fix. Significant holes are resolved or explicitly remain open. No additional review tier is invented. |
| 7 · Nov 29 | Check progress and costs. | Conductor window | Existing records show stage movement, remaining bars, blocked time, helper spend and owner minutes. Missing figures say UNMEASURED. Findings return in the requesting conversation. |
| 8–10 · Nov 30–Dec 2 | Finish remaining acceptance work. | Helper runs; Conductor routes | All required acceptance evidence is sufficient and consistent. Failed bars remain failed until proved. |
| 11 · Dec 3 | Prepare the owner’s sitting. | Fresh helper run | Stage 7 produces the walk brief and prepared saves. It has no veto, as the specification requires. |
| 12–13 · Dec 4–5 | Conduct the live walk; resolve touched findings where possible. | Owner; Conductor; helpers | The owner gives the pass or names problems. Fixes retain the required checks and independent review. Divergent ideas belong to another version. |
| 14 · Dec 6 | Record the result and decide what follows. | Conductor assembles; owner decides | A passed version has its pass record and tag. Otherwise the report names the exact remaining bar or blocker. Costs and failures accompany successes. |

If the version finishes early, record completion early. Do not expand its scope to fill the fortnight.

For each act, the Conductor records the reason, executor, build, result and next act using existing records. This is a narrative explanation of routing, not another authoritative state store.

## 3. COSTS

**The complete token cost is UNMEASURED.** The pack excludes Conductor-window spend and supplies no suitable GPT cost baseline.

| Component | Planning allowance | Basis and limitation |
|---|---:|---|
| Mod implementation, acceptance and independent judging | **25–42 M** [guess ~40%] | Assumes 12–20 helper runs [guess ~40%]. The historical mod bucket was 750 M across 353 runs (`advice.md` §2); it mixes workloads and contains upper-bound conversions. |
| Necessary machinery repairs | **0–4.2 M** [guess ~30%] | Assumes zero to two small repairs [guess ~30%], using today’s measured 1.2–2.1 M consolidation-run range (§4). A difficult blocker could exceed this. |
| Conductor routing, reading and reporting | **UNMEASURED** | Increased supervision could move substantial spend into this missing category. |
| GPT participation | **UNMEASURED** | Use only where it fills a needed independent role. |
| Routine owner attention | **45–85 minutes** [guess ~40%] | Approximately 5–10 minutes for the sprint decision, 30–60 for the walk, and 10–15 for the final reading [each guess ~40%]. Unexpected reserved acts are additional and UNMEASURED. |

The helper allowances total **25–46.2 M** [guess ~30%]. **That is not a total sprint forecast.**

What stops or slows:

- General pipeline consolidation, engine experiments, SDK adoption, recorder construction, rule compression and backlog sweeps.
- New starts on other mods receive lower priority. Existing queued owner walks may proceed, but their results do not count as Pyrelands output.
- Improvements to unattended operation wait.

The risks are concentrated: the Conductor becomes a bottleneck; routing knowledge may remain in its context; recurring manual recovery may become habitual; and infrastructure volume remains largely unchanged. Existing handoffs and records reduce these risks but do not establish restart reliability. The sprint accepts that limitation openly.

## 4. WHAT IT KEEPS AND WHAT IT DROPS

| `advice.md` §5 recommendation | Sprint treatment |
|---|---|
| **Freeze** | **Keep, tighten.** No new automation, including replacements undertaken merely to consolidate. Only a demonstrated blocker on the selected mod’s immediate path earns machinery work. |
| **Observe** | **Defer the recorder and parking.** Read existing records and note sprint acts. Do not infer that untouched files are dead. |
| **Thin line** | **Keep Pyrelands; change routing.** The Conductor chooses acts explicitly. A hand act is measured work, not automatically a defect requiring automation. |
| **Strangle** | **Defer scheduled mergers.** Consolidation happens only when necessary to repair an immediate blocker. |
| **Core** | **Defer implementation.** No decision inventory, routing transfer or rule-line deletion campaign during the sprint. |
| **Typed worker output** | **Defer adoption.** Retain current result formats and inspect evidence. A format improvement must earn its place through an actual blocker. |
| **Three-day engine Trial** | **Defer.** It does not finish the selected mod. |
| **Architecture page and new freeze gate** | **Defer construction.** Record the sprint’s authority and scope through existing mechanisms. |
| **Lease migrations** | **Defer.** Keep existing game locks and resource controls. |
| **No rebuild** | **Keep.** No replacement pipeline or revival of retired loops. |
| **Day-14 measurement and decision** | **Keep.** Judge fixed acceptance work, owner attention, spend and reversals. Automatic recovery remains UNTESTED unless actually exercised. |
| **Weekly generated metrics script** | **Defer construction.** Use existing outputs and disclose manual collection and missing coverage. |

Of §5’s stop rules, keep the pauses on slice studies, new rule sections and cosmetic compression. Keep owner reaction before turning study recommendations into tickets. Replace “each hand act becomes a core fix” with “each hand act remains visible.” Defer the permanent architecture-wide prohibitions until this experiment supplies evidence.

## 5. HOW IT COULD BE PROVED WRONG

These are **proposed decision thresholds**, not measured historical norms.

| Falsifier | Threshold and date | How the measurement could mislead |
|---|---|---|
| **Supervision does not deliver the selected version.** | **Zero Pyrelands pass tags by December 6**, despite readiness being established by November 24 and the owner completing an offered walk by December 5. The strategy failed its fortnight objective. | Remaining mod work may be much larger than the status label suggests. Report the starting bar inventory and discovered defects; do not substitute an easier mod. |
| **The owner becomes the dispatcher.** | **More than 30 owner minutes spent selecting next acts or rescuing orchestration by November 29.** Exclude his five reserved acts and reading the sprint decision. | Informal chat can hide routing work or mix it with enjoyable design discussion. Record the purpose and duration when it occurs. |
| **“Only today’s blockers” still consumes the sprint.** | **More than 10 M weighted tokens on machinery repairs by December 6.** That falsifies the proposed narrow repair allowance. | Helpers may label machinery as mod work or perform repairs inside Conductor windows. Classify mixed runs explicitly; if substantial spend cannot be attributed, report this test as UNMEASURED. |

An independent finding that a claimed pass lacks required evidence also invalidates that claimed result. The sprint cannot count a softened bar or an undecided bar as completion.

## 6. THE OWNER’S DECISIONS

Only two:

1. **Authorize the dated operating exception through December 6:** Pyrelands first; explicit Conductor routing; no new automation; immediate blockers repaired in existing homes; no automatic obligation to turn each hand act into a permanent fix. Preserve locked bars, readiness, independent judges, holds and his five acts.
2. **Provide a live-walk opportunity by December 5**, plus a short December 6 decision reading.

The Conductor can choose helpers, games and next acts under existing delegated authority. No engine, SDK, architecture-seat or backlog decision is needed for this sprint.

## Round 2: the rebuttal and concessions

## 1. REBUTTALS

**Repair-current-runtime.** Your warning that repair must not become “permission to leave permanent workarounds” is right for recurring mechanical failures. It does not establish that explicit supervision itself requires repair. The Maturation specification assigns stewardship and decisions after three cycles to the Conductor. The sweep leaves the causes of overlapping hand acts unresolved.

Your schedule nevertheless assigns reconstruction of two mods, cutover investigation and repair before its scheduled execution phase. Existing sweeps and an unblocking run are already in flight. The immediate task is to collect their results and establish the next legal act, then execute it. Investigating another mod or completing a migration earns priority only through a demonstrated obstruction. I accept your incident discipline; I reject making runtime maintenance the fortnight’s organizing objective.

**Controlled-live-research.** Your question—whether automation or supervision reaches the same standard more cheaply—is stronger than my original assumption that supervision deserves the entire sprint. But “two matched pairs of remaining tasks” are not established as available. FlowWorks and Pyrelands sharing an in-game stage does not establish equivalent work, dependencies or difficulty.

You correctly stop if matching or accounting fails. That makes the proposal honest, but it could leave the project with experimental setup rather than accepted work. Its accounting also requires precisely the Conductor coverage the pack lacks. Your proposed total remains an estimate, not evidence that comparison is cheap.

Record the next real acts, failures and costs first. Use an opportunistic comparison if suitable work and accounting already exist. Do not duplicate acceptance work or construct instrumentation merely to obtain a comparison.

**Freeze-strangle-core.** You say, “The proposed destination is justified; its superiority remains unproved.” The evidence justifies consistent operational facts. It does not yet justify transferring more execution authority to the tick. The sweep explicitly says slow ticks may explain hand interventions and gives only `[guess ~40%]` confidence that the next-step consolidation removes them.

Your plan commits **34–66 M weighted tokens of incremental machinery work**, with mod work and Conductor tokens additional, before that uncertainty is resolved. Launcher replacement, typed output, an engine trial and transition reconciliation compete with finishing acceptance.

Your intervention falsifier requires “at least two comparable completions in each week.” The pack establishes no such workload. An inconclusive result could therefore follow substantial machinery expenditure. Freeze discretionary growth now; require an observed obstruction before each replacement.

**Consolidate-facts-only:** “Audit every group’s callers” reaches beyond the selected mod’s immediate needs; verify its actual callers first, while retaining your independently specified expected answers.

**Rebuild-small-core:** “Failure leaves the existing factory operating” limits outage exposure, but leaves the proposed **100–180 M weighted tokens** and shared-resource contention spent without establishing that replacement was necessary.

**Replace-durable-slice:** Your admission that the pack identifies no reproducible interrupted-run incident defeats making replacement the default allocation; keep your incident-first stopping rule.

**Shrink-the-fleet:** “One concurrent helper” is an experimental setting without measured concurrency evidence; it could serialize independent review and repair without reducing their total work.

## 2. CONCESSIONS

Repair-current-runtime and consolidate-facts-only establish that today’s reported consolidations need verification where active work uses them. I withdraw any interpretation of “automate nothing new” that would prohibit completing a demonstrated, necessary caller migration.

Controlled-live-research correctly challenges my untested preference for supervision. I change compulsory manual routing to **explicit Conductor stewardship, using existing automatic execution when it works**. Supervised routing remains an available, recorded operating mode.

My original appeal to “Only what proved boring by hand gets automated” overstated its authority. That sentence is marked **[PROPOSAL]**; the agreed hand pilot concerned ExplosiveKnockback. It does not authorize a new Pyrelands exception. Any temporary departure from the permanent-fix rule must be stated explicitly.

I withdraw the narrow machinery allowance and helper-total forecast as reliable forecasts. Consolidation-run prices do not price live acceptance or difficult recovery. Total sprint spend, including Conductor work, remains **UNMEASURED**.

I also change my falsifiers:

- Missing readiness or an unavailable owner walk must produce an incomplete result, not shelter a success claim behind conditions that never became true.
- Excess machinery spend rejects my allowance, not supervision itself.
- Owner minutes alone cannot expose costs transferred into Conductor windows. Those tokens and recovery acts must also remain visible.

The corrected **November 18** control act supplies no new November 22 slowdown instruction. Existing stops still bind until changed; their age does not cancel them.

## 3. YOUR REVISED POSITION

For the next two weeks, prioritize completing Pyrelands’ current locked version. Collect existing sweep and unblocking results, establish its remaining bars and next legal act, and proceed through existing tools.

The Conductor explicitly stewards the passage. Working automatic routes remain available; supervised routing may replace an obstructed route under a stated temporary exception. Neither route may bypass readiness, holds, independent judgment, build evidence or the owner’s five acts.

Repair demonstrated machinery blockers in their existing homes, including incomplete caller migrations. Record recurring mechanical failures for permanent repair; do not normalize repeated rescue.

Defer scheduled mergers, new instrumentation, SDK adoption, engine trials and replacement cores. Return progress, failures, blocked time, weighted tokens and accounting gaps on day seven and December 6. Completion still requires the owner’s walk.

## 4. THE COMBINED PLAN YOU COULD ACCEPT

I could combine:

- **Repair-current-runtime:** collect existing work, classify actual blockers, fix their causes and preserve GimmeSomeSlack’s prepared walk.
- **Consolidate-facts-only:** verify active callers against independent expectations; remove displaced computation when a repair requires it.
- **Controlled-live-research:** register acceptance and accounting before execution; compare modes only where existing work permits a credible comparison.
- **Freeze-strangle-core:** freeze discretionary machinery growth and keep judgment distinct from routine execution.
- **Shrink-the-fleet:** reduce new admissions and safely account for in-flight work, without imposing an unmeasured universal helper cap.
- **Replace-durable-slice and rebuild-small-core:** retain incident fixtures, recovery invariants and explicit stopping conditions as evidence for a later decision.

I could not accept factory-wide cutover, scheduled broad mergers or a primary engine-replacement effort alongside this sprint. They consume the same attention and resources the sprint is meant to reserve for accepted mod work.

Under any combination, I reject softened bars, fabricated completeness, hidden Conductor spend, competing active controllers, and treating non-use during this narrow sprint as proof that machinery is dead.

## 5. THE ONE QUESTION

**What actually prevents Pyrelands’ next accepted advance: mod work, deciding-check or scene work, routing, or recovery?**

This week, use existing sweep results, launch records, control acts and acceptance evidence to follow its next legal acts. For each obstruction, record the concrete failure, elapsed blocked interval, intervention and available weighted-token reading. Include Conductor work where attributable; otherwise write **UNMEASURED**.

If routing and recovery repeatedly prevent ready work, my narrow sprint needs machinery investment. If acceptance work dominates, that investment should wait. Neither outcome alone selects an engine or proves supervision superior.
