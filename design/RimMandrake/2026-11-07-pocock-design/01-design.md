# Pass 1: where Pocock's ideas could earn a trial in RimMandrake, and in Artisan

*2026-11-07, committed 14:07 PST by the detached helper on item `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL`.
Companion assessment: `D:\Luke\dev\RimMandrake\design\RimMandrake\mattpocock_design_suggestions.md`.*

**Independence note.** The brief allowed no subagents, so this pass is the helper's own. The second model's blind answer
(`02a-gpt-blind.md`) came back at 14:03, before this file was finished, and the helper read it. The blind step is still
blind (GPT never saw this file), but this pass is not blind of GPT. Elements formed before reading it are marked
**[pre]**; anything adopted from it is marked **[GPT-blind]**.

## 1. The problem

His words, 2026-11-07: *"do a deep design pass on RimMandrake on where we might benefit from a test to see where they can
help us, as well as whether they could inform Artisan so it doesn't create nonsense code as it iteratively gropes
forward. I am open to your recommendations."*

Two questions:

1. **Where would a trial of each skill's idea pay here?** Small, bounded, measured trials, ranked by value per minute of
   his time.
2. **Could the ideas stop Artisan loops writing poor code pass after pass?** First establish what the poor code is.

And one option he is weighing: becoming more involved in interface and module design himself (the talk's grey box: he
owns interfaces and the tests at them, agents own implementations). Present it as his option, with its weekly cost.

**Constraints (his rulings):** agents decide nearly everything (2026-10-22); "use it, break it, grow" over predictive
review rounds (2026-11-02); the builder writes its own verification (2026-08-26); north-star bars are his, loosening
them is his; reviews go to Codex; geometry offline in Python first; he specifies by reacting; the pipeline sitting
(`PIPELINE_RETHINK_OWNER_STOPPED_BURN`) is his and not to be pre-empted.

**Success:** a trial is worth running if a cheap, falsifiable result would change what we do. A loop option is worth
taking if it reduces a measured cost (landing, maintenance, false passes) without adding owner minutes or a review
ceremony.

## 2. What exists, so nothing is rebuilt

- **Checker discipline:** `mutate-your-checker`, `grader-validation`, selftests with planted mutants, the nightly full
  selftest sweep. Strong on "can this test go red?". Silent on *which layer* a test protects (see 3.1).
- **Design argument:** the Designer (dialectic stages, `designer_dialogue.md`: show before you ask), `deep-design-3x2`
  (three real options, blind second model, re-measure), `question-card`.
- **Code review:** Codex per file, `code_review_status.py`: correctness, not shape.
- **Shared harness modules that already exist:** `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\scenes\scenelib.py`
  (295 lines, a scene harness with `rect`, `cell`, `room`, `put`, `power`; used by 21 files on main) and the
  `validation_core.py` family (`prepare_site`, `LogTap`). **No loop prompt names either** (grep of the three
  `ralph/PROMPT.md`: 0 mentions).
- **Artisan:** the judge reads screenshots and claims, never code (`artisan-judge` SKILL.md, evidence table); the loop
  prompts hand the code over whole: *"Everything but that section is yours: code, defs, art, tests, harnesses. If a test
  is wrong or in your way, fix it or drop it."* (gss and pyrelands `PROMPT.md`). No loop has landed yet
  (`learned.md`, open question "What does landing cost?").
- **Nothing anywhere names code shape**: no deletion test, no seam vocabulary, no record of which modules are meant to be
  stable.

## 3. What the measurements say (method in the claims table)

### 3.1 RimMandrake hot spots, 2026-10-07 to 2026-11-07

6,919 commits touched `src/RimMandrake`. Top code files by commits, with fix-subject commits and size now:
`relentless.py` 248 / 32 / 8,494 lines; `ops_watch.py` 174 / 21 / 5,704; FlowWorks `SelfTest/Program.cs` 161 / 18;
FlowWorks `validation.py` 130 / 13; `dispatcher.py` 91 / 22 (24%); `seat_restart.py` 71 / 16 (23%);
`concept_tree.py` 22 / 11 (50%). Modules: `Utils` 1,757 commits, FlowWorks 1,390, `rimflow` 1,017, `Utils/art` 411,
`Utils/arena` 247 (55 fix) in its 7-day life before the trial ended and it was deleted.

What the fix commits are: **about half of the fix-subject commits before 11-02 name a review round** (276 of 516: "fix
the fifth review pass", "review round 14 fixed"). From 11-02, fix commits fell from 11% to 6% of all commits, and 35% name
a review. `concept_tree.py`'s 50% fix ratio is one afternoon (11-01, 18:14 to 20:31) of 14 review rounds hardening a
Markdown parser against ever stranger input; the hunt ended when the *accepted input* was narrowed ("sheet is plain
bullets", "bracket allow-list"). **An interface decision ended it, not more defensive code.** That is codebase-design's
"small interface" in one commit log.

Test shape across the repo:

- **52 mods have a pure `Kernel/` folder**, the project's pattern for offline-testable logic.
- **38 selftest checks in 21 mods are tautological truth tables**: `Check(RM_HoistKernel.HoldsRiderInTransit(may, col,
  down) == (may || !col || down))`, `Check(HugeGates.Animal(ga, f) == (ga && f))`. The expected value restates the
  one-line implementation. (Regex lower bound; 4 of 4 sampled were real.) Mutating the kernel line is caught, so
  mutation scores look good; what such a test cannot see is the *caller*, which computes every boolean it passes in.
  Graffiti's caller passes a literal `true` for `ThoughtActive`'s `markFound`.
- **About 50 of 1,537 Python selftest files assert on source text** (read a `.py`/`.cs`, check a string): 66 regex
  matches, 5 of 6 sampled real.

### 3.2 The loops' code (`origin/ralph/{gss,pyrelands,graffiti}` against main)

**His hypothesis, "nonsense code as it iteratively gropes forward", is mostly not what the branches show.**

| suspected | measured | verdict |
|---|---|---|
| code rewritten pass after pass | gross/net lines 1.0 to 1.5 on nearly every file the loops touched | refuted |
| interfaces churn pass to pass | public signatures mostly added; at most 8 removed lines per file | refuted |
| dead code from abandoned approaches | about 6 of 1,300 declared names unreferenced (after removing Harmony patch classes and RimWorld overrides): `ArtInset` (gss), `AridShrublandScore`, `ClearArsonDebt`, `IgniteRiteFront` (pyrelands), `ProbeWallFaces`, `WallGone` (graffiti) | rare |
| tests that pass by construction | Graffiti's tautological gate checks are older than the loop (git log -S: 2026-10-07 and 2026-11-03 builders); the loop's 45 added checks are literal or behavioural ("a psychopath mourns nobody", vertices stay inside the face, `CreaseCrossing(...) == 6`) | inherited, not the loop's |
| proof scripts that check themselves | GSS rows read the mod's own state through `GimmeSomeSlackProbe`, but with explicit negative controls; Pyrelands `validation.py` rewritten heavily (gross/net 10.3), rows dropped ("canonical-save rows dropped") and rows tightened (the furnace row had passed while heating nothing) | real risk, partly mitigated |

What the branches **do** show:

- **Accretion without consolidation.** Graffiti's kernel grew from 21 to 62 static functions; one-line boolean gates
  doubled from 6 to 12; functions taking four or more bools from 6 to 8. GSS's new `CordShape.cs` went from nothing to 15
  public members over 11 commits. Most of the new code is real logic (geometry, decision tables); the gates are the part
  that fails the deletion test.
- **Copies instead of a shared module.** GSS's `line`/`perimeter` exist in four new scripts with drifting signatures
  (`perimeter(x0,z0,x1,z1)`, `perimeter(..., gaps=())`, `perim(...)` returning a set), while `scenelib.py` already exists
  and no prompt names it. That matches Artisan's own Seen rule: *"A loop doesn't discover what it isn't told about."*
- **Code shape is invisible to every signal the loop has.** The running count, the judge and his look all judge the
  experience. The code is a free variable by design, so it drifts toward whatever passes the look. The cost lands at
  landing time (graffiti's branch is +7,530 / -1,445 lines over 160 files), and no loop has landed.

## 4. Question 1: trials

Every trial below uses agents only, works offline unless stated, touches no loop, no `relentless*.py` and no
`dispatcher.py` (the stopped pipeline's switch is the dispatcher's PAUSE file, so it is inside his sitting), and ends with
a one-line verdict in the digest.

### T1. Mutate the caller, not the kernel (tdd's tautology + codebase-design's deletion test) [pre]

- **Module:** three mods with tautological gate checks and an offline selftest: Graffiti (on main), KeelHoist,
  HugeThings.
- **What it does:** in a scratch clone, plant about 10 call-site mutants per mod (negate an argument at the call site,
  swap two boolean arguments, replace a computed argument with a literal) and 10 kernel mutants; run the mod's selftests
  and, where the 22-second minimal list loads the mod, its functional script once.
- **Says it helps** (Pocock right): kernel mutants caught at 90% or more while call-site mutants escape at 50% or more.
  Then the follow-on is concrete: inline gates that fail the deletion test, and move each test to the seam where the
  decision is made (the ThoughtWorker or JobGiver), with literal scenarios.
- **Says it doesn't:** call-site mutants caught at 70% or more by existing selftests or proofs. Then the kernel pattern
  is fine and the tautologies are a lint at most.
- **Cost:** 3 to 4 agent hours, at most one 22-second game load per mod. **His minutes: 0.**
- **Extends** `mutate-your-checker` with one question it lacks: does the test protect the layer where bugs are made?

### T2. One-module survey with the deletion test (improve-codebase-architecture, adapted) [pre]

- **Module:** `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\ops_watch.py` (5,704 lines, 174 commits, 21 fix, live).
- **What it does:** a fresh agent samples the module's real failures first (fix commits that are not review rounds)
  **[GPT-blind: failure-led]**, then walks the module for shallow interfaces and leaky seams, applies the deletion test,
  and writes at most five badged candidates to `Transient/`, self-contained (no CDN). If one is `Strong`, it builds that
  one deepening.
- **Says it helps:** at least one `Strong` candidate that Codex, reading cold, also rates real; after the change, the
  next two weeks' commits in that area touch fewer files per change than the last two weeks' (measured from `git log`).
- **Says it doesn't:** every candidate `Speculative` or a restatement of an open item; or files per change does not fall.
- **Cost:** 1 to 2 agent hours for the survey, 2 to 4 for one deepening. **His minutes: 0** (a digest line), 5 if he
  wants to look at the report.

### T3. Narrow the input before hardening the parser (codebase-design's small interface) [pre]

- **Module:** any checker that takes free text: `concept_tree.py` lint, the moddefs lint, review-sheet parsers.
- **What it does:** writes one rule into the builder brief: when a second review round finds a new input class, narrow
  what the tool accepts and refuse the rest by name, before adding a parser case. Retro-check it on the last three hunts
  in the log.
- **Says it helps:** of the last three hunts, the narrowing (where it came) ended each in one round. **Says it doesn't:**
  hunts ended without narrowing as often as with.
- **Cost:** 1 agent hour. **His minutes: 0.** Lower value now that "use it, break it" has cut review rounds; fold it into
  T2's brief rather than run it alone.

### T4. Behaviour tests in place of source-text selftests (tdd, obra's "Name the Break") [pre]

- **Module:** the ~50 Python selftests that assert on source text.
- **What it does:** classifies them (a real structure rule, such as "no `pkill -f` in a hook", versus a disguised
  behaviour check); converts five of the second kind into behaviour tests that name their break, and plants a behaviour
  mutant in each.
- **Says it helps:** the converted tests catch the planted behaviour mutants and the originals did not. **Says it
  doesn't:** the originals already catch them, or the conversions need game scaffolding.
- **Cost:** 2 agent hours. **His minutes: 0.**

### T5. A per-mod glossary (domain-modeling) [pre]

- **Module:** FlowWorks (pit, superdeep cell, canal, hose, excavation; the largest mod, 277k lines) or GSS (cord,
  conduit, run, strand, span).
- **What it does:** an agent writes the mod's glossary with `_Avoid_` lists from its code and his rulings, then counts
  synonyms for the same concept in identifiers and in the last 50 commit subjects.
- **Says it helps:** a fresh agent given the glossary answers a ten-question "which X do you mean" quiz on the mod better
  than one without (8 of 10 against fewer). **Says it doesn't:** both score the same.
- **Cost:** 1 to 2 agent hours. **His minutes: 0** to 5 (correcting a term).

### T6. Seams agreed with him before one build: the grey box (tdd's pre-agreed seams, the talk's thesis) [pre]

- **Module:** one upcoming rebuild with a real logic core. Candidate: the FlowWorks drawbridge under option B
  (`design/concepts/FlowWorks_Drawbridge/`, sitting 1 of 2026-11-03: the mechanics exist, option B replaces the
  upright-leaf contract the 78 art files were made for, so a seam between leaf state and its drawing is about to move).
- **What it does:** an agent drafts a one-page seam map (three to five seams; for each, the interface with its
  invariants, ordering and error modes, what a test there catches and misses, drawn as a picture and a table). He reacts
  for 10 minutes. The builder builds against it, tests at those seams first.
- **Says it helps:** after the build, fewer interface changes after the first commit and fewer fix commits in the first
  week than a comparable rebuild without a map (FlowWorks has several), and he can say what each seam does without
  opening code. **Says it doesn't:** the map is overturned by the first live run, or the numbers match the comparison.
- **Cost:** 1 agent hour for the map, normal build. **His minutes: 15 to 20.**

### Ranking by value per minute of his time

All but T6 cost him nothing, so among them the order is expected information per agent hour:

1. **T1** caller mutation: it tests the sharpest claim (logic extracted for testing, bugs in the calls) against the
   project's most widespread pattern (52 mods with kernels).
2. **T2** one-module survey on `ops_watch.py`, with T3's narrowing rule in its brief.
3. **T4** behaviour tests for source-text selftests.
4. **T5** glossary.
5. **T6** the grey box, the only one that costs him minutes and the only direct test of the talk's thesis. Run it after
   T1: if T1 shows the bugs live at call sites, a seam map is the remedy and T6 is worth his 20 minutes.

## 5. Question 2: options for Artisan

Three things are true at once: the loops' code is mostly sound; it accretes and duplicates; and nothing the loop sees
measures its shape. The options differ in **who decides the shape, and when**.

### Option A. A seam and module map agreed with him at loop setup (grey box) [pre]

- **How:** at setup the head drafts a one-page map of the mod's modules (which exist, which are meant to be stable, the
  interface of each stable one) as a picture plus table. He reacts. The map goes into `PROMPT.md` beside the frozen
  statement, as "stable unless a live failure shows otherwise; say so in `QUESTIONS.md` when you change one".
- **Cost:** 10 to 15 of his minutes per loop, at setup; a few hundred prompt tokens per pass.
- **Fits "use it, break it":** partly. It is a prediction made before use, but it carries an escape hatch led by live
  failure.
- **Buys:** the talk's thesis tested where it matters; landing gets easier if the stable seams hold.
- **Risk:** conflicts with Artisan's own core, *"trusts it to change anything except that experience"*; a wrong map
  steers the loop into the wrong abstraction for 20M tokens.
- **Dominates when:** the mod has a large existing codebase other work depends on (FlowWorks), so seams carry other
  people's code.

### Option B. Make shape visible at the claim: a shape report and one code line for the judge [pre]

- **How:** when `DONE.md` appears, a script (no model) prints the branch's shape against main: public-surface growth per
  module, near-duplicate function bodies across files, symbols referenced nowhere, tautological-check patterns, proof
  rows dropped or loosened since the last claim, and which shared modules (scenelib, validation_core) it bypassed. The
  judge gets it plus one question: *"Would the deletion test pass for the three biggest new modules, and is any new test
  tautological?"* Findings go into "Why you are back" only if they would hurt landing.
- **Cost:** 0 per pass. Per claim, one script run and perhaps 50k to 100k judge tokens; against a first claim at 4.5M to
  8.2M weighted tokens, under 2%.
- **Fits "use it, break it":** yes. It measures what happened at the one boundary that already exists, and adds no
  round.
- **Buys:** an answer to his question on every claim, in numbers, so "nonsense" stops being a fear and becomes a count.
- **Risk:** a script can be gamed (the loop could learn the patterns); judges asked about code may weigh it above the
  experience. Keep it advisory, never a gate.
- **Dominates when:** we do not yet know whether bad shape costs anything, which is the case today.

### Option C. A consolidation pass at landing (improve-codebase-architecture as a one-off) [pre]

- **How:** after he accepts, and before the branch lands, a fresh agent takes the branch: deletion test on new modules,
  merge duplicates onto shared modules, delete the unreferenced, replace tautological tests with behaviour tests at the
  real seam; the proof suite and the accepted look must stay as they were (re-shot and compared).
- **Cost:** 0 per pass; one run of about 1M to 3M tokens per landing (assumed: about one to two guarded passes).
- **Fits "use it, break it":** yes. It runs once, on code that has been used and accepted, and the acceptance is its
  regression check.
- **Buys:** main gets clean code without slowing exploration; answers learned.md's "What does landing cost?".
- **Risk:** a refactor after acceptance can break what he accepted; it needs his re-look or a strict before/after capture.
- **Dominates when:** loops reach acceptance; until then it costs nothing.

### Option D. Two lines in the prompt (tdd and obra, minimal) [pre]

- **How:** add to `PROMPT.md`, under resources and how to work: *"Reuse before you write: `scenelib.py` and
  `validation_core.py` are the shared harness; extend them rather than copy a helper."* and *"A test names the break it
  catches; its expected value comes from a literal, his words or the spec, never from the code's own formula."*
- **Cost:** about 60 tokens per pass.
- **Fits "use it, break it":** yes for the first line (the duplication is Seen); the second answers a problem the loops
  have not shown (their tests are good), so Artisan's own rule, *"Don't add a rule ... to answer a problem nobody has
  seen"*, argues against it.
- **Risk:** prompt creep (one prompt already doubled from 6.9 KB to 13.9 KB).

### Recommendation

**B now, D's first line now, C at the first landing; A only as his option, on one loop.**

- B costs him nothing and answers his actual question with numbers on every claim; it is the only option that can tell
  us whether the shape problem is worth solving.
- D's first line is the one fix for a problem we have seen, and it uses Artisan's own rule about naming resources.
- C puts clean-up where it is cheapest and safest: once, after use, before main.
- A is the talk's thesis. It is worth one trial if he wants to be more involved, on the mod where seams carry the most
  other code (FlowWorks), and after T1 says whether call-site bugs are real.

**What would change it:** T1 showing call-site mutants are caught well (then shape matters less and B can shrink to the
duplication and proof-row lines); a first landing that is cheap (C becomes optional); a B report on the next claim
showing little growth or duplication (the problem is smaller than measured today); or his saying he wants to own seams
(then A first, on one loop).

## 6. The "more involved in interfaces" option, priced

| version | what he does | his minutes a week | basis |
|---|---|---|---|
| none (today) | nothing at code level | 0 | today |
| digest | reads a weekly page of at most ten new public interfaces in the five hottest modules, each with a deletion-test verdict and a one-line contract; replies "fine", "narrow it" or "that one is mine" | 10 to 15 | estimated |
| setup seams | reacts to a seam map at each new build or loop he cares about (T6 / option A) | 10 to 15 per module, so 20 to 60 at two to four modules a week | estimated; module rate assumed |
| Pocock as written | confirms seams before every TDD session, grilled per change | hours | 523 new non-test code files were added in the last 8 days; he would see under 2% of them |

**Advice:** take the digest for four weeks only if T1 and the first B report show shape problems that cost something,
and add setup seams on one loop. The full version is out of reach at this commit rate and contradicts the delegation
ruling.

## 7. Open decisions for him

1. Whether he wants to own any interfaces at all, and if so the digest (10 to 15 min a week) or setup seams (10 to 15 min
   per module).
2. Whether the Artisan head may add option B's shape report and one judge question to the judge procedure (a change to
   the Artisan method, his or the head's).
3. Whether a landing consolidation pass (option C) may change code he has accepted, given a strict before/after capture.
4. Whether D's reuse line goes into running loops' prompts now (a prompt change on running loops is the head's channel,
   not this helper's).

## 8. Claims table

`*` = the recommendation changes if this is wrong.

| # | claim | value | status, method |
|---|---|---|---|
| C1* | Loop code is rarely rewritten | gross/net 1.0 to 1.5 on most files | measured: `git log --numstat main..origin/ralph/<b>` summed per file (`/tmp/pocock_measure/churn.py`) |
| C2* | Dead code is rare in loop code | about 6 of 1,300 names | measured: declarations in loop-touched `.cs`, word grep over the branch tree incl. `ralph/`; Harmony classes and RimWorld overrides removed by hand |
| C3* | Loop interfaces grow, rarely change | Graffiti kernel 21 to 62 static fns; bool one-liners 6 to 12 | measured: regex over `git show` of main and branch |
| C4* | Tautological truth-table checks exist across the project | 38 checks in 21 mods | measured, regex lower bound; 4 of 4 sampled real |
| C5 | Graffiti's tautological checks predate the loop | 991aa22225 (10-07), 523eae3e75 and 346d2d1a2b (11-03) | measured: `git log -S` |
| C6* | The loop's own new checks are not tautological | 45 added `Check(` lines, read | measured by reading; judgement |
| C7 | 52 mods have a `Kernel/` folder | 52 | measured: `git ls-files` |
| C8* | Call-site mutants of kernel gates escape offline tests | unknown | **unmeasured**; T1 measures it |
| C9* | No loop prompt names `scenelib.py` or `validation_core.py` | 0 of 3 | measured: grep of the three `PROMPT.md` |
| C10 | GSS copied `line`/`perimeter` into four scripts | 4 | measured: read |
| C11* | The judge reads no code; the prompts give tests to the agent | as quoted | measured: read `artisan-judge` SKILL.md and the prompts |
| C12 | About half of pre-11-02 fix commits are review-round fixes | 276 of 516; 35% after | estimated: subject regex |
| C13 | concept_tree's hunt ended by narrowing the input | 14 rounds, 11-01 | measured: commit subjects |
| C14 | About 50 selftests assert on source text | 66 matches, 5 of 6 real | estimated: regex and sample |
| C15* | His minutes for a seam map | 10 to 15 per module | estimated |
| C16 | New non-test code files in the last 8 days | 523 | measured: `git log --diff-filter=A` (rename detection on) |
| C17 | A guarded pass costs 1.0M to 1.9M weighted tokens; a first claim 4.5M to 8.2M | as stated | read: `artisan` SKILL.md (their measurement) |
| C18* | A landing consolidation pass costs about 1M to 3M tokens | 1M to 3M | assumed |
| C19 | `dispatcher.py` is inside the stopped pipeline | PAUSE file under `D:\ClaudeWork\rimmandrake\dispatcher` | read: ledger task of 2026-11-07 02:26 |
| C20 | No loop has landed | 0 | read: `learned.md` |
