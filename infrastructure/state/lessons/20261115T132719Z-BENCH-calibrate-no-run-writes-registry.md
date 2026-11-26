A refusal_contract.py run you meant as a read writes the judge registry: refusal_contract.py calibrate --no-run is not a read-only status, and neither is the calibration status read or calibrate --help: each rewrites infrastructure/state/judge_calibration.json. To read calibration state without writing, read the JSON file itself (or git show HEAD:infrastructure/state/judge_calibration.json), and check git status after any refusal_contract.py run and drop a change you did not mean.

Sightings:
- 2026-11-15, calibrate --no-run: it changed the coverage_judge row's hash c2940c3ffd7f1054 -> b181fc39756c9d7f and reset_at. The changed hash also shows the coverage judge brief was edited after its last reading and is UNTESTED.
- 2026-11-19, refusal_contract.py calibration (a status read): the Conductor's clone had an edited infrastructure/state/judge_calibration.json that blocked ./sync; check git status after a status command on that file and drop the change.
- 2026-11-25, calibrate --help: refusal_contract.py calibrate ignores --help and runs a full calibrate. It writes infrastructure/state/judge_calibration.json, and it resets every family whose brief hash moved, other seats' families included (seven on 2026-11-25: CALIBRATED rows went to UNTESTED). When one edit moves one family's hash, recalibrate only that row: run its free_check with refusal_contract.run_check, then write it with _write. Do not commit the result of a full calibrate unless every reset is yours.
item: NONE
item: RIMMANDRAKE_COMPARE_TEST_PILOT_WITH_FABLE_RESCUER_ONE_MAY_HOLD_BOTH
home: src/RimMandrake/rimflow/refusal_contract.py
home: infrastructure/state/facts/tool_traps.md
