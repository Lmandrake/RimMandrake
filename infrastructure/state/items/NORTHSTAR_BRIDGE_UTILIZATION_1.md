# NORTHSTAR_BRIDGE_UTILIZATION_1

Owner, 2026-10-01 (typed): *"Multitasking to keep the bridge active is a good idea. That's what we want to maximize. Live bridge usage. In fact that's a great metric to track."*

## spec
Measure live bridge utilization: active time (bridge calls plus game ticks advanced by the driver) divided by time the bridge was held (`rimflow bridge take` to `release`, from the ledger), per day and per run. The driver's call log (`TimedTransport.log`, `northstar_driver/transport.py`) already times every call; add tick-advance wall time, write both into each results JSON's `timing`, and add a small report (`python3 src/RimMandrake/Utils/northstar_driver/bridge_utilization.py`) that joins results JSONs with the bridge take/release events and prints held minutes, active minutes, utilization, and the idle gaps over 5 minutes with who held the bridge. Process rule it supports: author scripts offline behind a live run, never hold the bridge idle (`design/RimMandrake/debug_process.md`).

## verify
Selftest over a fixture ledger plus two fake results JSONs; one live day's report checked by hand against the ledger events.

## criteria
The report runs, utilization for 2026-10-01 is computed and recorded in the item, and the idle gaps are attributable to a stated cause (cold load, site build, waiting for a script, owner away).
