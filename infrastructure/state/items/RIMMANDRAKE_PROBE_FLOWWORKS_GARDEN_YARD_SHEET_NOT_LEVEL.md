# RIMMANDRAKE_PROBE_FLOWWORKS_GARDEN_YARD_SHEET_NOT_LEVEL

Caused by RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO (FlowWorks 0.1.0, in-game visit 2, game a, flowworks tier).

## spec

sc_garden GARDEN_walled_yard_lies_level FAILed (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_garden_20261119T214405.json): SPILL offered=15000 accepted=15000; SHEETRECT dl=7798 wet=25 maxDl=461 (mean 312) film=21 sheet=4. Not diagnosed in the sitting (bound): either the yard ground has relief (a level surface gives unequal depths, and the row checks equal depth), the sheet had not settled when read, or the sheet kernel leaves a mound. First experiment: read the yard squares' ground heights and re-read after more ticks. Every other sc_garden row PASSed, including the owed caller rows (head draws its net, no pump no spray, faucet, filter rate, still rate, drill pours and charges what landed).

## verify

python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_garden --out <json>: GARDEN_walled_yard_lies_level PASS (or the row re-pinned to surface level if the ground has relief)

## criteria

Acceptance test: none offline yet, the cause is not known; live: the sc_garden row.
