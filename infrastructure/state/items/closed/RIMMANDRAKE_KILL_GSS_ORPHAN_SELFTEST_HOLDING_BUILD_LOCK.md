# RIMMANDRAKE_KILL_GSS_ORPHAN_SELFTEST_HOLDING_BUILD_LOCK

## spec
found-by: BENCH detached helper RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_SIX_TESTS_FIRST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 6, judge-1794822790, 2026-11-16, code c991553a4f). Class Polish, bar no_hose.
Criterion: an offline rerun repeats its recorded verdict
Evidence:
- lane2/reruns.jsonl: T_GATE first rerun FAIL in 52 s (validation O3_core_selftest, O3n_selftest_can_fail red), T_CORD_GEOMETRY_OFFLINE 'selftest build FAILED' (MSB3027: SelfTest.dll locked by '.NET Host (11224)', a dotnet.exe running the SelfTest DLL from the same WINBUILD_ROOT, started 02:16:54 PST, gone ~2 min later)
- both PASS when rerun alone afterwards (T_GATE 225.7 s, T_CORD_GEOMETRY_OFFLINE 4523/4523); no mod change between
- cause not settled: a selftest run outliving its caller's timeout or kill (a Windows child survives its WSL parent) is the guess [guess ~60%]
Would pass: two back-to-back runs of `python3 src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --offline-gate` then `python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --geometry` with one WINBUILD_ROOT both exit 0
Smallest fix: unknown until reproduced; candidate: the selftest runner kills the Windows process tree on timeout (taskkill.exe /T /F /PID) and waits for the staging DLL to unlock before building
Verdict on the criterion: criterion sound; a harness flake, no wrong green; Polish. Acceptance test: none, the race was not reproduced on demand

## verify
Acceptance test: none, the race was not reproduced on demand; would-pass above is the check once a reproduction exists.
