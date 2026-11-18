# RIMMANDRAKE_COUNT_REPAIR_PASSAGE_BLOCKS_FIFTH_MISSED_AT_CLOSE

## spec
The owner's fifth count, asked on RIMMANDRAKE_PRINT_JUDGE_COUNTS_WHEN_COVERAGE_CLOSES (OWNER note tsn
1794970570840907329, 2026-11-17 ~6:50 PM PST; his words: "We can try the confirmed new problem that quotes a passage a
repair changed thing: hopefully the judge doesn't just start polishing anything we repair."): second-look blocks raised
on a repaired passage, per mod, each listed with the changed passage it quotes and the promise it says is not kept.
That ticket closed at 28341732bb with four counts; the fifth was not built (close_line has no such count, and its
comment's "fifth" means flaws found in play, a different count).

Contract (coverage_judge.py only):
- record_round writes `repair_blocks` on every coverage_rounds row: [{gid, entry, passage, promise}] for each gap in
  `gaps` (blocking), tagged `new_since: late`, carrying `repair_passage`, not `carried`; [] when there is none.
- close_counts adds `repair_blocks` (blocks summed over looks that recorded the list, each listed) and
  `repair_blocks_unmeasured` (looks recorded before the list existed: never read as 0).
- close_line names "second-look blocks on a repaired passage N" and, per block, its entry, the passage it quotes and
  the promise; unmeasured looks are named UNMEASURED.

## verify
Acceptance test: `python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_stage_close_counts.py` reads
`wrong 0` (10 new cases; watched failing on base c6f9f55a7e/0a4688042: "cases read 36; wrong 10", exit 1, the 26 older
cases still right). Plus `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_coverage_judge
selftest_coverage_judge_loop selftest_coverage_delta selftest_coverage_refusal_record` green.

## criteria
- The case file reads wrong 0; the four coverage suites are green.
- A look recorded before this build reads UNMEASURED for the fifth count, never 0.

## refs
file: src/RimMandrake/rimflow/coverage_judge.py
file: design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_stage_close_counts.py
