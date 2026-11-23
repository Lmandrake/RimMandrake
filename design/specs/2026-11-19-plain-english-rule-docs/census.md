# Census: every file that tells an agent how to behave

Item: `RIMMANDRAKE_REWRITE_RULE_DOCS_PLAIN_ENGLISH_LOSE_NOTHING`. Run 1, 2026-11-19. The census read commit
`328611932d`, before this run changed a file.

## What the census found

- The census holds 130 files and 1,906,073 bytes. [measured]
- The files have 4,247 sentences over 20 words. `CLAUDE.md` has 2 of them. [measured]
- The STE lint gives 4.29 violations per 100 words for the 130 files together. `CLAUDE.md` scores 1.51. [measured]
- So `CLAUDE.md` is the only large file that follows Simplified Technical English now.
- Skills are the largest class: 34 files and 638,704 bytes.
- Nine files are candidates to delete or to move. The section "Candidates to delete or to move" gives the evidence.
- Seven files are bound to a judge calibration. An edit to one of those files changes the calibration status.
- A subagent does not load `CLAUDE.md`. A subagent gets its project rules from the shared block in its agent file.

## How to read the table

- **bytes**: the size of the file.
- **STE**: STE lint violations per 100 words. The tool is `rule_doc_lint.py` in this folder. A lower figure is better.
- **long**: the count of sentences over 20 words.
- **flagged**: the count of lines that the tool flags for a cold reader. The next section explains the flags.
- **cited by**: the count of other tracked files that name this file. The three counts are code, role and agent
  files, and skills. A citation is evidence of a reader. A citation is not proof that a program loads the file.
- **last commit**: the date of the last commit that changed the file.

The STE figure measures obedience to the STE spec. The STE figure does not measure clarity. The clear-findings skill
says the same about its own lint.

## The count of lines that a cold reader cannot act on

No tool can count those lines. Only a reader who does not know the project can judge a line. So the census gives
two counts.

1. **The flagged count is mechanical.** It is in the table for each file. A flagged line is a line to read. A flagged
   line is not a verdict. The tool flags four things:
   - `pronoun`: a sentence that opens with "It", "This", "That" or "They" and names no subject;
   - `bare-id`: a short coded id with no title beside it, for example `D31` or `WP-15`;
   - `shout`: an emphasis emoji, or three words in a row in capital letters;
   - `above`: "see above", "the latter" and like phrases, which make the reader hunt for the subject.
2. **The hand count is a judgement.** This run read two files line by line.
   - `CLAUDE.md`: 24 lines that a cold reader cannot act on. The tool flagged 20 lines. Only 3 lines are in both
     counts. `claude_md_review.md` lists the 24 lines.
   - `src/RimMandrake/rimflow/roles/artist.md`: 10 lines. The tool flagged 3 lines. `batch_plan.md` lists the 10 lines.

The two counts disagree, and that is a finding. The flags find weak sentence shapes. The flags do not find a coined
term such as "the dials" or "stamp-only". Each later batch must do its own hand count. The plan requires that.

## How this run searched

1. The run took the list in the brief as the start.
2. The run read `LIVE_ALWAYS` in `src/RimMandrake/rimflow/era_text.py`. That list is the repo's own list of live
   instruction files. The list added `design/specs/2026-11-13-maturation-pipeline.md`.
3. The run read `.claude/settings.json` for each hook, and `.claude/` for each agent and command file.
4. The run read `dispatcher_schedule.json` and `designer_manifest.json` for the role files that launchers load.
5. The run read `infrastructure/state/judge_calibration.json` for the files in each calibrated brief.
6. The run searched the tracked file names for these words: prompt, judge, brief, template, policy, process, workflow,
   charter, rulings, rubric.
7. For each file, the run searched the tracked files for the file's name (`git grep`). The search left out
   conversations, ledger shards, handoffs, items and concept records.

The census leaves out dated records on purpose. A dated record tells what happened. A dated record does not tell an
agent how to behave. Examples: `design/RimMandrake/*_2026-*.md`, exam briefs in `design/concepts/`, closed items.

## Instruction text that the census did not lint

- **Text inside code.** Some programs build a brief from strings in the code. Fourteen modules hold such text. The
  largest are `coverage_judge.py`, `maturation.py`, `maturation_autonomy.py`, `detached_helper.py`, `role_launch.py`
  and `seat_restart.py`. The footer of this run's own brief comes from `detached_helper.py`.
- **Hook messages.** `.claude/hooks/` holds 34 hooks. A refusal message from a hook is an instruction to the agent.
- **Lessons.** `infrastructure/state/lessons/` holds 547 files and 41,826 words. Each lesson is one short file.
- **Boundary pages.** `design/specs/*/boundary.md` holds 26 pages. Each page states what one piece of pipeline code
  promises.
- **Skill reference files.** `skills/` holds 144 markdown files. The census lints the 32 `SKILL.md` files, the roster
  and the work map. The census lints 5 prompt files from one skill. The other reference files are not in the table.

`batch_plan.md` gives each of these groups a batch or a reason to leave the group alone.

## Candidates to delete or to move

Each row is a candidate only. This run deleted no file.

| file | evidence | what must happen first |
|---|---|---|
| `GLOBAL_CLAUDE.md` | `infrastructure/STRUCTURE.md` calls it a mirror of `~/.claude/CLAUDE.md`. The last commit is 2026-10-30. A diff against the live file shows 628 changed lines. So the mirror states old rules. No file cites it except a test list. | Remove it from `DOCS` in `.claude/hooks/selftest_documented_commands.py` and from `infrastructure/STRUCTURE.md`. |
| `final.md` | The file is a result report from a Codex run. The last commit is 2026-11-11. No file cites the root `final.md`. The 14 code hits name other files with the same name. | Nothing. |
| `infrastructure/agents/POLICY.md` | The file says that it is superseded by `CHARTER.md` since 2026-08-27. Two live strings still sent agents to it. This run pointed both at `CHARTER.md`. | Repoint `skills/generating-rimworld-sprites/SKILL.md` line 385 in a skill session. Remove it from `selftest_documented_commands.py`. |
| `infrastructure/agents/REP.md` | The file says that the seat retired on 2026-08-27. Two code comments name it as history. | Nothing. |
| `infrastructure/agents/CODEX_PROPOSAL_ART_WORKER.md`, `CODEX_PROPOSAL_GENERATING_IMAGES_SKILL_DRAFT.md`, `CODEX_PROPOSAL_GRAPHICS_WORKFLOW.md` | Each file opens with "status: PROPOSAL … NOT ruled, NOT validated, NOT wired to anything live". Only the three files cite each other. They sit in the folder for seat rules. They hold 70,638 bytes. | Move them to `design/RimMandrake/`. Do not delete: they are a design record. |
| `infrastructure/README.md` | The last commit is 2026-08-26. No file cites it. It describes seat definitions that are retired. | Check each claim against `infrastructure/STRUCTURE.md`. |
| `infrastructure/REFRESH.md` | The last commit is 2026-08-14. No file cites it. `CLAUDE.md` names `refresh.py` and not this file. | Check that `skills/rimworld-load-round/SKILL.md` holds its content. |

Three more groups have no reader that this run found. The three groups are records, so no group is a candidate:

- `Fable_Review/rewrites/` (2 files);
- `src/RimMandrake/rimflow/docs/` (5 files, last commit 2026-11-01);
- the dated fact files.
 The Conductor decides if `src/RimMandrake/rimflow/docs/` still describes the live `rimflow`.

## Findings that the census made on the way

- `.claude/hooks/set_session_title.py` told each seat to follow `infrastructure/agents/POLICY.md`. That file is
  superseded. This run changed the string to `CHARTER.md`. `set_agent_window.sh` had the same error and the same fix.
- `src/RimMandrake/rimflow/selftest_artist_role.py` read a skill through `.claude/skills/`. The skill is not
  registered, so the test stopped with an error. This run pointed the test at `skills/`. The test passes now.
- `.claude/rm_agent_shared_block.md` says that `CLAUDE.md` "cost ~23k tokens per call". `CLAUDE.md` is now 40,856
  bytes, which is about 10k tokens [guess ~70%]. The figure in the block is old. The block is in six agent files.
- Six of eight scheduled roles are switched off. Their files are still live: `run-now` starts a role by hand.

## The table

### Root files

The harness loads `CLAUDE.md` into each session in this repo: the Conductor window, each detached helper and each role run. A subagent does not load `CLAUDE.md` (`omitClaudeMd: true`). `CLAUDE.md` sends each new agent to `PURPOSE.md`.

| file | bytes | STE | long | flagged | cited by: code, roles and agents, skills | last commit | note |
|---|---|---|---|---|---|---|---|
| `CLAUDE.md` | 39902 | 1.51 | 2 | 20 | 125, 14, 12 | 2026-11-19 | Before this run. After: see `claude_md_review.md`. |
| `PURPOSE.md` | 9457 | 4.75 | 29 | 9 | 1, 0, 0 | 2026-11-17 |  |

Class total: 2 files, 49359 bytes, STE 2.17 per 100 words, 31 sentences over 20 words, 29 flagged lines.

### Agent definitions (`.claude/`)

The harness loads one `rm-*.md` file when a session starts a subagent of that type. That file is all that the subagent knows of the project rules. `selftest_skills_by_work.py` checks that each agent file holds the shared block. The `/broadcast` command loads `broadcast.md`.

| file | bytes | STE | long | flagged | cited by: code, roles and agents, skills | last commit | note |
|---|---|---|---|---|---|---|---|
| `.claude/agents/rm-bridge.md` | 6441 | 4.88 | 11 | 0 | 0, 0, 0 | 2026-11-19 |  |
| `.claude/agents/rm-builder.md` | 8921 | 4.69 | 22 | 0 | 2, 0, 0 | 2026-11-19 |  |
| `.claude/agents/rm-consult.md` | 6136 | 5.02 | 10 | 0 | 0, 0, 0 | 2026-11-19 |  |
| `.claude/agents/rm-fixer.md` | 7510 | 4.62 | 13 | 0 | 1, 0, 0 | 2026-11-19 |  |
| `.claude/agents/rm-judge.md` | 6379 | 4.67 | 11 | 0 | 0, 0, 0 | 2026-11-19 |  |
| `.claude/agents/rm-testpilot.md` | 20852 | 5.42 | 51 | 3 | 3, 1, 0 | 2026-11-19 |  |
| `.claude/commands/broadcast.md` | 351 | 3.7 | 0 | 0 | 0, 0, 0 | 2026-10-30 |  |
| `.claude/rm_agent_shared_block.md` | 4227 | 5.47 | 8 | 0 | 0, 0, 0 | 2026-11-19 | Each `rm-*.md` agent file holds this text word for word. A test enforces that. |
| `.claude/rm_positive_steps.md` | 404 | 5.8 | 1 | 0 | 1, 0, 0 | 2026-11-19 | One source for a quoted owner text. A test enforces the copies. |

Class total: 9 files, 61221 bytes, STE 5.05 per 100 words, 127 sentences over 20 words, 3 flagged lines.

### Seat files (`infrastructure/agents/`)

`CLAUDE.md` sends each agent to `CHARTER.md` and to `Agent_Policy.md`. The Conductor reads `CONDUCTOR.md` at wake. That file sends the Conductor to `roles/conductor.md`.

| file | bytes | STE | long | flagged | cited by: code, roles and agents, skills | last commit | note |
|---|---|---|---|---|---|---|---|
| `infrastructure/agents/Agent_Policy.md` | 21688 | 4.32 | 50 | 10 | 10, 4, 1 | 2026-11-19 |  |
| `infrastructure/agents/CHARTER.md` | 15405 | 4.1 | 37 | 8 | 1, 14, 1 | 2026-11-19 |  |
| `infrastructure/agents/CODEX_PROPOSAL_ART_WORKER.md` | 26083 | 3.51 | 25 | 4 | 0, 2, 0 | 2026-11-19 | MOVE CANDIDATE. |
| `infrastructure/agents/CODEX_PROPOSAL_GENERATING_IMAGES_SKILL_DRAFT.md` | 14018 | 4.14 | 11 | 3 | 0, 1, 0 | 2026-10-04 | MOVE CANDIDATE. |
| `infrastructure/agents/CODEX_PROPOSAL_GRAPHICS_WORKFLOW.md` | 30537 | 4.42 | 22 | 9 | 0, 1, 0 | 2026-11-19 | MOVE CANDIDATE. |
| `infrastructure/agents/CONDUCTOR.md` | 1218 | 3.97 | 3 | 0 | 8, 3, 0 | 2026-11-13 |  |
| `infrastructure/agents/POLICY.md` | 524 | 1.67 | 1 | 0 | 2, 0, 1 | 2026-11-18 | DELETE CANDIDATE. |
| `infrastructure/agents/REP.md` | 477 | 3.28 | 1 | 0 | 2, 0, 0 | 2026-11-04 | DELETE CANDIDATE. |

Class total: 8 files, 109950 bytes, STE 4.09 per 100 words, 150 sentences over 20 words, 34 flagged lines.

### Role files (`src/RimMandrake/rimflow/roles/`)

`role_launch.py` gives a scheduled role its file (`dispatcher_schedule.json`, field `instructions`). `designer_stage.py` puts the Designer files into a run by stage (`designer_manifest.json`). The pipeline code names the other role files in the briefs that it writes.

| file | bytes | STE | long | flagged | cited by: code, roles and agents, skills | last commit | note |
|---|---|---|---|---|---|---|---|
| `src/RimMandrake/rimflow/roles/artist.md` | 8374 | 3.41 | 15 | 3 | 1, 0, 3 | 2026-11-19 | Before this run. After: 2.30. See `batch_plan.md`. Scheduled role, switch off. |
| `src/RimMandrake/rimflow/roles/auditor.md` | 17429 | 4.15 | 59 | 9 | 5, 0, 0 | 2026-11-19 | Scheduled role, switch off. |
| `src/RimMandrake/rimflow/roles/code_review.md` | 6007 | 4.08 | 14 | 6 | 2, 0, 0 | 2026-11-19 | In a calibration row (now UNTESTED). |
| `src/RimMandrake/rimflow/roles/conductor.md` | 40292 | 4.15 | 108 | 8 | 4, 2, 1 | 2026-11-19 | Scheduled role, switch on. |
| `src/RimMandrake/rimflow/roles/conductor_restart.md` | 10708 | 3.89 | 29 | 1 | 0, 1, 0 | 2026-11-19 |  |
| `src/RimMandrake/rimflow/roles/criteria_fixer.md` | 2535 | 4.68 | 8 | 1 | 1, 0, 0 | 2026-11-19 |  |
| `src/RimMandrake/rimflow/roles/designer.md` | 21595 | 4.45 | 58 | 4 | 6, 8, 0 | 2026-11-19 | In the Designer packets (`designer_manifest.json`). Scheduled role, switch off. |
| `src/RimMandrake/rimflow/roles/designer_cleanse.md` | 23026 | 4.63 | 65 | 4 | 2, 1, 0 | 2026-11-19 |  |
| `src/RimMandrake/rimflow/roles/designer_dialogue.md` | 9088 | 4.55 | 22 | 1 | 2, 2, 0 | 2026-11-18 | In the Designer packets (`designer_manifest.json`). |
| `src/RimMandrake/rimflow/roles/designer_exam.md` | 8880 | 3.47 | 26 | 1 | 5, 1, 0 | 2026-11-19 | In the Designer packets (`designer_manifest.json`). |
| `src/RimMandrake/rimflow/roles/designer_examples.md` | 9824 | 5.36 | 30 | 0 | 1, 2, 0 | 2026-11-03 | In the Designer packets (`designer_manifest.json`). |
| `src/RimMandrake/rimflow/roles/designer_grounding.md` | 6784 | 4.15 | 16 | 1 | 2, 1, 0 | 2026-11-19 | In the Designer packets (`designer_manifest.json`). |
| `src/RimMandrake/rimflow/roles/designer_lock.md` | 6768 | 4.02 | 23 | 1 | 6, 2, 0 | 2026-11-19 | In a calibration row (now UNTESTED). In the Designer packets. |
| `src/RimMandrake/rimflow/roles/designer_scene_contract.md` | 9330 | 4.63 | 21 | 1 | 7, 6, 0 | 2026-11-19 | In a calibration row (now UNTESTED). In the Designer packets. |
| `src/RimMandrake/rimflow/roles/designer_write.md` | 7868 | 4.01 | 18 | 3 | 2, 2, 0 | 2026-11-18 | In the Designer packets (`designer_manifest.json`). |
| `src/RimMandrake/rimflow/roles/fable_rescue.md` | 19456 | 4.57 | 67 | 3 | 3, 0, 0 | 2026-11-19 |  |
| `src/RimMandrake/rimflow/roles/innovator.md` | 18278 | 4.22 | 57 | 7 | 1, 0, 0 | 2026-11-19 | Deleted 2026-11-23: the role is retired. |
| `src/RimMandrake/rimflow/roles/operations.md` | 27080 | 4.38 | 85 | 4 | 1, 0, 0 | 2026-11-19 | Scheduled role, switch on. |
| `src/RimMandrake/rimflow/roles/producer.md` | 15565 | 3.58 | 43 | 5 | 2, 0, 0 | 2026-11-19 | Scheduled role, switch off. |
| `src/RimMandrake/rimflow/roles/runner_options.md` | 15447 | 3.03 | 16 | 6 | 0, 1, 0 | 2026-11-19 | Only `designer.md` cites it. |
| `src/RimMandrake/rimflow/roles/walk_brief.md` | 3485 | 2.53 | 7 | 0 | 2, 0, 0 | 2026-11-19 |  |

Class total: 21 files, 287819 bytes, STE 4.20 per 100 words, 787 sentences over 20 words, 69 flagged lines.

### Rulings, policy and process

`CLAUDE.md` points at each of these files. An agent reads one section when a `CLAUDE.md` rule sends the agent there.

| file | bytes | STE | long | flagged | cited by: code, roles and agents, skills | last commit | note |
|---|---|---|---|---|---|---|---|
| `design/RimMandrake/CLAUDE.history.md` | 6140 | 4.24 | 15 | 15 | 0, 0, 0 | 2026-11-19 |  |
| `design/RimMandrake/GIT_WORKFLOW.md` | 31842 | 3.72 | 37 | 2 | 4, 1, 1 | 2026-11-19 |  |
| `design/RimMandrake/biome_rulings.md` | 17383 | 3.88 | 40 | 25 | 3, 0, 0 | 2026-11-01 |  |
| `design/RimMandrake/debug_process.md` | 28737 | 4.63 | 70 | 8 | 40, 4, 3 | 2026-11-19 |  |
| `design/RimMandrake/delegation_policy.md` | 16053 | 5.03 | 47 | 4 | 23, 4, 6 | 2026-11-19 |  |
| `design/RimMandrake/standing_rulings.md` | 126133 | 4.47 | 357 | 59 | 27, 7, 4 | 2026-11-19 |  |
| `design/specs/2026-11-13-maturation-pipeline.md` | 80156 | 4.23 | 133 | 14 | 7, 6, 0 | 2026-11-19 |  |
| `infrastructure/GAME_STATE_WORKFLOW.md` | 6479 | 5.41 | 12 | 8 | 2, 0, 0 | 2026-11-19 |  |

Class total: 8 files, 312923 bytes, STE 4.40 per 100 words, 711 sentences over 20 words, 135 flagged lines.

### Judge and review briefs

A judge or a reviewer gets the brief as its instructions. The art-evaluation code reads the prompt files (`src/RimMandrake/Utils/art_eval/`).

| file | bytes | STE | long | flagged | cited by: code, roles and agents, skills | last commit | note |
|---|---|---|---|---|---|---|---|
| `design/RimMandrake/art_judge_brief.md` | 12420 | 3.25 | 28 | 29 | 3, 2, 4 | 2026-11-19 | CALIBRATED. An edit makes it UNTESTED. |
| `design/RimMandrake/gpt_reviews/PROMPT.md` | 1477 | 4.98 | 2 | 2 | 0, 0, 0 | 2026-10-07 |  |
| `design/RimMandrake/scene_look_judge_brief.md` | 11614 | 4.76 | 32 | 4 | 3, 0, 0 | 2026-11-18 | In a calibration row (now UNTESTED). |
| `design/RimStarWars/canon_references/AGENT_BRIEF.md` | 12534 | 3.7 | 29 | 12 | 1, 0, 1 | 2026-10-22 |  |
| `design/RimStarWars/canon_references/gpt_review/PROMPT.md` | 1647 | 3.98 | 5 | 1 | 0, 0, 0 | 2026-10-07 |  |
| `skills/rimworld-art-evaluation/references/prompts/departures_brief.md` | 2421 | 3.75 | 9 | 0 | 3, 0, 1 | 2026-11-05 |  |
| `skills/rimworld-art-evaluation/references/prompts/gpt_targeted_second_look.md` | 1588 | 5.43 | 3 | 0 | 2, 0, 1 | 2026-10-23 |  |
| `skills/rimworld-art-evaluation/references/prompts/opus_first_pass.md` | 1722 | 4.56 | 2 | 0 | 2, 0, 0 | 2026-10-23 | In a calibration row (now UNTESTED). |
| `skills/rimworld-art-evaluation/references/prompts/preamble.md` | 4481 | 4.1 | 14 | 1 | 1, 0, 0 | 2026-11-05 | In a calibration row (now UNTESTED). |
| `skills/rimworld-art-evaluation/references/prompts/regen_prompt_edit.md` | 1723 | 3.89 | 6 | 0 | 1, 0, 2 | 2026-10-23 |  |

Class total: 10 files, 51627 bytes, STE 4.02 per 100 words, 130 sentences over 20 words, 49 flagged lines.

### Fact files (`infrastructure/state/facts/`)

`CLAUDE.md` points at `instrument_traps.md` and `tool_traps.md`. The other fact files are dated records. An agent reads one when a search finds it.

| file | bytes | STE | long | flagged | cited by: code, roles and agents, skills | last commit | note |
|---|---|---|---|---|---|---|---|
| `infrastructure/state/facts/README.md` | 1294 | 2.84 | 2 | 5 | 0, 0, 0 | 2026-08-27 |  |
| `infrastructure/state/facts/almost_out_codex_log.md` | 12791 | 3.35 | 1 | 6 | 0, 0, 0 | 2026-10-25 |  |
| `infrastructure/state/facts/biome_paint_list.md` | 10790 | 3.97 | 11 | 5 | 3, 0, 1 | 2026-11-06 |  |
| `infrastructure/state/facts/biome_rosters.md` | 5780 | 2.71 | 8 | 5 | 0, 0, 0 | 2026-10-21 |  |
| `infrastructure/state/facts/clone_memory_peak.md` | 4291 | 2.95 | 13 | 2 | 1, 0, 0 | 2026-11-19 |  |
| `infrastructure/state/facts/codex_live_2026-11-10.md` | 3771 | 4.04 | 6 | 1 | 0, 0, 0 | 2026-11-19 |  |
| `infrastructure/state/facts/distress_signals.md` | 5813 | 4.74 | 14 | 12 | 1, 1, 0 | 2026-08-23 |  |
| `infrastructure/state/facts/dump-is-pre-cherrypicker.md` | 5165 | 4.42 | 17 | 14 | 6, 0, 0 | 2026-09-05 |  |
| `infrastructure/state/facts/heap_reload_ratchet_2026-11-06.md` | 7519 | 3.57 | 23 | 2 | 2, 0, 0 | 2026-11-06 |  |
| `infrastructure/state/facts/instrument_traps.md` | 45694 | 4.21 | 152 | 52 | 4, 13, 0 | 2026-11-19 |  |
| `infrastructure/state/facts/log_spam_rises_ee0fbaa8_2026-11-06.md` | 2560 | 2.93 | 6 | 0 | 0, 0, 0 | 2026-11-06 |  |
| `infrastructure/state/facts/logbound_deploy_2026-11-10.md` | 3154 | 4.88 | 4 | 0 | 0, 0, 0 | 2026-11-10 |  |
| `infrastructure/state/facts/naming_inventory.md` | 7033 | 3.01 | 7 | 7 | 0, 0, 0 | 2026-08-23 |  |
| `infrastructure/state/facts/oom_kills_2026-10-31.md` | 3888 | 2.45 | 7 | 3 | 0, 0, 0 | 2026-11-19 |  |
| `infrastructure/state/facts/oom_kills_2026-11-03.md` | 5988 | 2.45 | 11 | 3 | 0, 0, 0 | 2026-11-19 |  |
| `infrastructure/state/facts/operations.md` | 15273 | 3.79 | 44 | 3 | 0, 2, 0 | 2026-11-19 |  |
| `infrastructure/state/facts/post_incident_health_2026-11-02.md` | 7015 | 2.05 | 4 | 0 | 0, 0, 0 | 2026-11-19 |  |
| `infrastructure/state/facts/roll_arm_harvest_2026-08-24.md` | 4516 | 3.38 | 6 | 10 | 0, 0, 0 | 2026-08-24 |  |
| `infrastructure/state/facts/roll_arm_harvest_2026-08-28.md` | 3836 | 3.79 | 7 | 4 | 0, 0, 0 | 2026-08-28 |  |
| `infrastructure/state/facts/steve_c_drive_fill_2026-11-03.md` | 3749 | 3.24 | 9 | 1 | 1, 0, 0 | 2026-11-03 |  |
| `infrastructure/state/facts/steve_fault_diagnosis.md` | 10465 | 2.9 | 23 | 7 | 0, 0, 0 | 2026-11-17 |  |
| `infrastructure/state/facts/tool_traps.md` | 34854 | 4.02 | 121 | 15 | 4, 0, 0 | 2026-11-19 |  |

Class total: 22 files, 205239 bytes, STE 3.79 per 100 words, 496 sentences over 20 words, 157 flagged lines.

### Skills

The harness loads a registered skill when its description matches the task. A skill that is not registered is read by path. `skills/BY_WORK.md` maps kinds of work to those paths. Each agent file and each role file has a "Read first" list of skill paths.

| file | bytes | STE | long | flagged | cited by: code, roles and agents, skills | last commit | note |
|---|---|---|---|---|---|---|---|
| `skills/BY_WORK.md` | 8244 | 5.0 | 4 | 0 | 1, 17, 1 | 2026-11-19 |  |
| `skills/README.md` | 14777 | 5.63 | 10 | 3 | 2, 0, 1 | 2026-11-19 |  |
| `skills/clone-landing-commits/SKILL.md` | 4405 | 3.04 | 5 | 0 | 1, 5, 3 | 2026-11-07 | registered. |
| `skills/generating-rimworld-sprites/SKILL.md` | 24471 | 5.29 | 59 | 27 | 17, 3, 9 | 2026-11-19 | registered. |
| `skills/gravship-layout/SKILL.md` | 24269 | 5.04 | 52 | 27 | 1, 0, 2 | 2026-11-07 | not registered, read by path. |
| `skills/live-debugging-proof-harness/SKILL.md` | 22055 | 3.17 | 33 | 11 | 6, 9, 11 | 2026-11-19 | registered. |
| `skills/northstar-validation/SKILL.md` | 17389 | 4.75 | 33 | 3 | 1, 3, 3 | 2026-11-07 | not registered, read by path. |
| `skills/reading-rimworld-graphics/SKILL.md` | 21305 | 4.67 | 59 | 21 | 0, 0, 5 | 2026-11-07 | not registered, read by path. |
| `skills/rimbridge-companion/SKILL.md` | 16326 | 4.33 | 31 | 17 | 0, 0, 7 | 2026-11-07 | registered. |
| `skills/rimbridge/SKILL.md` | 28193 | 4.29 | 62 | 55 | 803, 3, 35 | 2026-11-19 | registered. |
| `skills/rimflow-operations/SKILL.md` | 9641 | 4.31 | 13 | 1 | 1, 1, 2 | 2026-11-19 | registered. |
| `skills/rimworld-art-evaluation/SKILL.md` | 11959 | 3.58 | 18 | 0 | 14, 2, 4 | 2026-11-07 | not registered, read by path. |
| `skills/rimworld-canon-references/SKILL.md` | 15842 | 5.45 | 45 | 16 | 0, 2, 2 | 2026-11-07 | not registered, read by path. |
| `skills/rimworld-content-moderation/SKILL.md` | 22350 | 4.81 | 65 | 27 | 1, 0, 3 | 2026-11-19 | not registered, read by path. |
| `skills/rimworld-crew-and-nemesis-events/SKILL.md` | 8267 | 3.73 | 16 | 3 | 0, 0, 4 | 2026-10-10 | not registered, read by path. |
| `skills/rimworld-custom-incidents/SKILL.md` | 8600 | 3.85 | 17 | 5 | 0, 0, 3 | 2026-11-07 | not registered, read by path. |
| `skills/rimworld-debug-testing/SKILL.md` | 28834 | 4.33 | 66 | 36 | 2, 5, 11 | 2026-11-07 | not registered, read by path. |
| `skills/rimworld-deploy/SKILL.md` | 23924 | 4.97 | 60 | 29 | 3, 2, 13 | 2026-11-07 | registered. |
| `skills/rimworld-ideoligion/SKILL.md` | 16629 | 4.18 | 29 | 13 | 0, 0, 2 | 2026-11-07 | not registered, read by path. |
| `skills/rimworld-layout-layers/SKILL.md` | 18869 | 4.79 | 50 | 17 | 0, 0, 2 | 2026-09-04 | not registered, read by path. |
| `skills/rimworld-live-review/SKILL.md` | 29533 | 4.23 | 77 | 25 | 5, 2, 9 | 2026-11-07 | registered. |
| `skills/rimworld-load-round/SKILL.md` | 26255 | 4.36 | 68 | 27 | 2, 1, 14 | 2026-11-07 | registered. |
| `skills/rimworld-modding/SKILL.md` | 29005 | 4.33 | 68 | 36 | 13, 7, 14 | 2026-11-07 | not registered, read by path. |
| `skills/rimworld-quests/SKILL.md` | 24409 | 4.07 | 52 | 25 | 4, 0, 5 | 2026-11-07 | not registered, read by path. |
| `skills/rimworld-review-sheets/SKILL.md` | 9925 | 4.64 | 26 | 0 | 6, 2, 3 | 2026-11-07 | registered. |
| `skills/rimworld-savegame/SKILL.md` | 14282 | 4.39 | 35 | 20 | 5, 1, 5 | 2026-11-07 | not registered, read by path. |
| `skills/rimworld-scenario-building/SKILL.md` | 11925 | 5.57 | 22 | 29 | 1, 0, 2 | 2026-08-15 | not registered, read by path. |
| `skills/rimworld-scene-composition/SKILL.md` | 16924 | 4.19 | 40 | 12 | 0, 0, 2 | 2026-09-06 | not registered, read by path. |
| `skills/rimworld-sprite-facings/SKILL.md` | 28066 | 4.72 | 79 | 29 | 4, 2, 6 | 2026-11-19 | not registered, read by path. |
| `skills/rimworld-start-prep/SKILL.md` | 26486 | 4.76 | 71 | 30 | 2, 1, 7 | 2026-11-19 | not registered, read by path. |
| `skills/rimworld-world-editing/SKILL.md` | 25228 | 4.46 | 45 | 46 | 2, 0, 3 | 2026-11-07 | not registered, read by path. |
| `skills/rimworld-xenotypes/SKILL.md` | 24706 | 4.2 | 51 | 34 | 0, 0, 3 | 2026-11-07 | not registered, read by path. |
| `skills/telemetry/SKILL.md` | 5733 | 5.0 | 11 | 0 | 44, 3, 6 | 2026-11-19 | not registered, read by path. |
| `skills/using-rimflow/SKILL.md` | 19878 | 4.73 | 52 | 16 | 3, 12, 2 | 2026-11-19 | registered. |

Class total: 34 files, 638704 bytes, STE 4.51 per 100 words, 1424 sentences over 20 words, 640 flagged lines.

### Other documents

No hook or launcher loads these files. An agent reads one only when a search or another document finds it.

| file | bytes | STE | long | flagged | cited by: code, roles and agents, skills | last commit | note |
|---|---|---|---|---|---|---|---|
| `Fable_Review/rewrites/CHARTER.md` | 3968 | 3.56 | 4 | 0 | 0, 0, 0 | 2026-10-30 |  |
| `Fable_Review/rewrites/WINDOWS.md` | 2698 | 2.72 | 6 | 0 | 0, 0, 0 | 2026-10-30 |  |
| `GLOBAL_CLAUDE.md` | 11099 | 5.59 | 28 | 14 | 0, 0, 0 | 2026-10-30 | DELETE CANDIDATE. |
| `LEXICON.md` | 4025 | 2.08 | 0 | 0 | 0, 0, 0 | 2026-11-19 | The lexicon skill reads it. That skill is outside this repo. |
| `README.md` | 4295 | 3.38 | 12 | 4 | 49, 0, 2 | 2026-11-18 |  |
| `final.md` | 1240 | 7.1 | 2 | 0 | 14, 0, 0 | 2026-11-11 | DELETE CANDIDATE. |
| `infrastructure/DETERMINISM_ASSESSMENT.md` | 49790 | 4.55 | 115 | 65 | 8, 0, 0 | 2026-11-19 |  |
| `infrastructure/README.md` | 1954 | 6.61 | 5 | 1 | 0, 0, 0 | 2026-08-26 | DELETE CANDIDATE. |
| `infrastructure/REFRESH.md` | 3348 | 4.24 | 8 | 0 | 0, 0, 0 | 2026-08-14 | DELETE CANDIDATE. |
| `infrastructure/STRUCTURE.md` | 15666 | 5.23 | 19 | 8 | 1, 0, 0 | 2026-11-19 |  |
| `infrastructure/VALIDATION_LADDER.md` | 4293 | 4.19 | 8 | 12 | 2, 0, 4 | 2026-11-19 |  |
| `src/RimMandrake/rimflow/docs/AGENTS.md` | 10569 | 3.77 | 15 | 2 | 0, 0, 0 | 2026-11-01 |  |
| `src/RimMandrake/rimflow/docs/COMPARISON.md` | 21280 | 4.66 | 45 | 8 | 0, 0, 0 | 2026-10-30 |  |
| `src/RimMandrake/rimflow/docs/DESIGN_HISTORY.md` | 17895 | 4.57 | 43 | 20 | 0, 0, 0 | 2026-10-24 |  |
| `src/RimMandrake/rimflow/docs/README.md` | 23863 | 4.77 | 45 | 14 | 0, 0, 0 | 2026-11-18 |  |
| `src/RimMandrake/rimflow/docs/RIMFLOW_ideogram.md` | 13248 | 4.98 | 36 | 7 | 0, 0, 0 | 2026-10-30 |  |

Class total: 16 files, 189231 bytes, STE 4.61 per 100 words, 391 sentences over 20 words, 155 flagged lines.
## What this census did not measure

- The census did not test if an agent behaves better after a rewrite. No tool in this repo measures that.
- The reader column counts citations. The census did not trace each program to prove that it loads the file.
- The census did not lint text inside code, hook messages, lessons, boundary pages or skill reference files.
- The hand count covers 2 of 130 files.
