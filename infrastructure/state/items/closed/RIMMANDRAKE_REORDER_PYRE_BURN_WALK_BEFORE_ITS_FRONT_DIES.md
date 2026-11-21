# RIMMANDRAKE_REORDER_PYRE_BURN_WALK_BEFORE_ITS_FRONT_DIES

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20). Class HARNESS (presumed:
the chain's order and premise; a MOD cause is not ruled out).

## spec

`sc_burn_line_walks` (bars burn_line_walks, inv_burn_line_fire_clock), chain `burn_line`, visit 2, two runs
(design/concepts/Pyrelands/version/in_game/visit_2/evidence/pv2_burn_line.json):
- `burn_line_present` PASS: burnLineEnabled on, the map extinguished, after BURN_LINE_WAIT_TICKS (> 120,000) the standing
  burn reseeded 12 free-standing fires.
- `burn_line_walks_hourly` FAIL both runs: 0 fires at every one of 24 hourly reads, so no burn_line_walking save. Run 1
  followed an extinguish at the end of burn_line_present; run 2 (that extinguish removed, a7d25d9f33) still read 0 at
  the first hour. ProbeOpeningFront: done True, lit 5, litTick 620039 (the map's birth), mapAge ~121,861.
- `burn_line_burned_share` UNMEASURED both runs (a fire-hawk turned Manhunter; then the governor's monitor disarmed).
The row's docstring asserts the OPENING front is lit and watches it walk. On the site fixture that front was lit at
map birth and is out long before the chain's quiet window ends. Then the 12 reseeded fires are gone within an hour.

Two questions:
1. HARNESS: run the walk on a fresh map whose opening front is alive (before any long quiet window), or light a line the
   scene names; read the walk there.
2. MOD: does a reseeded standing burn on deep-ash ember-grass ground go out within an hour? The bar says the fire is
   "never out for long" and relights in open grass. If the reseed lights only cells with no fuel beside them, that is
   the mod's.

## verify

The walk row reads a front (fires > 0) on most hourly reads, then PASS or FAIL on front_walks.

## criteria

- burn_line_walks_hourly never runs on a map with no live front; a reseed that dies within an hour is named MOD or not.

## Acceptance test

Live only. Red now: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains burn_line`
reads burn_line_walks_hourly FAIL "no burn_line_walking save was made while the front walked: None" with fires 0 at
every hour (2 of 2 runs, 2026-11-20). Green: the hourly fires read above 0 and the row decides on front_walks.

## refs

file: src/RimMandrake/Pyrelands/validation.py
file: src/RimMandrake/Pyrelands/Source/MapComponent_BurnLine.cs
