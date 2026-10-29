# ARENA_RALPHC_BUILD_BUILDERS_WAIT_ON_TESTERS

Architecture-trial build, order 14 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Assemble `ralph_c` (design/RimMandrake/architecture_switch_harness_2026-10-29.md step 14; design/RimMandrake/testpilot_merged_2026-10-29.md §2.3): two builder loops split by area with bounded read/search subagents (C+sub), each loop with the same fresh blind tester pass as `ralph_a` after every build pass, both runners pulling oldest first, and back-pressure: a builder whose live candidate waits for a runner gets no new live-needing item.

## criteria
Done when: a stolen item's out-of-area edit is refused; a builder with a waiting live candidate is given no new live item; every `build_end` has a `test_start` from a different agent before that loop's next build pass.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Sonnet: test-checkable code (owner's rule: Sonnet for code tests can check).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
