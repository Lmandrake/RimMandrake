# Result: `RIMMANDRAKE_REWRITE_STANDING_RULINGS_SESSION_TWO_OF_FIVE`

Session 2 of 5 of batch `RIMMANDRAKE_REWRITE_STANDING_RULINGS_LARGEST_HOME_FILE` (`batch_plan.md`, order 8). File:
`design/RimMandrake/standing_rulings.md`. Run 2026-11-24.

Base: d039c3af322ad51de53e603427ba8178f5901223

Scope: the 9 `## ` sections from `## Code is clean when its promises are tested` up to, but not including,
`## There are several live games`. The text before and after the scope is byte for byte the same as the base (compared by
a script: True, True). Every `## ` heading of the file is unchanged.

## Scores

"Section" is the scope. "Rule text" is the same text with each owner quote `*"..."*` replaced by one word, and without
the paragraphs of dated quotes and the two evidence paragraphs (`batch_plan.md` §The STE target).

| measure | before | after |
|---|---|---|
| bytes (section) | 39,436 | 42,782 |
| words in linted prose (section) | 6,406 | 6,931 |
| STE violations per 100 words (section, quotes included) | 4.51 | 3.09 |
| STE violations per 100 words (rule text) | 4.15 | 2.26 |
| sentences over 20 words (section) | 115 | 47 |
| sentences over 20 words (rule text) | 80 | 15 |
| flagged lines (mechanical, section) | 12 (6 pronoun, 6 shout) | 8 (7 shout, 1 pronoun) |
| whole file: STE per 100 words, long sentences, flagged lines | 4.10, 545, 63 | 3.82, 477, 59 |
| lines that a cold reader cannot act on (hand count, by the writer) | 16 | 0 |

The section grew by 8%.

### The 15 long sentences that stay in the rule text

- Bold lead, or a kept slogan, joined by the lint to the next sentence: "Test 1 …", "Test 2 …", "Such a drop … §You do not
  trim work …", "So when a pass …", "🔴 Back up the Saves folder's keepers …", "🔑 Caught live, 2026-09-20 …", "Live runs
  finish past …" (holds his dated quotes), "(Owner 2026-11-19, …) The `--why` …".
- A slogan kept word for word with its dates: "A fault is fixed in the sitting …" (a test pins it), "A small change is
  checked by …", "🔑 Every art review sheet …", "🔴 Whatever we put in front of him …".
- A sentence that holds a command: "Then the agent closes it … `rimflow close …`".
- A list that the meaning reader or the old text fixed as one sentence: "A small change is a change whose check is …" and
  "The evidence is one of these: no tools, …".

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "the filing gate (below)" | where "below" is | "Both are bullets of this section" |
| "It fixed only significant findings and converged on quiet files" | what "It" is | "That loop" |
| "this is what CLEAN means everywhere" | what "this" is | "PAGE-CLEAN is what CLEAN means everywhere" |
| "(A mod fault fixed in a sitting: §Touching code has a cost; that reader reads only the fix.)" | which reader "that" is | "There the reader reads only the fix" |
| "The Conductor does this until a timer does. Proposal, not wired: …" | false now | the Friday run does it (conflicts) |
| "it is a record (his words above)" | which words | "his card of 5:54 PM PST, quoted at the top of this section" |
| "(his card above)" on the standing scan | which card | "his card of 5:54 PM PST" |
| "Its own page:" | whose page | "The page of `check` itself" |
| "a `.cs` file dropped from the `.csproj` … is the same" | the same as what | "is a DEAD-FILE candidate when …" |
| "It binds tickets filed before the ruling too" | what "It" is | "The rule also binds tickets from before the ruling" |
| "That is a go." | what "That" is | "Such a red test is a go." |
| "(`class` MOD)" | that `class` is a field to write | "Write the class in the field `class`." |
| "its repair does not touch the mod" | whose repair | "The repair of a check or scene does not touch the mod." |
| "This replaces the whole new blind cycle" | what "This" is | "This one read replaces …" |
| "its hand-off list is the list above"; "unless the evidence above says otherwise" | where "above" is | "the list under test 2"; "the evidence under test 2" |
| "a row without one says so" | without what | "A row without a canon entry says so." |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 2 (`rule_doc_lint.py keep`) | a copy with "14 to 25 claims per 1,000 lines" and "8,749 readings" made vague | 4 lost (1,000; 14; 25; 8,749), exit 1 |
| check 1 (`checkable.py compare`) | the same copy | 0 lost, exit 0. Check 1 did not see these numbers (each has another copy, or no unit that check 1 reads). |
| check 1 | a copy without the path `design/specs/2026-11-20-account-drain/boundary.md` and without the id `RIMMANDRAKE_CALIBRATE_JUDGE_STOP_RULES_WORDS_UNTIL_RUN` | 2 lost (path, id), exit 1 |
| check 2 | the same copy | 3 lost, exit 1 |
| check 2 | the final rewrite (final bytes) | 1,191 spans, 0 lost |
| check 1 | the final rewrite | 657 items, 0 lost |
| `rule_doc_lint.py selftest`, `checkable.py selftest`, `batch_done.py selftest` | — | PASS; 19 of 19; GREEN 12 planted cases |
| 22 tests that read the file (selftests, acceptance tests) | old text, then new text | the same result on each. 19 pass. 3 fail on both (below) |

The three tests that fail on the base and on the rewrite alike: `code_review_brief_accept.py` ("the code_review family is
CALIBRATED now UNTESTED"), `acceptance_stop_rules_calibrated.py` (FAIL 2/6), `selftest_conductor_authority.py` (2
failures). They read the same on the base text, so this rewrite did not cause them. The 22 ran on the rewrite before the reader's repairs and the late edits. On the
final bytes, six of them ran again and passed: `selftest_touching_code_cost_rule.py`, `selftest_self_fix_rule.py`,
`selftest_rule_homes_in_briefs.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py` and
`selftest_wrong_check_fixed_in_sitting.py`.

Names of people: the script counted names in the old and new file. "Conductor" 110 and 110, "Opus" 8 and 8, "Mandrake"
89 and 89, "Relentless" 11 and 11, "FOUNDRY" 4 and 4. "Steven" goes from 2 to 3: the old "steven's 52% leave line" is
now at the start of a sentence, as "Steven's".

## What the meaning read found

A fresh Opus reader (`rm-judge`, model opus) read the old and the new text of the scope. The reader got no reasoning of
the writer. A script of the reader checked all 47 owner quotes: 47 in the old text, 47 in the new, word for word. The
reader found 7 lines. The writer repaired or declared each of them. The same reader then read the repairs: 7 of 7 FIXED.
After that the writer split ten long sentences; the same reader read those ten: 9 SAME, 1 CHANGED (repaired).

| first draft | why it was wrong | repair |
|---|---|---|
| "The Friday run … does this examination" | a changed duty against the old text | kept as a declared update (conflict 1); "(`flagged=0`)" added, so nobody reads it as files examined |
| "The state of the build is the state of that item" | lost "the scan is not built yet" | "Until that item closes, the scan is not built." |
| "The Conductor may also rule on it, as its recorded act" | widens authority against the old text | declared (conflict 2); "A departure that replaces art he kept stays his." added |
| "The item … judged the tickets that were open that day" | a claim that the old text does not hold | claim deleted; the old pointer restored |
| "… validation. Examples: …" | opens a closed list | the old colon restored |
| "counts only after two readings … The record of both readings is beside the row" | the record was no longer a condition | three conditions, all required |
| "Either act is better than a review of code that nobody runs" | a ban became a preference | "Do not spend a review on code that nobody runs." |
| the three "Plant with what exists" bullets without "or" (late edit) | the list read as "use all three" | the old "or" restored; the reader read it |

After the first publish, the prose check of `./publish` listed 8 lines. The writer repaired them. A second fresh Opus reader read
those 8 against the old text: 6 SAME, 2 CHANGED. Both were new definitions that the writer had taken wrong (a blind cycle,
the road back). The writer replaced them with the reader's wording, from `maturation.py` `ROADS_BACK` and the blind brief.
A third fresh Opus reader read the two lines: TRUE and SAME, no repair.

Lines that no reader read: none. After the reads, the writer only re-wrapped lines over 120 characters.

## Conflicts and stale lines: decided

| line | the two sides | decision | rule and evidence |
|---|---|---|---|
| Who examines the FLAGGED files | this file: "The Conductor does this until a timer does. Proposal, not wired" / `findings_judge_friday.md` and the journal | the Friday run does it | 1: the step is in `src/RimMandrake/Utils/findings_judge_friday.md` (added in `384e651a21`); the 2026-11-20 run of `rm-findings-judge.service` ends `flagged=0`. The wiring item stays open |
| Who rules on a deliberate departure from canon | this file, 2026-09-15: "he rules" / §Only five acts stay his, 2026-11-19: everything but five acts is open to the Conductor | the owner, or the Conductor as its recorded act; a departure that replaces art he kept stays his | 2: the later ruling |
| `design/specs/2026-11-20-wrong-check-fixed-in-sitting/boundary.md`: title and cited heading "repaired or set aside" | the heading in this file says "repaired or removed"; his words on "set aside" reject it; `line_class` ignores a `set_aside` field | title, citation and promise line corrected to "removed" | 1: `maturation.py` `line_class` |
| `selftest_touching_code_cost_rule.py`: two comment lines "repaired or set aside" | the same | corrected to "removed" | 1 |
| "The soft line: no new run starts" (this file) / no program refuses it | already settled in `RIMMANDRAKE_REWRITE_SKILL_RIMFLOW_OPERATIONS` | kept as the rule | ticket `RIMMANDRAKE_REFUSE_NEW_RUN_AT_SOFT_LINE_DRAIN_TOO_LATE` |

Sent to the owner (rule 5): none.

## Could not determine

None.

## What this run did not test

- No agent run read the new text to do work. No measurement shows that an agent acts better on it.
- Sessions 3 to 5 rewrite the rest of the file. This run did not touch those sections.
- The `CLAUDE.md` pointers into this file were not read one by one. Each heading in scope is unchanged.
- 16 of the 22 tests were not run again on the final bytes.
