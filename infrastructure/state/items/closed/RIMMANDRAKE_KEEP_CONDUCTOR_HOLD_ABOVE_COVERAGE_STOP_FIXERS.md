## spec
resolve runs the final-stop and coverage-stop branches before the HOLDS branch, so a held row on a coverage-stopped mod becomes a fix-ticket fixer and launches (item 2): nothing automatic may route past a Conductor hold. Fix: a held row reads no Designer state, as live and settling rows already do.
Pre-existing, found by the Codex full-file review of the split fixes (D:\ClaudeWork\rimmandrake\conductor\cr\r_ma_split_fixes.txt). Minimal diff inside maturation_autonomy.py.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py --all (section hold_beats_coverage_stop, red on 260b1dc67a, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Its section fails on base and passes after; selftest_maturation_autonomy stays green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
