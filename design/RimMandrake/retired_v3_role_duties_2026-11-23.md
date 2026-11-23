# Duties of the retired v3 roles: who does each one now (2026-11-23)

The owner, 2026-11-23: *"Those are old v3 roles we retired! V3 and relentless was supposed to be retired. Get those out if active rules. The codex versions of modern roles though are valuable for when we need to burn their tokens instead."*

The Producer and the Auditor are deleted. The Arbiter, the Setter and the Innovator were retired before them. The table
takes each duty of `design/RimMandrake/role_responsibilities_2026-10-26.md` Part 4. Item:
`RIMMANDRAKE_REMOVE_RETIRED_V3_ROLES_FROM_ACTIVE_RULES_STILL_LISTED`. REVIVE-OR-DROP means that nothing does the duty now
and that the Conductor decides if it matters. Nobody is assigned here.

## Producer

| duty | who or what does it now | evidence |
|---|---|---|
| P-1 goals into a daily list, a weekly plan and tickets; focus WIP cap | The Conductor orders its lane from `CONDUCTOR_GOALS.md`. The mod pipeline takes each mod's next act, and the List Pipeline works the list. Nobody writes a daily list or a weekly plan. The WIP cap holds no window. | `roles/conductor.md` §Goals down; `maturation_dispatch.py`; `rm-list-dispatch.timer` enabled; `focus_cap.seats` is `[]` |
| P-2 critical path for each focus mod | The mod's own folder: version, bars, gaps, stage. | `CLAUDE.md` §Mods keep their own state |
| P-3 named scenarios before a build | The Designer's tree and scenes, for a mod. The filer's acceptance test, for a ticket. | `roles/designer_write.md`; `~/.claude/CLAUDE.md` (a ticket is filed with its acceptance test) |
| P-4 replan on a failed plan step or a forecast miss | Operations files one item for the Conductor, and the Conductor decides the cut. (Three `REPLAN REQUEST` notes of 2026-11-18 to 11-20 were read by nobody: `RIMMANDRAKE_ROUTE_REPLAN_REQUESTS_TO_CONDUCTOR_PRODUCER_OFF`.) The automatic run on a failed plan step: REVIVE-OR-DROP. | `roles/operations.md` §The economy pass; `role_launch.py` event runs deleted |
| P-5 weekly backlog hygiene (blocked and stale items) | The Conductor sweeps after a major system event. The List Pipeline closes and escalates list items. The weekly run of `queue_staleness_review.py`: REVIVE-OR-DROP (no unit and no role names it). | `roles/conductor.md` §After a major system event; `git grep queue_staleness_review` |
| P-6 what the test lane runs | A program: `wired_mods.json`, rotated. The variable `TESTQ_FILL_MODS` still overrides. | `Utils/testq/coverage.py` |
| P-7 bar coverage; test budget for each mod | The coverage judge. The budget for each mod: nobody, and a stage ceiling takes its place. | `rimflow/coverage_judge.py`; `maturation_dispatch.py releases` |
| P-8 order finish, strengthen, explore; a stopping point for each item | The pipeline's stages and the two tests of §Touching code has a cost. | `standing_rulings.md` |
| P-9 read the idea bank `design/V2_DREAMS.md` | Any seat may write to it. Nobody reads it: REVIVE-OR-DROP. | `CHARTER.md` (the only live rule line that names it) |

## Arbiter

| duty | who or what does it now | evidence |
|---|---|---|
| A-1, A-2, A-3 verdict on a done claim; verify backlog; conditional pass | The pipeline's blind judges, for a mod. A test, for a ticket. The conditional pass no longer exists. | `design/specs/2026-11-13-maturation-pipeline.md` |
| A-4 keep each mod's floor wired | The program `modcheck floor`, and the mod's builder. | `modcheck floor --all` |
| A-5 judge protocol for taste calls | The judge briefs. | `design/RimMandrake/art_judge_brief.md`; `.claude/agents/rm-judge.md` |
| A-6 code review gate | The reviewer with a boundary page, then one fresh reader. | `CLAUDE.md` §Code is clean when its promises are tested |
| A-7 an escape becomes a check, red on the old build | The run that fixes it. | `CLAUDE.md` §Touching code has a cost |
| A-8 new bars, regression checks, merges | Agents, delegated. Only the Conductor loosens a bar. | `delegation_policy.md` §1 |

## Auditor

| duty | who or what does it now | evidence |
|---|---|---|
| AU-1 sample closed items and passes | The mechanical check of every close: `close_check.py`, daily, no AI (a close whose commit is not on main reopens its item). The sample by a reader: the weekly follow-through audit reads needs, not closes; a sample of closes is REVIVE-OR-DROP. | `rm-close-check.timer`; `design/specs/2026-11-23-close-check/boundary.md` |
| AU-2 re-check each verdict that sets blocking evidence aside | A rule, not a re-check: a repaired check counts only when it is seen to fail and pass, and one fresh reader reads a fix. | `CLAUDE.md` §Touching code has a cost |
| AU-3 a repeat error becomes an enforced rule | The findings judge files `Rule candidate:` items for the Conductor, on Fridays. The run that sees a defect fixes it. A program that counts repeats over lessons: REVIVE-OR-DROP. | `Utils/findings_judge_friday.md`; `rm-findings-judge.timer` enabled |
| AU-4 scheduled adversarial reviews that he released | Nobody. GPT and Codex reviews of pipeline code stay stopped. | `CLAUDE.md` §Code is clean |
| AU-5 spot check of the daily digest | The owner only: REVIVE-OR-DROP. | `delegated_digest.py` builds it, and no reader checks it |
| AU-6 instrument trust | A rule for whoever counts. | `facts/instrument_traps.md` |
| AU-7 read codebase health | The page is made each night. Nobody reads it on a schedule: REVIVE-OR-DROP. | `rm-codebase-health.timer` enabled |
| AU-8 re-check the v3-against-v2 verdict | Dead: `v3_vs_v2.py` no longer exists. `Utils/v3_vs_v2_rules.json` is a leftover. | `ls src/RimMandrake/Utils` |
| weekly sample of the findings fold's merges and retire decisions | Nobody: REVIVE-OR-DROP. | `dispatcher_schedule.json` `findings_fold` named the Auditor |
| token talk in the reports of token-blind roles (the check that Operations owns) | The check measures nothing: the two roles that it listed are gone. Point it at the Designer, or delete it: REVIVE-OR-DROP. | `ops_watch_rules.json` `token_talk.roles` is `[]` |

## Retired names that are still in use (for the Conductor)

- `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE` is the parent item where Operations and the Conductor post `OPS PROPOSAL`,
  `OPS DECISION` and `QUESTION FOR OPERATIONS` notes. Its ledger state is already `dropped`. A rename touches the
  Conductor's `ledger_item` and the Operations `on_alarm` text in `dispatcher_schedule.json`, the role files
  `conductor.md` and `operations.md`, the goals file head, `canon.yml`, and the tests that name it. Its name says
  "eight chairs".
- `audits.py`, `audits.schema.json` and `audits.jsonl` stay: `contracts/` replays them as one of six record families.
- `stage_dispute.py` and `stage_dispute.json` are the retired Arbiter's loop. Nothing starts them.
- `concept_tree.py` keeps the leaf value `setter_sweep` and an error text that names the Setter. No code reads
  `binding.json`.
- The priority list (`infrastructure/state/priority_list.json`) orders `rimflow next` only. Its three entries are closed,
  so it orders nothing. Only the Conductor writes it now. The alarms that watched its age are retired.
