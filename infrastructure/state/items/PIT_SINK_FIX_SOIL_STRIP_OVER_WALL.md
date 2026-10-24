## spec
found-by: BENCH bridge run (2026-10-23, run 1 driver 3, build 1f37da7100 = after 084ca107fc, 14-mod list, save e).
Class: MOD (look). Repro: load `RM_fw_walkthrough_20261023e`, map C, pause; `rimworld/step_game_ticks` 120 (pauseFirst)
moves WildBoar1995107 38,22 -> 39,23 into the C3 superdeep pit (38-39,22-23); frame 37,18 4x7 rootSize 4.
PIT_BOAR_FIX_SUNBATHES_ON_THE_WALL's headline is fixed: the boar is now drawn on the pit's south lip, not on the wall.
Still wrong, and unchanged after a further 1, 60 and 300 paused-stepped ticks (so not tween lag):
- a soil-coloured strip ~2.7 cells wide (about x 37-39) is drawn OVER the top face of the room's south steel wall (z~20);
- a lighter soil square sits under the boar just OUTSIDE the pit's south edge (z~21).
Both read as the pawn-carried ground patch (PIT_PAWN_FIX_CARRIES_A_SUNNY_SQUARE family) drawn south of the drawn boar.
Evidence: `Transient/bridge_run_1_20261023/captures/br1d3_c3_boar_zoom.png`, `br1d3_c3_boar_s1.png`, `br1d3_c3_boar_s300.png`,
`br1d3_c3_boar_wide.png`; before-fix frames `br1_pit_boar_zoom.png` (same columns showed soil either side of the boar).
Done when: same repro, no soil-coloured cells on the wall or outside the pit rim; the boar stays on the lip.
