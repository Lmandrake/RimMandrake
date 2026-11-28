# BOUNDARY: a leave line that changes through the week (the line schedule), Design Version 0.1.0

Code: `src/RimMandrake/Utils/account_plan.py` (`parse_schedule`, `place_schedule`, `line_of_step`: the one function
that gives the leave line of a step at a moment; `rule_of` and `standing_line` call it), the command
`./acct line <account> --schedule "..."`, and the sweep `src/RimMandrake/Utils/account_plan_sweep.py` (`codex_week`, the
line-schedule regions). Item: `RIMMANDRAKE_SCHEDULE_LEAVE_LINES_BY_WEEKDAY_FLAT_NUMBER_TODAY`. The plan that this
extends: `design/specs/2026-11-24-account-plan-one-file/boundary.md`. The sweep that this extends:
`design/specs/2026-11-25-account-plan-sweep/boundary.md`. The owner's operating page: `ops_rules.md` beside this page.
Each promise has a check of its name in `src/RimMandrake/Utils/selftest_account_plan.py` (prefix `ls_`) or
`src/RimMandrake/Utils/selftest_account_plan_sweep.py`. Planted faults: `src/RimMandrake/Utils/account_plan_mutants.py`.

## Words

- The **leave line** of a step is the percent that is left on the account when the fleet leaves it (the owner's
  "preservation percent").
- A **line schedule** is a leave line with a different percent at different times of the account's week. A step that
  has no line schedule has one flat number, as before.
- The **account's week** runs from one reset of that account to the next: the interval (R - 7 days, R], with R the
  next reset that the meter reports.
- A **point** is a weekday, a Pacific time, a percent and the word `hold` or `ramp`.

## The form

The owner types the points in the order of the account's week, from the reset:

    ./acct line codex --schedule "Sat 23:59=40 hold; Tue 13:30=0 ramp" --why "..."

- Each point says the leave line up to its moment. `hold`: the line is this point's percent from the point before (or
  from the reset) up to this point. `ramp`: the line moves in a straight line from the point before (its percent, at
  its moment) to this point (this percent, at this moment).
- From the reset to the first point, the first point's percent applies. After the last point, the last point's percent
  applies until the reset.
- So the owner's example is: 40% from the reset through Saturday 11:59 PM, then a straight fall from 40% to 0% at the
  reset on Tuesday afternoon.
- The plan stores the text that was typed, in the step field `schedule`. The same write sets the step's `leave` to the
  highest percent of the schedule: that is the line that a pass uses when it cannot read the schedule (below).
- `./acct line codex 25` sets the flat number again and removes the schedule. `./acct undo` reverses either write.
  `--until-reset`, `--for` and `--until` give a temporary step with a schedule. `./acct step set NAME schedule="..."`
  and `./acct set steps.NAME.schedule="..."` are the same write.
- Day names: `mon` to `sun`, or the full names, any letter case. Times: `13:30`, `1:30pm`, `11:59 PM`. The word may be
  left out: it is then `hold`.

**The case that the brief's form got wrong.** The brief defined `hold` as "the percent stays until the next point" and
`ramp` as "a straight line from this point to the next point", and gave the owner's example as
`"Sat 23:59=40 hold; Tue 13:30=0 ramp"`. Under those words that string holds 40% from Saturday to Tuesday 1:30 PM and
then ramps to nothing: the last point has no next point. Under the words of this page the same string is exactly the
owner's sentence ("save 40% Wed through Sat, then drop to 0% by Tuesday afternoon"). So the word describes how the line
reaches its point, not how it leaves it. A `ramp` on the first point has no point before it and is refused, with the
repair.

### Where a point falls in the week (the pass computes this at each read)

1. The first point is placed at its first moment (its weekday and its Pacific clock) after R - 7 days - `SNAP_S`; a
   place before R - 7 days is moved to R - 7 days (the reset itself).
2. Each next point is placed at its first moment after the point before it.
3. A point placed after R but no more than `SNAP_S` after it is moved to R: "a point at the reset" survives a reset that
   moves by minutes, or by the hour of a daylight-saving change.
4. A point placed more than `SNAP_S` after R is **outside the account's week** (the reset came earlier than the
   schedule assumed). The pass drops it: a ramp towards it keeps its slope, so the line at the reset is where that ramp
   has got to. The status line and the reason say `outside the week` with the point and the hours.
5. A reset that comes later than the schedule assumed makes the last point's percent apply for longer: the line at
   each wall-clock moment is what the owner typed for that moment.

`./acct status`, `./acct plan` and `./acct forecast` print each point with its place as hours before the reset, so a
reader sees what the pass computes.

## ACCEPTS

- **a-schedule-text.** 1 to 14 points, separated by `;`, each `Day H:MM=PCT [hold|ramp]` (a `%` after the number may
  be typed). A Claude account's points are at least `numbers.floor_pct`; a meter account's points are 0 to 100.
- **a-reset.** The account's next reset as the meter reports it (`reading()["reset"]`), or a simulated reset (the week
  ahead, the sweep).

## DOES NOT SURVIVE (not promised)

- **a-reset-that-moves-by-days.** A reset that moves by more than `SNAP_S` is no longer the reset that the owner typed
  the weekdays against. The line still follows the typed weekdays (rule 4 and 5 above), and the output says so; whether
  that is still what he wants is his call (`ops_rules.md`, "after a reset moves").
- **a-schedule-for-jpl-genai.** JPL GenAI has no step and no meter that the plan reads; a schedule on it does nothing.
- **a-second-burner-that-the-plan-cannot-see.** The owner's own use of Codex or of a Claude account is a burn that the
  plan does not control. The plan keeps the line against the fleet only; the sweep measures what his use does
  (`ops_rules.md`).

## PROMISES (each one is owed a check of the same name)

### The form and the command

- **ls_a_schedule_is_set_in_one_line.** `./acct line codex --schedule "Sat 23:59=40 hold; Tue 13:30=0 ramp" --why X`
  writes one revision: the step keeps the text as typed in `schedule`, its `leave` is 40, the history line has the why,
  the output prints each point with its hours before the reset, and `./acct undo` gives the plan as it was.
- **ls_a_bad_schedule_is_refused_at_the_command.** Refused (exit 3, the plan file byte for byte as it was), each with
  its reason and repair: a percent under 0 or over 100; a Claude point under the floor; a weekday that does not exist;
  a time that does not exist; a point that cannot be read; no point; a `ramp` on the first point; two points in a row at
  the same moment; points that run past a week; with the reset measured, a point that is outside the account's week.
- **ls_a_flat_line_clears_the_schedule.** `./acct line codex 25` after a schedule leaves no `schedule` field and the
  flat line 25.

### The line of the moment (one function)

- **ls_hold_and_ramp_give_the_line_of_the_moment.** On the owner's example with the reset on Tuesday 1:30 PM: 40 on
  Wednesday, 40 at Saturday 11:59 PM, about 15.6 at Monday 1:30 PM (on the ramp), 0 at the reset; a first `hold` point
  later in the week gives its percent from the reset; after the last point its percent applies.
- **ls_a_point_at_the_reset_is_its_end.** With the reset at 1:25 PM, at 1:36 PM, and one hour later (daylight saving),
  the point `Tue 13:30` is the end of the week, and the line on Wednesday is still 40.
- **ls_a_point_past_the_reset_is_dropped_and_said.** With the reset a day earlier than the schedule assumed, the line at
  the reset is the ramp's value there (not 0 and not 40), and the line's note says `outside the week`.
- **ls_an_unreadable_schedule_uses_its_highest_percent.** A schedule text that a hand edit broke, or a reset that is not
  measured, gives the step's `leave` (the highest percent) and a note that starts `COULD NOT LOOK`; the plan file is not
  refused for it, and `./acct status` says it. The account is never free to burn under it.
- **ls_every_reader_gets_the_line_from_one_function.** On one plan with a Codex schedule and a Claude schedule, at two
  moments with different lines, each reader gives the line of that moment: `decide`, `week_ahead`, `can_use` (Codex),
  `burn_mode`, `legacy_view` (the actuator and `account_end`), `pool_pace` (the allocator), `rules_now` (the
  Dispatcher's priority), `temporary_line` (the allocator), `account_lines` (status), `ops_watch`'s runway,
  `codex_advice` (Codex's door; `codex_lane` asks it). No code outside `line_of_step` reads a step's `leave` to make a
  line (a scan of the source).
- **ls_a_schedule_replaces_the_reset_day_rule.** Inside the reset-day hours, an account whose step has a schedule keeps
  the schedule's line; a flat step keeps the reset-day rule as before.
- **ls_the_week_ahead_follows_the_schedule.** The week ahead erases at a reset the points above the schedule's line at
  that reset; a falling line makes an account a target in the week ahead before its reset; Burn Mode counts at risk
  against the line at the reset.

### The readers' output

- **ls_status_plan_forecast_show_the_schedule.** `./acct status`, `./acct plan` and `./acct forecast` each print the
  line now, the next change with its Pacific time, and every point with its hours before the reset; `./acct whatif --
  line codex --schedule "..."` shows the line before and after and writes nothing.

### The flat plan of today

- **ls_the_live_plan_replays_pass_for_pass.** Today's live plan (rev 4, steps with flat numbers only, copied into
  `src/RimMandrake/Utils/account_plan_replay.golden.json`) is decided over a simulated week (every 30 min, and every
  5 min near each line and reset), with the code before this change and with this code: each pass has the same act,
  target, line, warning line, level and drain; `can_use` for Codex, Burn Mode's states and the actuator's lines are the
  same. The golden file was written by the code before this change (`--write-golden`, commit 34121b95c6).

### The measures

- **ls_measures_count_the_reserve.** `./acct measures` gives, per account and week, the minutes that the level read
  under the leave line of that moment and the lowest gap (level less line), beside the points erased at each reset
  (against the line at that reset) and the switches.

## THE MEASURES (the sweep, per account and week; also `./acct measures` where marked)

- **reserve kept** (`under_line_min`, `lowest_gap`): the minutes in which the true level was under the leave line of
  that moment (the line that the pass computed), and the lowest of level less line. `./acct measures` computes the same
  from the MEASURED readings (each reading counts until the next one).
- **fleet under the line** (`fleet_under_pts`): the points that the fleet burned while the level was at or under the
  line of that moment. The owner's own use is not counted here.
- **points erased at the reset** (`erased`): at each reset, the level less the line one second before the reset (0 when
  under): the percent that was left and that no line asked to keep. `left_at_reset` is the whole level.
- **dark hours** (`dark_h`): the hours in which work waited (the fleet's demand was over 0) and no account of the plan
  could take a new run (the real gate refused on every account that the work could use). For Codex: the hours in which
  Codex jobs waited and `can_use codex` refused.
- **owner starved** (`owner_starved_min`): the minutes in which the owner burned and the level was 0.
- **switches**, and the runs that were alive at each switch (`runs_ended_by_switch`), as before.

## LIMITS

- `SNAP_S` = 2 h (`account_plan.py`): not a limit (it ends no work); a tolerance. Danger of a small one: a reset that
  moves by minutes (the meter moves it by up to a minute between readings, `account_end.RESET_JITTER_S` 15 min), or by
  the hour of a daylight-saving change (a reset that is fixed in UTC moves one hour in Pacific time), puts the point
  `Tue 13:30` at the start of the week and the schedule reads backwards. Danger of a large one: a point meant hours
  after the reset is read as at the reset. 2 h is the daylight-saving hour plus the jitter, with margin.
- `MAX_POINTS` = 14 (`account_plan.py`): two points a day. Danger: a list that nobody can read in one status line.
  Ends no work: the command refuses it with the repair.

Later lists beside this page: `polish.md` (none yet).
