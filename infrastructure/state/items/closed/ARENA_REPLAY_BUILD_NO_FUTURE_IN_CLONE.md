# ARENA_REPLAY_BUILD_NO_FUTURE_IN_CLONE

Architecture-trial build, order 6 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build the replay runner (design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.4, §3.2): `git init` + `git fetch` of only the base sha into /home/mandrake/rm/arena/replay/<arm>/<task> (full clones, never worktrees), interleaved randomised scheduling seeded by the freeze hash, the arena/replay tree added to `rm-scratch-reap` roots, and deletion of each clone after judging.

## criteria
Done when: a replay clone cannot `git show` the original fix sha; the run order differs per arm and is reproducible from the seed; a judged clone is gone.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Sonnet: test-checkable code (owner's rule: Sonnet for code tests can check).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
