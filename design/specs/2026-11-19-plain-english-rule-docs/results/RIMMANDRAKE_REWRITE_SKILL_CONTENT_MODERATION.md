# Result: `RIMMANDRAKE_REWRITE_SKILL_CONTENT_MODERATION`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-content-moderation/SKILL.md`. Run 2026-11-23.

Base: `5bc3126cec`
Also: skills/rimworld-content-moderation/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 22,350 | 26833 |
| words in linted prose | 3,204 | 3791 |
| STE violations per 100 words | 4.81 | 1.98 |
| sentences over 20 words | 65 | 34 |
| flagged lines (mechanical) | 27 | 21 |
| lines that a cold reader cannot act on (hand count, by the writer) | 9 | 0 |

Most of the 34 long sentences are two short sentences that the lint joined at a bold lead, an emoji or a closing mark. One
is an owner quote. Three are a few words over 20 around a code span (`CommonalityOfAnimal`, `ConfigErrors`, the
`FactionDef` fields). The front matter and every heading stay byte for byte.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "hunting magenta" | what magenta means | "the colour of missing art" |
| "beyond the builder's grade" | which grade | "the grade of the model that built the work" |
| "the biome's tile augmentor" | what it is | the meaning from `VALIDATION_LADDER.md` |
| "contact sheet" | what it is | defined at first use |
| "the donor's art" | what a donor is | "the mod that first made the def" |
| "kill list" | what it is | defined at Cherry Picker |
| "does not resolve → the cut is already in effect" | false against the paragraph above it | replaced by the table of what Cherry Picker does per type |
| "throws NRE" | what NRE is | defined |
| "'All its animals are cut' (below)" | where below is | the words stand alone |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy with 5 planted losses (`OuterRim_Geonosian`, 1,308, `AA_FlamingoPhoenix`, the 2026-08-19 quote, `BIOME_CAST_REFS_BREAK_MAPGEN_1`) | 1 lost (the quote). The id is also in the history file, so it is not a loss. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 3 lost, exit 1. It did not see the quote. |
| check 1 | the final rewrite, with `--also` | 37 items, 0 lost |
| check 2 | the final rewrite, with `--also` | 140 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | PASS; 19 of 19; GREEN, 12 cases |
| 11 selftests: skills (3), guiding prose, game-names prose, retired era, and those that use the edited tools (5) | new text | 11 of 11 PASS (before the last round of comment edits) |
| `py_compile`; `apparel_tag_audit.py --anyway`; `thing_contact_sheet.py -h` | the edited tools | run; the new printed lines show |

Names: no real person is named in either text. `BENCH` is a seat name; `DECIDE` and FOUNDRY are retired seat names.

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read both texts without the writer's reasoning. It found 10 real items, and
7 trivial items.

| finding | repair |
|---|---|
| REAL: "still dressed from the general pool" (copied from the `apparel_tag_audit.py` docstring) is false | `PawnApparelGenerator.CanUsePair` read; skill, docstring and printed line corrected |
| REAL: the two audit tools do not find emptied tags | the skill says so, and that the zero is not a measurement |
| REAL: the two audit tools compare only the mod count | the skill and both docstrings say so; "compare the mod sets yourself" |
| REAL: "Cherry Picker runs first in the load" | "at game startup, after the XML and the patches" |
| REAL: presence is evidence for the 13 deleted types | narrowed to the first row of the table |
| REAL: "every census … includes cut content" | "an unfiltered census"; XML and dump separated |
| REAL: what an unresolved old key means was lost | restored per row |
| REAL: `from_log()` stops at a FAILED line, and does not read the second block | a trap bullet |
| REAL: the `coastalWildAnimals` line had no action | "Sweep that list after an animal cut" |
| REAL: when the `FactionDef` patch helps | said |
| trivial: `apparel.tags`, `PowerDef`/`PsycasterPathDef`, "it" in the 74-rows line, "every other spot-checked entry" | repaired |
| trivial: "already know by sight" moved; extractor interpreter; "every removal" | left: no meaning lost; the CP code supports the new words |

The same reader then read the repairs and the edits in the other files. It found 0 real items in the skill and the history
file, and 5 real leftovers in edited files: `apparel_tag_audit.py`, `genome_matrix_build.py`, `biome_animal_conflicts.py`,
`thing_contact_sheet.py` and `validate_save_artifact.py`. All 5, and the 4 trivial ones, are repaired. No reader read
those last repairs. After the first landing (ba9a9e0c7e), the prose check of `./publish` named 15 lines. The writer repaired
them (subjects in place of pronouns, two terms). No reader read those lines either, or the next-line wording of "in either
direction".

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| the dump is captured BEFORE Cherry Picker / Cherry Picker runs first, deletes 13 types and neuters the rest | the second; the fact file and 10 tools corrected too | 1: `Player.log` lines 1279 and 2817 of one load; capture `2026-11-23T19-47-11Z`; `RemoveDef` in `CherryPicker.dll` |
| "does not resolve → in effect" stood under a correction that reversed it | old text to the history file | 1: the same |
| a Cherry Picker animal cut makes `wildAnimals` refs throw / the def stays and the weight is 0 | the rule now covers a def that leaves the load | 1: `CherryPicker.dll`; 178 entries at commonality 0; "0 threw" in the log |
| `FactionDef` cuts are no-ops / three world-creation fields change, and a gate skips some | the second | 1: `CherryPicker.dll` |
| `ConfigErrors` throws on one unresolved animal or plant record / animals only, dev mode, two or more | the second | 1: `BiomeDef.cs` 1.6 (RimSage) |
| vanilla art cannot be rendered offline / the bundle cache | the second; `animal_contact_sheet.py` docstring corrected | 1: `extract_bundle_textures.py`, `--bundles` |
| "build a weapon sheet the same way" / `thing_contact_sheet.py` exists | the tool is listed | 1 |
| "a def dump is disk, not runtime" / the dumper runs in the game | "mod XML on disk is not the running game" | 1: `DefDumper.cs` |
| the ikwa is cut / un-cut | un-cut, evidence kept | 1: `OWNER_EXCLUDE`; the live list |
| a contact sheet is built from the dump / from mod XML | the second, in two sheet tools | 1: `def_inventory.build` |
| `cherrypick_build.py`: BiomeDef is deleted / `implemented = false` | the second | 1: `CherryPicker.dll`; 11 of 11 in the dump |
| who may cut (the skill did not say) | the owner, or the Conductor as a recorded act | 2 and 3: `delegation_policy.md` §2 |
| `mod_patterns.md` cites a deleted study | `git show` command | 4: d3487d7b3f |

## Could not determine

| line | question | who would know |
|---|---|---|
| `biome_animal_conflicts.py`: cut animals have no `wildBiomes` entry in the dump | what empties the list: Cherry Picker only zeroes it | a capture with the REVIEW profile |
| `cherrypick_build.py`, the 21 xenotypes: "expected cross-reference warnings" | Cherry Picker runs after cross-references resolve, so the warnings may never come. Left as written. | a log of that load |

## What this run did not test

- No live game was driven. The log and captures of ArchBig were read only.
- `coastalWildAnimals` after a cut is read from the code, not seen in game.
- `cherrypicker.from_log()` was not changed: no log with a FAILED line was found.
- The trigger evals were not run, because the description did not change.
- No measurement shows that an agent behaves better with the new text.
