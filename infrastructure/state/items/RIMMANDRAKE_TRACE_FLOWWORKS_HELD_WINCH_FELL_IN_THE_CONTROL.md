# RIMMANDRAKE_TRACE_FLOWWORKS_HELD_WINCH_FELL_IN_THE_CONTROL

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. Lowest stage that shows the fault: Stage 6 only (game-only).

## spec

Steward class: RECORD GAP in the control (or a mod fault), cause unknown.

sc_islands read UNMEASURED (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_islands_20261119T213413.json): the four main rows PASS (trapped while winches stand, raiders destroy a winch, a lost winch drops its leaf, raiders escape); the control ISL_control_unbreakable_winches_stay_trapped UNMEASURED: 'a held winch fell anyway [2, 19]; on an island [], leaves ['0', '0'], resets 100'. Not decided: the control's hold (how the scene makes a winch unbreakable) does not hold (harness), or the mod drops a leaf whose winch still stands (mod). First experiment: read the winch's HP and the hold flag each poll in the control.

## verify

Stage 6 check: sc_islands, `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_islands --out <json>  (bridge held; flowworks tier)`.
Acceptance test: none offline, the cause is known only from a live experiment (no fake models it); the live row above is the test.

## refs

file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py

## criteria

- The control's winches stay standing for the whole control and its raiders stay on the island, or a mod defect is filed with its test.
