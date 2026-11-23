# Result: `RIMMANDRAKE_REWRITE_BIOME_RULINGS_FILE_SEAS_AND_ROSTERS`

Part of batch 7 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_BIOME_DELEGATION_DEBUG_DOCS_CODE_CITES_THEM`). File:
`design/RimMandrake/biome_rulings.md`. Run 2026-11-23, run 1 of the list lane.

Base: cf7ef42ad2051da5867f0934b18fa783cec06fb2

## Scores

| measure | before | after |
|---|---|---|
| bytes | 32,964 | 35,375 |
| words in linted prose | 5,151 | 5,556 |
| STE violations per 100 words | 3.63 | 1.91 |
| sentences over 20 words | 84 | 41 |
| flagged lines (mechanical) | 28 | 13 |
| lines that a cold reader cannot act on (hand count, by the writer) | 14 | 0 that this run could resolve; 2 listed under "Could not determine" |

The file grew by 7%.

### The 41 long sentences that stay

| line (at publish) | kind |
|---|---|
| 124, 139, 161 (2), 170, 182, 217 (2), 274 (2), 431, 444, 462, 465 (2) | an owner quote |
| 309 (4), 330 (4), 349 (3), 373 (3), 391 (2) | an owner quote (card text and his picked option, kept word for word) |
| 31, 38, 40, 42, 156, 158, 186, 197, 221, 242 | two short sentences that the lint joined at a bold lead |

### The 13 flags that stay

- 7 `shout` flags on headings. The special rule of batch 7 keeps each heading word for word, emoji included.
  `CLAUDE.md` cites `§"Star Wars style" naming is NOT Star Wars IP`, and `selftest_rule_homes_in_briefs.py` checks that
  pointer. 25 biome designs cite `§Five biome answers`.
- 3 `shout` flags on bold slogans kept from the old text: "EVICTIONS ARE STOPPED, AND THIS IS NOT A RULE SYSTEM", "THE
  SHIP IS THE ONLY WAY DOWN AND THE ONLY WAY BACK", "RETIRED AND DELETED FROM THE CODE".
- 4 `bare-id` flags (one line holds two kinds) on Q17, Q11 and Q11a. Each id now has a gloss: a question in §7 of
  `design/RimMandrake/biome_mod_architecture.md`.

## Code and files that read this file, and what the rewrite kept for them

- `selftest_rule_homes_in_briefs.py` checks that each `CLAUDE.md` pointer names a heading of this file. Every heading
  stays word for word (a diff of the `#` lines against the base is empty).
- `selftest_conversion_owed.py` checks that the file demands no offline name-swap test. The rewrite adds none.
- `selftest_close_gate.py` and `selftest_designer_cleanse.py` name the path only. The path stays.
- 25 biome designs in `design/concepts/` cite `§Five biome answers`. Three files in `design/RimMandrake/` cite
  `§Five biome answers, 3` or `, 4`. The numbered subheadings `### 1.` to `### 5.` stay.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "Moved from the project `CLAUDE.md` on 2026-10-11 …, text unchanged except heading levels." | false for the entries dated after 2026-10-11 | the first entries moved; later entries started here |
| "A biome depends on a mechanic, showcases it, or holds its materials or sources." | what "it" and "its" are | names the mechanic in each place |
| "mod-migrated", "mid-migration state" | what migration | "moved into mods"; the slogan stays |
| "§7 Q17 of `biome_mod_architecture.md`" | what Q17 is | "question Q17 in §7" |
| "its RM_ successor wins" | wins what | "So the count of 27 holds the `RM_` def, not its twin." |
| "already Scribed" | a RimWorld code term | "(saved)" added |
| "the split did that work" | which split | names item `BIOME_MOD_SPLIT_EXECUTION_1` (from `rimflow show`) |
| "one pass in this very session" | which session | "the session of 2026-09-26" (the date of commit `cd335ec02d`, which wrote the line) |
| "for ongoing spawns only" | ongoing when | "spawns during play" |
| "§7 **Q11a**, beside Q11" | what Q11 and Q11a are | gloss: questions of that §7 |
| "(Scald ban 1, never potable)" | what Scald ban 1 is | row 1 of `design/Jawa/worldbuilding/biomes/kits/scald_kit_spec.md` |
| "the build owes a change to a built default" | which change | from `design/concepts/Contagion/design.md`: the dose must also ask if the pawn is inside the screen's bubble |
| "the Settling", "the vhorrin", "the tar's burden" | design names with no gloss | one line points at `design/concepts/<Biome>/`, where each name is defined |
| bullets of 100 to 250 words under "Design process" | one bullet holds six rules | split into one bullet per rule, with sub-bullets |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of the rewrite with `PYRELANDS_WRONG_BIOME_DEF_1` removed, "222 tiles" changed to "some tiles", and `RM_SeabedLayer` changed to "the seabed layer" | 1 lost (the id), exit 1. Check 1 did not see the lost 222 or the lost code span. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 4 lost (2 code spans, the id, one copy of 222), exit 1 |
| check 1 | the final rewrite | 107 items, 0 lost, exit 0 |
| check 2 | the final rewrite | 202 spans, 0 lost, exit 0 |
| `rule_doc_lint.py selftest`, `checkable.py selftest` | — | exit 0; 19 of 19 |
| `selftest_rule_homes_in_briefs.py`, `selftest_conversion_owed.py`, `selftest_close_gate.py`, `selftest_designer_cleanse.py` | new file | PASS (each exit 0) |
| `selftest_retired_era_gone.py`, `selftest_skills_by_work.py` | new file | PASS |
| headings | `grep '^#'` of base and new | identical |

Names of people: this run read the diff for names. "owner" (any case) stays at 27, "Mandrake" at 8, "Conductor" at 1,
"Empire" at 1. "BENCH" goes from 1 to 3, because the rewrite names the subject of two sentences.

## What the meaning read found

A fresh Opus reader (rm-judge, model opus) read the old and the new text. It did not get the writer's reasoning. It
found no change that would make a reader act differently. It checked all 46 owner quotes and card texts with a
script: each one matches the old text word for word. It listed 5 small additions for the writer to confirm or drop.

| new text in the draft | what the reader said | repair |
|---|---|---|
| "Later entries started here." | a claim the old text did not make | kept: the old "text unchanged" claim is false for each entry dated after 2026-10-11, and the correction is the plain fact |
| "So count the `RM_` def as the biome." | a new instruction | replaced with a fact from the same section: "So the count of 27 holds the `RM_` def, not its twin." |
| "The split of each biome into an `RM_` def and a `RUT_` twin did that work." | decides what "the split" means | replaced with the item that did the split, `BIOME_MOD_SPLIT_EXECUTION_1`, and its title |
| "the session of 2026-09-26" | adds a date | kept: commit `cd335ec02d` of 2026-09-26 wrote the line |
| "While the mod is on hold, nobody files a build ticket." | a firmer ban than the old state line | restored the old line: "No build ticket is filed while the mod is held." |

The reader also listed 3 polish notes (no action). After the repair, the writer added the glosses for Scald ban 1, the
Contagion dose and the design names, and fixed two pronoun lines. No reader read that last edit. The checks and tests
ran again after it.

## Conflicts (listed, not decided)

None found. This run compared the file with the rule lines of `CLAUDE.md` §Biomes, rosters and seas, §A biome with
zero tiles is not a defect and §Star Wars style naming is not Star Wars IP. Each `CLAUDE.md` line agrees with its
home section here.

## Could not determine

| line | question | who would know |
|---|---|---|
| "**A sea IS its floor:** one row per sea" | a row of which table: the painted map's biome list, or `_freeze_matrix.csv` | the Conductor; the author of the 2026-10-28 ruling entry |
| "the grubs' two behaviours", "with one axis widened each" | which creature "the grubs" are, and what axis | the author of the 2026-09-23 measurement; the greatbole roster |

## What this run did not test

- No agent read the new file in real work. No measurement shows that an agent acts better on the new text.
- The last edits after the meaning read (three glosses, two pronoun fixes, two sentence splits) had no second
  meaning read.
- The tests that read the file ran on the new text only, not on the old text first.

## Second read of the repairs

Run 2026-11-23, item `RIMMANDRAKE_REREAD_REWRITE_REPAIRS_NO_READER_SAW_THEM`. One fresh Opus reader that made none of
these edits read each repair, restored line and late edit against the base text and the lines that travel with it. SAME
means that a reader of the new line acts as a reader of the old line. A gloss reads SAME when its source says the same.
His quotes: a script compared each quote of three words or more in the base with today's text, whitespace ignored. No quote differs.

| file | line read | verdict | what was done |
|---|---|---|---|
| biome | "Later entries started here." | SAME | none |
| biome | "So the count of 27 holds the `RM_` def, not its twin." | SAME | none |
| biome | the split item and its title | SAME | none |
| biome | "the session of 2026-09-26" | SAME | true: the date of commit `cd335ec02d` |
| biome | "No build ticket is filed while the mod is held.", restored | SAME | none |
| biome | late: the Scald ban 1 gloss | SAME | true by `scald_kit_spec.md` line 48 |
| biome | late: the Contagion dose gloss | SAME | true by `design/concepts/Contagion/design.md` line 279 |
| biome | late: the design-folder line for the design names | SAME | true: `WeepingStones/design.md` and `Warscar/design.md` define them |
| biome | late: two pronoun lines and two sentence splits, not listed one by one | SAME | so this reader read each changed line of the file; no line moved |
