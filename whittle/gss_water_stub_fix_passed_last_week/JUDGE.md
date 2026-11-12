# JUDGE — GSS_WATER_STUB_FIX_PASSED_LAST_WEEK

Judge: CLAUDE_ARCHMAGI_FWLIVE judge seat, 2026-11-11 ~21:50 PST. I did not read DONE.md or BROADEN.md.
Read: STATEMENT.md, NOTES.md, every file in evidence/ (the logs and JSON, the run 5 board PNG and the old-rule swim-ON
PNG), the 2026-10-23 FAIL at `D:\ClaudeWork\rimmandrake\scratch\br1_gss\gss_A.json`, the ledger events for the item,
and git for the fix commit and the DLL.
I also ran the proof myself: `proof_all.py --live --only matrix` at 21:43:32, HEAD 8d9f9db9c3, output
`D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_ARCHMAGI_FWLIVE\gss_ws\judge_run2.json`. Result: 36/36 PASS.

## A1 (GREEN-MIN): true
- My own run: MX_F60_T15_S0 PASS with got = stubs 2, cord_edges 2, strands 2, nets 1,
  node_types {battery 1, consumer 1, stub_water 2}. Expected cords_min/max are 2/2, so strands [2,2] is met. The edge
  hashes (`battery:20,20|stub_water:29,20`, `consumer:35,20|stub_water:32,20`) match the builder's runs 2, 3 and 5 exactly.
- Tier: `env.tier` was read from ModsConfig.xml activeMods: matched_list fw_gss_sitting, 14 active, and
  active_equals_running is true. The 14 mods are 5 DLC, Harmony, RimBridgeServer, VEF core, SimpleCameraSetting,
  GSS, FlowWorks, LuminousPigment and Biomes. The statement leaves out LuminousPigment and the camera mod, but they are
  part of the tier the statement names.
- Deep swim was read live: `deepSwimEnabled: True` (swimOpenWaterEnabled False), in both my run and run 5.
- DLL: the running assembly sha256 is c16983bc…, which equals the repo DLL and the deployed DLL.
  `gss_dll_matches_source_run5.json` checks 70 srchash files with 0 mismatches. The GSS deploy is in-sync and
  src_dirty is false. The fix line (`!hasEdifice && water && terrainImpassable → Water`) is in the current
  SnapshotBlock.cs, and 4b01d06994 is an ancestor of HEAD.

## Cause named: true
- The 2026-10-24 `implemented` event records "root cause: candidate 1 (FlowWorks co-loaded) … R12 deep swim makes
  WaterDeep walkable … adapter read walkable as ground before water".
- The statement says the before/after comparison (the 11-11 PASS against the 10-23 FAIL) confirms the cause. On its
  own it does not. Three weeks of GSS commits landed between the two runs, including several snapshot/adapter rewrites
  that touch SnapshotBlock.cs (5389e65f64, e7b402c553, b05e9ce45d).
- What does isolate the cause is `cause_experiment_old_vs_new_rule_x_swim.json`, a 2x2 test. It used one source base
  (487769d00c56, an ancestor of HEAD) with only the fix line removed, on the same site and the same 14 mods, with the
  canal cells read off the path grid:

  | rule | deep swim | canal walkable | result |
  |---|---|---|---|
  | old | on | yes | FAIL, 0 stubs, 1 edge (identical to 10-23) |
  | old | off | no | PASS |
  | new | on | — | PASS |
  | new | off | — | PASS |

  The fault appears only with the old rule and swim on, which is exactly the named cause.
- The images agree:
  - `cause_oldrule_swimON_F60.png` shows one cord laid straight across the canal.
  - `MX_F60_T15_S0_board_run5.png` shows the cord stopping at both canal banks.
- So the claim is true, and the evidence for it is stronger than the reason the statement gives.

## No regression in the run: true
- Run 5 and my run: all 30 matrix scenes PASS, D1/D2 PASS, Z_log_budget 0 errors, offline gate 0 red.
- Run 4 (`proof_all_fw_gss_sitting_run4_D2_fail.*`) had all 30 matrix scenes PASS. Its one non-PASS was D2 on board
  B00_ground (F00/D00 ground scenes, no water, missing 1 + extra 1). It is classified MOD and filed as
  RIMMANDRAKE_EXPLAIN_GSS_D2_SPLIT_ONCE_IN_TWELVE (2026-11-12T05:31Z). It is plausibly unrelated to the fix, which
  only changes cells that are both water and def-impassable.
- The builder included the failing run in the evidence instead of showing only a clean one.

## Staging / flattering-evidence notes
- F60 is a synthetic board: one 3-wide canal, an idle scene, and a still image. It cannot show a cord re-laying when
  swim is toggled at runtime.
  - The cause experiment covers this partly: it sets swim through mod settings, calls RM_SwimWater.Reapply and reads
    the path grid back.
  - Topology is the claim here, and the JSON counts and hashes carry it, so a still is enough.
- The fix covers only def-impassable water. FlowWorks' superdeep pit water is def-Standable, so a cord still lies on
  top of it. That gap is outside this statement and is filed as RIMMANDRAKE_BURY_GSS_CORDS_IN_FW_SUPERDEEP_PIT_WATER
  (`sibling_XW1_fw_superdeep_cord_on_water.png`).
- Provenance error in the ledger:
  - The statement header and the `verify` event both name "built c29007b6b66e".
  - The DLL that was actually run is c16983bc…, last changed at 732415605f.
  - The DLL at c29007b6b6 hashes to 210f6607…, a different build.
  - Both builds contain the fix, so the A1 verdict stands. The verify event should name the sha that was tested
    (HEAD 8d9f9db9c3, DLL c16983bc).
- NOTES.md warned that the clone has someone else's uncommitted FlowWorks edits. The evidence only shows that
  FlowWorks was running. It does not show which FlowWorks build was deployed. That does not change this scene's
  verdict, because what matters is the swim behaviour, and the run read it live.

would show: yes
