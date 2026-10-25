# ALMOST_OUT mode: Codex/GPT consultation log

Owner, 2026-10-24: *"start using CODEX consultations more aggressively on heavy items that will burn lots of tokens, if possible. Keep track of these attempts to see if it's actually helping."*

One row per attempt. **Saved Claude work** = yes / partial / no, judged by whether Claude had to redo the reasoning itself.

| date | seat | task (item) | what Codex was asked | result | saved Claude work | notes |
|---|---|---|---|---|---|---|
| 2026-10-24 | BENCH | perf audit (DEPLOY_PLAN_FIX_REDUNDANT_TREE_PASSES) | deep audit of deploy/verify slowness | ranked wins; top win confirmed in code, one idea rejected | yes | pre-mode baseline; fix cut plan 250 s → 117 s |
| 2026-10-24 | BENCH | design session (BRIDGES_DIG_DESIGN_THREE_WAYS_EACH) | 3 options × 3 areas | 9 options with cost/gotchas; 2 claims rejected vs code | yes | pre-mode baseline |
| 2026-10-24 | BENCH | second-workstation study | per-token value of a 2nd machine | conditional yes (script-driven runner only); overturned a wrong "80% offline" claim; its % gains unbaselined | partial | Sonnet still gathered all measurements |
| 2026-10-24 | BENCH | SteveDesktop bring-up plan | enhance a Claude-drafted plan | concrete reorder, 8 risks, 7 simplifications, sharper Wed measurement, Lodestar criteria; adopted nearly whole | yes | one consult, ~8 KB reply, replaced a design subagent |
| 2026-10-24 | BENCH | MODCHECK_SITE_FIX_RAIDS/MECHS fix review | full-file review of runner.py+suite.py diff | 3 real findings (fixture raiders exempt from later holds, tx enter/exit failures) fixed | yes | 1 of 3 passes |
| 2026-10-24 | BENCH | same, re-review | verify fixes + remaining bugs | 2 more real (failed hold still ran chain setup; test could touch live fixture ledger) fixed | yes | 2 of 3 |
| 2026-10-24 | BENCH | same, third pass | confirm NONE | NONE; files marked clean on it | yes | 3 of 3, 32 s |
| 2026-10-25 | BENCH | FILL_IN_FIXTURE_FIX_CRUSHES_COLONIST unroof fix review | diff since clean mark + new selftest_plot_unroof.py | NO FINDINGS; marked clean on it | yes | 1 pass |
| 2026-10-25 | BENCH | DRAWBRIDGE_BUILD_ONE_DRAG_DOES_IT_ALL review | diff since clean marks (C#+defs+northstar py) + new RM_DrawbridgePackage.cs, 77k chars | NO SIGNIFICANT FINDINGS; marked clean on it | yes | 1 pass |
| 2026-10-25 | BENCH | SUSPENSION_ISLANDS_BUILD_TOWERS_COST_PLENTY design | critique island-split + tower cost + restore-ground plan (math+designator+fill files) | 18 points; real: towers[0] per-lane bug, cancel must drop restore intent, outer ground runs, split spec, plan batch before place | partial/yes | 1 pass |
| 2026-10-25 | BENCH | SUSPENSION_ISLANDS_BUILD_TOWERS_COST_PLENTY review | diff (C#+defs+patch+northstar py) + full new/changed files, 141k chars | 1 med: a paused restore had no designation to Cancel; fixed (forget when no fill order can stand, pawn no longer pauses) | yes | 1 pass |
| 2026-10-25 | BENCH | SUSPENSION_ISLANDS_BUILD_TOWERS_COST_PLENTY re-review | Designator_RestoreGround.cs after fix | NO SIGNIFICANT FINDINGS; marked clean on r1+r2 | yes | 1 pass |
