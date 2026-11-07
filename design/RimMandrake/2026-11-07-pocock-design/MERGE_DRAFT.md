# Merge draft for the Conductor: Pocock's ideas, trials, and the loops

*Draft, 2026-11-07 14:19 PST, by the detached helper on `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL`. The
Deep-Design-3x2 skill gives the merge to whoever holds the conversation with him, so this is a draft: rewrite it as
`03-merged.md` with his answers under a Rulings heading. Inputs, all in
`D:\Luke\dev\RimMandrake\design\RimMandrake\2026-11-07-pocock-design\`: `01-design.md` (pass 1, the helper),
`02a-gpt-blind.md`, `02-gpt.md` (the second model, blind then critique), `02m-remeasure.md`. The run is a full 3x2 with
one caveat: pass 1 was finished after the blind answer arrived, so pass 1 is not blind of it (the blind answer is blind
of pass 1). Provenance tags: **[P1]** pass 1, **[GB]** GPT blind, **[GC]** GPT critique, **[RM]** re-measure, **[M]**
this merge.*

## The answer in five lines

1. **His worry is mostly not what the code shows.** The loops' code is rarely rewritten (81% to 100% of what they add
   survives), rarely dead (about 6 of 1,300 names), and the loop's own tests are better than the tests it inherited
   (0 of 45 Graffiti checks tautological). Quality is not *proven*; the feared nonsense is not *found* [P1, RM, GC].
2. **What is real:** interfaces accrete (Graffiti's kernel 21 to 62 functions, one-line boolean gates 6 to 12), harness
   helpers get copied because no prompt names the shared ones (GSS, 4 copies; `scenelib.py` exists, 0 mentions), and a
   loop deleted 102 lines of its inherited proof (Pyrelands) with no record of what each row guarded [P1, RM].
3. **The best Pocock trial costs him nothing:** mutate the *callers* of the project's pure "kernel" gates, not the kernels.
   38 truth-table tests in 21 mods restate one-line gates, and 52 mods have kernels. If caller mistakes escape, Pocock's
   "logic extracted for testing, bugs in the calls" is true here and the repair is clear [P1, GB, GC].
4. **For the loops:** keep code delegated and repair a boundary when a live failure, a misleading proof, a repeated
   copied fix or the landing review exposes its cost (option E, the second model's); add a pointer to the shared harness
   now; count shape at each claim for the head, not the judge [GB, GC, M].
5. **His "more involved in interfaces" option:** not yet. If he wants it, one module, at most 20 minutes a week for four
   weeks, reacting to a shown behaviour and its contract, never C# signatures. Decide after the caller trial reports
   [P1, GB, GC converge].

## Question 1: trials, final set

All are agents only and offline unless stated, touch no loop branch, no `relentless*.py` and no `dispatcher.py` (the
stopped pipeline's first undo step deletes `D:\ClaudeWork\rimmandrake\dispatcher\PAUSE`, so the dispatcher is inside
his sitting [RM]; the blind answer's dispatcher trial is withdrawn, as GPT itself agreed once told [GC]).

| rank | trial | Pocock idea | what it does | helps if | doesn't if | cost: agent / his minutes |
|---|---|---|---|---|---|---|
| 1 | **Caller, not kernel** | tdd (tautological), codebase-design (deletion test) | one Graffiti thought path first (`ThoughtWorker_ViewedGraffitiMark.cs` calls `ThoughtActive(..., true)` with a literal) [RM]: plant valid caller mutants and kernel mutants, excluding equivalent ones (a swapped argument to a symmetric AND is no mutant) [GC]; run the selftests; then, if callers escape, replace the truth-table tests with literal scenarios at the ThoughtWorker, one at a time, and inline gates that fail the deletion test [GB]. Repeat on HugeThings and KeelHoist only if the first is informative | kernel mutants caught, caller mutants escape at half or more; the replacement tests catch the caller mutants | caller mutants already caught at 70% or more: the kernel pattern is fine where it is | 2 to 4 h / **0** |
| 2 | **Dropped proof rows** | tdd's "an interface includes invariants", applied to a proof | trace each of the 102 inherited lines the Pyrelands loop removed from `validation.py` to the bar it served; disposition replaced, redundant, obsolete or coverage lost [GB, RM]. **Filed** as `RIMMASTER_TRACE_PYRELANDS_PROOF_ROWS_THE_LOOP_DROPPED` | every removed row has a disposition before the next Pyrelands claim is judged | n/a: this is a finding, not an experiment | 1 to 2 h / **0**, unless a north-star bar was loosened (then his) |
| 3 | **Behaviour tests for source-text selftests** | tdd, obra's Name the Break | classify the ~50 Python selftests that assert on source text; convert five disguised behaviour checks; score both catching planted behaviour faults *and* staying green on a harmless refactor [GC] | conversions catch faults the originals miss, or stop false reds on refactors | originals already do both | 2 to 4 h [GC raised it] / **0** |
| 4 | **One-module survey, failure-led** | improve-codebase-architecture, adapted | `ops_watch.py` (5,704 lines, 174 commits a month): start from one recurring real failure, deepen one responsibility only if it explains that failure; report in `Transient/`, self-contained; no extra review rating [GC removed it] | the failure stops recurring and related changes touch fewer coordinated places | no failure mechanism found: stop with "no justified change" | 2 to 4 h, plus a bounded build if justified / **0** |
| 5 | **Glossary for confused terms only** | domain-modeling | only terms implicated in a real misunderstanding (the greatbole three-way already earns its CLAUDE.md line) [GC]; watch whether later work confuses them | later work stops confusing them | no confusion found to fix | 1 h / **0** |
| 6 | **Grey box on one module (his option)** | tdd's pre-agreed seams; the talk | show him one consequential behaviour (FlowWorks drawbridge under option B is the candidate) and its contract in his terms: what must happen, in what order, what failure looks like; agents keep the technical seams; vertical tests [GC] | his accepted outcome arrives with less total owner time | the contract is overturned by the first live run with nothing learned | 1 to 2 h prep / **15 to 20** per module [RM] |

Folded into the builder brief, not run alone: *establish the supported input before adding defensive cases* (the
`concept_tree.py` episode: 14 review rounds on 11-01 ended when the accepted input was narrowed) [P1, GC wording].

## Question 2: options for the loops, final set

| option | how | cost per pass | fits "use it, break it" | from |
|---|---|---|---|---|
| **E. Failure-led repair by the builder** (default) | the builder repairs a boundary when a live failure, a misleading proof, a repeated copied correction or an integration conflict shows its cost; existing bars preserved; ordinary verification | about 0 to 5 agent minutes; 15 to 60 when an incident warrants (estimate) | yes, by construction | GB, GC |
| **D'. A pointer to the shared harness** | one line in each loop's resources: *inspect `Utils/scenes/scenelib.py` and `validation_core.py` before writing scene or proof helpers; reuse what fits, and say why a local helper differs* | about 60 tokens | yes: the duplication is seen, and Artisan's own rule says a loop finds only what it is told about | P1, GC qualified |
| **B'. Shape counts at each claim, for the head** | at `DONE.md`, a script (no model) prints surface growth per module, near-duplicate bodies, unreferenced names, tautology patterns and proof rows removed since the last claim; the head reads it beside the judge's verdict; **no judge criterion, no send-back on shape alone** | 0 per pass; one script run per claim | yes: a measurement at an existing boundary | P1, cut down by GC |
| **C'. Consolidation at landing, when needed** | at landing, repair only what the required file review or B' counts show (copies, unreferenced code, a weak test); proofs and his accepted look re-checked | 0 per pass; at landing, 1.0M to 3.8M tokens if needed [RM], beside a review of 127 code files across the three loops [RM] | yes: after use, before main | P1, made conditional by GC |
| **A. Seams agreed with him at loop setup** | grey box on one boundary of one loop, for a short run; agents may revise details and record why | 15 to 20 of his minutes per loop; prompt tokens negligible | partly: a prediction before use | P1, narrowed by GC |

**Where the passes disagreed, kept as disagreements:**

- **B, judge-facing or not.** Pass 1 wanted one code question for the blind judge. The critique called that a review
  ceremony and noted that routing shape through "Why you are back" makes it a gate in practice. **Merge sides with the
  critique**: the counts go to the head, not the judge, because they are needed to answer his question at all (without
  them "nonsense" stays a fear), but they do not gate a claim.
- **C, unconditional or not.** Pass 1 put consolidation at every first landing; the critique made it conditional.
  The re-measure settles it for the critique: landing is textually cheap (each branch conflicts only on `CLAUDE.md`,
  plus one DLL pair to rebuild), and the existing required file review already sees every line, so a consolidation pass
  is only worth running on what that review or B' finds.
- **"Mostly sound".** Pass 1 said the loop code is mostly sound; the critique said the measurements weaken suspicions
  without proving quality. **The critique is right**; the line above now reads "not found, not proven".
- **Order of T2 and T4.** The critique ranks behaviour tests above the survey (smaller intervention on a seen problem).
  Adopted.

**Combinations:** E + D' + B' compose and cost nothing of his; C' fires only at landing; A is independent and only on
his word. Order: D' now (the head's prompt channel), B' with the next claim, E as standing practice, C' at the first
acceptance.

## Claims after the re-measure

| claim | value | trust |
|---|---|---|
| loop-added lines survive at the tip | 81% to 100% (blame) | measured twice, two methods |
| Pyrelands' proof churn | loop removed 102 inherited lines, added 84, kept all 84 | measured (blame); **moved** from "rewritten" |
| unreferenced names in loop C# | about 6 of 1,300; two have the bridge-handler shape | measured twice; "rare", not "none" |
| Graffiti kernel growth | 21 to 62 static functions; bool one-liners 6 to 12 | measured twice |
| tautological truth-table tests | 38 in 21 mods, all from builders before the loops | measured; lower bound |
| loop's own Graffiti checks | 0 of 45 tautological (26 literal, 19 invariant) | measured twice; Graffiti only |
| shared harness named to the loops | 0 files across all three `ralph/` folders | measured twice |
| code review has seen loop code | never yet; latest records predate the loops | measured |
| review-round share of real fixes before 11-02 | about half (regex 53%; hand sample 10 of 19) | measured twice |
| landing conflicts | `CLAUDE.md` in all three; one FlowWorks DLL pair | measured (merge-tree) |
| landing review load | 127 code files, about 10,300 added lines | measured |
| caller mutants escape | **unmeasured**: trial 1 measures it | — |
| his minutes per seam contract | 15 to 20 | estimate |

## Review findings and their status

| finding (from) | status |
|---|---|
| dispatcher trial collides with his sitting (P1 raised; GC conceded) | **confirmed** by the ledger event of 02:26 |
| equivalent mutants must be excluded from T1 (GC) | **adopted**, a method fact |
| T2's "Codex rates Strong" is a ceremony (GC) | **adopted** |
| "files touched" rewards concentrating complexity (GC) | **adopted**: measure recurrence and coordinated edits instead |
| B's judge question is a ceremony and a gate in practice (GC) | **adopted** |
| C should be conditional (GC) | **confirmed** by the re-measure of landing cost |
| C18 arithmetic: 1.0M to 3.8M, not 1M to 3M (GC) | **confirmed** |
| B's share 0.6% to 2.2%, not "under 2%" (GC) | **confirmed** |
| "shape is invisible to every signal" too strong (GC) | **confirmed, sharpened**: invisible inside the loop; the landing review sees it |
| a scratch integration with main measures landing directly (GC new direction) | **done** in the re-measure (merge-tree) |
| compatibility checks against old saves and downstream consumers (GC new direction) | **unverified**: no trial designed; a candidate for C' at landing |
| replacing art he kept would need him in the drawbridge trial (GC) | **unverified**: the drawbridge's option B was already picked at its sitting; any art replacement in T6 stays his |

## What he decides, card-ready

Only one decision is his under the delegation policy. Trials 1 to 5 are technical calls (§1): the Conductor takes them
and logs `--why "delegated: technical"`. E, D', B' and C' are changes to how the head runs loops: the head's call, made
through `PROMPT.md` and the claim procedure, logged the same way. A conditional second card appears only if trial 2 finds
a loosened bar.

**Card 1** (put the real local time from `date "+%a %b %-d, %-I:%M %p %Z"` on its own line above it)

- Header: `Interfaces`
- Question: *"You watched Matt Pocock argue that you should own module interfaces while agents write the code. We
  measured the loops and the repo: the loops' code is not the nonsense feared (what they write survives, little is dead),
  but small one-line gates pile up and their old tests only restate them. A free trial will tell us whether bugs hide in
  the code that calls those gates. An "interface" here means what a piece of code promises its callers: what happens, in
  what order, and how it fails. Do you want to own any of those yourself?"*
- Options:
  1. **Not yet: run the free trials, decide when the caller trial reports** ← recommended: it costs you nothing and the
     trial tells us whether owning interfaces would fix a real problem. *Why:* evidence before your minutes. *Buys:* no
     time from you this week. *Costs:* a week or so before you can try the talk's idea.
  2. **One module, 20 minutes a week for four weeks.** *Why:* test the talk's thesis directly. *Buys:* you shape one
     behaviour (the drawbridge is the candidate) and see whether it lands with fewer surprises. *Costs:* 80 minutes over
     a month plus agent preparation; makes you a dependency for that module.
  3. **A weekly page of new interfaces, 10 to 15 minutes.** *Why:* stay aware of shape without owning it. *Buys:* a
     cheap look at what agents created in the five busiest areas. *Costs:* a weekly read that may change nothing; agents
     add about 65 code files a day, so you see a sample only.
  4. **No: keep code shape fully delegated.** *Why:* your minutes go to experience, art and bars. *Buys:* nothing changes.
     *Costs:* the talk's idea goes untested here.

**Card 2, only if trial 2 finds a row that guarded a north-star bar**

- Header: `Proof rows`
- Question: *"The Pyrelands loop removed <n> checks from the mod's proof script, and <k> of them guarded a bar you wrote:
  <bar, plain words>. Loosening a bar is yours. Restore those checks, or accept the loss?"*
- Options: **Restore them before the next claim is judged** ← recommended: a bar you wrote should not lapse by accident |
  **Accept the loss: the bar is obsolete** | **Replace them with a check the loop proposes, shown to you first**.

## What the "more involved" option costs him per week

| version | his minutes a week | agent cost | verdict |
|---|---|---|---|
| none (today) | 0 | 0 | today |
| one module for four weeks (card option 2) | about 20 | 1 to 2 h preparation per session | the converged advice of both passes, if he wants it |
| weekly interface page (option 3) | 10 to 15 | about 1 h a week to build the page | cheap, low leverage |
| a seam contract at each new build he cares about | 15 to 20 per module, so 30 to 80 at two to four a week | 1 to 2 h per module | only after option 2 proves out |
| Pocock as written (seams confirmed per change) | hours | — | out of reach: about 65 new code files a day, and it contradicts the delegation ruling |
