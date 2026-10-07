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
