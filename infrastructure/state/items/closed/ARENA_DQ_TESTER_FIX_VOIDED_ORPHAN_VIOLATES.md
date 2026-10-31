# ARENA_DQ_TESTER_FIX_VOIDED_ORPHAN_VIOLATES

Can change a verdict: YES (disqualifies an arm).

A kill between build_end and test_start leaves an untested build. Restart voids it with a signed `invalid` event under runner.lock (`v3_control.void_orphans`, as ARENA_ORPHAN_BUILD_UNSTICK_V3_ARM_BRICKED intends) and the next attempt starts a new build. `arena_analysis.dq_tester` (line 948) never reads `invalid`, so it sees a build pass after an untested build: tester VIOLATED, arm disqualified.

Trail in `D:\ClaudeWork\rimmandrake\arena_readiness\logs\v3.jsonl`, task RP_SAVE_GUARD_FIX_BOM_READ_AS_BROKEN: build_end 3a8a2303 19:08:41, invalid (operator) 19:08:48, pass_start 19:11:20. Result in `an_spend3b.json`: dq tester VIOLATED, evidence build 3a8a2303. (The same file's scope VIOLATED is my stub editing outside the task area: not a defect.)

Fix direction: dq_tester drops builds voided by a harness `invalid` (v3_control.invalidated_builds) and only those; an arm-written invalid must not launder an untested build.
