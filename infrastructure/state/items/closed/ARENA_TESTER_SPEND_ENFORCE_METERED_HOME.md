# ARENA_TESTER_SPEND_ENFORCE_METERED_HOME

Found by BENCH independent verify of ARENA_ANALYSIS_WRITE_JUDGE_EVENTS_AND_SPEND (2026-10-30).

## Defect
Every arm's tester spend is silently unmetered, and the analysis still DECIDEs.
- ralph_a_loop.py Loop._tester_root (~964-976) makes a tempdir OUTSIDE the arena root; tester_env (~266-281)
  gives the tester a fresh HOME inside it and strips RM_ARM and RM_GPT_CALL_LOG; the root is rmtree'd after.
- So the tester's Claude transcripts are deleted (or, if kept, land as an "outside" session = UNATTRIBUTED,
  non-blocking in spend_census), and its GPT calls are untagged (overhead) or unlogged.
- Same pattern: v3_control.py:454,469; trio_loop.py:626-660; ralph_c inherits from ralph_a.
- Violates design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.6 ("helpers included").

## Evidence
D:\ClaudeWork\rimmandrake\arena_verify2_20261030\bfeed.py probe d1 (output bfeed.txt): 10M tokens of a tester
session inside trio T003's span, written where the tester actually writes, are not seen; verdict stays
DECIDE_FOR_trio and blocking == [].

## Fix wanted
Tester transcripts must land somewhere the meter reads, attributed to the arm (project slug under the arena
root, or copied there before rmtree), and RM_ARM / RM_GPT_CALL_LOG must pass through; OR the meter must refuse
(block) when an arm ran a tester whose spend it cannot see. Add a selftest that fails on today's code.

## Minor (same area)
selftest_arena_spend does not kill BENCH mutants B2 (span end exclusive, `lo <= t < hi`) and B13 (census sink
called before the window filter); bfeed.py does. Pin both in the selftest.
