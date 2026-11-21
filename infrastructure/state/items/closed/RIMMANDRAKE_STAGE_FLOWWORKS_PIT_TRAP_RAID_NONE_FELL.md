# RIMMANDRAKE_STAGE_FLOWWORKS_PIT_TRAP_RAID_NONE_FELL

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. Lowest stage that shows the fault: Stage 6 only (game-only).

## spec

Steward class: RECORD GAP in staging (or a mod fault), cause unknown.

sc_pit_trap_raid read UNMEASURED (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_pit_trap_raid_20261119T214307.json): PTR_two_fall {'raidersSeen': 11, 'polls': 40, 'refused': 0, 'held': []}, PTR_fallen_become_prisoners 'nobody fell', PTR_control_open_pit_no_one_falls held [] (vacuous without a main-run fall). Not decided: the raid never crossed the covered pit (staging) or raiders crossing a covered pit do not fall (mod; FLOWWORKS_PIT_FALL_ONLY_FORCED_1 and PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO are his rulings on falls). First experiment: log each raider's path against the covered cells per poll.

## verify

Stage 6 check: sc_pit_trap_raid, `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_pit_trap_raid --out <json>  (bridge held; flowworks tier)`.
Acceptance test: none offline, the cause is known only from a live experiment (no fake models it); the live row above is the test.

## refs

file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py

## criteria

- PTR_two_fall, PTR_fallen_become_prisoners and the control read PASS or FAIL on a raid that crossed the covered pit.
