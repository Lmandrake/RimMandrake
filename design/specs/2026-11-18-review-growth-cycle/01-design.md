# Ending the review treadmill on pipeline code: a design for the owner to react to

Written 2026-11-18, 10:20 to 10:50 PM PST, by a detached designer (Fable) for the Conductor. Item
`RIMMANDRAKE_DESIGN_REVIEW_TREADMILL_FIX_COUNT_WAS_FLAT`. Problem statement: `00-problem.md` beside this file.
No second model has read this. **Ruled since:** the owner picked the recommended option on all three decisions of
section 8 by card (2026-11-18, 11:19 to 11:25 PM PST): `design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code. Enacted so far: the control store's page and its later lists
(`design/specs/2026-11-18-pipeline-control-surface/boundary.md`, `polish.md`, `next_version.md`). Sections 5.2 to 5.5
and section 6 steps 4 to 6 are open tickets, not built.

Tags: [measured: source] is a number read or counted tonight, by me or by the report named. [guess ~N%] is my
estimate. "The analyst" means the two read-only reports in `D:\ClaudeWork\rimmandrake\conductor\`
(`control_review_rounds_real_or_treadmill_20261118.md`, `codex_findings_problem_or_polish_20261118.md`); its
problem-or-polish labels are its own judgment at about 70% confidence, and it ran no probes.

Words used here, each with one meaning:
- **Pipeline component:** one piece of the Maturation Pipeline's own machinery (the control store, the coverage
  judge, the publish tool). Not a mod.
- **Probe:** any place where code reads the world outside itself: systemd, a cgroup file, the store, git, a JSON file.
- **Problem, Polish, next version:** as in the owner's Design Versions rule. A Problem is fixed in the current
  version. Polish goes on a list and is not part of passing. Work that extends what the thing does is for the next
  version and never moves the current bars.
- **Boundary page:** proposed here (section 3). One page that says where a component stops.

## 1. What tonight's record shows

| What | Figure | Tag |
|---|---|---|
| First commit of the control store to "live for every launch" | 1 h 1 min (11:53 AM to 12:54 PM) | [measured: `00-problem.md`, git log] |
| Size of `control.py` | 1,823 lines at first commit, 2,799 now | [measured: `00-problem.md`; `wc` at 10:20 PM] |
| Claims per whole review, counted the same way each time | 15, 11, 15: flat | [measured: the analyst, raw review texts] |
| Real problems among them, per review | 2, 0, 2, all mild, all fixed | [the analyst's labels, ~70%] |
| Polish share per review | 78%, 100%, 87% | [the analyst's labels, ~70%] |
| Lines each repair added (code plus tests) | 370 to 420 | [measured: the analyst, git] |
| Claims per 1,000 lines written by a repair | 14 to 25 | [measured: the analyst, `git blame`] |
| Claims per 1,000 lines of older code | about 3 | [measured: the analyst, `git blame`] |
| Dangerous findings across all of tonight's reviews | 3 of 96 tickets, every one from a file's first review, none ever fired | [measured: the analyst] |
| "Could not look" read as "nothing there" | at least 5 separate times in one file | [`00-problem.md`, a reading of claim text, ~80%] |
| Live stops that used the kill path the reviews argued about | 0 of 15 | [measured: the analyst, the control store] |
| Spend on runs whose item was a Codex-review ticket | at least 52.8 million weighted tokens, 18 runs | [measured: `D:\ClaudeWork\rimmandrake\conductor\log.md`; a lower bound, see section 9] |
| All detached runs since midnight PST, for scale | 303.5 million weighted tokens, 86 runs | [measured: same log] |

Four things follow, and the options below are judged against them.

1. **Nothing says where the control store stops.** I read the merged design
   (`design/specs/2026-11-18-pipeline-control-surface/03-merged.md`) in full. It names the store's tables, its verbs,
   seven acceptance tests and a build order. It has no list of the states a run can be in and the moves between them,
   no list of failures the store does not promise to survive, and no list of the input forms it accepts [measured:
   read in full; a search for "state machine", "transition", "out of scope", "non-goal" and "not survive" finds 0 of
   136 non-empty lines]. So every case a reviewer can reproduce is in scope, and a builder has no ground to say "that
   is outside".
2. **The rule for "clean" has no stopping point.** `standing_rulings.md` §Code review says: "Fixing a finding does
   not clean a file. Only a full-file review returning zero significant findings does." Each repair therefore earns
   another whole-file review, and the repair's new lines draw claims at 5 to 8 times the rate of old lines. That rule
   is the engine of the treadmill. He has already made one exception to it, by card on 2026-11-06, for two files:
   "Only serious ones count".
3. **Unit tests were present and did not stop it.** `selftest_control.py` is 1,750 lines with 24 test functions
   [measured: `wc`, `grep`], and every repair was watched red, then green. The tests were added one claim at a time
   (`t_review_round_four_p1` is named for a review round, not a promise). Tests can be the bar
   only when something lists what must be tested. So his two statements tonight ("the only thing I know ... are unit
   tests" and "no proper design document") are one fix seen from two sides, and the missing document is much smaller
   than a design document: three lists.
4. **A written rule did not prevent the recurring mistake.** The control surface's first design pass states the
   four-answers rule as a binding constraint (`01-design.md` §1.2), and `control.py` has an `Unreadable` error for
   its store. The mistake still recurred for the systemd and cgroup reads. Seven pipeline files each define their own
   `Unreadable` or `Unmeasured` error class [measured: `grep '^class'`]; nothing shared forces a caller to look at it.

## 2. What already exists (searched before proposing anything)

Searched `src/RimMandrake/rimflow`, `src/RimMandrake/Utils` and `design/` by file name and by phrase.
| Need | Exists already | Gap |
|---|---|---|
| Sort a finding into Problem, Polish or next version | yes, for mods: the Design Versions rule; `standing_rulings.md` §Mod Design Versions | never applied to pipeline code. The control surface is labelled Design Version 0.1.0 (`03-merged.md`), but nothing lists what 0.1.0 contains |
| A reviewer that refuses flaws and not polish, two looks, then stops | yes, for mod judges: §The judge refuses flaws, not polish (his card, 2026-11-17) | not applied to code review |
| A refusal that carries its evidence, what would pass, and the smallest fix | yes: `src/RimMandrake/rimflow/refusal_contract.py` (`check`, `status`, `repair`) and its calibration file | no family for code review |
| Tests that run at the door for pipeline code | yes: `src/RimMandrake/Utils/pipeline_tests.json`, 37 path patterns and 64 tests, run by `./publish` [measured] | nothing says which tests a component owes |
| The test is written with the item, and watched red | yes: two standing rulings | per item, not per component |
| A CLEAN or DIRTY record per file | yes: `src/RimMandrake/Utils/code_review_status.py` | its meaning of "clean" is point 2 above |
| Running new machinery in shadow (it decides and records, and refuses nothing) | yes, twice: `ticket_preflight.py` at the ledger doors, `evidence_gate.py` | a habit of two tools, not a rule for new components |
| Turning one mod or one family on or off at once | yes: the control store's scope switches | not yet used to stage a new component |
| A lint at `./publish` that reads the code's structure, with a counted allowlist | yes: `src/RimMandrake/Utils/call_deadline_lint.py` (subprocess calls without a deadline) | none for "could not look" |
| A page that bounds a pipeline component, or a promises list for one | **no.** `design/concepts/<Mod>/contracts_*.json` are scene contracts for mods; `promise_scan.py` reads the Conductor's promises in a reply | this is the new part |

So the design is mostly re-use. Four things would be new: the boundary page, a small checker that ties its promises
to tests, one shared probe-result type with its lint, and a code-review brief.

## 3. Four options

They differ in **what does the bounding**: a judge's rule, a written page, the running system, or the code's shape.

### Filter only: keep building as today, sort the findings

- **What it is.** One review, then one recheck of the repairs, then stop. A finding is a Problem only if it names an
  ordinary-day input (a command we run, a file we write, a state we have been in) and the record, gate, commit or
  spend it gets wrong. Everything else is written to a polish list and not fixed. This is the analyst's sorting rule
  and the option the 7:47 PM card recommended.
- **Why someone would pick it.** It is one ruling and one prompt edit, in place tomorrow. Applied to tonight it would
  have kept 4 of the 35 claims in reviews two to four [the analyst].
- **What it costs.** About 1 to 2 million weighted tokens to enact [guess ~60%].
- **What it leaves open.** "Ordinary day" is judged afresh by an agent for every finding, with nothing written to
  judge against: the first review called paths with spaces polish, and the third filed the same thing as a defect
  [measured: `00-problem.md`]. The builder still has no ground to decline. Tests stay a pile, one per claim. A new
  component still goes live in an hour. "Could not look" is still caught only if a reader happens to see it.

### Boundary page: say where the component stops before code, and make its promises the tests

- **What it is.** Before code, one page per component with four short parts: its life cycles, the failures it does
  and does not survive, the closed set of inputs it accepts, and its promises, each tied to a named test. "Done"
  means every promise has a test that has been seen to fail. A review checks the code against the page and nothing
  else. Section 5 describes it in full.
- **Why someone would pick it.** It is the only option that gives the builder, the reviewer and the owner the same
  place to point at and say "inside" or "outside". It is his Design Versions rule applied to a component: the page
  is what version 0.1.0 *is*.
- **What it buys.** A claim outside the page costs one line on a list, where tonight it cost 370 to 420 lines that
  drew new claims. Tests are counted against promises, so "can a fix regress something" has an answer: a promise
  test goes red at `./publish`.
- **What it costs.** A page and one fresh read of it per new component, about 1.5 million weighted tokens before any
  code [guess ~50%], plus building the checker and the brief once (section 7). The page can be wrong: a real case
  left off it is not found by a reviewer told to stay inside it.
- **What it leaves open by itself.** A page is prose. Point 4 of section 1 says prose did not stop "could not look".
  And a page says nothing about when a new component may act on real runs.

### Run it, don't read it: evidence from running replaces review rounds

- **What it is.** After one first review, a component earns trust by running, not by more reading. It runs in
  **shadow** (beside the old path, deciding and recording, acting on nothing), then a **drill** exercises each verb
  that kills, deletes, locks or launches on a throwaway unit in real systemd, then it acts for one mod, then for all.
  A test harness makes each probe fail in turn. Findings are what the shadow disagreed on and what the injected
  failures broke; each is already a reproducible case.
- **Why someone would pick it.** Four reviews argued about a kill path that live runs used 0 of 15 times. A
  ten-minute drill would have run it for real. The one Codex-origin finding that was actually firing tonight (advance
  refusals going uncounted) was confirmed by reading live state, not code [measured: the analyst].
- **What it costs.** Time to live goes from an hour to between half a day and two days [guess ~50%]. A shadow
  harness and a failure-injection harness, about 8 to 12 million weighted tokens once [guess ~40%].
- **What it leaves open.** Rare but ordinary sequences do not show up in a short shadow: the hold bug the analyst
  rated dangerous needed a hold placed on an already-stopped mod and never fired in 5,604 ticks [measured: the
  analyst]. It still does not tell a builder where to stop.

### Unwritable mistakes: rules on the shape of the code, enforced by tools, no document

- **What it is.** Three rules checked at `./publish`. Each life cycle is one table in the code (state, event, next
  state), moved by one function that refuses any unlisted move. Every probe returns a four-answer value that cannot
  be used as a list or a truth value. A component takes structured inputs built by our own code and never parses
  free text.
- **Why someone would pick it.** 20 of the 43 claims were about four small life cycles written as scattered
  conditions; 13 were about parsing and tooling that a structured input would delete; at least 5 were "could not
  look" [measured counts from `00-problem.md`; the sorting is ~80%]. No reader and no judgment are involved.
- **What it costs.** Rewriting the core of `control.py`, 8 to 15 million weighted tokens [guess ~40%], plus the type
  and lints, about 4 to 6 million [guess ~50%]. It also changes live machinery again, which is how tonight began.
- **What it leaves open.** It bounds how code is written, not what the component promises. A reviewer can still say
  "it should also survive X", and nothing says no.

## 4. Comparison

| Question from the brief | Filter only | Boundary page | Run it, don't read it | Unwritable mistakes |
|---|---|---|---|---|
| What bounds a component | a judge's rule, per finding | a written page, before code | what real runs do | the code's own tables |
| What "done" means | two looks happened | every promise has a test seen to fail | N clean shadow runs and a drill | lints pass |
| Unit tests are the bar | no | yes | partly (injection tests) | partly (table tests) |
| What a review may do | two looks, sorted findings | two looks, against the page only | one look, then running | little left to review |
| How new code reaches live runs | unchanged (one hour tonight) | unchanged unless added | shadow, drill, one mod, all | unchanged |
| "Could not look" prevented by structure | no | no (prose) | found by injection | yes |
| Cost to enact [guess] | 1 to 2 million | 13 to 17 million | 8 to 12 million | 12 to 21 million |
| Slows a new component by | nothing | about an hour (the page) | half a day to two days | nothing after the rewrite |

## 5. Recommendation: the boundary page, with one part taken from each of the last two options

**The boundary page is the spine.** A filter without a page is re-judged every time; tests without a page pile up;
shape rules without a page bound form and not scope. The page is the only thing all four need. Two parts are added
because the page alone is prose: the four-answer probe type with its lint (from "unwritable mistakes") answers
question 5, and shadow-then-drill (from "run it, don't read it") answers question 4. The rest of those two options
(rewriting life cycles as tables, a standing checker of the books against systemd) is not adopted now.

### 5.1 What bounds a component: the boundary page

- **Where.** `design/specs/<component>/boundary.md`, versioned with the component's Design Version.
- **Who and when.** The agent that designs the component writes it before any code. One fresh reader that did not
  write it reads it once and may ask one thing only: "name an ordinary input or failure this page neither accepts nor
  refuses." A hole found here costs a line. A builder does not start without the page.
- **The four parts.** Entries are named with words, never numbered, and a test carries the same name.

```
BOUNDARY: control store, Design Version 0.1.0        (an illustration only; the real page is the pilot's work)
LIFE CYCLES   every move not listed is refused, in one function
  run          admitted -> started -> ended | killed       admitted -> refused | cancelled
  stop order   pending -> seen -> done                      pending -> done (the run ended first)
SURVIVES      one promise each
  locked-store        another writer holds the store for up to 3 s
  end-races-kill      a run's own end receipt lands just before or just after a kill
  same-command-twice  any command sent twice has the effect of once
DOES NOT SURVIVE   it says so, stops, and records nothing it did not verify
  two-failures-at-once   a kill that fails AND a cgroup that cannot be read
  child-cgroups          a unit that makes its own child cgroups (no pipeline unit does)
  corrupt-store          nothing launches; `pipe doctor` names the fix
ACCEPTS       anything else is refused by name before any effect
  launches only as launch_unit(unit=..., payload=[...]); no systemd-run command line is ever read
  a unit named with or without `.service`; deadlines of 1 whole second or more; paths without spaces or `$`
PROMISES      each is one test of the same name
  kill-verified-dead   `--kill` returns only after the whole process group is verified dead   (his words, 11:28 AM)
  off-blocks-starts    after `pipe off` returns, nothing that had not begun can begin
  void-gives-back-once a voided run's charges come back exactly once
  probe-never-lies     a probe that could not look never reads as an answer (on every page)
```

- **How small it can be.** Three parts are required: ACCEPTS, DOES NOT SURVIVE, PROMISES. LIFE CYCLES is required
  only when the component keeps state between calls. LIMITS is required when the component enforces any limit (a
  cap, pause, timeout, retry bound or text cut): each one with the danger it guards and the evidence that the danger
  happens, or it is removed, not tuned (added 2026-11-19 by Crystallize 2026-W47: `design/RimMandrake/standing_rulings.md`,
  the limits ruling of 2026-10-31 to 2026-11-17). A tool with no state and no probes has a page of about five
  lines. The control store, the largest case tonight, needs about 60 lines [guess ~60%]. A page over about 80 lines
  means two components. The evidence that so little is enough: 33 of tonight's 43 claims sort onto four life cycles
  and four input threads [measured counts, `00-problem.md`], so about eight entries would have placed three quarters
  of the claims inside or outside before any code existed.
- **Which code owes one.** A pipeline component (a path matched by `pipeline_files` in `pipeline_tests.json`) owes a
  page when it is new, or when a change adds a state, an input form, a probe, or a verb that kills, deletes, locks or
  launches. A one-line fix does not. Existing components get a page when they are next extended, not in a sweep.
- **Changing the page.** Adding a survived failure, an accepted input or a promise after the page has passed is
  next-version work: it is written up for version 0.2.0 and never added to 0.1.0's bars. Moving a failure to DOES
  NOT SURVIVE is accepting a risk: the Conductor decides it (delegated, logged) and he sees it in the daily digest.

### 5.2 What "done" means, and how tests become the bar

- **Done** is: every promise and every SURVIVES entry has a test of the same name; each such test has been seen to
  fail (it ships with one deliberately broken stand-in that it must reject, the `mutate-your-checker` pattern); one
  test shows an input outside ACCEPTS is refused and one shows an unlisted move is refused; the probe test of 5.5
  passes; all are registered in `pipeline_tests.json`, so `./publish` runs them.
- **Who writes them.** The builder, with the code, as the standing ruling already requires. What changes is where the
  list of tests comes from: the page, written before the code, not the reviewer's claims, written after it.
- **A small checker** (`boundary_check.py`, new, about 150 lines [guess ~60%]) reads the page, finds the test for
  each named entry, runs each broken stand-in, and prints `promises covered N of M`. `./publish` refuses on a
  promise with no test.
- **Tests as the bar.** After done, a change to the component passes when the promise tests pass at `./publish`. It
  is owed a review only if it changed the page. Every admitted finding lands as a red test first, named for the
  promise it broke, so a later fix that undoes it turns the door red. That is the regression protection he asked
  for, and it needs no reader.

### 5.3 What a code review may do after this

The judge's four rules, carried over to code with the page in the place of the mod's promises.

- **When it runs.** Twice per component version, never more: one full inspection when the component is first done
  (page, code and tests, the whole file), and one recheck that reads only the repairs. The first inspection is kept
  because every dangerous finding tonight came from a file's first review [measured: the analyst].
- **What a finding must contain to be admitted as a Problem.** One of three reasons, with the page quoted:
  1. a promise is not kept: the promise, an input inside ACCEPTS or a failure inside SURVIVES that breaks it, and
     the record, gate, commit or spend that comes out wrong;
  2. a promise could be broken and no test would go red: the broken component that would get through;
  3. the page or a test is itself wrong.
  Each is a refusal record (`refusal_contract.py`, a new `code_review` family): evidence, what would pass, the
  smallest fix. The smallest fix is "refuse the input" before "handle the input".
- **Where everything else goes.** "It should also survive or accept X" goes to `next_version.md` beside the page.
  A stricter test with no broken component described, style, and robustness go to `polish.md` beside the page: one
  line each, in the repo, no ticket, no repair lane. That is his "We'll get to that later". An input outside
  ACCEPTS that is mishandled and not refused is a Problem only if a call site in the repo or a documented command
  produces it (checked by search, as the analyst did); otherwise it is polish.
- **What stops it.** The count of looks is two. The recheck raises something new only when a repair itself broke
  something, quoting the changed lines. What is left after the recheck goes to him as a short list in the digest,
  not to another reviewer. A third look happens only for a new page version.
- **Calibration.** The standing ruling lets only a calibrated brief's refusal send work back. Tonight's 35 claims
  with the analyst's labels (4 problems, 31 polish) are a ready first calibration set [measured: they exist; the
  labels are ~70%].
- **Measured both ways.** Each look appends one row to a tally. Polish lines that later fire in real runs are the
  evidence to tighten the rule; first inspections that admit nothing are the evidence to drop even those.

### 5.4 How a brand-new component reaches live runs

Tonight's design did say "cut over with new starts off" (`03-merged.md` §5), and the store was still live for every
launch an hour after its first commit [measured]. One sentence in a design was not enough, so the steps become
switches:

1. **Offline:** done, as in 5.2.
2. **Shadow:** it runs beside the old path on real launches, records what it would have done, and acts on nothing.
   It leaves shadow after 20 real launches with no unexplained disagreement [the number is a guess; a dial]. The
   control store saw 91 runs in about 8 hours tonight [measured: the analyst], so that is roughly two hours.
3. **Drill:** each verb that kills, deletes, locks or launches is run once on a throwaway unit in real systemd, not
   on a fake. Shadow cannot cover these.
4. **One mod, then all,** using the control store's own scope switches.

Two limits. Verbs that only read or only block new starts (tonight: `pipe show`, `pipe off`) skip steps 2 and 3 and
can be live the same hour, because being wrong costs little; this follows his rule that checking should be
proportional to the cost of being wrong. And while a component is in steps 2 to 4, one run at a time edits it:
tonight several runs edited `control.py` at once [`00-problem.md`].

### 5.5 How "could not look" read as "nothing there" is prevented by structure

Three mechanical parts; none depends on a reader noticing.
1. **One shared result type for probes** (new, small). A probe returns exactly one of: a value, empty, could not
   look (with the cause), failed (with the cause). The last two cannot be used as a list, a number or a truth value;
   doing so raises at once. The line round three faulted, `(_procs(cg) or [])` [measured: `00-problem.md`], would
   have raised in its first test run.
2. **A lint at `./publish`,** built like `call_deadline_lint.py`: in pipeline files, an `except` that returns an
   empty value, and `<call> or []` (or `{}`, `0`, `None`), are red unless on a counted allowlist. A crude search for
   those shapes finds 14 lines in `control.py` today [measured: `grep -c`; a sanity reading that the lint would have
   something to see, not a count of bugs].
3. **One injected-failure test per component:** the harness makes each probe answer "could not look" in turn and
   asserts that every verb either says UNREADABLE or UNMEASURED or exits non-zero, and never prints an ordinary
   answer. This is the promise `probe-never-lies`, and it is on every page.

## 6. What happens to tonight's state

State at 10:23 PM PST [measured unless tagged]:
- 12 of the 96 Codex-review tickets still have live item files: 5 minor, 6 polish, 1 unverified list. None is
  dangerous. (The analyst counted 24 open at 7:15 PM; lanes closed the rest.)
- `RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_FOUR_FIFTEEN_UNTRIED` holds 10 claims nobody verified or fixed. The analyst
  labels all 10 polish [~70%].
- `control.py` has about 310 lines of feature work (consumables, the queue) that no review has read [measured: the
  analyst].
- `code_review_status.py check` reads DIRTY for all seven files reviewed tonight: `control.py`, `coverage_judge.py`,
  `maturation_autonomy.py` and `land.sh` were never marked clean; `designer_stage.py`, `publish.py` and
  `seat_sync.py` changed since their mark.
- Three finished `designer_stage.py` fixes sit uncommitted in a bundled clone (ledger note on
  `RIMMANDRAKE_FIX_OPEN_CODEX_FINDINGS_ONE_AGENT_KEEPS_CONTEXT`) [not re-checked tonight].
- `RIMMANDRAKE_MEASURE_TWO_MORE_REVIEW_ROUNDS_BEFORE_ANY_FILTER` is open; the tally file it names was never written.

Proposed, in order, with the control store as the pilot of this design:

1. **Do not roll the control store back.** On ordinary days it works: 91 runs and 15 stops on its books, no
   dangerous finding open [measured: the analyst].
2. **Write its boundary page now,** from the merged design, his rulings and the 43 claims (they are the raw material
   for ACCEPTS and DOES NOT SURVIVE). One fresh read of the page.
3. **Sort every open control-store claim against the page.** Inside: red test, fix, no review round. Outside:
   `polish.md` or `next_version.md`. Going by the analyst's labels, few or none of the 10 land inside [guess ~60%].
4. **Shrink the code to the page, once, by one run.** Where the page says "refused", delete the handling. The
   clearest case: the reader of systemd-run command lines, written tonight to answer a claim and then faulted itself
   [measured: `00-problem.md`], goes away if `launch_unit` takes the unit name and payload as fields. All 9 call
   sites are ours and use one form [measured: `00-problem.md`].
5. **Run the kill drill** on a throwaway unit: no live stop has used that path yet.
6. **Give `control.py` its two looks against the page** (this covers the 310 unread lines), then stop.
7. **The other six files** had their first review tonight. They are owed at most the one recheck, no page until
   they are next extended, and their open tickets are sorted by the rule in 5.3 using "produced by a call site or a
   documented command" in place of a page.
8. **Land the three finished `designer_stage.py` fixes** from the bundle on their passing tests; the work exists.
9. **Close the two-more-rounds item as overtaken** by his stop at about 8:24 PM. Its condition was met on the analyst's
   count: 15, 11, 15, with a polish share of 78% or more.

Step 3 moves work he chose to fix ("Fix all 24", by card at 7:47 PM) onto a later list, so it is his decision
(section 8).

## 7. What it costs and what it slows

All figures are weighted tokens. For scale, four of tonight's detached repair runs cost 0.8 to 5.4 million each
[measured: run-end lines in the Conductor's log].

| Piece | One-time cost | Tag |
|---|---|---|
| `boundary_check.py`, the page template, the builder's start check | about 2 million | [guess ~55%] |
| Probe result type, the lint, its first allowlist | about 3 million | [guess ~50%] |
| Code-review brief, the `code_review` refusal family, calibration on tonight's 35 claims | about 3 million, plus Codex's own reading | [guess ~50%] |
| Control-store pilot: page, fresh read, sort, shrink, drill, two looks | about 8 to 12 million | [guess ~45%] |
| **Total to enact** | **about 16 to 20 million** | [guess ~45%] |

Against that: runs on Codex-review tickets cost at least 52.8 million tonight [measured, a lower bound], and by claim
more than half of the landed work was polish [the analyst, ~70%]. So one night of the treadmill cost more in polish
alone, roughly 25 to 30 million [guess ~50%], than enacting this.

Per new component afterwards: about 1.5 million for the page and its read, 1 to 2 million for shadow and drill [guess ~50%].

What it slows:
- A component that kills, deletes, locks or launches: from an hour to about half a day before it acts on all runs.
- Parallel work on one component: one editing run at a time until it has left its two looks.
- A real but unlisted case waits on a polish list until it fires or someone promotes it. Tonight that risk was
  small: 3 dangerous in 96, all at first review, none fired [measured: the analyst]. It is not zero.

## 8. The owner's decisions

**1. How should a new piece of pipeline machinery be bounded from now on?**
Evidence against "keep going as we are": 15, 11, 15 claims per review with 2, 0, 2 real problems; repairs drew
claims at 5 to 8 times the rate of older code.
- *One page before code, and its promises are the tests (Recommended).* Adds a shared probe type and a shadow-then-
  drill step. About 16 to 20 million weighted tokens to enact; a new component that kills things takes half a day
  to go fully live.
- *Sort the review findings only.* One ruling, in place tomorrow; nothing written to sort against.
- *Trust running over reading.* One review, then shadow and drills; no page.
- *Rules on the code's shape only.* Rewrites the control store's core; no page.

**2. When is a piece of pipeline code "clean"?**
This changes his standing rule ("Only a full-file review returning zero significant findings" cleans a file), which
section 1 identifies as the engine of the treadmill.
- *When every promise on its page has a test and it has had its two looks (Recommended).* A later edit stays clean
  while those tests pass and the page is unchanged.
- *Only serious findings block.* His 2026-11-06 answer for two files, extended to all pipeline code; no page needed.
- *Keep today's rule.* A whole-file review that finds nothing; the treadmill's cost returns with the reviews.

**3. What happens to tonight's open review findings and the control store?**
12 tickets are open (5 minor, 6 polish, 1 unverified list) plus 10 unverified claims on the control store; none is
dangerous. At 7:47 PM he picked "Fix all 24"; at about 8:24 PM he stopped the review cycle.
- *Write the control store's page first, then fix only what falls inside it (Recommended).* The rest goes on its
  later list; the store is shrunk to the page and drilled.
- *Fix everything still open, as picked at 7:47 PM, with no further reviews.* About 5 to 10 million weighted tokens
  [guess ~40%], mostly on polish.
- *Fix nothing more now.* Every open finding becomes a later-list line until one fires.

Left to the Conductor under Evidence-for-Ask, each a dial he can turn later: the shadow length (20 launches), who
approves a DOES NOT SURVIVE entry (the Conductor), and which model does the fresh read of a page (per the ladder).

## 9. Not known

- Whether the pattern holds as strongly on the other six files. Only the control store was read claim by claim; the
  analyst's per-file table rests on ticket prose [~70%].
- Whether any claim is truly reachable: neither analyst ran a probe, and neither did I.
- Whether Codex will stay inside a page when told to. The calibration in 5.3 is the test of that.
- Codex's own token use tonight. The 52.8 million counts Claude-side detached runs matched by item name, so repair
  lanes filed under another item's name and everything Codex read are missing from it.
- This design has had no second reader. If he leans toward the recommendation, one blind external pass on section 5
  before enacting would cost little.
