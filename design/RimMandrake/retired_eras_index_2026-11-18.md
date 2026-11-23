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
something, delete it and add a "Removed" row. Since 2026-11-19 it also reads text (rule: `src/RimMandrake/rimflow/era_text.py`):
an instruction file (CLAUDE.md, agent definitions, roles, SKILL.md files, seat files, the standing rulings, top-level
`infrastructure/*.md`) must say on the line that a retired era or deleted module it names is past, and a record file
(design doc, skill reference, lesson, fact) may instead open with the HISTORY head that
`src/RimMandrake/Utils/era_history_mark.py --apply` writes (`design/INDEX.md` shows it as "📜 names a retired era").

## Removed

| what it was | path | era | why it is gone | last sha that held it |
|---|---|---|---|---|
| the Whittle loops' work folder: STATEMENT/PROMPT/JUDGE/OBSERVER, FINDINGS, the Codex live-driver report, the STOP switch and every round's evidence (15,365 files) | `whittle/` | Whittle | loops retired 2026-11-13; nothing current reads it (live items that cite `whittle/<run>/evidence/...` read it with `git show`) | `f2ce40bac8` |
| the Claude Whittle worker kit: loop.sh, wc.py, gate.py, install/setup, lane briefs, `whittle-claude@.service` | `infrastructure/whittle_claude/` | Whittle | its unit is masked and its runs ended 2026-11-13 | `f2ce40bac8` |
| the Stop hook that held a Whittle session open, and its `.claude/settings.json` Stop entry | `.claude/hooks/whittle_stop.py` | Whittle | armed only by `WHITTLE=1`, which nothing sets | `f2ce40bac8` |
| the Whittle status page and its selftests | `src/RimMandrake/Utils/whittle_now.py`, `selftest_whittle_now.py`, `selftest_whittle_claude_{admission,gate,pick}.py` | Whittle | its timer is masked; the claude-worker selftests tested `infrastructure/whittle_claude/` | `f2ce40bac8` |
| the repo copies of the status page's units | `src/RimMandrake/Utils/systemd/rm-whittle-now.{service,timer}` | Whittle | masked on Archmagi since 2026-11-13; the mask stays | `f2ce40bac8` |
| the Whittle Codex-runner note | `src/RimMandrake/rimflow/roles/whittle.md` | Whittle | described a retired runner; `runner_options.md` keeps the live-driver rules, and `design/RimMandrake/roles.history.md` keeps its stall table | `f2ce40bac8` |
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
| the expedite route by which Operations handed alarms and unclaimed steward incidents to Relentless (`steve_incident_early`, `expedite_of`, `expedite_owner`, the alarm title's "owner: Relentless, ... expedited", the rules' `expedite_after_min` and `expedite_field`) and its test | `src/RimMandrake/Utils/ops_watch.py` (functions), `ops_watch_rules.json` (keys), `src/RimMandrake/Utils/selftest_steve_incident_expedite.py` | Relentless | it ran `relentless.py expedite set` into the retired tick's store, so every expedite went nowhere while the alarm title named Relentless as the owner; `target_problem` now refuses an `expedite_field` | `1a3a2baae7` |
| the Relentless game-hold reader (`rl_game_hold_idle`, `rl_broker_turn_ended`, the `relentless.game_hold_idle_min` target) and its tests and fixture | `src/RimMandrake/Utils/ops_watch.py` (functions), `src/RimMandrake/Utils/selftest_relentless_watch.py`, `selftest_relentless_game_hold_agrees.py`, `src/RimMandrake/Utils/testdata/relentless_jam_2026-11-01.jsonl` | Relentless | it read `relentless_broker.py` and `relentless_jobs.py` (deleted with the tick); the point now reads UNMEASURED with that reason | `1a3a2baae7` |
| the Relentless tick and everything only it reached: `relentless.py` (now only dead code over `run_store`) and the 42 `relentless_*.py` modules | `src/RimMandrake/rimflow/relentless*.py` | Relentless | no live file reaches a function in any of them (`era_reach.py`, 2026-11-18, after moves 1 to 4; the from-package import gap fixed first) | `d2a0462048` |
| the tick's remaining config: `relentless_boxrun`, `_broker`, `_jobs`, `_selfbuild`, `_wake` `.json` | `src/RimMandrake/rimflow/relentless_*.json` | Relentless | read only by the deleted modules | `d2a0462048` |
| 117 selftests of the deleted modules, their fixture, and the bridge-seat test | `src/RimMandrake/rimflow/selftest_relentless*.py`, `selftest_bridge_seat_relentless.py`, `testdata/relentless_packet_handscored.json` | Relentless | each tested deleted code; their live cases moved first (moves 1 to 4, step 1) | `d2a0462048` |
| 22 tests with neutral names that tested only the dead tick, live round, pool or validator replay | `rimflow/selftest_{companion_cover_batchreads,engine_review_leftovers,jam_classes,live_companion_gate,live_mods_tooling_dirs,live_pacing_pruned,live_round_item_gate,live_verdict,liveround_stale_build,names_modcheck_closure,pool_dead_runs_release,pool_game_waiters_release,proof_cost,proof_sha_cited_mods,repro_miss,workshop_live_mods,books_untracked_runs,evidence_wire_repair,fake_effects_drift,fakeworld_parity,livecheck_reader,validator_mutants}.py` | Relentless | the dead-root list of the cut line (above) | `d2a0462048` |
| the four Relentless-era tools | `rimflow/validator_replay.py` (with `validator_replay/`), `lightspeed_wire.py`, `block_migrate.py`, `replay_unreached_closes.py`, and the tests of two of them (`selftest_validator_replay.py`, `selftest_lightspeed_wire.py`) | Relentless | each replays or rewrites Relentless store history; their own docstrings say so | `d2a0462048` |
| the tick's seed-compare prover and the repo copies of the masked units | `rimflow/prove_relentless_s03_compare.py`, `Utils/systemd/rm-relentless*` | Relentless | read only by deleted selftests; the host units stay masked (`retired_loops_check.py`) | `d2a0462048` |
| the station note box: the PostToolUse and Stop hook that handed a note to the Relentless worker it was bound to, its module and its test, and both `.claude/settings.json` entries | `.claude/hooks/notebox_deliver.py`, `src/RimMandrake/rimflow/notebox.py`, `src/RimMandrake/Utils/selftest_notebox.py` | Relentless | the hook ran on every tool call and exited at once: it acts only when env `RELENTLESS_GEN` is set and `.git/relentless.json` exists, and nothing sets the one or writes the other (2026-11-19: no code, unit or environment file sets it; only readers and `agent_runner.py`'s pass-through list name it) | `ed3b6ca7a5` |
| the telemetry exporter's `pulse` source (RimPulse alarm rows from `~/.local/state/rm-dashboard/metrics.jsonl`, last written 2026-11-03) | `src/RimMandrake/Utils/telemetry/wsl_export.py` (two lines and its docstring row) | RimPulse | the daemon that wrote it is retired; `telemetry/ingest.py` still reads old `pulse` rows already in the store | `ed3b6ca7a5` |
| the seat files of the 2026-08-27 redesign, each already "SUPERSEDED" and pointing at a CLAUDE.md section that no longer exists | `infrastructure/agents/BUILD.md`, `CHECK.md`, `DECIDE.md` | FOUNDRY-era seats | they sent a reader to Relentless as the place the work went (`.claude/hooks/selftest_documented_commands.py` no longer lists them) | `9761a57a92` |
| `./bridge foundry` (gave the bridge to the retired FOUNDRY seat, which has no window) | `bridge` (one case and its hint) | FOUNDRY | the override now names `conductor` and `free` only; `rimflow bridge give FOUNDRY` still replays old events | `9761a57a92` |
| the Innovator role: its instruction file, its schedule row and go-live name, its `ops_watch` word-list and acted-share rows, its live promise and its note name (the owner, 2026-11-23: "Role is retired.") | `src/RimMandrake/rimflow/roles/innovator.md`, the row in `dispatcher_schedule.json`, rows in `ops_watch_rules.json`, `live_baseline.txt`, `contracts/blind*.py` | rimflow v3 | switched off, last ran 2026-10-30, and waited on two items dropped 2026-11-01. The idea list `design/RimMandrake/innovations.md` stays. `selftest_retired_era_gone.py` (`RETIRED_ROLES`) refuses its return | `2a9009e7ec` |

## Phase 2: renames

Live code with an old name, an allow row for the guard each: the path, who uses it (blast radius), and the proposed new
name. Empty since 2026-11-18: the last rows (`Utils/pulse/**`, the `./pulse` launcher and
`rimpulse_redesign_2026-10-23.md`) went in Phase 2 step 4b below.

| path | who uses it (blast radius) | proposed new name |
|---|---|---|

Old names inside live files (not paths, so the guard does not see them), for the same phase:

- `src/RimMandrake/Utils/bridge_holder.py` `CODEX_SEATS`: the `CLAUDE_*` seats were the Claude Whittle workers; their
  ledger shards stay as history, so the names must keep replaying.
- `set_agent_window.sh` refuses FOUNDRY and `./bridge foundry` is gone (2026-11-19); `model.bridge_identity` still accepts RELENTLESS
  for old `bridge` events; `cli.py` `RETIRED_SEATS` maps FOUNDRY to the Conductor's key (keep that mapping: old
  events name it).
- `ops_watch.py` still reads the Relentless points (`c_relentless`, `rl_game_hold_idle`) and judges them retired;
  `slot_allocator` and `slot_rules.json` keep a FOUNDRY seat key and a RELENTLESS key that "gets the whole machine total"
  (`RIMMANDRAKE_RETIRE_FOUNDRY_SLOT_KEY_INDEX_NAMED_A_GHOST`; this index named it `SLOTS_RENAME_FOUNDRY_KEY_RELENTLESS_READS_IT`
  before 2026-11-19, an item that never existed).
- `src/RimMandrake/rimflow/live_retired.txt` and `src/RimMandrake/Utils/retired_loops_check.py` name the retired units on
  purpose: they keep them masked. Keep both.

## Kept on purpose

| path | why it stays |
|---|---|
| *(none)* | The last row, the Ralph FlowWorks pit-features ticket, left on 2026-11-22: the FlowWorks ticket sweep dropped it as DEAD (main built its own fetch-fallen, bedless pit prison and pit drawing). Its prose is in `infrastructure/state/items/closed/`; the 36 commits stay on `origin/ralph/flowworks` as the archive. |

## Outside this repo

Nothing outside the repo was changed by the 2026-11-18 item; what moved on 2026-11-19 is under "Outside this repo:
done". What remained, for the Conductor:

- `~/.claude/skills/` links into MandrakeWorkflows: `artisan`, `artisan-head`, `artisan-judge`, `relentless-pipeline`,
  `whittle`. Done 2026-11-18 (below): the links stay, and RimMandrake sessions no longer see the skills.
- Masked user units on Archmagi (`systemctl --user list-unit-files` shows them `masked`): `rm-relentless*`,
  `rm-artisan-now.*`, `rm-whittle-now.*`, `whittle-claude@.service`, `rm-pulse.service`. Keep the masks:
  `retired_loops_check.py` (deadman, every 15 min) alarms if one is unmasked. SteveDesktop's `whittle-claude@` mask
  likewise (read 2026-11-19 over ssh: masked, the only era unit there).
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
| the walled box a checker runs in: `box_config`, `profile`, `make_box`, `remove_box`, `props`, `unit_env` and their grants, copies and constants (24 functions, 475 of 719 lines) | `rimflow/relentless_wall.py` | `rimflow/checker_box.py` (importers repointed: `evidence.py`, `item_exam.py`) | `selftest_evidence.py`; `selftest_relentless_wall.py` green through the shim. Its config is still `relentless_box.json` (renamed in the json step) | `a164008a3e` |
| the Setter seam: `status`, `set_status`, `kick`, `unit_name`, `run_setter`, `box_runner`, `apply_patch` and their readers (18 functions, 249 of 911 lines) | `rimflow/relentless_exam.py` | `rimflow/item_exam.py` (importers repointed: `role_launch.py`, two role_launch tests) | `selftest_role_launch*.py` (6, green); `selftest_relentless_exam.py` green with its box stand-in on `checker_box` | `a164008a3e` |
| the arbiter seam: `role_stage_dispute` and the arbiter run it starts (14 functions, 239 of 712 lines) | `rimflow/relentless_dispute.py` | `rimflow/stage_dispute.py` (imports `item_exam`, `run_store`; importers repointed: `role_launch.py`, `selftest_role_launch_reject_routes.py`) | `selftest_relentless_dispute.py` (its role-entry case now patches `run_store`/`stage_dispute`) | `a164008a3e` |
| the live config the moved code and the pipeline read: `relentless_rules.json` (the whole file: helper budget, dispatch, steward, pipeline watch, running_now, incident, circling and the mod proofs read keys of it), `relentless_owner_pause.json`, `relentless_box.json`, `relentless_exam.json`, `relentless_dispute.json` | `rimflow/` | `rimflow/run_rules.json`, `owner_pause.json`, `checker_box.json`, `item_exam.json`, `stage_dispute.json` (git mv; every reader in `src/` and `.claude/agents/rm-builder.md` updated; skills, handoffs, ledger and dated design docs keep the old name as history) | the readers' 26 tests; `selftest_evidence_recovery.py` R7 repointed (its fake `relentless` module had gone stale at move 2) | `829686e552`, old names deleted `99d4de3569` |
| the seeded-set trust numbers (`compute`, `on_target`, `wilson`, `CLASSES`, `PRIVATE`) and the WEAK reading rule (`acted_weak`, `narrow_word`, `names_strong` and their two patterns), which `delivery_metrics.py` reads for the daily findings judge (`regrade.py`, `evidence_metrics.py`). `era_reach.py` had missed them: it did not read `from rimflow import relentless_x` (fixed, case added to `selftest_era_reach.py` and watched red first) | `rimflow/relentless_trust.py`, `rimflow/relentless_wall.py` | `rimflow/seed_trust.py`, `rimflow/weak_reading.py` (importer repointed: `delivery_metrics.py`) | `rimflow/selftest_seed_trust_weak_reading.py` (cases from `selftest_relentless_seeds.py` and `selftest_relentless.py`; watched red on two mutants) | `5eef0e3ea4` |

For move 3, `selftest_role_launch_reject_routes.py` was also set aside as a root (its wildcard use of `relentless_dispute` made the whole module look live). Measured first: the exam's own unit (`relentless_exam.py run`, what `kick` starts) counts as dead, because every unit the Setter seam, the arbiter and the box start is launched as family `relentless`, which the control store refuses (`./pipe show`: `family:relentless OFF`, 2026-11-18). Both seams act only on an item with a Relentless-era exam (102 in the store, newest 2026-11-06). Their retirement is filed as `RIMMANDRAKE_RETIRE_SETTER_ARBITER_SEAMS_EVERY_LAUNCH_REFUSED`, with its acceptance test. `era_reach.py` gained `--roots` for script entries.

For move 2 the cut line also set aside the relentless cases of eight more tests (`Utils/selftest_codex_runner`, `selftest_conductor_log_guard`, `selftest_ops_health_incidents`, `selftest_ops_health_fan_in`, `rimflow/selftest_incident`, `selftest_testpilot_model`, `selftest_prooflint_at_filing`, `selftest_run_tmp`: the tick's launch, alarms, pause, finish gate and tmp sweep), and ran `era_reach.py --only-methods "relentless.Effects=__init__,remove_clone,circling_tree,transcripts,stop,restore_bundle;relentless_game.GameFx="`. After it `relentless_usage.py` has no live function.

The cut line for moves 1 onward (BENCH, second run, 2026-11-18): `era_reach.py . selftests --exclude-roots <list>`, the list being the four era tools, `Utils/ops_watch.py` (its only era roots are the relentless points) and 29 rimflow tests that test the dead tick, live round, pool or validator replay: `selftest_{companion_cover_batchreads,engine_review_leftovers,jam_classes,live_companion_gate,live_mods_tooling_dirs,live_pacing_pruned,live_round_item_gate,live_verdict,liveround_stale_build,names_modcheck_closure,pool_dead_runs_release,pool_game_waiters_release,proof_cost,proof_sha_cited_mods,repro_miss,workshop_live_mods,books_untracked_runs,evidence_wire_repair,fake_effects_drift,fakeworld_parity,livecheck_reader,validator_mutants,wrapup_restore,first_touch,evidence_gate,evidence,close_gate,concept_tree,judge_card_answers}.py`. The last eight test live modules too: at the deletion step only their relentless cases go, the rest stay. Measured with that list: **270 functions live** (plus their constants) of 1,569, in 11 modules: `relentless` 68, `dispute` 55, `live` 52, `exam` 36, `wall` 24, `live_round` 11, `usage` 10, `disk` 7, `game` 4, `integrity` 2, `wake` 1.

State after the third run (2026-11-18, about 6:45 PM PST). Steps 1 to 3 are done. Step 1: the tick's cases are out of the 17 partial tests (`0e52f58619`, `b4c7cf2ce8`), and `concept_tree.relentless_refusal` (only the tick called it) is gone. Step 2: `publish.py` and `land.sh` no longer poke `relentless_wake.py` (`9c404c5657`); `ops_watch.py` no longer hands alarms to the tick (the expedite route, whose alarm titles named Relentless as owner) and no longer reads the game hold through deleted modules (`d2a0462048`); `era_reach.py` was blind to `from rimflow import relentless_x`, so a fourth move was owed and made (`5eef0e3ea4`). Step 3: the deletion (the Removed rows above), measured first in a full-checkout scratch clone at `9c404c5657` (17 tests went green to red; an earlier count of 38 came from a cone-sparse clone and was wrong), with each of those tests fixed in the same commit, 16 by stripping the tick's cases and the live-proofs directory guard carried into `rimflow/selftest_live_proofs_dir.py`. `entrypoint_inventory.py` now keeps 30 of the deleted module names unreached for good.

Renamed 2026-11-18, every live reference repointed in the same commit (history, open-item prose and recorded fixtures keep the old names): `rimflow_v3_2026-10-26.md` to `dispatcher_design_2026-10-26.md`; `rimflow_v3_arbiter_tiers_2026-10-27.md` to `dispatcher_arbiter_tiers_2026-10-27.md`; `rimflow_v3_flows.svg` to `dispatcher_flows.svg`; `rimflow_v3_golive_wave1.md` to `dispatcher_golive_wave1.md`; `rimflow_v3_responsibilities_2026-10-26.md` to `role_responsibilities_2026-10-26.md`; `rimflow_v3_risk_response_2026-10-29.md` to `dispatcher_risk_response_2026-10-29.md`; `rimflow_v3_audit_remeasure_2026-10-31.md` to `dispatcher_audit_remeasure_2026-10-31.md`; `rimflow_v3_roles.html` to `dispatcher_roles.html`; `rimflow_v3_trial_night_2026-10-28.md` to `dispatcher_trial_night_2026-10-28.md`; `relentless_tree_schema_2026-11-01.md` to `concept_tree_schema.md`.

Renamed 2026-11-18 the same way: `sim/ralph_loop_sim.py` to `sim/loop_sim.py` and `sim/rimflow_v3_sim.py` to `sim/process_sim.py`, with their params, selftests and `rimflow_v3_sim_findings_2026-10-27.md` (now `process_sim_findings_2026-10-27.md`); `rimflow/selftest_foundry_literals.py` to `rimflow/selftest_retired_seat_literals.py`.

Removed 2026-11-18: `infrastructure/agents/FOUNDRY.md`, with FOUNDRY out of `set_agent_window.sh`; a window naming the seat is refused and gets no identity (`selftest_conductor_identity.py`). `model.SEATS` and `cli.RETIRED_SEATS` keep FOUNDRY so its closed items replay.
Removed 2026-11-18: `design/RimMandrake/relentless_recovery_plan_2026-11-05.md`; its §3 ruling and the measured reason now stand in `standing_rulings.md` (An unhealthy system pauses only what it touches); every citer points at `git show 9e35e61381:design/RimMandrake/relentless_recovery_plan_2026-11-05.md`.
Renamed 2026-11-18: `relentless_improvement_loop_2026-11-03.md` to `improvement_loop_rules_2026-11-03.md`, kept whole rather than folded into the findings judge prompt: four live modules besides the prompt cite its rules.

Left, in order:

1. Done: `RIMMANDRAKE_RETIRE_RELENTLESS_COLLECTOR_READS_A_DEAD_STORE`. `ops_watch.py` lost `c_relentless` and the 49 names only it reached (834 lines), its family, 10 targets, 8 ranges and the rules block; the three SLIs on its keys went from `health.slis` (`infra_share` is listed unmeasured, its instrument gone) and its three routes from `alarm_routes.json`. A removed family's old keys read as its removal, not silence, in `ops_watch.andon` and `incident.retired_sane` (`REMOVED_FAMILIES`). `running_now.py` lost the Relentless Pipeline panel, its chips, phone section, tree branch, chain rows and every reader of the dead store (3151 to about 1960 lines); MODS ACCEPTED moved to the Progress-by-mod panel. Four era tests and one fixture went; nine tests were rebuilt on live families.
2. Done: `RIMMANDRAKE_RETIRE_CIRCLING_WATCH_ONLY_THE_DEAD_TICK_CALLED`. `circling.py` kept only `classify` and `_ts` (pulse/time_ledger read them; 341 lines went, its replay CLI with them; the rest went with time_ledger in step 4a); `run_store.Effects` lost `stop`, `circling_tree` and `transcripts`, which only `circling.watch` called; `run_rules.json` lost `same_failure_limit` and the eight `circling` keys only the watch read, keeping the four time_ledger reads.
3. Text that still names a deleted module. Done: 25 alarm routes for kinds only the tick raised (measured with `alarm_census`: no live code raises them), the pre-push hook's lease fence, the masked unit copies `Utils/systemd/rm-store-ledger-diff.{service,timer}` (the host units stay masked: `retired_loops_check.py`), the `relentless_stage.py` mutants of `selftest_second_game_mutants.py`, the `_doc` of `item_exam.json` and `stage_dispute.json`; six more names joined the inventory batch. Done too: `run_rules.json` cut from 112 keys to 19 (the 93 the tick alone read went, with `circling.help_*` and `live.auto`; measured by quoting each key against every non-test file under `rimflow/`, `Utils/` and `.claude/hooks/`, then reading each word-collision hit by hand: `share`, `staffing`, `game`, `showings`, `stale_s`, `max_workers`, `proof_paths` are other things there). `selftest_run_rules_keys.py` (at the door) refuses a key no live file names. Two kept keys go with their tickets: `only_system_and_live` (running_now's panel) and `same_failure_limit` (`circling.watch`). `prove_relentless_s03_compare` joined the inventory batch. Left: the skills (`live-debugging-proof-harness`, `rimflow-operations`; curation sessions only) for `lightspeed_wire`, `relentless_game`, `relentless_live`, `relentless_live_round`, `relentless_reachfix`; and the bare word `relentless` (store paths, kept on purpose). Once a name has none, add it to the step-3 batch in `entrypoint_inventory.py`.
4. Done: the sims, the v3 docs, `FOUNDRY.md`, both relentless_* docs, `RIMMANDRAKE_RETIRE_SETTER_ARBITER_SEAMS_EVERY_LAUNCH_REFUSED` (closed by another lane), `RIMMANDRAKE_RETIRE_LEASE_GUARD_TWENTY_FIVE_GHOST_LEASES` (bb0f483b3a) and the pulse package (4a, 4b).
4a. Done: the pulse package's reach, measured with `era_reach.py --era-dir src/RimMandrake/Utils/pulse` (roots: every live importer, plus the scripts units run by path: `pulse.py update`, `streams.py collect`, `testing_metrics.py`). Before: 11 modules, 386 functions, 106 reached (89 once streams' panel renderer, reached only by its own `render` verb, counted dead). Deleted whole (no live importer): `agents_timeline.py`, `mission_page.py`, `time_ledger.py` with `time_ledger_replay/` (53 fixture files), `brief.py` (streams' panel took only its CSS) and their four selftests; with `time_ledger` went `rimflow/circling.py`, `selftest_circling.py` and `run_rules.json` `circling` (time_ledger was its only reader). Trimmed to what is reached: `pulse.py` 43 functions to 3 and a 10-line `main` (only `update` is run: rm-deploy-update), `pulse_core.py` 100 to 11 (the ledger readers and the owner-ask fold), `usage.py` 15 to 2 (`config`, `panel`), `streams.py` 53 to 36 (the panel renderer went; `collect`, `backfill`, `show` stay). `failreport.py` went: it appended to `~/.local/state/rm-dashboard/failures.jsonl`, which only the retired daemon read; winbuild, findings_judge.sh, rm-agent-improve and rm-selftests-nightly stop writing it. The testq steward still writes its `steve:lane` record there inline (its selftest reads it; nothing else does). `usage.json`, which `streams.budget` and `account_usage.py` read, has no writer since the daemon stopped (it was present but last written 2026-11-03; moved out 2026-11-19), so streams' budget measure reads UNMEASURED (`RIMMANDRAKE_WIRE_STREAMS_GAME_STATE_OFF_A_FROZEN_SNAPSHOT`).
4b. Done: the pulse package's live part moved to `src/RimMandrake/Utils/ops_core/` as a cutover: `pulse.py` is `deploy_update.py` (verb `update`), `pulse_core.py` is `ops_ledger.py`, `selftest_pulse.py` is `selftest_ops_core.py`, `selftest_pulse_{deploy_on_ext4,sparse_dirs}.py` are `selftest_deploy_{on_ext4,sparse_dirs}.py`; `phone_push`, `streams`, `testing_metrics`, `usage` and their selftests keep their names. `rm-deploy-update.service` and `rm-streams-collect.service` run the new paths (repo copies and installed copies, the same sitting); the deploy checkout's sparse list holds `Utils/ops_core`. Removed with it: the `./pulse` launcher (only the retired dashboard verbs and `update` were behind it) and `design/RimMandrake/rimpulse_redesign_2026-10-23.md` (`git show 4b1c4a745c:design/RimMandrake/rimpulse_redesign_2026-10-23.md`). Kept on purpose, names live code and units read, not tree paths: the deploy checkout `/home/mandrake/rm/pulse-deploy` (ops_watch's `PULSE_DEPLOY`, `scratch_reap.py`, 66 tracked files measured 2026-11-18; a rename needs a fresh clone there, both units and ops_watch in one commit), its `.git/pulse_update_last_good` stamp (ops_watch `deploy_update_age`), the env names `RM_PULSE_STATE` and `RM_PULSE_DEPLOY`, and the state dir `~/.local/state/rm-dashboard/` (the steward's `failures.jsonl`, phone_push's `phone_push.json`). `skills/telemetry/references/history.md` still cites `$U/pulse/pulse.py:82` as history, under its HISTORY head.

Filed on the way: `RIMMANDRAKE_WIRE_WRAPUP_RESTORE_ORPHANED_BY_RETIRED_TICK` (nothing calls `wrapup restore` since the tick) and `RIMMANDRAKE_FIX_ALARM_RECEIVER_TRUSTS_RETIRED_RELENTLESS_POOL` (`incident.receiver_problem` still reads the retired pool as draining BENCH offline alarms), each with its acceptance test.

Found on the way (2026-11-18 continuation), red on the untouched base as well, not caused by the split: `selftest_known_reds.py` (2 WIRE checks on an overdue NIGHTLY_RED alarm) and `rimflow/selftest_incident.py` (role_launch alarm kinds `stage_void` and `system_fault` fall through to cause roles unreviewed). Neither is in `pipeline_tests.json`.

Found on the way, not caused by the split: `selftest_relentless_checkbox.py` is red 8 at HEAD (a box cannot read
`rimflow/control.py`; era test, goes at step 3); `selftest_focus_cap.py` is red (filed
`RIMMANDRAKE_FIX_FOCUS_CAP_REFUSED_CLAIM_STILL_TAKES_LEASE`). The tools need `PYFLAKES_PYTHON` (a venv with pyflakes).

Kept on purpose (on-disk paths live code reads, NOT renamed by this item): `/home/mandrake/rm/relentless/store`
(`Store`'s default root: `scratch_clone.py`, `running_now.py`, `circling.py`, `evidence.py` and `role_launch.py` read
it) and `/home/mandrake/rm/relentless/clones` (the detached-helper pool, `detached_helper.pool_root`; running helpers
live in it). A later rename needs: no detached run alive, the pool's clones moved or reaped, `RM_DETACHED_POOL` and
`DEFAULT_ROOT` changed in one commit, and the 128 tracked files outside the ledger, conversations and replay fixtures that spell `rm/relentless` (measured 2026-11-18) updated.


## State, 2026-11-19 (BENCH, item `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS`)

The 2026-11-19 census (`D:\ClaudeWork\rimmandrake\conductor\retired_era_remains_20261119.md`) found 21 remains with no
ticket, and 11 places that told a fresh agent to use a retired thing, while the guard read green. What was done:

- **Lines that sent an agent to a deleted thing** (`ed3b6ca7a5`): `rm-builder.md`, `rm-judge.md`, `rm-consult.md` (the
  Relentless Pipeline and `relentless.py`, and a "Relentless freeze" no live ruling backs); `BUILD.md`, `CHECK.md`,
  `DECIDE.md` deleted; `./bridge foundry` removed; the proof-harness skill now names `proof_lint.py`/`proof_lines.py`;
  11 role files, `standing_rulings.md` (the `relentless.py` review exception deleted), `delegation_policy.md`,
  `GIT_WORKFLOW.md`, `GAME_STATE_WORKFLOW.md`, `Agent_Policy.md`, both facts trap files and 20 skill files rewritten to
  what runs today. The installed `rm-dispatcher.service` comment now matches its repo copy.
- **Dead things** (`d55f855dbd`): the note-box hook (wired on every tool call; nothing sets `RELENTLESS_GEN`) with its
  module and test, and the telemetry exporter's RimPulse source. Outside the repo, nothing deleted: 87 era-named entries
  of `D:\ClaudeWork\rimmandrake\` and 12 files of `~/.local/state/rm-dashboard/` MOVED to
  `D:\ClaudeWork\retired-trees\rimmandrake_eras_20261119\` (`MANIFEST.md`, `MANIFEST.tsv`).
- **Wisdom marked as history** (`2fe7aae28d`): 297 design docs, 49 lessons, 7 facts and 1 skill reference carry the
  HISTORY head; core live docs (`maturation_pipeline.md`, `biome_mod_architecture.md`, `STRUCTURE.md`,
  `VALIDATION_LADDER.md` and others) were fixed line by line instead; `lessons.py` reads past the head and no longer reads
  the Whittle loop's `WC_ITEM`.
- **The gate reads text** (`fbdf50a5b2`): watched red on the pre-fix tree, 2011 era text lines
  (`D:\ClaudeWork\rimmandrake\conductor\era_finish_20261119\gate_prefix_run.txt`); green after, 1782 files read.
- **Settled from "could not tell"**: `rm-dispatcher.service` is live (static, started by the live wakes; it ran
  2026-11-19 06:31 PST; its timer is disabled). The Auditor is a scheduled role in
  `dispatcher_schedule.json`, `enabled: false`. The store's `transcripts` (written by `scratch_clone.py`) and
  `store/evidence_shadow.jsonl` (written by `rimflow close`) are live.

Left, one ticket each, every one with its acceptance test watched failing:

| ticket | what |
|---|---|
| `RIMMANDRAKE_RENAME_RUN_STORE_AND_POOL_OFF_TICK_PATH` | the store and pool under `/home/mandrake/rm/relentless`, and the `RELENTLESS_*` env names |
| `RIMMANDRAKE_RETIRE_FOUNDRY_SLOT_KEY_INDEX_NAMED_A_GHOST` | the allocator's RELENTLESS and FOUNDRY keys and the FOUNDRY seat clone lists |
| `RIMMANDRAKE_RENAME_FLEET_STATES_READER_STILL_NAMED_FOR_TICK` | `fleet_mods.relentless_states`; dropped 2026-11-19, not worth the touch (`infrastructure/state/facts/pipeline_polish_parked.md`) |
| `RIMMANDRAKE_RENAME_DEPLOY_CHECKOUT_OFF_THE_PULSE_NAME` | `pulse-deploy`, `RM_PULSE_*`, `rm-dashboard` |
| `RIMMANDRAKE_RENAME_SEVEN_WORK_DIRS_STILL_NAMED_FOR_LOOPS` | seven `D:\ClaudeWork\rimmandrake\` dirs live code reads; dropped 2026-11-19, not worth the touch (`infrastructure/state/facts/pipeline_polish_parked.md`) |
| `RIMMANDRAKE_SWEEP_SELFTEST_TEXT_STILL_NAMING_THE_OLD_TICK` | 56 selftests naming the tick in text |
| `RIMMANDRAKE_PROBE_STORE_LEFTOVERS_A_WEEK_FOR_ANY_READER` | 8 store leftovers last written 2026-11-04 to 11-06 |
| `RIMMANDRAKE_SWEEP_STEVEDESKTOP_CLONES_CARRYING_LOOP_TREES` | SteveDesktop clones with `ralph/` and `whittle/` trees |
| `RIMMANDRAKE_WIRE_HEALTH_VERDICT_READER_NOBODY_OBEYS_IT` | Operations' health verdict, whose one reader was the tick |
| `RIMMANDRAKE_FIX_LIVE_PANEL_COUNTS_A_LOG_NOBODY_WRITES` | `running_now`'s Archmagi panel counting a dead run log as 0 |
| `RIMMANDRAKE_WIRE_STREAMS_GAME_STATE_OFF_A_FROZEN_SNAPSHOT` | `streams.py` game state and budget from frozen RimPulse files |
| `RIMMANDRAKE_ADD_AUTHORITY_LINE_NEW_CODE_REVIEW_ROLE_MISSED` | found on the way: `roles/code_review.md` lacks the authority line (red on origin) |

## UNMEASURED

What this run could not settle, and what would settle it:

- Whether `LIVEPROOF_REDEPLOY_FIX_TRIPS_PEER_DLL` (a live proof re-deploying into the running game) still happens in
  today's live drivers: left open. Settled by grepping today's proof scripts for `modcheck run` without
  `MODCHECK_SKIP_DEPLOY`.
- Whether `DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE` (FOUNDRY's code-review loop over ~140 dirty C# files) should be
  re-filed in today's words: left open; `code_review_status.py` still measures the dirt.
- SteveDesktop: read 2026-11-19 (units above; its old clones still carry `ralph/` and `whittle/` trees:
  `RIMMANDRAKE_SWEEP_STEVEDESKTOP_CLONES_CARRYING_LOOP_TREES`).

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
