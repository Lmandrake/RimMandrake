# Matt Pocock's design skills: what they do, what to keep

*Assessed 2026-11-07 (Pacific) for item `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL`. Read as text only from
`D:\Luke\checkout\mattpocock-skills` (MIT, v1.3.2, commit 4ae2317 of 2026-10-31), `D:\Luke\checkout\RobMitt-grill-me-skill`
(31d61d6) and `D:\Luke\checkout\obra-superpowers` (22f0b46). Nothing was installed or run. The trial design that follows
from this file is `D:\Luke\dev\RimMandrake\design\RimMandrake\2026-11-07-pocock-design\`.*

## The answer in one paragraph

Pocock's set is a small, honest, well-documented kit for one problem: agents speed up code entropy, so a human should own
the shape of the code (where the seams go, what each interface promises) and let agents fill in behind it. Most of the
*process* we already have in stronger, measured forms (question cards, Deep-Design-3x2, mutate-your-checker, the Designer,
functional scripts). What we do **not** have is his **vocabulary for code shape** (deep module, seam, the deletion test,
"one adapter is a hypothetical seam") and **any place where code seams are agreed before code is written**: today our
agreed things are experience-level bars (north stars), never module interfaces. That gap is the only thing here worth a
trial, and it is exactly what his talk asks him to take on. Install nothing; lift four ideas (listed at the end) into our
own briefs, and test them on real work first.

## The talk he watched

**Found, as best search can tell:** Matt Pocock, *"Software Fundamentals Matter More Than Ever"* (also titled *"It Ain't
Broke: Why Software Fundamentals Matter More Than Ever"*), AI Engineer, about 18 minutes, on YouTube April 2026
(id `v4F1gFy-hqg`; page https://ai.engineer/talks/v4F1gFy-hqg-software-fundamentals-for-ai-coding). Its chapters, per
the AI Engineer page: shared understanding, verbose AI, feedback and TDD, "brain strain". It pushes back on "specs to code,
code is cheap". The companion article, *"How to make codebases AI agents love"*
(https://www.aihero.dev/how-to-make-codebases-ai-agents-love), states the split he is weighing as a **grey box**: you
design and control the interface, the agent owns the implementation, and tests lock the module's behaviour at its
interface. **Caveat: I read search summaries of both, not a transcript or the article itself** (this run had no page
fetcher). The repo's README sections #1 to #4 restate the same argument and are the primary text used below.

## How to read the ratings

Novelty, complexity and insight, 1 (low) to 5 (high), judged against what this project already does, not against the
average team. *Novelty* = new to us. *Complexity* = cost to adopt here. *Insight* = how much the idea explains about why
work goes wrong.

## The skills

### `grilling` (and `grill-me`, a one-line wrapper that calls it)

**What it really does.** Thirty lines. Model the plan as a design tree; each round asks the whole *frontier* (every
question whose prerequisites are settled), numbered, each with a recommended answer worded so "yes" accepts it. Facts are
the agent's job (it sends a subagent to look things up and does not block the round on it); decisions are the user's. It
ends when the frontier is empty and the user confirms shared understanding. `grill-me` has no body beyond "call
grilling" and is user-invoked only.

**Keep:** *the frontier round.* Ask every independent question at once, never one that depends on an answer not yet
given. It is a batching rule with a reason, and it cuts rounds, not questions (his docs: "thirteen questions in about
three rounds").

**Rating:** novelty 2, complexity 1, insight 3.

**We already have:** `question-card` (one decision per card, options with trade-offs, recommendation first, real local
time), the Designer's dialectic stage 1 (`D:\Luke\dev\RimMandrake\src\RimMandrake\rimflow\roles\designer_dialogue.md`),
and the rule that facts are found, never asked (global CLAUDE.md, "run it yourself").

**Conflicts.** "Interview relentlessly" collides with *"Nearly everything including art"* (owner, 2026-10-22,
`D:\Luke\dev\RimMandrake\design\RimMandrake\delegation_policy.md` §1): grilling him on a §1 class (technical, scope, design detail) is a leak, not a courtesy.
His own explainer names the worst failure mode as **passivity**, "agreed, agreed, agreed for forty questions", which
produces a plan the agent wrote and the human nodded at; at our scale that is the default outcome. And it is text-only:
it has no way to show him something, which is how he specifies.

**Verdict: adapt.** Teach `question-card` sessions the frontier rule (independent cards in one batch; dependent cards
wait). Do not install.

### `grill-with-docs` and `domain-modeling`

**What it really does.** `grill-with-docs` is one line: run `grilling` and `domain-modeling` together. `domain-modeling`
challenges fuzzy words against a `GLOSSARY.md` ("you said account: Customer or User?"), invents edge-case scenarios,
cross-checks the user's claims against the code, and writes the glossary inline as terms settle (format: one or two
sentences per term, plus an `_Avoid_:` list of banned synonyms; no implementation detail ever). It offers an ADR only
when a decision is hard to reverse, surprising without context, and a real trade-off, all three.

**Keep:** *the `_Avoid_` list.* Naming the banned synonyms is what makes a glossary bite: "materialization cascade"
instead of a sentence. And *the three-part ADR test*, which is a good filter for what deserves a standing ruling.

**Rating:** novelty 3, complexity 3, insight 4.

**We already have:** ADRs in substance: owner rulings with dates in `D:\Luke\dev\RimMandrake\design\RimMandrake\standing_rulings.md`, `D:\Luke\dev\RimMandrake\design\RimMandrake\biome_rulings.md` and the
ledger's `--owner-said` / `--by-card` events, which are stronger than ADRs because they carry his words. Glossary entries
exist but are scattered: CLAUDE.md's "Say which greatbole you mean" is a textbook `_Avoid_` entry
(`RM_Greatbole` vs `RUT_GreatboleHeartwood` vs `RUT_GreatboleCore`), and `D:\Luke\dev\RimMandrake\design\NAMING_SCHEME_PLAN.md` fixes prefixes.
No `GLOSSARY.md` exists anywhere in the repo (checked with `git ls-files`).

**Conflicts.** Assumes one `GLOSSARY.md` at the root plus `docs/adr/NNNN-*.md`; we keep neither and the numbering is
banned here (*"EVERY ITEM IS NAMED, NOT NUMBERED"*, owner 2026-08-20). A new doc kind also needs an owner, or it decays
like any dump. The explainer itself reports the open complaint that answers land "into the conversation only" and no
record links a resolved answer to a spec, ticket and test.

**Verdict: adapt, narrowly.** A per-mod glossary with `_Avoid_` lists is worth one trial on a loop (see the design pass);
a repo-wide glossary is not, until the trial shows the loop's code names change.

### `tdd`

**What it really does.** A reference, not a driver. Tests go only at **pre-agreed seams**: before any test, write down
the seams under test and confirm them with the user, each with a line on what it catches and misses. Three named
anti-patterns: **implementation-coupled** (mocks internals, tests private methods, verifies through a side channel),
**tautological** (the expected value is recomputed the way the code computes it, so it passes by construction), and
**horizontal slicing** (all tests first, then all code; tests verify imagined behaviour). Rules: red before green, one
slice at a time. The refactor step was **removed** (June 2026) because agents almost never did it; refactoring moved to
review. Mock only at system boundaries.

**Keep:** *the tautological anti-pattern by name*, and *pre-agreed seams* as the place a human's design attention buys
the most per minute. The explainer's open gap is also a lesson: nothing in the skill decides whether a change has an
independent source of truth to assert against, and without one you get a tautology "reached from the other direction"
(its issue #746).

**Rating:** novelty 2, complexity 2, insight 4.

**We already have:** `mutate-your-checker` (plant faults, confirm red; stronger than a written warning, because it
measures), `grader-validation`, selftests with mutants, and the 2026-08-26 ruling that the builder writes its own
verification (accepted for speed).

**Conflicts.** "Confirm seams with the user" is a §1 technical call under `D:\Luke\dev\RimMandrake\design\RimMandrake\delegation_policy.md`; it becomes his only if
he takes the more-involved option. Red-first per slice fits pure logic and geometry (our offline Python sweeps) and does
not fit live-game behaviour, where the red is a proof run on a shared game. The skill's own explainer warns against
browser/e2e tests first: our analogue is a live proof first, and it is equally slow.

**Evidence it applies here:** a rough census finds **66 of our 1,537 selftest files read source text** (`read_text` on a
`.py`/`.cs`, `inspect.getsource`); 5 of 6 sampled were real source reads, so about 50 selftests assert on what the code
*says* rather than what it *does*. obra's list below names that exact smell ("the test greps source text"). Some are
legitimate structure checks; how many are not is UNMEASURED.

**Verdict: adapt.** Put the three anti-patterns and "name the seam and what it misses" into the builder and Codex
review briefs. Not into the Artisan judge's brief: the design pass found a code question there works as a review
ceremony and a gate (`2026-11-07-pocock-design\MERGE_DRAFT.md`). Do not install.

### `codebase-design` (with `DEEPENING.md` and `DESIGN-IT-TWICE.md`)

**What it really does.** Pure vocabulary. **Module** (anything with an interface and an implementation, any scale),
**interface** (everything a caller must know: types *plus* invariants, ordering, error modes, config, performance),
**depth** (behaviour per unit of interface; it rejects Ousterhout's line ratio because it rewards padding), **seam**
(Feathers: where behaviour can change without editing there), **adapter**, **leverage**, **locality**. Four principles:
depth is a property of the interface; **the deletion test** (delete it in your head: if complexity vanishes it was a
pass-through, if it reappears across N callers it earned its keep); the interface is the test surface; **one adapter
means a hypothetical seam, two means a real one**. `DEEPENING.md` sorts dependencies into four kinds (in-process,
local-substitutable, remote-but-owned, true-external) that decide how a deepened module is tested, and says "replace,
don't layer": delete the old shallow tests once interface tests exist. `DESIGN-IT-TWICE.md` spawns 3+ subagents with
different constraints (minimal interface, maximal flexibility, optimise the common caller, ports and adapters) and
compares on depth, locality and seam placement.

**Keep:** *the deletion test* and *one adapter = hypothetical seam*. Both are cheap, falsifiable questions a reviewer
or builder can ask of any new file. And "interface includes invariants, ordering and error modes", which is what our proofs keep
discovering the hard way.

**Rating:** novelty 4, complexity 1, insight 5. The most valuable file in the set for us.

**We already have:** nothing for code shape. `deep-design-3x2` covers "design it twice" (three genuinely different
options) and adds what Pocock's lacks: an independent second model answering blind, and a re-measure of starred claims.

**Conflicts.** Its own docs report it burning 100k tokens redesigning unasked things when run as a task (issue #449):
it has no stopping rule. Use it only as vocabulary inside another brief.

**Verdict: keep the vocabulary**, as a short section in briefs. No install.

### `improve-codebase-architecture`

**What it really does.** Scope first by **commit-history hot spots** (YAGNI: deepen only what keeps changing), then a
fresh subagent walks the code noting friction (one concept spread over many small modules, shallow modules, pure
functions extracted for testability while the bugs live in the calls, leaky seams, untested code), applies the deletion
test, and writes a self-contained HTML report of candidates, each with files, problem, solution, benefits, a before/after
diagram and a badge (`Strong`, `Worth exploring`, `Speculative`). It proposes no interfaces until the user picks one,
then grills on that one.

**Keep:** *hot spots decide where to look*, and *"if every candidate is Speculative, it found nothing"* (its docs admit
it rarely says a codebase is fine).

**Rating:** novelty 3, complexity 3, insight 4.

**We already have:** Codex reviews per file (`D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\code_review_status.py`), which judge correctness, not shape; nothing that
surveys shape.

**Conflicts.** Writes the report to the OS temp directory "so nothing lands in the repo": our rule puts a human-read
report in `Transient/` (pinned if kept) and anything anyone-later reads in the repo. It loads **Tailwind and Mermaid from
CDNs**, which its own docs say breaks silently offline or behind an SRI hook; our pages must render self-contained. It
assumes `GLOSSARY.md` and ADRs. The grilling loop after the report is its most complained-about part ("borderline
unusable"), and at our size (rimflow alone is 394 code files, 164k lines) a whole-repo survey is a context bomb.

**Verdict: adapt** as a one-module survey on a measured hot spot, report in `Transient/`, no grilling unless he picks a
card. This is a trial candidate.

### `prototype`

**What it really does.** Throwaway code that answers one question. Logic branch: a single self-contained HTML file with
a *pure* reducer or state machine inside, free-play buttons, guided walkthrough tabs, the full state shown after every
click, labelled in domain words for a non-developer. UI branch: several radically different variants on one route.
Captured afterwards on a throwaway branch; only the validated decision enters main.

**Keep:** *the logic module inside the prototype is pure and liftable* (the page is throwaway, the reducer is not), and
the *ungrillable* rule from the `grill-me` explainer: "one long form or three pages?" cannot be answered by talking;
build the thing, look, answer in one line.

**Rating:** novelty 2, complexity 2, insight 4.

**We already have:** "show before you ask" (`D:\Luke\dev\RimMandrake\src\RimMandrake\rimflow\roles\designer_dialogue.md`, Drawing requirements out of him), review sheets,
savegames for options, Artisan's contrast sheets ("got a decision in one look", `D:\Luke\dev\MandrakeWorkflows\skills\artisan\references\learned.md`), and
the geometry-offline-in-Python-first rule, which is the same "pure module first" idea.

**Verdict: skip the skill; the ideas are already ours.** One addition worth a line in the Designer: a state-machine
mechanic (a timer, a lifecycle) can get a clickable logic prototype as cheaply as a picture.

### `diagnosing-bugs`

**What it really does.** Phase 1 is the skill: build a **tight, red-capable** feedback loop (one command, already run,
deterministic, seconds, agent-runnable) that goes red on *this* bug, before reading code for theories. Then minimise,
3 to 5 ranked falsifiable hypotheses, instrument with tagged logs, regression test at a *correct seam*, clean up.

**Keep:** *"if no correct seam exists for the regression test, that is itself the finding"*: the architecture is
stopping the bug being locked down. That sentence is the bridge between debugging and module design.

**Rating:** novelty 2, complexity 2, insight 4.

**We already have:** `D:\Luke\dev\RimMandrake\design\RimMandrake\debug_process.md` (every mod has a functional script; every live session writes back what it
learned, false theories included), the Test Pilot (`rimflow pilot`), the rm-consult hypothesis role, and
`verify-before-you-escalate`.

**Verdict: skip**; add the no-seam sentence to `debug_process.md` if a trial shows it fires.

### `wayfinder`, `to-tickets`, `implement`, `code-review` (Pocock's)

- **`wayfinder`**: a map of *decision* tickets for work bigger than a session, frontier by blocking edges, one ticket per
  session; "refer by name, never by bare id" (the same conclusion as our naming rule, reached independently). Rimflow
  plus the Designer's concept tree already do this. **Skip.**
- **`to-tickets`**: tracer-bullet vertical slices with blocking edges; **expand-contract** for wide refactors (add the
  new form beside the old, migrate in batches, delete the old). The expand-contract recipe is worth knowing for any
  rename. **Skip the skill.**
- **`implement`**: seventeen lines: run `tdd` at pre-agreed seams, then `code-review`, then commit. **Skip.**
- **`code-review`**: two parallel axes kept separate on purpose, **Standards** (repo rules plus a fixed **Fowler smell
  baseline**: mysterious name, duplicated code, feature envy, data clumps, primitive obsession, repeated switches,
  shotgun surgery, divergent change, speculative generality, message chains, middle man, refused bequest) and **Spec**
  (does it do what was asked; scope creep). Our reviews go to Codex and ask about correctness. **Adapt:** the smell
  baseline, labelled as judgement calls, is a ready-made shape section for the Codex brief.

### RobMitt `grill-me` (21 lines, 2026-04)

One question at a time through the multiple-choice popup, 2 to 4 concrete options, acknowledge in a sentence, explore
files yourself rather than ask. It is the older Pocock behaviour plus `AskUserQuestion`. `question-card` already does
this and more (trade-offs per option, recommendation first, local time). Rating 1/1/2. **Skip.**

### obra `test-driven-development` (Jesse Vincent, superpowers)

**What it really does.** The strict form: "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"; code written before its
test is deleted, "delete means delete"; a table of rationalisations refused in advance. Its companion
`writing-good-tests.md` is the better half: **Name the Break** (before writing a test, say what production change should
make it fail, and whether that change is a bug or a decision), derive expected values by hand, a **mutation check** before
finishing, and a warning list that includes "the test greps source text" and "setup and assertion share the same object".

**Keep:** *Name the Break.* It is the cheapest form of mutate-your-checker: a test that cannot name its break is not
a test yet.

**Rating:** novelty 2 (we have mutation testing), complexity 4 to adopt as written, insight 4 for the companion file.

**Conflicts.** The Iron Law contradicts the builder-writes-its-own-verification ruling (2026-08-26) and the
offline geometry sweep (a sweep is a measurement, not a red test), and "delete it, start over" is the review ceremony that
*"use it, break it, grow"* (owner, 2026-11-02) rules out. The repo also holds 72 script files; none was run.

**Verdict: skip the skill; lift Name the Break** into the builder and Codex review briefs.

## The online references

| reference | what it is | worth |
|---|---|---|
| skillselion.com guides (grill-me; improve-codebase-architecture; "Matt Pocock's skills, mapped", v1.1) | third-party maps of the intended flow (`grill-with-docs → to-spec → to-tickets → implement → code-review`, `wayfinder` above it) and of renames; reports grill-me at about 508k installs | useful for history; the repo's `docs/` is newer and primary |
| besthub.dev, "How the grill-me skill turns vibe coding chaos into clear plans" | a republished summary, full text behind a sign-in | nothing beyond the SKILL.md |
| skills.sh, claudemarketplaces.com, claude-plugins.dev, claudskills.com, vibeindex, mcpservers.org | install listings; descriptions copied from SKILL.md frontmatter, sometimes from an older version (one still says improve-codebase-architecture writes GitHub RFC issues) | none; they lag the repo |
| aihero.dev skill pages (`aihero.dev/skills-<name>`) | the published form of the repo's `docs/` explainers (assumed from the link pattern; not fetched) | **high**: the explainers' "Common questions" record real failures with issue numbers, which no listing does |

**Lesson:** for a skill set, read the repo's own explainers before any listing; the listings flatter and lag. Pocock's
explainers are unusually honest about what does not work (issues #449, #589, #607, #746), and those admissions were the
most useful text in the whole set.

## What they assume that we do not have

An issue tracker configured by `setup-matt-pocock-skills`; one `GLOSSARY.md` and numbered ADRs; TypeScript (types as a
feedback loop; the deep-module enforcement answer is a TS linter, dependency-cruiser); a human present at every grilling
round and every seam confirmation; reports in the OS temp dir and assets from CDNs. Every one of these is either absent
here, banned here (numbering), or contradicts a placement rule (`Transient/`).

## What to keep, as one list

1. **The deletion test, and one adapter = hypothetical seam** (codebase-design). For the builder and Codex review briefs.
2. **Tautological / implementation-coupled tests by name, plus Name the Break** (tdd, obra). For the builder and Codex review briefs.
3. **Seams agreed before code, for the few modules that matter** (tdd). The only place his added involvement would buy
   something we lack. A trial, not a rule.
4. **Hot spots first** (improve-codebase-architecture). Decide where to look from `git log`, not from taste.

Plus two small adaptations: the frontier batching rule for `question-card` sessions, and the Fowler smell baseline as
a labelled section of the Codex review brief.

## Verdicts

| skill or source | verdict | one line why |
|---|---|---|
| `grilling` / `grill-me` | adapt | frontier batching only; question-card already covers the rest |
| `grill-with-docs` / `domain-modeling` | adapt, narrowly | per-mod glossary with `_Avoid_` lists, as a trial |
| `tdd` | adapt | anti-patterns and pre-agreed seams into briefs |
| `codebase-design` | keep the vocabulary | the deletion test is the cheapest shape check we could add |
| `improve-codebase-architecture` | adapt | one-module survey on a measured hot spot, report in `Transient/` |
| `prototype` | skip | we already show before we ask |
| `diagnosing-bugs` | skip | debug_process.md covers it; take the no-seam sentence |
| `wayfinder`, `to-tickets`, `implement` | skip | rimflow and the Designer do this |
| Pocock `code-review` | adapt | Fowler smell baseline into the Codex brief |
| RobMitt `grill-me` | skip | question-card is a superset |
| obra `test-driven-development` | skip, lift one idea | Name the Break; the Iron Law fights two of his rulings |
| listings and guides | skip | they lag the repo; read `docs/` instead |

## What the design pass that followed found

`D:\Luke\dev\RimMandrake\design\RimMandrake\2026-11-07-pocock-design\MERGE_DRAFT.md`, measured the same day:

- The Artisan loops' code is not the nonsense feared: 81% to 100% of the lines they add survive, about 6 of 1,300 names
  are unreferenced, and their own tests are literal or behavioural. What is real is accretion (one-line boolean gates
  pile up), copies of harness helpers no prompt told them were shared, and proof rows deleted without a record.
- The top trial is free: mutate the callers of the project's pure kernel gates (38 truth-table tests in 21 mods restate
  one-line gates) and see whether caller mistakes escape.
- Owning interfaces himself: not yet; if he wants it, one module, about 20 minutes a week for four weeks.
