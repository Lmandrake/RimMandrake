# FlowWorks walk prep, 2026-10-16

- Close: taskkill.exe (WM_CLOSE, no /F), gone at once; ./game down stamped.
- Deploy: FlowWorks 1 file (Defs/LiquidTypes/ThingDefs/RM_Filth_LiquidSpill.xml), biomes compose 29 files (textures + RM_Salvessa.xml), GimmeSomeSlack and PyrelandsMechanics already in sync. ModsConfig untouched. Log: Transient/bench_live_20261016b/deploy_apply.txt
- Relaunch via Steam: bridge answered ~70 s; ./game loading then up.
- L5 (`liquid_checks.py --fresh-map --only L5`): **FAIL, MOD** `L5_switched_off_hose_spills`: filthInRect [1,1], spilledUnits [1,10001] (held 10000 -> 0, drained 10000, unplaced 0). Spill filth did not fix. `L5_colonists_clean_spill` UNMEASURED (no filth to clean). Result: `D:\Luke\dev` mirror path src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T130318.json (in `\\wsl.localhost\Ubuntu\home\mandrake\rm\bench\src\RimMandrake\FlowWorks\northstar\`). Raw: Transient/bench_live_20261016b/L5.txt
- Review map: review_map.py --build --fresh-map, 241.7 s: visuals 39/39, gallery 87/87 verified (stations 1, 2, 3, 8, 9, 11, 12, 45, 51 all built). Notes: station 61 pipe_adapter_Chemfuel not loaded (empty pad); RM_WaterBottle_Rust/Verdigris/Amber/Violet have no ThingDef (5 stacks each refused, free-area stock only). --labels: 462 pinned. Camera framed on station 1, calm world (peaceful, noon, hostiles swept).
- Save: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\RM_FW_walk_20261016.rws`. NOTE: an earlier `RM_fw_walk_20261016.rws` (Oct 15 23:20, same name on case-insensitive NTFS) was OVERWRITTEN; its copy is in the pre-save backup of all 324 saves at `\\wsl.localhost\Ubuntu\home\mandrake\.seat-tmp\BENCH\saves_backup_20261016b\`.
- Game left running at the map, paused. Bridge released.

## Level solve live
- Deploy: FlowWorks DLL + .srchash only (plan Transient/bench_live_20261016b/level_plan.txt), VERIFIED in sync; dll_source_stamp MATCH. ModsConfig untouched. Relaunched via Steam, save RM_FW_walk_20261016 loaded, 462 labels re-pinned.
- L7 (no --fresh-map): L7_levelset_setting_on PASS MOD {"levelSetEnabled": "True"}; L7_block UNMEASURED HARNESS: GovernorStop, safe_advance stopped after 780 of 1500 ticks, pawn Bennett (39867) downed (health 1). No level-solve row measured. Raw: L7.txt, result liquid_checks_result_20261016T144034.json.
- Station 1 framed, game left paused. Screenshot: station1_after.bmp (3840x2160) and station1_after.png (1600px).
