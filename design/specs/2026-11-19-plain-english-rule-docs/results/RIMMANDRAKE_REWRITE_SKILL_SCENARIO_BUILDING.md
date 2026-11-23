# Result: `RIMMANDRAKE_REWRITE_SKILL_SCENARIO_BUILDING`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-scenario-building/SKILL.md`. Run 2026-11-23.

Base: `067ef51d2f12b37d0ed08055b0d2b3867effbf51`
Also: skills/rimworld-scenario-building/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 11,925 | 16,141 |
| words in linted prose | 1,096 | 1,632 |
| STE violations per 100 words | 5.57 | 1.47 |
| sentences over 20 words | 22 | 10 |
| flagged lines (mechanical) | 29 | 29 |
| lines that a cold reader cannot act on (hand count, by the writer) | 8 | 0 |

The long sentences that stay: two short sentences that the lint joins at a bold lead, and one line with two quotes.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "The question that governs everything: WHEN is this fixed?" / "Getting this wrong" | what "this" is | a wrong bucket |
| "Accept it early rather than discovering it" | what to accept | the start ships as a save |
| "`StatFactor` is the most abusable part" | what the part does | one multiplier on a stat, for every thing that has the stat |
| "a quest can still fire one deliberately" | which call gets past each part | `forced`, `bypassStorytellerSettings`; the callers without `CanRun` |
| "a legible difficulty curve would fight the fiction" | who reads it | a curve that the player can read |
| "the threat fractions at 0" | which field | `overrideAnomalyThreatsFraction` |
| "a real bug, found in a real state file" | nothing to do | moved to the history file |
| "Most ... problems are really zonation problems" | whether our world uses a planet type | the spec names it; the hand work stays |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without `sunlightFactor` and one quote, no `--also` | 2 lost (the planted quote; the quote that moved to the history file), exit 1. Check 1 did not see `sunlightFactor` |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 3 lost (the planted code span; the number 72 and the quote that moved), exit 1. Check 2 did not see the planted quote |
| check 1, check 2 | the rewrite, with `--also` | 6 items, 0 lost; 94 spans, 0 lost (also after the last repair) |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | pass; 19 of 19; GREEN, 12 cases |
| `selftest_warn_skill_unwired.py`, `selftest_guiding_prose.py`, `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_image_skills.py`, `selftest_retired_era_gone.py` | the first draft | exit 0 each |

No test names the skill file itself. Names of people: none in the old text or the new text. The front matter is byte for
byte the same.

## What the meaning read found

A fresh Opus reader (rm-judge, read-only) compared every line of both texts, the history file and the diff of the two
design files. The reader checked the corrections against a decompile of the installed game.

| finding | repair |
|---|---|
| significant: "at 0 the storyteller draws no Anomaly incident" is false. The slider gates only `ThreatSmall` and `ThreatBig` | skill, history, both design files. The writer read `StorytellerComp.UsableIncidentsInCategory` and `IncidentCategoryDefs.xml` |
| significant: lines of the spec's R-S4, R-S5 and B1 contradicted the corrected lines around them | four lines corrected |
| significant: "use no planet type" works against the spec's planet type row | the skill says to set the spec's planet type |
| significant: the planet type control is not on a world-creation page | the skill names Mod settings |
| significant: four factions come back at load | an exception line in the skill; `Empire` corrected in the history file |
| `hideOffMap` was not explained; the invalid-scenario line had no evidence | added to the history file |

The reader did not confirm "marks the scenario invalid". The writer read it in `GameDataSaveLoader.TryLoadScenario`.
No reader read the repairs. Each repair follows what the reader proposed or a source line that the writer read. Our
scenario already disables the `Misc` and `GiveQuest` Anomaly incidents (`Scenario_Utinni.xml`), so no mod fault follows.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| 0% is on `anomalyThreatsActiveFraction` and its pair / on `overrideAnomalyThreatsFraction` | the second | 1: `GameComponent_Anomaly.AnomalyThreatFractionNow` |
| nothing auto-spawns under `AmbientHorror` / 0.15 by default; `Misc`, `GiveQuest` and `GrayPall` ignore the slider | the second | 1: `Dialog_AnomalySettings`, `StorytellerComp`, `WeatherDecider` |
| harbinger trees need low pollution / they cannot spawn with no monolith | the second, in two design files | 1: `GenStep_HarbingerTrees` |
| the Anomaly slider shows only on Custom / the entry window shows it with each preset | the second, skill and spec | 1: `Dialog_AnomalySettings`, `StorytellerUI` |
| a non-Custom preset loses the Anomaly value / the preset keeps it | the second, in the spec | 1: `SetupNonCustomDifficultyAnomalySettings`, `Difficulty.CopyFrom` |
| pawn modifier parts hit everyone / `chance` and `context` | the second | 1: `ScenPart_PawnModifier` |
| `DisableQuest` lets a quest fire one deliberately / only callers without `CanRun` | the second | 1: `QuestScriptDef.CanRun` |
| `StartingHumanlikes` / `HAR_StartingHumanlikes` | the second, marked as a mod part | 1: the mod's `ScenPart.xml` |
| `scariaRotChance` is animal hostility / corpse rot | the second | 1: `Pawn.Kill` |
| the save holds no faction list / it can | the second, skill and spec | 1: `WorldInfo.ExposeData` |
| a `PlanetTypeDef` does zonation better than a person / one hand-made map | the second | 3: root `CLAUDE.md` §There is no worldgen feature |
| the frequency "dropdown" / a slider | a slider | 1: `Dialog_AnomalySettings` |

None goes to the owner.

## Changed outside the skill file

`references/history.md` (new), `design/Jawa/worldbuilding/SCENARIO_SETTINGS_SPEC.md`, `design/V2_DREAMS.md`.

## Could not determine

None.

## What this run did not test

- No live game was driven. Each engine fact was read in the decompiled 1.6 source or the shipped defs.
- The count of 72 ScenPartDefs was not made again. It is in the history file as the old text stated it.
- The field list of the Alien Worlds Framework was read in its shipped source file, and found in its 1.6 DLL by a literal
  search (`MEASURE_ALLOW_SCAN=1`). What each field does was not tested.
- No measurement shows that an agent behaves better with the new text.
- The trigger evals were not run, because the description did not change.
