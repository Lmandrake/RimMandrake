# RIMFLOW_RETIRE_DEAD_MODULES

## spec

Deferred WP-14 (redesign_final.md G20): retire dead rimflow modules, close_audit KEPT. Needs an entry-point inventory first (imports, 'python3 path' strings in units/hooks/scripts, importlib) because grep misses CLI/timer/hook/dynamic entry points, and a revert commit ready.

Done when: each retired module is absent from the inventory of entry points, selftests are green, and the revert commit sha is named in the closing note.

Source: /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/redesign_final.md row 14 and G20
