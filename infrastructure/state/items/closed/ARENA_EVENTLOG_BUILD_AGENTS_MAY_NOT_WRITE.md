# ARENA_EVENTLOG_BUILD_AGENTS_MAY_NOT_WRITE

Architecture-trial build, order 2 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build the one-format event log (design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.7): one JSONL per arm under D:\ClaudeWork\rimmandrake\arena\events\, written only by harness code. The event set includes `build_end`, `test_start` and `test_end` (with builder and tester agent ids, for the different-agent rule, design/RimMandrake/testpilot_merged_2026-10-29.md §2.3) and `card` (owner design cards per arm, with rm-pulse dwell minutes and the tasks each answer unblocked). Also `arena_v3_adapter.py`, which translates v3 ledger events and testq records into the same schema.

## criteria
Done when: an agent-written event is rejected; adapter output matches `rimflow_metrics.py` close counts for one sampled day; a `test_start` whose tester id equals the builder id is flagged; owner minutes are reported per arm, and output with and without owner-unblocked work.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Sonnet: test-checkable code (owner's rule: Sonnet for code tests can check).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
