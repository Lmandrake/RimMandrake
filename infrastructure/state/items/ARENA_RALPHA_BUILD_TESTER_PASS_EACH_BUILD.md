# ARENA_RALPHA_BUILD_TESTER_PASS_EACH_BUILD

Architecture-trial build, order 7 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build `ralph_a` (design/RimMandrake/architecture_switch_harness_2026-10-29.md step 8; Ralph doc §1): `loop.sh`, `PROMPT.md`, `POLICY.md`, the owed parts (`run_selftests --quick`, `bridge release --mine`, runway check), and, to meet the owner's binding rule (design/RimMandrake/testpilot_merged_2026-10-29.md §2.3), `TESTER.md`: every build pass that passes the gate is followed at once by a fresh blind tester pass (new context, only the frozen spec, test plan and diff, told to break it) whose verdict feeds the next build pass. Live-needing items go to a minimal-list lane and the loop waits on them. Opus because prompt and policy behaviour is hard to validate by tests.

## criteria
Done when: Ralph §8's planted failing check and killed pass both recover; a planted defect the gate passes is caught by the tester pass; the loop refuses to start a second build pass with no `test_start` from the tester for the first.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Opus: hard-to-validate work (owner's rule: Opus for code that is hard to validate).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
