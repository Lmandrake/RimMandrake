# RIMMANDRAKE_PROVE_FLOWWORKS_DRILL_SURVEY_ROLLS_PER_BIOME_LIVE

Filed by the detached helper on RIMMANDRAKE_CLEAR_FLOWWORKS_PAPERWORK_TO_GAME_ONLY_ROAD (FlowWorks 0.1.0, the game-only road). Bar `inv_drilling`; source event `DRILL_RIGHT_MAPS_NOT_KERNEL`. One ticket per source event.

## spec
Lane 1 of blind cycle 4 left `DRILL_RIGHT_MAPS_NOT_KERNEL` UNSETTLED (`design/concepts/FlowWorks/version/blind_challenge/cycle_4/lane2/lane1_rows_after_fix.jsonl`): the bar says the drill finds liquid "on the right maps", which is the subsurface survey roll per biome (`RM_MapComponent_SubsurfaceLiquid` reading `RM_SubsurfaceLiquidBiomeExtension`). `sc_garden` SETS the yield, so it proves the pour, not which maps hold what (its header says so). No live test reads the roll today.

The scene that decides it: a new row set (in `concept_scenes.py` or a small proof beside it) that loads quicktest maps on tiles of at least two biomes whose extension Defs differ (one that should hold a subsurface liquid, one that should not), and reads the map component's survey result on each with no yield written by the test. This is reading the one existing planet, not worldgen: pick existing tiles, generate nothing.

Acceptance test: none offline, live-game behaviour (the cycle-4 judge recorded that no offline test can show it). The live command is under verify; record it UNRUN with `maturation.py unrun` if the visit does not reach it.

## verify
python.exe <the new survey proof> on two quicktest maps of different biomes (minimal flowworks tier), results to D:\ClaudeWork\rimmandrake\evidence\flowworks_visit2\drill_survey.json

## criteria
On each map the survey result matches that biome's extension Def (liquid present where the Def gives one, none where it does not), read with no yield set by the test; the lane-1 row is then settled by that evidence.

## refs
file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
file: src/RimMandrake/FlowWorks/Source/Drilling/RM_MapComponent_SubsurfaceLiquid.cs
file: src/RimMandrake/FlowWorks/Source/Drilling/RM_SubsurfaceLiquidBiomeExtension.cs
tier: flowworks
