# RIMMANDRAKE_REPIN_FLOWWORKS_SOURCE_PAYS_STOP_AT_LAST_DECILITRE

Caused by RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO (FlowWorks 0.1.0, in-game visit 2, game a, flowworks tier).

## spec

sc_source_pays FAILed on SRC_flow_stops_when_empty (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_source_pays_20261119T213541.json): pond not dry after 5x100 pulses, sink drained 502.6 then 514.3 L. Experiment (design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/source_pays_long.json, 25x100 pulses): every pond square reads at or below the wet line (dry True), yet the sink still drained 545.4 then 548.35 L with 53 L left. His ruling POND_PUMP_FIX_LAST_DROP_COUNTS ('ponds pump to last dL') says the sink should keep drawing the film, so the row's test (stopped once every square is under the wet line) asks for what the ruled build must not do. Likely a CRITERION FLAW in the scene, not the mod; a neutral fixer re-pins the row to 'the drained total stops changing once the pond's litres reach 0' and checks the litres do reach 0. SRC_lake_reads_endless stays owed on the river site.

## verify

python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_source_pays --out <json>: SRC_flow_stops_when_empty PASS on a pond pumped to 0 L

## criteria

Offline: python3 src/RimMandrake/FlowWorks/northstar/selftest_source_pays_scene.py gains a case where the fake pond keeps a film under the wet line that the sink still draws; the row must not read FAIL until litres reach 0 (red on today's scene).
