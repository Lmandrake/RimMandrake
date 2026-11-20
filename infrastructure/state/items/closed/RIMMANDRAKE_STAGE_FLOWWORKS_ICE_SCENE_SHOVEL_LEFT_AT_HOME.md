# RIMMANDRAKE_STAGE_FLOWWORKS_ICE_SCENE_SHOVEL_LEFT_AT_HOME

Caused by RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO (FlowWorks 0.1.0, in-game visit 2, game a, flowworks tier).

## spec

sc_ice FAILed in visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_ice_20261119T213243.json). Two harness faults, found by experiment in the sitting: (1) `_ice` in concept_scenes.py stages no shovel, so RM_DigCanalWorkGiver says 'Needs a shovel (none free on the map).' on the ice square; with `shovelRequired` off the work giver offers RM_DigCanalJob (design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/ice_noshovel.json). (2) `_ice_cut` designates the square with designate_batch, then reads the probe's own second designation ('Already being dug.') as a mod refusal and classes the row FAIL. With both changed (design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/ice_noshovel_desig.json) every row reads UNMEASURED: the ordered cut does not land in 6000 ticks and the ice is gone at the last poll (iceAtLastPoll 0); the open-water control gets no job (the work giver deletes the designation on WaterShallow). Fix: stage a shovel with shovel_stage.give_shovel (as extensions.py _stage_shovel does), accept an existing designation, keep the ice frozen until the cut lands (temperature lock), then find whether the open-water control is the mod's rule.

## verify

python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_ice --out <json>: rows ICE_cut_leaves_crushed_ice and ICE_melts_back_into_pond PASS, control PASS

## criteria

Offline: python3 src/RimMandrake/FlowWorks/northstar/selftest_ice_scene.py gains a case where the fake work giver refuses without a shovel and the scene must stage one (red before the fix). Live: the sc_ice row.
