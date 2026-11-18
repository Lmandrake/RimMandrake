# RUN_SELFTESTS_FIX_STDERR_EATS_MARKER

## Findings

Codex full-file review of run_selftests.py at 494774e9d3 (round 4 of CLEANER_SANITY_REVIEW_FINISH_FULL_FILES), quoted as it answered. Each is a claim: verify it before fixing, and drop any that is not real.

1. **`_suite`: quick reuse precedes the quarantine check.** Suppose a slow test has a saved quick PASS, then a real run detects a false hit and quarantines it. If that suite is interrupted before `save_quick()`, the old quick PASS remains. With unchanged source hashes, the next `--quick` removes the test before quarantine is loaded. The known failing test prints `SKIPPED(quick)` and can leave the pre-check GREEN, despite the requirement that quarantined tests run until explicitly cleared.

2. **`_harness_child` / `_split_marker`: unterminated child stderr destroys the wrapper report.** A successful test containing `sys.stderr.write("checking...")` without a final newline leaves the wrapper’s JSON marker appended to that same line. `_split_marker()` recognizes markers only at the beginning of a line, so it returns no report. In contained mode, `_run_one_in()` consequently reports CRASH and makes the suite RED although the test exited successfully. The wrapper must ensure its report begins on a new line.
