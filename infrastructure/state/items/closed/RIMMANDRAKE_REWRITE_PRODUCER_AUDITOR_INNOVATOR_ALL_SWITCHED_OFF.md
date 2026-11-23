# RIMMANDRAKE_REWRITE_PRODUCER_AUDITOR_INNOVATOR_ALL_SWITCHED_OFF

Caused by RIMMANDRAKE_LAUNCH_REMAINING_PLAIN_ENGLISH_BATCHES_ELEVEN_LEFT (2026-11-23). The rewrite's parent item is `RIMMANDRAKE_REWRITE_RULE_DOCS_PLAIN_ENGLISH_LOSE_NOTHING`. His words are on it: "let's make sure we're not being oracular or obtuse, without losing information ... This is very important."

## spec

This item is the batch `RIMMANDRAKE_REWRITE_PRODUCER_AUDITOR_INNOVATOR_ALL_SWITCHED_OFF` of `design/specs/2026-11-19-plain-english-rule-docs/batch_plan.md`: producer.md, auditor.md, innovator.md, runner_options.md. The
batch is larger than one helper run can do well, so its work is in the items below, one run each. This item has no
work of its own. It waits on its parts and closes when every part is closed.

- `RIMMANDRAKE_REWRITE_PRODUCER_AND_AUDITOR_ROLES_SWITCHED_OFF`
- `RIMMANDRAKE_REWRITE_INNOVATOR_AND_RUNNER_OPTIONS_ROLE_FILES`

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/list_effect.py closed RIMMANDRAKE_REWRITE_PRODUCER_AND_AUDITOR_ROLES_SWITCHED_OFF RIMMANDRAKE_REWRITE_INNOVATOR_AND_RUNNER_OPTIONS_ROLE_FILES` exits 0. At filing each part was open,
so the test failed.

## criteria

- Every part above is closed, each with its own result file and fresh meaning read.
