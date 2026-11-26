# BOUNDARY: the account plan as one file, commanded in one line, Design Version 0.1.0

Code: `src/RimMandrake/Utils/account_plan.py` (the plan file, the decision, the forecast, Burn Mode, the measures, the
gate, the notice of each machine, the commands, the timed pass), `src/RimMandrake/Utils/account_plan_machines.py` (the
ssh transport to another machine), `src/RimMandrake/Utils/account_plan_replay.py` (both engines over the recorded
readings), `acct` (the one-line door), `src/RimMandrake/Utils/account_plan.seed.json` (the numbers of a first plan only).
Readers: `src/RimMandrake/rimflow/detached_helper.py` (`drain_refusal`, the launcher's gate),
`src/RimMandrake/Utils/codex_advice.py` (Codex's door), `src/RimMandrake/Utils/slot_allocator.py` (Burn Mode, the pool,
the Codex advice line), `src/RimMandrake/Utils/ops_watch.py` (the fleet runway), `src/RimMandrake/rimflow/account_pick.py`
(the priority).
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
- **the-old-actuator.** `switching_plan._check` and `account_end.py`. Its notice (`notice.json`, built by
  `switching_plan.notice_of`) is what each machine's launch gate and hooks read.
- **another-machine.** A machine that the plan lists (`./acct machine add <name> --ssh <ssh name>`): reachable by ssh
  with no password, with the switcher (`claude-account --json status`) and the folder
  `/mnt/d/ClaudeWork/rimmandrake/switching_plan`.
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
  runs that are still live (the old actuator's rule of 2026-11-20). 95 of 100 runs end inside 2 h. The same bound ends
  a drain at the line of an account with no emergency step (an_account_end_drain_ends_at_its_bound): such a run is
  stopped, and the account goes under its line by the burn of those hours.
- **many-accounts.** The week ahead tries each account that can take over at each finish. It is built for the three
  Claude accounts of today; with more than about five it gets slow.
- **a-switch-that-neither-log-names.** A switch made by copying credentials by hand, outside `claude-account`.
- **a-lost-history-file.** Undo then has nothing to read, and answers NONE.
- **the-old-engine-file.** `switching_plan.py` stays: its actuator half (`_check`, the notice, the markers, the fleet
  stop) is what the timed pass drives, and its decision half is the fallback when `./acct driver` reads `old` or the
  plan file is refused. `switching_plan.json` carries a tombstone that says so.
- **a-run-on-another-machine-deaf-past-its-stop-deadline.** A run on a listed machine that is still live
  `machine_bound_s` after its save order gets `pipe stop --write-now` there. A run that makes no tool call inside the
  stop's deadline (`control.WRITE_NOW_DEADLINE_S`) is killed by the stop's escalation, or closed by the switch. A
  killed run is not carried on (`left_open_continue` never continues a killed run); its PROGRESS notes stay on its
  item. On 2026-11-26 the waiting run made one tool call each 55 min.
- **a-listed-machine-whose-code-lacks-the-acts.** The save order, the stop and the kick run on that machine with its own
  code (`~/rm/bench`). A clone there without `control.order_runs`, `control.stop` or `left_open_continue.kick_waiting`
  answers no `REMOTE_STEP` line: the order and the stop are tried again each pass, and the machine is not switched while
  no stop is written. The pass's line says so (`probe_machine` reads it).
- **a-machine-that-the-plan-does-not-list.** It has no notice and no gate from here. It is as it was before.
- **the-deciding-machine-off.** While this machine is off or its pass is dead, each listed machine refuses new runs
  (could not look) from 20 min after its last notice, until a notice arrives.
- **clocks-that-differ-by-minutes.** A listed machine reads the age of its notice by its own clock.
- **a-plan-file-on-two-machines.** One machine holds the plan file. A second plan file on a listed machine makes that
  machine decide for itself.

## PROMISES (each one is owed a check of the same name)

### The decision

- **live_account_stays_until_its_own_line.** With the live account above its line and no step condition that ends
  it, the decision is never a switch because of the step order, whatever the order and the other levels. The live
  account is finished at its line, not at its warning line.
- **the_account_burns_to_its_line.** Between the warning line and the line, with or without a live run and with
  another account that can take over, the decision is no switch and no stop and refuses no start; it carries
  `warning`, and the old actuator warns each live run (save a note, publish, keep working). At the line it switches.
- **order_only_answers_which_account_is_next.** When the live account is finished and the burn is unknown, the next
  account is the first in step order that can take over. A change of order with the live account unfinished changes
  no act.
- **no_start_is_refused_for_a_preference.** New runs are refused only at the live account's own line (a drain that
  waits for its runs), or when its level cannot be confirmed near its warning line (below). A small rescue, a request,
  a reset that is near and the warning zone all read `normal`.
- **a_rescue_switch_needs_points_worth_a_switch.** The live account is left before its line only when the week ahead
  of that switch costs less than the week ahead of staying by at least `switch_cost_pts`, each switch counted.
- **a_rescue_switch_waits_for_no_live_run.** With a run live (unreadable runs count as live), a rescue is a switch
  only when it betters the week ahead by `switch_cost_pts` plus the work that a wait of `rescue.drain_h` hours delays
  (the burn rate times those hours). The old actuator then refuses new starts while the live runs finish, for at most
  `rescue.drain_h` hours, and the reason line says so. A smaller rescue reads `normal`, refuses no start, and names the
  points and the command that goes at once. With `rescue.drain_h` null, a rescue goes only with no run live.
- **an_account_end_drain_ends_at_its_bound.** On an account with no emergency step (a line over
  `account_end.emergency_max_line`), a drain off the live account that still has live runs (or runs that cannot be
  read) `rescue.drain_h` hours after it began ends: the switch, or the stop when no account can take over, goes then
  and stops those runs. The drain began at its save order (at the line), or, for a drain with no save order (an account
  past its window), at the `since` of its drain notice. With `rescue.drain_h` null the drain waits for its runs. An account with an emergency step keeps
  its own end (the emergency order at `emergency_pct`). Found by the sweep (`design/specs/2026-11-25-account-plan-sweep/`).
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
- **a_stopped_fleet_switches_when_an_account_refills.** A fleet stopped on an account that it does not start again
  (the level is inside its warning zone plus `entry_margin_pct`) is finished there once another account can take over
  (a reset refilled it): the decision is the switch to it, behind the same fresh-reading guard as every switch. Found by
  the sweep (`design/specs/2026-11-25-account-plan-sweep/`).
- **a_failed_switch_off_an_account_above_its_line_stops_nothing.** A switch that failed off an account that no step uses
  now and that is above its line is tried again; neither the decision nor the actuator's brake stops the fleet for it.
  The brake (a stop, and the switch tried again from the stopped fleet) stays for an account at or under its line.
  Found by the sweep.
- **unknown_never_gives_permission.** A `when` condition that is unknown keeps its step not alive; an `until`
  condition that is unknown does not end a step; a level that is not MEASURED and fresh makes no account a target.
- **a_level_not_confirmed_near_the_line_refuses_starts.** Within `fresh.near_pct` of its warning line, a level that is
  still older than `fresh.max_age_min` after a poll reads `soft`: nobody can say that the account is above its line.
  Far from the line an old reading refuses nothing.
- **a_level_not_read_is_no_pending_switch.** A `soft` decision only because the live level is not read (its reset has
  passed and no reading came since, or a stale reading near its warning line after a poll) is no pending switch. Its
  notice reads `switch_pending` false and says that no new run starts until the level is read and that live runs go
  on; on another machine it still refuses a new run, with the same words. A notice of a real drain, or of a switch due
  before its poll, reads `switch_pending` true. The checkpoint hook (`.claude/hooks/switch_checkpoint_signal.py`) tells
  a run or a window that a switch is pending only on a notice that reads it. On another machine a last level at
  its line that is not read now is no level at the line: its notice carries no save order (found by the sweep, with no
  account readable and the account's last reading at its 2% wait floor).
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

### The gate, the machines and the readers

- **can_use_is_the_one_answer_for_a_new_run.** `./acct can-use` (no account: the live account of this machine) is the
  one question that a launcher asks. NO when the account is not live here; when the actuator's fresh notice refuses (a
  stop, a drain); when the decision that the last pass published for this plan revision refuses new runs. With no
  such pass inside 20 min the plan decides at once on the last readings. The warning zone is yes. An unknown live
  account is exit 2, and on the deciding machine a launcher then refuses nothing. The launcher's refusal carries the
  mark `ACCOUNT GATE`, which the pipeline reads as a wait and no fault.
- **a_carried_run_goes_until_the_line.** A continuation of a live run, or a resume of its session, passes a drain that
  is no account end, by the notice and by the published decision. At the line and under a stop it is refused.
- **each_machine_on_the_account_gets_its_decision.** Each timed pass (new driver, shadow, hold) asks each listed machine
  which account it is on, decides for that account with the same readings and rules, and writes the result there as
  its notice: nothing refused, the warning text, or no new run (at the line: save and publish). An account that could
  not be read is could not look and no new run. `status` has one line for each machine.
- **a_machine_at_its_end_is_switched_when_its_runs_end.** A machine whose notice says its account is at its end is
  switched by the pass to the plan's next account (`claude-account use NEXT --confirm NAME` over ssh), when it lists
  no live helper run, or after the stop of a run that does not end (a_machine_at_its_end_stops_a_run_that_does_not_end);
  runs that cannot be read switch nothing and the pass says so. The same switch is
  not asked again for `SWITCH_RETRY_S` (30 min). A machine whose account no step uses now (Steve's account past its
  window) is at its end too, above its line: its notice drains, and it is switched the same way when its runs end. Any
  other machine above its line, and a machine whose level is not read, is never switched.
- **a_machine_at_its_end_orders_its_runs_to_save.** At the end of its account, with runs live, each live run of a listed
  machine (its control store's detached and role runs, and the units that it lists) gets the save order of the line once
  (`control.order_runs` there, mode at_easy_spot, the words of `account_end.save_text` and the bound). A run that ends
  in time is not stopped: the switch waits for it, then goes. Runs that could not be read get no order, no stop and no
  switch, and the line says COULD NOT LOOK. A machine whose account is not at its end gets no order, no stop and no
  switch. Each pass whose notice to a machine refuses nothing runs `left_open_continue.kick_waiting` there, so a
  continuation that waited for that machine's switch starts (no timer on a listed machine runs it).
- **a_machine_at_its_end_stops_a_run_that_does_not_end.** A run still live `machine_bound_s` after the save order
  (`rescue.drain_h`, at least ten times `save_need_min`; 0 at the emergency step of an account with one) gets `pipe stop
  UNIT --write-now` on its machine: its trial is voided, its hook says the order, the stop kills it at its deadline,
  and a run that saved a LEFT OPEN note is carried on by `left_open_continue`. The switch goes when the runs end, or
  `stop_grace_s()` after the stop (the pause `pause_max_s` at the emergency step), once. A stop that did not reach the
  machine is tried again at each pass, and nothing is switched while no stop is written. The machine's record keeps the
  order, the stop and the switch, and `status` prints the pass's last step on the machine's line. The case of
  2026-11-26 (steven at its 52% line from 3:13 AM PST, one run that waited, the hand switch at 7:10 AM) is stopped at
  5:13 AM and switched at 5:23 AM.
- **a_push_that_fails_leaves_the_pass_whole.** A machine that cannot be reached is said by name in the pass's log; the
  pass and the other machines go on; a notice that did not arrive is not kept as that machine's last.
- **a_following_machine_that_cannot_look_refuses.** A machine that got a notice from the deciding machine starts no
  new run when that notice is missing, unreadable or older than 20 min, and says COULD NOT LOOK with the name of the
  deciding machine. A machine that follows nothing and holds no plan refuses nothing.
- **readers_take_the_rules_through_one_door.** `old_shape` gives a program that calls an old-engine function (the
  allocator's pool, the fleet runway, the Dispatcher's priority) the order and the lines of the plan file while it
  drives, and `switching_plan.json` while the old engine drives or the plan file is refused; it says which.
- **the_allocator_raises_its_pace_to_the_target_burn.** `slot_allocator.py` reads `burn_mode.json` and raises its pace to
  `target_burn_pct_h` while Burn Mode is on for its burn account and `raise_ok` is true; never past it, never from a
  record older than 20 min, and it says why when it does not raise.
- **codex_door_asks_the_plan.** `codex_advice.gate` (every direct Codex caller) refuses a job, exit 4, when the plan
  answers NO for Codex, required or not; a plan or meter that cannot be read is COULD NOT LOOK and the job is sent.

- **status_and_help_are_the_operators_page.** `./acct status` prints the end of the live account with the numbers and
  names in force: the warning zone, the line, the emergency percent, the next account (only one that can take over
  now; else that the fleet stops and which reset is first), each listed machine on the same account with its hand
  switch, and the hand commands. `./acct --help` shows each command an operator types, what the timed pass does by
  itself, and what to do when it looks wrong; it states no percent and no account name. The skill
  `skills/rimflow-operations` sends the operator to those two and holds no rule of its own.

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
  (arm, use, disarm), and the account-end sequence is the old actuator's: the warning at the warning line, the steps
  at the line, the live level read again each `poll_min`, and an account confirmed by a fresh reading beats a stop. An account left only because no step uses
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

- `NOTICE_FRESH_S` = 20 min (`account_plan.py`), `BURN_MODE_FRESH_S` = 20 min (`slot_allocator.py`): how old a record of
  the timed pass may be. Danger of none: a record that outlived its pass (the timer stopped) holds every launch, or
  raises the pace for a reset that has passed. Evidence: the pass writes each 5 min, so 20 min is four missed passes;
  a stopped engine's HOLD file held launches on 2026-11-05. On a listed machine the same age is the line for could
  not look.
- `SSH_DEADLINE_S` = 120 s and `ACCOUNT_DEADLINE_S` = 180 s (`account_plan_machines.py`): hang guards on the two ssh
  calls of the pass for each listed machine. Danger: a hung ssh holds the pass and the next pass waits on its lock.
  Measured 2026-11-24 on stevedesktop-wsl: three pushes took 0.3 to 0.6 s; four reads of that machine's account took
  4.0 to 16.8 s. A read that is cut is could not look, and that machine then gets a notice that refuses new runs.

- `machine_bound_s` (`account_plan.py`): from the save order to the write-now stop of a run on a listed machine,
  `rescue.drain_h` (2 h), never under ten times `save_need_min` (10 min: 100 min). Danger: a listed machine that refuses
  every launch while one run waits (2026-11-26: over 3 h, five tickets with 3 to 6 refused launches each). Measured need:
  17 of 19 save orders heard on 2026-11-24 ended p50 5.0, p90 9.5, max 13.8 min after the order. The same bound as this
  machine's own drain at an account with no emergency step.
- `stop_grace_s()` = twice `control.WRITE_NOW_DEADLINE_S` (300 s, the kill deadline of `pipe stop --write-now`, which
  the stop on the other machine uses): the wait from the stop to the switch. Danger: a run that the stop did not end
  keeps the machine on an ended account; the switch then closes it. Evidence: 3 of 15 write-now stops reached their run
  and were escalated, longest 599 s (control.db, 14 days to 2026-11-24).
- The remote acts of the pass (`remote_step`: order, stop, kick, probe) use `SSH_DEADLINE_S`, a hang guard. Measured
  2026-11-26 on stevedesktop-wsl: a probe took 1.9 s.

Later lists beside this page: `polish.md`.
