# Cherry Picker drift keys — SHIP vs LIVE, 2026-09-10

Computed via `cherrypicker.py` (the one parser), never a fresh regex.
SHIP = `infrastructure/state/cherrypicker/CherryPicker.SHIP.xml` (1,509 keys).
LIVE = `Mod_3521312241_Mod_CherryPicker.xml` as of this read (1,972 keys,
file mtime 2026-09-10 15:21 — drift has grown since the item was filed
last night at 1,948).

## REVERSED (in SHIP, un-cut in LIVE) — 178 keys

BackstoryDef: 141
ThingDef: 30
PawnKindDef: 5
TraitDef: 2

### BackstoryDef (141) — full list
RBM_Akabeko, RBM_Alpha, RBM_AnimalGuardian, RBM_BraveGuardian, RBM_CityDweller,
RBM_ClumsyGuardian, RBM_CompassionateGuardian, RBM_CutOfMeat, RBM_ElegantGuardian,
RBM_Feral, RBM_FriendlyGuardian, RBM_Hothead, RBM_HumanFighter, RBM_HumanRancher,
RBM_IllicitGuardian, RBM_IndependentMonarch, RBM_Isolated, RBM_Lab-GrownGuardian,
RBM_Logger, RBM_MazeDweller, RBM_MinotaurCultist, RBM_PiningGuardian,
RBM_Powerhouse, RBM_ProspectiveGuardian, RBM_ProtectedMonarch, RBM_RejectedGuardian,
RBM_RoyalYouth, RBM_Runaway, RBM_SearchingMonarch, RBM_ShowCalf,
RBM_StandardGuardian, RBM_StoicGuardian, RBM_Treasurekeeper, RBM_Veal,
RBM_WildBeast, RBM_Xenohustler (35, source: tug.Minotaur)
REBC118, REBC119, REBC120, REBC121 (4, source: shavius.medieval.flavour)
SH_MED_LandlessKnight, SH_MED_MedievalCommander, SH_MED_MedievalLabourer,
SH_MED_MedievalMason, SH_MED_MedievalRoyalty, SH_MED_MedievalScholar,
SH_MED_PlagueDoctor, SH_MED_ReligiousKnight, SH_MED_RuralLord (9, source:
shavius.medieval.flavour)
VA_MED_Archer, VA_MED_Brave, VA_MED_ConventChild, VA_MED_CountryLordling,
VA_MED_MedievalLordling, VA_MED_MedievalSlave, VA_MED_PoliticalCaptive,
VA_MED_RichKid, VA_MED_RoyalBastard, VA_MED_RoyalMasseuse, VA_MED_ServingBoy,
VA_MED_UnwantedSurvivor, VA_MED_Warrior (13, source: shavius.medieval.flavour)
VQE_ArchiteVolunteer1, VQE_BetrayalStudy21, VQE_BoneReforged6, VQE_BrainProbed8,
VQE_CombatDrills15, VQE_CompassionPunished24, VQE_DeceptionStudy16,
VQE_EnhancedSoldier5, VQE_EyeReplaced10, VQE_FalseFamily22, VQE_GeneFighter3,
VQE_GroupConflict17, VQE_IdealPatient, VQE_IsolationChamber14, VQE_IsolationTest19,
VQE_KidnappedChild, VQE_LossExperiment20, VQE_MilitaryExperiment4,
VQE_MuscleStitched9, VQE_ObedienceTrial18, VQE_PainTolerance13,
VQE_SilenceStudy25, VQE_SkinGrafted7, VQE_StarvationTrial23, VQE_StressTest11,
VQE_ToxicExposure12, VQE_TrialSubject2 (26, source: vanillaquestsexpanded.ancients)
VREA_ArchohavenArchitect, VREA_ArchonCadet, VREA_ArchonChildExplorer,
VREA_ArchonCrystalCarver, VREA_ArchonDimensionalFarmer, VREA_ArchonDreamchild,
VREA_ArchonDreamseer, VREA_ArchonLuminaryApprentice, VREA_ArchonMindweaver,
VREA_ArchonNexusScholar, VREA_ArchonNexusborn, VREA_ArchonNoviceCasterChild,
VREA_ArchonPsyLord, VREA_ArchonStarChild, VREA_ArchonStarwhisperer,
VREA_ArchonStrategyProdigy, VREA_ArchonVoidrunner, VREA_ArchonVoidwalker,
VREA_AstralHunter, VREA_AstralVanguard, VREA_CelestialDiplomat,
VREA_CelestialStrategist, VREA_DimensionalArtisan, VREA_DimensionalNomad,
VREA_DimensionalPhilosopher, VREA_DimensionalSmith, VREA_DimensionalStrategist,
VREA_DimensionalWarden, VREA_EclipsedGeneral, VREA_EltexAlchemist,
VREA_EltexHunter, VREA_EltexScholar, VREA_EtherealAgriculturist,
VREA_EtherealAssassin, VREA_HarmonicArtisan, VREA_HarmonicTuner, VREA_NexusGuard,
VREA_OmnipotentGardener, VREA_StarWhisperer, VREA_StellarAgriculturist,
VREA_StellarCartographer, VREA_VoidFarmer, VREA_VoidHarmonizer,
VREA_VoidHarmonizer2, VREA_VoidMarauder, VREA_VoidMediator, VREA_VoidPhilosopher,
VREA_VoidStrider, VREA_VoidVanguard, VREA_VoidWhisperer, VREA_VoidshieldGuardian,
VREA_WarpBladesman (54, source: vanillaracesexpanded.archon)

### ThingDef (30) — full list
BMAD_GrowthTurret, BMAD_ShrinkTurret, BreadMoAM_Turret_ShotgunTurret,
BreadMoAM_Turret_ShotgunTurretN, DP_MinigunTurret, DeadColumnMod, FT_AutoCannon,
FT_Maxim4M, FT_Turret_Mortar, Grenade_TurretPack, Metalhorror,
ShipWallMountMiniTurret, Trispike, Turret_AncientArmoredTurret,
Turret_AutoMiniTurret, Turret_Autocannon, Turret_MiniTurret, Turret_Mortar,
Turret_TacticalTurret, VFES_Complex_Charge, VFES_Complex_Hmg,
VFES_Complex_Minigun, VFES_Turret_ArmoredTurret, VFES_Turret_ChargeTurret,
VFES_Turret_Concealed, VFES_Turret_MilitaryTurret, VFES_Turret_ShotgunTurret,
VGE_PointDefenseTurret, VQE_AncientShieldedTurret, VulcanTurret

### PawnKindDef (5) — full list
Ghoul, Metalhorror, ShamblerSoldier, ShamblerSwarmer, Trispike

### TraitDef (2) — full list
RBM_Herculean_Trait, VQE_IdealPatient

## ADDED (newly cut in LIVE, not in SHIP) — 620 keys, for reference only
ThingDef 370, ResearchProjectDef 120, RecipeDef 81, PawnKindDef 14,
BackstoryDef 10, HediffDef 8, QuestScriptDef 5, GenStepDef 4, AbilityDef 4,
TerrainDef 4, GeneDef 4, TraitDef 3, SpecialThingFilterDef 2, ThoughtDef 2,
FactionDef 2, ScenarioDef 2, TraderKindDef 1, BiomeDef 1, MainButtonDef 1,
IncidentDef 1, WeatherDef 1, DesignationCategoryDef 1. Overwhelmingly `AM_*`/
`Administer_AM_*` (sarg.alphamechs) — the droid/mech consolidation work; not
investigated further here, not in scope of this question.
