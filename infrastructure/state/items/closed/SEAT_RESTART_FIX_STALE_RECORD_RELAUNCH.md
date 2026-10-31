## Finding
No message is lost, but a dead Dispatcher leaves a stale handoff record. Proved by real SIGKILL
(`selftest_seat_restart_death.py`).

The Dispatcher tick saves state only in `finally`, so SIGKILL loses the tick. If it dies after writing the record
and input then cancels the handoff, the record stays non-aborted; a window that quits inside the tile window
relaunches and replays a message already answered. Likewise, after a kill plus Dispatcher death the stale state.json
cancels what actually happened, so first-turn verification and fallback are lost.

## Fix idea
Persist state before `restart_kill` (the `claimed` reconcile needs a persisted claim) and abort the record on cancel.

## verify
- L0: GAP_STALE rows in selftest_seat_restart_death.py flip; the window quit after a cancel does not relaunch.

## criteria
- A cancelled handoff never relaunches, and a killed handoff keeps first-turn verification across Dispatcher death.
