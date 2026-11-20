# RIMMANDRAKE_ALLOW_REWRITE_BATCH_ITS_ONE_MEANING_READER

Caused by RIMMANDRAKE_REWRITE_SUBAGENT_FILES_SHARED_BLOCK_SIX_COPIES (2026-11-19).

## spec

- Each batch of the plain-English rewrite runs as a detached helper (`rm-detached-bench-rimmandrake-rewrite-<batch>-…`).
- Step 6 of `design/specs/2026-11-19-plain-english-rule-docs/batch_plan.md` requires a fresh Opus meaning reader per
  file before the batch publishes. The Conductor's brief makes that reader the one exception to "a helper starts no
  helpers".
- `block_agent_over_slots.py` counted these readers against the shared CONDUCTOR budget. The 17 batches and the
  Conductor window share that budget.
- Measured 2026-11-19 15:47-15:52 PST: batch RIMMANDRAKE_REWRITE_SUBAGENT_FILES_SHARED_BLOCK_SIX_COPIES had every
  reader refused, three times ("CONDUCTOR already has 3 helper(s) running … N=3").
- The fix: `slot_rules.json` `role_runs` gets the prefix `rm-detached-bench-rimmandrake-rewrite-` with N=1. This uses
  the same mechanism as RIMMANDRAKE_ALLOW_STEWARD_EXAM_RETAKE_ITS_OWN_FIVE_READERS.
- The danger that N=1 guards: one batch fans out readers on the shared account. A batch runs its readers one at a
  time. Total spend does not change, because each file gets one reader in any case.
- His word (`slot_override.json`) still caps the allowance.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_designer_exam_slots.py` prints `GREEN: 0 failed`. On the
base commit `25c18fb733`, with the new cases added, the test printed `RED: 3 failed`. The 3 cases:

- the rules give the rewrite prefix exactly 1;
- with CONDUCTOR N=0, a rewrite batch's first reader is allowed;
- with its one reader running, the batch's next reader waits (`slots_full`).

Also: `python3 .claude/hooks/selftest_block_agent_over_slots.py` prints GREEN.

## criteria

- A rewrite batch starts its meaning reader while CONDUCTOR is full.
- A second reader at the same time waits.
- Any other detached run stays under the Conductor budget (the existing case of the same test).
