"""Explicit def-name overrides for l1_batch_manifest.py.

Key: (item id, criterion id). Every row here replaces the generator's token-matching guess (criterion text, then
item prose) with names a human read the item, the building commits and src/ to establish. The generator still
CHECKS every name against the src/ XML index and reports any name src/ does not contain as a build defect --
an override never makes a missing def pass.

Spec fields (all optional):
  defs      ["Name" | "DefType/Name"]   names that must exist in src/ (a bare name with two def types in src/ must
                                        be written DefType/Name, otherwise the row is flagged ambiguous)
  external  ["DefType/Name"]            vanilla / DLC / donor defs the criterion needs that src/ cannot hold.
                                        Never verified offline: reported UNMEASURED-OFFLINE, resolved by the live read.
  files     ["src/.../File.xml"]        every top-level defName in these files
  dirs      ["src/.../Defs"]            every defName under these directories
  child     "surfaceLook"               with files/dirs: keep only defs carrying this child element
  patch_targets "src/.../Patch.xml"     every  Defs/Type[defName="X"]  xpath target in this patch file
  derive    "sea"                       special derivation (see l1_batch_manifest.derive_sea)
  note      free text carried into the report (what is NOT a def, what is stale, what is owed live)
  no_defs   True                        the item authored NO def for this criterion: reported, never papered over
"""

OVERRIDES = {
    # ---- 1 criterion naming a def missing from src/ -------------------------------------------------
    ("UTINNI_WORLDMAP_FLIGHT_ICON_1", "A1"): dict(
        defect="The one criterion naming a name absent from src/ (RUT_Utinni) was a texture folder, not a def, so no def is missing. Real defect on record: commit df9370e09 found the deployed icon patch is NOT rendering live.",
        defs=[],
        external=["WorldObjectDef/Gravship"],
        note="`RUT_Utinni` is a TEXTURE name (Textures/World/WorldObjects/Expanding/RUT_Utinni.png and "
             "World/WorldObjects/RUT_UtinniCaravan.png, both on disk), never a def. The only def is vanilla/Odyssey "
             "WorldObjectDef/Gravship, patched by src/RimUtinni/UtinniPatches/Patches/UtinniWorldIcon.xml. Live read "
             "must check expandingIconTexture and texture on Gravship. Commit df9370e09 already recorded that the "
             "deployed patch was NOT rendering live."),

    # ---- 10 criteria with no def name found -----------------------------------------------------------
    ("PYRINTH_FIRST_SCRIPT_1", "A2"): dict(
        dirs=["src/RimMandrake/Pyrinth/Defs"],
        note="The script's defs_resolve bar reads every def parsed from the mod's own XML; this is that set. "
             "validation.py itself says a live read cannot tell this dormant pack from the donor det.epochspyrinth."),
    ("SURFACE_RIVER_WEIRS_1", "A1"): dict(
        defs=["RM_BankWeir", "RM_SiltTrap", "RM_BankStake", "RM_FerryPost",
              "RimMandrake.FlowWorks.Rivers.RM_RiverDriftDef/RM_RiverDrift_Temperate",
              "RimMandrake.FlowWorks.Rivers.RM_RiverDriftDef/RM_RiverDrift_Wetland",
              "RimMandrake.FlowWorks.Rivers.RM_RiverDriftDef/RM_RiverDrift_Cold",
              "RimMandrake.FlowWorks.Rivers.RM_RiverDriftDef/RM_RiverDrift_Arid",
              "RimMandrake.FlowWorks.Rivers.RM_RiverDriftDef/RM_RiverDrift_Tropical",
              "TerrainDef/RM_FordStones"],
        note="River Works was merged into FlowWorks (409d1f57c): the defs live in src/RimMandrake/FlowWorks/Defs/Rivers/, "
             "and the old src/RimMandrake/RiverWorks folder is gone. The LEVEE is the continuous RM_BankStake line "
             "(RM_BankWorks.xml: 'a continuous line of them holds back a flood like a levee'); no def is named levee. "
             "Drift is five RM_RiverDriftDef rows whose DefType is a namespaced class, so confirm get_defs accepts that spelling."),
    ("CAULDRON_ENRICHMENT_VISUALS_1", "A1"): dict(
        defect="A1 asks for the flora-accent dew defs; src/ holds no def or XML modExtension for dewfall saturation (RM_DewfallGraphicExtension is C#-only, dormant pending dew art and the owner's accent-plant pick). Only 3 of the 4 named things have a def anchor. Build gap for the saturation half, not a typo.",
        defs=["ThingDef/RM_Filth_DewBeads", "ThingDef/RM_TwistingThornwood", "ThingDef/RM_TreeMartyr",
              "ThingDef/RM_Vexxiss"],
        note="Only the bead is a standalone def. Assay flecks = RM_AssayFlecksExtension on RM_TwistingThornwood and RM_TreeMartyr "
             "(modExtension, overlay art owed so dormant). Vexxiss prints = code (RM_VexxissPrints.cs) hung off RM_CompVexxissBehaviour "
             "on RM_Vexxiss, no print def. Flora-accent dew variant: NO def and NO XML extension exists in src/ (RM_DewfallGraphicExtension "
             "is C# only, 'DORMANT, no XML ext added' per Transient/cauldron_visuals_20261006.md), so that quarter of the criterion "
             "has nothing to resolve. See BUILD DEFECTS."),
    ("LIQUID_INDUSTRY_SETPIECES_1", "A1"): dict(
        defs=["RM_DesalPlant_Wrecked", "RM_DesalPlant_Kludged", "RM_DesalPlant_Repaired",
              "RM_DetoxWorks_Wrecked", "RM_DetoxWorks_Kludged", "RM_DetoxWorks_Repaired",
              "RM_TarRefinery_Wrecked", "RM_TarRefinery_Kludged", "RM_TarRefinery_Repaired",
              "RM_PumpingStation_Wrecked", "RM_PumpingStation_Kludged", "RM_PumpingStation_Repaired"],
        note="Twelve tier defs (4 machines x Wrecked/Kludged/Repaired). Each machine also has a *_RuinScatter def, not asked for here."),
    ("WRECKED_DISTILLATION_MODULE_1", "A1"): dict(
        defs=["RM_WM_Distillation_Wrecked", "RM_WM_Distillation_Kludged", "RM_WM_Distillation_Repaired"],
        note="These three exist ONLY as PatchOperationAdd values in WreckedMachines/Patches/WreckedMachines_DistillationModule.xml, "
             "guarded by PatchOperationFindMod 'RimMandrake: FlowWorks'. They resolve live only when FlowWorks is in the list."),
    ("FORGE_WHITE_PLUME_FRONTS_1", "A2"): dict(
        defect="A2 names 'the plume-front defs'; the build authored none (code plus six settings only). Criterion/build mismatch: either re-word A2 to a settings read or build the defs the criterion expects.",
        no_defs=True,
        note="The plume-front build (09ccb3ca5) is C# + Mod Settings only: RM_MapComponent_PlumeFronts, RM_ForgePlumeFronts.cs, six "
             "settings (plumeFrontsEnabled, plumeObscureEnabled, plumeSoakEnabled, plumeHeatEnabled, plumeAdaptedExempt, plumeStrength). "
             "It authors NO def; the only defs it touches are vanilla (Filth_Water, GasType.BlindSmoke is an enum). The criterion's 'plume-front "
             "defs' do not exist. Re-word A2 as a settings read (the six names above) before a live round."),
    ("FLOWWORKS_VISUAL_PRINCIPLES_1", "A1"): dict(
        files=["src/RimMandrake/FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml"],
        child="surfaceLook",
        patch_targets="src/RimMandrake/FlowWorks/Patches/LiquidTypes/RM_FluidSurfaceLooks.xml",
        note="Fifteen LiquidDefs carry surfaceLook inline; FluidDefs (oil, poison, blood, chemfuel, astrofuel) get it by patch. "
             "DefType spellings are namespaced classes; confirm what get_defs accepts."),
    ("FORCE_DISTURBANCE_REFLAVOR_1", "A1"): dict(
        patch_targets="src/RimStarWars/StarWarsPatches/Patches/PsychicToForceDisturbance.xml",
        note="Every target is a vanilla/DLC/donor def (PsychicDrone, PsychicSoothe, PsychicEmanatorShipPartCrash, PsychicDroner, "
             "PsychicSuppression and VEE_* donor rows), so none is in src/. They are UNMEASURED offline by construction; "
             "VEE_* only exist if that donor is loaded."),
    ("GRAVSHIP_ACOUSTIC_SCANNER_1", "A1"): dict(
        defs=["ThingDef/RM_AcousticSounder", "ResearchProjectDef/RM_AcousticSounding",
              "BiomeDef/RM_FloodedCanyon", "BiomeDef/RM_Stillsand", "BiomeDef/RUT_CrackedLands"],
        note="Every BiomeDef defined in src/ (62) carries the payload extension by a FindMod-guarded patch; "
             "AcousticScanner/validation.py static_checks fails on any owned BiomeDef without one. The three listed are the live-probe biomes."),
    ("THE_SUMP_FIRST_SCRIPT_1", "A2"): dict(
        defect="A2's premise ('35 DEPLOY_HOLD held defs') is stale: all TheSump holds were lifted 2026-10-03, so 0 defs are held now. Not a missing def; the criterion needs re-wording.",
        files=["src/RimMandrake/TheSump/Defs/ThingDefs_Plants/RM_SumpFlora.xml",
               "src/RimMandrake/TheSump/Defs/ThingDefs_Items/RM_SumpFloraItems.xml",
               "src/RimMandrake/TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml",
               "src/RimMandrake/TheSump/Defs/ThingDefs_Buildings/RUT_BeastBulge.xml",
               "src/RimMandrake/TheSump/Defs/MapGeneration/RUT_SumpTarBeastGenStep.xml",
               "src/RimMandrake/TheSump/Defs/ThingDefs_Misc/RUT_Filth_MouseTrack.xml",
               "src/RimMandrake/TheSump/Defs/ThingDefs_Buildings/RUT_MoatFusePost.xml",
               "src/RimMandrake/TheSump/Defs/BiomeDefs/RM_TheSump_Biome.xml"],
        note="STALE PREMISE: src/DEPLOY_HOLD.txt has no active TheSump line (the 11 holds were lifted 2026-10-03, comment at its "
             "line 443), so no def is 'held' now. These eight files are the former hold group (9+3+18+1+1+1+1+1 = 35 defs, the "
             "criterion's number). Re-word A2 as 'every TheSump def resolves'."),

    # ---- 15 prose-derived rows ------------------------------------------------------------------------
    ("SCALD_WATER_AGITATION_FLECKS_1", "A1"): dict(
        defs=["RUT_ScaldMargin", "RUT_ScaldWaterDeep", "RUT_ScaldWaterShallow", "RUT_ScaldWaterOceanDeep",
              "RUT_ScaldWaterOceanShallow", "RUT_ScaldWaterMovingChestDeep", "RUT_ScaldWaterMovingShallow"],
        note="Agitation 'tags' (RM_WaterAgitationLight / RM_WaterAgitationHeavy) are terrainTags on the terrains, and the 'setting defs' "
             "are Mod Settings fields; neither is a def. Check the tags with a terrain field read, not get_defs presence. "
             "The three wreck defs (RUT_ScaldWreck*) belong to the shadow fix, not this criterion's wording."),
    ("VAULT_THAW_QUEST_FAMILY_1", "A1"): dict(
        defs=["QuestScriptDef/RUT_VaultThaw_V1_RustCathedral", "QuestScriptDef/RUT_VaultThaw_V2_Scorch",
              "QuestScriptDef/RUT_VaultThaw_V3_FallLine", "QuestScriptDef/RUT_VaultThaw_V4_Deadstone",
              "QuestScriptDef/RUT_VaultThaw_V5_Slough", "QuestScriptDef/RUT_VaultThaw_V6_Umbra",
              "QuestScriptDef/RUT_VaultClaimConflict", "QuestScriptDef/RUT_Reclamation"],
        note="Exactly the eight QuestScriptDefs, in src/RimUtinni/StructureInjectionsRUT/Defs/VaultDungeons/QuestScriptDefs/RUT_VaultThaw.xml "
             "(the item prose says src/RimUtinni/VaultDungeons/, which is stale)."),
    ("GREENTIDE_BASE_PORT_BUILD_1", "A2"): dict(
        defs=["WeatherDef/RM_RoilWeather", "WeatherDef/RM_BreaklightClear",
              "GameConditionDef/RM_RoilLock", "GameConditionDef/RM_BreaklightCondition",
              "IncidentDef/RM_Breaklight", "IncidentDef/RM_GreatboleFruitfall", "IncidentDef/RM_SteamDevilAppears",
              "HediffDef/RM_DryAirAversion",
              "ThingDef/RM_DryAirBlower", "ThingDef/RM_GreatboleHeartwood", "ThingDef/RM_GreatboleCore",
              "ThingDef/RM_GreatboleTrunkSegment", "ThingDef/RM_GreatboleDeadHusk", "ThingDef/RM_SteamDevil",
              "TerrainDef/RM_RootCauseway"],
        note="The 17 typed names are copied from the item's own ## criteria list (foundCount must equal 17)."),
    ("WASTELAND_MECHANICS_BUILD_1", "A1"): dict(
        defs=["WeatherDef/RM_WastelandAshStorm", "WeatherDef/RM_WastelandRadiationHalo", "WeatherDef/RM_WastelandPlasmaStorm",
              "ThingDef/RM_Sloghog", "PawnKindDef/RM_Sloghog", "ThingDef/RM_Sootgrazer", "PawnKindDef/RM_Sootgrazer",
              "ThingDef/RM_Smolderback", "PawnKindDef/RM_Smolderback", "ThingDef/RM_ContaminantBezoar",
              "ThingDef/RM_VitrifiedBezoar", "ThingDef/RM_SootBrick", "ThingDef/RM_Cinderfelt", "ThingDef/RM_Middenshell"],
        note="Built defs for the item's four mechanics. The Middenshell def exists but the ruled 20-cell width exceeds the engine's 4x4 "
             "footprint (FOUNDRY note 2026-09-30, owner call); RM_WastelandPlasmaStorm is 'def only, UNWIRED'. Presence is not function."),
    ("SCARLANDS_MECHANICS_2", "A1"): dict(
        defs=["HediffDef/RUT_ScarlandsMark", "GameConditionDef/RUT_ScarlandsMarkLock", "HediffDef/RUT_ScariaIncubation",
              "GameConditionDef/RUT_ScariaOnsetArming", "DutyDef/RUT_SentinelDefend", "ThingDef/RUT_SentinelGraveWard"],
        note="The criterion text is cut in the queue view ('... sentinel defs wit...'). No Sentinel PawnKindDef exists in src/; "
             "RUT_SentinelGraveWard (a ThingDef) is the only sentinel body. If the full criterion wants a sentinel kind, that is absent."),
    ("STILLSAND_PRECIOUS_CAVES_LIVE_1", "A1"): dict(
        defs=["BiomeDef/RM_Stillsand", "GenStepDef/RM_PreciousCaveCarve", "GenStepDef/RM_PreciousCaveContents",
              "RimMandrake.Stillsand.RM_PreciousCaveDef/RM_PreciousCave_GuzzkaLair",
              "RimMandrake.Stillsand.RM_PreciousCaveDef/RM_PreciousCave_LensGrotto",
              "RimMandrake.Stillsand.RM_PreciousCaveDef/RM_PreciousCave_SealedCache",
              "RimMandrake.Stillsand.RM_PreciousCaveDef/RM_PreciousCave_Seep",
              "RimMandrake.Stillsand.RM_PreciousCaveDef/RM_PreciousCave_Taken"],
        note="Two genstep defs plus the five RM_PreciousCaveDef rows; the biome carries the genstep via extraGenSteps (patch RM_PreciousCaves_BiomeGenSteps.xml). "
             "Four more cave rows live in the RSW_/RUT_ tiers and are not asked for on the minimal list."),
    ("WARSCAR_RAINBOW_POOLS_1", "A1"): dict(
        defs=["ThingDef/RM_BloomLiquor", "ThingDef/RM_DielectricGel", "ThingDef/RM_Etchant", "ThingDef/RM_MedicalCoagulant",
              "RimMandrake.FlowWorks.LiquidTypes.LiquidDef/RM_Liquid_ReactionLiquor"],
        note="Four reagent items plus the registry row. RM_ReactionPool/RM_ReactionTap/RM_ReactionPools genstep exist too but are not 'reagent defs'. "
             "The earlier prose-derived list wrongly included RM_GlowerCrust."),
    ("WYYYSCHOKK_FANG_PENDANT_1", "A1"): dict(
        defs=["ThingDef/RSW_WyyyschokkFang", "ThingDef/RSW_Apparel_FangPendant", "RecipeDef/RSW_Make_FangPendant",
              "ThoughtDef/RSW_TrophyCraft_ObserverBraveFang"],
        note="One recipe exists (criterion says 'recipes'). The thought's workerClass RSW_ThoughtWorker_ObserverFactionApparel is C#, so the "
             "worker resolving is a ThoughtDef load, not a def lookup."),
    ("WARSCAR_TOTCHAK_WAKES_1", "A1"): dict(
        defs=["GenStepDef/RM_TotchakInWall", "JobDef/RM_TotchakGnaw", "JobDef/RM_TotchakLieDown", "ThinkTreeDef/RM_Totchak"],
        note="CORRECTED: the prose-derived name RUT_SealedSleeper was the wrong creature (the sealed sleeper, not the totchak). "
             "The lie-down 'giver' is a JobGiver C# class reached via the think tree (ThinkTreeDef RM_Totchak, file RM_ThinkTree_Totchak.xml); the def is JobDef RM_TotchakLieDown."),
    ("RUST_CATHEDRAL_MECHANICS_1", "A1"): dict(
        dirs=["src/RimMandrake/RustCathedral/Defs"],
        note="CORRECTED: the shipping mod is src/RimMandrake/RustCathedral (RM_ tier); the prose-derived RUT_CathedralRoach/RUT_ScarRoach/RUT_RustCathedral "
             "are the RimUtinni twins and not what 'all RustCathedral defs' means. The twin roaches live in src/RimUtinni/RustCathedralRoaches."),
    ("FOOTPRINT_TRACK_GRID_1", "A2"): dict(
        patch_targets="src/RimMandrake/Stillsand/Patches/RM_TrackSurface_Stillsand.xml",
        defs=["BiomeDef/RM_Stillsand"],
        note="The patch adds RM_TrackSurfaceExtension to vanilla TerrainDef/Sand and to RM_DeepSand. Vanilla Sand is external (UNMEASURED offline)."),
    ("SEA_FISHABLES_ALIVE_IN_DEPTHS_1", "A2"): dict(
        derive="sea",
        body_aliases={"RM_Saal": "RM_Noohm"},  # RM_ScaldFloorFauna.xml line 31: RM_Saal <-> RM_Noohm, catch and body are two names
        note="Derived from the four sea BiomeDefs (RM_GreySea, RM_TwilightSea, RM_TheScald, RM_TheChill): every fishTypes catch plus its living "
             "body from wildAnimals (inline or patch-added). A catch with no living body is a build defect."),
    ("LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1", "A1"): dict(
        defs=["ThingDef/RM_VisslerArm"],
        note="Only the arm item is asked for. 'rottable and ingestible' is a field read on the def, not presence."),
    ("SHIELD_MODS_LEVERAGE_1", "A1"): dict(
        defs=["ThingDef/RUT_ShieldGenerator", "ThingDef/RUT_ShieldModule_Cryo", "ThingDef/RUT_ShieldModule_Particulate",
              "ThingDef/RUT_ShieldModule_Thermal", "ResearchProjectDef/RUT_ModulatedShieldFields"],
        note="The 'four shield fields' are ShieldFieldMode enum values, and the landing advisory / hazard exposure tracker are C# classes "
             "(ShieldLandingAdvisory.cs, ShieldHazardExposureTracker.cs): none is a def, so get_defs cannot show them. They need a state read."),
    ("SUMP_TAR_NASTINESS_1", "A1"): dict(
        defs=["ThingDef/RM_Filth_Tar", "TerrainDef/RM_TarShallow", "HediffDef/RM_Tarred", "RecipeDef/RM_ScrubTarred",
              "ThoughtDef/RM_TarredThought", "ThingDef/RM_Bitumen", "ThingDef/RM_WeakTarSolvent", "ThingDef/RM_StrongTarSolvent",
              "ThingDef/RM_ThrummelSeepwax"],
        note="Nine tar-kit defs under RM_ names. The prose-derived RSW_RemoveBrainWorm / RUT_Hardwood / RUT_Greenwood were noise."),
}
