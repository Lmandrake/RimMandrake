# Polish list (a record; nobody works it)

- `tps_record.py` counts the test-state monitor's `vitals` rows as `invalid` (25,040 of them in Steve2's record on
  2026-11-23); the copies were byte-identical to the originals (47 of 47 md5).
- `telemetry bridge --game X` prints the count of calls that carry no game (from before 2026-11-23) above the game's own.
- The `health` source reads one folder of ArchBig's and has no row.
- Fixed ArchBig paths that give no wrong result today: `Utils/running_now.py` `bridge_events`, `bridgetools/build.py` game
  a's root, `Utils/rimbench/gl_sheet_run.sh`, `Utils/loadsweep/*.sh`, `bridgetools/crash_watch.sh`,
  `Utils/planet_atmosphere_cost.py`, the one-shot `bridgetools/prove_*.py`.
