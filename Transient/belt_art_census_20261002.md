# Belt art census 2026-10-02 (build pause: shipped defs only)

Instrument: `scratchpad/census.py` + `classify.py` (python; texPath/flyingAnimationFramePathPrefix of non-abstract Thing/PawnKind/Terrain/Plant defs prefixed RM_/RSW_/RUT_ under src/**/Defs).
Art-exists = loose PNG (or _north/_east/_south variants, or folder) under any src Textures dir, or any installed Mods/workshop Textures dir. 2273 texPath rows over 1820 defs: 1986 exist, 287 missing.
Missing split: 53 rows vanilla-looking (Things/... with no own prefix; live in resources.assets, NOT checked, excluded), 234 rows / 217 defs own-looking (own prefix or donor roots swanimals/swresource/swplants/OasisMaker; donor roots may be absent donor mods).
Sanity probe: korrum / stoneback artpipe hit counts printed at run time: ({'artsrc': 3, 'done': 6, 'reg': 0, 'dec': 1}, {'artsrc': 3, 'done': 6, 'reg': 57, 'dec': 1}).
Classification: ART_EXISTS_UNWIRED = finished _artsrc/done art matches name; UNCERTAIN = queued, registry/decision mention only, or placeholder/test; NEEDS_REGEN = no trace anywhere.
Caveat: name-substring matching; inherited (ParentName) graphicData and non-ThingDef graphics not covered.

Counts: {'ART_EXISTS_UNWIRED': 154, 'NEEDS_REGEN': 51, 'UNCERTAIN': 12}


## NEEDS_REGEN

| def | kind | first missing texPath (+n more) | file | evidence |
|---|---|---|---|---|
| RUT_YearningFruitHarvested | ThingDef | Things/Item/Plant/RUT_YearningFruitHarvested | RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_YearningFruit.xml |  |
| RUT_DyingCreep | ThingDef | Things/Plant/RUT_DyingCreep | RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_DyingCreep.xml |  |
| RUT_MetalSaltBezoar | ThingDef | Things/Item/Resource/RUT_MetalSaltBezoar | RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_WastelandItems.xml |  |
| RUT_DeadCreep | ThingDef | Things/Filth/RUT_DeadCreep | RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_DeadCreep.xml |  |
| RUT_VentSmelter | ThingDef | Things/Building/Production/RUT_VentSmelter | RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_VentSmelter.xml |  |
| RUT_VentForge | ThingDef | Things/Building/Production/RUT_VentForge | RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_VentForge.xml |  |
| RUT_DryAirBlower | ThingDef | Things/Building/Production/RUT_DryAirBlower | RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_DryAirBlower.xml |  |
| RUT_VentKiln | ThingDef | Things/Building/Production/RUT_VentKiln | RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_VentKiln.xml |  |
| RUT_Fuzz | ThingDef | Things/Plant/RUT_Fuzz | RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_Fuzz.xml |  |
| RUT_SweetlineWool | ThingDef | Things/Item/Resource/RUT_SweetlineWool | RimUtinni/AshkarrFlora/Defs/ThingDefs_Items/RUT_SweetlineTree_Items.xml |  |
| RUT_GreentideAntSoldier | PawnKindDef | Things/Pawn/Animal/RUT_GreentideAnt/RUT_GreentideAnt | RimUtinni/GreentideRaidAnt/Defs/ThingDefs_Races/RUT_PawnKinds_GreentideAnt.xml |  |
| RUT_GreentideAntCarapaceWall | ThingDef | Things/Building/Linked/RUT_GreentideAntCarapaceWall_Atlas | RimUtinni/GreentideRaidAnt/Defs/ThingDefs_Buildings/RUT_Building_GreentideAntCarapaceWall.xml |  |
| RSW_RawBloddle | ThingDef | swresource/PlantFoodRaw/Bloddle | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Plants.xml |  |
| RSW_RawChakroot | ThingDef | swresource/PlantFoodRaw/Chakroot | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Plants.xml |  |
| RSW_RawHubbaGourd | ThingDef | swresource/PlantFoodRaw/HubbaGourd | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Plants.xml |  |
| RSW_RawNysyllin | ThingDef | swresource/PlantFoodRaw/Nysyllin | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Plants.xml |  |
| RSW_Ikee | PawnKindDef | Things/Pawn/Animal/RSW_Ikee/RSW_Ikee | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml |  |
| RSW_Zhakka | PawnKindDef | Things/Pawn/Animal/RSW_Zhakka/RSW_Zhakka | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml |  |
| RSW_SurraGrass | ThingDef | Things/Plant/RSW_SurraGrass | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Plants.xml |  |
| RSW_DommoTree | ThingDef | Things/Plant/RSW_DommoTree | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Plants.xml |  |
| RSW_Uvak | PawnKindDef | swanimals/Uvak/Uvak_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Uvak.xml |  |
| RSW_Porg | PawnKindDef | swanimals/Porg/Porg_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Porg.xml |  |
| RSW_PustuleHornetSpawned | PawnKindDef | swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/PustuleHornet/PustuleHornet_Flying_ | RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml |  |
| RSW_ColonyPustuleHornetQueen | PawnKindDef | swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/PustuleHornetQueen/PustuleHornetQueen_Flying_ | RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml |  |
| RSW_ColonyPustuleHornet | PawnKindDef | swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/PustuleHornet/PustuleHornet_Flying_ | RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml |  |
| RSW_PustuleHornetQueen | PawnKindDef | swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/PustuleHornetQueen/PustuleHornetQueen_Flying_ | RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml |  |
| RSW_SmogMoth | PawnKindDef | swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/SmogMoth/SmogMoth_Flying_ | RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml |  |
| RSW_Sacapillar | PawnKindDef | swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/SacaPillar/SacaPillar_Flying_ | RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml |  |
| RSW_PustuleHornet | PawnKindDef | swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/PustuleHornet/PustuleHornet_Flying_ | RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml |  |
| RUT_LivingBolt | PawnKindDef | Things/Pawn/Animal/RUT_LivingBolt/RUT_LivingBolt (+1) | RimMandrake/RustCathedral/Defs/ThingDefs_Races/RUT_LivingBolt.xml |  |
| RM_ColdWax | ThingDef | Things/Item/Resource/RM_ColdWax/RM_ColdWax | RimMandrake/BlueDesert/Defs/ThingDefs_Items/RM_ColdWax.xml |  |
| RM_AblationEmergence | ThingDef | Things/Special/RM_AblationSilhouette | RimMandrake/BlueDesert/Defs/IncidentDefs/RM_AblationSalvage.xml |  |
| RM_IlbareenDead | ThingDef | Things/Plant/RM_Ilbareen/RM_Ilbareen_dead | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_Mangals.xml |  |
| RM_DeltaSalt | ThingDef | Things/Item/Resource/RM_DeltaSalt/RM_DeltaSalt | RimMandrake/Miasma/Defs/ThingDefs_Items/RM_Miasma_Goods.xml |  |
| RM_DeltaSilt | ThingDef | Things/Item/Resource/RM_DeltaSilt/RM_DeltaSilt | RimMandrake/Miasma/Defs/ThingDefs_Items/RM_Miasma_Goods.xml |  |
| RM_OasisMaker | ThingDef | OasisMaker/RM_OasisMaker | RimMandrake/OasisMaker/Defs/ThingDefs_Buildings/RM_OasisMaker.xml |  |
| RM_CinderCrust | ThingDef | Things/Plant/RM_CinderCrust | RimMandrake/TheForge/Defs/ThingDefs_Plants/RM_TheForge_Flora.xml |  |
| RM_RawDorvel | ThingDef | Things/Plant/RM_Dorvel/RM_Dorvel_a | RimMandrake/TheSump/Defs/ThingDefs_Items/RM_SumpFloraItems.xml |  |
| RM_RawSkelver | ThingDef | Things/Plant/RM_Skelver/RM_Skelver_a | RimMandrake/TheSump/Defs/ThingDefs_Items/RM_SumpFloraItems.xml |  |
| RM_KorvethPitch | ThingDef | Things/Plant/RM_Korveth/RM_Korveth_a | RimMandrake/TheSump/Defs/ThingDefs_Items/RM_SumpFloraItems.xml |  |
| RUT_BeastBulge | ThingDef | Things/Building/Natural/RUT_BeastBulge | RimMandrake/TheSump/Defs/ThingDefs_Buildings/RUT_BeastBulge.xml |  |
| RUT_MoatFusePost | ThingDef | Things/Building/Production/RUT_MoatFusePost | RimMandrake/TheSump/Defs/ThingDefs_Buildings/RUT_MoatFusePost.xml |  |
| RUT_Filth_MouseTrack | ThingDef | Things/Filth/RUT_MouseTrack | RimMandrake/TheSump/Defs/ThingDefs_Misc/RUT_Filth_MouseTrack.xml |  |
| RM_Graffiti_Glyph_Bloodfeeding | ThingDef | Things/Filth/Art/RM_Graffiti_Glyph_Bloodfeeding | RimMandrake/Graffiti/Defs/ThingDefs_GraffitiMemeGlyphs.xml |  |
| RM_SweetlineWool | ThingDef | Things/Item/Resource/RM_SweetlineWool | RimMandrake/LeaningScrub/Defs/ThingDefs_Items/RM_SweetlineTree_Items.xml |  |
| RUT_AncientShieldedTurret_Gun | ThingDef | Things/Building/Ancient/RUT_AncientShieldedTurret | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientSecurityAndUtility.xml |  |
| RUT_AncientSpacerAutocannon_Gun | ThingDef | Things/Building/Ancient/RUT_AncientSpacerAutocannon | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientSecurityAndUtility.xml |  |
| RM_FineSand | ThingDef | Things/Item/Resource/RM_FineSand | RimMandrake/Stillsand/Defs/ThingDefs_Items/RM_GlassChain_Items.xml |  |
| RM_LensGlass | ThingDef | Things/Item/Resource/RM_SunGlass | RimMandrake/Stillsand/Defs/ThingDefs_Items/RM_GlassChain_Items.xml |  |
| RM_SolarOvenCrest | ThingDef | Things/Building/Production/RM_SolarOven | RimMandrake/Stillsand/Defs/ThingDefs_Buildings/RM_GlassChain_Buildings.xml |  |
| RM_GreatboleHardwood | ThingDef | Things/Item/Resource/RM_GreatboleHardwood | RimMandrake/Greentide/Defs/ThingDefs/RM_Greentide_TreeRoster_Items.xml |  |

## ART_EXISTS_UNWIRED

| def | kind | first missing texPath (+n more) | file | evidence |
|---|---|---|---|---|
| RUT_YearningFruit | ThingDef | Things/Plant/RUT_YearningFruit | RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_YearningFruit.xml | artsrc=1 done=1 [yearningfruit]; reg=7 status=2 [yearningfruit] |
| RUT_DarkCrust | ThingDef | Things/Plant/RUT_DarkCrust | RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_PollutedFlora.xml | artsrc=1 done=1 [darkcrust] |
| RUT_Glower | ThingDef | Things/Plant/RUT_Glower | RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_ScarlandsFlora.xml | artsrc=4 done=4 [glower]; reg=14 status=0 [glower] |
| RUT_BloomCrop | ThingDef | Things/Plant/RUT_BloomCrop | RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_BloomCrop.xml | artsrc=1 done=1 [bloomcrop]; reg=11 status=2 [bloomcrop] |
| RUT_SealedSleeper | PawnKindDef | Things/Pawn/Animal/RUT_SealedSleeper/RUT_SealedSleeper | RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_SealedSleeper.xml | artsrc=3 done=3 [sealedsleeper]; reg=33 status=6 [sealedsleeper] |
| RUT_FleetFlier | PawnKindDef | Things/Pawn/Animal/RUT_FleetFlier/RUT_FleetFlier | RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_FleetFlier.xml | artsrc=3 done=3 [fleetflier] |
| RUT_Radiothermal | PawnKindDef | Things/Pawn/Animal/RUT_Radiothermal/RUT_Radiothermal | RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_Radiothermal.xml | artsrc=3 done=3 [radiothermal]; reg=36 status=9 [radiothermal] |
| RUT_VWake | PawnKindDef | Things/Pawn/Animal/RUT_VWake/RUT_VWake | RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PropaneLakeFauna.xml | artsrc=3 done=3 [vwake] |
| RUT_BrineBattery | PawnKindDef | Things/Pawn/Animal/RUT_BrineBattery/RUT_BrineBattery | RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_BrineBattery.xml | artsrc=6 done=6 [brinebattery]; reg=37 status=6 [brinebattery] |
| RUT_Karrobel | PawnKindDef | Things/Pawn/Animal/RUT_Karrobel/RUT_Karrobel | RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_Karrobel.xml | artsrc=1 done=1 [karrobel] |
| RUT_MortuaryCrawler | PawnKindDef | Things/Pawn/Animal/RUT_MortuaryCrawler/RUT_MortuaryCrawler | RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_MortuaryCrawler.xml | artsrc=3 done=3 [mortuarycrawler] |
| RUT_EmperorVulture | PawnKindDef | Things/Pawn/Animal/RUT_EmperorVulture/RUT_EmperorVulture | RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_EmperorVulture.xml | artsrc=3 done=3 [emperorvulture]; reg=33 status=6 [emperorvulture] |
| RUT_SlimeGrazer | PawnKindDef | Things/Pawn/Animal/RUT_SlimeGrazer/RUT_SlimeGrazer | RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_SlimeGrazer.xml | artsrc=6 done=6 [slimegrazer]; reg=33 status=6 [slimegrazer] |
| RUT_DeltaLoam | ThingDef | Things/Item/Resource/RUT_DeltaLoam | RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_DeltaLoam.xml | artsrc=1 done=1 [deltaloam] |
| RUT_GlowerCrust | ThingDef | Things/Item/Resource/RUT_GlowerCrust | RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_ScarlandsItems.xml | artsrc=1 done=1 [glowercrust] |
| RUT_Grellbush | ThingDef | Things/Plant/RUT_Grellbush | RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_AridShrublandVanillaReplacements.xml | artsrc=1 done=1 [rut_grellbush]; reg=19 status=2 [rut_grellbush] |
| RUT_WildHealroot | ThingDef | Things/Plant/RUT_WildHealroot | RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_AridShrublandVanillaReplacements.xml | artsrc=1 done=1 [rut_wildhealroot]; reg=19 status=2 [rut_wildhealroot] |
| RUT_Grellspine | ThingDef | Things/Plant/RUT_Grellspine | RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_AridShrublandVanillaReplacements.xml | artsrc=1 done=1 [rut_grellspine]; reg=19 status=2 [rut_grellspine] |
| RUT_GreentideAnt | PawnKindDef | Things/Pawn/Animal/RUT_GreentideAnt/RUT_GreentideAnt (+1) | RimUtinni/GreentideRaidAnt/Defs/ThingDefs_Races/RUT_PawnKinds_GreentideAnt.xml | artsrc=8 done=8 [rut_greentideant]; reg=108 status=16 [rut_greentideant] |
| RSW_Graffiti_Stencil_ImperialCog | ThingDef | Things/Filth/Art/RSW_Graffiti_Stencil_ImperialCog | RimStarWars/GraffitiImperial/Defs/ThingDefs_GraffitiImperial.xml | artsrc=1 done=1 [rsw_graffiti_stencil_imperialcog]; reg=11 status=2 [rsw_graffiti_stencil_imperialcog] |
| RSW_Plant_Nysyllin_Wild | ThingDef | swplants/Nysillin | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Plants.xml | artsrc=1 done=1 [plant_nysyllin_wild]; reg=19 status=2 [plant_nysyllin_wild]; decisions=desert_family_review_2026-09-20.decisions.json |
| RSW_Zakkro | PawnKindDef | swanimals/DesertPort/Zakkro/Zakkro (+1) | RimStarWars/SWBestiary/Defs/DesertPort/RSW_Zakkro.xml | artsrc=5 done=5 [rsw_zakkro]; reg=95 status=10 [rsw_zakkro] |
| RSW_Ossik | PawnKindDef | Things/Pawn/Animal/RSW_Ossik/RSW_Ossik | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml | artsrc=3 done=3 [ossik]; reg=21 status=0 [ossik] |
| RSW_Kudda | PawnKindDef | Things/Pawn/Animal/RSW_Kudda/RSW_Kudda | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml | artsrc=3 done=3 [kudda]; reg=21 status=0 [kudda] |
| RSW_Thurra | PawnKindDef | Things/Pawn/Animal/RSW_Thurra/RSW_Thurra | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml | artsrc=3 done=3 [thurra]; reg=21 status=0 [thurra] |
| RSW_Vosska | PawnKindDef | Things/Pawn/Animal/RSW_Vosska/RSW_Vosska | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml | artsrc=3 done=3 [vosska]; reg=21 status=0 [vosska] |
| RSW_Khorrak | PawnKindDef | Things/Pawn/Animal/RSW_Khorrak/RSW_Khorrak | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml | artsrc=3 done=3 [khorrak]; reg=21 status=0 [khorrak] |
| RSW_Ommok | PawnKindDef | Things/Pawn/Animal/RSW_Ommok/RSW_Ommok | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml | artsrc=5 done=5 [ommok]; reg=35 status=0 [ommok] |
| RSW_Ulgga | PawnKindDef | Things/Pawn/Animal/RSW_Ulgga/RSW_Ulgga | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml | artsrc=6 done=6 [ulgga]; reg=54 status=6 [ulgga] |
| RSW_Vozzik | PawnKindDef | Things/Pawn/Animal/RSW_Vozzik/RSW_Vozzik | RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml | artsrc=4 done=4 [vozzik]; reg=28 status=0 [vozzik] |
| RSW_Ultracactus | ThingDef | Things/Plant/RSW_Ultracactus | RimStarWars/SWBestiary/Defs/DesertPort/RSW_Ultracactus.xml | artsrc=3 done=3 [ultracactus]; reg=45 status=4 [ultracactus] |
| RSW_RawUltracactus | ThingDef | Things/Item/Plant/RSW_RawUltracactus | RimStarWars/SWBestiary/Defs/DesertPort/RSW_Ultracactus.xml | artsrc=1 done=1 [rawultracactus]; reg=19 status=2 [rawultracactus] |
| RSW_Convor | PawnKindDef | swanimals/Convor/Convor_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Convor.xml | artsrc=3 done=3 [convor]; reg=21 status=6 [convor]; decisions=desert_family_review_2026-09-20.decisions.json |
| RSW_Beldon | PawnKindDef | swanimals/Beldon/Beldon_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Beldon.xml | artsrc=0 done=3 [beldon]; decisions=port_swac_2026-09-20.decisions.json |
| RSW_Shyrack | PawnKindDef | swanimals/Shyrack/Shyrack_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Shyrack.xml | artsrc=3 done=3 [shyrack]; reg=21 status=6 [shyrack]; decisions=desert_family_review_2026-09-20.decisions.json |
| RSW_CanCell | PawnKindDef | swanimals/CanCell/CanCell_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_CanCell.xml | artsrc=0 done=3 [cancell]; decisions=port_swac_2026-09-20.decisions.json |
| RSW_ScrapNestBird | PawnKindDef | swanimals/Whisperbird/Whisperbird_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_ScrapNestBird.xml | artsrc=3 done=3 [rsw_scrapnestbird]; reg=21 status=0 [rsw_scrapnestbird] |
| RSW_PekoPeko | PawnKindDef | swanimals/PekoPeko/PekoPeko_m_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_PekoPeko.xml | artsrc=1 done=3 [pekopeko]; reg=28 status=8 [pekopeko]; decisions=port_swac_2026-09-20.decisions.json,bulk_art_misroute_2026-09-19.decisions.json |
| RSW_Dactillion | PawnKindDef | swanimals/Dactillion/Dactillion_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Dactillion.xml | artsrc=1 done=3 [dactillion]; reg=28 status=8 [dactillion]; decisions=port_swac_2026-09-20.decisions.json |
| RSW_Hawkbat | PawnKindDef | swanimals/Hawkbat/Hawkbat_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Hawkbat.xml | artsrc=3 done=6 [hawkbat]; reg=21 status=6 [hawkbat]; decisions=port_swac_2026-09-20.decisions.json,bulk_art_misroute_2026-09-19.decisions.json |
| RSW_Strill | PawnKindDef | swanimals/Strill/Strill_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Strill.xml | artsrc=3 done=3 [strill]; reg=57 status=6 [strill]; decisions=desert_family_review_2026-09-20.decisions.json |
| RSW_Sketto | PawnKindDef | swanimals/Sketto/Sketto_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Sketto.xml | artsrc=3 done=3 [sketto]; reg=21 status=6 [sketto]; decisions=desert_family_review_2026-09-20.decisions.json |
| RSW_Urusai | PawnKindDef | swanimals/Urusai/Urusai_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Urusai.xml | artsrc=3 done=3 [urusai]; reg=25 status=6 [urusai]; decisions=desert_family_review_2026-09-20.decisions.json |
| RSW_Whisperbird | PawnKindDef | swanimals/Whisperbird/Whisperbird_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Whisperbird.xml | artsrc=6 done=9 [whisperbird]; reg=78 status=12 [whisperbird]; decisions=desert_family_review_2026-09-20.decisions.json,bulk_art_misroute_2026-09-19.decisions.json |
| RSW_ZakkroEgg | ThingDef | swresource/RSW_ZakkroEgg | RimStarWars/SWBestiary/Defs/ThingDefs_Items/RSW_ZakkroEgg.xml | artsrc=1 done=1 [rsw_zakkroegg]; reg=19 status=2 [rsw_zakkroegg] |
| RM_Glower | ThingDef | Things/Plant/RM_Glower | RimMandrake/Scarlands/Defs/ThingDefs_Plants/RM_WarscarFlora.xml | artsrc=2 done=2 [rm_glower]; reg=14 status=0 [rm_glower] |
| RM_GlowerCrust | ThingDef | Things/Item/Resource/RM_GlowerCrust | RimMandrake/Scarlands/Defs/ThingDefs_Items/RM_WarscarItems.xml | artsrc=1 done=1 [glowercrust] |
| RM_Parasol | ThingDef | Things/Item/Equipment/RM_ShadeGear/RM_Parasol | RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Buildings/RM_ShadeGear.xml | artsrc=1 done=1 [rm_parasol]; reg=28 status=0 [rm_parasol] |
| RM_ShadeTent | ThingDef | Things/Building/RM_ShadeGear/RM_ShadeTent | RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Buildings/RM_ShadeGear.xml | artsrc=1 done=1 [rm_shadetent]; reg=7 status=0 [rm_shadetent] |
| RM_Palefloss | ThingDef | Things/Plant/RM_Palefloss/RM_Palefloss | RimMandrake/BlueDesert/Defs/ThingDefs_Plants/RM_BlueDesertFlora.xml | artsrc=3 done=3 [palefloss] |
| RM_Glassfern | ThingDef | Things/Plant/RM_Glassfern/RM_Glassfern | RimMandrake/BlueDesert/Defs/ThingDefs_Plants/RM_BlueDesertFlora.xml | artsrc=3 done=3 [glassfern] |
| RM_Chimeglobe | ThingDef | Things/Plant/RM_Chimeglobe/RM_Chimeglobe | RimMandrake/BlueDesert/Defs/ThingDefs_Plants/RM_BlueDesertFlora.xml | artsrc=2 done=2 [chimeglobe] |
| RM_BlueIceMeltwaterCan | ThingDef | Things/Item/Resource/RM_BlueIceMeltwaterCan/RM_BlueIceMeltwaterCan | RimMandrake/BlueDesert/Defs/ThingDefs_Items/RM_BlueIceMeltwaterCan.xml | artsrc=1 done=1 [rm_blueicemeltwatercan]; reg=7 status=0 [rm_blueicemeltwatercan] |
| RM_ColdSinkRack | ThingDef | Things/Building/RM_ColdSinkRack/RM_ColdSinkRack | RimMandrake/BlueDesert/Defs/ThingDefs_Buildings/RM_ColdSinkRack.xml | artsrc=1 done=1 [rm_coldsinkrack]; reg=7 status=0 [rm_coldsinkrack] |
| RM_Thessamor | ThingDef | Things/Plant/RM_Thessamor/RM_Thessamor_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_Mangals.xml | artsrc=1 done=1 [thessamor]; reg=7 status=2 [thessamor] |
| RM_Brelloch | ThingDef | Things/Plant/RM_Brelloch/RM_Brelloch_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_Mangals.xml | artsrc=1 done=1 [brelloch]; reg=7 status=2 [brelloch] |
| RM_Quennath | ThingDef | Things/Plant/RM_Quennath/RM_Quennath_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_Mangals.xml | artsrc=1 done=1 [quennath]; reg=7 status=2 [quennath] |
| RM_Ilbareen | ThingDef | Things/Plant/RM_Ilbareen/RM_Ilbareen_live | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_Mangals.xml | artsrc=2 done=2 [ilbareen]; reg=14 status=4 [ilbareen] |
| RM_Ollamane | ThingDef | Things/Plant/RM_Ollamane/RM_Ollamane_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_RainbowBlooms.xml | artsrc=1 done=1 [ollamane]; reg=7 status=2 [ollamane] |
| RM_Vellamine | ThingDef | Things/Plant/RM_Vellamine/RM_Vellamine_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_RainbowBlooms.xml | artsrc=1 done=1 [vellamine]; reg=7 status=2 [vellamine] |
| RM_Ismerrow | ThingDef | Things/Plant/RM_Ismerrow/RM_Ismerrow | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_RainbowBlooms.xml | artsrc=4 done=4 [ismerrow]; reg=28 status=8 [ismerrow] |
| RM_Aphreen | ThingDef | Things/Plant/RM_Aphreen/RM_Aphreen_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_RainbowBlooms.xml | artsrc=1 done=1 [aphreen]; reg=7 status=2 [aphreen] |
| RM_Nyssolet | ThingDef | Things/Plant/RM_Nyssolet/RM_Nyssolet_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_RainbowBlooms.xml | artsrc=1 done=1 [nyssolet]; reg=7 status=2 [nyssolet] |
| RM_Sarrash | ThingDef | Things/Plant/RM_Sarrash/RM_Sarrash_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_RainbowBlooms.xml | artsrc=1 done=1 [sarrash]; reg=7 status=2 [sarrash] |
| RM_Ullavess | ThingDef | Things/Plant/RM_Ullavess/RM_Ullavess_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_Predators.xml | artsrc=1 done=1 [ullavess]; reg=7 status=2 [ullavess] |
| RM_Nemreth | ThingDef | Things/Plant/RM_Nemreth/RM_Nemreth_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_Predators.xml | artsrc=1 done=1 [nemreth]; reg=7 status=2 [nemreth] |
| RM_Velluric | ThingDef | Things/Plant/RM_Velluric/RM_Velluric_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_Predators.xml | artsrc=1 done=1 [velluric]; reg=7 status=2 [velluric] |
| RM_Braskeen | ThingDef | Things/Plant/RM_Braskeen/RM_Braskeen | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_Predators.xml | artsrc=2 done=2 [braskeen]; reg=18 status=4 [braskeen] |
| RM_Ommolyn | ThingDef | Things/Plant/RM_Ommolyn/RM_Ommolyn_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_Predators.xml | artsrc=1 done=1 [ommolyn]; reg=7 status=2 [ommolyn] |
| RM_Immarel | ThingDef | Things/Plant/RM_Immarel/RM_Immarel_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_MuckAndSilt.xml | artsrc=1 done=1 [immarel]; reg=7 status=2 [immarel] |
| RM_Thrannock | ThingDef | Things/Plant/RM_Thrannock/RM_Thrannock_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_MuckAndSilt.xml | artsrc=1 done=1 [thrannock]; reg=7 status=2 [thrannock] |
| RM_Pallasheen | ThingDef | Things/Plant/RM_Pallasheen/RM_Pallasheen_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_MuckAndSilt.xml | artsrc=1 done=1 [pallasheen]; reg=7 status=2 [pallasheen] |
| RM_Wessaline | ThingDef | Things/Plant/RM_Wessaline/RM_Wessaline_a | RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_MuckAndSilt.xml | artsrc=1 done=1 [wessaline]; reg=7 status=2 [wessaline] |
| RM_Dorvel | ThingDef | Things/Plant/RM_Dorvel/RM_Dorvel_a | RimMandrake/TheSump/Defs/ThingDefs_Plants/RM_SumpFlora.xml | artsrc=1 done=1 [rm_dorvel]; reg=7 status=2 [rm_dorvel] |
| RM_Skelver | ThingDef | Things/Plant/RM_Skelver/RM_Skelver_a | RimMandrake/TheSump/Defs/ThingDefs_Plants/RM_SumpFlora.xml | artsrc=1 done=1 [rm_skelver]; reg=7 status=2 [rm_skelver] |
| RM_Korveth | ThingDef | Things/Plant/RM_Korveth/RM_Korveth_a | RimMandrake/TheSump/Defs/ThingDefs_Plants/RM_SumpFlora.xml | artsrc=1 done=1 [rm_korveth]; reg=7 status=2 [rm_korveth] |
| RM_Brindeth | ThingDef | Things/Plant/RM_Brindeth/RM_Brindeth_a | RimMandrake/TheSump/Defs/ThingDefs_Plants/RM_SumpFlora.xml | artsrc=1 done=1 [rm_brindeth]; reg=7 status=2 [rm_brindeth] |
| RM_Soffeth | ThingDef | Things/Plant/RM_Soffeth/RM_Soffeth_a | RimMandrake/TheSump/Defs/ThingDefs_Plants/RM_SumpFlora.xml | artsrc=1 done=1 [rm_soffeth]; reg=7 status=2 [rm_soffeth] |
| RM_Tolleth | ThingDef | Things/Plant/RM_Tolleth/RM_Tolleth_a | RimMandrake/TheSump/Defs/ThingDefs_Plants/RM_SumpFlora.xml | artsrc=1 done=1 [rm_tolleth]; reg=7 status=2 [rm_tolleth] |
| RM_Velloch | ThingDef | Things/Plant/RM_Velloch/RM_Velloch_a | RimMandrake/TheSump/Defs/ThingDefs_Plants/RM_SumpFlora.xml | artsrc=1 done=1 [rm_velloch]; reg=7 status=2 [rm_velloch] |
| RM_Mirrelin | ThingDef | Things/Plant/RM_Mirrelin/RM_Mirrelin_a | RimMandrake/TheSump/Defs/ThingDefs_Plants/RM_SumpFlora.xml | artsrc=1 done=1 [rm_mirrelin]; reg=7 status=2 [rm_mirrelin] |
| RM_Pallick | ThingDef | Things/Plant/RM_Pallick/RM_Pallick_a | RimMandrake/TheSump/Defs/ThingDefs_Plants/RM_SumpFlora.xml | artsrc=1 done=1 [rm_pallick]; reg=7 status=2 [rm_pallick] |
| RM_SumpMouse | PawnKindDef | Things/Pawn/Animal/RM_SumpMouse/RM_SumpMouse | RimMandrake/TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml | artsrc=3 done=3 [rm_sumpmouse]; reg=45 status=6 [rm_sumpmouse] |
| RM_Gulveth | PawnKindDef | Things/Pawn/Animal/RM_Gulveth/RM_Gulveth | RimMandrake/TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml | artsrc=3 done=3 [rm_gulveth]; reg=41 status=6 [rm_gulveth] |
| RM_Thrummel | PawnKindDef | Things/Pawn/Animal/RM_Thrummel/RM_Thrummel | RimMandrake/TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml | artsrc=9 done=9 [rm_thrummel]; reg=135 status=18 [rm_thrummel] |
| RM_ThrummelWarden | PawnKindDef | Things/Pawn/Animal/RM_ThrummelWarden/RM_ThrummelWarden | RimMandrake/TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml | artsrc=3 done=3 [rm_thrummelwarden]; reg=45 status=6 [rm_thrummelwarden] |
| RM_ThrummelBroodmother | PawnKindDef | Things/Pawn/Animal/RM_ThrummelBroodmother/RM_ThrummelBroodmother | RimMandrake/TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml | artsrc=3 done=3 [rm_thrummelbroodmother]; reg=45 status=6 [rm_thrummelbroodmother] |
| RM_Brommet | PawnKindDef | Things/Pawn/Animal/RM_Brommet/RM_Brommet | RimMandrake/TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml | artsrc=3 done=3 [rm_brommet]; reg=33 status=6 [rm_brommet] |
| RM_Dredgel | PawnKindDef | Things/Pawn/Animal/RM_Dredgel/RM_Dredgel | RimMandrake/TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml | artsrc=1 done=1 [rm_dredgel]; reg=37 status=6 [rm_dredgel] |
| RM_Skarrid | PawnKindDef | Things/Pawn/Animal/RM_Skarrid/RM_Skarrid | RimMandrake/TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml | artsrc=3 done=3 [rm_skarrid]; reg=45 status=6 [rm_skarrid] |
| RM_Skellarn | PawnKindDef | Things/Pawn/Animal/RM_Skellarn/RM_Skellarn | RimMandrake/TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml | artsrc=3 done=3 [rm_skellarn]; reg=45 status=6 [rm_skellarn] |
| RM_Titanoslime | PawnKindDef | Things/Pawn/Animal/Titanoslime/RM_Titanoslime | RimMandrake/GelatinousSlime/Defs/ThingDefs_Races/Titanoslime.xml | artsrc=3 done=3 [titanoslime]; reg=60 status=9 [titanoslime] |
| RM_DewfringeSprig | ThingDef | Things/Item/Plant/RM_DewfringeSprig | RimMandrake/LongShade/Defs/ThingDefs_Plants/RM_Dewfringe.xml | artsrc=1 done=1 [rm_dewfringesprig]; reg=7 status=0 [rm_dewfringesprig] |
| RM_GreatDevourer | PawnKindDef | Things/Pawn/Animal/RM_GreatDevourer/RM_GreatDevourer (+3) | RimMandrake/LongShade/Defs/ThingDefs_Races/RM_LongShade_Fauna.xml | artsrc=3 done=3 [rm_greatdevourer]; reg=21 status=0 [rm_greatdevourer] |
| RM_Groundrunner | PawnKindDef | Things/Pawn/Animal/RM_Groundrunner/RM_Groundrunner4 (+6) | RimMandrake/LongShade/Defs/ThingDefs_Races/RM_LongShade_Fauna.xml | artsrc=3 done=3 [rm_groundrunner]; reg=21 status=0 [rm_groundrunner] |
| RM_MatureFleshbeast | PawnKindDef | Things/Pawn/Animal/RM_MatureFleshbeast/RM_MatureFleshbeast (+1) | RimMandrake/LongShade/Defs/ThingDefs_Races/RM_LongShade_Fauna.xml | artsrc=3 done=3 [rm_maturefleshbeast]; reg=21 status=0 [rm_maturefleshbeast] |
| RM_Dewblade | ThingDef | Things/Plant/RM_Dewblade | RimMandrake/WeepingStones/Defs/ThingDefs_Plants/RM_WeepingStonesNativeFlora.xml | artsrc=1 done=1 [dewblade]; reg=7 status=2 [dewblade] |
| RM_Weepmat | ThingDef | Things/Plant/RM_Weepmat | RimMandrake/WeepingStones/Defs/ThingDefs_Plants/RM_WeepingStonesNativeFlora.xml | artsrc=1 done=1 [weepmat]; reg=7 status=2 [weepmat] |
| RM_Verdimoss | ThingDef | Things/Plant/RM_Verdimoss | RimMandrake/WeepingStones/Defs/ThingDefs_Plants/RM_WeepingStonesNativeFlora.xml | artsrc=1 done=1 [verdimoss]; reg=7 status=2 [verdimoss] |
| RM_Shadefern | ThingDef | Things/Plant/RM_Shadefern | RimMandrake/WeepingStones/Defs/ThingDefs_Plants/RM_WeepingStonesNativeFlora.xml | artsrc=1 done=1 [shadefern]; reg=7 status=2 [shadefern] |
| RM_Bladderquill | ThingDef | Things/Plant/RM_Bladderquill | RimMandrake/WeepingStones/Defs/ThingDefs_Plants/RM_WeepingStonesNativeFlora.xml | artsrc=1 done=1 [bladderquill]; reg=7 status=2 [bladderquill] |
| RM_Salvecomb | ThingDef | Things/Plant/RM_Salvecomb | RimMandrake/WeepingStones/Defs/ThingDefs_Plants/RM_WeepingStonesNativeFlora.xml | artsrc=1 done=1 [salvecomb]; reg=7 status=2 [salvecomb] |
| RM_Rockfinger | ThingDef | Things/Plant/RM_Rockfinger | RimMandrake/WeepingStones/Defs/ThingDefs_Plants/RM_WeepingStonesNativeFlora.xml | artsrc=1 done=1 [rockfinger]; reg=7 status=2 [rockfinger] |
| RM_Dripfringe | ThingDef | Things/Plant/RM_Dripfringe | RimMandrake/WeepingStones/Defs/ThingDefs_Plants/RM_WeepingStonesNativeFlora.xml | artsrc=1 done=1 [dripfringe]; reg=7 status=2 [dripfringe] |
| RM_Steamfrond | ThingDef | Things/Plant/RM_Steamfrond | RimMandrake/WeepingStones/Defs/ThingDefs_Plants/RM_WeepingStonesNativeFlora.xml | artsrc=1 done=1 [steamfrond]; reg=7 status=2 [steamfrond] |
| RM_Dewgourd | ThingDef | Things/Plant/RM_Dewgourd | RimMandrake/WeepingStones/Defs/ThingDefs_Plants/RM_WeepingStonesNativeFlora.xml | artsrc=2 done=2 [dewgourd]; reg=14 status=4 [dewgourd] |
| RM_BladderFruit | ThingDef | Things/Item/Plant/RM_BladderFruit | RimMandrake/WeepingStones/Defs/ThingDefs_Items/RM_WeepingStonesNativeFlora_Items.xml | artsrc=1 done=1 [bladderfruit]; reg=7 status=2 [bladderfruit] |
| RM_SeepSalt | ThingDef | Things/Item/Resource/RM_SeepSalt | RimMandrake/WeepingStones/Defs/ThingDefs_Items/RM_WeepingStonesNativeFlora_Items.xml | artsrc=1 done=1 [seepsalt]; reg=7 status=2 [seepsalt] |
| RM_DewgourdFruit | ThingDef | Things/Item/Plant/RM_DewgourdFruit | RimMandrake/WeepingStones/Defs/ThingDefs_Items/RM_WeepingStonesNativeFlora_Items.xml | artsrc=1 done=1 [dewgourdfruit]; reg=7 status=2 [dewgourdfruit] |
| RUT_AncientAirlock | ThingDef | Things/Building/Ancient/RUT_AncientAirlock_Top (+2) | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientAirlocks.xml | artsrc=2 done=2 [rut_ancientairlock]; reg=14 status=0 [rut_ancientairlock] |
| RUT_AncientAirlock_Large | ThingDef | Things/Building/Ancient/RUT_AncientAirlock_Large_Top (+2) | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientAirlocks.xml | artsrc=1 done=1 [rut_ancientairlock_large]; reg=7 status=0 [rut_ancientairlock_large] |
| RUT_JammedAncientAirlock | ThingDef | Things/Building/Ancient/RUT_JammedAncientAirlock | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientAirlocks.xml | artsrc=2 done=2 [rut_jammedancientairlock]; reg=14 status=0 [rut_jammedancientairlock] |
| RUT_JammedAncientAirlock_Large | ThingDef | Things/Building/Ancient/RUT_JammedAncientAirlock_Large | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientAirlocks.xml | artsrc=1 done=1 [rut_jammedancientairlock_large]; reg=7 status=0 [rut_jammedancientairlock_large] |
| RUT_ForcedAncientAirlock | ThingDef | Things/Building/Ancient/RUT_ForcedAncientAirlock | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientAirlocks.xml | artsrc=2 done=2 [rut_forcedancientairlock]; reg=14 status=0 [rut_forcedancientairlock] |
| RUT_ForcedAncientAirlock_Large | ThingDef | Things/Building/Ancient/RUT_ForcedAncientAirlock_Large | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientAirlocks.xml | artsrc=1 done=1 [rut_forcedancientairlock_large]; reg=7 status=0 [rut_forcedancientairlock_large] |
| RUT_FrozenEmptyCryptosleepPod | ThingDef | Things/Building/Ancient/RUT_FrozenEmptyCryptosleepPod | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientAirlocks.xml | artsrc=1 done=1 [rut_frozenemptycryptosleeppod]; reg=7 status=0 [rut_frozenemptycryptosleeppod] |
| RUT_BustedShieldedTurret | ThingDef | Things/Building/Ancient/RUT_BustedShieldedTurret | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientDecorativeAndRecreation.xml | artsrc=1 done=1 [rut_bustedshieldedturret]; reg=7 status=0 [rut_bustedshieldedturret] |
| RUT_BustedSpacerAutocannon | ThingDef | Things/Building/Ancient/RUT_BustedSpacerAutocannon | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientDecorativeAndRecreation.xml | artsrc=1 done=1 [rut_bustedspacerautocannon]; reg=7 status=0 [rut_bustedspacerautocannon] |
| RUT_AncientShipLandingBeacon | ThingDef | Things/Building/Ancient/RUT_AncientShipLandingBeacon | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientDecorativeAndRecreation.xml | artsrc=1 done=1 [rut_ancientshiplandingbeacon]; reg=7 status=0 [rut_ancientshiplandingbeacon] |
| RUT_AncientTransmitterBeacon | ThingDef | Things/Building/Ancient/RUT_AncientTransmitterBeacon | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientDecorativeAndRecreation.xml | artsrc=1 done=1 [rut_ancienttransmitterbeacon]; reg=7 status=0 [rut_ancienttransmitterbeacon] |
| RUT_AncientShieldedTurret | ThingDef | Things/Building/Ancient/RUT_AncientShieldedTurret | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientSecurityAndUtility.xml | artsrc=1 done=1 [rut_ancientshieldedturret]; reg=7 status=0 [rut_ancientshieldedturret] |
| RUT_AncientSpacerAutocannon | ThingDef | Things/Building/Ancient/RUT_AncientSpacerAutocannon | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientSecurityAndUtility.xml | artsrc=1 done=1 [rut_ancientspacerautocannon]; reg=7 status=0 [rut_ancientspacerautocannon] |
| RUT_AncientFloorHeater | ThingDef | Things/Building/Ancient/RUT_AncientFloorHeater | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientSecurityAndUtility.xml | artsrc=1 done=1 [rut_ancientfloorheater]; reg=7 status=0 [rut_ancientfloorheater] |
| RM_Muurrok | PawnKindDef | Things/Pawn/Animal/RM_Muurrok/RM_Muurrok | RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Muurrok.xml | artsrc=4 done=4 [rm_muurrok]; reg=28 status=0 [rm_muurrok] |
| RM_GlassSand | ThingDef | Things/Item/Resource/RM_GlassSand | RimMandrake/Stillsand/Defs/ThingDefs_Items/RM_GlassChain_Items.xml | artsrc=1 done=1 [rm_glasssand]; reg=7 status=0 [rm_glasssand] |
| RM_SunGlass | ThingDef | Things/Item/Resource/RM_SunGlass | RimMandrake/Stillsand/Defs/ThingDefs_Items/RM_GlassChain_Items.xml | artsrc=1 done=1 [rm_sunglass]; reg=7 status=0 [rm_sunglass] |
| RM_PrecisionLens | ThingDef | Things/Item/Resource/RM_PrecisionLens | RimMandrake/Stillsand/Defs/ThingDefs_Items/RM_GlassChain_Items.xml | artsrc=1 done=1 [rm_precisionlens]; reg=7 status=0 [rm_precisionlens] |
| RM_PearlLens | ThingDef | Things/Item/Resource/RM_PearlLens | RimMandrake/Stillsand/Defs/ThingDefs_Items/RM_GlassChain_Items.xml | artsrc=1 done=1 [rm_pearllens]; reg=7 status=0 [rm_pearllens] |
| RM_CrestPlate | ThingDef | Things/Item/Resource/RM_CrestPlate | RimMandrake/Stillsand/Defs/ThingDefs_Items/RM_CrestPlate.xml | artsrc=1 done=1 [rm_crestplate]; reg=7 status=0 [rm_crestplate] |
| RM_SunFurnace | ThingDef | Things/Building/Production/RM_SunFurnace | RimMandrake/Stillsand/Defs/ThingDefs_Buildings/RM_GlassChain_Buildings.xml | artsrc=1 done=1 [rm_sunfurnace]; reg=7 status=0 [rm_sunfurnace] |
| RM_CrystalFlower | ThingDef | Things/Plant/RM_CrystalFlower/RM_CrystalFlower_a | RimMandrake/Cauldron/Defs/ThingDefs_Plants/RM_CauldronFlora.xml | artsrc=0 done=1 [crystalflower]; reg=7 status=2 [crystalflower]; decisions=lantern_deeps_strange_life_2026-09-20.decisions.json,port_tail_2026-09-20.decisions.json |
| RM_BloodBouquet | ThingDef | Things/Plant/RM_BloodBouquet/RM_BloodBouquet_a | RimMandrake/Cauldron/Defs/ThingDefs_Plants/RM_CauldronFlora.xml | artsrc=0 done=1 [bloodbouquet]; reg=7 status=2 [bloodbouquet]; decisions=port_tail_2026-09-20.decisions.json,bulk_art_misroute_2026-09-19.decisions.json |
| RM_RavenNettle | ThingDef | Things/Plant/RM_RavenNettle/RM_RavenNettle_a | RimMandrake/Cauldron/Defs/ThingDefs_Plants/RM_CauldronFlora.xml | artsrc=0 done=1 [ravennettle]; reg=7 status=2 [ravennettle]; decisions=port_tail_2026-09-20.decisions.json |
| RM_RedBugloss | ThingDef | Things/Plant/RM_RedBugloss/RM_RedBugloss_a | RimMandrake/Cauldron/Defs/ThingDefs_Plants/RM_CauldronFlora.xml | artsrc=0 done=1 [redbugloss]; reg=7 status=2 [redbugloss]; decisions=port_tail_2026-09-20.decisions.json |
| RM_GiantAgariTox | ThingDef | Things/Plant/RM_GiantAgariTox/RM_GiantAgariTox_a | RimMandrake/Cauldron/Defs/ThingDefs_Plants/RM_CauldronFlora.xml | artsrc=0 done=1 [giantagaritox]; reg=7 status=2 [giantagaritox]; decisions=port_tail_2026-09-20.decisions.json,bulk_art_misroute_2026-09-19.decisions.json |
| RM_KeeningCordax | ThingDef | Things/Plant/RM_KeeningCordax/RM_KeeningCordax_a | RimMandrake/Cauldron/Defs/ThingDefs_Plants/RM_CauldronFlora.xml | artsrc=0 done=1 [keeningcordax]; reg=7 status=2 [keeningcordax]; decisions=port_tail_2026-09-20.decisions.json,bulk_art_misroute_2026-09-19.decisions.json |
| RM_GiantToxicFlower | ThingDef | Things/Plant/RM_GiantToxicFlower/RM_GiantToxicFlower_a | RimMandrake/Cauldron/Defs/ThingDefs_Plants/RM_CauldronFlora.xml | artsrc=0 done=1 [gianttoxicflower]; reg=7 status=2 [gianttoxicflower] |
| RM_Mourvel | ThingDef | Things/Plant/RM_Mourvel/RM_Mourvel_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml | artsrc=1 done=1 [rm_mourvel]; reg=19 status=2 [rm_mourvel] |
| RM_Kaddrath | ThingDef | Things/Plant/RM_Kaddrath/RM_Kaddrath_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml | artsrc=1 done=1 [rm_kaddrath]; reg=19 status=2 [rm_kaddrath] |
| RM_Sarnstilt | ThingDef | Things/Plant/RM_Sarnstilt/RM_Sarnstilt_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml | artsrc=1 done=1 [rm_sarnstilt]; reg=19 status=2 [rm_sarnstilt] |
| RM_Brunnock | ThingDef | Things/Plant/RM_Brunnock/RM_Brunnock_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml | artsrc=1 done=1 [rm_brunnock]; reg=19 status=2 [rm_brunnock] |
| RM_Vurmeloth | ThingDef | Things/Plant/RM_Vurmeloth/RM_Vurmeloth_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml | artsrc=1 done=1 [rm_vurmeloth]; reg=19 status=2 [rm_vurmeloth] |
| RM_Mirrelbole | ThingDef | Things/Plant/RM_Mirrelbole/RM_Mirrelbole_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml | artsrc=1 done=1 [rm_mirrelbole]; reg=19 status=2 [rm_mirrelbole] |
| RM_Zhorrel | ThingDef | Things/Plant/RM_Zhorrel/RM_Zhorrel_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml | artsrc=1 done=1 [rm_zhorrel]; reg=19 status=2 [rm_zhorrel] |
| RM_Quathis | ThingDef | Things/Plant/RM_Quathis/RM_Quathis_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml | artsrc=1 done=1 [rm_quathis]; reg=19 status=2 [rm_quathis] |
| RM_Thalquith | ThingDef | Things/Plant/RM_Thalquith/RM_Thalquith_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml | artsrc=1 done=1 [rm_thalquith]; reg=19 status=2 [rm_thalquith] |
| RM_Cundral | ThingDef | Things/Plant/RM_Cundral/RM_Cundral_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml | artsrc=1 done=1 [rm_cundral]; reg=19 status=2 [rm_cundral] |
| RM_Gorbeleth | ThingDef | Things/Plant/RM_Gorbeleth/RM_Gorbeleth_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml | artsrc=1 done=1 [rm_gorbeleth]; reg=19 status=2 [rm_gorbeleth] |
| RM_Tumbel | ThingDef | Things/Plant/RM_Tumbel/RM_Tumbel_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_UnderstoryRoster.xml | artsrc=1 done=1 [rm_tumbel]; reg=19 status=2 [rm_tumbel] |
| RM_Sarquin | ThingDef | Things/Plant/RM_Sarquin/RM_Sarquin_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_UnderstoryRoster.xml | artsrc=1 done=1 [rm_sarquin]; reg=19 status=2 [rm_sarquin] |
| RM_Phorrik | ThingDef | Things/Plant/RM_Phorrik/RM_Phorrik_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_UnderstoryRoster.xml | artsrc=1 done=1 [rm_phorrik]; reg=19 status=2 [rm_phorrik] |
| RM_Wollick | ThingDef | Things/Plant/RM_Wollick/RM_Wollick_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_UnderstoryRoster.xml | artsrc=1 done=1 [rm_wollick]; reg=19 status=2 [rm_wollick] |
| RM_Greatbole | ThingDef | Things/Plant/RM_Greatbole/RM_Greatbole_a | RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greatbole.xml | artsrc=1 done=1 [rm_greatbole]; reg=7 status=2 [rm_greatbole] |
| RM_Krannock | PawnKindDef | Things/Pawn/Animal/RM_Krannock/RM_Krannock | RimMandrake/Greentide/Defs/ThingDefs_Races/RM_Krannock.xml | artsrc=3 done=3 [rm_krannock]; reg=21 status=0 [rm_krannock] |

## UNCERTAIN

| def | kind | first missing texPath (+n more) | file | evidence |
|---|---|---|---|---|
| RSW_Neebray | PawnKindDef | swanimals/Neebray/Neebray_Flying_ | RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Neebray.xml | decisions=port_swac_2026-09-20.decisions.json |
| RSW_BloodletterPetrel | PawnKindDef | swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/BloodletterPetrel/BloodletterPetrel_Flying_ | RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml | decisions=bulk_art_misroute_2026-09-19.decisions.json |
| RSW_Screecher | PawnKindDef | swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/Screecher/Screecher_Flying_ | RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml | decisions=bulk_art_misroute_2026-09-19.decisions.json |
| RM_SunShield | ThingDef | Things/Building/RM_ShadeGear/RM_SunShield | RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Buildings/RM_ShadeGear.xml | reg=21 status=0 [rm_sunshield]; reg=21 status=0 [sunshield] |
| RUT_CryptoAncientTerminal | ThingDef | Things/Building/Ancient/RUT_CryptoAncientTerminal | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientDecorativeAndRecreation.xml | reg=42 status=0 [rut_cryptoancientterminal]; reg=42 status=0 [cryptoancientterminal] |
| RUT_CryptoAncientTerminalBank | ThingDef | Things/Building/Ancient/RUT_CryptoAncientTerminalBank | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientDecorativeAndRecreation.xml | reg=21 status=0 [rut_cryptoancientterminalbank]; reg=21 status=0 [cryptoancientterminalbank] |
| RUT_RuinedHospitalBed | ThingDef | Things/Building/Ancient/RUT_RuinedHospitalBed | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientDecorativeAndRecreation.xml | reg=21 status=0 [rut_ruinedhospitalbed]; reg=21 status=0 [ruinedhospitalbed] |
| RUT_AncientWargamingTable | ThingDef | Things/Building/Ancient/RUT_AncientWargamingTable | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientDecorativeAndRecreation.xml | reg=21 status=0 [rut_ancientwargamingtable]; reg=21 status=0 [ancientwargamingtable] |
| RUT_AncientBlackBox | ThingDef | Things/Building/Ancient/RUT_AncientBlackBox | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientSecurityAndUtility.xml | reg=42 status=0 [rut_ancientblackbox]; reg=42 status=0 [ancientblackbox] |
| RUT_AncientBlackBox_Off | ThingDef | Things/Building/Ancient/RUT_AncientBlackBox_Off | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientSecurityAndUtility.xml | reg=21 status=0 [rut_ancientblackbox_off]; reg=21 status=0 [ancientblackbox_off] |
| RUT_BlueprintsBench | ThingDef | Things/Building/Ancient/RUT_BlueprintsBench | RimMandrake/AssailantSalvage/Defs/ThingDefs/RUT_AncientSecurityAndUtility.xml | reg=21 status=0 [rut_blueprintsbench]; reg=21 status=0 [blueprintsbench] |
| RM_LensBench | ThingDef | Things/Building/Production/RM_LensBench | RimMandrake/Stillsand/Defs/ThingDefs_Buildings/RM_GlassChain_Buildings.xml | reg=21 status=0 [rm_lensbench]; reg=21 status=0 [lensbench] |

Note: NEEDS_REGEN rows ending in _Flying_ are optional flip-book frames (never block flight) and donor-root (swanimals/swresource) rows may just be absent donor mods; treat as lower priority.
