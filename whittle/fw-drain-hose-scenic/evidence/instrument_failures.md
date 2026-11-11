# Preserved instrument failures

1. First fast C# probe compile: rc=1. Actual raw stdout/stderr and command/return-code receipt are `probe_initial_stdout.txt`, `probe_initial_stderr.txt`, `probe_initial_receipt.json`; failing script is `fast_probe_initial.py`. Missing production DrawOrder, LiquidJoinRule and HoseCarry dependencies. No production behavior was measured on that attempt. Adding the actual source dependencies produced the successful `probe_baseline_*` run before the repair.

2. The first exact-fixture orchestration attempt stopped before invoking dotnet. The failing script remains `pre_broaden/exact_mutant_path_error.py`. The following is a transcription of the actual exec tool response (the terminal response is also in the parent conversation), not a separately captured subprocess log:

```
Traceback (most recent call last):
  File "/home/mandrake/rm/scratch/BENCH/fw-drain/whittle/fw-drain-hose-scenic/evidence/exact_mutant.py", line 65, in <module>
    (here/('mutant' if mutant else 'exact')+'_program.cs.txt').write_text(program)
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~
TypeError: unsupported operand type(s) for +: 'PosixPath' and 'str'
```

Correcting path-expression parentheses allowed the exact-fixture runs. The subsequent expected mutant FAIL is a successful negative control, not a mod failure. No three consecutive genuine nonpasses occurred: successful production baseline separated these harness faults. Opus independently diagnosed the first compile fault in its broaden report. No mod failure was hidden or relabelled.

3. After the authorized wrapper passed, the first derived `verify_proof.py` check incorrectly expected individual successful `Program.Check` messages in C# stdout. Actual full-suite output reports `HoseGptFix: 27/27`, `hose: 457/457 assertions passed`, and `1240/1240 passed`; `HoseChecks.cs` prints individual Check messages only on failure. The failed verifier is preserved as `verify_proof_silent_check_error.py`. The actual terminal failure was `AssertionError` at line 30, asserting that `scenic: the cost never blocks (both poses cross both remote reel columns with no way round: laid)` was in csharp. The verifier now requires the actual suite summary and uses the exact-fixture executable's per-check output for individual ScenicRoute passes. No source, test log, or suite run was changed or repeated.
