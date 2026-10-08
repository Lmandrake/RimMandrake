# Live checks 4 (2026-10-08)

- [start] skeleton created
- killed game, flowworks tier applied, FlowWorks DLL + composed biomes deployed (8 files), 4 deleted scald files moved to D:\Luke\dev\_rmscratch\scald_moved_20261008\
- flowworks tier game up; running validation_v2 --live --fresh-map
- FlowWorks v2 GREEN 59/59: E4, E1c, X10 PASS (Transient/belt_live_checks4_fw_run_20261008.txt)
- live tier (16 mods) relaunched for Scald checks
- A3 PASS: Player.log 0 mentions of 4 deleted defs; get_defs RM_ScaldArmor notFound, RUT_ScaldExposure/RUT_Scald loaded
- A4 PASS (measured): RUT_ScaldSteam locked + carrier; bare pawn vs boil-suit (ArmorRating_Heat 0.85 on instance), severity delta over 5000 ticks 0.0476 vs 0.00702 = ratio 0.1475 (2500-tick window 0.1625)
- A5 PASS: DamageDef RUT_Scald armorCategory=Heat live; 8-dmg Torso hits: bare pawn 8.0 dealt each (6/6, died of accumulation), boil-suit pawn 0,0.. then 0,5,0,2,0 for 5-dmg hits (armor deflection)
