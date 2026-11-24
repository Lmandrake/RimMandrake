# Result: `RIMMANDRAKE_REWRITE_STANDING_RULINGS_SESSION_THREE_OF_FIVE`

Session 3 of 5 of batch `RIMMANDRAKE_REWRITE_STANDING_RULINGS_LARGEST_HOME_FILE` (`batch_plan.md`, order 8). File:
`design/RimMandrake/standing_rulings.md`. Run 2026-11-24.

Base: a399f59d23735b010239cb238089b03c929dfb32

Also: design/RimMandrake/CLAUDE.history.md

The `Also:` line is for one retired line (the arena lane's `owner_playing` key, see the conflicts).

Scope: the `## ` sections from `## There are several live games` up to, but not including, `## Mod Design Versions use
Semantic Versioning`. The text before and after the scope is byte for byte the same as the base (compared by a script:
True, True). Every heading of the file is unchanged.

Sections 1 to 8 of §Live tests have three kinds are the text that the owner approved (*"Approve updated draft 3."*). This
run left them as they are, except for the later ruling inside section 3 ("Short of X of Y"), which was split into bullets.

## Scores

"Section" is the scope. "Rule text" is the same text without the block quotes and with each `*"..."*` quote replaced by one
word (`batch_plan.md` §The STE target).

| measure | before | after |
|---|---|---|
| bytes (section) | 62,951 | 66,129 |
| words in linted prose (section) | 9,841 | 10,332 |
| STE violations per 100 words (section, quotes included) | 4.21 | 3.48 |
| STE violations per 100 words (rule text) | 3.37 | 2.37 |
| sentences over 20 words (section) | 160 | 111 |
| sentences over 20 words (rule text) | 106 | 54 |
| flagged lines (mechanical, section) | 12 (11 shout, 1 pronoun, 1 above) | 2 (shout) |
| whole file: STE per 100 words, long sentences, flagged lines | 3.82, 480, 59 | 3.61, 431, 49 |
| lines that a cold reader cannot act on (hand count, by the writer) | 14 | 0 |

### The 54 long sentences that stay in the rule text

- 26 are in the two sections whose text the owner approved or that this run left for that reason (§Live tests have three
  kinds sections 1 to 8), or in the short numbered rules of §The cheapest test and §What Python cannot reach.
- The rest is of three kinds: a line that holds an owner quote or the evidence beside the quote (a record's name, its date,
  its item); a sentence that holds a command or a path; and a bold lead that the lint joins to the next sentence.
- A few rule sentences of 21 to 30 words stay as one sentence, because a split let the meaning reader read a changed rule.
  Examples: "His touching, leaving or returning …" and "When the lock says that the bridge is yours …".

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "The owner overrides both of you" | who "both of you" are (two retired seats) | "every holder" |
| "lands in the same file you already read" | which file | the driver lock is named |
| "It errs toward ALLOWING" | what "It" is | the slogan stays; "Here 'It' names the driver lock" |
| "The same limits bind as above" | which limits | the bold lead of those limits is named |
| "his OWNER hold (below)" | where below is | "below in this section" |
| "the game-state relay above" | nothing above holds the relay | the relay is described in the section |
| "Adopted regardless of the arena trial verdict" | which trial | the arena trial, retired, is named |
| "Crystallize 2026-W47" | what this is | the weekly Crystallize pass of 2026 week 47 |
| "a spent offline road back of game-only items" | what is spent | defined from `pilot_holders` and `fixer_spent` |
| "The judge rule below" | which rule | the section is named |
| "without a green certificate" | which certificate | `maturation.py certificate` is named |
| "The quota gate" | which gate | `quota_gate` in `agent_runner.py` |
| "closes without a claim form" | which form | a claim in `coverage_fixes.json` |
| "It was asked when Codex ran on Windows" | what was asked | "He gave this order when …" |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 2 (`rule_doc_lint.py keep`) | a copy with "17.5 GB", "8 blocks in 7 records", one path and one id removed | 6 lost, exit 1 |
| check 1 (`checkable.py compare`) | the same copy | 3 lost (17.5 GB, the path, the id), exit 1. Check 1 did not see the lost "8" and "7". |
| check 2 | the final rewrite (final bytes) | 1,199 spans, 0 lost |
| check 1 | the final rewrite | 661 items, 0 lost |
| `rule_doc_lint.py selftest`, `checkable.py selftest`, `batch_done.py selftest` | — | PASS; 19 of 19; GREEN 12 planted cases |
| 26 tests that read the file or the two 2026-11-17 judge pages | old text, then new text | the same result on each: 21 pass, 5 fail on both (below) |
| the 3 `selftest_testpilot_*` tests | the edited docstrings and rule file | pass |

The 5 that fail on the base text and on the rewrite alike, so this rewrite did not cause them:
`case_carried_gap_closes_on_ok_rows.py`, `case_four_rules_two_looks.py` (run again on the base text of
`6_proposed_ruling_plain.md`: the same), `acceptance_stop_rules_calibrated.py` (2/6), `code_review_brief_accept.py` and
`selftest_conductor_authority.py` (2 failures). The 26 ran on the draft before the reader's repairs. On the final bytes, nine
of them ran again and passed (the game names, rule homes, touching-code, self-fix, conversion, objections, rule files,
bar rule and retired era tests).

Names of people and roles, counted by a script in the scope: each name is the same or higher, except "OWNER" 8 to 7 (the
false "OWNER-attributed ledger event", see the conflicts). "Conductor" goes 32 to 36.

The prose check of `./publish` was run by hand with the base. The 15 lines of its first run and 4 of the 5 of its second run
were repaired. Four small ones stay: the slogan "It errs", and the words "role units", "row" and "second reader" (its
third run; each is an old word of the old text in an evidence line or a defined term of the pipeline).

## What the meaning read found

A fresh Opus reader (`rm-judge`, model opus) read the old and the new text of the scope. The reader got no reasoning of the
writer. A script of the reader compared 120 quoted strings and 12 block quotes: each is word for word. The reader listed
14 lines. Five were false or changed, six were corrections that needed a declaration, and three were checked TRUE.

| first draft | why it was wrong | repair |
|---|---|---|
| "When he touches … nothing is gated …" | can read as "no gate applies then" | the old verb construction |
| "ask no question first. Start Steam …" | a permission became an order | "you may start Steam … Ask no question first." |
| "hand it off with that evidence" | points at nothing | "hand the defect off with the evidence" |
| "On the day of the ruling, only late findings got a second reader" | lost the dial's present setting | "Its setting: today only late findings …" |
| "He was asked when Codex ran on Windows" | false: he gave an order | "He gave this order when …" |
| "a question card that he answers there" | "there" points nowhere | "in a seat window" |

The same reader then read each repair, the 12 edits that the prose check caused, and four glosses: all SAME or TRUE, except
two wordings that the reader gave ("spent offline road back", "that week") and that the writer took word for word. The
reader could not determine "strike", so that gloss was deleted. Lines that no reader read: the lines that were only
re-wrapped, and those two taken wordings in place.

## Conflicts and stale lines: decided

| line | the two sides | decision | rule and evidence |
|---|---|---|---|
| What restarts his 45-minute clock | "any OWNER-attributed ledger event … anything run on his words, card or ruling" / the same paragraph: an agent's relay restarts nothing | an event that his own hands wrote; a card that he answers in a seat window also counts | 1: `owner_interaction.py` `is_his_act` and its docstring |
| "The arena lane config key `owner_playing` is ignored and dropped"; "arena lane" in a list | no code reads the key | both lines deleted; the first is in `CLAUDE.history.md` | 4: the arena was removed at `1f0e666566` |
| "the game-state relay above is its only other carve-out" | no relay stands above | the relay is described | 1: `broadcast.py` docstring |
| When the four judge rules bind: "once … recalibrated, not before" | the coverage judge read CALIBRATED on 2026-11-18 (12 of 12) | they bind; the status file is named | 1: `judge_calibration.json`, item `RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE` (done) |
| `6_proposed_ruling_plain.md` and its `README.md`: "The build is still owed" | the same | both corrected to "Built" | 1 |
| A north-star bar that pins a number is "his to change" / §Only five acts stay his | 2026-11-16 / 2026-11-19 | his, or the Conductor's mindful act with `lost:` and `undo:` when looser | 2: the later ruling |
| A test that asks for a mod change is "a question for the owner" / the same | 2026-11-17 / 2026-11-19 | the owner; the Conductor may take it since 2026-11-19 | 2 |
| `testpilot_route.py`, `testpilot_reload.py`, `testpilot_reload_rule.json` name the arena's `testpilot.py` as live | the file is gone | the words deleted | 4: `1f0e666566` |
| ArchBig memory line: "19.6 GB of headroom over a 12 GB floor" | read two ways | "a 12 GB floor of it must stay free" | 1: `two_rimworld_instances_2026-11-07.md` (no launch under 12 GB headroom) |

Sent to the owner (rule 5): none.

## Could not determine

- "strike" in "the item waits without a strike" (§Broken tests are expected, 2026-11-03). The retired Relentless counted
  failed tries in this way. No record gives the exact definition. The Conductor's 2026-11-03 records would hold it.

## What this run did not test

- No agent run read the new text to do work. No measurement shows that an agent acts better on it.
- Sessions 4 and 5 rewrite the rest of the file. This run did not touch those sections.
- The `CLAUDE.md` pointers into this file were not read one by one. Each heading in scope is unchanged.
- 17 of the 26 tests were not run again on the final bytes.
