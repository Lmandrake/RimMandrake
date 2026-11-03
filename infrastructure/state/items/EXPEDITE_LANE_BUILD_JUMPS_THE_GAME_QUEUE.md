# EXPEDITE_LANE_BUILD_JUMPS_THE_GAME_QUEUE

Owner's card, 2026-11-03: "No limits on how many can be requested, leaves the live game alone unless it needs it (last slot to take). Should have a switch: is it Interrupt-level urgency (very rare, only for imminent threats to machine safety or panicked user requests), or 'next available slot' expedited. Otherwise agree." "Build it."

Kept from the proposal: Operations or the Conductor set it, never Relentless on its own work; 4 h expiry unless renewed; every use in the daily digest.

## As built

Code: src/RimMandrake/rimflow/relentless_expedite.py, wired in relentless.py and relentless_game.py. Test: selftest_relentless_expedite.py.

- `relentless.py expedite {set,renew,clear,list} <item> --level interrupt|expedited --by Operations|Conductor --why "..."` appends one line to `store/expedite.jsonl`. A process carrying a Relentless worker's environment is refused.
- Each tick folds the log onto `st["expedite"]`. The order is expedite tier > Operations' system order > priority list > returned > fresh; inside the tier interrupt comes before expedited, then the older request.
- `expedited` stops nothing. `interrupt` stops one running worker per interrupt that has no place coming, only when the house is full (`max_workers`): content before system, later in Operations' order first, newest first. Never another expedited item, never a worker on the live game, and an open breaker, a pause or low memory stops nobody.
- Game line: an expedited item waiting its turn goes next, nothing behind it starts, nothing running is stopped.
- Digest: each use is a ledger note with a `delegated:` why, written by the tick; delegated_digest.py lists those.
