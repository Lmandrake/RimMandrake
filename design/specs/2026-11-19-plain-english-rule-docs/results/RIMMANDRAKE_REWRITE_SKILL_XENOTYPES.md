# Result: `RIMMANDRAKE_REWRITE_SKILL_XENOTYPES`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-xenotypes/SKILL.md`. Run 2026-11-23.

Base: `f8661e0c431ecf2bffa2a600ce8e1db805678ff0`
Also: skills/rimworld-xenotypes/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 24,706 | 31,337 |
| words in linted prose | 2,786 | 3,759 |
| STE violations per 100 words | 4.20 | 1.70 |
| sentences over 20 words | 51 | 32 |
| flagged lines (mechanical) | 34 | 33 |
| lines that a cold reader cannot act on (hand count, by the writer) | 9 | 0 |

The flags that stay are emphasis marks and a few pronouns. The long sentences that stay: an owner quote; sentences that hold a path, a code form or a list; and
bold leads that the lint joined to the short sentence after them.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "Measured on this project's 587-mod 1.6 stack … `src\Jawa\RimMandrake_StarWarsRaces`" | the folder is gone | the live folder named |
| "OPEN, and do not guess it" (which colour renders) | what to do | the engine's pick, from the code |
| "The survivor expires … That sentence was measured" | which sentence | the result named |
| "the live Jawa xenotypes are `MandrakeJawa` and `RimMandrakeJawa`" | neither name loads now | the `RSW_` names |
| "Bridge rights belong to CHECK — ask before driving" | CHECK is a retired seat | `game_lock.py claim` |
| "The switch is … not in your def" / the last bullet: the mod ships a postfix | which of the two | FA's switch, then our shipped opt-out |
| "keep the two in step by hand" | they differ on purpose | which three genes differ, and why to keep them |
| `genome_register.html` as "the rendered result" | the page is deleted | removed; `CANDIDATE_PACKS` named |
| "write it HERE, not only into a script" | a skill is edited in curation only | `lessons.py add` |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of the rewrite with "29 / 35 / 5", a date, a code span and part of the owner quote changed, no `--also` | the date and the owner quote listed as lost |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 26 lost, exit 1 |
| check 1, check 2 | the first draft, with `--also` | 2 lost; 3 lost. Each one is restored |
| check 1, check 2 | the rewrite after the last edit, with `--also` | 24 items, 0 lost; 199 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | pass; 19 of 19; GREEN, 12 cases |
| `selftest_one_path_seam.py`, `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_warn_skill_unwired.py`, `selftest_guiding_prose.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py`, `selftest_checkers.py` | the first draft | exit 0 each |
| `selftest_gen_races_mod.py`, `selftest_fa_optout.py` | the repo | PASS each |

Names of people: the old text holds none, and the new text holds none. The front matter is byte for byte the same.

## What was measured for the corrections

- **RimWorld 1.6** was read with RimSage: `Pawn_GeneTracker`, `GeneDef`, `XenotypeDef`, `XenotypeChance`, `XenotypeSet`,
  `PawnGenerator`, `DirectXmlToObjectNew`, `ParseHelper`, `Pawn_StoryTracker`, `PawnRenderTree`, `PawnRenderNode`,
  `CustomXenotype`, `XmlInheritance`, and the vanilla gene and faction defs. No game was driven.
- **The live files** (read only): `ModsConfig.xml` (the three donors are off), FA's settings file, `MandrakeJawa.xtp`, the
  BTD and Outland mod folders, the FA def folder.
- **StarWarsRaces** was counted with ElementTree. No `xenotypeChances` in our `Defs` holds an `<li>` (193 read). No head
  type of ours is in the global pool (128 read).

## What the meaning read found

A fresh Opus reader (rm-builder, read-only) compared every section of both texts without the writer's reasoning. The reader checked
the engine claims in a decompile of the 1.6 game. The reader found ten things. Each is repaired.

| finding | repair |
|---|---|
| "Every `GeneSkinColorOverride` child has the tag": four Dathomirian genes replace it | said, with both tags |
| §4 gave four routes as the whole list | three more routes named; "ordinary generation" |
| `skipFlag`: `renderSkipFlags` and `forceEyesVisibleForRotations` left out | added, here and in `appearance.md` |
| `iconPath is empty.` is reported only in dev mode | said |
| §1 sent the eye-colour reader to §3a, which did not hold that path | a bullet in §3a: 50/50 for each added gene |
| the fixed rule for genes that are not `RandomChosen` was not stated | stated, with its timing for skin colour |
| `texPaths`: the gene's `loadID` is part of the seed; pawns can differ, not must | repaired |
| an unresolved `ParentName` is not a silent discard (old and new text wrong) | it logs one error, and the child loads without inherited fields; also in `closure.md`, `verifying.md`, `gen_races_mod.py` |
| the head pool also tests `gender`, and the callers test `randomChosen` | said |
| the description still holds two wrong statements | the history names both; see "For the owner or a later session" |

The same reader then read each repair. Three lines were still wrong, and each is repaired as the reader proposed: the §4 bold lead; one
line of `closure.md`; four more comments of `gen_races_mod.py`. One false line stays: the generated header of
`src/RimStarWars/StarWarsRaces/Defs/PawnKindDefs/SW_RescuedKinds.xml` ("discards the child silently"). Its correction changes a mod
def file and its generator together, for a comment only. It is not worth the touch.
No reader read these last three repairs. After the first landing (db3a8fbef7a0), the prose check of `./publish` named seven lines.
The writer put the noun in each. No reader read those.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| §1 "the engine picks one per pawn" / §3a "adds no variety" | the engine picks one | 1: `SelectGene` |
| "unset defaults are `0` and `false`" / the class | `1` and `true` | 1: `XenotypeDef` |
| `<li>` loss is silent / the loader | one error line | 1: `DirectXmlToObjectNew.DefFromNodeNew` |
| `skipFlag Hair` by drawn hair / by headgear | headgear | 1: `PawnRenderTree.AdjustParms` |
| `appearance.md`: no `rotDrawMode`, the corpse reverts to human / the default | all three states | 1: `PawnRenderNodeProperties` |
| §4 "unverifiable in game" / `spawn_pawn` takes `xenotype` | the bridge tool | 1 |
| `.xtp` "carries only `name` and `inheritable`" / the class | also genes and `iconDef` | 1: `CustomXenotype` |
| "the live def dump is disk state" / a DefDump comes from a load | a dump is not the process; two kinds | 1: `dump-is-pre-cherrypicker.md` |
| old paths, old names, 35 genes, deleted page, CHECK seat | current ones | 4 |
| "write it HERE" / skills change only in curation | `lessons.py add` | 3 |

## Changed outside the skill file

`references/history.md` (new). False lines corrected in `references/appearance.md`, `references/closure.md`, `references/verifying.md`,
`skills/rimbridge/references/map-authoring.md`, `src/RimMandrake/Utils/gen_races_mod.py` (docstring and one printed label).
A note is on `FACE_OPTOUT_REPAIR_ONLY_AT_HOME`: nothing excludes `RSW_MandrakeJawa` from Facial Animation now.

## For the owner or a later session

None goes to the owner. Two statements in the description wait for a session with the trigger evals of `skill-creator`:
"cannot be spawned at all without a PawnKindDef" and "discards the whole FactionDef silently". Each is too strong, and each still sends the
agent to the right skill.

Two stale uses of `BTD_Jawa` stay. The tool descriptions in `JawaBenchTerrainTools.cs` use it as an example name, and the tool prints
suggestions for a name that does not load. An edit there changes the companion's source hash, so each game needs a new build and deploy.
`load_session.py` row 5 expects it; that row is ruled closed. Neither is worth the touch.

## Could not determine

- Why `BTD_Jawa` once read `0.0 / False` at runtime. The engine defaults say otherwise. A run with the donors on would show it.
- Whether an active mod patches the colour pick. A spawn of 20 Bith on a game would show the spread.

## What this run did not test

- No game was driven. The colour pick is read in code and agrees with the old Bith observation.
- No measurement shows that an agent behaves better with the new text.
- The trigger evals were not run, because the description did not change.
