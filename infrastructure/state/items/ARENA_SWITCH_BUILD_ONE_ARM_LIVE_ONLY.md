# ARENA_SWITCH_BUILD_ONE_ARM_LIVE_ONLY

Architecture-trial build, order 8 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build the switch (design/RimMandrake/architecture_switch_harness_2026-10-29.md §2): `arm.toml` outside git; `rm-arm-<arm>.target` units with `PartOf=` and mutual `Conflicts=`; `arena switch <mode>` (STOP file, wait idle at most 90 min, release bridges, `modlist_swap.py restore` with ModsConfig.xml parsed not grepped, unpushed-work check, switch event); `arena who` and the ops_watch `ARENA_TWO_LIVE` rule; pre-push hooks confining each arm to `arena/<arm>/*`. A trial win runs `arena switch <winner>` on production the same day (owner, 2026-10-29), so the switch must work on the production seats too.

## criteria
Done when: starting two arm targets fails; a push from a stopped arm is refused and alarmed; `arena who` exits non-zero on each of its four checks when forced; a switch into production mode is rehearsed in a throwaway user session.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Sonnet: test-checkable code (owner's rule: Sonnet for code tests can check).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
