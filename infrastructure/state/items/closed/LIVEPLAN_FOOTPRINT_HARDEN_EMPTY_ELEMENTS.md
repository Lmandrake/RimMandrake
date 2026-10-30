# LIVEPLAN_FOOTPRINT_HARDEN_EMPTY_ELEMENTS

Filed by BENCH 2026-10-30, while independently verifying TRIO_FROZEN_TASKS_WIRE_LIVE_PLAN (commits 7843f73f9c, 798509d059, a2674e58c9).

## Gap
`testpilot.check_live_plan` checks each footprint list element with `isinstance(x, str) and x`.
Mutant M10 cut that to `isinstance(x, str)`, so `footprint.files: [""]` is accepted. The mutant passed
selftest_arena_testpilot, selftest_arena_trio and BENCH's bench_lp.py. The existing test covers only
non-list footprint values, never bad elements.

## Done when
selftest_arena_testpilot refuses `footprint: {"files": [""]}`, `{"files": [3]}` and `{"defs": [""]}`, and running M10
against it fails.

## Also (nit, same review)
In trio_loop, a 0-round park (no live_plan) files its rimflow park item with a title that says to look at
the trio/failed branch. No such branch exists for a 0-round park, and the park record correctly has evidence None. Reword that title.

## Evidence
`D:\ClaudeWork\rimmandrake\trio_liveplan_bench_verify_20261030\` contains mut_results.jsonl (16 mutants: 13 killed,
M10 a gap, M11 and M14 equivalent), run_mut.py (the exact mutations) and bench_lp.py (the E2E check).
