# RIMMANDRAKE_BUILD_PYRELANDS_ROUND_SIX_PARTS_AFTER_THE_TEN

## spec

Pyrelands 0.1.0 locked change (his card 2026-11-15 12:22 PM PST, "Fix the 17 gaps, one final look",
OWNER:1794774724955142310): RIMMANDRAKE_FIX_PYRELANDS_ROUND_SIX_SEVENTEEN_GAPS fixed the round-6 coverage gaps
(rm-coverage-judge-1794750987, design/concepts/Pyrelands/coverage_verdict.json) in design/concepts/Pyrelands/scenes.json.
Every scene that now carries `owed_parts_item` = this item asks for reads or stagings that
src/RimMandrake/Pyrelands/validation.py (or firehawk_rewards_live.py) does not make yet. Build them, script only, no
gameplay change, offline and live, per the project rule that the test is built with the item. Comes after
RIMMANDRAKE_BUILD_PYRELANDS_GAP_SCENE_PARTS_TEN_SCENES_OWED (same scenes, earlier parts); do not redo its parts.

The table below is the work list (scene, entry point, owed parts, gap). It is filled as each gap lands.

| scene | entry point | owed parts | gap |
|---|---|---|---|
| sc_furnace_hide_bank | validation.py::furnace_hide_bank (NEW chain) | whole scene: tundra quicktest map below 0 C, butcher a furnace-beast corpse, count RM_FurnaceHide, build RM_FurnaceHideBank from it in one of two twin closed rooms, assert no fuel/power comps, hourly room temperatures for 12 h | g1 |
| sc_walk | walk_season | the Mod enabled master (pyrelandsEnabled) off a day then on: front, ProbeAsh, bed fires | g4 |
| sc_scorchfruit | scorchfruit_fire_born | a second fresh burn with scorchFruitEnabled off reads 0 fruit | g4 |
| sc_ash_ground | ground_deep_ash | ash fall again with ashfallAccumulationEnabled off; clear half-day with ambientAshEnabled off | g4 |
| sc_roof_withers | validation.py::roof_withers (NEW chain) | whole scene: roofed and unroofed ember-grass patches read hourly for 2 days, again with PyrelandsMechanicsGate off | g5 |
| sc_herd_thirst | validation.py::herd_thirst (NEW chain) | whole scene: needs FlowWorks; RM_Thirst hourly on 4 ullai vs 4 muffalo, wild herds' starting levels, 7-day water arrivals by herd, toggle-off same-seed map | g5 |
| sc_ash_ground | ground_deep_ash | seed/tile asserted to roll water (regenerate on none); shore ring read; toggle-off regeneration; vanilla shore read; noon capture pair as-they-lie vs ClearAsh | g6, g7 |
| sc_no_rain | no_ordinary_rain | a GameCondition_ForceWeather forced to Rain on the Pyrelands map and on the vanilla control; read the weather after the change and an hour later | g8 |
| sc_heat_dome | heat_dome | ProbeDome bodyGraphic at +60 and after surfacing; two captures at play zoom for a judge | g9 |
| sc_furnace_giant | ullai_and_giant | body and draw size of every resolved roster kind (biome_probe), margin asserted | g10 |
| sc_firehawk_rewards | firehawk_rewards_live.py | the letter's label and text read for the hawk's LabelShortCap and the ember string; live crestfeather MarketValue vs RM_FireHawk's, Beauty | g11 |
| sc_burn_line_walks | burn_line | 24 hourly captures at play zoom with the hour asserted at each; one save while the front walks (burn_line_walking), kept | g13 |
| sc_burn_compounds | fresh_burn_bonus | vitals and pending incidents before the 7-day wait and at day 7 | g14 |
| sc_grass_regreens | embergrass_regrow | cover census first on a fresh map (no sow/spawn/set_terrain before it, from the call log), live plantDensity read; same-seed map at plantDensity 1.0 | g15 |
| sc_foreign_arrivals | foreign_arrivals | IncidentWorker_HerdMigration.CanFireNow on the Pyrelands map; executed migration brings RM_Ullai | g16 |

## Acceptance test

`python3 src/RimMandrake/Pyrelands/selftest_pyrelands_round6_gaps.py --entry-points` exits 0 (every scene owed by this
item has its entry point in its script); watched it fail on the filing base (sc_furnace_hide_bank's furnace_hide_bank is
not in validation.py). It proves the entry points, not the reads: the live half of each row is the scene's
`live_command`, recorded UNRUN until a sitting runs it with the bridge.
