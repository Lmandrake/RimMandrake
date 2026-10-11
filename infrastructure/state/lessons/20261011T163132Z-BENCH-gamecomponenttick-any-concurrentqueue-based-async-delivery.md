GameComponentTick, and any ConcurrentQueue-based async delivery built on it (Oracle's), never drains while the game is PAUSED, which start_debug_game_ready leaves it by default. step_game_ticks a handful of ticks (still paused) to force delivery before reading a result. Source: FOUNDRY_REBOOT_HANDOFF_202609132338.md.
home: skills/rimbridge/references/traps.md
