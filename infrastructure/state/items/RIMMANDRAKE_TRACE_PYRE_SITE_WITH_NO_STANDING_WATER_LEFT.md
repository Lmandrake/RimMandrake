# RIMMANDRAKE_TRACE_PYRE_SITE_WITH_NO_STANDING_WATER_LEFT

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20).

## spec

The visit-2 site `NS_Pyrelands_site_1_bf7f9e1fe4_visit2` (tile 3, built by `northstar_site.py --site 1`) holds 0
standing-water cells. Measured two ways: the whole-map terrain census (`jawa/get_terrain_batch`, 62,500 cells: Mud 372,
RM_FE_Ground_SoilRich 769, no Water* or Marsh*), and the GenStep's own log line at generation, `[RimMandrake.Pyrelands]
standing water: water 0, mud 372, rich soil 769; shore cells 0`. So rich-soil bands ring mud with no water in them.

The scene `sc_ash_ground` (design/concepts/Pyrelands/scenes.json) needs "a seed and tile that rolls at least one
standing-water body (asserted ... a map with none is regenerated ..., never passed)". So its `shore_ring` clause cannot
be read on this site (SITE). The site builder does not assert water.

Two questions, in this order:
1. MOD or SITE? Read the terrain just before and just after `GenStep_PyrelandsStandingWater` on this tile. If water
   was there before and `RaggedShores` (PyrelandsShoreShape.Shape) turned all of it to mud, that is a MOD fault: the bar
   says "richer ground ringing standing water", and a player on this map sees none. If no water was there before, the
   tile's patch maker only made mud. Then the site is wrong for this scene.
2. If SITE: the site recipe asserts a water-cell count above 0 for the shore-ring scene. A seed sweep stays banned; pick a
   tile that the scratch world's own terrain reads wet.

Also: `shore_ring` counted Mud as water (is_water_family). That is fixed in e02accbb59: it now counts Water*/Marsh*
only, and on this site it reads UNMEASURED ("no standing water").

## verify

A fresh site read, cell by cell, before and after the GenStep.

## criteria

- The cause is named (MOD with the pass that removes the water, or SITE).
- A site for `sc_ash_ground` holds at least one standing-water cell, and `shore_ring` runs on it.

## Acceptance test

Live only. Red now: on the visit-2 site, `python.exe design/concepts/Pyrelands/version/in_game/visit_2/scripts/terrain_census.py` (whole-map census) prints no Water*
or Marsh* key (seen 2026-11-20). Green: the census on the scene's site prints a Water* count above 0, and the
`shore_ring` row reads PASS or FAIL, not UNMEASURED.

## refs

file: src/RimMandrake/Pyrelands/Source/GenStep_PyrelandsStandingWater.cs
file: src/RimMandrake/Pyrelands/northstar_site.py
file: src/RimMandrake/Pyrelands/validation.py
