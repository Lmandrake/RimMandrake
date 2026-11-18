run_selftests.py --only X exiting non-zero with zero bytes of output is the runner failing, not the test: it is UNMEASURED, rerun it (it passed under python3 -u on an unchanged tree). Under load inside rm-harness.slice a selftest with a Windows-exe child can die on 'UtilAcceptVsock ... accept4 failed 110' or rsync 'Cannot allocate memory'; such a selftest must carry the child's stderr into its FAIL detail so the runner can see the interop marker and rerun it instead of counting a red.
item: RIMMANDRAKE_RETIRE_OLD_PIPELINE_REMNANTS_TEN_SLIPPED_INTO_LANES
home: NONE
