# GimmeSomeSlack 0.1.1 — in-game acceptance, visit 1

Run: detached helper on RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_ONE_RUN_TWO, game b on Archmagi
(`D:\ClaudeWork\rimmandrake\instances\b\game`). Started 2026-11-20 9:33 PM PST.

## Progress
- 9:33 PM precondition `in_game 0.1.1` [measured]; item claimed by this unit; bridge archmagi.b taken by BENCH; skeleton written.
- 9:35-9:41 PM GSS on game b in sync (362 files; DLL sha256 7157d9f1 = its .srchash over the 0.1.1 source 934b35e053);
  JawaBench companion FRESH; tier gimmesomeslack (12 mods, all 5 DLC) applied; game b launched (34 s). Game b's Saves
  backed up to D:\ClaudeWork\rimmandrake\backups\saves_b_gss_011_visit1_20261120; RM_TestSite_calm_v3 and
  GSS_OWNER_LOOK_20261116 copied in from game a's Saves (md5 checked; game a's copies untouched).
- 9:42 PM offline gate (proof_all --offline-gate): 0 red [measured].
- 9:43 PM PIPELINE DEFECT: the unit carried RM_GAME_INSTANCE=b with an empty WSLENV, so python.exe never saw it and the first
  batch drove game a (port 5174): it loaded RM_TestSite_calm_v3 there 10 s after a FlowWorks judge run took game a's bridge,
  then stopped at its preflight (18 mods, GSS absent). No save written, nothing deployed. That run was told at once.
  Filed and fixed test first: RIMMANDRAKE_CARRY_WSLENV_INTO_B_RUNS_PROOF_HIT_A (selftest_detached_game_env.py 6 FAIL on
  9708ac4b5e, 10 PASS after), published 08b3ba8881, closed. Measured on the way: WSLENV=NAME/u does not reach python.exe.
  From here every command runs with game_instance.env("b") (Transient/gss_env_b.sh); game b answers on 5175.
- 9:50-9:53 PM runA matrix,core on game b: 81/81 PASS [measured].
- 9:57-10:03 PM runB aerial,style,save_load,d4_save,statics: 64/64 PASS (P_R3b_sway_looks_each_draw among them);
  runC matrix,core,scenes: 108 PASS + 2 UNMEASURED that need FlowWorks loaded (SC_shock_reach_deck_cord_per_value,
  SC_under_liquid_pit; their tier is gimmesomeslack_flowworks) [measured].
- 10:03 PM the four 0.1.1 scenes: sc_pole_icons_loaded PASS, sc_switch_off_ends PASS, sc_no_roof_over_pole FAIL on one row
  (SC_forced_roof_still_cuts_spans: read 3 ticks after the forced roof; the mod cuts in its roof sweep, once per 250 ticks):
  class HARNESS, repaired test-first in the sitting (wait 260 ticks, read the roof back), published a2b606e05f; planted
  (roof gone before the sweep) FAIL, real PASS. sc_pole_south_of_tree: draw layer PASS, its capture waits a read.
- 10:10-10:15 PM gravship on PASS, off PASS.
- 10:16-10:22 PM sc_stub_joins on his review save (a copy in game b's Saves; md5 a1c76e27c41e before and after): PASS.
  All 31 stations captured (screenshots/sheet0-7.jpg) and looked at. Walk save built (human_review.py --build --fresh-map,
  31 stations, 62 labels, 31 sign books) and saved as GSS_011_VISIT1_WALK_20261120.rws. save_keeper read game a's Saves:
  filed and fixed test first (RIMMANDRAKE_POINT_REVIEWMAP_AT_GAME_B_SAVES_KEEPER_BLIND, 4ee4209d57).
- 10:30-10:55 PM sc_pole_south_of_tree: a planted control (fault_mast_on_building_layer.patch deployed, cold load): layer
  row FAIL and the south mast drawn behind the oak; real build redeployed (hash back to b9ae8819): layer row PASS and the
  south mast drawn in front (evidence/pole_south_look_read.json). Filed RIMMANDRAKE_RESTORE_SLACK_LOOK_FILE_AFTER_PROOF_LEFT_EXTCORD
  (the proof leaves the GSS settings file on ExtensionCord).

## Exit
```
ingame_rows: {}
strange_open: UNMEASURED
savegame: UNMEASURED
exit_met: false
```
