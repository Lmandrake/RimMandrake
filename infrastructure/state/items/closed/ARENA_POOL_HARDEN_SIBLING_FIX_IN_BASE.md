# ARENA_POOL_HARDEN_SIBLING_FIX_IN_BASE

## spec
The census chain dedup only compares PUBLIC task bytes with other tasks' hidden checks. A later task's base_sha tree can already contain an earlier pool task's fix and its hidden test, as in the fixture where ESC's base is GOOD's fix. An arm given both tasks, or an arm clone at the later base, can therefore read the earlier task's answer. The leak scan only catches this once a clone has been built. GPT second read, finding 3 (BENCH review of 67094dc0f6).
Decide this at scheduling time, not census time: record for each task the set of pool tasks whose fix commit is an ancestor of its base (a `base_contains` list in the report). The assignment and round planner must then never give one arm a task together with a task listed in its base_contains, or must order them so the earlier one is judged first.

## criteria
Done when: the census report lists base_contains for every task, the planner refuses a conflicting pairing in a selftest, and the real pool reports how many pairs conflict.
