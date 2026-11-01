# ARENA_PLANNERS_ENFORCE_SIBLING_ORDER

## Finding
arena_tasks.base_contains / schedule_conflicts / check_schedule exist (selftest t_vet_siblings) and the census reports
base_contains_pairs: 854 of 861 possible pairs in the 42-task pool (linear history: a later base contains every earlier fix).
No planner calls check_schedule yet: ralph_c_loop and arena_judge.assign may put two tasks in one round where one task's base
already holds the other's fix. Those files were off-limits to the builder (others editing).
## Done when
Every planner that forms rounds calls arena_tasks.check_schedule (or orders by base chronology and refuses same-round pairs)
and a selftest proves a conflicting round is refused.
