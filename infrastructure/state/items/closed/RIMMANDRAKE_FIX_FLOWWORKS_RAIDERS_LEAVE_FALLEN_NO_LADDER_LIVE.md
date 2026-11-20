# RIMMANDRAKE_FIX_FLOWWORKS_RAIDERS_LEAVE_FALLEN_NO_LADDER_LIVE

Caused by RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO (FlowWorks 0.1.0, in-game visit 2, game a, flowworks tier).

## spec

sc_fetch_fallen FAILed live (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_fetch_fallen_20261119T214154.json): FETCH_two_fell held ['Human21224'] (one, not two), FETCH_ladder_into_pit [] (no ladder came for the one held raider), control PASS. The offline decider T_FETCH_FALLEN_OFFLINE passed at closing of FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN (636550d40b36). Related open finding: RAIDER_CHOP_FIX_AXE_NEVER_LANDS (ladderless raiders take RM_RaiderChopForLadder jobs that never land). Not diagnosed further in the sitting (bound): first experiment, read the raiders' jobs while one is held (jawa job list) to see whether a chop job starts and stalls.

## verify

python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_fetch_fallen --out <json>: FETCH_two_fell, FETCH_ladder_into_pit, FETCH_fallen_brought_out PASS

## criteria

Acceptance test: none offline beyond T_FETCH_FALLEN_OFFLINE (green while the live row fails: the offline test cannot see it); live: the sc_fetch_fallen row.
