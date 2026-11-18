# Retired eras: what was removed, where it lived, what stays and why (2026-11-18)

Item `RIMMANDRAKE_RETIRE_OLD_PIPELINE_REMNANTS_TEN_SLIPPED_INTO_LANES`. The owner, 2026-11-18 about 1:15 PM PST:

> "That is upsetting. At this time, I want you to immediately dispatch a subagent worker who MOVES OUT OF THE WAY, ARCHIVES, RETIRES anything from the previous pipelines and their ticket/queue items that are specific to them, period. Nothing of that era should remain. No more collisions or confusion. I do not want to lose the wisdom, just remove all future confusion please. If it is just basically git provenance, then go ahead and delete them and we can always reconstruct from Git. It may be that that is the right answer, especially on very old system components. Advise and execute please."

What set it off: ten tickets filed in the Foundry / Relentless / rimflow v3 era were launched among Maturation Pipeline
tickets, because nothing marked old-era material as old.

**The current system** (never touched here): the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md`),
the Conductor, Dispatcher, Operations and Designer roles, rimflow the ledger, testq, the control store, and everything
they execute.

**The retired eras**: the Relentless Pipeline, the Artisan (Ralph) loops and the Whittle loops (owner 2026-11-13,
`design/RimMandrake/retired_loops_2026-11-13.md`); the FOUNDRY seat and its build queue (owner by card 2026-11-02);
RimPulse (owner 2026-11-03); Fleet Watch; the parts of rimflow v3 that never went live or were replaced.

## How to get anything back

Git is the archive. Each row below names the last commit that still held the thing:

```
git show <sha>:<path>                       # one file
git archive <sha> <dir> | tar -x -C <dest>  # a whole folder
git log --oneline -- <path>                 # its history
```

A wisdom-bearing file was read before it went: any lesson it held that was not already in
`infrastructure/state/lessons/` was filed there first, worded for today's reader.

## The guard that keeps it gone

`src/RimMandrake/rimflow/selftest_retired_era_gone.py`, a whole-tree check at `./publish`
(`src/RimMandrake/Utils/publish_tree_checks.json`). It fails on any tracked path, or any unmasked systemd user unit,
whose name belongs to a retired era and is not allowed by a row of the two tables "Phase 2: renames" and "Kept on
purpose" below. An allow row that matches nothing fails too. To keep something, add a row with its reason; to remove
something, delete it and add a "Removed" row.

## Removed

| what it was | path | era | why it is gone | last sha that held it |
|---|---|---|---|---|
| the Whittle loops' work folder: STATEMENT/PROMPT/JUDGE/OBSERVER, FINDINGS, the Codex live-driver report, the STOP switch and every round's evidence (15,365 files) | `whittle/` | Whittle | loops retired 2026-11-13; nothing current reads it (live items that cite `whittle/<run>/evidence/...` read it with `git show`) | `f2ce40bac8` |
| the Claude Whittle worker kit: loop.sh, wc.py, gate.py, install/setup, lane briefs, `whittle-claude@.service` | `infrastructure/whittle_claude/` | Whittle | its unit is masked and its runs ended 2026-11-13 | `f2ce40bac8` |
| the Stop hook that held a Whittle session open, and its `.claude/settings.json` Stop entry | `.claude/hooks/whittle_stop.py` | Whittle | armed only by `WHITTLE=1`, which nothing sets | `f2ce40bac8` |
| the Whittle status page and its selftests | `src/RimMandrake/Utils/whittle_now.py`, `selftest_whittle_now.py`, `selftest_whittle_claude_{admission,gate,pick}.py` | Whittle | its timer is masked; the claude-worker selftests tested `infrastructure/whittle_claude/` | `f2ce40bac8` |
| the repo copies of the status page's units | `src/RimMandrake/Utils/systemd/rm-whittle-now.{service,timer}` | Whittle | masked on Archmagi since 2026-11-13; the mask stays | `f2ce40bac8` |
| the Whittle Codex-runner note | `src/RimMandrake/rimflow/roles/whittle.md` | Whittle | described a retired runner; `runner_options.md` keeps the live-driver findings | `f2ce40bac8` |
| the mod list saved before the Whittle trial | `infrastructure/state/modlists/ModsConfig.BEFORE_WHITTLE_TRIAL_20261110.xml` | Whittle | a mod-list backup; the owner's mod list is never restored (owner 2026-10-24) | `f2ce40bac8` |
| the Artisan (Ralph) loop kit: PROMPT, RATCHET, LOOK, QUESTIONS, PROGRESS, loop.sh, game_gate.py, tally.py, handoff notes | `ralph/` | Artisan | loops retired 2026-11-13; nothing current reads it | `108d42482` |
| the Artisan status page, its selftest and its unit copies | `src/RimMandrake/Utils/artisan_now.py`, `selftest_artisan_now.py`, `src/RimMandrake/Utils/systemd/rm-artisan-now.{service,timer}` | Artisan | its timer is masked on Archmagi (the mask stays) | `108d42482` |
| the Artisan Codex-runner note | `src/RimMandrake/rimflow/roles/artisan.md` | Artisan | described a retired runner | `108d42482` |
| the RimWorld layer of the Artisan skills, and its `.claude/skills` link | `skills/rimworld-artisan/`, `.claude/skills/rimworld-artisan` | Artisan | operated retired loops (rm-ralph units, ARTISAN_NOW) | `108d42482` |
| the Relentless skill (SKILL.md and a 309-line traps file), and its `.claude/skills` link | `skills/relentless/`, `.claude/skills/relentless` | Relentless | operated the retired tick; five traps still true today were filed as lessons first (2026-11-18, BENCH) | `108d42482` |
| two by-hand Relentless readers | `src/RimMandrake/rimflow/relentless_head_age.py`, `relentless_tickp95.py` | Relentless | nothing but the deleted skill and `entrypoint_inventory.py` named them; now in its RETIRED list | `108d42482` |
| the Archmagi Artisan-only capacity design | `design/RimMandrake/archmagi_artisan_only_2026-11-07.md` | Artisan | a plan for a retired loop; its machine numbers were dated estimates | `108d42482` |
| the Artisan judgment seed (owner's ask of 2026-11-08) | `design/RimMandrake/artisan_judgment_seed_2026-11-08.md` | Artisan | his still-binding words moved to `standing_rulings.md` §Aim at a playable version | `108d42482` |
| the Ralph loop design | `design/RimMandrake/ralph_loop_design_2026-10-29.md` | Artisan | design of a retired loop; `run_selftests.py --quick` no longer cites it | `108d42482` |
| two Lodestar tickets for retired machinery | `tickets/RIMMASTER_AUTOTUNE_ARTISAN_LOOPS_WHEN_TOKENS_RESET_WEDNESDAY.md`, `tickets/RIMMASTER_RUN_V3_AUTOTUNER_AS_SELF_TUNING_TESTBED.md` | Artisan, rimflow v3 | the first was open for a retired loop, the second already dropped | `108d42482` |
| 19 Relentless design, research, review and forensics docs (agent design and research, TRUST and counting rules, daily release, failure catalog and its GPT read, fixed waits, incident forensics, live mode, owner design, pool why, progress page and mock, selfbuild, tick slow step, verdict identity, Relentless vs FOUNDRY) | `design/RimMandrake/relentless_{agent_design_2026-11-01,agent_gpt_review_2026-11-01,agent_research_2026-11-01,TRUST_2026-11-01,counting_rules_2026-11-01,daily_release_2026-11-06,failure_catalog_2026-11-05,failure_review_gpt_2026-11-05.gpt_read,fixed_waits_2026-11-06,incident_forensics_2026-11-02,live_mode_2026-11-02,owner_design_2026-10-31,pool_why_2026-11-05,progress_page_2026-11-03,progress_page_mock_2026-11-02,selfbuild_2026-11-06,tick_slow_step_2026-11-03,verdict_identity_design_2026-11-02,vs_foundry_2026-11-02}.*` | Relentless | designs of a retired system; no current code, role or policy cites them (only Phase 2 relentless code comments, dated docs and transcripts). The failure catalog's nine cross-cutting roots were filed first as a lesson (2026-11-18, BENCH, nine roots) | `f5089a41de` |
| 12 rimflow v3 design-round docs that never went live or were replaced (build closeout, two collapse docs, three explainer pictures, field evidence, GPT risk review, two minimal designs, poster, system map, workflow as built) | `design/RimMandrake/rimflow_v3_{build_closeout_2026-10-31,collapse_compare_2026-10-29,collapse_settlement_2026-10-31,explainer_code,explainer_flows,explainer_starts,field_evidence_2026-10-27,gpt_risk_review_2026-10-29,minimal_gpt_2026-10-29,minimal_opus_2026-10-29,poster,system_map,workflow_as_built_2026-10-29}.*` | rimflow v3 | nothing current cites them; the v3 docs that live code still cites are in Phase 2 below | `f5089a41de` |
| the process model v2/v3 design | `design/RimMandrake/process_model_v2_v3_design_2026-10-29.md` | rimflow v3 | cited only by dated docs | `f5089a41de` |
| five RimPulse design and review docs | `design/RimMandrake/rimpulse_{gpt_review_2026-10-22,intent_2026-10-22,make_it_great_2026-10-25,redesign_2026-10-23.gpt_review,relentless_prototype_2026-11-02}.md` | RimPulse | RimPulse retired 2026-11-03; nothing current cites them | `f5089a41de` |
| the FOUNDRY management analysis | `design/RimMandrake/foundry_management_analysis_2026-11-01.md` | FOUNDRY | the seat is retired; `bridge_hours.py` now cites it by sha | `f5089a41de` |
| the Relentless Codex-runner note | `src/RimMandrake/rimflow/roles/relentless.md` | Relentless | described a runner option of the retired tick | `f5089a41de` |

## Phase 2: renames

Live code with an old name: current machinery runs or reads it, so it was **not** renamed or moved in this run (about
ten builders were running from `/home/mandrake/rm/relentless/clones` and import these modules). The Conductor
schedules phase 2 once those builders are done. Each row: the path (an allow row for the guard), who uses it (blast
radius), and the proposed new name.

| path | who uses it (blast radius) | proposed new name |
|---|---|---|
| `src/RimMandrake/rimflow/relentless.py` | 8,562 lines. Imported by `detached_helper.py` (Store, Effects, rules, unit_state, run_tokens, read_result, role_scope, _stop_call), `cli.py` (guard, rules), `role_launch.py` (kick, set_status, status, unit_name, Store), `maturation_autonomy.py` (pilot_model, CHAIN_MAX_PER_DAY, day_of), `evidence.py` (Store, harvest_receipts, marker_receipt, verdict), `circling.py`, `validator_replay.py`, `scratch_clone.py` and about 40 selftests. Its store lives at `/home/mandrake/rm/relentless/store`; the clone pool at `/home/mandrake/rm/relentless/clones`. The tick, leasing and Builder/Judge stages inside it are dead (rm-relentless.timer masked 2026-11-13). | split: `rimflow/run_store.py` (Store, Effects, rules, receipts), `rimflow/run_units.py` (unit_state, kick, unit_name, stop), the pool under a neutral path (`/home/mandrake/rm/pool/`); delete the tick and every function only it reaches, with their selftests |
| `src/RimMandrake/rimflow/relentless_*.py` | 54 modules, all reachable by import from `relentless.py` (measured by an AST import walk from every non-era file). Most serve only the dead tick (stage, wake, wall, exam, seeds, dispute, live_round...). | delete each one the split modules above do not import; rename the rest beside them |
| `src/RimMandrake/rimflow/relentless_*.json` | config read by `relentless.py` and its modules (`relentless_rules.json` is read by `cli.py guard`, `detached_helper.py`, `circling.py`) | move the keys the split modules still read into `rimflow/run_rules.json`; delete the rest |
| `src/RimMandrake/rimflow/selftest_relentless*.py` | about 130 selftests of the code above; none is in `pipeline_tests.json` or `publish_tree_checks.json` | each goes with the code it tests: deleted with dead code, renamed with live code |
| `src/RimMandrake/rimflow/selftest_bridge_seat_relentless.py` | tests the bridge seat RELENTLESS that `model.bridge_identity` still accepts for old `bridge` events | goes with the split |
| `src/RimMandrake/rimflow/testdata/relentless_packet_handscored.json` | fixture of `selftest_relentless_packet.py` | goes with its selftest |
| `src/RimMandrake/Utils/testdata/relentless_jam_2026-11-01.jsonl` | fixture of `selftest_relentless_watch.py` (ops_watch's relentless reader) | goes with ops_watch's relentless points |
| `src/RimMandrake/Utils/selftest_fixtures/relentless_checker_deaths_2026-11-03.jsonl` | fixture read by an ops_watch selftest | goes with ops_watch's relentless points |
| `src/RimMandrake/Utils/selftest_relentless_watch.py` | tests `ops_watch.c_relentless`, which still runs in every ops_watch pass (it judges the relentless points as retired) | delete with `ops_watch`'s relentless points |
| `src/RimMandrake/Utils/selftest_relentless_game_hold_agrees.py` | tests `ops_watch.rl_game_hold_idle` against `relentless_game` | delete with `ops_watch`'s relentless points |
| `src/RimMandrake/Utils/selftest_ops_watch_relentless_retired.py` | tests that ops_watch reads the relentless points as retired, not failing | delete with `ops_watch`'s relentless points |
| `src/RimMandrake/Utils/pulse/**` | RimPulse's dashboard is retired (owner 2026-11-03), but its package is live: `pulse_core` (ops_watch, deadman_check, known_reds), `phone_push` (switching_plan, deadman_check, login_watch), `failreport` (winbuild, testq steward), `streams` and `testing_metrics` (rm-streams-collect.timer, enabled), `pulse.py report` / `update` (findings_judge.sh, rm-deploy-update.service, rm-agent-improve.service, rm-selftests-nightly.service). Units run it from the deploy checkout `/home/mandrake/rm/pulse-deploy` (65 tracked files name that path). | `src/RimMandrake/Utils/ops_core/` (pulse_core, phone_push, failreport, streams, testing_metrics, usage, the `report`/`update` verbs); delete the dashboard pages (mission_page, brief, agents_timeline, time_ledger and its replay fixtures) once nothing imports them; rename the deploy checkout |
| `pulse` | the repo-root launcher of `pulse.py` (`./pulse back`, `report`, `update`) | goes with the package rename |
| `src/RimMandrake/Utils/sim/ralph_loop_sim.py` | imported by `sim/fanout_sim.py` and `sim/testpilot_sim.py` (with their selftests) | `sim/loop_sim.py` |
| `src/RimMandrake/Utils/sim/selftest_ralph_loop_sim.py` | its selftest | goes with it |
| `src/RimMandrake/Utils/sim/rimflow_v3_sim.py` | imported by `sim/fanout_sim.py`, `sim/ralph_loop_sim.py`, `sim/testpilot_sim.py` and `rimflow/selftest_dispatcher.py` | `sim/process_sim.py` |
| `src/RimMandrake/Utils/sim/rimflow_v3_sim_params.json` | its parameters | goes with it |
| `src/RimMandrake/Utils/sim/selftest_rimflow_v3_sim.py` | its selftest | goes with it |
| `design/RimMandrake/relentless_tree_schema_2026-11-01.md` | the concept-tree schema in use today: cited by `rimflow/concept_tree.py`, `rimflow/roles/designer.md` and `design/RimMandrake/maturation_pipeline.md` | `design/RimMandrake/concept_tree_schema.md`, its four citations moved in the same commit |
| `infrastructure/agents/FOUNDRY.md` | the session identity hook injects `infrastructure/agents/<SEAT>.md` into a window recorded as `AGENT FOUNDRY` (`set_agent_window.sh` still accepts FOUNDRY; `selftest_conductor_identity.py` checks the injection). It now says only that the seat is retired. | delete with FOUNDRY in `set_agent_window.sh` SEATS and the hook test |
| `src/RimMandrake/Utils/systemd/rm-relentless*` | repo copies of the masked Relentless units, read as fixtures by `selftest_relentless_release.py` and `selftest_relentless_wake.py` (Phase 2 tests). The host units stay masked (`retired_loops_check.py` checks it every 15 min). | delete with those selftests |
| `src/RimMandrake/rimflow/prove_relentless_s03_compare.py` | read by `selftest_relentless_seed_compare.py` | delete with its selftest |
| `design/RimMandrake/relentless_improvement_loop_2026-11-03.md` | cited by `Utils/findings_judge_prompt.md` (the live findings judge), `rimflow/concept_tree.py`, `rimflow/evidence_metrics.py`, `rimflow/jam_classes.json` | fold what the findings judge still needs into its prompt, then delete |
| `design/RimMandrake/relentless_recovery_plan_2026-11-05.md` | cited by `standing_rulings.md` (§3 "pause only what it touches"), `selftest_alarm_closed_reopen.py`, `selftest_ops_health_stamp.py` | move §3 into `standing_rulings.md`, then delete |
| `design/RimMandrake/rimflow_v3_2026-10-26.md` | design of record of the live Dispatcher: cited by `dispatcher.py`, `dispatcher_schedule.json`, `slot_rules.json`, `selftest_slot_allocator_v3.py` | `design/RimMandrake/dispatcher_design_2026-10-26.md` |
| `design/RimMandrake/rimflow_v3_arbiter_tiers_2026-10-27.md` | cited by `Utils/close_evidence.py` | `dispatcher_arbiter_tiers_2026-10-27.md` |
| `design/RimMandrake/rimflow_v3_flows.svg` | linked from `roles/conductor.md` and `roles/producer.md` | `dispatcher_flows.svg` |
| `design/RimMandrake/rimflow_v3_golive_wave1.md` | cited by `audits.py`, `dispatcher.py`, `dispatcher_schedule.json`, `seat_restart.py`, `selftest_dispatcher.py` | `dispatcher_golive_wave1.md` |
| `design/RimMandrake/rimflow_v3_responsibilities_2026-10-26.md` | cited by `delegation_policy.md` and role code | `role_responsibilities_2026-10-26.md` |
| `design/RimMandrake/rimflow_v3_risk_response_2026-10-29.md` | cited by `testq/steward.py` and by open items (`ROLE_HEADERS_RETIRE_ENABLED_PROSE` and others) | `dispatcher_risk_response_2026-10-29.md` |
| `design/RimMandrake/rimflow_v3_audit_remeasure_2026-10-31.md` | cited by open items (`ROLE_HEADERS_RETIRE_ENABLED_PROSE`, `ROLE_DUTIES_FIX_CARRY_MISSED_SLOTS`, `LESSONS_RETIRE_INBOX_AS_QUEUE`) | `dispatcher_audit_remeasure_2026-10-31.md` |
| `design/RimMandrake/rimflow_v3_roles.html` | cited by `dispatcher_schedule.json` | `dispatcher_roles.html` |
| `design/RimMandrake/rimflow_v3_sim_findings_2026-10-27.md` | cited by `sim/rimflow_v3_sim.py`, `roles/auditor.md`, `roles/conductor.md` | goes with `sim/process_sim.py` |
| `design/RimMandrake/rimflow_v3_trial_night_2026-10-28.md` | cited by `dispatcher_schedule.json`, `selftest_dispatcher.py` | `dispatcher_trial_night_2026-10-28.md` |
| `design/RimMandrake/rimpulse_redesign_2026-10-23.md` | cited by `Utils/pulse/brief.py` and the docs map `rimflow/docs/README.md` | goes with the pulse package rename |

## Kept on purpose

| path | why it stays |
|---|---|
| `infrastructure/state/items/RIMMANDRAKE_LAND_RALPH_FLOWWORKS_PIT_FEATURES.md` | mod content, out of scope: 36 FlowWorks pit-feature commits on `origin/ralph/flowworks` are not on main; the ticket is to land them. The name keeps "RALPH" because the branch does. |

## Outside this repo

Nothing outside the repo was changed by this item. What should go, for the Conductor:

## UNMEASURED

What this run could not settle, and what would settle it:

## Tickets
