# RIMMANDRAKE_SEAL_STEWARD_SECTION_BLIND_JUDGE_READ_IT_FIRST

A blind judge reads the sealed "Steward's decisions" section of its brief before lane 1, because the launch line of a
detached run orders it to read the whole brief file (FlowWorks blind cycle 5, 2026-11-27). The launch keeps the sealed
section out of the brief file the judge is handed, and writes it to its own file that the brief names.

## refs
file: src/RimMandrake/rimflow/maturation.py
new: src/RimMandrake/rimflow/selftest_seal_steward_section.py

## verify
python3 src/RimMandrake/rimflow/selftest_seal_steward_section.py
