# Result: `RIMMANDRAKE_REWRITE_SKILL_SPRITE_FACINGS`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-sprite-facings/SKILL.md`. Run 2026-11-23.

Base: `1a0a54621e6705cc123c2f1cdd0276996b6e0ac9`
Also: skills/rimworld-sprite-facings/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 28,066 | 32,607 |
| words in linted prose | 4,023 | 4,744 |
| STE violations per 100 words | 4.72 | 2.26 |
| sentences over 20 words | 79 | 32 |
| flagged lines (mechanical) | 29 | 20 |
| lines that a cold reader cannot act on (hand count, by the writer) | 10 | 0 |

The long sentences that stay are owner quotes, sentences that hold a command, two short sentences that the lint joined at
a bold lead, a heading, and pointer lines that `traps.md` section names need.
The front matter, each heading, each table and the XML block are the same as at the base.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "the daemon's facing hook must forbid the overhead camera" | which hook; whether it does so now | names `build_job_prompt`; says that it does |
| "can become a literal cyclops in the render if you don't" | if you don't do what | names the condition |
| "still owed from the Windows box" | who acts | measured; the reading is in the text |
| "The general rule this points at" | what "this" is | the rule stands first |
| "the check's own docstring" | which check | `SYMMETRY_MIN_NS` in `art_checks.py` |
| "Run a cross-facing size audit" | with which tool | `facing_set_audit.py` |
| "This file needs a curation pass" | nothing to do | deleted |
| "search this repo's CLAUDE.md for …" | the text moved | names `standing_rulings.md` and `flight.md` |
| "per the worked-example lie above" | no such lie above | deleted |
| "stabilize" in the list of red controls | which tool | `flier_body_stabilize.py` |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without `FIREHAWK_FLIGHT_BEHAVIOR_1`, `flightStartChanceOnJobStart` and 3,901 | saw the id; did not see the other two |
| check 2 (`rule_doc_lint.py keep`) | the same copy | saw all three; failed |
| check 1, check 2 | the final text, with `--also` | 61 items, 0 lost; 166 spans, 0 lost |
| `rule_doc_lint.py` and `checkable.py` selftests | none | pass; 19 of 19 |
| `selftest_warn_skill_unwired.py`, `selftest_guiding_prose.py`, `selftest_image_skills.py`, `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py` | the first draft | exit 0 each |
| `selftest_guiding_prose.py`, `selftest_validate_skills.py`, `selftest_skills_by_work.py`, `selftest_retired_era_gone.py` | the final text | exit 0 each |

Names: 14 names of creatures, mods and seats were counted in old and new. Anooba, Nuna and Alpha Animals occur once more;
the others are equal. No name of a person is in either text.

## What the meaning read found

One fresh Opus reader (rm-judge) read old and new, with no reasoning from the writer. It checked each correction in the code.

| finding | repair |
|---|---|
| significant: the stamp and the refusal of `load_job` were overclaimed, and false for a "building sprite" | names the refused phrases and the building stamp |
| significant: the conditions of the derivation in `fill_queue.py` were lost | conditions added |
| significant: the cyclops line became a new rule and lost its cause | the old condition is back |
| significant: the judge is "the instrument" and then "advisory" | says that this judge failed its calibration |
| significant: "Set those faint pixels to zero" replaced the fix at the export step | the old line is back |
| borderline: `facing_set_audit.py` does not compare variants | said so |
| the history file of the Codex hang named the old 120 s rule as current | corrected |
| the two-image change was not in the history file; the 2026-10-14 edit was a building | both added |
| the height model has exceptions | added |

The same reader then read each repair. One repair was still wrong (the feet test binds only some body plans) and two needed a
small fix. The writer made these three fixes from the reader's text and the code (`judge` in `facing_scale_lint.py`). No
reader read these last three fixes.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| vanilla not checked / vanilla can be read here | measured: median 0.99 for north and south, 123 and 122 of 127 reach 0.80 | 1: `art_checks.py` formula on the extracted `ludeon.*` textures. The reader ran it again with the same result |
| `art_review_facts_spec.md`: the same owed line | corrected in that file | 1 |
| `art_review_facts_spec.md` A4: an outline check is built / no outline check exists | retired | 2: card 2026-10-04 (`ART_VERSION_WRANGLING_1`); `art_checks.py` |
| `art_review_facts_spec.md` A3: height never changes / top-down art differs | limited to ground-camera art | 1: `facing_scale_lint.py` |
| duplicate pairs "are" / no pair exists now | past tense | 1: sha256 of the installed files |
| one master "takes 3 renders per creature to 1" / each derived facing is a render | the second | 1: `artpiped.py`, `fill_queue.py` |
| the viewpoint judge is the measurement / advisory since 2026-09-20 | the second | 1: `facing_set_audit.py` |
| 120 s and a retry loop / 105 s and a retry by hand | the second | 1: `generating-images` "Cost and timing" |
| anchor with two images / two images are not reliable | the hang was not the second image; unproven for sibling facings | 1: `codex-edit-hang-history.md`, `attach_image` in `artpiped.py` |
| prompt words "hard black outline" / no outlines | the method stays; the words are marked as old | 2: card 2026-10-04, rule B1a |
| a 15% spread / a 1.35 ratio / the vanilla spread | each is named with its tool | 1 |
| height never changes with the angle / vanilla north and south stand taller | limited to ground-camera art | 1 |
| a torso change is the owner's to rule / the Conductor may loosen a bar | owner or Conductor; hold still until then | 3: "Only five acts stay his" |
| `fill_queue.py` comment: "already documents as owed" / documented | comment corrected | 1 |

For the owner: nothing.

## Seen, not fixed (one line of record)

`artpiped.py` `build_job_prompt` stamps a facing job with "building sprite" as a camera that looks straight down, and the
measured building camera is ~35°. 57 such jobs ran since 2026-10-14, the last on 2026-10-26. This run saw no bad result from
one, so it changed no prompt. `SKILL.md` warns the reader.

## Could not determine

None.

## What this run did not test

- No art run used the new text. No image was made.
- No measurement shows that an agent works better with the new text.
- The trigger evals of the description did not run: the description did not change.
