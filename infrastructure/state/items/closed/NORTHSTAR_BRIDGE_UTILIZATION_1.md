# NORTHSTAR_BRIDGE_UTILIZATION_1

Owner, 2026-10-01 (typed): *"Multitasking to keep the bridge active is a good idea. That's what we want to maximize. Live bridge usage. In fact that's a great metric to track."*

## spec
Measure live bridge utilization: active time (bridge calls plus game ticks advanced by the driver) divided by time the bridge was held (`rimflow bridge take` to `release`, from the ledger), per day and per run. The driver's call log (`TimedTransport.log`, `northstar_driver/transport.py`) already times every call; add tick-advance wall time, write both into each results JSON's `timing`, and add a small report (`python3 src/RimMandrake/Utils/northstar_driver/bridge_utilization.py`) that joins results JSONs with the bridge take/release events and prints held minutes, active minutes, utilization, and the idle gaps over 5 minutes with who held the bridge. Process rule it supports: author scripts offline behind a live run, never hold the bridge idle (`design/RimMandrake/debug_process.md`).

## verify
Selftest over a fixture ledger plus two fake results JSONs; one live day's report checked by hand against the ledger events.

## criteria
The report runs, utilization for 2026-10-01 is computed and recorded in the item, and the idle gaps are attributable to a stated cause (cold load, site build, waiting for a script, owner away).

## result 2026-10-04 (FOUNDRY builder)
- Built `src/RimMandrake/Utils/northstar_driver/bridge_utilization.py` + `selftest_bridge_utilization.py` (8/8). No
  transport change: tick advance is itself a bridge call (`step_game_ticks`), so `CallLog` already times it.
- **2026-10-01: held 674.2 min, active 21.2 min, utilization 3.1% — a LOWER BOUND (PROVISIONAL).** ACTIVE counts only
  the two drivers that leave a timed record (modcheck live-queue rows, north-star results JSONs). That day's live
  passes were mostly ad-hoc `python.exe` bridge scripts (`Transient/northstar_live_pass*_2026-10-01.md`), which
  leave no timing, so 6 of 7 idle gaps (80-297 min) read "unattributed"; one (09:37, 81 min) is a cold load.
  All-time: 6162.8 held / 655.1 active = 10.6%.
- The real cause of the unattributed gaps is unlogged activity, not proven idleness. To make the metric honest,
  ad-hoc bridge drivers must append to a call log too — follow-up, not this item.
