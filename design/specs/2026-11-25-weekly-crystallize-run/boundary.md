# BOUNDARY: the weekly Crystallize pass runs by itself, Design Version 0.1.0

Code: `src/RimMandrake/Utils/crystallize_weekly.py`, its brief `src/RimMandrake/Utils/crystallize_weekly_brief.md`,
and `src/RimMandrake/Utils/systemd/rm-crystallize.{service,timer}`. Item:
`RIMMANDRAKE_REVIVE_WEEKLY_CRYSTALLIZE_RAN_31_DAYS_APART`. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_crystallize_weekly.py`.

## What it is for

The pass ran 2026-10-19 and 2026-11-19, 31 days apart, because nothing scheduled it. The Conductor decided on
2026-11-23 that it is a weekly scheduled run, not a reminder. Rule: `design/RimMandrake/standing_rulings.md` §The
weekly Crystallize pass improves the agents. `rm-crystallize.timer` ticks daily at 05:40 local on Archmagi. A tick
launches the ISO week's pass once, as a detached opus helper on the item `RIMMANDRAKE_RUN_WEEKLY_CRYSTALLIZE_<YYYY>W<WW>`
(filed by the tick, with the outcome check `crystallize_weekly.py report <week>`). The pass writes
`<agent storage>/rimmandrake/conductor/crystallize_<YYYY>W<WW>/CYCLE_REPORT.md`, and its line `Status: FINAL` marks it
done. Each tick writes the reading `<agent storage>/rimmandrake/crystallize_weekly/last.json`.

## ACCEPTS (the only inputs this is built for)

- **a-conductor-folder.** `agent_storage.py rimmandrake`/conductor (`RM_CRYSTALLIZE_DIR` overrides it, tests only),
  with zero or more `crystallize_<YYYY>W<WW>/CYCLE_REPORT.md`. A folder whose name is not a week is skipped.
- **the-ledger.** The week item's state, folded by `model.replay` over every shard.

## DOES NOT SURVIVE (not promised)

- **a-pass-that-dies-after-a-good-launch.** The detached run's own `finish` and `left_open_continue.py` carry it. The
  tick does not launch the week again; the repair item's check (`fresh`) goes red the week after.
- **another-machine.** The reports and the timer are on Archmagi. On another machine `fresh` reads no timer and fails.

## PROMISES (each one is owed a test of the same name)

- **weeks-are-iso-weeks.** A week is `<ISO year>W<two-digit ISO week>`.
- **a-final-report-is-the-stand-alone-status-line.** A report is FINAL only when a line starts `Status: FINAL`; a
  quote of that line inside another line is not. `report <week>` exits 0 only on a FINAL report of that week.
- **a-week-with-a-final-report-launches-nothing.** A FINAL report of this week, or the week's item closed, launches
  nothing.
- **a-good-launch-is-not-repeated-in-its-week.** After a launch that exited 0 in this week, a tick launches nothing.
- **a-refused-launch-is-tried-again-next-tick.** A launch or filing that failed is planned again on the next tick; an
  item already filed is launched, not filed again.
- **a-plan-writes-nothing.** `tick` without `--apply` files, launches and writes nothing.
- **fresh-needs-the-timer-and-a-report-of-this-or-last-week.** `fresh` exits 0 only when the timer is enabled and
  active and the newest FINAL report is of this ISO week or the week before.
- **an-unreadable-timer-is-could-not-look.** When systemctl gives nothing, `fresh` exits 2, never 0.
- **the-brief-names-the-week-item-and-last-pass.** The brief has every slot filled: the week, the item, the report
  folder, and the last FINAL report (or says there is none).

## LIMITS

- `LAUNCH_TIMEOUT_S` is `time_budget.LAUNCH_S`: hang guard (class launch).
- `CONTINUE_ON_CAP` 1: danger, a spend-capped pass relaunched without end.
- The spend cap is `opus_cap_usd` of `src/RimMandrake/rimflow/list_dispatch.json`, read there; its danger is written there.
- `TimeoutStartSec` 11400 of the service (`# budget: class=launch`): a hung tick stops the timer for good.
