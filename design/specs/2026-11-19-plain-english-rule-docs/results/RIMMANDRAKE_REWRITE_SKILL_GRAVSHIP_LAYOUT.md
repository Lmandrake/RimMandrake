# Result: `RIMMANDRAKE_REWRITE_SKILL_GRAVSHIP_LAYOUT`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/gravship-layout/SKILL.md`. Run 2026-11-23.

Base: `c7a4f98b98`
Also: skills/gravship-layout/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 24,269 | 27860 |
| words in linted prose | 2,681 | 3312 |
| STE violations per 100 words | 5.04 | 2.36 |
| sentences over 20 words | 52 | 27 |
| flagged lines (mechanical) | 27 | 2 |
| lines that a cold reader cannot act on (hand count, by the writer) | 9 | 0 |

The long sentences that stay are of three kinds. Most are two short sentences that the lint joined at a bold lead. Others
hold a command, a code name or a game string. One holds the owner's quote. The 2 flags are the bold names THE FOUR GATES and
CLAIM EVERY PART.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "⚠️ Overtaken by the section above — read that first" | which of two sections binds | the live route is first; the old route says that nobody built it |
| "That is a CHECK job, queued as B-v2" | the queue file is gone | deleted; record in the history file |
| "Until it exists, a layout can only enter the game at world creation" | what "it" is; also false | deleted |
| "Three more tools", with four rows | the count | four |
| "offline-first" | what to do | which tools plan before they write, and which one does not |
| "the choose-page's ship marker is consumed" | which marker | the landing marker of a ship in flight |
| "no restart-into-Defs dance" | the meaning | no mod, no `About.xml`, no restart |
| "Colour the hull with STUFF, not paint" beside `repaint_hull.py` | which one to use | paint; stuff is named as the only colour that an export keeps |
| "VGE" | the meaning | Vanilla Gravship Expanded |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without 4,424 W, `onlyRequiresLooseConnection`, (2026-09-02) and 380 | 0 lost. Check 1 is blind to all four. |
| check 1 | the first draft | 4 quotes lost, so check 1 can fail; repaired |
| check 2 (`rule_doc_lint.py keep`) | the planted copy | 4 lost, exit 1 |
| check 1, check 2 | the final rewrite, with `--also` | 42 items, 0 lost; 217 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | 18 PASS; 19 of 19; GREEN, 12 cases |
| `selftest_skills_by_work.py`, `selftest_guiding_prose.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py` | final text: the first, second, fourth and sixth; before the repairs: all six | exit 0 |
| `selftest_gravship_layout.py` (new) | the old library, then the new library | 4 of 5 FAIL, then 5 of 5 PASS |

Names: neither text names a person, except "the owner". The front matter and all 8 fenced blocks are byte for byte the same.

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read both texts without the writer's reasoning. It found 5 items to repair. It
checked the other corrections against the source and found each one true, with small gaps (below).

| finding | repair |
|---|---|
| the root of a layout inside a mod is `<Defs>`, not the layout element (added by the draft, false) | corrected here and on the boundary page |
| "design notes as named zones" is false; the code sends letters | "letters" restored; the stale docstring of `ship_dress.py` corrected |
| "the library carries the whole file" is too strong | the blind area of `--roundtrip` is named |
| "the owner refused" is stronger than his words | "disliked" |
| "plan each step offline": `ship_dress.py` has no dry run | the row says so |
| small gaps: the radius rises only below 79; the landing tool pauses the game; claiming beside the print script | all three added |

The same reader then read each repair, the history file and the two changed reference files. It found nothing real. Every
changed line of those files was read.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| the choose page is after `Page_CreateWorldParams` / after `Page_SelectStoryteller` | the second | 1: `Patch_Scenario_GetFirstConfigPage.cs`; `Scenario.GetFirstConfigPage` |
| `validate()` needs a `GravEngine` thing / an export holds none | the library is corrected, test first | 1: `GravshipExporter.BuildLayout`; 6 of 6 exports |
| the round trip proves the format / the library dropped 26 settings blocks of the ring export | the library is corrected, test first | 1: `selftest_gravship_layout.py` |
| settings fields never populated / later exports hold them | the second | 1: six exports read |
| rooms spawn under fog / the code clears all fog | both sides stated; live is UNMEASURED | 1: `HarmonyPatch_DoGravship.UnfogEntireMap` |
| a preview is placed by hand / the export writes it | the second | 1: `ShipPreviewRenderer.Capture` |
| `ShipLayoutDefV2` is never a Def / the class is a Def | only a loose file is never registered | 1: `ShipLayoutDefV2.cs`, `1.6/Defs` |
| `BuildFromLayout` is pure / it changes the `GravEngine` def | the second | 1: `ExpandGravEngineRange` |
| B-v2 in `CHECK.md` / no such file | deleted, also in `references/validation-plan.md` | 4 |
| no mid-game import / `print_gravship.py` | the script; its docstring that cited the old line is corrected | 1 |
| colour the hull with stuff / paint is the only wall-colour tool | paint; stuff named as what an export keeps | 1 and 5: `repaint_hull.py`; his line in 57f92fcebb |
| an extender adds +500 / 4,680 to 51,480 with nine | no fixed number; read the settings; also in `references/measured-2026-08-13.md` | 1: the settings file; the arithmetic is in the history file |
| the landing tool can wedge / `jawa/gravship_land` skips the chain | both stated | 1: `JawaBenchGravshipTools.cs` |
| a load costs 23–30 minutes / many minutes, a small tier takes seconds | no figure here | 3 |
| the licence permits adaptation / public domain | the second | 1: `LICENSE` |

## Changed outside the skill file

- `src/RimMandrake/Utils/gravship_layout.py`, with its first boundary page and selftest.
- The docstrings of `print_gravship.py` and `ship_dress.py`.

## Could not determine

| line | question | who would know |
|---|---|---|
| the factor 1.04 between the settings and the measured caps | its source | a live read of the `SubstructureSupport` stat explanation |
| "36 Aurebesh word decals" | 37 names match in the mod; one can be a base | the def file of `Neronix17.OuterRim.FurnitureAndDecor` |

## What this run did not test

- No live game was driven. Fog on arrival, the choose page and the new `save` output in the game are UNMEASURED.
- No measurement shows that an agent authors a better ship with the new text.
- The trigger evals were not run, because the description did not change.
- The lesson in the inbox whose home is this skill was not folded in: the item covers the rewrite only.
