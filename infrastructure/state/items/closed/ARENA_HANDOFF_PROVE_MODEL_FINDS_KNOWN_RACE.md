# ARENA_HANDOFF_PROVE_MODEL_FINDS_KNOWN_RACE

Architecture-trial build, order 16 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Write the TLA+ model (design/RimMandrake/architecture_switch_harness_2026-10-29.md §7): one parameterised spec for the goodbye restart, the TestPilot handoff and the arena switch, with invariants S1-S6 and liveness L1-L2, checked with TLC (install and check tla2tools/Java on this machine first). Off the critical path. Opus because a model's fidelity to the code is hard to validate.

## criteria
Done when: TLC finds the known goodbye interleaving in the unfixed model, and the fixed protocol passes S1-S6 and L1-L2 at the stated bounds.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Opus: hard-to-validate work (owner's rule: Opus for code that is hard to validate).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
