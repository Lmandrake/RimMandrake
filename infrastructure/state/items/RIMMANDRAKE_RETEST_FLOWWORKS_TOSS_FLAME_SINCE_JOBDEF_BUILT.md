# RIMMANDRAKE_RETEST_FLOWWORKS_TOSS_FLAME_SINCE_JOBDEF_BUILT

Filed by the detached helper on RIMMANDRAKE_CLEAR_FLOWWORKS_PAPERWORK_TO_GAME_ONLY_ROAD (FlowWorks 0.1.0, the game-only road). Bar `inv_toss_flame`; source event `sc_toss_flame`. One ticket per source event.

## spec
In-game visit 1 failed `sc_toss_flame` (`design/concepts/FlowWorks/version/in_game/visit_1/rows.jsonl`, row `TOSS_picked_square_lights_first`: MOD, "Unknown JobDef 'RM_TossFlame'"). The order was built since (`RIMMANDRAKE_BUILD_FLOWWORKS_TOSS_FLAME_JOBDEF_STILL_UNKNOWN`, closed) and its offline test is green, but the scene has not run on the game since. Bars `inv_toss_flame` and `toss_flame_from_rim`; north-star line `toss_flame_from_rim`.

The scene that decides it: `concept_scenes.py --scene scene_toss_flame` (a chemfuel moat, the toss ordered on a square 6 cells from the nearest colonist, a water-moat twin), on the deployed build.

Acceptance test: none offline, live-game behaviour (the cycle-4 judge recorded that no offline test can show it). The live command is under verify; record it UNRUN with `maturation.py unrun` if the visit does not reach it.

## verify
python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_toss_flame --out D:\ClaudeWork\rimmandrake\evidence\flowworks_visit2\sc_toss_flame.json

## criteria
Every row of scene_toss_flame PASS: the colonist walks to the rim, the picked square lights first, the water twin does not light.

## refs
file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
tier: flowworks
