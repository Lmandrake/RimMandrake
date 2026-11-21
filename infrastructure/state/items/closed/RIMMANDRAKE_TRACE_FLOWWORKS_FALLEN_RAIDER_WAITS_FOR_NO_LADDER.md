# RIMMANDRAKE_TRACE_FLOWWORKS_FALLEN_RAIDER_WAITS_FOR_NO_LADDER

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. It takes over RIMMANDRAKE_FIX_FLOWWORKS_RAIDERS_LEAVE_FALLEN_NO_LADDER_LIVE (filed by the visit driver; superseded by this filing so the maturation tick, which launches fixers on items caused by the steward run, finds it). Its prose stays in items/closed/RIMMANDRAKE_FIX_FLOWWORKS_RAIDERS_LEAVE_FALLEN_NO_LADDER_LIVE.md. Lowest stage that shows the fault: Stage 6 only (game-only).

## spec

Steward class: REAL MISS (mod, live-only).

sc_fetch_fallen FAILed (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_fetch_fallen_20261119T214154.json): FETCH_two_fell held ['Human21224'] (one, not two), FETCH_ladder_into_pit [] (no ladder came), control PASS. T_FETCH_FALLEN_OFFLINE passed at the close of FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN (636550d40b36). Related open finding: RAIDER_CHOP_FIX_AXE_NEVER_LANDS (ladderless raiders take RM_RaiderChopForLadder jobs that never land). First experiment: read the raiders' jobs while one is held, to see whether a chop job starts and stalls.

## verify

Stage 6 check: sc_fetch_fallen, `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_fetch_fallen --out <json>  (bridge held; flowworks tier)`.
Acceptance test: none offline, the cause is known only from a live experiment (no fake models it); the live row above is the test.

## refs

file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py

## criteria

- Raiders whose comrades fell into a pit bring a ladder (or chop and build one) and take their fallen out; FETCH_two_fell, FETCH_ladder_into_pit and FETCH_fallen_brought_out PASS.
