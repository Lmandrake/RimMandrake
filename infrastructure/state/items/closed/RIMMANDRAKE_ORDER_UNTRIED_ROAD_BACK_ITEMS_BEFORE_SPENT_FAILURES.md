## spec
Regression introduced by RIMMANDRAKE_RETRY_ROAD_BACK_FIXER_AFTER_TRANSIENT_LAUNCH_FAIL (f9ebc4f931), found by the Codex full-file review of the split fixes (D:\ClaudeWork\rimmandrake\conductor\cr\r_ma_split_fixes.txt, item 1): with open road-back items [A, B], A failed three times (retries spent) and B never launched, _road_back picked A every tick and _gate refused it, so B never ran. Fix: untried items go first in todo, failed-with-no-unit ones after.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py (section road_back_retries_transient_fixer, the two-item case red on bcb440c842, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- The two-item case passes; selftest_maturation_autonomy stays green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
