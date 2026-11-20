# RIMMANDRAKE_REPIN_SOURCE_PAYS_FILM_IS_NOT_A_LEAK

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. It takes over RIMMANDRAKE_REPIN_FLOWWORKS_SOURCE_PAYS_STOP_AT_LAST_DECILITRE (filed by the visit driver; superseded by this filing so the maturation tick, which launches fixers on items caused by the steward run, finds it). Its prose stays in items/closed/RIMMANDRAKE_REPIN_FLOWWORKS_SOURCE_PAYS_STOP_AT_LAST_DECILITRE.md. Lowest stage that shows the fault: offline (the scene's pure half, fake engine).

## spec

Steward class: CRITERION FLAW (the check demands what the ruled build must not do), bar source_pays_and_refills keeps its meaning.

sc_source_pays read SRC_flow_stops_when_empty FAIL (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_source_pays_20261119T213541.json): after 5x100 pulses the sink had drained 502.6 then 514.3 L. The driver's longer run (design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/source_pays_long.json, 25x100 pulses): every pond square at or under the wet line, yet the sink still drew 545.4 then 548.35 L with 53 L left. His ruling POND_PUMP_FIX_LAST_DROP_COUNTS ('GPT review Q6 -> ponds pump to last dL') says the sink must draw that film. The row (concept_scenes._source_pays) stops its loop once every square is under the wet line and then asks the drained total to stand still, so it FAILs the ruled build and PASSes a build that stops with the film left (the old last-dL bug).

Refusal record: evidence = the two JSON files above; would_pass = a pond that drains to 0 L and then the sink's drained total stands still; smallest_fix = keep pulsing until the pond's litres read 0 (or a bound with UNMEASURED past it), then judge 'drained total unchanged and litres 0'. The bar's words are unchanged, so the row text is re-pinned in version/bars.md with a journal line (re-pin rule, 2026-11-14).

## verify

Offline: `python3 design/concepts/FlowWorks/version/in_game/visit_2/accept/accept_source_pays_last_decilitre.py` exit 0 (film_drains PASS, film_stuck FAIL, endless_pond FAIL), and `python3 src/RimMandrake/FlowWorks/northstar/selftest_source_pays_scene.py` still exit 0.
Stage 6 check: sc_source_pays, `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_source_pays --out <json>  (bridge held; flowworks tier)`; the fixer records it UNRUN with `maturation.py unrun` when it closes on the offline test.

## launch-checks
must-fail: python3 design/concepts/FlowWorks/version/in_game/visit_2/accept/accept_source_pays_last_decilitre.py

(Watched exit 1 on 2026-11-19 at the steward run's base. It is a refusal guard; the acceptance test is the one in ## verify.)

## refs

file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
file: src/RimMandrake/FlowWorks/northstar/selftest_source_pays_scene.py
file: design/concepts/FlowWorks/version/in_game/visit_2/accept/accept_source_pays_last_decilitre.py
file: design/concepts/FlowWorks/version/bars.md

## criteria

- SRC_flow_stops_when_empty PASSes only when the pond's litres reach 0 and the sink's drained total then stands still.
- A sink that stops with film left reads FAIL, never PASS; the other source_pays rows keep their verdicts in the selftest.
