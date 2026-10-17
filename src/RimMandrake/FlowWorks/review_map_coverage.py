"""review_map_coverage.py -- what FlowWorks does today, read off disk, and where the review map shows each piece.

    (run by review_map.py --plan, which writes northstar/review/map/COVERAGE.md and fails on any uncovered item)

The INVENTORY is derived, never typed: every non-abstract def in Defs/ (and every def a patch adds), every Mod Settings
field a settings class saves (Scribe_Values.Look in Source/, SelfTest excluded), every gizmo label (defaultLabel in
Source/) and the two designators, and every texture under Textures/. The FEATURES table below groups inventory items
into the features a player would name and says where each is shown: a gallery station id, "V" (the pits visuals
block), "F" (the free area), "R:<id>" (map R, the river site), or "matrix: <reason>" when no frozen station can show
it. First matching rule wins. An item no rule matches is UNCOVERED and --plan fails.
"""
import glob
import os
import re
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "northstar", "review", "map", "COVERAGE.md")
REL = "src/RimMandrake/FlowWorks/"

LIVE_CMD = [
    "python.exe src/RimMandrake/FlowWorks/review_map.py --build --fresh-map --save | tr -d '\\r'",
    "python.exe src/RimMandrake/FlowWorks/northstar/river_site.py | tr -d '\\r'",
    "python.exe src/RimMandrake/FlowWorks/review_map.py --rivers --build --save | tr -d '\\r'",
]
RUNTIME = ("about 12 minutes: the main map about 6 (fresh quicktest map ~1.5 min; the last build, 52 stations + 39 "
           "visuals, took 112 s; this one has {n} stations and ~250 more staging calls) plus its save; river_site.py "
           "about 3 to 4 (founding a colony on a river tile and generating its map); map R about 1 (25 terrain reads, "
           "~60 placing calls) plus its save. Budget 20 minutes before calling it stuck.")

M = "matrix: "
# (kind, regex on the item's name, feature, where shown). kind: def | set | gizmo | tex.
FEATURES = [
    # ---- digging
    ("def", r"^DesignationDef/RM_DigCanal$|^JobDef/RM_DigCanalJob$|^WorkGiverDef/RM_DigCanalWorkGiver$",
     "Dig-canal order", "dig_canal"),
    ("def", r"^TerrainDef/RM_Channel_", "Four dug depths (channel grounds D1-D4)", "dig_canal"),
    ("def", r"RM_FillInCanal", "Fill-in order", "dig_fill_in"),
    ("gizmo", r"Dig canal", "Dig canal designator", "dig_canal"),
    ("gizmo", r"Fill in canal", "Fill in canal designator", "dig_fill_in"),
    ("tex", r"FlowWorks/Tank/", "Tank look art", "tank_styles"),
    ("tex", r"UI/Designators/FlowWorks/RM_DigCanal", "Dig canal icon", "dig_canal"),
    ("tex", r"UI/Designators/FlowWorks/RM_FillInCanal", "Fill in icon", "dig_fill_in"),
    ("set", r"^digToDepthEnabled$", "Dig deeper", "dig_canal"),
    ("set", r"^fillIn", "Fill-in and its push-back", "dig_fill_in"),
    ("set", r"^digFind", "Digging turns up minerals", "dig_finds"),
    ("set", r"^(digRock|digSoilChunk)", "Digging rock takes longer and drops chunks (soil less)", "dig_canal"),   # DIG_ROCK_TUNE_STONE_FIGHTS_BACK: no rock-dig station, so the canal-dig one
    # ---- flow
    # FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS: dev-placed flow source / sink (no station yet; review-map station
    # 11-type staging is to move onto them later)
    ("def", r"^ThingDef/RM_Flow(Source|Sink)$", "Map controls: flow source and flow sink", M + "dev-placed map controls, no station yet"),
    ("set", r"^mapControlsEnabled$", "Map controls: flow source and flow sink", M + "dev-placed map controls, no station yet"),
    ("gizmo", r'^"(On|Remove|Rate\.\.\.)"$|^"(Liquid|Takes): " \+ FluidLabel', "Map controls: flow source and flow sink", M + "dev-placed map controls, no station yet"),
    # FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES: the six further dev-placed map controls (small stones; no station yet)
    ("def", r"^ThingDef/RM_(FlowMeter|LevelHolder|TimerSwitch|MapEdgeSetter|CurrentPainter|LiquidThermostat)$",
     "Map controls: meter, level holder, timer, map-edge setter, current painter, thermostat", M + "dev-placed map controls, no station yet"),
    ("gizmo", r'^"(Read now|Schedule\.\.\.|Invert|Fast)"$|^"(Hold at|Radius:|Flows) " \+|^EdgeNames\[edge\] \+',
     "Map controls: meter, level holder, timer, map-edge setter, current painter, thermostat", M + "dev-placed map controls, no station yet"),
    ("set", r"^(depthEngineEnabled|pulseIntervalTicks|flowPerPulse)$", "The flow engine and its pulse", "flow_spreads"),
    ("set", r"^(viscosityEnabled|thickCreepEnabled|waterFrontCreepEnabled|levelBySurfaceEnabled|levelSetEnabled)$", "Viscosity: tar crawls", "flow_identity"),
    ("set", r"^(sourceBudgetEnabled|stickyLimitlessEnabled|sourceBudgetMultiplier|minLimitlessBodyCells)$",
     "Ponds pay out; map-edge lakes never run dry", "flow_ponds"),
    ("set", r"^(recessionEnabled|recedeKeepsLastCell|recedeSparesOutflow)$", "A pond visibly recedes", "flow_shrinks"),
    ("set", r"^(pondDepthEnabled|pondMudDays|pondStageWritesPerPulse)$", "A drying pond shallows all over, then mud", "flow_shrinks"),
    ("def", r"^TerrainDef/RM_(WaterChestDeepStill|WaterThin)$", "Pond stage waters (still chest-deep, thin)", "flow_shrinks"),
    ("set", r"^pondHeadRuleEnabled$", "A pond feeds a canal only while its surface is higher", "flow_ponds"),
    ("set", r"^(dugBedLeavesPondEnabled|pondBedHollowEnabled|mouseoverDepthEnabled|deepBedsEnabled|deepBedMaxDepth|deepBedCellsPerLevel|drainableLakeMaxCells)$", "A drained pond leaves a hollow bed", "pond_bed"),
    ("def", r"^TerrainDef/RM_Lakebed_", "Lakebed ground", "pond_bed"),
    ("tex", r"Terrain/FlowWorks/RM_Lakebed_", "Lakebed art", "pond_bed"),
    ("set", r"^(refillEnabled|refillWaitsForOccupants|refillRateMultiplier)$", "Refill, and waiting for occupants",
     "pond_occupied"),
    ("set", r"^pondReturnLegEnabled$", "Filled-in water returns to its pond", "pond_return"),
    ("set", r"^(rainFillsExcavationsEnabled|rainFillPerPulse)$", "Rain fills open trenches", "flow_rain"),
    ("set", r"^edgeSinksEnabled$", "Map-edge sinks", "flow_drains"),
    ("def", r"^ThingDef/RM_FluidCanalFlood$", "Floods released into canals (canyon flood, belch)", "flow_canyon"),
    ("set", r"^(excavationLoadRepairEnabled|legacyFillFallbackEnabled|legacyFloodViaEngineEnabled)$",
     "Old-save repair and legacy fallbacks", M + "they act only when an OLD save loads; a fresh review map has nothing "
     "to repair"),
    ("set", r"^(networkSeamsMoveEnabled|maxNetworkCells)$", "Flow network bounds",
     M + "performance bounds on very large canal networks; nothing to see at station size"),
    # ---- liquids in canals (the V block holds eleven at every depth)
    ("def", r"^RimMandrake\.FlowWorks\.FluidDef/RM_Fluid_(Water|Tar|Oil|SlimeGreen|SlimeWhite|SlimeRed|Blood|Chemfuel|Astrofuel)$",
     "Canal liquids in the V block", "V"),
    ("def", r"^RimMandrake\.FlowWorks\.FluidDef/RM_Fluid_", "Four more canal liquids", "canal_fluids_more"),
    ("def", r"^TerrainDef/RM_Fill_(Water|Tar|Oil|SlimeGreen|SlimeWhite|SlimeRed|Blood|Chemfuel|Astrofuel)_(Brim|Superdeep)$",
     "Canal fill grounds, brim and pit", "V"),
    ("def", r"^TerrainDef/RM_Fill_Water_(Trace|Half)$", "Partial fills (trace, half)", "look_canal"),
    ("def", r"^TerrainDef/RM_Fill_(Poison|SlimeYellow|BoilingWater|IcyWater)_Brim$", "Fill grounds of the four more",
     "canal_fluids_more"),
    ("def", r"^TerrainDef/RM_Fill_", "Trace/half/pit fill grounds of the other liquids",
     M + "the same tier drawing as water's, tinted per liquid; every tier is shown once for water (look_canal) and "
     "every liquid once at brim (V, canal_fluids_more)"),
    # ---- fire
    ("set", r"^(liquidIgnitionEnabled|canalFireEnabled|explosionIgnitesLiquidEnabled|fireFrontSpeedMultiplier)$",
     "Liquid catches fire and the front travels", "fire_lights"),
    ("def", r"^ThingDef/RM_LiquidFlame$", "Burning liquid", "fire_lights"),
    ("set", r"^(canalBurnDaysPerLevel|sourceBurnDaysPerLevel|sourceFireReach)$", "Burns for days, back into the pond",
     "fire_lasts"),
    ("set", r"^(foamSmothersLiquidFireEnabled|rainDousesLiquidFireEnabled)$", "Foam and rain put it out", "fire_out"),
    ("set", r"^liquidCorrosionEnabled$", "Corrosion", "fire_corrosion"),
    ("set", r"^chemfuel(InfernoEnabled|Intensity|SpreadSpeed|BurnRate)$", "Chemfuel burns like gasoline", "fire_chemfuel"),
    ("def", r"^ThingDef/RM_LiquidFlame_Inferno$", "Big chemfuel flame", "fire_chemfuel"),
    ("set", r"^astrofuel(DetonationEnabled|BlastScale)$", "Astrofuel detonates", "fire_astrofuel"),
    ("set", r"^pitScorch", "A burnt-out pit stays scorched", "look_fire"),
    ("tex", r"Terrain/FlowWorks/(RM_Scorch_|Debris/RM_ScorchDebris)", "Scorch art", "look_fire"),
    # ---- pits: catching
    ("set", r"^superdeepCaptureEnabled$", "A pit holds", "pit_holds"),
    ("set", r"^pitWidthBodySizeMultiplier$", "Pit must be as wide as the creature", "pit_width"),
    ("set", r"^(pitRelativeClimbEnabled|pitClimbAbilityMultiplier|pitSlowClimbFactor)$", "Climbing by relative height",
     "pit_climb"),
    ("set", r"^(pitRampsEnabled|pitRampMaxSpan)$", "Ramps", "pit_ramp"),
    ("def", r"^ThingDef/RM_PitRamp$", "Pit ramp", "pit_ramp"),
    ("tex", r"Excavation/RM_PitRamp_", "Pit ramp art", "pit_ramp"),
    ("set", r"^(superdeepCapturesOwnFaction|fallDamageEnabled|fallDamageMultiplier)$",
     "Own colonists are not captured; falling hurts", "pit_fall"),
    ("gizmo", r"JumpIntoPit", "Jump into pit button", "pit_ways_in"),
    ("set", r"^superdeepShootingRuleEnabled$", "Shooting only from the lip", "pit_shooting"),
    ("set", r"^(blastsBreakPitCovers|trapTriggerEnabled|trapSensitivityMultiplier)$", "Covers give way", "pit_cover_drop"),
    ("def", r"^ThingDef/RM_PitCover_", "Three pit covers", "pit_cover_drop"),
    ("tex", r"Canals/RM_PitCover_", "Pit cover art", "pit_cover_drop"),
    ("set", r"^(spikesEnabled|spikeDamageMultiplier)$", "Spikes", "pit_spikes"),
    ("def", r"^ThingDef/RM_Spikes$", "Pit spikes", "pit_spikes"),
    ("tex", r"RM_Spikes\.png$", "Spike art", "pit_spikes"),
    ("set", r"^(pitDrowningEnabled|pitDrowningRateMultiplier|poisonFillEnabled)$", "Flooding a pit drowns or poisons",
     "pit_flood"),
    ("def", r"^HediffDef/RM_PitDrowning$", "Drowning", "pit_flood"),
    ("set", r"^slime(SlipEnabled|SlipChanceMultiplier|SlipStunSeconds|ClimbOutSlipFactor)$",
     "Slime slips: nearly uncrossable, slow to climb out of", "flow_slime"),
    # ---- pits: holding
    ("set", r"^(ladderRequiredToExitEnabled|ladderPrisonDoorEnabled|ladderRaiseLowerEnabled|pitLadderSlowness)$",
     "Ladders", "hold_ladder_raised"),
    ("def", r"^ThingDef/RM_Ladder$", "Ladder", "hold_ladder"),
    ("gizmo", r"RMFlow_Ladder", "Ladder up / down button", "hold_ladder_raised"),
    ("tex", r"Canals/RM_Ladder", "Ladder art, lowered and raised", "hold_ladder_raised"),
    ("set", r"^(superdeepRoomsEnabled|captureDownEnabled|wardenFromLipEnabled)$", "A pit prison run from the lip",
     "hold_prison"),
    ("def", r"^JobDef/RM_CaptureDown$", "Capture down from the lip", "hold_prison"),
    ("set", r"^(pitExposureEnabled|pitExposureNarrowing|pitTemperatureCoupling|pitResistanceLossMultiplier)$",
     "Exposure in an open pit", "hold_exposure"),
    ("def", r"^(HediffDef/RM_PitExposure|ThoughtDef/RM_ExposedPrisoner)$", "Exposure and its thought", "hold_exposure"),
    ("set", r"^(flowDoorsSealedFromPitEnabled|sluiceLetsBigThroughEnabled|sluiceGate)", "Sluice and grate doors",
     "hold_gates"),
    ("def", r"^ThingDef/RM_(Sluice|SecurityGrateDoor)$", "Sluice and security grate", "hold_gates"),
    ("tex", r"Doors/RM_\w+_Mover", "Door leaves (open/shut)", "look_parts"),
    ("tex", r"Doors/RM_\w+_MenuIcon", "Door menu icons", "F"),
    ("tex", r"Canals/RM_(Sluice|SecurityGrateDoor)\.png", "Sluice and grate art", "look_parts"),
    # ---- looks
    ("set", r"^(pitDepthDrawOffsetEnabled|pitSinkPerLevel|pitSinkClampEnabled)$", "People sink with depth", "look_sink"),
    ("set", r"^(excavationWallFacesEnabled|excavationWallMaterialEnabled)$", "Wall faces and their material", "look_walls"),
    ("tex", r"Excavation/RM_WallFace_", "Wall face art", "look_walls"),
    ("set", r"^(pitLipOcclusion|pitLipOccupant|pitOutlineEnabled|pitHidesShadowEnabled|pitWalkNormalEnabled)",
     "A pit reads as one dark hole", "look_pit"),
    ("set", r"^(liquidSurfaceMotionEnabled|liquidWakesEnabled|liquidLooksEnabled|liquidBubble|liquidSeeThroughEnabled)",
     "Liquid surfaces: motion, wakes, bubbles", "look_liquids"),
    ("def", r"^FleckDef/RM_Fleck_LiquidBubble$", "Liquid bubbles", "look_liquids"),
    ("def", r"^TerrainDef/RM_Slime(Green|White|Yellow)Deep$", "Slime pools", "look_liquids"),
    # ---- bottles, tanks, pumps, hoses
    ("set", r"^(bottleLoopEnabled|bottleDirtyStageEnabled|bottleRevertEnabled)$", "The bottle loop", "carry_bottles"),
    ("def", r"^(ThingDef/RM_(Bottle_FreshWater|Bottle_Tar|BottleEmpty|BottleDirty|BucketEmpty|BarrelEmpty)|"
     r"ThingCategoryDef/RM_LiquidBottleItems|JobDef/RM_(FillBottleJob|WashBottleJob)|"
     r"WorkGiverDef/RM_(FillBottleWorkGiver|WashBottleWorkGiver))$", "Bottles, buckets, barrels", "carry_bottles"),
    ("def", r"^ThingDef/RM_(Bottle|Bucket|Barrel)(_|Dirty)", "Every liquid in every container", "containers_all"),
    ("def", r"^ThingStyleDef/RM_(Bottle|Bucket|Barrel)_(Scrapper|Industrial|Modern|Futuristic)$", "Containers in the four looks",
     "containers_styles"),
    ("tex", r"Item/Resource/FlowWorks/(Scrapper|Industrial|Modern|Futuristic)/", "Container art in the four looks", "containers_styles"),
    ("tex", r"Item/Resource/FlowWorks/RM_WaterBottle", "Coloured water bottle art", "many_waters"),
    ("tex", r"Item/Resource/FlowWorks/", "Container art", "carry_bottles"),
    ("def", r"^RecipeDef/RM_Make_", "Container recipes in each material", "carry_containers"),
    ("set", r"^(tankLoopEnabled|tankCapacityMultiplier)$", "Tank capacity", "tank_sizes"),
    ("def", r"^ThingDef/RM_(LiquidTankTall|UniversalCargoTankXTall)$", "Tall and extra-tall tanks", "tank_sizes"),
    ("tex", r"RM_(LiquidTankTall|UniversalCargoTankXTall)\.png$", "Tall tank art (placeholder)", "tank_sizes"),
    ("def", r"^ThingDef/RM_(LiquidTank|UniversalCargoTank|LiquidPump)$", "Tank, cargo tank, pump", "carry_tanks"),
    ("tex", r"RM_(LiquidTank|UniversalCargoTank|LiquidPump)\.png$", "Tank and pump art", "carry_tanks"),
    ("set", r"^liquidPumpEnabled$", "Pumps", "carry_tanks"),
    ("set", r"^pumpFedSpreadEnabled$", "A pump pours into canals", "pump_pour"),
    ("gizmo", r"RMFlow_PumpMode", "Pump Draw / Pour button", "pump_pour"),
    ("def", r"^(JobDef|WorkGiverDef)/RM_(EmptyIntoTank|FillFromTank)", "Tank jobs", "tank_modes"),
    ("gizmo", r"RMFlow_TankMode", "Tank mode button", "tank_modes"),
    ("set", r"^(enabled|tankModesEnabled|tankLitresPerCycle)$", "Hoses on; tank modes", "tank_modes"),
    ("def", r"^ThingStyleDef/RM_(LiquidTank|LiquidTankTall)_", "Tank looks", "tank_styles"),
    ("def", r"^ThingStyleDef/RM_(UniversalCargoTank|UniversalCargoTankXTall)_", "Cargo tank looks", "tank_styles_cargo"),
    ("def", r"^ThingStyleDef/RM_HoseReel_", "Hose reel looks", "hose_styles"),
    ("set", r"^defaultLook$", "Default hose reel look", "hose_styles"),
    ("tex", r"FlowWorks/Hose/Styles/", "Hose reel look art", "hose_styles"),
    ("def", r"^(ThingDef/RM_HoseReel|JobDef/RM_(CarryHoseEnd|RetractHose)|WorkGiverDef/RM_HoseOrders)$",
     "Hose reel and its jobs", "hose_reel"),
    ("tex", r"FlowWorks/Hose/", "Hose, reel and fitting art", "hose_reel"),
    ("gizmo", r"Choose style", "Choose style button", "pipe_styles"),
    ("gizmo", r"(hose|Hose|Fitting|Free end|DEV:)", "Hose reel buttons", "hose_reel"),
    ("set", r"^(freeEndRolesEnabled|dumpLitresPerCycle|minBendRadius|plumpAmount|transitionTicks|releaseTicks|minPlumpDwell|"
     r"maxLength|maxLengthDefaults|couplingSpacing|handlingTime|windCellsPerSecond|autoResumeDroppedHose|slack|"
     r"tintByContents|fillWobble|thickness)$", "Hose behaviour and look", "hose_reel"),
    ("set", r"^(pipeLinksIntoMachines|joinFittings)$", "Pipe-to-machine joins and connector fittings",
     M + "art only, and the connector art awaits the owner's ruling on design/RimMandrake/liquid_connections_visuals_2026-10-16.md; stage it once ruled"),
    ("set", r"^waterBodyTypeFlipFixEnabled$", "Water-body count fix",
     M + "fixes vanilla bookkeeping when water changes type; nothing on the map to look at"),
    ("set", r"^(hoseHoldsLiquid|hoseLitresPerCell|litresPerFilth)$", "A hose holds liquid and spills it", "liquid_spill"),
    ("def", r"^ThingDef/RM_Filth_", "Spilled liquid and tracked tar", "liquid_spill"),
    ("tex", r"Filth/RM_FilthTar", "Tar filth art", "liquid_spill"),
    ("def", r"^(ThingDef/RM_UniversalPipe|ThingStyleDef/RM_UniversalPipe_|DesignationCategoryDef/VCHE_PipeNetworks)",
     "Rigid pipe, its looks and its menu tab", "pipe_styles"),
    ("tex", r"FlowWorks/Pipe/", "Pipe look art", "pipe_styles"),
    ("set", r"^(universalPipesEnabled|pipeDefaultLook)$", "Pipes and their default look", "pipe_styles"),
    ("def", r"RM_PipeAdapter_", "Pipe-net adapters", "pipe_adapter"),
    ("tex", r"RM_PipeAdapter_", "Adapter art", "pipe_adapter"),
    ("gizmo", r"RMFlow_AdapterMode", "Adapter mode button", "pipe_adapter"),
    ("set", r"^pipeAdaptersEnabled$", "Adapters", "pipe_adapter"),
    ("set", r"^liquidTheft", "Liquid theft",
     M + "needs another faction's tank in sight and goodwill to lose; the matrix stages it (A7 of the liquid ledger)"),
    ("def", r"^HistoryEventDef/RM_LiquidTheftCaught$", "Liquid theft caught", M + "as liquid theft"),
    ("def", r"^ThingDef/RM_(LiquidDrill|LiquidTap|SunPanStill|DripFilter|FueledStill)$", "Drills, taps and stills",
     "carry_drills"),
    ("tex", r"Machinery/RM_(LiquidDrill|LiquidTap|SunPanStill|DripFilter|FueledStill)", "Drill and still art",
     "carry_drills"),
    ("set", r"^(liquidDrillingEnabled|drillYieldChanceMultiplier|drillUnitsPerCycle)$", "Drilling", "carry_drills"),
    ("def", r"^ThingDef/RM_\w+_Wrecked$", "Four wrecked liquid plants", "carry_industry"),
    ("tex", r"Machinery/RM_\w+_Wrecked", "Wreck art", "carry_industry"),
    ("def", r"^ThingDef/RM_DesalPlant_", "Desal plant stages", "industry_stages"),
    ("tex", r"Machinery/RM_DesalPlant_", "Desal stage art", "industry_stages"),
    ("def", r"^ThingDef/RM_(DetoxWorks|TarRefinery|PumpingStation)_(Kludged|Repaired)$", "The other plants, mended",
     "industry_stages_more"),
    ("tex", r"Machinery/RM_(DetoxWorks|TarRefinery|PumpingStation)_", "Mended plant art", "industry_stages_more"),
    ("set", r"^(liquidWorksRuinsEnabled|liquidWorksRuinStockEnabled|industrialWorksBuildAnywhere|converterRateMultiplier)$",
     "Liquid works ruins and converters", "carry_industry"),
    ("def", r"^GenStepDef/RM_\w+_RuinScatter$", "Ruins scattered on new maps",
     M + "map generation only; no player generates a map (the one fixed world), so the review shows the ruins built"),
    ("def", r"^(ThingDef/RM_ReactionVat|RimMandrake\.FlowWorks\.Machinery\.Kits\.RM_LiquidReactionDef/)", "Reaction vat",
     "carry_kits"),
    ("tex", r"Machinery/RM_ReactionVat", "Vat art", "carry_kits"),
    ("set", r"^(liquidBathRecipesEnabled|liquidReactionsEnabled|reactionRateMultiplier|hotLiquidEnabled|"
     r"hotLiquidBurnMultiplier|fluidResidueEnabled)$", "Liquid kits", "carry_kits"),
    ("set", r"^legacy$", "Legacy machinery migration", M + "acts only on an old save"),
    ("set", r"^hoseSettingsImported$", "Hose settings import flag", M + "internal one-time migration flag, not a mechanic"),
    # ---- land
    ("def", r"^TerrainDef/RM_(WaterBrine|WaterBoiling|Propane|Acid|Tar|SlimeRed)Deep$", "Liquid grounds", "land_liquids"),
    ("def", r"^TerrainDef/RM_(WaterFrigid|WaterBrackish|WaterMineral|WaterPoisoned|Ammonia|Coolant)Deep$",
     "Six more liquid grounds", "land_liquids_2"),
    ("def", r"^TerrainDef/RM_((FuelSap|Ichor|Ooze|ReactionLiquor)Deep|Churnmud|TarGlass)$", "Odd grounds", "land_liquids_3"),
    ("def", r"^TerrainDef/RM_WaterBoilingShallow$", "Boiling shallows", "land_shores"),
    ("def", r"^TerrainDef/RM_Slime(Green|White|Yellow)Shallow$", "Shallow slime edges", "look_liquids"),
    ("def", r"^TerrainDef/RM_(WaterBrine|WaterBoiling|Propane|Acid|Tar|SlimeRed)Shallow$", "Shallow rims", "land_liquids"),
    ("def", r"^TerrainDef/RM_(WaterFrigid|WaterBrackish|WaterMineral|WaterPoisoned|Ammonia|Coolant)Shallow$",
     "Shallow rims", "land_liquids_2"),
    ("def", r"^TerrainDef/RM_(FuelSap|Ichor|Ooze|ReactionLiquor)Shallow$", "Shallow rims", "land_liquids_3"),
    ("def", r"^(RimMandrake\.FlowWorks\.LiquidTypes\.LiquidDef/|RimMandrake\.FlowWorks\.LiquidTypes\.RM_LiquidBodyDef/)",
     "Liquid registry and named world bodies (the Scald, the Grey Sea...)",
     M + "registry data with no thing of its own; its liquids are the grounds at the land stations, its bodies are "
     "world-map tags"),
    ("def", r"^RM_Liquid_", "Liquid registry rows added by a patch (astrofuel)", M + "as the liquid registry"),
    ("def", r"^GenStepDef/RM_LiquidShores$", "Typed liquid shores", M + "map generation only (the shores of a new map)"),
    ("set", r"^typedLiquidShoresEnabled$", "Typed shores", M + "map generation only"),
    ("set", r"^(liquidHeatPushEnabled|liquidHeatStrength)$", "Hot liquid warms the air", "land_shores"),
    ("def", r"^(TerrainDef/RM_(Water|Slime)_|(ThingDef/)?RM_(Bottle|Bucket|Barrel)_(Rust|Verdigris|Amber|Violet|Chalk)Water$)",
     "Coloured waters and slimes", "many_waters"),
    # RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW (2026-10-16): its settings section had no coverage row
    ("set", r"^(riverColorsEnabled|headwaterColor|jungleColor|terminusColor)$", "River colours",
     M + "the planet-map river gradient, read on the world map"),
    # THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY: behaviour with no look of its own (a need bar, a hediff, jobs)
    ("def", r"^(NeedDef/RM_Thirst|HediffDef/RM_Dehydration|ThoughtDef/RM_Thought_(Thirsty|Parched|Dehydrated|DrankDistilled)"
            r"|JobDef/RM_(DrinkFromTerrain|DrinkFromTank|AdministerWater)|WorkGiverDef/RM_AdministerWater(Prisoner)?"
            r"|ThinkTreeDef/RM_Thirst\w+)$",
     "Thirst (need, dehydration, drinking jobs)", M + "behaviour with no look of its own; proven by validation.py's thirst chain"),
    ("set", r"^(thirstEnabled|thirstRateMultiplier|thirstHeatScaling|animalsGetThirst|drinkFromTerrain|waterQualityEffects"
            r"|dbhBottleBridge)$", "Thirst", M + "as thirst"),
    # SPRINKLER_HEADS_BUILD_PUMP_REQUIRED: no frozen station yet (a head needs a pump net and an hour of game time to show
    # anything); proven by validation.py's sprinkler rows (owed live), art on its own review sheet
    ("def", r"^(ThingDef/RM_SprinklerHead|ThingStyleDef/RM_SprinklerHead_\w+|ThingDef/RM_Mote_SprinklerSpray)$",
     "Sprinkler heads on pipes", M + "no station yet; a pump net plus an hour of spray (validation.py sprinkler rows, owed live)"),
    ("set", r"^(sprinklersEnabled|sprinklerLitresPerCellHour|sprinklerNativeRadius|sprinklerNonWaterEffects|vfeSprinklerAdapterEnabled"
            r"|vfeThirstValve)$", "Sprinkler heads on pipes", M + "as sprinkler heads"),
    ("gizmo", r'^"(Daily budget|Reserve floor): " \+', "Sprinkler heads on pipes", M + "VFE sprinkler valve gizmos (needs VFE Farming)"),
    ("tex", r"FlowWorks/Sprinkler/", "Sprinkler heads on pipes", M + "art on its own true-scale review sheet"),
    ("def", r"^FleckDef/RM_Fleck_Steam_", "Coloured river steam", M + "rises only off a RIVER of a coloured water; no "
     "generated map here has one"),
    ("set", r"^(riverSteamEnabled|puffRateMultiplier)$", "River steam", M + "as coloured river steam"),
    ("def", r"^TerrainDef/RM_DeepSand$", "Deep sand", "land_deepsand"),
    ("def", r"^ThingDef/RM_Swale$", "Swale", "land_swale"),
    ("tex", r"Canals/RM_Swale", "Swale art", "land_swale"),
    ("set", r"^swale", "Swale", "land_swale"),
    # ---- rivers: looks on the main map, mechanics on map R
    ("def", r"^(TerrainDef/RM_FordStones|TerrainAffordanceDef/RM_Fordable)$", "Ford stones", "river_ford"),
    ("tex", r"Surfaces/RM_FordStones", "Ford stone art", "river_ford"),
    ("tex", r"Rivers/RM_FerryRope", "Ferry rope art (drawn only between paired posts)", "R:r_ferry"),
    ("tex", r"Rivers/RM_(SluiceBox|PanningSpot)", "Sluice box and panning art", "land_panning"),
    ("tex", r"Rivers/", "Bank works art", "river_works_looks"),
    ("tex", r"FlowWorks/Weir/", "Weir art: four looks, per heading, joined wall, water overlay", "river_works_looks"),
    ("def", r"^ThingStyleDef/RM_BankWeir_(Scrapper|Industrial|Modern|Futuristic)$", "Weir looks", "river_works_looks"),
    ("def", r"^ThingDef/RM_(BankWeir|BankStake|SiltTrap|FerryPost)$", "Bank works", "river_works_looks"),
    ("def", r"^(ThingDef/RM_(SluiceBox|PanningSpot)|JobDef/RM_PanForPlacerJob|WorkGiverDef/RM_PanForPlacer)$",
     "Sluice box and panning", "land_panning"),
    ("def", r"^RimMandrake\.FlowWorks\.Quarry\.RM_PlacerPoolDef/", "River placer minerals", "R:r_placer"),
    ("set", r"^(sluiceBoxEnabled|panningEnabled|placerFloodRefill|placerStockPercent|sluiceYieldMultiplier|"
     r"panningYieldMultiplier)$", "Placer mining", "R:r_placer"),
    ("def", r"^RimMandrake\.FlowWorks\.Rivers\.RM_RiverDriftDef/", "River drift by biome", "R:r_weir"),
    ("set", r"^(riverWorksEnabled|surfaceCurrentEnabled|currentStrength|centreTicksPerCell|marginTicksPerCell|"
     r"itemDriftFactor|scaleWithRiverSize|carryAnimals|carryStrangers|carryItems|washOffMapEdge|washedAwayM..Days|"
     r"takenByLandTraceEnabled|crossingHazardsEnabled|bruiseChancePerStep|dropChancePerStep)$",
     "The current carries and sweeps away", "R:r_current"),
    ("set", r"^(fordsEnabled|pathfinderAvoidsCurrents)$", "Fords and route-finding round currents", "R:r_ford"),
    ("set", r"^(bankWorksEnabled|wearRateMultiplier|weirPoolLength|weirCatchesFish|weirCatchIntervalHours|weirHeldCatchCap|"
     r"weirCatchesDrift|weirDriftChance)$", "Weir pool and catch", "R:r_weir"),
    ("set", r"^(breachEnabled|breachHpFraction|breachWashesCatch|breachWashCells|floodSurgeEnabled|countSeasonalFloods|"
     r"countTorrentialRainFloods)$", "Floods and breaches", "R:r_breach"),
    ("set", r"^(stakeSnapTicksPerCell|stakeLineLevee)$", "Stake-line levee", "R:r_stakes"),
    ("set", r"^silt", "Silt trap", "R:r_silt"),
    ("set", r"^ferry", "Ferry rope", "R:r_ferry"),
]


# ------------------------------------------------------------------------------------------------ inventory
def _src_files(ext, root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ("bin", "obj", "__pycache__", "SelfTest")]
        for f in fn:
            if f.endswith(ext):
                yield os.path.join(dp, f)


def inventory(mod=HERE):
    """-> [(kind, name, source)] derived from the mod's files."""
    items, seen = [], set()

    def add(kind, name, src):
        if (kind, name) not in seen:
            seen.add((kind, name))
            items.append((kind, name, src))
    for p in sorted(glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True)):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            add("def", "UNPARSEABLE/" + os.path.relpath(p, mod), p)
            continue
        for d in root:
            if isinstance(d.tag, str) and d.get("Abstract", "").lower() != "true" and d.findtext("defName"):
                add("def", "%s/%s" % (d.tag, d.findtext("defName")), os.path.relpath(p, mod))
    defined = {n.split("/", 1)[1] for k, n, _ in items}
    for p in sorted(glob.glob(os.path.join(mod, "Patches", "**", "*.xml"), recursive=True)):
        txt = re.sub(r"<!--.*?-->", " ", open(p, encoding="utf-8", errors="replace").read(), flags=re.S)
        for dn in re.findall(r"<defName>(RM_\w+)</defName>", txt):
            if dn not in defined and "<value>" in txt:
                add("def", "patch-added/%s" % dn, os.path.relpath(p, mod))
    rx = re.compile(r'Scribe_Values\.Look\(ref (\w+),')
    for p in sorted(_src_files(".cs", os.path.join(mod, "Source"))):
        b = os.path.basename(p)
        if "Settings" in b or b == "RimMandrakeFlowWorksMod.cs":
            txt = open(p, encoding="utf-8", errors="replace").read()
            for f in rx.findall(txt):
                add("set", f, os.path.relpath(p, mod))
    grx = re.compile(r'defaultLabel\s*=\s*([^;\n]+)')
    for p in sorted(_src_files(".cs", os.path.join(mod, "Source"))):
        for g in grx.findall(open(p, encoding="utf-8", errors="replace").read()):
            add("gizmo", g.strip().rstrip(",").strip(), os.path.relpath(p, mod))
    for p in sorted(glob.glob(os.path.join(mod, "Textures", "**", "*.png"), recursive=True)):
        add("tex", os.path.relpath(p, os.path.join(mod, "Textures")).replace(os.sep, "/"), "Textures")
    return items


def classify(items, rules=FEATURES):
    """-> ({rule index: [item]}, [uncovered item])."""
    got, unc = {}, []
    for it in items:
        k, name = it[0], it[1]
        if name.startswith("patch-added/"):
            name = name.split("/", 1)[1]
        for i, (kind, rx, _, _) in enumerate(rules):
            if kind == k and re.search(rx, name):
                got.setdefault(i, []).append(it)
                break
        else:
            unc.append(it)
    return got, unc


def where(target, num, river_ids):
    """A rule's target -> its place on the map, as the owner reads it."""
    if target.startswith("matrix: "):
        return "no station", target[len("matrix: "):]
    if target == "V":
        return "V", "the pits visuals block"
    if target == "F":
        return "F", "the Architect menu, in the free area"
    if target.startswith("R:"):
        i = target[2:]
        return ("R%d" % (river_ids.index(i) + 1)) if i in river_ids else "R?", "map R"
    return ("%d" % num[target]) if target in num else "?", ""


def check_targets(S, river_ids, rules=FEATURES):
    """Every rule names a station that exists (a renamed station must not leave a row pointing nowhere)."""
    ids = {s["id"] for s in S}
    bad = []
    for kind, rx, feat, t in rules:
        if t.startswith("matrix: ") or t in ("V", "F"):
            continue
        if t.startswith("R:"):
            if t[2:] not in river_ids:
                bad.append("%s -> %s" % (feat, t))
        elif t not in ids:
            bad.append("%s -> %s" % (feat, t))
    return bad


def write(S, path=OUT, items=None):
    import review_map_rivers as RV
    river_ids = [s["id"] for s in RV.STATIONS]
    items = inventory() if items is None else items
    got, unc = classify(items)
    bad = check_targets(S, river_ids)
    num = {s["id"]: s["n"] for s in S}
    kinds = ("def", "set", "gizmo", "tex")
    count = {k: sum(1 for it in items if it[0] == k) for k in kinds}
    shown = set(num) & {r[3] for r in FEATURES}
    no_station = [s for s in S if s["id"] not in shown]
    md = ["# FlowWorks review map - feature coverage", "",
          "Generated by `review_map.py --plan` from `review_map_coverage.py` (inventory read off disk; feature rules "
          "there). Do not hand-edit: change the rules or the stations and re-plan.", "",
          "## Live build (one driver, the 22-mod `ratchet_pilot` tier, bridge held, game Playing)", "", "```"]
    md += LIVE_CMD + ["```", "", "Expected runtime: " + RUNTIME.format(n=len(S)), "",
                      "Then `review_map.py --goto N` (or `--rivers --goto R3` on the river save) frames a station; "
                      "`--labels` / `--rivers --labels` re-pin labels after a load.", "",
                      "## Which file is the live review map", "",
                      "`review_map.py` is the live map builder (`--plan/--build/--goto/--labels/--clear/--save`, and "
                      "`--rivers` for map R in `review_map_rivers.py`). `human_review.py` is NOT a second map: it is the "
                      "feature sheet (browser) and the status data layer `review_map.py` reads, so no consolidation was "
                      "needed; the method doc's per-mod `human_review.py` builder role is `review_map.py` here.", "",
                      "## Rivers: a separate map", "",
                      "Every river mechanic reads the river current, which is copied from the map's river flow map, which "
                      "only map generation writes. Painted river ground (the main map) has no current: a weir never pools, "
                      "nothing is carried, a ferry rope never matters, a flood breaches nothing. So the main map keeps the "
                      "bank works as LOOKS (stations `river_ford`, `river_works_looks`, `land_panning`, labelled so), and "
                      "the mechanics are map R: `northstar/river_site.py` founds a colony on a river tile, then "
                      "`review_map.py --rivers --build` anchors eight stations on that river's real crossings "
                      "(`review_map_rivers.river_anchors`) and saves a second keeper. river_site.py vanishes the main "
                      "map's colonists, so the main save is written first.", "",
                      "## Counts", "",
                      "Inventory: %d defs, %d Mod Settings fields, %d gizmo labels, %d textures = %d items, grouped into "
                      "%d features. Stations: %d on the main map + %d on map R + the V block (39 plots). Uncovered items: "
                      "**%d**. Rule targets that name no station: **%d**." % (
                          count["def"], count["set"], count["gizmo"], count["tex"], len(items), len(got),
                          len(S), len(river_ids), len(unc), len(bad)), ""]
    if unc:
        md += ["## UNCOVERED (add a rule or a station)", ""] + ["- %s `%s` (%s)" % it for it in unc] + [""]
    if bad:
        md += ["## Rules pointing at no station", ""] + ["- " + b for b in bad] + [""]
    md += ["## Feature inventory -> station", "",
           "| # | feature | kind | station | items | source |", "|---|---|---|---|---|---|"]
    matrix = []
    for i, (kind, rx, feat, t) in enumerate(FEATURES):
        its = got.get(i, [])
        if not its:
            continue
        st, note = where(t, num, river_ids)
        names = ", ".join(sorted(it[1].split("/")[-1] for it in its))
        if len(names) > 300:
            names = names[:300] + " ... (%d in all)" % len(its)
        srcs = ", ".join(sorted({it[2] for it in its}))[:120]
        md.append("| %d | %s | %s | %s | %s | %s |" % (i + 1, feat, kind, st if st != "no station" else "-",
                                                        names.replace("|", "/"), srcs.replace("|", "/")))
        if st == "no station":
            matrix.append((feat, len(its), note))
    md += ["", "## Features with no station (and why)", ""]
    md += ["- **%s** (%d items): %s" % m_ for m_ in matrix] + [""]
    md += ["## Stations whose feature is shown by setup alone", "",
           "These stations exist for a feature-sheet FEATURE or a staged mechanism the rules above do not name by an "
           "inventory item (a mechanism made of code paths, not defs): " +
           ", ".join("%d %s" % (s["n"], s["id"]) for s in no_station) + ".", ""]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    return dict(path=path, items=len(items), features=len(got), uncovered=len(unc) + len(bad),
                matrix=len(matrix))
