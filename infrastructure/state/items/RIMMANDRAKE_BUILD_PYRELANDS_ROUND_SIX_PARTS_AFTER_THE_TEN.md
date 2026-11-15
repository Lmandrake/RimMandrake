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

## Acceptance test

`python3 src/RimMandrake/Pyrelands/selftest_pyrelands_round6_gaps.py --entry-points` exits 0 (every scene owed by this
item has its entry point in its script); watched it fail on the filing base (sc_furnace_hide_bank's furnace_hide_bank is
not in validation.py). It proves the entry points, not the reads: the live half of each row is the scene's
`live_command`, recorded UNRUN until a sitting runs it with the bridge.
