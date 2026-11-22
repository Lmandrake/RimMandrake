# RIMMANDRAKE_SPARE_HELD_STATEMENT_CHECKS_FROM_NEEDLESS_REMOVAL

## spec
maturation.read_ingame_exit turns a wrong (HARNESS/SITE) line that no bar needs into "needless" and orders the check removed
from the test table. A check that decides no bar passes that test vacuously, even when the table's held_statements (the
owner's held approvals, kept for re-check) name it as their test. FlowWorks visit 4 (2026-11-21): OL_OWNER_LOOK_READS is the
test of 31 held look approvals and the reader ordered its removal. Fix: a check a held statement names (whole word, in its
`test` text) is never needless; it stays not counted with its owner.
## verify
python3 src/RimMandrake/rimflow/selftest_wrong_check_fixed_in_sitting.py
## criteria
Acceptance test: the command above, case held-statement-check-is-not-needless: RED on the parent reader (c4 reads needless),
GREEN on the fix (c4 not_counted, the unnamed c5 still needless); 18 tests, every planted fault caught. Watched red on the parent
in the visit-4 run before the fix.
## refs
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/selftest_wrong_check_fixed_in_sitting.py
