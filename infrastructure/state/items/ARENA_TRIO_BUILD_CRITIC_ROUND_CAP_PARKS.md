# ARENA_TRIO_BUILD_CRITIC_ROUND_CAP_PARKS

Architecture-trial build, order 9 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build the trio build half (design/RimMandrake/testpilot_merged_2026-10-29.md §2.1 L2-L5, L4): FOUNDRY runs a fresh Ralph builder subagent per item, then at once a fresh blind Opus critic that runs the item's offline tests itself and reviews code, plan and evidence; 2 rounds, then one automatic simplify-or-split, 2 more, then park to the Conductor with the last verdict; ids, priority and round counts survive simplify/split; the gate is run by the loop script, never self-reported. Opus because critic prompts are hard to validate.

## criteria
Done when: a task built never to satisfy the critic ends in simplify/split after round 2 and park after round 4, never a 5th round; every critic accept is bound to the sha it saw; `test_start` from the critic follows each `build_end` before the builder's next pass.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Opus: hard-to-validate work (owner's rule: Opus for code that is hard to validate).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
