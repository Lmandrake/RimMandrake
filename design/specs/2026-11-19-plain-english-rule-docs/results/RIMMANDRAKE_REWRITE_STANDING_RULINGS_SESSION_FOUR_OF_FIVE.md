# Result: `RIMMANDRAKE_REWRITE_STANDING_RULINGS_SESSION_FOUR_OF_FIVE`

Session 4 of 5 of batch `RIMMANDRAKE_REWRITE_STANDING_RULINGS_LARGEST_HOME_FILE` (`batch_plan.md`, order 8). File:
`design/RimMandrake/standing_rulings.md`. Run 2026-11-24.

Base: ec58f1e220ef18a647e7cab9ed1e66c680cc3bea

Also: design/RimMandrake/CLAUDE.history.md

The `Also:` line is for two item paths that moved to `items/closed/` (see the stale lines).

Scope: the `## ` sections from `## Mod Design Versions use Semantic Versioning` up to, but not including, `## The nightly
checks finished mods only`. The text before and after the scope is byte for byte the same as the base (compared by a
script: True, True). Every heading of the file is unchanged (compared by a script).

## Scores

"Section" is the scope. "Rule text" is the same text with each `*"..."*` quote replaced by one word (`batch_plan.md` §The
STE target).

| measure | before | after |
|---|---|---|
| bytes (section) | 37,174 | 41,685 |
| words in linted prose (section) | 5,890 | 6,609 |
| STE violations per 100 words (section, quotes included) | 4.53 | 3.31 |
| STE violations per 100 words (rule text) | 3.93 | 2.44 |
| sentences over 20 words (section) | 119 | 66 |
| sentences over 20 words (rule text) | 84 | 34 |
| flagged lines (mechanical, section) | 5 (4 pronoun, 1 shout) | 2 (1 shout, 1 coded id `L4`, which the line explains) |
| whole file: STE per 100 words, long sentences, flagged lines | 3.61, 431, 49 | 3.41, 378, 46 |
| lines that a cold reader cannot act on (hand count, by the writer) | 13 | 0 |

### The 34 long sentences that stay in the rule text

They are of these kinds: a line that holds an owner quote or its evidence (record, date, item); a sentence that holds a
command, a path or a list in brackets; a bold lead that the lint joins to the next sentence; a pinned phrase that a test
reads ("Hand off only with the evidence that …"). A few rule sentences of 21 to 27 words stay as one sentence. A split of
the sentence about the list's reversion changed its meaning (third read, below), so the writer undid that split.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "(§Evidence-for-Ask, below)" | the place | "in this file" |
| "The Conductor decides both" | which two | the two questions are named |
| "spec 18c" | which spec | "decision 18c of the pipeline spec" |
| "moves its book entries" | which books | the tick's `state.json` |
| "gives back a coverage look it applied (the grant stands again …)" | what a look and a grant are | `coverage_judge.py release` grants one look of the Designer's coverage judge |
| "the fold of its lines" | what a fold is | "the sum of the void and unvoid lines, read in order" |
| "the steward" in the list of pipeline programs | which one | the run that `maturation_autonomy` starts |
| "accepts a root or a flagship pick" | which | the concept's `root` and the choice of showcase scene 1 |
| "The fault loop" | what it is | defined at its first rule |
| "a family refusing most of what it sees" | what a family is | one judge brief, or one gate's set of clauses |
| "(owner 2026-11-16, below)" | nothing is below | the item is named |
| "the walk identity", "deciders", "an owner bar" | what they are | each has its meaning beside it |
| "a ghost run", "the road back" | what they are | each has its meaning beside it |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 2 (`rule_doc_lint.py keep`) | a copy with one number, one path, one id and one time removed | 4 lost, exit 1 |
| check 1 (`checkable.py compare`) | the same copy | 2 lost (the path, the id), exit 1 |
| check 2 | the final bytes | 1,205 spans, 0 lost |
| check 1 | the final bytes | 662 items, 0 lost |
| `rule_doc_lint.py selftest`, `checkable.py selftest`, `batch_done.py selftest` | — | PASS; 19 of 19; GREEN 12 planted cases |
| 20 tests that read the file, and the selftests of `run_void.py` and `coverage_judge.py` | the draft after the first reader pass | 18 pass, 4 fail |
| the 4 failures, on the base text | `case_four_rules_two_looks.py`, `acceptance_stop_rules_calibrated.py`, `code_review_brief_accept.py`, `selftest_conductor_authority.py` | the same output on the base, so this rewrite did not cause them |

The 22 tests ran again on a later draft. `selftest_touching_code_cost_rule.py` then failed on a pinned phrase that a late
split had changed. The writer put the phrase back, and the test passes. On the final bytes 9 of the 22 ran and passed.

Names of people and roles, counted by a script in the scope: each is the same or higher. All 27 owner quotes are word for
word.

The prose check of `./publish` was run by hand five times. The writer repaired each named line that the code explains.

## What the meaning read found

A fresh Opus reader (`rm-judge`, model opus) read the old and the new text of the scope. The reader got no reasoning of the
writer. The reader listed 22 places. Six needed repair; the other 16 were checked additions and corrections.

| first draft | why it was wrong | repair |
|---|---|---|
| "That evidence is one of these:" and four items | reads as a closed list; test 2 lists seven, so a judge lost "my verdict must stay independent" | "The ones that come up most here:" |
| "The Conductor reviews every other card first" | "other" pointed at nothing | "every card that is not about one of the five acts" |
| "parks a concept whose spend reaches twice the item's cap" | too wide: only the judge-and-rework loop's spend counts | the loop is named |
| "A launch that never started adds no fault" | the same refusal after a finished repair counts once | the exception is written |
| "The tick starts one repair run … resets the count" | reads as an endless loop | the killed repair run and the two-repair limit are written |
| the kinds of a changed file | the whole-file case was missing | the case is written |

The same reader then read each repair and each edit that the prose check caused (28 lines: all SAME or TRUE), and then the
later sentence splits (14 lines: two changed, both undone or repaired with the reader's wording or the old wording).

Lines that no reader read in place: the reader's own wording for the tick's books; the undone split; the undone pinned
phrase; "the 45 minutes after his last deliberate interaction"; "one blind judge's run of the blind challenge"; the meaning
of an owner bar (the reader read its source line and called it TRUE); the lines that were only re-wrapped.

## Conflicts and stale lines: decided

| line | the two sides | decision | rule and evidence |
|---|---|---|---|
| "nothing launches" at `system_fault`; "its faults go on the mod's own count" | the tick starts one repair run; a launch that never started adds no fault | the code's behaviour is written; the `run_void.py` docstring is corrected too | 1: `fault_repair_step`, `FAULT_REPAIRS_MOST`, `form_fault.py` |
| "Every refusal that reaches it carries a class; an unclassed one counts as form and is logged for the census" | "There is no table of refusal kinds" | the line is replaced | 1: `form_fault.fault_class`, the boundary page |
| "a C# change by source file" | the relation is by member and switch section | the code's behaviour is written | 1: `rerun_relation.py` docstring |
| "an owner bar is never repaired: it is a card for him" | the Conductor's recorded act also changes one | both are written | 2 and 1: the ruling of 2026-11-19; `refusal_contract.diffguard`; `criteria_fixer.md` |
| "The Judge makes the call" (Problem or Polish) | the Conductor decides each move to Polish | both are written, the later one named | 2: card 2026-11-23 |
| "the fourth refused verdict … raises `REFUSAL_NOTHING_COULD_EVER_PASS`" | the third refusal of one clause raises it too | written | 1: `refusal_contract.submit` |
| coverage judge "parks on a second refusal while he is away" | only a concept that needs his answer | written | 1: `coverage_judge.py` (`designer_can_fix`) |
| two item paths | both items are closed | `items/closed/`; the old paths are in `CLAUDE.history.md` | 4 |
| `2026-11-13-mod-design-versions.md`: "Not built: the pass record" | `version/passes/` and the pass tag exist | corrected to "Built since" | 1: `PASS_RECORD_DIR` in `maturation.py` |
| `coverage_judge.py` docstring: "only his own word on the item lifts" a park | its own messages name the Conductor's act too | corrected | 1: `his_answers` in `designer_stage.py` (the reader read it) |

Sent to the owner (rule 5): none.

## Could not determine

- Which agent "the steward" was that wrote the 203-checks message of 2026-11-21 (§After a change). The line stays as it was.
  The records of item `RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203` would show it.
- "the bars of 2026-11-13" as the meaning of "today's bars" agrees with the section's date. No other record was read.

## What this run did not test

- No agent run read the new text to do work. No measurement shows that an agent acts better on it.
- Session 5 rewrites the rest of the file. This run did not touch those sections.
- The `CLAUDE.md` pointers into this file were not read one by one. Each heading in scope is unchanged.
- 13 of the 22 tests were not run again on the final bytes.
