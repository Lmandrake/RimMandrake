#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 🔴 FROZEN 2026-08-16. The owner has finished selecting world-map elements and his
# decisions live in design/Jawa/worldbuilding/review/worldmap_elements.prefill.json
# (296 keep / 52 NO / 2 deliberately left to be stripped).
# THIS SCRIPT WOULD OVERWRITE THEM WITH CHECK'S ORIGINAL GUESSES. It now refuses to
# run unless you pass --i-know-this-overwrites-the-owners-decisions.
import sys as _sys
if "--i-know-this-overwrites-the-owners-decisions" not in _sys.argv:
    _p = "design/Jawa/worldbuilding/review/worldmap_elements.prefill.json"
    print("REFUSING: %s is FROZEN (owner, 2026-08-16)." % _p)
    print("Re-run with --i-know-this-overwrites-the-owners-decisions to replace his calls.")
    raise SystemExit(1)
"""Pre-fill the world-map curation decisions for the Jawa desert planet.

    python3 src/RimMandrake/Utils/worldmap_prefill.py
    ->  design/Jawa/worldbuilding/review/worldmap_elements.prefill.json
    then re-run worldmap_review.py to bake it into the sheet.

🔑 The point is that the owner REVIEWS rather than decides. Every one of the 449
defs already carries a keep/cut call and a note saying WHERE on the planet it
belongs, so his job is to disagree with the ones that are wrong.

The brief the calls were made against:
  Tatooine-like Star Wars desert world. A Jawa scavenger clan: salvage, trade,
  and fleeing the Empire across long distances. Tone is SERIOUS - a dusty,
  lived-in, hard-scrabble Outer Rim world - with ONE exemption, the owner's:
  "save for Jawa slapstick". Comedy that belongs to the Jawas themselves
  (scrap, junk, hoarding, sandcrawler life) is welcome; whimsy that is not
  Jawa-flavoured is not. The world has oceans (~17% water), has Geonosians as a
  faction, and may be tidally locked - permanent day side, night side, and a
  habitable terminator ring, which is why night-side ice content is KEPT.
  🔴 VOLCANISM IS ACTIVE (owner, 2026-08-16): no plate tectonics means mantle
  plumes never migrate, so hotspots build sustained volcanic provinces. Lava,
  magma and volcano content is KEPT. Only the occult "vent" content stays out.

🔴 Posture is WHITELIST: reject and undecided both strip. `rej` here means "I
looked and the answer is no"; the handful of genuinely open calls are left
undecided ON PURPOSE, each with a note starting "UNSURE:", so they stand out.

One structural limit worth knowing: the sheet keys state by defName, and 99 of
the 449 rows are a mutator and a landmark SHARING a defName (Odyssey pairs each
landmark with the mutator it forces). One decision therefore covers both rows -
which is correct, since they are the same feature, but it means you cannot keep
the mutator while rejecting its landmark.
"""
import json, pathlib, re, sys

REPO = pathlib.Path("/mnt/d/Luke/dev/Rimworld")
HTML = REPO / "design/Jawa/worldbuilding/review/worldmap_elements.html"
OUT  = REPO / "design/Jawa/worldbuilding/review/worldmap_elements.prefill.json"

K = "keep"; R = "rej"; U = ""      # U = deliberately left undecided

# defName -> (state, note).  One entry covers both the mutator and the
# landmark row when they share a defName - the sheet keys state by defName.
D = {

# ---------------------------------------------------------------- Alpha Biomes
"AB_ExtremeTemperatureFluctuations": (K, "deep desert - scorching day, freezing night"),
"AB_AmbientRadiation":      (K, "old crash sites and Imperial installations"),
"AB_FeraliskNest":          (K, "canyon country - giant arachnid dens"),
"AB_DunealiskNest":         (K, "deep desert - sand-burrowing predators"),
"AB_BlizzariskNest":        (K, "night side - the frozen hemisphere"),
"AB_BumbledroneNests":      (R, "cutesy giant bees - whimsy that is not Jawa"),
"AB_AncientFreezingVent":   (K, "night side - buried machinery venting cold"),
"AB_AncientGreyPallVent":   (K, "derelict Imperial industry - toxic exhaust"),
"AB_AncientDeathPallVent":  (R, "necromantic pall - occult, not Star Wars"),
"AB_AncientBloodRainVent":  (R, "blood rain - occult horror"),
"AB_ExplodingAnimals":      (R, "cartoon physics - breaks the serious tone"),
"AB_TechnoTrees":           (R, "half-synthetic forest - wrong for a desert world"),
"AB_LuminescentTrees":      (R, "glowing trees - fantasy lushness"),
"AB_DessertTrees":          (R, "candy trees - owner named these out"),
"AB_FleshTrees":            (R, "flesh trees - body-horror fantasy"),
"AB_GoldenTrees":           (R, "golden cube trees - pure whimsy"),
"AB_OcularTransformation":  (R, "eyeball forest - body-horror fantasy"),
"AB_DiminutiveRegion":      (K, "tight canyon pockets - cramped 100x100 sites"),
"AB_NarrowRegion":          (K, "slot canyons and ravine corridors"),
"AB_WideRegion":            (K, "long dune ridges and salt flats"),
"AB_DerelictArchonexus":    (K, "deep desert - ancient alien ruins"),
"AB_SterileGround":         (K, "salt flats and hardpan - nothing grows"),
"AB_DerelictBioLab":        (K, "remote desert - an Imperial black-site lab"),
"AB_AgariluxPrime_Mutator": (R, "mycotic spore-lord - jungle content"),
"AB_ButterflySwarms":       (R, "gentle temperate whimsy"),
"AB_DerelictClusters":      (K, "crash fields - prime Jawa salvage"),
"AB_DerelictKemeticTemple": (K, "deep desert - ancient tomb temple"),
"AB_DerelictResort":        (K, "coastal - an abandoned Hutt pleasure resort"),
"AB_DigestiveSurface":      (R, "living digestive ground - fantasy"),
"AB_EdibleAirborneMicrofungi": (R, "airborne edible spores - wrong climate"),
"AB_GelatinousMemoryEcho":  (R, "living memory lattice - fantasy"),
"AB_GeothermalHotspots":    (K, "hotspot uplands - colony power sites"),
"AB_GiantFossils":          (K, "deep desert - krayt dragon bones in the sand"),
"AB_HealingSprings":        (U, "UNSURE: curative spring reads mystical - keep only if reskinned as a mineral spa"),
"AB_LocustPlagues":         (K, "terminator farm belt - swarms strip the crops"),
"AB_MagmaVents":            (K, "hotspot volcanism - fixed plumes, no plate drift"),
"AB_MagmaticQuagmire":      (K, "hotspot volcanism - molten ground near the plumes"),
"AB_MoldyEnvironment":      (R, "fungal humidity - wrong climate"),
"AB_MutagenicSprings":      (R, "ocular mutagen - body-horror fantasy"),
"AB_OversaturatedSoil":     (K, "oasis floors - the only rich soil on the planet"),
"AB_PetalStorms":           (R, "petal storms - temperate whimsy"),
"AB_PollinationFrenzy":     (R, "temperate pollen bloom"),
"AB_PropaneLakes":          (R, "physics-defying gag lakes"),
"AB_QuicksandPits":         (K, "deep desert - sinking sand between the dunes"),
"AB_QuiveringSurface":      (R, "living ground - fantasy"),
"AB_ResidualOverclocking":  (K, "old droid battlefields - scavengeable power"),
"AB_SymbioticNutrients":    (R, "free-nutrition magic"),
"AB_TarLakes":              (K, "deep desert tar pits - bones and salvage"),

# ------------------------------------------------------------------------ Core
"Coast":            (K, "the world's shorelines - 17% of it is ocean"),
"Mountain":         (K, "mesas and ranges - the planet's spine"),
"Caves":            (K, "canyon country - Jawa shelter and Tusken lairs"),
"UndergroundCave":  (K, "the deep cave network under the mesas"),
"River":            (K, "rare - the terminator ring only"),

# ------------------------------------------------------------- Biome / Designer
"GL_BiomeTransitions": (K, "technical - blends biome borders, keep for smooth edges"),
"ZMD_NoMutator":       (K, "technical - Map Designer's empty slot, not content"),

# ------------------------------------------------- Dark Ages: Beasts & Monsters
"DA_LeviathanNest":          (K, "coastal shallows - large sea beasts"),
"DA_SnaptoadBreedingGrounds":(R, "wetland amphibians - no swamps on this world"),
"DA_SnaptoadSpawningPools":  (R, "wetland spawning pools - wrong world"),

# ------------------------------------------------------- Geological Landforms
"GL_Archipelago":    (K, "offshore island chains"),
"GL_Atoll":          (K, "ring reefs offshore"),
"GL_Badlands":       (K, "canyon country - eroded badlands"),
"GL_Caldera":        (K, "caldera in the volcanic highlands"),
"GL_Canyon":         (K, "canyon country - sandcrawler routes"),
"GL_CaveEntrance":   (K, "cave mouths in the mesa walls"),
"GL_Cirque":         (K, "night side - glacially carved bowls"),
"GL_Cliff":          (K, "mesa escarpments"),
"GL_CliffAndCoast":  (K, "sea cliffs"),
"GL_CliffCorner":    (K, "mesa escarpments"),
"GL_Coast":          (K, "shoreline"),
"GL_CoastCorner":    (K, "shoreline"),
"GL_CoastalIsland":  (K, "offshore island"),
"GL_Cove":           (K, "sheltered coves - smuggler landings"),
"GL_CoveWithIsland": (K, "sheltered cove with a rock"),
"GL_Crater":         (K, "impact craters in the deep desert"),
"GL_DesertPlateau":  (K, "the high desert plateau - core terrain"),
"GL_DryLake":        (K, "dry lakebeds and salt pans"),
"GL_Fjord":          (K, "night side - glacial sea inlets"),
"GL_Glacier":        (K, "night side - permanent ice"),
"GL_Gorge":          (K, "canyon country"),
"GL_IceOasis":       (K, "night side - meltwater ice oasis"),
"GL_Island":         (K, "offshore island"),
"GL_Lake":           (K, "rare - terminator ring lakes"),
"GL_LakeWithIsland": (K, "rare - terminator ring lakes"),
"GL_Landbridge":     (K, "land bridge between two coasts"),
"GL_LoneMountain":   (K, "a lone peak out on the flats"),
"GL_Oasis":          (K, "oasis - the only green in the deep desert"),
"GL_Peninsula":      (K, "coastal headland"),
"GL_Rift":           (K, "the great rift - deep desert"),
"GL_River":          (K, "rare - terminator ring rivers"),
"GL_RiverConfluence":(K, "rare - terminator ring rivers"),
"GL_RiverDelta":     (K, "where the few rivers meet the sea"),
"GL_RiverIsland":    (K, "rare - terminator ring rivers"),
"GL_RiverSource":    (K, "springs in the terminator highlands"),
"GL_RiverTerrain":   (K, "technical - river bank terrain"),
"GL_SecludedCove":   (K, "hidden cove - smuggler landing"),
"GL_SecludedValley": (K, "hidden valley - a Jawa fortress site"),
"GL_Sinkhole":       (K, "sinkholes down into the cave network"),
"GL_Skerry":         (K, "rocky offshore skerries"),
"GL_SurfaceCave":    (K, "cave mouths in the rock"),
"GL_SwampHill":      (R, "swamp - wrong world"),
"GL_Tombolo":        (K, "sand spit out to an offshore rock"),
"GL_Valley":         (K, "valleys between the mesas"),

# --------------------------------------------------------------------- Odyssey
"MixedBiome":            (K, "biome boundaries - everywhere"),
"SunnyMutator":          (K, "day side - twin suns, cloudless"),
"AnimalHabitat":         (K, "wherever the local fauna concentrates"),
"AnimalLife_Increased":  (K, "oases and the terminator belt"),
"AnimalLife_Decreased":  (K, "deep desert - almost nothing lives here"),
"WildPlants":            (K, "scrub wherever there is any moisture"),
"SteamGeysers_Increased":(K, "geothermal fields - colony power"),
"DryGround":             (K, "deep desert - no standing water anywhere"),
"PlantGrove":            (K, "oasis groves"),
"Fertile":               (K, "rare fertile pockets near the terminator"),
"WetClimate":            (K, "coastal fringe and terminator belt only"),
"PlantLife_Decreased":   (K, "most of the planet"),
"PlantLife_Increased":   (K, "oases and the terminator belt"),
"Junkyard":              (K, "Jawa heartland - the scrap fields"),
"FoggyMutator":          (K, "coastal sea fog at dawn"),
"Sandy":                 (K, "everywhere - this is the Dune Sea"),
"Muddy":                 (K, "oasis margins and river banks only"),
"Marshy":                (R, "marshland - no wetlands on this world"),
"RiverIsland":           (K, "rare - terminator ring rivers"),
"Headwater":             (K, "spring source in the terminator highlands"),
"CoastalAtoll":          (K, "offshore atoll"),
"CoastalIsland":         (K, "offshore island"),
"Hollow":                (K, "cliff-ringed hollow - a good hideout"),
"HotSprings":            (K, "geothermal springs in the uplands"),
"MineralRich":           (K, "the mining belt - ore worth digging"),
"Oasis":                 (K, "oasis - the deep desert's lifeline"),
"Stockpile":             (K, "buried ancient cache - the Jawa jackpot"),
"WindyMutator":          (K, "open flats and dune seas"),
"AbandonedColonyOutlander": (K, "abandoned moisture-farm homesteads"),
"AbandonedColonyTribal": (K, "abandoned Tusken-style camps"),
"AncientChemfuelRefinery": (K, "derelict Imperial fuel refinery"),
"AncientGarrison":       (K, "abandoned Imperial garrison"),
"AncientHeatVent":       (K, "day side - buried machinery venting heat"),
"AncientInfestedSettlement": (K, "settlement overrun by the Geonosian hive"),
"AncientLaunchSite":     (K, "derelict launch pads - an escape route"),
"AncientQuarry":         (K, "old strip mines - Jawa salvage"),
"AncientRuins":          (K, "ruins everywhere - the Outer Rim's dead cities"),
"Ruins":                 (K, "ruins everywhere - the Outer Rim's dead cities"),
"AncientRuins_Frozen":   (K, "night side - ruins locked in ice"),
"FrozenRuins":           (K, "night side - ruins locked in ice"),
"AncientSmokeVent":      (K, "badlands - venting machinery, smoke on the horizon"),
"AncientToxVent":        (K, "Imperial industry - toxic vents"),
"AncientUplink":         (K, "ancient comm uplink - hacking finds orbit"),
"AncientWarehouse":      (K, "sealed depot - prime Jawa salvage"),
"ArcheanTrees":          (R, "soil-making forest - too lush for this world"),
"Archipelago":           (K, "offshore island chains"),
"Basin":                 (K, "mountain basin holding groundwater"),
"Bay":                   (K, "sheltered bay - a port site"),
"CaveLakes":             (K, "water deep in the caves - precious"),
"Cavern":                (K, "cave networks - Jawa shelter"),
"Chasm":                 (K, "deep fissures in the mesas"),
"Cliffs":                (K, "cliff-ringed sites"),
"Cove":                  (K, "sheltered cove - smuggler landing"),
"Crevasse":              (K, "night side - glacial rift"),
"DryLake":               (K, "dry lakebed - salt pan"),
"Dunes":                 (K, "the Dune Sea itself - the planet's signature"),
"Fish_Decreased":        (K, "most coasts - poor fishing"),
"Fish_Increased":        (K, "the few rich coastal shallows"),
"Fjord":                 (K, "night side - glacial sea inlets"),
"Harbor":                (K, "abandoned coastal port"),
"IceCaves":              (K, "night side - ice caves"),
"IceDunes":              (K, "night side - wind-packed snow dunes"),
"Iceberg":               (K, "night-side seas"),
"InsectMegahive":        (K, "Geonosian megahive - a major faction site"),
"Lake":                  (K, "rare - terminator ring lakes"),
"LakeWithIsland":        (K, "rare - terminator ring lakes"),
"LakeWithIslands":       (K, "rare - terminator ring lakes"),
"Lakeshore":             (K, "lake shores in the terminator ring"),
"LavaCaves":             (K, "hotspot volcanism - lava tubes; the one hive-free cave"),
"LavaCrater":            (K, "hotspot volcanism - standing lava lake"),
"LavaFlow":              (K, "hotspot volcanism - active flows off the shield"),
"LavaLake":              (K, "hotspot volcanism - standing lava lake"),
"ObsidianDeposits":      (K, "volcanic country - obsidian to trade"),
"Peninsula":             (K, "coastal headland"),
"Plateau":               (K, "mesa tops"),
"Pollution_Increased":   (K, "Imperial industry and mine tailings"),
"Pond":                  (K, "rare oasis ponds"),
"RiverConfluence":       (K, "rare - terminator ring rivers"),
"RiverDelta":            (K, "where the few rivers reach the sea"),
"TerraformingScar":      (K, "deep desert - an ancient terraformer misfire"),
"ToxicLake":             (K, "poisoned water below the old mines"),
"Valley":                (K, "valleys between the mesas"),
"Wetland":               (R, "wetland - no swamps on this world"),
"WildTropicalPlants":    (R, "tropical flora - wrong climate"),

# ----------------------------------------------- Star Wars Animal Collection
"WildGalacticPlants":  (K, "widespread galactic scrub"),
"WildTattooinePlants": (K, "everywhere - this is the world's own flora"),
"WildRylothPlants":    (K, "near the terminator - Ryloth is tidally locked too"),
"WildDantooinePlants": (K, "terminator grasslands - Dantooine savanna scrub"),
"WildAlderaanPlants":  (R, "Alderaanian temperate flora - wrong climate"),
"WildNabooPlants":     (R, "Naboo lushness - wrong climate"),
"WildFelucianPlants":  (R, "Felucian fungal jungle - wrong climate"),
"sw_Sarlacc":          (K, "deep desert - the Pit of Carkoon"),
"sw_SarlaccLair":      (K, "deep desert - the Pit of Carkoon"),
"sw_DeadSarlacc":      (K, "deep desert - a dead sarlacc, hollowed out for shelter"),
"sw_DeadSarlaccCave":  (K, "deep desert - a dead sarlacc, hollowed out for shelter"),

# ----------------------------------------------- Vanilla Landmarks Expanded
"VEE_LargerRegion":     (K, "open desert - big sprawling maps"),
"VEE_SmallerRegion":    (K, "tight canyon and mesa-top sites"),
"VEE_FertileRains":     (R, "nutrient-rich rainfall - lush temperate"),
"VEE_FeralKinship":     (K, "near Jawa territory - beasts used to people"),
"VEE_ToxicVents":       (K, "mine country and Imperial industry"),
"VEE_RodentPlagues":    (K, "womp rats - the Jawa staple pest"),
"VEE_ColossalFauna":    (K, "deep desert - krayt dragon country"),
"VEE_SmokeVents":       (K, "badlands - smoking fissures"),
"VEE_WanderingCompanions": (K, "near Jawa territory - bondable beasts"),
"VEE_StrongerTides":    (K, "coastal - tidal generators worth building"),
"VEE_DeadlifeVents":    (R, "necromantic dust that raises the dead - occult"),
"VEE_Microfauna":       (K, "dune sea - tiny burrowers"),
"VEE_DeepOrePoor":      (K, "worked-out mining districts"),
"VEE_IncreasedInfestations": (K, "Geonosian hive country"),
"VEE_DomesticatedEscapees": (R, "feral Earth chickens, pigs and cows - breaks the setting"),
"VEE_NobleSteeds":      (R, "Earth horses and donkeys - banthas and dewbacks instead"),
"VEE_MineralDevoid":    (K, "barren sand seas - nothing to mine"),
"VEE_RotstinkVents":    (K, "badlands - sulfur and carrion stink"),
"VEE_AggressiveHerds":  (K, "deep desert - bantha and dewback herds that turn"),
"VEE_Fertility_Reduced":(K, "most of the planet - dead soil"),
"VEE_Alphabeavers":     (R, "alphabeavers - forest joke fauna"),
"VEE_DeepOreRich":      (K, "the mining belt - deep ore worth drilling"),
"VEE_TornadoAlley":     (K, "open flats - sand twisters"),
"VEE_MigratoryHerds":   (K, "bantha migration routes"),
"VEE_DistressedWildlife":(K, "deep desert - wary, half-starved beasts"),
"VEE_ReducedPredators": (K, "picked-over flats"),
"VEE_AbundantPredators":(K, "canyon country - predator dens"),
"VEE_SteamGeysers_Decreased": (K, "geologically dead ground - no geothermal"),
"VEE_VenomousEcosystem":(K, "deep desert - venomous crawlers"),
"VEE_VolcanicRichSoil": (K, "old ash beds - rare good soil"),
"VEE_ReducedPrey":      (K, "the starved deep desert"),
"VEE_UndergroundGasDeposits": (K, "gas fields - fuel worth extracting"),
"VEE_MineableComponentSpacer": (K, "buried machinery - Jawa component seams"),
"VEE_Sinkholes":        (K, "collapsed ground over the cave network"),
"VEE_PoisonousFlora":   (K, "deep desert - toxic scrub"),
"VEE_NoWind":           (K, "sheltered basins behind the mesas"),
"VEE_AbundantPrey":     (K, "oasis margins"),
"VEE_GeomagneticStorm": (K, "polar and night side - magnetic storms"),
"VEE_MechanoidShipChunks": (K, "crash fields - the best Jawa salvage"),
"VEE_Megafauna":        (K, "deep desert - engineered megafauna gone feral"),
"VEE_MoreSolarPower":   (K, "day side - twin suns at full glare"),
"VEE_NoTrees":          (K, "almost the whole planet"),
"VEE_PlantLife_Overgrown": (R, "extreme overgrowth - wrong world"),
"VEE_BombardedSurface": (K, "Imperial orbital bombardment craters"),
"VEE_Mycelium":         (K, "caves and night side - fungus that needs no sun"),
"VEE_RottenStench":     (K, "sulfur flats and carrion grounds"),
"VEE_SkygazingSpot":    (K, "clear desert nights - the twin moons"),
"VEE_NaturalAerie":     (K, "mesa tops - nesting fliers"),
"VEE_AuburnTree_Oaks":  (R, "autumn oaks - temperate Earth"),
"VEE_AuburnTree_Maples":(R, "autumn maples - temperate Earth"),
"VEE_AuburnTree_Birches":(R, "autumn birches - temperate Earth"),
"VEE_AuburnTree_Poplars":(R, "autumn poplars - temperate Earth"),
"VEE_AuburnForest":     (R, "autumn forest landmark - temperate Earth"),
"VEE_LessSolarPower":   (K, "near the terminator - low, slanting sun"),
"VEE_EasyToTraverse":   (K, "hardpan and the old road lines"),
"VEE_WildWheat":        (R, "Earth wheat - temperate cropland"),
"VEE_WildRice":         (R, "rice needs paddies"),
"VEE_DeepOreDevoid":    (K, "dead sand seas"),
"VEE_HardToTraverse":   (K, "dune seas and broken rock"),
"VEE_MangroveTrees":    (R, "mangroves - wrong world"),
"VEE_Mangrove":         (R, "mangroves - wrong world"),
"VEE_MangroveTerrain":  (R, "coastal wetland - wrong world"),
"VEE_MarineSanctuary":  (K, "coastal - the rich shallows"),
"VEE_WildSucculents":   (K, "deep desert - succulent scrub"),
"VEE_Blooming_ForgetMeNot": (R, "temperate wildflowers"),
"VEE_Blooming_Loosestrife": (R, "temperate wildflowers"),
"VEE_Blooming_Buttercup":   (R, "temperate wildflowers"),
"VEE_Blooming_Knapweed":    (R, "temperate wildflowers"),
"VEE_BloomingFields":       (R, "wildflower fields - temperate Earth"),
"VEE_PlantLife_Decimated":  (K, "the deep desert - near sterile"),
"VEE_PlentifulGrass":       (K, "terminator grasslands"),
"VEE_IncreasedDiseases":    (K, "crowded oasis settlements"),
"VEE_LargeRiverBanks":      (K, "the few real rivers"),
"VEE_NoDiseases":           (K, "sterile deep desert - too dry for plague"),
"VEE_ReducedDiseases":      (K, "dry uplands"),
"VEE_Sandstorms":           (K, "everywhere - the planet's defining weather"),
"VEE_DustStorms":           (K, "the flats and the badlands"),
"VEE_FloodPlains":          (K, "the few rivers - flash-flood plains"),
"VEE_MeteorCrater":         (K, "deep desert impact craters"),
"VEE_RagingWind":           (K, "open dune sea - screaming wind"),
"VEE_StagnantRivulet":      (K, "a dying river near the terminator"),
"VEE_TemperateGrasslands":  (R, "temperate grassland landmark - wrong world"),
"VEE_AbandonedFarmland":    (K, "abandoned moisture farms, killed by drought"),
"VEE_AlluvialFan":          (K, "where a wadi spills out onto the flats"),
"VEE_AnimaCoast":       (U, "UNSURE: a Force-nexus grove? only if reskinned - reject as anima forest"),
"VEE_AnimaForest":      (U, "UNSURE: a Force-nexus grove? only if reskinned - reject as anima forest"),
"VEE_AnimaFlora":       (U, "UNSURE: Force-nexus flora if reskinned; the dense forest is the problem"),
"VEE_AnimaFauna":       (U, "UNSURE: rides on the anima call above"),
"VEE_AnimaSoils":       (U, "UNSURE: rides on the anima call above"),
"VEE_AnimaSoils_Coast": (U, "UNSURE: rides on the anima call above"),
"VEE_BasaltCape":           (K, "sea cliffs of black basalt"),
"VEE_BurnedForest":         (R, "burned forest - there are no forests here"),
"VEE_CactusFields":         (K, "deep desert - cactus stands"),
"VEE_Cactus_Barrel":        (K, "deep desert - barrel cacti"),
"VEE_Cactus_Beavertail":    (K, "deep desert - beavertail cacti"),
"VEE_Cactus_Hedgehog":      (K, "deep desert - hedgehog cacti"),
"VEE_Cactus_OrganPipe":     (K, "deep desert - organ pipe cacti"),
"VEE_CalmBasin":            (K, "windless sand basin behind a crater rim"),
"VEE_Cenotes":              (K, "water-filled sinkholes - hidden desert water"),
"VEE_ContaminatedCoast":    (K, "coast below an Imperial dump site"),
"VEE_ContaminatedReservoir":(K, "irradiated reservoir near the old mines"),
"VEE_ContaminatedRiver":    (K, "river poisoned downstream of Imperial works"),
"VEE_CoralReef":            (K, "offshore reefs"),
"VEE_CradleOfLife":         (R, "overgrowth landmark - wrong world"),
"VEE_CraterLake":           (K, "caldera lake - rare open water"),
"VEE_DeepSnow":             (K, "night side - compacted snow"),
"VEE_DetachedIceberg":      (K, "night-side seas"),
"VEE_DriftwoodShore":       (K, "coast - bleached timber and wreckage to scavenge"),
"VEE_DryRiver":             (K, "wadis - dry riverbeds all over the desert"),
"VEE_DustBowl":             (K, "the great dust bowl - scorched waste"),
"VEE_FirewoodTrees":        (R, "firewood forest - too lush for this world"),
"VEE_FleshPits":            (R, "flesh caves - Anomaly body-horror"),
"VEE_FrequentAuroras":      (K, "polar and night side - aurora over the ice"),
"VEE_GlacialMoraine":       (K, "night side - glacial rubble"),
"VEE_GravelBeach":          (K, "harsh gravel shoreline"),
"VEE_IceAndFire":           (R, "iceberg with a lava lake - gag geology"),
"VEE_IceSpires":            (K, "night side - wind-carved ice columns"),
"VEE_JadeChunks":           (K, "mineral seams worth trading"),
"VEE_JadeiteMountains":     (K, "jade-rich rock in the mining belt"),
"VEE_JaggedRocks":          (K, "broken rock ridges - canyon country"),
"VEE_LaurelForest":         (R, "laurel forest - temperate lushness"),
"VEE_LittoralDunes":        (K, "coastal dunes"),
"VEE_LoneIsland":           (K, "offshore island"),
"VEE_LoneIslandWithLake":   (K, "offshore island with an inner lake"),
"VEE_LoneIslandWithMountain": (K, "offshore island with a peak"),
"VEE_LushLavaFields":       (K, "hotspot volcanism - warm ground; watch it does not read too green"),
"VEE_Moor":                 (R, "peat moor - temperate bog"),
"VEE_MoorFlora":            (R, "moor plants - temperate bog"),
"VEE_Mossy":                (R, "moss needs constant damp"),
"VEE_ObsidianChunks":       (K, "obsidian in the old volcanic country"),
"VEE_PebbleDunes":          (K, "reg - pebble desert pavement"),
"VEE_PermafrostBasin":      (K, "night side - permafrost basin"),
"VEE_QuicksandDunes":       (K, "the Dune Sea - sinking sand"),
"VEE_QuicksandPits":        (K, "deep desert - quicksand between the dunes"),
"VEE_RedDesert":            (K, "the red sand desert - a whole region of it"),
"VEE_RedDesertPlants":      (K, "the red sand desert - cacti of the red sands"),
"VEE_RelictDelta":          (K, "fossil delta - a river that died long ago"),
"VEE_ResurgentCaldera":     (K, "resurgent caldera - the plume is still alive"),
"VEE_RisingWaters":         (K, "flat tidal coast - the sea walks inland"),
"VEE_RockRidge":            (K, "rock ridge across the flats"),
"VEE_SaltPlains":           (K, "salt flats - the bed of a dried inland sea"),
"VEE_SerpentineCanyons":    (K, "canyon country - slot canyons"),
"VEE_StoneForest":          (K, "wind-carved stone spires - a rock forest"),
"VEE_SulfuricLake":         (K, "badlands - sulfur lake, foul but fertile at the edge"),
"VEE_SulfuricRiver":        (K, "acid river below the sulfur springs"),
"VEE_ToxicCrater":          (K, "impact crater turned toxic pool - Imperial dump"),
"VEE_TropicalBeach":        (R, "tropical beach - lush, wrong climate"),
"VEE_TropicalBeachFlora":   (R, "palms and cocoa - tropical lushness"),
"VEE_VolcanicSandDesert":   (K, "black sand desert downwind of the plumes"),
"VEE_VolcanicSandDesertFlora": (K, "cacti of the black volcanic sands"),
"VEE_Volcano":              (K, "hotspot volcanism - a fixed plume builds a real cone"),
"VEE_WastelandFauna":       (K, "the badlands - wasteland animals"),
"VEE_WindBlownPlateau":     (K, "high plateau under a screaming wind"),
}

# ---------------------------------------------------------------------------
# 🔴 THE CONTESTED CALLS. Each of these is defensible both ways, so the note is
# prefixed with a warning marker and the sheet's "⚠ flagged for review" filter
# pulls exactly this set. Reviewing these ~20 rows is worth more than skimming
# the other 430.
# ---------------------------------------------------------------------------
FLAGGED = {
    # 🔴 SETTLED BY THE OWNER 2026-08-16, and it overturned our invented rule:
    # "The planet has PLENTY of volcanism due to hot spots no longer moving without
    # plate tectonics." A tidally locked world has no plate drift, so mantle plumes
    # stay put and build sustained volcanic provinces. All lava content is now KEPT.
    # These three stay REJECTED for a different reason - they are occult, not volcanic:
    "AB_AncientBloodRainVent": "occult, not volcanic - kept out on theme, not on geology",
    "AB_AncientDeathPallVent": "occult, not volcanic - kept out on theme, not on geology",
    "VEE_DeadlifeVents":       "Anomaly necromancy, not volcanic - flip if you want it",
    # rule vs fiction pull apart
    "WildAlderaanPlants": "cut as temperate, but it IS Star Wars flora - imported ornamentals?",
    "VEE_DomesticatedEscapees": "feral stock by dead moisture farms is a good beat, but reads Earth",
    "VEE_NobleSteeds":  "feral stock by dead moisture farms is a good beat, but reads Earth",
    "AB_BumbledroneNests": "cut as cutesy, yet Geonosians make insect nests entirely apt",
    "AB_DerelictResort": "kept only by reframing it as a derelict Hutt pleasure resort",
    "VEE_RotstinkVents": "kept as badlands sulfur; description leans gross",
    "VEE_SulfuricLake":  "kept as badlands sulfur; description leans gross",
    "VEE_SulfuricRiver": "kept as badlands sulfur; description leans gross",
    "Marshy":            "split from Muddy - the wet/dry line on a desert world is thin",
    "Muddy":             "kept as oasis margin; the wet/dry line on a desert world is thin",
    "AB_AncientGreyPallVent": "kept as Imperial exhaust while death-pall/blood-rain were cut as occult",
    "AB_HealingSprings": "mystical unless read as a mineral spa",
}


def apply_flags(decisions):
    """Prefix the contested notes so the sheet can filter to exactly them."""
    n = 0
    for name, why in FLAGGED.items():
        d = decisions.get(name)
        if not d:
            continue
        note = d.get("note", "")
        if note.startswith("⚠") or note.startswith("UNSURE"):
            continue
        d["note"] = "⚠ %s | %s" % (why, note) if note else "⚠ %s" % why
        n += 1
    return n


# ---------------------------------------------------------------------------
data = json.loads(re.search(r'^const DATA = (\[.*\]);$',
                            HTML.read_text(encoding="utf-8"), re.M).group(1))

names = {r["defName"] for r in data}
missing = sorted(names - set(D))
extra   = sorted(set(D) - names)
if missing or extra:
    print("MISSING (%d): %s" % (len(missing), missing[:40]))
    print("EXTRA   (%d): %s" % (len(extra), extra[:40]))
    sys.exit(1)

whitelisted, rejected, notes, items = [], [], {}, {}
seen = set()
for r in data:
    dn = r["defName"]
    st, note = D[dn]
    if dn not in seen:
        seen.add(dn)
        if st == K: whitelisted.append(dn)
        elif st == R: rejected.append(dn)
        if note: notes[dn] = note
    items[dn] = {"state": "whitelisted" if st == K else "rejected" if st == R else "undecided",
                 "note": note, "label": r["label"], "mod": r["mod"],
                 "type": r["type"], "occurrences": r["n"]}

flagged_n = apply_flags(items)
for dn, it in items.items():
    if it["note"]:
        notes[dn] = it["note"]

payload = {
    "posture": "whitelist",
    "meaning": "ONLY defNames in `whitelisted` may exist on the planet. "
               "Everything else in `universe` is stripped, whether it was "
               "rejected on purpose or never looked at.",
    "source": "PRE-FILLED for the owner to REVIEW, not to decide from scratch. "
              "Setting: Tatooine-like Star Wars desert world, Jawa scavenger clan fleeing the "
              "Empire, serious tone save for Jawa slapstick; ~17% ocean, Geonosians present, "
              "possibly tidally locked. `undecided` here is DELIBERATE: the call is genuinely open.",
    "world": "prefill",
    "universeSize": len(data),
    "whitelistedCount": len(whitelisted),
    "strippedCount": len(data) - sum(1 for r in data if D[r["defName"]][0] == K),
    "whitelisted": whitelisted, "rejected": rejected,
    "notes": notes, "items": items,
    "universe": [r["defName"] for r in data],
}
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

rows_k = sum(1 for r in data if D[r["defName"]][0] == K)
rows_r = sum(1 for r in data if D[r["defName"]][0] == R)
occ = [r for r in data if r["n"] > 0]
ok = sum(1 for r in occ if D[r["defName"]][0] == K)
orj = sum(1 for r in occ if D[r["defName"]][0] == R)
print("rows   %d  keep %d  rej %d  undecided %d" % (len(data), rows_k, rows_r, len(data)-rows_k-rows_r))
print("uniq   %d  keep %d  rej %d  undecided %d"
      % (len(seen), len(whitelisted), len(rejected), len(seen)-len(whitelisted)-len(rejected)))
print("occurs %d  keep %d  rej %d  undecided %d" % (len(occ), ok, orj, len(occ)-ok-orj))
print("flagged %d contested calls prefixed with the warning marker" % flagged_n)
print("wrote", OUT)

