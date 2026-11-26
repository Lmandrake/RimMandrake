run_selftests.py --only X exiting non-zero with zero bytes of output is the runner failing, not the test: it is UNMEASURED, rerun it (it passed under python3 -u on an unchanged tree). Under load inside rm-harness.slice a selftest with a Windows-exe child can die on 'UtilAcceptVsock ... accept4 failed 110' or rsync 'Cannot allocate memory'; such a selftest must carry the child's stderr into its FAIL detail so the runner can see the interop marker and rerun it instead of counting a red.

- Evidence: run_selftests.py --only selftest_stillsand exited 120 with ZERO bytes of output twice in a row (2026-11-02), then passed GREEN on an unchanged tree with python3 -u; an empty-output non-zero exit is the runner, not the test - rerun before reading it as red. (Rescued 2026-11-25 from the stranded clone backup backups/stranded_clones_20261102/STILLSAND_ROOF_COVER_EXPOSURE_1 before its delete.)
item: RIMMANDRAKE_RETIRE_OLD_PIPELINE_REMNANTS_TEN_SLIPPED_INTO_LANES
item: RIMMANDRAKE_EXTEND_CLEANER_TO_FAMILIES_NO_CLEANER_COVERS_265_GB_ON_D
home: NONE
