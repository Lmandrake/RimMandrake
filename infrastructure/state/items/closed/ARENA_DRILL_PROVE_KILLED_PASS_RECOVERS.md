# ARENA_DRILL_PROVE_KILLED_PASS_RECOVERS

Architecture-trial build, order 12 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Run the failure-path drill (design/RimMandrake/architecture_switch_harness_2026-10-29.md §4.2): plant a failing check in one task, kill one build pass mid-run, kill the gate mid-run, and kill a tester pass mid-run in `ralph_a`. Record the drill in the event log.

## criteria
Done when: nothing unchecked reaches an `arena/*` branch the judge reads; each killed process's next pass recovers; the killed tester pass leaves the builder blocked, not running ahead.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Sonnet: test-checkable code (owner's rule: Sonnet for code tests can check).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
