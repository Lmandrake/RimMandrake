# BOUNDARY: the guard on progress (progress_guard.py), Design Version 0.1.0

Code: `src/RimMandrake/Utils/progress_guard.py`. Tests: `src/RimMandrake/Utils/selftest_progress_guard.py`.
Item: `RIMMANDRAKE_MEASURE_TIME_BUDGETS_AGAINST_REAL_RUNS_HE_SEES_TEN_PERCENT`. `./publish`, `run_selftests.py` and
`scratch_reap.py` use it.

## ACCEPTS

- **a-child-with-pipes.** The guard reads a child whose output goes to pipes that the guard made or was given.

## DOES NOT SURVIVE

- **a-hang-that-uses-the-cpu.** A child that spins is ended at the backstop, not sooner. With no backstop it is not ended.
- **work-on-another-machine.** A child that waits on Windows or on SteveDesktop, with no output and no CPU time here, reads
  as silent.

## PROMISES (each one is owed a test of the same name)

- **silent-child-ends.** A child with no output and no CPU time in its process tree is ended after `SILENCE_S`.
- **slow-writer-lives.** A child that writes is never ended for being slow.
- **silent-worker-lives.** A child that uses the CPU with no output is never ended for silence. A grandchild's CPU counts.
- **spinning-child-ends-at-the-backstop.** A child that spins is ended at its cap.
- **ended-child-keeps-its-result.** The exit code and the whole output come back.
- **run-kills-the-session.** A child that the guard ends leaves no grandchild.
- **could-not-look-is-not-a-hang.** A process tree that cannot be read ends nothing.
- **a-left-behind-process-does-not-hold-the-result.** A process that a finished child left does not hold its result.

## LIMITS

- `progress_guard.SILENCE_S = 1800`. Danger: a hung child holds its caller with no end. Evidence: a WSL interop launch that
  never answered (`INTEROP_RETRY_FIX_EIGHTY_SCRIPTS_LEFT`, 2026-11-03). Longest silence of a live child: UNMEASURED.
- `progress_guard.LEFT_OPEN_S = 15`. Danger: a process that a finished child left holds the pipe of the child with no end. It
  ends no work: the child has exited.
- At load 40: the guard does not change with the load, because a live child gets some CPU time in 30 minutes.
