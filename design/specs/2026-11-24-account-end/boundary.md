# BOUNDARY: the end of an account: warn, save, pause, switch, sized from the burn rate, Design Version 0.1.0

Code: `src/RimMandrake/Utils/account_end.py` (the numbers, the two orders, the records), `switching_plan.py` (`decide`,
`_check`, `check`), `src/RimMandrake/rimflow/control.py` (`order_runs`, `withdraw_orders`),
`src/RimMandrake/rimflow/detached_helper.py` (`drain_refusal`), `src/RimMandrake/rimflow/left_open_continue.py`
(`account_end_wait`, `kick_waiting`). Numbers: `switching_plan.json` `account_end`.
Item: `RIMMANDRAKE_BUILD_ACCOUNT_END_WARN_SAVE_PAUSE_SWITCH_SIZED_BY_BURN`, written 2026-11-24.
Each promise has a check of its name in `src/RimMandrake/Utils/selftest_account_end.py`.

The owner, 2026-11-24 11:05 to 11:15 AM PST: "At 2% no new work is started and "wrap it up cleanly and safely save your
work" is sent to everyone. At 1% "emergency: record your state immediately and prepare for termination." Give it a
beat... don't just kill at 1%. After a brief pause that has <10% chance of reaching 0% account, initiate the switch.
Don't bother manually killing everything, it will happen all by itself". By card, "Sized from the burn rate": "that may
also initiate the "no new work / save now" warning up at 3% as well if the burn is going crazy fast. Scale both 3/2%
(initiate saves) warning and the time-constant post 1% based on load. If the reading is believed to be stale, default
to safe values. TELL THE PROCESSES these numbers. Estimate how long they have to complete their saves."

## ACCEPTS (the only inputs this is built for)

- **a-meter.** `account_usage.read_now()` records, and the MEASURED lines of `series.jsonl`.
- **live-runs.** The live `rm-detached-*` units, or None when systemd cannot be read. The wait and the emergency read
  these. The orders go also to every other started run of family `detached` or `role` in the control store.
- **a-run-with-the-stop-hook.** A run started by `detached_helper` or `role_launch` (its PostToolUse hook reads the
  control store's `stops` table), whatever the age of the code in its clone.

## DOES NOT SURVIVE (not promised)

- **a-run-inside-one-long-tool-call.** The hook speaks after a tool call ends. A run inside a 50-minute command hears
  nothing until the command ends (2 of 19 orders on record were never heard).
- **an-interactive-window.** A window has no stop hook. The notice, the Conductor log and the ledger event are what it
  reads. The switch closes it and relaunches the Fleet.
- **a-deaf-run-on-a-kept-account.** Steven's account gets no emergency step, so a run that never ends keeps the machine
  on it. One run spends about 0.3 points an hour (4 points an hour over about 12 runs, 2026-11-24).
- **a-jump-over-the-warning.** A burn over about 0.5% a minute can pass 3% and 1% between two meter reads. Then the
  emergency order is the first order that a run gets.
- **a-crash-between-an-order-and-its-record.** The order is sent once more.

## PROMISES (each one is owed a check of the same name)

- **the-warning-fires-at-two-at-an-ordinary-burn.** For a floor account (line 1 or 2) the warning line is 2% while the
  time from 2% to the emergency line (1%) is at least `save_need_min`.
- **the-warning-fires-at-three-at-a-fast-burn.** When that time is shorter, the warning line is 3%. For any other
  account the warning line is its own line, and one point more at a fast burn.
- **the-order-tells-the-numbers.** Each order says the percent left, the burn rate, and the minutes to the emergency
  step (the warning) or the seconds of the pause (the emergency). It names the account end as the cause, and says how
  the run's work is carried on.
- **no-new-work-after-the-warning.** The notice then reads soft, `drain` true and `account_end` true, and
  `drain_refusal` refuses a new run, a continuation and a resume alike. With `account_end` false, a continuation and a
  resume go as before.
- **the-switch-goes-when-the-last-run-ends.** After the warning, with no live run, the switch goes at once, above 1%.
- **the-warning-is-latched.** A burn that slows after the warning does not take the warning back. A reading above the
  warning line plus `clear_pct` (a reset) does, and its undelivered orders are withdrawn.
- **the-emergency-orders-pauses-then-switches.** At 1% or less with a run live: the order goes to every live run, the
  machine waits the computed pause (less when the last run ends sooner), then the switch or the stop starts. No run is
  killed one by one. A pass that died in the pause does not start the pause again.
- **the-pause-keeps-the-chance-of-zero-under-ten-percent.** pause = a fifth of the time from 0.5% to zero at the burn
  rate, less the age of the reading, at most 180 s and at least 20 s. Reasoning: a whole-percent meter that reads 1%
  can stand for anything from just over 0% to 1.5%. The pause spends 0.1 points. If the meter rounds down what is used,
  the true level is uniform in 0 to 1, and the chance that it is under 0.1 is 10% at most. If the meter rounds to the
  nearest, the chance is zero. After the warning the burn falls, so the spend in the pause is smaller still.
- **a-stale-reading-uses-the-safe-values.** A burn or a level that is older than `stale_min`, or cannot be read: the
  warning line is the fast one, the pause is the shortest, and each order says that the reading is stale. A read that
  failed is never "plenty left".
- **a-kept-account-has-no-emergency.** An account whose line is over `emergency_max_line` gets the warning and the
  switch at the end of the last run, and never an emergency order or a pause, at any percent.
- **the-last-account-goes-dark-and-comes-back.** With nowhere to go, the two orders go out and no switch; the fleet
  stops at the account's own line when the runs end, or after the pause at 1%. After a reset reading the plan starts
  the fleet, or switches to the account that refilled.
- **a-one-percent-line-is-not-killed-unwarned.** An account with a 1% line and a run live drains at 2%, and at 1% it
  orders and pauses before the switch (the fault of 2026-11-24).
- **unreadable-runs-count-as-live.** Runs that cannot be read: the plan drains, and at 1% it orders the store's runs,
  pauses and switches.
- **each-step-is-recorded-once.** The warning, the emergency and the switch each write one Conductor log line and one
  ledger event with the step, the percent, the burn, the minutes and the runs. The switch's line says for each ordered
  run: ended before the switch; saved a note (with its time); no note seen; or could not look.
- **an-order-spends-no-trial-and-blocks-nothing.** `order_runs` writes no OFF switch, voids no run, releases no
  reservation and sets no kill timer.
- **a-wrapped-run-is-carried-on-after-the-switch.** A run that ended with a LEFT OPEN note is not continued while the
  account ends. The first pass with headroom starts its continuation.
- **a-switch-never-lands-on-an-ending-account.** An account at or under 3% (or its own line) is no switch target.
- **the-hold-file-stops-it.** A HOLD file that appears in the pause stops the switch.

## LIMITS (all are machine-safety brakes: an account at 0% errors every window and helper on it)

- `emergency_pct` = 1. Danger: an account at 0%. Evidence: the lowest percent a whole-percent meter shows (8,749 stored
  readings to 2026-11-20, none fractional).
- `warn_pct` = 2, `warn_fast_pct` = 3. Danger: a run killed with its work unsaved. His words above.
- `save_need_min` = 10, the minutes a run needs to finish its unit and save. Danger: the emergency reaches a run that
  had no time to save. Evidence, measured 2026-11-24 over every at-easy-spot order on record (19): 17 were heard, and
  those runs ended p50 5.0, p90 9.5, max 13.8 min after the order. So the 3% line starts over 0.1% a minute.
- `burn_window_min` = 45. Danger: one whole-percent step read as a rate. Evidence: 45 min holds three 15-min readings,
  and one step is then 0.022% a minute, a third of 2026-11-24's 0.067.
- `stale_min` = 20. Danger: a burn rate or a level from before the load changed. Evidence: the meter's timer reads every
  15 min; an age over 20 means that a read was missed.
- `poll_min` = 0.5, and one more pass each 60 s, at most 4, inside each 5-min beat while an account ends: each pass
  reads the meter. Danger: 1% is seen 5 to 10 min late (half a point at 0.067% a minute), and the age of the reading
  takes the pause down to its shortest. `/usage` makes no model call.
- `pause_max_s` = 180, `pause_min_s` = 20. Danger: 0% reached in the pause; a run that never hears the order. Evidence:
  his card ("a fifth of the time to zero, 3 minutes at most"); half of the orders on record were heard within 48 s.
- `emergency_max_line` = 10. Danger: an emergency kill on an account that is far from zero (his words: such an account
  "does not need the emergency kill at all"). Evidence: the plan's lines are 1 to 5 and 52.
- `clear_pct` = 5. Danger: a meter step back of one point taken for a reset. Evidence: a reset adds 90 points or more.

Later lists beside this page: `polish.md`.
