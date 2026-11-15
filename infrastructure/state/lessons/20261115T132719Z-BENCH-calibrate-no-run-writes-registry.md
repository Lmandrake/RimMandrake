refusal_contract.py calibrate --no-run is not a read-only status: it rewrites infrastructure/state/judge_calibration.json (on 2026-11-15 it changed the coverage_judge row's hash c2940c3ffd7f1054 -> b181fc39756c9d7f and reset_at). To read calibration state without writing, read the JSON file itself (or git show HEAD:infrastructure/state/judge_calibration.json). The changed hash also shows the coverage judge brief was edited after its last reading and is UNTESTED.
item: NONE
home: src/RimMandrake/rimflow/refusal_contract.py
