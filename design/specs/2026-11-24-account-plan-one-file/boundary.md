# BOUNDARY: the account plan as one file, commanded in one line, Design Version 0.1.0

Code: `src/RimMandrake/Utils/account_plan.py` (the plan file, the decision, the forecast, Burn Mode, the measures, the
commands, the timed pass), `src/RimMandrake/Utils/account_plan_replay.py` (both engines over the recorded readings),
`acct` (the one-line door), `src/RimMandrake/Utils/account_plan.seed.json` (the numbers of a first plan only).
Design: `design.md` beside this page. Item: `RIMMANDRAKE_DESIGN_ACCOUNT_PLAN_ONE_FILE_COMMANDED_IN_ONE_LINE`.
Each promise has a check of its name in `src/RimMandrake/Utils/selftest_account_plan.py`. The planted faults:
`src/RimMandrake/Utils/account_plan_mutants.py`.

## ACCEPTS (the only inputs this is built for)

- **the-plan-file.** `plan.json` of schema 1 in `$RM_ACCOUNT_PLAN_DIR` (default
  `~/.local/state/rimmandrake/account_plan`), written only by this tool.
- **the-meter.** `account_usage.read_now()` rows, the MEASURED lines of its `series.jsonl`, `read_codex_points()` and
  `read_genai_status()`. No other reader of a level.
- **the-live-account.** `account_live` (the switcher's status), and the switcher's own `log.jsonl` for past switches.
- **the-live-runs.** The live `rm-detached-*` units, or None when systemd cannot be read.
- **the-old-actuator.** `switching_plan._check` and `account_end.py`, unchanged.
- **a-command-line.** One `./acct` command, from the owner, the Conductor or a program.

## DOES NOT SURVIVE (not promised)

- **a-hand-edit-of-the-plan-file.** A plan that a hand edit broke is refused at the next read, and every pass then
  acts on nothing and says so. The repair is `./acct undo` (the last good plan is in the history).
- **accounts-of-unequal-size.** The week ahead counts one point of each Claude account as the same work.
- **a-burn-that-changes.** The week ahead uses one burn rate (the last 24 h). A forecast is not a promise of the week.
- **a-small-rescue-on-a-fleet-that-is-never-idle.** A rescue worth less than a switch plus `rescue.drain_h` hours of
  burn waits for a pass with no live run. On a fleet that always has one, those points are erased, and the status
  line said so each pass. Measured 2026-11-18 to 11-24: 11.5% of passes had no live run; the longest stretch with one
  was 50.8 h.
- **a-run-that-outlives-the-rescue-drain.** After `rescue.drain_h` hours of drain the switch goes, and it stops the
  runs that are still live (the old actuator's rule of 2026-11-20). 95 of 100 runs end inside 2 h.
- **many-accounts.** The week ahead tries each account that can take over at each finish. It is built for the three
  Claude accounts of today; with more than about five it gets slow.
- **a-switch-that-neither-log-names.** A switch made by copying credentials by hand, outside `claude-account`.
- **a-lost-history-file.** Undo then has nothing to read, and answers NONE.
- **two-machines.** The file is this machine's. Another machine has its own plan.

## PROMISES (each one is owed a check of the same name)

### The decision

- **live_account_stays_until_its_own_line.** With the live account above its warning line and no step condition that
  ends it, the decision is never a switch because of the step order, whatever the order and the other levels.
- **order_only_answers_which_account_is_next.** When the live account is finished and the burn is unknown, the next
  account is the first in step order that can take over. A change of order with the live account unfinished changes
  no act.
- **no_start_is_refused_for_a_preference.** The decision is `soft` (the state that refuses new runs) only when the
  live account is at or under its own warning line, or its level cannot be confirmed near that line (below). A small
  rescue, a request, a reset that is near and the zone above the warning line all read `normal`.
- **a_rescue_switch_needs_points_worth_a_switch.** The live account is left before its line only when the week ahead
  of that switch costs less than the week ahead of staying by at least `switch_cost_pts`, each switch counted.
- **a_rescue_switch_waits_for_no_live_run.** With a run live (unreadable runs count as live), a rescue is a switch
  only when it betters the week ahead by `switch_cost_pts` plus the work that a wait of `rescue.drain_h` hours delays
  (the burn rate times those hours). The old actuator then refuses new starts while the live runs finish, for at most
  `rescue.drain_h` hours, and the reason line says so. A smaller rescue reads `normal`, refuses no start, and names the
  points and the command that goes at once. With `rescue.drain_h` null, a rescue goes only with no run live.
- **a_rescue_drain_in_flight_goes_on.** A drain that the old actuator has started for a rescue goes on while the rescue
  still betters the week ahead by `switch_cost_pts`. It ends when the rescue is worth less than a switch.
- **an_unknown_burn_never_causes_a_switch.** With no measured burn rate there is no rescue switch, and the next
  account is by step order.
- **a_hand_switch_is_respected.** When the last switch in the switcher's log was not this tool's, no rescue switch
  leaves that account. Nor when that switch is the one that a `switch` command asked for. A pin does the same until
  its end.
- **the_reason_is_one_checkable_line.** Each decision carries one line with the live account, its level and line,
  the next account, and the erased points and switches of the choice taken and of the best other choice.
- **the_forecast_is_the_pick.** `forecast` and the decision call the same function: the first target of the week
  ahead is the account that the decision keeps or switches to.
- **no_marker_decides.** With the same plan and readings, the decision is the same whatever marker files exist. Only
  an act in flight changes an act: a `pending` marker under 40 min old (a switcher call), a `failed` one, and the
  actuator's notice of a rescue drain (`a_rescue_drain_in_flight_goes_on`).
- **an_account_left_at_its_line_is_no_target.** An account at or under its entry line (its step's `warn` leeway
  counted) is never a switch target. An account whose step has ended (`until` true) is a target only where the live
  account is at its own line and no other account can take over.
- **a_refilled_account_is_a_target_at_once.** The same account, read above its entry line after its reset, is a
  target at the next pass, with no command.
- **unknown_never_gives_permission.** A `when` condition that is unknown keeps its step not alive; an `until`
  condition that is unknown does not end a step; a level that is not MEASURED and fresh makes no account a target.
- **a_level_not_confirmed_near_the_line_refuses_starts.** Within `fresh.near_pct` of its warning line, a level that is
  still older than `fresh.max_age_min` after a poll reads `soft`: nobody can say that the account is above its line.
  Far from the line an old reading refuses nothing.
- **an_account_outside_the_plan_is_left_alone.** When the live account is no account of the plan, the decision is
  `normal`: no switch, no stop, no refusal. The reason names the repair. An account of the plan that no step uses now
  (Steve's account past its window) is left when its live runs end.
- **the_last_account_waits_at_its_wait_floor.** With no account that can take over, the live account's line is the
  wait floor, and the decision at that line is the old actuator's stop.

### The plan file and the commands

- **one_file_binds_at_the_next_read.** A write changes the next decision of another process with no commit, publish
  or pull, and the decision reads no number from `switching_plan.json`, a skill or a constant in the code.
- **a_step_that_is_not_alive_says_so.** A write that adds a step which gives no rule now (its reset is not measured,
  its `when` is false or unknown, now is outside its life) is done, and its first line says NOT ALIVE NOW with the
  cause.
- **a_bad_write_keeps_the_old_plan.** A write that fails validation exits 3, names its repair, and leaves the file
  byte for byte as it was.
- **two_writers_lose_no_change.** Two writes at once both land, or one is refused by name; neither is lost in silence.
- **every_write_has_an_undo.** Each write prints its undo, and that undo restores the plan as it was before.
- **a_write_is_never_refused_for_a_missing_flag.** A write with no `--why` and no owner flag is done, and its history
  line says that no reason was given. `--owner-said` records his words as typed.
- **a_hold_needs_an_end_and_ends_by_itself.** A hold with no end is refused with the repair; after its end a pass acts
  again with no command.
- **a_request_is_done_by_the_switchers_log.** `switch A` is decided once: after the switcher's log shows a switch to A
  written after the request, the request causes no further switch. An ended request causes none.
- **whatif_writes_nothing.** `whatif` shows the decision and the week ahead of the changed copy and leaves the plan
  file, the history and the published files as they were.
- **the_four_answers_stay_apart.** A level that could not be read prints UNMEASURED with its cause and makes the
  command exit 2 where the answer needs it; a measured zero prints 0 and exits 0; nothing to list exits 5 with NONE;
  a write that broke exits 4.
- **every_account_is_listed_as_left.** `status` and `readings` have one line for system, lukas, steven, codex and
  jpl-genai: what is left, the reset in Pacific time, the age; never what is used; an absent one says so.
- **status_reads_no_slow_source.** `status`, `next`, `plan`, `readings`, `forecast` and `whatif` run no poll, no model
  and no Codex reader, and answer in under a second on a full plan.
- **the_tool_never_touches_a_credential.** The code opens no credential file and calls the switcher only for `status`
  (and, in `tick`, through the old actuator).

### Burn Mode and the measures

- **burn_mode_enters_on_measured_allowance_at_risk.** `on` needs a measured level, reset and burn, the reset inside
  the window, and points at risk at or over the minimum. An unknown burn reads `unmeasured`, never `on`.
- **burn_mode_never_counts_under_a_leave_line.** The target burn is computed on the points above the leave line in
  force. Codex at 30% with a 25% line and no reset day has 5 usable points, not 30.
- **burn_mode_does_not_raise_on_a_loaded_machine.** Over the load number, `raise_ok` is false and the reason names the
  load.
- **burn_mode_ends_at_the_reset.** After the reset passes, the state is `off` with no command.
- **the_reset_day_rule_is_plan_data.** Inside the reset-day hours, Codex's line is 0 and a Claude account's line is
  its floor, for the accounts that the plan lists; Steve's account keeps its line.
- **measures_count_erased_points_and_switches.** `measures` gives, per account and week, the points above the line at
  the reset from the reader's series, and the switches of the week from the switcher's log, and the live runs at each
  switch that this plan decided, from its own log (a pass whose runs could not be read is counted apart). A week with
  no reading before its reset reads UNMEASURED, not 0.

### The old actuator, shadow and replay

- **tick_drives_the_old_actuator.** `tick` makes the switch that the decision names through `switching_plan._check`
  (arm, use, disarm), and the account-end sequence at the warning line is the old one: the live level is read again
  each `poll_min`, and an account confirmed by a fresh reading beats a stop. An account left only because no step uses
  it now, above its line, waits for a fresh reading of the next account; the fleet is not stopped for that.
- **the_timer_runs_the_driver_that_the_plan_names.** `./acct pass` is what the timer runs. With `driver` old (the
  value of a new plan file) the old engine runs as it is, and this tool's pick is logged beside it. With `driver` new
  this plan decides. `./acct driver new` and its undo are each one command. With a plan file that is missing or
  refused, the old engine runs and the pass says why: the fleet is never left with no engine.
- **shadow_acts_on_nothing.** `tick --shadow` calls no switcher verb but `status`, writes no notice and no marker, and
  logs both picks.
- **a_hold_makes_the_pass_passive.** While a hold stands (or a hand-made HOLD file), `tick` calls no switcher verb.
- **shadow_drain_is_not_the_plan_tools.** The drain, the orders and the pause are `switching_plan` and `account_end`
  code; `account_plan.py` defines none of them.
- **replay_names_each_difference.** The replay gives each pass where the two engines differ a cause from a fixed
  list, or the word UNEXPLAINED; a count of zero unexplained is printed with the count of passes compared.

### The census (each row is one command)

- **census_lent_account_window_and_leave_line.** Row 1.
- **census_fixed_priority_order.** Row 2: `order` sets which account is next.
- **census_set_floor_and_leave_line.** Row 3.
- **census_hold_with_why_and_end.** Rows 4 and 8.
- **census_one_week_allowance_ends_at_reset.** Row 5.
- **census_leave_line_relative_to_entry_level.** Row 6.
- **census_pin_account_now_plan_does_not_fight.** Row 7.
- **census_temporary_order_and_line_until_reset.** Row 9.
- **census_line_by_time_of_day.** Row 10.
- **census_switch_now_when_no_run_is_live.** Rows 11, 12 and 16.
- **census_use_until_pct_then_next.** Row 13.
- **census_reorder_and_lower_line_until_reset.** Row 15.
- **census_no_rule_lives_in_prose.** Row 17: the plan has no evening share, and `plan` prints that as data.
- **census_set_warn_and_emergency_numbers.** Row 18.
- **census_refill_is_seen_from_the_meter_no_marker.** Row 19.
- **census_codex_leave_line_in_the_same_plan.** Row 20.
- **status_shows_pool_pace_not_sets_it.** Row 21: the tool prints the burn and the target and calls no allocator write.

### Today's faults, 2026-11-24 (each is a check)

- **fault_stale_marker_kept_a_refilled_account_out.** Same check as `a_refilled_account_is_a_target_at_once`, with
  the 11-21 marker file present.
- **fault_forecast_disagreed_with_the_pick.** Same check as `the_forecast_is_the_pick`, with marker files present.
- **fault_preference_switch_drained_at_eighteen_percent.** lukas live at 18%, steven first in the order at 97%, runs
  live: the decision is `normal`, no notice refuses a start.
- **fault_plan_change_needed_edit_publish_pull.** One command changes the order; the next decision of a process in
  another working directory follows it.
- **fault_hand_hold_six_seconds_before_a_pass.** `hold` and `whatif` answer in under a second, and a hold written while
  a pass runs is seen before the pass acts.
- **fault_stop_and_undo_crossed.** A `switch` request and its `undo` leave one plan, one history line each, and no act
  that follows a withdrawn request.

## LIMITS (each number is in the plan file; `./acct set numbers.<key>=<value>` changes it)

- `floor_pct` = 1, `last_account_floor_pct` = 2, and the fourteen `account_end` numbers, `fresh`, `stale_min`:
  machine-safety brakes, carried from `switching_plan.json`. Danger and evidence:
  `design/specs/2026-11-24-account-end/boundary.md` LIMITS.
- `entry_margin_pct` = 2. Danger: a switch that lands on an account inside its own warning zone, and is warned at
  once. Evidence: the old plan's `soft_margin_pct`, his card of 2026-10-28 ("Soft line, then hard stop").
- `switch_cost_pts` = 3: what one switch is worth, in points of a week. Not a limit: a weight. Danger of a low one:
  a switch for a point or two, and every window restarts. Evidence: 2026-11-18, one hand switch with 9 live runs cost
  4.73M weighted tokens in missed caches; a point of a week in weighted tokens is UNMEASURED, so 3 is a delegated
  choice, shown in every reason line and changed by one command.
- `rescue.drain_h` = 2: the longest that a rescue refuses new starts while live runs finish, and the measure of the
  work that such a wait delays. Danger without it: on a fleet that is never idle, a reset erases allowance that a
  switch would have used (modelled over 2026-11-10 to 11-24 with no idle moment: 43 points of Steve's account;
  measured: a stretch of 50.8 h with a run always live). Danger of a long one: starts refused for hours behind one
  run. Evidence for 2 h: 724 detached runs measured 2026-11-20 ran p50 24 min, p95 122 min. `null` turns the drain
  off: then a rescue goes only at a pass with no live run, and no start is ever refused for one. This number goes
  against the letter of "new runs are refused only at the warning line" (the brief of 2026-11-24) and with "allowance
  that a reset would erase is a reason to act, weighed against the cost of a switch"; the Conductor is told.
- `forecast.burn_window_h` = 24, `forecast.step_min` = 30. Not limits: the forecast's sample. Danger of a short
  window: one busy hour read as the week's rate.
- `burn_mode.window_h` = 24. His words: "on the day of an account reset".
- `burn_mode.min_at_risk_pts` = 5. Danger: Burn Mode on for a point that one run spends anyway. Evidence: the meter
  reads whole points, and a burn rate from 45 min of readings is good to about 2 points over a day.
- `burn_mode.max_load_per_core` = 1.5. Danger: an overloaded machine makes tests flaky. Evidence: 2026-11-24, load 41
  to 64 on 14 cores (2.9 to 4.6 a core) with flaky tests; 1.5 is half the lowest such reading, a delegated choice.
- `request_default_h` = 24, `hold` (no default: an end is asked). Danger: a request or a brake that outlives its
  reason (census rows 4, 5, 8).
- The pass deadlines (600 s a switcher call, 420 s a poll, the 40-min `pending` marker) are the old actuator's hang
  guards and stay in its code.

Later lists beside this page: `polish.md`.
