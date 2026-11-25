# Census of the monitors, pages, reports and digests (2026-11-24)

Item `RIMMANDRAKE_REMOVE_RELENTLESS_NOW_PAGE_CONSOLIDATE_MONITORS_HE_SAID_SLEEK`. Measured on Archmagi on 2026-11-24 at 5:00–5:25 PM PST.
Sources: `systemctl --user list-timers --all` (52 named timers, plus 116 transient `run-p*` timers), `src/RimMandrake/Utils/systemd/ops_clocks.json`,
the folders `D:\ClaudeWork\rimmandrake\conductor`, `ops_watch`, `dispatcher` and `dashboard`, the bench clone's `Transient`, and a `git grep` for a
reader of each output. `infrastructure/dashboards/hub` is not in the repo, so it has no row.

**"Read in 7 days"**: a reader in code that runs on a live timer is evidence. A person's open in Typora or Chrome cannot be read, so it is
UNMEASURED. The plan for the pages that stay: `plan.md` beside this file.

## Pages that a person reads

| page | writer, cadence | reader (7 days) | duplicates | verdict |
|---|---|---|---|---|
| `D:\ClaudeWork\augur\dashboard\FLEET_NOW.md` | Augur `augur.dashboard.render`, `augur-dashboard.timer`, 30 s | the owner (UNMEASURED); Augur opens it in Typora | none: the one fleet page | KEEP |
| `D:\ClaudeWork\rimmandrake\conductor\MATURATION_NOW.md` and `.html` | `maturation_now.py`, `rm-maturation-page.timer`, 60 s after each build | `pages_open.py` (`./pages` opens the HTML), `owner_queue.py`, ops_watch freshness rule; the owner (UNMEASURED) | none | KEEP |
| `D:\ClaudeWork\rimmandrake\conductor\MATURATION_DETAIL.md` and `.html` | the same run of `maturation_now.py` | the link at the foot of MATURATION_NOW; agents | the lists behind MATURATION_NOW, not a copy of it | KEEP |
| `D:\ClaudeWork\rimmandrake\conductor\MATURATION_NOW_phone\*.png` | the same run | the owner on the phone (UNMEASURED) | the phone form of MATURATION_NOW | KEEP |
| `D:\ClaudeWork\rimmandrake\conductor\CODEBASE_NOW.html` | `codebase_now.py`, `rm-codebase-now.timer`, 15 min | `pages_open.py`; the owner (UNMEASURED) | none | KEEP |
| `D:\ClaudeWork\rimmandrake\ops_watch\digest.md` | `ops_watch.py`, Dispatcher job `ops_watch`, 900 s | Operations (`role_launch.py`), the Conductor role | none | KEEP |
| `D:\ClaudeWork\rimmandrake\ops_watch\digest_blind.md` | the same run | token-blind roles (`conductor.md`) | the token-blind form of digest.md, by design | KEEP |
| `D:\ClaudeWork\rimmandrake\ops_watch\memory.md` | `ops_memory.py`, each ops_watch pass | Operations (`role_launch.py` incident runs) | none | KEEP |
| `Transient\delegated_digest_<date>.md` (bench clone) | `delegated_digest.py`, daily, Conductor pre-step | the Conductor delivers it to the owner (written each day 11-17 to 11-24) | none | KEEP |
| `D:\ClaudeWork\rimmandrake\findings_fold\findings_fold.md` | `findings_fold.py`, Dispatcher schedule | `rm-findings-judge.timer` (ran 11-24 07:20) | none | KEEP |
| `D:\ClaudeWork\rimmandrake\canon_sweep\findings.md` | `canon_sweep.py`, `rm-canon-sweep.timer`, 30 min | the Conductor role (`conductor.md`) | none | KEEP |
| `D:\ClaudeWork\rimmandrake\conductor\log.md` | hooks, `pager.py`, `account_handover.py`, the steward | `CONDUCTOR.md`, ops_watch rule | a log, not a page | KEEP |
| Grafana dashboards (Windows telemetryd, built by `telemetry/grafana/build_dashboards.py`) | `rm-telemetry-export/pull/health` timers feed it | UNMEASURED | none seen | KEEP, reader UNMEASURED |
| `D:\ClaudeWork\rimmandrake\conductor\RELENTLESS_NOW.md`, `RELENTLESS_NOW_PHONE.md` | `running_now.py`, removed at `ec2637b7b6` | none in code | FLEET_NOW and MATURATION_NOW (Part 1 note) | REMOVED (code at ec2637b7b6, files today) |
| `D:\ClaudeWork\rimmandrake\conductor\STATUS_BOARD.html` and `.tmp.1765065` | `status_board.py`, removed at `ec2637b7b6` | none | RELENTLESS_NOW | REMOVED |
| `ARTISAN_NOW.md`, `ARTISAN_NOW_PHONE.md`, `WHITTLE_NOW.md`, `WHITTLE_NOW_PHONE.md`, `artisan_now_state.json`, `whittle_now_state.json` (conductor folder) | none: last written 11-13, the retired Artisan and Whittle loops | none in code; Augur's config links (repointed today) | retired eras | REMOVED today |
| `relentless_view_mock_20261102.html`, `running_v2_progress.md` (conductor folder) | one-off files of the Relentless era | none | none | REMOVED today |
| `D:\ClaudeWork\rimmandrake\dashboard\digests\` (90 files) | none in code; last written 11-03 | none | the ops digest and the delegated digest | REMOVED today |

## Data files that a program reads (no person reads them)

| file | writer, cadence | reader | verdict |
|---|---|---|---|
| `conductor\running_steve.json` | `steve_reading.py`, `rm-steve-reading.timer`, 1 min | Augur `remote_hosts` (FLEET_NOW) | KEEP |
| `conductor\running_fleet.json`, `running_history.jsonl`, `running_state.json` | `running_now.py`, removed | none | REMOVED today |
| `conductor\CODEBASE_NOW.json` | `codebase_now.py` | `codebase_now.py` | KEEP |
| `ops_watch\digest.json`, `status.json`, `alarms.json` | `ops_watch.py` | `slot_allocator.py`, Operations, `deadman_check.py` | KEEP |
| `dispatcher\owner_view\view.json` | Dispatcher tick | `owner_queue.py`, the art tools | KEEP |
| `vv_matrix\last.json` | `rm-vv-matrix.timer`, weekly | `vv_matrix_clock.py` | KEEP |
| `Transient\selftests_nightly.log` | `rm-selftests-nightly.timer`, 03:00 | `known_reds.py`, `nightly_green.py`, `nightly_catchup.py` | KEEP |
| `testing_metrics\history.jsonl`, `streams\series.jsonl` | `rm-streams-collect.timer`, 15 min | `ops_watch.py`, `streams.py`, `deploy_update.py` | KEEP |
| `game_health\history.jsonl` | the health observer | `ops_watch.py` | KEEP |

## Counts

25 rows [measured]. Pages that a person reads: 12 KEEP, 6 REMOVED. Data files: 8 KEEP, 1 REMOVED. Nothing is MERGE: each kept page answers
its own question, and the kept pages do not repeat each other's facts.

## What only RELENTLESS_NOW showed, and where it is now

- On another page: accounts, sessions, machines, games and jobs on FLEET_NOW; what needs him, the mods and the game drivers on MATURATION_NOW;
  the steward state and jobs in 24 h in the ops digest.
- In the JSON, not drawn: the SteveDesktop services (`view.services` in `running_steve.json`). Ticket
  `RIMMANDRAKE_DRAW_STEVE_SERVICES_ON_FLEETNOW_JSON_HAS_THEM`.
- On no page now: the process tree and its NOT RECOGNISED list, the chain diagrams, the recent events feed, "finished today", the mods
  accepted (`modcheck status` has them), the timer list (`systemctl --user list-timers` has it), and the fuel words AHEAD, EQUAL and
  BEHIND (FLEET_NOW shows when each account runs out).

## Retired names in the kept pages

- `ops_watch\memory.md` still shows open alarms on retired families: `relentless.under_min`, `relentless.returned_tokens_pct`,
  `relentless.churn_item.*`, `tokentalk.FOUNDRY.share`, `tokentalk.commits.FOUNDRY.share` (all retired; open since 11-06, "absent from this
  generation"). Ticket `RIMMANDRAKE_CLEAR_RETIRED_ALARMS_OPS_MEMORY_OPEN_SINCE_NOV`.
- `CODEBASE_NOW.html` names `/home/mandrake/rm/pulse-deploy`. Its rename ticket, `RIMMANDRAKE_RENAME_DEPLOY_CHECKOUT_OFF_THE_PULSE_NAME`, was
  dropped on 2026-11-20 as not worth the touch (a polish line in `infrastructure/state/facts/pipeline_polish_parked.md`), so no new ticket.
  The other "Pulse" words there are mod file names (`RM_ForgePulse.xml`, `RM_GameCondition_WeatherPulse.cs`), not the era.
- `digest.md`, `MATURATION_DETAIL.md` and `FLEET_NOW.md` use the words only inside item names, ledger seat names and quoted rule text.
  These are data, so no rename is owed.

## Found on the way

- 116 transient `run-p*.timer` units (144 at 4:45 PM PST), each `systemctl --user start rm-dispatcher.service`, armed by
  `seat_restart.py` (`--on-active`). `rm-dispatcher.service` is loaded and inactive, with no start this boot. UNDIAGNOSED. Ticket
  `RIMMANDRAKE_DIAGNOSE_RUNP_TIMERS_PILING_ON_IDLE_DISPATCHER`.
