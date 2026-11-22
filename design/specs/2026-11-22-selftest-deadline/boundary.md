# BOUNDARY: the selftest runner's deadline, Design Version 0.1.0

Code: `src/RimMandrake/Utils/run_selftests.py` (`PER_TEST_TIMEOUT_S`, `per_test_timeout`). Tests:
`src/RimMandrake/Utils/selftest_selftest_deadline.py`. Written 2026-11-22 for
`RIMMANDRAKE_GENERALIZE_PIPELINE_REPAIRS_INTO_FEW_PRINCIPLES` (principle 7, a limit names its danger).

## ACCEPTS

- **a-test-file.** A `selftest*.py` file. Its first 40 lines may hold one `# selftest-timeout: N` tag (N whole seconds).

## DOES NOT SURVIVE

- A test that hangs inside a child process the runner cannot kill (a Windows process across interop). The runner kills
  its own process group at the deadline; a process outside it lives on.

## PROMISES (each one is owed a test of the same name)

- **one-hang-guard.** A test with no tag gets the deadline `PER_TEST_TIMEOUT_S`, 600 s.
- **a-tag-only-raises.** A tag above 600 s is that test's deadline. A tag at or below 600 s has no effect: the deadline
  is a hang guard, never a speed bar, so no tag makes it tighter.
- **no-dead-tag.** No tracked test file carries a tag at or below 600 s.

## LIMITS

- `PER_TEST_TIMEOUT_S = 600`. Danger: a hung test holds a worker, and the run, with no end. Evidence: a WSL interop
  launch that never answered read as a hang (`INTEROP_RETRY_FIX_EIGHTY_SCRIPTS_LEFT`, 2026-11-03). Why this value and
  not less: the 240 s default killed real passes of 273 s, 367 s, 420 s and 526 s, and 121 tests carried a tag
  above 240 s and at most 600 s to escape it (107 of them exactly 600). 15 more carried a tag of 240 s or less that
  named no danger. All 136 were deleted on 2026-11-22 [measured]. Speed is a different signal:
  `selftest.slow_test_flag_s` (120 s for 3 nights) flags a slow test for a split; the deadline does not.
