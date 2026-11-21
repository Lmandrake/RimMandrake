## spec
found-by: FlowWorks in-game visit 3, game a, flowworks tier, calm site, 2026-11-21 6:35 AM PST.
sc_source_pays row SRC_flow_stops_when_empty FAIL on the repaired check (design/concepts/FlowWorks/version/in_game/visit_3/evidence/sc_source_pays_20261121T063524.json):
the unlimited RM_FlowSink drew the pond to its wet line (800 pulses) and through 1700 film pulses, then its drained total stood
still at 559.996 while 80 core squares each still held 1 dL (the readout rounds to 0 L). His ruling POND_PUMP_FIX_LAST_DROP_COUNTS
("ponds pump to last dL") says the draw reaches 0 dL. Class MOD [guess ~65%]: the kernel stops a sink's draw on a 1 dL film; the
other reading (a 1 dL film is meant to stay and dry, not be drawn) is the Designer's to rule. Not fixed in the sitting: kernel work,
fix not known.
The check was repaired in the same sitting (6db14ea26c: it waited a flat 500 pulses for the wet line, so it read a pond still
draining as one that never stops); the repaired check reads FAIL on the offline planted cases film_stuck and endless_pond
(accept_source_pays_last_decilitre.py ok) and PASS on film_drains.

## verify
- `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_source_pays --out <json>`: SRC_flow_stops_when_empty PASS.

Acceptance test: the command above, SRC_flow_stops_when_empty PASS (rows other than SRC_lake_reads_endless PASS); watched red at
visit 3 6:35 AM PST (dry True, 0 L, max dL 1 on 80 squares, drained still). Offline: `python3 design/concepts/FlowWorks/version/in_game/visit_2/accept/accept_source_pays_last_decilitre.py` stays ok.

## refs
file: src/RimMandrake/FlowWorks/Source/RM_FlowKernel.cs
file: src/RimMandrake/FlowWorks/Source/MapControls

## stage (steward, RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_THREE_FAILURES_BACK, 2026-11-21)
needs offline. His ruling POND_PUMP_FIX_LAST_DROP_COUNTS ("ponds pump to last dL") settles the design question above: the draw
reaches 0 dL. The fault lives in code the C# SelfTest can drive without the game: `Building_RM_FlowSink.FlowPulse`
(MapControls/RM_FlowTaps.cs) takes only from `Reach()` and breaks on the first `took <= 0`, so a 1 dL film outside the reach
must be levelled toward the sink by the kernel (RM_FlowKernel / RM_LevelSolve; LevelExactChecks.cs and FlowKernelFuzz.cs already
run them). Offline acceptance: a C# SelfTest case that lays 80 squares at 1 dL each around an unlimited sink and pulses until
the drained total stops; red when any square keeps 1 dL, green when every square reaches 0 dL. Run it at the parent first (red),
then on the fix (green). If the offline case cannot reproduce the stall, return the item to `needs game-up` with that
evidence on it.
In-game check: test table stage-6 id `sc_source_pays` (row SRC_flow_stops_when_empty), live command
`python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_source_pays --out <json>`. The fixer records it
UNRUN for Stage 6 with `maturation.py unrun` when it closes this item on the offline test.
