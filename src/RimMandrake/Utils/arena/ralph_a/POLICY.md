# ralph_a policy (what the loop enforces in code, and what the passes must follow)

Enforced by `ralph_a_loop.py` (code, not prompt):
1. One item per build pass, fresh context per pass, agent id minted by the loop for that invocation.
2. A build pass whose model exits non-zero or is killed at the timeout is not published; its failure note feeds the
   next pass. So is a pass that commits nothing, or whose build-phase gate fails.
3. Every build that passes the build-phase gate is followed AT ONCE by a tester pass: a different agent id, a fresh
   invocation, `test_start` logged before it runs. The loop refuses to start the next build pass while any logged
   `build_end` lacks a later `test_start` from a different agent (`require_tested`).
4. The tester sees only TESTER.md, the frozen spec, the test plan, the diff and a history-less export of the
   candidate tree. It never sees the builder's prompt, transcript, failure notes or commit messages.
5. A tester FAIL (or no verdict after two fresh testers) is a failed try; its findings feed the next build pass.
6. Three failed tries of one item: the candidate is parked on `ralph/failed/<item>` and the loop moves on.
7. A task whose `live` is not `none` goes to the minimal-list lane after the tester passes; the loop WAITS (starts no
   build and no tester pass) until the lane records a verdict for that exact sha.
8. Publish only after the final gate verdict is `pass` (step 9, the test record, included): ff-merge `ralph/wip`
   into `main`, then `./publish`. A failed publish writes STOP.
9. No pass starts when the account runway is below `$RALPH_A_RUNWAY_MIN` (default 0.15) or cannot be measured.
10. The bridge is released (`rimflow bridge release --mine`) after every model pass, whatever it did.
11. A red pre-check (`run_selftests --quick`) at the start of a pass is allowed only when `last_failure.md` explains
   it; otherwise the loop writes STOP.
12. A STOP file in the control dir stops the loop before the next pass.

Followed by the passes (checked by the gate and the tester, not by trust):
- No worldgen of any kind; every DLC is assumed; never live-test a flyer's flight.
- Never name a GenAI account, host or key in code.
- Agent scratch goes under the control dir or `D:\ClaudeWork`, never in the repo.
