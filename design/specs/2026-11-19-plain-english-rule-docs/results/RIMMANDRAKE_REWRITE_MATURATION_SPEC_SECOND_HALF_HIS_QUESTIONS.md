# Result: `RIMMANDRAKE_REWRITE_MATURATION_SPEC_SECOND_HALF_HIS_QUESTIONS`

Session 2 of 2 of batch `RIMMANDRAKE_REWRITE_MATURATION_SPEC_EIGHTY_KILOBYTES` (`batch_plan.md`, order 14). File:
`design/specs/2026-11-13-maturation-pipeline.md`. Run 2026-11-24.

Base: 3d9fc1c5da78d10baf6f949331b3336f7267d1b2

Scope: from `## 5. Floating above` to the end of the file. The text before it is byte for byte the same as the base,
except one false line in §4 (the lock rule, item 4, "A bar is made easier or deleted outright"; see the first row of
"Conflicts and stale lines"). Each heading in scope stays word for word. Each numbered item keeps its number.

## Scores

"Section" is the scope above. "Rule text" is the same section with each quote of 25 characters or more replaced by one
word. The lint reads no table rows.

| measure | before | after |
|---|---|---|
| bytes (section) | 36,883 | 44,092 |
| words in linted prose (section) | 4,786 | 5,855 |
| STE violations per 100 words (section, quotes included) | 4.03 | 2.92 |
| STE violations per 100 words (rule text) | 3.68 | 2.36 |
| sentences over 20 words (section) | 77 | 44 |
| sentences over 20 words (rule text) | 60 | 25 |
| flagged lines (mechanical, section) | 5 | 1 |
| whole file: STE per 100 words, long sentences, flagged lines | 3.67, 99, 8 | 3.06, 67, 4 |
| lines that a cold reader cannot act on (hand count, by the writer) | 16 | 0 that this run could resolve |

The section grew by 20%. Most of the growth is the corrected Dispatch text.

### The long sentences that stay in the rule text

| lines (what they are) | kind |
|---|---|
| the headed questions 2, 6, 8, 9, 12, 18; the `[HIS]` and `[CARRIED]` marks; "(Item ...)" before the in-game bullet; the hand-act lead; the steward-line lead; "The form is:"; the light-path mark; "55 schemes"; "for the five mods"; the List Pipeline line; the pilot line; question 15 (an option in italics) | two or more short pieces (a bold lead, a mark, a quote, a path) that the lint joined |
| "Dispatch sends a Stage 6 mod's scripted bar verdicts ..."; "A cleansed design ..." | a short sentence joined to its mark and its citation |
| "(That evening all four advancing mods had sat ..."; "What that means, for every agent and program ..." | the old words, kept |
| "An intervention is one of these ..."; "The kind is one of ..." | a closed list in one sentence |
| "An item that only the game can show ..."; "Such a thing is a file ..."; "only two kinds are re-run ..." | 20 to 23 words; a split would repeat the subject |

The one flag that stays: "The older level words (L0 to L4, GREEN-MIN, GREEN-FULL)", which are names.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| the Dispatch paragraph of 2026-11-14 (one bullet, about 20 facts) | which number is in force, who acts | a list, one fact in each bullet, with the settings key |
| "it asks one question" | the subject | "Dispatch asks" |
| "Built for the offline build: ..." | what is built | "This watch is built" |
| "It finds ...", "It hands off ..." | the subject, and which cases | "The agent or program", a list of cases |
| "Every hand act is recorded" | what a hand act is | one sentence |
| "a `clear`", "a coverage release" | the object of each act | the command and the act |
| "Today's measured example", "measured by the Conductor today", "today's notes", "filed today" | which day | 2026-11-13 |
| "Bounds proposed by the Conductor: ..." | which agent each bound binds | two sentences |
| "reads both every run" | both of what | "both places" |
| "under the entry rule", "the queue" | which rule, which queue | §4 Stage 6, SteveDesktop's test queue |
| "his order below" | which order | "his order of 2026-11-15 (the next quote)" |
| "the file ... a banner pointing here" | which file | "The file of the earlier map" |
| "the five mods" | which five | "the five mods that were in the Designer on 2026-11-13" |
| "It will exercise art ..." | the subject | "The mod" |
| "Rule 1 lets ...", "that game" | which rule 1, which game | "Rule 1 of the earlier map (§7)", "the game that gives the verdict" |
| "What this draft takes from Artisan ..." (retired) in one sentence | five facts | a list |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 2 (`rule_doc_lint.py keep`) | a copy with "10.7 million" made vague, one alarm id and one dated time removed | 5 lost, exit 1 |
| check 1 (`checkable.py compare`) | the same copy | 1 lost, exit 1 |
| check 2 | the final rewrite | 272 spans, 0 lost, exit 0 |
| check 1 | the final rewrite | 158 items, 0 unfindable, exit 0 |
| `guiding_prose.py check --base` | the drafts | 8 faults, then 3, then 3 or more; each fault that it printed in view is repaired; the final text was not checked again by the model reader before `./publish` |
| `selftest_retired_era_gone.py` | a draft that split the line about the retired Artisan loop | red (2 era-text lines); green after the repair |
| `selftest_self_fix_rule.py`, `selftest_touching_code_cost_rule.py`, `selftest_offline_stage_road_back.py`, `selftest_retired_era_gone.py`, `selftest_maturation_now.py`, `selftest_maturation_dispatch.py`, `selftest_maturation_autonomy.py`, `selftest_first_touch.py` | the final text (`selftest_first_touch.py`: after its own edit) | PASS, each one |

Names of people: this run counted "Mandrake", "Conductor", "Dispatch", "Operations", "Designer" and "steward" in the old
and the new section. No count goes down. The marks: [HIS] 30 to 34 in the first draft, [CARRIED] 6 to 6, [PROPOSAL] 14
to 14 (the count of the first reader); the later edits added marks and removed none.

## What the meaning read found

Three fresh Opus readers (`rm-judge`, model opus), one at a time, without the writer's reasoning. Reader 1 read both
texts in full. By script, all 48 old quotations of three words or more are in the new text word for word. Reader 1 also
checked each correction against the code, the rulings and the ledger. Readers 2 and 3 read the repairs and later edits.

| reader | first draft | why it was wrong | state |
|---|---|---|---|
| 1, significant | "A steward run does one of three things" | a closed list that the code does not hold | examples, plus the other steward and fixer runs |
| 1, significant | "A value changes only there" | `./pipe`, `pipe model` and `release` also change a value | names the three |
| 1, significant | "the list that the program reads is `advancing`" | the tick adds Designer concepts; `./pipe queue` changes the list | says both |
| 1, significant | question 9, "A mod is added only by his order" | a prohibition became a permission | the old words are back |
| 1, significant | the deferral row, "a recorded act of the Conductor" | no mark, no `lost:` and `undo:`, could be read as a steward run; §4 still said "his call" | the Conductor window only; mark added; §4 corrected |
| 1, minor | "Every ended cycle is a Needs Conductor line"; "The deletion is done"; results placed inside [HIS] marks (2); the journal test; a condition that became an assertion; the mark of a moved table cell; "a mod on his hold gets nothing"; "the plan as of 2026-11-13" | each one adds, loses or moves meaning | repaired |
| 2, significant | "except design work that its hold row allows" | the tick never launches it; `designer_cleanse.py` does | repaired |
| 2, minor | "past the Designer's coverage judge"; the road-back item; "no second hand-run"; the settings note on ended visits | inexact | repaired |
| 3, significant | "an item that a steward run filed for a failed line"; "each ended visit" in the settings note | the judge, the driver and his walk also file; a visit with no exit block goes to the Conductor | repaired |
| 3, minor | game-only items; the cycle limit; "Such a thing"; the place of a pointer | inexact | repaired |

No reader read these last lines, each one written with the words that reader 3 gave: the two road-back sentences and
"pilot mod" (§5 Dispatch), the sentence about a visit with no exit block, the order of "Such a thing" (§6), the pointer
in question 16, and the two clauses in `maturation_dispatch.json`.

## Conflicts and stale lines: settled

| line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| A looser bar "is his call" (§4 lock rule, §7 deferral row) / root `CLAUDE.md` | the Conductor window's recorded act | 2: his ruling of 2026-11-19 |
| Dispatch numbers: two builders, USD 60, one blind cycle, one driver, in-game off / the settings | the settings key in force, the first value kept as its history | 1: `maturation_dispatch.json` |
| "the pre-human check onward stay hand steps"; "a hand step of the Conductor" / the tick | steward runs do the hand steps | 1: `maturation_autonomy.py`; 2: his words 2026-11-15 13:35Z |
| The page is written by the Dispatch program / its own timer | its own timer | 1: `rm-maturation-page.timer` |
| The advancing list has five names / six | Contagion is named, and the hold | 1: the settings file, `mod_owner_hold.json` |
| "Question 7 is still open"; the Exam "is open question 7" / its answer | answered: the gates stay | 2: his card 2026-11-14 19:22Z |
| Question 14 open / the List Pipeline | his words are quoted under it | 2: his words 2026-11-23 10:46Z |
| Question 16 open, "nothing else until the second hand-run" / automated stages | his words are quoted under it | 2: his words 2026-11-15 |
| Pre-look judges at Stage 7 / Stage 7 has no veto | Stage 6 (PROPOSAL); Stage 7 keeps its reader | 2: his words 2026-11-17 |
| The minimal-list verdict "not settled" / §4 Stage 6 | settled 2026-11-17 | 1: `build_match.py` |
| Relentless "stays switched off" / the era is retired | his order of 2026-11-18 is named, with the index of what is left | 2 |
| `first_touch.py`: "write it out for Relentless as build items" (retired) | the words "for Relentless" are deleted (retired) | 4 |
| `maturation_dispatch.py` docstrings (one cycle, not at in-game), its settings notes, `maturation_pipeline.md` §4, §8, §9 (one cycle, one in-game run on any mod, `max_live` 2, five mods) | corrected | 1 |
| `standing_rulings.md` §A refusal carries its path to pass: an owner bar "is a card for him" / `criteria_fixer.md` | not edited: a live run holds the file. The note is on `RIMMANDRAKE_REWRITE_STANDING_RULINGS_SESSION_THREE_OF_FIVE` | 2 |

For the owner: none.

## Could not determine

None. Whether a mod's road back reads right for every pilot case is decided by `pilot_holders`, not by this spec.

## What this run did not test

- No agent run read the new text to do work. No measurement shows that an agent acts better on it.
- No lint reads the table rows. Reader 1 covered them.
- The [CARRIED] and [PROPOSAL] claims of sections 6, 9 and 10 were not checked against the code, except the rows above.
