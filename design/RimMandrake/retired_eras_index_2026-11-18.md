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
| the Relentless Pipeline naming guard (owner 2026-11-03: the system is "the Relentless Pipeline") | `src/RimMandrake/rimflow/selftest_relentless_pipeline_naming.py` | Relentless | it required live docs to name a retired system and read deleted docs | `ba609865bd` |

## Phase 2: renames

Live code with an old name: current machinery runs or reads it, so it was **not** renamed or moved in this run (about
ten builders were running from `/home/mandrake/rm/relentless/clones` and import these modules). The Conductor
schedules phase 2 once those builders are done. Each row: the path (an allow row for the guard), who uses it (blast
radius), and the proposed new name.

| path | who uses it (blast radius) | proposed new name |
|---|---|---|
| `src/RimMandrake/rimflow/relentless.py` | 8,562 lines. Imported by `detached_helper.py` (Store, Effects, rules, unit_state, run_tokens, read_result, role_scope, _stop_call), `cli.py` (guard, rules), `role_launch.py` (kick, set_status, status, unit_name, Store), `maturation_autonomy.py` (pilot_model, CHAIN_MAX_PER_DAY, day_of), `evidence.py` (Store, harvest_receipts, marker_receipt, verdict), `circling.py`, `validator_replay.py`, `scratch_clone.py` and about 40 selftests. Its store lives at `/home/mandrake/rm/relentless/store`; the clone pool at `/home/mandrake/rm/relentless/clones`. The tick, leasing and Builder/Judge stages inside it are dead (rm-relentless.timer masked 2026-11-13). | split: `rimflow/run_store.py` (Store, Effects, rules, receipts), `rimflow/run_units.py` (unit_state, kick, unit_name, stop), the pool under a neutral path (`/home/mandrake/rm/pool/`); delete the tick and every function only it reaches, with their selftests |
| `src/RimMandrake/rimflow/relentless_*.py` | 42 modules, all reachable by import from `relentless.py`; at function level most are dead (see "Phase 2: measured reach" below). Most serve only the dead tick (stage, wake, wall, exam, seeds, dispute, live_round...). | delete each one the split modules above do not import; rename the rest beside them |
| `src/RimMandrake/rimflow/relentless_*.json` | config read by `relentless.py` and its modules (`relentless_rules.json` is read by `cli.py guard`, `detached_helper.py`, `circling.py`) | move the keys the split modules still read into `rimflow/run_rules.json`; delete the rest |
| `src/RimMandrake/rimflow/selftest_relentless*.py` | 117 selftests of the code above (119 tracked `selftest_relentless*` files with the two in `Utils/`); none is in `pipeline_tests.json` or `publish_tree_checks.json`. `selftest_relentless.py` case `real` (the pool is every eligible item) is red on the real ledger; its ticket `RIMMANDRAKE_POOL_ELIGIBLE_FINISH_ITEMS_LEFT_OUT` was dropped because the pool selection serves only the retired tick | each goes with the code it tests: deleted with dead code, renamed with live code |
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
| `src/RimMandrake/rimflow/selftest_foundry_literals.py` | a live guard: no code routes work to the FOUNDRY seat by a string literal (`FOUNDRY_LITERALS_EXCISE_FROM_CODE`) | `selftest_retired_seat_literals.py` |

Old names inside live files (not paths, so the guard does not see them), for the same phase:

- `src/RimMandrake/Utils/bridge_holder.py` `CODEX_SEATS`: the `CLAUDE_*` seats were the Claude Whittle workers; their
  ledger shards stay as history, so the names must keep replaying.
- `./bridge foundry` and `set_agent_window.sh` still accept FOUNDRY; `model.bridge_identity` still accepts RELENTLESS
  for old `bridge` events; `cli.py` `RETIRED_SEATS` maps FOUNDRY to the Conductor's key (keep that mapping: old
  events name it).
- `ops_watch.py` still reads the Relentless points (`c_relentless`, `rl_game_hold_idle`) and judges them retired;
  `slot_allocator` and `slot_rules.json` keep a FOUNDRY seat key (`SLOTS_RENAME_FOUNDRY_KEY_RELENTLESS_READS_IT`).
- `src/RimMandrake/rimflow/live_retired.txt` and `src/RimMandrake/Utils/retired_loops_check.py` name the retired units on
  purpose: they keep them masked. Keep both.
- `skills/using-rimflow/SKILL.md` uses FOUNDRY in two examples (`reassign --to FOUNDRY`, `next --seat FOUNDRY`); skills
  are edited in curation sessions, so it is listed here, not edited.

## Kept on purpose

| path | why it stays |
|---|---|
| `infrastructure/state/items/RIMMANDRAKE_LAND_RALPH_FLOWWORKS_PIT_FEATURES.md` | mod content, out of scope: 36 FlowWorks pit-feature commits on `origin/ralph/flowworks` are not on main; the ticket is to land them. The name keeps "RALPH" because the branch does. |

## Outside this repo

Nothing outside the repo was changed by this item. What should go, for the Conductor:

- `~/.claude/skills/` links into MandrakeWorkflows: `artisan`, `artisan-head`, `artisan-judge`, `relentless-pipeline`,
  `whittle`. Done 2026-11-18 (below): the links stay, and RimMandrake sessions no longer see the skills.
- Masked user units on Archmagi (`systemctl --user list-unit-files` shows them `masked`): `rm-relentless*`,
  `rm-artisan-now.*`, `rm-whittle-now.*`, `whittle-claude@.service`, `rm-pulse.service`. Keep the masks:
  `retired_loops_check.py` (deadman, every 15 min) alarms if one is unmasked. SteveDesktop's `whittle-claude@` mask
  likewise (not checked from here).
- On disk, not in git: the Relentless store `/home/mandrake/rm/relentless/store` (read by live code: Phase 2), the clone
  pool `/home/mandrake/rm/relentless/clones` (live), the kept Ralph clone `/home/mandrake/rm/scratch/BENCH/ralph_flowworks`
  (ticket `RIMMANDRAKE_LAND_RALPH_FLOWWORKS_PIT_FEATURES`), `D:\ClaudeWork\rimmandrake\whittle_claude\`,
  `D:\ClaudeWork\rimmandrake\ralph_*`, `D:\ClaudeWork\rimmandrake\relentless_agent\`, and the deploy checkout
  `/home/mandrake/rm/pulse-deploy` (live: units run from it).
- The Conductor's memory files: any that describe Relentless, Artisan, Whittle, FOUNDRY or RimPulse as running. Done
  2026-11-18 (below).

## Outside this repo: done

Item `RIMMANDRAKE_RETURN_LOOP_WISDOM_TO_MANDRAKEWORKFLOWS_SKILLS`, 2026-11-18. The owner, about 2:10 PM PST: "Whittle,
Artisan, and Ralph loops (and relentless workers) were all in MandrakeWorkflows anyway, so a lot of that wisdom can be
shoved back in there for future users."

- **The wisdom went back to MandrakeWorkflows** (commit `37f0e9a`). Each loop's skill now holds a
  `references/first-deployment-record.md`: what this project measured, why it retired the loop, and the lessons the
  skill lacked (`skills/artisan/`, `skills/whittle/`, `skills/relentless-pipeline/`; the nine roots and the generic proof
  traps are in the last). All five SKILL.md files (`artisan`, `artisan-head`, `artisan-judge`, `whittle`,
  `relentless-pipeline`) say plainly that RimMandrake retired them on 2026-11-13 and why; the stale scoreboards
  ("zero sessions", "zero acceptances as of 2026-11-07") were corrected. The skills stay for other projects.
- **Hidden from RimMandrake sessions only.** `.claude/settings.json` sets `skillOverrides` to `"off"` for the five
  skills. The `~/.claude/skills/` links are global and stay, so his other projects still see them; `~/dev/Lodestar/claude/skills.md`
  is unchanged. Tested 2026-11-18 with `claude -p`: from this repo the five read absent (`handoff` present as the
  control); from a folder with no project settings all five read present.
- **The Conductor's memory** (`/home/mandrake/.claude/projects/-home-mandrake-rm-bench/memory/`): twelve files that
  described a retired system as current (or, in the last one, as only paused) were corrected and three `MEMORY.md` index lines fixed. They are
  `artisan-phase-conductor-does-it-question-cards`, `conductor-is-proactive-situation-officer`,
  `live-progress-board-for-long-builds`, `open-markdown-in-typora`, `ask-before-large-autonomous-builds`,
  `review-tiers-and-review-environments`, `owner-modes-bench-belt-afk`, `token-budget-plentiful-test-constantly`,
  `rimflow-redesign-built-validated-leases-2026-10-07`, `gimmesomeslack-flowworks-first`,
  `code-review-check-reachability-first` and `whittle-relentless-stay-off-until-validated`. Every owner preference in
  them was kept; only the retired machinery they pointed at changed. Files that only mention FOUNDRY items as filed
  history were left alone.

## Phase 2: measured reach (2026-11-18, BENCH, item `RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES`)

Instrument: `src/RimMandrake/Utils/era_reach.py` (its selftest plants a repo and is watched to fail on a mutant). It
walks the call graph from every non-era file's real uses (`from relentless_x import a`, `alias.attr`, `getattr(alias,
"a")`) into `relentless.py` and the 42 `relentless_*.py`: a function is a node, a class's methods are nodes reached
only when the class is reached and the method's name is used somewhere reached, a module's import-time statements run
when it is imported, and a parameter named `sup` is `relentless` itself (the tick passes `sys.modules[__name__]`).
What it cannot see: `getattr` on a non-module object, `exec`, string tables; so every cut is followed by an
undefined-name check. Script-path calls are not imports and were grepped by hand: `publish.py` `wake_relentless` and
`Utils/land.sh` run `relentless_wake.py poke` after every landing (it pokes the masked tick: dead in effect), and
`ops_watch.py` runs `relentless.py expedite set` (inside its retired relentless points). No enabled systemd unit names
`relentless` (every `rm-relentless*` and `rm-store-ledger-diff.*` unit is masked).

Function counts (functions plus methods; constants not counted). Columns: reached from **all importers**; from **live
code only**, after setting aside the importers that are themselves Relentless-era tools (below); and the **cut line**:
live code plus every live test (mod proofs in FlowWorks, GimmeSomeSlack, TerminalBiomes, BlueDesert, modcheck, perf
and `Utils/`, and the rimflow tests of live code), the set the split keeps.

| module | all importers | live code only | + live tests (the cut line) | lines kept / all |
|---|---|---|---|---|
| `relentless.py` | 103/388 | 49 | 121 | 1,981 / 7,784 |
| `relentless_account.py` | 0/11 | 0 | 0 | 0 / 134 |
| `relentless_answer.py` | 0/6 | 0 | 0 | 0 / 70 |
| `relentless_attrib.py` | 8/24 | 0 | 8 | 88 / 423 |
| `relentless_binding.py` | 6/12 | 0 | 0 | 0 / 133 |
| `relentless_bindjudge.py` | 0/16 | 0 | 0 | 0 / 194 |
| `relentless_block.py` | 3/16 | 0 | 0 | 0 / 315 |
| `relentless_books_left.py` | 0/12 | 0 | 12 | 140 / 140 |
| `relentless_boxrun.py` | 18/20 | 0 | 0 | 0 / 362 |
| `relentless_breakers.py` | 13/18 | 0 | 11 | 117 / 216 |
| `relentless_broker.py` | 7/35 | 0 | 0 | 0 / 372 |
| `relentless_canary.py` | 0/15 | 0 | 0 | 0 / 154 |
| `relentless_cause.py` | 2/5 | 0 | 2 | 20 / 103 |
| `relentless_disk.py` | 7/12 | 7 | 7 | 50 / 160 |
| `relentless_dispute.py` | 14/55 | 14 | 55 | 712 / 712 |
| `relentless_envcause.py` | 0/8 | 0 | 0 | 0 / 91 |
| `relentless_exam.py` | 22/66 | 18 | 36 | 513 / 911 |
| `relentless_expedite.py` | 0/11 | 0 | 0 | 0 / 146 |
| `relentless_explain.py` | 1/14 | 0 | 0 | 0 / 130 |
| `relentless_game.py` | 8/145 | 3 | 9 | 85 / 2,342 |
| `relentless_incident.py` | 9/20 | 0 | 3 | 13 / 281 |
| `relentless_integrity.py` | 2/19 | 2 | 2 | 41 / 289 |
| `relentless_jobs.py` | 23/23 | 0 | 0 | 0 / 215 |
| `relentless_live.py` | 96/114 | 11 | 39 | 654 / 1,968 |
| `relentless_live_round.py` | 13/59 | 1 | 11 | 111 / 792 |
| `relentless_names.py` | 13/58 | 13 | 13 | 239 / 1,151 |
| `relentless_packet.py` | 2/7 | 0 | 0 | 0 / 69 |
| `relentless_pool_why.py` | 0/8 | 0 | 0 | 0 / 125 |
| `relentless_prooflines.py` | 1/9 | 0 | 0 | 0 / 88 |
| `relentless_reach.py` | 20/26 | 0 | 1 | 7 / 422 |
| `relentless_reachfix.py` | 21/38 | 0 | 21 | 270 / 708 |
| `relentless_release.py` | 0/25 | 0 | 0 | 0 / 344 |
| `relentless_repair_slot.py` | 0/2 | 0 | 0 | 0 / 37 |
| `relentless_seeds.py` | 0/56 | 0 | 0 | 0 / 777 |
| `relentless_selfbuild.py` | 0/15 | 0 | 0 | 0 / 259 |
| `relentless_showing.py` | 1/35 | 0 | 0 | 0 / 512 |
| `relentless_stage.py` | 0/44 | 0 | 0 | 0 / 485 |
| `relentless_strikes.py` | 3/3 | 0 | 3 | 15 / 15 |
| `relentless_tickprof.py` | 0/18 | 0 | 0 | 0 / 134 |
| `relentless_trust.py` | 0/14 | 0 | 0 | 0 / 215 |
| `relentless_usage.py` | 10/11 | 9 | 10 | 147 / 153 |
| `relentless_wake.py` | 2/12 | 1 | 1 | 2 / 191 |
| `relentless_wall.py` | 43/64 | 24 | 32 | 373 / 719 |
| **all 43 modules** | 471/1569 | 152 | 397 | 5,578 / 24,841 |

So **397 of 1,569 functions are live (25%)**; about 5,600 of 24,800 function lines move, the rest is deleted. 23
of the 42 modules have no live function at all: `account`, `answer`, `binding`, `bindjudge`, `block`, `boxrun`,
`broker`, `canary`, `envcause`, `expedite`, `explain`, `jobs`, `packet`, `pool_why`, `prooflines`, `release`,
`repair_slot`, `seeds`, `selfbuild`, `showing`, `stage`, `tickprof`, `trust` (some show a count in the first column
only through the era tools set aside below).

Importers that are themselves Relentless-era tools, set aside from the roots (each says so in its own docstring; each
goes with the dead code): `rimflow/validator_replay.py` (replays "the REAL supervisor transitions"; it alone pins
`relentless.contract/finish/unhold/verdict` and 85 functions of `relentless_live`), `rimflow/lightspeed_wire.py` (writes
proof lines "for owed Relentless criteria"), `rimflow/block_migrate.py` (one-shot over relentless store items),
`rimflow/replay_unreached_closes.py` (replays past Relentless closes), and `ops_watch.py`'s relentless points
(`c_relentless`, `rl_game_hold_idle`, `rl_broker_turn_ended`, the `expedite` caller). Also set aside: 29 rimflow tests
with non-era names that test the dead tick or the dead live round (for example `selftest_live_verdict.py`,
`selftest_repro_miss.py`, `selftest_workshop_live_mods.py`, `selftest_pool_dead_runs_release.py`); they go with the
code they test.

The live callers, by what they reach: `detached_helper.py` (`Store`, `Effects.remove_clone` and the bundle path,
`rules`), `cli.py` (`guard` on every guarded verb; `prooflint` at file/close/implemented through
`relentless_live.lint_item`, `live_rules`, `relentless_game.proof_lines`), `role_launch.py` (`Store`; the Setter seam
`relentless_exam.kick/status/set_status/unit_name`; the arbiter seam `relentless_dispute.role_stage_dispute`),
`maturation_autonomy.py` (`pilot_model`, `CHAIN_MAX_PER_DAY`, `day_of`), `circling.py` (`Store`, `rules`), `evidence.py`
(`Store`, `relentless_wall.box_config`), `owner_queue.py` (`relentless_game.flyer_hold`), `modlist_swap.py`
(`relentless_names.default_index`), `modledger_backfill.py` (`relentless_wake.store_dir`), and the mod proofs
(`relentless_live_round.proof_lines/live_mods/folders/site_for`, `relentless_live.live_rules/refused_proof/refused_site`).

A live retired-era behaviour found on the way: `relentless.guard` refuses `rimflow close/claim/start/...` on an item
the dead tick still "carries". Measured 2026-11-18 14:50 PST: 25 store items sit in leased states (19 `game`,
4 `checking`, 2 `stopping`) with no tick to settle them. The split moves the guard unchanged (a move, not a redesign);
its removal is filed as `RIMMANDRAKE_RETIRE_LEASE_GUARD_TWENTY_FIVE_GHOST_LEASES`.

## Phase 2: moved

How a move is made (tools: `src/RimMandrake/Utils/era_reach.py`, then `src/RimMandrake/Utils/era_split.py`, each with
its selftest): the live top-level nodes of one module go verbatim into a module named for what it does; a live class
moves whole (dead code may still hold its instances). The old module keeps only its dead nodes and imports the live
names back from the new one, so the dead code and its old tests run unchanged until the deletion step removes them.
Live importers are repointed in the same commit, and the live cases of the old tests move into the new module's test.

| live part | moved from | moved to | its test | sha |
|---|---|---|---|---|
| the one live-mods name resolver: `Index`, `resolve`, `default_index`, `nearest`, `repo_defs`, `_srchashes` and their constants (15 names, 279 of 1,384 lines) | `rimflow/relentless_names.py` | `rimflow/mod_names.py` (importer repointed: `Utils/modlist_swap.py`) | `rimflow/selftest_mod_names.py` (20 cases from `selftest_relentless_needs.py`; watched red on a mutant) | `25308a5645` |
| the proof-line lint and live-proof rules: `lint_item`, `lint_lines`, `live_rules`, `refused_proof`, `refused_site`, `proof_budget`, the `Fx` file reads they use (live methods only; `relentless_live.Fx` subclasses it with the dead ones) and their constants (100 names, 1,029 of 2,256 lines) | `rimflow/relentless_live.py` | `rimflow/proof_lint.py` (importers repointed: `cli.py` and 24 mod proofs and tests) | the mod-proof selftests that call it (all green) | `4ada623de6` |
| the live-proof lines of an item: `proof_lines`, `site_for`, `live_mods`, `folders`, `clause_tier`, `mods_tier`, `is_package`, `live_deploy/menu/toggle/tiers` and the line grammars (28 names, 181 of 902 lines) | `rimflow/relentless_live_round.py` | `rimflow/proof_lines.py` (imports `proof_lint`, not `relentless_live`; importers repointed: `testq/schema.py` comment and 18 mod proofs and tests) | the same tests plus `selftest_live_mods_names.py`, `selftest_testq_tier.py` | `4ada623de6` |
| the run store and the clone effects: `Store` (its live methods; `relentless.Store` subclasses it with the dead ones), `Effects` narrowed to what live code calls (`__init__`, `remove_clone`, `bundle_clone`, `restore_bundle` and what they call through `self`; `circling_tree`, `transcripts`, `stop` for `circling.py`), `rules`, `guard` (unchanged: it still refuses on the 25 ghost leases, `RIMMANDRAKE_RETIRE_LEASE_GUARD_TWENTY_FIVE_GHOST_LEASES`), `pilot_model`, `new_state`, the pool constants; plus `flyer_hold`/`FLYER` from `relentless_game.py` and a copy of `relentless_wake.store_dir` (the wake module keeps its own until the poke goes). `run_store.Effects` no longer inherits `relentless_game.GameFx`: no GameFx method is reached by live code (measured); `relentless.Effects` inherits both (42 functions, 798 of 7,784 lines) | `rimflow/relentless.py` | `rimflow/run_store.py` (importers repointed: `detached_helper.py`, `cli.py`, `role_launch.py`, `evidence.py`, `circling.py`, `maturation_autonomy.py`, `modledger_backfill.py`, `Utils/owner_queue.py`, and 7 tests) | `selftest_circling`, `selftest_scratch_clone`, `selftest_detached_helper`, `selftest_conductor_authority`, `selftest_maturation_dispatch`, `selftest_role_launch_*`, `selftest_evidence`; a real `evict_clone` on a planted pool bundled and parked | `7a910cdd97` |
| park or remove a returned clone: `park`, `remove_tree`, `warm_clones`, `reset_clean`, `is_warm`, `gone_ok` (7 functions) | `rimflow/relentless_disk.py` | `rimflow/clone_park.py` | `selftest_relentless_disk.py` still green through the shim; moves at the deletion step | `7a910cdd97` |
| read a clone for damage: `clone_damage`, `nul_or_empty` | `rimflow/relentless_integrity.py` | `rimflow/clone_integrity.py` | `selftest_relentless_integrity.py` likewise | `7a910cdd97` |
| the walled box a checker runs in: `box_config`, `profile`, `make_box`, `remove_box`, `props`, `unit_env` and their grants, copies and constants (24 functions, 475 of 719 lines) | `rimflow/relentless_wall.py` | `rimflow/checker_box.py` (importers repointed: `evidence.py`, `item_exam.py`) | `selftest_evidence.py`; `selftest_relentless_wall.py` green through the shim. Its config is still `relentless_box.json` (renamed in the json step) | move 3 |
| the Setter seam: `status`, `set_status`, `kick`, `unit_name`, `run_setter`, `box_runner`, `apply_patch` and their readers (18 functions, 249 of 911 lines) | `rimflow/relentless_exam.py` | `rimflow/item_exam.py` (importers repointed: `role_launch.py`, two role_launch tests) | `selftest_role_launch*.py` (6, green); `selftest_relentless_exam.py` green with its box stand-in on `checker_box` | move 3 |
| the arbiter seam: `role_stage_dispute` and the arbiter run it starts (14 functions, 239 of 712 lines) | `rimflow/relentless_dispute.py` | `rimflow/stage_dispute.py` (imports `item_exam`, `run_store`; importers repointed: `role_launch.py`, `selftest_role_launch_reject_routes.py`) | `selftest_relentless_dispute.py` (its role-entry case now patches `run_store`/`stage_dispute`) | move 3 |

For move 3, `selftest_role_launch_reject_routes.py` was also set aside as a root (its wildcard use of `relentless_dispute` made the whole module look live). Measured first: the exam's own unit (`relentless_exam.py run`, what `kick` starts) counts as dead, because every unit the Setter seam, the arbiter and the box start is launched as family `relentless`, which the control store refuses (`./pipe show`: `family:relentless OFF`, 2026-11-18). Both seams act only on an item with a Relentless-era exam (102 in the store, newest 2026-11-06). Their retirement is filed as `RIMMANDRAKE_RETIRE_SETTER_ARBITER_SEAMS_EVERY_LAUNCH_REFUSED`, with its acceptance test. `era_reach.py` gained `--roots` for script entries.

For move 2 the cut line also set aside the relentless cases of eight more tests (`Utils/selftest_codex_runner`, `selftest_conductor_log_guard`, `selftest_ops_health_incidents`, `selftest_ops_health_fan_in`, `rimflow/selftest_incident`, `selftest_testpilot_model`, `selftest_prooflint_at_filing`, `selftest_run_tmp`: the tick's launch, alarms, pause, finish gate and tmp sweep), and ran `era_reach.py --only-methods "relentless.Effects=__init__,remove_clone,circling_tree,transcripts,stop,restore_bundle;relentless_game.GameFx="`. After it `relentless_usage.py` has no live function.

The cut line for moves 1 onward (BENCH, second run, 2026-11-18): `era_reach.py . selftests --exclude-roots <list>`, the list being the four era tools, `Utils/ops_watch.py` (its only era roots are the relentless points) and 29 rimflow tests that test the dead tick, live round, pool or validator replay: `selftest_{companion_cover_batchreads,engine_review_leftovers,jam_classes,live_companion_gate,live_mods_tooling_dirs,live_pacing_pruned,live_round_item_gate,live_verdict,liveround_stale_build,names_modcheck_closure,pool_dead_runs_release,pool_game_waiters_release,proof_cost,proof_sha_cited_mods,repro_miss,workshop_live_mods,books_untracked_runs,evidence_wire_repair,fake_effects_drift,fakeworld_parity,livecheck_reader,validator_mutants,wrapup_restore,first_touch,evidence_gate,evidence,close_gate,concept_tree,judge_card_answers}.py`. The last eight test live modules too: at the deletion step only their relentless cases go, the rest stay. Measured with that list: **270 functions live** (plus their constants) of 1,569, in 11 modules: `relentless` 68, `dispute` 55, `live` 52, `exam` 36, `wall` 24, `live_round` 11, `usage` 10, `disk` 7, `game` 4, `integrity` 2, `wake` 1.

Left for the next run, in this order (each one move per commit, the launcher check after any that touches
`detached_helper.py`, `role_launch.py`, `maturation_autonomy.py` or `cli.py`):

1. `relentless_live.py` (the proof-line lint `cli.py prooflint` calls: `lint_item`, `live_rules`, `refused_proof`,
   `refused_site`, `proof_budget`) and `relentless_live_round.py` (`proof_lines`, `live_mods`, `folders`, `site_for`,
   `clause_tier`, `is_package`, `mods_tier`: the mod proofs' helpers) -> `proof_lint.py` and `proof_lines.py`;
   `relentless_game.py` `flyer_hold`/`proof_lines` with them. Repoint `cli.py`, `owner_queue.py` and the ~25 mod
   proof tests listed in the measured-reach section.
2. `relentless.py` -> `run_store.py` (`Store`, `Effects`, `rules`, `guard`, `pilot_model`, `CHAIN_MAX_PER_DAY`,
   `day_of`, the clone/bundle helpers), with `relentless_disk.py`, `relentless_integrity.py`, `relentless_usage.py`,
   `relentless_wake.store_dir` beside it; `relentless_rules.json` -> `run_rules.json` (live keys only). Repoint
   `detached_helper.py`, `circling.py`, `evidence.py`, `role_launch.py`, `maturation_autonomy.py`, `cli.py`,
   `modledger_backfill.py`. Then the launcher check.
3. `relentless_exam.py` (Setter seam) -> `item_exam.py`; `relentless_dispute.py` (arbiter seam) -> `stage_dispute.py`;
   `relentless_wall.py` (the walled box they run in, `box_config`) -> `checker_box.py`; their json beside them.
4. Deletion: every `relentless*.py` and `relentless_*.json`, the 117 era selftests, the four era tools
   (`validator_replay.py` with `validator_replay/`, `lightspeed_wire.py`, `block_migrate.py`,
   `replay_unreached_closes.py`), `ops_watch.py`'s relentless points and their three Utils selftests and two fixtures,
   the 29 dead-machinery rimflow tests, the wake poke in `publish.py` and `Utils/land.sh`; one Removed row each.
5. Then the rest of the Phase 2 table (`Utils/pulse/**`, the sims, the v3 docs, `FOUNDRY.md`, unit copies).

Kept on purpose (on-disk paths live code reads, NOT renamed by this item): `/home/mandrake/rm/relentless/store`
(`Store`'s default root: `scratch_clone.py`, `running_now.py`, `circling.py`, `evidence.py` and `role_launch.py` read
it) and `/home/mandrake/rm/relentless/clones` (the detached-helper pool, `detached_helper.pool_root`; running helpers
live in it). A later rename needs: no detached run alive, the pool's clones moved or reaped, `RM_DETACHED_POOL` and
`DEFAULT_ROOT` changed in one commit, and the 128 tracked files outside the ledger, conversations and replay fixtures that spell `rm/relentless` (measured 2026-11-18) updated.

## UNMEASURED

What this run could not settle, and what would settle it:

- Whether `LIVEPROOF_REDEPLOY_FIX_TRIPS_PEER_DLL` (a live proof re-deploying into the running game) still happens in
  today's live drivers: left open. Settled by grepping today's proof scripts for `modcheck run` without
  `MODCHECK_SKIP_DEPLOY`.
- Whether `DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE` (FOUNDRY's code-review loop over ~140 dirty C# files) should be
  re-filed in today's words: left open; `code_review_status.py` still measures the dirt.
- SteveDesktop was not read (a soak is running there).

## Tickets

Open ledger items whose target is a retired loop, seat or tool were dropped on 2026-11-18 with `rimflow drop --reason
"retired era: <why>. Index: design/RimMandrake/retired_eras_index_2026-11-18.md"` (the reason is on each item's drop
event in the ledger). The earlier triage (`D:\ClaudeWork\rimmandrake\conductor\pipeline_ticket_triage_20261118.md`)
had already dropped ten. Ten pre-2026-11-13 tickets were left to the Conductor's own check, untouched here. Concept
anchors (each `design/concepts/<Mod>/stage.json` item) stay open whatever their title says; mod-content items were out
of scope.

| item | era | dropped? |
|---|---|---|
| `BRIDGE_LOCK_CROSS_CLONE_RACE_1` | FOUNDRY | dropped |
| `RIMPULSE_SHEETS_FIX_OWN_PROBE_REOPENS_THEM` | RimPulse | dropped |
| `RIMPULSE_LOOKS_BUILD_UNREAD_NEVER_LISTED` | RimPulse | dropped |
| `RIMPULSE_ALERTS_FIX_TELEMETRY_CRIES_WOLF` | RimPulse | dropped |
| `RIMPULSE_FAILED_FIX_COUNTS_MANIFESTS_TOO` | RimPulse | dropped |
| `RIMPULSE_PACKETS_BUILD_ANSWERED_NOT_APPLIED` | RimPulse | dropped |
| `RIMPULSE_LOOK_ASK_PROMISED_AT_GOODBYE` | RimPulse | dropped |
| `STEWARD_ESCALATION_REWIRE_TO_ENGINE` | FOUNDRY | dropped |
| `RIMFLOW_V3_BUILD_DISPATCHER_FIRST` | rimflow v3 | dropped |
| `LIVE_FIXER_DESIGN_ONE_SEAT_NO_SHUTTLE` | rimflow v3 | dropped |
| `LIVEFIXER_BUILD_NOBODY_EVER_DID` | FOUNDRY | dropped |
| `PRIORITY_LIST_BUILD_ONE_SHORT_FILE` | Relentless | dropped |
| `BUSY_SEAT_FIX_WAITING_COUNTS_AS_WORK` | FOUNDRY | dropped |
| `FOCUS_CAP_FIX_LIST_CANNOT_REACH` | FOUNDRY | dropped |
| `FOUNDRY_THROUGHPUT_MEASURE_V2_GAP` | FOUNDRY | dropped |
| `BOOKS_STALE_FIX_ART_SHARD_REORDER` | Relentless | dropped |
| `BOOKS_STALE_FIX_OPS_CANNOT_SEE_IT` | Relentless | dropped |
| `BLINDCHECK_PROVE_VERDICTS_EATEN_BY_DISK` | Relentless | NOT dropped: it has dependents (rimflow refused without --release-dependents); left for the Conductor |
| `WALLBOX_SHRINK_STILL_SHIPS_WHOLE_TREE` | Relentless | dropped |
| `TICKSLOW_REWIRE_CLONES_OFF_THE_BELT` | Relentless | dropped |
| `RIMMANDRAKE_POOL_ELIGIBLE_FINISH_ITEMS_LEFT_OUT` | Relentless | dropped |
| `BUILT_ORPHANS_WIRE_NOBODY_LEFT_TO_CHECK` | Relentless and FOUNDRY | dropped |
| `PIPELINE_BUDGET_ENFORCE_HEAL_THYSELF` | Relentless | dropped |
| `RIMMASTER_BRIEF_BUILDERS_REUSE_BEFORE_BUILDING` | Relentless | dropped |
| `RIMMANDRAKE_CUT_RELENTLESS_RELEASE_BEFORE_ANY_TIMER_RESTART` | Relentless | dropped |
| `FLEETWATCH_NEEDS_FIX_NOTHING_WHILE_MODS_WAIT` | Fleet Watch | dropped |
| `STEVE_BUILD_ARTISAN_LOOPER_THIRTEEN_MINUTES` | Artisan loops | dropped |
| `RIMMANDRAKE_BUILD_WHITTLE_ADMISSION_AND_HARD_STOPS` | Whittle loops | dropped |
