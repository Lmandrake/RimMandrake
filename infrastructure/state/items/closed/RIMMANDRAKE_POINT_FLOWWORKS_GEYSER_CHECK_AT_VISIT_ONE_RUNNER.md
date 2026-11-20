# RIMMANDRAKE_POINT_FLOWWORKS_GEYSER_CHECK_AT_VISIT_ONE_RUNNER

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. It takes over RIMMANDRAKE_REWIRE_FLOWWORKS_GEYSER_SCENE_READS_GEYSER_NOT_POOL (filed by the visit driver; superseded by this filing so the maturation tick, which launches fixers on items caused by the steward run, finds it). Its prose stays in items/closed/RIMMANDRAKE_REWIRE_FLOWWORKS_GEYSER_SCENE_READS_GEYSER_NOT_POOL.md. Lowest stage that shows the fault: offline (the check's command and the scene's reads).

## spec

Steward class: RECORD GAP on the check (the build was shown right by the real runner; the table runs the draft).

sc_geyser_tub FAILed (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_geyser_tub_20261119T214557.json). test_table.json's sc_geyser_tub runs concept_scenes.scene_geyser_tub, whose `_geyser_tub` inspects the SteamGeyser cell and waits for a 'HotSpring' need. geyser_tub_live.py (visit 1; its docstring: 'The draft scene_geyser_tub read inspect_string and a HotSpring need, which the mod never writes; this replaces it') read PASS 4 of 4 on the same build and map after geyser_pit_scene.py stage (design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/geyser_tub_live.json). Fix: point sc_geyser_tub at geyser_pit_scene.py stage + geyser_tub_live.py (a command change, re-pinned with a journal line), or make scene_geyser_tub use the same reads (ProofPitLabel on the pool cell, an ordered RM_SoakInGeyserPool, RM_HotPoolSoak and RM_HotPoolAfterglow).

## verify

Offline: `python3 design/concepts/FlowWorks/version/in_game/visit_2/accept/accept_geyser_tub_reads_the_pool.py` exit 0.
Stage 6 check: sc_geyser_tub, `python.exe src\RimMandrake\FlowWorks\northstar\geyser_pit_scene.py <out> stage` then `python.exe src\RimMandrake\FlowWorks\northstar\geyser_tub_live.py <out.json>` (or the rewired scene); recorded UNRUN with `maturation.py unrun` at close.

## launch-checks
must-fail: python3 design/concepts/FlowWorks/version/in_game/visit_2/accept/accept_geyser_tub_reads_the_pool.py

(Watched exit 1 on 2026-11-19 at the steward run's base. It is a refusal guard; the acceptance test is the one in ## verify.)

## refs

file: design/concepts/FlowWorks/version/test_table.json
file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
file: src/RimMandrake/FlowWorks/northstar/geyser_tub_live.py

## criteria

- The command that decides sc_geyser_tub reads the pool cell's Hot tub label and the soak hediffs, never a HotSpring need.
