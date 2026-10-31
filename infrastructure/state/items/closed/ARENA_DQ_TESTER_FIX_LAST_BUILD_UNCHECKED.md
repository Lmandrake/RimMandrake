# ARENA_DQ_TESTER_FIX_LAST_BUILD_UNCHECKED

Can change a verdict: YES.

`arena_analysis.dq_tester` only looks at a build when a LATER build pass_start follows it, so the last build of an arm's stream is never checked. Real arena_analysis, signed synthetic logs, 26 tasks, ralph_a's build left untested:
- task index 24: tester VIOLATED, verdict TIE.
- task index 25 (last): tester CLEAN, verdict DECIDE_FOR_ralph_a.

Evidence: `D:\ClaudeWork\rimmandrake\arena_readiness\logs\s5_lasttask.txt`. The move from 29 to 26 tasks exposed it (my task-25 case used to have followers).

Fix direction: every build_end that reached a gate or judge needs a different-agent test first, last build included, excepting harness voids (ARENA_DQ_TESTER_FIX_VOIDED_ORPHAN_VIOLATES).
