# Result: `RIMMANDRAKE_REWRITE_JUDGE_BRIEFS_ONE_IS_CALIBRATED`

Batch 6 of `batch_plan.md`. Run 2026-11-23 (run 1 of the list item).

Base: `7538c96970766211b044f7a2edc7d4295c93f7e1`

Files:

- `design/RimMandrake/art_judge_brief.md`
- `design/RimMandrake/scene_look_judge_brief.md`
- `design/RimStarWars/canon_references/AGENT_BRIEF.md`
- `design/RimMandrake/gpt_reviews/PROMPT.md`
- `design/RimStarWars/canon_references/gpt_review/PROMPT.md`

## Scores

| file | bytes | words | STE per 100 words | sentences over 20 words | flagged lines |
|---|---|---|---|---|---|
| `art_judge_brief.md` | 12,550 → 13,533 | 1,620 → 1,761 | 3.21 → 2.39 | 28 → 19 | 29 → 29 |
| `scene_look_judge_brief.md` | 12,735 → 13,970 | 1,830 → 2,033 | 4.75 → 3.20 | 34 → 17 | 7 → 7 |
| `AGENT_BRIEF.md` | 12,534 → 13,006 | 1,755 → 1,854 | 3.70 → 2.21 | 29 → 15 | 12 → 8 |
| `gpt_reviews/PROMPT.md` | 1,477 → 1,580 | 221 → 238 | 4.98 → 2.52 | 2 → 0 | 2 → 2 |
| `gpt_review/PROMPT.md` | 1,647 → 1,706 | 251 → 264 | 3.98 → 2.27 | 5 → 2 | 1 → 1 |

Two files stay above the 2.5 target:

- `scene_look_judge_brief.md` (3.20). Of its 65 violations, 9 come from the answer label `COULD NOT SEE` ("could" is a
  banned modal to the lint). About 10 come from owner quotes. Others are slogans and headings that code or other files
  cite ("Front-back ordering", "Resetting a scene is harness housekeeping"). Two edits that removed the word "should"
  and a passive verb changed the meaning; the meaning reader found them, and this run restored the old words.
- `gpt_reviews/PROMPT.md` (2.52). The meaning reader found that three plainer project facts said more than the old
  text ("The mod uses Harmony patches"). This run restored the old bare facts.

### The long sentences that stay

- `art_judge_brief.md`, 19: each lettered constraint is joined by the lint with its source line (`— Owner …`), so
  15 are two short sentences that the lint joined. Lines 41 (A4) and 115 (F1) hold a command. Line 151 is an owner
  quote. Lines 37 and 68 (A1, C1) stay word for word, because `art_calibration.py` and `selftest_art_calibration.py`
  read C1 by its first words, and the calibration cases were judged on these lines.
- `scene_look_judge_brief.md`, 17: lines 12 (two), 47 and 142 are owner quotes or hold one. Lines 63, 66, 69, 109,
  113 and 180 hold a command or a checklist item. Lines 19, 52, 88, 95, 105, 107 and 119 hold a command or a slogan
  with its reason.
- `AGENT_BRIEF.md`, 15: each holds a command, or is a bold lead joined with its paragraph.
- `gpt_review/PROMPT.md`, 2: each is a list of the items that GPT must cover (a command).

The flagged lines that stay: 29 `bare-id` flags in the art brief are the constraint ids (A1 … F1). The item says to
keep each id. The `shout` flags are answer labels that code parses (`COULD NOT SEE`, `DEBUGGING.`, `MUST-SHOW
IMPROVEMENTS`) or 🔴 headings.

## Code that reads the files, and what the rewrite kept for it

- `src/RimMandrake/rimflow/art_calibration.py` parses each constraint as a line `- <A-F><n>[a]. ` with indented
  continuation lines. Each constraint keeps that form. The `D4 exception` sub-bullet stays inside D4.
- `selftest_art_calibration.py` needs C1 to start "North is the creature's rear (no face, no eyes); south looks at the
  camera", and D4 to hold "backdrop", "halo", "ground shadow", "scenery", "description" and "CL-035". All hold.
- `selftest_art_judge_no_keyline.py` needs a rule that says "No outlines" with 2026-10-04, and no rule that asks for an
  outline. B1a keeps the negation in front of "black outline".
- `judge_cli.py` holds the pass-1 question of the scene brief as code. The brief keeps the question word for word.
- The GPT answer labels stay word for word: `check_late_review.py` parses the ERRORS and ENRICHMENT sections of the
  canon review answers.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| art: "Judge only against what is written here and there" | what "there" is | names the canon entry |
| art: "what he has shown by overriding the pipeline" | who "he" is (the Artist or the owner) | "The owner has overridden the pipeline", from `art_style_memory.md` line 1 |
| art: "(req 6)", "(req 2)", "(req 3)", "(req 9)" | which list of requirements | gloss: requirement N of `skills/rimworld-review-sheets/references/art_requirements.md` (req 6 there is "The canon grader is an ADVISOR", as A5 says) |
| art A4: "Owner, three defect classes" | which three | names them: missing gene, engine limit, rig limit, and the table in `AGENT_BRIEF.md` |
| art C5: "a wing render-tree" | what a render-tree is | gloss from `skills/rimworld-modding/references/flight.md` |
| art C5a: "These passed stills once" | what "These" is | "Frames with these faults passed a still-image check once" |
| art E3: "a delegated call" | what a delegated call is | gloss from `delegation_policy.md` |
| art Output: "committed by the window" | which window | "The window that launched you" |
| art: "A malformed record is itself refused: you are re-asked once" (one sentence, three steps) | the order of the steps | split into steps; the window's two acts are a list |
| scene: "For judges that did NOT build the work, looking at …" | a fragment with no verb | a full sentence |
| scene: "the per-station zoomed stare" | what the stare is | gloss from root `CLAUDE.md` §Nothing reaches the owner unread |
| scene: "What the presenter gives" | who the presenter is | gloss: the agent that gives the images to the judges, and stages each frame (from the reset rule of the same file) |
| scene: "Owner pick 11" | which pick | names OWNER.jsonl tsn 1794524114165680240, from `infrastructure/state/items/closed/RIMMANDRAKE_FOLD_FRAME_JUDGE_INTO_PRELOOK.md` |
| scene: "Its ODD or WRONG is a doubt listed …" | who lists it | `judge_cli.py` (the meaning reader checked the code) |
| scene: "(its framed `__cell_rect` crop when one exists)" | where the crop comes from | "The capture tool writes that crop" |
| canon: "The index's 'in repo' column" | which index | names `DROIDS_INDEX.md` |
| canon: "Several agents share this index" | which index | "this git index" |
| canon: "Distil from what the brief already says" | which brief | "the visual brief" |
| canon: "These are … / That is …" lines (5) | what the pronoun points at | the subject named |

Lines that a cold reader still cannot act on are under "Could not determine".

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | the art brief with `ART_SHEET_FIX_SIBLING_KEEPS_UNSEEN` removed and "0.56 tall" changed to "a bit taller" | 1 lost (the id), exit 1. Check 1 did not see the lost 0.56. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 3 lost (the code span, the id, the number 0.56), exit 1 |
| check 1 | each final file | art 53, scene 38, canon brief 16, prompts 0 and 0 items; 0 lost, exit 0 |
| check 2 | each final file | art 92, scene 64, canon brief 70, prompts 5 and 6 spans; 0 lost, exit 0 |
| `rule_doc_lint.py selftest`, `checkable.py selftest`, `batch_done.py selftest` | — | PASS; 19 of 19; GREEN 12 planted cases |
| `selftest_art_calibration.py`, `selftest_judge_open_look.py`, `selftest_judge_refusal_records.py`, `selftest_judge_brief_records.py`, `selftest_judge_calibration.py`, `selftest_judge_card_answers.py`, `selftest_scene_look_calibration.py`, `selftest_touching_code_cost_rule.py` | old, then new | PASS, then PASS |
| `src/RimMandrake/Utils/selftest_art_judge_no_keyline.py` | old, then new | FAIL, then PASS (see "A red test repaired") |
| `design/specs/2026-11-19-touching-code-cost/acceptance_stop_rules_calibrated.py` | old, then new | FAIL 0/7, then FAIL 0/7 before calibration and FAIL 2/7 after (another item's acceptance test; see Conflicts 1) |

Names of people: this run read the diff for names. The owner, the Artist, the Conductor, Lucasfilm, and each species
and creature name (Ithorian, Kaminoan, Muun, Lasat, Herglic, Cathar, Iktotchi, Bothan, Gungan, Duros, Twi'lek, Rakata,
Tuskens, Varactyl, ullai, fermatalis) keep the same count or more in each file.

## A red test repaired

`src/RimMandrake/Utils/selftest_art_judge_no_keyline.py` was red on the base: "B1a asks for an outline/keyline:
'black outline'". The cause: commits `f8003374bc` and `99cede2bfa` (2026-11-22 and 2026-11-23) added the owner's
one-creature exception to B1a ("the Pyrelands ullai carries a MEDIUM black outline … by the owner's pick of
2026-11-23, this creature only"). The check was wrong for that state: the exception is his ruling, not the retired
general clause. The repair exempts only an "Exception:" sentence that names a dated owner pick and ends "only.".

- Red before the repair on the real brief, green after.
- Planted cases, still red after the repair: the same exception with no dated owner pick; an exception that is not
  limited to one subject ("creatures carry a MEDIUM black outline by the owner's pick of 2026-11-23."); a general demand
  ("Sprites carry a black outline.").

## What the meaning read found

Five fresh Opus readers (rm-judge, model opus), one per file and one at a time, read the old and the new text. No
reader got the writer's reasoning. The writer repaired every finding. No reader read the repairs.

| file | finding | repair |
|---|---|---|
| art | "The owner overrode the pipeline on some art": "on some art" is new | "The owner has overridden the pipeline." (owner confirmed by `art_style_memory.md` line 1) |
| art | the "req N" gloss is new | kept: requirement 6 of `art_requirements.md` is the canon-grader rule that A5 cites |
| art | B2 gloss "(a body that blends into the ground)" can narrow "grey mud" | gloss removed |
| art | C4 gloss "the frames and heads line up on the body parts that do not move" broadens C4 | old wording restored |
| art | C5 gloss of "render-tree" is new | kept: the reader checked it against `flight.md` line 69 |
| art | "a verdict on each refused constraint itself" narrows "a verdict on the constraint itself" | old wording restored |
| art | "`refusal_contract.py` refuses … the alarm … goes up" names an actor and a kind that the old text does not | "A malformed record is itself refused … `REFUSAL_NOTHING_COULD_EVER_PASS` is raised" |
| art | polish: "Only judge-KEEP pictures reach him" then "also reach him" reads as a contradiction | "Judge-KEEP pictures reach him … Rows flagged … also reach him. Nothing else reaches him." |
| art | polish: B6 "Never use bright red" speaks to an artist, not a judge | "A Modern tier is never bright red or paint-coloured as a tier marker." |
| scene | "A matrix scene is one prepared cell" is a wrong definition | "In a matrix scene, one prepared cell … is replicated over the variables that matter" |
| scene | "The presenter replicates the cell" gives the presenter a new job | removed (the passive of the old text) |
| scene | the presenter gloss is new | narrowed to what the file says: the presenter gives the images and stages each frame |
| scene | "what a player expects to see" is softer than "should see" | "what a player should see" restored |
| scene | "`refusal_contract.py` refuses … The presenter then asks you once more" names new actors | "A malformed record is itself refused and re-asked once." restored |
| scene | "that crop of the subject's cell" adds a detail | "The capture tool writes that crop." |
| scene | polish: "a judge that you ask again" | "a judge that is asked again" restored |
| canon brief | the gloss "A regen is a new generation of the art for a subject" is new | removed |
| canon brief | "The Rakata entry is the standard" broadens "that is the standard" | "That record of unsourced values is the standard." |
| canon brief | "nobody briefs the batch again" bans more than "instead of being re-briefed" | "each future batch reads this file instead of a new brief" |
| mod prompt | "The mod uses Harmony patches", "The campaign has 'one kind of heat'", "when we add content" each say more | old wording restored for all three |
| canon prompt | "These include: size; …" makes the list open | "The facts to cover are: size; …" |

## Calibration

Both calibrations ran after the last edit of the briefs, on the final text, in this clone.

Status before this run (`infrastructure/state/judge_calibration.json`, read at the start): `art_judge_brief` UNTESTED
(hash `876d86436ad6b980`, which an earlier edit had moved), `scene_look_judge_brief` UNTESTED (hash `51cc3deaa9a369cb`,
its planted cases never run).

### `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --model art_judge_brief`

Exit 0. It printed the registry table; the art row read:

```
art_judge_brief          CALIBRATED 11 planted case(s) ran and came out as planted
```

| case | planted | got |
|---|---|---|
| `regress_RM_Shadefern_B` | pass | pass |
| `regress_RM_Huldu_C` | refuse | refuse |
| `regress_RM_Ssurr_B` | refuse | refuse |
| `regress_RM_Vellak_B` | refuse | refuse |
| `regress_RM_Murrin_C` | refuse | refuse |
| `regress_RM_Dewblade_B` | pass | pass |
| `regress_RM_DecayDrake_r2` | pass | pass |
| `regress_RM_Peeper_r2` | refuse | refuse |
| `regress_RM_Danglemaw_r1` | refuse | refuse |
| `kept_RM_Gawpsack_live` | pass | pass |
| `north_from_south_RM_DecayDrake_r2` | refuse | refuse |

Status after: CALIBRATED at hash `31822b34d2eb6fb3`, run at 2026-11-23T13:39:14Z. Spend: ≈1.68M weighted_v2 tokens
(Opus 5.5), converted from the cases' recorded list cost of $6.72.

### `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --model scene_look_judge_brief`

Exit 0. The scene row read:

```
scene_look_judge_brief   CALIBRATED 3 planted case(s) ran and came out as planted
```

| case | planted | got |
|---|---|---|
| `brim_pit_open_look` | refuse | refuse |
| `brim_pit_ladder_bar` | refuse | refuse |
| `one_m_pit_ladder_bar` | pass | pass |
| `one_m_pit_open_look` | recorded, not planted | pass |

Status after: CALIBRATED at hash `da6d873488f43611`, run at 2026-11-23T13:41:01Z. Spend: UNMEASURED (the case rows
record no cost). This calibration tests the prompts in `judge_cli.py` and `modcheck/judge.py`, not the brief's prose
(Conflicts 3).

The rest of the table did not change in either run: `code_review` UNTESTED, `coverage_judge` UNTESTED,
`art_eval_first_pass` UNTESTED, `evidence_gate` and `maturation_advance` CALIBRATED.

## Conflicts (listed, not decided)

1. **The art brief has no stopping level.** Root `CLAUDE.md` §Touching code has a cost: "A brief that reviews, judges,
   audits or files findings states three things: the level that is enough; when to stop looking; the polish route".
   The scene brief states them. The art brief does not. Commit `0d4d48310c` (2026-11-20) reverted the art brief's
   flaw-or-polish section, because its recalibration came out wrong on 2 of 11 planted cases.
   `acceptance_stop_rules_calibrated.py` (item `RIMMANDRAKE_CALIBRATE_JUDGE_STOP_RULES_WORDS_UNTIL_RUN`) read FAIL 0/7
   before this run and FAIL 2/7 after the two calibrations (the scene and art briefs are CALIBRATED; the art brief still
   lacks "## When the look is enough"). This run did not add a stop rule: that changes the brief's meaning.
2. **A stale section name in code.** A comment in `src/RimMandrake/Utils/northstar_driver/judge_cli.py` cites the scene
   brief's section "Every refusal is a record". The scene brief has no such heading. Its heading is "Refusal record:
   every ODD, WRONG or COULD NOT SEE is one". "Every refusal is a record" is a bullet of `standing_rulings.md` §A refusal
   carries its path to pass. Pipeline code, so not edited in this prose batch.
3. **The scene calibration does not read the scene brief.** The `scene_look_judge_brief` row hashes the brief,
   `judge_cli.py` and `modcheck/judge.py`. `scene_look_calibration.py` sends the prompts in `judge_cli.py` and
   `judge.py`, not the brief's text. So an edit of the brief resets the row to UNTESTED, but the planted cases test
   only the code's prompts.

## Could not determine

| line | question | who would know |
|---|---|---|
| canon brief: "WebSearch is dead on this model group." | which model group, and whether this is still true | the Conductor; the author of the 2026-09-15 canon batches |
| canon brief: "invoke the `fetcher` skill", "`MANIFEST.txt` in the delivery folder", "`Complete/<id>.txt.log`" | no `fetcher` skill is linked under `~/.claude/skills/` on Archmagi, although the Fetcher project exists (`~/dev/Fetcher`); where the delivery folder is | the Fetcher project's docs (`~/dev/Fetcher`) |
| canon brief: the `sips` commands | `sips` is a macOS tool; this run did not find it on Archmagi (WSL). Which machine runs this brief | the Conductor |
| art D4: "B1's prompt" | which prompt B1 names | the author of `RIMMANDRAKE_RECONCILE_ART_BRIEF_SIZE_RULE_THREE_PICKS_REFUSED` |
| art D4: "owner_escalations_cauldron" | a file, a sheet or a record | the same author |
| art B2: "grey mud" | the exact meaning (a body that blends into the ground, or a dull muddy colour); the reader showed that the first gloss can narrow it | the owner (Lesson 2026-09-12, softened 2026-09-14) |
| art C4: "Registration on the rigid body" | whether registration covers all frames or only heads and a flyer's body | the owner (Owner 2026-10-20) |
| art and scene: `criterion_hash`, `new_since` | defined in `design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md` section 1; left as field names | — |

## Found on the way (no ticket)

- `.claude/hooks/block_agent_over_slots.py`: an Agent call that a different PreToolUse hook refused still left a
  90-second spawn reservation, so the next four spawns of this run read `slots_full`. Not worth the touch: the
  reservation clears itself after 90 s, and the cost was one wait.

## What this run did not test

- No canon-entry agent and no GPT review ran on the new text of `AGENT_BRIEF.md` or the two `PROMPT.md` files. The
  art and scene judges ran on the new text only in the calibration runs.
- No reader read the repairs of the meaning-read findings.
- No measurement shows that an agent acts better on the new text.
