# ARENA_GATE_BUILD_UNMEASURED_NEVER_PASSES

Architecture-trial build, order 3 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build `arena_gate.py --task --base --head --arm` (design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.2): a separate process in a clean checkout runs scope, non-empty/no-placeholder, tests (`run_selftests.py --only`), `validate_patch.py --live --defs`, `winbuild.py`, deploy plan, the task's proof, the live record check (sha match, modcheck, canary; a failed canary is `invalid`) and step 9, the different-agent test record. A step that cannot run is UNMEASURED, never pass. Output is one JSON record.

## criteria
Done when: a placeholder diff, an out-of-area edit, a red test and a dead-colony canary are each refused or marked invalid; a candidate with no `test_start` from an agent other than its builder is refused; a step forced to be unrunnable reads UNMEASURED.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Sonnet: test-checkable code (owner's rule: Sonnet for code tests can check).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
