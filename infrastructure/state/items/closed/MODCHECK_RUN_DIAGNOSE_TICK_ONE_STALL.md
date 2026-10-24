# MODCHECK_RUN_DIAGNOSE_TICK_ONE_STALL

Diagnosed live 2026-10-24 (BENCH). The stall was not in the bridge, a modal or the game. It was an offline chain.

py-spy dump of the runner (stall_stack.txt):
run_suite -> chain_fn -> rivers_switch_flips (FlowWorks/validation.py) -> _selftest_cases -> subprocess.run(wsl
python3 selftest_flowworks_stock.py) -> dotnet run of the FlowWorks C# SelfTest.

That one subprocess took about 9 minutes; the docstring claimed ~80 s. Meanwhile the game sat paused at tick 1,
because the chain needs no game. The runner printed nothing per chain, so even with unbuffered output nobody
could see which chain was running. After the SelfTest finished, the run went on and completed:
345 PASS / 6 FAIL / 265 UNMEASURED.

Fixes:
- runner.run_suite prints "[modcheck] chain <name> START/END <s> PASS= FAIL= UNMEASURED=" to stderr.
- _selftest_cases announces itself on stderr, and its docstring now gives the measured time.

Also seen in this run:
- The runner calls rimflow verify. That call needs RIMFLOW_SEAT passed through WSLENV. Without it the verify
  is REFUSED and record_run is skipped. This was an operator error at launch, not a harness bug.

Evidence: D:\ClaudeWork\rimmandrake\live_20261024\stall_stack.txt, D:\ClaudeWork\rimmandrake\live_20261024\modcheck_fw.log
