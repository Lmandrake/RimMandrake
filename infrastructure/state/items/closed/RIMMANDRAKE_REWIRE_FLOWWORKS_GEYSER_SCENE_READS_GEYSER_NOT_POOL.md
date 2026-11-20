# RIMMANDRAKE_REWIRE_FLOWWORKS_GEYSER_SCENE_READS_GEYSER_NOT_POOL

Caused by RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO (FlowWorks 0.1.0, in-game visit 2, game a, flowworks tier).

## spec

sc_geyser_tub FAILed (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_geyser_tub_20261119T214557.json): `_geyser_tub` inspects the SteamGeyser thing's string and looks for a 'HotSpring' need after 30000 ticks with no order to soak. Experiment in the sitting: geyser_pit_scene.py stage then geyser_tub_live.py on the same build and map (design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/geyser_tub_live.json) PASS 4 of 4: the pit cell reads 'Hot tub', a dry pit and a pit beside the geyser do not, a pawn soaks (RM_HotPoolSoak) and keeps RM_HotPoolAfterglow. HARNESS: the scene should read the pool cell's terrain readout and the RM_HotPoolSoak/Afterglow hediffs (or call geyser_tub_live's reads).

## verify

python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_geyser_tub --out <json>: TUB_reads_hot_tub and TUB_pawn_soaks_bonus PASS

## criteria

Offline: a selftest of scene_geyser_tub against a fake map whose geyser thing has no 'Hot tub' text but whose pool cell does (red on today's scene).
