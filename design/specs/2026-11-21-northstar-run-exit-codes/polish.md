# Polish: northstar run exit codes

- 2026-11-21: `src/RimMandrake/Utils/northstar_bar_proof.py` prints `FAIL: the driver wrote no ... (exit 2)` and exits 1 when the driver REFUSED (bridge unreachable or dirty site); a refusal reads as a failed bar there. Not worth the touch: no test table or pipeline caller runs it (only `selftest_unproven_legs_triage.py` names it).
