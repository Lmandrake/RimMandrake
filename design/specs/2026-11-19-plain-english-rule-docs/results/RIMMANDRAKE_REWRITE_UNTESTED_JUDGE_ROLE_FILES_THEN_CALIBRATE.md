# Result: `RIMMANDRAKE_REWRITE_UNTESTED_JUDGE_ROLE_FILES_THEN_CALIBRATE`

Batch 12 of `batch_plan.md`. Run 2026-11-24 (run 1 of the list item).

Base: `108c603d63c03ef208fcdab2512851e204065aad`

Files, all in `src/RimMandrake/rimflow/roles/`: `designer_scene_contract.md`, `designer_lock.md`, `code_review.md`. This run
also corrected one line of `src/RimMandrake/rimflow/showcase_rules.json` (see "Conflicts settled").

No `rm-role-designer*` unit was active at the start. A changed packet hash does nothing to an open concept
(`RIMMANDRAKE_REWRITE_DESIGNER_PACKET_FIRST_FOUR_FILES.md`).

## Scores

| file | bytes | words | STE per 100 words | sentences over 20 words | flagged lines |
|---|---|---|---|---|---|
| `designer_scene_contract.md` | 10,891 → 11,571 | 1,485 → 1,585 | 3.37 → 2.08 | 17 → 6 | 0 → 0 |
| `designer_lock.md` | 6,531 → 7,206 | 988 → 1,086 | 3.64 → 1.93 | 19 → 8 | 1 → 0 |
| `code_review.md` | 7,931 → 8,626 | 1,269 → 1,386 | 2.84 → 2.31 | 11 → 8 | 5 → 5 |

Each file meets the 2.5 target. The 5 flags of `code_review.md` are the page's part name DOES NOT SURVIVE.

### The long sentences that stay

- `designer_scene_contract.md`, 6: lines 63, 113, 116, 142 and 147 hold a command or a list of three; line 131 is two short
  sentences that the lint joined at a bold lead.
- `designer_lock.md`, 8: lines 5, 33, 52 and 70 hold a command or a command text. Line 26 is two sentences that the lint joined.
  Line 38 stays word for word (`case_carried_gap_closes_on_ok_rows.py` reads it). Line 36 is a list of three. Line 41 stays near its old words,
  because the meaning reader found that a comma loosened it.
- `code_review.md`, 8: lines 15 and 74 hold a path, a date or a joined bold lead. Lines 7, 36, 59, 69, 81 and 126 are
  definitions or a rule with its list. The calibration reads these words, so they stay close to the old text.

## Code that reads the files, and what the rewrite kept for it

- `selftest_flagship_contract.py` reads the bullet "- **Showcase 1 is the flagship" up to the next top-level bullet or blank
  line. The bullet holds no blank line and keeps each phrase that the test reads.
- `selftest_live_kinds.py` (`test_kind`, `tag_evidence`, `budget`, `x_of_y`) and `selftest_raid_pause.py` ("cheapest test that
  decides") read the contract.
- `case_carried_gap_closes_on_ok_rows.py` and `case_four_rules_two_looks.py` read `designer_lock.md`.
- `code_review_brief_accept.py` reads the part names of `code_review.md`.

## The hand count

| file | old line | what a cold reader lacks | state after |
|---|---|---|---|
| contract | "so none of this goes in `tree.json`" | who acts | "So write none of this in `tree.json`." |
| contract | "a hand or mock scene … is refused" | what refuses it | "The check refuses …" (`designer_stage.py`) |
| contract | the cheap-to-dear line | the order in one sentence of six parts | a numbered list |
| contract | "Or, under the Evidence-for-Ask rule …" (one sentence of five conditions) | which condition belongs to which record | one sentence for each part of the call |
| contract | "What the program checks: …" | six checks in one paragraph | a list |
| lock | "Injected with `designer.md` at stage 5." | the subject | "The launcher injects …" |
| lock | "that is his word, or the Conductor window's act" | what "that" is | "the validation is …" |
| lock | item 3, one paragraph of 24 sentences | where each rule starts | four bold leads and lists |
| lock | "then it closes only when its slot also says repaired" | what "it" is | "that gap" |
| lock | "It must also match that verdict" | what "it" is | "the stamp" |
| lock | "GSS" | what GSS is | "GSS (Gimme Some Slack)" |
| review | "That rule, his words … are in" | which rule | a list "Where the rules live" |
| review | "failures it does not promise to handle" | what "it" is | "the component" |
| review | "Rare is anything that needs more: …" | four kinds in one sentence | a list |
| review | "**A minor nit, …**: one line" (six kinds in one lead) | each kind | a list |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | the contract with the Evidence-for-Ask id removed and 0.25 changed to "a quarter" | 1 lost (the id), exit 1. It did not see the lost 0.25. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 3 lost, exit 1 |
| check 1 | each final file | 25, 12 and 20 items; 0 lost |
| check 2 | each final file | 84, 67 and 48 spans; 0 lost |
| the selftests of both checks and of `batch_done.py` | — | PASS |
| `selftest_flagship_contract`, `_live_kinds`, `_raid_pause`, `_coverage_judge`, `_designer_stage`, `_retired_era_gone`, `_role_headers_state_free`, `_role_start_package`, `_bench_word_prose`, `_game_names_prose`, `_lessons_corpus_rule`, `_offline_model_rule`, `_rule_files_lose_nothing`, `_skills_by_work`, `_judge_calibration` | new text | PASS |

Four tests read red for a cause that is not in these files:

- `selftest_conductor_authority.py`: `item_packet.py` line 86 compares to "OWNER" and has no Conductor route.
- `case_carried_gap_closes_on_ok_rows.py`: one case looks for a sentence in the prompt of `coverage_judge.py`.
- `case_four_rules_two_looks.py`: one case looks for rule 4 in `designer_write.md`.
- `code_review_brief_accept.py`: the family is not CALIBRATED (see Calibration).

This run did not run these four on the base. The first three name a file that this run did not edit.

Names of people: no person's name is in the three files. The read of the diff found the same roles, models and mods.

## What the meaning read found

Four fresh Opus readers (rm-judge, model opus), one at a time. Three read one file each. The fourth read each repair and
later edit of all three files against the old text. No reader got the writer's reasoning.

| file | finding | repair |
|---|---|---|
| contract | "a showcase exercises every unit, or `coverage_rest` lists it" reads as one showcase for all units | the old words restored |
| contract | polish: "the Conductor's included" covered the mock too | "The Conductor's mock or demonstration is included." |
| contract | polish: "is the harness's job" became a plain fact | the old words restored |
| contract | polish: a list of "two kinds" or "two routes" with more bullets | the lead names which bullets |
| lock | "while no showcase and no scene exercises a … capability" reads as "nothing exercises any" | "while any … capability has no showcase and no scene that exercises it" |
| lock | "file a build item" orders the stage-5 run to file; the old line is a precondition | "must be a filed build item" |
| lock | the wording of the owner-event condition left out the item that a refusal record names | the words follow `caused_by_mod` |
| lock | polish: "could not reach", "a file", a comma | restored, or named |
| review | the sentence on mod files let reason 3 (wrong page) edit a locked bar | "A change to a bar is not yours: set it down with its evidence." |
| review | "a test of the same name" conflicts with a mod's test table rows; no NO PAGE case | one line for each |
| review | LIMITS had no consequence | "A limit that cannot name both is removed, not tuned." |
| review | "**Polish**: … The kinds of polish are" reads as a closed list | "**Each of these** is one line on `polish.md`" |

The fourth reader: 0 unsupported changes, 0 unsupported additions, 1 change that the code supports (the owner-event condition).
No line was edited after that read.

## Calibration

Both calibrations ran after the last edit, on the final text, in this clone. Both families read UNTESTED before
(`coverage_judge` hash `74bd06973476df0e`, `code_review` hash `f5fc230be16849e5`).

### `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --model coverage_judge`

Exit 0. It printed:

```
coverage_judge           CALIBRATED 12 planted case(s) ran and came out as planted
```

| case | planted | got |
|---|---|---|
| `good_lanterns` | pass | pass |
| `good_lanterns_tuning` | pass | pass |
| `good_lanterns_no_reset` | pass | pass |
| `good_round2_repaired` | pass | pass |
| `good_pyrelands_look8` | pass | pass |
| `good_one_kind_enough` | pass | pass |
| `bad_leaf_no_scene` | refuse | refuse (route designer) |
| `bad_scene_no_control` | refuse | refuse (route designer) |
| `bad_conflict_routing` | refuse | refuse (route criteria) |
| `bad_mixed_row` | refuse | refuse (route designer) |
| `bad_late_serious` | refuse | refuse (route designer, late confirmed) |
| `bad_fire_never_touched` | refuse | refuse (route designer) |

Status after: CALIBRATED at hash `a89f53a9cd6c3647`, run at 2026-11-24T08:48:24Z. Spend: ≈1.64M weighted_v2 tokens (Opus 5.5),
converted from the cases' recorded list cost with the rate of the judge-briefs batch.

### `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --model code_review`

Exit 0. It printed:

```
code_review              FAILED     came out the other way: c2.9, c3.4, c4.1, c4.10, c4.14
```

The check's own last line: "pass mark FAIL: agreed real caught 2 of 3 (limit all); agreed polish called problem 1 of 9
(limit 1); unscored: 30 of 35 as labelled". Status after: FAILED at hash `e4e11112e343453b`, run at 2026-11-24T08:51:09Z.
Spend: one Codex call, weighted tokens UNMEASURED.

The last run on the old text (2026-11-19T13:54:07Z) missed four of the same claims (c2.9, c3.4, c4.1, c4.14) and read 31 of 35.
Its pass mark line was the same. So four of the five misses are not from this rewrite. The fifth is c4.10:

- The claim: a re-hold of a mod on the same day with new words is not imported. The label is `real`.
- The answer: polish, because the page says "a mod the store already holds keeps the store's words".
- That page line came in commit `97f0cc2819` (2026-11-19 06:58 PST). The label file last changed in commit `c89dea59f0`
  (2026-11-19 05:53 PST), before it. So the label is older than the page. The label of c4.10 is probably stale
  [guess ~85%]; this run did not change the label, because that would edit the grader.

This run made one call and no repeat, so the noise between two calls on one text is UNMEASURED. No word of the brief was
changed to pass a case. Only a CALIBRATED family's refusal sends work back, so FAILED and UNTESTED have the same consequence
for a review. The finding is on the open item `RIMMANDRAKE_WRITE_REVIEW_BRIEF_CALIBRATE_ON_THIRTY_FIVE_CLAIMS` as a note.

The other rows of the table did not change.

## Conflicts settled

| conflict (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| lock: the owner event "names this concept's item" / the code also takes an item that a refusal record names, or one caused by these | the code | 1: `concept_tree.owner_event_problem`, `caused_by_mod`, `mod_items` |
| review: four page parts / five, with LIMITS | LIMITS added | 3: root `CLAUDE.md` §No limit without the danger it guards; `standing_rulings.md` §A boundary page, Decision 1 |
| review: a `boundary.md` for all code / a mod's locked bars are the page of its files | three short lines added | 3: root `CLAUDE.md` §Code is clean when its promises are tested; `standing_rulings.md`, his card of 2026-11-19 evening |
| `showcase_rules.json` `units_doc` "approved/opened_by_owner" / the code and the contract, with `opened_by_conductor` | the code; corrected | 1: `designer_stage.py` `OPENED_SCOPES` |

For the owner: none.

## Could not determine

| line | question | who would know |
|---|---|---|
| review: "Ordinary operation is an input inside ACCEPTS" for a mod file | locked bars have no ACCEPTS and no DOES NOT SURVIVE. No ruling says what is ordinary, or where a rare-failure line goes, for a mod file | the Conductor |
| review: "beside the page" for a mod file | whether `polish.md` there is `version/polish.md` (the mod's Polish list) or a separate record | the Conductor |
| lock: "only `coverage_judge.py release`" beside `./pipe grant <Mod> look` | `look_balance` adds a `pipe grant` to the look that a release granted. So the line reads true for the first look; the file does not name the second command | `coverage_judge.py`; left as it was |

## What this run did not test

- No code review and no Designer run read the new text, except the judge calls of the two calibrations.
- A second call of the `code_review` calibration.
- No measurement shows that an agent acts better on the new text.
