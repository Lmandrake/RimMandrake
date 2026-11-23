# RIMMANDRAKE_REWRITE_DESIGNER_PACKET_FILES_HASH_IN_STAGE_RECORD

Caused by RIMMANDRAKE_LAUNCH_REMAINING_PLAIN_ENGLISH_BATCHES_ELEVEN_LEFT (2026-11-23). The rewrite's parent item is `RIMMANDRAKE_REWRITE_RULE_DOCS_PLAIN_ENGLISH_LOSE_NOTHING`. His words are on it: "let's make sure we're not being oracular or obtuse, without losing information ... This is very important."

## spec

This item is the batch `RIMMANDRAKE_REWRITE_DESIGNER_PACKET_FILES_HASH_IN_STAGE_RECORD` of `design/specs/2026-11-19-plain-english-rule-docs/batch_plan.md`: the seven Designer packet files, only while no Designer run is live. The
batch is larger than one helper run can do well, so its work is in the items below, one run each. This item has no
work of its own. It waits on its parts and closes when every part is closed.

- `RIMMANDRAKE_REWRITE_DESIGNER_PACKET_FIRST_FOUR_FILES`
- `RIMMANDRAKE_REWRITE_DESIGNER_PACKET_LAST_THREE_FILES`

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/list_effect.py closed RIMMANDRAKE_REWRITE_DESIGNER_PACKET_FIRST_FOUR_FILES RIMMANDRAKE_REWRITE_DESIGNER_PACKET_LAST_THREE_FILES` exits 0. At filing each part was open,
so the test failed.

## criteria

- Every part above is closed, each with its own result file and fresh meaning read.
