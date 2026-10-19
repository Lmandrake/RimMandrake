"""FlowWorks north-star trial site: the data every other script reads.

Authority: design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md section 3 (site
preparation), 3.9 (preflight), 6 (driver). Item FLOWWORKS_NORTHSTAR_SITE_PREP_1.
Dev tooling: its .py never deploys (deploy_custom_mods.py skips *.py/*.md), but the northstar/ folder's result JSONs,
player_missions_spec.json and review/ DO land in the deployed Mods/FlowWorks/northstar/ (no folder exclusion there).

Holds: the shipped Mod Settings defaults (selftest cross-checks them against the C#),
the plot layout (bar footprint + 8-cell buffer, 12-cell gaps, limitless plots on an
edge, limited plots >= 15 cells in), the per-cell manifest model, the tool census,
the golden-save names, the run-ops parser for the bridge's run-length terrain/roof
reads, and the exact-bytes config backup/restore.
"""
import glob
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_DIR = os.path.dirname(HERE)                                   # src/RimMandrake/FlowWorks
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(MOD_DIR)))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for _p in (UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

PREP_VERSION = "1"                     # bump whenever prep_site.py's output changes
PACKAGE_ID = "mandrake.rm.flowworks"
TIER = "flowworks"
GOLDEN_NAME = "NS_FlowWorks_TrialSite_v1"
REPO_SIDECAR_DIR = os.path.join(ROOT, "infrastructure", "state", "northstar")
DLL_REL = os.path.join("Assemblies", "RimMandrakeFlowWorks.dll")
SEATS = ("BENCH", "FOUNDRY")

# --------------------------------------------------------------------- Mod Settings
# Shipped defaults, MEASURED from every settings class's static initialisers (one key per class below).
# selftest re-reads the C# so this table cannot drift from what ships.
SETTINGS = {
    "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings": {
        "depthEngineEnabled": True, "pulseIntervalTicks": 250.0, "flowPerPulse": 1.0,
        "digToDepthEnabled": True,
        "maxDigDepth": 16.0, "digCostRisesWithDepth": True,   # PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT: 8 m cap; P6 curve
        "liquidCorrosionEnabled": True, "liquidIgnitionEnabled": True,
        "fillInEnabled": True, "fillInDisplacementEnabled": True, "sourceBudgetEnabled": True,
        "stickyLimitlessEnabled": True, "wetnessCutoffEnabled": True, "recessionEnabled": True, "refillEnabled": True,
        "pondReturnLegEnabled": True, "refillWaitsForOccupants": True, "dugBedLeavesPondEnabled": True,   # POND_RETURN_LEG
        "pondBedHollowEnabled": True,   # POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE step 2
        "mouseoverDepthEnabled": True,   # LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS: depth + litres in the cell readout
        "deepBedsEnabled": True, "deepBedMaxDepth": 100.0,   # POND_ELEVATION_BUILD_LAKES_RUN_DEEP; 50 m ceiling (P11)
        "lakeDepthScale": 1.0, "lakeFloorRoughness": 1.0, "lakeShoreShelfMetres": 0.0, "lakeWayOutMetres": 1.0,   # LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP
        "drainableLakeMaxCells": 40000.0,
        "pondDepthEnabled": True, "pondMudDays": 2.0, "pondStageWritesPerPulse": 400.0, "pondHeadRuleEnabled": True,   # POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD
        "rainFillsExcavationsEnabled": True, "liquidLooksEnabled": True, "pitOutlineEnabled": True, "pitHidesShadowEnabled": True, "edgeSinksEnabled": True,
        "minLimitlessBodyCells": 50.0, "refillRateMultiplier": 1.0,
        "rainFillPerPulse": 0.1,
        "recedeKeepsLastCell": True, "recedeSparesOutflow": True,   # 2026-10-09 recession passes
        "legacyFillFallbackEnabled": True, "legacyFloodViaEngineEnabled": True, "pumpFedSpreadEnabled": True,
        "networkSeamsMoveEnabled": True, "maxNetworkCells": 6000.0,   # FLOW_ORDER_EXTERNAL_INPUT_1 part 2
        "superdeepCaptureEnabled": True, "superdeepCapturesOwnFaction": False,
        "ladderRequiredToExitEnabled": True, "ladderPrisonDoorEnabled": True,
        "superdeepShootingRuleEnabled": True, "shootingCliffMetres": 2.0,   # PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE V5
        "blastsBreakPitCovers": True,          # owner Q5/Q9 2026-10-06 (Explosive Knockback build)
        "pitWidthBodySizeMultiplier": 1.0,
        "pitRelativeClimbEnabled": True, "pitClimbAbilityMultiplier": 1.0,   # PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP
        "pitSlowClimbFactor": 2.0,   # PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS
        "pitRampsEnabled": True, "pitRampMaxSpan": 3, "pitLadderSlowness": 2.0,   # PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS
        "ladderRaiseLowerEnabled": True, "liquidBubblesEnabled": True, "liquidBubbleDensity": 1.0,
        "liquidSeeThroughEnabled": True, "pitWalkNormalEnabled": True,   # 2026-10-06 looks round / ladder raise-lower
        # PIT_LEGACY_CODE_RETIRE_1: the four survivors of the retired PitsSettings, rehoused here
        "trapTriggerEnabled": True, "trapSensitivityMultiplier": 1.0,
        "fallDamageEnabled": True, "fallDamageMultiplier": 1.0, "fallDamagePerMetrePast2": 0.5, "fallDamageCap": 4.0, "fallDeathEnabled": True, "fallDeathFromMetres": 6.0, "fallDeathCertainMetres": 25.0,   # P7 V3; FALL_DAMAGE_BUILD_DEEP_DROPS_KILL
        "spikesEnabled": True, "spikeDamageMultiplier": 1.0, "spikeMinDropMetres": 2.0, "pitGuardrailEnabled": True,   # P7 V4;     # CANAL_BOTTOM_SPIKES_1
        "pitExposureEnabled": True, "pitExposureNarrowing": 8.0, "pitTemperatureCoupling": 3.0, "pitResistanceLossMultiplier": 1.0,   # PIT_TEMPERATURE_SOFTENING_1 (narrowing: owner Q1 2026-10-11)
        "pitDepthDrawOffsetEnabled": True, "pitSinkPerLevel": 0.3,   # PIT_DEPTH_DRAW_OFFSET_1 (PROVISIONAL)
        "flowDoorsSealedFromPitEnabled": True, "sluiceLetsBigThroughEnabled": True,   # FLOWWORKS_DOOR_FAMILY_1
        "canalFireEnabled": True, "burnDaysPerNotch": 1.0,   # Phase 6 (ruling 7); one rate since LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD
        "fireFrontSpeedMultiplier": 1.0, "sourceFireReach": 3.0,                                  # Phase 6 (PROVISIONAL)
        "liquidHeatPushEnabled": True, "liquidHeatStrength": 1.0,                                 # LIQUID_HEAT_PUSH_1 (PROVISIONAL)
        "pitDrowningEnabled": True, "pitDrowningRateMultiplier": 1.0, "pitDrowningHeadFraction": 0.9, "pitDrowningLyingFraction": 0.2, "poisonFillEnabled": True,   # P7 V2;   # PIT_FILL_EFFECTS_1
        "slimeSlipEnabled": True, "slimeSlipChanceMultiplier": 1.0, "slimeSlipStunSeconds": 2.0,
        "slimeClimbOutSlipFactor": 2.0,    # SLIME_CROSSING_BUILD_SLIPPERY_SLOPE (PROVISIONAL)
        "viscosityEnabled": True,          # FLOWWORKS_BUILD_PROGRAM_1 Phase 3/7 viscosity (PROVISIONAL stride)
        "waterFrontCreepEnabled": True,    # CANAL_FRONT_FIX_WRONG_END_WETS_FIRST: water front advances one cell per pulse from the mouth
        "levelBySurfaceEnabled": True,     # WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND: water levels by surface, not dug depth
        "levelSetEnabled": True,           # WATER_LEVELSET_SOLVE: each wet region solved to its flat level (one patch, never 0,1,0,1)
        "levelExactEnabled": True,         # WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: decilitres, one surface per connected body
        "waterBodyTypeFlipFixEnabled": True,   # FLOWWORKS_WATERBODY_DIAGNOSE_SOIL_THROW: vanilla water-body count fix on type change
        "thickCreepEnabled": True,         # THICK_LIQUID_CREEP_1: a thick front moves one cell per moving pulse
        "excavationLoadRepairEnabled": True,   # EXCAVATION_LOAD_SANITY_REPAIR_1: dig grids repaired and liquid list compacted on load
        "bottleLoopEnabled": True, "bottleDirtyStageEnabled": True,
        "tankLoopEnabled": True, "tankCapacityMultiplier": 1.0,
        "liquidDrillingEnabled": True, "drillYieldChanceMultiplier": 1.0, "drillUnitsPerCycle": 1.0,
        "typedLiquidShoresEnabled": True,
        "swaleEnabled": True, "swaleRateMultiplier": 1.0,     # CRACKEDLANDS_MECHANICS_BUILD_1 swale
        "explosionIgnitesLiquidEnabled": True, "foamSmothersLiquidFireEnabled": True,
        "rainDousesLiquidFireEnabled": True,                    # Phase 6 owed (ignition by explosion, extinguishing)
        "chemfuelInfernoEnabled": True, "chemfuelIntensity": 1.0, "chemfuelSpreadSpeed": 1.0, "chemfuelBurnRate": 1.0,
        "astrofuelDetonationEnabled": True, "astrofuelBlastScale": 1.0,   # CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL fuel fires
        "pitStuckAlertEnabled": True, "superdeepRoomsEnabled": True, "captureDownEnabled": True, "wardenFromLipEnabled": True, "pitRoomMinDepthMetres": 3.0,   # PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER (3.0 m for a person);   # SUPERDEEP_PRISON_ROOM_1
        "excavationWallFacesEnabled": True,                     # EXCAVATION_WALL_ART_1 carrier
        "bottleRevertEnabled": True,                            # LIQUID_BOTTLE_LOOP_1 revert timer
        "liquidPumpEnabled": True,                              # Phase 8 slice 1 (universal pump)
        "digFindsEnabled": True, "digFindsLocalOnly": True, "digFindChanceMultiplier": 1.0,
        "digFindBudgetPercent": 5.0, "digFindLetterEnabled": True,
        "digRockGroundEnabled": True, "digRockWorkMultiplier": 4.0, "digRockChunksEnabled": True,
        "digRockChunkMultiplier": 1.0, "digSoilChunkPercent": 0.5,   # DIG_ROCK_TUNE_STONE_FIGHTS_BACK
          # FLOWWORKS_QUARRY_DIGGING_1 (FlowWorks half)
        "excavationWallMaterialEnabled": True, "pitLipOcclusionEnabled": True, "pitLipOcclusion": 0.85, "pitLipOccupantCutEnabled": True, "pitLipOccupantCutWidth": 1.0, "pitSinkClampEnabled": True,
        "liquidSurfaceMotionEnabled": True, "liquidWakesEnabled": True, "pitScorchEnabled": True,
        "pitScorchFadeDays": 20.0,                              # visual principles 1-5 (belt_fwvisuals 2026-10-05)
        "trenchCoverEnabled": True, "trenchCoverStrength": 1.0, "trenchCoverCap": 0.9, "trenchAiAvoidsCages": True,   # TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT
        "portableLadderEnabled": True, "portableLadderMaxLevels": 6, "climbingGearEnabled": True, "climbingGearSlowness": 3.0,
        "pitJumpLandsSafe": True, "pitTeleportLandsSafe": True, "pitRescueLadderEnabled": True,   # PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS
    },
    "RimMandrake.FlowWorks.ManyWaters.RiverSteamSettings": {
        "riverSteamEnabled": True, "puffRateMultiplier": 1.0,
    },
    # River Works merged into FlowWorks 2026-10-05 (409d1f57c); its own static settings class
    "RimMandrake.FlowWorks.Rivers.RM_RiversSettings": {
        "riverWorksEnabled": True, "surfaceCurrentEnabled": True, "currentStrength": 1.0, "centreTicksPerCell": 45.0,
        "marginTicksPerCell": 90.0, "itemDriftFactor": 2.0, "scaleWithRiverSize": True, "floodSurgeEnabled": True,
        "countSeasonalFloods": True, "countTorrentialRainFloods": True, "carryAnimals": True, "carryStrangers": True,
        "carryItems": True, "washOffMapEdge": True, "washedAwayMinDays": 1.0, "washedAwayMaxDays": 3.0, "takenByLandTraceEnabled": True,
        "pathfinderAvoidsCurrents": True, "crossingHazardsEnabled": True, "bruiseChancePerStep": 0.15,
        "dropChancePerStep": 0.25, "fordsEnabled": True, "bankWorksEnabled": True, "wearRateMultiplier": 1.0,
        "breachEnabled": True, "breachHpFraction": 0.5, "stakeSnapTicksPerCell": 150.0, "stakeLineLevee": True,
        "weirPoolLength": 8.0, "weirCatchesFish": True, "weirCatchIntervalHours": 6.0, "weirHeldCatchCap": 30.0,
        "weirCatchesDrift": True, "weirDriftChance": 0.25, "breachWashesCatch": True, "breachWashCells": 4.0,
        "siltRichening": True, "siltIntervalDays": 0.5, "ferryEnabled": True, "ferryMaxSpan": 40.0,
        "ferryRopeGuidesColonists": True,
    },
    # liquid machinery pass 2026-10-05 (3e473f37c); disabledLiquidMachines is a private list (per-machine switches),
    # not a field this table can hold; pipeDefaultLook (rigid pipe looks, 2026-10-11) is a string, art only, not in this table
    "RimMandrake.FlowWorks.Machinery.RM_MachinerySettings": {
        "universalPipesEnabled": True, "converterRateMultiplier": 1.0, "liquidWorksRuinsEnabled": True,
        "liquidWorksRuinStockEnabled": True, "industrialWorksBuildAnywhere": False, "pipeAdaptersEnabled": True,
        "litresPerFilth": 400.0, "liquidTheftEnabled": True, "liquidTheftGoodwillPerDay": 2.0, "liquidTheftSightRange": 12.0,
        "pipeLinksIntoMachines": True, "joinFittings": False,   # HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY (art only; fittings OFF until the owner rules)
        "pipesUnderToCentre": True,   # PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE (art only)
    },
    # the flexible hose's section (moved from Gimme Some Slack at the hose port, 2026-10-11); Scribed with a `hose_` key prefix.
    # String fields (defaultLook) are not in this bool/float table; hoseSettingsImported is an internal flag.
    "RimMandrake.FlowWorks.Hose.RM_HoseSettings": {
        "enabled": True, "tankModesEnabled": True, "tankLitresPerCycle": 2000.0, "freeEndRolesEnabled": True, "dumpLitresPerCycle": 1000.0, "hoseHoldsLiquid": True, "hoseLitresPerCell": 5.0, "minBendRadius": 1.2, "plumpAmount": 1.0, "transitionTicks": 30.0, "releaseTicks": 500.0,
        "minPlumpDwell": 600.0, "thickness": 1.0, "maxLength": 40.0, "maxLengthDefaults": 1.0, "couplingSpacing": 8.0, "handlingTime": 1.0,
        "windCellsPerSecond": 3.0, "autoResumeDroppedHose": True, "slack": 1.0, "tintByContents": True, "fillWobble": True,
        "hoseSettingsImported": False,
    },
    # FLOWWORKS_QUARRY_DIGGING_1 river half: sluice box + panning
    "RimMandrake.FlowWorks.Quarry.RM_QuarrySettings": {
        "sluiceBoxEnabled": True, "panningEnabled": True, "placerFloodRefill": True, "placerStockPercent": 2.0,
        "sluiceYieldMultiplier": 1.0, "panningYieldMultiplier": 1.0,
    },
    # both scribed into the FlowWorks settings file from RimMandrakeFlowWorksSettings.ExposeData; missing from this table
    # until 2026-10-15 (independent review), so L2 / P-B4 never read them and the O2 census never saw their toggles
    "RimMandrake.FlowWorks.Machinery.Kits.RM_KitSettings": {
        "liquidBathRecipesEnabled": True, "liquidReactionsEnabled": True, "reactionRateMultiplier": 1.0,
        "hotLiquidEnabled": True, "hotLiquidBurnMultiplier": 1.0, "fluidResidueEnabled": True,
    },
    "RimMandrake.FlowWorks.Machinery.Logistics.RM_SluiceGateSettings": {
        "sluiceGatesEnabled": True, "sluiceGateOpenDelayTicks": 120, "sluiceGateCloseDelayTicks": 240,
    },
    # FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS (2026-10-16): the map controls' master switch
    "RimMandrake.FlowWorks.MapControls.RM_MapControlSettings": {
        "mapControlsEnabled": True,
    },
    # RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW (2026-10-16): River Colors (was mandrake.rut.rivercolors); its three
    # anchor Colors are not in this bool/float table
    "RimMandrake.FlowWorks.RiverColors.RM_RiverColorsSettings": {
        "riverColorsEnabled": True,
    },
    # THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY (2026-10-16, design §6): defaults = the ruled behaviour (animals ON, OQ-5)
    "RimMandrake.FlowWorks.Thirst.RM_ThirstSettings": {
        "thirstEnabled": True, "thirstRateMultiplier": 1.0, "thirstHeatScaling": True, "animalsGetThirst": True,
        "drinkFromTerrain": True, "waterQualityEffects": True, "dbhBottleBridge": True,
        # THIRST_RULES_BUILD_SALT_OFF_THE_MENU + owner Q12 (2026-10-17, c72cea8a08)
        "lastResortDrinking": True, "saltBreakEnabled": True, "roughDrinkPenalty": True,
        "drinkingReserveLitres": 200.0, "bucketFirefighting": True, "snowGathering": True,
        "sanguophageBloodQuenches": True, "filledBottlesPerColonist": 3,
    },
    # SPRINKLER_HEADS_BUILD_PUMP_REQUIRED (2026-10-16, design §5): defaults = the ruled behaviour (OQ-S1..S7)
    "RimMandrake.FlowWorks.Sprinklers.RM_SprinklerSettings": {
        "sprinklersEnabled": True, "sprinklerLitresPerCellHour": 0.5, "sprinklerNativeRadius": 2.9,
        "sprinklerNonWaterEffects": True, "vfeSprinklerAdapterEnabled": True, "vfeThirstValve": True,
    },
}
SETTINGS_SOURCES = {     # type -> C# file (relative to the mod's source folder)
    "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings": "RimMandrakeFlowWorksMod.cs",
    "RimMandrake.FlowWorks.ManyWaters.RiverSteamSettings": os.path.join("ManyWaters", "RiverSteamSettings.cs"),
    "RimMandrake.FlowWorks.Rivers.RM_RiversSettings": os.path.join("Rivers", "RM_RiversSettings.cs"),
    "RimMandrake.FlowWorks.Machinery.RM_MachinerySettings": os.path.join("Machinery", "RM_MachinerySettings.cs"),
    "RimMandrake.FlowWorks.Quarry.RM_QuarrySettings": os.path.join("Quarry", "RM_QuarrySettings.cs"),
    "RimMandrake.FlowWorks.Hose.RM_HoseSettings": os.path.join("Hose", "RM_HoseSettings.cs"),
    "RimMandrake.FlowWorks.Machinery.Kits.RM_KitSettings": os.path.join("Machinery", "Kits", "RM_KitSettings.cs"),
    "RimMandrake.FlowWorks.Machinery.Logistics.RM_SluiceGateSettings": os.path.join("Machinery", "Logistics", "RM_SluiceGateSettings.cs"),
    "RimMandrake.FlowWorks.MapControls.RM_MapControlSettings": os.path.join("MapControls", "RM_MapControlSettings.cs"),
    "RimMandrake.FlowWorks.RiverColors.RM_RiverColorsSettings": os.path.join("RiverColors", "RM_RiverColorsSettings.cs"),
    "RimMandrake.FlowWorks.Thirst.RM_ThirstSettings": os.path.join("Thirst", "RM_ThirstSettings.cs"),
    "RimMandrake.FlowWorks.Sprinklers.RM_SprinklerSettings": os.path.join("Sprinklers", "RM_SprinklerSettings.cs"),
}
# Scribed migration flags the MOD sets itself (hoseSettingsImported goes True on the first load after the hose port): no
# control, never a player setting, never on the toggle floor, never compared to a shipped default.
INTERNAL_FLAGS = ("hoseSettingsImported",)
# Mod subclasses whose ModSettings files the run must restore byte-for-byte (plan 3.3).
MOD_CLASSES = ("RimMandrakeFlowWorksMod", "RiverSteamMod")   # PitsMod retired 2026-10-02


def toggles():
    """Every boolean Mod Settings field (the whole registry), NOT the harness toggle floor: validation.py's suite.toggles
    is the floor, and validation.TOGGLES_NOT_ON_FLOOR names the registry bools left off it."""
    return sorted(f for fields in SETTINGS.values() for f, v in fields.items() if isinstance(v, bool) and f not in INTERNAL_FLAGS)


def settings_equal(got, want):
    """Bridge values come back as strings; compare by the default's type."""
    if isinstance(want, bool):
        return str(got).strip().lower() == str(want).lower()
    try:
        return abs(float(got) - float(want)) < 1e-4
    except (TypeError, ValueError):
        return False


# --------------------------------------------------------------------- tools
EXISTING_TOOLS = (            # MEASURED: [Tool] names in JawaBench.BridgeTools / bench_tools_dump
    "rimworld/get_game_info", "rimworld/pause_game", "rimworld/step_game_ticks",
    "rimworld/screenshot_cell_rect", "rimworld/save_game", "rimworld/list_windows",
    "jawa/map_info", "jawa/list_things", "jawa/list_pawns", "jawa/destroy_batch",
    "jawa/set_terrain_batch", "jawa/get_terrain_batch", "jawa/get_terrain_layers",
    "jawa/set_roof_batch", "jawa/get_roof_batch", "jawa/set_fog", "jawa/paint_area",
    "jawa/weather_set", "jawa/weather_get", "jawa/game_condition", "jawa/incident_queue_clear",
    "jawa/cell_temperature", "jawa/time_clock", "jawa/time_set_ticks", "jawa/time_perf",
    "jawa/mod_settings_field", "jawa/type_probe", "jawa/research_bulk", "jawa/clear_ui",
    "jawa/flowworks_excavation_drive", "jawa/flowworks_excavation_report", "jawa/canal_cell_report",
)
P_B3_TOOLS = ("jawa/flowworks_excavation_drive", "jawa/flowworks_excavation_report",
              "jawa/canal_cell_report", "jawa/mod_settings_field")
# Built 2026-10-01 (JawaBenchFlowWorksNorthstarTools.cs + type_probe identity) and used live (v2 S3/E1c read
# jawa/flowworks_engine_state); callers still gate on the LIVE tool list. The response shape given here is the
# CONTRACT the tool meets; FakeFlowWorksGame implements exactly this shape and nothing else.
NEEDED_TOOLS = {
    "jawa/flowworks_body_report":
        "{x,z,classify=true} -> success, classified (bool; classify=true, the default, classifies via "
        "RM_LiquidStock.BodyAt, which is the plan 3.4 'force classification once'; false is a pure read), "
        "body{id, limitless, stock, capacity, cellCount, recededCount, truncated}, activeFluid, ticksGame "
        "(the subset prep needs; the live tool also answers formedByThisCall, isSourceCell, ...)",
    "jawa/flowworks_engine_state":
        "{} -> success, nextPulseTick, pulseIntervalTicks, activeFluid, rainAccumulator, "
        "excavatedCellCount, ticksGame (plan 6.11)",
    "jawa/type_probe+identity":
        "type_probe extended with assemblyLocation, assemblyMvid, assemblyFileSha256 for the "
        "loaded RimMandrake.FlowWorks assembly (plan 3.2 / 6.12, P-E6)",
}

# --------------------------------------------------------------------- layout
BUFFER = 8          # plan 3.4: bar footprint + 8-cell buffer
GAP = 12            # >= 12-cell gaps between buffered plots
EDGE_LIMITED = 15   # limited plots sit >= 15 cells from every edge
HALO = 15           # no natural water within 15 cells of a plot except its own reservoir
MIN_MAP = 200       # plan 3.4: size >= 200x200
SOIL = "Soil"
WET_OR_ROUGH = ("Water", "Marsh", "Mud", "Ice", "Lava")   # substrings refused near a plot

# Plot footprints are bar-derived (plan 2.3/2.4/2.5); bodies are rects RELATIVE to the plot.
# edge: None (interior, limited) | "west" | "east" (touches that edge; limitless/sink plots).
PLOTS = [
    {"id": "A", "w": 8, "h": 3, "bars": ["canal_reads_as_dug_channel", "canal_dry_reads_as_obstacle",
                                         "never_gravel_path"], "bodies": []},
    {"id": "B", "w": 6, "h": 7, "bars": ["canal_partial_fill_distinct", "fill_tier_legible"], "bodies": []},
    {"id": "D", "w": 18, "h": 5, "bars": ["reservoir_fill_visibly_drops", "never_full_reservoir_after_heavy_draw"],
     "bodies": [{"name": "D_pond", "terrain": "WaterShallow", "rect": (0, 0, 5, 5), "limitless": False}]},
    # E: the tar pond is painted by the bar itself as RM_TarShallow terrain (a body's fluid is its terrain's,
    # LIQUID_BODY_FLUID_IDENTITY_1; no ActiveFluid switch), so the golden plot is bare Soil; the buffer is the
    # 8-cell fire moat.
    {"id": "E", "w": 14, "h": 6, "bars": ["canal_burning_reads_as_burning_liquid", "canal_fire_reaches_reservoir",
                                          "canal_spent_after_burn"], "bodies": [],
     "deferred": [{"name": "E_tarpond", "fluid": "RM_Fluid_Tar", "rect": (0, 1, 4, 4)}]},
    {"id": "F", "w": 6, "h": 3, "bars": ["slime_reads_as_viscous_not_water", "slime_occupant_below_surface"],
     "bodies": []},
    {"id": "G", "w": 13, "h": 9, "bars": ["pit_reads_as_hole", "pit_occupant_below_floor", "pit_trapped_reads_as_trapped",
                                          "pit_occupied_distinguishable", "ladder_state_legible"], "bodies": []},
    {"id": "H", "w": 10, "h": 5, "bars": ["pit_depth_ladder_legible"], "bodies": []},
    {"id": "R", "w": 3, "h": 1, "bars": ["toggle:rainFillsExcavationsEnabled"], "bodies": [],
     # The rain twin is NOT roofed in the golden: MEASURED 2026-10-05 a lone roofed cell collapses within ~250
     # ticks (RoofConstructed AND RoofRockThick, even with a steel wall adjacent), leaving rubble in the plot.
     # The rain bar roofs its own cell on its working copy, right before the pulse it judges.
     "roofed": []},
    {"id": "K", "w": 32, "h": 2, "bars": ["toggle:sourceBudgetEnabled"],
     "bodies": [{"name": "K_pond", "terrain": "WaterShallow", "rect": (0, 0, 2, 2), "limitless": False}]},
    {"id": "C", "w": 20, "h": 12, "edge": "west",
     "bars": ["canal_fill_spreads_along_itself", "canal_fill_front_watchable", "canal_holds_only_the_channel",
              "canal_reads_as_same_liquid_as_reservoir", "never_liquid_on_open_ground"],
     "bodies": [{"name": "C_sea", "terrain": "WaterDeep", "rect": (0, 0, 8, 12), "limitless": True}]},
    {"id": "S", "w": 22, "h": 4, "edge": "east", "bars": ["toggle:edgeSinksEnabled"],
     "bodies": [{"name": "S_pond", "terrain": "WaterShallow", "rect": (0, 0, 4, 4), "limitless": False}]},
]


def _buffered(r, b=BUFFER):
    x, z, w, h = r
    return (x - b, z - b, w + 2 * b, h + 2 * b)


def _overlap_gap(a, b):
    """Smallest axis gap between two rects (negative = overlap)."""
    ax, az, aw, ah = a
    bx, bz, bw, bh = b
    gx = max(bx - (ax + aw), ax - (bx + bw))
    gz = max(bz - (az + ah), az - (bz + bh))
    return max(gx, gz)


def clip(r, size):
    x, z, w, h = r
    x0, z0 = max(0, x), max(0, z)
    x1, z1 = min(size[0], x + w), min(size[1], z + h)
    return (x0, z0, max(0, x1 - x0), max(0, z1 - z0))


def layout(size):
    """Place every plot on a map of `size` (W, Z). Deterministic; raises ValueError if it
    cannot honour plan 3.4. Returns [{id, rect, buffered, edge, bodies[abs], roofed[abs], ...}]."""
    W, Z = size
    if W < MIN_MAP or Z < MIN_MAP:
        raise ValueError("map %dx%d is below the plan 3.4 minimum %dx%d" % (W, Z, MIN_MAP, MIN_MAP))
    out = []
    # interior plots: row packer over buffered rects, footprints >= EDGE_LIMITED from edges
    lo = EDGE_LIMITED - BUFFER
    x, z, row_h = lo, lo, 0
    interior = [p for p in PLOTS if not p.get("edge")]
    for p in interior:
        bw, bh = p["w"] + 2 * BUFFER, p["h"] + 2 * BUFFER
        if x + bw > W - lo:
            x, z, row_h = lo, z + row_h + GAP, 0
        if z + bh > Z - lo:
            raise ValueError("interior plots do not fit on %dx%d" % (W, Z))
        out.append(_place(p, (x + BUFFER, z + BUFFER, p["w"], p["h"])))
        x += bw + GAP
        row_h = max(row_h, bh)
    # edge plots: top band, west and east edges
    top = z + row_h + GAP + BUFFER
    for p in (q for q in PLOTS if q.get("edge")):
        fz = top
        fx = 0 if p["edge"] == "west" else W - p["w"]
        if fz + p["h"] + BUFFER > Z:
            raise ValueError("edge plot %s does not fit on %dx%d" % (p["id"], W, Z))
        # C: the sea sits on the west edge. S: the pond sits at the plot's INNER (west) end and
        # the channel the bar digs runs east to the map edge -- both fall out of rect (0,0,..).
        out.append(_place(p, (fx, fz, p["w"], p["h"])))
    errs = validate_layout(out, size)
    if errs:
        raise ValueError("; ".join(errs))
    return out


def _place(p, rect):
    x, z = rect[0], rect[1]
    return {
        "id": p["id"], "rect": rect, "buffered": _buffered(rect), "edge": p.get("edge"),
        "bars": list(p["bars"]),
        "bodies": [dict(b, rect=(x + b["rect"][0], z + b["rect"][1], b["rect"][2], b["rect"][3]))
                   for b in p["bodies"]],
        "deferred": [dict(d, rect=(x + d["rect"][0], z + d["rect"][1], d["rect"][2], d["rect"][3]))
                     for d in p.get("deferred", ())],
        "roofed": [(x + dx, z + dz) for dx, dz in p.get("roofed", ())],
        # a roofed cell with no roof holder within range COLLAPSES on the first ticks, thick rock included
        # (MEASURED 2026-10-05: CollapsedRocks + Filth_RubbleRock): one steel wall in the buffer, north of it, holds it
        "supports": [(x + dx, z + dz - 1) for dx, dz in p.get("roofed", ())],
    }


def validate_layout(plots, size):
    W, Z = size
    errs = []
    for i, a in enumerate(plots):
        x, z, w, h = a["rect"]
        if x < 0 or z < 0 or x + w > W or z + h > Z:
            errs.append("%s off map" % a["id"])
        edge_d = min(x, z, W - (x + w), Z - (z + h))
        if a["edge"] is None and edge_d < EDGE_LIMITED:
            errs.append("limited plot %s is %d < %d from an edge" % (a["id"], edge_d, EDGE_LIMITED))
        if a["edge"] == "west" and x != 0:
            errs.append("%s must touch the west edge" % a["id"])
        if a["edge"] == "east" and x + w != W:
            errs.append("%s must touch the east edge" % a["id"])
        for b in a["bodies"]:
            bx, bz, bw, bh = b["rect"]
            if b["limitless"]:
                if bw * bh < 80:
                    errs.append("limitless body %s has %d < 80 cells" % (b["name"], bw * bh))
                if not (bx == 0 or bz == 0 or bx + bw == W or bz + bh == Z):
                    errs.append("limitless body %s does not touch the map edge" % b["name"])
            elif min(bx, bz, W - (bx + bw), Z - (bz + bh)) < EDGE_LIMITED:
                errs.append("limited body %s within %d of an edge" % (b["name"], EDGE_LIMITED))
        for b in plots[i + 1:]:
            g = _overlap_gap(clip(a["buffered"], size), clip(b["buffered"], size))
            if g < GAP:
                errs.append("plots %s/%s buffered gap %d < %d" % (a["id"], b["id"], g, GAP))
    return errs


def plots_from_json(plots):
    """A sidecar's plots after a JSON round trip (lists) -> the tuple form layout() returns."""
    out = []
    for p in plots:
        q = dict(p, rect=tuple(p["rect"]), buffered=tuple(p["buffered"]),
                 roofed=[tuple(c) for c in p.get("roofed", ())],
                 supports=[tuple(c) for c in p.get("supports", ())])
        q["bodies"] = [dict(b, rect=tuple(b["rect"])) for b in p.get("bodies", ())]
        q["deferred"] = [dict(d, rect=tuple(d["rect"])) for d in p.get("deferred", ())]
        out.append(q)
    return out


def plot_by_id(plots, pid):
    for p in plots:
        if p["id"] == pid:
            return p
    raise KeyError(pid)


def cells(rect):
    x, z, w, h = rect
    return [(cx, cz) for cx in range(x, x + w) for cz in range(z, z + h)]


def rect_str(r):
    return "%d,%d,%d,%d" % tuple(r)


# DORMANT plumbing: no plot sets "roofed" today (plot R's comment: a lone roofed cell collapses, rock roof included),
# so TWIN_ROOF / SUPPORT_THING and the "supports" cells are never used; kept for a plot that roofs with a holder.
TWIN_ROOF = "RoofConstructed"
SUPPORT_THING = "Wall"


def expected_cells(plot, size):
    """The manifest model for one plot: {(x,z): {base, temp, roof, D, F, things}} over
    footprint + buffer (clipped to the map). Bodies are their terrain, any "roofed" cell
    (none today) is roofed, everything else is bare Soil, unroofed, undug, empty."""
    want = {}
    for c in cells(clip(plot["buffered"], size)):
        want[c] = {"base": SOIL, "temp": "none", "roof": "none", "D": 0, "F": 0, "things": []}
    for b in plot["bodies"]:
        for c in cells(b["rect"]):
            want[c]["base"] = b["terrain"]
    for c in plot["roofed"]:
        want[c]["roof"] = TWIN_ROOF
    for c in plot.get("supports", ()):
        if c in want:
            want[c]["things"] = [SUPPORT_THING]
    return want


def check_points(plot):
    """Cells sampled for temperature / D-F spot reads: footprint corners + centre +
    every body's centre and every roofed cell (plan 3.5: source, excavated, shot cells)."""
    x, z, w, h = plot["rect"]
    pts = {(x, z), (x + w - 1, z), (x, z + h - 1), (x + w - 1, z + h - 1), (x + w // 2, z + h // 2)}
    for b in plot["bodies"]:
        bx, bz, bw, bh = b["rect"]
        pts.add((bx + bw // 2, bz + bh // 2))
    pts.update(plot["roofed"])
    return sorted(pts)


# --------------------------------------------------------------------- run-length reads
def parse_ops(ops, default=None):
    """'Def:x,z,w,h;Def:x,z,...' (the get_terrain_batch / get_roof_batch grammar) ->
    {(x,z): Def}. Bare 'x,z,w,h' entries take `default`. Raises on a malformed op."""
    out = {}
    for op in str(ops or "").replace("\n", ";").split(";"):
        op = op.strip()
        if not op:
            continue
        name, _, coords = op.rpartition(":")
        name = name or default
        parts = [int(v) for v in coords.split(",")]
        x, z = parts[0], parts[1]
        w = parts[2] if len(parts) > 2 else 1
        h = parts[3] if len(parts) > 3 else 1
        for c in cells((x, z, w, h)):
            out[c] = name
    return out


# --------------------------------------------------------------------- hashing
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_hash(root, exts=(".xml",)):
    """sha256 over (relpath, file sha256) of every file with `exts` under root, sorted."""
    h = hashlib.sha256()
    for dp, dn, fn in os.walk(root):
        dn.sort()
        for f in sorted(fn):
            if f.lower().endswith(exts):
                p = os.path.join(dp, f)
                h.update(os.path.relpath(p, root).replace("\\", "/").encode())
                h.update(sha256_file(p).encode())
    return h.hexdigest()


def defs_hash(mod_dir=MOD_DIR):
    return tree_hash(os.path.join(mod_dir, "Defs"))


def read_prefs(prefs_path):
    """Render profile + autosave from Prefs.xml (read-only). Missing keys are absent, never 0."""
    import xml.etree.ElementTree as ET
    r = ET.parse(prefs_path).getroot()
    keys = ("screenWidth", "screenHeight", "fullscreen", "uiScale", "langFolderName",
            "textureCompression", "resetModsConfigOnCrash", "autosaveIntervalDays")
    return {k: r.findtext(k).strip() for k in keys if r.findtext(k) is not None}


RENDER_KEYS = ("screenWidth", "screenHeight", "fullscreen", "uiScale", "langFolderName", "textureCompression")


# --------------------------------------------------------------------- config backup / restore
def settings_files(config_dir):
    out = []
    for cls in MOD_CLASSES:
        out += glob.glob(os.path.join(config_dir, "Mod_*_%s.xml" % cls))
    return sorted(set(out))


def backup_configs(config_dir, out_dir, stamp=None):
    """Copy ModsConfig.xml + every FlowWorks ModSettings file byte-for-byte into out_dir and
    write a manifest with each sha256 (plan 3.1 / 3.3, GPT #6/#13). Returns the manifest path.
    A ModSettings file that does not exist is recorded as absent: restore then deletes any
    file the run created under that name pattern."""
    stamp = stamp or time.strftime("%Y%m%dT%H%M%S")
    os.makedirs(out_dir, exist_ok=True)
    entries = []
    src = os.path.join(config_dir, "ModsConfig.xml")
    for path, label in [(src, "ModsConfig.pre-ns-flowworks.%s.xml" % stamp)] + \
            [(p, "%s.pre-ns-flowworks.%s.xml" % (os.path.splitext(os.path.basename(p))[0], stamp))
             for p in settings_files(config_dir)]:
        dst = os.path.join(out_dir, label)
        shutil.copyfile(path, dst)
        sha = sha256_file(path)
        if sha256_file(dst) != sha:
            raise IOError("backup of %s does not hash-match its source" % path)
        entries.append({"src": os.path.basename(path), "backup": label, "sha256": sha})
    man = {"stamp": stamp, "config_dir": config_dir, "entries": entries,
           "settings_patterns": ["Mod_*_%s.xml" % c for c in MOD_CLASSES]}
    mpath = os.path.join(out_dir, "ns_flowworks_backup.%s.json" % stamp)
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)
    return mpath


def verify_backup(manifest_path):
    """[] when every backup file still hashes to its recorded sha; else the problems."""
    man = json.load(open(manifest_path, encoding="utf-8"))
    d = os.path.dirname(manifest_path)
    bad = []
    for e in man["entries"]:
        p = os.path.join(d, e["backup"])
        if not os.path.isfile(p):
            bad.append("missing backup %s" % e["backup"])
        elif sha256_file(p) != e["sha256"]:
            bad.append("backup %s no longer matches its recorded sha" % e["backup"])
    if not any(e["src"] == "ModsConfig.xml" for e in man["entries"]):
        bad.append("no ModsConfig.xml in the backup")
    return bad


def restore_configs(manifest_path, config_dir=None):
    """Put every backed-up file back by exact bytes, delete ModSettings files the run
    created, and prove each restored file hashes to the recorded sha. Re-runnable by hand:
      python3 src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py restore <manifest>"""
    man = json.load(open(manifest_path, encoding="utf-8"))
    config_dir = config_dir or man["config_dir"]
    d = os.path.dirname(manifest_path)
    kept = set()
    for e in man["entries"]:
        dst = os.path.join(config_dir, e["src"])
        shutil.copyfile(os.path.join(d, e["backup"]), dst)
        kept.add(e["src"])
    removed = []
    for p in settings_files(config_dir):
        if os.path.basename(p) not in kept:
            os.remove(p)
            removed.append(os.path.basename(p))
    bad = [e["src"] for e in man["entries"]
           if sha256_file(os.path.join(config_dir, e["src"])) != e["sha256"]]
    if bad:
        raise IOError("restore did not reproduce the recorded bytes for %s" % bad)
    return {"restored": sorted(kept), "removed": removed}
