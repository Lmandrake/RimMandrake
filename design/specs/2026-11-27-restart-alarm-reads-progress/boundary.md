# BOUNDARY: the restart alarm counts a restart lost only when the restart shows no progress

Code: `src/RimMandrake/Utils/restart_reconcile.py` (`join`, `window_progress`).
Test: `src/RimMandrake/Utils/selftest_restart_reconcile_progress.py`.

Item: `OPS_RESTART_UNSTICK_BENCH_YCVY_ZEXY`. On 2026-11-28 the alarm opened an incident at 05:04:29Z on a BENCH
goodbye. The fresh window `82515ae6` was alive and wrote its transcript the whole time. Its first turn ended at
05:16:43Z, and `restart_verified` came at 05:17:28Z. The alarm's time (`restart_reconcile_s`) is shorter than a long
first turn, so the alarm read work as an outage.

## ACCEPTS

- The Dispatcher journal's `restart_relaunched` lines. Each line names the seat, its time and the fresh window's
  `session_id`.
- The session files of Claude Code (`<claude home>/sessions/<pid>.json`) and the fresh window's transcript. The alarm
  reads both with the readers of `seat_restart.py` (`window_alive`, `transcript_for`, `tx_summary`), the same readers
  that write the evidence of `restart_verified`. The alarm has no reader of its own.

## PROMISES

- **alive-and-writing-is-no-incident.** A request that has no `restart_verified` is not due while a fresh window of
  its seat, relaunched at or after the request, is alive and its transcript has a record newer than the alarm's fire
  time (`restart_reconcile_s` less pass and slack). The length of the first turn does not matter.
- **alive-and-silent-is-an-incident.** A fresh window that is alive and writes no record for the fire time is due, as
  before. The incident is told inside `restart_reconcile_s` of the last record.
- **no-fresh-window-is-an-incident.** A request with no `restart_relaunched` line after it, or whose fresh window is
  gone, is due at the fire time, as before.

## DOES NOT SURVIVE

- A first turn that writes no transcript record for the fire time (one model call that runs that long, or a question
  card that waits that long for him) is an incident. The longest gap between records in the 2026-11-28 instance was
  88 s.
- A session file that cannot be read for its process birth counts as alive (`window_alive` fails toward alive). The
  transcript must still grow.
- An incident that was told stays open until `restart_verified`, even if the window then writes again.
