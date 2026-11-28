# Line schedules: what the sweep found, and the rules that follow

For the owner. The words are defined on `boundary.md` beside this page. Each figure is `[measured]` by one of two sweep
runs of 2026-11-27 on the code of item `RIMMANDRAKE_SCHEDULE_LEAVE_LINES_BY_WEEKDAY_FLAT_NUMBER_TODAY`:
**run S** = `account_plan_sweep.py schedules --seeds 3` (Claude accounts, the real pass, 75 regimes) and **run C** =
`account_plan_sweep.py codex --seeds 4` (Codex, the real gate, 116 regimes). Both read 0 VIOLATES. The regions and every
regime's measures: `regime_map.md`. The numbers here are not chosen for you: you and the Conductor set them.

## How to set one

    ./acct line codex --schedule "Sat 23:59=40 hold; Tue 13:30=0 ramp" --owner-said "..."
    ./acct whatif -- line codex --schedule "..."      (the same, written nowhere)
    ./acct line codex 25                              (one flat number again)

Each point is the line up to its moment. `hold`: that percent from the point before (or the reset) up to the point.
`ramp`: a straight line from the point before to this point. Type the points in the order of the week from the reset.
`./acct status` then shows the line now, its next change, and each point as hours before the reset.

## The corner cases, with the rule for each

1. **The reset moves.** A reset that moves by up to 2 hours is absorbed: the point at the reset stays the end of the
   week. In the two daylight-saving weeks the points keep their Pacific clock and a reset fixed in UTC moves one hour,
   so a ramp starts an hour earlier or later against the reset: the line differs from the typed one by at most 0.7 points
   [measured, run C, the two daylight-saving regions]. A reset that moves by days restarts the week on the real reset:
   a reset a day early starts next week's 40% a day early, a reset a day late holds 0% for the extra day (Codex dark
   hours rose from 25.8 to 51.5 a week in one regime) [measured, run C, "1-3 days"]. A jitter of the meter's reset by
   up to an hour costs nothing (0.4 to 0.5 points erased a week, as with none) [measured, run C, "jitters by 1-60 min"].
   **Rule: after a reset moves by more than 2 hours, type the schedule again against the new reset.** `./acct status`
   says `OUTSIDE THE WEEK`, or the hours before the reset of the last point are no longer 0.

2. **A falling ramp on a Claude account that is the last account.** The fleet stops at the line, the line falls, the
   fleet starts, reaches the line within about an hour, its runs are told to save, and it stops again: up to 12 stops in
   96 hours [measured, run S, "a schedule on system beside steven's 48 h step | 4 runs" and "the live account's line
   falls, the next account flat | no run"]. **Rule: on a Claude account, use a few `hold` steps, not a ramp,** unless
   another account can always take over. Codex has no runs to stop: a ramp suits it.

3. **A rising line on the live Claude account, with a run that does not end.** The fleet keeps burning under the new
   line until the drain bound (`rescue.drain_h`, 2 h) ends the run: up to 61 points under the line in 96 hours [measured,
   run S, "two schedules that cross | a run that never ends"]. With runs that save in under 30 minutes, a rising line
   on the live account cost at most 1.1 points, and the deepest overshoot was 1.7 points [measured, run S, "the live
   account's line ramps up past its level | 4 runs"]. **Rule: let a
   Claude line rise only on an account that is not live, or put the rise 2 hours before the moment the reserve must
   hold.**

4. **His own use.** The plan keeps the line against the fleet only. His use eats the reserve, which is what it is for:
   with 0.3 to 0.7 points an hour from Wednesday to Saturday (about 31 points a week) he was never left with an empty
   Codex under his example; under today's flat 25% a fast fleet left him with none for 6.1 hours a week [measured, run
   C, the comparison]. Use of 1 to 3 points an hour on those days (about 110 a week) is more than any reserve: Codex was
   empty for 22 to 29 hours a week [measured, run C, "more than the reserve"]. **Rule: size the reserve to his own week
   of use, not more.**

5. **A schedule set in the middle of the week** moves the line at once. If Codex is under the new line, the Codex lane
   pauses until the line falls (up to 24 hours a week under the line, and a gap down to -8.3 points) [measured, run C,
   "set in the middle of the week"]. **Rule: set a higher reserve when Codex is above it, or accept the pause.**

6. **A fast fleet rides a falling ramp** just under the line: Codex reads under the line for many hours of the ramp,
   but never by more than 0.5 points [measured, run C, the fast regime]. Nothing to do.

7. **A schedule that a hand edit broke** is read as its highest percent: the reserve is kept and nothing is erased, but
   the Codex lane is dark for longer (83 to 125 hours a week, against 26 to 97 with the schedule read) [measured, run C,
   "a hand edit broke"]. `./acct status` says `COULD NOT LOOK`. **Rule: never edit `plan.json` by hand; type the
   schedule again with `./acct line`.**

8. **The reset-day rule does not apply to a step with a schedule.** The schedule says the line up to the reset.
   **Rule: end the schedule at 0% at the reset if the last day is to be burned** (the example does).

9. **The meter unread near a point or near the reset, or a reading from before the reset**: no harm beyond what the
   flat line has (at most 1.7 points erased a week) [measured, run C, those three regions].

## The owner's example against today's flat 25% (Codex)

The real Codex week (reset Tuesday 1:36 PM), three weeks, four regimes for each row, the mean per week (the lowest gap
is the lowest seen). "Dark" is the hours in which Codex jobs waited and the gate refused. Codex makes no switches.
[measured, run C]

| burn regime | his own use | plan | h/week under the line | lowest gap | erased at the reset, pts/week | dark h/week | his Codex empty, h/week | fleet pts/week | his pts/week |
|---|---|---|---|---|---|---|---|---|---|
| slow (0.05-0.3/h) | none | flat 25% | 0 | 46.2 | 79 | 0 | 0 | 21 | 0 |
| slow (0.05-0.3/h) | none | his example | 0 | 38.7 | 79 | 0 | 0 | 21 | 0 |
| slow (0.05-0.3/h) | Wed-Sat 0.3-0.7/h | flat 25% | 0 | 21.4 | 48.2 | 0 | 0 | 21 | 30.8 |
| slow (0.05-0.3/h) | Wed-Sat 0.3-0.7/h | his example | 0 | 10.2 | 48.2 | 0 | 0 | 21 | 30.8 |
| medium (0.5-1.2/h, today's 0.8) | none | flat 25% | 0 | 0.4 | 8.7 | 34.5 | 0 | 91.4 | 0 |
| medium (0.5-1.2/h, today's 0.8) | none | his example | 0 | 0.2 | 2 | 24.4 | 0 | 98 | 0 |
| medium (0.5-1.2/h, today's 0.8) | Wed-Sat 0.3-0.7/h | flat 25% | 63.6 | -11.3 | 1.1 | 69.3 | 0 | 68.2 | 30.8 |
| medium (0.5-1.2/h, today's 0.8) | Wed-Sat 0.3-0.7/h | his example | 64 | -19.1 | 1.3 | 69.8 | 0 | 67.9 | 30.8 |
| fast (2.5-5/h) | none | flat 25% | 0 | 0.3 | 0.4 | 136.4 | 0 | 99.7 | 0 |
| fast (2.5-5/h) | none | his example | 29.8 | -0.5 | 0.4 | 136.4 | 0 | 99.7 | 0 |
| fast (2.5-5/h) | Wed-Sat 0.3-0.7/h | flat 25% | 120.2 | -25 | 0.1 | 144.9 | 6.1 | 73.1 | 26.9 |
| fast (2.5-5/h) | Wed-Sat 0.3-0.7/h | his example | 140.1 | -37.8 | 0.4 | 146.4 | 0 | 68.9 | 30.8 |
| a burst of 3-8/h in the 12 h before the ramp | none | flat 25% | 0 | 0.1 | 20.3 | 40.5 | 0 | 79.7 | 0 |
| a burst of 3-8/h in the 12 h before the ramp | none | his example | 0.8 | -0.5 | 27.6 | 5.8 | 0 | 72.5 | 0 |
| a burst of 3-8/h in the 12 h before the ramp | Wed-Sat 0.3-0.7/h | flat 25% | 43.5 | -4.5 | 17.9 | 44.1 | 0 | 57 | 25.2 |
| a burst of 3-8/h in the 12 h before the ramp | Wed-Sat 0.3-0.7/h | his example | 13.4 | -5.7 | 25.4 | 14.1 | 0 | 49.4 | 25.2 |

How to read it: "under the line" with his own use is his reserve in use, not a fault (the fleet never went more than
0.5 points under). At today's burn and no use of his own, the example erases 2 points a week instead of 8.7 and has 24
dark hours instead of 34.5. With a fast fleet and his use, the example keeps him supplied (0 hours empty instead of
6.1) for about 4 points a week less fleet work. A burst just before the ramp is refused while the 40% holds: fewer dark
hours (5.8 against 40.5) but more erased (27.6 against 20.3), because the points that the ramp frees come after the
burst.

## What the sweep does not show

The meter's own lags, a real Codex job's length (a job is sent or not each 5 minutes), and a reset that moves for some
other reason than the two daylight-saving weeks (`boundary.md`, DOES NOT SURVIVE). The Claude regimes start from drawn
levels, many of them spent, so their dark hours are large with or without a schedule; read them against each other,
not as the fleet's week.
