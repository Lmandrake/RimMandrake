# Duties of the retired v3 roles: who does each one now (2026-11-23)

The owner, 2026-11-23: *"Those are old v3 roles we retired! V3 and relentless was supposed to be retired. Get those out if active rules. The codex versions of modern roles though are valuable for when we need to burn their tokens instead."*

The Producer and the Auditor are deleted. The Arbiter, the Setter and the Innovator were retired before them. The table
takes each duty of `design/RimMandrake/role_responsibilities_2026-10-26.md` Part 4. Item:
`RIMMANDRAKE_REMOVE_RETIRED_V3_ROLES_FROM_ACTIVE_RULES_STILL_LISTED`. A row that reads DROPPED or REVIVED names a duty that
nothing did on 2026-11-23, and the ruling of 2026-11-25 on it. Nobody is assigned here.

## Producer

| duty | who or what does it now | evidence |
|---|---|---|
| P-1 goals into a daily list, a weekly plan and tickets; focus WIP cap | The Conductor orders its lane from `CONDUCTOR_GOALS.md`. The mod pipeline takes each mod's next act, and the List Pipeline works the list. Nobody writes a daily list or a weekly plan. The WIP cap holds no window. | `roles/conductor.md` §Goals down; `maturation_dispatch.py`; `rm-list-dispatch.timer` enabled; `focus_cap.seats` is `[]` |
| P-2 critical path for each focus mod | The mod's own folder: version, bars, gaps, stage. | `CLAUDE.md` §Mods keep their own state |
| P-3 named scenarios before a build | The Designer's tree and scenes, for a mod. The filer's acceptance test, for a ticket. | `roles/designer_write.md`; `~/.claude/CLAUDE.md` (a ticket is filed with its acceptance test) |
| P-4 replan on a failed plan step or a forecast miss | Operations files one item for the Conductor, and the Conductor decides the cut. (Three `REPLAN REQUEST` notes of 2026-11-18 to 11-20 were read by nobody: `RIMMANDRAKE_ROUTE_REPLAN_REQUESTS_TO_CONDUCTOR_PRODUCER_OFF`.) The automatic run on a failed plan step: DROPPED (ruling of 2026-11-25). | `roles/operations.md` §The economy pass; `role_launch.py` event runs deleted |
| P-5 weekly backlog hygiene (blocked and stale items) | The Conductor sweeps after a major system event. The List Pipeline closes and escalates list items. The weekly run of `queue_staleness_review.py`: REVIVED as an age line in the List Pipeline (ruling of 2026-11-25; the tool is already gone) (no unit and no role names it). | `roles/conductor.md` §After a major system event; `git grep queue_staleness_review` |
| P-6 what the test lane runs | A program: `wired_mods.json`, rotated. The variable `TESTQ_FILL_MODS` still overrides. | `Utils/testq/coverage.py` |
| P-7 bar coverage; test budget for each mod | The coverage judge. The budget for each mod: nobody, and a stage ceiling takes its place. | `rimflow/coverage_judge.py`; `maturation_dispatch.py releases` |
| P-8 order finish, strengthen, explore; a stopping point for each item | The pipeline's stages and the two tests of §Touching code has a cost. | `standing_rulings.md` |
| P-9 read the idea bank `design/V2_DREAMS.md` | Any seat may write to it. Nobody reads it: DROPPED; the file stays (ruling of 2026-11-25). | `CHARTER.md` (the only live rule line that names it) |

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
| AU-1 sample closed items and passes | The mechanical check of every close: `close_check.py`, daily, no AI (a close whose commit is not on main reopens its item). The sample by a reader: the daily findings judge (step 3, `regrade.py`, at most 3 closed items a day) sampled closes from 2026-11-06 until its own stop rule ended the sample ("18 days since the first regrade and nothing held up: stopped, as the owner asked"). The weekly follow-through audit reads needs. To start the regrade again is DROPPED (ruling of 2026-11-25). | `regrade.py report` (exit 3, 2026-11-24); `findings_judge_prompt.md` step 3; `rm-close-check.timer`; `design/specs/2026-11-23-close-check/boundary.md` |
| AU-2 re-check each verdict that sets blocking evidence aside | A rule, not a re-check: a repaired check counts only when it is seen to fail and pass, and one fresh reader reads a fix. | `CLAUDE.md` §Touching code has a cost |
| AU-3 a repeat error becomes an enforced rule | The findings judge files `Rule candidate:` items for the Conductor, on Fridays. The run that sees a defect fixes it. A program that counts repeats over lessons: DROPPED (ruling of 2026-11-25). | `Utils/findings_judge_friday.md`; `rm-findings-judge.timer` enabled |
| AU-4 scheduled adversarial reviews that he released | Nobody. GPT and Codex reviews of pipeline code stay stopped. | `CLAUDE.md` §Code is clean |
| AU-5 spot check of the daily digest | The owner only: DROPPED (ruling of 2026-11-25). | `delegated_digest.py` builds it, and no reader checks it |
| AU-6 instrument trust | A rule for whoever counts. | `facts/instrument_traps.md` |
| AU-7 read codebase health | Dead: the page's timer and publisher are retired, and `rm-codebase-now.timer` makes the page that replaced it. No scheduled read is owed on either page. | `live_retired.txt`; `selftest_retired_era_gone.py` RETIRED_UNITS |
| AU-8 re-check the v3-against-v2 verdict | Dead: `v3_vs_v2.py` no longer exists. `Utils/v3_vs_v2_rules.json` is the default `--rules` file of `sim/process_sim.py backtest`. | `git grep v3_vs_v2_rules` |
| weekly sample of the findings fold's merges and retire decisions | Nobody: DROPPED (ruling of 2026-11-25). | `dispatcher_schedule.json` `findings_fold` named the Auditor |
| token talk in the reports of token-blind roles (the check that Operations owns) | The check measures nothing: the two roles that it listed are gone. Point it at the Designer, or delete it: DROPPED; the dead measure is removed when a run next changes `ops_watch.py`, and `terms` stays (ruling of 2026-11-25). | `ops_watch_rules.json` `token_talk.roles` is `[]` |

## Retired names that are still in use (for the Conductor)

- `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE` is no longer the notes item: the roles write on
  `RIMMANDRAKE_KEEP_ROLE_NOTES_ON_ONE_LIVE_ITEM` (2026-11-23), and `selftest_retired_era_gone.py` refuses the old name on
  a live instruction line. The old name stays only in code comments and test data.
- `audits.py`, `audits.schema.json` and `audits.jsonl` stay: `contracts/` replays them as one of six record families.
- `stage_dispute.py` and `stage_dispute.json` are the retired Arbiter's loop. Nothing imports them, and the
  config reads `shadow` (`git grep stage_dispute`, 2026-11-24).
- `concept_tree.py` keeps the leaf value `setter_sweep` and an error text that names the Setter. No code reads
  `binding.json`.
- The priority list and its tool were deleted 2026-11-23 (retire census): the order of work comes from the Maturation
  Pipeline, the List Pipeline and `CONDUCTOR_GOALS.md`.

## Evidence and the ruling for each open decision (2026-11-24 evidence; ruled 2026-11-25)

Item: `RIMMANDRAKE_DECIDE_RETIRED_ROLE_DUTIES_NOBODY_DOES_NOW`. Each recommendation below is taken as the ruling, by
delegation of the Conductor's brief of 2026-11-25 (no evidence against any of them was found). Two facts moved since the
evidence was read: `stage_dispute.py` and `stage_dispute.json` are already gone (`git grep stage_dispute` finds no tracked
code), and `queue_staleness_review.py` and its selftest are already gone. The token-talk measure is dead code that harms
nothing, so it is removed only when a run next changes `ops_watch.py` (§Touching code has a cost).

| open decision | evidence, measured 2026-11-24 unless tagged | recommendation and its act |
|---|---|---|
| P-4 automatic replan run on a failed plan step | There is no plan to replan (no daily list, no plan list). Operations files one item for the Conductor when a goal's work does not fit a date (`operations.md` §forecast against the goals). | DROP. No act. |
| P-5 weekly run of `queue_staleness_review.py` | Its run reads 301 doing or blocked items: 30 blocked past 3 days, 0 doing past 7 days, 18 of them with a `needs` tag that its window already met (up to 21.6 days idle). `list_dispatch.py` reads `blocked` as a reason to wait, and that file holds no age rule for a block (other files were not searched). Many of the 30 belong to held biome mods [guess ~60%]. | REVIVE, as an age line inside the List Pipeline (a block idle past 3 days whose `needs` window has opened since is due for Shape), not as a weekly page. Then delete the tool and its selftest. This is the one duty here with a measured gap. |
| P-9 a reader of `design/V2_DREAMS.md` | An idea for a mod's next version is already a ticket (`CHARTER.md`). The file is the overflow for ideas that bind nobody. | DROP the reading duty; keep the file. No act. |
| AU-1 the regrade of closes | It sampled from 2026-11-06 to 2026-11-19 and ended by its own rule with nothing held up. `close_check.py` checks every close daily. | DROP. No act; step 3 of the judge prompt skips itself. |
| AU-3 a program that counts repeat lessons | `lessons.py add` refuses a near-twin and offers `--merge`. `findings_fold.py` groups each failure under one signature and lists DECIDED-and-failed-again each day. | DROP. No act. |
| AU-5 a spot check of the daily digest | A program builds the digest, three selftests cover the program, and the Conductor delivers it. No wrong digest is on record in this run's reading [guess ~70%: the ledger was not searched whole]. | DROP. No act. |
| the sample of the findings fold's merge and retire decisions | `decisions.jsonl` holds 159 decisions in 2026-11: 67 merge, 42 route, 30 work, 19 retire, 1 memory. A wrong merge or retire comes back by itself under DECIDED-and-failed-again, which the judge must decide again each day. | DROP. No act. |
| the token-talk check of role reports | `token_talk.roles` and `.seats` are both `[]`. The word list `token_talk.terms` is live: `dispatcher.py` and `ops_watch.py` use it to withhold lines from the blind digest. | DROP the measure (`c_tokentalk`, `tt_texts`, `tt_point`, `tt_groups`, `tt_retired`, its tests, §Drift check of `operations.md`). KEEP `terms` and `tt_regex`. |
| `audits.py`, its schema and fixture | `contracts/` replays them as a record family. | KEEP. No act. |
| `stage_dispute.py`, `stage_dispute.json` | Nothing imports the module. | DELETE both, with their line in `failure_counter_list.json`. |
| `setter_sweep` in `concept_tree.py` | A value that the schema accepts, with a selftest. No tracked JSON holds the value (`git grep`). | KEEP the value. No failure is on record (§Touching code has a cost). |
| `v3_vs_v2_rules.json` | `process_sim.py backtest` reads it by default. | KEEP with the simulator. No act. |
