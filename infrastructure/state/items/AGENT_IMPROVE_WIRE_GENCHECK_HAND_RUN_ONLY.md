# AGENT_IMPROVE_WIRE_GENCHECK_HAND_RUN_ONLY

`agent_improve.py general <target> v<N>` (the 4.3 check) runs by hand and as the L2 pre-apply gate only. Not yet built from design section 4.3: the cadence (every fifth change at L1, weekly for the newest version of each target), enacting a revert verdict (overfit/no_gain -> a new version restoring the old text, design 4.2), and the digest line counting a target's narrow changes.
## criteria
- run_pass triggers the check on the cadence above and records it; a revert verdict publishes a revert version; the digest line counts narrow changes per target; selftests cover each with stubs.
- Blocked in spirit by AGENT_IMPROVE_HARDEN_NOISE_CALLED_OVERFIT: do not enact reverts until the verdict has a noise floor.
