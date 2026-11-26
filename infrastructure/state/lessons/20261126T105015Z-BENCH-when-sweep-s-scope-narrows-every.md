When a sweep's scope narrows, every list that routes a check to that sweep goes dead silently. publish_tree_checks.json nightly_only kept 5 whole-tree guards 'for the nightly' after the nightly was narrowed to finished mods (2026-11-15); nothing read the list, and 4 guards sat red on main for days. Before narrowing a sweep, grep for every config that names it as a destination.
item: RIMMANDRAKE_CLEAN_NIGHTLY_SWEEP_ONCE_THEN_RED_RINGS
home: design/RimMandrake/validation_map_and_rules.md
