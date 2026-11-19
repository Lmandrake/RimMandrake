## spec
autolock_and_land writes VERSION.json and the delegated record before its rollback try, so a failure creating the delegated folder leaves VERSION.json locked with no record and version_locked() reads true (finding 2). Fix: the writes go inside the try that restores both files.
Parent RIMMANDRAKE_FIX_MATURATION_AUTONOMY_CODEX_REVIEW_FINDINGS. Minimal diff inside maturation_autonomy.py.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py (section autolock_failure_before_landing_rolls_back, 1 case(s) red on 796e441f35 with --all, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Its section fails on base and passes after; selftest_maturation_autonomy stays green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_autonomy
