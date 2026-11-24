# Result: `RIMMANDRAKE_REWRITE_ART_EVAL_PROMPT_FILES_THEN_CALIBRATE`

One part of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`). Run 2026-11-24.

Base: `246a44cdf35e69aa690ca7992b578f40a112595b`

Also: `skills/rimworld-art-evaluation/references/history.md`

Files, all in `skills/rimworld-art-evaluation/references/prompts/`. One span left `opus_first_pass.md` because it
was false; `history.md` holds it, so both checks read that file as `--also`.

## Scores

| file | version | bytes | words | STE per 100 words | long sentences | flags |
|---|---|---|---|---|---|---|
| `preamble.md` | v3 → v4 | 4,481 → 6,370 | 756 → 1,066 | 4.10 → 1.50 | 14 → 6 | 1 → 0 |
| `opus_first_pass.md` | v2 → v3 | 1,722 → 2,154 | 241 → 312 | 4.56 → 3.53 | 2 → 3 | 0 → 0 |
| `departures_brief.md` | v3 (kept) | 2,421 → 2,616 | 373 → 406 | 3.75 → 1.97 | 9 → 4 | 0 → 0 |
| `gpt_targeted_second_look.md` | v1 → v2 | 1,588 → 1,760 | 221 → 254 | 5.43 → 3.15 | 3 → 1 | 0 → 0 |
| `regen_prompt_edit.md` | v1 → v2 | 1,723 → 2,300 | 257 → 357 | 3.89 → 1.68 | 6 → 4 | 0 → 0 |

**Two files miss the 2.5 target: `opus_first_pass.md` (3.53) and `gpt_targeted_second_look.md` (3.15).** The JSON object in each
is a format contract, and the lint reads that object as prose. With the JSON object removed, an earlier draft read 2.93 (from
4.61) and 2.99 (from 5.95); these are short texts, where six hits make 3 per 100 words. The long sentences that stay are the
JSON object, a command, an owner quote, or a list with its quoted examples.

The prose check (`guiding_prose.py check`) reads no fault in 209 sentences.

## The hand count

| file | old line | what a cold reader lacks | state after |
|---|---|---|---|
| preamble | "every checklist item the card lists", "the card's list" | the card holds neither; each is its own section | a list of the parts of the prompt |
| preamble | "the class module and the card" | what each is and where | the same list |
| preamble | "Report improvement wishes as findings too" beside "put it in `proposals`" | which of the two | the first has the exception of the second |
| preamble | "`proposals`" | the second reviewer's JSON has no such field | "or leave it out" |
| preamble | the two long lists of what he keeps and redoes | each item | the redo list is bullets |
| opus | "he", "would keep it" | who, what | "the owner", "the picture" |
| opus | "that item's code" | item id or reason code | the reason code after "fails as" |
| brief | "A reviewer checks each one" | false for a plant (`cards.card_md`) | "each departure of a creature" |
| brief | "body plan, if one of: … else null" | who writes what | two sentences |
| gpt | "the same codes and fields" | where they are | "Reason codes"; the JSON object |
| regen | "name the invariants … so fixing …" | the act | two sentences |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a planted preamble (0.56, `earth_body_named: no`, 128–256, the camel quote lost) and a planted brief (the date, 0 to 5, a quote lost) | 1 lost and 1 lost, exit 1. It did not see the numbers. |
| check 2 (`rule_doc_lint.py keep`) | the same two copies | 5 lost and 6 lost, exit 1 |
| check 1, check 2 | the five final files | 0 lost; 33, 28, 23, 16 and 10 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | PASS; 19 of 19; GREEN, 12 cases |
| `selftest_art_judge_no_keyline.py` | old files, then new; then the old code lines, then new | 4 FAIL, PASS; 2 FAIL, PASS |
| `art_eval/` `selftest_art_eval`, `_round_series`, `_fauna_drive`, `_auto_judge`, `_override_rate`; `selftest_skills_by_work`, `_validate_skills`, `_skills_registered_or_listed`, `_guiding_prose`, `_game_names_prose`, `_retired_era_gone` | final text | exit 0 |

Names of people: no person's name is in the old or the new text. This run read the diff for names.

## Calibration

`python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --no-run` reads **`art_eval_first_pass UNTESTED`**. The family has
no free check and no model check, so no run can calibrate it, and this run built none. The other families read as the tool
printed them: `art_judge_brief`, `coverage_judge`, `evidence_gate`, `guiding_prose_reader`, `maturation_advance` CALIBRATED;
`code_review` FAILED; `scene_look_judge_brief` UNTESTED. This run changed no row. (`refusal_contract.py calibrate --help` runs
the free checks and writes the registry: this run did that once and restored the file.)

### The regression set, the skill's own rule for a prompt change

`runner.py regress` could judge only 6 of its 11 rows. The pictures of the other 5 are gone (they were in the `Transient/` folder
of the retired `foundry` clone). The item `RIMMANDRAKE_RESTORE_ART_EVAL_REGRESSION_PICTURES_FIVE_ROWS_POINT_AT_NOTHING` holds that.

| run | Huldu, Ssurr, Vellak, Murrin (expect not ACCEPT) | Shadefern, Dewblade (expect ACCEPT) |
|---|---|---|
| `regress_departures_v3c_20261105`, the old prompts then | 4 of 4 | Shadefern ACCEPT, Dewblade REGEN |
| `regress_plain_english_20261124`, new prompts | 4 of 4 | REGEN, REGEN |
| `race_old_a`, `race_old_b`, the old prompts on 2026-11-24 | not run | REGEN, REGEN, both times |
| `race_new_a`, `race_new_b`, the new prompts on 2026-11-24 | not run | REGEN, REGEN, both times |
| `regress_plain_english_final_20261124`, the final bytes | 4 of 4 | REGEN, REGEN |

So the rewrite is not the cause of the two REGENs: the same models give them on the old prompts that day. The 5 unread rows are
UNMEASURED, not passed. The new outline words make the judge file STYLE_OFF on the four creature rows, whose pictures have
a drawn outline (B1a); a row that expects ACCEPT and has an outline was not measured.

## What the meaning read found

Five fresh Opus readers (rm-judge, model opus), one file each, one at a time, without the writer's reasoning. A sixth read the
repairs, `creature.md` and the code changes against the old text.

| file | finding | repair |
|---|---|---|
| preamble | "The card of an invented creature lists the departures" is false for a plant or an empty list | "Unless the card lists a departure that the art lacks, a wish …" (the sixth reader's words) |
| preamble | "with the departures bolted on" was a condition; the draft dropped it | the condition is back |
| preamble | "keeps a picture when …" made a rule of a description | "keeps pictures with flaws that …" |
| preamble | "reads at standard zoom" was lost with the outline clause | kept: the silhouette reads at standard zoom |
| preamble | "for each image, first write" could mean image by image | "before you compare anything …" |
| preamble | the ladder shadow: "at the foot" for "attached to the foot" | "attached to the foot" |
| preamble | `templates/creature.md` items 3 and 7 and its ALPHA question contradict the preamble | `creature.md` defers to the preamble (v4 of the template) |
| opus | `<reason code from the card>` is false | corrected; the old words are in `history.md` |
| brief | both examples tied to one quote | the second stands alone again |
| gpt | no meaning changed; nothing lost | none |
| regen | "no outlines" in a prompt makes `fill_queue.py` and `artpiped.py` leave out the whole house style text | the prompt says nothing of outlines; the queue adds the text |
| regen | the "one permitted prohibition" has no source | removed |
| regen | "every finding becomes a change" beside "write nothing about an outline" | the change for such a finding is named |

No reader read: the last repair of each of three lines (the preamble's "Unless the card lists", the regen sentence on an outline
finding, the opus line on the card and `nearest_earth_animal`). The first two follow the sixth reader's own wording. The third
was added after the prose check asked for it: `runner.py` places the section "The card" and `cards.card_md` prints the Canon heading.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| "a clean dark outline" in the preamble and the regen prompt / no outlines | no outlines | 2: owner card 2026-10-04, `art_judge_brief.md` B1a |
| the preamble has no exception for the ullai / B1a has one | the exception is in the preamble | 2: his pick of 2026-11-23 |
| "no ground patch or painted shadow" / the fermatalis's own ground matter and the ladder's floor shadow are allowed | both exceptions are in the preamble; `creature.md` defers to them | 2: D4, owner 2026-10-24 and card 2026-10-22 |
| `creature.md` item 3 (ALIEN fails only when most departures are absent) / the preamble rule for `earth_body_named: no` | the preamble decides first | 2: preamble v3 of 2026-11-05 is the later text; `traps.md` line on the floor |
| `round_series.py` and `policy.py` prompts say "no outlines" (a fix of 2026-11-23) / the queue then leaves out `HOUSE_ART_REGISTER` | the words left those two prompts; the queue adds them | 1: `fill_queue.py` and `artpiped.py`; test first |
| the criteria ledger says to bump the version of each changed file / `cards.BRIEF_TAG` requires the tag `departures_brief@v3` | `departures_brief.md` keeps the tag; its sha moves | 1: with another tag, no brief gives departures (`cards.apply_brief`) |

## Could not determine

None.

## What this run did not test

- The 5 rows without pictures, and no owner-kept picture with a drawn outline.
- No generator prompt from the new regen text was rendered. No regen was filed.
- A wish that fits only a blocking code is now told to the second reviewer as "leave it out"; no measurement shows the effect.
- The trigger evals were not run: no skill description changed.
