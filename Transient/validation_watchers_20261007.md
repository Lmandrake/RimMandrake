# Watchers validation, 2026-10-07 - LINT ONLY (under the ~800-line non-engine bar), nothing committed

Sizing: 1014 lines in 10 files. Non-engine logic is about 120 lines: NearestOther / flinch radius test (35), the stay-on-medium gate in RM_CompWatcher.CompTick (20), the watch -> flinch -> hidden cycle in RM_JobDriver_Watch (45), the flush hunt-mark rule (10). Mostly engine calls: hediff add/remove, Designation, job starts, terrain lookup, reflection-bound geophone, dust puffs. Rejected as kernels for that reason.

## Lint
`python3 src/RimMandrake/Utils/lint_watchers_defs.py [--quiet]`: 7 defs + 1 patch file, 15 classes, 9 refs, 2 field checks, 3 drivers, 9 settings: 0 ERROR, 0 WARN.
