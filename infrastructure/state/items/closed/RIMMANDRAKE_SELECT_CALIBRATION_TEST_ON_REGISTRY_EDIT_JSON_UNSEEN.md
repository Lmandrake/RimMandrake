## spec
RIMMANDRAKE_RECHECK_ADVANCE_CALIBRATION_TEST_PASSES_WITHOUT_ROW added selftest_calibration_rows_current.py: at the
./publish door it refuses a change whose free-check calibration rows (maturation_advance, evidence_gate) are missing or
not CALIBRATED at the brief's current hash. The door selects it only for a change to a .py file it names or imports
(publish.door_inputs reads .py files and same-stem .json only) that matches a pipeline_files pattern. So two changes
land with no recheck [measured 2026-11-18, acceptance test below 1/3]: a commit touching only
infrastructure/state/judge_calibration.json (deleting or hand-editing the maturation_advance row), and a commit touching
only src/RimMandrake/rimflow/evidence_gate_corpus.json (a brief file of evidence_gate, so status() goes UNTESTED).
Found by the Codex review of that item (D:\ClaudeWork\rimmandrake\conductor\codex_review_advance_calibration_row_20261118.md,
finding 2). Likely fix: let door_inputs take .json paths a test names as string literals (and add both paths to
pipeline_files); keep the unrelated-json control green.

## verify
python3 src/RimMandrake/rimflow/acceptance/calibration_registry_door_accept.py   # exit 0, "PASS 3/3"
Watched failing 2026-11-18 on the commit that added selftest_calibration_rows_current.py: rc 1, "FAIL 1/3".

## criteria
- A one-file change to judge_calibration.json or evidence_gate_corpus.json runs selftest_calibration_rows_current.py at
  the door; an unrelated .json change selects no pipeline test.

## refs
file: src/RimMandrake/Utils/publish.py
file: src/RimMandrake/Utils/pipeline_tests.json
