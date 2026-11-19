## spec
_road_back: an item whose fixer launch failed (no unit) is excluded from todo because it has a book entry, so the row reads fixer_spent and _gate's retry (transient fault or fresh code, under launch_tries) is never reached (finding 3). Fix: an entry with failed and no unit stays in todo; _gate decides.
Parent RIMMANDRAKE_FIX_MATURATION_AUTONOMY_CODEX_REVIEW_FINDINGS. Minimal diff inside maturation_autonomy.py.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py (section road_back_retries_transient_fixer, 1 case(s) red on 796e441f35 with --all, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Its section fails on base and passes after; selftest_maturation_autonomy stays green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_autonomy
