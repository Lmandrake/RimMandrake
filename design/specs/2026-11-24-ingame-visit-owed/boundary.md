# BOUNDARY: an in-game visit owed a driver

Code: `ingame_testq` in `src/RimMandrake/rimflow/maturation_dispatch.py`, `c_maturation` and
`ingame_visit_owed` in `src/RimMandrake/Utils/ops_watch.py`, and the target in
`src/RimMandrake/Utils/ops_watch_rules.json`.
Item: `RIMMANDRAKE_WATCH_INGAME_VISIT_OWED_NO_DRIVER_UNSEEN`.

## ACCEPTS

- **dispatch-and-lock-readings.** The dispatch tick names in-game visits and their running units. The lock query
  `game_lock.py query all --json` on Archmagi gives the current holder and has no release history. A purpose names
  the mod as a whole word, including in an underscore-delimited item id. Systemd gives each named unit's current state.

Over 30 temporary-state reads per case, the maturation collector took 0.03 ms median when quiet,
70.28 ms when waiting (138.92 ms max), and 66.41 ms with an active unit reported by a stub systemctl (101.83 ms max).
The parent took 70.54 ms median on the waiting fixture and 65.17 ms on the active-unit fixture.

## PROMISES

- **only-owed-bridge-checks-wait.** The dispatch reading lists checks in `to_run` with no testq block and no row in
  the current visit. A FAIL row counts as a recorded run. An earlier visit's row leaves the check owed. A held,
  blocked or completed visit, or an empty list of owed bridge checks, reads measured zero `quiet`.
- **either-game-driving-the-mod-is-busy.** A matching driver lock on either Arch game covers that mod. Owed checks
  all covered read measured zero `busy`. A lock for unrelated work leaves the mod uncovered.
- **undriven-clock.** With work still uncovered, the point reads `waiting` and the longest continuous observed
  wait. Each mod and visit starts at zero and keeps its start only from the previous fresh waiting series point.
  A busy, quiet, blind, missing or stale point breaks the wait.
- **live-pipeline-visit-is-busy.** A dispatch-named in-game unit that is still active covers its visit with both
  locks free. Confirmed dead units leave the visit uncovered. An unreadable unit or occupancy reads UNMEASURED.
- **could-not-look-is-unmeasured.** An incomplete, stale or unreadable dispatch reading, or unreadable lock state
  when work is owed, reads UNMEASURED. The lock and unit queries share a 250 ms budget and use only the time left
  on the sense beat.
- **alarm-crosses-and-reopens.** Over 30 minutes raises one fixed alarm. A repeat reopens that item and writes a line
  in the Conductor log, as on the first crossing.
