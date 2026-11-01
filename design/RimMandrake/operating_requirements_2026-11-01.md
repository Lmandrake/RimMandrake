# Operating requirements (2026-11-01)

**Status: requirements, set by the owner's instruction of 2026-11-01:** *"please improve these requirements to a useful
level. Then do a GPT review, and then let's get to work on this right away."* They turn §8a of
`tentative_plan_after_v2_lessons_2026-11-01.md` and `return_to_building_checklist_2026-11-01.md` into testable rules.
The six v3 roles and the Dispatcher stay: every requirement names its owner in [brackets], and no new role is added.
Four parts in his words, plus test economy, roles, and the 19 questions. Readings are MEASURED 2026-11-01 unless marked.

**Every requirement has:** behaviour; signal and source; threshold as data (file named); who is told and what counts as
acknowledged; a planted-fault acceptance test; what exists and what is missing. A requirement is met only when its
planted fault was caught on the real path, never on a statement.

## 0. What the search changed

The Conductor's gap list was marked "to be proved". Proved against the ledger and code:

| Stated gap | Reading |
|---|---|
| Operations did not catch the 6-hour jam | **False.** `CLONE_POOL_BREACH` 04:23Z; staffing alarm 06:59Z (+32 min, breaker named, 383 ready); the Operations run diagnosed "the relentless belt is DEADLOCKED on the pool" at 07:05Z, with the cause. That went into a note on an item nobody reads. Next human-side move 12:33Z. **The failure was delivery.** |
| No definition of sane | Partly false. `ops_watch_rules.json` holds targets, bands, run rules, silence rules, each with its why. Missing: idle/distressed/emergency classes, and any relentless or seat family at all (zero matches). |
| Delivery is a log read at wake | Half true. Alarm items launch Operations by event. Toward the Conductor it is a log line and a note. **No acknowledgement exists anywhere.** Flags stand for days (`TEST_HOURS_WASTED`, `PROCESS_SHARE` since 10-27). |
| Repeats counted by failure class only | False. `unchanged_returns_limit` 9 counts returns of any class. The real gap: 9 hour-long runs is too slow, and nothing watches inside a run. |
| No test-waste awareness | Partly false. `selftest_cache.py` (6 declared tests), `run_selftests --quick`, modcheck gates, `testing.nothing_h` exist. Workers are neither told nor interrupted. |
| Blind review fixed at cycle end | False. The worker calls `finish` on its own evidence and that triggers the blind judge. |
| Nothing proves timers stay alive but deadman | False. `timer-guard.timer`, `c_timers`, `signal_watch`, deadman 72/72. Missing only: a check that every enabled timer is on the list. |
| FOUNDRY staffing, cause not established | Established: the clone-pool deadlock (fix `bbcff75f26`). `POOL REFUSED` was charged as a launch failure, so the breaker cooled up to 4 h. Separate failure: `idle_full_queue:FOUNDRY` on 10-30 and 10-31, rung forever, nothing brought it back. |
| Nightly RED 14 of 14, today UNMEASURED | Now MEASURED: 18 RED of 18 RESULT lines in `Transient/selftests_nightly.log`. No ops metric reads it. |

## 1. The required catches

| Past failure | Caught by | Told within |
|---|---|---|
| Relentless jammed 6 h behind an open breaker, 382 ready | OP2, DI2, OP3 | 30 min, acked or escalated by 60 |
| FOUNDRY idle with work ready | DI1 | 30 min; brought back automatically |
| 279 clones outside the cap | OP2 (`disk.scratch_outside_cap`) | next 15-min pass |
| Selftest sweep RED 14 of 14 nights | TE1 | the morning of the first new red |
| A helper's fake alarms | OP5 | at write time |
| A goodbye cancelled silently | CK3 | 10 min |
| A machine stuck testing what it already knew | RW1, RW2, TE2 | within the run, 30 min |
| Busy for days with no real advance (GPT) | MI1 | `advance_max_days` |

## 2. Context keeper

*"When windows get too big, they close out and get restarted by Dispatch."*

**CK1 Every seat closes itself.** [Dispatcher runs; Operations reads] A seat over its context limit at a boundary is restarted by Dispatcher, with no human.
Signal: `dispatcher.jsonl` context reading per seat. Threshold: `dispatcher_schedule.json` seats (FOUNDRY 110k, BENCH
120k). Told: nobody on success; a `restart_verified` line. Test: a stub seat at limit+1 at a boundary is restarted and
verified. Exists: FOUNDRY. Missing: BENCH `backstop: false`; his §8a words settle the open question, so it goes on once
its open review findings close. Tentative plan §8 question closed by his words.

**CK2 No seat outruns the hard limit.** [Dispatcher measures; Operations reads] A seat over `hard` with no boundary for `hard_alarm_s` raises an acked alarm.
Signal: `hard_no_boundary`. Threshold: same file. Told: the seat's reader by OP3. Test: stub seat over hard, no boundary;
alarm in told ledger; unacked escalates. Exists: the log line (00:06Z). Missing: delivery.

**CK3 Every restart request ends.** [Dispatcher measures; Operations reads] Any goodbye or restart request ends in `restart_verified` or a told alarm, read from
outside the code path that might have dropped it. Signal: requests joined to `restart_verified` by seat. Threshold:
`dispatcher_schedule.json` new `restart_reconcile_s` 600. Told: the seat, then Operations. Test: plant a goodbye then
cancel it the way the peer message did; alarm inside 10 min. Exists: `restart_verified`. Missing: the join. Each past fix
was on the code path; this one does not trust it.

**CK4 A fresh window takes work.** [Dispatcher runs; Operations reads] A restarted seat with ready work makes a handoff or a `started` event within
`fresh_take_s`, else one more restart, then alarm. Signal: `started` events after `restart_verified`. Threshold:
`fresh_take_s` 900. Test: a fresh stub that ignores its prompt is restarted once, then alarms. Exists: `no_handoff`
rings. Missing: the bring-back (shared with DI1).

## 3. Operations

*"They know what sane looks like, idle looks like, what the current plan is, and what broken/distressed/emergency looks
like."*

**OP1 Ranges are data.** [Operations] Each watched metric has idle, sane, distressed, emergency ranges with an owner and
`ack_within_min`, in a `ranges` block in `Utils/ops_watch_rules.json`, beside the existing rules. Programs check every
15 min. A range change names why. A metric fills only the classes it can act on; the four words are the vocabulary, not a form. Test: lint refuses a metric
with no owner; a fixture value in each filled class reports it. Exists: targets, bands. Missing: the classes.

**OP2 It watches the work, not just the machine.** [Dispatcher measures; Operations reads] New collector family, in the digest: `relentless.live`,
`relentless.under_min`, `relentless.breaker_open_min`, `relentless.checks_wait`, `relentless.ready`,
`relentless.tick_age_s`; `seats.idle_with_work_min`; `disk.scratch_outside_cap`; `selftests.new_reds`,
`selftests.red_nights`. Sources: `relentless/store/staffing.json`, `reading.json`, `breaker.json`; `dispatcher.jsonl`;
`scratch_reap` sanity record; `selftests_nightly.log`. Test: replay the 04:00-13:00Z staffing record and the 10-31 idle
record; each metric reads distressed at the same minute the record says. Point a metric at a missing file: it reads
UNMEASURED and alarms, never sane. **Freshness:** every metric carries `max_age_min` and, where work is claimed, a
progress reading; a source frozen at a sane value while work has stopped must alarm. Second test: freeze `staffing.json`
sane; keep the timers firing with collection suppressed. Both alarm within two passes. Exists: `relentless.*`, `seats.*`, `disk.scratch_outside_cap` (limits in `ops_watch_rules.json` ranges, owner Operations). Missing: `selftests.*`.

**OP3 One incident, from told to recovered.** [Dispatcher delivers; each role acks] A distressed or emergency reading
opens one row in `told.jsonl` beside `alarms.json`: cause key, metric, reader, told_at, ack_due, recover_by. It rings the
reader's seat by doorbell. Readings sharing a cause key join that incident, so one outage is one ring. An **ack** gives
ownership only: the reader's action on the named item or `rimflow ack <id> --plan "<next>"`, and sets `recover_by`. A ring
or a read is not an ack. An incident **closes only on reading**: the metric sane for `sustain_min`. Past `ack_within_min`
(default 30) or past `recover_by`, acked or not, it moves to the next reader; relapse inside `relapse_h` reopens it.
Alarm-launched runs share a per-hour budget so an outage cannot spend the capacity to repair it. Test: reader stubbed
silent, next reader on time. Reader acks "investigating", fault stays, reader killed: escalates anyway. Plant one outage
tripping 10 metrics: one incident, one run. Recover, then relapse: same incident reopens. Exists: rings, alarm items,
`alarm_limit_hold`. Missing: everything else. OP3, OP4 and RO4 are one build.

**OP4 Reaching him.** [Conductor] Chain: role owner → Conductor → fresh Operations run → owner. The last agent reads the alarm and
writes the line he sees, so the rule *nothing reaches him unread* holds. Only if no agent can run does a fixed-template
line go out unread: that is his accepted exception. Route: RimPulse owner banner and desktop toast. Threshold: emergency
goes to him at 60 min unacked, distressed only after 4 h. Test: all agents stubbed dead; his banner shows the template
inside the limit. Exists: toast route, pulse. Missing: banner, chain. **Phone push is ON since 2026-11-01 (3645471658).**

**OP5 An alarm proves its origin.** [Auditor (instrument trust)] Alarm lines carry writer and a sane timestamp; anything else is refused and counted
(`alarms.rejected`). Weekly a DRILL alarm walks the real path to an ack; a failed drill is itself an emergency. Test: a
selftest writing to the real log is refused; a drill with the reader stubbed silent escalates; a drill with the told
ledger unwritable alarms by the deadman path. Exists: guard `fa573c87c2`. Missing: `alarms.rejected`, drill.

**OP6 A flag has an end.** [Operations] A flag standing past `flag_max_age_h` must become an incident, a changed range, or a retirement
with reason; a bare new item does not end it. Test: an aged fixture flag reddens the twice-daily report until one of the three happens. Exists:
`signal_watch` flags. Missing: the end state.

**OP7 The twice-daily run reads and judges.** [Operations] It reads the report plus the priority list (DI3), and handles what ranges
cannot: reads that are sane but wrong against the plan. It must end with a verdict per family and act on a told row or
explain. Test: a fixture where 3 workers run sanely on items not on the priority list; the run must name it. Exists:
`roles/operations.md`. Missing: the list and the check.

## 4. Relentless workers

*"Aware of low-productivity testing traps or rapidly iterating between multiple poor solutions."*

**RW1 Time ledger, per run.** [Operations reads] Each run's hours are charged to selftest, live, build, reading, editing, waiting, from
tool records (reuse `pulse/agents_timeline.py`). Threshold: `relentless_rules.json` new `circling` block. Test: a fixture transcript of known split reads within 5%; then replay real runs labelled by
hand, measuring both missed waste and wrongful stops. Missing: all (`WORKER_TIME_LEDGER_BUILD_WHERE_HOURS_WENT`).

**RW2 Circling is seen from outside and interrupts.** [relentless runs; Operations reads] Tick-side rule, reading RW1 and the run's clone, never the worker's
own words: (a) testing share over `test_share_limit` for `test_share_min` with the diff hash unchanged; (b) `no_change_min`
with no new code and no new finding; (c) a diff hash returning to an earlier hash, A-B-A, `oscillation_limit` times. A hit
stops the run by the existing path, class `circling`, carrying the reading to the next run, and counts as a forced
change of approach. It starts **report-only**, and may stop runs only after a replay of hand-labelled real runs shows wrongful
stops under `false_stop_limit`. A stop keeps the clone's work and the fencing `gen`, so nothing is lost or doubled. Test:
planted workers for each of (a), (b), (c) stopped within the limit; trivial churn caught; a long read-only investigation
and a long build with a moving diff left alone. Exists: `unchanged_returns_limit`, between runs only. Missing: inside-the-run reading.

**RW3 Help is a built-in call.** [Foundry worker calls] `relentless.py help --item X` sends a fresh agent, with no history, the problem and the
failed approaches and returns options into the state file. Forced after two circling hits on an item; a worker may call
it any time. Threshold: `help_after_circling` 2, one per item per `help_cool_h`. Test: a planted item with two hits gets
exactly one consult; its options reach the next run's brief; a consult from a run with no failed approach is refused.
Exists: `snag`→redesign. Missing: the call.

**RW4 Blind review is called on evidence.** [Arbiter] The worker calls `finish` near the end, on its own evidence; that triggers
the blind judge. Stated as a rule only. Test: existing relentless selftests.

**RW5 Finding-kind meter.** [Operations reads; Innovator acts] Per item and per mod, count new kinds of finding per day and where caught. Flat new kinds
with rising run count reads `going_round`. Source: receipts and `finding` events; kind is the class slug. Test: fixture history reads converging and going-round correctly. Missing: all. Reports only; Operations reads it (C5).
Deferred until the pilot: class slugs can be gamed, so it is built after RW1 and MI1 show a need.

## 5. Dispatch

*"Doesn't forget to keep checking ever. Looks for idle agents and brings them back up on useful items. Is plan-aware."*
Dispatch stays a plain program.

**DI1 Idle with work is ended, not just rung (one state machine with CK4).** [Dispatcher runs; Operations reads] Seat idle with ready work: ring, then after `no_handoff.escalate_after`
rings the Dispatcher restarts it once (a window that does not take work is treated as dead), then alarms. Threshold:
`dispatcher_schedule.json` new `idle_bringback_after_min` 30. Told: the told ledger. Test: stub window that ignores rings
restarted at the limit; still silent, alarm; a seat with a human active is left alone. Exists: rings, `idle_full_queue`.
Missing: the restart.

**DI2 A stall names itself, and a breaker cannot sleep on it.** [Dispatcher runs; Operations reads] Live under target with work ready names one cause.
Breaker cools are capped at `breaker_cool_max_s`, lowered from 14400 to 1800; the same cause opening it twice is an
emergency. Infrastructure refusals never charge the breaker. Test: plant a pool refusal and a failing launcher;
the first does not open it; the second opens twice and reaches the told ledger as emergency. Exists: breaker, jam alarm
to log. Missing: same-cause count, delivery, cap.

**DI3 Plan-aware by one short list.** [Producer writes; Dispatcher obeys] `infrastructure/state/priority_list.json`: ordered item ids and row names, under 30
entries, written by Producer or Conductor, with `set_at`. Dispatcher's ring and relentless's pool read it, nothing else
does. A closed entry or age past `list_max_age_h` is a distressed reading. Test: a listed item is launched before a
ranked one; a stale list alarms; a missing list falls back to today's order and reads distressed. Exists: `rimflow raise`,
V1 rows, `priority.py`. Missing: the file. `raise` stays as the way to add one.

**DI4 Nothing falls off the schedule.** [Operations] Every enabled `rm-*` timer appears in the deadman baseline or in an explicit
exempt list with reason. Test: enable a stub timer; the next pass reports it. Keep a timer firing while its job does nothing:
OP2's freshness catches that, not this. Exists: guard, baseline. Missing: the
coverage check.

**DI5 Steve is kept topped up, or parked with an end.** [Producer picks; Operations reads] Steve's queue depth stays in range while it is available; a park
carries an expiry and a reason, and an expired park alarms. Today parked, verdict about 2026-11-07. Test now: expired
park fixture alarms. Test deferred until unparked: drain the queue to zero; filler refills inside the limit. Exists:
`testq` filler, steward. Missing: park expiry.

## 6. Test economy

*"Yup, testing things I already knew again."*

**TE1 Nightly carries news.** [Operations reads; Foundry drains] A known-red list, each entry naming its item with an age limit. Alarm only on a red not on
the list, or an entry past its age. `known_red_after_nights` 3 (`testing_policy.json`) is the threshold to enter it. An
entry with no open item is refused. Test: plant a new red; alarm next morning. Plant a listed red; silence. Exists: the
log, the policy number, the list (`src/RimMandrake/rimflow/selftest_known_reds.json`, `known_reds.py`), the metric
(`testing.nightly_news`, alarm `NIGHTLY_NEWS`). Items: `SELFTEST_NIGHTLY_SILENCE_KNOWN_REDS`,
`NIGHTLY_SELFTESTS_DRAIN_THIRTEEN_RED_NIGHTS`.

**TE2 Known results return without running (C3).** [Operations] Same test, same dependency hash: the stored answer comes back.
`--no-cache` needs `--because "<what could differ>"`. Live keyed on deployed hash via the modcheck gate. Metric:
`selftests.cache_hit_share`, and a worker rerunning a known result feeds RW2(a). Test: identical rerun takes under 1 s and
says so; a touched declared dependency reruns; change an undeclared one (config, toolchain, seed) with the key held: it must
rerun, or the test is excluded from caching with a reason; `--no-cache` with no reason is refused. Exists: `selftest_cache.py` (6 tests),
`--quick`. Missing: coverage, reason. Build after RW1 shows the size of the waste.

**TE3 Tests that say nothing are named.** [Operations proposes; Arbiter proves detection kept] Tests that never failed in `retire_after_days` and cost over `slow_test_flag_s`
are candidates only. Never failing is no proof of no value: a candidate leaves only when a mutation run shows detection
kept. No automatic removal. Test: fixture history lists the
right test. Exists: `testing.nothing_h`. Missing: the list.

**TE4 Every escape yields a test or a reason (C6).** [Auditor; Arbiter specifies the check] A bug found by him, live, or blind and not by tests is counted; its
item cannot close without a test or a stated reason. The added test must fail on the old build. Test: close refused on a fixture
escape with neither; a new test that passes on the old build is refused. Missing: all.

## 7. Mission progress

**MI1 Busy is not progress.** [Producer writes; Operations reads; Conductor acts] Every entry on the priority list (DI3)
names a finish-line reading. `plan.days_since_advance` per entry: a list entry with no rise in that reading past
`advance_max_days` is distressed, however many tickets closed. Exists: `modcheck floor`, north-star bars. Test: fixture with
20 closes and a flat reading on a listed mod alarms; a rise clears it. The rest of C1, C2, C7, C8 waits for the pilot.

## 7a. Roles: rules move into programs, the chairs stay

The chairs stay. `rimflow_v3_minimal_opus_2026-10-29.md` found rules written in role prose were not enforced; its
invariants go into `next`, `close` and programs here, and the role keeps the judgment: **a role sets the number, a program
holds it, and a role that is not read is a defect in the wiring, not a reason to remove the chair.**

**RO1 Every role proves its use.** [Operations reads; Conductor acts] Metric `roles.<role>.acted_share` per week:
its outputs (items, notes, verdicts, reports) with a later action by another role ÷ outputs; plus `runs` and `silent_days`.
Source: ledger, `role_done` notes. Threshold: `ranges`, `roles.*`. A role under range for two weeks gets a named fix of
its input or its reader. Report-only and coarse: it is not a target a role can
earn, and it never gates anyone. Test: fixture ledger with an ignored Auditor item reads under range. MEASURED since 10-25 (name
prefix on the ledger, so approximate):

| Role | Output | Used? | To fix |
|---|---|---|---|
| Operations | 26 run notes; diagnosed the jam | The diagnosis sat unread for 5.5 h | OP3 |
| Auditor | 14 items filed | **9 untouched** | RO1; its items reach `next`, `audit` findings get a reader |
| Arbiter | 179 run notes, 2 items filed | Verdicts feed gates; both filed items untouched | RO1 |
| Producer | 30 raises, 10 items | Used: 8 implemented. The plan's WIP line binds nothing | RO2 |
| Innovator | 4 notes, 2 items, 2 list entries | **Nothing shown adopted; not yet reading finding curves** | RW5, RO1 |

**RO2 WIP cap held by `rimflow next`.** [Producer sets; `next` enforces] MEASURED: no rimflow code reads a WIP cap;
`producer.md` writes one as a line of prose. Number in `dispatcher_schedule.json`. Foundry at the cap: `next` offers only
the next step of a focus item (fix, answer, retest). A wait is a state and the waiting count is capped too. Relentless's
budget 8 caps workers, not open focus, so it reads the same number. Test: at N focus items `next` offers no new item; a
dated wait frees a place; a third wait is refused. Minimal design I2.

**RO3 Done is earned at `close`.** [Arbiter rules; `close` enforces; Auditor samples] A close needs a named sha that
touches more than the ledger, or `--no-code "<what>"`; owed checks passed on that sha; a non-maker verdict on that sha; no
newer fail. Relentless's path has the blind judge; hand closes do not. Test: each of the four missing is refused; a fail
after a pass demotes; seed a behavioural regression that passes current checks and confirm a later catch reopens it. Minimal design I1. Metric AU4 (unverified closes, 813 of 823 on 10-26) must be re-read and falls in
range, else this is not done.

**RO4 Every alarm lands on a role that wakes.** [Operations owns the table; `file` enforces] One routing table: alarm
kind → program containment, role, or him. `rimflow file --for` a reader nothing wakes is refused. The OP3 chain reads this
table. Test: selftest fails on an alarm kind not in the table; a filing for an unwoken reader is refused. Minimal design I4.

**RO5 Reds the Auditor reads become rules.** [Auditor] A repeat error class in escapes or his `repeat` messages becomes
an enforced hook or program rule, not a prose line. Metric AU3 (lessons → rules). Test: a fixture class repeated
twice reads owed until a hook names it. Exists: weekly lessons fold.

## 8. His 19 questions: instrument, gate, reader

"Gate" is what stops or forces action. Questions from `csuite_brief_2026-10-26.md`, numbered in the 10-26 census.

| Q | His question | Instrument | Gate | Role that reads |
|---|---|---|---|---|
| 1 | Stale helpers, processes | `flow.lapsed_leases`, long-helper alarm | CK4, OP3 | Operations |
| 2 | Testing known-good code | RW1, `selftest_cache` hit share | RW2, TE2 | Operations |
| 3 | Focus-mod bugs | RW5 per mod, mission page | DI3 orders them | Producer; Conductor (FlowWorks) |
| 4 | Game framerate | `tps` family | OP1 range, OP3 | Operations |
| 5 | Token pace and resets | `accounts`, `codex` runway | OP3; forecast miss → cut list | Operations; Producer |
| 6 | Bottlenecks | OP2, D2 idle with work | DI1, DI2 | Operations |
| 7 | Owner asks: needed or ceremony | L3, prereview | OP4, nothing unread | Conductor |
| 8 | Could we have found his feedback ourselves | TE4 escapes | TE4 at `close` | Auditor |
| 9 | Validation too much or too little | `testing.nothing_h`, escapes | TE3, TE4 | Operations; Arbiter |
| 10 | Archmagi and Steve split | rig utilisation | DI5 | Operations; Producer |
| 11 | Design flapping | Rework F2, re-ruled items | RO5 | Auditor |
| 12 | Git and disk | `disk.*`, publish alarms | OP1, OP3 | Operations |
| 13 | Machine reboots | deadman baseline | DI4 | Operations |
| 14 | Memory | `memwatch` | OP1 | Operations |
| 15 | Wake size | CK1 context reading | OP1 range | Operations |
| 16 | Art sheet efficiency | repeat-offer rate (UNMEASURED) | OP1 once measured | Arbiter; Conductor |
| 17 | When he is present | presence log | Live looks ring only then | Conductor; Dispatcher |
| 18 | What is not getting done | P4 blocked, DI3 stale list | RO2, OP6 | Producer |
| 19 | What is done or frozen | finish line, Arbiter verdicts | RO3 | Arbiter |

## 9. Duties with no gate yet (Part 3 of the register)

Register duties that still have an instrument and no enforcing gate after this document: enact-what-he-ruled (reconciler,
`RULINGS_BUILD_STATE_RECONCILER_NEWEST_WINS`; Conductor), canon drift sweep (`CANON_BUILD_SWEEP_WHEN_CANON_MOVES`;
Dispatcher, Conductor fixes), focus theft (`FOCUS_ENFORCE_HEADLESS_LAUNCH_ALLOWLIST`; Operations), compaction without
handoff (Operations), Innovator trial registry (metric I1), Auditor's check-defect backlog alarm. Each stays with its
item or goes to Foundry; D1-D5 doubles are not reopened. Status of those items is to be read before anyone trusts this list.

## 10. Build order

Smallest proof first; jams and idle first; then read-only pages. Enrolled in this order in relentless (§12). DI4, DI5,
OP5, OP6, OP7, CK1, CK2, TE2-TE4 and RW5 are filed when the first batch is proven, so a watcher exists to prove them.

## 11. GPT review

Asked for missing failure classes, weak tests, and cuts (one consult; the answer was a 471-word list).

**Applied.** Freshness and frozen-source test (OP2, DI4). Ack gives ownership only; closing needs a sustained reading;
escalation runs despite ack; relapse reopens; one outage is one incident; alarm-run budget (OP3, OP6). Interruption starts
report-only with a false-stop limit, and keeps clone and fencing (RW2). New MI1 for busy with no advance. Sharper tests:
RW1 replay, TE2 undeclared dependency, RO3 seeded regression, TE4 old-build red. Merged CK4 into DI1 and OP3, OP4, RO4 into
one build. Deferred RW5. TE3 needs mutation proof. OP1 no longer forces four bands.

**Rejected, with why.**
- Cut RO1 acted-share: kept, by the owner's word that roles need proof of use. Made report-only so it cannot be gamed into a target.
- An independent off-machine alarm path: needs his phone push decision, and Steve is parked. Stated in §12 as his.
- Mission deadlines and total effort budget: `item_spend_limit` and MI1's flat reading do this without a date he never asked for.

## 12. Items

All owned by FOUNDRY, acceptance in the item file, each proved by its planted fault.

| # | Item | Requirement | State |
|---|---|---|---|
| 1 | `JAM_WATCH_BUILD_RELENTLESS_IN_OPS_DIGEST` | OP2, DI2 | enrolled |
| 2 | `IDLE_WATCH_BUILD_SEAT_MINUTES_IN_DIGEST` | OP2 | enrolled |
| 3 | `BREAKER_COOL_FIX_SAME_CAUSE_ALARMS_EMERGENCY` | DI2 | enrolled |
| 4 | `ALARM_RANGES_BUILD_CLASSES_AS_DATA` | OP1 | enrolled |
| 5 | `INCIDENT_LEDGER_BUILD_TOLD_ACKED_RECOVERED` | OP3, OP4, RO4 | enrolled |
| 6 | `IDLE_SEAT_RESTART_BUILD_BRINGS_QUIET_BACK` | DI1, CK4 | enrolled |
| 7 | `RESTART_JOIN_BUILD_EVERY_GOODBYE_ENDS` | CK3 | enrolled |
| 8 | `DISK_WATCH_BUILD_SCRATCH_OUTSIDE_CAP` | OP2 | enrolled |
| 9 | `SELFTEST_NIGHTLY_SILENCE_KNOWN_REDS` | TE1 | enrolled |
| 10 | `PRIORITY_LIST_BUILD_ONE_SHORT_FILE` | DI3, MI1 | enrolled |
| 11 | `FOCUS_CAP_ENFORCE_IN_RIMFLOW_NEXT` | RO2 | enrolled |
| 12 | `WORKER_TIME_LEDGER_BUILD_WHERE_HOURS_WENT` | RW1 | enrolled |
| 13 | `MISSION_PAGE_BUILD_READ_ONLY_STATE` | C7, MI1 | enrolled |

Queue note, 2026-11-01: the first five were retired by a tick because they were enrolled before publication; restored by hand and all 13 placed ahead of the older queued items. Bug filed: `RELENTLESS_ENROL_FIX_UNPUBLISHED_RETIRED`.
| 14 | `CIRCLING_WATCH_BUILD_REPORT_ONLY_FIRST` | RW2 | filed |
| 15 | `HELP_CALL_BUILD_FRESH_EYES_ON_FAILURES` | RW3 | filed |
| 16 | `ROLE_USE_MEASURE_OUTPUT_READ_AND_ACTED` | RO1 | filed |
| 17 | `CLOSE_GATE_ENFORCE_DONE_IS_EARNED` | RO3 | filed |

Phone push (OP4): ON since 2026-11-01 (3645471658, Todoist due-now task, one send per incident, red only); the earlier "needs him" is answered.
