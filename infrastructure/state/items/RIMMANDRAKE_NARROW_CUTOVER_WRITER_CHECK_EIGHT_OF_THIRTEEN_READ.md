## spec
src/RimMandrake/rimflow/acceptance/modledger_cutover_accept.py's last clause ("no writer of the old stores is left outside modledger") counts a .py that names stage.json / journal.md / stage_record.json anywhere AND writes any file at all. On 3e3f32e50 it lists 13 candidates; 8 of them only READ an old store or merely name one [measured, per-line evidence in D:\ClaudeWork\rimmandrake\conductor\cr\cutover_writer_candidates_20261118.txt]: Utils/modset_builder.py:961 (a path inside a "why" string), Utils/ops_watch.py:3820, rimflow/concept_tree.py:1161, rimflow/control.py:1540/1582/1840, rimflow/coverage_calibration.py:74 (a name list), rimflow/pipeline_control.py:394, rimflow/role_launch.py:2187/2715, rimflow/run_void.py:182/189. The clause's text matching could not tell those readers from writers, and it excused rimflow/maturation.py, a real writer, for importing modledger inside a function.
Fix (Conductor's decision 2026-11-18 7:35 PM PST): writers are measured at run time by src/RimMandrake/rimflow/store_write_census.py (a hook over the pipeline selftests and each candidate's own selftests), no hand allowlist. Measured on 2026-11-18 [D:\ClaudeWork\rimmandrake\evidence\narrow_cutover\census_real2.json]: WRITER coverage_calibration, designer_cleanse, designer_stage, maturation, maturation_autonomy, role_launch; NOT MEASURED Utils/maturation_now (its save() never runs: its selftest is live_excluded), modset_builder, ops_watch, testq/pipeline_admit, control; NO WRITE SEEN the other 11, maturation_rescue among them.
Acceptance test: src/RimMandrake/rimflow/selftest_store_write_census.py (red 5 of 5 on af59572e5, the census absent; 15 checks green after).

## refs
file: src/RimMandrake/rimflow/acceptance/modledger_cutover_accept.py

## criteria
- The writer clause names as writers only modules measured writing one of the three stores, and names every module it could not measure.

## verify
python3 src/RimMandrake/rimflow/acceptance/modledger_cutover_accept.py ExplosiveKnockback GimmeSomeSlack FlowWorks
