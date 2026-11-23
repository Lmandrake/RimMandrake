# Result: `RIMMANDRAKE_REWRITE_OTHER_DOCS_AFTER_DELETE_DECISION`

Batch 16 of `batch_plan.md`. Files: `infrastructure/STRUCTURE.md`, `infrastructure/VALIDATION_LADDER.md`, `README.md`,
`LEXICON.md`. Run 2026-11-23.

Base: 5d5cf515ce13c7d4e839cb7599677d21a91fbe8c

Special rule: this run deleted no file. The delete candidates of `census.md` were not touched.

## Scores

| file | measure | before | after |
|---|---|---|---|
| `STRUCTURE.md` | bytes | 15,666 | 18,869 |
| | words in linted prose | 1,052 | 1,328 |
| | STE violations per 100 words | 5.23 | 2.26 |
| | sentences over 20 words | 19 | 0 |
| | flagged lines (mechanical) | 8 | 7 (all shout marks that the old file held) |
| | hand count (lines a cold reader cannot act on) | 14 | 0 that this run could resolve; 3 under "Could not determine" |
| `VALIDATION_LADDER.md` | bytes | 4,293 | 5,219 |
| | words in linted prose | 620 | 785 |
| | STE violations per 100 words | 4.19 | 2.17 |
| | sentences over 20 words | 8 | 2 |
| | flagged lines | 12 | 12 |
| | hand count | 6 | 0 that this run could resolve; 3 under "Could not determine" |
| `README.md` | bytes | 4,295 | 5,909 |
| | words in linted prose | 591 | 788 |
| | STE violations per 100 words | 3.38 | 0.63 |
| | sentences over 20 words | 12 | 1 |
| | flagged lines | 4 | 1 |
| | hand count | 5 | 0 |
| `LEXICON.md` | bytes | 4,025 | 4,159 |
| | words in linted prose | 48 | 75 |
| | STE violations per 100 words | 2.08 | 0.00 |
| | sentences over 20 words | 0 | 0 |
| | flagged lines | 0 | 0 |
| | hand count | 2 | 0; 1 under "Could not determine" |

The lint does not read table rows. Most of `LEXICON.md` and much of `STRUCTURE.md` is tables.

`LEXICON.md`: each table row is byte-identical to the base. Several rows are the owner's own edits (commit `bec6628a6d`)
or his ruling (commit `c2a078f336`). This run rewrote the opening paragraph only.

### The long sentences that stay

- `VALIDATION_LADDER.md`, 2: both are inside the owner's quote.
- `README.md`, 1: the experiment sentence. The meaning reader showed that a split of this sentence changes its meaning.

## The hand count

| file | old line | what a cold reader lacks | state after |
|---|---|---|---|
| STRUCTURE | "This file names homes" | what a home is | glossed |
| STRUCTURE | "Pinned" | what it means | glossed: must stay at the root |
| STRUCTURE | "Five entries in `.claude/skills/`" | false: 11 entries | no count; "the file carries no counts" is its own rule |
| STRUCTURE | "`GLOBAL_CLAUDE.md`: tracked mirror" | the mirror is out of date | says so, cites `census.md` |
| STRUCTURE | "Every tracked path is in exactly one" | false: the root holds more | excepts the root entries outside the seven tiers |
| STRUCTURE | the `src/Jawa/` row: six mods | none of the six is there | names the new home of five; `Jawa_Patches` was split up |
| STRUCTURE | the `*Fix/` row: eight folders | none is there | names the new home of seven; `SauridFrillFix` has no folder in `src/` |
| STRUCTURE | `MissingArtFixes/` | absent | says so (commit `78b6c1fb23`) |
| STRUCTURE | `observed/2026-08-13/dumps/` "the current generated-data home" | absent | says so, names the design target of `CLAUDE.md` |
| STRUCTURE | "per stamp", "the teardown" | coined terms | glossed |
| STRUCTURE | "Published by CHECK" | CHECK is a retired seat | says so |
| STRUCTURE | the items row with one cell | the table row was broken | two cells |
| STRUCTURE | the skills list of ten | not the roster; one entry moved out | says so |
| STRUCTURE | "One working tree, five seats" | the five seats are retired | the slogan stays; the next lines say what shares a tree now |
| LADDER | "tier", "L0" to "L4" | no line says that the headings are the tiers | one sentence |
| LADDER | "NRE" | the term | glossed |
| LADDER | "Blocked on: deep-serialize upgrade … (scalar-only today)" | stale: the upgrade is built | corrected from `JawaBenchTerrainTools.cs` |
| LADDER | "It hung a 589-mod game" | the subject | "The step" |
| LADDER | "an L3 sitting … stages … judges" in one sentence | where each step starts | four numbered steps |
| LADDER | `MASS_VALIDATION_LADDER_1` bare | a title, and its state | title; done in the ledger |
| README | "It is intended", "This is not merely" | the subject | names the project |
| README | `publish.py`, `mirror.py` with no folder | where they are | `src/RimMandrake/Utils/` |
| README | "the C# side cannot be built here" | false on Archmagi | `winbuild.py` builds it with the `dotnet.exe` of Windows |
| README | "no `install*.sh` or systemd unit exists" | false | names examples |
| README | "`infrastructure/agents/` … watch that login's health" | false: no file there mentions the login | removed |
| LEXICON | "say so loudly when one happens" | one of what | names the collision |
| LEXICON | "he", "him", "his" in the tables | who | glossed: Mandrake |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of the new `STRUCTURE.md` with "~430 MB" and `ASHKARR_WORLD_DEFINITION.md` removed | 3 lost, exit 1 |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 3 lost, exit 1 |
| check 1 | the repaired `README.md` | 1 lost: the short path `rimflow/login_watch.py`. The writer put it back. |
| check 1 | final, each file | 46, 17, 9 and 1 items; 0 unfindable |
| check 2 | final, each file | 193, 28, 43 and 2 spans; 0 lost |
| `checkable.py selftest`, `rule_doc_lint.py selftest`, `batch_done.py selftest` | — | 19 of 19; 18 PASS lines; GREEN, 12 planted cases |
| `selftest_retired_era_gone.py`, `selftest_game_names_prose.py`, `selftest_skills_by_work.py`, `selftest_expectations_l2.py`, `.claude/hooks/selftest_documented_commands.py` | new | all exit 0 |

The path check: this run compared about 100 paths of `STRUCTURE.md` with `git ls-tree -r HEAD` (2026-11-23). The absent
paths are the ones that the new text marks.

Names of people: "Lukas Mandrake" and "Mandrake" stay. No name was lost.

## What the meaning read found

One fresh Opus reader per file (rm-judge, model opus), one at a time. Each reader got the old and the new text, and not
the writer's reasoning.

- `VALIDATION_LADDER.md`: 0 findings. After the read, the writer shortened the `get_defs` line.
- `LEXICON.md`: 0 findings. Before the read, the writer removed one gloss of its own that was wrong ("the word "it" means
  the term of the row").
- `STRUCTURE.md`: 5 findings. All are repaired.

| first draft | why it was wrong | repair |
|---|---|---|
| "except the root entries that the Root section names" | more root entries exist than the section names | "outside the seven tiers" |
| "The line of an absent path says that it is absent" | `DefDump_OFFICIAL/` is gitignored and not in this clone | its row says so; one line says that a gitignored path can be absent from one clone |
| "Each writer now works in its own clone" | wider than `CLAUDE.md` §Git | "each seat has its own clone, and a helper works in the clone that its brief names" |
| "five" removed | reported; the count was false | no repair |
| "No file matches this pattern now" | four closed run sheets exist | says where they are |

- `README.md`: 7 findings. Six are repaired. The seventh (the C# build) is a correction that the reader confirmed.

| first draft | why it was wrong | repair |
|---|---|---|
| "Those pipelines must do more than execute …" | turned part of a question into a duty | the one sentence is back |
| "An experiment cannot test taste if …" | the "because" was lost | "The reason: …" |
| one installer named | more exist | named as examples |
| "The root also holds `pipe` and `sync`" | `pages` too | added |
| "use only the standard library" | the programs import sibling modules | says so |
| "The lines marked 2026-11-23 were measured then" | some changed lines had no mark | the footer covers the section, with its exception |

The reader also reported one false line of the old text: the seat windows run from tooling "outside this repo's own
files". `launch_fleet.ps1` is in the repo. The new text says so. No second reader read the repairs.

## Conflicts (listed, not decided)

1. **Who may move `skills/`.** `STRUCTURE.md`: "gated on the owner". Root `CLAUDE.md` §Only five acts stay his: the
   Conductor may do every act but five, and this act is not one of the five.
2. **`Jawa/` or the three tiers.** The owner's promotion test says "Remake → `Jawa/`". `design/NAMING_SCHEME_PLAN.md`
   names RimMandrake, RimStarWars and RimUtinni, and root `CLAUDE.md` says that "Jawa" is lore text only.
3. **Which skill to load when.** `STRUCTURE.md`: "`CLAUDE.md`'s job". Root `CLAUDE.md` §Skills gives the roster to
   `skills/README.md`.
4. **The v1/v2 authority.** `STRUCTURE.md` says "Check `V1_CHAIN.md` before you queue anything". Root `CLAUDE.md` sends
   open work to mod folders and the one list.
5. **`WORLDGEN_FACTION_CHECKLIST.md`.** Its row is "for world creation". Root `CLAUDE.md`: there is no worldgen feature.
6. **`observed/` tracks.** `STRUCTURE.md`: only `MANIFEST.json` is tracked. The reader measured 0 tracked `MANIFEST.json`
   files and 154 other tracked files under `observed/`.
7. **`vendor/mod_sources/` size.** "~430 MB". The reader measured 48 KB in this clone and 141 MB in the mirror.
8. **The size of the minimal list.** `VALIDATION_LADDER.md` and `rimworld-modding` §2: 19 mods.
   `infrastructure/GAME_STATE_WORKFLOW.md` and `rimworld-load-round`: 13 mods. All say 22 seconds.
9. **The levels.** `VALIDATION_LADDER.md`: five tiers. `src/RimMandrake/rimflow/model.py` `LEVELS`: seven, with GREEN-MIN
   and GREEN-FULL between L2 and L3.
10. **SteveDesktop.** `LEXICON.md`: "a game that runs test jobs". Root `CLAUDE.md`: two games, Steve1 and Steve2. Also
    Archmagi has two games. The row stays: the owner reviewed this file.
11. **`jawa/get_defs`.** `skills/rimworld-modding/SKILL.md` §2 and `skills/rimbridge/SKILL.md` say "scalar-only" and do
    not name `deep=true`. A skill changes only in a curation session.
12. **The order of the minimal and full list.** `LEXICON.md`: a pass on the minimal list "proves nothing about his real
    game". Root `CLAUDE.md`: "Work that a tier mod list can prove goes to any free game".
13. **`infrastructure/README.md`** still has the "five" symlinks and the four seat files. It is a delete candidate, so
    this run left it.
14. **The root table of `STRUCTURE.md`** has no row for several root folders, and the state table has no row for many
    entries. The file's own rule wants a row for each. A rewrite does not add them.

## Could not determine

| line | question | who would know |
|---|---|---|
| "The charter describes them" (`deployed/`) | which charter; `CHARTER.md` does not name the two paths, `deployed/README.md` does | the Conductor |
| "what earns a skill versus a traps entry" | if the traps index is still the home of a lesson; `CLAUDE.md` sends lessons to `infrastructure/state/lessons/` | the Conductor |
| "redesign #4" (`CHARTER.md` row) | what redesigns 1 to 3 were | the Conductor |
| "eaten defs" (L2) | a def that a patch or a duplicate removes, probably | the author of `expectations_l2.py` |
| "the builder's grade" (L3) | the model grade of the builder, probably | the Conductor |
| "augmentors", "tile augmentor" (L4, his words) | the kind of def | the owner |
| `LEXICON.md`, Test Pilot: "check that it produces the fail" (his edit) | probably a check that goes red for the reported reason | the owner |

## What this run did not test

- No agent acted on the new text in a measured run.
- No reader read the repairs after the meaning read.
- The in-game LLM call line of `README.md` and the RimSage login line are UNMEASURED.
- The facts behind lines that this run did not change are not all checked again.
