# BOUNDARY: a SteveDesktop game that no job uses is stopped, Design Version 0.1.0

Code: `src/RimMandrake/Utils/testq/idle_stop.py`, and its caller in `testq.py` (`cmd_tick`, after `games_reading`).
Item: `RIMMANDRAKE_FIX_STEVEDESKTOP_TOP_WASTE_HE_SAID_END_THIS`. The owner's words (2026-11-25): "If you're not running
the live game, kill them for the memory and simplicity." Each promise has a test of its name in
`src/RimMandrake/Utils/testq/selftest_idle_stop.py`.

A game is **in use** while the queue holds a running job on it, or any ready pending job. A game is **idle** from the
first tick that finds it not in use.

## ACCEPTS

- The queue's `running` and `pending` records, read by `testq.py`.
- The output and exit code of the game's own `rw_game.sh down` on SteveDesktop, over ssh.

## DOES NOT SURVIVE

- A game that something outside the queue starts while the tick reads it idle: the next stop asks `down` again, and
  `down` refuses while a holder (the bridge lock, a host guard) uses the game.
- A tick that cannot reach SteveDesktop: nothing is stopped, and the idle clock keeps running.

## PROMISES

- **a-game-in-use-is-never-stopped.** A running job on the game, or any ready pending job, clears its idle clock, and
  no stop is sent.
- **an-idle-game-is-stopped-after-the-idle-time.** After `IDLE_STOP_S` idle, the tick sends that game's own
  `rw_game.sh down` (Steve2 through its own clone and instance), once, and starts a new idle clock.
- **a-refused-stop-waits-and-is-named.** A `down` that refuses (a holder uses the game) is logged with its words and is
  not asked again before `RETRY_S`.
- **the-next-job-starts-the-game.** No code here: the worker's load (`rw_game.sh init && up --wait`) starts a stopped
  game, as it does after every reboot.

## LIMITS

- `IDLE_STOP_S` 30 min. Danger of a shorter time: the next job pays one cold start (262 s on Steve1,
  J20261125T200030Z-271675.a1, 2026-11-25). Evidence for 30 min: 18 of 458 gaps between jobs in the 7 days to
  2026-11-25 were longer than 30 min, and the 8 longer than 1 h held 51 game-hours (testq done records).
- `RETRY_S` 30 min. Danger: a `down` refused every minute while a helper drives the game.
- The ssh call's deadline is the `call` class of `time_budget.py`: a hung ssh would hold the tick.
