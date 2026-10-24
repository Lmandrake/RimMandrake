# ART_EVAL_REGEN_FIX_FILING_GATE_REFUSES

runner.py --file-regens writes regen prompts that artpipe/fill_queue.py's per-facing filing gate refuses: the
preamble/edits contain 'top-down-friendly', 'consistent across all facings', 'the three facings', 'overhead'.
Seen in gptredo_00 (Harrok/Mirrak/Pirrik), gptredo_01 (Gizka/Clodhopper) and fauna_contagion_r2_00. Workaround used:
reworded copies (gptredo_0{0,1}/regen_jobs_filing in the evidence dir, gptredo_*_jobs_filing.json), filed by hand,
regen_filing.json written by hand. Also: the departures brief for RM_Pirrik asked for an unrenderable scene (gloomcast
shadow on sand, multi-view sentence) which went into the prompt.

Fix: the regen prompt template must speak per-facing (one view) language and pass the same gate before filing;
departures briefs must not ask for scene/background content. Add a selftest that runs the gate on a generated prompt.

Evidence: D:\ClaudeWork\rimmandrake\art_eval\gptredo\ and infrastructure/state/art_eval/runs/gptredo_*. Found during GPTREDO_JUDGE_UNJUDGED_ROWS (2026-10-24).
