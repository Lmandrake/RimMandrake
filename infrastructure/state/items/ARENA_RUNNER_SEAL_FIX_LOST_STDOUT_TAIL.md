# ARENA_RUNNER_SEAL_FIX_LOST_STDOUT_TAIL

## Finding (FOUNDRY, 2026-10-30, while making C# checks build: ARENA_CSHARP_CHECK_BUILD_IN_JUDGE_SANDBOX)
arena_judge RUNNER's `_seal` ends the check with `posix._exit(0|1)` without flushing sys.stdout. Whatever the check
printed after its last flush (with a pipe, stdout is block-buffered) never reaches the judge's tail: under the RUNNER
a C# check's `dotnet run` output and its own FAIL lines were missing from `tail`, while the same check outside the
runner printed them. The pass/fail RESULT is unaffected (rc and the nonce line are right); only the evidence is lost,
so a base failure reads as a bare rc 1.
## Done when
`_seal` flushes sys.stdout/sys.stderr before `_exit`, and a selftest shows a check's last unflushed print in `tail`.
