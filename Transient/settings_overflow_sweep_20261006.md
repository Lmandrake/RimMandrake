# Settings overflow sweep 2026-10-06

Heuristic estimate (rows x ~30px, GapLine 12, long labels +22/55 chars; largest Listing_Standard segment per file). UNK = scroll present but start height is a measured variable; treated as RISK when est > 560 (first-frame measure is the defect). Over = est - start (560 if none).

| file | rows | est h | start h | class | over | status |
|---|---|---|---|---|---|---|
| src/RimMandrake/FlowWorks/Source/RimMandrakeFlowWorksMod.cs | 159 | 10530 | 10800f | RISK | 9450 | SKIPPED (other agents) |
| src/RimMandrake/CreatureBehaviors/Source/RM_CreatureBehaviorsMod.cs | 179 | 9388 | Mathf.Max(lastContentHeight, i | UNK | 8828 | SKIPPED (other agents) |
| src/RimMandrake/LuminousPigment/Source/LuminousPigmentMod.cs | 129 | 4384 | - | NO-SCROLL | 3824 | FIXED |
| src/RimMandrake/DivingInteraction/Source/RM_DivingSettings.cs | 49 | 3948 | - | NO-SCROLL | 3388 | FIXED |
| src/RimMandrake/FeverWood/Source/RM_FeverWoodMod.cs | 71 | 3864 | viewHeight | UNK | 3304 | FIXED |
| src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs | 73 | 3804 | - | NO-SCROLL | 3244 | FIXED |
| src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs | 65 | 3338 | viewHeight | UNK | 2778 | FIXED |
| src/RimMandrake/LanternDeeps/Source/LanternDeepsMod.cs | 61 | 3298 | Mathf.Max(inRect.height, outer | UNK | 2738 | FIXED |
| src/RimMandrake/TheRot/Source/RM_TheRotMod.cs | 74 | 2900 | scrollHeight | UNK | 2340 | FIXED |
| src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs | 108 | 7274 | 5170f | RISK | 2104 | FIXED |
| src/RimMandrake/Greentide/Source/RM_GreentideMod.cs | 55 | 2658 | Mathf.Max(lastContentHeight, i | UNK | 2098 | FIXED |
| src/RimMandrake/Wasteland/Source/RM_WastelandMod.cs | 53 | 2634 | viewHeight | UNK | 2074 | FIXED |
| src/RimMandrake/TheForge/Source/RM_TheForgeMod.cs | 45 | 2474 | viewHeight | UNK | 1914 | FIXED |
| src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs | 42 | 2442 | - | NO-SCROLL | 1882 | FIXED |
| src/RimStarWars/Droidworks/Source/Droidworks/RSW_DroidworksSettings.cs | 58 | 2368 | lastContentHeight | UNK | 1808 | not fixed (beyond top 12) |
| src/RimMandrake/Abyss/Source/RM_AbyssMod.cs | 31 | 1986 | Mathf.Max(inRect.height, lastH | UNK | 1426 | not fixed (beyond top 12) |
| src/RimMandrake/Miasma/Source/RM_MiasmaMod.cs | 37 | 1920 | viewHeight | UNK | 1360 | not fixed (beyond top 12) |
| src/RimMandrake/RimProperty/Source/PropertySettings.cs | 44 | 1880 | - | NO-SCROLL | 1320 | not fixed (beyond top 12) |
| src/RimMandrake/BlueDesert/Source/RM_BlueDesertMod.cs | 34 | 1846 | Mathf.Max(inRect.height, lastL | UNK | 1286 | not fixed (beyond top 12) |
| src/RimMandrake/TheSump/Source/RM_TheSumpMod.cs | 36 | 1650 | - | NO-SCROLL | 1090 | not fixed (beyond top 12) |
| src/RimStarWars/Sarlacc/Source/RSW_SarlaccSettings.cs | 27 | 1516 | - | NO-SCROLL | 956 | not fixed (beyond top 12) |
| src/RimMandrake/KeelHoist/Source/KeelHoistMod.cs | 31 | 1426 | - | NO-SCROLL | 866 | not fixed (beyond top 12) |
| src/RimUtinni/UnfinishedLine/Source/UnfinishedLineMod.cs | 37 | 1332 | Mathf.Max(inRect.height, viewH | UNK | 772 | not fixed (beyond top 12) |
| src/RimStarWars/Armoury/Source/RSW_ArmourySettings.cs | 58 | 2268 | 1500f | RISK | 768 | not fixed (beyond top 12) |
| src/RimMandrake/GimmeSomeSlack/Source/GimmeSomeSlackMod.cs | 34 | 1256 | viewHeight | UNK | 696 | not fixed (beyond top 12) |
| src/RimStarWars/Bacta/Source/BactaMod.cs | 39 | 1748 | 1060f | RISK | 688 | not fixed (beyond top 12) |
| src/RimMandrake/LongShade/Source/RM_LongShadeMod.cs | 17 | 1230 | - | NO-SCROLL | 670 | not fixed (beyond top 12) |
| src/RimMandrake/Contagion/Source/RM_ContagionMod.cs | 20 | 1188 | Mathf.Max(viewHeight, inRect.h | UNK | 628 | not fixed (beyond top 12) |
| src/RimMandrake/Stillsand/Source/RM_GlassChainMod.cs | 27 | 1168 | - | NO-SCROLL | 608 | not fixed (beyond top 12) |
| src/RimMandrake/NightsideIce/Source/RM_NightsideIceMod.cs | 25 | 1136 | - | NO-SCROLL | 576 | not fixed (beyond top 12) |
| src/RimMandrake/GimmeSomeSlack/Source/Hose/HoseSettings.cs | 28 | 1116 | - | NO-SCROLL | 556 | not fixed (beyond top 12) |
| src/RimUtinni/UtinniPatches/Source/UtinniPatchesSettings.cs | 22 | 1102 | - | NO-SCROLL | 542 | not fixed (beyond top 12) |
| src/RimUtinni/ShipShields/Source/ShipShieldsSettings.cs | 18 | 1058 | - | NO-SCROLL | 498 | not fixed (beyond top 12) |
| src/RimStarWars/JawaIonWeapons/Source/RSW_JawaIonWeaponsSettings.cs | 24 | 1022 | - | NO-SCROLL | 462 | not fixed (beyond top 12) |
| src/RimMandrake/ExplosiveGrowth/Source/ExplosiveGrowthMod.cs | 40 | 1590 | 1150f | RISK | 440 | not fixed (beyond top 12) |
| src/RimUtinni/FallLineArrivals/Source/FallLineArrivalsMod.cs | 22 | 980 | - | NO-SCROLL | 420 | not fixed (beyond top 12) |
| src/RimStarWars/GizkaStowaway/Source/RSW_GizkaSettings.cs | 32 | 1190 | 780f | RISK | 410 | not fixed (beyond top 12) |
| src/RimMandrake/WeepingStones/Source/RM_WeepingStonesSettings.cs | 15 | 906 | - | NO-SCROLL | 346 | not fixed (beyond top 12) |
| src/RimMandrake/Warcasket/Source/RM_WarcasketSettings.cs | 11 | 900 | - | NO-SCROLL | 340 | not fixed (beyond top 12) |
| src/RimMandrake/TitanicCreatures/Source/RM_TitanicCreaturesSettings.cs | 23 | 878 | - | NO-SCROLL | 318 | not fixed (beyond top 12) |
| src/RimStarWars/JawaRules/Source/RSW_JawaRulesSettings.cs | 14 | 842 | - | NO-SCROLL | 282 | not fixed (beyond top 12) |
| src/RimUtinni/PlantGrowth/Source/PlantGrowthMod.cs | 22 | 790 | - | NO-SCROLL | 230 | not fixed (beyond top 12) |
| src/RimUtinni/Atlas/Source/AtlasSettings.cs | 25 | 968 | 760f | RISK | 208 | not fixed (beyond top 12) |
| src/RimUtinni/PyrelandsMechanics/Source/PyrelandsMechanicsMod.cs | 20 | 762 | - | NO-SCROLL | 202 | not fixed (beyond top 12) |
| src/RimMandrake/OasisMaker/Source/RM_OasisMakerSettings.cs | 25 | 744 | - | NO-SCROLL | 184 | not fixed (beyond top 12) |
| src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialSettings.cs | 20 | 722 | - | NO-SCROLL | 162 | not fixed (beyond top 12) |
| src/RimUtinni/ScavengerEvents/Source/ScavengerEventsSettings.cs | 19 | 678 | - | NO-SCROLL | 118 | not fixed (beyond top 12) |
| src/RimMandrake/RustCathedral/Source/RustCathedral/RM_RustCathedralMod.cs | 17 | 654 | - | NO-SCROLL | 94 | not fixed (beyond top 12) |
| src/RimMandrake/MovingDunes/Source/MovingDunesSettings.cs | 11 | 602 | - | NO-SCROLL | 42 | not fixed (beyond top 12) |
| src/RimMandrake/Stillsand/Source/RM_SkeletonSettings.cs | 15 | 602 | - | NO-SCROLL | 42 | not fixed (beyond top 12) |
| src/RimMandrake/WreckedMachines/Source/WreckedMachinesMod.cs | 11 | 584 | - | NO-SCROLL | 24 | not fixed (beyond top 12) |
| src/RimMandrake/Ninefold/Source/RM_NinefoldMod.cs | 12 | 548 | - | OK | -12 |  |
| src/RimMandrake/Stillsand/Source/RM_StillsandEventsMod.cs | 12 | 546 | - | OK | -14 |  |
| src/RimMandrake/Graffiti/Source/RM_GraffitiMod.cs | 11 | 544 | - | OK | -16 |  |
| src/RimStarWars/BrainWorms/Source/RSW_BrainWormsSettings.cs | 11 | 536 | - | OK | -24 |  |
| src/RimMandrake/Stillsand/Source/RM_DuneGale.cs | 13 | 526 | - | OK | -34 |  |
| src/RimMandrake/ProximityHatch/Source/RM_ProximityHatchMod.cs | 11 | 518 | - | OK | -42 |  |
| src/RimMandrake/FlameStatues/Source/FlameStatuesMod.cs | 7 | 496 | - | OK | -64 |  |
| src/RimMandrake/RaidRedesigner/Source/RaidRedesignerSettings.cs | 11 | 496 | - | OK | -64 |  |
| src/RimMandrake/WeatherSuite/Source/WeatherSuiteSettings.cs | 11 | 492 | - | OK | -68 |  |
| src/RimUtinni/LongHunger/Source/LongHungerMod.cs | 13 | 490 | - | OK | -70 |  |
| src/RimMandrake/ShipVermin/Source/RM_ShipVerminMod.cs | 11 | 444 | - | OK | -116 |  |
| src/RimUtinni/FungalSoilTrade/Source/FungalSoilTradeOptions.cs | 11 | 422 | - | OK | -138 |  |
| src/RimStarWars/SWBestiary/Source/BeastMechanics/RSW_BeastMechanicsSettings.cs | 7 | 420 | - | OK | -140 |  |
| src/RimMandrake/AcousticScanner/Source/RM_AcousticScannerMod.cs | 14 | 406 | - | OK | -154 |  |
| src/RimMandrake/Visibility/Source/RM_VisibilityMod.cs | 9 | 406 | - | OK | -154 |  |
| src/RimUtinni/RestrainingBolts/Source/RestrainingBoltsMod.cs | 9 | 388 | - | OK | -172 |  |
| src/RimMandrake/Aftermath/Source/RM_AftermathMod.cs | 9 | 384 | - | OK | -176 |  |
| src/RimStarWars/SWBestiary/Source/Livestock/RSW_LivestockSettings.cs | 9 | 384 | - | OK | -176 |  |
| src/RimUtinni/Antiquities/Source/AntiquitiesMod.cs | 9 | 366 | - | OK | -194 |  |
| src/RimMandrake/Inhabited/Source/RM_InhabitedMod.cs | 6 | 338 | - | OK | -222 |  |
| src/RimMandrake/Oracle/Source/OracleSettings.cs | 10 | 334 | - | OK | -226 |  |
| src/RimUtinni/PropaneLakeMechanics/Source/PropaneLakeMechanicsSettings.cs | 8 | 332 | - | OK | -228 |  |
| src/RimMandrake/Wreckage/Source/RM_WreckageMod.cs | 9 | 318 | - | OK | -242 |  |
| src/RimMandrake/Stillsand/Source/RM_StillsandMod.cs | 6 | 316 | - | OK | -244 |  |
| src/RimUtinni/ScarlandsLadder/Source/PilgrimCamps.cs | 4 | 230 | - | OK | -330 |  |
| src/RimUtinni/UtinniStatues/Source/UtinniStatuesMod.cs | 3 | 222 | - | OK | -338 |  |
| src/RimUtinni/DroidRepairJobs/Source/DroidRepairJobsMod.cs | 5 | 220 | - | OK | -340 |  |
| src/RimUtinni/ShokkweaveEconomy/Source/ShokkweaveEconomySettings.cs | 2 | 214 | - | OK | -346 |  |
| src/RimUtinni/StructureInjectionsRUT/Source/StructureInjectionsRUTSettings.cs | 2 | 214 | - | OK | -346 |  |
| src/RimMandrake/BiomesShell/Source/RM_BiomesMod.cs | 6 | 188 | rows * rowH | OK | -372 |  |
| src/RimMandrake/StructureInjections/Source/RM_StructureInjectionsMod.cs | 1 | 184 | - | OK | -376 |  |
| src/RimStarWars/DesertVehicleReskin/Source/Fuel/RSW_DesertVehicleReskinSettings.cs | 1 | 184 | - | OK | -376 |  |
| src/RimStarWars/TrophyCraft/Source/RSW_TrophyCraftSettings.cs | 3 | 178 | - | OK | -382 |  |
| src/RimMandrake/TheBazaar/Source/RM_BazaarSettings.cs | 2 | 170 | - | OK | -390 |  |
| src/RimUtinni/RiverColors/Source/RiverColorsMod.cs | 3 | 160 | - | OK | -400 |  |
| src/RimUtinni/ShipMemory/Source/ShipMemorySettings.cs | 3 | 156 | - | OK | -404 |  |
| src/RimMandrake/GravshipLanding/Source/GravshipLandingMod.cs | 1 | 140 | - | OK | -420 |  |
| src/RimMandrake/LoreStages/Source/RM_LoreStagesMod.cs | 1 | 140 | - | OK | -420 |  |
| src/RimUtinni/KyberTradePlot/Source/KyberTradePlotSettings.cs | 1 | 140 | - | OK | -420 |  |
| src/RimMandrake/FlowWorks/Source/ManyWaters/RiverSteamSettings.cs | 3 | 134 | - | OK | -426 | SKIPPED (other agents) |
| src/RimMandrake/SacredGraffiti/Source/RM_SacredGraffitiMod.cs | 3 | 134 | - | OK | -426 |  |
| src/RimUtinni/EggReckoning/Source/EggReckoningSettings.cs | 1 | 118 | - | OK | -442 |  |
| src/RimStarWars/SWBestiary/Source/JawaIkee/RSW_JawaIkeeSettings.cs | 1 | 96 | - | OK | -464 |  |
| src/RimUtinni/WildsteamEggBounty/Source/WildsteamEggBountySettings.cs | 1 | 96 | - | OK | -464 |  |
| src/RimMandrake/RustChrome/Source/RustChromeMod.cs | 1 | 74 | - | OK | -486 |  |
| src/RimUtinni/EmpirePursuit/Source/Settings.cs | 1 | 30 | - | OK | -530 |  |
| src/RimMandrake/SeaShores/Source/RM_SeaShoresMod.cs | 0 | 0 | - | OK | -560 |  |
| src/RimUtinni/PropaneLakeMechanics/Source/PropaneLakeMechanicsMod.cs | 0 | 0 | - | OK | -560 |  |
