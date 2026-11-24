# RIMMANDRAKE_NAME_GAME_ON_WRAPUP_DEBTS_ARCHBIG_VOIDS_ALL

## spec

A wrap-up debt (`src/RimMandrake/rimflow/wrapup.py`, `owe`) is a setting or a scene left changed in ONE game's memory. The
debt names no game. `World.game_relaunched` reads one file, ArchBig's `Player-prev.log`, by a fixed path. So a relaunch of
ArchBig pays ArchSmall's debts, which then stay forced, and a relaunch of ArchSmall voids nothing.

- `owe` stamps the game's letter as `game` (`game_names`/`game_instance.current`, the process's `RM_GAME_INSTANCE`).
- The relaunch of a game is read from that game's previous log: ArchBig's `Player-prev.log` (`RM_WRAPUP_PREV_LOG` still
  overrides it), a named game's `<instances root>/<letter>/Player.log.prev` (`game_instance.launch` moves it there).
- A debt with no `game` (written before) is ArchBig's. A log that cannot be read voids nothing.
- `restore_at_release` replays only the debts of the game that is released.

Found while `RIMMASTER_WIRE_STEVEDESKTOP_TELEMETRY_FLYING_BLIND` (telemetry that takes a game name) looked for other tools
that read ArchBig only. The same look found these, which give no wrong result today and are a record only: the ledger
bridge share in `Utils/running_now.py` (`bridge_events` counts ArchBig's holds only), `bridgetools/build.py`'s root for game
a (Steam's C: path), and fixed log paths in `Utils/rimbench/gl_sheet_run.sh`, `Utils/loadsweep/*.sh`,
`bridgetools/crash_watch.sh`, `Utils/planet_atmosphere_cost.py` and the one-shot `bridgetools/prove_*.py`.

## verify

Acceptance test: `python3 infrastructure/state/acceptance/RIMMANDRAKE_NAME_GAME_ON_WRAPUP_DEBTS_ARCHBIG_VOIDS_ALL.py`, 6 checks; 3 of 6 pass on 9e3c73ab1f (watched red,
2026-11-23), 6 of 6 when done. Then `selftest_wrapup_void_relaunch.py`, `selftest_wrapup_restore.py`,
`selftest_wrapup_restore_at_release.py` and `selftest_wrapup.py` (if present) stay green.

## criteria

Six of six, and the existing wrap-up selftests green.
