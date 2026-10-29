# ARENA_CONTROL_BUILD_V3_TESTER_AFTER_CLOSE

Architecture-trial build, order 11 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build the v3 control (design/RimMandrake/architecture_switch_harness_2026-10-29.md step 9; design/RimMandrake/testpilot_merged_2026-10-29.md §6.2): today's FOUNDRY brief run in a throwaway clone, changed in one place only to meet the owner's binding rule: after each helper's close, a fresh tester helper tests that sha before FOUNDRY briefs the next build. And `v3c`: plus the done gate and a GPT review per sha, both requiring the tester record bound to the sha (reuse collapse step 1 if it landed). The owner answers this arm's design cards like any arm's and does nothing else in it. Opus because procedure briefs are hard to validate.

## criteria
Done when: v3c refuses a close without both a review record and a tester record bound to the sha; the v3 procedure briefs no new build before the tester helper's `test_start`.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Opus: hard-to-validate work (owner's rule: Opus for code that is hard to validate).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
