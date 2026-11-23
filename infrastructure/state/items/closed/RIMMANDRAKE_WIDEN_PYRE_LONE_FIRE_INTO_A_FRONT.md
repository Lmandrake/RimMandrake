## spec
Pyrelands 0.1.0, in-game visit 7, class MOD (the steward looked at the captures and agrees). Bar `burn_line_walks`: grass
fire that moves "like a natural grass fire". The four harness rows PASS; the judge clause fails. One cause, two things seen
in `visit_7/screenshots/burn_line_dayend_sheet.jpg` (top row, wind on):
- lone fires walk as one-cell, ruler-straight lanes 20-27 cells long, one cell per about 1,300 ticks
  (`visit_7/evidence/script_line_speed.log`, `lanes_burn_line_walking_mask.png`);
- the larger burns run as flat-sided bands of constant width with a ruler-straight head (days 1-4, the lower half of the
  map). The wind-off row of the same sheet shows ragged edges: the straightness is the carry's.
Presumed cause: the wind carry moves a lit cell downwind and almost never aside, so a burn keeps the width it was lit with.
What lights a lone fire is not read (a fire-hawk ember or lightning is a guess). Not a fix: stop lone fires.

The trade to hold: the burned share stays at most half of the open ground at every day end (T_BURN_ECOLOGY and the same bar),
so a wider carry must not become the wind-off flood. How a lit cell spreads under the carry is the fixer's choice; the numbers
in the acceptance test are its measure of "not a strand", not a target to tune the mod to.

## verify
Offline: the acceptance command (0 of 8 on the base, exit 1, re-run by the steward 2026-11-23; expect 8 of 8), T_BURN_LANES,
T_BURN_ECOLOGY, T_FUZZ. If a cheap model read of the bands' flat flanks exists (edge straightness of a burn lit as a short
front), add it to T_BURN_LANES; otherwise the Stage 6 judge decides them by eye.
Stage 6, record UNRUN with `maturation.py unrun` at the close: test table id `sc_burn_line_walks`, command
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains burn_line`,
then a judge (not the maker) reads the hourly and the whole-map day-end captures.

## criteria
- `accept_lone_fire_lane.py` prints PASS, 8 of 8 cases.
- The Stage 6 judge reads the day-end captures as natural grass fire: no one-cell lanes, no flat-sided bands.

## launch-checks
must-fail: python3 design/concepts/Pyrelands/version/evidence/accept_lone_fire_lane.py

## refs
file: src/RimMandrake/Pyrelands/Source/
file: src/RimMandrake/Pyrelands/pyre_burn_sim.py
file: src/RimMandrake/Pyrelands/selftest_pyrelands_burn_front_lanes.py
