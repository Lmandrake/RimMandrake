# Result: `RIMMANDRAKE_REWRITE_STANDING_RULINGS_SESSION_ONE_OF_FIVE`

Session 1 of 5 of batch `RIMMANDRAKE_REWRITE_STANDING_RULINGS_LARGEST_HOME_FILE` (`batch_plan.md`, order 8). File:
`design/RimMandrake/standing_rulings.md`. Run 2026-11-23.

Base: 97b1d5273dfc1bb8d394773f7a8d5c0b00ed30f8

Scope: the 16 `## ` sections from the top of the file down to `## Git` inclusive. The rest of the file, from
`## Code is clean when its promises are tested` to the end, is byte for byte the same as the base (`cmp` against the base
text: identical). Every `## ` heading in scope stays word for word.

## Scores

"Section" is the scope above. "Rule text" is the same section with each owner quote in `*"..."*` replaced by one word,
and with the five evidence paragraphs of card answers and dated quotes removed. The STE target binds only the rule text
(`batch_plan.md` §The STE target: this file is a home for evidence).

| measure | before | after |
|---|---|---|
| bytes (section) | 36,312 | 39,370 |
| words in linted prose (section) | 5,646 | 6,104 |
| STE violations per 100 words (section, quotes included) | 4.64 | 3.10 |
| STE violations per 100 words (rule text) | 4.50 | 2.19 |
| sentences over 20 words (section) | 111 | 45 |
| sentences over 20 words (rule text) | 78 | 7 |
| flagged lines (mechanical, section) | 21 (17 shout, 5 pronoun) | 13 (13 shout) |
| whole file: STE per 100 words, long sentences, flagged lines | 4.43, 524, 71 | 4.10, 458, 63 |
| lines that a cold reader cannot act on (hand count, by the writer) | 21 | 0 that this run could resolve; 4 listed under "Could not determine" |

The section grew by 8%.

### The 7 long sentences that stay in the rule text

| text | kind |
|---|---|
| "If the act of a card is not one of the five, and no concrete evidence goes against the obvious answer, the Conductor acts now." | a sentence that holds a command |
| "When a seat or helper finds why an item is stuck, that seat or helper does the fix and the remaining check itself." | a sentence that holds a command |
| "So its 24 ORPHAN_WALKs … **34 of 78 walks are …**" | two short sentences that the lint joined at a bold lead |
| "Whoever rebuilds `OracleHttpClient` against this ruling: verify …" | a sentence that holds a command |
| "🔴 **And that assumption covers the PLAYER, not just us** — owner, 2026-09-26: … ⇒ **Every DLC is …**" | a slogan kept word for word, joined with an owner quote |
| "**Do not spend a review, … configuration.** No such supported configuration exists." | two short sentences that the lint joined at a bold lead |
| "by card, 2026-11-02 18:35 PST: "How hard should Relentless run this machine? …"" | an owner quote |

The 13 flags that stay are all `shout`: the two headings that open with 🔴 (kept word for word: `CLAUDE.md` points at
them), the 🔴 bold leads, and the ALL-CAPS slogans (`ALL TEST MOD LISTS include ALL FIVE EXPANSIONS`). This run removed
the ⛔ ✅ 🔑 ⚠️ marks on 12 bullets that already say "Never" or "Do not". The 🔴 marks stay.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "Moved from the project `CLAUDE.md` on 2026-10-11 …, text unchanged except heading levels" | false now: later rulings are in the file | "At that move, only the heading levels changed. Later rulings were added here." |
| "(Thu 2026-11-19 ~7:40 AM PST.)" after the quote | which quote the date belongs to | the date opens the quote: "His words, Thu 2026-11-19 ~7:40 AM PST:" |
| "a Conductor instruction still carries his authority to them" in one long sentence | three facts in one sentence | split into bullets |
| "This sits beside §Evidence-for-Ask" | the subject of "This" | "This rule sits beside" |
| "Its ban on `push --force`" | what "Its" is | "The ban in those instructions" |
| "(he said it of Relentless, since retired)" | what "it" is | "He said this of Relentless, which is now retired." |
| "With "See it, fix it, then" in the CHARTER." | what "With" asks | "This rule goes with …" |
| "With "The pipeline never blesses a small change" above." | where "above" is | names the section and says that it comes just before |
| "Do not casually edit their `## north star` sections" | whose sections | "the `## north star` section of a mod" |
| "which is false the moment it is" | what "it" is | "the moment the mod is validated" |
| "Don't re-open this as a live defect" | what "this" is | "that bug" |
| "Affects `PLOT_MECHANISM_MODS_WAVE_1` Part 1" | the subject | "The ruling affects" |
| "the item lists the revisions it is owed" | the subject of "it" | "the revisions that the spec is owed" |
| "never the three he described and then talked himself out of" | the subject | "The door family is never the three defs …" |
| "on/off per major feature/mechanic, …, all-off degrades gracefully" | five demands in one sentence | one bullet each |
| "Brief helpers that `reset --hard`, `checkout --` and `stash` are forbidden" | the grammar reads two ways | "Tell each helper in its brief: …" |
| "Pair it with the deletion rule directly below" | "it" and "below" | "this rule", "the next section" |
| ""Not my file" does not discharge it." | what "it" is | "this duty" |
| "D/F primitive rulings 18/19" | what D/F is | could not determine (below) |
| "(the belt carries those)" | what the belt is | could not determine (below) |
| "Revert if a clone strands work …" | what to revert | could not determine (below) |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 2 (`rule_doc_lint.py keep`) | a copy with "(1127 lines)" changed to "(a long file)" and one copy of `RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS` removed | 1 lost (the number 1127), exit 1. The id has other copies in the file, so its loss is not a lost span. |
| check 1 (`checkable.py compare`) | the same copy | 1 lost ("1127 lines"), exit 1 |
| check 2 | the final rewrite | 1084 spans, 0 lost, exit 0 |
| check 1 | the final rewrite | 579 items, 0 unfindable, exit 0 |
| `rule_doc_lint.py selftest`, `checkable.py selftest`, `batch_done.py selftest` | — | PASS; 19 of 19; GREEN 12 planted cases |
| `selftest_retired_era_gone.py`, `selftest_conductor_acts.py`, `selftest_rule_files_lose_nothing.py`, `selftest_close_gate.py`, `selftest_bar_rule_tuning_numbers.py`, `selftest_owner_objections.py`, `selftest_boundary_check.py`, `selftest_codex_advice.py`, `selftest_judge_refusal_records.py` | old, then new | PASS, then PASS |
| `acceptance_stop_rules_calibrated.py` (FAIL 2/7), `code_review_brief_accept.py` (FAILED 1), `selftest_conductor_authority.py` (6 failures) | old, then new | the same failures on the base and on the rewrite. None of the failures names `standing_rulings.md`. |

A lint artifact: `keep` reads the text between two italic quotes as one quote span. The first draft split the card
answers (a) to (k) into bullets, and the bullet dash broke 3 such spans. Those evidence paragraphs are back in their old
form. A first draft also put "retired" on the line after "Relentless", and `selftest_retired_era_gone.py` reads per
line. The line is re-wrapped.

Names of people: this run read the diff for names. "Conductor" goes from 25 to 29 uses. No other name is in the scope,
outside the owner quotes, which are unchanged.

## What the meaning read found

A fresh Opus reader (`rm-judge`, model opus) read the old and the new text of the section. The reader did not get the
writer's reasoning. The reader checked by script that all 40 owner quotes match word for word. The reader found 8 lines.
The writer fixed 7 and restored the old line for 1. The same reader then read only the repaired lines: 8 of 8 fixed, 0
new findings.

| first draft | why it was wrong | repair |
|---|---|---|
| "keeps a one-line rule for each topic" | "for each topic" is a new scope | "keeps a one-line rule and points here" |
| "tested … only on its home biome, never away from it" | a ban; the old text says only that no such test is owed | "No test away from the home biome is owed." |
| "a game that degrades gracefully when every switch is off" | the promise is about the mod | "a mod that degrades gracefully …" |
| "Six mechanics have an "Enable outside this biome" switch: Greentide, …" | the list names mods, not mechanics | "Six switches are named … The six switches are in Greentide, …" |
| "changes the shade" | old "either" covers the sun's strength too | "changes the shade or the sun's strength" |
| "Revert the pool if a clone strands work …" | adds an object; the reader reads "revert" as undo the disk-floor policy | old bare "Revert if …" restored; listed under "Could not determine" |
| "does the fix itself" / "does the remaining check, in the same sitting" | the same sitting covered only the check | "does the fix and the remaining check itself" / "Do both in the same sitting" |
| "A card can be outside the five acts, … Then the Conductor acts now" | the two conditions no longer read as both required | "If the act of a card is not one of the five, and no concrete evidence …, the Conductor acts now." |

After the repair read, the writer made no further edit.

## Conflicts (listed, not decided)

1. **What "Revert" acts on.** Root `CLAUDE.md` §Git: "Revert the pool if a clone strands work or the free space on `/`
   goes under the disk floor." This file: "Revert if a clone strands work …" with no object. The meaning reader read it
   as "undo the disk-floor policy". The two readings ask for different acts. The Conductor decides.
2. **What degrades gracefully with every switch off.** Root `CLAUDE.md` §Every mod ships superb Mod Settings: "a game
   that still works when every switch is off". This file: the mod "degrades gracefully". The two can be the same
   demand. This run did not determine it.

## Could not determine

| line | question | who would know |
|---|---|---|
| "A pit is depth 4 on the D/F primitive that rulings 18/19 already established" | what D and F stand for. `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` says "Rulings 17-29 (D/F primitive = 18 …)" in `flowworks_mod_definition.md`; this run did not read it to the end | the FlowWorks designer; `flowworks_mod_definition.md` |
| "The ruling is made and fully specified, and its build is in progress" | the item `PIT_SUPERDEEP_COLLAPSE_1` reads `ready`, not `doing`, on 2026-11-23. The build can be in progress without a claim. The line stays | the Conductor; the item's owner (BENCH) |
| "a trailing lesson/ledger commit (the belt carries those)" | what "the belt" is. Conversations of 2026-10-22 to 2026-11-05 use it for the process that commits ledger and lesson files that a run leaves. This run found no code of that name | the author of `disk.pool_breach` (`design/specs/2026-11-22-clone-pool-disk-floor/boundary.md`) |
| "Revert if a clone strands work, or if the free space on `/` goes under the disk floor." | what to revert (conflict 1) | the Conductor |

## Seen on the way (not this item's work)

The slot hook `.claude/hooks/block_agent_over_slots.py` runs beside `block_unbounded_agent.py` on each `Agent` call. A
spawn that the second hook refused still left a 90 s reservation from the first. With this run's allowance of N=1, three
retries of the one reader were refused as "slots_full … Running: reserved-0" while no helper ran. The reservation expires
by itself after 90 s (`RESERVE_S`). Polish line only: no run was voided, and the refusal clears with a wait.

## What this run did not test

- No agent run read the new text to do work. No measurement shows that an agent acts better on it.
- Sessions 2 to 5 of this batch rewrite the rest of the file. This run did not touch those sections.
- `CLAUDE.md` pointers into this file were not re-read one by one. Each heading in scope is unchanged, so each pointer by
  heading still finds its section.

## Second read of the repairs

Run 2026-11-23, item `RIMMANDRAKE_REREAD_REWRITE_REPAIRS_NO_READER_SAW_THEM`. One fresh Opus reader that made none of
these edits read each repair, restored line and late edit against the base text and the lines that travel with it. SAME
means that a reader of the new line acts as a reader of the old line. A gloss reads SAME when its source says the same.
His quotes: a script compared each quote of three words or more in the base with today's text, whitespace ignored. No quote differs (one match in the list was prose between two quotes).

| file | line read | verdict | what was done |
|---|---|---|---|
| standing | "keeps a one-line rule and points here" | SAME | none |
| standing | "No test away from the home biome is owed." | SAME | none |
| standing | "a mod that degrades gracefully when every switch is off" | SAME | none |
| standing | the six "Enable outside this biome" switches | SAME | none |
| standing | "changes the shade or the sun's strength" | SAME | none |
| standing | "does the fix and the remaining check itself", "Do both in the same sitting" | SAME | none |
| standing | "If the act of a card is not one of the five, and no concrete evidence …" | SAME | none |
| standing | late edit `de63778138`: "Revert the pool … return to at most 4 writers" | SAME | gloss true: commit `5e603a1d82` approved the pool for writers above 4 |
| standing | late edit `de63778138`: D/F is depth and fill; rulings 18 and 19 are in §20 and §21 | SAME | gloss true: `pit_superdeep_collapse_spec.md` line 8; `flowworks_mod_definition.md` lines 818 and 883 |
| standing | late edit `de63778138`: the clone's return step bundles a trailing commit | SAME | gloss true: `detached_helper.py` lines 49 to 50 |
| standing | late edit `de63778138`: the state of the pit build is read from its item | changed on purpose | none: the old "in progress" was state written as prose, and the item reads `ready` |
