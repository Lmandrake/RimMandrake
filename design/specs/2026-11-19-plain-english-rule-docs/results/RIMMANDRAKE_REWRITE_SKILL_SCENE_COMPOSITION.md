# Result: `RIMMANDRAKE_REWRITE_SKILL_SCENE_COMPOSITION`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-scene-composition/SKILL.md`. Run 2026-11-23.

Base: `867022074e7423c12601ab33d4a1995af60ee12f`
Also: skills/rimworld-scene-composition/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 16,924 | 18,420 |
| words in linted prose | 2,076 | 2,400 |
| STE violations per 100 words | 4.19 | 1.13 |
| sentences over 20 words | 40 | 12 |
| flagged lines (mechanical) | 12 | 9 |
| lines that a cold reader cannot act on (hand count, by the writer) | 10 | 0 |

The 12 long sentences that stay are of these kinds: an owner quote (line 8); a quoted example or story (lines 96 and 141); old bold
slogans kept word for word (lines 37 and 71); short sentences that the lint joined (the other seven). The flags that stay are
emphasis marks.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "`grep <packageId> ModsConfig.xml`" | the ids are lower case, so the search finds nothing | parse and compare in lower case |
| "Already active." | in which list | the two lists and the missing mod are named |
| "linked/auto-tiling" | what linked means | defined |
| "face below/in-front, top behind/above" | which way on the map | north, a higher z |
| "That is not a limitation to work around quietly" | what to do | the instruction, then the reason |
| "a finished promise/whisper" | what each is | defined, with the roster path |
| "quicktest map" | what a quicktest is | defined |
| "per `rimbridge` §4a discipline" | no such section | `rimworld-debug-testing` §4a |
| "`rimworld-debug-testing` §9" | the text is not there now | the path that holds it |
| "a counter-example is found and recorded here" | how, as a skill is edited only in curation | filed as a lesson |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of the rewrite with a code span, "15-20", the dates and a quote removed, no `--also` | 1 lost (the date), exit 1 |
| check 2 (`rule_doc_lint.py keep`) | the same copy, with `--also` | 5 lost, exit 1. The run did not see the code span, because history.md also holds it |
| check 1, check 2 | the first draft, with `--also` | 3 lost; 9 lost. Each one is restored |
| check 1, check 2 | the rewrite, with `--also` | 21 items, 0 lost; 67 spans, 0 lost (both run again after the last edit) |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | pass; 19 of 19; GREEN, 12 cases |
| `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_warn_skill_unwired.py`, `selftest_guiding_prose.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py`, `selftest_inhabited_augmentation_wiring.py` | the draft before the meaning read | exit 0 each |
| rimplace selftest; `rimplace lint` of the three templates | after the template edits | 62/62; 0 findings each (the defName part of lint is UNMEASURED: no fresh def dump) |

Names of people: the old text holds none. The history file names none. The front matter is byte for byte the same.

## What the meaning read found

A fresh Opus reader (rm-judge, read-only) read every line of both texts without the writer's reasoning. The reader checked the new
facts against the mod XML, the texture sheets, the mod lists, the templates and the cited files.

| finding | repair |
|---|---|
| face rows that touch draw posts, so "2-3 rows of depth" as stacked rows breaks §1 | said, in a bullet of its own |
| "one of two things" is false with a rule from the texture sheets | three sources |
| "the texture sheet is the cause" is an inference; the south end cell differs | "probable cause"; the end cell named |
| `long_crossing.lua` contradicts itself: south, or leeward | two comments and the note string repaired |
| "does not send work back" softens the gate | the builder still repairs a score below 3 |
| the two author quotes are not in the installed files | said in the table |
| §4a does not say "jump the camera" | "frame the subject" |
| "most of the research" narrows "most of this" | "most of this skill" |
| `history.md`: the claim on templates and tickets is too wide | narrowed |
| `boneyard.lua`: "nothing else needs to move" is untested for `RM_Ollim` | said, with the drawn size |

The same reader then read each repair and the whole of both files again. Three of the repairs did not hold: the note string of
`long_crossing.lua`, the sentence on tickets in `history.md`, and the sentence on depth in §6. They are repaired as the reader
proposed. No reader read these last edits, nor the sentence on the south end cell in `history.md` and the rewrapped lines.
After the first landing (be6f6ba0e38e), the prose check of `./publish` named six lines. The writer put the noun in each, and said that
Long Crossing is a truck hull. No reader read those.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| grep ModsConfig / parse it | parse | 3, and the ids are lower case in the file |
| "Already active"; "three mods to use" / the lists | SimpleStairs is not in FULL.LATEST | 1: `infrastructure/state/modlists/` |
| no mechanical backing / path costs and cover | path costs and cover named | 1: the XML of the three mods |
| links need the same defName and the same row / links by flag, in four directions | by flag; the rule on east-west stays as measured | 1: `Graphic_Linked` |
| the top piece is the plateau surface / a thin back edge | a back edge | 1: the texture sheets |
| the top row in `long_crossing.lua` is north / one z lower, so south | the code and its comments corrected | 1: z grows to the north; the reading in the render |
| `waste_camp.lua` row 0 is the north edge / the south edge | south | 1 |
| `boneyard.lua`: no silverbole exists / `RM_Ollim` | it exists | 1: Stillsand defs; `design/concepts/Stillsand/rewrite_choices.md` |
| `rimbridge` §4a; `rimworld-debug-testing` §9 | `rimworld-debug-testing` §4a; the proof-harness file | 4 |
| "add it here" / a skill is edited only in curation | `lessons.py add` | 3 |
| low scores are work orders / only a calibrated brief sends work back | both, each named: the builder's bar, and the pipeline's rule | 3 |
| "external, cited source" / no source is named | "outside research"; the sources are unknown | 1: git `d8e152500d` |

None goes to the owner.

## Changed outside the skill file

`references/history.md` (new), and in `design/Jawa/templates/`: `long_crossing.lua` (the order and place of the dune rows, its
comments, the note string), `waste_camp.lua` (one comment), `boneyard.lua` (one comment).

## Could not determine

- The source of the two author quotes. The Workshop pages are likely. Nobody checked.
- Why `TreeDead` did not spawn on the live path. `jawa/set_plants` in a live game can show it.
- The names of the outside sources of 2026-09-06. The session that wrote the first version knows.

## What this run did not test

- No live game was driven. The corrected order of the Long Crossing rows has no live look. The claims on posts and rails come from
  the texture sheets.
- No measurement shows that an agent behaves better with the new text.
- The trigger evals were not run, because the description did not change.
