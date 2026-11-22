## spec
Pyrelands 0.1.0, HARNESS, unrepaired in in-game visit 3 (game b, 2026-11-21). Check `sc_burn_line_walks` (bars
`burn_line_walks`, `inv_burn_line_fire_clock`, both undecided without it). `burn_line_off_control` first counted the
fire clock's fronts (`fireClockEnabled` is its own switch). Repaired to hold the fire clock, hawk spread and weather,
it then read PASS on its planted state too (`PYRE_PLANT_BURNLINE_TOGGLE_IGNORED=1`: toggle left on, 0 fires), so it
cannot fail. What `burnLineEnabled` gates (WatchApproach, NudgeBurrowers, AccrueArsonDebt, KeepTheBurnAlive) acts on
a live burn, not a cold map [guess ~60%]: the control likely needs a live burn line to observe.
Evidence: `design/concepts/Pyrelands/version/in_game/visit_3/evidence/run_burn_line_off_control_planted.log`, `design/concepts/Pyrelands/version/in_game/visit_3/evidence/run_burn_line_rerun.log`.

## verify
Stage 6 (game-up). In-game check `sc_burn_line_walks`: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains burn_line_off_control`.

## criteria
- The control reads FAIL on the planted state and PASS on the real build, both readings beside the row.
- The repair never weakens what the check observes and never touches the mod.

## Acceptance test
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains burn_line_off_control` with `PYRE_PLANT_BURNLINE_TOGGLE_IGNORED=1` (through WSLENV) reads FAIL, and without it
PASS; red now (the planted run reads PASS).
