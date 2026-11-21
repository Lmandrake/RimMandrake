# RIMMANDRAKE_READ_FLOWWORKS_PAWN_HEIGHT_CONTROL_SINK_NONE

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. Lowest stage that shows the fault: Stage 6 only (game-only).

## spec

Steward class: RECORD GAP in the read, cause unknown.

sc_pawn_height read UNMEASURED twice (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_pawn_height_20261119T213631.log timeout 220 s; design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_pawn_height_20261119T220537.json at 510 s): PH_offset_follows_depth and PH_swims_and_tires_at_2m PASS; PH_control_undug_no_offset UNMEASURED: sinks [0.0, None, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, None, 0.0] (samples 1 and 8 None). First experiment: log the raw reply of the sink read at each sample to see why it returns nothing (a pawn between cells, a busy bridge, or a refused read).

## verify

Stage 6 check: sc_pawn_height, `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_pawn_height --out <json>  (bridge held; flowworks tier)`.
Acceptance test: none offline, the cause is known only from a live experiment (no fake models it); the live row above is the test.

## refs

file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py

## criteria

- PH_control_undug_no_offset reads every sample, and PASSes when each reads 0 on undug ground.
