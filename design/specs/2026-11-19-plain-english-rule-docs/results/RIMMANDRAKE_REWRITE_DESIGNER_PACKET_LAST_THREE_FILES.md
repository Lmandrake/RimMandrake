# Result: `RIMMANDRAKE_REWRITE_DESIGNER_PACKET_LAST_THREE_FILES`

Part 2 of batch 11 (`RIMMANDRAKE_REWRITE_DESIGNER_PACKET_FILES_HASH_IN_STAGE_RECORD`) of `batch_plan.md`. Files:
`src/RimMandrake/rimflow/roles/designer_exam.md`, `designer_examples.md`, `designer_cleanse.md`. This part also edited
the copy of the first-version block in `designer.md` (see "The shared block"). Run 2026-11-23. No `rm-role-designer*`
unit was active at the start or before the landing (the item's launch check).

Base: `4391e9d6e380d16616598dd33f6d8dbae6a344e1`

Also: src/RimMandrake/rimflow/roles/designer.md

## What a changed packet hash does to an open concept (the batch's special rule)

Part 1 found the answer at its base (`RIMMANDRAKE_REWRITE_DESIGNER_PACKET_FIRST_FOUR_FILES.md`). This run read
`src/RimMandrake/rimflow/designer_stage.py` again at this base. The answer is the same: **nothing**. A changed hash is
recorded, and no code compares it.

- `open_run` (line 2084) computes `manifest_hashes(stage)` and stores the hashes in `stage.json` as
  `running.manifest` (line 2086). The packet text is built at the same moment (`packet()`, line 2095).
- `close_run` copies `running.manifest` into the accepted result entry (line 2696).
- No other line in `src/` reads `manifest` from `stage.json` (`git grep` for `["manifest"]` and `get("manifest")`).
- So an edit to a packet file does not reopen a stage, reject a result or void a run. An open run keeps the text that
  it got at open. The next run gets the new text and records the new hash.

Per file of this part:

- `designer_exam.md` is the `stage_4` packet file. Its hash is recorded at each stage-4 open, as above.
- `designer_examples.md` is under `on_request` in `designer_manifest.json`. `manifest_hashes` reads only the `stage_N`
  lists. So no hash of this file is ever recorded.
- `designer_cleanse.md` is in no manifest list. `designer_cleanse.py` reads it as the cleanse brief. So no hash of this
  file is recorded in `stage.json`.
- `designer.md` is in every stage list. Its hash changes with this landing, with no effect beyond the record.

## Scores

| file | measure | before | after |
|---|---|---|---|
| `designer_exam.md` | bytes | 9,219 | 10,108 |
| | words / STE / long / flagged | 1,300 / 1.54 / 5 / 0 | 1,420 / 1.13 / 2 / 0 |
| `designer_examples.md` | bytes | 8,869 | 9,525 |
| | words / STE / long / flagged | 1,242 / 4.67 / 22 / 0 | 1,352 / 3.92 / 20 / 0 |
| `designer_cleanse.md` | bytes | 23,164 | 23,813 |
| | words / STE / long / flagged | 3,778 / 3.47 / 27 / 1 | 3,839 / 3.15 / 19 / 0 |
| | the shared block alone: words / STE / long / flagged | 692 / 5.49 / 14 / 1 | 721 / 3.88 / 5 / 0 |
| `designer.md` (block only edited) | bytes | 25,024 | 25,268 |
| | words / STE / long / flagged | 3,456 / 2.78 / 29 / 2 | 3,485 / 2.47 / 20 / 1 |
| all three files | lines that a cold reader cannot act on (hand count, by the writer) | 19 | 0 that this run could resolve; 4 listed under "Could not determine" |

Two files miss the 2.5 target:

- `designer_examples.md` (3.92). The file is mostly his quotes. The lint masks a quote only when the quote holds no
  inner `"`, so many of his words still count: "would", "should", "might" and -ing forms inside his sentences, and
  in the table. Of 53 violations, about 35 to 40 are inside his quotes or in the table (a hand count from the
  per-sentence listing, not a tool count). The writing rules forbid a change to his words. 4 more quote-bounded prose fragments must stay
  word for word, because `rule_doc_lint.py keep` reads the prose between two quotes on one line as a quote.
- `designer_cleanse.md` (3.15). 5 of the 19 long sentences are his quotes in §Why you were called. Most of the
  remaining violations are "would" and "could" in the tests that the rule needs ("would he reject the mod?", "could
  only fail the same way") and -ing forms in names ("land, life", "Settle the ambiguities", "using it").

### The long sentences that stay

| file, line | kind |
|---|---|
| `designer_exam.md` 65 | an owner quote (his 2026-11-20 words), joined at a bold lead |
| `designer_exam.md` 79 | two short sentences that the lint joined at a bold lead |
| `designer_examples.md` 3, 11 | a sentence that holds a command (11 also holds his 2026-11-03 quote) |
| `designer_examples.md` 28, 43, 47 (×3), 57, 72, 73, 75, 79, 89, 93, 97 (×2), 104, 110, 117 | an owner quote, or two short sentences that the lint joined at a quote or a bold lead |
| `designer_examples.md` 101 | two short sentences that the lint joined at a bold lead |
| `designer_cleanse.md` 25, 30, 32, 34 (×2) | an owner quote (§Why you were called) |
| `designer_cleanse.md` 52, 238 | a sentence that holds a command |
| `designer_cleanse.md` 62, 72, 76, 79 (×2) | two short sentences that the lint joined at a bold lead, or a command |
| `designer_cleanse.md` 89, 91, 116 | a definition after a bold lead (Land, Life, a mod that is not a biome) |
| `designer_cleanse.md` 107, 134 | a sentence that holds a command |
| `designer_cleanse.md` 168 | a rule example in quotes, joined at a bold lead |
| `designer_cleanse.md` 354 | the Authority line, a sentence that holds a command (left word for word; the same line stands in other role files) |

## The shared block

`designer.md` holds a copy of `designer_cleanse.md` from "## What a first version may contain" to the line before "## What
a bar is". `selftest_designer_first_version_rules.py` keeps the two copies equal. Part 1 left the block to this part.
This run rewrote the block in `designer_cleanse.md` and copied it, byte for byte, into `designer.md`.

The block is the brief's own prose. It is not his card text. His three card answers of 2026-11-17T06:24:09Z are on
`OWNER.jsonl` as card labels and descriptions with different words ("Land, life, one signature (Recommended)", "Next
version, switched off (Recommended)"). So the rewrite of the block changes none of his words. The phrase "one signature"
stays, because the test's mutation case edits it.

## Code that reads the files, and what the rewrite kept for it

- `designer_stage.py` cites `designer_exam.md` steps 3, 4 and 5 in comments and in refusal text. The step numbers stay.
  `selftest_designer_stage.py` looks for "Cold Reader" in the stage-4 packet. The title stays.
- `exam_retake.py` and `acceptance/exam_retake_map_accept.py` cite step 4. The step stays.
- `designer_cleanse.py` pastes the text below the first `---` line, and reads the section "## Why you were called" for the
  reviewer. Both stay. The brief body adds no spend word (`selftest_designer_cleanse.py` refuses one in the prompts).
- `selftest_designer_first_version_rules.py`: the block, the three headings, and "one signature".

## The hand count

| file | old line | what a cold reader lacks | state after |
|---|---|---|---|
| `designer_exam.md` | "Injected with `designer.md` whenever the concept is at stage 4, resumed or not." | a fragment with no subject | "The launcher injects this file …" |
| `designer_exam.md` | "Skill `evaluation-independence` for the readers and judges." | a fragment with no verb | "For the readers and judges, read the skill …" |
| `designer_exam.md` | "Each rule binds with or without it." | what "it" is | "with or without that check" |
| `designer_exam.md` | "The read map comes from these answers." | what a read map is | gloss from `exam_retake.py`: which leaves each scenario read, written as `exam_reads.json` |
| `designer_exam.md` | "every later retake is whole" | what "whole" means | points at step 8, **WHOLE** |
| `designer_exam.md` | "neither declares a self-read or a role in its own words" | what a declared role looks like | the example from `declared_role` in `designer_stage.py`, and that `check` refuses it |
| `designer_examples.md` | "Loaded only on an explicit request …; never injected by stage." | a fragment with no subject | three sentences, each with its subject |
| `designer_examples.md` | "What he says on looking is the raw material." | raw material for what | "the raw material for acceptance lines" |
| `designer_examples.md` | "passes the same pre-review as an ask" | what the pre-review is | gloss from `designer_dialogue.md` §A turn with him, part 5 |
| `designer_examples.md` | "A mock of a game object is not, so his reaction to it settles less." | what "is not" and "it" refer to | "is not nearly the object"; "a mock of a game object" |
| `designer_examples.md` | "Option A had the recommendation, GPT and a blind reader on *can you tell up from down*. … None of them was set that test." | who judged on what | "had our recommendation, GPT and a blind reader behind it. All three judged on one test …" |
| `designer_examples.md` | "Ask the form per surface" | what the form is | gloss from the quotes and `designer_dialogue.md`: a glance at a snapshot, or a read of a write-up ("surface" stays undetermined) |
| `designer_examples.md` | "the unit is the reader's" | what the unit does | the old words stay (the check needs them); a plain sentence follows |
| `designer_cleanse.md` | "Runner: Codex or Fable." | a fragment | "The runner is Codex or Fable." |
| `designer_cleanse.md` | "The launcher pastes …" | which launcher | names `designer_cleanse.py` |
| `designer_cleanse.md` | "Make that impossible to repeat." | what "that" is | "Make a repeat of that impossible." after the 64/60 sentence |
| `designer_cleanse.md` | "On Slack, a "proven dead zone" …" | Slack the chat service, or the mod | "Slack (the Gimme Some Slack mod)", from `LEXICON.md` |
| `designer_cleanse.md` | "this project keeps having already built it" | the subject of "it" | "in this project, the thing is often already built" (the same repair as part 1 in `designer_grounding.md`) |
| `designer_cleanse.md` | "the review prints the refusal here" | where "here" is | "on his pages" |

Other changes on the way, not counted above: long paragraphs became bullet lists (§Your authority, stance 2, the bar
parts 3, 5 and 6, the whole bar, the model entry, procedure steps 5 and 6, his two pages); one 60-word sentence on the
deletion argument became a condition and a sentence.

Names of people: this run read the diff for names. No person's name is in the three files. "Torres" (a pawn, in his
quote) stays in `designer_examples.md`. Conductor, Examiner, Challenger and Reader keep their counts or rise. No name was
lost.

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of `designer_cleanse.md` with `RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED` replaced, "locked 64 bars" changed to "locked many bars", and "proven dead zone" changed | 1 lost (the id), exit 1. Check 1 did not see the lost 64 or the changed quote. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 4 lost (the code span, the 64, the quote, the id), exit 1 |
| check 2 | the first draft of `designer_examples.md` | 4 lost: prose fragments between two quotes on one line, which the check reads as quotes. This run restored each fragment word for word. |
| check 1, the 3 files and `designer.md` | the final rewrite | 10, 63, 25 and 52 items, 0 lost, exit 0 |
| check 2, the 3 files and `designer.md` | the final rewrite | 80, 68, 95 and 204 spans, 0 lost, exit 0 |
| `rule_doc_lint.py selftest`, `checkable.py selftest` | — | PASS; 19 of 19 |
| `selftest_designer_first_version_rules.py`, `selftest_designer_cleanse.py` (288 checks), `selftest_designer_exam_slots.py`, `selftest_designer_stage.py`, `selftest_cleanse_plan.py` (48 checks), `selftest_maturation_autonomy.py`, `selftest_mod_owner_hold.py`, `selftest_wrapup_live_clone.py`, `acceptance/exam_retake_map_accept.py` (39 of 39) | the final files | PASS |
| part 1's tests on `designer.md`: `selftest_touching_code_cost_rule.py`, `selftest_rule_homes_in_briefs.py`, `selftest_self_fix_rule.py`, `selftest_restart_now.py`, `selftest_conversion_owed.py`, `selftest_flagship_contract.py`, `selftest_designer_park.py`; also `selftest_skills_by_work.py`, `selftest_retired_era_gone.py` | the final files | PASS |

## What the meaning read found

Three fresh Opus readers (rm-judge, model opus), one for each file, one at a time. Each reader got the old and the new
text and not the writer's reasoning. The `designer_cleanse.md` reader also covered the block that `designer.md` copies.

| file | finding | repair |
|---|---|---|
| `designer_exam.md` | No meaning change. One borderline line: "reopens the stages that depended on the changed input" can narrow the old "them", which may include the owner event. | "depended on the voiding change" |
| `designer_examples.md` | "The launcher loads this file only on an explicit request" is false. The launcher reads only the `stage_N` lists; no `.py` file reads `on_request`. A run could wait for the launcher to supply the file. | old passive wording restored: "This file is loaded only on an explicit request …"; who loads it is listed under "Could not determine" |
| `designer_examples.md` | "In the game, stills that an agent called good met …" can read as if the stills were captures from the game. The old order says the stills met his words when he saw the thing in the game. | old order restored: "Stills that an agent called good met *"…"* in the game." |
| `designer_cleanse.md` | No meaning change. The reader checked the authority bullets, stance 2, the deletion condition, the seven standing rulings, the fate of an extra, the six parts of a bar, the whole bar, the models, the procedure, his two pages, and each number and date. | one long line rewrapped (style) |

No reader read the repairs. The repairs restore old wording or narrow a reference, and both no-loss checks ran again
after them.

## Conflicts (listed, not decided)

1. **"quote those answers word for word".** `designer.md` says: "The two sections below quote those answers word for word
   from `roles/designer_cleanse.md`". The two sections are the brief's own prose about his three card answers. His card
   answers on `OWNER.jsonl` (2026-11-17T06:24:09Z) have other words. The sentence is true if "word for word" means "a
   copy of the brief's text". The sentence is false if it means "his answers, word for word". This run did not edit
   the sentence. The Conductor decides.

## Could not determine

| file | line | question | who would know |
|---|---|---|---|
| `designer_exam.md` | "the reject case of a core line"; "a core leaf removed" | What makes a line or a leaf "core" at stage 4. `concept_tree.py` allows the `[core]` tag only on `## open` lines and refuses an open core line at Gate A, so no core line is open at stage 4. The exam may mean the leaves that carry the mod's main experience. | the author of `design/RimMandrake/concept_agent_design_2026-11-01.md` §5; the Conductor |
| `designer_examples.md` | "This file is loaded only on an explicit request" | Who loads the file. No `.py` file reads `on_request` (`git grep`). | the author of `designer_manifest.json`; the Conductor |
| `designer_examples.md` | "Ask the form per surface; never infer it." | What a "surface" is (a page, a screen, a moment in a mod). Part 1 listed the same question. | the author of the 2026-11-02 dialogue rules |
| `designer_cleanse.md` | "Never write "the family" by itself." | What "the family" names. The spec `2026-11-16-designer-cleanse-and-bar-definition.md` has no "family". It may mean a group of situations with no stated range. | the author of the v2 brief (`design/RimMandrake/roles.history.md` §designer_cleanse.md: header) |

## What this run did not test

- No Designer run and no cleanse run read the new files. `selftest_designer_stage.py` builds packets from them, and
  `selftest_designer_cleanse.py` builds prompts on fixtures; no live stage or cleanse ran.
- No measurement shows that a Designer run acts better on the new text.
- The three repairs of the meaning-read findings had no second meaning read.
