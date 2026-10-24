# ART_EVAL_SHADOW_FIX_PLANT_KEPT_ROWS

shadow.py build failed its art_sheet gate on three of six gptredo runs:
- gptredo_03 / gptredo_04 (plants RM_AgariluxPrime, RM_Ruskara): req 2 'no row has art' - the sheet cannot find
  plant art for these subjects. Related: art.py status shows 0 variants for Graphic_Random RM_Ruskara (art-ledger
  blind spot?).
- gptredo_01 (RSW_Gizka): req 15 - installed GizkaW_north.png sha 1172ecf05b75 shown only as a canonregen render.
Owed: the owner's shadow sheet for these runs, including the kept-art redraw rows (Gizka, Clodhopper) with REVERT.
Sheets for gptredo_00, 01b, 02 built under Transient/biome_ffar/.

Evidence: D:\ClaudeWork\rimmandrake\art_eval\gptredo\ and infrastructure/state/art_eval/runs/gptredo_*. Found during GPTREDO_JUDGE_UNJUDGED_ROWS (2026-10-24).
