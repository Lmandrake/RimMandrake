# RimFlow v3 agent workflow, as built (2026-10-29)

Status: as-built description, written 2026-10-29 around 13:00 PDT from the bench clone (`/home/mandrake/rm/bench`)
at commit 6b7127714c, extended the same day with a second pass over the designs, charters and code listed at the end of §8. Item `V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR`, step 1 of 3. The next step is a skeptical review
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
  [LIVE, `rl` header lines 12-20] Exact rule: the role launches only after the other role's own *scheduled* run for the slot it follows has finished `done` and none is going (Conductor 08:00 follows Operations 07:30; 20:00 follows 19:30). Alarm runs and yesterday's late run never count. If the band skipped the followed slot on purpose, the previous slot within 24 h is used instead. If Operations misses its slot, the follower does not launch; by the slot rules above it is then journaled missed once its own `slot_late_s` passes (inferred from the two rules together; not observed).
- Event runs read events with a cursor, looking back `EVENT_LOOKBACK_S` = 6 h.
- An unreadable ledger means UNMEASURED, and nothing launches.

**Launch mechanics** [LIVE]:
- A transient unit `systemd-run --user rm-role-<name>-<epoch>` runs `claude_bounded.sh -p <prompt> --output-format json`. The Arbiter's runs add `--json-schema`.
- An optional `pre_launch` program runs first (in each card).
- The only hard stop is wall time, `run_max_s`. The default is 1800 s, and some roles set 2700 s.
- **Tokens are not stopped mid-run.** Caps are an admission check at launch (refused with `role:<name>:cap` when the day's spend plus the run budget would pass `daily_token_cap`) plus an alarm after the fact: a run over its `run_token_cap` raises `role:<name>:overbudget` in state.json. Only `run_max_s` stops a run.
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
- The Conductor's interactive session mode has `session_helpers_max` 3 in every band (`sched:52-55`), but no program reads it; the role file states the owner's limit of 2. Which number governs is open (§8 item 32).
- [LIVE] Code enforces a per-seat count, not the owner's cross-role 2: the spawn hook `.claude/hooks/block_agent_over_slots.py` reads `helper_budget.json` per seat (§2.14). No code enforces "2 across all roles"; that waits on `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` [DESIGNED].

**Scope stop** [LIVE, `rl:116-165`]:
- `SCOPE_GRACE_S` = 600 s and `SCOPE_STOP_S` = 30 s govern stopping a role run whose scope overran. The alarm kind `role:Operations:scope` is open.
- [LIVE, `rl:686-703`] Trigger: the role's systemd unit reads as gone ("unit ..." state) while its `claude_bounded` scope is still busy. `role:<name>:scope` is raised, the run is kept as running and re-checked next tick; after `SCOPE_GRACE_S` the scope is stopped. A unit state of UNMEASURED raises `role:<name>:unit` instead. At `run_max_s` the role is stopped and the stop re-issued every tick (`rl` header lines 77-79).

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
- **Off switch.** The `PAUSE` file (stops rings AND role launches [LIVE, `dispatcher.py:30` "stops everything"; disp:339-340 skip launches; running roles are still supervised first, disp:327; the release path re-checks PAUSE, disp:891-894, 926-927]); `systemctl --user stop rm-dispatcher.timer`; `enabled: false` per seat or role.

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
- **BENCH / the Conductor** [BUILT 2026-10-29]: kind `conductor`. The goodbye hook (`.claude/hooks/conductor_goodbye.py`) triggers the request. The fresh window is verified when it ends its first turn. The context backstop fires only after 4 h with no human message.
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
- **Decides alone** [LIVE as charter, `infrastructure/agents/FOUNDRY.md`]: everything outside `delegation_policy.md` §2 ("Decide; don't escalate taste", FOUNDRY.md:65-68), art and cosmetic calls through a judge agent logged `--why "delegated: <class>"`; first-guess tuning numbers marked PROVISIONAL (owner 2026-10-03, FOUNDRY.md:201-206); game restarts of its own (`./game --why`); acceptance of its own items including FlowWorks, L1 to GREEN-FULL (FOUNDRY.md:19-23). Never: work order, helper count, a ruling's twins (§1 calls).
- **Lanes** [LIVE, FOUNDRY.md:18]: since the v3 cutover FOUNDRY owns ALL FlowWorks and Gimme Some Slack (see §2.20).
- **Work states** [LIVE, FOUNDRY.md:8-17]: `rimflow next` reserves with a 45-minute token lease; `implemented --sha` moves the item to `built` with owed criteria tagged L0-L4; each passing `verify --criterion` moves it towards `validated`, the last one to `done`; `close --sha` is for items with nothing live owed.
- **Turn loop** [LIVE, FOUNDRY.md:145-172]: after each ticket it commits its ledger shard, files open promises and runs `seat_restart.py request --reason closed`. `CONTEXT OK` (under 110k tokens) means take `next --ringed` and continue in the same turn; `RESTART REQUESTED` means end the turn. The restart is held, never forced, while a helper is alive, it holds the bridge or driver lock, its last game event is a deploy/load/shutdown, PAUSE is on, or the owner touched the machine in the last 2 minutes. A new owner prompt within 30 s cancels it.
- **Full belt** [LIVE as charter, owner 2026-10-03, FOUNDRY.md:180-199]: one helper on the bridge whenever free, the art pipeline up, one helper building offline; "Never go idle waiting for no one" (FOUNDRY.md:194).
- **Hands to.** The Arbiter and interim reviewer (closes); the Auditor (samples).
- **Owner touchpoints** [LIVE as charter]: a §2 call goes to him only by saying it in its reply or `rimflow file --for OWNER --kind decision` (FOUNDRY.md:67-68); L4 validation belongs to the owner (FOUNDRY.md:23); his game-state words are recorded with `./game --said` (FOUNDRY.md:59); anything left for him is read first (FOUNDRY.md:69-71). A new prompt from him cancels a pending restart.
- **Off switch.** `seats.FOUNDRY.enabled` or `wake: false`.
- **Day-one state** [LIVE]: in `cooldown` with `last_verified` set; `cap:FOUNDRY` is an open alarm kind.

### 2.6 BENCH seat (the owner's interactive workshop)

- **Purpose.** The owner's own working session. It holds the "CONDUCTOR" session name.
- **Appears.** When the owner opens it. It is **never woken** by the Dispatcher (`wake: false`, `sched:24`).
- **Disappears.** When the owner closes it. There is no backstop restart for it.
- **Model.** opus (`sched:24`). FlowWorks and GSS belong to FOUNDRY since the v3 cutover (`infrastructure/state/flowworks_lane.json`); BENCH takes only their needs=owner live looks.
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
- **Bands.** Its `_why` says the bands are neutralized (§2.1), so every band runs every check (c2dfc21445).


**From `infrastructure/agents/CONDUCTOR.md`** [LIVE as charter]:
- First rule (owner, 2026-10-28, verbatim): "Conductor from now on should function as a light orchestrator focussed on communication with the human primary. Make that absolutely clear in its definition." It answers him first each turn, does no work itself (backgrounded helpers do), never blocks his window (CONDUCTOR.md:12-29).
- Quick mode (phone) builds, tests and deploys nothing, takes no bridge and runs no helper. Session mode runs helpers, "never more than two at once across all roles, never more than the allocator gives" (CONDUCTOR.md:48-56).
- Scheduled quick checks 08:00 and 20:00 run headless through `role_launch.py` **as seat BENCH** and append 3-5 lines to `D:\ClaudeWork\rimmandrake\conductor\log.md` (CONDUCTOR.md:57-60).
- Goodbye: his message `goodbye` / `bye` / `gn` / `good night` / `done for now` / `that's all` runs a light close-out (rulings to the ledger, promises filed `--for OWNER`, 3-5 log lines). It then requests `seat_restart.py request --seat BENCH --fresh`, and the Dispatcher relaunches a fresh CONDUCTOR window after a 120 s grace (`CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME`, CONDUCTOR.md §Goodbye).
- Seat models (`infrastructure/agents/Agent_Policy.md:17-35`, owner 2026-10-20): the orchestrating seat runs Opus and backgrounds design to Opus helpers; FOUNDRY runs Sonnet and escalates to Opus per item; Haiku for mechanical bulk work with a checkable outcome.
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
- **Bands.** operations.md's throttle section says the bands are neutralized (2a5ec4a7ee).

### 2.9 Producer (role)

- **Purpose.** Order the work: a daily list, a weekly plan, a replan when a plan fails, and the cut list.
- **Appears** [LIVE, `sched:112-115`]:
  - At `runs_local` 09:00 after Operations. Wednesday's run is mode weekly (`weekly_plan_weekday` "Wed").
  - Event runs on `plan_step_failure` and `replan_request` (prefix "REPLAN REQUEST"), at most 1 a day, with `plan_scope` [raised, row].
- **Disappears.** The run ends, or hits `run_max_s` 1800.
- **Runs/day.** 1 plus up to 1 event run.
- **Caps** [LIVE]: `run_token_cap` 800000; `daily_token_cap` 2000000. The daily cap was raised by commit de4815dbaa, "owner: less caution". Its `_caps_why` quotes these numbers (c2dfc21445).
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
- **Role file.** The heading says the role is enabled (4d9171a1e5; fixed in 2a5ec4a7ee).

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
- **Role file.** The heading says the role is enabled (4d9171a1e5; fixed in 2a5ec4a7ee).

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
- `sched:42` has `enabled: false`, `every_s` 604800, `at_local` "Mon 07:05", unit `rm-v3-vs-v2.timer`. The units are in `Utils/systemd/` and installed in `~/.config/systemd/user`, timer NOT enabled (aa4adea115); a manual `systemctl --user start rm-v3-vs-v2.service` on 10-29 exited 0 and rewrote `verdict.md`.
- The health check of 2026-10-29 quotes this program's output for the week ending 2026-10-26, labelled `NOT_V3`. It was therefore run by hand at least once. UNVERIFIED: by whom and when.
- The Auditor's Monday quality recheck and Operations' cost verdict depend on its outputs.

### 2.14 helper_budget and the spawn hook

- [LIVE, `sched:14` `helper_budget.enabled: true`; `src/RimMandrake/rimflow/helper_budget.py` header]: every Dispatcher tick publishes `dispatcher\helper_budget.json` for two seats.
  - **FOUNDRY.** The machine's whole helper budget (the pace fit from `slot_allocator`, rules in `src/RimMandrake/Utils/slot_rules.json`), less any payback owed.
  - **CONDUCTOR.** Helpers only while the owner is in its window. Every Conductor helper-hour is owed and is paid back from FOUNDRY after he leaves.
- The spawn hook `.claude/hooks/block_agent_over_slots.py` reads that file first. If the file is older than MAX_AGE_S or older than the owner's last word (`slot_override.json`), the hook computes for itself.
- Role runs count as the seat they run as (`AGENT_SEAT`).
- [LIVE, `helper_budget.py:32-33`] `MAX_AGE_S` = 600 s (five missed ticks); `FUTURE_SLACK_S` = 5 s.
- [LIVE, `D:\ClaudeWork\rimmandrake\dispatcher\helper_budget.json`, read 2026-10-29 12:57 PDT] mode `CRUISE+OWNER`; CONDUCTOR 6, FOUNDRY 4. Why text: account 87% left, 6.08 d to reset, pace P 1.00, no burn rate measured, CRUISE step gives 4; Codex runway 0.25 (<1.0).
- [LIVE, owner override in the same file] set 2026-10-28 21:53, BENCH 6 until 2026-11-04T14:00-08:00. Owner's words: "For this checkout, use as many subagents as you like. This is taking too long and I'm getting tired." BENCH still has an override after the v3 cutover removed the BENCH seat (§2.20).
- [LIVE, `src/RimMandrake/Utils/slot_rules.json`] seats BENCH and FOUNDRY; `split.rule` "v3"; `conductor_session_n` 3; `total_max` 10; `fallback_n` BENCH 3, FOUNDRY 1. Token modes: DARK n 0 at ≥98% used; ALMOST_OUT n 1 (enter p<0.5, leave p>0.8, hold 2 h); CRUISE n 6 with steps p 0.8→2, 1.0→3, 1.2→4; BURN n 10 (enter p>1.5 with reset <48 h; leave p<1.2 or reset <6 h); SWEEP n 3, hold 12 h. `cross_hold_h` 2, `min_mode_min` 60, `session_brake_pct_used_gt` 90. Fit: 3 h window, ≥4 points over ≥1.5 h, `msgs_per_pct` 1460. `spare.min_pct_left` 10. Lent account (`lent_accounts.steven`): we may use at most 48%, prefer the first 48 h of its week, floor 10% left, off limits through 2026-10-28T15:00-07:00. Queue paydown: enter when A1>100 or D1≥10, leave when A1<60 and D1<5. Presence: bench_min 30, afk_min 60. Overage: finish_margin_h 6, default_window_h 24, bench_floor 1. `helpers.live_window_s` 900. ops: stale_min 45, disk_brake_free_gb 210, codex_conserve_runway 1.0, steve_stall_min 30, steve_invalid_streak 3.
- Note: `conductor_session_n` 3 here, `session_helpers_max` 3 in the schedule, the live budget's CONDUCTOR 6 and the role file's "2 across all roles" are four different numbers for Conductor helpers [LIVE, each as cited].
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
- **Who consumes findings.** Nobody on a cadence [LIVE as evidence: the untriaged count rises, 128 on day one; no role file or timer names a consumer]. Part 4 gives no duty row to findings triage. `FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X` (option B of the findings curation design, §2.19) is the owner-chosen design, filed for FOUNDRY, not built [DESIGNED].
- **Mod choice** [LIVE, `~/.config/systemd/user/testq-tick.service:10`, `testq-sweep.service:9`]: the filler and sweep loop over `${TESTQ_FILL_MODS:-FlowWorks}` and `${TESTQ_SWEEP_MODS:-FlowWorks}`. Neither unit sets the variable (no `Environment=` for it, no drop-in directory, absent from the user manager's environment, checked 2026-10-29), so both run FlowWorks only.
- **Off switches.** `fill.stop`, `testq.py pause`, `quarantine.json`, or stopping `testq-tick.timer`.

### 2.16 Bridge lock and companion grant

- **Bridge lock** [LIVE as a rimflow verb]: `rimflow bridge take/release/who` serializes driving of the live game (the RimBridge server). The Archmagi lane honours it.
- **Companion test grant** [LIVE, manual]: `companion_profile.json` holds a test grant with an expiry.
  - It lapsed at 03:00Z on 10-28/29 and 5 FOUNDRY tickets bounced (Conductor night audit). It was renewed by hand.
  - The item that would automate it, `COMPANION_GRANT_WIRE_LAPSES_AT_BEDTIME`, is `proposed` [DESIGNED].
  - [LIVE, `src/RimMandrake/Utils/modcheck/runner.py:104-110`] modcheck refuses to start a suite when the companion is not in its TEST profile or the grant lapses within `PROFILE_MIN_MINUTES` = 45.
  - UNVERIFIED: the grant file's path and current expiry. I did not find or open the live file.
- **Owner idle gate** [LIVE]: tickets needing the game, the bridge or a deploy are rung only when `idle_probe` MEASURES the owner idle ≥1200 s (`sched:12`).

### 2.17 Interim GPT reviewer

- **Purpose.** Today's binding gate on closes; the Arbiter is advisory (arbiter.md, auditor.md step 3).
- **Mechanism** [DESIGNED, responsibilities Part 4 rules and rows A-1, A-3, AU-2; LIVE as a rule in `roles/arbiter.md:167` and `roles/auditor.md:97`]: an outside non-maker read through `gpt_consult.py`, applying the Arbiter's evidence rules and mandatory bars, requested by the maker at the done claim and never written by it. Trigger: per claim (A-1), before every conditional close (A-3), on every check-defect verdict (AU-2). It stands in for the Arbiter until that role binds and for the Auditor's per-verdict re-checks. No schedule and no cap: it is a ritual of the closing seat.
- UNVERIFIED: whether any program or hook refuses a close that lacks the reviewer's read. I found none; the role files describe it only as a rule.
- The contracts carry its verdict as the `interim` field of each Arbiter verdict (`src/RimMandrake/contracts/models.py:262`) [LIVE as schema].

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

### 2.19 Designed on 2026-10-29, not built [DESIGNED]

Four designs were written today. Each is DESIGN ONLY: no code, timer, schedule key or role-file text from them is live. The owner's rulings below are quoted from each item's ledger history (`rimflow show <ID>`). All four items are now owned by FOUNDRY.

**a. Findings curation** (`design/RimMandrake/findings_curation_design_2026-10-29.md`; item `FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X`, filed by the owner 2026-10-29T15:39Z for FOUNDRY, kind build).
- Why: the owner refused `FINDINGS_REDESIGN_BORN_AS_ITEMS_NO_LOBBY`; 127 findings were 50 distinct failures, one repeated 27 times.
- Options: A, a daily FOUNDRY curation ticket; B, a program folds repeats and FOUNDRY judges only what is new; C, a weekly Auditor pass. The owner filed B.
- Option B actors: a no-AI sorter run after every ingest from the Dispatcher's measure list (like ops_watch). It signs each finding (mod, test row, normalized failure text) into a standing-failures table, and on its own only merges repeats into an existing decision, routes red canaries and refused pulls to Operations' lane item, retires a row after 3 later passes in a row (reopens on a new fail), and flags done-but-failing items (§6 of the design). FOUNDRY judges what is new, daily, with a weekly pass (item title).
- New handoffs if built: testq ingest → sorter → Operations (rig health) and → FOUNDRY (new failures).

**b. v3 health daily check** (`design/RimMandrake/v3_health_daily_check_2026-10-29.md`; item `V3_HEALTH_BUILD_DAILY_PULSE_DAY_ONE`).
- Owner, verbatim: "1, 2, 3 - should be a daily check performed by a responsible party all the time (could be Ops, could be Arbiter). Everything but 4. Switching off agents is a good idea later when we show that at least a nominative system is functional for awhile."
- By card 17:06Z: Operations owns all of it (message tagging, planted faults, output tracing, the daily page); the Auditor's weekly re-check guards Operations grading its own usefulness.
- By card 17:23Z: the kill-test baseline is an Opus gold-labelling of the v2 week; the Haiku tagger is measured against it. A BENCH note at 17:31Z says the spec's §2 still describes the old baseline and is owed a revision.
- Planted faults, owner's revision (17:23Z): plants come "from outside the system (I would suggest Auditor by its very design)", are treated as real faults, are recorded in a secret register, and are marked as plants after the experiment, with "corrected fault-free" parallel stats. By card 17:34Z: the Arbiter reads only ended plants; the Conductor alone reads live plants. Owner 17:34Z: the build may proceed but the plant part ships OFF (schedule switch disabled); turning it on is his call once v3 has stabilized.
- Designed actors and cadences (design §1): `owner_tags.py extract` every 15 min inside the ops_watch pass (no AI); `owner_tags.py tag` hourly on its own timer (Haiku); `health_drill.py plant` on its own timer at a random minute (Auditor's program) and `health_drill.py watch` every 15 min; ops_watch collector `health.trace.*` every 15 min; `v3_health_page.py` as the last step of the ops_watch pass, one dated copy a day. Operations reads the page in its existing 07:30 and 19:30 runs and on health alarms; no new role run. Outputs under `D:\ClaudeWork\rimmandrake\v3_health\`. Using `health.*` keys for dispatch decisions is out of scope.
- Part 4 (switch roles off to see what breaks) is deferred by his ruling.

**c. Process model v2/v3** (`design/RimMandrake/process_model_v2_v3_design_2026-10-29.md`; item `OPS_MODEL_BUILD_V3_TWIN_FIT_DAILY`).
- Owner, verbatim: "Operations should be using a custom v3-based model fit. v2 models should be specific to that v2 workflow and parameterized appropriatley, only fit to past v2 data logs. v3 should have different parameterizations ... v3 model should be tuned at least once a day on the ongoing data record".
- By card 17:34Z: compare on the shared work core plus v3 tickets re-counted the v2 way; v2 fit window 2026-10-06..10-26 (fit two weeks, predict the third); owner-habit shifts go to the daily summary only, never a direct alert.
- Designed actor: `rm-process-model.timer` (user systemd) daily at 06:30 local, hard 30-minute timeout, nice 10; deterministic ABC-MCMC (20 chains × 150 steps, 120 members, about 10-15 CPU-minutes on 4 processes); a held-out-day check gates `current.json`; 3 failures in a row → RED, filed as an item. Outputs under `D:\ClaudeWork\rimmandrake\process_model\`, nothing in the repo. ops_watch adds a daily series line and an alarm (no fit for 36 h, or RED). Operations reads `digest.md` at 07:30 and never retunes by hand.

**d. Producer cadence** (`design/RimMandrake/producer_cadence_2026-10-29.md`; item `PRODUCER_CADENCE_DESIGN_MORE_THAN_WEDNESDAYS`).
- Owner, verbatim: "I think calling the Producer once a week for planning is not at all the entirely of Producer. It also needs to track that schedule (relative to the stats from Operations, Foundry, etc.) and make a daily plan to follow as well. Likely 2-3 times a day may be needed, that's a tuning parameter."
- By card 19:42-19:43Z: option B, gated check-ins at 12:00 and 18:00 (new schedule key `track_slots_local`); a big slip triggers an immediate Conductor run ("Wake me at once"); on-schedule counts only items built with a real commit (ledger-only or under-5-minute closes excluded as suspect).
- Designed actors: a no-AI tracker (ops_watch collector `plan.*`) compares the day's plan `today.json` checkpoints with measured progress. A tracking slot launches the Producer only when the newest MEASURED reading shows `BEHIND`, `AHEAD`, `RUNNING_DRY`, a big slip or a failure; a new event kind `plan_slip` (edge-triggered) shares the existing `event_runs_per_day` 1. At most three Producer runs a day inside the existing 2.0M daily cap; add 15:00 if FOUNDRY runs dry between 12:00 and 18:00 most days of the first week.

### 2.20 v3 cutover (program, one-shot) [LIVE, applied]

- **What.** `src/RimMandrake/rimflow/v3_cutover.py`; record `infrastructure/state/v3_cutover/record.json` (state `applied`, 2026-10-29T01:32:17Z, item `V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY`).
- **Owner, verbatim (ownerSaid in the record):** "Once we switch over to Conductor + ispatch + Foundry, all bench items get reassigned to Dispatch-> Foundry".
- **Effect.** 691 BENCH items moved to FOUNDRY; 40 kept (they need the owner or L4); 0 deferred. The FlowWorks/GSS lane seat flipped from BENCH to FOUNDRY, and the docs patch was applied to `infrastructure/agents/BENCH.md` and `FOUNDRY.md`. A revert path exists in the program.
- **Design of record** (quoted in the record): "there is no BENCH seat in v3; the Conductor absorbs Bench and works only in live sessions with him; FOUNDRY is the one autonomous builder."
- **Residue** [LIVE]: `slot_rules.json` still lists seats BENCH and FOUNDRY with `fallback_n` BENCH 3, and the live helper budget carries the owner's BENCH override of 6 until 2026-11-04 (§2.14). Older standing text that "BENCH owns all FlowWorks + GSS" contradicts FOUNDRY.md:18 after the cutover.

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
| 07:05 Mon | v3_vs_v2 | weekly v3-vs-v2 scoring (timer installed, not enabled) | [OFF] |
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
- [LIVE, `rl:351, 382, 388, 401` use `time.localtime`] "Local day" is the machine's local timezone (PDT/PST on this box), so the day boundary is local midnight.

**Designed additions to the day, not live (§2.19):** 06:30 process-model fit (timer); 09:00 Producer daily plan as today; 12:00 and 18:00 gated Producer tracking slots; every 15 min owner-message extract, output trace, drill watch and the health page inside the ops_watch pass; hourly Haiku tagging; planted-fault timer at a random minute (ships OFF); findings sorter after every ingest.

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
| Operations → owner | proposals | `ops_watch\owner\OP-<ts>.md`, relayed by the Conductor (OPS PROPOSAL / OPS DECISION) | Waits for the next Conductor check or BENCH session. No timeout: none is named in `roles/conductor.md:80`, `roles/operations.md:154` or `ops_watch.py`. [LIVE] |
| Operations → Producer | replan request | `REPLAN REQUEST RR-<ts>` note | Triggers a Producer event run (≤1 a day). Otherwise read at the 09:00 run. [LIVE] |
| Producer → FOUNDRY | ordered work | ledger raises and queue order | FOUNDRY picks it up when rung. [LIVE] |
| Producer → owner | cut list | CUT LIST -r<N>, relayed by the Conductor; owner CUT DECISION; Producer CUT APPLIED | Waits. [LIVE as a role-file rule] |
| Producer → Conductor | TESTQ mod choice | note | Designed: the Conductor sets env `TESTQ_FILL_MODS` / `TESTQ_SWEEP_MODS` (Part 4 row P-6). Live: the variables are set nowhere, so the units default to FlowWorks (§2.15). No program path carries the choice to the units. [DESIGNED / LIVE as absent] |
| FOUNDRY → interim reviewer and Arbiter | close with sha and evidence | `rimflow close` | The closing seat asks the interim GPT reviewer itself (`gpt_consult.py`, §2.17); no program enforces it. The Arbiter judges at 11:00/17:00 if pending work exists. [LIVE as rule / LIVE] |
| Arbiter → Auditor | verdicts | `arbiter\verdicts.jsonl` | Read at 13:00. On day one the trial wrote `arbiter\trial\verdicts.jsonl` instead, so the Auditor could not compare (health check). [LIVE] |
| Arbiter → owning seat | FAIL | ticket | Waits in the queue. [LIVE] |
| Auditor → owning seat | DEFECT | ticket via `rimflow file/spawn` | Waits in the queue. Day one: `AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH` was reassigned to FOUNDRY with no work event seen (health check). [LIVE] |
| Auditor → Arbiter | escapes | ticket | Read at the next Arbiter run. [LIVE] |
| Auditor → Conductor | waiting picks after 3 runs; charter drafts; questions | ledger note | Next Conductor run. [LIVE as a rule] |
| Innovator → Conductor → owner | proposals | ledger, then the Conductor card | Nothing happens until he answers. [LIVE as a rule] |
| testq → ledger | test results and findings | `ingest.py` RUNNER events | Findings pile up UNTRIAGED: 128 on day one. No running consumer (§2.15). [LIVE] |
| steward → BENCH → owner | Steve lane fault | `STEVE_LANE_UNSTICK_*` item at T+10; raise at T+30; owner item at T+120 | BENCH absent: it escalates to the owner at 120 min. [LIVE] |
| seat_restart → FOUNDRY | kill and relaunch | SIGTERM/SIGKILL, then `seat_loop.sh` | Cancelled by any human input. The live kill path is unexercised. [LIVE] |
| Conductor → owner | everything above, batched | question cards, `conductor\log.md`, BENCH session | Held until he is present. [LIVE] |
| owner → system | rulings | `--owner-said` notes, schedule edits, OFF files, PAUSE, `slot_override.json` | n/a |
| testq ingest → findings sorter → Operations / FOUNDRY | repeats merged, rig health routed, new failures | standing-failures table, outcome events | [DESIGNED, §2.19a] |
| ops_watch health pass → Operations | message tags, trace, drill catches, the health page | `v3_health\` files, `health.*` keys in `status.json` | Read at 07:30 / 19:30 and on alarm. [DESIGNED, §2.19b] |
| Auditor planter → secret register → Conductor (live) / Arbiter (ended only) | planted faults | secret register; public reveal verb | Ships OFF until the owner turns it on. [DESIGNED, §2.19b] |
| process-model timer → Operations | daily v3 fit, held-out check, drift | `process_model\digest.md`, `current.json` | Read at 07:30. [DESIGNED, §2.19c] |
| plan tracker → Producer → Conductor | BEHIND / AHEAD / RUNNING_DRY / big slip | ops_watch `plan.*`, `today.json`, event `plan_slip` | Gated slots 12:00 / 18:00; a big slip wakes the Conductor at once. [DESIGNED, §2.19d] |

---

## 5. Arbitrary parameters

"Who may change" is taken from the doc and role files. Sources: Part 4 of `design/RimMandrake/rimflow_v3_responsibilities_2026-10-26.md` gives the owner "the starting schedule" (row L-1) and gives Operations the tightening of `slot_rules.json`, with any loosening his (row O-14) [DESIGNED]. No code enforces either: anyone with commit rights can edit these files [LIVE: I found no hook or check that guards them]. Where a row says "not named", no file I read names who may change it.

| parameter | value | where set | who may change | why (if recorded) |
|---|---|---|---|---|
| tick_s | 120 | sched:4 | owner (P4 L-1) | Dispatcher cadence |
| timer OnUnitInactiveSec / OnBootSec / TimeoutStartSec | 120 s / 3 min / 600 s | rm-dispatcher.timer/.service | not named | |
| tick_budget_s | 420 | dispatcher | owner (P4 L-1) | |
| stall_after_s | 240 | sched:5 | owner (P4 L-1) | idle before a ring |
| verify_s | 300 | sched:6 | owner (P4 L-1) | ring must be consumed in |
| handoff_s | 600 | sched:7 | owner (P4 L-1) | claim must follow the ring in |
| max_retries | 2 | sched:8 | owner (P4 L-1) | |
| cooldown_s | 3600 | sched:9 | owner (P4 L-1) | |
| dead_after_s | 600 | sched:10 | owner (P4 L-1) | |
| recover_verify_s | 300 | sched:11 | owner (P4 L-1) | unused (recovery off) |
| owner_idle_s | 1200 | sched:12 | owner (P4 L-1) | game/bridge tickets wait for an idle owner |
| alarm_every_s | 21600 | sched:13 | owner (P4 L-1) | |
| HOLD_ALARM_EVERY_S | 21600 | disp:573 | code | |
| ops_stale_s / OPS_STALE_S | 2700 | sched:3, rl:116-165 | owner (P4 L-1) | |
| FUTURE_TOL_S | 300 | rl:116-165 | code | |
| EVENT_LOOKBACK_S | 21600 | rl header | code | |
| RUN_NOW_TTL_S | 3600 | rl:116-165 | code | |
| SCOPE_GRACE_S / SCOPE_STOP_S | 600 / 30 | rl:116-165 | code | |
| wakes_per_seat_hour / _seat_day / _per_day | 12 / 96 / 120 | sched:20 | BENCH changed them 10-29 | `FOUNDRY_IDLE_DIAGNOSE_CAP_STARVES_TRIAGE`; were 6/48/80 |
| recovers_per_seat_day | 3 | sched:20 | owner (P4 L-1) | unused |
| code cap defaults | 3/30/80/3 | disp:99 | code | |
| RM_DOORBELL_MAX_WAIT_S / POLL_S | 23 h / 3 s | doorbell hook | env | |
| backstop_ctx_tokens / backstop_idle_s / grace_s (FOUNDRY) | 110000 / 1800 / 30 | sched:35 | owner (P4 L-1) | |
| seat_restart defaults | see §2.4 table | seat_restart.py DEFAULTS | code | |
| lease length / renew | 45 min / every 10 min | `lease.py:72-73` `LEASE_TTL_S`, `RENEW_EVERY_S` | code | [LIVE] |
| helper_budget MAX_AGE_S / FUTURE_SLACK_S | 600 s / 5 s | `helper_budget.py:32-33` | code | [LIVE] |
| owner idle required / boot slack | 1200 s / 60 s | `idle_probe.py` `IDLE_REQUIRED_SECONDS`, `BOOT_SLACK_MS`; owner card 2026-10-26 19:06 | owner (card) | [LIVE]; any probe failure is UNMEASURED, never idle |
| slot_rules modes, caps and lent-account limits | see §2.14 | `slot_rules.json` | code | [LIVE] |
| slot_late_s | 3600 (every role) | sched:59,76,92,108,123,136 | owner (schedule) | |
| run_max_s | Conductor 1800, Arbiter 2700, Auditor 2700, Operations 1800, Producer 1800, Innovator 2700 | same lines | owner | the only hard stop |
| Conductor quick_token_cap / daily | 450000 / 1350000 | sched:50 | owner | |
| Conductor session_week_pct_cap | 6 | sched:51 | owner | |
| Conductor session_helpers_max | 3, every band | sched:52-55 | owner | role file says 2 across roles |
| Arbiter run / daily cap | 500000 / 1250000 | sched:66 | owner | |
| Arbiter pre_launch budget / tiers cap / pre_launch_max_s | 900 s / 6 / 1200 s | Arbiter entry | owner (P4 L-1) | |
| Auditor run / daily cap | 700000 / 875000 | sched:81 | owner | `_caps_why` matches (c2dfc21445) |
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
| ops_watch every_s | 900 | sched:38, timer `*:07/15` | owner (P4 L-1) | |
| ops_watch band k_sigma / baseline / min_points | 3.0 / 7 d / 20 | ops_watch_rules.json `band` | not named | |
| ops_watch run n | 8 | ops_watch_rules.json `run` | not named | |
| ops_watch silent windows | 2 h default; accounts/production 3 h; process/testing/tokentalk 6 h | ops_watch_rules.json `silent` | not named | |
| alarm clear_passes / lock_wait_s | 4 / 90 | ops_watch_rules.json `alarm` | not named | |
| target: runway (accounts, codex) | <1.0 alarm | targets | owner brief 10-26 | |
| target: steve.unowned_stall_min | >30 alarm | targets | owner brief | |
| target: steve.incident_unclaimed_min | >10 alarm | targets | owner 10-28 15:50 | |
| target: steve.invalid_streak | ≥3 alarm | targets | owner brief | |
| target: disk root / C: / D: free GB | <210 / <200 / <200 alarm; root <420 flag | targets | not named | scratch grew 207 GB in one day |
| target: timers.failed_units / evidence.tamper | >0 alarm | targets | not named | |
| target: testing.nothing_h_7d | >18 flag only | targets | v3 §6 | |
| target: process.share_7d | ≥61 flag only | targets | v3 §6 | |
| target: tokentalk share | ≥10 flag only | targets | owner 10-27 | |
| target: flow.untriaged_findings | >0 flag only | targets | not named | |
| testq tick / probe | 60 s / 300 s | testq-tick.timer, TESTQ_PROBE_S | env | |
| testq fill chains / hours / cap | 4 / 8 h a day / 200 | TESTQ_FILL_CHAINS, TESTQ_FILL_HOURS (testq.py:1016), TESTQ_FILL_CAP | env | |
| testq DRY rule | 2 UNMEASURED runs; retry after 3 days | testq.py header | code | |
| steward escalation | 10 / 30 / 120 min; manual pause fault at 60 min; READY fault at 5 min; heartbeat stale 5 min | steward.py header | code | |
| Archmagi silent / backoff | 600 s / 1800 s | testq.py header | env | lane OFF |
| testq sweep | 01:30, FlowWorks | testq-sweep.timer | env | |
| memory | claude-seats.slice 24G (10G per seat); rm-harness.slice 12G | systemd slices | not named | |
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
6. **Closed.** `rimflow implemented --sha` (to `built`) or `rimflow close --sha <sha>` with evidence. The lease is 45 min and is renewed every 10 min while held (`lease.py:72-73`). [LIVE]
7. **Judged.**
   - The interim GPT reviewer gates the close: the maker requests a `gpt_consult.py` read at the claim (§2.17). Nothing in code refuses a close without it.
   - The Arbiter gives an advisory verdict at its next batch, written to `verdicts.jsonl`.
   - A FAIL-check or RESTART-environment verdict waits for an Auditor SOUND before its set-aside red stops blocking. [LIVE as a rule]
8. **Sampled.** The Auditor's pre-screen checks every close since its last run. Hard flags become defect tickets; risk-ranked and random picks are re-checked. A DEFECT reopens the cycle as a new ticket, since the Auditor never reopens an item itself. [LIVE]
9. **Accepted.** Not a defined state or event [LIVE: absent from FOUNDRY.md's ladder and from the ledger per the health check]. The health check says no ledger event marks "pass on named scenarios, specific build, non-maker check", so accepted items/day is UNMEASURED.
   - The item states seen are `proposed`, `validated`, `implemented` and `superseded`.
   - [LIVE, FOUNDRY.md:8-17] The state ladder is reserved (lease) (claim takes the same lease) → `built` (`implemented --sha`, criteria tagged L0-L4) → `validated` (passing `verify --criterion`) → `done` (the last criterion), or `close --sha` straight to done when nothing live is owed. No state or event is called "accepted"; `done` is the last state, and the health check found no event marking the north-star sense of accepted.
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
1. Role file headings now say each role is enabled, with its enabling commit (e35afe1dcc for the Conductor and Operations, 4d9171a1e5 for the rest); fixed in 2a5ec4a7ee.
2. The schedule's top-level `_doc` now states that every role is enabled, that caps are admission checks plus alarms, and that the bands are neutralized; fixed in c2dfc21445.
3. The throttle bands are neutralized (all "slots: all", ×1.0, commit d92c4c825e). The Conductor `_why` and the operations.md throttle section now say so (2a5ec4a7ee, c2dfc21445). `throttle_order` is read only by the simulator `Utils/sim/rimflow_v3_sim.py`.
4. Every `_caps_why` now quotes the live caps (Producer 800k run / 2.0M day, Auditor 700k / 875k) (c2dfc21445).
5. `session_helpers_max` (Conductor, 3) and `helpers_max` (2 on three roles) are read by no program; the schedule `_why` says so (c2dfc21445). Helpers are bounded by the helper hook and `helper_budget.json` only (see item 32).

**Built but off or missing:**

6. v3_vs_v2 is `enabled: false`. Its units `rm-v3-vs-v2.{service,timer}` (Mon 07:05 local) are committed in `Utils/systemd/` and installed, but the timer is NOT enabled; switching it on is the owner's (aa4adea115). One manual start on 10-29 exited 0. No program reads `enabled`; the timer is the switch. HC: the only scored week precedes the cutover (`NOT_V3`). The counterfactual backtest failed on coverage (0.429 of 14 cells, needs 0.75). Four settled weeks put the earliest verdict around 2026-11-23.
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

**Caps are admission checks plus alarms, not stops:**

18. Token caps are admission checks at launch plus after-the-fact alarms: a launch is refused (`role:<name>:cap`) when the day's spend plus the run budget would pass `daily_token_cap`, and an overrun raises `role:<name>:overbudget` after the run. Only `run_max_s` stops a run. Day-one overruns:
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

31. The v3 cutover moved 691 BENCH items and the FlowWorks/GSS lane to FOUNDRY (§2.20), yet `slot_rules.json` still lists a BENCH seat with `fallback_n` 3, the helper budget carries a BENCH override of 6 until 2026-11-04, and the Conductor's scheduled checks launch as seat BENCH (CONDUCTOR.md:57). The standing text that said BENCH owns all FlowWorks + GSS was corrected to FOUNDRY in CLAUDE.md, the charter and the helper rules (efabf1399a).
32. Four different numbers govern Conductor helpers: role file and CONDUCTOR.md "two across all roles", schedule `session_helpers_max` 3 (read by no program), `slot_rules.json` `conductor_session_n` 3, live `helper_budget.json` CONDUCTOR 6 (§2.14). Only the per-seat budget is enforced in code.
33. The Producer's test-lane mod choice has no path to the testq units: `TESTQ_FILL_MODS` / `TESTQ_SWEEP_MODS` are set nowhere, so testq fills FlowWorks only (§2.15).
34. Findings have no consumer on any cadence and no Part 4 duty row; the chosen fix is designed, not built (§2.19a).
35. The v3 health spec's §2 still describes the pre-ruling kill-test baseline (BENCH note 17:31Z on `V3_HEALTH_BUILD_DAILY_PULSE_DAY_ONE`).
36. Part 4 hands a duty over only when its role is enabled and its first run is recorded; it names no record of which duties have handed over. Whether each Wed/Fri/Sun handover happened is answered role by role in §2 (run records), not by a hand-over ledger.

**Still UNVERIFIED after the second pass (counted):**
1. Whether any program refuses a close that lacks the interim GPT reviewer's read (§2.17).
2. The companion grant file's path and current expiry (§2.16).
3. The Dispatcher's full-day ring count for day one (§2.5).
4. Who ran `v3_vs_v2.py` by hand for the week ending 2026-10-26, and when (§2.13).
5. Archmagi lane run history behind the 4.39 h in 7 days (§2.15).
6. Whether the Arbiter's weekly pass, designed in `roles/arbiter.md`, has ever run (§2.10).

Resolved in the second pass: helper_budget numbers and MAX_AGE_S; `after_role` semantics; local-day timezone; PAUSE versus role launches; the scope-stop trigger; FOUNDRY's charter and owner touchpoints; the accepted-state definition (none exists); the interim reviewer's mechanism (a closing-seat ritual); how the TESTQ mod choice is applied (it is not); the owner-proposal timeout (none); the lease constants; the findings consumer (none); the "who may change" column (Part 4 L-1 and O-14).

**Sources read for the second pass:** the four 2026-10-29 designs and their ledger rulings (`rimflow show`); `rimflow_v3_responsibilities_2026-10-26.md` Part 4; `infrastructure/agents/CHARTER.md`, `CONDUCTOR.md`, `FOUNDRY.md`, `Agent_Policy.md` (targeted); `slot_rules.json`; `idle_probe.py`; `lease.py`; `helper_budget.py` and the live `helper_budget.json`; `v3_cutover.py` with `record.json`; the testq systemd units. Not read: `conductor_briefing_2026-10-28.md`, `delegation_policy.md` beyond what FOUNDRY.md cites.
