# Census of shipped mod code that gates a mechanic by biome (read-only helper, 2026-11-21)

Not a ruling. Each row is a pointer for review; the helper lists at its end where it did not look.

This is a census with no files changed. I read about 130 of the 575 filtered C# hits in context and classed the rest from the hit line. Paths below are relative to `/home/mandrake/rm/bench/src/RimMandrake/`.

Two classing rules I used:
- A hard-coded `defName == "RM_X"` check in a runtime behaviour is MECHANIC-GATE.
- A mechanic that runs only where the biome carries a `DefModExtension` is listed as UNCLEAR "ext". It is data-driven, but the mechanic is still off everywhere else. The owner's ruling decides how these are classed.

## MECHANIC-GATE and UNCLEAR rows (66 rows)

| # | Mod | file:line | What is gated | How | Class |
|---|---|---|---|---|---|
| 1 | TheForge | `TheForge/Source/RM_ForgeSkyPastures.cs:40` and `:215`; `Kernel/RM_SkyKernel.cs:51-59` | Geyser vapour-column haze and ash spirals are drawn only on The Forge. This is the d07e03a938 case: "Biome mechanics are promised inside our own biomes only". | `ColumnVisualsShow(setting, defName)` compares to `HomeBiome="RM_TheForge"` | MECHANIC-GATE |
| 2 | Pyrelands | `Pyrelands/Source/RM_JobGiver_BurrowOnFire.cs:76-80` | The ashwallow dive from fire runs only on a Pyrelands map. This is the 675ab57651 case. | `burnLine.IsPyrelandsMap`, which is a defName list at `MapComponent_BurnLine.cs:146-158` | MECHANIC-GATE |
| 3 | Pyrelands | `MapComponent_BurnLine.cs:150-158` | The burn line is measured only on Pyrelands maps. | `PyrelandsBiomeDefNames` | MECHANIC-GATE |
| 4 | Pyrelands | `FireEcologyHook.cs:128-149`, `:197` | Fire ecology (ash, scorch, fruit) runs per map: native biome, or an opted-in map. | `FireEcologyOnMap(native, RM_PyrelandsSettings.AppliesToBiome)` | MECHANIC-GATE |
| 5 | Pyrelands | `PyrelandsAshSand.cs:153` | Ambient ash-sand build-up runs on the native biome, or on opted-in maps at the coverage percentage. | `defName == NativeBiomeDefName` plus `crossBiomeCoverage` | MECHANIC-GATE |
| 6 | Pyrelands | `PyrelandsNoOrdinaryRain.cs:40` | Ordinary rain turns into black rain only in Pyrelands. | `PyrelandsBiomeDefNames` | MECHANIC-GATE |
| 7 | Pyrelands | `PyrelandsHerdThirst.cs:43` | Herd thirst runs only in Pyrelands. | `defName != "RM_Pyrelands"` early return | MECHANIC-GATE |
| 8 | Pyrelands | `PyrelandsFireSense.cs:54` | Fire sense applies only in Pyrelands. | `defName == "RM_Pyrelands"` | MECHANIC-GATE |
| 9 | Pyrelands | `ThinkNode_ConditionalPyrelandsColonist.cs:19-20` | The colonist fire behaviour applies only in Pyrelands. | `defName == "RM_Pyrelands"` | MECHANIC-GATE |
| 10 | Pyrelands | `PyrelandsMechanicsGate.cs:28-47`; `RM_PyrelandsMod.cs:46` | Every Pyrelands mechanic reads `pyrelandsEnabled` ("Mod enabled") plus the shell's per-biome `Enabled(key)`, found by reflection. | Per-biome setting | MECHANIC-GATE |
| 11 | Pyrelands | `RM_PyrelandsMod.cs:209-210` | The cross-biome opt-in switch (setting #1 in the switch list below). | Setting | MECHANIC-GATE |
| 12 | Pyrelands | `PyrelandsAshField.cs:161` | The ash-field scan shortcuts to true on a Pyrelands biome. It also detects by terrain extension. | defName | UNCLEAR |
| 13 | Pyrelands | `PyrelandsForeignArrivals.cs:43-53`; `Patches/RM_Pyrelands_NoForeignArrivals.xml:15-70` | Foreign herds and aggressive animals are kept out of Pyrelands. This is 6 incident patches with `<disallowedBiomes>`. | Harmony postfix and def list | UNCLEAR |
| 14 | TheRot | `TheRot/Source/RM_LivingMatRoot.cs:126`, `:172`, `:464` | The living mat eats food and dies back when food runs out. Outside the Rot it is switched by `InRot`, and `portableWarmMatDieBack` applies only when `!InRot`. | `IsRotBiome(map.Biome)` | MECHANIC-GATE |
| 15 | TheRot | `RM_LivingMatRoot.cs:305-306` | The mat heats rooms only when the biome carries `RM_WarmGroundExtension` and `Enabled("warmGround")`. | ext | MECHANIC-GATE |
| 16 | TheRot | `RM_TheRotMod.cs:163-177`, `:447`, `:456-470`; `RM_TheRotMod.cs:485-497` | The Rot's kit mechanics are on or off by `Governs(biome)` (Rot or opt-in). Outside that, the intensity is `crossBiomeCoverage`. | Per-biome setting | MECHANIC-GATE |
| 17 | TheRot | `Defs/GameConditionDefs/RM_RotSporeKit_SporeCloud.xml:80` | The spore-cloud condition names `<disallowedBiomes>`. | def list | UNCLEAR |
| 18 | EnvHazards | `EnvironmentalHazards/Source/RM_MapComponent_WarmGround.cs:93-94` | Warm ground (floor heat) runs only where the biome carries `RM_WarmGroundExtension` and `Enabled`. | ext + `KitFronts` | MECHANIC-GATE |
| 19 | EnvHazards | `RM_MapComponent_AcceleratedRot.cs:65-66` | Accelerated rot (food spoils faster) runs only where the biome carries `RM_AcceleratedRotExtension`. | ext + `KitFronts` | MECHANIC-GATE |
| 20 | EnvHazards | `RM_IncidentWorker_SporeCloud.cs:25`; `RM_SporeAllergyIncidents.cs:11`, `:29`; `RM_MapComponent_LivingProduce.cs:35`; `RM_Patch_LivePrepViability.cs:68`; `RM_HediffComp_SheenExposure.cs:43` | Spore cloud, spore allergy, live-produce heat, strict live prep, sheen exposure. | `RM_KitFronts.Enabled(key, biome)` per-biome switch | MECHANIC-GATE |
| 21 | EnvHazards | `RM_IncidentWorker_SteamDevil.cs:27`; `RM_MapComponent_RoilVortexSpawner.cs:75` | Steam devils and roil vortices appear only in Greentide. | defName | MECHANIC-GATE |
| 22 | EnvHazards | `RM_HediffComp_ForgeOnSurvival.cs:132-133` (7 `<onlyInBiomes>` entries in `Miasma/Patches/RM_Miasma_ForgeOnSurvival.xml:74-224`) | The forge-on-survival hediff effect fires only in Miasma. | def list `onlyInBiomes` | MECHANIC-GATE |
| 23 | EnvHazards | `RM_IncidentWorker_ContagionProbe.cs:36` | The contagion probe incident fires only on The Forge. | defName | UNCLEAR |
| 24 | EnvHazards | `RM_IncidentWorker_WalkerSurfacing.cs:39`; `TerminalBiomes/Defs/IncidentDefs/RM_WalkerSurfacing.xml:63` | The walker surfacing incident is limited to listed biomes. | `<allowedBiomes>` | UNCLEAR |
| 25 | EnvHazards | `RM_MapComponent_StrandingPools.cs:165`, `:286`; `RM_JobGiver_ReturnToWater.cs:49` | Stranding pools and returning to water run only if the biome carries `RM_StrandingPoolsExtension`. | ext | UNCLEAR |
| 26 | EnvHazards | `RM_MapComponent_GradientAxis.cs:233`, `:277`; `RM_GameCondition_GradientSurge.cs:51` | The gradient axis and gradient surge need the biome's extension. | ext | UNCLEAR |
| 27 | EnvHazards | `RM_MapComponent_WaterTruce.cs:64`; `RM_MapComponent_CarriedFilthHediffLink.cs:32` | Water truce and the carried-filth hediff link need the biome's extension. | ext | UNCLEAR |
| 28 | EnvHazards | `RM_MapComponent_SumpLivingMap.cs:87` | Sump living map; I did not read the context. | biome read | UNCLEAR |
| 29 | CreatureBehaviors | `CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs:172-175` | Every map-wide sun-heat effect is "gated on it": the biome must carry `RM_SunHeatExtension`. This is the Stillshade sun-exposure mechanic. | ext | MECHANIC-GATE |
| 30 | CreatureBehaviors | `RM_MapComponent_PinnedSun.cs:63`; `RM_HeatSoundscape.cs:127`, `:175`; `RM_TrackGridPatches.cs:106`; `RM_TrackSurfaceExtension.cs:84` | Pinned sun, heat soundscape and track surface run only on biomes with the extension or listed in `<biomes>`. | ext and list | MECHANIC-GATE |
| 31 | LongShade | `LongShade/Source/RM_ShadeExtras.cs:46`; used at `:79`, `:290`, `:539`, `:596` | Tollok infestation, stampede and the other Stillshade extras run only on RM_LongShade. | defName | MECHANIC-GATE |
| 32 | LongShade | `Defs/IncidentDefs/RM_SmokeHaze.xml:48`; `RM_ShadeStampede.xml:13` | Smoke haze and shade stampede are allowed only in RM_LongShade. | `<allowedBiomes>` | UNCLEAR |
| 33 | LongShade | `RM_ShipfallCommons.cs:129` | Shipfall commons need the extension. | ext | UNCLEAR |
| 34 | Stillsand | `Stillsand/Source/RM_MapComponent_Zuurrik.cs:84-87`, `:97` | The zuurrik swarm wakes only in RM_Stillsand. | defName | MECHANIC-GATE |
| 35 | Stillsand | `RM_DuneTrackEraser.cs:124` | Dune wind erases tracks only in RM_Stillsand. | defName | MECHANIC-GATE |
| 36 | Stillsand | `RM_SandSwimRemainder.cs:131` (used `:136`, `:167`) | Sand-listening hiss runs on any biome whose name contains "Stillsand". | `defName.Contains` | MECHANIC-GATE |
| 37 | Stillsand | `RM_DuneGale.cs:115`; `RM_WaterLedger.cs:102`; `RM_SandLeviathan.cs:179` | Dune gale, water ledger and sand leviathan work only on listed biomes. | `biomes` list on the def extension | MECHANIC-GATE |
| 38 | Stillsand | `RM_StillsandWater.cs:132`; `RM_GiantSkeletons.cs:320`, `:448`; `RM_HorizonWarning.cs:190`; `RM_PreciousCaves.cs:657` | Sand remembers water, giant skeletons, horizon warning and precious caves need the extension. | ext | UNCLEAR |
| 39 | Stillsand | `Defs/IncidentDefs/RM_SandBusterEruption.xml:42`; `RM_SandLeviathanIncidents.xml:34`; `Defs/WeatherDefs/RM_DuneGale.xml:247` | Sand buster, leviathan and dune gale are tied to biomes. | `<allowedBiomes>` / `<biomes>` | UNCLEAR |
| 40 | Scald (DivingInteraction) | `DivingInteraction/Source/RM_MapComponent_ScaldVentForecast.cs:43`; `RM_MapComponent_ScaldImmersionBerth.cs:32` | The vent forecast (steam clock) and the immersion berth run only on Scald floor maps. | defName | MECHANIC-GATE |
| 41 | Scald / Chill | `RM_ChillFireGate.cs:30`; `RM_MapComponent_ChillBoilShroud.cs:106` | The Chill boil shroud runs only on Chill seabed maps. | defName plus pocket-map flag | MECHANIC-GATE |
| 42 | DivingInteraction | `RM_SeaDiveHatch.cs:44-45`, `:68-69` | The sea-dive hatch accepts only biomes in `SeaGenerators`. | defName table | UNCLEAR |
| 43 | TerminalBiomes | `TerminalBiomes/Source/RM_GreyHullCrust.cs:36` | Grey hull crust runs on Grey Sea maps. | defName | MECHANIC-GATE |
| 44 | TerminalBiomes | `RM_PlaceWorker_ChillFloorOnly.cs:17-19` | Chill-floor-only placement. | defName plus pocket-map flag | MECHANIC-GATE |
| 45 | TerminalBiomes | `RM_MapComponent_VeilFall.cs:60`; `RM_MapComponent_WellLedger.cs:130-131`; `RM_TwilightFloraBehaviour.cs:50` | Veil fall, well ledger and twilight flora behaviour run only on Twilight Sea maps. | defName | MECHANIC-GATE |
| 46 | TerminalBiomes | `RM_JobGiver_SeekGlow.cs:36`; `RM_GreyLampResponse.cs:484` | Seek-glow is gated by `ext.onlyBiome`; the Grey lamp response refuses non-Grey maps. | ext field / defName | MECHANIC-GATE |
| 47 | TerminalBiomes | `Defs/IncidentDefs/RM_SuulkArrival.xml:40`; `RM_VeilFallPaneStrike.xml:39`; `RM_IncidentWorker_SuulkArrival.cs:36` | Suulk arrival and veil-fall pane strike are limited to biomes. | `<allowedBiomes>` | UNCLEAR |
| 48 | Scarlands | `Scarlands/Source/RM_WarscarMark.cs:193`; `RM_ChatrakSnap.cs:305` | Warscar mark and chatrak snap run only in the Warscar. | `map.Biome != Warscar` | MECHANIC-GATE |
| 49 | Scarlands | `RM_Settling.cs:225`; `MapComponent_WreckLichen.cs:45`; `RM_WarscarMod.cs:183-196` | Settling and wreck lichen run on the Warscar or an opted-in map (lichen strength by slider). | `RM_WarscarSettings.Governs` and `Coverage` | MECHANIC-GATE |
| 50 | Scarlands | `RM_WarscarPatches.cs:19` | The Warscar rarity patch applies only to RM_Warscar. | defName | UNCLEAR |
| 51 | Miasma | `Miasma/Source/RM_DecayCells.cs:128`; `RM_MapComponent_FlotsamYard.cs:32`; `RM_MapComponent_YoungCall.cs:27` | Decay cells, flotsam yard and young call run only in Miasma. | defName | MECHANIC-GATE |
| 52 | Miasma / BlueDesert / TheSump | `Miasma/Defs/IncidentDefs/RM_Surge.xml:71`; `BlueDesert/Defs/IncidentDefs/RM_AblationSalvage.xml:58`; `TheSump/Defs/IncidentDefs/RM_TarPitBelch.xml:51` | Surge, ablation salvage and tar-pit belch are limited to their biome. | `<allowedBiomes>` | UNCLEAR |
| 53 | Abyss | `Abyss/Source/RM_MapComponentDark.cs:88`, `:258`; `RM_AbyssSoundHook.cs:32`; `RM_AbyssSoundscape.cs:48`, `:127`; `RM_AbyssCryptid.cs:52`; `RM_MapComponentShipCover.cs:58` | Darkness tick, sound, gust soundscape, cryptid signs and ship cover run only in the Abyss. | defName | MECHANIC-GATE |
| 54 | Cauldron | `Cauldron/Source/RM_AcidAir.cs:47` | Acid air burns pawns only on biomes with `RM_AcidAirExtension`. | ext | MECHANIC-GATE |
| 55 | Cauldron | `RM_VentBloomExposure.cs:75`; `RM_AcidAir.cs:64` | Animals native to the biome are exempt. Their native status is read from the biome's animal list. | `CommonalityOfAnimal` | UNCLEAR |
| 56 | Cauldron | `RM_CauldronRuinKit.cs:127`; `RM_CauldronVents.cs:320` | Ruin kit and vents are placed only in the Cauldron. | defName | BIOME-DATA (map gen) |
| 57 | Contagion | `Contagion/Source/CompZhoolHaze.cs:119-141` | Zhool haze converts only on a map whose biome comes from a `mandrake.*` mod. | `OurBiome`, package-id prefix | MECHANIC-GATE |
| 58 | Contagion | `RM_ContagionSkyExtension.cs:77`; `RM_GameCondition_ContagionBurn.cs:58` | Contagion sky and burn need the biome's extension; natives are exempt. | ext | UNCLEAR |
| 59 | FeverWood | `FeverWood/Source/RM_OilBoil.cs:82` | Oil boil needs the weather to be in the biome's weather table at its temperature. | `baseWeatherCommonalities` | UNCLEAR |
| 60 | LeaningScrub | `LeaningScrub/Source/RM_TheLean.cs:114`, `:143`; `RM_PlantLean.cs:144`, `:244-247` | Plants lean only if the biome carries `RM_LeanExtension` ("does not lean (needs a Leaning Scrub map)"). | ext | MECHANIC-GATE |
| 61 | LeaningScrub | `RM_VenomvineIslands.cs:57` | Venomvine islands need the extension. | ext | UNCLEAR |
| 62 | GelatinousSlime | `GelatinousSlime/Source/GeneSeeker.cs:112`, `:279`; `FarmRuins.cs:52`; `SlimeVisitors.cs:55`, `:231` | Gene extraction ("Not on a gelatinous slime map."), farm ruins and slime visitors run only on the slime biome. | `map.Biome == SlimeDefs.GelatinousSlime` | MECHANIC-GATE |
| 63 | GelatinousSlime | `SlimeExposure.cs:114` | Slime exposure runs only if the biome lays slime grass. | `BiomeLaysSlimeGrass` | UNCLEAR |
| 64 | Greentide | `Greentide/Source/RM_MapComponent_CrossBiomeChurnmud.cs:59`; `Kernel/RM_RulesKernel.cs:36-40`; `RM_StellockLace.cs:53` | Churnmud conversion on foreign maps (setting-driven). Stellock lace branches drop only if felled in Greentide. | `AppliesToBiome`, defName | MECHANIC-GATE |
| 65 | CrackedLands / ExplosiveGrowth | `CrackedLands/Source/RM_MercyLedges.cs:296`; `RM_FossilStrata.cs:240`; `RM_MapComponent_CanyonFlood.cs:126`; `ExplosiveGrowth/Source/RM_ExplosiveGrowthRegistry.cs:95-104`, `:129-134`; `RM_MapComponent_ExplosiveGrowth.cs:135`, `:176`, `:340`, `:479`; `RM_SoakSources.cs:54`; `RM_IncidentWorker_BloomBurst.cs:41` | The flood cycle and mercy ledges run only in Flooded Canyon. Explosive growth runs only in `HomeBiomes`; vanilla crops need water only in scope; soak is refused in `noSoakBiomes`; snowmelt applies in `snowmeltBiomes`. | def or hash list, biome checks, settings | MECHANIC-GATE |
| 66 | Other runtime gates | `Webwork/Source/RM_WebworkSiege.cs:65`; `WeepingStones/Source/RM_WalkingCondenser.cs:63`; `SleepingIce/Source/RM_HeatDial.cs:45`; `RustCathedral/Source/Hum/RM_MapComponent_BiomeAttitude.cs:409-424`; `Hum/RM_HumReading.cs:111`, `:204`; `Hum/RM_HullBolts.cs:83`, `:237`; `Hum/RM_LineCycle.cs:60`, `:180`; `Hum/RM_IncidentWorker_CathedralResponse.cs:96`; `Walls/HarmonyPatch_GateLivePatternMetal.cs:46`; `Wastes/Source/RM_Middenshell.cs:861`; `Wastes/Source/RM_MapComponent_WastesStorms.cs:46`; `Minerals/Source/RM_MineralQuarry.cs:116-132` | Webwork siege, the walking condenser, the Sleeping Ice heat dial, the whole Cathedral hum/attitude system, hull bolts, line cycle, the Cathedral response, live-pattern metal, Middenshell, Wastes storms and the mineral quarry. Most run only on their own biome (defName, `targetBiome`, ext). The mineral quarry picks its plan by biome. | defName / ext / def table | MECHANIC-GATE (UNCLEAR for Wastes storms and Minerals quarry) |

Also a MECHANIC-GATE: `LanternDeeps/Source/RM_AuroraCollapse.cs:268-269` (collapse warnings only in the home biome) and `Patch_GateLanternstoneDeep.cs:29`. Both are hard defName checks. They sit outside the 66 numbered rows.

XML incident rows in the table (13, 17, 24, 32, 39, 47, 52) are UNCLEAR because an incident's biome list can read as "weather and event odds are biome data". I did not decide that.

## BIOME-DATA counts

The XML counts are measured with grep. The C# counts are my own file counts.

| Mod | C# files (judgement) | XML hits (measured) | Two examples |
|---|---|---|---|
| BiomesShell | 8 | n/a | world look and landmarks (`RM_WorldLook.cs:197`); canopy |
| RustCathedral | 4 | 3 | `RM_GenStep_BorehulkPlacement.cs:38`; `GenStep_ScatterSacredWalls.cs:39` |
| EnvironmentalHazards | 9 | 4 `biomeWhitelist` | `RM_GenStep_LivingBoles.cs:31`; `RM_GenStep_RootCauseways.cs:47` |
| FlowWorks | 7 | 20 `<biomes>` | `RM_WorldComponent_LiquidTags.cs:114`; `RM_DigDiscovery.cs:688` |
| Minerals | 3 | 48 | `RM_MineralSurface.cs:117`; `RM_MineralRegistry.xml:135` |
| Webwork | 3 | 0 | `RM_GenStep_WebworkNest.cs:46`; `RM_GenStep_WebworkWeb.cs:50` |
| LanternDeeps | 5 | 7 | `GenStep_ScatterLanternstone.cs:58`; `GenStep_ScatterCavePortal.cs:36` |
| Cauldron | 4 | 0 | `RM_CauldronVents.cs:320`; `RM_CompRhossakGrove.cs:156` |
| Stillsand | 3 | 7 | `RM_StillsandTraderProbe.cs:37`; Stillsand track-surface patch |
| Others (FeverWood, TheSump, Warcasket, MovingDunes, SeaShores, TileFeatures, SolarMirrors, TheBazaar, Pyrelands, HugeThings, ColdStorage, DeepDrill, WeatherSuite, AcousticScanner, DivingInteraction seafloor gen steps) | about 25 | Abyss 1, Scarlands 1, Wastes 2, Greentide 2, Pyrelands 3 | `RM_GenStep_AntHiveDungeon.cs:53`; `GenStep_SeaFloorFauna.cs:39` |

## Cross-biome and per-biome settings switches

All defaults below were read from the code.

| Mod | Setting (label) | Default |
|---|---|---|
| Pyrelands | `crossBiomeEnabled` "Enable outside the Pyrelands biome" (`RM_PyrelandsMod.cs:176`, `:610`); `crossBiomeEverywhere` "Every biome"; `crossBiomeBiomeList`; `crossBiomeCoverage` | false / false / "" / 1.0 |
| Pyrelands | `pyrelandsEnabled` "Mod enabled" (`:46`) | true |
| TheRot | `crossBiomeEnabled` "Enable outside The Rot biome" (`RM_TheRotMod.cs:158`, `:417`) plus the same three sub-settings | false / false / "" / 1.0 |
| Scarlands | "Enable outside the Warscar" (`RM_WarscarMod.cs:292`, `:728`), plus the same three | false / false / "" / 1.0 |
| TerminalBiomes | "Enable outside the Scald biome" (`RM_TerminalBiomesMod.cs:276`, `:687`), plus the same three | false / false / "" / 1.0 |
| RustCathedral | "Allow this mod's mechanics on other biomes" (`RM_RustCathedralMod.cs:151`, `:361`), plus the same three | false / false / "" / 1.0 |
| Greentide | "Enable outside the Greentide biome" (`RM_GreentideMod.cs:177`, `:325`), plus the same three | false / false / "" / 1.0 |
| CrackedLands | `featureInOtherBiomes` "Run the flood cycle in other biomes too" (`RM_CrackedLandsMod.cs:155`, `:227`) | false |
| CrackedLands | `fossilSeamsInOtherBiomes` "Fossil seams in other biomes too (worldgen)" (`:164`, `:282`) | false |
| ExplosiveGrowth | `nativesSameRuleInOtherBiomes` "UNSUPPORTED: our plants follow the same rule in other biomes" (`ExplosiveGrowthMod.cs:122`, `:243`) | false |
| BiomesShell | Per-biome roster `enabled[key]` (`RM_BiomesMod.cs:123-130`). It gates Pyrelands and ExplosiveGrowth mechanics (`mechanicsGated`). | true |
| LanternDeeps | `entranceBiomes` list (`LanternDeepsMod.cs:115-122`) | BiomeGRimond, RM_SleepingIce, RM_TheChill |
| Minerals | `OtherBiomes` policy per mineral row (`RM_MineralPolicyKernel.cs:17`, `:239`) | not read |

The "Unsupported: may work outside our biomes, not tested." text is a Keyed string for Greentide, Pyrelands, Scarlands, TerminalBiomes, TheRot and RustCathedral.

## Totals and gaps

- **Totals per mod (rows in my table, not hits).**
  - EnvHazards 10.
  - Pyrelands 13.
  - Stillsand 6.
  - TerminalBiomes 5.
  - TheRot 4.
  - Scarlands 3.
  - LongShade 3.
  - CreatureBehaviors 2.
  - The following have 1 row each: TheForge, DivingInteraction, Miasma, Abyss, Cauldron, Contagion, FeverWood, LeaningScrub, GelatinousSlime, Greentide, CrackedLands/ExplosiveGrowth (shared row), and "Other runtime gates" (shared row).
  - The grep found 575 filtered C# hit lines in total.
- **Mods with no hit:** Aftermath, AtmosphericBase, Bones, ExplosiveKnockback, FlameStatues, GimmeSomeSlack, Graffiti, GravshipLanding, Inhabited, KeelHoist, KineticArms, LoreStages, LuminousPigment, MandrakePatches, MineShaft, NullTexTrace, OasisMaker, Oracle, PlanetPresetPrime, ProximityHatch, Pyrinth, RaidRedesigner, RustChrome, SacredGraffiti, ShipVermin, StructureInjections, Visibility, Watchers, Wreckage and WreckedMachines. I mean "no hit on my patterns". I did not read these mods for gates that use other patterns.
- **Rows I classed from the hit line only:** I did not open the surrounding code for rows 28, 55, 59 and 63, or for parts of the "Other runtime gates" row (Minerals quarry, Wastes storms). I also did not open RustCathedral beyond the BiomeAttitude lookup and a few reads.
- **Places I did not search:**
  - `Utils/`, `tools/`, `rimflow/`, `mapsynth/`, `arena/`, `contracts/`, `RimDefDump/` and `LoadTracer/` (excluded as dev tooling), and the 42 `JawaBench.BridgeTools` hits (dev tooling, not classed).
  - Files whose name contains "Test", "Selftest", "proof" or "validation". About 10 `*Proof.cs` classes sit inside shipped mod DLLs (for example `LongShade/Source/RM_ShadeExtrasProof.cs`, `Scarlands/Source/RM_HospiceProof.cs`). Per your instruction I skipped them. A path filter on "test" may also have dropped an unrelated filename.
  - Patterns outside my regex: string compares such as `b == "RM_..."` where no `.Biome` appears in the same line, XML element names like `commonalityPerBiome` or `biomeDefs`, and PatchOperation xpaths that target a BiomeDef.
  - `Languages/` and `Textures/` XML.
  - I did not run the game or check how each mod behaves on a foreign biome. Every row is from reading the source.
