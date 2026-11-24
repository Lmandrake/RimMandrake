# SteveDesktop: the forms behind the tickets

Item `RIMMANDRAKE_CLEAN_STEVEDESKTOP_TICKETS_FIX_THE_FORM_NOT_EACH_COMPLAINT`, written 2026-11-23, evening PST.
The owner that evening: *"PLEASE look over ALL the tickets and perform the 'form over specific complaint' procedure:
what's REALLY wrong, not just this one time, but for all times?"*

The set is every open ticket about SteveDesktop, Steve1, Steve2, the test lane, its worker and its steward. The study
beside this page (`one_page.md`, `analysis.md`) gave seven changes. This page checks the seven changes against the
tickets and adds what the changes miss. Numbers are `[measured]` in the study or on the named ticket.

A **form** is a fault that comes back with new details. One change ends a form. A ticket that only repeats a form is
superseded by the form's item.

## The forms

| form | what is really wrong, for all times | the one change that ends it | state |
|---|---|---|---|
| **1. A result has no reader** | The lane makes a verdict and no program carries the verdict to where it decides something. | The program that stores the result also writes the result where it counts. | proofs half BUILT; visit half `RIMMANDRAKE_COUNT_LANE_RESULTS_WHERE_VISITS_DECIDE` |
| **2. The second equal refusal changes nothing** | The lane meets a wall, writes the wall down, and walks into the wall again. | Two equal bad endings on one game stop that game, file one ticket, and retry once in 30 min. | BUILT (`RIMMANDRAKE_STOP_GAME_ON_SECOND_EQUAL_REFUSAL_FORTYSEVEN`) |
| **3. The job is sent before the host is read** | Whether the host can run a job is learned from a failed job, one mod, save, package, companion or driver at a time. | One command fills the job in and reads a file of host facts first. "Absent" and "could not look" stay apart. | `RIMMANDRAKE_ASK_LANE_IN_ONE_LINE_AFTER_HOST_FACTS` |
| **4. A stop does not name its end** | A stop waits for a person who does not know of it. | Each pause and each stop carries its end, and the tick lifts it. | BUILT (`RIMMANDRAKE_END_EVERY_LANE_PAUSE_ITSELF_FORTYNINE_HOURS`) |
| **5. A spoiled game goes to the next job** | The worker knows that the colony is dead, and hands the colony on. | A row that says the map is spoiled puts the kept game down. | BUILT (`RIMMANDRAKE_DOWN_SPOILED_KEPT_GAME_BEFORE_NEXT_JOB`) |
| **6. The line does not say what spoiled it** | The reader of the ledger cannot tell a verdict from a verdict inside a machine fault. | Every ledger line of a result in a fault window names the window. | BUILT (`RIMMANDRAKE_MARK_FAULT_WINDOW_ON_LEDGER_LINE`) |
| **7. An agent waits by hand** | Each submitter writes its own wait loop and reads a hung job as a slow job. | One command waits, reads the heartbeat and returns the rows. | `RIMMANDRAKE_WAIT_AND_WAKE_ON_ONE_LANE_JOB` |
| **8. One cause, many tickets** | An alarm is named for its moment, so a return makes a new ticket, and a ticket's age reads as the incident's age. | A ticket is keyed on the cause. An incident has its own clock and ends by itself. | `RIMMANDRAKE_TICKET_LANE_CAUSE_ONCE_THIRTEEN_FOR_ONE` |
| **9. A gauge goes blind on what it cannot know yet** | One young job, one old torn line or one missing package turns a whole reading into "unknown" or into a false FAIL. | Judge the part that is settled, name the rest beside it. Never turn "could not look" into a verdict. | BUILT for the four cases found |
| **10. The fault era outlives the fault** | Trackers, probes, reboots and tickets stay after the cause is off. | One tracker. Each guard runs only while its danger is seen, and a return wakes the one sleeping ticket. | BUILT |
| **11. The runner clone is everybody's** | A clone that a program pins takes a commit, dirt or a stale lock, and then the next pull refuses. | The worker makes the clone safe before each pull: lock, pin, dirt, and a hook that refuses a commit. Both runner clones. | BUILT |

Forms 1 to 7 are the study's ranks 1, 2, 3, 4, 5, 6 and 7. Forms 8 to 11 are what the seven miss.

## Each form: its cases, and the acceptance test

**1. A result has no reader.** Cases: `RIMMANDRAKE_READ_TIER_JOB_VERDICTS_THE_READER_RETIRED_FIRST`; 22 finished visit
jobs with 163 passes and 3 fails that no visit counted; 12 proof jobs since 2026-11-18, 3 of them with no ledger line.
Test: `selftest_ingest.py` (`a-proofs-jobs-verdict-lands-on-its-item`), green. `acceptance/count_visit_rows_accept.py`,
FAIL 0/12 on 2026-11-23.

**2. The second equal refusal changes nothing.** Cases: `RIMMANDRAKE_FIX_STEVE2_LOAD_PREPARE_REFUSES_RUNNING` (47 equal
refusals in 11 h); the companion runs of 15, 9, 6 and 6; 81 jobs in 21 days after the second equal one;
`OPS_STEVE_DIAGNOSE_INVALID_MBTX_YAHV`. Test: `selftest_lane_stop.py`, green, 8 of 8 planted faults caught. Page:
`design/specs/2026-11-23-lane-stops-name-their-end/boundary.md`.

**3. The job is sent before the host is read.** Cases: `RIMMANDRAKE_TAG_GSS_LIVE_CHECKS_FOR_STEVE_NONE_OF_203_CAN_GO`,
`HARNESS_REPAIR_CAUSE_8135787B_2`, `HARNESS_REPAIR_CAUSE_C1B99C19_2`, `HARNESS_REPAIR_CAUSE_44117724` (checks with no
driver on the lane), `LIGHTSPEED_WIDEN_STEVE_TIERS_MISSING_MODS`, `ACCOUNT_KEEPALIVE_VERIFY_STILL_BREATHING` (the
keep-alive said "renewed" while the login's end never moved: two of three logins were dead on 2026-11-23), the old address
in `sps.sh` (fixed), `CUISINE_LXML_MEND_STEVE_HAS_NONE`, the missing site save, the companion race.
`RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE` is a missing route and stays its own build. Test:
`acceptance/ask_lane_accept.py`, FAIL 0/11.

**4. A stop does not name its end.** Cases: the 49 h pause; 142.7 h of asked work under a pause; `STEVE_LANE_*` auto pauses.
Test: `selftest_lane_stop.py`. Not built: work moves to another game while the machine is paused. The machine's pause
covers Steve1 and Steve2, and the Archmagi half of the lane is switched off on purpose (`archmagi.stop`).

**5. A spoiled game goes to the next job.** Cases: `HARNESS_REPAIR_CAUSE_CEF341B8`, `_6236AE26`, `_4AFBF8A2_2`,
`_F6CADE57`, `_01DAD227_2`, `_E0B6DA41_3`, `_AC81755A_3` (rows that the stopped chain never reached), `_4E52E202_2`;
33 jobs in 21 days; 138 rows since 2026-11-20 that could not hold the site quiet. Test: `selftest_steve_worker.py`
(`a-spoiled-kept-game-goes-down-before-the-next-job`), green, with a FAIL row that only quotes the words kept up.

**6. The line does not say what spoiled it.** Cases: 157 verdicts from fault windows with no mark;
`RIMMANDRAKE_RERUN_FAULT_WINDOW_VERDICTS_ON_CLEAN_BOOT`. Test: `selftest_ingest.py`
(`the-ledger-line-names-the-fault-window`), green. The old 157 lines stay as they are.

**7. An agent waits by hand.** Cases: 111 wait turns and 275 read turns in a week, 1.8M and 4.1M weighted tokens. Test:
`acceptance/wait_lane_accept.py`, FAIL 0/6.

**8. One cause, many tickets.** Cases: `RIMMANDRAKE_KEY_STEWARD_ITEMS_ON_CAUSE_NOT_FRESH_NAMES` (13 tickets for one brake),
`STEWARD_FIX_LEAVES_THE_LIGHTS_ON`, `OPS_STEVE_UNSTICK_UNCLAIMED_ETBS`, `OPS_TESTQ_UNSTICK_ECPK`,
`RIMMANDRAKE_READ_STEVE_RESUME_REPORT_CAN_FILL_RAISE_NOISE` (its question is answered: yes, 31 `HARNESS_REPAIR_*` in 21
days), 50 `STEVE_LANE_UNSTICK_*` in 21 days, 37 of them dropped. Test: `acceptance/lane_cause_once_accept.py`, FAIL 0/8.

**9. A gauge goes blind on what it cannot know yet.** Cases, all fixed, each test seen red first:
`RIMMANDRAKE_MEASURE_STEVE_NOTHING_HOURS_ON_SETTLED_JOBS_ONLY` (`selftest_ops_watch.py`); `fault_monitor.py check`, BAD for
days on five torn lines of 2026-11-08 to 14 (`selftest_testq_fault_monitor.py`); `CUISINE_LXML_MEND_STEVE_HAS_NONE`
(`selftest_static_no_lxml.py`); the stall alarm that counted a paused span (`selftest_ops_watch_queues.py`).

**10. The fault era outlives the fault.** Cases: `RIMMANDRAKE_DIAGNOSE_STEVE_GAME_VANISHES_FIVE_BEFORE_BREAKFAST`,
`RIMMANDRAKE_DIAGNOSE_HAR_CTOR_TOKEN_ZERO`, `BRIDGE_STRANDING_DIAGNOSE_SEVEN_MORE_DRIVERS`,
`MINIDUMP_PROVE_SPIKE_BEFORE_THE_KILL`, `RIMMANDRAKE_FIX_JAWABENCH_AWARENESS_INSTALL_CRASHES_START`,
`RIMMANDRAKE_UNBLIND_SOAK_WORKER_PROBE_SYSTEM_SEES_NO_DISTRO`, `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO` (asleep).
The tracker: the register probe (task `SteveDiag Register Probe`) and `rm-steve-fault.timer`. It retired `watch2.ps1`, the
heat sampler, the CPU soak and reader, the CPU retest and `driver_death_recurrence.py`. The 12 h reboot runs only
while a fault or its driver was seen in 48 h. Test: `selftest_testq_fault_monitor.py`, 5 planted faults caught.

**11. The runner clone is everybody's.** Cases: `STEVE_RUNNER_CLONE_ENFORCE_NO_LLM_WRITES`,
`RIMMANDRAKE_FIX_STEVE_WORKER_STALE_INDEX_LOCK_BEFORE_PULL` (its fix cleared the lock after the checkouts that need the
index: fixed), runner_b got none of the self-repair (fixed), `RIMMANDRAKE_CENSUS_STEVEDESKTOP_ERA_REMAINS_WHILE_SOAK_RUNS`,
`RIMMANDRAKE_SWEEP_STEVEDESKTOP_CLONES_CARRYING_LOOP_TREES`, `RUNNERCLONE_FIX_STRANDED_BY_HISTORY_REWRITE`. Test:
`selftest_steve_worker_stale_lock.py`, red on the parent for the order.

## The baseline, and how to measure that the forms ended

Baseline: the study's 21 days and 7 days to 2026-11-23 8:30 PM PST. Run again 7 days after the last landing:

    cd design/specs/2026-11-23-stevedesktop-work-to-code/census && python3 kinds.py && python3 repeats.py && python3 idle_why.py && python3 windows.py

| form | reading | baseline | good |
|---|---|---|---|
| 2 | `repeats.py` "saved by a stop after two" | 81 in 21 days | 3 or fewer in 7 days |
| 4 | `idle_why.py` hours of a pause with no end | 49.3 h | 0 |
| 5 | `kinds.py` "Kept game was spoiled", jobs in a row on one game | 33 jobs in 21 days | no second job in a row |
| 6 | `windows.py` ledger verdicts in a window with no mark | 157 | 0 new |
| 1 | proofs jobs with no ledger line after their end | 3 of 12 | 0 |
| 3 | asked jobs that a setup fault killed | 16 of 61 in 7 days | 5 or fewer |
| 8 | `STEVE_LANE_UNSTICK_*` filed | 50 in 21 days | 4 or fewer in 7 days |

## The outcome of each ticket

See the table at the end: `ticket_outcomes.tsv` beside this page. It lists before and after.
