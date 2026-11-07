## criteria
- A cadence generalization check on a change record with empty source_kinds never publishes a revert from its "held-out" reading (or the design says why it may).
- selftest_agent_improve_cadence.py covers it.

## why
AGENT_IMPROVE_HARDEN_GATE_EMPTY_SOURCE_KINDS closed this hole only in the pre-apply gate (agent_improve.general_gate). agent_improve_general.run_for_version still reads `source_kinds` from the change record, and agent_improve_cadence.run_one enacts a revert when `keep` is False. Both change records on file (rimworld-modding_v1, using-rimflow_v1) have source_kinds [], so an overfit reading on them comes from a sample that excluded nothing, and it would revert the change. rimworld-modding_v1 already read overfit once, before the noise floor existed. Decide whether the cadence reads such a record as unmeasured; a record already on file cannot regain kinds its pieces do not name.
