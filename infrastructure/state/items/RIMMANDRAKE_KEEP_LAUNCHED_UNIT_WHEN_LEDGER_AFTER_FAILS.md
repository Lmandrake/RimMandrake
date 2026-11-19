## spec
_execute_one: MD.ledger_after raising after a successful launch lands in execute's handler, which books unit None / launch_failed for an active run, losing the road-back link and inviting a duplicate (finding 4). Fix: a ledger_after failure is reported in the launch text; the started unit is booked.
Parent RIMMANDRAKE_FIX_MATURATION_AUTONOMY_CODEX_REVIEW_FINDINGS. Minimal diff inside maturation_autonomy.py.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py (section ledger_after_failure_keeps_the_run, 1 case(s) red on 796e441f35 with --all, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Its section fails on base and passes after; selftest_maturation_autonomy stays green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_autonomy
