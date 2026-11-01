# Operations: clockwork gatherers, one judge

Design only; nothing here is built. Written 2026-11-01. Counts are measured today unless marked ESTIMATE. Your words:
*"a gathering of mostly procedural evidence gatherers and trackers, dispatch, etc. that work like clockwork and monitor
things, with a single Operations LLM to oversee, judge, adjust thresholds, and report to Conductor how things are going."*
By your card, the Arbiter, Auditor and Innovator fold into Operations and Relentless.

**In five lines.** Programs measure, ring and dispatch; they use no tokens and decide nothing. One Operations agent reads
one prepared packet twice a day, judges what the numbers cannot say, and sends the Conductor a short report that must be
answered. It may move alarm limits inside a band you signed, under a program's guard; it can never touch a bar that decides
whether work is good enough. Judging one piece of work goes to Relentless's blind checker. Reading patterns across much
work goes to Operations. Dispatch follows your signed orders and writes the plan onto the Board.

## 1. What exists

Most of the clockwork is built. The weak part is the judge at the top of it, not the gatherers.

| Gatherer | Runs | Measures | Tells |
|---|---|---|---|
| `ops_watch.py` | every 15 min | 152 readings in 19 families: accounts, Codex, Steve, testing, disk, timers, ledger flow, process share, game speed, production, Relentless, seats, plan, roles. 24 have sane/distressed limits in `ops_watch_rules.json` | Digest file, flags (17 up now), 5 open alarms |
| Dispatcher (`dispatcher.py`) | every 2 min | Each seat's window: idle, busy, dead, context size. Queue depth. Clock slots for roles | Rings seats, brings back dead ones, launches roles. Note-only on the ledger |
| Restart path (`seat_restart.py`, `rm-restart-reconcile`) | on the tick, plus its own timer | Each restart request joined to its finish | Alarm if a goodbye never ended |
| Incidents (`incident.py`, `alarm_routes.json`) | in the Dispatcher tick | One row per cause: told, acked, recovered. 65 routes, 5 readers | Moves up reader, Conductor, fresh Operations run, you. Phone push is on |
| Alarm census (`alarm_census.py`) | in selftests | Every alarm kind the code can raise has a route | Red test |
| Deadman (`deadman_check.py`) | every 15 min | 106 promises in the ledger and baseline: 102 kept, 4 paused. Also whether Dispatcher and ops_watch still stamp | Reopens the item; phones you with no AI in the path |
| `timers_guard.py` | own timer, outside the watched names | Every enabled timer is running (26 enabled, 3 disabled) | Alarm on a mass stop |
| Other clocks | 1 to 60 min | Memory, account usage, scratch disk, nightly selftests (`testing.nightly_news`), production streams, findings fold, Relentless's own tick: staffing, breaker, circling (report-only), time ledger, `trust` | Feed the digest or their own alarms |
| Run by hand, or only with a stopped role | | `close_audit.py` (unearned closes; today 1 of 32 code closes), `audit_prescreen.py`, `arbiter_tiers.py`, `belt_watchdog.py` | Nobody, unless asked |

The agent: `roles/operations.md`, clock runs 07:30 and 19:30, two alarm runs a day at most, 1.65M tokens a day.

**The fault that matters.** Every one of the 11 open incidents is routed to Operations, and today its run was refused at
its daily cap. So the ladder asked for a run the budget denied (`INCIDENTS_FIX_ONE_READER_ELEVEN_OPEN`). When a run did
happen, at 22:20Z, one run took all 11. So the need is one run that reads everything, and a budget that can never strand a
ladder. It does not need more runs per alarm.

## 2. What is still missing from the operating requirements

Most of `operating_requirements_2026-11-01.md` is built: 15 of its 17 items are closed. Read from code today, not from the
closes, since one closed watcher (`IDLE_WATCH_BUILD_SEAT_MINUTES_IN_DIGEST`) later missed an idle FOUNDRY.

| Req | Missing | Note |
|---|---|---|
| CK1 | The Conductor restarting itself | Your card: same limits as Foundry. Settled, not built |
| OP2 | `selftests.*` under those names | `testing.nightly_news` covers new reds. Rename nothing; mark it done |
| OP5 | `alarms.rejected` count, weekly drill alarm | Nothing proves the alarm path still works end to end |
| OP6 | A flag having an end | 17 flags stand; `TEST_HOURS_WASTED` and `PROCESS_SHARE` since 10-27 |
| OP7 | The judge checking work against the plan | Role file never mentions the list. Becomes section 3 |
| DI4 | Every enabled timer on the deadman's list or exempted | No exempt list |
| DI5 | A park with an expiry | Steve's verdict date (about 11-07) is in prose only |
| RW2 | Stopping a run, not just reporting | `stop: false` until 20 replayed runs show few wrongful stops |
| RW5 | Finding-kind meter | Deferred; section 5 gives it a reader |
| TE1 | Close `SELFTEST_NIGHTLY_SILENCE_KNOWN_REDS` | Built; 9 unlisted reds read now |
| TE3, TE4 | Slow tests that say nothing; escape needs a test | None built |
| RO3 | A close with no verdict still passes | Your blind-pass card closes this for ticks only: section 6 |
| RO5 | Repeat errors become rules | Was the Auditor's; stopped with it |

**Not in that document at all, and needed now:**
- `close_audit.py` is not in the digest, so unearned closes have no alarm.
- A refused run strands the ladder (section 1).
- Nobody measures whether an alarm was worth ringing. Without that, thresholds can only be guessed.
- No program changes a limit under a guard. `roles/operations.md` forbids the agent to edit limits at all.
- No report form, and no sign the Conductor read one.
- The role owners named in those requirements are out of date: Arbiter, Auditor and Innovator tags must move (section 5).

## 3. The one agent

**Job.** Four things, and only these:
1. Judge what a limit cannot see: readings sane but wrong against the orders. Three workers healthily busy on the wrong
   thing is the classic case.
2. Own every open incident in one pass: name the cause, say what happens next, and ack. Cases a program can contain stay
   with the program.
3. Tune alarm limits (section 4).
4. Report (section 7).

It does not fix things or replan. It files items, and the Producer replans. It runs no helpers. It stops doing the weekly
v3-against-v2 assessment: the arms are over and you closed that question.

**Input: one packet, built by a program** before each run, under a size cap, so it never gathers:
- the digest, open incidents, and told rows since the last run;
- flags with their age;
- orders: set, ticks, lost ticks, flat readings, orders with no worker;
- the alarm quality table (section 4);
- past limit changes and how each turned out;
- Relentless: time ledger, circling, escapes, Marker disagreements, `trust`;
- the sampled-close results (section 5);
- its last report and what the Conductor did with it.

**How often.** Clock runs at 07:30 and 19:30, as now. One event run for an emergency, with 1 run a day held back for
that. Each run reads everything open, so alarms never buy a run each. The caps stay as they are (ESTIMATE that they
suffice: the weekly assessment leaves, sampling and quality reading arrive).

**A refused run must not strand anything.** If the budget refuses a run, the program says so and the incident moves to the
next rung at once. Past the fresh-Operations rung, the Conductor's quick check takes it.

**Who watches the watcher.** A clock run with no report inside 2 hours is an alarm the program raises. The drill (OP5) walks
the real path weekly. Its own numbers (`roles.Operations.*`, incident age, report ack time) can never be tuned by it.

## 4. What it may change by itself

Today it may change no limit, and any loosening is yours. Your new words add "adjust thresholds", and your bar stays yours.
So numbers split in three.

| Class | Examples | Who |
|---|---|---|
| **Alarm limits** | Limits in `ranges`, `ack_within_min`, `max_age_min`, band and run rules: only entries carrying a signed `tune` block | Operations, inside the band, under the guard |
| **Budgets and machinery** | Token caps, slots, `dispatcher_schedule.json`, worker counts | Tighten alone inside slot rules, as now. Widen: yours |
| **Bars** | Mod bars and north-star checks, Relentless contract clauses, finish readings, `close_gate_rules.json`, TRUST bars, `false_stop_limit`, anything in a signed order | Never. A loosening request goes through the Conductor to you, as now |

**The guard is `ops_tune.py`, the only writer.** The agent asks; the program applies or refuses:
1. **A band you sign once.** Each tunable entry holds `tune: {base, min, max}`. The band is measured from the signed base, so
   twenty small steps cannot walk past it. No entry, no tuning. A value outside the band goes up as a proposal.
2. **No moving the bar under an open incident.** A metric with an open incident is frozen until it closes, because
   incidents close on reading and a loosened limit would close one by fiat.
3. **Replay before loosening.** The program replays the series for 30 days with the new limit (ESTIMATE). Every incident that
   led to a real action must still ring, no later than `tune.late_min`. The §1 catches in the requirements stay in the replay
   set forever. Tightening needs no replay.
4. **Slow.** One change per metric per 7 days, 3 per run.
5. **It can only move numbers.** It may not remove a metric, change an owner, delete an emergency class, or loosen an
   emergency limit. Emergency limits only tighten.
6. **It undoes itself.** A loosening expires after 14 days unless the next review keeps it. If a fault is found by anything
   else (deadman, the Conductor, you) on a loosened metric, the program restores the base and tells the Conductor.
7. **Everything is on the record.** Each change is a ledger event with old, new, why and replay result, and a line in the next
   report.
8. **Starts as advice.** For two weeks the tool applies nothing and writes what it would do; the Conductor reads those lines.

**The alarm quality table** is the evidence for all of this. Per metric over 30 days: rings, time to ack, whether an action on
an item followed, time open. Program-built, from `told.jsonl` and the ledger. A metric that rings often with no action is
noise; one that a fault passed quietly is deaf. The action count can be gamed by notes, so only an item state change counts.

## 5. Arbiter, Auditor, Innovator: where each job goes

**The rule.** One piece of work is judged by Relentless's walled blind checker, the Marker. It sees no budget and no maker's
story. Patterns across much work go to Operations. Numbers go to programs. This matters because the Auditor and Arbiter were
token-blind on your order, and Operations is not: so Operations never judges a single piece of work.

All three are off since the replan. `role_use.py`: Arbiter 0.3% of output acted on, 5 of 235 verdicts settled; Auditor 3.8%;
Innovator 25% of very few outputs.

**Arbiter**

| Did | Goes to |
|---|---|
| Judges done claims in batches | Dropped as a batch. Marker per close: Relentless work always, orders always (section 6), a random sample for the rest |
| FAIL blocks a close, reopens a closed item | Marker FAIL, same lock: below |
| Tier triage of claims (`arbiter_tiers.py`) | Dropped, once the sample replaces it. |
| Escape gets a check that is red on the old build | Relentless (`escape`, TE4). The Marker reads the check |
| Every bar claimed by a check (`modcheck floor`) | Program; a gap reading goes to Operations, which files it |
| Adds new bars | The Designer, in the tree; you validate |
| Signs tree coverage before lock | Marker, blind against the root. Not the Designer: a maker may not sign its own. The Designer's doc needs this edit |
| Tunes the Marker from disagreements | Operations names the pattern; a Relentless item makes the change; `trust` must show it held. Operations never edits the prompt |
| Drafts loosenings | Whoever hits the bar raises it; Conductor brings it to you, as now |
| Doc-growth pass | Dropped as a chair. A size reading in the digest |

**Auditor**

| Did | Goes to |
|---|---|
| No-AI screen of every close (`audit_prescreen.py`) | Stays, as a program on a clock |
| Random sample of closes | Program draws it, keyed so nobody can steer it, Marker reads, FAIL reopens. Rate 1 in 10 (ESTIMATE) |
| AU4 unearned closes | `close_audit.py` as a metric, alarm in range |
| Classifies escapes by layer | Operations, weekly |
| Repeat errors become rules (RO5) | Operations names the class; a Relentless item builds the hook; `rimflow` shows it owed until then |
| Alarm drill and origin (OP5) | Program, Operations reads |
| Samples FOUNDRY's findings decisions | Dropped; no evidence it was read |

**Innovator**

| Did | Goes to |
|---|---|
| Finding curves, RW5 | Program builds it, Operations reads it |
| Retiring rules: each names the assumption it encodes | Operations, weekly: rules and checks that have never fired, proposed for a test. TE3 applies: nothing goes without proof that detection held |
| Better ways for agents to work | Relentless refines itself from its own failures (your word: it "won't work well at first and that's ok"). At most one idea a week in Operations' report |
| Trials | Dropped as a separate system. A trial is an order in a signed set |
| Innovations list | Stays a file; any seat adds a line. Read at the planning session |
| Game ideas, new mods, merging mods; Sunday game review | **Does not fit.** See flag |

**Flag: game ideas.** Your card names Operations and Relentless, and neither is the right home for new game ideas. Your
Oct 26 question, *"What could we be doing much better?"*, also included redesigning agents. I recommend game ideas go to The
Designer, and that each planning session's page carries one line for that question. If this is wrong, the Sunday review is
simply lost.

**Close the chairs in a safe order.** Delete each role's file, schedule entry and `roles.*` reading only after its work has a
live new home, and fix inbound references (`relentless_agent_design` §10, `concept_agent_design` §5 and step 2, the requirement
owner tags, `alarm_routes.json`).

## 6. The power to block a close, and the blind pass

**Recommendation, with a flag.** You said move it to the Relentless close gate. **That gate does not exist as one thing, and
moving it there as stated would lose something.** There are two:
- **The Close gate** (`model.close_refusals`): every close in the project passes it. It holds the lock. An Arbiter FAIL on a
  build stops the close until a new build passes, or your word lifts it. With the Arbiter off, nothing feeds the lock.
- **Relentless's blind check:** a Marker FAIL sends work back to the worker. Nothing reaches the ledger, so today anyone
  could hand-close an item the Marker just failed.

If the power moved only into Relentless, every order run by ring, live or by hand would have no block. So: **keep the lock in
the Close gate, where nothing can walk around it, and change who feeds it. A Marker FAIL goes on the ledger as the verdict the
lock reads.** It lifts the same way: a new build that passes, or your word. WEAK does not lock: the item just stays open.

This is the substance of what you asked, so it needs no card unless you object. Two honest costs:
- **The Marker's false fails.** 1 of 9 good controls failed (95% 2-44%, MEASURED, E1). A wrong FAIL now blocks, not merely
  returns. The maker can't overrule it. The way out is a new build, or the Conductor's word under your authority.
- **It will slow things.** On that same set, only 1 of 11 good controls got a PASS; 7 of 11 read WEAK. Until that improves, most
  good work costs a proof round.

**The blind pass for ticks.** Your card: *"Must a tick need a pass from someone other than the maker? → Yes, a blind pass."*
The tick gets a fourth test: a PASS, on the build that closed, by a judge who never saw the maker's story.

| Order's worker | Who gives the pass |
|---|---|
| Relentless | Marker, already; it is recorded as `marker:blind-check` |
| Ring or hand, offline | New `relentless.py blind-check --item X --sha S`: the same walled run, no worker. Any Conductor hand close in an order takes the same road |
| Live | The Marker cannot run the game. It reads the receipts at the deployed hash; this is weaker and marked. RA_S09 is the first real case. A needs=owner look is itself a blind pass, by you |
| `--no-code` | No build to rerun. The Marker reads the evidence and the finish reading. Stays a hollow tick |

Items outside a signed set keep ruling D1(b): no verdict blocks nothing. Your card was about ticks. Sampling covers the rest.

## 7. The report to the Conductor

Twice a day, 15 lines at most, fixed shape, in `D:\ClaudeWork\rimmandrake\ops_watch\reports\<stamp>.md`:

```
OPS 2026-11-03 07:30   overall: distressed
orders   day 2 of 5, 6 of 15 ticked, 1 lost, 1 flat 2 days
relentless  sane   5 live, 0 stuck; time 41% testing
seats       sane
machine     wrong  disk fine but scratch growth doubles in 3 days
money       sane
incidents   3 open: 2 acked, 1 mine, none past due
changed     raised disk.x 85 to 88, replay held, expires 11-17
needs you   GSS order has no worker since 04:00; Producer told, card if still stuck tonight
drop        nothing
```

**Delivered so an old failure cannot recur:** Operations once diagnosed a jam correctly, and the diagnosis sat unread in a note for 5.5 hours. The report rings the
Conductor and is a row in `told.jsonl`. It stays unacked until the Conductor answers with `rimflow ack`, naming what it did;
past 4 hours it moves on the ladder. The packet's next run shows what the Conductor did. Emergencies do not wait for a report;
they take the incident ladder. Figures the blind roles may not see stay in this file, not on shared items. The Conductor reads
the report and tells you what matters; you are not its reader. Nothing reaches you unread.

## 8. How Dispatch follows 5-day signed orders

Full design in `planning_session_design_2026-11-01.md`. Dispatch stays a program; it decides nothing. A new step on the tick,
every 5th tick, about 10 min (ESTIMATE, as a tick reads the whole ledger), reads the signed file and the ledger, works out what
should be true, and repairs differences. A crash is just the next tick. Your answers shape it:

- **Lifting links:** the program lifts a link in a signed set. It lifts on the **tick**, which is the Close gate plus the
  blind pass plus the finish reading. Your card said the Close gate; the tick is stricter, because a blind pass is now part of
  a tick and a link should not lift on less. A lost tick re-blocks what has not started.
- **The set's end:** a set is at most 5 days. If none follows, the last orders keep running, shown on the Board as
  `OVERTIME day N`. In overtime no new tickets get added, and the signed money ceiling still holds, so overtime ends itself.
  `plan.days_since_advance` still alarms, and one card goes out on day 1.
- **The plan view:** the Board markdown. The program writes one marked block in
  `D:\ClaudeWork\rimmandrake\arena\ARENA_BUILD_BOARD.md`, in the top section agents already keep. Ticks are never typed, and a
  hand edit is overwritten at the next step. That is what keeps your *"REALLY ticked off"* true. The block carries its time, and
  a block going stale is an alarm.

**What must change first.**
- The Dispatcher's seat may only write notes (`DISPATCHER_VERBS`). The step needs its own seat, allowed only link and wait
  verbs, and only on items in the open signed set.
- FOUNDRY's rings and the Producer are both off now. While so, `check` must refuse any `ring:FOUNDRY` order, and a stuck order has
  nobody to replan it. **The Producer must be back on before the first set.**
- `plan.list_age_h` needs the swap the planning doc describes.

**How Operations meets orders.** It reads ticks and reports them. It may not amend orders; that stays the Producer's, and goals
stay yours. If orders and reality part, it says so in the report.

## 9. Build order

All ESTIMATE, in helper days; nothing like this has been timed. Each step ends with its planted fault caught on the real path.

| # | Step | Days |
|---|---|---|
| 1 | Refused run moves the rung; held-back emergency run; reports' missing-report alarm | 0.5 |
| 2 | Marker FAIL feeds the Close gate lock; `blind-check` for non-Relentless closes | 1 |
| 3 | `close_audit` in the digest; OP5 drill; OP6 flag ends; DI4 exempt list; DI5 park expiry | 1.5 |
| 4 | Packet, report form, ack row; retire the weekly assessment; role file rewritten | 1 |
| 5 | Close sample; escape and repeat-class readings | 1 |
| 6 | Delete the three roles, fix references | 0.5 |
| 7 | Alarm quality table, then `ops_tune.py` in advice mode; his band signed | 2 |
| 8 | Two weeks of advice read by the Conductor, then applying | watching only |
| 9 | Planning doc's steps 0 to 7, with tick fourth test, Board block, overtime, own seat | 7 to 9 |

Steps 1 and 2 first: the first unjams the ladder, the second gives the lock a feeder. Step 6 waits for 2, 4 and 5, or the work
would have no home. About 7 days for 1 to 7, then the orders work on top; the planning doc's first hand-run set (its step 0) can
start any time. Foundry owns the items once filed; Relentless may take the offline ones.

## 10. A skeptical read

Pending.
