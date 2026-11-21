# RIMMANDRAKE_PROBE_FLOWWORKS_GARDEN_YARD_MOUND_RELIEF_OR_KERNEL

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. It takes over RIMMANDRAKE_PROBE_FLOWWORKS_GARDEN_YARD_SHEET_NOT_LEVEL (filed by the visit driver; superseded by this filing so the maturation tick, which launches fixers on items caused by the steward run, finds it). Its prose stays in items/closed/RIMMANDRAKE_PROBE_FLOWWORKS_GARDEN_YARD_SHEET_NOT_LEVEL.md. Lowest stage that shows the fault: Stage 6 only (game-only).

## spec

Steward class: REAL MISS, cause unknown.

sc_garden GARDEN_walled_yard_lies_level FAILed (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_garden_20261119T214405.json): SPILL offered=15000 accepted=15000; SHEETRECT dl=7798 wet=25 maxDl=461 (mean 312) film=21 sheet=4. Three candidate causes, not separated: the yard ground has relief (a level surface gives unequal depths, and the row checks equal depth), the sheet had not settled when read, or the sheet kernel leaves a mound. First experiment: read the yard squares' ground heights, then re-read the sheet after more ticks. If the ground has relief, the row is re-pinned to surface level (its bar's meaning unchanged). Every other sc_garden row PASSed.

## verify

Stage 6 check: sc_garden, `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_garden --out <json>  (bridge held; flowworks tier)`.
Acceptance test: none offline, the cause is known only from a live experiment (no fake models it); the live row above is the test.

## refs

file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py

## criteria

- GARDEN_walled_yard_lies_level reads PASS on a settled sheet whose surface (ground plus depth) is level, or the mound's cause is filed as a mod defect with its test.
