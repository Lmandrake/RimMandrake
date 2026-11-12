# CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK: done statement

Item: `conductor_closeout.py check`, a program check of B2 step 1 (his rulings and answers in the window vs the ledger)
before the goodbye restart. First closed at b00bfae (selftests green), live promise `hook=conductor_goodbye.py`.
Reopened 2026-11-08T20:34Z by rm-deadman: "hook conductor_goodbye.py is not wired in ~/.claude/settings.json,
/home/mandrake/rm/dispatch/.claude/settings.json". Cause: the Pyrelands squash landing 8fb9f7f2b6 replaced
`.claude/settings.json` with the branch's copy, dropping every hook; 943a7a66da restored it. The ledger says it owes a
class guard (`rimflow guard ... --test <selftest*.py> [--instance "<args>"]`) before it closes again.

Each line is a checkable claim, with the evidence that shows it:

- The check still works at HEAD: `src/RimMandrake/rimflow/selftest_conductor_closeout.py` and
  `.claude/hooks/selftest_conductor_goodbye.py` exit 0 at the closing sha (output saved in
  `whittle/conductor_closeout_build_ledger_check/evidence/`).
- The hook is wired now: `live_line._hook("conductor_goodbye.py", None)` returns None (the promise holds).
- A class guard exists for the cause: a selftest the nightly sweep runs that fails when ANY hook named by a `hook=`
  promise on the ledger or in `src/RimMandrake/rimflow/live_baseline.txt` is missing from the committed
  `.claude/settings.json` (or its script is absent), not just this one hook.
- The guard is shown failing on the instance: `rimflow guard CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK --test <test>
  --instance "<args>"`, replaying the 8fb9f7f2b6 settings file, is accepted (the test fails on it), and the same test is
  green on HEAD's settings.
- The item closes against the published sha with the promise `hook=conductor_goodbye.py`, the guard test and the ledger
  shard committed.
