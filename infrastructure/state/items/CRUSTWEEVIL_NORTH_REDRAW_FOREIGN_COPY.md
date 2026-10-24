## What is wrong
Found while calibrating CODEX_FOREIGN_COPY_GUARD_FIX_RESIZED: artpipe output `arteval_RM_Crustweevil_r2_north` sits at picture
distance 1.61 from `arteval_RM_TentacularPlant__AB_TentacularPlant_r1_f` (16x16 alpha-cropped thumbnail, mean abs diff; the
nearest legitimate pair measured is 7.05). It is very probably a resized foreign copy that the byte-only guard passed.
Evidence: /mnt/d/ClaudeWork/rimmandrake/guard_resize/calib.json, calib.out.

## To do
Look at both images; if Crustweevil north is the tentacular plant, find whether it was installed or judged, and redraw it
through the art-eval pipeline (the new guard now refuses this case).
