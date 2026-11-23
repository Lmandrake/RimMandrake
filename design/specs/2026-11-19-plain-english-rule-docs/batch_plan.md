# Batch plan: the plain-English rewrite of every other rule file

Item: `RIMMANDRAKE_REWRITE_RULE_DOCS_PLAIN_ENGLISH_LOSE_NOTHING`. Run 1, 2026-11-19. This plan covers each file in
`census.md` except `CLAUDE.md`. `claude_md_review.md` covers `CLAUDE.md`.

## The plan in short

- The plan has 17 batches. Each batch has a name. No two batches edit one file. So the batches can run at the same time.
- One batch is done: the worked example, `src/RimMandrake/rimflow/roles/artist.md`.
- Each batch writes with Opus. A fresh Opus reader then compares old and new text for meaning.
- Each batch runs two no-loss checks, the STE lint and the tests that read its files.
- The worked example showed one thing that the checks do not see. The first draft changed the meaning of 3 lines.
  Both no-loss checks passed on that draft. Only a read against the source found the 3 lines.
- So the meaning read by a second reader is a required step. It is not optional polish.

## What each batch does, in order

1. **Record the base.** Note the commit. Each check reads the old text as `git:<commit>:<path>`.
2. **Hand count.** Read each file as a cold reader. List each line that the reader cannot act on. Use the three
   checks of `~/.claude/skills/clear-findings/references/wordings/D-binding-test.md`. Check 1 decides: can the reader
   point at what each noun means? Grade a line together with the lines that travel with it.
3. **Rewrite.** Follow "The writing rules" below.
4. **Run the no-loss checks.** Use the commands in "The checks". Watch each check fail on a planted loss first.
5. **Run the tests that read the file.** Find them with `git grep -l <file name> -- '*selftest*' '*accept*'`.
6. **Meaning read.** A fresh Opus agent that did not write the text reads old and new text side by side. The agent
   lists each line whose meaning changed. The writer repairs each line, or restores the old line.
   Then the same reader reads each repair and each later edit against the old text. If the writer edits a line after
   that read, the reader reads that line too. The result file names each line that no reader read.
7. **Write the result file.** The path is `design/specs/2026-11-19-plain-english-rule-docs/results/<BATCH NAME>.md`.
   The file holds the scores before and after, and the hand count. The file lists each conflict. The file lists each
   line that the batch could not determine.
8. **Land.** One `./publish` for the batch, with explicit paths.

Each batch has its own result file. So no two batches edit one file.

## The writing rules

- **Simplified Technical English.** No sentence over 20 words. Active voice. One instruction in each sentence. The
  condition comes before the command. The same word for the same thing.
- **Name the subject in each sentence.** Do not open a sentence with "it" or "this" if another bullet holds the
  subject.
- **Give a coined term its meaning at first use.** Take the meaning from the code or from the home file. Never invent
  a meaning or a cost. If the batch cannot determine the meaning, write `could not determine` in the result file and
  name who knows.
- **Keep the slogan.** A heading or a bold lead that other files cite stays word for word. Add the plain sentence
  after the slogan.
- **Never rewrite the owner's quoted words.** Text around a quote can change.
- **Never change what a rule means.** When two files disagree, list the conflict in the result file. Do not pick.
- **Keep each code span, number, path, date and named id.** A rule can move to its home file. Then the old file keeps
  a pointer, and the check runs with the home file as `--also`.
- **Do not grade a heading as a rule.** A heading is a label for the lines below it.
- **Leave a line alone when the line already binds.** A short line that a reader can act on is correct.

## The checks

```
CK=~/dev/MandrakeWorkflows/skills/crystallize/scripts/checkable.py
RL=design/specs/2026-11-19-plain-english-rule-docs/rule_doc_lint.py

python3 $CK compare git:<base>:<path> <path> [--also <home file>...]     # no-loss check 1: exit 1 lists each lost span
python3 $RL keep    git:<base>:<path> <path> [--also <home file>...]     # no-loss check 2: exit 1 lists each lost span
python3 $RL lint <path> --show                                           # STE lint, long sentences, flagged lines
python3 $RL selftest                                                     # 16 planted cases for the lint and for keep
python3 $CK selftest                                                     # 19 planted cases for check 1
```

- Check 1 reads dates, quotes of four words or more, numbers with a unit, paths and named ids.
- Check 2 reads each code span, each number, each quote and each named id. Check 2 counts numbers. So one lost copy of
  a number is a loss.
- Neither check reads prose. A rule with no number, name or code span has no mechanical guard. The meaning read
  guards such a rule.
- Neither check reads the names of people. Read the diff for names, and say so in the result file.
- Exit code 3 means that the tool could not read a file or its lint module. Exit code 3 is not a pass.

## The STE target

- The STE lint is at or below 2.5 violations per 100 words.
- A sentence over 20 words can stay only if it is one of three kinds. The result file lists each one with its kind:
  - an owner quote;
  - a sentence that holds a command;
  - two short sentences that the lint joined.
- The flagged count is at or below the count before.
- The file can grow. The worked example grew by 16%. A plain sentence is longer than a coined term.

The target for `design/RimMandrake/standing_rulings.md` and the fact files is different. Those files are homes for
evidence. Their quotes, dates and measurements stay. The target binds only their rule bullets.

The STE lint counts "may" as a violation. Keep "may" where "may" gives permission. The drain of `CLAUDE.md` made the
same decision. The lint also counts passive voice. Passive voice is not a defect by itself
(`~/dev/MandrakeWorkflows/skills/clear-findings/FINDING.md`). Do not bend a clear sentence to remove one passive verb.

## The model tier

- **Writer: Opus.** A rewrite that loses nothing is bounded work on complex text. A test does not prove the meaning,
  so Sonnet is the wrong tier.
- **Meaning reader: a fresh Opus.** The reader judges the work of another agent.
- **Census and lint runs: Sonnet**, or no model. The tool is deterministic.
- **Fable: none.** The batches are a parallel fleet. `infrastructure/agents/Agent_Policy.md` holds the ladder.

## The batches

Sizes and scores are from `census.json` at commit `328611932d`. "STE" is violations per 100 words. "long" is the
count of sentences over 20 words.

The order puts the most-read files first. In a group of equal reach, the file with the worse score comes first.

| order | batch | files | bytes | STE | long | who reads the files | special rule |
|---|---|---|---|---|---|---|---|
| 1 | `RIMMANDRAKE_REWRITE_SUBAGENT_FILES_SHARED_BLOCK_SIX_COPIES` | the 6 `.claude/agents/rm-*.md` files, `.claude/rm_agent_shared_block.md`, `.claude/rm_positive_steps.md`, `.claude/commands/broadcast.md` | 61,221 | 5.05 | 127 | each subagent at its start | The shared block is in each agent file word for word. Edit the block once, then copy it. `selftest_skills_by_work.py` and `selftest_positive_steps_one_source.py` must pass. Keep the front matter and each "Read first" list. |
| 2 | `RIMMANDRAKE_REWRITE_CONDUCTOR_FILES_LONGEST_ROLE_FILE` | `roles/conductor.md`, `roles/conductor_restart.md`, `infrastructure/agents/CONDUCTOR.md` | 52,218 | 4.09 | 140 | the Conductor at each wake | `owed_view_accept.py` reads the "## Start of turn" heading. Keep each heading. |
| 3 | `RIMMANDRAKE_REWRITE_CHARTER_AND_AGENT_POLICY_EVERY_SEAT_READS` | `infrastructure/agents/CHARTER.md`, `infrastructure/agents/Agent_Policy.md` | 37,093 | 4.22 | 87 | each agent that `CLAUDE.md` sends there | `Agent_Policy.md` is the only home of the model ladder. Keep each figure. |
| 4 | `RIMMANDRAKE_REWRITE_OPERATIONS_ROLE_ONE_OF_TWO_SWITCHED_ON` | `roles/operations.md` | 27,080 | 4.38 | 85 | each Operations run | None. |
| 5 | `RIMMANDRAKE_REWRITE_RESCUE_AND_WALK_ROLES_PIPELINE_NAMES_THEM` | `roles/fable_rescue.md`, `roles/walk_brief.md`, `roles/criteria_fixer.md` | 25,476 | 4.38 | 82 | a rescue run, a walk-brief writer, the neutral fixer | `maturation.py` quotes a marked block in `fable_rescue.md` step 2. Keep the marks. |
| 6 | `RIMMANDRAKE_REWRITE_JUDGE_BRIEFS_ONE_IS_CALIBRATED` | `design/RimMandrake/art_judge_brief.md`, `design/RimMandrake/scene_look_judge_brief.md`, `design/RimStarWars/canon_references/AGENT_BRIEF.md`, the two `PROMPT.md` files | 39,692 | 3.95 | 96 | each art judge and scene judge | `art_judge_brief.md` reads UNTESTED in `infrastructure/state/judge_calibration.json` (measured 2026-11-23). Calibrate it after the edit, in the same batch: `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --model art_judge_brief` (its model check is `python3 src/RimMandrake/rimflow/art_calibration.py run`). Keep each constraint id, for example A1 and E3. |
| 7 | `RIMMANDRAKE_REWRITE_BIOME_DELEGATION_DEBUG_DOCS_CODE_CITES_THEM` | `design/RimMandrake/biome_rulings.md`, `delegation_policy.md`, `debug_process.md` | 62,173 | 4.52 | 157 | each agent that a `CLAUDE.md` pointer sends there | Code cites `debug_process.md` from 40 files and `delegation_policy.md` from 23. Keep each heading and each section number. |
| 8 | `RIMMANDRAKE_REWRITE_STANDING_RULINGS_LARGEST_HOME_FILE` | `design/RimMandrake/standing_rulings.md` | 126,133 | 4.47 | 357 | each agent that a `CLAUDE.md` pointer sends there | `CLAUDE.md` holds 38 pointers to sections of this file. Keep each heading word for word. Keep each quote and date. One batch, in several sessions, one after another. |
| 9 | `RIMMANDRAKE_REWRITE_TRAP_FACT_FILES_TWO_FILES` | `infrastructure/state/facts/instrument_traps.md`, `tool_traps.md` | 80,548 | 4.13 | 273 | each agent before it trusts a count or a tool | Keep each measurement. |
| 10 | `RIMMANDRAKE_REWRITE_GIT_GAME_PURPOSE_DOCS_THREE_FILES` | `design/RimMandrake/GIT_WORKFLOW.md`, `infrastructure/GAME_STATE_WORKFLOW.md`, `PURPOSE.md` | 47,778 | 4.34 | 78 | each agent before it touches git or the game state; each new agent | Keep each owner quote. |
| 11 | `RIMMANDRAKE_REWRITE_DESIGNER_PACKET_FILES_HASH_IN_STAGE_RECORD` | `roles/designer.md`, `designer_grounding.md`, `designer_dialogue.md`, `designer_write.md`, `designer_exam.md`, `designer_examples.md`, `designer_cleanse.md` | 87,065 | 4.46 | 235 | each Designer run, by stage | `designer_stage.py` records the hash of each packet file in the concept's `stage.json`. Run the batch while no Designer run is live. This run did not determine what a changed hash does to an open concept. |
| 12 | `RIMMANDRAKE_REWRITE_UNTESTED_JUDGE_ROLE_FILES_THEN_CALIBRATE` | `roles/designer_scene_contract.md`, `roles/designer_lock.md`, `roles/code_review.md` | 22,105 | 4.27 | 58 | the coverage judge, the code reviewer, the Designer | Each file is in a calibration row that reads UNTESTED now. Do this batch together with the calibration of those briefs (`refusal_contract.py calibrate`). |
| 13 | `RIMMANDRAKE_REWRITE_PRODUCER_AUDITOR_INNOVATOR_ALL_SWITCHED_OFF` | `roles/producer.md`, `roles/auditor.md`, `roles/innovator.md`, `roles/runner_options.md` | 66,719 | 3.85 | 175 | a role run that someone starts by hand | The three roles are switched off. The Conductor can decide to wait until a role is switched on. |
| 14 | `RIMMANDRAKE_REWRITE_MATURATION_SPEC_EIGHTY_KILOBYTES` | `design/specs/2026-11-13-maturation-pipeline.md` | 80,156 | 4.23 | 133 | each agent that works on the pipeline | The file is a spec with `[HIS, date]` marks on his words. Keep each mark and each numbered item. |
| 15 | `RIMMANDRAKE_REWRITE_UNDATED_FACT_FILES_DATED_ONES_STAY` | 10 fact files with no date in the name (`operations.md`, `distress_signals.md`, `dump-is-pre-cherrypicker.md`, `biome_paint_list.md`, `biome_rosters.md`, `README.md`, `naming_inventory.md`, `steve_fault_diagnosis.md`, `clone_memory_peak.md`, `almost_out_codex_log.md`) | 78,695 | 3.57 | 140 | an agent that a search sends there | The 10 dated fact files are records. Leave them. |
| 16 | `RIMMANDRAKE_REWRITE_OTHER_DOCS_AFTER_DELETE_DECISION` | `infrastructure/STRUCTURE.md`, `infrastructure/VALIDATION_LADDER.md`, `README.md`, `LEXICON.md` | 28,279 | 4.41 | 39 | an agent that a search sends there | The Conductor first decides each candidate in `census.md`. A file that stays joins this batch. |
| 17 | `RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH` | the 32 `SKILL.md` files, `skills/README.md`, `skills/BY_WORK.md`, 5 prompt files | 650,639 | 4.51 | 1,458 | an agent that does the work that the skill names | See "Skills" below. |

A last group is not a batch of this plan: `RIMMANDRAKE_REWRITE_BRIEF_TEXT_INSIDE_CODE_FOURTEEN_MODULES`. See "Text
inside code" below.

These files are in no batch:

- `CLAUDE.md` (see `claude_md_review.md`);
- `roles/artist.md` (done);
- `design/RimMandrake/CLAUDE.history.md` (a history file);
- the 10 dated fact files;
- the two `Fable_Review/rewrites/` files;
- `infrastructure/DETERMINISM_ASSESSMENT.md` (a dated assessment);
- each candidate in `census.md`.

### How the remaining batches run (from 2026-11-23)

- Batches 6 to 17 are items on the rimflow list. The List Pipeline (`src/RimMandrake/rimflow/list_dispatch.py`) launches
  each one as a detached helper, inside its own slot limits. Item `RIMMANDRAKE_LAUNCH_REMAINING_PLAIN_ENGLISH_BATCHES_ELEVEN_LEFT`
  filed them.
- Each item's prose is its brief: `infrastructure/state/items/<ID>.md`.
- One helper run does well up to about 50 KB of text. So a larger batch is split into parts, one item each. The batch
  item waits on its parts and closes when every part is closed.
  - `standing_rulings.md` is five session items, by heading. Each session waits on the one before.
  - The maturation spec is two session items. The second waits on the first.
  - The skills batch is one item per skill, one item for `skills/README.md` and `skills/BY_WORK.md`, and one item for
    the five art-evaluation prompt files. The 11 registered skills were filed first, so the pipeline takes them first.
- The two calibration batches never run at one time: the untested judge role files wait on the judge briefs. The
  prompt files wait on the untested judge role files.
- Each Designer packet part has a launch check. The check refuses the launch while a `rm-role-designer*` unit is active.
- The outcome check of each part is `batch_done.py check <ID> <paths>` beside this file. The check holds when the result
  file has its `Base:` line and its meaning-read heading, each file changed since the base, and `rule_doc_lint.py keep`
  loses nothing. `batch_done.py selftest` runs 12 planted cases.

### Which batches can run at the same time

Each batch can run with each other batch. Three limits apply.

- The batch for `standing_rulings.md` is one file. Its sessions run one after another.
- Two batches end with a calibration run: the judge briefs, and the untested judge role files. A calibration run
  uses the model quota. Do not run both at one time.
- The batch for the Designer packet files runs only while no Designer run is live.

### Skills

`CLAUDE.md` allows a skill edit only in a fresh-context curation session. So the skills batch is a set of curation sessions.

- One session rewrites one skill. So two sessions never edit one file.
- Do the 11 registered skills first. The harness loads a registered skill by itself, so more agents read it.
- Then do `skills/README.md` and `skills/BY_WORK.md`. Each agent file and role file points at `BY_WORK.md`.
- Then do the 21 skills that are read by path.
- Never change a skill's `description` in a rewrite. The description decides when the skill loads. Change one only
  with the trigger evals of `skill-creator`.
- A skill keeps its lessons. Evidence moves to `references/history.md` beside the skill (`skills/README.md`).
- Two prompt files are in a calibration row (`preamble.md`, `opus_first_pass.md`). Handle them like the untested judge role files.
- `skills/generating-rimworld-sprites/SKILL.md` line 385 cites `infrastructure/agents/POLICY.md`. That file is
  superseded. Point the line at `infrastructure/agents/CHARTER.md` in the session for that skill.

### Text inside code

Fourteen modules build brief text from strings in the code. Hooks print refusal messages. That text tells an agent
how to behave, so the owner's request covers it. A change to that text is a code change.

- Pipeline code is under the boundary-page rule of `CLAUDE.md`. Its tests run at `./publish`.
- So each module is one ticket with its own tests. It is not a prose batch.
- Start with the footer that `src/RimMandrake/rimflow/detached_helper.py` adds to each helper brief. Each detached
  helper reads that footer.
- The Conductor decides if this group is in the scope of the item.

## The worked example: `src/RimMandrake/rimflow/roles/artist.md`

The Artist role file is a mid-size role file: 8,374 bytes. No calibration row and no packet hash binds it. One test
reads it (`src/RimMandrake/rimflow/selftest_artist_role.py`).

### Scores

| measure | before | after |
|---|---|---|
| bytes | 8,374 | 9,684 |
| words in linted prose | 1,026 | 1,260 |
| STE violations per 100 words | 3.41 | 2.30 |
| sentences over 20 words | 15 | 6 |
| flagged lines (mechanical) | 3 | 1 |
| lines that a cold reader cannot act on (hand count, by the writer) | 10 | 0 |

Six long sentences stay. Two are the owner's quote. One holds a command. The lint joined the other three at a bold
lead.

### The 10 lines of the hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "its `enabled` field, which the Conductor may flip … Off, nothing starts it but …" | the subject of "Off" | rewritten |
| "You are the codification of something that already runs" | what "codification" asks the reader to do | rewritten |
| "What needs him goes to the Conductor (below)" | where "below" is | names the section |
| "flag a factual error. Record it …" | what "it" is | rewritten |
| "only through the routes below, each with its regression run" | where "below" is | names the section |
| "For each override" | what an override is | meaning added from `skills/rimworld-art-evaluation/references/criteria_ledger.md` |
| "with its CL id" | what a CL id is | meaning added from the same file |
| "as the skill says" | which skill | names the skill |
| "`art_judge_brief.md` A1-A5 hold" and "brief E3" | two coded ids with no title | names the section; gives E3 in short |
| "Tuning to one key is how a judge learns a single sitting." | what a "key" is | rewritten |

One line holds a possible error. The file says "the ledger rows carry no timestamp". Row `CL-001` of
`infrastructure/state/art_eval/criteria_ledger.jsonl` carries an `at` field with a time. The two disagree. This run
kept the line and lists the conflict here. The Conductor decides.

### The checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy with one ruling id removed and "at most 4 subjects" changed to "a few subjects" | 1 lost (the id), exit 1. Check 1 did not see the lost "4". |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 3 lost (the code span, the id, one copy of "4"), exit 1 |
| check 1 | the real rewrite | 24 items, 0 lost, exit 0 |
| check 2 | the real rewrite | 81 spans, 0 lost, exit 0 |
| `selftest_artist_role.py` | old file, then new file | PASS, then PASS |
| `src/RimMandrake/Utils/selftest_skills_by_work.py` | the new file | PASS |
| `selftest_retired_era_gone.py` | the new file | PASS |

The first form of check 2 did not see the lost "4" either. This run then made check 2 count each number. That is why
the plan has two checks: each check has a blind area, and the two areas differ.

### What the meaning read found

The writer read the first draft against the source file and found 3 lines with a changed meaning. Both no-loss checks
had passed on that draft.

| first draft | why it was wrong | repair |
|---|---|---|
| "You write down what the art pipeline does." | The old line says that the role is the written form of existing work. The old line does not tell the Artist to write things down. | "This role is the written form of work that already runs." |
| "An override is a verdict of the owner that differs from the verdict of the art pipeline." | The draft invented the meaning. | The meaning from `criteria_ledger.md`: a ledger row with the source `owner_override`. |
| "If you tune the judge to one verdict, …" | A "key" is the set of answers of one sitting, not one verdict. | "If you tune the judge to the answers of one sitting, …" |

In this run the writer did the meaning read. A second reader did not. A writer misses the errors of the writer's
own draft. So the plan requires a second reader for each later batch.

## What this plan does not prove

- No measurement shows that an agent behaves better after a rewrite. The clear-findings study measured 5 comparisons
  of a good wording against another good wording. Behaviour changed in 0 of 5. That study did not test bad wording
  against good wording.
- The plan was tested on one file of 8,374 bytes. The plan is not tested on a file of 126,133 bytes.
- The 2.5 target comes from one worked example and from the `CLAUDE.md` drain (1.51).
- The reader column of the census counts citations. A batch must check its own readers before it trusts the order.
