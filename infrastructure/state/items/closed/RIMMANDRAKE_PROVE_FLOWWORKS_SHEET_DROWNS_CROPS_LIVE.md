# RIMMANDRAKE_PROVE_FLOWWORKS_SHEET_DROWNS_CROPS_LIVE

Filed by the detached helper on RIMMANDRAKE_CLEAR_FLOWWORKS_PAPERWORK_TO_GAME_ONLY_ROAD (FlowWorks 0.1.0, the game-only road). Bar `inv_overflow_sheet`; source event `SHEET_GAME_SIDE_NOT_KERNEL`. One ticket per source event.

## spec
Lane 1 of blind cycle 4 left `SHEET_GAME_SIDE_NOT_KERNEL` UNSETTLED (`design/concepts/FlowWorks/version/blind_challenge/cycle_4/lane2/lane1_rows_after_fix.jsonl`): the kernel and its caller pass offline, but no offline test can show that (a) crops standing in the overspill sheet are actually killed by the CropDrowning report on a live map, and (b) each FluidDef's authored soak and drying percents act on the live map. `sc_garden` does not stage this (its header: only the walled yard lies level). The overspill ships switched off (`RM_SheetSettings.sheetOverflowEnabled = false`), so the scene must switch it on and restore it.

The scene that decides it: `src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py` row `CROPS_IRRIGATE_THEN_DROWN` (function `crops`), on the deployed build, with `sheetOverflowEnabled` on; plus one row per sheet-carrying FluidDef (water, chemfuel, tar) that the film on open ground soaks in and dries at that def's authored rate, read from the map, not from the def. Record the result in the visit's rows; add the proof to `test_table.json` as a stage-6 supporter of `inv_overflow_sheet` if the table still lacks it.

Acceptance test: none offline, live-game behaviour (the cycle-4 judge recorded that no offline test can show it). The live command is under verify; record it UNRUN with `maturation.py unrun` if the visit does not reach it.

## verify
python.exe src\RimMandrake\FlowWorks\northstar\sheet_overflow_proof.py (rows crops and the per-fluid soak/drying rows) on the minimal flowworks tier, results to D:\ClaudeWork\rimmandrake\evidence\flowworks_visit2\sheet_crops.json

## criteria
CROPS_IRRIGATE_THEN_DROWN PASS (crops in the sheet die; dry crops live) and each fluid's soak/drying row PASS on the live map; the lane-1 row is then settled by that evidence.

## refs
file: src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py
file: src/RimMandrake/FlowWorks/Source/Sheet/RM_MapComponent_Sheet.cs
file: src/RimMandrake/FlowWorks/Source/Sheet/RM_SheetSettings.cs
tier: flowworks
