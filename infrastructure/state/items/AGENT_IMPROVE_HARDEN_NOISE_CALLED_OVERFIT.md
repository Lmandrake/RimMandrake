# AGENT_IMPROVE_HARDEN_NOISE_CALLED_OVERFIT

The 4.3 generalization verdict has no noise floor. Its first real run (agent/rimworld-modding/v1, a one-line path fix in skills/rimworld-modding/SKILL.md) read held-out 2 win / 3 loss / 1 tie -> `overfit`, yet the judge's own reasons say the two plans were "nearly equivalent" and differ by run-to-run variation (evidence: infrastructure/state/agent_improve/general/rimworld-modding_v1_20261106T085827Z.json). With 6 pairs, losses > wins is a coin flip on any small change, so the rule would revert good changes at random.
## criteria
- Measure the noise: a null control (old text vs the same old text) on the same sample, recorded beside each check.
- The verdict calls harm or gain only past a margin the null control cannot reach (or a sign test at a stated level); otherwise `no_signal`, which neither reverts nor keeps-as-general.
- The change to the Conductor's 2026-11-02 verdict rule is recorded on the ledger with its reason; selftest_agent_improve_general.py covers it.
