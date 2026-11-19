## spec
A steward launch that raises after filing books item None (the handler reads row.get('item'), which _execute_one never set), and a retry whose republish fails books filed=False; either way the next retry files a second item instead of launching the first (item 4). Fix: _execute_one records the filed item on the row before launching; an established filed=True is never cleared by a failed republish.
Pre-existing, found by the Codex full-file review of the split fixes (D:\ClaudeWork\rimmandrake\conductor\cr\r_ma_split_fixes.txt). Minimal diff inside maturation_autonomy.py.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py --all (section filed_item_kept_on_failure, red on 260b1dc67a, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Its section fails on base and passes after; selftest_maturation_autonomy stays green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
