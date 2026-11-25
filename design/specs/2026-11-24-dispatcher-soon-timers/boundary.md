# BOUNDARY: extra Dispatcher ticks for seat restart

Code: `src/RimMandrake/rimflow/seat_restart.py` (`_tick_soon`).
Test: `src/RimMandrake/rimflow/selftest_seat_restart.py`.

## ACCEPTS

The seat restart paths supply delays in seconds for extra Dispatcher ticks. `SEAT_RESTART_NO_TICK` skips these ticks.

## PROMISES

- **dispatcher-ticks-use-wall-clock-slots.** Each delay has one fixed transient unit name. Rearming stops the previous
  timer and its helper, then arms a one-shot at an absolute local wall-clock time so a daemon-reload cannot reset the
  delay. When the timer elapses, its helper starts `rm-dispatcher.service` and the transient units can unload.
  With `SEAT_RESTART_NO_TICK` set to a nonempty value, no commands run.

## DOES NOT SURVIVE

If the user systemd manager cannot arm an extra tick, seat restart still depends on the regular Dispatcher timer.
