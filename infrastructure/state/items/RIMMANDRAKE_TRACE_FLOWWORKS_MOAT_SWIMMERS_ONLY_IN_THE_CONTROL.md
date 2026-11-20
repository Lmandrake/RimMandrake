# RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_SWIMMERS_ONLY_IN_THE_CONTROL

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. It takes over RIMMANDRAKE_PROBE_FLOWWORKS_MOAT_RAIDERS_SWIM_ONLY_WHEN_BRIDGED (filed by the visit driver; superseded by this filing so the maturation tick, which launches fixers on items caused by the steward run, finds it). Its prose stays in items/closed/RIMMANDRAKE_PROBE_FLOWWORKS_MOAT_RAIDERS_SWIM_ONLY_WHEN_BRIDGED.md. Lowest stage that shows the fault: Stage 6 only (game-only).

## spec

Steward class: REAL MISS, cause unknown (harness or mod).

sc_moat_raid FAILed (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_moat_raid_20261119T214016.json): MOAT_raiders_swim swimmers [] over 25 polls (last positions x 64-89, z 53-81), MOAT_two_held_and_captured UNMEASURED (none held), MOAT_control_bridge_down_no_swim FAIL (Human24618 and Human24640 swam with the bridge down). MOAT_drains_fast, MOAT_chemfuel_pumped, MOAT_moat_burns PASS. Not separated: whether the main run's raiders ever reached the moat (site geometry, harness) or the swim path is chosen only when a bridge is also in play (mod). First experiment: log the raiders' path targets and distance to the moat ring each poll.

## verify

Stage 6 check: sc_moat_raid, `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_moat_raid --out <json>  (bridge held; flowworks tier)`.
Acceptance test: none offline, the cause is known only from a live experiment (no fake models it); the live row above is the test.

## refs

file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py

## criteria

- With the bridge raised raiders swim the filled moat; with it down they cross the bridge and nobody swims; every sc_moat_raid row PASSes.
