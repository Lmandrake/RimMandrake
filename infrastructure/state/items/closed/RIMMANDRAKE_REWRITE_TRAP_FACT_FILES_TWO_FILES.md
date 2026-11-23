# RIMMANDRAKE_REWRITE_TRAP_FACT_FILES_TWO_FILES

Caused by RIMMANDRAKE_LAUNCH_REMAINING_PLAIN_ENGLISH_BATCHES_ELEVEN_LEFT (2026-11-23). The rewrite's parent item is `RIMMANDRAKE_REWRITE_RULE_DOCS_PLAIN_ENGLISH_LOSE_NOTHING`. His words are on it: "let's make sure we're not being oracular or obtuse, without losing information ... This is very important."

## spec

This item is the batch `RIMMANDRAKE_REWRITE_TRAP_FACT_FILES_TWO_FILES` of `design/specs/2026-11-19-plain-english-rule-docs/batch_plan.md`: instrument_traps.md and tool_traps.md. The
batch is larger than one helper run can do well, so its work is in the items below, one run each. This item has no
work of its own. It waits on its parts and closes when every part is closed.

- `RIMMANDRAKE_REWRITE_INSTRUMENT_TRAPS_KEEP_EVERY_MEASUREMENT`
- `RIMMANDRAKE_REWRITE_TOOL_TRAPS_KEEP_EVERY_MEASUREMENT`

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/list_effect.py closed RIMMANDRAKE_REWRITE_INSTRUMENT_TRAPS_KEEP_EVERY_MEASUREMENT RIMMANDRAKE_REWRITE_TOOL_TRAPS_KEEP_EVERY_MEASUREMENT` exits 0. At filing each part was open,
so the test failed.

## criteria

- Every part above is closed, each with its own result file and fresh meaning read.
