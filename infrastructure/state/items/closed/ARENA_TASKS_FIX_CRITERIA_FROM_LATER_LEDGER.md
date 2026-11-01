# ARENA_TASKS_FIX_CRITERIA_FROM_LATER_LEDGER

## spec
arena_tasks.census falls back to `it.criteria`, the ledger manifest replayed at its FINAL state, when the base prose has no ## criteria. It still records prompt_source base_parent, but the manifest may hold criteria added after the fix, and those could describe the answer. GPT second read, finding 6. Latent: measured 2026-10-30, 0 of the 241 written tasks have criteria_source "ledger manifest" (the rest are title or prose).
Replay the ledger only up to the close's tsn, or drop the fallback. Either way, record the true source.

## criteria
Done when: a fixture whose criteria were added after the close does not reach the task, and selftest_arena_tasks passes.
