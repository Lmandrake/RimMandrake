# ARTEVAL_REGEN_CANVAS_FIX_HARDCODED_SIZE

Owner, on owner_escalations_leaningscrub_1 2026-10-24 (RM_Chikka): "What's with the HUGE resolution on the 10-24 version? The original one was fine."

## Defect
`src/RimMandrake/Utils/art_eval/runner.py:470` (regen_jobs, used by `run --file-regens`) writes every regen job with
`canvas_w/canvas_h 1024` and `reference ""`. The artpipe validator skips a job with no reference, so a full-bleed
1024 creature ships to the sheet; fauna_drive's canvas_for uses the shipping rule (Chikka r3 came out 256). Every r2
render on both leaningscrub escalation sheets is 1024 (Surrik, Durrok, Chikka ...). No reviewer code caught it:
Opus said "good" on Chikka r2.

## Fix wanted
regen_jobs takes canvas from fauna_drive.canvas_for / the live texture and passes the live texture as reference;
plus a deterministic pre-judge canvas gate (canvas != shipping rule, or content bbox scale vs live > ~1.3x =>
SCALE/F_SIZE_JUMP blocking, no model call). Selftest + `runner.py regress` (a policy change).
Criteria ledger: CL-019 (Chikka), CL-021 (Durrok V_B is ~1.5x the base for the same reason).
Evidence: enact dry runs /home/mandrake/.seat-tmp/FOUNDRY/ls1_enact_dry.txt, ls1_enact_apply.txt; verdict dump ls1_verdicts.txt; sheet Transient/biome_ffar/owner_escalations_leaningscrub_1_sheet_2026-10-24.decisions.json; run infrastructure/state/art_eval/runs/owner_escalations_leaningscrub1_20261024/.
