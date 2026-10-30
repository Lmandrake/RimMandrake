# ARENA_LANE_BUILD_MINIMAL_LIST_ONLY

Architecture-trial build, order 13 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build `arena_lane.py` and the `ralph_c` runner (design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.5, step 12): per-lane take/release/deploy/reload/canary logging under `rimflow bridge take/release`; profiles limited to the 13-mod minimal list or minimal plus an item's load dependencies (`modset_builder.py --tier`, load time measured), with no full-list profile in trial mode (owner, 2026-10-29); Archmagi `owner_playing` flag and 20-minute idle rule; never a flyer's flight, never a canonical save, no C# deploy while the game runs; `modlist_swap.py restore` charged to the arm. The runner tests fixed shas oldest first. Opus because live-lane behaviour is hard to validate offline. Mechanism never observed running: the arena lane wrapper itself.

## criteria
Done when: a result for a stale sha is refused; a dead colony gives `invalid`; a full-list request in trial mode is refused; a minimal+deps profile records its measured launch-to-ready time.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Opus: hard-to-validate work (owner's rule: Opus for code that is hard to validate).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
