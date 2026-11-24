# BOUNDARY: a switch or a stop that falls due waits for live runs, Design Version 0.2.0

Code: `src/RimMandrake/Utils/switching_plan.py` (`decide`, `drained`, `live_detached_runs`, `check`) and
`src/RimMandrake/rimflow/detached_helper.py` (`drain_refusal`, read by `_launch`).
Item: `RIMMANDRAKE_LAUNCH_SIX_CONTEXT_KEEPING_CHANGES_FROM_THE_SCAN`, report change 3
(`design/specs/2026-11-20-context-kept-not-reloaded/report.md` §1 row 3), written 2026-11-20.
Each promise has a check of its name in `src/RimMandrake/Utils/selftest_switching_plan_drain.py`.

The owner, 2026-11-20 about 5:30 AM PST: "And yes for live runs finish past, absolutely. Actually 0.1% is even ok kept.
We just don't want to crash to zero and get stuck. Please make that true everywhere." About 6 AM PST: "Agreed for 1% at
the moment".

Why the switch must wait: `claude-account use` moves the live credential and stops every Claude process on the machine,
so a run cannot go on with the old account after a switch. "Live runs finish" therefore means the switch waits until
they end. Measured cost of not waiting: on 2026-11-18 a stop and a switch killed 9 runs, and their resumes on the next
account missed the prompt cache: 4.73M weighted on the first turns alone (the report, §1 row 3).

The meter reads whole percents, so the hard floor is 1%, not 0.1%. Measured 2026-11-20: 8,749 stored readings in
`/mnt/d/ClaudeWork/rimmandrake/account_usage/series.jsonl` (2026-10-26 to 2026-11-20; `claude /usage` and the plan usage
endpoint) hold no fraction. A 0.1% line cannot be seen until a meter reads tenths (item
`RIMMANDRAKE_FIND_FINER_QUOTA_METERS_WHOLE_PERCENT_TODAY` looks for one).

## ACCEPTS (the only inputs this is built for)

- **a-meter.** `account_usage.read_now()` records, as `decide` has always read them.
- **live-runs.** A list of the live detached run units (`rm-detached-*` services, active, less their `-return` and
  `-continue` steps), or None when systemd cannot be read.
- **a-notice.** `notice.json` as `write_notice` writes it, read by `drain_refusal`.

## DOES NOT SURVIVE (not promised)

- **a-window-helper.** A subagent of an interactive window is not a detached run and is not waited for; the soft
  notice already gives each seat 0 new helpers (`slot_allocator`), and the switch relaunches the windows.
- **a-run-launched-outside-detached-helper.** A run that does not start through `detached_helper.launch` is not
  refused in a drain.

## PROMISES (each one is owed a check of the same name)

- **a-spent-account-drains-while-runs-live.** At or under its warning line, with a live run, the plan neither switches
  nor stops: it reads `soft` with `drain` true, and names the runs and the warning line. How the account then ends (the
  orders, the emergency at 1%) is the page `design/specs/2026-11-24-account-end/boundary.md`.
- **no-live-run-means-no-wait.** At or under its line with no live run, the switch or the stop goes ahead at once.
- **unreadable-runs-count-as-live.** When the live runs cannot be read, the plan drains and the why says UNMEASURED; a
  blind reading is never read as "no runs".
- **the-floors-never-reach-zero.** The shipped plan's `switch_away_pct_left` and `account_end.emergency_pct` are 1, every floor is
  at least 1, steven's leave line is 52 and the order is steven, system, lukas.
- **a-pull-switch-waits-for-live-runs.** A switch made above the line (a priority or reset pull) waits while a run is
  live, up to `pull_drain_max_s` after the first drain notice; with no live run it goes at once.
- **a-new-launch-waits-while-the-account-drains.** While a fresh notice reads `soft` with `drain` true,
  `detached_helper.launch` refuses a new run with a reason that names the drain. A continuation of a live run
  (`continued_from`) or a resume of its session is the run finishing, and is let through, unless the notice reads
  `account_end` true.
- **a-new-launch-goes-at-the-soft-line.** Between the soft line and the warning line, with no drain, a new run starts.

## LIMITS

- `pull_drain_max_s` = 7200. Danger: a run that does not end keeps every new start waiting and the machine off the
  account the order wants (steven's window is 48 h). Evidence: 724 detached runs measured 2026-11-20 ran p50 24 min,
  p90 82, p95 122, p99 216, max 804; 2 h lets 95 of 100 runs finish.
- A notice older than 20 min (`NOTICE_FRESH_S`) refuses nothing: the plan's timer writes every 5 min, so an older one
  means the timer stopped, and a dead timer must not hold every launch.

Later lists beside this page: `polish.md`.
