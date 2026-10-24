# ART_EVAL_SPEC_FIX_GRAPHIC_SINGLE_FACINGS

fauna_spec.py (src/RimMandrake/Utils/art_eval) ignores graphicData/graphicClass and always fills south/east/north
facing images. RSW_Mynock is Graphic_Single (texPath RimStarWars/SWBestiary/ShipVermin/Mynock/Mynock, also per
lifeStage in RSW_Mynock_PawnKind.xml), so run gptredo_01 judged Mynock_east/_north files the game never draws; that
row is void and Mynock was re-judged in gptredo_01b on images.single. It also always writes owner_kept:false, so kept
defs fall to HOLD_KEPT unless patched by hand (patch_specs.py in the evidence dir).

Fix: read graphicClass from the race def / PawnKind lifeStages; Graphic_Single -> images.single only;
Graphic_Random -> variants; set owner_kept + kept_install from art.py status PROTECTED. Add a selftest.

Evidence: D:\ClaudeWork\rimmandrake\art_eval\gptredo\ and infrastructure/state/art_eval/runs/gptredo_*. Found during GPTREDO_JUDGE_UNJUDGED_ROWS (2026-10-24).
