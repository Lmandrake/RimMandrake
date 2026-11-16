# RELENTLESS_REMEASURE_TICK_P95_DETACH_NEXT

## spec

WP-10a re-measure: record tick wall p50/p95 over >=100 live ticks with prof.py (wp10a/ in the redesign dir; before was 118 ticks p50 327/p95 499 s, after only 2 ticks). Then pick the next detach candidates by measured cost: relentless_wall.make_box in step (1362 s over 118 ticks, the Marker box build), relentless_integrity.clone_damage nul_or_empty (829 s), clean_checkout _detached_clone (763 s). The steps phase is now ~68% of the tick.

Done when: an after.txt over >=100 ticks reports p95 and the top slow phases, and a detach is filed or landed for each phase still over budget.

Source: /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/stage4_log.md WP-10a FOLLOWUPS; wp10a/before.txt, after.txt
