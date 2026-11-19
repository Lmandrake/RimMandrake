## spec
seed_and_land cleans the seeded record on a refusal and (since eb05bc2073) a timeout, but not when land.sh cannot start (PermissionError, FileNotFoundError), so later ticks read 'had a record' for good (item 6). Fix: OSError takes the same cleanup.
Pre-existing, found by the Codex full-file review of the split fixes (D:\ClaudeWork\rimmandrake\conductor\cr\r_ma_split_fixes.txt). Minimal diff inside maturation_autonomy.py.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py --all (section seed_any_exec_failure_cleans, red on 260b1dc67a, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Its section fails on base and passes after; selftest_maturation_autonomy stays green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
