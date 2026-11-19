## spec
_stop_tickets drops any ticket with a fixers entry, so a ticket whose fixer launch failed (no unit) reads spent without reaching _gate's retry (item 3). Fix: the same ordering as RIMMANDRAKE_ORDER_UNTRIED_ROAD_BACK_ITEMS_BEFORE_SPENT_FAILURES: untried tickets first, failed-no-unit ones after.
Pre-existing, found by the Codex full-file review of the split fixes (D:\ClaudeWork\rimmandrake\conductor\cr\r_ma_split_fixes.txt). Minimal diff inside maturation_autonomy.py.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py --all (section stop_tickets_retry_failed_launch, red on 260b1dc67a, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Its section fails on base and passes after; selftest_maturation_autonomy stays green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
