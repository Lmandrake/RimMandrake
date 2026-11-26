# Regime map of the account plan, 2026-11-25

Made by `./acct sweep grid --seeds 6` (`src/RimMandrake/Utils/account_plan_sweep.py`, page `boundary.md` beside this
map) on the code published at e4d4515487, on SteveDesktop. The sweep ran the real pass (`account_plan.tick`) every 5
minutes: 63 regions, 378 regimes, 43,632 simulated hours, 523,584 passes, in 939 s on 16 workers. Each region is a set
of ranges; six seeds drew six regimes inside it. Tonight's 24 regions ran 30 h each; the 39 axis regions ran a week
each. The plan swept is today's plan as this machine can build it (`today_plan`: the legacy file and the seed, steven
52% in its 48 h window, system 1%, lukas 1%, driver new, SteveDesktop listed). The live plan file is on Archmagi, and
`ssh archmagi` from SteveDesktop failed (host key verification), so it was not read.

## The count

- Final run: 62 OK, 0 VIOLATES, 1 COSTLY.
- Before the fixes of this run: 5 reachable VIOLATES classes. Each one is fixed with a selftest case, seen red on the
  parent, then green, and a planted fault in `account_plan_mutants.py` (112 of 112 plants caught).

## The VIOLATES that this run found and fixed

| check | smallest case (this plan, these readings, this clock, this wrong result) | fix |
|---|---|---|
| STUCK (Archmagi) | steven live at 54.6% in its window, burn 4-6/h, 3 runs, one of which does not end after its save order; at steven's 52% line the drain waited for that run: no new run for 30 h while system (90%) and lukas could take over, and the run burned steven to 1% (no emergency step over a 10% line) | 455a6145cc and e4d4515487: `an_account_end_drain_ends_at_its_bound`: on a line with no emergency step, a drain off the live account ends after `rescue.drain_h` (2 h) from its save order or its drain notice's `since`, and the switch goes |
| STUCK (Archmagi) | burn 6.7/h, no run; every account ran out and the fleet stopped on system at its 2% wait floor at 18.1 h; lukas reset to 100% at 19.1 h; the fleet stayed stopped ("no start inside its warning zone") until system's own reset, 70 h later | 455a6145cc: `a_stopped_fleet_switches_when_an_account_refills` |
| FALSE_PENDING (SteveDesktop) | no account readable for 1-6 h, SteveDesktop on system, whose last reading was 2.0% at its 2% wait floor; the deciding machine read soft (level unread, no switch pending), and SteveDesktop's notice said "at its line: save your work now", switch pending | fc4bc079d0: a last level that is not read now is no level at the line in `machine_notice` (`a_level_not_read_is_no_pending_switch`) |
| STOP_WITH_TAKER (Archmagi) | steven live at 59.1%, its 48 h window over, so it is left for lukas; the switcher failed once; the pass stopped the whole fleet though steven was 7 points above its line and system and lukas could take over | fc4bc079d0: `a_failed_switch_off_an_account_above_its_line_stops_nothing` (`decide` and the actuator's brake in `switching_plan._check`) |
| (the gate) | `./publish` refused a publish because `scene_library_mutants`, red on origin/main the same way, printed a sha of digits only (836753201427) where the base printed one with letters | a3640eb84e: `publish._norm` blanks both to one token (`selftest_publish_tree_checks`) |

In tonight's regions (steven at 53-58%, burn 4-12/h, SteveDesktop on steven with and without runs) the switch at
steven's line was right before any fix when the runs save inside 2 h: steven is left at its line when its runs end,
and SteveDesktop is switched when its own runs end. Two of the faults above were in tonight's regions all the same: the
run that does not end, at steven's line, and the stopped fleet, 18 to 27 h later, once every account had run out.

## COSTLY (not a fault; the plan's numbers are unchanged)

| region | worst regime | over the bound | the plan change that would help |
|---|---|---|---|
| burn constant 0.5-3/h | seed 5: burn 0.6/h, steven live at 8.7% (spent), system 88.5% (reset in 104.7 h), lukas 59.8% (reset in 9.4 h), 4 runs always live | 51.4 points (plan: 140.1 erased, 4 switches; bound: 83.5 erased, 6 switches); 65.2 points over 336 h | `./acct whatif -- set numbers.rescue.drain_h=null` takes this regime to 12 points under the bound. Cause: after lukas's reset the plan left system for lukas (a rescue worth 36 points by its week ahead), because the week ahead models "stay" as staying on system after system's own reset too, with no later rescue, so lukas's allowance read as lost. A burn under 3 points an hour cannot use the accounts anyway. `rescue.drain_h` null gives up the rescues that the page measured as worth 43 points of Steve's account (2026-11-10 to 11-24), so this is a trade for the Conductor, not a fix. A better fix is in the code: a week ahead that models a rescue after each future reset. |

The next largest gaps were under COSTLY_PTS (10 points) and read OK: "start: every account 0-5% left" (7.9 points, all
of it in switches: both machines follow every reset), "plan: a line changed until the reset" (6.5) and "tonight, a run
that never ends" (5.7: the 2 h drain before the switch, which the bound does not pay).

## Faults of the sweep's own stand-ins, found and repaired in this run (no plan fault)

- Burn history: the 24 h of readings before the start first put all of the start burn on the live account, more than
  its level could hold, so the plan read 0.3 instead of 4.4 points an hour and made two rescues that a real reader
  would not (two FLIP_FLOP hits). Then it used the burn of hour 0 for the whole day (a zero-burn hour). Repaired: the
  history follows the burn's own pattern back in time and lands on accounts that can hold it.
- A stop for a reset read as a pending switch (MISSED_PENDING) and as stuck (STUCK_SAME). Repaired: a stop is no
  switch; a stop with no account that can take over is the designed wait.
- A return from an account that was spent read as a flip-flop. Repaired: FLIP_FLOP needs the middle account left above
  its entry line.
- An account that started under its line read as an overshoot. Repaired: the overshoot is measured from the lower of
  the line and the level at the start.
- The bound counted one machine's switches while the plan switches both machines. Repaired: the bound counts two.
- A stop after a failed switch off a spent account read as STOP_WITH_TAKER. It is the designed brake (the switch is
  tried again from the stopped fleet). Repaired: only such a stop off an account above its line is flagged.

## A case that ordinary operation cannot reach (one line, no fix)

- None found. A run on SteveDesktop that never ends is on the plan's page as not survived
  (`a-run-on-another-machine-that-does-not-end`).

## What the sweep cannot show

- That the real switcher switches, how long it takes, or that the windows open again after it.
- That a real run saves and ends when it is told, or how long a real run takes to do it.
- The real meter's lags and errors. The stand-in reads whole points, with no jitter in the reset time.
- The live plan file of today, which is on Archmagi. The swept plan is the one that the legacy file and the seed make.
- The model of a switch is not yet compared with a real switch: no real switch had happened when this map was written.
  After the first real one, compare the time from the line to the switch, the runs that the switch ended and the
  overshoot (`./acct measures`, the plan's `log.jsonl`) with the sweep's stand-ins, and correct them.

## What is untested

- A hand switch (`hand`), a pin on an account other than the live one, and a `switch` request with `--now` in a
  regime with runs, beyond what the plan's own selftest stages.
- The old driver (`driver old`).
- A second deciding machine, and clocks that differ between the machines.
- Codex and JPL GenAI (the sweep sweeps the three Claude accounts only).
- A burn that lands on a machine with no run model (the windows) while runs also burn there.
- One recorded week of Archmagi's readings as a check of the model: `ssh archmagi` did not work from SteveDesktop.
  That check is left to the Conductor (`account_plan_replay.py` on Archmagi).

## Every region (the final run)

| region | regimes | verdict | worst gap to the foresight bound (points) |
|---|---|---|---|
| tonight | burn 4-6 | no run | SteveDesktop idle on steven | 6 | OK | 2.7 |
| tonight | burn 4-6 | no run | SteveDesktop with runs on steven | 6 | OK | 0.0 |
| tonight | burn 4-6 | runs, quick save | SteveDesktop idle on steven | 6 | OK | 2.3 |
| tonight | burn 4-6 | runs, quick save | SteveDesktop with runs on steven | 6 | OK | 0.2 |
| tonight | burn 4-6 | runs, slow save | SteveDesktop idle on steven | 6 | OK | 2.4 |
| tonight | burn 4-6 | runs, slow save | SteveDesktop with runs on steven | 6 | OK | 2.1 |
| tonight | burn 4-6 | a run that never ends | SteveDesktop idle on steven | 6 | OK | 5.7 |
| tonight | burn 4-6 | a run that never ends | SteveDesktop with runs on steven | 6 | OK | 5.1 |
| tonight | burn 6-9 | no run | SteveDesktop idle on steven | 6 | OK | 2.7 |
| tonight | burn 6-9 | no run | SteveDesktop with runs on steven | 6 | OK | -8.7 |
| tonight | burn 6-9 | runs, quick save | SteveDesktop idle on steven | 6 | OK | 1.9 |
| tonight | burn 6-9 | runs, quick save | SteveDesktop with runs on steven | 6 | OK | -11.1 |
| tonight | burn 6-9 | runs, slow save | SteveDesktop idle on steven | 6 | OK | 1.2 |
| tonight | burn 6-9 | runs, slow save | SteveDesktop with runs on steven | 6 | OK | -15.8 |
| tonight | burn 6-9 | a run that never ends | SteveDesktop idle on steven | 6 | OK | 5.7 |
| tonight | burn 6-9 | a run that never ends | SteveDesktop with runs on steven | 6 | OK | -13.4 |
| tonight | burn 9-12 | no run | SteveDesktop idle on steven | 6 | OK | 3.3 |
| tonight | burn 9-12 | no run | SteveDesktop with runs on steven | 6 | OK | -21.0 |
| tonight | burn 9-12 | runs, quick save | SteveDesktop idle on steven | 6 | OK | 2.4 |
| tonight | burn 9-12 | runs, quick save | SteveDesktop with runs on steven | 6 | OK | -23.0 |
| tonight | burn 9-12 | runs, slow save | SteveDesktop idle on steven | 6 | OK | -4.6 |
| tonight | burn 9-12 | runs, slow save | SteveDesktop with runs on steven | 6 | OK | -31.2 |
| tonight | burn 9-12 | a run that never ends | SteveDesktop idle on steven | 6 | OK | -4.9 |
| tonight | burn 9-12 | a run that never ends | SteveDesktop with runs on steven | 6 | OK | -27.8 |
| burn constant 0-0.5/h | 6 | OK | 2.9 |
| burn constant 0.5-3/h | 6 | COSTLY | 51.4 |
| burn constant 3-8/h | 6 | OK | 0.4 |
| burn constant 8-15/h | 6 | OK | 0.7 |
| burn constant 15-22/h | 6 | OK | -0.8 |
| burn constant 22-30/h | 6 | OK | -4.7 |
| burn steps up mid-week (2-4 -> 12-25/h) | 6 | OK | 0.2 |
| burn steps down mid-week (12-25 -> 0-2/h) | 6 | OK | -1.5 |
| burn in bursts (base 1-3, peaks 15-30 for 1-4 h) | 6 | OK | -1.5 |
| burn with 6-14 hours of zero a day | 6 | OK | 0.9 |
| laptop on the live account 1-4/h, all week | 6 | OK | 1.0 |
| laptop starts and stops at any hour | 6 | OK | 1.4 |
| start: live account 0-10% left | 6 | OK | 3.7 |
| start: live account 90-100% left | 6 | OK | 4.5 |
| start: every account 0-5% left | 6 | OK | 7.9 |
| start: two resets in the same hour | 6 | OK | 2.2 |
| start: a reset 1 s before or after a pass | 6 | OK | 1.3 |
| start: steven's 48 h window opens or closes within the week | 6 | OK | -3.6 |
| meter: readings 10-60 min old | 6 | OK | -0.1 |
| meter: no reading for 2-24 passes | 6 | OK | 3.7 |
| meter: RESET PASSED with no level for 5-60 min | 6 | OK | -0.4 |
| meter: one account unread for 2-12 h | 6 | OK | -2.7 |
| meter: no account readable for 1-6 h | 6 | OK | -0.4 |
| runs: none | 6 | OK | -167.8 |
| runs: always, save in 1-30 min | 6 | OK | 2.1 |
| runs: always, save in 30-120 min | 6 | OK | 0.4 |
| runs: one never ends | 6 | OK | 0.4 |
| SteveDesktop on the live account with runs | 6 | OK | -125.0 |
| SteveDesktop on another account with runs | 6 | OK | -106.6 |
| SteveDesktop on an account that no step uses (steven past its window, above its line) | 6 | OK | -133.5 |
| SteveDesktop not reachable for 1-12 h | 6 | OK | -130.0 |
| SteveDesktop's run count unread for 1-12 h | 6 | OK | -125.0 |
| plan: a hold of 1-8 h | 6 | OK | 0.8 |
| plan: a pin on the live account for 6-48 h | 6 | OK | 0.8 |
| plan: a line changed until the reset | 6 | OK | 6.5 |
| plan: the order changed mid-week | 6 | OK | 0.8 |
| plan: a switch request | 6 | OK | 0.5 |
| switcher fails once | 6 | OK | 1.3 |
| switcher fails for an hour | 6 | OK | 0.8 |
