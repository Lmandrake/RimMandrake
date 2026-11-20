# RIMMANDRAKE_JUDGE_FLOWWORKS_DROWNED_BODY_COVER_BY_EYE

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. Lowest stage that shows the fault: Stage 6 only (game-only).

## spec

Steward class: CRITERION FLAW (the check cannot pass by its own reader).

PIT_LOOK_1114_LIVE read 19 PASS, 0 FAIL, 1 UNMEASURED (design/concepts/FlowWorks/version/in_game/visit_2/evidence/PIT_LOOK_1114_LIVE_20261119T222659.log). The one UNMEASURED row is `body_cover_is_a_look`: pit_look_1114_live.py:100 writes `row("body_cover_is_a_look", None, ...)` unconditionally; its docstring says 'stage a pawn in a pit with 2 m of clear water, zoom in, capture, and have a judge that did not make it compare body, head and hands against the surrounding water ... Recorded UNMEASURED here by design.' So no build can pass this check (CRITERION FLAW in the check's shape, the bar's meaning unchanged).

Refusal record: evidence = the log line and pit_look_1114_live.py:94-100; would_pass = a staged drowned pawn whose zoomed capture a naive judge (rm-judge, against design/RimMandrake/art_judge_brief.md) reads as covered by the water's tint; smallest_fix = the script stages the pawn and writes the capture, the judge's verdict file decides the row (or the row moves to the look lane LOOK_STAGE8 and PIT_LOOK_1114_LIVE keeps its 19 script rows), re-pinned in version/bars.md with a journal line.

## verify

Stage 6 check: PIT_LOOK_1114_LIVE, `python.exe src\RimMandrake\FlowWorks\northstar\pit_look_1114_live.py  (bridge held; FlowWorks deployed)`.
Acceptance test: none offline, the cause is known only from a live experiment (no fake models it); the live row above is the test.

## refs

file: src/RimMandrake/FlowWorks/northstar/pit_look_1114_live.py

## criteria

- PIT_LOOK_1114_LIVE reads PASS or FAIL: body cover is decided by a naive judge on a zoomed capture, and the other 19 rows keep their verdicts.
