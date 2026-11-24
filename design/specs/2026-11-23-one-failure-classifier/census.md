# CENSUS: every counter that counts bad outcomes and then stops, gives up, escalates or files (2026-11-23)

How: an AST sweep of every non-test `.py` file under `src/RimMandrake` and `infrastructure` for comparisons, retry loops,
increments and integer constants whose words name a failure, an attempt or a limit: 913 comparisons and 233 increments or
constants [measured]. The shell and PowerShell files were read with a text search. Each candidate below was read in its
code. A comparison that is no counter (a length of text, a pixel count, a tick budget of a scene, a simulation in
`Utils/sim`, a wait on a clock) is not in the tables. `src/RimMandrake/Utils/failure_counter_list.json` holds the 61
places of pipeline machinery that the lint sees and why each needs no call.

## Had the hole, fixed (16 counters)

| counter | what it counts, what it does | what it read | the input that was counted as the work's failure | fix and its test |
|---|---|---|---|---|
| `testq/visit_feed.py` FAILS_TO_STOP 2 | runs of a visit's chain that measured nothing; stops sending the chain | not DONE, or no PASS or FAIL row | two INTERRUPTED/CRASH, INVALID/GAME_DIED or CANARY, a cancel, all rows UNMEASURED | `visit-feed-spends-a-chain-only-on-its-own-fault` |
| `testq/testq.py` FILL_DRY_RUNS 2 | runs of a chain with only UNMEASURED rows; the filler skips it 3 days | the rows, whatever the job's outcome | two killed jobs that left UNMEASURED rows | `a-dry-chain-is-read-from-done-runs-only` |
| `testq/ingest.py` MAX_TRIES 6 | ingests of one result that failed; the record is marked done, its verdict lost | any error | six timeouts of the rimflow CLI | `a-verdict-is-not-dropped-by-a-crash` |
| `testq/fault_monitor.py` RERUN_DEPTH 2 | re-queues after a machine-fault quarantine; the job stays out | the count | a third fault window | `a-quarantined-job-is-queued-again` (limit removed: no danger named) |
| `testq/steward.py` wake (one per incident, TESTQ_WAKE_RETRIES 2) | wakes that died; the incident is not woken again | exit and log | a wake killed at its cap; a third login death | `a-dead-wake-is-tried-after-its-cooldown` |
| `rimflow/testpilot_route.py` STREAK 3 (`rimflow pilot`) | non-pass runs in a row; routes the item to a Test Pilot | `result` only | three `partial` runs of UNMEASURED rows | `an-unmeasured-run-is-in-no-pilot-streak`, `ingest-says-could-not-look` |
| `rimflow/stop_resume.py` MAX_TRIES 3 | refused resumes of a stopped run; gives the run up | a launch that failed | three refusals for a full clone pool | `a-refused-resume-is-tried-again` |
| `rimflow/red_dispatch.py` (one attempt) | the fixer's launch or run; the red item stops until `clear` | an attempt is recorded | a launch that never started; a run killed by a fleet stop | `a-red-fixer-that-died-spends-no-attempt` |
| `rimflow/list_dispatch.py` max_runs_per_item 2, max_never_started 2, one Shape run | Work and Shape runs, launches that never started; the item stops until `clear` | an attempt is recorded | a killed Work or Shape run; two refusals for a full pool | `a-list-run-that-died-spends-no-run`, `a-launch-that-never-started-is-not-spent` |
| `rimflow/designer_cleanse.py` CONVERGE_ROUNDS 2 | converge rounds; what is open goes to the owner's pages | a round is written | an author run that died; a reader unreadable twice | `a-dead-author-spends-no-converge-round` |
| `rimflow/form_fault.py`, `maturation_dispatch.py` FAULT_REPAIRS_MOST 2 and "the repair did not hold" | ended repair runs; names the Conductor, or counts a fault | the run ended | a repair run killed by a fleet stop | `a-killed-repair-run-is-no-repair` |
| `rimflow/left_open_continue.py` MAX_PER_DAY 3 | continuations of one item in a day; an alarm, no launch | launched and not refused | three continuations killed by a fleet stop | `a-killed-continuation-spends-no-slot` |
| `rimflow/role_launch.py` RESUME_MAX 3 | resumes of a role run; gives the run up | every resume | three legs that did work and met the account limit | `an-account-ending-after-work-spends-no-resume` |
| `Utils/maturation_now.py` CYCLE_ALARM 3 ("has run N times") | runs of a stage; a Needs Conductor line | every run | three killed runs | `a-killed-run-is-no-cycle-on-the-page` |
| `rimflow/roles/conductor.md` CHURNING, 3+ returns (a rule that an agent reads) | returns of a queued item; the sweep holds it | any return | three returns after killed runs | the rule's text names the returns that do not count; no code, no test |
| `art/facing_regen_batch.py` MAX_ATTEMPTS 2, `artpipe/requeue_flakes.py --max 3` | failed renders of a picture or job; not drawn or requeued again | the attempt count; any parked manifest | a Codex call that timed out or crashed | `a-dead-render-spends-no-attempt` |

## Has the hole, and waits (1 counter; the file is held by the live FlowWorks visit 9 run)

| counter | the input | the change |
|---|---|---|
| `FlowWorks/northstar/extensions_rivers.py` PAN_TRIES 8 | eight panning sessions at 50 % or better that all roll nothing (1 in 256 at worst) raise ExpectationFailed, so a RANDOM MISS reads FAIL, class MOD | the note on the item |

Two more scenes decide on a random result after a few tries. Each is kind A and its miss is rare: Stillsand `fish`
(2 jobs, about 1 in 2500) and Contagion `extraction surgery` (3 completed tries) end FAIL when all miss [guess ~70% on
the odds]. No false FAIL of either is on record [guess ~80%]. They are on `polish.md`.

## Checked, no such input (named in the brief)

| counter | evidence |
|---|---|
| `Utils/publish.py` MAX_TRIES 8 | counts push races; on giving up the commit is intact on HEAD, the refusal names the cause, and no check, trial or item reads it |
| `FlowWorks/prove_pump_tank_coupler.py` MAX_TRIES 400 | candidate cells, not failures; none clear exits 2 (no verdict), never 1 |
| maturation trial, turn, look and cycle counts (`blind_cycles_*`, `ingame_runs_visit`, steward, fixer, `launch_tries`, coverage looks, Designer retries, chain cap) | `design/RimMandrake/pipeline_trial_counters_census_2026-11-18.md`: `run_void` takes killed, timed out and never started runs out of each book first; `selftest_run_void.py` and `selftest_void_counters.py` |

## Checked, no such input (found by the sweep)

| counter | evidence |
|---|---|
| `coverage_judge.py` NOT_COVERED_LIMIT, JUDGE_RUNS_MAX, MALFORMED_LIMIT, ROW_REASK_MAX | dead rounds are `void_system` and are in no count (ad019a7e19) |
| `coverage_judge.py` JUDGE_FAULT_LIMIT, `run_void.py` SYSTEM_FAULT_LIMIT, `control.py` FAULT_LIMIT, `role_launch.py` void_held and void_route | the system-fault meters: they count machine faults by design and charge nothing |
| `refusal_contract.py` item, clause and family alarms | a well-formed verdict of a judge only |
| `designer_stage.py` two rejections in a row | void_system rejections are moved out (4fe2af3f9e) |
| `maturation_dispatch.py` REPAIR_LAUNCH_MOST | refused launches name the Conductor; the mod is not charged; a wait refusal spends none |
| `live_kinds.py` budget | APPARATUS FAULT and COULD NOT LOOK spend none (NO_BUDGET) |
| `model.py` deaths of a fix | a reading `broken` only; a shared outage charges its host only |
| `art_eval` regen and veto rounds | rounds are judged pictures; an errored compare vetoes nothing |
| `stage_dispute.py` arbiter_tries | no ruling reads void |
| `modcheck/governor.py` max_restarts, `modcheck/clockgate.py` max_stalls, `validation_core.py` dead replies and SITE_RECOVER_MAX | the row ends RESTART, ClockStall or WatchdogAbort, which read UNMEASURED; a bridge fault is no FAIL |
| proof loops: ExplosiveKnockback, climb_proof, concept_scenes, suspension_bridge, stage_proof_site, raid_trench, gss_playtest, LongShade (3), TheForge, TheSump, Cauldron (2), Stillsand vekka, Contagion sunbeam, liquid_checks, live_session, map_awareness | each ends UNMEASURED or INVALID when its tries run out |
| `run_selftests.py` INTEROP_RERUNS 2 | a test whose launch dropped three times stays red, with the drop in its text: turning it unmeasured could hide a real FAIL printed in the same output (its own selftest pins this) |
| machine brakes: `testq.py` brake_tail, auto_retries; `archmagi_switch.py`; `fault_monitor.py` MAX_REBOOTS_DAY; `nightly_catchup.py` cap; `artpiped.py` streaks and attempts; `raise_ladder.py`; `login_watch.py`; `signal_watch.py`; `dispatcher.py` rings; `ops_watch.py` blips and INVALID streak; `slot_allocator.py`; `deadman_check.py` FOLD_AT (a report line); `timers_guard.py`; `pager.py`; `restart_reconcile.py`; `seat_loop.sh` | the subject is the machine, a window or a lane; no check, trial, item or mod is charged |
| transport retries: git locks, ssh, `winbuild.py`, `gate_browser.py`, `decisions_v2.py`, `nemotron_*`, `control_acts_export.py`, `scan_marked*`, `land_ledger`, `game_audio_route.ps1` | each gives up with a named failure and records no verdict |
| SteveDesktop lane: `worker.py`, `bootstrap_wsl.sh`, `verify_from_archmagi.sh` | no attempt limit; `FAILS` counts setup steps of one run |
