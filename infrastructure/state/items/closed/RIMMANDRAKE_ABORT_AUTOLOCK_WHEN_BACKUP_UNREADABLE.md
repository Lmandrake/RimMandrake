## spec
autolock_and_land treats any OSError reading the old file as 'absent', so an existing writable-but-unreadable delegated record is overwritten and then deleted by the rollback when landing fails (item 7; reproduced: the file is gone). Fix: only FileNotFoundError means absent; any other read failure aborts before writing.
Pre-existing, found by the Codex full-file review of the split fixes (D:\ClaudeWork\rimmandrake\conductor\cr\r_ma_split_fixes.txt). Minimal diff inside maturation_autonomy.py.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py --all (section autolock_keeps_unreadable_record, red on 260b1dc67a, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Its section fails on base and passes after; selftest_maturation_autonomy stays green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
