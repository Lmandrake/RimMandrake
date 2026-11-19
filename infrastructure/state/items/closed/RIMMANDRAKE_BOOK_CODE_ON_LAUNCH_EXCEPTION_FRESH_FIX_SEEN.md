## spec
execute's exception handler books a launch failure without cfg['_code'], so _gate never sees fresh code after the fix lands and the item stays spent (finding 5). Fix: book the code as _execute_one does.
Parent RIMMANDRAKE_FIX_MATURATION_AUTONOMY_CODEX_REVIEW_FINDINGS. Minimal diff inside maturation_autonomy.py.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py (section launch_exception_books_code, 2 case(s) red on 796e441f35 with --all, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Its section fails on base and passes after; selftest_maturation_autonomy stays green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_autonomy
