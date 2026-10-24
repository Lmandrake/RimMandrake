## spec
found-by: BENCH bridge run (2026-10-23, run 1 driver 3, build 1f37da7100, 14-mod list, save e map C, god mode on).
Class: HARNESS (bridge/companion). A FloatMenu opened by a debug action cannot be read or picked through the bridge.
Repro: `rimworld/execute_debug_action {path:"Actions\\Tanks: fill ALL on map to max (pick liquid)"}` returns success; then
`rimworld/get_context_menu_options` returns no options (optionCount absent), and `rimworld/get_ui_layout` shows only the
menu's title label "Pick the liquid to fill every tank on this map with." with no option targets. Nothing can be picked, so
the tanks stay unfilled (0/26). Gizmo-opened menus (tank "Dev: fill") and UI-clicked menus (Architect pipe button) read fine.
Effect: TANK_DEBUG_BUILD_FILL_AT_WILL A1's debug-action click route stays UNMEASURED.
Evidence: `Transient/bridge_run_1_20261023/fillall_probe.log`, `s117.log` (TD_fillall_click_route).
Done when: after that debug action, get_context_menu_options lists the liquids (or the menu's options appear as clickable
layout targets), and picking one fills every tank. Re-run `Transient/bridge_run_1_20261023/fillall_probe.py`.
