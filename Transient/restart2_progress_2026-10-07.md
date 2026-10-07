# Full restart #2, 2026-10-07 (GSS into full list + Kinetic Arms/GSS live checks)

- 03:48 start; bridge held by BENCH
- 03:58 game was already gone (a 34-mod instance had started ~03:5x and exited); FOUNDRY deployed Greentide/Stillsand/CreatureBehaviors meanwhile (23550555d)
- 04:02 pulled to 23550555d; deployed 16+1 files (GSS DLL, StructureInjectionsSW + UtinniPatches fall-line wrecks) + Biomes 15 files (Abyss/FeverWood/RustCathedral/Warscar DLLs, Bileworm). Abyss, Stillsand, CreatureBehaviors, GSS, KineticArms, ExplosiveKnockback DLLs md5-match the repo
- 04:05 ModsConfig = FULL.LATEST 610 + explosiveknockback, kineticarms, gimmesomeslack after flowworks = 613 (ET parse, 6 Ludeon); snapshot infrastructure/state/modlists/ModsConfig.FULL_plus_EK_KA_GSS_2026-10-07.xml
- 04:05 launched via steam.exe -applaunch 294100
- 04:08 my 613-mod load was killed mid-load and ModsConfig swapped to a 34-mod tier at 04:09:09 by a FOUNDRY modcheck run (LeaningScrub/WeepingStones) that did not take the bridge; FOUNDRY game PID 108028 now up. Waiting for it to finish rather than fight
- 04:26 FOUNDRY's tier game exited; 613 list rewritten; relaunched via Steam (PID 148624)
- 04:39 second load killed mid-load (LoadTracer ctor 1118/1632, no crash dump, no WER event): AGENT FOUNDRY session (PID 16130, /home/mandrake/rm/foundry) ran `Stop-Process -Name RimWorldWin64 -Force` then `modset_builder.py --tier acc_biomes --apply`. FOUNDRY took the bridge at 10:47:16Z ("FOUNDRY GREEN-MIN + standalone tiers while owner AFK"), one minute before BENCH's take, and keeps cycling tier loads. Its restores write FULL.LATEST (610), which drops EK/KA/GSS. Stopped here, not racing it; live checks NOT run
- deploy state is good (all committed mods deployed, DLLs md5-match); 613-mod snapshot committed; scripts for the checks staged in Transient/kinetic_gss_live_2026-10-07/

## retry 2026-10-07
- 06:07 pulled 7cf477ce3; deploy plans: all committed mods + composed Biomes in sync (only FlowWorks result JSONs differ, evidence not content). Killing idle 610 game PID 224144
- 06:07 ModsConfig = FULL.LATEST 613 (ET parse, core+5 DLC); launched via steam.exe -applaunch 294100
- 06:07:54 game PID 246780 up; 06:25:58 Bridge token -> load 18m04s on 613 mods
- first exception (log line 82): `Exception loading from System.Xml.XmlElement: MissingMethodException: Default constructor not found for type System.String` (DirectXmlToObject, no def named; vanilla-load phase)
- ours, red: RSW_FreshTIEPanelWreck/RSW_FreshLandspeederWreck/RUT_FallLineWreckHull/RUT_FallLineWreckCarapace "null thingClass" because parents RM_WreckFamily_Hull/Speeder/Carapace not found -> RUT_WreckList_FallLine cannot land them (fall-line wrecks deployed 04:02 are dead); KA guns forcedMiss + smeltable-no-products; RM_Gun_PulseCannonTurret forcedMiss; RM_ThurrockShatter duplicate compClass; RM_Thurrock/RM_Borehulk textures missing; RM_Urraveth_*_Wrapped, RM_YearningFruitHarvested, RM_SweetlineToken textures missing; RM_DryAirBlower tickerType Never with per-tick fuel
- 06:27 starting debug quicktest colony
- 06:27-06:37 quicktest FAILED: NRE in ReadingPolicyDatabase.GenerateStartingPolicies inside Game ctor (GenTypes.SameOrSubclassOf null) = the 4 null-thingClass wreck defs. Cause: RM_WreckFamily_* parents are in mandrake.rm.biomes (load 608), children in rsw.injections (165) / rut.patches (554); GetBestParentFor only takes a parent with loadOrder <= child. Fix c8b886a75: children shipped as patch-added defs (mod-less node -> parent resolves globally), Conditional on parent. Deployed (+prune old Defs files). Reloading.
- 06:39:48 relaunch PID 55976; 06:59:03 token (19m15s); 0 wreck/null-thingClass errors; 07:01 quicktest map Playing (fix confirmed)
- 07:01-07:14 live checks on the quicktest map (Mycotic biome, ~7C):
  - (a) KA: runner sampled at 300 ticks -> 17 FAIL, almost all "across" contamination: unarmed hostiles walk off after landing. Runner now takes a tick arg; at 90 ticks: PASS thump_shell (6), grav_ram 8 cells (>=7; one run 2 new injuries, rerun 0), slam_charge, kicker N/E/S + dud_rearm, pulse_push + pulse_charge_gate, repulsor_westward, palm_arrest_wall, thudder_crowd, pit_colonist/pit_enemy (thrown into pit, stillInPit). FAIL product: thump_cannon throws 2 cells (verdict wants >=4, design 5). FAIL mixed: repulsor_along_shot 3 cells but 1 new injury (no-wound bar); gravram_big_body; looted_pirates pirateFactions=False. Scene stillness defect: thump_off/strength_zero/palm_shove side pawn walk 1 cell, so "unmoved" bars cannot pass (journals show no launch). kicker_west launches=0 at 90t.
  - (b) GSS dive PASS: conduit under wall -> stub_wall both sides, StubWall decals, net live
  - (c) sway PASS: span Up hp30 before/after thump_shell blast, kineticSways 0->1, explosionCuts 0
  - (d) Chill PASS: vaunoom + hoolen post "A <x> is leaving the area: It is too warm here for it (comfortable at -150C..-30C)"; heemin die (corpses) instead of leaving
  - (e) containers PASS: 9/9 RecipeDefs live with their benches; spawned labels Plainleather/Glass(granite)/Steel bottle, Wooden/Steel/Plasteel barrel, Wooden/Steel/Plainleather bucket. Screenshot did not frame the items (inconclusive visually)
- 07:15 swept 20 non-colonists; Saves backed up to D:\Luke\dev\_rmscratch\saves_backup_20261007T0714; keeper RM_kinetic_gss_review_20261007.rws NEW (30.7 MB), no other save changed
- GSS_INTO_FULL_LIST_1 closed
