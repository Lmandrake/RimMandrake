# RIMMANDRAKE_STAGE_FLOWWORKS_TRENCH_RAID_NEVER_CAME_CLOSE

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. Lowest stage that shows the fault: Stage 6 only (game-only).

## spec

Steward class: RECORD GAP in staging (the event never happened).

sc_trench_cover read UNMEASURED (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_trench_cover_20261119T213212.json): TR_trench_pawn_covered, TR_trench_hit_falls and TR_control_open_ground_no_cover PASS; TR_no_raider_shelters_in_pit UNMEASURED (HARNESS): 'the raid never came within 3 squares of the trench or pit (raiders seen 7 ...)'. The scene must stage the raid so it passes the trench and pit (an arrival spot and a goal on the far side, or a drafted target), then read whether any raider shelters in the pit.

## verify

Stage 6 check: sc_trench_cover, `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_trench_cover --out <json>  (bridge held; flowworks tier)`.
Acceptance test: none offline, the cause is known only from a live experiment (no fake models it); the live row above is the test.

## refs

file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py

## criteria

- TR_no_raider_shelters_in_pit reads PASS or FAIL on a raid that came within 3 squares of the trench and pit.
