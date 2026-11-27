# BOUNDARY: the sweep of the SteveDesktop test lane, Design Version 0.1.0

Code: `src/RimMandrake/Utils/testq/steve_lane_sweep.py` (commands `grid [--quick]`, `one '<json>' [--plant P]`,
`gate [--plant]`). Its selftest: `src/RimMandrake/Utils/testq/selftest_steve_lane_sweep.py`.
Item: `RIMMANDRAKE_BUILD_STEVE_LANE_SWEEP_PAUSE_HELD_49_HOURS`. The code that it sweeps:
`src/RimMandrake/Utils/testq/testq.py` (`cmd_tick`, `reconcile`, `finish`, `admit`, `ssh_reachable`, `cmd_pause`),
`src/RimMandrake/Utils/testq/lane_stop.py` (`step`, `on_finish`, `stopped`) and, for part C,
`src/RimMandrake/Utils/account_plan.py` through `src/RimMandrake/Utils/account_plan_sweep.py`.

Offline simulation: yes. The sweep runs the real testq tick (`T.cmd_tick`) and the real job builder (`S.make_job`) every
60 s pass of a simulated day on a fake clock, in a temp queue home, against fake games; part C runs the real
`account_plan.tick` through `account_plan_sweep`'s world. After every pass it checks that no job, pause, stop or ssh mark
stands in a state that no later pass of the real code can leave.

## What it is

Part A/B is the lane. Each pass: the regime's hand events (a pause, a legacy pause record, hand jobs), `cmd_tick`, one
fill per mod (`pick` stands in for the modcheck ranking; the job is the real `S.make_job`, deduped by the real
`T.same_request`), `cmd_tick` again, then the checks. Part C is the account gate on SteveDesktop: a run there that never
ends by itself, on the live account, while a switch falls due.

The stand-ins replace only what touches the world:

| stand-in | replaces | model |
|---|---|---|
| the games | `worker.py` over ssh (`T.remote`) for Steve1 and Steve2 | the verbs `status`, `status --job`, `start [--retry]`, `result`, `ack`, `outbox`, `stop`; each game is free, runs an attempt for its minutes, and has windows: `broken` (the same REFUSED note on every job), `canary` (INVALID/CANARY), `crash`, `lose` (the worker forgets the attempt), `unread` (result unreadable), `busy` (a driver holds the guard), `guard` (late GUARD_HELD), `sync` (a refusal that pauses every game) |
| ssh | `T.remote` raising `SshDown` | down windows |
| systemd | `subprocess` in testq and lane_stop | `systemctl is-active` reads the regime's unit windows; an `systemd_unread` window times out |
| the clock | `time.time`, `S.utcnow`, `S.new_job_id` | the fake clock from 2026-11-23T00:00Z |
| git, the ledger, the steward's ticket | `T.git` and the hand-only helpers | no-ops |
| the meter and the switcher (part C) | as in `design/specs/2026-11-25-account-plan-sweep/boundary.md` | its `World`, with the order and stop seams of 44a3797f6e added |

## ACCEPTS

- **a-regime.** A JSON object (`one '<json>'`): `hours`, `seed`, `mods`, `steve1` and `steve2` (each a map of windows
  in hours: `broken`, `canary`, `sync`, `crash`, `lose`, `unread`, `busy`, `guard`; `off` for a game switched off),
  `ssh_down`, `units` (a unit's active window), `systemd_unread`, and `events` (`pause`, `legacy_pause`, `jobs`).
- **a-plant.** One name of `PLANTS` (a monkeypatched reversal of a shipped fix, or a mutant of a shipped step), for the
  selftest only; `STEVE_LANE_SWEEP_PLANT` forces one on every regime.
- **a-blind-list.** `STEVE_LANE_SWEEP_BLIND=<CHECK,...>`: checks switched off, to see each fault test red.

## DOES NOT SURVIVE (not shown by the sweep)

- The steward's escalation and `brake_release`: a person ends that state; it is a hand state by design.
- The modcheck fill ranking and `cmd_submit`'s refusals: `pick` stands in for them.
- The Archmagi lane, the visit feed, the site stage and companion staging: stubbed; they hold no SteveDesktop lane state.
- systemd unreadable for ever: a unit pause then stands until a person reads it (designed in 767bcaeba9); the sweep
  reads only unread windows that end.
- A torn pause or stop record: `S.dump` writes atomically.
- A refusal whose note differs in its words each time: `lane_stop.on_finish` keys on the signature; the sweep plants
  only equal ones.
- Real game timing: an attempt lasts the regime's minutes; a pass is exactly 60 s.

## PROMISES (each one is owed a check of the same name in the selftest)

- **pause with no end found.** With `lane_stop.step` taken out of the tick and a pause record that names no end
  (the 2026-11-15..17 pause of 49.3 h), the sweep reports PAUSE_PAST_END and the pause stands 49.3 h; on the shipped
  code the same regime ends the pause on time.
- **one refusal repeated found.** With `lane_stop.on_finish` stopping nothing (2026-11-23: Steve2 gave one refusal 47
  times in 11 h), the sweep reports REPEAT on Steve2 and at least 47 equal refusals in a row; on the shipped code no
  third equal refusal comes sooner than `lane_stop.RETRY_S` after the one before.
- **account gate refusing every launch found.** With `account_plan.machine_bound_s` unbounded (the code before
  44a3797f6e; 2026-11-26: 3.6 h of refusals), part C reports STUCK on SteveDesktop; on the shipped code it switches and
  refuses no longer than the STUCK limit.
- **each check sees its fault.** Each check with no measured fault of its own is red on a planted one: a stop that
  names an end 10 days out (STOP_PAST_END), no `reconcile` (JOB_STUCK), no `admit` (JOB_STUCK), no re-probe of ssh
  (SSH_MARK_PAST_END).
- **shipped lane sweeps clean.** The shipped code over every regime below reports no violation, and jobs end.

## THE WANTED BEHAVIOUR (checked on every pass)

- **PAUSE_PAST_END.** A lane pause ends by its `until`, else `since` + `lane_stop.DEFAULT_PAUSE_H`, else at the end of its
  unit's active window (time that systemd could not answer is not counted).
- **STOP_PAST_END.** A repeat stop that is in effect (`lane_stop.stopped`) ends by `since` + `lane_stop.RETRY_S`.
- **REPEAT.** No third equal refusal in a row on one game comes sooner than `RETRY_S` after the one before.
- **JOB_STUCK.** A running attempt (keyed by job and attempt) whose game is reachable and readable moves; a ready job
  does not wait while a game is free.
- **SSH_MARK_PAST_END.** testq does not mark SteveDesktop down past `T.PROBE_S` after ssh is back.

## THE MEASURES (each regime)

Each check prints its worst value, its limit and how many cases it read: `pause_late_s`, `stop_late_s`,
`repeat_gap_s`, `running_stale_passes`, `pending_free_passes`, `ssh_mark_late_s`; and `jobs_done`, `done_ok`,
`same_refusals_max`.

The regimes: calm; ssh flaps; Steve2 broken all day with 60 hand jobs; Steve1 broken 3-11 h; canary reds; sync refusals;
crashes, lost attempts, unreadable results, a busy guard and late GUARD_HELD; Steve2 off with a pause in an ssh outage;
hand pauses of every kind (hours, `until_unit` with the unit ending, with
systemd unreadable for a window, a legacy record with no end); and four seeded mixes of all of these, 24 h each.
`--quick` cuts each named regime to 16 h and drops the seeded mixes; the planted faults run whole either way.

## LIMITS

- `PASS_S` = 60 s: `testq-tick.timer` fires each minute (measured: the unit file).
- `END_LIMIT_S` = 2 passes: an end is due at the first tick past it; one more pass absorbs the order of the tick's steps
  (danger: a looser limit hides a late end; evidence: the shipped worst is -60 s on every regime).
- `STUCK_PASSES` = 2: a running attempt is read each tick; two passes with no move on a readable game is no move
  (evidence: the shipped worst is 1).
- `RETRY_S`, `DEFAULT_PAUSE_H`, `PROBE_S`: read from `lane_stop` and `testq`, never copied.
- The smallest shipped repeat gap is `RETRY_S` + one pass to admit + the 1-2 min refusal (measured 1920 s): the
  designed retry, with one ticket filed through ingest.
- The planted pause regime is 51.3 h (the measured 49.3 h past the 2 h default); its shipped control is cut to 11 h,
  past the fault's own end, to keep the selftest near 35 s with `--quick`.

