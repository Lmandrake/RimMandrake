# Result: `RIMMANDRAKE_REWRITE_SKILL_SAVEGAME`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-savegame/SKILL.md`. Run 2026-11-23.

Base: `84a83f57a5d5ab5d738b8fa7dc4357e0ed99bba6`
Also: skills/rimworld-savegame/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 14,282 | 18,258 |
| words in linted prose | 1,775 | 2,532 |
| STE violations per 100 words | 4.39 | 1.74 |
| sentences over 20 words | 35 | 23 |
| flagged lines (mechanical) | 20 | 15 |
| lines that a cold reader cannot act on (hand count, by the writer) | 9 | 0 |

Each long sentence that stays is two short sentences that the lint joined, or a sentence that holds an owner quote or a long
path. The joins are at a bold lead or a quote. The flags are emphasis marks on the worst traps. They were there before.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "The paint-once rule covers a tile" | where that rule is | cites `CLAUDE.md` by heading |
| "check the live world's tiles, decoded" | the tool that decodes them | `WorldGrid(save).census()`, with its limits |
| "VEF's quest-chain framework" | what VEF is | named in full |
| "the thing-ID reference graph" | what the graph is | defined under the table |
| "Those go through `rimbench/savemap.py` or the live bridge" | which tool for which data | one tool for each kind of data |
| "`measure explain <save>.rws`" | where `measure` is | the `cli.py` of `measuring-large-artifacts` |
| "shortHash" | what a shortHash is | defined in §5 |
| "Leaving it alone is safe by construction" | who must not act | "When nobody touches the grid" |
| "never a parent while its children are still in flight" | which element to clear | says which element must stay |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`), with `--also` | a copy without `MEASURE_ALLOW_SCAN=1`, one path, "7,813 bytes", "2026-08-18" and "~500 KB" | lost spans listed, exit 1 |
| check 2 (`rule_doc_lint.py keep`), with `--also` | the same copy | 5 lost, exit 1. Check 2 did not see "7,813", which history.md also holds. |
| check 1, check 2 | the rewrite, with `--also` | 27 items, 0 lost; 143 spans, 0 lost (run again after the last edit) |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | pass; 19 of 19; GREEN, 12 cases |
| `selftest_block_blind_scan.py`, `selftest_warn_skill_unwired.py`, `selftest_guiding_prose.py`, `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py` | the first draft | exit 0 each |

Names of people: none in the old text or the new text. The front matter is byte for byte the same.

## What the meaning read found

A fresh Opus reader (rm-judge, read-only) read every line of both texts without the writer's reasoning.

| finding | repair |
|---|---|
| significant: the head and "hand-tune a crew" give two answers; canonical saves have no condition | the bridge for other changes; the condition on canonical saves; the rows say "low risk" |
| significant: `unresolved()` `[]` is not proof that the dump is right | the dump must come from the mod set of the save; an empty list alone is no proof |
| the live world became one save | every keeper save; the live game when newer |
| `<def>NAME</def>` cannot match a longer defName (false in the old text too) | corrected, and listed in history.md |
| the general lesson on Scribe state was narrowed to quest mods | general again; VEF is one case |
| `paint` and `write` still read as steps | marked "do not use" in the code block |
| the roof route is not named | `jawa/set_roof_batch` |
| `measure explain` names `savemap.py` for biomes | the skill warns of it |
| `missing_mods` only warns in the game's menu | said |

The same reader then read each repair. Finding 1 needed the words on a resave of a canonical save. The history line on the
search needed a correction. Both are repaired. The reader also proposed a new title for §3. The title stays, because headings
stay, and the first line of §3 sends the reader to the head. No reader read those last two repairs, nor the line break of the
`missing_mods` line and "The bridge also paints".

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| the skill teaches save edits / "Please don't write to the savegame file anymore." (2026-08-18) | no painted world or map; a small ordered repair is allowed | 2: his words of 2026-09-06 on `DROID_ASIMOV_SAVE_SCRUB_1`; `worldmap.py` `write()` raises |
| the save does terrain, rock, water, roofs / the bridge does | the bridge | 2, and 1: `jawa/set_terrain_batch`, `jawa/set_roof_batch`; nothing calls `SaveMap.paint` |
| `lifecycle.md`: the canonical resave is owner-reserved / root `CLAUDE.md`: the Conductor may do all but five acts | the owner or the Conductor window | 3 |
| snow depth is a shortHash grid / a float as a ushort | the second | 1: `SnowGrid.ExposeData` (1.6 source) |
| `foundationGrid` is uniform / it varies | it varies on R3 | 1: `SaveMap.census("foundation")`: 59,225 `0`, 3,275 `Substructure` |
| biomes through `savemap.py` / `worldmap.py` | `worldmap.py` | 1: `GRIDS` in `savemap.py` |
| things are grid indices / Things are XML | only compressed things are indices | 1: `IsSaveCompressible`; R3 holds 6,605 `<thing>` elements |
| the `missing_mods` gate is unconditional / it has an override | it has one | 1: `lifecycle.md`, `northstar_site.py` |
| the newest autosave tells the loaded set / `jawa/running_mods` | the tool; the autosave without a bridge | 1: `JawaBenchNorthstarTools.cs` |
| a search with `<def>NAME</def>` matches a longer name / it cannot | it cannot | 1: the string itself |
| never clear a parent early / never clear a child early | the child | 1: the order of `end` events |
| a reload is ~23–30 minutes / ~15 minutes | `rimworld-load-round` holds the times | 4: the figure is in history.md |
| `traps.md`: captures from 2026-11 write a string hash / the 4 on disk write a number | some captures | 1: 5 def types in each of the 4 captures |

None goes to the owner.

## Changed outside the skill file

`references/history.md` (new), one line of `references/traps.md`, the docstrings of `src/RimMandrake/Utils/rimbench/savemap.py` (no
code), `design/RimMandrake/rimworld_file_lore.md` ("snow") and `design/RimMandrake/map_content_injection_research.md` ("pollution").

## Could not determine

- Which search gave the 9 hits of 2026-09-14. The seat that ran it would know.
- What an edit of `foundationGrid` does. Only a live test shows it.

## What this run did not test

- No live game was driven. `measure explain` ran. `SaveMap` was run read-only on R3.
- `SaveMap.write()` in text mode was read in the code, not run.
- `artifacts.py` of `measuring-large-artifacts` (repo MandrakeWorkflows) still names `savemap.py` for biomes. That repo is outside
  this clone. The skill now warns of that line.
- The trigger evals were not run, because the description did not change.
