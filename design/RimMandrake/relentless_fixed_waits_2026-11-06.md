# Relentless fixed waits: profile and inventory (2026-11-06)

Item `RELENTLESS_TICK_MEASURE_OUTLASTS_ITS_NAP`. The owner, 2026-11-06: *"WHY must we wait 10 minutes?! All these
arbitrary pauses cost us a lot of time! Please stop building arbitrary pauses into the system..."*

## 1. One tick, profiled

Instruments: the tick's own journal phases (last 15 ticks, 2026-11-06 05:23-07:34Z) and a 0.5 s `ps` sample of
every child of two live ticks (2026-11-06 07:48-07:53Z). systemd: 5-8 min wall, 3-6 min CPU, 2-9.6 GB memory peak.

| phase | seconds (15 ticks) | what the sample saw in it |
|---|---|---|
| prelude | 4-45 | books sync, `git fetch` |
| steps (all 1106 items, ~50 game items) | 130-351 | `scratch_clone.py clone` for checks (fetch, `git read-tree -mu`, `git checkout-index` into a walled box), `relentless_live_round.py round` (~46 s), `deploy_custom_mods.py --compose biomes` (~16 s), `publish.py` of ledger lines (~8 s), Windows `tasklist`/`powershell` game reads |
| enrol_lease | 11-227 | `scratch_clone.py clone` for builders; each pool-reuse candidate ran `git cherry` once per local tag (~3 s each, 6 tags: 18 s per candidate) |
| staffing_live | 29-111 | live tier and showings |
| flush | 0-90 | `publish.py` |

Every slow call is a blocking subprocess inside one serial loop: the tick IS the wait. From this tick on, each
tick's journal row carries `proc` (the top 8 child commands by seconds waited, with counts) and `proc_s` (their
total), from `src/RimMandrake/rimflow/relentless_tickprof.py`, so the next slow tick names its command itself.

## 2. Cuts made by this item

- **Timer gap 2 min -> 15 s** (`src/RimMandrake/Utils/systemd/rm-relentless.timer`, installed). The gap paced
  nothing: `tick.lock` already keeps one tick at a time, and `game_next` serves a round's end without a tick.
- **`git cherry` only where it can answer** (`scratch_clone.py cherry_on_origin`): a ref that reaches none of the
  asked commits beyond the remotes is skipped. The same answer; a reuse candidate no longer pays ~3 s per old tag.

## 3. Owed: the cut to seconds

`TICKSLOW_REWIRE_CLONES_OFF_THE_BELT`: clone creation and reuse, the live round, the compose deploy and publishing
become detached jobs the tick launches and reads back next tick, so a tick only decides. The `proc` rows above
are its before-measurement.

## 4. Inventory of every fixed wait

Kinds: a **bound** only ends a hung thing (a timeout, a run limit) and delays nothing that is going well; a
**pacing** wait delays a state change on purpose and must give its reason or go; a **budget** defers work to the
next tick, so with a slow tick it costs a whole tick. `RELWAITS_PRUNE_PAUSES_WITH_NO_REASON` owes, for every
pacing row whose reason reads "none given", a measured reason in its comment or its replacement by an event.

Verdicts on the ones that bite now:

| wait | kind | verdict |
|---|---|---|
| `OnUnitInactiveSec` | pacing | cut to 15 s here; justified as a floor against a tight crash loop of the unit |
| `OnBootSec=3min` | pacing | keep: it lets WSL mounts and the books clone come up after a boot (once per boot) |
| `tick_game_budget_s`, `work_launch_per_tick`, `enrol_per_tick` | budget | each costs a whole tick while the tick is slow; revisit after `TICKSLOW_REWIRE_CLONES_OFF_THE_BELT` |
| `unmeasured_retry_s` 6 h, `harness_retry_s` x n | pacing | no reason given: `RELWAITS_PRUNE_PAUSES_WITH_NO_REASON` |
| `live.round_every_s` 30 min, `game.prove_every_s` 15 min | pacing | "pacing only": a round should start when a proof waits and the game is free, not on a clock |
| `help_wait_s`, `unmeasured_recheck_s`, `pool_parked_release_s`, `POOL_IDLE_S` | pacing | no reason given: `RELWAITS_PRUNE_PAUSES_WITH_NO_REASON` |
| `stale_s`, `launch_grace_s`, `stop_force_s`, `stop_quarantine_s`, `run_max_s`, `check_max_s` | bound | keep: they end a dead or hung run and cost nothing on a live one |
| `game.renew_s` 1200 s | bound | its comment says 45 min, the value is 20 min: `RELWAITS_PRUNE_PAUSES_WITH_NO_REASON` |
| `breaker_cool_s`, `ALARM_TOLD_EVERY_S`, `ATTENTION_EVERY_S` | pacing | keep: each gives its reason (a jam's measured length, no flooding of the log) |

The full census (a read-only sweep of `src/RimMandrake/rimflow/relentless*.py`, `relentless_rules.json`,
`scratch_clone.py` and the units, by grep; a few may be missing) follows. Values are as of this commit.


### Timers
| name | value | file:line | gates | reason given |
|---|---|---|---|---|
| OnUnitInactiveSec | 15s | Utils/systemd/rm-relentless.timer:8 | next tick starts 15 s after the previous ends | none given (description: "15 s after each tick ends") |
| OnBootSec | 3min | rm-relentless.timer:7 | first tick after boot | none given |
| TimeoutStartSec | 1200 | Utils/systemd/rm-relentless.service:10 | unit kill; GAME_NEXT_WAIT_S mirrors it | none given |
| GAME_NEXT_WAIT_S | 1200 | relentless.py:6625 | game-wake waits for tick.lock this long else "next tick serves it" | "the unit's own kill" |
| TICK_WAITS_GAME_NEXT_S | 180 | relentless.py:6626 (+6734 rules key tick_waits_game_next_s) | tick waits for a game pass before skipping | "a game pass is short; losing the turn costs two more minutes" |
| tick_game_budget_s | 240 | rules:138 | game steps stop for this tick after this long | long note: ops_watch tick_age alarm at 10 min |
| staffing.tick_gap_max_s | 600 | rules:209 | caps one gap's dt in the staffing clock | none given |

### Sleeps / polls
| name | value | file:line | gates | reason |
|---|---|---|---|---|
| settle_wait / staffing.settle_s | 15 s | relentless.py:2579,6067; rules:213 | pause before a claim is re-read | "a claim that passed the guard just before the reservation reaches its shard in this time" |
| tick.lock poll (game wake) | sleep 2 | relentless.py:6680 | poll up to GAME_NEXT_WAIT_S | none given |
| tick.lock poll (game next) | sleep 2 | relentless.py:6742 | poll up to 180 s | none given |
| seeds memory wait | sleep 30 (until mem >= min+4 GB) | relentless_seeds.py:866 | start of next replay case | none given |
| seeds verdict poll | sleep 15 | relentless_seeds.py:877 | poll to check_max_s+launch_grace_s | none given |
| seeds checker-exit poll | 16 x sleep 15 (=240 s) | relentless_seeds.py:889-891 | wait for checker to exit after expiry | none given |
| stage stop poll | sleep 2 (STOP_GRACE_S 90) | relentless_stage.py:36,142 | game graceful stop before /F | "live_session.stop_game's graceful wait, then /F" |
| stage forced-stop poll | sleep 2, 30 s | relentless_stage.py:146-147 | after /F | none given |
| stage post-exit settle | sleep 5 | relentless_stage.py:153 | before list written | "exit's own writes (Player.log, ModsConfig) settle" |
| LAUNCH_SETTLE_S | 20 | relentless_stage.py:37,188 | after launch before log read | "Steam's own hand-off before the log is read" |
| START_GRACE_S | 180 | relentless_stage.py:41 | no "died" before this | "cold Steam may not have the game process yet" |
| MARGIN_S / REMEDY_MAX_S / REMEDY_TOTAL_S | 120 / 480 / 420 | relentless_stage.py:38-40 | budget left for game-ready / remedies | "inside the supervisor's stage_idle_s (600)" |
| offbox_max_s | 120 | rules:69 | off-box command bound | none given |
| live.proof_max_s / plan_max_s / gate_plan_max_s | 600 / 500 / 180 | rules:156-158 | live proof/plan bounds | none given |
| relentless_seeds PROOF_S | 420 | relentless_seeds.py:48 | proof bound | none given |
| READING_TTL_S | 30 | relentless_game.py:50 | cached game reading reused | none given |

### Cooldowns & not_before
| name | value | file:line | gates | reason |
|---|---|---|---|---|
| not_before via snag wait_hours | per snag, capped MAX_WAIT_HOURS=6 h | relentless.py:72,1115-1116 | no worker starts before | "a worker's word cannot park an item for longer" |
| snag_again_wait_h | 1 h per earlier same-class snag | rules:109 | repeat snag delays restart | "nothing changes for a worker to find" |
| breaker_cool_s (x2^n) | 900 s | rules:131; relentless.py:4376 | launch breaker open time | "DI2 in operating_requirements" |
| breaker_cool_max_s | 1800 s | rules:132; relentless.py:4261 | cap on a cool | "14400 slept 6 h on the 2026-11-01 jam" |
| breaker_same_cause_window_s | 21600 | rules:135 | 2 opens same cause = emergency | "that jam's length" |
| breaker_ack_min | 30 | rules:140 | breaker acknowledgement | none given |
| help_cool_h | 6 h | rules:185; relentless.py:1298-1300 | one consult per item per 6 h | "one per item per help_cool_h" |
| help_wait_s | 2400 | rules:188; relentless.py:5714 | wait for a consult answer | none given |
| help_max_s | 1200 | rules:187 | consult run bound | none given |
| unmeasured_recheck_s | 1800 | rules:39; relentless.py:566 | recheck_at after an unmeasured verdict | none given |
| harness_retry_s (x n) / max | 1800 / 14400 | relentless_game.py:64,1699 | restage after harness fail (retry_at) | "staged again after harness_retry_s x the count" |
| live.unmeasured_retry_s | 21600 (6 h) | rules:162; relentless_live_round.py:89 | unmeasured proof retried | none given |
| live.round_every_s | 1800 | rules:160; relentless.py:6589 | one live round at most this often | "Pacing only" |
| game.prove_every_s | 900 | rules:165; relentless_game.py:1960 | reprove interval | none given |
| RECARRY_EVERY_S | 600 | relentless_game.py:1604 | stale build asks carry again | "each ask is a few git calls" |
| ALARM_TOLD_EVERY_S | 6 h | relentless.py:219 | each alarm kind told once | "inside incident.py event_quiet_min" |
| ATTENTION_EVERY_S | 6 h | relentless.py:4281 | crossing kind one line per 6 h | "a standing crossing does not flood the log" |
| PAUSE_ALARM_S | 6 h | relentless.py:4706 | paused runnable content told to Conductor | none given |
| FRESH_RULING_S | 48 h | relentless.py:4705 | ruling passes a scoped pause | "section 3 of the spec" |
| staffing alarm_after_min / jam_alarm_s | 30 min / 300 s | rules:205-206 | staffing under-target alarm | none given |
| staffing.hold_s | 3600 | rules:195 | clean-reading hold per stage | "hold_s at full stage" (staffing note) |
| expedite TTL_S | 4 h | relentless_expedite.py:20 | expedite flag lifetime | none given |
| CONTROL_AGE_DAYS | 5 | relentless_seeds.py:351 | min age of a replay control | none given |
| OWNER_NOTE_DAYS | 14 | relentless_showing.py:48 | owner note age | none given |

### Stale / idle windows
| name | value | file:line | gates | reason |
|---|---|---|---|---|
| stale_s | 1500 | rules:115; relentless.py:5086 | run with no sign for this long is stale | none given |
| launch_grace_s | 240 | rules:116; relentless.py:5085,5194 | no stale before this after start | none given |
| account_settle_s | 240 | rules:118; relentless.py:5211,5450 | dead run w/o receipt waits before counting | "waits this long before it counts" |
| run_max_s / check_max_s | 3600 / 1800 | rules:113-114 | run / check bound | none given |
| stop_force_s / stop_quarantine_s | 180 / 600 | rules:119-120; relentless.py:5028-5029 | stop politely, then force, then quarantine | none given |
| pool_parked_release_s | 1800 | rules:127; relentless.py:4550 | parked clone released after | none given |
| POOL_ORPHAN_IDLE_S | 3600 | relentless.py:95,4472 | orphan clone rank | none given |
| POOL_IDLE_S | 3600 | Utils/scratch_clone.py:362 | pool clone idle before reclaim | none given |
| ALLOCATION_FRESH_S | 1800 | relentless.py:87,2611 | allocation record fresh | none given |
| game.renew_s / showings.renew_s | 1200 | rules:165; relentless_game.py:2139; relentless_showing.py:425 | bridge hold lapses | "a hold with no event for 45 min is anyone's" (comment disagrees with 1200 s=20 min) |
| game.stage_max_s | 3600 | rules:165 | staging bound | none given |
| showings build_max_s / judge_max_s | 3600 / 1800 | rules:167 | showing bounds | none given |
| staffing.tomb_max_s | 172800 (48 h) | rules:214; relentless.py:5564 | tombstone age | none given |
| breaker_same_cause window | see cooldowns | | | |

### Budgets deferring to next tick
| name | value | file:line | gates | reason |
|---|---|---|---|---|
| enrol_per_tick | 2 | rules:27 | enrolments per tick | none given |
| staffing.launch_per_tick | 16 | rules:197 | check/consult launches per tick | owner Q 2026-11-06 "no practical cap" |
| staffing.work_launch_per_tick | 8 | rules | builder clones per tick | "one shared count let two checks stop every builder" |
| check_backlog_max | 4 | rules | queued checks | none given |
| "clones per tick" hold | n/a | relentless.py:5289,5760 | launch refused when tick's clone count used | none given |
| tick_game_budget_s | 240 | see timers | | |
| SLOW_STEP_S | 20 | relentless.py:6614 | naming only (no deferral) | "named in tick journal" |
| RECARRY / pool no_room | per tick | relentless.py:6138 | make_room hold for rest of tick | none given |

### Other
| name | value | file:line | gates | reason |
|---|---|---|---|---|
| close_retry | next tick | relentless.py:5567-5606 | failed close retried once | "a retry is a new decision" |
| MAX_WAIT_HOURS | 6 | relentless.py:72 | cap (listed above) | |
| help_launch_tries | 3 | rules:189 | consult runs before item carries | none given |
| stage_tries / showings tries | 2 | rules:165,167 | restage count | none given |
| unchanged_returns_limit / same_failure_limit / unmeasured_limit | 9 / 2 / 2 | rules | count-based, not time | none given |
