# Census: every time budget in pipeline machinery against its real run time, 2026-11-24

Item `RIMMANDRAKE_MEASURE_TIME_BUDGETS_AGAINST_REAL_RUNS_HE_SEES_TEN_PERCENT`. Owner, 2026-11-24 about 9:30 AM PST: *"Why do
we have them set to within 10% of what the process really needs?"* A time budget is a number that ends, skips, defers or
fails work because time passed. This page is the reading of one day, before the repair of that day. The check that
holds the rule from now on is `src/RimMandrake/Utils/time_budget_lint.py` (`boundary.md` beside this page).

## The answer

499 time budgets stood in the files of the scope (`time_budget_lint.scope_files`) [measured].

| ratio (budget / longest real run) | budgets |
|---|---|
| under 1.5 | 38 |
| 1.5 to under 3 | 12 |
| 3 to under 10 | 37 |
| 10 or more | 142 |
| no record joined by the first run of the day; the second run classed each one (§The 270) | 270 |

- **"Within 10%" is true of 27 budgets** (ratio 1.10 or less), and it is worse than he said: 17 of these stood
  under the longest real run. 12 of the 27 rest on an upper bound (the time of a whole that holds the work), so their true ratio may be
  higher. They are the first rows of the next table.
- 15 of the 38 rows under 1.5 rest on an upper bound. A longest run that a budget cut is a floor: the true ratio is lower.
- 159 of 499 budgets name no danger at the number.
- The machine's load is the other half of the answer. `selftest_maturation_autonomy.py` took 36 s alone (2026-11-15) and
  599 s at load 45 (2026-11-24). A budget of 5 times the idle run is a budget of 0.3 times the loaded run.
- The first run counted 181 more budgets inside selftests and acceptance programs. The lint reads them now: 196
  (why the count moved is not known). Each stands at its value (`in_test`), and a new or
  lowered one is checked when it lands. A record of a run that such a budget ended: none seen.

## Where the ten tightest came from

| budget | commit | who chose the number |
|---|---|---|
| metronome `dispatch` 20 s, `budget_s` 45 s | a09d26c480 (2026-11-03) | the agent; no reason at the number then |
| metronome `raise` 4 s, `ring` 2 s | 3377f2be73 (2026-11-06) | a ticket (WP-12b, a review finding): the limit was cut to twice the longest run seen, to free time for a sibling |
| `./publish` pipeline check 180 s | 277260bc81 (2026-11-15) | the agent; no reason at the number (the owner's card of that day asked for the checks, not for a deadline) |
| `rm-scratch-reap` `--max-seconds` 1800 | 7802f5d927 (2026-10-31) | the agent; the reason named another limit (the unit's TimeoutStartSec) |
| detached helper clone 540 s | f310ac01b0 (2026-11-01) | the agent; no reason at the number |
| `testq-tick` 900 s | 76bd31f806 (2026-11-22) moved the text; older | the agent; no reason at the number |
| SteveDesktop worker plan 600 s and tier check 180 s | 0b4698b7fa (2026-10-25), fad513f97e (2026-11-05) | the agent; no reason at the number |
| `rm-running` 90 s | 7967a22410 (2026-11-03) | the agent; no reason at the number |
| `rm-memwatch` 50 s | 58dda0a656 (2026-10-08) | the agent; no reason at the number (the timer beat is 60 s) |
| Operations `run_max_s` 1800 | aba6f427e5 (2026-10-27) | the agent; no reason at the number |

Rule: 0. Ticket: 1. An agent's own choice: 9. No rule or ticket of the owner asked for any of the ten numbers.
The habit is visible in the text of three more numbers: the selftest deadline went from 240 s to 600 s on 2026-11-22
because a pass took 526 s; the SteveDesktop load wait was "about twice the longest"; the metronome limits name their own maximum
run and stand at 1 to 2 times it. An agent measured the longest run on that day and added a little.

## Every budget under 10, and every budget that live work reached

`stays` is explained under LIMITS of `boundary.md`. "14 d" is the 14 days to 2026-11-24.

| file:line | budget | s | ends | danger it named | longest real s | usual s | record | ratio | reaches, 14 d | cost of the reaches | after |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Utils/systemd/metronome_phases.json:6 | limit_s | 20 | the call, run or phase is ended | reason text in the file names the past runs, no danger | 97 | 5.0 | beats.jsonl, 14 d; 97 s is the old timer (2026-11-06) | 0.21 | 28 | one Dispatcher tick cut, each | raised to 1000 |
| Utils/pipeline_tests.json:4 | timeout_s | 180 | the call, run or phase is ended | NONE | 599 | 17 to 104 (one run of 8 tests, load 13 to 45) | this run, 2026-11-24; reaches: agent transcripts, 14 d | 0.30 | 202 in 91 publishes (8 tests), 2026-11-19 to 2026-11-24 | each reached check read UNMEASURED and the landing went on without its verdict; 10 h of process time | guard on progress, backstop 6000 |
| Utils/systemd/rm-scratch-reap.service:13 | --max-seconds | 1800 | rows of the run are deferred | NONE | 3707 | 320 | rm-scratch-reap runs.jsonl (164 runs) and user journal, 14 d | 0.49 | 45 of 164 runs | 18,902 rows deferred; 8,946 fixture rows deferred in the run of 2026-11-24 9:00 AM PST | removed |
| rimflow/detached_helper.py:582 | timeout | 540 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 896 | 145 | user journal, 14 d (whole rm-list-dispatch run, upper bound) | 0.60 | 0 seen (journal, agent transcripts, 14 d) | a half-made clone | raised to 10800 |
| Utils/systemd/testq-tick.service:15 | TimeoutStartSec | 900 | systemd kills the run | NONE | 1386.2 | 17.6 | user journal, 14 d (12818 runs) | 0.65 | 6 | the SteveDesktop feed, steward and ingest of that tick | raised to 14400 |
| Utils/systemd/metronome_phases.json:6 | limit_s | 4 | the call, run or phase is ended | reason text in the file names the past runs, no danger | 5.7 | 0.4 | beats.jsonl, 14 d | 0.70 | 150 | one restart-reconcile pass lost, each | raised to 60 |
| infrastructure/stevedesktop/worker.py:986 | timeout | 600 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 827 | 74 | testq done records, 14 d (whole deploy phase, upper bound) | 0.73 | 0 | none | raised to 10800 |
| infrastructure/stevedesktop/worker.py:1479 | timeout | 600 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 827 | 74 | testq done records, 14 d (whole deploy phase, upper bound) | 0.73 | 0 | none | raised to 10800 |
| infrastructure/stevedesktop/worker.py:1445 | timeout | 180 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 241 | 10 | testq done records, 14 d (whole attest phase, upper bound) | 0.75 | 0 | none | raised to 2500 |
| Utils/publish_tree_checks.json:4 | timeout_s | 60 | the call, run or phase is ended | NONE | 80.2 | 14.5 | whole-list wall of 2758 publishes (agent transcripts, 14 d), an upper bound for one check | 0.75 | 0 | none | guard on progress, backstop 6000 |
| rimflow/dispatcher_schedule.json:85 | run_max_s#Operations | 1800 | the call, run or phase is ended | NONE | 2162 | 52 | control.db runs, 14 d (cut, so a floor) | 0.83 | 2 | two live runs cut with no result; one had used 1.35M weighted tokens | raised to 22000 |
| Utils/systemd/metronome_phases.json:6 | limit_s | 8 | the call, run or phase is ended | reason text in the file names the past runs, no danger | 9.1 | 0.6 | beats.jsonl, 14 d | 0.88 | 11 | one memory pass lost, each | raised to 100 |
| rimflow/maturation.py:2600 | timeout | 900 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 998 | 24 | user journal, 14 d (the whole tick that ran a biomes deploy, upper bound) | 0.90 | 0 | none | raised to 10800 |
| Utils/systemd/metronome_phases.json:6 | limit_s | 2 | the call, run or phase is ended | reason text in the file names the past runs, no danger | 2.1 | 0.1 | beats.jsonl, 14 d | 0.95 | 0 | none | raised to 30 |
| Utils/systemd/metronome_phases.json:6 | limit_s | 120 | the call, run or phase is ended | reason text in the file names the past runs, no danger | 125.3 | 6.4 | beats.jsonl, 14 d | 0.96 | 3029 sense reaches in 14 d (limits of 15 to 120 s) | a pair of reading families lost, each | raised to 1300 |
| Utils/systemd/rm-running.service:17 | TimeoutStartSec | 90 | systemd kills the run | NONE | 90.3 | 1.0 | user journal, 14 d (19732 runs) | 1.00 | 660 | the page stood stale for about 17 h in all; the cut runs had used 83 of their 90 s on the CPU | raised to 1800 |
| Utils/systemd/rm-memwatch.service:20 | TimeoutStartSec | 50 | systemd kills the run | NONE | 50.1 | 0.1 | user journal, 14 d (20091 runs) | 1.00 | 52 | 5 h of one day with no memory reading | raised to 600 |
| Utils/scratch_reap.py:856 | timeout | 900 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 900 | UNMEASURED | tmp_runs.jsonl (the find was cut, so the longest is a floor) | 1.00 | 2 | each made the borrower map partial, so that run could free nothing | guard on progress |
| rimflow/dispatcher_schedule.json:85 | run_max_s#DesignerCodex | 3600 | the call, run or phase is ended | NONE | 3600 | UNMEASURED | DISPATCHER.jsonl role_stop (cut, so a floor) | 1.00 | 1 | one live run stopped | raised to 37000 |
| Utils/run_selftests.py:76 | PER_TEST_TIMEOUT_S | 600 | the call, run or phase is ended | One hang guard for every test, never a speed bar: its danger, evidence and value are the LIMITS entry of design/specs/2026-11-22-selftest-de | 599 | under 5 | this run (slowest PASS, load 45); selftest_timings.json has a 533 s PASS | 1.00 | 3 (and 17 at the 240 s before 2026-11-22) | each read CRASH and turned its run red | guard on progress, backstop 6000 |
| Utils/follow_through.py:59 | LAUNCH_TIMEOUT_S | 900 | the call, run or phase is ended | hang guard: one detached_helper.py launch (a clone sync, a fetch) | 896 | 145 | user journal, 14 d (whole rm-list-dispatch run, upper bound) | 1.00 | UNMEASURED | a half-made clone | raised to 10800 |
| rimflow/list_dispatch.py:76 | LAUNCH_TIMEOUT_S | 900 | the call, run or phase is ended | Hang guard (the class of call_deadline_lint.py) for one `detached_helper.py launch` (a clone sync, a fetch). | 896 | 145 | user journal, 14 d (whole rm-list-dispatch run, upper bound) | 1.00 | UNMEASURED | a half-made clone | raised to 10800 |
| rimflow/maturation.py:2997 | timeout | 900 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 896 | 145 | user journal, 14 d (whole rm-list-dispatch run, upper bound) | 1.00 | 0 seen (journal, agent transcripts, 14 d) | a half-made clone | raised to 10800 |
| rimflow/maturation_autonomy.py:2159 | timeout | 900 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 896 | 145 | user journal, 14 d (whole rm-list-dispatch run, upper bound) | 1.00 | 0 seen (journal, agent transcripts, 14 d) | a half-made clone | raised to 10800 |
| rimflow/quiet_scan.py:54 | LAUNCH_TIMEOUT_S | 900 | the call, run or phase is ended | NONE | 896 | 145 | user journal, 14 d (whole rm-list-dispatch run, upper bound) | 1.00 | UNMEASURED | a half-made clone | raised to 10800 |
| rimflow/red_dispatch.py:320 | timeout | 900 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 896 | 145 | user journal, 14 d (whole rm-list-dispatch run, upper bound) | 1.00 | 0 seen (journal, agent transcripts, 14 d) | a half-made clone | raised to 10800 |
| Utils/systemd/rm-codebase-now.service:26 | TimeoutStartSec | 1200 | systemd kills the run | Danger: a hung run blocks every later page. Measured 2026-11-19: a full run with all 32 boundary tests files took 98 s; a cached run 1 s. On | 1108.2 | 4.1 | user journal, 14 d (445 runs) | 1.08 | 0 | none | raised to 11400 |
| Utils/systemd/metronome_phases.json:3 | budget_s | 45 | the call, run or phase is ended | reason text in the file names the past runs, no danger | 40.2 | 10.5 | user journal, 14 d (rm-metronome) | 1.12 | phases deferred (beats.jsonl) | the phase waits one beat | raised to 1500 |
| Utils/systemd/rm-metronome-sense.service:14 | TimeoutStartSec | 150 | systemd kills the run | A hang guard for the metronome process itself: above the phase's 120 s limit and 5 s cleanup. | 126 | 4.9 | user journal, 14 d (1882 runs) | 1.19 | 0 | none | raised to 1800 |
| Utils/systemd/rm-maturation-dispatch.service:19 | TimeoutStartSec | 1200 | systemd kills the run | NONE | 997.7 | 24.2 | user journal, 14 d (12062 runs) | 1.20 | 0 | none | raised to 10800 |
| Utils/testq/testq.py:2607 | timeout | 2700 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 2103 | 137 | testq done records, 14 d | 1.28 | 0 | none | raised to 21600 |
| Utils/systemd/rm-deploy-update.service:12 | TimeoutStartSec | 120 | systemd kills the run | NONE | 86.3 | 3.8 | user journal, 14 d (2380 runs) | 1.39 | 0 | none | raised to 900 |
| infrastructure/stevedesktop/worker.py:956 | timeout | 1200 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 827 | 74 | testq done records, 14 d (whole deploy phase, upper bound) | 1.45 | 0 | none | raised to 10800 |
| infrastructure/stevedesktop/worker.py:977 | timeout | 1200 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 827 | 74 | testq done records, 14 d (whole deploy phase, upper bound) | 1.45 | 0 | none | raised to 10800 |
| infrastructure/stevedesktop/worker.py:996 | timeout | 1200 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 827 | 74 | testq done records, 14 d (whole deploy phase, upper bound) | 1.45 | 0 | none | raised to 10800 |
| Utils/systemd/rm-streams-collect.service:12 | TimeoutStartSec | 420 | systemd kills the run | NONE | 288.6 | 30.9 | user journal, 14 d (1346 runs) | 1.46 | 0 | none | raised to 3000 |
| Utils/systemd/rm-scratch-reap.service:12 | TimeoutStartSec | 5400 | systemd kills the run | NONE | 3707.4 | 320.4 | user journal, 14 d (340 runs) | 1.46 | 0 | none | raised to 39600 |
| rimflow/designer_stage.py:2793 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 1.50 | 0 | none | raised to 21600 |
| Utils/systemd/rm-restart-now.service:10 | TimeoutStartSec | 420 | systemd kills the run | NONE | 272.9 | 0.1 | user journal, 14 d (122 runs) | 1.54 | 0 | none | raised to 3000 |
| rimflow/list_dispatch.py:78 | EFFECT_TIMEOUT_S | 900 | the call, run or phase is ended | Hang guard for `rimflow effect` (it runs the check once, then publishes). | 584 | 39.6 | user journal, 14 d (rm-list-effect, upper bound) | 1.54 | UNMEASURED | UNMEASURED | raised to 6000 |
| rimflow/maturation.py:2777 | timeout | 1800 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 998 | 24 | user journal, 14 d (the whole tick that ran a biomes deploy, upper bound) | 1.80 | 0 | none | raised to 10800 |
| Utils/systemd/rm-deadman.service:9 | TimeoutStartSec | 300 | systemd kills the run | NONE | 156.7 | 6.0 | user journal, 14 d (1345 runs) | 1.91 | 0 | none | raised to 1800 |
| rimflow/dispatcher_schedule.json:85 | run_max_s#Conductor | 1800 | the call, run or phase is ended | NONE | 887 | 123 | control.db runs, 14 d | 2.03 | 0 | none | raised to 9000 |
| Utils/systemd/rm-metronome.service:18 | TimeoutStartSec | 90 | systemd kills the run | NONE | 40.2 | 10.5 | user journal, 14 d (13600 runs) | 2.24 | 0 | none | raised to 3600 |
| infrastructure/stevedesktop/worker.py:619 | LOAD_TIMEOUT_S | 1500 | the call, run or phase is ended | `init && up --wait`: rw_game.sh waits up to RW_UP_WAIT_S (1200 s) for the bridge, after init and Steam. This outer limit guards a load comma | 602 | 6 | testq done records, 14 d | 2.49 | 0 | none | raised to 6300 |
| rimflow/maturation_dispatch.py:1380 | RERUN_MAX_S | 14400 | the call, run or phase is ended | NONE | 5325 | 542 | control.db runs, 14 d (31 cert_rerun) | 2.70 | 0 | none | raised to 54000 |
| Utils/testq/brake_release.py:175 | timeout | 7200 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 2554 | 221 | testq done records, 14 d | 2.82 | 0 | none | raised to 21600 |
| Utils/testq/testq.py:2314 | timeout | 7200 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 2554 | 221 | testq done records, 14 d | 2.82 | 0 | none | raised to 21600 |
| Utils/testq/visit_feed.py:467 | timeout | 7200 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 2554 | 221 | testq done records, 14 d | 2.82 | 0 | none | raised to 21600 |
| rimflow/seat_restart.py:3159 | timeout | 240 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 2.99 | 0 | none | raised to 21600 |
| rimflow/judge_certificate.py:42 | RUN_TIMEOUT_S | 1800 | the call, run or phase is ended | NONE | 599 | UNMEASURED | the slowest offline PASS on a loaded machine (this run) | 3.01 | UNMEASURED | a reach was written as result FAIL | raised to 6000 |
| Utils/systemd/rm-artpipe-idle-fill.service:26 | TimeoutStartSec | 4500 | systemd kills the run | NONE | 1353.5 | 6.1 | user journal, 14 d (671 runs) | 3.32 | 0 | none | raised to 13800 |
| Utils/testq/testq.py:1949 | timeout | 14400 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 4073 | 1059 | testq done records, 14 d | 3.54 | 0 | none | raised to 21600 |
| Utils/systemd/testq-steward-watch.service:8 | TimeoutStartSec | 300 | systemd kills the run | NONE | 81.7 | 0.1 | user journal, 14 d (19503 runs) | 3.67 | 0 | none | raised to 900 |
| rimflow/detached_helper.py:2160 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 3.74 | 0 | none | raised to 21600 |
| rimflow/maturation_autonomy.py:178 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 3.74 | 0 | none | raised to 21600 |
| rimflow/maturation_autonomy.py:461 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 3.74 | 0 | none | raised to 21600 |
| rimflow/maturation_autonomy.py:573 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 3.74 | 0 | none | raised to 21600 |
| rimflow/maturation_autonomy.py:771 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 3.74 | 0 | none | raised to 21600 |
| rimflow/maturation_autonomy.py:825 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 3.74 | 0 | none | raised to 21600 |
| rimflow/maturation_dispatch.py:3417 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 3.74 | 0 | none | raised to 21600 |
| Utils/systemd/rm-list-dispatch.service:25 | TimeoutStartSec | 3600 | systemd kills the run | Hang guard: a tick is a ledger replay, each item's check (list_effect.CMD_TIMEOUT_S each), and at most 2 launches (LAUNCH_TIMEOUT_S each). | 895.7 | 145.4 | user journal, 14 d (183 runs) | 4.02 | 0 | none | raised to 10800 |
| rimflow/dispatcher_schedule.json:4 | tick_budget_s | 420 | the call, run or phase is ended | NONE | 97 | UNMEASURED | metronome_phases.json text (old timer, 2026-11-06) | 4.33 | 0 | none | raised to 1000 |
| Utils/systemd/rm-maturation-page.service:24 | TimeoutStartSec | 600 | systemd kills the run | A hang guard, not a speed bar: a build stuck on a dead drvfs read or a git call never ends, and a oneshot that never ends never fires again. | 124.3 | 30.3 | user journal, 14 d (1136 runs) | 4.83 | 0 | none | raised to 1800 |
| Utils/systemd/rm-steve-fault.service:14 | TimeoutStartSec | 600 | systemd kills the run | NONE | 120.3 | 1.9 | user journal, 14 d (10125 runs) | 4.99 | 0 | none | raised to 1800 |
| Utils/systemd/rm-telemetry-health.service:8 | TimeoutStartSec | 30 | systemd kills the run | NONE | 5.7 | 0.1 | user journal, 14 d (10051 runs) | 5.26 | 0 | none | raised to 120 |
| Utils/systemd/rm-dispatcher.service:14 | TimeoutStartSec | 600 | systemd kills the run | NONE | 111.5 | 3.2 | user journal, 14 d (3065 runs) | 5.38 | 0 | none | raised to 1200 |
| Utils/scratch_reap.py:2815 | timeout | 900 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 165.2 | UNMEASURED | last_run.json phase_s.orphans (1 run) | 5.45 | 0 seen (journal, agent transcripts, 14 d) | UNMEASURED | guard on progress |
| rimflow/evidence_gate.py:77 | GIT_TIMEOUT_S | 5 | the call, run or phase is ended | NONE | 0.9 | 0.02 | 210 local git calls sampled at load 20 to 52, 2026-11-24 | 5.56 | 0 | none | raised to 60 |
| rimflow/dispatcher_schedule.json:85 | run_max_s#Designer | 2700 | the call, run or phase is ended | NONE | 464 | 49 | control.db runs, 14 d | 5.82 | 0 | none | raised to 9000 |
| rimflow/maturation.py:4340 | timeout | 480 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 5.99 | 0 | none | raised to 21600 |
| Utils/systemd/rm-list-effect.service:23 | TimeoutStartSec | 3600 | systemd kills the run | Hang guard: a beat is a ledger replay plus each check (CMD_TIMEOUT_S each) and a close per passing item. | 583.9 | 39.6 | user journal, 14 d (139 runs) | 6.17 | 0 | none | raised to 6000 |
| Utils/systemd/rm-red-dispatch.service:19 | TimeoutStartSec | 1200 | systemd kills the run | NONE | 187.5 | 1.3 | user journal, 14 d (630 runs) | 6.40 | 0 | none | raised to 1920 |
| Utils/systemd/rm-arteval-autojudge.service:25 | TimeoutStartSec | 3300 | systemd kills the run | NONE | 489.4 | 120.6 | user journal, 14 d (170 runs) | 6.74 | 0 | none | raised to 5400 |
| Utils/systemd/rm-ops-reds.service:15 | TimeoutStartSec | 900 | systemd kills the run | NONE | 126.8 | 1.5 | user journal, 14 d (1295 runs) | 7.10 | 0 | none | raised to 1800 |
| Utils/follow_through.py:60 | CLI_TIMEOUT_S | 600 | the call, run or phase is ended | hang guard: one rimflow write with --publish | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 7.48 | 0 | none | raised to 21600 |
| rimflow/role_clones.py:258 | timeout | 600 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 7.48 | 0 | none | raised to 21600 |
| Utils/systemd/rm-mirror.service:10 | TimeoutStartSec | 1800 | systemd kills the run | NONE | 235 | 22.2 | user journal, 14 d (1302 runs) | 7.66 | 0 | none | raised to 2400 |
| Utils/testq/gaps.py:52 | GIT_TIMEOUT_S | 30 | the call, run or phase is ended | NONE | 3.8 | 0.02 | 210 local git calls sampled at load 20 to 52, 2026-11-24 | 7.89 | 0 | none | raised to 60 |
| rimflow/modledger_backfill.py:911 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.8 | 2.9 | 30 path logs sampled at load 20 to 52, 2026-11-24 | 7.89 | 0 (journal and agent transcripts, 14 d) | none | raised to 60 |
| Utils/systemd/rm-account-usage.service:7 | TimeoutStartSec | 420 | systemd kills the run | NONE | 50.6 | 15.2 | user journal, 14 d (1343 runs) | 8.30 | 0 | none | raised to 600 |
| Utils/systemd/rm-findings-judge.service:13 | TimeoutStartSec | 5400 | systemd kills the run | NONE | 637.2 | 392.0 | user journal, 14 d (13 runs) | 8.47 | 0 | none | raised to 7200 |
| Utils/testq/stage6_checks.py:462 | timeout | 7200 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 822 | UNMEASURED | testq done records, 14 d (4 checks jobs) | 8.76 | 0 | none | raised to 28800 |
| Utils/testq/stage6_checks.py:537 | timeout | 7200 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 822 | UNMEASURED | testq done records, 14 d (4 checks jobs) | 8.76 | 0 | none | raised to 28800 |
| Utils/systemd/rm-vv-matrix.service:17 | TimeoutStartSec | 28800 | systemd kills the run | NONE | 3271.7 | 2342.8 | user journal, 14 d (11 runs) | 8.80 | 0 | none | raised to 36000 |
| Utils/systemd/rm-fleet-now.service:16 | TimeoutStartSec | 30 | systemd kills the run | NONE | 3.4 | 0.2 | user journal, 14 d (6600 runs) | 8.82 | 0 | none | raised to 60 |
| Utils/systemd/rm-telemetry-export.service:13 | TimeoutStartSec | 50 | systemd kills the run | NONE | 5.1 | 0.2 | user journal, 14 d (4398 runs) | 9.80 | 0 | none | raised to 60 |

## The other rows

| file:line | budget | s | ends | danger it named | longest real s | usual s | record | ratio | reaches, 14 d | cost of the reaches | after |
|---|---|---|---|---|---|---|---|---|---|---|---|
| infrastructure/stevedesktop/worker.py:293 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 333.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| infrastructure/stevedesktop/worker.py:423 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 333.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| infrastructure/stevedesktop/worker.py:1966 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 8571.43 | 0 | none | stays |
| Utils/call_deadline_lint.py:250 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/guiding_prose.py:57 | GIT_TIMEOUT_S | 60 | the call, run or phase is ended | a hang guard on local git reads (a stuck drvfs read), which take well under 1 s | 3.8 | 0.02 | 210 local git calls sampled at load 20 to 52, 2026-11-24 | 15.79 | 0 | none | stays |
| Utils/launch_permissions.py:307 | timeout | 120 | the call, run or phase is ended | hang guard | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/publish.py:83 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 33.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/publish.py:1266 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/run_selftests.py:349 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 33.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/run_selftests.py:432 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 2142.86 | 0 | none | stays |
| Utils/scratch_reap.py:232 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/scratch_reap.py:2207 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/scratch_reap.py:2786 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 2142.86 | 0 | none | stays |
| Utils/systemd/account-plan.service:7 | TimeoutStartSec | 2700 | systemd kills the run | NONE | 50.3 | 0.9 | user journal, 14 d (4031 runs) | 53.68 | 0 | none | stays |
| Utils/systemd/rm-artpiped.service:19 | TimeoutStopSec | 900 | systemd kills the run | NONE | 74.9 | 18.3 | user journal, 14 d (4 runs) | 12.02 | 0 | none | stays |
| Utils/systemd/rm-canon-sweep.service:19 | TimeoutStartSec | 420 | systemd kills the run | NONE | 25.3 | 0.2 | user journal, 14 d (528 runs) | 16.60 | 0 | none | stays |
| Utils/systemd/rm-close-check.service:20 | TimeoutStartSec | 3600 | systemd kills the run | Hang guard: two ledger replays, two git calls and one rimflow write per finding. | 36.8 | 20.3 | user journal, 14 d (2 runs) | 97.83 | 0 | none | stays |
| Utils/systemd/rm-control-acts-export.service:20 | TimeoutStartSec | 300 | systemd kills the run | NONE | 6.9 | 1.1 | user journal, 14 d (492 runs) | 43.48 | 0 | none | stays |
| Utils/systemd/rm-follow-through.service:23 | TimeoutStartSec | 3600 | systemd kills the run | Hang guard: a ledger replay, two rimflow writes (CLI_TIMEOUT_S each) and one launch (LAUNCH_TIMEOUT_S). | 42.5 | 23.5 | user journal, 14 d (2 runs) | 84.71 | 0 | none | stays |
| Utils/systemd/rm-guiding-prose.service:21 | TimeoutStartSec | 900 | systemd kills the run | Hang guard: the two throwaway doors (DOOR_TIMEOUT_S each) and one git log. | 2.5 | 1.1 | user journal, 14 d (3 runs) | 360.00 | 0 | none | stays |
| Utils/systemd/rm-host-facts.service:12 | TimeoutStartSec | 600 | systemd kills the run | NONE | 4.1 | 3.3 | user journal, 14 d (11 runs) | 146.34 | 0 | none | stays |
| Utils/systemd/rm-launch-permissions.service:21 | TimeoutStartSec | 600 | systemd kills the run | Hang guard: one git call, one ssh. | 20 | 16.0 | user journal, 14 d (7 runs) | 30.00 | 0 | none | stays |
| Utils/systemd/rm-objstore.service:19 | TimeoutStartSec | 900 | systemd kills the run | NONE | 89.9 | 20.4 | user journal, 14 d (336 runs) | 10.01 | 0 | none | stays |
| Utils/systemd/rm-order7.service:16 | TimeoutStartSec | 90 | systemd kills the run | NONE | 0.4 | 0.1 | user journal, 14 d (1344 runs) | 225.00 | 0 | none | stays |
| Utils/systemd/rm-quiet-scan.service:23 | TimeoutStartSec | 2400 | systemd kills the run | Hang guard: a tick is one git log of a week (GIT_TIMEOUT_S) and at most one launch (LAUNCH_TIMEOUT_S). | 30.5 | 12.5 | user journal, 14 d (34 runs) | 78.69 | 0 | none | stays |
| Utils/systemd/rm-run-alive.service:21 | TimeoutStartSec | 600 | systemd kills the run | Hang guard: a beat is a few reads for each live run and one ledger append for each lease that is due. | 49.9 | 7.3 | user journal, 14 d (114 runs) | 12.02 | 0 | none | stays |
| Utils/systemd/rm-seat-tidy.service:16 | TimeoutStartSec | 1800 | systemd kills the run | Hang guard on the unit (one fetch of 120 s and one land.sh of 600 s per clone are seat_dirt's own call guards). | 79.8 | 11.5 | user journal, 14 d (162 runs) | 22.56 | 0 | none | stays |
| Utils/systemd/rm-selftests-nightly-catchup.service:14 | TimeoutStartSec | 180 | systemd kills the run | NONE | 0.5 | 0.1 | user journal, 14 d (217 runs) | 360.00 | 0 | none | stays |
| Utils/systemd/rm-telemetry-pull.service:20 | TimeoutStartSec | 1200 | systemd kills the run | Danger: a hung run blocks every later pull. pull_games.HANG_S (15 min) ends a hung ssh first; the first pull of 136 MB took 99 s, a usual on | 28.9 | 6.0 | user journal, 14 d (704 runs) | 41.52 | 0 | none | stays |
| Utils/systemd/timer-guard.service:8 | TimeoutStartSec | 300 | systemd kills the run | NONE | 20.1 | 0.3 | user journal, 14 d (2016 runs) | 14.93 | 0 | none | stays |
| Utils/testq/brake_release.py:170 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/companion_stage.py:130 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/ingest.py:922 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 333.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/ingest.py:934 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 333.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/ingest.py:1010 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/ingest.py:1155 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/ingest.py:1158 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/ingest.py:1160 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/ingest.py:1170 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 333.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/lane_stop.py:80 | timeout | 20 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 1428.57 | 0 | none | stays |
| Utils/testq/repeat_guard.py:41 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 33.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/steward.py:359 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 2142.86 | 0 | none | stays |
| Utils/testq/steward.py:369 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 4285.71 | 0 | none | stays |
| Utils/testq/steward.py:385 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 2142.86 | 0 | none | stays |
| Utils/testq/testq.py:1373 | timeout | 60 | the call, run or phase is ended | a hang guard on a local read | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/testq.py:1906 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/testq.py:2304 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/testq.py:2465 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 33.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/testq.py:2535 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| Utils/testq/visit_feed.py:389 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/build_match.py:291 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.8 | 2.9 | 30 path logs sampled at load 20 to 52, 2026-11-24 | 15.79 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/control.py:1493 | timeout | 10 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 11.11 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/control.py:1915 | timeout | 5 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 357.14 | 0 | none | stays |
| rimflow/control_acts_export.py:49 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/control_acts_export.py:58 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/control_acts_export.py:146 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 33.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/coverage_calibration.py:398 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/designer_stage.py:572 | timeout | 20 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 22.22 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/designer_stage.py:575 | timeout | 20 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 22.22 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/designer_stage.py:2771 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/designer_stage.py:2778 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/designer_stage.py:2803 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/designer_stage.py:2919 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/designer_stage.py:2966 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/detached_helper.py:164 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/detached_helper.py:293 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.7 | 1.0 | 15 fetches sampled at load 20 to 52, 2026-11-24 | 32.43 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/detached_helper.py:300 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/detached_helper.py:527 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 333.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/detached_helper.py:1617 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 2142.86 | 0 | none | stays |
| rimflow/dispatcher.py:2684 | timeout | 10 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 714.29 | 0 | none | stays |
| rimflow/item_packet.py:24 | GIT_S | 120 | the call, run or phase is ended | hang guard | 3.8 | 0.02 | 210 local git calls sampled at load 20 to 52, 2026-11-24 | 31.58 | 0 | none | stays |
| rimflow/judge_certificate.py:291 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/judge_certificate.py:350 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/judge_certificate.py:398 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/judge_certificate.py:412 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/ledger_landing.py:21 | GIT_TIMEOUT_S | 60 | the call, run or phase is ended | hang guard on one `git rev-parse`/`ls-files` (a local read takes well under 1 s) | 3.8 | 0.02 | 210 local git calls sampled at load 20 to 52, 2026-11-24 | 15.79 | 0 | none | stays |
| rimflow/ledger_landing.py:22 | PUBLISH_TIMEOUT_S | 3600 | the call, run or phase is ended | hang guard on one ./publish: its own git calls are bounded at 300 s each, its checks run on top | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 44.89 | 0 | none | raised to 21600 |
| rimflow/list_effect.py:65 | CLOSE_TIMEOUT_S | 900 | the call, run or phase is ended | Hang guard for the `rimflow close` subprocess (a publish retries a push; minutes at worst). | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 11.22 | 0 | none | raised to 21600 |
| rimflow/list_effect.py:156 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:751 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.8 | 2.9 | 30 path logs sampled at load 20 to 52, 2026-11-24 | 15.79 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:755 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:758 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:1205 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:1494 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:1509 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:1944 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:1949 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:2577 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:3171 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:3463 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.8 | 2.9 | 30 path logs sampled at load 20 to 52, 2026-11-24 | 15.79 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:3467 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:3707 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:4277 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 33.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:4291 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 33.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:4310 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:4349 | timeout | 180 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 200.00 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:4372 | timeout | 240 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 266.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation.py:5350 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.8 | 2.9 | 30 path logs sampled at load 20 to 52, 2026-11-24 | 31.58 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_autonomy.py:276 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 2142.86 | 0 | none | stays |
| rimflow/maturation_autonomy.py:565 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_autonomy.py:728 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:1533 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:1537 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:1541 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:1585 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:1588 | timeout | 900 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 11.22 | 0 | none | raised to 21600 |
| rimflow/maturation_dispatch.py:1598 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:1637 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.8 | 2.9 | 30 path logs sampled at load 20 to 52, 2026-11-24 | 15.79 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:1846 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 33.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:2435 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:2439 | timeout | 180 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.7 | 1.0 | 15 fetches sampled at load 20 to 52, 2026-11-24 | 48.65 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:2453 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:2463 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:2543 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:2546 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:3411 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:3531 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 33.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/maturation_dispatch.py:4220 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 8571.43 | 0 | none | stays |
| rimflow/maturation_dispatch.py:4713 | timeout | 900 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 80.2 | 14.5 | tree-check wall of 2758 publishes (agent transcripts, 14 d); 584 s when a pipeline file is in the landing | 11.22 | 0 | none | raised to 21600 |
| rimflow/maturation_rescue.py:279 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/modledger.py:840 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.7 | 1.0 | 15 fetches sampled at load 20 to 52, 2026-11-24 | 16.22 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/modledger.py:842 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 33.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/modledger_backfill.py:872 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.8 | 2.9 | 30 path logs sampled at load 20 to 52, 2026-11-24 | 31.58 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/modledger_backfill.py:978 | timeout | 300 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.8 | 2.9 | 30 path logs sampled at load 20 to 52, 2026-11-24 | 78.95 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/modledger_sample.py:65 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.8 | 2.9 | 30 path logs sampled at load 20 to 52, 2026-11-24 | 15.79 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/quiet_scan.py:53 | GIT_TIMEOUT_S | 300 | the call, run or phase is ended | Hang guards (the class of call_deadline_lint.py), far above a real run: the week's `git log` took 6 s (2026-11-24). | 3.8 | 0.02 | 210 local git calls sampled at load 20 to 52, 2026-11-24 | 78.95 | 0 | none | stays |
| rimflow/rerun_relation.py:76 | timeout | 120 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/role_clones.py:200 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/role_clones.py:251 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/role_launch.py:3512 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 2142.86 | 0 | none | stays |
| rimflow/role_launch.py:3527 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 2142.86 | 0 | none | stays |
| rimflow/role_launch.py:3542 | timeout | 30 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 2142.86 | 0 | none | stays |
| rimflow/run_void.py:926 | timeout | 120 | the call, run or phase is ended | hang guard on a slow mount; a real status takes about 2 s | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 133.33 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/run_void.py:971 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.8 | 2.9 | 30 path logs sampled at load 20 to 52, 2026-11-24 | 15.79 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/run_void.py:973 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/seat_restart.py:760 | timeout | 10 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 714.29 | 0 | none | stays |
| rimflow/seat_restart.py:2874 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/seat_restart.py:2893 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/seat_restart.py:2896 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 3.8 | 2.9 | 30 path logs sampled at load 20 to 52, 2026-11-24 | 15.79 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/seat_restart.py:2916 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/seat_restart.py:3566 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.9 | 0.02 | 180 local git calls of 6 kinds sampled at load 20 to 52, 2026-11-24 | 66.67 | 0 (journal and agent transcripts, 14 d) | none | stays |
| rimflow/seat_restart.py:3929 | timeout | 60 | the call, run or phase is ended | class: a call hang guard (call_deadline_lint.py; a hung copy held a seat 4 h, 2026-11-02) | 0.014 | 0.007 | 30 calls sampled, 2026-11-24 | 4285.71 | 0 | none | stays |

## The 270 with no record, classed by their danger

Item `RIMMANDRAKE_MEASURE_EVERY_UNMEASURED_TIME_BUDGET_HE_CALLED_IT_LAZINESS`, 2026-11-24. Owner: *"if no one ever looks, and we
can't see a value now, shouldn't we just delete it?"* Nothing was run only to time it. Each site was read in the code. The
records that exist were joined: the user journal, the agent transcripts, `control.db`, `tick_steps.jsonl`, `stage_timings.jsonl`
and the SteveDesktop job results, 14 days to 2026-11-24.

| class | budgets |
|---|---|
| NO DANGER, removed | 3 |
| RECORD, under 10 times its longest run, raised (4 of them by the first run) | 36 |
| RECORD, value stays | 23 |
| replaced by a guard on progress | 0 |
| NEVER REACHED: a danger is named, no reach in the 14 days, no record of its run | 91 |
| REACH NOT RECORDED: a danger is named, and the code swallows its own timeout, so a reach could not have been seen | 30 |
| ENDS NO WORK: a refresh, an alarm, a wait, a size. The danger is named | 93 |
| all: the 270, and 6 that the first run had counted as measured or had added | 276 |

- **Judge (LLM) call times are in the agent transcripts** (first to last line of the session): COVERAGE JUDGE 198 and 462 s
  (2 sessions), coverage calibration case 166 s at most of 119, art calibration case 134 s of 100, second reader 13 s of 17,
  criteria fixer 17 s (1). The reader of `guiding_prose.py` keeps no session; its 4 to 13 s is a note of 2026-11-23.
- **One record stood for unlike budgets.** 9 entries of `time_budgets.json` held one `longest_s` for two or more different
  budgets of one function (a 0.9 s git read and a 300 s ssh). The lint refuses that now, and each budget has its own tag.
- `"RuntimeMaxSec=1800"` in four argument lists (a string, which the lint does not read) stood at 6 times the longest clone
  return (289 s) and 2 times the longest launch (896 s, an upper bound). Raised to 3600 and 10800.

| file:line (at 24841afcbf) | budget | s | class | danger, or why removed | longest real s | record, or what happens when the time passes | change |
|---|---|---|---|---|---|---|---|
| .claude/hooks/role_result_before_stop.py:28 | TIMEOUT_S | 45 | NEVER REACHED | a hung result check holds a role run open at its stop |  |  | stays |
| infrastructure/stevedesktop/bootstrap_wsl.sh:127 | timeout | 25 | NO DANGER | tailscale ends itself (`--timeout=20s`) |  |  | removed |
| infrastructure/stevedesktop/preflight.py:184 | timeout | 30 | NEVER REACHED | a hung reg.exe or sc.exe (WSL interop) holds the SteveDesktop worker's preflight, and so the lane |  |  | stays |
| infrastructure/stevedesktop/preflight.py:195 | timeout | 30 | NEVER REACHED | a hung reg.exe or sc.exe (WSL interop) holds the SteveDesktop worker's preflight, and so the lane |  |  | stays |
| infrastructure/stevedesktop/preflight.py:236 | timeout | 180 | RECORD | a hung modset_builder holds the SteveDesktop worker's preflight, and so the lane | 241 | the whole attest phase, an upper bound; testq done records, 14 days to 2026-11-24 | raised to 2500 |
| infrastructure/stevedesktop/serve_bootstrap.sh:37 | timeout | 70 | NO DANGER | the server ends itself (`--minutes 1`) |  |  | removed |
| infrastructure/stevedesktop/sync_test_mods.py:109 | timeout | 300 | REACH NOT RECORDED | a hung ssh holds the sync, and the tick that runs it |  |  | stays |
| infrastructure/stevedesktop/sync_test_mods.py:123 | timeout | 120 | REACH NOT RECORDED | a hung ssh holds the sync, and the tick that runs it |  |  | stays |
| infrastructure/stevedesktop/sync_test_mods.py:137 | timeout | 600 | NEVER REACHED | a hung ssh holds the push, and the tick that runs it |  |  | stays |
| infrastructure/stevedesktop/sync_test_mods.py:176 | timeout | 1800 | NEVER REACHED | a hung ssh holds the push, and the tick that runs it |  |  | stays |
| infrastructure/stevedesktop/sync_test_mods.py:194 | timeout | 60 | REACH NOT RECORDED | a hung ssh holds the sync, and the tick that runs it |  |  | stays |
| infrastructure/stevedesktop/verify_from_archmagi.sh:78 | timeout | 5 | REACH NOT RECORDED | a dead port holds the verify script with no end |  |  | stays |
| infrastructure/stevedesktop/worker.py:167 | DUMP_TIMEOUT_S | 180 | NEVER REACHED | a hung minidump of a hung game holds the kill of that game |  |  | stays |
| infrastructure/stevedesktop/worker.py:168 | PROBE_TIMEOUT_S | 30 | NEVER REACHED | a wedged kept game holds the lane at its bridge probe |  |  | stays |
| infrastructure/stevedesktop/worker.py:719 | timeout | 60 | NEVER REACHED | a hung systemd-run holds the spawn of the worker, and so the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:776 | timeout | 120 | NEVER REACHED | a hung repair of the mod list holds the lane's reset |  |  | stays |
| infrastructure/stevedesktop/worker.py:812 | timeout | 120 | NEVER REACHED | a hung closure read holds the attempt, and so the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:918 | timeout | 10 | REACH NOT RECORDED | a child that ignores SIGTERM holds the attempt; SIGKILL follows |  |  | stays |
| infrastructure/stevedesktop/worker.py:951 | timeout | 300 | NEVER REACHED | a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:993 | timeout | 300 | NEVER REACHED | a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:1076 | timeout | 300 | NEVER REACHED | a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:1133 | timeout | 300 | NEVER REACHED | a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:1167 | timeout | 300 | NEVER REACHED | a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:1329 | timeout | 120 | NEVER REACHED | a hung bridge client holds the attempt, and so one game of the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:1345 | timeout | 120 | NEVER REACHED | a hung status command holds the attempt, and so one game of the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:1376 | timeout | 120 | NEVER REACHED | a hung bridge client holds the attempt, and so one game of the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:1474 | timeout | 300 | NEVER REACHED | a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:1617 | timeout | 300 | NEVER REACHED | a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:1664 | timeout | 300 | NEVER REACHED | a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane |  |  | stays |
| infrastructure/stevedesktop/worker.py:1716 | timeout | 30 | REACH NOT RECORDED | a hung wslpath holds the dump of a hung game, and the kill after it |  |  | stays |
| infrastructure/stevedesktop/worker.py:1745 | timeout | 300 | NEVER REACHED | a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane |  |  | stays |
| Utils/game_watcher.py:15 | STALL_S | 60 | ENDS NO WORK | a stalled main thread read as healthy |  | a silence this long reads STALLED and a dump is written; the game goes on | stays |
| Utils/game_watcher.py:16 | LOAD_S | 600 | ENDS NO WORK | a stuck load read as a slow load (MapInitializing stall, 2026-10-26) |  | a load this old reads stuck_load; the game goes on | stays |
| Utils/guiding_prose.py:51 | READER_TIMEOUT_S | 300 | RECORD | a model call that never returns keeps the writer's ./publish open after the landing | 13 | real calls of 4 to 13 s on 61 to 434 sentences, 2026-11-23 | stays |
| Utils/guiding_prose.py:58 | DOOR_TIMEOUT_S | 180 | RECORD | a hung throwaway landing or launch holds the recheck | 5 | each took 2 to 5 s | stays |
| Utils/launch_permissions.py:467 | timeout | 60 | NEVER REACHED | a hung probe (ssh to another machine) holds the permission check |  |  | stays |
| Utils/maturation_nonmod.py:38 | RED_STALE_S | 1800 | ENDS NO WORK | a dead rm-red-dispatch.timer leaves the red list silently old |  | the page says that the reading is old | stays |
| Utils/maturation_now.py:497 | LONG_RUN_S | 3600 | ENDS NO WORK | a long run is not seen on the page |  | the page marks the run as long | stays |
| Utils/maturation_trend.py:34 | STALE_DAYS | 604800 | ENDS NO WORK | the old backlog hides the week's change |  | the trend leaves the ticket out | stays |
| Utils/no_home.py:37 | TTL_S | 300 | ENDS NO WORK | both pages recount on every build |  | the count is made again | stays |
| Utils/progress_guard.py:27 | SILENCE_S | 1800 | NEVER REACHED | a hung child holds its caller with no end (new on 2026-11-24) |  |  | stays |
| Utils/progress_guard.py:105 | timeout | 15 | REACH NOT RECORDED | a killed child in uninterruptible IO never reaps |  |  | stays |
| Utils/publish.py:462 | timeout | 1200 | NEVER REACHED | a hung winbuild holds a landing |  |  | stays |
| Utils/publish.py:1110 | CHECKTREE_STALE_S | 3600 | RECORD | the sweep deletes the check tree of a live landing | 584 | the longest door-check wall of 636 publishes, 14 days to 2026-11-24; one check may now take 6000 s | raised to 21600 |
| Utils/publish_tree_checks.json:3 | budget_s | 30 | NO DANGER | none: a speed bar on the list of door checks |  |  | removed |
| Utils/rimbridge_client.py:271 | LOAD_READY_WAIT_S | 180 | NEVER REACHED | a game that never reads Playing holds the caller after a load reply (live r8: stuck over 3 min) |  |  | stays |
| Utils/rimbridge_client.py:339 | STALL_DUMP_SECONDS | 60 | ENDS NO WORK | a stalled call with no pointer to its stall dump |  | the call's end row names the dumps | stays |
| Utils/rimbridge_client.py:634 | JOURNAL_READ_TIMEOUT_S | 10 | NEVER REACHED | a hung journal read holds every mutating call |  |  | stays |
| Utils/rimbridge_client.py:909 | DEADLINE_MARGIN_S | 10 | ENDS NO WORK | a kill in mid call strands an UNKNOWN-outcome marker that refuses every later mutation |  | a mutation that could not finish before the caller's own kill does not start | stays |
| Utils/rimbridge_client.py:910 | DEADLINE_MIN_CALL_S | 30 | ENDS NO WORK | a kill in mid call strands an UNKNOWN-outcome marker that refuses every later mutation |  | a mutation that could not finish before the caller's own kill does not start | stays |
| Utils/rimbridge_client.py:1070 | timeout | 30 | NEVER REACHED | a dead bridge holds its caller |  |  | stays |
| Utils/rimbridge_client.py:1070 | connect_timeout | 5 | NEVER REACHED | a dead bridge holds its caller |  |  | stays |
| Utils/rimbridge_client.py:1692 | timeout | 30 | NEVER REACHED | a dead bridge holds its caller |  |  | stays |
| Utils/run_selftests.py:466 | timeout | 60 | NEVER REACHED | a hung systemd-run holds the runner before its first test |  |  | stays |
| Utils/run_selftests.py:550 | timeout | 15 | ENDS NO WORK | a descendant that escaped the group holds the pipe, and the whole runner (audit 7) |  | the test has ended; its pipe is closed and its result stands | stays |
| Utils/run_selftests.py:1375 | timeout | 1 | ENDS NO WORK | the runner reads the memory only when a test ends |  | a poll; the loop waits again | stays |
| Utils/scene.py:42 | STALL_S | 60 | ENDS NO WORK | a run whose clock stands still never ends (a window that pauses the game) |  | the silence bound of a progress guard: a clock that moves starts it again | stays |
| Utils/scene.py:43 | SETTLE_S | 600 | NEVER REACHED | a load that never settles holds the scene and its game |  |  | stays |
| Utils/scene.py:363 | timeoutMs | 280000 | NEVER REACHED | a load that never answers holds the scene and its game |  |  | stays |
| Utils/scene_world.py:17 | CALL_TIMEOUT_S | 600 | NEVER REACHED | a bridge call that never answers holds the scene and its game |  |  | stays |
| Utils/scene_world.py:121 | timeout | 60 | NEVER REACHED | a hung wsl.exe (interop) holds the lock take, and so the scene |  |  | stays |
| Utils/scene_world.py:232 | timeout | 120 | NEVER REACHED | a hung git (interop, drvfs) holds the scene and its game |  |  | stays |
| Utils/scratch_reap.py:130 | FIXTURE_TTL_S | 86400 | ENDS NO WORK | test fixtures fill /tmp (owner-authority brief, 2026-11-01) |  | a fixture this old may go; an open one is held by its process | stays |
| Utils/scratch_reap.py:154 | BORROW_REFRESH_S | 120 | ENDS NO WORK | the borrower list is stale while the run deletes |  | the list is read again | stays |
| Utils/scratch_reap.py:239 | timeout | 600 | NEVER REACHED | a hung git holds the cleaner, and the disk fills |  |  | stays |
| Utils/scratch_reap.py:983 | timeout | 300 | NEVER REACHED | a hung git holds the cleaner, and the disk fills |  |  | stays |
| Utils/scratch_reap.py:1364 | CORPUS_REFRESH_S | 60 | ENDS NO WORK | an item filed in mid run does not reserve its clone |  | the ledger text is read again | stays |
| Utils/scratch_reap.py:1839 | timeout | 1800 | NEVER REACHED | a hung git holds the cleaner, and the disk fills |  |  | stays |
| Utils/scratch_reap.py:1843 | timeout | 1800 | NEVER REACHED | a hung git holds the cleaner, and the disk fills |  |  | stays |
| Utils/scratch_reap.py:1860 | timeout | 1800 | NEVER REACHED | a hung git holds the cleaner, and the disk fills |  |  | stays |
| Utils/scratch_reap.py:1874 | timeout | 1800 | NEVER REACHED | a hung git holds the cleaner, and the disk fills |  |  | stays |
| Utils/scratch_reap.py:1889 | timeout | 1800 | NEVER REACHED | a hung git holds the cleaner, and the disk fills |  |  | stays |
| Utils/scratch_reap.py:1896 | timeout | 1800 | NEVER REACHED | a hung git holds the cleaner, and the disk fills |  |  | stays |
| Utils/scratch_reap.py:1960 | timeout | 1800 | NEVER REACHED | a hung tar holds the cleaner, and the disk fills |  |  | stays |
| Utils/scratch_reap.py:1963 | timeout | 600 | NEVER REACHED | a hung tar holds the cleaner, and the disk fills |  |  | stays |
| Utils/slot_rules.json:83 | stale_min | 2700 | ENDS NO WORK | a dead ops reading steers the allocator |  | the old reading is reported and not used | stays |
| Utils/slot_rules.json:91 | steve_stall_min | 1800 | ENDS NO WORK | a stalled SteveDesktop lane goes unseen |  | the allocator reads the lane as stalled | stays |
| Utils/systemd/metronome_phases.json:6 | cleanup_s | 5 | REACH NOT RECORDED | a phase that ignores SIGTERM holds the one beat lock; SIGKILL follows |  |  | stays |
| Utils/systemd/metronome_phases.json:6 | cleanup_s | 2 | REACH NOT RECORDED | a phase that ignores SIGTERM holds the one beat lock; SIGKILL follows |  |  | stays |
| Utils/systemd/metronome_phases.json:6 | cleanup_s | 2 | REACH NOT RECORDED | a phase that ignores SIGTERM holds the one beat lock; SIGKILL follows |  |  | stays |
| Utils/systemd/metronome_phases.json:6 | cleanup_s | 2 | REACH NOT RECORDED | a phase that ignores SIGTERM holds the one beat lock; SIGKILL follows |  |  | stays |
| Utils/systemd/metronome_phases.json:6 | cleanup_s | 3 | REACH NOT RECORDED | a phase that ignores SIGTERM holds the one beat lock; SIGKILL follows |  |  | stays |
| Utils/systemd/metronome_phases.json:6 | limit_s | 100 | ENDS NO WORK | the beat's reserve sum needs a number for each phase |  | no command runs in this phase | stays |
| Utils/systemd/metronome_phases.json:6 | cleanup_s | 2 | REACH NOT RECORDED | a phase that ignores SIGTERM holds the one beat lock; SIGKILL follows |  |  | stays |
| Utils/testq/archmagi_phases.py:59 | timeout | 60 | NEVER REACHED | a hung Windows program (interop) holds the Archmagi lane |  |  | stays |
| Utils/testq/archmagi_phases.py:75 | timeout | 600 | RECORD | a hung deploy holds its caller and the game copy with no end | 998 | class `deploy` (time_budget.py) | raised to 10800 |
| Utils/testq/archmagi_phases.py:114 | timeout | 30 | NEVER REACHED | a hung Windows program (interop) holds the Archmagi lane |  |  | stays |
| Utils/testq/archmagi_phases.py:115 | timeout | 120 | NEVER REACHED | a hung Windows program (interop) holds the Archmagi lane |  |  | stays |
| Utils/testq/archmagi_phases.py:138 | timeout | 60 | NEVER REACHED | a dead bridge holds the Archmagi lane |  |  | stays |
| Utils/testq/archmagi_switch.py:37 | OLDEST_WAIT_S | 1800 | ENDS NO WORK | Archmagi takes SteveDesktop's work while SteveDesktop keeps up |  | a ready job this old may turn the backfill on | stays |
| Utils/testq/archmagi_switch.py:41 | COOLDOWN_S | 1800 | ENDS NO WORK | the backfill turns on and off at each reading |  | the switch waits before it turns on again | stays |
| Utils/testq/archmagi_switch.py:46 | LOAD_S | 900 | ENDS NO WORK | a load that costs more than the work it serves |  | a size that the rule compares; nothing is timed by it | stays |
| Utils/testq/archmagi_switch_reading.py:38 | max_age_s | 7200 | ENDS NO WORK | a dead switch read as a live one |  | the reading says that it is old | stays |
| Utils/testq/brake_release.py:39 | RELEASE_GRACE_S | 1800 | ENDS NO WORK | a known brake that nobody releases |  | the steward's ladder starts | stays |
| Utils/testq/companion_stage.py:51 | BUILD_TIMEOUT_S | 420 | NEVER REACHED | a hung winbuild holds the testq tick (its queue on the shared stage lock included) |  |  | stays |
| Utils/testq/companion_stage.py:53 | PROOF_MAX_AGE_S | 7200 | ENDS NO WORK | an old proof read as a current one |  | the proof reads old | stays |
| Utils/testq/companion_stage.py:82 | timeout | 120 | REACH NOT RECORDED | a hung ssh holds the testq tick |  |  | stays |
| Utils/testq/coverage.py:47 | PROBE_TIMEOUT_S | 60 | NEVER REACHED | a hung modcheck preview holds the coverage table |  |  | stays |
| Utils/testq/fault_monitor.py:68 | BOOT_TIMEOUT_S | 2400 | ENDS NO WORK | a reboot of SteveDesktop that never comes back goes unseen |  | the monitor says so and raises its alarm | stays |
| Utils/testq/fault_monitor.py:69 | BLIND_S | 1200 | ENDS NO WORK | a dead canary read as a clean one |  | the monitor says that the canary is blind | stays |
| Utils/testq/fault_monitor.py:70 | HOLD_S | 7200 | ENDS NO WORK | a result with no clean canary cycle waits for ever |  | the result counts, marked unguarded | stays |
| Utils/testq/fault_monitor.py:71 | STALE_S | 1800 | ENDS NO WORK | an old reading read as a current one |  | the reading says nothing | stays |
| Utils/testq/fault_monitor.py:278 | timeout | 120 | NEVER REACHED | a hung ssh to SteveDesktop holds the fault monitor |  |  | stays |
| Utils/testq/fault_monitor.py:373 | timeout | 180 | NEVER REACHED | a hung ssh to SteveDesktop holds the fault monitor |  |  | stays |
| Utils/testq/fault_monitor.py:731 | timeout | 300 | NEVER REACHED | a hung ssh to SteveDesktop holds the fault monitor |  |  | stays |
| Utils/testq/gaps.py:54 | PROBE_TIMEOUT_S | 480 | RECORD | a hung probe holds the ranking of the fill; evidence=at 120 s the ranking went blind | 118 | a FlowWorks probe at load 20, 2026-11-24 | raised to 1200 |
| Utils/testq/host_facts.py:24 | MAX_AGE_S | 7200 | ENDS NO WORK | old facts of a host read as current |  | the facts are read again | stays |
| Utils/testq/host_facts.py:164 | timeout | 180 | NEVER REACHED | a hung ssh holds the host facts |  |  | stays |
| Utils/testq/ingest.py:81 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| Utils/testq/ingest.py:121 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| Utils/testq/ingest.py:1013 | STALE_LOCK_S | 300 | ENDS NO WORK | a live git's index.lock is removed, or a dead one stops every publish |  | a lock this old with no live git process is removed | stays |
| Utils/testq/ingest.py:1015 | FRESH_LOCK_WAIT_S | 10 | ENDS NO WORK | a fresh index.lock of a live git stops the publish |  | a short wait for the lock; then the publish says why it stopped | stays |
| Utils/testq/ingest.py:1140 | timeout | 120 | NEVER REACHED | a hung ledger_lint holds the ingest lock |  |  | stays |
| Utils/testq/regprobe_log.py:25 | STALE_CYCLES | 3 | ENDS NO WORK | a dead probe read as a live one |  | a count of cycles, no time: the probe reads as not running | stays |
| Utils/testq/retest.py:228 | timeout | 60 | NEVER REACHED | a hung ssh holds the retest |  |  | stays |
| Utils/testq/stage6_checks.py:34 | FRESH | 1e+08 | ENDS NO WORK | live_site refuses an old test game as a colony |  | a tick count that the site check is given | stays |
| Utils/testq/stage6_checks.py:408 | timeout | 60 | REACH NOT RECORDED | a hung wslpath holds one game of the lane |  |  | stays |
| Utils/testq/stage6_site.py:45 | timeout | 120 | NEVER REACHED | a dead bridge holds one game of the lane |  |  | stays |
| Utils/testq/steward.py:116 | READY_GRACE_S | 300 | ENDS NO WORK | a ready lane that nobody works goes unseen |  | the steward's clock starts | stays |
| Utils/testq/steward.py:118 | CLAIM_HOLD_S | 7200 | ENDS NO WORK | a claim with no lease holds the escalation for ever |  | the steward's clock runs again | stays |
| Utils/testq/steward.py:119 | LOCK_WAIT_S | 30 | ENDS NO WORK | two passes wait on each other |  | the pass is skipped; the next timer beat runs it | stays |
| Utils/testq/steward.py:120 | STALE_S | 300 | ENDS NO WORK | a dead steward goes unseen |  | the watcher says that the steward is stale | stays |
| Utils/testq/steward.py:144 | COMPANION_GRACE_S | 900 | ENDS NO WORK | a hold that outlasts a build and a push goes unseen |  | the steward's clock starts | stays |
| Utils/testq/steward.py:309 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| Utils/testq/steward.py:517 | timeout | 60 | RECORD | a hung launch holds the steward's pass | 1.3 | admission to start of 1057 runs, control.db | stays |
| Utils/testq/steward.py:549 | timeout | 120 | NEVER REACHED | a hung git pull holds the steward's pass |  |  | stays |
| Utils/testq/testq.py:219 | HUNG_S | 300 | ENDS NO WORK | a worker that stopped its heartbeat reads as running (ticks stalled 7 to 15 min, Nov 21 and 23) |  | a wait reads HUNG; the job goes on | stays |
| Utils/testq/testq.py:380 | timeout | 180 | NEVER REACHED | a hung ssh or worker call holds the testq tick |  |  | stays |
| Utils/testq/testq.py:399 | timeout | 60 | NEVER REACHED | a hung ssh or worker call holds the testq tick |  |  | stays |
| Utils/testq/testq.py:811 | timeout | 900 | NEVER REACHED | a hung copy of the site saves holds the testq tick |  |  | stays |
| Utils/testq/testq.py:830 | ARCH_SILENT_S | 600 | ENDS NO WORK | the Archmagi backfill starts between two calls of a driver |  | the backfill waits for the next tick | stays |
| Utils/testq/testq.py:987 | timeout | 180 | NEVER REACHED | a hung ssh or worker call holds the testq tick |  |  | stays |
| Utils/testq/testq.py:1093 | YIELD_GRACE_S | 180 | ENDS NO WORK | a bridge take waits for the whole attempt |  | the taker waits this long for a row boundary, then takes the game, as it ordered | stays |
| Utils/testq/testq.py:1408 | timeout | 60 | REACH NOT RECORDED | a hung modcheck preview holds the submit |  |  | stays |
| Utils/testq/tier_load.py:68 | timeout | 60 | NEVER REACHED | a dead bridge holds one game of the lane |  |  | stays |
| Utils/testq/visit_feed.py:37 | READING_MAX_AGE_S | 1800 | ENDS NO WORK | a check is read from a dead dispatch step, and may have run already |  | the feed says that the reading is old | stays |
| Utils/testq/visit_feed.py:45 | FAULT_BACKOFF_MAX_S | 7200 | ENDS NO WORK | a chain is sent again every tick into the same fault (20 h of lane lost, 2026-10-25) |  | the longest wait before the chain is sent again | stays |
| Utils/waitalive.py:25 | MAX_WAIT_S | 3300 | ENDS NO WORK | the wait outlives the one-hour prompt cache |  | it reads STILL RUNNING; attach waits again | stays |
| Utils/waitalive.py:26 | SILENCE_S | 600 | ENDS NO WORK | a hung job holds its caller |  | the silence bound of a progress guard: it reads HUNG and kills nothing | stays |
| Utils/waitalive.py:29 | START_S | 30 | NEVER REACHED | a supervisor that never starts holds its caller |  |  | stays |
| rimflow/art_calibration.py:67 | CASE_TIMEOUT_S | 1500 | RECORD | a judge call that never returns holds the calibration | 134 | 100 case sessions, agent transcripts, 14 days to 2026-11-24 | stays |
| rimflow/art_calibration.py:186 | timeout | 30 | NEVER REACHED | a hung agent_storage.py holds the calibration |  |  | stays |
| rimflow/card_capture.py:63 | timeout | 30 | NEVER REACHED | a hung agent_storage.py holds the card record |  |  | stays |
| rimflow/card_capture.py:536 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| rimflow/close_check.py:31 | MAX_AGE_S | 129600 | ENDS NO WORK | the close check stops and nobody sees it (2026-11-01 to 2026-11-23) |  | the dead-man alarms | stays |
| rimflow/conductor_acts.py:188 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| rimflow/control.py:112 | WRITE_NOW_DEADLINE_S | 300 | RECORD | a run that is told to write now never stops; evidence=3 of 15 write_now stops reached it and were escalated | 599 | control.db stops, 14 days to 2026-11-24 | stays |
| rimflow/control.py:113 | KILL_WAIT_S | 1 | REACH NOT RECORDED | a process that does not die, or a locked store, holds a kill |  |  | stays |
| rimflow/control.py:114 | KILL_STORE_WAIT_S | 0.2 | REACH NOT RECORDED | a process that does not die, or a locked store, holds a kill |  |  | stays |
| rimflow/control.py:213 | timeout | 3 | REACH NOT RECORDED | a locked store holds its caller |  |  | stays |
| rimflow/control.py:237 | timeout | 5 | REACH NOT RECORDED | a locked store holds its caller |  |  | stays |
| rimflow/control.py:252 | timeout | 3 | REACH NOT RECORDED | a locked store holds its caller |  |  | stays |
| rimflow/control.py:281 | timeout | 1.5 | REACH NOT RECORDED | a locked store holds its caller |  |  | stays |
| rimflow/control.py:1786 | timeout | 10 | REACH NOT RECORDED | a hung journal holds the hook of a live run |  |  | stays |
| rimflow/control.py:1941 | timeout | 10 | NEVER REACHED | a hung systemd holds the pipeline's control |  |  | stays |
| rimflow/control.py:2307 | timeout | 10 | RECORD | a hung systemd-run holds the stop | 1.3 | admission to start of 1057 runs, control.db | raised to 30 |
| rimflow/control.py:2383 | timeout | 10 | RECORD | a hung systemd-run holds the stop | 1.3 | admission to start of 1057 runs, control.db | raised to 30 |
| rimflow/control.py:2416 | timeout | 0.5 | REACH NOT RECORDED | a locked store holds a hook of a live run |  |  | stays |
| rimflow/coverage_calibration.py:75 | CASE_TIMEOUT_S | 1200 | RECORD | a judge call that never returns holds the calibration | 166 | 119 case sessions, agent transcripts, 14 days to 2026-11-24 | raised to 1800 |
| rimflow/coverage_judge.py:86 | TIMEOUT_S | 1500 | RECORD | a judge (LLM) call that never returns holds its caller with no end | 462 | class `judge` (time_budget.py) | stays (its file is the calibrated brief); role_launch passes 5400 |
| rimflow/coverage_judge.py:89 | READER_TIMEOUT_S | 600 | RECORD | a reader call that never returns holds the judge | 13 | 17 second readers, agent transcripts, 14 days to 2026-11-24 | stays |
| rimflow/detached_helper.py:90 | MIN_MAX_S | 60 | ENDS NO WORK | a wall bound under one minute ends a run before its first turn |  | a launch that asks for it is refused, with the repair | stays |
| rimflow/detached_helper.py:91 | STOP_S | 600 | RECORD | a stopped run that never ends holds its clone | 584 | the stop steps hold a publish: the longest of 636 | stays |
| rimflow/detached_helper.py:92 | GRACE_S | 120 | NEVER REACHED | a run with a wall bound is ended while it finishes and publishes |  |  | stays |
| rimflow/detached_helper.py:107 | LAUNCH_GRACE_S | 120 | ENDS NO WORK | a launching run with no unit yet reads as dead |  | the record reads as a dead launch | stays |
| rimflow/detached_helper.py:108 | RETURN_WAIT_S | 600 | RECORD | a return that never ends holds the launch | 289 | 1151 return units, user journal, 14 days to 2026-11-24 | raised to 3000 |
| rimflow/detached_helper.py:334 | timeout | 600 | RECORD | a hung ./publish or land.sh holds its caller with no end | 584 | class `publish` (time_budget.py) | raised to 21600 |
| rimflow/detached_helper.py:722 | REAP_TERM_WAIT_S | 5 | REACH NOT RECORDED | a process that never exits holds the return, and so the clone |  |  | stays |
| rimflow/detached_helper.py:872 | timeout | 300 | RECORD | a hung return step holds the clone | 289 | the whole return, an upper bound; 1151 return units, user journal, 14 days to 2026-11-24 | raised to 3000 |
| rimflow/detached_helper.py:924 | grace_s | 3600 | ENDS NO WORK | a clone is taken from a run whose launcher still reads it |  | the sweep leaves the clone for a later sweep | stays |
| rimflow/detached_helper.py:1225 | DRAIN_NOTICE_FRESH_S | 1200 | ENDS NO WORK | a stopped switching plan holds every launch |  | an older notice is not obeyed | stays |
| rimflow/detached_helper.py:1357 | timeout_s | 120 | NEVER REACHED | a hung launch check holds the launch |  |  | stays |
| rimflow/detached_helper.py:1684 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| rimflow/detached_helper.py:2203 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| rimflow/detached_helper.py:2322 | grace_s | 3600 | ENDS NO WORK | a clone is taken from a run whose launcher still reads it |  | the sweep leaves the clone for a later sweep | stays |
| rimflow/detached_helper.py:2347 | timeout | 300 | RECORD | a hung launch (its clone, its sync, its checks) holds the tick with no end | 896 | class `launch` (time_budget.py) | raised to 10800 |
| rimflow/dispatcher.py:303 | timeout | 60 | NEVER REACHED | a hung `claude agents` holds the Dispatcher's tick |  |  | stays |
| rimflow/dispatcher.py:318 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| rimflow/dispatcher.py:740 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| rimflow/dispatcher.py:1364 | timeout | 120 | NEVER REACHED | a hung recovery command holds the Dispatcher's tick |  |  | stays |
| rimflow/dispatcher.py:1381 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| rimflow/dispatcher.py:1543 | kill_wait | 10 | REACH NOT RECORDED | a child that does not die holds the Dispatcher's tick |  |  | stays |
| rimflow/dispatcher.py:1580 | timeout | 0.3 | REACH NOT RECORDED | a child that does not die holds the Dispatcher's tick |  |  | stays |
| rimflow/dispatcher.py:1591 | wait_s | 90 | ENDS NO WORK | a peer that holds ingest.lock holds the tick |  | the notes and the publish wait for the next beat | stays |
| rimflow/dispatcher.py:2466 | wait_s | 120 | NEVER REACHED | a role run that does not end holds the rollback command |  |  | stays |
| rimflow/dispatcher_schedule.json:3 | ops_stale_s | 2700 | ENDS NO WORK | a dead ops reading steers the launches |  | the gate says that the reading is old | stays |
| rimflow/dispatcher_schedule.json:6 | stall_after_s | 60 | ENDS NO WORK | an idle window with work is never rung |  | the window is rung | stays |
| rimflow/dispatcher_schedule.json:7 | verify_s | 300 | ENDS NO WORK | a ring that nobody took is never tried again |  | the ring is tried again | stays |
| rimflow/dispatcher_schedule.json:8 | handoff_s | 600 | ENDS NO WORK | a ring that was taken with no hand-off goes unseen |  | it is recorded, and the next ring may go | stays |
| rimflow/dispatcher_schedule.json:10 | cooldown_s | 3600 | ENDS NO WORK | a window that does not answer is rung at every tick |  | a wait before the next ring | stays |
| rimflow/dispatcher_schedule.json:12 | recover_verify_s | 300 | ENDS NO WORK | a recovery that did not work goes unseen |  | the recovery is read again | stays |
| rimflow/dispatcher_schedule.json:44 | restart_reconcile_hold_fresh_s | 480 | ENDS NO WORK | a held restart read as lost |  | an older hold line is not counted | stays |
| rimflow/dispatcher_schedule.json:51 | grace_s | 20 | ENDS NO WORK | a restart cuts his last words |  | the restart waits this long first | stays |
| rimflow/dispatcher_schedule.json:54 | helper_stale_s | 1800 | ENDS NO WORK | a dead helper holds a restart for ever |  | a helper this silent no longer holds the restart | stays |
| rimflow/dispatcher_schedule.json:56 | hold_max_s | 14400 | ENDS NO WORK | his hold is left on and the window's context grows with no end |  | the hold no longer holds, and an alarm says so (CONDUCTOR_RESET_FIX_KILLED_MID_READ) | stays |
| rimflow/dispatcher_schedule.json:115 | pre_launch_max_s | 1800 | RECORD | a hung pre-step holds the role slot | 462 | the longest coverage judge, agent transcripts, 14 days to 2026-11-24 | raised to 6000 |
| rimflow/dispatcher_schedule.json:115 | pre_launch_max_s | 1800 | RECORD | a hung pre-step holds the role slot | 462 | the longest coverage judge, agent transcripts, 14 days to 2026-11-24 | raised to 6000 |
| rimflow/game_lock.py:68 | WRITING_WAIT_S | 1 | ENDS NO WORK | a lock read in mid write is empty for milliseconds |  | the reading says: could not look | stays |
| rimflow/judge_certificate.py:46 | START_PROBE_S | 20 | RECORD | a probe as long as the test doubles every red proof | 2 | start-up deaths of the 46 Pyrelands live commands, 2026-11-20 | stays |
| rimflow/judge_certificate.py:52 | EMPTY_GAME_TIMEOUT_S | 120 | RECORD | a hung scene on an empty game holds the certificate | 0.15 | FlowWorks' 17 scenes, 2026-11-18 | stays |
| rimflow/launch_checks.py:55 | timeout_s | 120 | NEVER REACHED | a hung launch check holds the launch |  |  | stays |
| rimflow/left_open_continue.py:110 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| rimflow/left_open_continue.py:640 | timeout | 60 | RECORD | a hung launch holds the run's end | 1.3 | admission to start of 1057 runs, control.db | stays |
| rimflow/list_dispatch.json:27 | shape_grace_h | 86400 | ENDS NO WORK | a Shape run is spent on an item that its filer is about to close or claim |  | the item is due for Shape | stays |
| rimflow/list_dispatch.py:71 | SYSTEM_WAIT_S | 3600 | ENDS NO WORK | a launch is sent again every tick into the same refusal (the night of 2026-11-20) |  | a wait before the next try | stays |
| rimflow/list_effect.py:60 | CMD_TIMEOUT_S | 600 | NEVER REACHED | a check command that never ends holds this beat's lock and stops every later check |  |  | stays |
| rimflow/list_pipeline.py:26 | LANE_STALE_S | 1800 | ENDS NO WORK | a dead rm-list-dispatch.timer leaves every verdict silently old |  | the lane reading says that it is old | stays |
| rimflow/maturation.py:2537 | REPAIR_STOP_S | 120 | NEVER REACHED | a game that ignores its close holds the repair (it is stopped with /F after this) |  |  | stays |
| rimflow/maturation.py:4349 | timeout | 120 | RECORD | a hung local command (git, systemctl, one small tool) holds its caller with no end | 4 | class `call` (time_budget.py) | stays |
| rimflow/maturation.py:5603 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| rimflow/maturation_dispatch.json:23 | settle_s | 180 | ENDS NO WORK | a run is judged before its published files reach the dispatch clone |  | the run is judged at a later tick | stays |
| rimflow/maturation_dispatch.json:45 | stalled_min | 600 | ENDS NO WORK | a stalled mod goes unseen |  | the stall is alarmed | stays |
| rimflow/maturation_dispatch.py:1562 | timeout | 60 | RECORD | a hung launch holds the dispatch tick | 1.3 | admission to start of 1057 runs, control.db | stays |
| rimflow/maturation_dispatch.py:1588 | timeout | 120 | RECORD | a hung local command (git, systemctl, one small tool) holds its caller with no end | 4 | class `call` (time_budget.py) | stays |
| rimflow/maturation_dispatch.py:1601 | timeout | 120 | RECORD | a hung local command (git, systemctl, one small tool) holds its caller with no end | 4 | class `call` (time_budget.py) | stays |
| rimflow/maturation_dispatch.py:2437 | RUN_MAX | 99 | ENDS NO WORK | an endless search on a wrong known set |  | a count of names, no time | stays |
| rimflow/maturation_dispatch.py:2615 | timeout | 300 | RECORD | a hung ledger test holds the dispatch tick | 0.2 | the docstring's reading, 2026-11-16 | stays |
| rimflow/maturation_dispatch.py:3612 | timeout | 600 | RECORD | a hung ./publish or land.sh holds its caller with no end | 584 | class `publish` (time_budget.py) | raised to 21600 |
| rimflow/maturation_dispatch.py:3617 | timeout | 120 | NEVER REACHED | a hung start of the return unit holds the dispatch tick |  |  | stays |
| rimflow/maturation_dispatch.py:3677 | DEAD_WAIT_S | 600 | ENDS NO WORK | the tick finishes a run whose own finish still runs |  | the tick leaves the run for a later tick | stays |
| rimflow/maturation_dispatch.py:3729 | CLONE_STALE_MIN | 300 | ENDS NO WORK | the tick launches from a clone that is behind origin |  | the tick launches nothing and says so; the next tick reads again | stays |
| rimflow/maturation_dispatch.py:3730 | CLONE_BLIND_S | 900 | ENDS NO WORK | a refused fetch read as level with origin |  | the reading says: could not look | stays |
| rimflow/maturation_dispatch.py:3914 | VOID_REPAIR_WAIT_S | 3600 | ENDS NO WORK | a launch is sent again every tick into the same refusal (the night of 2026-11-20) |  | a wait before the next try | stays |
| rimflow/maturation_dispatch.py:4384 | timeout | 600 | RECORD | a hung page build holds a hand tick | 124 | 1228 rm-maturation-page runs, user journal, 14 days to 2026-11-24 | raised to 1800 |
| rimflow/mod_next.py:30 | READING_MAX_AGE_S | 1800 | ENDS NO WORK | a dead tick's rows read as current (six hours of automatic on a paused mod) |  | the claim reads UNMEASURED | stays |
| rimflow/mod_owner_hold.py:74 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| rimflow/modledger.json:17 | lease_idle_minutes | 2700 | ENDS NO WORK | a dead holder keeps a mod's lease for ever |  | the lease lapses; a live holder's program renews it (run_alive.py, each 20 min) | stays |
| rimflow/modledger.py:840 | timeout | 60 | RECORD | a hung local command (git, systemctl, one small tool) holds its caller with no end | 4 | class `call` (time_budget.py) | stays |
| rimflow/modledger.py:842 | timeout | 30 | RECORD | a hung git holds the ledger read | 0.9 | 180 local git calls sampled at load 20 to 52, 2026-11-24 | stays |
| rimflow/modledger_reader.py:167 | timeout | 600 | RECORD | a model call that never returns holds the reader | 49 | every session run from /tmp (336), an upper bound; agent transcripts, 14 days to 2026-11-24 | stays |
| rimflow/owed.py:194 | timeout | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| rimflow/quiet_scan.json:9 | reading_max_age_s | 600 | ENDS NO WORK | a mod pipeline reading that stopped, read as an idle machine |  | the scan launches nothing and says so | stays |
| rimflow/quiet_scan.json:11 | system_wait_s | 3600 | ENDS NO WORK | a launch is sent again every tick into the same refusal |  | a wait before the next try | stays |
| rimflow/quiet_scan.py:455 | wait_s | 3600 | ENDS NO WORK | a launch is sent again every tick into the same refusal (the night of 2026-11-20) |  | a wait before the next try | stays |
| rimflow/red_dispatch.py:55 | SYSTEM_WAIT_S | 3600 | ENDS NO WORK | a launch is sent again every tick into the same refusal (the night of 2026-11-20) |  | a wait before the next try | stays |
| rimflow/refusal_contract.py:681 | timeout | 600 | NEVER REACHED | a calibration check that never ends holds the calibration |  |  | stays |
| rimflow/refusal_contract.py:739 | FIXER_TIMEOUT_S | 1200 | RECORD | a fixer call that never returns holds the repair of the criterion | 17 | 1 CRITERIA FIXER session, agent transcripts, 14 days to 2026-11-24 | stays |
| rimflow/role_clones.py:153 | timeout | 30 | NEVER REACHED | a hung systemd-run holds the launch of a role |  |  | stays |
| rimflow/role_clones.py:174 | timeout | 300 | NEVER REACHED | a hung git holds the launch of a role |  |  | stays |
| rimflow/role_launch.py:117 | RESUME_WAIT_S | 3600 | ENDS NO WORK | a run resumes on a dead account at every tick |  | a wait before the next try | stays |
| rimflow/role_launch.py:126 | RESUME_TTL_S | 172800 | ENDS NO WORK | a resume nobody can launch stays for ever |  | the resume is dropped, said | stays |
| rimflow/role_launch.py:199 | OPS_STALE_S | 2700 | ENDS NO WORK | a dead ops reading read as current |  | the launch gate says that the reading is old | stays |
| rimflow/role_launch.py:252 | RUN_NOW_TTL_S | 3600 | ENDS NO WORK | a hand request starts a run that nobody waits for any more |  | the request expires, said | stays |
| rimflow/role_launch.py:2116 | timeout | 45 | RECORD | a hung fetch holds the designer's judge | 3.7 | 15 fetches sampled at load 20 to 52, 2026-11-24 | stays |
| rimflow/role_launch.py:2238 | timeout | 21600 | RECORD | a judge (LLM) call that never returns holds its caller with no end | 462 | class `judge` (time_budget.py) | stays |
| rimflow/role_launch.py:2319 | CLOSE_OWED_MAX_S | 172800 | ENDS NO WORK | a stage close that raises on each tick is tried for ever |  | the close is given up, said to the Conductor | stays |
| rimflow/role_launch.py:2756 | CHAIN_SWEEP_GRACE_S | 600 | ENDS NO WORK | the sweep chains a concept that a harvest is about to chain |  | the sweep leaves it for a later sweep | stays |
| rimflow/role_launch.py:2965 | CAUSE_ATTACH_WAIT_S | 5 | ENDS NO WORK | a busy cause book holds the tick |  | the attachment is kept and tried again | stays |
| rimflow/role_launch.py:3303 | SCOPE_GRACE_S | 600 | NEVER REACHED | the scope ends a run before the Dispatcher's own stop |  |  | stays |
| rimflow/role_launch.py:3304 | SCOPE_STOP_S | 30 | REACH NOT RECORDED | a run that ignores SIGTERM holds its slot |  |  | stays |
| rimflow/role_launch.py:3489 | timeout | 60 | RECORD | a hung launch holds the Dispatcher's tick | 1.3 | admission to start of 1057 runs, control.db | stays |
| rimflow/role_launch.py:3664 | wait_s | 500 | RECORD | a hung tick holds a hand command with no end | 97 | a real --apply tick, 2026-11-06 | raised to 1000 |
| rimflow/run_alive.py:31 | SILENCE_S | 7500 | ENDS NO WORK | a hung run keeps its lease |  | the silence bound of a progress guard, above the longest call that the harness allows (7200 s): the lease is not renewed | stays |
| rimflow/run_alive.py:32 | LIVE_S | 3600 | ENDS NO WORK | a brief with no renewal lines while no program renews |  | the reading says that the timer is not live | stays |
| rimflow/run_alive.py:33 | START_S | 120 | ENDS NO WORK | a young run reads as gone |  | the run reads blind, not gone | stays |
| rimflow/run_alive.py:34 | CMD_S | 120 | RECORD | a hung ledger command (a note, a lease, a replay of the ledger) holds its caller with no end | 28.3 | class `rimflow` (time_budget.py) | raised to 300 |
| rimflow/run_end_wake.py:47 | MAX_WAIT_S | 82800 | ENDS NO WORK | the harness ends the wake hook with no message |  | the wake ends under the hook's own 86400 s and is armed again | stays |
| rimflow/run_end_wake.py:49 | STATE_DEADLINE_S | 20 | NEVER REACHED | a hung reader holds the wake |  |  | stays |
| rimflow/run_end_wake.py:50 | READER_S | 18 | NEVER REACHED | a hung reader holds the wake |  |  | stays |
| rimflow/seat_restart.py:105 | HELPER_STALE_FLOOR_S | 1200 | ENDS NO WORK | a live helper reads as dead at a restart |  | the floor of a reading's age | stays |
| rimflow/seat_restart.py:110 | FALLBACK_GRACE_S | 200 | ENDS NO WORK | a restart is reclaimed beside a launch |  | the reclaim waits | stays |
| rimflow/seat_restart.py:112 | TELL_RING_HOLD_S | 60 | ENDS NO WORK | two rings in one tick |  | the ring waits a tick | stays |
| rimflow/seat_restart.py:2173 | timeout | 10 | NEVER REACHED | a hung ps holds the restart |  |  | stays |
| rimflow/seat_restart.py:2229 | wait_s | 10 | REACH NOT RECORDED | a window that ignores SIGTERM holds the restart; SIGKILL follows |  |  | stays |
| rimflow/seat_restart.py:2359 | timeout | 180 | NEVER REACHED | a hung fallback launch holds the restart |  |  | stays |
| rimflow/seat_restart.py:3779 | timeout | 120 | NEVER REACHED | a hung handoff.py holds the window's wake |  |  | stays |
| rimflow/spend_watchdog.py:47 | GRACE_S | 30 | REACH NOT RECORDED | a run that ignores SIGTERM goes on spending past its stop (the per-run spend stop he ordered); SIGKILL follows |  |  | stays |
| rimflow/role_clones.py:216 | timeout | 600 | RECORD | a hung ./publish or land.sh holds its caller with no end | 584 | class `publish` (time_budget.py) | raised to 21600 by the first run |
| rimflow/role_clones.py:118 | timeout | 1800 | RECORD | a hung launch holds the tick with no end | 896 | class `launch` (time_budget.py) | raised to 10800 by the first run |
| Utils/guiding_prose.py:651 | timeout | 600 | RECORD | a hung ./publish or land.sh holds its caller with no end | 584 | class `publish` (time_budget.py) | raised to 21600 by the first run |
| rimflow/detached_helper.py:573 | timeout | 300 | RECORD | a hung local command holds its caller with no end | 4 | class `call` (time_budget.py) | raised to 1800 by the first run |
| rimflow/detached_helper.py:1604 | timeout | 60 | RECORD | a hung launch holds its caller | 1.3 | admission to start of 1057 runs, control.db | stays |
| rimflow/role_clones.py:227 | timeout | 600 | NEVER REACHED | a hung seat_sync holds the launch of a role |  |  | stays |
| rimflow/control_acts_export.py:143 | timeout | 120 | NEVER REACHED | a hung push holds the export tick |  |  | stays |
| rimflow/control.py:1495 | timeout | 300 | NEVER REACHED | a hung forecast holds the pipe command |  |  | stays |
| Utils/testq/testq.py:2484 | timeout | 300 | NEVER REACHED | a hung ssh holds the submit |  |  | stays |

## Left apart: the limits that stay (read, not changed)

- his holds and stops, `./pipe` and the OWNER bridge hold (45 min): not time budgets on work;
- the per-run spend stop (`spend_watchdog.py`): a spend, with no time in it;
- the account order and leave lines (`slot_rules.json` lent_accounts, token): not time budgets on work;
- the machine-safety brakes: the disk floor (`ops.disk_brake_free_gb`), the load line of 28, `MemoryMax` of each unit.
  `rm-memwatch` itself is a reader, not a brake: its deadline was raised, its memory limit was not.

## A budget outside the scope that cost the most this day

`src/RimMandrake/GimmeSomeSlack/validation.py:236`, 600 s, ends the offline gate of the live scenes. The gate runs
`selftest_gimmesomeslack.py`, which passes in 533 s on Archmagi (`selftest_timings.json`): ratio 1.13. On SteveDesktop it ran past 600 s: 4 jobs of
2026-11-24 4:17 AM to 5:20 AM PST, 196 check rows UNMEASURED, 48 min of a game [measured, testq done records]. The file is in a mod that a live run
stages for the owner's walk, so it is a ticket: `RIMMANDRAKE_RAISE_SLACK_GATE_DEADLINE_SIXTY_SECONDS_FROM_ITS_RUN`.
