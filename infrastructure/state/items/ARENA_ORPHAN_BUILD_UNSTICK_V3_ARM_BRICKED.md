# ARENA_ORPHAN_BUILD_UNSTICK_V3_ARM_BRICKED

Filed (OWNER): a kill between `build_end` and `test_start` leaves a build `require_tested` refuses forever (`NotTested`),
so the arm cannot run again; `v3_control` has no operator void. The signed log is not rewritten.

## verify
- L0: a signed void event (or an equally signed fresh start) is the only way past an orphaned build; it names the build
  and why; `require_tested` passes after it and still refuses an orphan with no void. A selftest kills in that window
  and covers both. Every arm with that window (ralph_a, trio, ralph_c) is either covered or shown not to have it.
- L1: the real v3 arm's stranded build from the 2026-10-31 OOM run is voided through this path, the signed log still
  verifies, and the arm's next brief starts. The voided run is recorded as invalid, not counted in any arm's result.
- Stopping point: finish.

## criteria
- A1 L0: orphan refused without a void, passes with one; signed log never rewritten; every arm's window accounted for
- A2 L1: the stranded v3 build voided live, arm runs on, run excluded from results
