# ARENA_METER_BUILD_SPEND_BY_CLONE_PATH

Architecture-trial build, order 5 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build per-arm metering (design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.6): `spend_census.py` attributes Claude spend by transcript project slug (each arm's cwd is its own clone, helpers included); `gpt_consult.py` tags each call from `RM_ARM` in the environment; judge and gate run from /home/mandrake/rm/arena/judge and bill to the harness. Unit ITE. No account, host or key named in code.

## criteria
Done when: a known 1-pass probe job in a fresh arm clone is seen by the census with nonzero ITE; a zero for an arm that ran is refused as a result, not reported.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Sonnet: test-checkable code (owner's rule: Sonnet for code tests can check).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
