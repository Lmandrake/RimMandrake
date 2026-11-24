# Result: `RIMMANDRAKE_REWRITE_STANDING_RULINGS_SESSION_FIVE_OF_FIVE`

Session 5 of 5 of batch `RIMMANDRAKE_REWRITE_STANDING_RULINGS_LARGEST_HOME_FILE` (`batch_plan.md`, order 8). File:
`design/RimMandrake/standing_rulings.md`. Run 2026-11-24.

Base: 13108164fbdfe7ba13d39c240080f9841758b530

Scope: the `## ` sections from `## The nightly checks finished mods only` to the end of the file (18 sections). The text
before the scope is byte for byte the same as the base. Every heading of the file is unchanged (both compared by a script).

## Scores

"Section" is the scope. "Rule text" is the same text with each `*"..."*` quote replaced by one word (`batch_plan.md` §The
STE target).

| measure | before | after |
|---|---|---|
| bytes (section) | 38,219 | about 43,900 |
| words in linted prose (section) | 5,805 | about 6,740 |
| STE violations per 100 words (section, quotes included) | 4.12 | 2.64 |
| STE violations per 100 words (rule text) | 3.88 | 2.10 |
| sentences over 20 words (section) | 108 | 66 |
| sentences over 20 words (rule text) | 88 | 42 |
| flagged lines (mechanical, section) | 21 (19 shout, 2 pronoun) | 7 (7 shout: headings and the part name DOES NOT SURVIVE) |
| whole file: STE per 100 words, long sentences, flagged lines | 3.41, 380, 46 | 3.16, 338, 32 |
| lines that a cold reader cannot act on (hand count, by the writer) | 12 | 0 |

The long sentences that stay in the rule text are of these kinds: a line with an owner quote or its evidence (record, date,
item); a sentence that holds a command, a path or a list in brackets; a bold lead that the lint joins to the next sentence.
Some rule sentences of 21 to 27 words stay as one sentence.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "his to overrule" | whose | "the owner may overrule it" |
| "`./pipe stop` (three modes, next-but-one section)" | which section | §One control store and `pipe` |
| "a stopped run spends no trial (next section)" | which section | §Stops that the work did not cause |
| "The Conductor's journal hold" | what the hold is | its meaning from `maturation.py` is beside it |
| "a Designer chain" | what it is | "each end starts the next" |
| "Consumables are reservations" | what a consumable is | defined, with the coverage look |
| "the harvest chain and a pending run-now" | both | each has its meaning beside it |
| "the limits ruling … above" | which | §No limit without the danger it guards |
| "any unrouted site" | unrouted through what | `control.launch_unit` is named, with its two exempt lists |
| "a composed member's packageId never loads" | a member of what | `mandrake.rm.biomes` |
| "`*south*` mask glob" in the trap list | what the trap is | the glob also matches `X_southm.png` |
| "Dumps and harvests decay" | what a harvest is | both words have their meaning beside them |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 2 (`rule_doc_lint.py keep`) | a copy with one number, one path, one id and "31 days apart" removed | 4 lost, exit 1 |
| check 1 (`checkable.py compare`) | the same copy | 2 lost (the path, the id), exit 1 |
| check 2 | the final bytes | 1,218 spans, 0 lost |
| check 1 | the final bytes | 671 items, 0 lost |
| `rule_doc_lint.py selftest`, `checkable.py selftest`, `batch_done.py selftest` | — | PASS; 19 of 19; GREEN 12 planted cases |
| 22 tests that name the file | the text after the last reader repair | 18 pass, 4 fail |
| the 4 failures, on the base text | `case_four_rules_two_looks.py`, `acceptance_stop_rules_calibrated.py`, `code_review_brief_accept.py`, `selftest_conductor_authority.py` | the same output on the base, so this rewrite did not cause them |
| `selftest_retired_era_gone.py` | an early draft, then the last text | 2 era lines (FOUNDRY without "retired"), then PASS |
| `selftest_scene_snapshot.py`, `selftest_scene_runner_driver.py` | after the docstring edit | 41 of 41; 22 of 22 |

Names of people and roles, counted by a script in the scope on an early draft: none is lower. All 45 owner and card quotes
are word for word. The prose check of `./publish` was run by hand four times. Each named fault was repaired.

## What the meaning read found

A fresh Opus reader (`rm-judge`, model opus) read the old and the new text of the scope. The reader got no reasoning of the
writer. The reader listed 13 places:

| first draft | why it was wrong | repair |
|---|---|---|
| "Every live scene runner shares it. The item is closed." | false: 3 runners use it, and the owed duty was lost | the 3 users are named; the **Owed** bullet is back |
| "No Relentless launch site is left in the code" | false: `item_exam.py` launches with that family | the launch sites that remain are named |
| "fails on any launch site that does not go through it" | two lists of sites are exempt | both lists are named |
| "The one measured reading" of the code-review sort | a later reading followed it | all three readings are listed |
| "stay inside a tool" (list dollars) | lost "only" | "only inside" |
| "The Conductor answered, and he may overrule" | "he" read as the Conductor | "the owner may overrule it" |
| "A component also owes a page" | wider than pipeline machinery | "Pipeline machinery also owes" |
| the journal hold, per mod | the hold is per stage | "for the stage" |
| the gloss of "whatever tier" | left out the full list | the full list is named |
| "until he rules" (a save for review) | the section says "until he says delete" | points to that section |
| `mod_owner_hold.py hold` | no publish step | "Then publish `mod_owner_hold.json`." |
| "An instrument that cannot see is a user-level rule" | nobody can act on it | "The rule about …" |
| "Those lines are:" | closed list | "Those lines include:" |

The same reader then read each repair and the later edits (16 places). 15 were SAME or TRUE. One was false: a third sort
(2026-11-24 08:51Z) was missing. The writer read that sort in `git show dfce52f1c1:infrastructure/state/judge_calibration.json`
and took the reader's wording.

Lines that no reader read in place: that last wording; "retired" on the two FOUNDRY lines; the `*south*` line (its source is
`instrument_traps.md`); the lines that were only re-wrapped.

## Conflicts and stale lines: decided

| line | the two sides | decision | rule and evidence |
|---|---|---|---|
| "the 13 publish tree checks" | 22 checks now | both, with dates | 1: `publish_tree_checks.json` |
| "every `systemd-run` launch" is stopped by the pause | `NOT_PIPELINE` and `BOOKKEEPING` sites are not | "that starts pipeline work", both lists named | 1: `control.py` |
| switch scopes: all, mod, stage, item, family, role | `game` is a scope too | added | 1: `control.py` |
| "Owed: the harness saves … (item)" | the item is closed; some older runners still do not use the snapshot | Built and Owed | 1: the imports of `scene_snapshot` |
| `scene_snapshot.py` docstring "shared by every live scene runner" | 3 users | corrected in this commit | 1 |
| "no alarm reaches his phone (last sent: none)" | a test page reached it 2026-11-23 11:08 AM PST | both | 1: `pager.py status`; the ledger note of that day |
| row `code_review` "reads UNTESTED" | FAILED after the sorts of 2026-11-24 | both, with dates, and "read the row" | 1: `judge_calibration.json` |
| "An Operations run is still told" the account's reading | a Conductor role run is too | added | 1: `role_launch.py` (`token_aware`) |
| "A new hold is a row in the same file" | `mod_owner_hold.py hold` writes the row | both | 1: `mod_owner_hold.py` |
| "The game reads … Mods" | ArchSmall reads its own | ArchBig and ArchSmall named | 3: root `CLAUDE.md` |
| the facts list "word for word" from `CLAUDE.md` | the list is now in plain words | the intro says so | 4 |
| parts of a boundary page | `boundary_check.py` also reads SURVIVES | added | 1 |

Sent to the owner (rule 5): none.

## Could not determine

- Which `D:` or ledger record holds "Fix all 24" (Decision 3) was not looked for. The line stays as it was.
- Whether each older live runner without `scene_snapshot` (for example `taozin_nest_live.py`, `firehawk_rewards_live.py`)
  needs the snapshot. Nobody saw it fail, so this run filed no ticket. A run that next changes such a runner would know.

## What this run did not test

- No agent run read the new text to do work. No measurement shows that an agent acts better on it.
- The `CLAUDE.md` pointers into this file were not read one by one. Each heading is unchanged.
- The 22 tests did not run again after the last edit (the `*south*` line).
