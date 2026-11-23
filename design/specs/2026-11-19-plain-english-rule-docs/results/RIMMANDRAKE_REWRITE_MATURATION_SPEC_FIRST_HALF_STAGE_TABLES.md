# Result: `RIMMANDRAKE_REWRITE_MATURATION_SPEC_FIRST_HALF_STAGE_TABLES`

Session 1 of 2 of batch `RIMMANDRAKE_REWRITE_MATURATION_SPEC_EIGHTY_KILOBYTES` (`batch_plan.md`, order 14). File:
`design/specs/2026-11-13-maturation-pipeline.md`. Run 2026-11-23.

Base: 6d6f1822bc805b75317015c288a953fde51982c7

Scope: from the top of the file up to, but not including, `## 5. Floating above` (lines 1 to 322 of the base). The rest
of the file is byte for byte the same as the base (`cmp` against the base text: identical). Each heading in scope stays
word for word. The section 1 block quotes and both forms of the map (section 3) are copied from the base by script.

## Scores

"Section" is the scope above. "Rule text" is the same section without the block quotes of section 1 and the lock rule,
and with each quote of 25 characters or more replaced by one word. The lint reads no table rows. 92 table rows hold most
of section 4, so the STE figure does not measure them.

| measure | before | after |
|---|---|---|
| bytes (section) | 45,718 | 47,731 |
| words in linted prose (section) | 3,778 | 4,007 |
| STE violations per 100 words (section, quotes included) | 4.45 | 3.22 |
| STE violations per 100 words (rule text) | 3.86 | 2.19 |
| sentences over 20 words (section) | 57 | 20 |
| sentences over 20 words (rule text) | 41 | 3 |
| flagged lines (mechanical, section) | 10 | 2 |
| whole file: STE per 100 words, long sentences, flagged lines | 4.22, 134, 15 | 3.67, 97, 7 |
| lines that a cold reader cannot act on (hand count, by the writer) | 18 | 0 that this run could resolve; 3 listed under "Could not determine" |

The section grew by 4.4%.

### The 20 long sentences that stay

| text | kind |
|---|---|
| 11 sentences of his message of 2026-11-13, and the sentence that opens "I had thought it would be useful" | owner quotes |
| "Designer is the only way I know how to do that..." | an owner quote |
| "Conductor may choose any of the options you offered..." | an owner quote |
| "The runner runs `python3 ... build_match.py identity ...` after the deploy and the list swap." | a sentence that holds a command |
| "The row counts when the change since its commit touches nothing ..." | a rule sentence joined to the two paths and the heading that it cites |
| "**Design Version**: the numbered design ... [CARRIED: ...]" | two short sentences that the lint joined |
| "**[CARRIED]** the roads back from 6 and 8 ...; the Divergent road ..." | two short items that the lint joined; the first holds a quote |
| "**Every one of these is one journal line** in the intervention form. §5 (...) ..." | two short sentences that the lint joined |
| "**[HIS, by card 2026-11-13]** "One stage, tests first." His question ..." | an owner quote |

The 2 flags that stay: his message (`pronoun`, `shout`), and "This is the answer offered to ..." (restored from the old
text after the meaning read).

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "(corrected 2026-11-15: this line said ...)" | which line, and what is built now | a bullet list |
| "A bar ... An acceptance criterion." | the second sentence has no subject | "A bar is an acceptance criterion." |
| "It has an id, the files it reads" | the subject of "It" | "A line item has" |
| "It stays. It is not the pipeline." | the subject | "RimFlow stays. RimFlow is not the pipeline." |
| "The two games: ... (§4 Stage 6 ...)" in one sentence | four facts and one mark in one sentence | four lines |
| "What it means in practice" | what "it" is | "What these two messages mean in practice" |
| "What "you recommend" ... makes them [HIS]" | what "them" is | "makes the six things" |
| "It is done by hand on Explosive Knockback first" | the subject | "The pipeline is done by hand" |
| "(Evidence-for-Ask)" | the meaning | a line in "Words used here", from `standing_rulings.md` |
| "(below)", "see below" in the Stage 2 Exit mark | where "below" is | names the passage |
| "the old map's stage 4" | which map | "stage 4 of the earlier stage map (§7)" |
| "His settings question of today" | which day | "of 2026-11-13" |
| "not a bar edit. It goes to" | the subject | "The change goes to" |
| "Verse-free" | the meaning | "(no Verse types)", from `fable_rescue.md` step 2 |
| "carries the offline model: ..." in one sentence | four facts in one sentence | a list |
| "a past-blind mod" | the meaning | "(a mod past the blind challenge)", from `testq/pipeline_admit.py` and `coverage.py` |
| "The program reads the same on Archmagi" | what "the same" is | a list of three readings |
| the Entry rule, one paragraph of 8 facts | who calls the gate, what the gate refuses | one bullet for each fact |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 2 (`rule_doc_lint.py keep`) | a copy with "22 seconds" changed to "fast", one ticket id and one date removed | 4 lost, exit 1 |
| check 1 (`checkable.py compare`) | the same copy | 2 unfindable, exit 1 |
| check 2 | the final rewrite | 259 spans, 0 lost, exit 0 |
| check 1 | the final rewrite | 153 items, 0 unfindable, exit 0 |
| `selftest_self_fix_rule.py`, `selftest_touching_code_cost_rule.py` (both read this file), `selftest_offline_stage_road_back.py` (cites it), `selftest_retired_era_gone.py`, `selftest_maturation_now.py` | the final rewrite | PASS, each one |

The selftests were run on the new text only. Names of people: this run counted "Mandrake", "Conductor", "Dispatch",
"Operations", "Designer" and "steward" in old and new. No count goes down. "Mandrake" goes up by 1 (a path).

## What the meaning read found

A fresh Opus reader (`rm-judge`, model opus) read the old and the new text of the section, without the writer's
reasoning. By script the reader matched 83 of 83 inline quotes, 7 of 7 block-quote lines, 54 of 54 marks and 92 of 92
table rows. The reader found 2 significant lines and 10 minor lines.

| first draft | why it was wrong | state |
|---|---|---|
| "Before any fix or tuning, the builder builds a generator ..." (significant) | "before any fix or tuning" no longer covered the checks that read the generator; "the builder" was added | the old words are back, as one list item |
| the mark of "After three cycles" inside the first bullet (significant) | the options and the fourth-judge rule lost the mark | the mark opens the passage again |
| "The offline model has three parts" | an invented count under a [HIS] mark | "The offline model is:" |
| "After that walk, mods enter" | the old text opens at Stage 8 | "After that, mods enter" |
| a sentence about Evidence-for-Ask in a row marked HIS 2026-11-14 | added text under his mark | moved to "Words used here", with its own [CARRIED] mark |
| the load times without [CARRIED] | the mark could be read as covering them | the old order is back |
| "Each deferral ..." in a bullet of its own | the 1:05 PM mark narrowed | joined to the marked bullet |
| "At that point the agent has not opened ..." | a rule of order read as a description | "The agent does this before it opens ..." |
| "This proposal is the answer" | narrowed "This" | the old words are back |
| "decide the bar", "any other look" | each picked one reading of an open pronoun | the old words are back |
| [HIS, 2026-11-21] held to one bullet of the build match | the old paragraph does not say where the mark ends | left: the quote behind the mark is about the touched checks only |
| "(a mod past the blind challenge)", the dated settings question, the pointers made explicit | added meanings | left: each one is in the code or in this file |

A second fresh Opus reader read only the repaired places: the same meaning in each. The second reader found 1 minor
line: the Evidence-for-Ask definition did not name the five acts. The writer added "His five acts still wait for him.
The home section gives the full rule." No reader read that last addition.

## Conflicts (listed, not decided)

1. **What SteveDesktop's queue takes.** "How to read this" (and §5 Dispatch) says that only tests that came through the
   offline stages are queued (2026-11-14). §2 item 4 and §4 "Entry rule" say any mod's token-free test, whatever its
   stage ([HIS, 2026-11-17]). The later ruling drops the earlier limit, so the first line reads as out of date.
2. **How many games.** This file says "the two games". Root `CLAUDE.md` §There are several live games names four games:
   ArchBig, ArchSmall, Steve1 and Steve2.
3. **The load time of the full list.** This file: about 15 minutes. `skills/rimworld-load-round/SKILL.md`: about 25
   minutes.
4. **The rule for leaving intake.** The Stage "Intake" Exit row says that the rule after Stage 8 "is asked of him then".
   The Who row and §8 decision 8 say that mods enter by his order of 2026-11-15 with no ask.
5. **How many mods.** Section 1 and Stage 3 say five current mods. Intake and the lock rule say four advancing mods.
   The two can be different sets.

## Could not determine

| line | question | who would know |
|---|---|---|
| "the recommendation that he answered" (the numbering of stages 6 to 8) | which recommendation text | the Conductor of 2026-11-13; `OWNER_WORDS.md` in the folder that section 1 names |
| "Lane 1 ... kept schemes, his picks of 2026-11-12" | the list of picks. §7 "The kept validation schemes" is session 2 of this batch | session 2 |
| "[HIS, 2026-11-21]" in the build match | how far the mark reaches: the walk-folder sentence only, or also the mod list | the Conductor |

## What this run did not test

- No agent run read the new text to do work. No measurement shows that an agent acts better on it.
- No lint reads the table rows. The meaning read covered them.
- `## 5. Floating above` and the sections after it are session 2 (`RIMMANDRAKE_REWRITE_MATURATION_SPEC_SECOND_HALF_HIS_QUESTIONS`).
