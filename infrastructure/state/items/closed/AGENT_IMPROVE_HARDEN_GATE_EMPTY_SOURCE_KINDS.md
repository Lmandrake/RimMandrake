## criteria
- The top-level pre-apply generalization gate refuses (or the design says why it does not) a change whose cited pieces yield no source kinds.
- selftest_agent_improve_general.py covers it.

## why
source_kinds(row, entry) reads only the cited pieces, and task_kind() needs an item id in a piece's text. Both change records on file have source_kinds [] and source 0-0-0, so nothing was excluded from "held-out" and narrow could not occur. The L2 three-kind bar in gather counts gathered pieces, not cited ones, so a citation with no item id can still reach the gate empty, and its "held-out" sample then is not held out. Found by review while building AGENT_IMPROVE_TUNE_L2_GATE_SAMPLE_POWER.
