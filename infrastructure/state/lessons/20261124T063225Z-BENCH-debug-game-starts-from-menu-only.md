rimworld/start_debug_game_ready works only from the main menu: called while a map is loaded it waits its whole timeoutMs (280 s) and answers 'Timed out waiting for RimWorld entry scene readiness', so call rimworld/go_to_main_menu and wait for programState Entry first (ArchSmall, 2026-11-23, twice).
item: RIMMANDRAKE_BUILD_SCENE_LIBRARY_TEN_NAMES_FIVE_LAYERS_TODAY
home: skills/rimbridge/references/traps/lifecycle.md
