# Producer cadence: more than Wednesdays (design, 2026-10-29)

Item: `PRODUCER_CADENCE_DESIGN_MORE_THAN_WEDNESDAYS`. Design only: no code, no role-file edit. Builder: FOUNDRY.

The owner, 2026-10-29 (verbatim): *"I think calling the Producer once a week for planning is not at all the entirely
of Producer. It also needs to track that schedule (relative to the stats from Operations, Foundry, etc.) and make a
daily plan to follow as well. Likely 2-3 times a day may be needed, that's a tuning parameter. Make sense? Do a design
pass here too."*

Read with: `src/RimMandrake/rimflow/roles/producer.md` (the role today), `src/RimMandrake/rimflow/roles/operations.md`,
`src/RimMandrake/rimflow/dispatcher_schedule.json` (`roles[name=Producer]`), `src/RimMandrake/rimflow/role_launch.py`
(how slots launch), `infrastructure/state/CONDUCTOR_GOALS.md`, `design/RimMandrake/rimflow_v3_2026-10-26.md` §2-3 and
§6, `design/RimMandrake/v3_health_daily_check_2026-10-29.md`, `design/RimMandrake/process_model_v2_v3_design_2026-10-29.md`.

## 1. The problem in plain words

The Producer today has one clock slot, 09:00 local. On Wednesday that run makes the weekly plan; on other days it
writes a daily list (the ordered items per seat, raised to the top of `rimflow next`). It also gets at most one
extra run a day when a plan step fails or Operations files a `REPLAN REQUEST`. Nothing looks at the plan again
between one 09:00 and the next.

Day one shows why that is not enough (evidence: `D:\ClaudeWork\rimmandrake\conductor\v3_health_2026-10-29.md`):

- FOUNDRY took about 20 of the Producer's raised items within 3 hours. FOUNDRY clears tickets fast, so a morning
  list can be used up by midday, after which FOUNDRY drifts to whatever `rimflow next` offers, on plan or not.
- Some of those items were marked implemented 1-3 minutes after the claim (GSS_CORD_SWAY 05:49 → 05:51,
  ARBITERTIERS 06:01 → 06:03, one a ledger-only "already done"). Counting those as progress would make the plan
  look on schedule when it is not.
- Test machine hours that catch nothing are about 37 h/week (ESTIMATE) against a target of 18, and 80% of the
  test runner's verdicts are `partial`. The Producer decides what the test lane runs, but only looks once a day.
- Until today's 09:00 (16:01Z) the Producer had never run from its own clock: its three earlier runs were run-now
  trials. Measured cost of its four runs (weighted tokens, from the run records in
  `D:\ClaudeWork\rimmandrake\dispatcher\roles\rm-role-producer-*.json`): weekly 660,585 and 942,824; event
  388,129; daily 595,409. Every one of them starts by writing the same 107,656 tokens of opening context to the
  cache (1-hour writes, weight 2), so **any Producer launch costs at least about 215,000 weighted before it reads
  anything**. This floor shapes the whole design.

The fix the owner asks for: a plan in three layers, and the Producer checking progress against it two or three
times a day, with the number of check-ins a setting in the schedule.

## 2. Three layers of the plan

| layer | when | what it is | exists today? |
|---|---|---|---|
| **Weekly plan** | Wednesday 09:00 (the weekly run) | per goal, highest rank first: the critical path, the scenarios each item must pass, what is cut first if short, the WIP cap, bar coverage, backlog hygiene | yes, unchanged |
| **Daily plan** | every day 09:00 (the daily run; on Wednesday after the weekly plan) | the day's ordered items per seat, each with its goal, stopping point and **an expected-by time** (a checkpoint), plus how many FOUNDRY items should be done by the next check-in; the test lane for today | partly: the daily list exists, the checkpoints and the machine-readable file are new |
| **Tracking runs** | the check-in slots (recommended 12:00 and 18:00 local), each launched only when the tracking sheet shows something to decide (§6) | compare the day so far with the daily plan; refill, re-order, change the test lane, or raise a slip alert | new |

The weekly plan answers "what this week"; the daily plan answers "what today, in what order, and by when"; the
tracking run answers "are we where today's plan said we would be, and if not, what changes". A tracking run never
rewrites the weekly plan: if the week no longer fits, it writes a slip alert and the next 09:00 run (or an event
run) replans, so the expensive weekly reasoning happens in one place.

## 3. What each run reads

All runs keep the Producer token-blind (owner, 2026-10-27): nothing they read carries an account, runway, budget or
token figure. Reads are cheap one-screen files written by programs; the Producer never re-gathers what a program holds.

| input | where | weekly | daily | tracking |
|---|---|---|---|---|
| goals | `CONDUCTOR_GOALS.md`, newest block | full | full | only if the sheet says the block changed |
| replan requests, cut notes | `blind_view.py show V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE --prefix ...` (as today) | yes | yes | yes |
| **the tracking sheet** (new, §5) | `D:\ClaudeWork\rimmandrake\producer\tracking.md` + `tracking.json`, rewritten by a program every 15 min | yes | yes | **first and mostly only read** |
| Operations' flags | the alarm and flag lines of `ops_watch\digest_blind.md` (never `digest.md`) | yes | yes | only the lines the sheet quotes |
| FOUNDRY throughput | on the sheet: items built and accepted today per seat, median claim-to-built time, off-plan share, suspect closes | summary | yes | yes |
| testq yield | on the sheet: per mod in `TESTQ_FILL_MODS` / `TESTQ_SWEEP_MODS`, hours run, verdicts pass / partial / fail, findings, "hours catching nothing" | yes | yes | yes |
| Arbiter verdicts | `arbiter\verdicts.jsonl` (absent = none yet, never "zero failures") | yes | yes | via the sheet |
| the model forecast | `process_model.py eta --queue <plan items>` and `forecast --days 7` (item counts and dates only) once it exists and its fit is PASS; until then the sheet's own trailing-rate estimate, marked ESTIMATE | yes | yes | via the sheet |
| queues | `blind_view.py queue BENCH` / `queue FOUNDRY` | full | full | only when refilling |
| completion of focus mods | `mod_completion.py <Mod> --md ...` | yes | yes | no |

## 4. What each run writes

| output | weekly | daily | tracking |
|---|---|---|---|
| `plan.md` in its own run folder `D:\ClaudeWork\rimmandrake\producer\<yyyy-mm-ddThhmmZ>_<mode>\` (as today, mode `track` added) | yes | yes | yes, short: what it saw, what it changed, `RUN COMPLETE` |
| **`today.json`** (new) in `D:\ClaudeWork\rimmandrake\producer\`: the daily plan the tracker measures against (per seat: ordered item ids, goal number, stopping point, expected-by time; the next check-in's target count; the test lane) | yes | **writes it** | **amends it** (refill, re-order, moved checkpoint), keeping the morning version as `today.<HHMM>.json` so drift is visible |
| ticket edits through `rimflow` (file, spawn, raise) so FOUNDRY's `rimflow next` follows the plan | yes | yes | only when it refills or re-orders |
| test-lane line `TESTQ_FILL_MODS=... / TESTQ_SWEEP_MODS=...` in `plan.md` `## Test lane` (the Conductor applies it, as today) | yes | yes | only when it changes it |
| **slip alert** to the Conductor: a note `PLAN SLIP PS-<yyyymmddThhmmZ>: <goal>, <what is behind>, <the new expected date>, <what the Producer already did>` on `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE` | if the week does not fit | if the week does not fit | when the sheet shows a big slip (§5) |
| status note on the parent item | yes | yes | **no** (the slip alert is the only note a tracking run writes) |

FOUNDRY follows the daily plan the way it follows it today: through `rimflow next`, whose top the Producer sets with
`rimflow raise`. FOUNDRY does not need to read `today.json`; the order is the plan. The new file is for the tracker
and for the Conductor and Auditor to check against.

## 5. How "on schedule" is measured

A program measures it, never the Producer by eye: a new Utils program (working name
`producer_track.py`), run as a collector in the existing 15-minute ops_watch
pass, writing `plan.*` keys into `status.json` and the one-screen `tracking.md`. No AI.

**What counts as done.** Two levels, kept apart:

- **built**: the item has an `implemented` or `close` event whose sha is a real commit that touches a non-ledger
  path (not a ledger-only sha; see `CLOSE_SHA_FIX_HEAD_FALLBACK_CLAIM_COMMITS`), and claim-to-built took at least
  the suspect floor (start at 5 minutes, a tuning key) or the item's `## verify` says it is a paperwork item.
  Anything faster, or ledger-only, is listed as **SUSPECT** and is not counted.
- **accepted**: the Arbiter passed it, or it closed with a passing verify on its named scenarios.

The schedule is measured on **built** (it moves within hours); quality is reported on **accepted** (it lags the
Arbiter's 11:00 and 17:00 batches). Both are on the sheet.

**The numbers on the sheet** (each with its mark, MEASURED / ESTIMATE / UNMEASURED):

1. **Day progress**: plan items built by now against plan items expected by now (from the expected-by times in
   `today.json`). Status `ON` within one item, `BEHIND` when two or more items past their expected-by time are not
   built, `AHEAD` when the plan's items for the next check-in are already built.
2. **Plan left for FOUNDRY**: raised plan items FOUNDRY has not yet claimed. Below the refill line (start at 2, a
   tuning key) the status is `RUNNING_DRY`: FOUNDRY is about to drift off plan.
3. **Off-plan share**: of FOUNDRY's claims since 09:00, how many were not on the daily plan.
4. **Critical path**: per goal, the model's p50 and p90 date for the last plan item of that goal (`process_model.py
   eta`), or until the model exists, today's built rate carried forward (ESTIMATE). A **big slip** is a goal whose
   p50 date passes the goal's date in `CONDUCTOR_GOALS.md` (this week: Wed 11-04), or a p50 that moved later by a
   day or more since the morning plan.
5. **Plan steps failed or blocked** since the last run (the existing `plan_step_failure` kind), and SUSPECT closes.
6. **Test lane yield**, per mod: hours run today and this week, verdicts pass / partial / fail, findings, and hours
   catching nothing (`testing.*` from ops_watch). A mod is `LOW_YIELD` when most of its hours this week caught
   nothing and none of its items is on today's plan.

**Probe before trust** (`infrastructure/state/facts/instrument_traps.md`): a sheet with zero plan items, zero claims
or zero built in a day when FOUNDRY committed is UNMEASURED, never ON. `today.json` missing or older than today's
09:00 run: every status is UNMEASURED and the tracking slot launches with that reason.

**Surplus counts too.** Operations' success test treats unused capacity as waste; likewise `AHEAD` and `RUNNING_DRY`
are reasons to act (pull work forward), not good news.

## 6. Triggers

| run | trigger | gate |
|---|---|---|
| weekly | Wednesday 09:00, after an Operations run (as today) | unchanged |
| daily | 09:00 every other day, after an Operations run (as today) | unchanged |
| **tracking** | each slot in a new schedule key `track_slots_local` (recommended `["12:00", "18:00"]`) | launches only when the sheet's newest MEASURED reading shows something to decide: `BEHIND`, `AHEAD`, `RUNNING_DRY`, a big slip, a failed or blocked plan step, a SUSPECT close, a `LOW_YIELD` lane mod, or a new Operations flag line since the last Producer run. Nothing to decide: the slot is journaled "on plan, nothing to decide" (a hold, no alarm, no tokens), the way the Arbiter's `pending_work` slots hold today. An unreadable or stale sheet launches, with the reason in its trigger. |
| event | the existing `plan_step_failure` and `replan_request`, plus a new kind `plan_slip` (the sheet's big-slip flag, edge-triggered: once per crossing) | shares the existing `event_runs_per_day` (1); past it, events wait for the next tracking or daily run, which reads them |

Times are chosen against the other roles: 12:00 follows the Arbiter's 11:00 batch, so its verdicts are on the
sheet; 18:00 follows the 17:00 batch and lands before the Conductor's 20:00 check, so a slip alert reaches the owner
the same evening. The count is the length of `track_slots_local`: `[]` is the old behaviour, three entries is the
owner's upper figure.

## 7. Token budget

The Producer itself stays token-blind; these are the Dispatcher's caps (schedule keys), set by the owner.

| run | cap (weighted) | basis |
|---|---|---|
| weekly | 800,000 (unchanged) | measured 660,585 and 942,824 |
| daily | 800,000 (unchanged; one `run_token_cap`) | measured 595,409 |
| **tracking** | **350,000** (new `track_token_cap`) | ESTIMATE: the ~215,000 opening floor, about 8 turns of cache reads (~90,000) and ~5,000 output tokens (~25,000), plus headroom. Re-measure on the first five real tracking runs. |
| event | 800,000 (unchanged) | measured 388,129 |
| **per day** | 2,000,000 (unchanged `daily_token_cap`) | weekday worst case: daily 595k + two tracking 700k + one event 388k ≈ 1.68M; Wednesday worst case: weekly 943k + two tracking 700k = 1.64M, and an event that would pass the cap waits (the existing rule) |

With the gate (§6), the expected day is the 09:00 run plus one tracking run (ESTIMATE: about 0.95M), not the worst
case. Two levers for FOUNDRY to measure, not decided here: a lean launch for tracking runs (a short `producer_track.md`
instruction file instead of the full `producer.md`, and checking what the 107,656-token opening load holds), and
whether tracking runs could use a smaller model (a schedule key `track_model`, default `opus`).

Note for the owner, not a change: the schedule's `_caps_why` text still says "day 1.0M" while the field reads
2,000,000; the field is what the Dispatcher enforces (filed as a finding, §11).

## 8. Process share

Process share is the share of commits in the last 7 days that touch only process paths (ops_watch `c_process`,
`process_regex`). Today 72.4% against a 61% target. Measured 2026-10-29: 4,204 commits in the last 7 days, 594 in the
last 24 hours.

- **Tracking runs write nothing to the repo unless they change tickets.** `plan.md`, `today.json` and `tracking.md` are
  scratch under `D:\ClaudeWork`. A held slot writes nothing at all. A tracking run that refills or re-orders makes one
  ledger commit, as a daily run does today.
- Worst case: two extra process-only commits a day against about 600 a day moves the 7-day share by about 0.3
  percentage points (ESTIMATE, arithmetic on the counts above). Gated, about half that.
- The build is a one-off: about 5 commits (tracker, schedule keys, role_launch mode and gate, role instructions,
  selftests), all process. Land it in one day so it moves one week's share, not several.
- The only way this design lowers the share is by keeping FOUNDRY on plan items, most of which are product work. That
  is not claimed; the off-plan share on the sheet (§5 item 3) is the number that would show it.

## 9. Hand-off with Operations

One line: **Operations measures and flags; the Producer decides the plan.** No input is produced by either AI for the
other to argue with: the shared numbers come from programs.

| question | owner | how it passes |
|---|---|---|
| Is there enough account capacity for the plan? | Operations (the only role that reads cost) | a `REPLAN REQUEST RR-...` in plan terms only, as today |
| Is a resource being wasted (test hours catching nothing, a redraw loop)? | Operations finds it in the economy pass and proposes the cut | its flag line in `digest_blind.md`; the Producer decides which mods the lane runs and writes the lane line |
| Is the work on schedule against the plan? | the tracker (a program) measures; the Producer decides what changes | `tracking.md` / `plan.*` keys; Operations never comments on order or scope |
| Is the tracker itself working (blind, stale, wrong)? | Operations, as for every ops_watch collector | `plan.*` keys are MEASURED / UNMEASURED like any other; a blind tracker is an Operations alarm, not a Producer question |
| Does the week fit? | the Producer, from the model's dates | a `PLAN SLIP` to the Conductor; the owner rules any cut through the Conductor, as today |

What changes for Operations: nothing in its runs. Its economy pass keeps flagging test hours that catch nothing; the
tracking sheet adds the per-mod split so the Producer can act on that flag the same day instead of the next 09:00.

## 10. Cadence options and recommendation

| option | what | for | against |
|---|---|---|---|
| **A. Fixed check-ins** | 09:00 plan + tracking at 12:00 and 18:00, always launched | simplest; the plan is looked at three times a day for certain | pays the ~215k floor on quiet days too; worst-case cost every day; more ledger commits |
| **B. Gated check-ins (recommended)** | 09:00 plan + tracking slots in `track_slots_local` (12:00, 18:00) that launch only when the sheet shows something to decide, + `plan_slip` as an event | check-ins happen when they matter; quiet days cost one run; the count stays the owner's tuning parameter; reuses the Arbiter's proven hold-on-nothing-pending pattern | depends on the tracker being right: a blind tracker that reads ON would silence the check-ins (covered by the UNMEASURED rules and the L0 probes below) |
| **C. Events only** | 09:00 plan; no tracking slots; the tracker fires a Producer run on a slip or running-dry, up to N a day | cheapest | no guaranteed check-in, which is what the owner asked for; every threshold error becomes silence; harder to reason about "when does the Producer look" |

**Recommendation: B, with two tracking slots (12:00 and 18:00).** Three Producer touches a day at most, inside the
existing 2.0M daily cap, no new repo writes on quiet slots, and the count is one list in the schedule. Move to three
slots (add 15:00) if the sheet shows FOUNDRY running dry between 12:00 and 18:00 on most days of the first week.

## 11. L0 checks for the build

Each is a selftest or a one-command probe FOUNDRY runs before calling a step done (`run_selftests.py --only ...`).

1. **Slot parsing.** With `track_slots_local: ["12:00","18:00"]`: 09:00 is mode `run`, Wednesday 09:00 is mode
   `weekly`, 12:00 and 18:00 are mode `track` with `track_token_cap`. `[]` gives no tracking runs. A tracking slot
   never becomes the weekly run. (Today `slots()` turns every non-weekly slot into `quick` as soon as a
   `quick_token_cap` exists; the build must not reuse that key for this.)
2. **The gate.** A fixture sheet that reads ON with nothing new: the slot is journaled "on plan, nothing to decide"
   and no run starts. Each of BEHIND, AHEAD, RUNNING_DRY, big slip, failed plan step, SUSPECT, LOW_YIELD, new
   Operations flag: the slot launches and the trigger names the reason. Stale or unreadable sheet: launches with that
   reason.
3. **Tracker on real data.** Run on the 10-28..10-29 ledger: it finds the ~20 Producer-raised items FOUNDRY claimed,
   lists GSS_CORD_SWAY, ARBITERTIERS and FOUNDRY_CLONE_SYNC as SUSPECT, and counts a known real close as built
   (sanity probe that the instrument can see a positive).
4. **Zero is not ON.** A day with an empty `today.json`, or no claims while FOUNDRY committed, reads UNMEASURED.
5. **Token-blind.** `tracking.md` and a fixture `plan.md` from a tracking run pass the ops_watch token-talk rule
   (`ops_watch_rules.json` `token_talk.terms`) with zero hits; a planted token word is caught (the probe).
6. **Caps.** On a Wednesday fixture with the weekly run at 943k spent, the two tracking slots stay reserved, and an
   event run that would pass 2.0M waits with the existing alarm, without a second alarm per tick.
7. **plan_slip is edge-triggered.** A slip that stays crossed all day fires one event run; it fires again only after
   it cleared and re-crossed; it shares `event_runs_per_day`.
8. **No commit when nothing changed.** A tracking run that edits no ticket leaves `git log` unchanged and its
   `plan.md` says `## Ticket edits: none`.
9. **today.json schema.** The tracker refuses (UNMEASURED, with the reason) a plan item without a stopping point or
   an expected-by time, and an item whose `## verify` section is missing.

Findings filed as lessons with this design (not fixed here, design only): the role files `producer.md` and `operations.md` still
open with "NOT enabled / DISABLED" while the schedule has both `enabled: true`; the Producer's `_caps_why` says
"day 1.0M" while `daily_token_cap` is 2,000,000.

## 12. Open questions for the owner

1. **Count and times**: two gated check-ins at 12:00 and 18:00 (recommended), or always-on, or three?
2. **Slip alerts**: should a big slip wake the Conductor at once (an extra quick check), or wait for its 20:00 check
   (recommended: wait, since 18:00 is two hours before)?
3. **What "on schedule" counts**: built with a real commit (recommended; fast) or Arbiter-accepted (strict; lags by
   up to six hours while the Arbiter is advisory)?
