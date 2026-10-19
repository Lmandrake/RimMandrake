# dregen_ eligibility, 2026-10-19 (src/RimMandrake/Utils/art/regen_eligibility.py)

Owner, 2026-10-19: "I ONLY want art queued that has either confirmed NONE, PLACEHOLDER, or DONOR art. If you can't confirm one of those three, do not queue. If it was previously regenerated and renamed, do not queue."

Measured against today's src/, the art ledger, and the game-texture index. A row is eligible only if every facing it writes is confirmed. Nothing was filed or requeued.

## donor_regen_jobs_2026-10-18.json: 627 rows

| class | rows |
|---|---:|
| NONE | 0 |
| PLACEHOLDER | 3 |
| DONOR | 272 |
| REFUSED_KEPT | 43 |
| REFUSED_REGEN | 303 |
| REFUSED_UNCONFIRMED | 6 |

By reason:

- 116 × DONOR: donor bytes per ledger
- 156 × DONOR: vanilla/donor serves the path (census)
- 3 × PLACEHOLDER: geometric placeholder
- 43 × REFUSED_KEPT: owner keep on the bytes
- 47 × REFUSED_REGEN: a finished render is already bound to this def+path
- 4 × REFUSED_REGEN: a render was registered at this path before
- 29 × REFUSED_REGEN: renamed: the def now draws a render of ours elsewhere
- 223 × REFUSED_REGEN: render of ours at the destination (hash)
- 6 × REFUSED_UNCONFIRMED: bytes of unknown provenance

## swbestiary_regen_jobs_2026-10-18.json: 208 rows

| class | rows |
|---|---:|
| NONE | 0 |
| PLACEHOLDER | 0 |
| DONOR | 101 |
| REFUSED_KEPT | 0 |
| REFUSED_REGEN | 107 |
| REFUSED_UNCONFIRMED | 0 |

By reason:

- 100 × DONOR: donor bytes per ledger
- 1 × DONOR: vanilla/donor serves the path (census)
- 18 × REFUSED_REGEN: a finished render is already bound to this def+path
- 2 × REFUSED_REGEN: renamed: the def now draws a render of ours elsewhere
- 87 × REFUSED_REGEN: render of ours at the destination (hash)

## All job lists together

| class | rows |
|---|---:|
| NONE | 0 |
| PLACEHOLDER | 3 |
| DONOR | 373 |
| REFUSED_KEPT | 43 |
| REFUSED_REGEN | 410 |
| REFUSED_UNCONFIRMED | 6 |

## The failed dregen_ jobs: 280 job files in failed/ (causes: 429 270, derived 10)

| class | jobs |
|---|---:|
| NONE | 0 |
| PLACEHOLDER | 3 |
| DONOR | 241 |
| REFUSED_KEPT | 1 |
| REFUSED_REGEN | 29 |
| REFUSED_UNCONFIRMED | 6 |

By reason:

- 82 × DONOR: donor bytes per ledger
- 159 × DONOR: vanilla/donor serves the path (census)
- 3 × PLACEHOLDER: geometric placeholder
- 1 × REFUSED_KEPT: owner keep on the bytes
- 3 × REFUSED_REGEN: a finished render is already bound to this def+path
- 2 × REFUSED_REGEN: a render was registered at this path before
- 2 × REFUSED_REGEN: renamed: the def now draws a render of ours elsewhere
- 22 × REFUSED_REGEN: render of ours at the destination (hash)
- 6 × REFUSED_UNCONFIRMED: bytes of unknown provenance

### Eligible to requeue (dry run, NOT filed): 244

| job | cause | class | why |
|---|---|---|---|
| `dregen_Force_KyberCrystal_crystal11_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_11.png: ledger variant |
| `dregen_Force_KyberCrystal_crystal16_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_16.png: ledger variant |
| `dregen_Force_KyberCrystal_crystal17_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_17.png: ledger variant |
| `dregen_Force_KyberCrystal_crystal18_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_18.png: ledger variant |
| `dregen_Force_KyberCrystal_crystal1_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_1.png: ledger variant  |
| `dregen_Force_KyberCrystal_crystal2_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_2.png: ledger variant  |
| `dregen_Force_KyberCrystal_crystal3_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_3.png: ledger variant  |
| `dregen_Force_KyberCrystal_crystal4_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_4.png: ledger variant  |
| `dregen_Force_KyberCrystal_crystal5_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_5.png: ledger variant  |
| `dregen_Force_KyberCrystal_crystal6_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_6.png: ledger variant  |
| `dregen_Force_KyberCrystal_crystal7_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_7.png: ledger variant  |
| `dregen_Force_KyberCrystal_crystal8_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_8.png: ledger variant  |
| `dregen_Force_KyberCrystal_crystal9_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_9.png: ledger variant  |
| `dregen_Force_KyberCrystal_crystalgem_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_gem.png: ledger varian |
| `dregen_Force_KyberCrystal_crystalheart_v1` | 429 | DONOR | src/RimStarWars/Armoury/Textures/StandIn/Things/Item/Resource/Crystal/Synthetic/crystal_heart.png: ledger vari |
| `dregen_RM_Apparel_LacquerCloak_Cape_v1` | 429 | DONOR | RM_Apparel_LacquerCloak:Things/Pawn/Humanlike/Apparel/Cape/Cape: the game serves Things/Pawn/Humanlike/Apparel |
| `dregen_RM_Apparel_RindCoat_Duster_v1` | 429 | DONOR | RM_Apparel_RindCoat:Things/Pawn/Humanlike/Apparel/Duster/Duster: the game serves Things/Pawn/Humanlike/Apparel |
| `dregen_RM_Apparel_ScaldWrap_Duster_v1` | 429 | DONOR | RM_Apparel_ScaldWrap:Things/Pawn/Humanlike/Apparel/Duster/Duster: the game serves Things/Pawn/Humanlike/Appare |
| `dregen_RM_BankSilt_Rich_SoilRich_v1` | 429 | DONOR | RM_BankSilt_Rich:Terrain/Surfaces/SoilRich: the game serves Terrain/Surfaces/SoilRich from regrowth.botr.core  |
| `dregen_RM_BasaltShingle_CooledLava_v1` | 429 | DONOR | RM_BasaltShingle:Terrain/Surfaces/CooledLava: the game serves Terrain/Surfaces/CooledLava from ludeon.rimworld |
| `dregen_RM_BellowsExhale_ReleaseDeadlifeDust_v1` | 429 | DONOR | RM_BellowsExhale:UI/Abilities/ReleaseDeadlifeDust: the game serves UI/Abilities/ReleaseDeadlifeDust from ludeo |
| `dregen_RM_BoltShedCuriosity_ComponentIndustrial_v1` | 429 | DONOR | RM_BoltShedCuriosity:Things/Item/Resource/ComponentIndustrial: the game serves Things/Item/Resource/ComponentI |
| `dregen_RM_BrakkelFruit_AgaveFruit_v1` | 429 | DONOR | RM_BrakkelFruit:Things/Item/Resource/PlantFoodRaw/AgaveFruit: the game serves Things/Item/Resource/PlantFoodRa |
| `dregen_RM_BrewingVessel_FermentingBarrel_v1` | 429 | DONOR | RM_BrewingVessel:Things/Building/Production/FermentingBarrel: the game serves Things/Building/Production/Ferme |
| `dregen_RM_BrineChannel_Sand_v1` | 429 | DONOR | RM_BrineChannel:Terrain/Surfaces/Sand: the game serves Terrain/Surfaces/Sand from regrowth.botr.core (VANILLA_ |
| `dregen_RM_BrineDippingSpot_CraftingSpot_v1` | 429 | DONOR | RM_BrineDippingSpot:Things/Building/Production/CraftingSpot: the game serves Things/Building/Production/Crafti |
| `dregen_RM_BrinePoolDeep_WaterDeepRamp_v1` | 429 | DONOR | RM_BrinePoolDeep:Terrain/Surfaces/WaterDeepRamp: the game serves Terrain/Surfaces/WaterDeepRamp from ludeon.ri |
| `dregen_RM_Bullet_Sunbeam_ChargeSmall_v1` | 429 | DONOR | RM_Bullet_Sunbeam:Things/Projectile/Charge_Small: the game serves Things/Projectile/Charge_Small from ludeon.r |
| `dregen_RM_CallingPyre_BurnCircle_v1` | 429 | DONOR | RM_CallingPyre:UI/Icons/Rituals/BurnCircle: the game serves UI/Icons/Rituals/BurnCircle from ludeon.rimworld.i |
| `dregen_RM_CathedralHeatLog_Leather_v1` | 429 | DONOR | RM_CathedralHeatLog:Things/Item/Resource/Leather: the game serves Things/Item/Resource/Leather from ludeon.rim |
| `dregen_RM_CathedralRoachShell_ComponentIndustrial_v1` | 429 | DONOR | RM_CathedralRoachShell:Things/Item/Resource/ComponentIndustrial: the game serves Things/Item/Resource/Componen |
| `dregen_RM_CaudalLeap_Longjump_v1` | 429 | DONOR | RM_CaudalLeap:UI/Abilities/Longjump: the game serves UI/Abilities/Longjump from ludeon.rimworld.biotech (VANIL |
| `dregen_RM_CauldronSoilRich_SoilRich_v1` | 429 | DONOR | RM_CauldronSoilRich:Terrain/Surfaces/SoilRich: the game serves Terrain/Surfaces/SoilRich from regrowth.botr.co |
| `dregen_RM_ChatrakPlate_Leather_v1` | 429 | DONOR | RM_ChatrakPlate:Things/Item/Resource/Leather: the game serves Things/Item/Resource/Leather from ludeon.rimworl |
| `dregen_RM_ChillAuroraCollector_DropBeacon_v1` | 429 | DONOR | RM_ChillAuroraCollector:Things/Building/Misc/DropBeacon: the game serves Things/Building/Misc/DropBeacon from  |
| `dregen_RM_ChillCraterGlass_Ice_v1` | 429 | DONOR | RM_ChillCraterGlass:Terrain/Surfaces/Ice: the game serves Terrain/Surfaces/Ice from ludeon.rimworld.core (VANI |
| `dregen_RM_ChillHeatedSuit_Vacsuit_v1` | 429 | DONOR | RM_ChillHeatedSuit:Things/Pawn/Humanlike/Apparel/Vacsuit/Vacsuit: the game serves Things/Pawn/Humanlike/Appare |
| `dregen_RM_ChillIceBedrock_Ice_v1` | 429 | DONOR | RM_ChillIceBedrock:Terrain/Surfaces/Ice: the game serves Terrain/Surfaces/Ice from ludeon.rimworld.core (VANIL |
| `dregen_RM_ChillRimeTerrace_Gravel_v1` | 429 | DONOR | RM_ChillRimeTerrace:Terrain/Surfaces/Gravel: the game serves Terrain/Surfaces/Gravel from regrowth.botr.core ( |
| `dregen_RM_ChimeLineAnchor_TorchLamp_v1` | 429 | DONOR | RM_ChimeLineAnchor:Things/Building/Misc/TorchLamp: the game serves Things/Building/Misc/TorchLamp from ludeon. |
| `dregen_RM_ChurnmudSealed_PavedTile_v1` | 429 | DONOR | RM_ChurnmudSealed:Terrain/Surfaces/PavedTile: the game serves Terrain/Surfaces/PavedTile from ludeon.rimworld. |
| `dregen_RM_CloakLacquer_Chemfuel_v1` | 429 | DONOR | RM_CloakLacquer:Things/Item/Resource/Chemfuel: the game serves Things/Item/Resource/Chemfuel from ludeon.rimwo |
| `dregen_RM_ContagionUnstableGenome_GeneWeakImmunity_v1` | 429 | DONOR | RM_ContagionUnstableGenome:UI/Icons/Genes/Gene_WeakImmunity: the game serves UI/Icons/Genes/Gene_WeakImmunity  |
| `dregen_RM_DeadSmartsteel_Steel_v1` | 429 | DONOR | RM_DeadSmartsteel:Things/Item/Resource/Steel: the game serves Things/Item/Resource/Steel from ludeon.rimworld. |
| `dregen_RM_DenseMud_ABDenseMud_v1` | 429 | DONOR | src/RimMandrake/Webwork/Textures/StandIn/Terrain/Surfaces/AB_DenseMud.png: ledger variant d22ba3958f5ae1d64d12 |
| `dregen_RM_DesignationDigOutBuried_Mine_v1` | 429 | DONOR | RM_DesignationDigOutBuried:Designations/Mine: the game serves Designations/Mine from ludeon.rimworld.core (VAN |
| `dregen_RM_Designation_FoulPool_Mine_v1` | 429 | DONOR | RM_Designation_FoulPool:Designations/Mine: the game serves Designations/Mine from ludeon.rimworld.core (VANILL |
| `dregen_RM_Designation_StakeLure_Slaughter_v1` | 429 | DONOR | RM_Designation_StakeLure:Designations/Slaughter: the game serves Designations/Slaughter from ludeon.rimworld.c |
| `dregen_RM_DhokkurPolishedTrail_SmoothVolcanicRock_v1` | 429 | DONOR | RM_DhokkurPolishedTrail:Terrain/Surfaces/SmoothVolcanicRock: the game serves Terrain/Surfaces/SmoothVolcanicRo |
| `dregen_RM_Duckboards_WoodFloor_v1` | 429 | DONOR | RM_Duckboards:Terrain/Surfaces/WoodFloor: the game serves Terrain/Surfaces/WoodFloor from ludeon.rimworld.core |
| `dregen_RM_DuskfireSpit_FireSpew_v1` | 429 | DONOR | RM_DuskfireSpit:UI/Abilities/FireSpew: the game serves UI/Abilities/FireSpew from ludeon.rimworld.biotech (VAN |
| `dregen_RM_EggBokkaUnfertilized_EggRound_v1` | 429 | DONOR | RM_EggBokkaUnfertilized:Things/Item/Resource/AnimalProductRaw/EggRound: the game serves Things/Item/Resource/A |
| `dregen_RM_ElectricGryllotalpa_Arc_LauncherShot_v1` | 429 | DONOR | RM_ElectricGryllotalpa_Arc:Things/Projectile/LauncherShot: the game serves Things/Projectile/LauncherShot from |
| `dregen_RM_EvaluateRing_Deconstruct_v1` | 429 | DONOR | RM_EvaluateRing:UI/Designators/Deconstruct: the game serves UI/Designators/Deconstruct from ludeon.rimworld.co |
| `dregen_RM_Eyeburst_BionicEye_v1` | 429 | DONOR | RM_Eyeburst:Things/Pawn/Wounds/BionicEye: the game serves Things/Pawn/Wounds/BionicEye from vanillaexpanded.vt |
| `dregen_RM_FE_Bullet_FirefoamSplash_ShellFirefoam_v1` | 429 | DONOR | RM_FE_Bullet_FirefoamSplash:Things/Projectile/ShellFirefoam: the game serves Things/Projectile/ShellFirefoam f |
| `dregen_RM_FE_Filth_LooseAsh_Ash_v1` | 429 | DONOR | RM_FE_Filth_LooseAsh:Things/Filth/Ash: the game serves Things/Filth/Ash from ludeon.rimworld.core (VANILLA) |
| `dregen_RM_FE_FirebreakLine_RoughHewnRock_v1` | 429 | DONOR | RM_FE_FirebreakLine:Terrain/Surfaces/RoughHewnRock: the game serves Terrain/Surfaces/RoughHewnRock from ludeon |
| `dregen_RM_FE_Ground_Gravel_Gravel_v1` | 429 | DONOR | RM_FE_Ground_Gravel:Terrain/Surfaces/Gravel: the game serves Terrain/Surfaces/Gravel from regrowth.botr.core ( |
| `dregen_RM_FE_Ground_Sand_Sand_v1` | 429 | DONOR | RM_FE_Ground_Sand:Terrain/Surfaces/Sand: the game serves Terrain/Surfaces/Sand from regrowth.botr.core (VANILL |
| `dregen_RM_FE_Ground_SoilRich_SoilRich_v1` | 429 | DONOR | RM_FE_Ground_SoilRich:Terrain/Surfaces/SoilRich: the game serves Terrain/Surfaces/SoilRich from regrowth.botr. |
| `dregen_RM_FermentedMound_RawFungus_v1` | 429 | DONOR | RM_FermentedMound:Things/Item/Resource/PlantFoodRaw/RawFungus: the game serves Things/Item/Resource/PlantFoodR |
| `dregen_RM_FessuCatch_MeatSmall_v1` | 429 | DONOR | RM_FessuCatch:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFoodRaw/Me |
| `dregen_RM_FilterCartridge_ComponentIndustrial_v1` | 429 | DONOR | RM_FilterCartridge:Things/Item/Resource/ComponentIndustrial: the game serves Things/Item/Resource/ComponentInd |
| `dregen_RM_FilthBone_Ash_v1` | 429 | DONOR | RM_FilthBone:Things/Filth/Ash: the game serves Things/Filth/Ash from ludeon.rimworld.core (VANILLA) |
| `dregen_RM_Filth_ChillFrostGlaze_PoolSoft_v1` | 429 | DONOR | RM_Filth_ChillFrostGlaze:Things/Filth/PoolSoft: the game serves Things/Filth/PoolSoft from ludeon.rimworld.cor |
| `dregen_RM_Filth_CleaverShards_RubbleRock_v1` | 429 | DONOR | RM_Filth_CleaverShards:Things/Filth/RubbleRock: the game serves Things/Filth/RubbleRock from ih.clean.textures |
| `dregen_RM_Filth_HullRime_Ash_v1` | 429 | DONOR | RM_Filth_HullRime:Things/Filth/Ash: the game serves Things/Filth/Ash from ludeon.rimworld.core (VANILLA) |
| `dregen_RM_Filth_RainPuddle_Spatter_v1` | 429 | DONOR | RM_Filth_RainPuddle:Things/Filth/Spatter: the game serves Things/Filth/Spatter from ludeon.rimworld.core (VANI |
| `dregen_RM_Filth_SurrikExitHole_RubbleRock_v1` | 429 | DONOR | RM_Filth_SurrikExitHole:Things/Filth/RubbleRock: the game serves Things/Filth/RubbleRock from ih.clean.texture |
| `dregen_RM_Filth_VeilFlakes_Ash_v1` | 429 | DONOR | RM_Filth_VeilFlakes:Things/Filth/Ash: the game serves Things/Filth/Ash from ludeon.rimworld.core (VANILLA) |
| `dregen_RM_Filth_WaterSpill_Spatter_v1` | 429 | DONOR | RM_Filth_WaterSpill:Things/Filth/Spatter: the game serves Things/Filth/Spatter from ludeon.rimworld.core (VANI |
| `dregen_RM_FineForsakenSand_ABFineForsakenSands_v1` | 429 | DONOR | src/RimMandrake/Abyss/Textures/StandIn/Terrain/Surfaces/AB_FineForsakenSands.png: ledger variant cf71c41067656 |
| `dregen_RM_FirevineTree_ABFirevineTreeA_v1` | 429 | DONOR | src/RimMandrake/TheForge/Textures/StandIn/Things/Plants/AB_FirevineTree/AB_FirevineTreeA.png: ledger variant 7 |
| `dregen_RM_FirevineTree_ABFirevineTreeD_v1` | 429 | DONOR | src/RimMandrake/TheForge/Textures/StandIn/Things/Plants/AB_FirevineTree/AB_FirevineTreeD.png: ledger variant 8 |
| `dregen_RM_Fleck_DeadlightRim_FireGlow_v1` | 429 | DONOR | RM_Fleck_DeadlightRim:Things/Mote/FireGlow: the game serves Things/Mote/FireGlow from ludeon.rimworld.core (VA |
| `dregen_RM_Fleck_LevitatingScrap_ThrownDebris_v1` | 429 | DONOR | RM_Fleck_LevitatingScrap:Things/Mote/ThrownDebris: the game serves Things/Mote/ThrownDebris from ludeon.rimwor |
| `dregen_RM_FloatHarness_Duster_v1` | 429 | DONOR | RM_FloatHarness:Things/Pawn/Humanlike/Apparel/Duster/Duster: the game serves Things/Pawn/Humanlike/Apparel/Dus |
| `dregen_RM_FloatstoneDoor_DoorSimpleMenuIcon_v1` | 429 | DONOR | RM_FloatstoneDoor:Things/Building/Door/DoorSimple_MenuIcon: the game serves Things/Building/Door/DoorSimple_Me |
| `dregen_RM_FloatstoneDoor_DoorSimpleMover_v1` | 429 | DONOR | RM_FloatstoneDoor:Things/Building/Door/DoorSimple_Mover: the game serves Things/Building/Door/DoorSimple_Mover |
| `dregen_RM_ForsakenSand_ABForsakenSands_v1` | 429 | DONOR | src/RimMandrake/Abyss/Textures/StandIn/Terrain/Surfaces/AB_ForsakenSands.png: ledger variant aac1535f64e66f94a |
| `dregen_RM_FrenzyDose_Yayo_v1` | 429 | DONOR | RM_FrenzyDose:Things/Item/Drug/Yayo: the game serves Things/Item/Drug/Yayo from ludeon.rimworld.core (VANILLA) |
| `dregen_RM_FrostLeaf_ABFrostLeafA_v1` | 429 | DONOR | src/RimMandrake/TerminalBiomes/Textures/StandIn/Things/Plants/AB_FrostLeaf/AB_FrostLeafA.png: ledger variant 7 |
| `dregen_RM_FrostLeaf_ABFrostLeafB_v1` | 429 | DONOR | src/RimMandrake/TerminalBiomes/Textures/StandIn/Things/Plants/AB_FrostLeaf/AB_FrostLeafB.png: ledger variant f |
| `dregen_RM_FrostLeaf_ABFrostLeafC_v1` | 429 | DONOR | src/RimMandrake/TerminalBiomes/Textures/StandIn/Things/Plants/AB_FrostLeaf/AB_FrostLeafC.png: ledger variant 2 |
| `dregen_RM_FuzzFiber_Cloth_v1` | 429 | DONOR | RM_FuzzFiber:Things/Item/Resource/Cloth: the game serves Things/Item/Resource/Cloth from ludeon.rimworld.core  |
| `dregen_RM_GalleryBreak_CaveEntranceA_v1` | 429 | DONOR | RM_GalleryBreak:Things/Building/CaveEntranceA: the game serves Things/Building/CaveEntranceA from ludeon.rimwo |
| `dregen_RM_GalleryOutlet_CaveEntranceA_v1` | 429 | DONOR | RM_GalleryOutlet:Things/Building/CaveEntranceA: the game serves Things/Building/CaveEntranceA from ludeon.rimw |
| `dregen_RM_GalleryPipe_CaveEntranceA_v1` | 429 | DONOR | RM_GalleryPipe:Things/Building/CaveEntranceA: the game serves Things/Building/CaveEntranceA from ludeon.rimwor |
| `dregen_RM_GargantuanLithops_ABLithops_v1` | 429 | DONOR | src/RimMandrake/CrackedLands/Textures/StandIn/Things/Plants/AB_Lithops.png: ledger variant 581141f9cea4422345e |
| `dregen_RM_Gene_Furnaceblood_GeneFurskin_v1` | 429 | DONOR | RM_Gene_Furnaceblood:UI/Icons/Genes/Gene_Furskin: the game serves UI/Icons/Genes/Gene_Furskin from ludeon.rimw |
| `dregen_RM_GenomeSample_Genepack_v1` | 429 | DONOR | RM_GenomeSample:Things/Item/Special/Genepack: the game serves Things/Item/Special/Genepack from ludeon.rimworl |
| `dregen_RM_GiantAgarilux_ABGiantAgariluxB_v1` | 429 | DONOR | src/RimMandrake/TheRot/Textures/StandIn/Things/Plants/AB_GiantAgarilux/AB_GiantAgariluxB.png: ledger variant a |
| `dregen_RM_GiantAgarilux_ABGiantAgariluxC_v1` | 429 | DONOR | src/RimMandrake/TheRot/Textures/StandIn/Things/Plants/AB_GiantAgarilux/AB_GiantAgariluxC.png: ledger variant 5 |
| `dregen_RM_GiantAgarilux_ABGiantAgariluxD_v1` | 429 | DONOR | src/RimMandrake/TheRot/Textures/StandIn/Things/Plants/AB_GiantAgarilux/AB_GiantAgariluxD.png: ledger variant 7 |
| `dregen_RM_GlobularPlant_ABGlobularPlant_v1` | 429 | DONOR | src/RimMandrake/Contagion/Textures/StandIn/Things/Plants/AB_GlobularPlant.png: ledger variant a37d45e467cb9941 |
| `dregen_RM_GloomcastHide_LeatherHeavya_v1` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swresource/Leather_Heavy/Leather_Heavy_a.png: ledger variant 87e4ea47a6c82 |
| `dregen_RM_GloomcastHide_LeatherHeavyb_v1` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swresource/Leather_Heavy/Leather_Heavy_b.png: ledger variant f9e04a82d600f |
| `dregen_RM_GlowerPlate_ShieldBelt_v1` | 429 | DONOR | RM_GlowerPlate:Things/Pawn/Humanlike/Apparel/ShieldBelt/ShieldBelt: the game serves Things/Pawn/Humanlike/Appa |
| `dregen_RM_GorbelethToxin_PsychoidLeaves_v1` | 429 | DONOR | RM_GorbelethToxin:Things/Item/Resource/PlantFoodRaw/PsychoidLeaves: the game serves Things/Item/Resource/Plant |
| `dregen_RM_GreatboleGrubSpines_Leather_v1` | 429 | DONOR | RM_GreatboleGrubSpines:Things/Item/Resource/Leather: the game serves Things/Item/Resource/Leather from ludeon. |
| `dregen_RM_GreentideChurnmud_Mud_v1` | 429 | DONOR | RM_GreentideChurnmud:Terrain/Surfaces/Mud: the game serves Terrain/Surfaces/Mud from ludeon.rimworld.core (VAN |
| `dregen_RM_HalfAlienTree_ABHalfAlienTreeA_v1` | 429 | DONOR | src/RimMandrake/Contagion/Textures/StandIn/Things/Plants/AB_HalfAlienTree/AB_HalfAlienTreeA.png: ledger varian |
| `dregen_RM_HalfAlienTree_ABHalfAlienTreeB_v1` | 429 | DONOR | src/RimMandrake/Contagion/Textures/StandIn/Things/Plants/AB_HalfAlienTree/AB_HalfAlienTreeB.png: ledger varian |
| `dregen_RM_HardenedGrass_ABHardenedGrass_v1` | 429 | DONOR | src/RimMandrake/TheForge/Textures/StandIn/Terrain/Surfaces/AB_HardenedGrass.png: ledger variant 69f75ca059a3e0 |
| `dregen_RM_HeatedSuitCharger_Battery_v1` | 429 | DONOR | RM_HeatedSuitCharger:Things/Building/Power/Battery: the game serves Things/Building/Power/Battery from ludeon. |
| `dregen_RM_HoolimbreLampClipped_BeamGlow_v1` | 429 | DONOR | RM_HoolimbreLampClipped:Things/Mote/BeamGlow: the game serves Things/Mote/BeamGlow from ludeon.rimworld.core ( |
| `dregen_RM_HulduBreedingStock_MeatSmall_v1` | 429 | DONOR | RM_HulduBreedingStock:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFo |
| `dregen_RM_HulduMeat_MeatSmall_v1` | 429 | DONOR | RM_HulduMeat:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFoodRaw/Mea |
| `dregen_RM_Iashiphus_ABIashiphus_v1` | 429 | DONOR | src/RimMandrake/FeverWood/Textures/StandIn/Things/Plants/AB_Iashiphus.png: ledger variant 5745a2da1c293a150057 |
| `dregen_RM_ImmersionSchematic_Leather_v1` | 429 | DONOR | RM_ImmersionSchematic:Things/Item/Resource/Leather: the game serves Things/Item/Resource/Leather from ludeon.r |
| `dregen_RM_IvvolBreedingStock_MeatSmall_v1` | 429 | DONOR | RM_IvvolBreedingStock:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFo |
| `dregen_RM_IvvolMeat_MeatSmall_v1` | 429 | DONOR | RM_IvvolMeat:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFoodRaw/Mea |
| `dregen_RM_JungleTree_ABJungleTreeA_v1` | 429 | DONOR | src/RimMandrake/Webwork/Textures/StandIn/Things/Plants/AB_JungleTree/AB_JungleTreeA.png: ledger variant 646862 |
| `dregen_RM_JungleTree_ABJungleTreeB_v1` | 429 | DONOR | src/RimMandrake/Webwork/Textures/StandIn/Things/Plants/AB_JungleTree/AB_JungleTreeB.png: ledger variant 65375d |
| `dregen_RM_JungleTree_ABJungleTreeC_v1` | 429 | DONOR | src/RimMandrake/Webwork/Textures/StandIn/Things/Plants/AB_JungleTree/AB_JungleTreeC.png: ledger variant bafb10 |
| `dregen_RM_JungleTree_ABJungleTreeG_v1` | 429 | DONOR | src/RimMandrake/Webwork/Textures/StandIn/Things/Plants/AB_JungleTree/AB_JungleTreeG.png: ledger variant dbf52f |
| `dregen_RM_KarrekBreedingStock_MeatSmall_v1` | 429 | DONOR | RM_KarrekBreedingStock:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatF |
| `dregen_RM_KarrekMeat_MeatSmall_v1` | 429 | DONOR | RM_KarrekMeat:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFoodRaw/Me |
| `dregen_RM_KurrethResinPlug_CollapsedRocks_v1` | 429 | DONOR | RM_KurrethResinPlug:Things/Building/Natural/CollapsedRocks: the game serves Things/Building/Natural/CollapsedR |
| `dregen_RM_LampBladder_BeamGlow_v1` | 429 | DONOR | RM_LampBladder:Things/Mote/BeamGlow: the game serves Things/Mote/BeamGlow from ludeon.rimworld.core (VANILLA) |
| `dregen_RM_LanternDeepEmergence_CaveEntranceA_v1` | 429 | DONOR | RM_LanternDeepEmergence:Things/Building/CaveEntranceA: the game serves Things/Building/CaveEntranceA from lude |
| `dregen_RM_LanternDeepMineshaft_PitGate_v1` | 429 | DONOR | RM_LanternDeepMineshaft:Things/Building/PitGate/PitGate: the game serves Things/Building/PitGate/PitGate from  |
| `dregen_RM_LastvineSpit_AcidSpray_v1` | 429 | DONOR | RM_LastvineSpit:UI/Abilities/AcidSpray: the game serves UI/Abilities/AcidSpray from ludeon.rimworld.core (VANI |
| `dregen_RM_LilacBeacon_ABLilacBeaconC_v1` | 429 | DONOR | src/RimMandrake/TheRot/Textures/StandIn/Things/Plants/AB_LilacBeacon/AB_LilacBeaconC.png: ledger variant d3550 |
| `dregen_RM_LivePatternMetal_Steel_v1` | 429 | DONOR | RM_LivePatternMetal:Things/Item/Resource/Steel: the game serves Things/Item/Resource/Steel from ludeon.rimworl |
| `dregen_RM_LoomuBreedingStock_MeatSmall_v1` | 429 | DONOR | RM_LoomuBreedingStock:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFo |
| `dregen_RM_LoomuMeat_MeatSmall_v1` | 429 | DONOR | RM_LoomuMeat:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFoodRaw/Mea |
| `dregen_RM_LureFruit_Berries_v1` | 429 | DONOR | RM_LureFruit:Things/Item/Resource/PlantFoodRaw/Berries: the game serves Things/Item/Resource/PlantFoodRaw/Berr |
| `dregen_RM_LushGrass_ABLushGrass_v1` | 429 | DONOR | src/RimMandrake/TheSump/Textures/StandIn/Terrain/Surfaces/AB_LushGrass.png: ledger variant a3ddc46ec3549ba41fd |
| `dregen_RM_MangrovePalm_ABMangrovePalmA_v1` | 429 | DONOR | src/RimMandrake/Miasma/Textures/StandIn/Things/Plants/AB_MangrovePalm/AB_MangrovePalmA.png: ledger variant 9b3 |
| `dregen_RM_MangroveTree_ABMangroveTreeC_v1` | 429 | DONOR | src/RimMandrake/Miasma/Textures/StandIn/Things/Plants/AB_MangroveTree/AB_MangroveTreeC.png: ledger variant 5f8 |
| `dregen_RM_MealMurrinBroth_Simple_v1` | 429 | DONOR | RM_MealMurrinBroth:Things/Item/Meal/Simple: the game serves Things/Item/Meal/Simple from ludeon.rimworld.core  |
| `dregen_RM_MercyCarving_SculptureSmall_v1` | 429 | DONOR | RM_MercyCarving:Things/Building/Art/SculptureSmall: the game serves Things/Building/Art/SculptureSmall from bi |
| `dregen_RM_MiasmaSaltCrust_DryLakeBed_v1` | 429 | DONOR | RM_MiasmaSaltCrust:Terrain/Surfaces/DryLakeBed: the game serves Terrain/Surfaces/DryLakeBed from ludeon.rimwor |
| `dregen_RM_MulchedSoil_SoilRich_v1` | 429 | DONOR | RM_MulchedSoil:Terrain/Surfaces/SoilRich: the game serves Terrain/Surfaces/SoilRich from regrowth.botr.core (V |
| `dregen_RM_MurrinBreedingStock_MeatSmall_v1` | 429 | DONOR | RM_MurrinBreedingStock:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatF |
| `dregen_RM_MurrinMeat_MeatSmall_v1` | 429 | DONOR | RM_MurrinMeat:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFoodRaw/Me |
| `dregen_RM_MushroomFloor_WoodFloor_v1` | 429 | DONOR | RM_MushroomFloor:Terrain/Surfaces/WoodFloor: the game serves Terrain/Surfaces/WoodFloor from ludeon.rimworld.c |
| `dregen_RM_NabbuqBladder_Potatoes_v1` | 429 | DONOR | RM_NabbuqBladder:Things/Item/Resource/PlantFoodRaw/Potatoes: the game serves Things/Item/Resource/PlantFoodRaw |
| `dregen_RM_NoothelmBulb_BeamGlow_v1` | 429 | DONOR | RM_NoothelmBulb:Things/Mote/BeamGlow: the game serves Things/Mote/BeamGlow from ludeon.rimworld.core (VANILLA) |
| `dregen_RM_NoothelmLampClipped_BeamGlow_v1` | 429 | DONOR | RM_NoothelmLampClipped:Things/Mote/BeamGlow: the game serves Things/Mote/BeamGlow from ludeon.rimworld.core (V |
| `dregen_RM_OdduCatch_MeatSmall_v1` | 429 | DONOR | RM_OdduCatch:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFoodRaw/Mea |
| `dregen_RM_OldCurrentMeter_SignalChip_v1` | 429 | DONOR | RM_OldCurrentMeter:Things/Item/Resource/SignalChip: the game serves Things/Item/Resource/SignalChip from ludeo |
| `dregen_RM_OssrithCrystal_Uranium_v1` | 429 | DONOR | RM_OssrithCrystal:Things/Item/Resource/Uranium: the game serves Things/Item/Resource/Uranium from ludeon.rimwo |
| `dregen_RM_PackedIce_ABWhiteIce_v1` | 429 | DONOR | src/RimMandrake/TerminalBiomes/Textures/StandIn/Terrain/Surfaces/AB_WhiteIce.png: ledger variant f0a03125726e5 |
| `dregen_RM_ParasiticMangrove_ABParasiticMangroveA_v1` | 429 | DONOR | src/RimMandrake/Miasma/Textures/StandIn/Things/Plants/AB_ParasiticMangrove/AB_ParasiticMangroveA.png: ledger v |
| `dregen_RM_ParasiticMangrove_ABParasiticMangroveB_v1` | 429 | DONOR | src/RimMandrake/Miasma/Textures/StandIn/Things/Plants/AB_ParasiticMangrove/AB_ParasiticMangroveB.png: ledger v |
| `dregen_RM_Proj_GrenadeStenchSmoke_ToxGrenadeThrown_v1` | 429 | DONOR | RM_Proj_GrenadeStenchSmoke:Things/Projectile/ToxGrenadeThrown: the game serves Things/Projectile/ToxGrenadeThr |
| `dregen_RM_Proj_TitanoslimeChunk_Grenade_v1` | 429 | DONOR | RM_Proj_TitanoslimeChunk:Things/Projectile/Grenade: the game serves Things/Projectile/Grenade from ludeon.rimw |
| `dregen_RM_PumiceRubble_Gravel_v1` | 429 | DONOR | RM_PumiceRubble:Terrain/Surfaces/Gravel: the game serves Terrain/Surfaces/Gravel from regrowth.botr.core (VANI |
| `dregen_RM_QuarrokChitin_Leather_v1` | 429 | DONOR | RM_QuarrokChitin:Things/Item/Resource/Leather: the game serves Things/Item/Resource/Leather from ludeon.rimwor |
| `dregen_RM_RandomBricks_StoneBlocks_v1` | 429 | DONOR | RM_RandomBricks:Things/Item/Resource/StoneBlocks: the game serves Things/Item/Resource/StoneBlocks from ludeon |
| `dregen_RM_RawMurrowbulb_Potatoes_v1` | 429 | DONOR | RM_RawMurrowbulb:Things/Item/Resource/PlantFoodRaw/Potatoes: the game serves Things/Item/Resource/PlantFoodRaw |
| `dregen_RM_RawSalvessa_Hay_v1` | 429 | DONOR | RM_RawSalvessa:Things/Item/Resource/PlantFoodRaw/Hay: the game serves Things/Item/Resource/PlantFoodRaw/Hay fr |
| `dregen_RM_RawThrannagourd_Potatoes_v1` | 429 | DONOR | RM_RawThrannagourd:Things/Item/Resource/PlantFoodRaw/Potatoes: the game serves Things/Item/Resource/PlantFoodR |
| `dregen_RM_ReturnCombIce_CaveEntranceA_v1` | 429 | DONOR | RM_ReturnCombIce:Things/Building/CaveEntranceA: the game serves Things/Building/CaveEntranceA from ludeon.rimw |
| `dregen_RM_RootCauseway_PackedDirt_v1` | 429 | DONOR | RM_RootCauseway:Terrain/Surfaces/PackedDirt: the game serves Terrain/Surfaces/PackedDirt from ludeon.rimworld. |
| `dregen_RM_RoyalRind_Leather_v1` | 429 | DONOR | RM_RoyalRind:Things/Item/Resource/Leather: the game serves Things/Item/Resource/Leather from ludeon.rimworld.c |
| `dregen_RM_RustCathedral_CrackedMetalSoil_ABSoilOnCrackedMetal_v1` | 429 | DONOR | src/RimMandrake/RustCathedral/Textures/StandIn/Terrain/Surfaces/AB_SoilOnCrackedMetal.png: ledger variant 2ea2 |
| `dregen_RM_RustCathedral_PolymerFloor_ABPolymer_v1` | 429 | DONOR | src/RimMandrake/RustCathedral/Textures/StandIn/Terrain/Surfaces/AB_Polymer.png: ledger variant 1d763e0790f7ecf |
| `dregen_RM_SapResin_Jade_v1` | 429 | DONOR | RM_SapResin:Things/Item/Resource/Jade: the game serves Things/Item/Resource/Jade from ludeon.rimworld.core (VA |
| `dregen_RM_SarquinSap_Hops_v1` | 429 | DONOR | RM_SarquinSap:Things/Item/Resource/PlantFoodRaw/Hops: the game serves Things/Item/Resource/PlantFoodRaw/Hops f |
| `dregen_RM_ScaldWalkerChitin_Leather_v1` | 429 | DONOR | RM_ScaldWalkerChitin:Things/Item/Resource/Leather: the game serves Things/Item/Resource/Leather from ludeon.ri |
| `dregen_RM_SeaDiveHatch_CaveEntranceA_v1` | 429 | DONOR | RM_SeaDiveHatch:Things/Building/CaveEntranceA: the game serves Things/Building/CaveEntranceA from ludeon.rimwo |
| `dregen_RM_Seepwax_Chemfuel_v1` | 429 | DONOR | RM_Seepwax:Things/Item/Resource/Chemfuel: the game serves Things/Item/Resource/Chemfuel from ludeon.rimworld.c |
| `dregen_RM_SeveredTentacleFlesh_MeatBig_v1` | 429 | DONOR | RM_SeveredTentacleFlesh:Things/Item/Resource/MeatFoodRaw/Meat_Big: the game serves Things/Item/Resource/MeatFo |
| `dregen_RM_ShipPart_HullPlating_Plasteel_v1` | 429 | DONOR | RM_ShipPart_HullPlating:Things/Item/Resource/Plasteel: the game serves Things/Item/Resource/Plasteel from lude |
| `dregen_RM_SkarrinBreedingStock_MeatSmall_v1` | 429 | DONOR | RM_SkarrinBreedingStock:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/Meat |
| `dregen_RM_SkarrinMeat_MeatSmall_v1` | 429 | DONOR | RM_SkarrinMeat:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFoodRaw/M |
| `dregen_RM_SkellarnChitin_Leather_v1` | 429 | DONOR | RM_SkellarnChitin:Things/Item/Resource/Leather: the game serves Things/Item/Resource/Leather from ludeon.rimwo |
| `dregen_RM_Skylight_BeamGlow_v1` | 429 | DONOR | RM_Skylight:Things/Mote/BeamGlow: the game serves Things/Mote/BeamGlow from ludeon.rimworld.core (VANILLA) |
| `dregen_RM_SlimeFarmLedger_Novel_v1` | 429 | DONOR | RM_SlimeFarmLedger:Things/Item/Book/Novel/Novel: the game serves Things/Item/Book/Novel/Novel from ludeon.rimw |
| `dregen_RM_SlimePit_TableStoveFueled_v1` | 429 | DONOR | RM_SlimePit:Things/Building/Production/TableStoveFueled: the game serves Things/Building/Production/TableStove |
| `dregen_RM_Slime_ABSlime_v1` | 429 | DONOR | src/RimMandrake/GelatinousSlime/Textures/StandIn/Terrain/Surfaces/AB_Slime.png: ledger variant 7ce135ea649494b |
| `dregen_RM_Slime_Grass_SoilRich_v1` | 429 | DONOR | RM_Slime_Grass:Terrain/Surfaces/SoilRich: the game serves Terrain/Surfaces/SoilRich from regrowth.botr.core (V |
| `dregen_RM_Slime_Hardened_Soil_v1` | 429 | DONOR | RM_Slime_Hardened:Terrain/Surfaces/Soil: the game serves Terrain/Surfaces/Soil from regrowth.botr.core (VANILL |
| `dregen_RM_Slime_Liquid_MarshyTerrain_v1` | 429 | DONOR | RM_Slime_Liquid:Terrain/Surfaces/MarshyTerrain: the game serves Terrain/Surfaces/MarshyTerrain from regrowth.b |
| `dregen_RM_Slime_Mud_Mud_v1` | 429 | DONOR | RM_Slime_Mud:Terrain/Surfaces/Mud: the game serves Terrain/Surfaces/Mud from ludeon.rimworld.core (VANILLA) |
| `dregen_RM_Slimecasia_ABSlimecasiaA_v1` | 429 | DONOR | src/RimMandrake/GelatinousSlime/Textures/StandIn/Things/Plants/AB_Slimecasia/AB_SlimecasiaA.png: ledger varian |
| `dregen_RM_SlimyFern_ABSlimyFernB_v1` | 429 | DONOR | src/RimMandrake/GelatinousSlime/Textures/StandIn/Things/Plants/AB_SlimyFern/AB_SlimyFernB.png: ledger variant  |
| `dregen_RM_SlimyFern_ABSlimyFernC_v1` | 429 | DONOR | src/RimMandrake/GelatinousSlime/Textures/StandIn/Things/Plants/AB_SlimyFern/AB_SlimyFernC.png: ledger variant  |
| `dregen_RM_SlimyPholiota_ABSlimyPholiotaA_v1` | 429 | DONOR | src/RimMandrake/TheRot/Textures/StandIn/Things/Plants/AB_SlimyPholiota/AB_SlimyPholiotaA.png: ledger variant 7 |
| `dregen_RM_SlimyTree_ABSlimyTreeA_v1` | 429 | DONOR | src/RimMandrake/GelatinousSlime/Textures/StandIn/Things/Plants/AB_SlimyTree/AB_SlimyTreeA.png: ledger variant  |
| `dregen_RM_SlimyTree_ABSlimyTreeB_v1` | 429 | DONOR | src/RimMandrake/GelatinousSlime/Textures/StandIn/Things/Plants/AB_SlimyTree/AB_SlimyTreeB.png: ledger variant  |
| `dregen_RM_SolidPropane_WaterShallowRamp_v1` | 429 | DONOR | RM_SolidPropane:Terrain/Surfaces/WaterShallowRamp: the game serves Terrain/Surfaces/WaterShallowRamp from lude |
| `dregen_RM_SpecimenCabinet_Shelf_v1` | 429 | DONOR | RM_SpecimenCabinet:Things/Building/Furniture/Shelf: the game serves Things/Building/Furniture/Shelf from ludeo |
| `dregen_RM_StenchSporeExtract_PsychoidLeaves_v1` | 429 | DONOR | RM_StenchSporeExtract:Things/Item/Resource/PlantFoodRaw/PsychoidLeaves: the game serves Things/Item/Resource/P |
| `dregen_RM_StrongTarSolvent_RMStrongTarSolvent_v1` | 429 | PLACEHOLDER | src/RimMandrake/TheSump/Textures/Things/Item/Resource/RM_StrongTarSolvent/RM_StrongTarSolvent.png: placeholder |
| `dregen_RM_SugarFamewort_ABSugarFamewort_v1` | 429 | DONOR | src/RimMandrake/Greentide/Textures/StandIn/Things/Plants/AB_SugarFamewort.png: ledger variant e73275d87b6ae597 |
| `dregen_RM_TallSlimyGrass_ABSlimeGrassB_v1` | 429 | DONOR | src/RimMandrake/GelatinousSlime/Textures/StandIn/Things/Plants/AB_SlimeGrass/AB_SlimeGrassB.png: ledger varian |
| `dregen_RM_TarnnCatch_MeatSmall_v1` | 429 | DONOR | RM_TarnnCatch:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFoodRaw/Me |
| `dregen_RM_TheChillDeep_WaterDeepRamp_v1` | 429 | DONOR | RM_TheChillDeep:Terrain/Surfaces/WaterDeepRamp: the game serves Terrain/Surfaces/WaterDeepRamp from ludeon.rim |
| `dregen_RM_ThornLitter_Grainy_v1` | 429 | DONOR | RM_ThornLitter:Things/Filth/Grainy: the game serves Things/Filth/Grainy from ludeon.rimworld.core (VANILLA) |
| `dregen_RM_ThrummelChitin_Leather_v1` | 429 | DONOR | RM_ThrummelChitin:Things/Item/Resource/Leather: the game serves Things/Item/Resource/Leather from ludeon.rimwo |
| `dregen_RM_ThrummelSeepwax_RMThrummelSeepwax_v1` | 429 | PLACEHOLDER | src/RimMandrake/TheSump/Textures/Things/Item/Resource/RM_ThrummelSeepwax/RM_ThrummelSeepwax.png: placeholder ( |
| `dregen_RM_TinkleGrass_ABTinkleGrass_v1` | 429 | DONOR | src/RimMandrake/TheForge/Textures/StandIn/Things/Plants/AB_TinkleGrass.png: ledger variant 9eb40203ef8c062e67a |
| `dregen_RM_TollukCapHarvest_RawFungus_v1` | 429 | DONOR | RM_TollukCapHarvest:Things/Item/Resource/PlantFoodRaw/RawFungus: the game serves Things/Item/Resource/PlantFoo |
| `dregen_RM_ToxiGrass_ABToxiGrass_v1` | 429 | DONOR | src/RimMandrake/BlueDesert/Textures/StandIn/Things/Plants/AB_ToxiGrass.png: ledger variant b94333099e204f9a072 |
| `dregen_RM_ToxinSealant_Leather_v1` | 429 | DONOR | RM_ToxinSealant:Things/Item/Resource/Leather: the game serves Things/Item/Resource/Leather from ludeon.rimworl |
| `dregen_RM_TumbelGourd_Corn_v1` | 429 | DONOR | RM_TumbelGourd:Things/Item/Resource/PlantFoodRaw/Corn: the game serves Things/Item/Resource/PlantFoodRaw/Corn  |
| `dregen_RM_VeilFallIncoming_Meteorite_v1` | 429 | DONOR | RM_VeilFallIncoming:Things/Skyfaller/Meteorite: the game serves Things/Skyfaller/Meteorite from ludeon.rimworl |
| `dregen_RM_VenomPool_Grainy_v1` | 429 | DONOR | RM_VenomPool:Things/Filth/Grainy: the game serves Things/Filth/Grainy from ludeon.rimworld.core (VANILLA) |
| `dregen_RM_VentReagent_Neutroamine_v1` | 429 | DONOR | RM_VentReagent:Things/Item/Resource/Neutroamine: the game serves Things/Item/Resource/Neutroamine from ludeon. |
| `dregen_RM_WasteCaskBay_Shelf_v1` | 429 | DONOR | RM_WasteCaskBay:Things/Building/Furniture/Shelf: the game serves Things/Building/Furniture/Shelf from ludeon.r |
| `dregen_RM_WaveglassShard_Steel_v1` | 429 | DONOR | RM_WaveglassShard:Things/Item/Resource/Steel: the game serves Things/Item/Resource/Steel from ludeon.rimworld. |
| `dregen_RM_Webwork_Web_RMWebworkWeb_v1` | 429 | PLACEHOLDER | src/RimMandrake/Webwork/Textures/Things/Building/Natural/RM_Webwork_Web.png: placeholder (allowlist/ledger) |
| `dregen_RM_WindVaporatorWreck_MoisturePump_v1` | 429 | DONOR | RM_WindVaporatorWreck:Things/Building/Misc/MoisturePump: the game serves Things/Building/Misc/MoisturePump fro |
| `dregen_RM_WollickTuber_Potatoes_v1` | 429 | DONOR | RM_WollickTuber:Things/Item/Resource/PlantFoodRaw/Potatoes: the game serves Things/Item/Resource/PlantFoodRaw/ |
| `dregen_RM_ZisskaMeat_MeatSmall_v1` | 429 | DONOR | RM_ZisskaMeat:Things/Item/Resource/MeatFoodRaw/Meat_Small: the game serves Things/Item/Resource/MeatFoodRaw/Me |
| `dregen_RSW_Acklay_AcklayA_v1_east` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Acklay/AcklayA_east.png: ledger variant 096eb0ec313090e77596 don |
| `dregen_RSW_Acklay_AcklayA_v1_north` | derived | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Acklay/AcklayA_north.png: ledger variant 521fd1e1fe67459c5a3f do |
| `dregen_RSW_Acklay_AcklayA_v1_south` | derived | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Acklay/AcklayA_south.png: ledger variant 1739ef5a44f8fd6d7a59 do |
| `dregen_RSW_Acklay_AcklayDessicated_v1` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Acklay/Acklay_Dessicated.png: ledger variant 9ee6b3af58dc77b5ec1 |
| `dregen_RSW_Acklay_AcklaySwimming_v1_east` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Acklay/Acklay_Swimming_east.png: ledger variant eff53949ff3549b3 |
| `dregen_RSW_Acklay_AcklaySwimming_v1_north` | derived | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Acklay/Acklay_Swimming_north.png: ledger variant 0820c4a746cadc8 |
| `dregen_RSW_Acklay_AcklaySwimming_v1_south` | derived | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Acklay/Acklay_Swimming_south.png: ledger variant de148e5a8083763 |
| `dregen_RSW_Akk_AkkDessicated_v1` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Akk/Akk_Dessicated.png: ledger variant 541726cf6f1cc770df01 dono |
| `dregen_RSW_Devourers_DevourerDessicated_v1` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Devourer/Devourer_Dessicated.png: ledger variant 9876e990f3addfe |
| `dregen_RSW_Dianoga_DianogaDessicated_v1` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Dianoga/Dianoga_Dessicated.png: ledger variant e9634a74fd7b84391 |
| `dregen_RSW_Dianoga_DianogaSwimming_v1_east` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Dianoga/Dianoga_Swimming_east.png: ledger variant 873a3cac2f5c4e |
| `dregen_RSW_Dianoga_DianogaSwimming_v1_north` | derived | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Dianoga/Dianoga_Swimming_north.png: ledger variant 60943223c995e |
| `dregen_RSW_Dianoga_DianogaSwimming_v1_south` | derived | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Dianoga/Dianoga_Swimming_south.png: ledger variant 75e4ad05584a2 |
| `dregen_RSW_FrogDog_FrogDog_v1_north` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/FrogDog/FrogDog_north.png: ledger variant 1271c9fd874d6e12a3cb d |
| `dregen_RSW_Gullipud_Gullipudi_v1_east` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Gullipud/Gullipud_i_east.png: ledger variant 3a7b37b7d6091f004b7 |
| `dregen_RSW_Gullipud_GullipudjDessicated_v1` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Gullipud/Gullipud_j_Dessicated.png: ledger variant 253b1afa55701 |
| `dregen_RSW_IthorianReek_ReekDessicated_v1` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Reek/Reek_Dessicated.png: ledger variant 6e777600fa1a2ecad1c5 do |
| `dregen_RSW_IthorianReek_ReekjDessicated_v1` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Reek/Reek_j_Dessicated.png: ledger variant 4029019d4678eb7a1b54  |
| `dregen_RSW_Jerba_Bantha_v1_east` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Bantha/Bantha_east.png: ledger variant 774e819e6d09218ce980 dono |
| `dregen_RSW_Jerba_Bantha_v1_north` | derived | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Bantha/Bantha_north.png: ledger variant e158d7303367b3956136 don |
| `dregen_RSW_Jerba_Bantha_v1_south` | derived | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Bantha/Bantha_south.png: ledger variant 0a4c4a09363dfd94aab9 don |
| `dregen_RSW_Jerba_DessicatedDromedary_v1_east` | 429 | DONOR | RSW_Jerba:Things/Pawn/Animal/Dromedary/Dessicated_Dromedary_east: the game serves Things/Pawn/Animal/Dromedary |
| `dregen_RSW_Jerba_DessicatedDromedary_v1_north` | derived | DONOR | RSW_Jerba:Things/Pawn/Animal/Dromedary/Dessicated_Dromedary_north: the game serves Things/Pawn/Animal/Dromedar |
| `dregen_RSW_Jerba_DessicatedDromedary_v1_south` | derived | DONOR | RSW_Jerba:Things/Pawn/Animal/Dromedary/Dessicated_Dromedary_south: the game serves Things/Pawn/Animal/Dromedar |
| `dregen_RSW_Mastmot_MastmotjDessicated_v1` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Mastmot/Mastmot_j_Dessicated.png: ledger variant 386342edbcc4fe6 |
| `dregen_RSW_Raxshir_RaxshirDessicated_v1` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Raxshir/Raxshir_Dessicated.png: ledger variant 1391a1e9faadeea76 |
| `dregen_RSW_Torton_Tortonf_v1_south` | 429 | DONOR | src/RimStarWars/SWBestiary/Textures/swanimals/Torton/Torton_f_south.png: ledger variant 4fd282911014bfda855c d |
| `dregen_RUT_BoughSoil_SoilRich_v1` | 429 | DONOR | RUT_BoughSoil:Terrain/Surfaces/SoilRich: the game serves Terrain/Surfaces/SoilRich from regrowth.botr.core (VA |
| `dregen_RUT_Boughway_WoodFloor_v1` | 429 | DONOR | RUT_Boughway:Terrain/Surfaces/WoodFloor: the game serves Terrain/Surfaces/WoodFloor from ludeon.rimworld.core  |
| `dregen_RUT_DigShaft_DeepDrill_v1` | 429 | DONOR | RUT_DigShaft:Things/Building/Production/DeepDrill: the game serves Things/Building/Production/DeepDrill from l |
| `dregen_RUT_FeverWoodMirrorPool_WaterDeepRamp_v1` | 429 | DONOR | RUT_FeverWoodMirrorPool:Terrain/Surfaces/WaterDeepRamp: the game serves Terrain/Surfaces/WaterDeepRamp from lu |
| `dregen_RUT_ScaldWaterMovingShallow_WaterShallowRamp_v1` | 429 | DONOR | RUT_ScaldWaterMovingShallow:Terrain/Surfaces/WaterShallowRamp: the game serves Terrain/Surfaces/WaterShallowRa |
| `dregen_RUT_ScaldWaterOceanDeep_WaterDeepRamp_v1` | 429 | DONOR | RUT_ScaldWaterOceanDeep:Terrain/Surfaces/WaterDeepRamp: the game serves Terrain/Surfaces/WaterDeepRamp from lu |
| `dregen_RUT_ScaldWaterShallow_WaterShallowRamp_v1` | 429 | DONOR | RUT_ScaldWaterShallow:Terrain/Surfaces/WaterShallowRamp: the game serves Terrain/Surfaces/WaterShallowRamp fro |

### Refused: 36

| job | class | why |
|---|---|---|
| `dregen_RM_ContagionMulch_Kibble_v1` | REFUSED_REGEN | a render is bound to RM_ContagionMulch at things/item/resource/kibble (binding 8ceeaa8df254718e7f0b job kit_contagionmulch_v1) |
| `dregen_RM_Dripfringe_RMDripfringeb_v1` | REFUSED_REGEN | src/RimMandrake/WeepingStones/Textures/Things/Plant/RM_Dripfringe/RM_Dripfringe_b.png: bytes are a render of ours (ledger variant  |
| `dregen_RM_FlakespireFungus_Flakespirefungusa_v1` | REFUSED_REGEN | src/RimMandrake/TheRot/Textures/RotSporeKit/Things/Plant/FlakespireFungus/Flakespirefungus_a.png: bytes are a render of ours (ledg |
| `dregen_RM_FogWater_Beer_v1` | REFUSED_REGEN | a render is bound to RM_FogWater at things/item/drug/beer (binding c919f05ca87a9f79e1d1 job kit_fogwater_v1) |
| `dregen_RM_GlassVeilKelp_RMGlassVeilKelpA_v1` | REFUSED_REGEN | src/RimMandrake/TerminalBiomes/Textures/Things/Plant/RM_GreySea/RM_GlassVeilKelp/RM_GlassVeilKelp_A.png: bytes are a render of our |
| `dregen_RM_GloomcastMeat_MeatSauriana_v1` | REFUSED_REGEN | src/RimStarWars/SWBestiary/Textures/swresource/Meat_Saurian/Meat_Saurian_a.png: bytes are a render of ours (ledger variant ef2435e |
| `dregen_RM_GloomcastMeat_MeatSaurianb_v1` | REFUSED_REGEN | src/RimStarWars/SWBestiary/Textures/swresource/Meat_Saurian/Meat_Saurian_b.png: bytes are a render of ours (ledger variant 7889e24 |
| `dregen_RM_GloomcastMeat_MeatSaurianc_v1` | REFUSED_REGEN | src/RimStarWars/SWBestiary/Textures/swresource/Meat_Saurian/Meat_Saurian_c.png: bytes are a render of ours (ledger variant d09cca2 |
| `dregen_RM_GlowGlobe_RMGlowGlobea_v1` | REFUSED_REGEN | src/RimMandrake/Abyss/Textures/RM_Abyss/Things/Plant/RM_GlowGlobe/RM_GlowGlobe_a.png: bytes are a render of ours (ledger variant d |
| `dregen_RM_Greatbole_RMGreatboleaa_v1` | REFUSED_REGEN | src/RimMandrake/Greentide/Textures/Things/Plant/RM_Greatbole/RM_Greatbole_a/RM_Greatbole_a_a.png: bytes are a render of ours (ledg |
| `dregen_RM_HumPrimer_SchematicOpen_v1` | REFUSED_REGEN | a render was registered at Things/Item/Book/RM_HumPrimer/RM_HumPrimer (ledger variant 237dde553ff4d4340297 kind=artpipe job=dregen |
| `dregen_RM_HumPrimer_SchematicVertical_v1` | REFUSED_REGEN | a render was registered at Things/Item/Book/RM_HumPrimer/RM_HumPrimer (ledger variant 237dde553ff4d4340297 kind=artpipe job=dregen |
| `dregen_RM_Kaddrath_RMKaddrathaa_v1` | REFUSED_REGEN | src/RimMandrake/Greentide/Textures/Things/Plant/RM_Kaddrath/RM_Kaddrath_a/RM_Kaddrath_a_a.png: bytes are a render of ours (ledger  |
| `dregen_RM_Lanternstone_Medium_A_v1` | REFUSED_REGEN | src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Crystals/LanternstoneMedium/A.png: bytes are a render of ours (ledger |
| `dregen_RM_Lanternstone_Medium_B_v1` | REFUSED_REGEN | src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Crystals/LanternstoneMedium/B.png: bytes are a render of ours (ledger |
| `dregen_RM_LungerFry_v1` | REFUSED_REGEN | src/RimMandrake/Greentide/Textures/Things/Item/Fish/RM_LungerFry.png: bytes are a render of ours (ledger variant ba14e8321143cd937 |
| `dregen_RM_Masonmat_RMMasonmatA_v1` | REFUSED_REGEN | src/RimMandrake/TerminalBiomes/Textures/Things/Plant/RM_GreySea/RM_Masonmat/RM_Masonmat_A.png: bytes are a render of ours (ledger  |
| `dregen_RM_Mournweft_RMMournweftA_v1` | REFUSED_REGEN | src/RimMandrake/TerminalBiomes/Textures/Things/Plant/RM_GreySea/RM_Mournweft/RM_Mournweft_A.png: bytes are a render of ours (ledge |
| `dregen_RM_Murkblush_RMMurkblushA_v1` | REFUSED_REGEN | src/RimMandrake/TerminalBiomes/Textures/Things/Plant/RM_GreySea/RM_Murkblush/RM_Murkblush_A.png: bytes are a render of ours (ledge |
| `dregen_RM_Nemmer_RMNemmeraa_v1` | REFUSED_KEPT | src/RimMandrake/Greentide/Textures/Things/Plant/RM_Nemmer/RM_Nemmer_a/RM_Nemmer_a_a.png: owner keep 3dbddd5be126cec247e5 via art i |
| `dregen_RM_Plant_Bellows_RMBellowsa_v1` | REFUSED_REGEN | src/RimMandrake/GelatinousSlime/Textures/Things/Plant/RM_Bellows/RM_Bellows/RM_Bellows_a.png: bytes are a render of ours (ledger v |
| `dregen_RM_PrennaLace_A_v1` | REFUSED_UNCONFIRMED | src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Plant/PrennaLace/PrennaLaceGrown/A.png: sha 8cad3faee8de has no donor |
| `dregen_RM_QuorrFern_A_v1` | REFUSED_UNCONFIRMED | src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Plant/QuorrFern/A.png: sha f74dfa6ca42e has no donor/placeholder prov |
| `dregen_RM_Rockfinger_RMRockfingerb_v1` | REFUSED_REGEN | src/RimMandrake/WeepingStones/Textures/Things/Plant/RM_Rockfinger/RM_Rockfinger_b.png: bytes are a render of ours (ledger variant  |
| `dregen_RM_RustPuff_RustPuffA_v1` | REFUSED_REGEN | src/RimMandrake/TheRot/Textures/RotSporeKit/Things/Plant/RustPuff/RustPuff_A.png: bytes are a render of ours (ledger variant 36388 |
| `dregen_RM_SaltBladeGrey_RMSaltBladeGreyA_v1` | REFUSED_REGEN | src/RimMandrake/TerminalBiomes/Textures/Things/Plant/RM_GreySea/RM_SaltBladeGrey/RM_SaltBladeGrey_A.png: bytes are a render of our |
| `dregen_RM_SaltBladeTwilight_RMSaltBladeTwilightA_v1` | REFUSED_REGEN | src/RimMandrake/TerminalBiomes/Textures/Things/Plant/RM_GreySea/RM_SaltBladeTwilight/RM_SaltBladeTwilight_A.png: bytes are a rende |
| `dregen_RM_Sarquin_RMSarquinab_v1` | REFUSED_REGEN | src/RimMandrake/Greentide/Textures/Things/Plant/RM_Sarquin/RM_Sarquin_a/RM_Sarquin_a_b.png: bytes are a render of ours (ledger var |
| `dregen_RM_ScorchedStars_RMScorchedStarsa_v1` | REFUSED_UNCONFIRMED | src/RimMandrake/Scarlands/Textures/Things/Plant/RM_ScorchedStars/RM_ScorchedStars_a.png: sha f86624c57933 has no donor/placeholder |
| `dregen_RM_SpunstoneHull_GravshipHullAtlas_v1` | REFUSED_REGEN | RM_SpunstoneHull no longer draws Things/Building/Linked/GravshipHull/GravshipHull_Atlas: renamed — RM_SpunstoneHull now draws src/ |
| `dregen_RM_TwitchingPuffer_a_v1` | REFUSED_UNCONFIRMED | src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Plant/TwitchingPuffer/PufferGrown/a.png: sha df997c12f650 has no dono |
| `dregen_RM_VellokReed_A_v1` | REFUSED_UNCONFIRMED | src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Plant/VellokReed/A.png: sha 3d2b7dd2ce4c has no donor/placeholder pro |
| `dregen_RM_VexxithDoor_DoorSimpleMover_v1` | REFUSED_REGEN | RM_VexxithDoor no longer draws Things/Building/Door/DoorSimple_Mover: renamed — RM_VexxithDoor now draws src/RimMandrake/Cauldron/ |
| `dregen_RM_WindVaporator_MoisturePump_v1` | REFUSED_REGEN | a render is bound to RM_WindVaporator at things/building/misc/moisturepump (binding bd17bb557628ba29304f job kit_windvaporator_v1) |
| `dregen_RM_Wrinklecap_WrinklecapA_v1` | REFUSED_REGEN | src/RimMandrake/TheRot/Textures/RotSporeKit/Things/Plant/Wrinklecap/Wrinklecap_A.png: bytes are a render of ours (ledger variant 7 |
| `dregen_RM_ZivvitTaper_A_v1` | REFUSED_UNCONFIRMED | src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Plant/ZivvitTaper/A.png: sha 573465a45520 has no donor/placeholder pr |

## Destinations that could not be classified (REFUSED_UNCONFIRMED, job lists)

| row | why |
|---|---|
| `dregen_RM_PrennaLace_A_v1` | src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Plant/PrennaLace/PrennaLaceGrown/A.png: sha 8cad3faee8de has no donor/placeholder provena |
| `dregen_RM_QuorrFern_A_v1` | src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Plant/QuorrFern/A.png: sha f74dfa6ca42e has no donor/placeholder provenance in the ledger |
| `dregen_RM_ScorchedStars_RMScorchedStarsa_v1` | src/RimMandrake/Scarlands/Textures/Things/Plant/RM_ScorchedStars/RM_ScorchedStars_a.png: sha f86624c57933 has no donor/placeholder provenance in the l |
| `dregen_RM_TwitchingPuffer_a_v1` | src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Plant/TwitchingPuffer/PufferGrown/a.png: sha df997c12f650 has no donor/placeholder proven |
| `dregen_RM_VellokReed_A_v1` | src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Plant/VellokReed/A.png: sha 3d2b7dd2ce4c has no donor/placeholder provenance in the ledge |
| `dregen_RM_ZivvitTaper_A_v1` | src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things/Plant/ZivvitTaper/A.png: sha 573465a45520 has no donor/placeholder provenance in the ledg |
