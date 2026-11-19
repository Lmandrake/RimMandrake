## spec
src/RimMandrake/rimflow/acceptance/modledger_cutover_accept.py's last clause ("no writer of the old stores is left outside modledger") counts a .py that names stage.json / journal.md / stage_record.json anywhere AND writes any file at all. On 3e3f32e50 it lists 13 candidates; 8 of them only READ an old store or merely name one [measured, per-line evidence in D:\ClaudeWork\rimmandrake\conductor\cr\cutover_writer_candidates_20261118.txt]: Utils/modset_builder.py:961 (a path inside a "why" string), Utils/ops_watch.py:3820, rimflow/concept_tree.py:1161, rimflow/control.py:1540/1582/1840, rimflow/coverage_calibration.py:74 (a name list), rimflow/pipeline_control.py:394, rimflow/role_launch.py:2187/2715, rimflow/run_void.py:182/189. Real writers left: designer_stage.py, designer_cleanse.py, maturation_autonomy.py, maturation_rescue.py, Utils/maturation_now.py. The test's header says the builder does not edit it (a wrong clause goes to the Conductor), so this is the Conductor's to fix: count a file only when a write targets one of the three paths.
Acceptance test: none, the fix is to the oracle itself; a corrected clause is checked by listing exactly the five real writers above on 3e3f32e50.

## refs
file: src/RimMandrake/rimflow/acceptance/modledger_cutover_accept.py

## criteria
- The writer clause names only modules that write one of the three stores.

## verify
python3 src/RimMandrake/rimflow/acceptance/modledger_cutover_accept.py ExplosiveKnockback GimmeSomeSlack FlowWorks
