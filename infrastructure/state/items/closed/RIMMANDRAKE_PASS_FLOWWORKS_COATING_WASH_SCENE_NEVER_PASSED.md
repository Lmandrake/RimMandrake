# RIMMANDRAKE_PASS_FLOWWORKS_COATING_WASH_SCENE_NEVER_PASSED

Filed by the detached helper on RIMMANDRAKE_CLEAR_FLOWWORKS_PAPERWORK_TO_GAME_ONLY_ROAD (FlowWorks 0.1.0, the game-only road). Bar `inv_liquid_coating`; source event `sc_coating_wash`. One ticket per source event.

## spec
`sc_coating_wash` has never passed. In-game visit 1 failed it (`design/concepts/FlowWorks/version/in_game/visit_1/rows.jsonl`, row `COAT_named_condition` FAIL: no coating condition after wading oil; `COAT_water_washes_it` passed vacuously). The coating was built since (`RIMMANDRAKE_BUILD_FLOWWORKS_COATING_WASH_PASSED_ON_NOTHING`, closed) and the scene's vacuous row was made honest, but the scene has not run on the game since. Bar `inv_liquid_coating` (added by his card of 2026-11-14); north-star line `liquid_coating_washes_off`. The open Polish note `RIMMANDRAKE_NOTE_FLOWWORKS_COATING_LAWS_MISS_COLONISTS` is not part of passing.

The scene that decides it: `concept_scenes.py --scene scene_coating_wash` (a pawn wades an oil pit and a blood pit; the condition shows in the health tab and the look is clean; he walks into water and both go), on the deployed build.

Acceptance test: none offline, live-game behaviour (the cycle-4 judge recorded that no offline test can show it). The live command is under verify; record it UNRUN with `maturation.py unrun` if the visit does not reach it.

## verify
python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_coating_wash --out D:\ClaudeWork\rimmandrake\evidence\flowworks_visit2\sc_coating_wash.json

## criteria
Every row of scene_coating_wash PASS, with COAT_named_condition seen before COAT_water_washes_it.

## refs
file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
file: src/RimMandrake/FlowWorks/Source/RM_LiquidCoating.cs
tier: flowworks
