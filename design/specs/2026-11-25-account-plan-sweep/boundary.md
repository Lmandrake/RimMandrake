# BOUNDARY: the sweep of the account plan over burn regimes, Design Version 0.1.0

Code: `src/RimMandrake/Utils/account_plan_sweep.py` (command `./acct sweep`). Its selftest:
`src/RimMandrake/Utils/selftest_account_plan_sweep.py`. Output: `regime_map.md` beside this page.
Item: `RIMMANDRAKE_SWEEP_ACCOUNT_BURN_REGIMES_TWO_FAULTS_ONE_DAY`. The plan that it sweeps:
`design/specs/2026-11-24-account-plan-one-file/boundary.md`.

## What it is

The sweep runs the real timed pass (`account_plan.tick`, which drives `switching_plan.check` and its actuator, and
calls `account_plan.decide`, `machine_notice`, `machine_switch` and `push_machines`) every 5 minutes through a simulated
stretch of a week, over a grid of regimes. It reads the files that the pass wrote (the notice, the published decision,
the state) the way the launchers and the checkpoint hook read them, and it asks the real launcher gate
(`account_plan.new_run_gate`) and the real hook (`switch_checkpoint_signal.switch_pending`). After each pass it checks the
wanted behaviour. It computes the owner's measures for each regime and a foresight bound. Each region of the grid gets
one verdict: OK, VIOLATES (which check) or COSTLY (how many points over the bound).

The stand-ins replace only what touches the world:

| stand-in | replaces | model |
|---|---|---|
| the meter | `account_usage`'s raw poll | a poll each `every_min` minutes records each readable account's level, rounded to whole points, and its reset; `account_usage.derive_record` (the real reader) makes the row from it. `poll_fn` polls at once. |
| the burn reader | `account_end.read_burn` | the true burn of the live account over the last 45 min |
| the switcher | `claude-account` (`SP.run`, `SP.switcher_status`) | `use` changes the live account at once and writes the switcher's log line; it can fail; `fleet-stop` and `fleet-start` set the fleet's state |
| the live runs | systemd and the order channel | each machine keeps `n` runs; a run starts when the real gate admits it, lasts 24 to 122 min, and ends `save_min` after a save order (2 min after an emergency order); a switch on Archmagi ends the runs still live |
| SteveDesktop's ssh door | `account_plan_machines` | its account, its notice, its run count and its switch; each can fail for hours |
| the second consumer | the owner's laptop | a burn on one fixed account that the plan does not move |
| the disk | `os.fsync` | a no-op: the scratch folder need not reach the disk |
| the phone and the ledger | `notify_stop`, `flush_ledger` | no-ops |

The burn of a machine lands on its live account: the whole demand with no run model (`none`: its windows burn), else
the demand times the share of its `n` runs that are live. A stopped fleet burns nothing. Demand that does not land is
`idle` points (it counts in the cost, as in the plan's own week ahead).

## ACCEPTS

- **a-region.** A name and a spec of ranges (`realize` draws one regime inside the ranges from a seed).
- **a-regime.** A JSON object: start levels, resets, the live account, burn, runs, SteveDesktop, laptop, meter, plan
  variant, switcher (`./acct sweep one '<json>'`). `numbers` (a dotted path to a value) changes a number of the
  sweep's copy of the plan, for a what-if; the live plan file is never read or written.
- **the-plan-code-of-this-checkout.** The sweep imports `account_plan.py` and `switching_plan.py` from beside it. A copy
  of the code with a planted fault is swept the same way (the selftest does this).

## DOES NOT SURVIVE (not shown by the sweep)

- **the-real-switcher.** The stand-in switches at once. The sweep does not show that `claude-account use` switches,
  how long it takes, or that a window opens again after it.
- **a-real-run.** The stand-in run ends when its save time is up. The sweep does not show that a real run saves and
  ends when it is told, or that a run tells the truth about being done.
- **the-real-meter.** The stand-in reads whole points with no error and no jitter in the reset time. The sweep does not
  show the Anthropic meter's own lags or wrong readings.
- **two-plan-files.** One machine decides. A second deciding machine is not modelled.
- **the-old-driver.** The sweep runs `driver new`. The old engine alone is not swept.
- **the-live-plan-file.** The live plan file is on Archmagi. This run built today's plan from the legacy file and the
  seed (`today_plan`); `ssh archmagi` from SteveDesktop failed (host key) on 2026-11-25.
- **a-model-not-yet-compared.** No real switch had happened when this page was written: the stand-in's model of a
  switch is not yet compared with a real one. After the first real switch, compare the sweep's switch with
  `./acct measures` and the plan's `log.jsonl` (the time from the line to the switch, the runs that the switch ended,
  the overshoot), and correct the stand-ins.

## PROMISES (each one is owed a check of the same name in the selftest)

- **the_sweep_runs_the_real_pass.** Each pass is `account_plan.tick` with seams; no decision, notice or gate is
  re-implemented in the sweep.
- **the_sweep_is_deterministic.** The same regime and seed give the same violations and measures.
- **the_sweep_touches_no_live_folder.** It writes only under its scratch folder, calls no real switcher, ssh, systemd,
  meter, phone or ledger, and refuses to run when a live folder is set.
- **the_sweep_finds_the_fault_of_391283b692.** With the `unread` mark taken out of `decide` in a copy of the code, the
  sweep reports FALSE_PENDING in the region "RESET PASSED with no level".
- **the_sweep_finds_the_fault_of_d469f03d9d.** With `machine_switch` back to "only at its line" in a copy of the code,
  the sweep reports STUCK on SteveDesktop in the region "SteveDesktop on an account that no step uses".
- **the_quick_part_is_green_on_this_code.** `./acct sweep quick` reports no VIOLATES on the published code.

## THE WANTED BEHAVIOUR (checked on every pass)

| check | wanted | how it is read |
|---|---|---|
| STUCK | no machine is refused new runs for more than K passes while another account of the plan is readable and above its entry line | the real gate after the pass; "can take over" on the true levels, an account that a step uses now and the meter can read |
| STUCK_SAME | not the same refusal for SAME_N passes with no input changed | the decision, the gate and the whole points of each level |
| STOP_WITH_TAKER | the fleet never stops while an account can take over | each `fleet-stop` call |
| FALSE_PENDING / MISSED_PENDING | a run or a window is told "switch pending" only on a pass where a switch is pending, and always on such a pass | the real hook on the notice, against the decision (a switch, its drain, a stop, the end at the line; not a level that is only unread) |
| UNREAD_ACT / ACT_ABOVE_LINE | a level that cannot be read never causes a switch or a stop by itself | an act at the line where the true level is more than the burn since the last reading plus 1.5 points above the line |
| SWITCH_TO_SPENT | no switch to an account at or under its line | the true level of the target at the switch |
| FLIP_FLOP | no A -> B -> A within FLIP_H hours with no reset of A or B between | the switches of each machine |
| SWITCH_ABOVE_LINE | a machine above its line is switched only in the stated cases: a rescue, a step that ended, an account that no step uses now, a request | the decision's reason line at the switch |
| OVERSHOOT | the live account goes under its line by no more than the burn of the save time | the true level against the line, while another account can take over; bound 1.5 points plus the burn of `save_min` + 15 min |
| CRASH | the pass never raises | any exception out of the pass |

The checks that come from the plan's PROMISES: `live_account_stays_until_its_own_line` and
`the_account_burns_to_its_line` (SWITCH_ABOVE_LINE), `an_account_left_at_its_line_is_no_target` (SWITCH_TO_SPENT),
`a_level_not_read_is_no_pending_switch` (FALSE_PENDING), `unknown_never_gives_permission` (UNREAD_ACT),
`the_last_account_waits_at_its_wait_floor` (STOP_WITH_TAKER), `a_machine_at_its_end_is_switched_when_its_runs_end`
(STUCK on SteveDesktop), `no_start_is_refused_for_a_preference` (STUCK).

## THE MEASURES (each regime)

The points above a line that each reset erases (the line of the step in force one second before the reset), the
switches (each counts 3 points), the minutes in which new runs were refused (Archmagi and SteveDesktop apart), the runs
that a switch ended, the stops, the idle points, and the largest overshoot under a line (`overshoot_max`). Cost = erased + 3 x switches + idle, the plan's own cost
(`idle_weight` 1).

The foresight bound: the best of five rules that know the whole burn ahead, on the same burn, levels, resets and
lines (earliest reset first; leave the account on it only when it is spent, or when more than theta + 3 points of an
account with an earlier reset would be erased by waiting; theta 0, 3, 6, 12 and never). The bound is an upper bound on
the optimum (it is a rule that could be run), so a gap to it is a lower bound on what the plan loses. It ignores the
drain, the meter's lag and the save time, so a gap under COSTLY_PTS is noise.

## LIMITS

- `K_STUCK` = 36 passes (3 h). Danger of a short one: a designed drain reads as stuck. Evidence: the longest designed
  refusal with another account able to take over is a drain, `rescue.drain_h` 2 h, or a run that needs up to 120 min to
  save and end (the top of the axis; 95 of 100 runs end inside 2 h, measured 2026-11-20), plus up to 60 min for a meter
  that reads late. SteveDesktop gets 6 passes more: one pass of ssh lag and `SWITCH_RETRY_S` after a failed switch.
- `SAME_N` = 288 passes (24 h). Danger: a refusal that nobody would end by itself. Evidence: no designed wait other
  than a stop for a reset lasts a day with every level the same.
- `FLIP_H` = 24 h. Danger: a switch costs 3 points and restarts every window; a return within a day with no reset is
  churn. Evidence: the plan's own week ahead counts each switch; a day is the burn window of its forecast.
- `COSTLY_PTS` = 10. Danger: a region called costly for the noise of the bound. Evidence: the bound ignores the drain
  and the save time, worth up to `rescue.drain_h` x the burn; 10 points is more than three switches.
- The regime length (`hours`, 30 h tonight, 96 h elsewhere, 12 h in the quick part). Not a limit: the sample. Danger of
  a short one: a reset that falls outside it is never seen. The grid draws the resets over the whole week.
- The quick part's size (3 regions, 2 seeds, 12 h): a few seconds a regime, so that `./publish` stays fast. Danger
  that it guards: a publish that waits minutes for a check that seldom changes. The full sweep is a command.

Later lists beside this page: `polish.md`.
