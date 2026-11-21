# RIMMANDRAKE_STAGE_FLOWWORKS_ICE_CUT_SHOVEL_KEEP_FROZEN

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. It takes over RIMMANDRAKE_STAGE_FLOWWORKS_ICE_SCENE_SHOVEL_LEFT_AT_HOME (filed by the visit driver; superseded by this filing so the maturation tick, which launches fixers on items caused by the steward run, finds it). Its prose stays in items/closed/RIMMANDRAKE_STAGE_FLOWWORKS_ICE_SCENE_SHOVEL_LEFT_AT_HOME.md. Lowest stage that shows the fault: Stage 6 only (game-only).

## spec

Steward class: REAL MISS (harness), with a live unknown left.

sc_ice FAILed (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_ice_20261119T213243.json). Two harness faults found by experiment: (1) `_ice` stages no shovel, so RM_DigCanalWorkGiver says 'Needs a shovel (none free on the map).' (design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/ice_noshovel.json); (2) `_ice_cut` reads the probe's own second designation ('Already being dug.') as a mod refusal. With both changed (design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/ice_noshovel_desig.json) every row reads UNMEASURED: the ordered cut does not land in 6000 ticks and the ice is gone at the last poll (iceAtLastPoll 0); the open-water control gets no job (the work giver deletes the designation on WaterShallow). Fix the two harness faults (shovel_stage.give_shovel, as extensions.py _stage_shovel; accept an existing designation), hold the ice frozen until the cut lands (temperature lock), then learn live whether the open-water control is the mod's rule.

## verify

Stage 6 check: sc_ice, `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_ice --out <json>  (bridge held; flowworks tier)`.
Acceptance test: none offline, the cause is known only from a live experiment (no fake models it); the live row above is the test.

## refs

file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py

## criteria

- sc_ice's rows read PASS or FAIL on the mod's behaviour: a shovel is staged, the cut lands on frozen ice, the control is decided.
