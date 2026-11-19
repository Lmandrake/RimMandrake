## spec
The Codex check of the maturation_autonomy repairs (D:\ClaudeWork\rimmandrake\conductor\cr\r_ma_split_repairs_check.txt) found two incomplete: (1) _road_back and _stop_tickets ordered untried items first but still put a spent failure (tries at launch_tries) ahead of a retriable one, so with both items failed the retriable one starved; (2) a steward retry whose republish RAISES lost its filed item (filed_item was set only after the republish). Fix: one retry rule _retriable(x, cfg) shared by _gate and both selectors (cfg passed through resolve and _route); filed_item set before the republish. The earlier road-back case used "TimeoutExpired: timed out", which transient() does not call transient; its fixture now names the transient fault its title claims.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py (sections spent_failure_never_starves_retry, raising_republish_keeps_filing; red on 4145666e04, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Both sections pass; selftest_maturation_autonomy and selftest_offline_stage_road_back stay green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
