## spec
seed_and_land: land.sh past its 300 s timeout raises TimeoutExpired before the cleanup that removes the seeded stage_record.json, so later ticks read 'had a record' and never seed again (finding 1). Fix: the timeout takes the same cleanup and raises RuntimeError.
Parent RIMMANDRAKE_FIX_MATURATION_AUTONOMY_CODEX_REVIEW_FINDINGS. Minimal diff inside maturation_autonomy.py.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py (section seed_timeout_leaves_no_record, 1 case(s) red on 796e441f35 with --all, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Its section fails on base and passes after; selftest_maturation_autonomy stays green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_autonomy
