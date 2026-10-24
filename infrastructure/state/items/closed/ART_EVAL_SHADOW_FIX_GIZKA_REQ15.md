# ART_EVAL_SHADOW_GIZKA_INSTALLED_AS_RENDER

Remaining half of ART_EVAL_SHADOW_FIX_PLANT_KEPT_ROWS. `shadow.py build gptredo_01` still fails art_sheet gate req 15:
RSW_Gizka's installed GizkaW_{south,east,north}.png (shas a2d1e6d4.., 6bca3a6c.., 1172ecf0..) are shown only as
'render canonregen_rsw_gizka_v1 - grader flagged (advisory)' (the --jobs render that is the same bytes), not as the
installed column. Needs an art_sheet decision: when the judged candidate is byte-identical to the installed file, show it
as installed (or relax req 15 for a candidate==installed row). Owed: owner shadow sheet for gptredo_01 (Gizka, Clodhopper
kept-art redraws with REVERT). gptredo_03/04 sheets now build (ebf6c468bf).
