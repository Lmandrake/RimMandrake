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

- **one-hang-guard.** A test with no tag gets the deadline `PER_TEST_TIMEOUT_S`, 6000 s.
- **a-tag-only-raises.** A tag above 6000 s is that test's deadline. A tag at or below 6000 s has no effect: the deadline
  is a hang guard, never a speed bar, so no tag makes it tighter.
- **out-of-time-is-unmeasured.** A test that a guard ended reads UNMEASURED, and its reason names the bound. It never
  reads FAIL or CRASH.

## LIMITS

- `PER_TEST_TIMEOUT_S = 6000`, the backstop for a test that spins. Danger: a test in an endless loop holds a worker, and
  the run, with no end. Evidence: a WSL interop launch that never answered read as a hang
  (`INTEROP_RETRY_FIX_EIGHTY_SCRIPTS_LEFT`, 2026-11-03). Longest real run: 599 s (`selftest_maturation_autonomy.py`, PASS,
  at load 45 on 2026-11-24; 36 s alone) [measured]. The two values before this one were tight: 240 s killed real passes of 273 s, 367 s,
  420 s and 526 s, and 600 s (2026-11-22) was 1.1 times 526 s.
- `progress_guard.SILENCE_S = 1800`: a test with no output and no CPU time in its process tree for this long is ended.
  Danger and evidence: the same. Longest silence of a live test: UNMEASURED.
- Speed is a different signal: `selftest.slow_test_flag_s` (120 s for 3 nights) flags a slow test for a split. The
  deadline does not.
- A tag at or below 6000 s is dead text. Nobody deletes the tags of 2026-11-22 for that: a deleted line makes the checks
  of that mod run again.
