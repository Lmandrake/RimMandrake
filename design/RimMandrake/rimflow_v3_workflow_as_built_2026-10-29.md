# RimFlow v3 agent workflow, as built (2026-10-29)

Status: as-built description, written 2026-10-29 around 13:00 PDT from the bench clone (`/home/mandrake/rm/bench`)
at commit 6b7127714c. Item `V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR`, step 1 of 3. The next step is a skeptical review
by a second model. This document describes. It does not judge or recommend.

Owner's words on the item: document the agentic workflow, then a skeptical review, for example *"the Steve desktop not
being used correctly or not being assigned the right work, but being counted as productive because it is using CPU
hours"*.

**Tags.** Every claim carries one tag:
- **[LIVE]**: running now. The tag cites a `file:line` or a config key with its value.
- **[OFF]**: built but switched off.
- **[DESIGNED]**: written in a design or role file but not built.
- **UNVERIFIED**: I could not check it against code, config or runtime state.

Paths are relative to the repo root unless they are absolute. `D:\ClaudeWork\...` is the same place as
`/mnt/d/ClaudeWork/...` under WSL. All times are local (America/Los_Angeles, PDT on this date).

**Main sources.**
- `src/RimMandrake/rimflow/dispatcher_schedule.json` (147 lines; cited below as `sched:<line>`).
- `src/RimMandrake/rimflow/dispatcher.py` (1503 lines; cited as `disp:<line>`).
- `src/RimMandrake/rimflow/role_launch.py` (1910 lines; cited as `rl:<line>`).
- `src/RimMandrake/rimflow/seat_restart.py` (cited as `sr`).
- `src/RimMandrake/rimflow/roles/*.md`.
- `design/RimMandrake/rimflow_v3_2026-10-26.md` (cited as `v3design`).
- The systemd user timers (`systemctl --user list-timers`).
- The Dispatcher's runtime state at `/mnt/d/ClaudeWork/rimmandrake/dispatcher/state.json`, read about 12:50 PDT.

---

## 1. Overview

RimFlow v3 splits the work of the repo across **people, AI seats, scheduled AI roles and plain programs**.

**People.**
- **Lukas, the owner.** He sets direction, answers question cards and switches roles on and off.

**AI seats.** These are long-lived interactive Claude Code sessions, each in its own terminal tile and git clone.
- **BENCH.** The owner's workshop. Its session name is `CONDUCTOR` and its tile alias is "AGENT BENCH" (`sched:24`). Clone: `/home/mandrake/rm/bench`.
- **FOUNDRY.** The worker seat. Its session name is "AGENT FOUNDRY" and it runs on sonnet (`sched:22`). Clone: `/home/mandrake/rm/foundry`.

**Scheduled AI roles.** Each role is a headless one-shot `claude -p` run, launched by a program at clock slots or on events.
- Conductor.
- Operations.
- Producer.
- Arbiter.
- Auditor.
- Innovator.

Every role is `enabled: true` today (`sched:48,64,79,95,110,126`; `golive.roles` at `sched:30`). They were switched on
2026-10-28 by commit 4d9171a1e5 ("v3 trial night").

**Programs (no AI).**
- **The Dispatcher.** `dispatcher.py tick --apply`, every 2 min from the timer `rm-dispatcher.timer`. It runs from a third clone, `/home/mandrake/rm/dispatch`. Each tick it:
  - watches the seats;
  - rings their "doorbell" to wake an idle FOUNDRY;
  - launches the roles through `role_launch.py`;
  - restarts a seat through `seat_restart.py`;
  - raises alarms.
- **ops_watch.** Every 15 min. It measures accounts, runway and burn, and writes `status.json`. Every role launch gates on that file.
- **testq.** Every 1 min. It queues and runs automated game test jobs.
- **About 25 other systemd user timers.** They cover telemetry, mirror, pulse/digest, health, reaping and selftests (§3).

**Where work lives.** Work items live in a sharded, append-only ledger, `infrastructure/state/ledger/events/<SEAT>.jsonl`.
- It is driven only through `python3 src/RimMandrake/rimflow/cli.py`, called `rimflow`.
- Queue views are projected to `queue/*.md`.
- Seats claim items, renew a 45-min lease while working (`lease.py`), and close with a sha.
- Closes are judged by the Arbiter and the interim GPT reviewer. Today the Arbiter's verdicts are advisory and the interim reviewer gates (`sched:65` `"verdicts": "advisory"`).
- The Auditor samples the closes.

```
                         Lukas (owner)
             messages | question cards | OFF files | schedule edits
                               |
              +----------------+-----------------------------+
              |                                              |
      BENCH seat (interactive, "CONDUCTOR")          role OFF files / enabled flags
      never woken by the Dispatcher                          |
              |                                              v
              |      systemd: rm-dispatcher.timer (every 120 s after the last run)
              |                         |
              |                  dispatcher.py tick
              |    +--------------------+------------------------+-----------------+
              |    | observe seats      | role_launch.decide     | seat_restart    | alarms -> ledger notes
              |    | (claude agents)    | (clock slots, events)  | (FOUNDRY ctx    | on RIMFLOW_V3_BUILD_
              |    v                    v                        |  backstop)      | DISPATCHER_FIRST
              |  doorbell ring   systemd-run rm-role-<name>-<t>  v
              |  armed/->inbox/  claude_bounded.sh -p ...       kill + relaunch FOUNDRY tile
              |    |                    |
              |    v                    v
              |  FOUNDRY seat     Conductor 08:00/20:00   Operations 07:30/19:30 (+alarm runs)
              |  (claims ledger   Producer 09:00 (+event) Arbiter 11:00/17:00 (if pending work)
              |   work, testq,    Auditor 13:00           Innovator Tue/Fri/Sun 15:00
              |   leases)                 |
              +--------+----------------- + ---- rimflow ledger (events/<SEAT>.jsonl), ./publish
                       |
     ops_watch (every 15 min) -> status.json -> gates every role launch
     testq-tick (every 60 s) -> game test jobs -> ingest -> ledger
```

**How work flows, in one paragraph.**
1. A finding becomes a ledger item, filed by a seat, a role or a program.
2. The Producer orders the work daily (09:00) and plans it weekly (Wednesday).
3. FOUNDRY is rung awake by the Dispatcher when it is idle and the queue has a ticket for it. It claims the item and works it under a lease.
4. FOUNDRY closes the item with a sha and verify evidence.
5. The interim reviewer gates the close. The Arbiter gives an advisory verdict on it (11:00/17:00).
6. The Auditor samples closes and Arbiter verdicts (13:00).
7. Operations watches cost and runway (07:30/19:30 plus alarm runs).
8. The Conductor runs a quick check twice a day (08:00/20:00) and relays proposals to the owner.
9. The Innovator proposes process changes (Tuesday/Friday) and design reviews (Sunday).

---

## 2. Per-actor cards

Fields:
- **Purpose.**
- **Appears.** Its trigger, schedule and gate.
- **Disappears.** How it ends: finishes, is killed, or says goodbye.
- **Runs/day.**
- **Caps.**
- **Inputs.**
- **Outputs.**
- **Decides alone.**
- **Hands to.**
- **Owner touchpoints.**
- **Off switch.**

### 2.1 Gates common to every scheduled role (role_launch.py)

A role run starts only when every gate below passes, checked in this order [LIVE, `rl` header lines 1-100, constants `rl:116-165`]:

1. **Enabled.** `enabled: true` on the role in the schedule [LIVE, every role true].
2. **Off file absent.** The role's `off_file` must not exist [LIVE; the paths are in each card below].
3. **Fresh ops_watch status.** `D:\ClaudeWork\rimmandrake\ops_watch\status.json` must exist and be fresh.
   - The launch is refused if the file is missing, older than `OPS_STALE_S` = 2700 s (`rl:116-165`; also top-level `ops_stale_s` 2700, `sched:3`), or marked UNMEASURED.
   - A future timestamp is tolerated up to `FUTURE_TOL_S` = 300 s.
4. **Throttle band.** This comes from the role's account runway: GREEN ≥1.5, AMBER ≥1.0, RED ≥0, FLOOR when week_left < 10 %.
   - [LIVE but neutralized] Every band on every role is `"slots": "all"` with `quick_cap_x` 1.0 (for example `sched:52-55`), so the band no longer changes what runs.
   - Neutralized 2026-10-28 by commit d92c4c825e, on the owner's order: *"Stop the whole account rated RED on runeway crap. Just do the checkout."*
   - Throttle order as designed: Innovator, then Auditor, then Producer, then Arbiter, then Operations; the Conductor is never throttled (`v3design`).
5. **Daily token cap.** The day's weighted tokens must still be under the role's `daily_token_cap`.
6. **account_pick verdict.** `account_pick` must return KEEP, SWITCH, UNMEASURED or HOLD (§2.13). `act` is "recommend" and `hold` is `[]` (`sched:141`), so the verdict blocks nothing today.

**Slot rules** [LIVE, `rl` header]:
- A clock slot runs at most once per local day.
- It runs no later than `slot_late_s` after the slot time. The default is 3600 s (`rl:116-165`), and every role sets 3600.
- A missed slot is journaled as missed and is **never run late**.
- `after_role: Operations` (Conductor `sched:60`, Producer `sched:115`) means: do not run until Operations has run its slot today.
  UNVERIFIED: the exact wait or skip semantics when Operations misses its slot.
- Event runs read events with a cursor, looking back `EVENT_LOOKBACK_S` = 6 h.
- An unreadable ledger means UNMEASURED, and nothing launches.

**Launch mechanics** [LIVE]:
- A transient unit `systemd-run --user rm-role-<name>-<epoch>` runs `claude_bounded.sh -p <prompt> --output-format json`. The Arbiter's runs add `--json-schema`.
- An optional `pre_launch` program runs first (in each card).
- The only hard stop is wall time, `run_max_s`. The default is 1800 s, and some roles set 2700 s.
- **Tokens are not stopped mid-run.** A run over its `run_token_cap` is an alarm after the fact (open alarm kinds `role:<name>:overbudget` in state.json).
- Weighting `weighted_v1`: input 1, cache write 1.25 (5 min) or 2 (1 h), cache read 0.1, output 5.

**Run-now** [LIVE, `rl:1393`]:
- A run outside the clock can be requested with `--by` and `--why`.
- Modes: run, quick, weekly, economy.
- The request lives `RUN_NOW_TTL_S` = 3600 s.
- It passes the same gates. On 2026-10-28 an Innovator run-now was refused twice with "band RED", before the bands were neutralized.

**Token blindness** [LIVE]:
- Every role except Operations is token-blind. It reads `digest_blind.md` and `blind_view.py` output, never cost figures.
- Only Operations is `token_aware: true` (`sched:96`).

**Helpers** [LIVE as a rule in the role files]:
- The owner's limit is 2 helpers at once across ALL roles together.
- Until `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` closes, a headless role runs **no** helpers (auditor.md §Helpers; arbiter.md; conductor.md). The schedule's `helpers_max` 2 (Arbiter, Auditor, Innovator) is therefore not used.
- The Conductor's interactive session mode has `session_helpers_max` 3 in every band (`sched:52-55`), yet its role file states the owner's limit of 2. This is a contradiction.
- UNVERIFIED: whether any code enforces the cross-role helper count. `helper_budget.enabled` is true (`sched:14`); see §2.14.

**Scope stop** [LIVE, `rl:116-165`]:
- `SCOPE_GRACE_S` = 600 s and `SCOPE_STOP_S` = 30 s govern stopping a role run whose scope overran. The alarm kind `role:Operations:scope` is open.
- UNVERIFIED: the exact trigger condition.

### 2.2 Dispatcher (program)

- **Purpose.** Keep the seats moving and the roles on time. It observes; it does not judge work.
- **Appears** [LIVE]:
  - systemd user timer `rm-dispatcher.timer`: `OnBootSec=3min`, `OnUnitInactiveSec=120s`, `AccuracySec=5s`.
  - The service runs `dispatcher.py tick --apply` from `/home/mandrake/rm/dispatch` with `TimeoutStartSec=600`.
  - The internal tick budget is `tick_budget_s` 420. `tick_s` is 120 (`sched:4`).
- **Disappears.** Each tick exits when done. systemd kills it at 600 s.
- **Runs/day.** About 700: one tick every 120 s plus its own run time, since the timer counts from when the last run ended.
- **Order inside one tick** [LIVE, `disp:316-570`]:
  1. Supervise running role units first.
  2. The account gate.
  3. The `PAUSE` file at `D:\ClaudeWork\rimmandrake\dispatcher\PAUSE`. If present, it withdraws every ring and does nothing more. It is absent today.
  4. Seats marked off: withdraw their rings.
  5. The agents gate: `claude agents --json`. If that is unreadable, the state is UNMEASURED and nothing is done (`disp` header lines 1-58).
  6. Role decisions (role_launch).
  7. seat_restart decisions.
  8. Per seat, in order: verify a pending ring, recover a dead seat, or wake an idle one.
- **Ring verification** [LIVE, `disp:316-570`; values from `sched:5-9`]:
  - Consumed, and a handoff is seen (a claim/start or a lease take): **verified**.
  - Consumed, but no handoff within `handoff_s` 600: `woke_no_handoff`, then a cooldown of `cooldown_s` 3600.
  - Not consumed within `verify_s` 300: withdraw, then retry.
  - After `max_retries`+1 attempts (2+1): an `undelivered` alarm and a cooldown.
- **Dead seat.** No sign of life for `dead_after_s` 600 (`sched:10`) means dead.
  - `recover_dead` is false for both seats (`sched:22,24`) and `golive.recover_dead` is `[]` (`sched:30`), so a dead seat raises an **alarm only** [LIVE].
  - `recover_verify_s` is 300 and `recovers_per_seat_day` is 3, but neither is used while recovery is off [OFF].
- **Wake.** All of these must hold:
  - The seat has been idle ≥ `stall_after_s` 240 (`sched:5`).
  - The seat has `wake: true`. Only FOUNDRY does (`sched:22`); BENCH is `wake: false` (`sched:24`).
  - Its doorbell is armed with a matching session id.
  - A peek at the queue finds a ticket for it.
  - The caps allow it.
  - **Owner gate.** A ticket that needs the bridge, the running game or a deploy (GAME_NEEDS) is held unless the owner has been MEASURED idle ≥ `owner_idle_s` 1200 (`sched:12`) by `idle_probe`.
  - The account gate passes.
- **Caps** [LIVE, `sched:20`]:
  - `wakes_per_seat_hour` 12, `wakes_per_seat_day` 96, `wakes_per_day` 120, `recovers_per_seat_day` 3.
  - BENCH raised these on 2026-10-29 from 6/48/80, per the `_why` (item `FOUNDRY_IDLE_DIAGNOSE_CAP_STARVES_TRIAGE`).
  - The code defaults, used when a key is absent, are 3/30/80/3 (`disp:99`).
- **Alarms** [LIVE]:
  - Alarms become ledger notes on `alarm_item` `RIMFLOW_V3_BUILD_DISPATCHER_FIRST`, plus token notes on `OPERATIONS_MONITOR_ACCOUNTS_OFF_SHARED_TABLE`. `ledger_notes` and `publish` are true.
  - Each alarm kind is rate-limited to once per `alarm_every_s` 21600 = 6 h (`sched:13`, `disp:876`).
  - Hold alarms repeat every `HOLD_ALARM_EVERY_S` 6 h (`disp:573`).
- **State.** All under `D:\ClaudeWork\rimmandrake\dispatcher\`: `state.json`, `journal.jsonl`, `runs.json`, `roles/`, `restart/`, `helper_budget.json`, `PAUSE`.
- **Decides alone.** Ring or not, launch or not, restart or not, alarm or not. These are mechanical.
- **Hands to.**
  - FOUNDRY, by doorbell.
  - Roles, by launch.
  - The ledger, by alarm notes, which Operations alarm runs and the Conductor read.
- **Owner touchpoints.** None directly. Alarms reach him only through the Conductor or Operations relays.
- **Off switch.** The `PAUSE` file (rings only; role launches: UNVERIFIED whether PAUSE also stops them); `systemctl --user stop rm-dispatcher.timer`; `enabled: false` per seat or role.

### 2.3 Doorbell (the mechanism that wakes a seat)

- **Purpose.** Wake an interactive seat that has gone idle, without typing into its terminal.
- **How it works** [LIVE]:
  1. The seat's Stop hook (asyncRewake) writes `armed/<SEAT>.json` with its session id and waits.
  2. The Dispatcher rings by writing `inbox/<SEAT>.json`.
  3. The hook sees the ring, moves it to `consumed/`, and re-wakes the session with the ring text.
  - Poll interval `POLL_S` 3 s. Maximum wait `RM_DOORBELL_MAX_WAIT_S`, default 23 h. After that the hook exits, and the seat cannot be rung until its next Stop.
- **Disappears.** When rung, or when the maximum wait elapses.
- **Off switch.** Not arming (the seat never stops); `wake: false`.
- **Day-one evidence** [LIVE, journal tail of 400 lines]: 53 FOUNDRY rings, 49 verified, 5 `woke_no_handoff`.

### 2.4 seat_restart (program, inside the Dispatcher tick)

- **Purpose.** Restart a seat whose context is too full (a "backstop"), or restart one on request.
- **Appears** [LIVE, `sched:32-35`; `enabled: true`, `dry: false`]:
  - FOUNDRY has `backstop: true`. The restart fires when context ≥ `backstop_ctx_tokens` 110000 and the seat has been idle ≥ `backstop_idle_s` 1800, with `grace_s` 30.
  - A request flows through request → pending → claimed → killed → relaunched.
- **Defaults** [LIVE, `seat_restart.py` DEFAULTS]:

  | setting | value | setting | value |
  |---|---|---|---|
  | grace_s | 120 | quiet_s | 30 |
  | busy_ticks | 3 | verify_s | 90 |
  | arm_s | 900 | intile_wait_s | 30 |
  | intile_window_s | 90 | backstop_ctx_tokens | 110000 |
  | backstop_idle_s | 1800 | helper_stale_s | 3600 |
  | game_hold_s | 3600 | cooldown_s | 1800 |
  | hold_alarm_s | 3600 | request_max_age_s | 3600 |
  | claimed_max_s | 300 | owner_idle_s | 120 |
  | backstop_owner_idle_s | 1200 | fence_s | 1020 |
  | ring_hold_s | 600 | | |

- **Kill and relaunch** [LIVE]:
  - Only human input cancels a pending restart.
  - The kill is SIGTERM, then SIGKILL after 10 s.
  - The tile relaunches through `seat_loop.sh` / intile, with `launch_fleet.ps1` as the fallback.
- **Day-one state** [LIVE]: the FOUNDRY restart record reads `cancelled` (new input).
- **Not covered** [DESIGNED]: BENCH (no backstop entry), and a Conductor "goodbye" restart, which is designed but not built.
- **Off switch.** `seat_restart.enabled: false`, or `dry: true`.

### 2.5 FOUNDRY seat (interactive AI worker)

- **Purpose.** Do the queued build and test work.
- **Appears.**
  - Rung by the Dispatcher when it is idle with a ticket waiting (§2.2).
  - Relaunched by seat_restart (§2.4).
  - Or launched by hand.
- **Disappears.** It stops on its own when it has no work, which arms its doorbell. Or seat_restart kills it.
- **Runs/day.** Up to 96 wakes a day (cap), 12 an hour.
  - Day one: 53 rings in the 400-line journal tail.
  - UNVERIFIED: the full-day count.
- **Model.** sonnet (`sched:22`). Clone: `/home/mandrake/rm/foundry`.
- **Inputs.** The ledger queue, testq results, ring text.
- **Outputs.** Commits, ledger claims, starts, closes and notes, and `./publish`.
- **Decides alone.** How to do a claimed item, within its charter (`infrastructure/agents/FOUNDRY.md`, UNVERIFIED: not read for this doc).
- **Hands to.** The Arbiter and interim reviewer (closes); the Auditor (samples).
- **Owner touchpoints.** UNVERIFIED.
- **Off switch.** `seats.FOUNDRY.enabled` or `wake: false`.
- **Day-one state** [LIVE]: in `cooldown` with `last_verified` set; `cap:FOUNDRY` is an open alarm kind.

### 2.6 BENCH seat (the owner's interactive workshop)

- **Purpose.** The owner's own working session. It holds the "CONDUCTOR" session name.
- **Appears.** When the owner opens it. It is **never woken** by the Dispatcher (`wake: false`, `sched:24`).
- **Disappears.** When the owner closes it. There is no backstop restart for it.
- **Model.** opus (`sched:24`). It owns all FlowWorks and GSS work (standing ruling).
- **Note.** This documentation run executes inside a BENCH helper. The BENCH session id in state.json equals this session's id.

### 2.7 Conductor (role; also the BENCH session when it is live)

- **Purpose.** The owner's chief of staff. It keeps the goals in `CONDUCTOR_GOALS.md`, relays OPS PROPOSAL / OPS DECISION and CUT DECISION, runs quick checks, and holds a light close-out at goodbye (`roles/conductor.md`).
- **Appears** [LIVE]:
  - At the `quick_checks_local` slots 08:00 and 20:00 (`sched:50`), after Operations (`after_role`, `sched:60`).
  - Its `pre_launch` is `delegated_digest.py --pre-launch`.
  - **Window hold:** no headless Conductor run while the "AGENT CONDUCTOR" window is live (`rl:1133`; `window_name`, `sched:59`).
- **Disappears.** The run ends, or hits `run_max_s` 1800.
- **Runs/day.** 2.
- **Caps** [LIVE, `sched:50-51`]: `quick_token_cap` 450000 per run; `daily_token_cap` 1350000; `session_week_pct_cap` 6 (percent of the account's week, for the interactive session).
- **Run steps** (conductor.md): quick-mode steps 1-4; at the scheduled check, steps (a) through (g). It appends a 3-5 line report to `D:\ClaudeWork\rimmandrake\conductor\log.md`.
- **Inputs.** An allow-list of sources (conductor.md). Some sources are closed to it, for example cost figures, which it is blind to.
- **Outputs.** `log.md`, ledger notes, and relays to the owner.
- **Decides alone.** Routing of questions, and the quick-check findings.
- **Hands to.** The owner (proposals, cut decisions, questions); FOUNDRY and the queue (tickets); the Producer (TESTQ mod decisions are the Producer's; the Conductor applies them).
- **Owner touchpoints.** It is the main one. Other roles "never talk to him directly" and go through the Conductor (auditor.md, arbiter.md).
- **Off switch.** `D:\ClaudeWork\rimmandrake\conductor\CONDUCTOR_OFF`, or `enabled: false`.
- **Ledger item.** `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE`.
- **Day one** [LIVE, state.json]: the 08:00 quick run used 233,151 tokens. On 10-28 both its slots were missed.
- **Contradiction.** Its `_why` says AMBER/RED runs only the 20:00 check, but the bands are neutralized (§2.1).

### 2.8 Operations (role; the only token-aware AI)

- **Purpose.** Watch the accounts, burn and runway; turn alarms into action; propose economy changes to the owner.
- **Appears** [LIVE, `sched:98,108`]:
  - At `runs_local` 07:30 (the economy pass) and 19:30.
  - Alarm runs on `OPS_*` items spawned from `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE`, with `alarm_runs` true. Their limits are `alarm_run_gap_s` 3600, `alarm_runs_per_alarm_per_day` 1 and `alarm_runs_per_day` 2.
- **Disappears.** The run ends, or hits `run_max_s` 1800.
- **Runs/day.** 2 clock runs plus up to 2 alarm runs, so at most 4.
- **Caps** [LIVE]: `run_token_cap` 450000; `economy_token_cap` 550000 (`sched:99`); `daily_token_cap` 1650000.
- **Inputs.** `ops_watch` status and the token tables.
- **Outputs** (operations.md):
  - Owner-only proposals at `D:\ClaudeWork\rimmandrake\ops_watch\owner\OP-<ts>.md`.
  - `REPLAN REQUEST RR-<ts>` to the Producer.
  - Ledger notes on `OPERATIONS_MONITOR_ACCOUNTS_OFF_SHARED_TABLE`.
- **Helpers.** None.
- **Decides alone.** Diagnosis of an alarm; whether to file a replan request.
- **Hands to.** The owner (proposals, through the Conductor relay); the Producer (replan request).
- **Owner touchpoints.** OP proposals, the account/runway picture, and the v3-vs-v2 cost verdict (designed; §2.13).
- **Off switch.** `D:\ClaudeWork\rimmandrake\ops_watch\OPERATIONS_OFF` (`sched:107`), or `enabled: false`.
- **Day one** [LIVE, state.json]:
  - The 07:30 economy run used 372,782 tokens.
  - Alarm runs: `OPS_STEVE_UNSTICK_UNCLAIMED_0B75` (256,967) and `alarm:RUNWAY_LOW:accounts.steven.runway` (319,552). That reached alarm_day n=2, so `OPS_STEVE_DIAGNOSE_INVALID_CE0E` was held.
  - Open alarm kinds: `role:Operations:scope` and overbudget.
- **Stale role file.** operations.md's band table (AMBER: no 07:30 run; RED ×0.75) no longer matches the neutralized bands.

### 2.9 Producer (role)

- **Purpose.** Order the work: a daily list, a weekly plan, a replan when a plan fails, and the cut list.
- **Appears** [LIVE, `sched:112-115`]:
  - At `runs_local` 09:00 after Operations. Wednesday's run is mode weekly (`weekly_plan_weekday` "Wed").
  - Event runs on `plan_step_failure` and `replan_request` (prefix "REPLAN REQUEST"), at most 1 a day, with `plan_scope` [raised, row].
- **Disappears.** The run ends, or hits `run_max_s` 1800.
- **Runs/day.** 1 plus up to 1 event run.
- **Caps** [LIVE]: `run_token_cap` 800000; `daily_token_cap` 2000000. The daily cap was raised by commit de4815dbaa, "owner: less caution". Its `_caps_why` text quotes older numbers.
- **Outputs** (producer.md):
  - The run folder `D:\ClaudeWork\rimmandrake\producer\<ts>_<mode>\plan.md`, ending "RUN COMPLETE".
  - A `## verify` block written before any raise.
  - The WIP cap.
  - The TESTQ mod choice, which the Conductor applies.
  - The cut-list state machine: RR → CUT LIST -r<N> → CUT DECISION (owner, via the Conductor) → CUT APPLIED.
- **Hands to.** FOUNDRY (ordered queue); the Conductor (cut lists for the owner, TESTQ mods).
- **Off switch.** `D:\ClaudeWork\rimmandrake\producer\PRODUCER_OFF` (`sched:123`), or `enabled: false`.
- **Day one** [LIVE]: the 09:00 run used 595,410 tokens, plus "event#1" at 388,130. Open alarm kind `role:Producer:cap`.
- **Cadence item.** `PRODUCER_CADENCE_DESIGN_MORE_THAN_WEDNESDAYS` is open (`design/RimMandrake/producer_cadence_2026-10-29.md`). Owner card answers were recorded 2026-10-29 (commit d09d1910f9) [DESIGNED; not applied to the schedule as of 6b7127714c].

### 2.10 Arbiter (role)

- **Purpose.** Judge closed work: does the evidence meet the item's `## verify` bar?
- **Appears** [LIVE, `sched:66`]:
  - At `runs_local` 11:00 and 17:00, but only when `slot_when: pending_work` finds escapes, unresolved verdicts, done claims or a verify backlog.
  - Its `pre_launch` runs `isolated_evidence.py --budget-s 900`, then `arbiter_tiers.py --cap 6`, with `pre_launch_max_s` 1200.
- **Disappears.** The run ends, or hits `run_max_s` 2700 (`sched:76`).
- **Runs/day.** 0 to 2.
- **Caps** [LIVE]: `run_token_cap` 500000; `daily_token_cap` 1250000; `helpers_max` 2 (unused, §2.1).
- **Verdicts** (arbiter.md): PASS / CONDITIONAL-PASS / FAIL-module / FAIL-check / RESTART-environment / BAR-defect / UNRESOLVED.
  - They go to `D:\ClaudeWork\rimmandrake\arbiter\verdicts.jsonl`, with `cutoff.json`.
  - They are **advisory**: they block nothing, and the interim GPT reviewer still gates closes.
  - Becoming binding [DESIGNED] needs ≥1 week, ≥30 verdicts with a MEASURED false-reject rate, and the owner's switch.
  - The pre-enable backlog (826 closes, 489 verify items) went to the Auditor, not the Arbiter.
- **Weekly** [DESIGNED in arbiter.md, UNVERIFIED as run]:
  - A doc-growth pass after the Auditor's Monday fold: merge, trim, propose a skill, ask elevation questions.
  - A regression check within 1 day of an escape.
- **Hands to.** The owning seat (FAIL tickets); the Auditor (its verdicts get sampled); the Conductor (questions).
- **Off switch.** `D:\ClaudeWork\rimmandrake\arbiter\ARBITER_OFF` (`sched:76`).
- **Day one** [LIVE]: the 11:00 run used **1,020,596 tokens against a 500000 run cap**. That raised an overbudget alarm after the fact; nothing stopped the run. On 10-28 both its slots were missed.

### 2.11 Auditor (role)

- **Purpose.** Ask "are you sure?". It samples closes and Arbiter passes, and turns repeat defect classes into enforced rules. It never closes, accepts, reopens, passes or verifies anything (auditor.md).
- **Appears** [LIVE, `sched:81`]:
  - At `runs_local` 13:00. Monday's run is mode weekly.
  - Its `pre_launch` runs `audits.py ensure`, then `audit_prescreen.py`, which writes `D:\ClaudeWork\rimmandrake\auditor\prescreen.json`.
- **Disappears.** The run ends, or hits `run_max_s` 2700 (`sched:92`). Unfinished picks carry over.
- **Runs/day.** 1.
- **Caps** [LIVE]: `run_token_cap` 700000; `daily_token_cap` 875000; `helpers_max` 2 (unused).
- **Daily order** (auditor.md):
  1. Pre-screen hard flags: each is filed as a defect ticket.
  2. Mandatory re-checks of FAIL-check and RESTART-environment verdicts. The set-aside red keeps blocking until one is SOUND.
  3. Disagreements between the Arbiter and the interim reviewer, then a sample of interim PASSes.
  4. Risk-ranked picks, with a 1-in-5 random calibration slice.
  - Before step 2, it scans the waiting index (`audits.py waiting`). A pick still waiting after 3 runs goes once to the Conductor.
- **Weekly pass (Monday)** (auditor.md):
  - Lessons → skills: every new lesson file, then the oldest, up to 40 folded. Owner 2026-10-29: *"The Auditor once a week."*
  - Pre-screen weights, codebase health, adversarial reviews.
  - Digest spot check.
  - The v3-vs-v2 quality recheck of ≥3 rows of `quality_blind.md`. That program is OFF (§2.13), so this duty has no input today.
  - Status up.
- **Outputs.**
  - `D:\ClaudeWork\rimmandrake\auditor\audits.jsonl`, append-only via `audits.py append`.
  - A ledger note per result: `audit: SOUND|DEFECT|UNRESOLVED <class> <sha>`.
  - Defect tickets, and rule specs.
  - A run note `AUDITOR RUN <unit>:` on `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE`.
- **Hands to.** The owning seat (defects); the Arbiter (escapes); a builder (rule builds); the Conductor (charter drafts, contested re-checks, questions).
- **Off switch.** `D:\ClaudeWork\rimmandrake\auditor\AUDITOR_OFF` (`sched:92`).
- **Owed programs** [DESIGNED]: `AUDITOR_BUILD_HARD_FLAG_FILER_NO_AI` and `AUDITOR_BUILD_WAITING_INDEX_REQUEUE_SCAN`.
- **Day one.** The 13:00 run had not appeared in state.json at 12:50. On 10-28 its slot was missed.
- **Stale role file.** The heading still says "NOT enabled; DISABLED until the Sunday wave".

### 2.12 Innovator (role)

- **Purpose.** Ask "what could we be doing much better?" (owner, 2026-10-26). It proposes process changes, agent changes and game concepts.
- **Appears** [LIVE, `sched:128`]: at `runs_local` "Tue,Fri 15:00" (mode run) and "Sun 15:00" (mode weekly, `weekly_plan_weekday` Sun).
- **Disappears.** The run ends, or hits `run_max_s` 2700 (`sched:136`).
- **Runs/day.** 0 or 1, about 3 a week.
- **Caps** [LIVE]: `run_token_cap` 500000; `daily_token_cap` 625000; `helpers_max` 2 (unused: no helpers until the shared cap item closes, innovator.md lines 83-87).
- **Authority** [LIVE as a role-file rule, innovator.md lines 41-69]:
  - It is on **probation, ask first**. Every change it wants is a PROPOSAL, and nothing is applied, trialled or filed as work until the owner says yes.
  - Proposals go to the Conductor, which brings them to him. His answer is recorded with `--owner-said`.
  - Probation ends after ≥3 accepted innovations reach `adopted` and no `revert-failed` or guard-breach revert in 30 days.
  - New game concepts, mods, and mod merges or splits are always his.
- **Trials** [DESIGNED]: no trial starts until `INNOVATOR_BUILD_EXPIRY_WATCHDOG_REVERTS` is closed and its program runs (innovator.md lines 99-111). Today it therefore starts no trial at all.
- **Hands to.** The Conductor, then the owner (proposals). The weekly Sunday "letter" lands before the Producer's Wednesday plan.
- **Off switch.** `D:\ClaudeWork\rimmandrake\innovator\INNOVATOR_OFF` (`sched:136`).
- **Day one** [LIVE, per v3_health_2026-10-29.md]:
  - One run (04:23Z) after two holds, both "band RED runs none". It used 262k of 500k.
  - It made one proposal, `FINDINGS_REDESIGN_BORN_AS_ITEMS_NO_LOBBY`. The owner superseded it with `FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X`.
- **Stale role file.** The heading still says "NOT enabled".

### 2.13 Measurement programs: ops_watch, account_pick, v3_vs_v2

**ops_watch** [LIVE]:
- **Program.** `src/RimMandrake/Utils/ops_watch.py`, 1608 lines. Timer `rm-ops-watch.timer` at `*:07/15` (every 15 min from minute 7), with Timeout 420 s. It is also registered in the schedule (`sched:38`, `every_s` 900).
- **Families it gathers** (header, lines 1-40): accounts, codex, steve, testing, disk, timers, flow, process, tps, production, v3, tokentalk, evidence.
- **Point format.** Every point is `{v, m: MEASURED|ESTIMATE|UNMEASURED}`. An instrument that errors writes UNMEASURED, never 0.
- **Files.** Series go to `D:\ClaudeWork\rimmandrake\ops_watch\series\<family>.jsonl`. Outputs are `status.json`, which every role launch gates on, plus `digest.json`, `digest.md` and `digest_blind.md` (an allow-list for the token-blind roles).
- **Flag rules** (`src/RimMandrake/Utils/ops_watch_rules.json`):
  - band: 7-day baseline, k_sigma 3.0, min_points 20.
  - run: n 8 same-direction changes.
  - silent: default 2 h; accounts 3 h, production 3 h, process/testing/tokentalk 6 h.
- **Alarms.** A `targets` row with `alarm: true` files ONE rimflow item when its condition is new.
  - It is filed as RUNNER from the dispatch clone, `--for BENCH --needs offline`, under parent `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE`.
  - It re-arms after `clear_passes` 4, with `lock_wait_s` 90.
  - Account and runway alarms (TOKEN_FAMILIES) are Operations' and are never filed as items.
  - The 16 targets are in §5.

**account_pick** [LIVE, `src/RimMandrake/rimflow/account_pick.py`, `sched:141-144`]:
- It returns KEEP / SWITCH / HOLD / UNMEASURED. It never switches an account itself; a switch is `claude-account use`, the owner's or a seat's call.
- With `act: "recommend"` and `hold: []` it blocks nothing. The owner's card of 2026-10-28 19:00 said to stay on the current account; the hold list `[role_launch, ring, recover]` is to be restored "when he is back" (`_hold_override`, `sched:141`).
- Day one: KEEP at 19:30Z. Open alarm kinds `account:switch:*` and `account:unmeasured`.

**v3_vs_v2** [OFF]:
- `sched:42` has `enabled: false`, `every_s` 604800, `at_local` "Mon 07:05", unit `rm-v3-vs-v2.timer`. That unit does **not exist** (systemctl: not-found).
- The health check of 2026-10-29 quotes this program's output for the week ending 2026-10-26, labelled `NOT_V3`. It was therefore run by hand at least once. UNVERIFIED: by whom and when.
- The Auditor's Monday quality recheck and Operations' cost verdict depend on its outputs.

### 2.14 helper_budget and the spawn hook

- [LIVE, `sched:14` `helper_budget.enabled: true`; `src/RimMandrake/rimflow/helper_budget.py` header]: every Dispatcher tick publishes `dispatcher\helper_budget.json` for two seats.
  - **FOUNDRY.** The machine's whole helper budget (the pace fit from `slot_allocator`, rules in `src/RimMandrake/Utils/slot_rules.json`), less any payback owed.
  - **CONDUCTOR.** Helpers only while the owner is in its window. Every Conductor helper-hour is owed and is paid back from FOUNDRY after he leaves.
- The spawn hook `.claude/hooks/block_agent_over_slots.py` reads that file first. If the file is older than MAX_AGE_S or older than the owner's last word (`slot_override.json`), the hook computes for itself.
- Role runs count as the seat they run as (`AGENT_SEAT`).
- UNVERIFIED: the MAX_AGE_S value, and the numeric budgets published today. I did not read `helper_budget.json` or `slot_rules.json` for this document.
- Relation to the role files' "2 helpers across all roles": a separate rule. `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` is still open, so no reservation mechanism exists, and headless roles run no helpers.

### 2.15 testq and the SteveDesktop lane (programs, no AI)

SteveDesktop is a second Windows machine. It runs RimWorld test jobs over SSH. The queue and dispatcher run on this machine.

- **testq-tick** [LIVE, `systemctl --user cat testq-tick.service`]:
  - Every 60 s after the last run (OnUnitInactiveSec 60 s, Timeout 900).
  - It first pulls `/home/mandrake/rm/dispatch`, then runs `testq.py tick`, then `fill` for each of `${TESTQ_FILL_MODS:-FlowWorks}`, then `steward`, then `ingest.py`.
- **One tick** (`src/RimMandrake/Utils/testq/testq.py` lines 40-75):
  - **SSH probe.** While SteveDesktop is unreachable, nothing is sent and it is re-probed every `TESTQ_PROBE_S` 300 s.
  - **Reconcile running jobs.** One automatic retry on INTERRUPTED/CRASH/INVALID/GAME_DIED. INVALID/CANARY or REFUSED/SYNC **pauses the lane** (`paused.json`) and files a finding.
  - **Drain the worker's outbox.**
  - **Admit one job** when the lane is idle: priority first, then the current "train" (same profile), then oldest.
  - **Archmagi backfill** (a local second lane) is [OFF]. It needs `TESTQ_ARCHMAGI=1` in the tick environment, and the service sets no such variable. The health check reports 4.39 archmagi test hours in 7 days, so it ran at some point. UNVERIFIED: when, and under what setting.
- **Filler** [LIVE, testq.py header lines 14-19, line 1016, line 1430]. "Steve never idles, no LLM."
  - If nothing is pending or running, it queues N = `TESTQ_FILL_CHAINS` 4 chains whose last real run is oldest, at prio 20, requested_by `BENCH.filler`.
  - It skips DRY chains (the last 2 runs all UNMEASURED) and retries them after 3 days.
  - Brakes:
    - `QHOME/fill.stop`;
    - `TESTQ_FILL_HOURS` 8 h of lane time per local day;
    - `TESTQ_FILL_CAP` 200 jobs;
    - a paused lane;
    - two non-DONE fillers in a row.
- **Nightly sweep** [LIVE]: `testq-sweep` at 01:30 queues one full sweep of each of `${TESTQ_SWEEP_MODS:-FlowWorks}`.
- **Steward** (`steward.py`, 640 lines) [LIVE]: one pass every 60 s inside the tick, plus `testq-steward-watch.timer` every 60 s as a heartbeat watcher.
  - **States**, first match wins: UNREACHABLE, QUARANTINE, RUNNING, PAUSED, READY, BRAKED, IDLE_EMPTY, EXHAUSTED, TICK_STOPPED, STALE_HEARTBEAT.
  - **Fault states** advance an "unowned clock".
    - **Only RUNNING ends an incident.**
    - EXHAUSTED and the daily lane-time brake are not faults.
  - **Escalation**, each once per incident:
    - T+10 min: spawn `STEVE_LANE_UNSTICK_<STATE>_UNOWNED_<hex4>` for BENCH.
    - T+30 min: `rimflow raise` it.
    - T+120 min with no claim: spawn for OWNER.
  - A claim with a live lease pauses the clock.
- **ops_watch Steve alarms** (`ops_watch_rules.json` targets):
  - `steve.unowned_stall_min` >30.
  - `steve.incident_unclaimed_min` >10 (owner 2026-10-28 15:50 PDT: "Keep SteveDesktop ...").
  - `steve.invalid_streak` ≥3.
  - These spawn `OPS_STEVE_*` items. Operations takes them as alarm runs.
- **Usefulness measure** [LIVE, flag only]: `testing.nothing_h_7d` counts test hours on runs that caught nothing (no FAIL, no finding, no close within `close_after_h` 24). Its target >18 is `alarm: false`, a flag only.
- **Day one:**
  - steward.json at 19:53Z: state RUNNING, job `J20261029T181522Z-8afa44`, no fault. `testq/done` holds 409 job files.
  - Health check: 109 jobs finished in 24 h, 10 of them INVALID. Test hours catching nothing: 37.05 h/7 d (ESTIMATE).
  - 128 UNTRIAGED findings, all seat RUNNER. `FLOWWORKS_QUARRY_DIGGING_1` shows 26 fail and 0 pass verifies while the item reads `validated`.
- **Results to the ledger.** `ingest.py` writes RUNNER ledger events: verify partial/pass/fail and findings. Since the cutover there were 308 events: 227 verify (181 partial, 30 pass, 16 fail) and 19 findings (health check).
- **Who consumes findings.** UNVERIFIED as a running mechanism. `FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X` (a program that folds findings into items) is the owner-chosen design and is not built [DESIGNED].
- **Off switches.** `fill.stop`, `testq.py pause`, `quarantine.json`, or stopping `testq-tick.timer`.

### 2.16 Bridge lock and companion grant

- **Bridge lock** [LIVE as a rimflow verb]: `rimflow bridge take/release/who` serializes driving of the live game (the RimBridge server). The Archmagi lane honours it.
- **Companion test grant** [LIVE, manual]: `companion_profile.json` holds a test grant with an expiry.
  - It lapsed at 03:00Z on 10-28/29 and 5 FOUNDRY tickets bounced (Conductor night audit). It was renewed by hand.
  - The item that would automate it, `COMPANION_GRANT_WIRE_LAPSES_AT_BEDTIME`, is `proposed` [DESIGNED].
  - UNVERIFIED: the grant file's path and current expiry. I did not open it.
- **Owner idle gate** [LIVE]: tickets needing the game, the bridge or a deploy are rung only when `idle_probe` MEASURES the owner idle ≥1200 s (`sched:12`).

### 2.17 Interim GPT reviewer

- **Purpose.** Today's binding gate on closes; the Arbiter is advisory (arbiter.md, auditor.md step 3).
- UNVERIFIED: the mechanism that invokes it (hook, seat ritual or program), its schedule and its caps. I did not trace these for this document.

### 2.18 Other systemd user timers (no AI)

Listed in full in §3. None decides work; they measure, mirror, publish or clean.

| timer | what it does |
|---|---|
| rm-pulse-* | the owner's phone brief and digest |
| rm-mirror | mirrors to `D:\Luke\dev\RimMandrake`, from the foundry clone |
| rm-deadman, timer-guard | watch other timers |
| rm-scratch-reap | deletes aged scratch (`--apply`) |
| rm-selftests-nightly | runs the selftests nightly |
| rm-codebase-health | read by the Auditor's Monday pass |

The account timers `account-plan` and `claude-account-warm` are [OFF] (disabled).

---

## 3. Master 24-hour timeline (local time, PDT)

**Continuous background, every ≤15 min, all day** [LIVE, `systemctl --user list-timers`]:

| interval | timers |
|---|---|
| every 1 min | rm-memwatch, rm-telemetry-export, testq-tick (60 s after the last run), testq-steward-watch |
| every 2 min | rm-dispatcher (120 s after the last run), claude-account-capture, rm-pulse-health, rm-telemetry-health |
| every 5 min | rm-mirror (5 min after the last run) |
| every 10 min | rm-pulse-update; rm-deadman (`*:03/10`); timer-guard (`*:08/10`) |
| every 15 min | rm-ops-watch (`*:07/15`), rm-account-usage, rm-codebase-health, rm-pulse-streams (`*:0/15`) |
| every 30 min | rm-arteval-autojudge, rm-artpipe-idle-fill |
| hourly | rm-objstore; rm-scratch-reap (random delay up to 300 s) |

Also continuous: FOUNDRY wakes on doorbell rings, at most 12 an hour and 96 a day, and the SteveDesktop lane runs one job at a time.

**Fixed-time events:**

| time | actor | event | tag |
|---|---|---|---|
| 01:30 | testq-sweep | queue the nightly full sweep of FlowWorks | [LIVE] |
| 03:00 | rm-selftests-nightly | nightly selftests | [LIVE] |
| 04:20 | claude-account-warm | (disabled) | [OFF] |
| 05:45 | rm-pulse-brief | the owner's morning brief | [LIVE] |
| 06:00 | rm-pulse-digest | digest | [LIVE] |
| 07:05 Mon | v3_vs_v2 | weekly v3-vs-v2 scoring (timer does not exist) | [OFF] |
| 07:30 | Operations | economy run (`sched:98`) | [LIVE] |
| 08:00 | Conductor | quick check, after Operations (`sched:50,60`) | [LIVE] |
| 09:00 | Producer | daily list; Wednesday is the weekly plan (`sched:112`) | [LIVE] |
| 11:00 | Arbiter | batch, only if pending work (`sched:66`) | [LIVE] |
| 13:00 | Auditor | daily audit; Monday adds the weekly pass (`sched:81`) | [LIVE] |
| 15:00 Tue, Fri | Innovator | run mode (`sched:128`) | [LIVE] |
| 15:00 Sun | Innovator | weekly mode: game review, letter | [LIVE] |
| 17:00 | Arbiter | second batch, only if pending work | [LIVE] |
| 17:15 | rm-pulse-brief | evening brief | [LIVE] |
| 17:30 | rm-pulse-digest | digest | [LIVE] |
| 19:30 | Operations | evening run | [LIVE] |
| 20:00 | Conductor | quick check | [LIVE] |
| any time | Operations | alarm runs, ≤2 a day, ≥3600 s apart, ≤1 per alarm per day | [LIVE] |
| any time | Producer | event run on plan_step_failure or replan_request, ≤1 a day | [LIVE] |
| any time | any role | run-now by `--by/--why`, valid for 3600 s | [LIVE] |

**Window and day rules:**
- Each clock slot may start up to `slot_late_s` 3600 s late. Outside that window it is "missed" and not run that day.
- The Conductor's headless runs are held while the owner's "AGENT CONDUCTOR" window is live.
- UNVERIFIED: whether "local day" for slots and caps is computed in PDT. I read this from the role_launch header ("once per local day") but did not trace the timezone call.

**Day one (10-28 15:00 PDT cutover to 10-29 about 13:00), from the health check and state.json:**
- On 10-28 every role slot was missed: the Arbiter 11:00/17:00, the Auditor 13:00, the Conductor 08:00/20:00, Operations 07:30, the Producer 09:00. Most of these fell before the cutover (22:00Z).
- 9 of the first 11 role runs were run-now trials, not clock runs.
- On 10-29 these ran on their clock: Operations 07:30, Conductor 08:00, Producer 09:00 (plus one event run) and Arbiter 11:00.
- The Dispatcher honoured a PAUSE file from 02:49 to 04:06Z (the owner's "wind down"; 29 skipped ticks).

---

## 4. Handoff matrix

| from → to | what | medium | if the receiver is absent |
|---|---|---|---|
| Dispatcher → FOUNDRY | "work is waiting" | doorbell `inbox/FOUNDRY.json` | Not consumed in 300 s: withdraw and retry, up to 3 attempts. Then an `undelivered` alarm and 3600 s cooldown. Doorbell not armed: no ring at all. [LIVE] |
| Dispatcher → BENCH | nothing | none (`wake: false`) | n/a [LIVE] |
| Dispatcher → roles | a run | `systemd-run` transient unit | n/a: the unit is created per run [LIVE] |
| Dispatcher → ledger | alarms | notes on `RIMFLOW_V3_BUILD_DISPATCHER_FIRST` and `OPERATIONS_MONITOR_ACCOUNTS_OFF_SHARED_TABLE`, then `./publish` | Read at the next Conductor or Operations run. Repeats are suppressed for 6 h. On day one, 18 publish errors ("Please commit or stash") were seen. [LIVE] |
| ops_watch → every role launch | measured state | `ops_watch/status.json` | Stale >2700 s, missing or UNMEASURED: every role launch is refused. [LIVE] |
| ops_watch → BENCH (ledger) | alarm items (disk, timers, Steve, evidence) | `rimflow` item filed as RUNNER, `--for BENCH --needs offline` | The item waits in the BENCH queue. `OPS_*` items also trigger Operations alarm runs. [LIVE] |
| ops_watch → Operations | account and runway alarms | `alarms.json` (never filed as items) | Read at the next Operations run. [LIVE] |
| ops_watch → token-blind roles | allow-listed health | `digest_blind.md` | n/a [LIVE] |
| Operations → owner | proposals | `ops_watch\owner\OP-<ts>.md`, relayed by the Conductor (OPS PROPOSAL / OPS DECISION) | Waits for the next Conductor check or BENCH session. UNVERIFIED: any timeout. [LIVE] |
| Operations → Producer | replan request | `REPLAN REQUEST RR-<ts>` note | Triggers a Producer event run (≤1 a day). Otherwise read at the 09:00 run. [LIVE] |
| Producer → FOUNDRY | ordered work | ledger raises and queue order | FOUNDRY picks it up when rung. [LIVE] |
| Producer → owner | cut list | CUT LIST -r<N>, relayed by the Conductor; owner CUT DECISION; Producer CUT APPLIED | Waits. [LIVE as a role-file rule] |
| Producer → Conductor | TESTQ mod choice | note | The Conductor applies it (env `TESTQ_FILL_MODS` / `TESTQ_SWEEP_MODS`). UNVERIFIED: how it is applied. |
| FOUNDRY → interim reviewer and Arbiter | close with sha and evidence | `rimflow close` | The interim reviewer gates (mechanism UNVERIFIED). The Arbiter judges at 11:00/17:00 if pending work exists. [LIVE / UNVERIFIED] |
| Arbiter → Auditor | verdicts | `arbiter\verdicts.jsonl` | Read at 13:00. On day one the trial wrote `arbiter\trial\verdicts.jsonl` instead, so the Auditor could not compare (health check). [LIVE] |
| Arbiter → owning seat | FAIL | ticket | Waits in the queue. [LIVE] |
| Auditor → owning seat | DEFECT | ticket via `rimflow file/spawn` | Waits in the queue. Day one: `AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH` was reassigned to FOUNDRY with no work event seen (health check). [LIVE] |
| Auditor → Arbiter | escapes | ticket | Read at the next Arbiter run. [LIVE] |
| Auditor → Conductor | waiting picks after 3 runs; charter drafts; questions | ledger note | Next Conductor run. [LIVE as a rule] |
| Innovator → Conductor → owner | proposals | ledger, then the Conductor card | Nothing happens until he answers. [LIVE as a rule] |
| testq → ledger | test results and findings | `ingest.py` RUNNER events | Findings pile up UNTRIAGED: 128 on day one. No running consumer (UNVERIFIED). [LIVE] |
| steward → BENCH → owner | Steve lane fault | `STEVE_LANE_UNSTICK_*` item at T+10; raise at T+30; owner item at T+120 | BENCH absent: it escalates to the owner at 120 min. [LIVE] |
| seat_restart → FOUNDRY | kill and relaunch | SIGTERM/SIGKILL, then `seat_loop.sh` | Cancelled by any human input. The live kill path is unexercised. [LIVE] |
| Conductor → owner | everything above, batched | question cards, `conductor\log.md`, BENCH session | Held until he is present. [LIVE] |
| owner → system | rulings | `--owner-said` notes, schedule edits, OFF files, PAUSE, `slot_override.json` | n/a |

---

## 5. Arbitrary parameters

"Who may change" is taken from the doc and role files. Where a file does not say, it is UNVERIFIED and the de facto rule is anyone with commit rights.

| parameter | value | where set | who may change | why (if recorded) |
|---|---|---|---|---|
| tick_s | 120 | sched:4 | UNVERIFIED | Dispatcher cadence |
| timer OnUnitInactiveSec / OnBootSec / TimeoutStartSec | 120 s / 3 min / 600 s | rm-dispatcher.timer/.service | UNVERIFIED | |
| tick_budget_s | 420 | dispatcher | UNVERIFIED | |
| stall_after_s | 240 | sched:5 | UNVERIFIED | idle before a ring |
| verify_s | 300 | sched:6 | UNVERIFIED | ring must be consumed in |
| handoff_s | 600 | sched:7 | UNVERIFIED | claim must follow the ring in |
| max_retries | 2 | sched:8 | UNVERIFIED | |
| cooldown_s | 3600 | sched:9 | UNVERIFIED | |
| dead_after_s | 600 | sched:10 | UNVERIFIED | |
| recover_verify_s | 300 | sched:11 | UNVERIFIED | unused (recovery off) |
| owner_idle_s | 1200 | sched:12 | UNVERIFIED | game/bridge tickets wait for an idle owner |
| alarm_every_s | 21600 | sched:13 | UNVERIFIED | |
| HOLD_ALARM_EVERY_S | 21600 | disp:573 | code | |
| ops_stale_s / OPS_STALE_S | 2700 | sched:3, rl:116-165 | UNVERIFIED | |
| FUTURE_TOL_S | 300 | rl:116-165 | code | |
| EVENT_LOOKBACK_S | 21600 | rl header | code | |
| RUN_NOW_TTL_S | 3600 | rl:116-165 | code | |
| SCOPE_GRACE_S / SCOPE_STOP_S | 600 / 30 | rl:116-165 | code | |
| wakes_per_seat_hour / _seat_day / _per_day | 12 / 96 / 120 | sched:20 | BENCH changed them 10-29 | `FOUNDRY_IDLE_DIAGNOSE_CAP_STARVES_TRIAGE`; were 6/48/80 |
| recovers_per_seat_day | 3 | sched:20 | UNVERIFIED | unused |
| code cap defaults | 3/30/80/3 | disp:99 | code | |
| RM_DOORBELL_MAX_WAIT_S / POLL_S | 23 h / 3 s | doorbell hook | env | |
| backstop_ctx_tokens / backstop_idle_s / grace_s (FOUNDRY) | 110000 / 1800 / 30 | sched:35 | UNVERIFIED | |
| seat_restart defaults | see §2.4 table | seat_restart.py DEFAULTS | code | |
| lease length | 45 min, renewed | lease.py | code | UNVERIFIED: exact constant line |
| slot_late_s | 3600 (every role) | sched:59,76,92,108,123,136 | owner (schedule) | |
| run_max_s | Conductor 1800, Arbiter 2700, Auditor 2700, Operations 1800, Producer 1800, Innovator 2700 | same lines | owner | the only hard stop |
| Conductor quick_token_cap / daily | 450000 / 1350000 | sched:50 | owner | |
| Conductor session_week_pct_cap | 6 | sched:51 | owner | |
| Conductor session_helpers_max | 3, every band | sched:52-55 | owner | role file says 2 across roles |
| Arbiter run / daily cap | 500000 / 1250000 | sched:66 | owner | |
| Arbiter pre_launch budget / tiers cap / pre_launch_max_s | 900 s / 6 / 1200 s | Arbiter entry | UNVERIFIED | |
| Auditor run / daily cap | 700000 / 875000 | sched:81 | owner | `_caps_why` quotes older numbers |
| Operations run / economy / daily cap | 450000 / 550000 / 1650000 | sched:99 | owner | |
| Operations alarm_run_gap_s / per alarm per day / per day | 3600 / 1 / 2 | sched:108 | owner | |
| Producer run / daily cap | 800000 / 2000000 | sched:112 | owner | commit de4815dbaa "owner: less caution" |
| Producer event_runs_per_day | 1 | sched:113 | owner | |
| Innovator run / daily cap | 500000 / 625000 | sched:128 | owner | |
| helpers_max (Arbiter, Auditor, Innovator) | 2 | role entries | owner | unused until the shared cap is built |
| owner helper limit | 2 across all roles | role files | owner | review roles r2 #4 |
| throttle bands GREEN/AMBER/RED/FLOOR | runway ≥1.5 / ≥1.0 / ≥0 / week_left <10 %; every band "all" with ×1.0 | sched:52-55 and per role | owner | neutralized 10-28, commit d92c4c825e |
| account_pick switch_when / target_min | runway <0.8 or week_left <10 / runway ≥1.2, week_left ≥20, MEASURED | sched:141-144 | owner | |
| account_pick lent_min_draw_pct / rank / act / hold | 10 / soonest_reset / recommend / [] | sched:141-144 | owner | owner card 10-28 19:00 |
| ops_watch every_s | 900 | sched:38, timer `*:07/15` | UNVERIFIED | |
| ops_watch band k_sigma / baseline / min_points | 3.0 / 7 d / 20 | ops_watch_rules.json `band` | UNVERIFIED | |
| ops_watch run n | 8 | ops_watch_rules.json `run` | UNVERIFIED | |
| ops_watch silent windows | 2 h default; accounts/production 3 h; process/testing/tokentalk 6 h | ops_watch_rules.json `silent` | UNVERIFIED | |
| alarm clear_passes / lock_wait_s | 4 / 90 | ops_watch_rules.json `alarm` | UNVERIFIED | |
| target: runway (accounts, codex) | <1.0 alarm | targets | owner brief 10-26 | |
| target: steve.unowned_stall_min | >30 alarm | targets | owner brief | |
| target: steve.incident_unclaimed_min | >10 alarm | targets | owner 10-28 15:50 | |
| target: steve.invalid_streak | ≥3 alarm | targets | owner brief | |
| target: disk root / C: / D: free GB | <210 / <200 / <200 alarm; root <420 flag | targets | UNVERIFIED | scratch grew 207 GB in one day |
| target: timers.failed_units / evidence.tamper | >0 alarm | targets | UNVERIFIED | |
| target: testing.nothing_h_7d | >18 flag only | targets | v3 §6 | |
| target: process.share_7d | ≥61 flag only | targets | v3 §6 | |
| target: tokentalk share | ≥10 flag only | targets | owner 10-27 | |
| target: flow.untriaged_findings | >0 flag only | targets | UNVERIFIED | |
| testq tick / probe | 60 s / 300 s | testq-tick.timer, TESTQ_PROBE_S | env | |
| testq fill chains / hours / cap | 4 / 8 h a day / 200 | TESTQ_FILL_CHAINS, TESTQ_FILL_HOURS (testq.py:1016), TESTQ_FILL_CAP | env | |
| testq DRY rule | 2 UNMEASURED runs; retry after 3 days | testq.py header | code | |
| steward escalation | 10 / 30 / 120 min; manual pause fault at 60 min; READY fault at 5 min; heartbeat stale 5 min | steward.py header | code | |
| Archmagi silent / backoff | 600 s / 1800 s | testq.py header | env | lane OFF |
| testq sweep | 01:30, FlowWorks | testq-sweep.timer | env | |
| memory | claude-seats.slice 24G (10G per seat); rm-harness.slice 12G | systemd slices | UNVERIFIED | |
| Innovator probation exit | ≥3 adopted; no revert-failed in 30 d | innovator.md | owner | |
| Arbiter binding threshold | ≥1 week, ≥30 verdicts, MEASURED false-reject rate, owner switch | arbiter.md | owner | |
| Auditor lessons fold | all new, then oldest, to 40 a pass; inbox ≤14 days | auditor.md | owner | |
| Auditor random slice | 1 in 5 | auditor.md | Auditor (retune ticket) | |
| v3 success targets | keep-going ≤26/day; nothing-tests ≤18 h/wk; failure-signal ≤25 %; process share <61 % | v3design lines 128-131 | owner | |
| v3 vs v2 SUPERIOR | ≥4 of 7 primaries BETTER, 3 of 4 settled weeks | v3design | owner | |

---

## 6. Life of a work item, from finding to accepted

1. **Born.** It starts as one of these:
   - a finding;
   - a RUNNER finding from testq `ingest.py`;
   - an ops_watch alarm item (RUNNER, for BENCH);
   - a steward `STEVE_LANE_UNSTICK_*` item;
   - an Auditor DEFECT ticket;
   - an Arbiter FAIL ticket;
   - a Producer-raised goal ticket;
   - a seat or owner `rimflow file`.

   The name must pass `rimflow namecheck`. RUNNER findings land as UNTRIAGED; 128 were untriaged on day one. No program turns them into items yet (`FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X` is [DESIGNED]). [LIVE]
2. **Ordered.** The Producer's 09:00 daily list, or Wednesday's plan, raises it in the queue. Before a raise it writes a `## verify` bar on the item. [LIVE as a role-file rule]
3. **Delivered.**
   - The Dispatcher peeks the queue. If FOUNDRY has been idle ≥240 s with its doorbell armed, and the caps, owner-idle gate (game, bridge, deploy tickets) and account gate pass, it rings. [LIVE]
   - BENCH work is not rung. It waits for the owner's session.
4. **Claimed.** FOUNDRY claims and starts the item, taking a 45-min lease that it renews while working. That is the handoff the Dispatcher looks for within 600 s. [LIVE]
5. **Worked.**
   - Live game work takes the bridge lock and needs the companion grant.
   - Test jobs go to testq (`testq.py submit`) and run on SteveDesktop. Results return as RUNNER verify events.
6. **Closed.** `rimflow close --sha <sha>` with evidence. [LIVE]
7. **Judged.**
   - The interim GPT reviewer gates the close (mechanism UNVERIFIED).
   - The Arbiter gives an advisory verdict at its next batch, written to `verdicts.jsonl`.
   - A FAIL-check or RESTART-environment verdict waits for an Auditor SOUND before its set-aside red stops blocking. [LIVE as a rule]
8. **Sampled.** The Auditor's pre-screen checks every close since its last run. Hard flags become defect tickets; risk-ranked and random picks are re-checked. A DEFECT reopens the cycle as a new ticket, since the Auditor never reopens an item itself. [LIVE]
9. **Accepted.** UNVERIFIED as a defined event. The health check says no ledger event marks "pass on named scenarios, specific build, non-maker check", so accepted items/day is UNMEASURED.
   - The item states seen are `proposed`, `validated`, `implemented` and `superseded`.
   - UNVERIFIED: the full state list and which state counts as accepted.
10. **Off-ramps.**
    - `rimflow drop` or `supersede`.
    - A lease that lapses returns the item to the queue (`flow.lapsed_leases` is measured).
    - A woke-no-handoff ring puts the seat in a 3600 s cooldown.

---

## 7. Owner interface

**What reaches him** [LIVE unless tagged]:
- **Conductor relays**, batched on question cards in the BENCH session or at quick checks:
  - OPS PROPOSAL / OPS DECISION (from Operations);
  - CUT LIST / CUT DECISION (from the Producer);
  - Innovator proposals;
  - Auditor questions and charter drafts;
  - Arbiter questions.
- **Phone brief and digest**: rm-pulse-brief at 05:45 and 17:15; rm-pulse-digest at 06:00 and 17:30. A raised `STEVE_LANE_UNSTICK_*` item appears as a brief line (steward T+30).
- **Owner items**: a steward escalation at T+120 min with no claim (titled "IN PERSON:" when SteveDesktop is unreachable).
- **Operations proposals**: `ops_watch\owner\OP-<ts>.md` (owner-only).
- **Conductor log**: `D:\ClaudeWork\rimmandrake\conductor\log.md` (3-5 lines a run).
- **Standing rule**: nothing reaches the owner unread.

**What he controls:**
- `enabled` flags.
- Role OFF files (anyone may create one).
- Dispatcher `PAUSE`.
- Schedule caps and bands.
- account_pick `hold`.
- `slot_override.json` (helper word).
- Rulings recorded `--owner-said` / `--by-card`.
- The Arbiter binding switch.
- Innovator probation.
- Cut decisions.

**What waits for him:**
- An account switch (`claude-account use` is his or a seat's call).
- The v3_vs_v2 timer (OFF).
- Restoring account_pick `hold`.
- Arbiter binding.
- Innovator trials (also blocked on the watchdog build).
- Game, bridge and deploy tickets while he is not MEASURED idle for 20 min.

**Touch volume target** (v3design §6): keep-going messages from 31 a day to ≤26 a day. UNMEASURED: there is no instrument.

---

## 8. Known gaps and day-one evidence

These are statements of fact, with no judgement. Sources: this document's reads; `/mnt/d/ClaudeWork/rimmandrake/conductor/v3_health_2026-10-29.md` (cited as HC); `/mnt/d/ClaudeWork/rimmandrake/conductor/foundry_night_audit_2026-10-29.md` (cited as NA).

**Config and docs that disagree:**
1. All six role files still head themselves "NOT enabled", while the schedule has every role `enabled: true` (`sched:48-136`).
2. The schedule's top-level `_doc` says every role stays `enabled: false` until the owner switches it on. All are true, by the 10-28 "v3 trial night" commit 4d9171a1e5.
3. Throttle bands are neutralized (all "slots: all", ×1.0). Yet the Conductor `_why` (AMBER/RED: 20:00 check only) and the operations.md band table (AMBER: no 07:30; RED ×0.75) still describe active bands.
4. The `_caps_why` texts for the Producer and Auditor quote older cap numbers than the live caps.
5. The Conductor's `session_helpers_max` is 3, while every role file states the owner's limit of 2 across all roles. `helpers_max` 2 on three roles is unused, because `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` is open.

**Built but off or missing:**

6. v3_vs_v2 is `enabled: false`, and its timer `rm-v3-vs-v2.timer` does not exist. HC: the only scored week precedes the cutover (`NOT_V3`). The counterfactual backtest failed on coverage (0.429 of 14 cells, needs 0.75). Four settled weeks put the earliest verdict around 2026-11-23.
7. `recover_dead` is false on both seats. A dead seat raises an alarm only.
8. account_pick `hold` is `[]`, so SWITCH and HOLD verdicts block nothing.
9. The Archmagi test lane needs `TESTQ_ARCHMAGI=1`, which the tick service does not set.
10. The account timers `account-plan` and `claude-account-warm` are disabled.

**Designed, not built:**

11. The Conductor goodbye restart.
12. `INNOVATOR_BUILD_EXPIRY_WATCHDOG_REVERTS`. No Innovator trial can start without it.
13. `AUDITOR_BUILD_HARD_FLAG_FILER_NO_AI` and `AUDITOR_BUILD_WAITING_INDEX_REQUEUE_SCAN`.
14. `FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X`. No running consumer turns RUNNER findings into items.
15. `COMPANION_GRANT_WIRE_LAPSES_AT_BEDTIME` (status proposed).
16. The `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` reservation pool.
17. Producer cadence beyond Wednesdays (`PRODUCER_CADENCE_DESIGN_MORE_THAN_WEDNESDAYS`): the owner's card answers were recorded, but the schedule is unchanged.

**Caps that are alarms, not stops:**

18. Token caps are not enforced during a run; only `run_max_s` stops one. Day-one overruns:
    - Arbiter 11:00: 1,020,596 tokens against a 500000 run cap (state.json).
    - Producer 05:06Z weekly re-plan: 943k against 800k (HC).
    - Auditor trial: 537k against 375k (HC; the cap was later raised to 700000).
    - Open alarm kinds: overbudget for the Arbiter, Auditor, Operations and Producer; `role:Producer:cap`; `role:Operations:scope`.

**Measures that cannot see yet (HC §2b, §4):**

19. Keep-going messages a day, failure-signal share and accepted items a day are UNMEASURED. The v3 kill criterion therefore cannot fire.
20. Process-commit share: 72.4 % (ops_watch, 7 d, MEASURED, rising 8 readings in a row) against 61.6 % (v3_vs_v2, week ending 10-26). The two instruments are not reconciled.
21. Test hours catching nothing: 37.05 h in 7 d (Steve 32.66, archmagi 4.39), ESTIMATE, against a target of ≤18. This is a flag, not an alarm.

**The SteveDesktop lane** (relevant to the owner's example):
- The steward's only incident-ending state is RUNNING. A running job is counted as the lane being healthy whatever the job catches.
- The filler queues the oldest-run chains whenever the lane is empty, up to 8 lane-hours a day.
- The usefulness measure (`testing.nothing_h_7d`) raises a flag, not an alarm.
- Day one:
  - 109 jobs finished in 24 h, 10 of them INVALID.
  - RUNNER verifies: 227, of which 181 partial, 30 pass and 16 fail.
  - `FLOWWORKS_QUARRY_DIGGING_1` shows 26 fail and 0 pass verifies but item status `validated` (HC §3.5).

**Seats and handoffs:**

22. Dispatcher rings, day one. HC: 59 rings, 55 verified (93 %), 4 woke_no_handoff. A later 400-line journal tail: 53 rings, 49 verified, 5 woke_no_handoff. FOUNDRY is in cooldown at 12:50 with `cap:FOUNDRY` open.
23. FOUNDRY's ticket yield from 05:00 to 07:42Z: 9 REAL of 18 (2 already done, 5 bounced, 1 unclear, 1 live-proof). This is a hand classification (NA, HC §3.6, ESTIMATE). The 5 bounces trace to the companion grant lapse at 03:00Z.
24. seat_restart's live kill path is unexercised. Its one request (04:27Z) was cancelled, and a stale `dispatcher/restart/FOUNDRY.request.json` remains (HC).
25. The Dispatcher hit 18 publish errors ("Please commit or stash") and 3 push-ref errors on day one (HC).
26. The Arbiter's trial verdicts went to `arbiter/trial/verdicts.jsonl`, not `arbiter/verdicts.jsonl`, so the Auditor could not compare the Arbiter with the interim reviewer (HC §4).
27. The Auditor filed `AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH`. The owner reassigned it to FOUNDRY, and no work event followed by the time of HC.
28. Lessons inbox: 1088 files, the oldest 48 days old, 594 without a home (HC §3.2). The Auditor's Monday fold is capped at 40 a pass.
29. Untriaged findings: 128 (ops_watch MEASURED, matching HC's independent ledger scan), rising.
30. A cutover on 10-28 at 05:04 stopped every rm-* and testq-* timer, and nobody restarted them. This was the steward's TICK_STOPPED lesson (steward.py header).

**Not checked by this document (UNVERIFIED, counted below):**
- The interim GPT reviewer's mechanism.
- The helper_budget numbers and MAX_AGE_S.
- The exact `after_role` semantics.
- The local-day timezone.
- The accepted-state definition.
- The companion grant file.
- FOUNDRY's charter and owner touchpoints.
- The full-day ring count.
- Who ran v3_vs_v2 by hand.
- Archmagi run history.
- Whether PAUSE also stops role launches.
- The scope-stop trigger.
- How the TESTQ mod choice is applied.
- The owner-proposal timeout.
- The lease constant line.
- The findings consumer.

**Sources not read for this document:**
- `design/RimMandrake/rimflow_v3_responsibilities_2026-10-26.md` (Part 4 activation table).
- `conductor_briefing_2026-10-28.md`.
- `delegation_policy.md`.
- `infrastructure/agents/*.md`.
- `slot_rules.json`.
- `idle_probe.py`.
- `lease.py`.
- `v3_cutover.py`.
- The four 2026-10-29 design files (findings curation, v3 health daily check, process model v2/v3, producer cadence), beyond their item names.
