# Telemetry traps (measured)

- **Visible windows.** Launching Grafana with `DETACHED_PROCESS` gave each `gpx_*` plugin child its own visible
  console; the owner saw a burst of windows (2026-10-11: *"STOP THE GRAFANA WINDOWS"*). `supervise.py` launches
  with `CREATE_NO_WINDOW` + `SW_HIDE` (children inherit the hidden console) and Grafana loads two plugins only
  (`disable_plugins`, `preinstall_disabled` in `grafana/custom.ini.template`). `selftest_telemetry.py --live`
  checks no telemetry process owns a window. Never open a browser to check Grafana: ask `/api/health`.
- **Duplicate `kind` keys.** JawaBench `incident` and `awareness` rows wrote `kind` twice; `json.loads` keeps the
  last, so an incident reads as kind `stall`. `tcommon.loads` keeps the first.
- **Store python's pid.** `pythonw.exe` from WindowsApps is a launcher; the pid Popen returns is not the
  interpreter (`pythonw3.13.exe`). telemetryd is judged by its own heartbeat (`state\heartbeat.json`).
- **NAT.** WSL cannot reach Windows localhost: the CLI runs under `python.exe`. Windows can reach WSL's
  (RimPulse on 8765).
- **SQLite over drvfs** is unsafe: only Windows processes open `E:\telemetry\events.db` (telemetryd writes,
  Grafana and the CLI read).
- **bridge_calls keeps ~10 h** (20 MB, one `.1`); telemetry's raw copy is the long record. Rotation is by
  rename, so cursors key on the file id, not the path.
- **Speed 3 is CPU-bound** on the full list (ratio ≈ 0.05): the low-ratio alert fires at normal speed only.
- **Merge histograms, never average p99s** (game_health_record rule 4): `rm_game_tick_hist` is bucket counts.
- **The 10k Verse.Log cap**: `rm_game_exc_suppressed` counts what the cap swallowed; direct
  `UnityEngine.Debug.LogError` after the cap stays invisible.
- **A round zero is a query bug until proven**: check `telemetry health` lag before trusting any series.
