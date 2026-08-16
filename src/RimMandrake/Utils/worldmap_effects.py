#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""worldmap_effects.py - "what this ACTUALLY DOES", one sentence per def.

🔑 THE PROBLEM THIS SOLVES - owner, 2026-08-16:

    "'headwater' for a river... so what? I can see where that is on the map...
     what does it mean if it has this particular mutator?"

A label and a flavour description tell you what a thing IS. Neither tells you
what changes when your colony lands on a tile carrying it. This module carries
the GAMEPLAY CONSEQUENCE - densities, suppressed generation steps, game
conditions, map size, raid behaviour - in one sentence per def, and
`worldmap_review.py` renders it as the `effect` line under every row.

🔴 CONFIDENCE IS MARKED AND IT MATTERS.

    no prefix   the sentence rests on something real: a non-default field value
                in TileMutatorDef.json, a workerClass whose mechanism is not
                ambiguous, or an explicit mechanical claim in the def's own
                in-game description ("disease chance is lowered by 75%").
    "~"         INFERRED FROM THE NAME. The def's mechanical fields are all
                default and the worker is generic, so this is a reading of the
                defName and nothing stronger. Treat it as a hypothesis.

    All 46 Geological Landforms / Biome Transitions defs share the single
    generic worker `TileMutatorWorker_Landform` and carry no label, no
    description and no mechanical fields - the actual shape lives in that mod's
    own Landform XML, which is not in the def dump. Every one of them is "~".

Fields that were read to build these, and the ones worth re-reading if a def
changes: workerClass · animal/plant/junk/geyser/chunk/fishPopulationFactor ·
additionalWildPlants · extraGenSteps · preventGenSteps · preventsPondGeneration
· preventsLandmarks · preventNaturalElevation · preventPatches ·
hillinessForElevationGen · hillinessForOreGeneration · allowRoofedEdgeWalkIn ·
blacklistedRaidStrategies · additionalGameConditions · the constraint ranges ·
and the mod's own `modExtensions` (map size, movement difficulty, disease MTB,
deep-ore yield, tide strength, what gets spawned and how many).

🔴 THREE FIELDS CHANGE COMBAT AND NO NAME HINTS AT THEM. They are called out
explicitly in the sentence wherever they are set:
  allowRoofedEdgeWalkIn      raiders may walk in under a roof
  blacklistedRaidStrategies  a whole raid type simply cannot be used here
  additionalGameConditions   a permanent map-wide condition rides along

🔑 JUNK IS THE JAWA METRIC. junkDensityFactor and anything that spawns
salvageable structures, chunks, barrels or ship debris is called out, because a
scavenger clan's tile choice turns on it. `Junkyard` is 15x junk; `Dunes` is the
same tile with the ruins, shrines and landing pads generation steps SUPPRESSED.
"""
from __future__ import annotations

# --------------------------------------------------------------------------
# TileMutatorDef - the effect sentence, keyed by defName.
# "~" prefix = inferred from the name only. Everything else is field-backed.
# --------------------------------------------------------------------------
MUTATOR = {
    # ---- Core / Odyssey: terrain shape ----
    "Mountain": "Fills one map edge with solid rock — overhead-mountain mining, deep ore, and infestations.",
    "Caves": "Adds roofed cave networks inside the rock — free enclosed space that insect hives also use.",
    "Coast": "Puts ocean on one map edge — that side is closed to raiders, and fishing and tidal power open up.",
    "River": "Cuts a river across the map — fresh water and watermill power, but a crossing that splits your defence.",
    "UndergroundCave": "Marks the tile as holding a descendable underground cave map layer.",
    "Headwater": "The river STARTS here, so it crosses only part of the map — one bank to defend instead of a split map.",
    "RiverConfluence": "Two rivers merge on the map — three water crossings and three separated wedges of land.",
    "RiverIsland": "The river splits and rejoins around a central island — a bridge-only, naturally defensible build site.",
    "RiverDelta": "The river fans into many branches and ponds are suppressed — heavily cut-up ground, hard to cross.",
    "Lake": "A large freshwater lake eats buildable ground — fishing and water, inland tiles only.",
    "LakeWithIsland": "Freshwater lake with an island in it — a walled-off build spot reachable only by bridge.",
    "LakeWithIslands": "Freshwater lake with several islands — fragmented buildable ground, bridges everywhere.",
    "Pond": "A small freshwater pond — water and a little fishing, minimal land lost.",
    "Lakeshore": "Puts a lake on one map edge — fresh water and fishing without losing the middle of the map.",
    "Oasis": "Hot tiles only (20–60°C): adds water plus palms, rat palms, grass and reeds — the desert's one green tile.",
    "DryLake": "A lake bed with no water — flat, open, sterile ground and nothing to fish.",
    "ToxicLake": "Standing water that causes toxic buildup on contact — do not drink it, do not fish it.",
    "Wetland": "Interconnected waterways carve up the whole map and ponds are suppressed — slow movement, forced chokepoints.",
    "HotSprings": "Mountainous inland only: warm pools that never freeze — year-round water and free heat.",
    "Valley": "Mountain walls on two sides with a flat floor, natural elevation suppressed — two approaches to hold.",
    "Cavern": "🔴 BLOCKS SIEGE RAIDS ENTIRELY, but lets raiders walk in under the roof — the biggest combat swing on this sheet.",
    "Chasm": "Deep impassable fissures split the mountain — they dictate every raid path across the map.",
    "Crevasse": "Flat inland only: a glacial rift cuts the map in two, forcing all traffic around the ends.",
    "Plateau": "Flat tile that rolls ORE AS IF MOUNTAINOUS — mountain-grade minerals with no mountain in the way.",
    "Cliffs": "Cliffs on three sides and ore rolled as mountainous — flat buildable floor, one approach, rich rock.",
    "Hollow": "A bowl ringed by cliffs with one entrance — the cheapest natural killbox terrain in the game.",
    "Basin": "A mountain depression holding a groundwater lake — water and cliff walls on the same map.",
    "IceDunes": "Flat tiles only: compacted snow hills that slow movement, with nothing to mine under them.",
    "TerraformingScar": "Flattened spiral ground that still rolls ore as LARGE HILLS — ore without the elevation.",
    "Archipelago": "Breaks the coast into small islands — very little contiguous land to build on. Needs 2–5 coastal sides.",
    "CoastalIsland": "A large island off the shore — water on 3–5 sides, so raiders have one narrow land approach.",
    "Peninsula": "Land juts into the ocean on 3–5 sides — one land approach for every raid that walks.",
    "Bay": "A sheltered coastal inlet — ocean access and calmer coast, on 1–5 coastal sides.",
    "Cove": "A sheltered coastal inlet — ocean access and calmer coast, on 1–5 coastal sides.",
    "CoastalAtoll": "A ring of land around a lagoon — the def's own text warns there is very little land to build on.",
    "Iceberg": "Sub-zero tiles only (max 0°C): a floating ice mass — no soil, no ore, nothing under you.",
    "Fjord": "Mountainous coast: a narrow steep-walled sea inlet — ocean access through a single channel.",
    "LavaLake": "A lake of deep lava — instantly lethal terrain plus permanent ambient heat. Inland only.",
    "LavaCrater": "A crater filled with deep lava — instantly lethal terrain plus permanent ambient heat. Inland only.",
    "LavaFlow": "Lava routinely floods this map and ponds are suppressed — the def calls it extremely inhospitable.",
    "LavaCaves": "Lava-filled caves, and it SUPPRESSES CaveHives — the one cave type that spawns no insect hives.",
    "IceCaves": "Roofed cave networks cut into ice rather than rock — shelter with no stone to mine.",
    "CaveLakes": "Water pools inside the caves — underground fresh water you can defend easily.",
    "MixedBiome": "Two biomes' plants and animals on one map — and it BLOCKS every landmark from that tile.",
    "Dunes": "🔑 The anti-scavenger tile: 85% fewer chunks, no landmarks, and ruins, shrines, utility buildings and landing pads all SUPPRESSED.",
    "InsectMegahive": "A permanent giant insect hive under the map — recurring infestations by design. Mountainous only.",

    # ---- Core / Odyssey: ancient structures and loot ----
    "AncientGarrison": "Spawns an ancient military prefab — real loot behind still-active security systems.",
    "AncientWarehouse": "Spawns an ancient warehouse prefab full of valuables, with security systems attached.",
    "AncientChemfuelRefinery": "Spawns a refinery prefab holding large quantities of chemfuel — and its defences.",
    "AncientInfestedSettlement": "Spawns a settlement destroyed by insects — resources still in it, and the insects too.",
    "AncientLaunchSite": "Spawns launch pads with WORKING transport pods — a free one-way ride off the tile.",
    "AncientRuins": "Scatters ancient ruins — salvage plus a wide grab-bag of possible threats sleeping in them.",
    "AncientRuins_Frozen": "Ancient ruins encased in ice — the same salvage, plus whatever the ice preserved.",
    "AncientQuarry": "🔑 Mountainous only: adds ancient mining charges, explosives crates, an excavator, a drill platform and a tunneller to strip.",
    "AncientSmokeVent": "Periodically vents smoke that BLOTS OUT THE SUN FOR DAYS — solar power and crops both stall.",
    "AncientToxVent": "Regularly spews toxic fallout across the map — permanent gas-mask and indoor-farming logistics.",
    "AncientHeatVent": "Regularly vents heat and dramatically raises map temperature — heatstroke and dead crops.",
    "AbandonedColonyTribal": "A recently abandoned tribal colony — pre-built structures and stockpiles to strip.",
    "AbandonedColonyOutlander": "A recently abandoned outlander colony — pre-built structures and stockpiles to strip.",
    "Harbor": "An abandoned coastal settlement — salvage on a tile that also has ocean access.",
    "Stockpile": "🔑 Buries a resource stockpile under the map, guarded by live ancient defences — pure scavenger loot.",
    "AncientUplink": "A hackable uplink that reveals a hidden ORBITAL location — the route to an off-world site.",

    # ---- Core / Odyssey: density and climate ----
    "AnimalLife_Increased": "1.5x animal density — more hunting meat, and more mass when a manhunter pack rolls.",
    "AnimalLife_Decreased": "Half the animals — hunting is thin and predators are rarer.",
    "AnimalHabitat": "Seeds a resident herd of one animal kind that keeps respawning — reliable meat, or a resident predator.",
    "PlantLife_Increased": "1.3x plant density — more foraging and more wood, on low-pollution tiles only.",
    "PlantLife_Decreased": "Half the plants — less wood, less forage, and less cover to shoot through.",
    "PlantGrove": "Packs the map with one tree species (oak, poplar, pine, birch, willow, maple, cecropia, timbershroom, willowgill or boomshroom).",
    "WildPlants": "Grows wild cotton, psychoid, smokeleaf, tinctoria, strawberries or fibercorn — free cloth and drug crops.",
    "WildTropicalPlants": "Grows wild cocoa trees — free chocolate ingredient, warm tiles only.",
    "Junkyard": "🔑 15x JUNK DENSITY plus scarlands junk clusters and prefabs — the single richest scavenging tile in the game.",
    "SteamGeysers_Increased": "Doubles steam geysers — twice as many free geothermal power sites.",
    "MineralRich": "More surface ore, but obsidian, jadeite, spacer components and every compressed-ore variant are excluded from the roll.",
    "ObsidianDeposits": "Adds mineable obsidian — the material for obsidian blades and glass.",
    "ArcheanTrees": "Archean trees whose roots CONVERT NEARBY TERRAIN INTO RICH SOIL — and they can never be replanted.",
    "FoggyMutator": "Fog weather at +10 commonality — recurring accuracy and solar-power losses.",
    "SunnyMutator": "Clear weather at +10 commonality — more solar output, fewer weather interruptions.",
    "WetClimate": "Rain, thunderstorms, snow and blizzards all at +10 commonality — bad for solar, good against fire.",
    "WindyMutator": "🔴 Adds a permanent WINDY game condition plus +10 windy weather — wind turbines run hot, fires spread.",
    "Pollution_Increased": "Paints the tile with toxic pollution — toxic buildup outdoors and poisoned soil until cleaned.",
    "Fish_Increased": "1.5x fish population — fishing is a real food source here.",
    "Fish_Decreased": "Fish population down to 35% — fishing barely repays the time.",
    "DryGround": "Suppresses ALL pond generation — no free water anywhere on the map.",
    "Marshy": "Scatters marsh patches — slow movement and soft ground through the middle of the map.",
    "Sandy": "Scatters large sand patches — fast to walk, useless to farm.",
    "Fertile": "Scatters extra-fertile soil patches — better crop yield without hydroponics. Low-pollution tiles only.",
    "Muddy": "Scatters mud patches — movement penalty and filth tracked into everything.",

    # ---- Alpha Biomes ----
    "AB_ButterflySwarms": "Adds harmless small butterflies to the animal roll — decoration, not a threat.",
    "AB_LocustPlagues": "Adds locust swarms that strip unprotected yellow grass — a standing threat to grazing and crops.",
    "AB_FeraliskNest": "Seeds feralisks into the tile — aggressive predators that will come for colonists.",
    "AB_BlizzariskNest": "Seeds blizzarisks into the tile — cold-adapted aggressive predators.",
    "AB_DunealiskNest": "Seeds dunealisks into the tile — desert-adapted aggressive predators.",
    "AB_BumbledroneNests": "Places 3–4 bumbledrone hives on the map — persistent hostile swarm spawners.",
    "AB_ExplodingAnimals": "🔴 Game condition: EVERY ANIMAL DETONATES ON DEATH — hunting and animal raids both become explosive.",
    "AB_AgariluxPrime_Mutator": "Spawns an Agarilux Prime that releases spores DESTROYING EVERYTHING around it.",
    "AB_OcularTransformation": "Fills the map with alien ocular trees instead of ordinary flora.",
    "AB_GoldenTrees": "Fills the map with golden cube trees — gold-yielding wood.",
    "AB_FleshTrees": "Fills the map with flesh trees — organic harvest rather than wood.",
    "AB_DessertTrees": "Fills the map with dessert trees — an edible tree crop.",
    "AB_TechnoTrees": "Fills the map with half-synthetic techno trees — component-yielding flora.",
    "AB_LuminescentTrees": "Fills the map with luminescent trees — light without power.",
    "AB_SterileGround": "Only grass grows here — BUT DISEASE CHANCE DROPS 75%, which is a serious long-run saving.",
    "AB_AncientFreezingVent": "Periodically vents freezing air across the map — recurring cold shocks.",
    "AB_AncientGreyPallVent": "Periodically vents smoke that plunges the map into DARKNESS — solar and plant growth stop.",
    "AB_AncientBloodRainVent": "Periodically vents vaporised blood that condenses into blood rain over the map.",
    "AB_AncientDeathPallVent": "🔴 Periodically vents archites that REANIMATE CORPSES — your own dead get up.",
    "AB_DerelictBioLab": "Spawns an abandoned biotech lab prefab to loot; investigating it can attract company. Flat tiles only.",
    "AB_DerelictArchonexus": "Spawns one of five derelict archonexus structures — the highest-tier salvage in the mod.",
    "AB_DerelictKemeticTemple": "Spawns a derelict kemetic temple structure to explore and strip.",
    "AB_DerelictResort": "Spawns a derelict resort prefab. Warm coastal tiles only (20–40°C, 1–6 coastal sides).",
    "AB_WideRegion": "🔴 FORCES THE MAP TO 400×100 — a long thin battlefield instead of a square one.",
    "AB_NarrowRegion": "🔴 FORCES THE MAP TO 100×400 — a tall narrow battlefield instead of a square one.",
    "AB_DiminutiveRegion": "🔴 FORCES THE MAP TO 100×100 — a quarter of normal area; everything is inside mortar range.",
    "AB_TarLakes": "Impassable tar pools that CANNOT EVEN BE BRIDGED — permanent no-go ground. Inland only.",
    "AB_PropaneLakes": "Lakes of liquid hydrocarbons — flammable terrain rather than water.",
    "AB_MagmaticQuagmire": "Molten, cracking, burning ground with no ponds — flat inland tiles only.",
    "AB_MagmaVents": "Places 6–12 magma vents that erupt with molten rock and searing gas.",
    "AB_GiantFossils": "Scatters giant skeleton structures across the map — bone salvage and huge natural cover.",
    "AB_DerelictClusters": "🔑 Scatters derelict MECHANOID CLUSTER structures to scavenge — steel, plasteel and components, no raid attached.",
    "AB_GeothermalHotspots": "Unlocks an efficient biome geothermal plant under Furniture → build biome structures.",
    "AB_EdibleAirborneMicrofungi": "Unlocks a microfungi collector building — edible ingredients pulled straight from the air.",
    "AB_MoldyEnvironment": "🔴 Game condition: being outdoors is near-unbearable — a standing mood cost on every outdoor job.",
    "AB_OversaturatedSoil": "Swaps fertile ground for even more fertile ground — higher crop yield with no work.",
    "AB_PollinationFrenzy": "1.1x plants, paid for with worse allergies.",
    "AB_PetalStorms": "Petal-storm weather at +50 commonality (five times the usual bump) — mood up, visibility and accuracy down.",
    "AB_DigestiveSurface": "🔑 The ground DIGESTS DROPPED ITEMS left too long — you cannot stockpile outdoors here.",
    "AB_SymbioticNutrients": "Colonists need 10% less nutrition to feel full — a permanent food saving.",
    "AB_QuiveringSurface": "The living ground raises movement difficulty across the whole map.",
    "AB_GelatinousMemoryEcho": "🔴 Game condition: stored memory echoes occasionally bleed into reality as events.",
    "AB_AmbientRadiation": "🔴 Game condition: background radiation subtly affects health and mutation rates.",
    "AB_ExtremeTemperatureFluctuations": "🔴 Game condition: scorching days and freezing nights — unheated rooms and crops both fail.",
    "AB_HealingSprings": "Springs with curative properties — free healing on a mountainous inland tile.",
    "AB_MutagenicSprings": "Springs that MUTATE colonists and animals that touch them — inland tiles only.",
    "AB_QuicksandPits": "Shallow quicksand pools that impede movement across the map. Inland only.",
    "AB_ResidualOverclocking": "Unlocks a collector building that taps leftover mechanoid energy for power.",

    # ---- Dark Ages : Beasts and Monsters ----
    "DA_SnaptoadBreedingGrounds": "🔴 FISHING BITES BACK — froglet attacks and tadpole bites are rolled as negative catch outcomes.",
    "DA_LeviathanNest": "🔴 Fishing this coast can hook a confused hatchling or an ANGRY LEVIATHAN. 1–5 coastal sides.",

    # ---- Geological Landforms — 🔴 ALL INFERRED, no label, no description, no fields ----
    "GL_Archipelago": "~ Probably scatters many small islands, leaving little contiguous land to build on.",
    "GL_Atoll": "~ Probably a ring of land around a central lagoon — very little buildable ground.",
    "GL_Badlands": "~ Probably eroded broken terrain — lots of rock outcrops, poor soil.",
    "GL_Caldera": "~ Probably a collapsed volcanic bowl with steep walls and a flat interior.",
    "GL_Canyon": "~ Probably a deep cut across the map that forces traffic to its ends.",
    "GL_CaveEntrance": "~ Probably places a cave mouth on the map — roofed space, likely insect risk.",
    "GL_Cirque": "~ Probably a glacier-carved amphitheatre — cliffs on three sides, one open approach.",
    "GL_Cliff": "~ Probably a cliff wall across part of the map — cover and a blocked approach.",
    "GL_CliffAndCoast": "~ Probably cliffs meeting ocean — two closed sides, minimal land approach.",
    "GL_CliffCorner": "~ Probably cliffs on two adjoining sides — a corner build site with two open edges.",
    "GL_Coast": "~ Probably an alternative coast shape — ocean on one edge.",
    "GL_CoastalIsland": "~ Probably an island near shore — water on most sides.",
    "GL_CoastCorner": "~ Probably ocean on two adjoining edges — a headland with two land approaches.",
    "GL_Cove": "~ Probably a small sheltered inlet with ocean access.",
    "GL_CoveWithIsland": "~ Probably a sheltered inlet containing an island — a bridge-only build spot.",
    "GL_Crater": "~ Probably an impact bowl with a raised rocky rim.",
    "GL_DesertPlateau": "~ Probably a flat-topped desert rise with cliff edges — a defensible desert build site.",
    "GL_DryLake": "~ Probably a waterless lake bed — flat sterile open ground.",
    "GL_Fjord": "~ Probably a narrow steep-walled sea inlet.",
    "GL_Glacier": "~ Probably a solid ice sheet — no soil, no ore.",
    "GL_Gorge": "~ Probably a narrow steep ravine cutting the map.",
    "GL_IceOasis": "~ Probably liquid water in an ice field — a rare unfrozen water source.",
    "GL_Island": "~ Probably a fully surrounded island — no land approach at all.",
    "GL_Lake": "~ Probably an alternative inland lake shape.",
    "GL_LakeWithIsland": "~ Probably a lake with an island in it — bridge-only interior.",
    "GL_Landbridge": "~ Probably a narrow isthmus between two waters — one very narrow land approach.",
    "GL_LoneMountain": "~ Probably an isolated mountain in open ground — mining and overhead cover without a mountain edge.",
    "GL_Oasis": "~ Probably water and greenery in dry terrain.",
    "GL_Peninsula": "~ Probably land jutting into water — one land approach.",
    "GL_Rift": "~ Probably a deep impassable split across the map.",
    "GL_River": "~ Probably an alternative river shape across the map.",
    "GL_RiverConfluence": "~ Probably two rivers merging — several crossings and separated land wedges.",
    "GL_RiverDelta": "~ Probably a branching river mouth — heavily cut-up ground.",
    "GL_RiverIsland": "~ Probably a river splitting around an island — bridge-only build site.",
    "GL_RiverSource": "~ Probably the river's origin, so it crosses only part of the map.",
    "GL_RiverTerrain": "~ Probably alters the terrain along the riverbanks rather than the river's shape.",
    "GL_SecludedCove": "~ Probably an enclosed inlet with a single narrow approach.",
    "GL_SecludedValley": "~ Probably a valley closed on most sides — one or two entrances to hold.",
    "GL_Sinkhole": "~ Probably a collapsed pit exposing bare rock.",
    "GL_Skerry": "~ Probably small rocky offshore islets — scenic, little buildable land.",
    "GL_SurfaceCave": "~ Probably a cave opening at ground level — roofed space with a walk-in mouth.",
    "GL_SwampHill": "~ Probably raised dry ground inside marsh — a small buildable island in slow terrain.",
    "GL_Tombolo": "~ Probably a sandbar linking an island to shore — one very narrow land approach.",
    "GL_Valley": "~ Probably an alternative valley shape — walls on two sides, two entrances.",
    "GL_BiomeTransitions": "~ Probably blends two neighbouring biomes across the tile; no mechanical fields are set on the def itself.",

    # ---- Map Designer ----
    "ZMD_NoMutator": "No mechanical effect — Map Designer's explicit 'none' placeholder for a category.",

    # ---- Star Wars Animal Collection ----
    "sw_SarlaccLair": "🔑 Generates a LIVE sarlacc pit on the map — a standing hazard that swallows pawns. Up to mountainous.",
    "sw_DeadSarlaccCave": "🔑 Generates a DEAD sarlacc as a cave structure — shelter and salvage with no live hazard.",
    "WildGalacticPlants": "Grows wild chakroot, meiloorun, muja fruit, jogan and nysyllin — off-world food and drug crops.",
    "WildRylothPlants": "Grows wild munch fungus — a Ryloth food crop that needs settled spores.",
    "WildTattooinePlants": "🔑 Grows wild hubba gourds — the Tatooine desert food crop, needs condensed moisture.",
    "WildNabooPlants": "Grows wild bubblespore and tooke traps.",
    "WildDantooinePlants": "Grows wild dantubers where light is sufficient.",
    "WildAlderaanPlants": "Grows wild hydenock trees.",
    "WildFelucianPlants": "Grows wild Felucian glowspores.",

    # ---- Vanilla Landmarks Expanded: fauna ----
    "VEE_AbundantPredators": "More predators spawn — more danger, and more high-value hunting.",
    "VEE_ReducedPredators": "Fewer predators spawn — safer hunting and safer outdoor work.",
    "VEE_AbundantPrey": "More prey animals spawn — easy meat.",
    "VEE_ReducedPrey": "Fewer prey animals spawn — hunting is thin.",
    "VEE_NaturalAerie": "More flying animals — harder to hunt, and they cross walls.",
    "VEE_MarineSanctuary": "More coastal animals. Needs 1–5 coastal sides.",
    "VEE_RodentPlagues": "Forces rats into the animal roll — constant small vermin.",
    "VEE_VenomousEcosystem": "More venomous animals — every hunt risks a toxic wound.",
    "VEE_ColossalFauna": "🔴 Game condition: ALL fauna is much larger — far more meat, far more dangerous manhunters.",
    "VEE_Microfauna": "🔴 Game condition: all fauna is much smaller — trivial threat, trivial meat.",
    "VEE_Alphabeavers": "Alphabeavers occur here — they eat trees en masse and are easy meat.",
    "VEE_MigratoryHerds": "Herd animals periodically cross the map — recurring bulk meat that arrives on its own.",
    "VEE_FeralKinship": "All animals have DECREASED wildness — taming is cheaper and faster across the board.",
    "VEE_DistressedWildlife": "All animals have INCREASED wildness — taming is slower and fails more.",
    "VEE_AggressiveHerds": "🔴 Animals go manhunter on damage far more often — every hunt can turn into a fight.",
    "VEE_DomesticatedEscapees": "🔑 Wild chickens, cows and pigs spawn in small herds — free livestock, no trader needed.",
    "VEE_NobleSteeds": "🔑 Wild horses and donkeys spawn — free caravan pack animals.",
    "VEE_WanderingCompanions": "Animals bond with colonists more easily here.",
    "VEE_WastelandFauna": "Forces toxic wasteland animals into the roll. Requires a heavily polluted tile (0.5–1.0).",
    "VEE_IncreasedInfestations": "Insectoid infestations are more common — a standing threat to any roofed base.",
    "VEE_Megafauna": "Forces megasloths, mastodons, scimitar cats, great wolves, megavoles and colossus toads into the roll.",
    "VEE_AnimaFauna": "Forces anima colossi and animalisks into the roll — psychically-touched megafauna.",

    # ---- Vanilla Landmarks Expanded: disease, ore, traversal, size ----
    "VEE_NoDiseases": "🔴 Disease interval ×1000 — plague, flu and infection events effectively never fire here.",
    "VEE_ReducedDiseases": "Disease interval ×1.25 — 25% fewer disease events.",
    "VEE_IncreasedDiseases": "Disease interval ×0.75 — 25% more disease events.",
    "VEE_SteamGeysers_Decreased": "No steam geysers at all — geothermal power is off the table on this tile.",
    "VEE_MineralDevoid": "Strips ore veins out of the map — nothing worth mining on the surface.",
    "VEE_Fertility_Reduced": "Deletes every fertile soil tile — hydroponics or import, no outdoor farm.",
    "VEE_VolcanicRichSoil": "Scatters volcanic soil patches with above-average fertility.",
    "VEE_DeepOreRich": "Deep drill yield +25%.",
    "VEE_DeepOrePoor": "Deep drill yield −25%.",
    "VEE_DeepOreDevoid": "Deep ores are effectively absent — deep drills return almost nothing.",
    "VEE_HardToTraverse": "World-map movement difficulty +2 — caravans crawl across this tile.",
    "VEE_EasyToTraverse": "World-map movement difficulty −2 — caravans cross this tile fast.",
    "VEE_UndergroundGasDeposits": "Adds 8 extra deep Helixien gas deposits — fuel for gas generators.",
    "VEE_StrongerTides": "Tidal generator output +40%. Coastal tiles only.",
    "VEE_LargeRiverBanks": "Riverbank terrain doubled in width — more shore terrain, wider crossing.",
    "VEE_MineableComponentSpacer": "🔑 ADVANCED COMPONENTS MINED FROM THE ROCK — spacer components with no trader and no crafting.",
    "VEE_LargerRegion": "Map area ×1.3 — 30% more ground to hold and to search.",
    "VEE_SmallerRegion": "Map area ×0.7 — 30% less ground; everything is closer, including the raiders.",

    # ---- Vanilla Landmarks Expanded: structures, junk and salvage ----
    "VEE_RotstinkVents": "Places 6–12 rotstink vents that belch corpse-stench miasma.",
    "VEE_ToxicVents": "Places 6–12 toxic vents that periodically spew noxious green gas.",
    "VEE_SmokeVents": "Places 6–12 smoke vents — recurring visibility loss and choking air.",
    "VEE_DeadlifeVents": "🔴 Places 6–12 deadlife vents whose dust REANIMATES THE DEAD.",
    "VEE_Sinkholes": "Adds deep unstable collapse pits that expose bare rock — hazard plus exposed mining faces.",
    "VEE_AbandonedFarmland": "🔑 Places 15–25 ruined farm prefabs to strip. Ponds suppressed, 0–2 coastal sides.",
    "VEE_BombardedSurface": "🔑 Pocks the map with large, medium and small bomb craters — natural cover everywhere you fight.",
    "VEE_MechanoidShipChunks": "🔑 Scatters crashed MECHANOID SHIP CHUNKS — steel, plasteel and components with no raid attached.",
    "VEE_ContaminatedReservoir": "🔑 Litters 100–200 RADIOACTIVE BARRELS over irradiated soil — mass salvage on poisoned ground.",
    "VEE_ContaminatedRiver": "🔑 A radioactive river with 100–200 radioactive barrels on irradiated soil. Flat tiles only.",
    "VEE_ContaminatedCoast": "🔑 An irradiated shoreline with 100–200 radioactive barrels. Flat coastal tiles, ponds suppressed.",
    "VEE_JadeChunks": "Adds jadeite chunks to haul — but 75% FEWER ordinary stone chunks.",
    "VEE_ObsidianChunks": "Adds obsidian chunks to haul — but 75% FEWER ordinary stone chunks.",
    "VEE_DriftwoodShore": "Adds driftwood logs along the shore — but 75% fewer stone chunks.",
    "VEE_JadeiteMountains": "The map's stone is jade-bearing — ordinary mining yields jade.",
    "VEE_Cenotes": "Adds large and small water-filled sinkholes — water plus hazards you can fall into.",
    "VEE_FleshPits": "🔴 Adds large and small anomalous cave entrances into a flesh realm — Anomaly-tier threats attached to the tile.",

    # ---- Vanilla Landmarks Expanded: landform shapes ----
    "VEE_MeteorCrater": "A jagged impact rim around a debris-littered basin. Flat inland tiles only.",
    "VEE_ResurgentCaldera": "🔑 Volcanic collapse zone with steep walls and a central rocky dome — volcanism without live lava.",
    "VEE_CraterLake": "A rocky ring around a deep lake — water inside a natural wall. Flat inland only.",
    "VEE_ToxicCrater": "A rocky ring around a stagnant glowing pool. Ponds suppressed, flat inland only.",
    "VEE_Volcano": "🔴 An ancient caldera with a MOLTEN heart — live lava on a flat inland tile.",
    "VEE_CalmBasin": "A wind-shielded sand basin — eerily still, and it always ships with the no-wind mutator.",
    "VEE_LoneIsland": "A large island detached from the shore — 3–5 coastal sides, no land approach.",
    "VEE_DetachedIceberg": "A floating ice mass far from shore. Sub-zero tiles only (max 0°C).",
    "VEE_IceAndFire": "A floating iceberg WITH AN ACTIVE LAVA LAKE inside it. Sub-zero tiles only.",
    "VEE_LoneIslandWithLake": "A detached island with a freshwater lake in its middle — water and total isolation.",
    "VEE_LoneIslandWithMountain": "A detached island with a central peak — isolation plus mining.",
    "VEE_CoralReef": "A detached atoll ringed by coral — almost no buildable land. 3–5 coastal sides.",
    "VEE_SaltPlains": "🔑 Sterile, HARD TO TRAVERSE dried inland sea bed — nothing grows and everything moves slowly.",
    "VEE_RockRidge": "A rock ridge splits the map in two — a natural wall you did not have to build.",
    "VEE_JaggedRocks": "Thin rock ridges criss-cross the map — cover everywhere, pathing broken up.",
    "VEE_SerpentineCanyons": "Several deep fissures cut the mountain, natural elevation suppressed. Mountainous only.",
    "VEE_DryRiver": "🔑 A river bed with NO WATER — river terrain and river shape, none of the water benefits.",
    "VEE_MangroveTerrain": "Brackish interconnected pools dominate the map, ponds suppressed. Flat coastal only.",
    "VEE_DustBowl": "🔑 Sun-scorched dust wasteland — vegetation nearly gone and relentless sandstorms. Inland only.",
    "VEE_SulfuricLake": "Mildly toxic volcanic lake with sulfur vents, but NUTRIENT-RICH surrounding soil.",
    "VEE_SulfuricRiver": "An acidic sulfur-laden river with sulfur vents and scorched banks. Flat tiles only.",
    "VEE_BurnedForest": "Standing burned trees — wood you can harvest, but nothing regrowing.",
    "VEE_FloodPlains": "Riverbank terrain ×4 WIDE — a huge fertile strip and a correspondingly huge water obstacle.",
    "VEE_AlluvialFan": "Riverbank terrain ×4 wide where a river meets the coast — rich sediment, wide crossing.",
    "VEE_RelictDelta": "Dried river channels and silt fans — delta shape with no water. Flat coastal only.",
    "VEE_StagnantRivulet": "A barely-flowing silted river — water access without a strong current. Flat tiles only.",
    "VEE_StoneForest": "Towering stone spires across the map — cover and mining faces, flat inland only.",
    "VEE_GravelBeach": "A loose gravel shoreline. 1–6 coastal sides.",
    "VEE_BasaltCape": "🔑 A basalt headland on 3–5 coastal sides, rich in volcanic rock — extinct volcanism, no lava.",
    "VEE_RedDesert": "🔑 Iron-red sand across the whole map — the Tatooine look, delivered as terrain.",
    "VEE_VolcanicSandDesert": "🔑 Black volcanic sand across the whole map — dead volcanism as terrain.",
    "VEE_PermafrostBasin": "Permanently frozen ground under a thin thaw. Flat tiles at 5°C or below.",
    "VEE_DeepSnow": "Compacted deep snow that resists movement and muffles sound. Tiles at 5°C or below only.",
    "VEE_QuicksandPits": "Shallow quicksand pools that impede movement, ponds suppressed. Inland tiles only.",
    "VEE_QuicksandDunes": "🔑 Dunes plus quicksand: 85% fewer chunks, no landmarks, and ruins, shrines, utility buildings and landing pads SUPPRESSED.",
    "VEE_PebbleDunes": "Low pebble dunes on flat ground — shifting surface, little else.",
    "VEE_LittoralDunes": "Fertile wind-shaped dunes along the shore. 1–5 coastal sides.",
    "VEE_RisingWaters": "🔴 Game condition TIDAL FLOODING — large stretches of your buildable land go underwater on a cycle.",
    "VEE_IceSpires": "Tall ice columns across the map — cover made of ice, flat inland only.",
    "VEE_GlacialMoraine": "Uneven unstable rock ridges full of meltwater ponds. Flat inland only.",
    "VEE_TropicalBeach": "Warm coast that also strews 500–1000 seashells over the beach sand. 1–5 coastal sides.",
    "VEE_AnimaSoils": "Anima-infused soil that subtly influences plants, animals and minds — psyfocus terrain.",
    "VEE_AnimaSoils_Coast": "Anima-infused soil on a coastal tile — psyfocus terrain with ocean access.",

    # ---- Vanilla Landmarks Expanded: flora ----
    "VEE_AnimaFlora": "Replaces the flora with anima bushes, roots and trees, ADDS an ancient anima tree and SUPPRESSES the normal AnimaTrees step.",
    "VEE_PlantLife_Overgrown": "4x PLANT DENSITY — the biggest plant multiplier here, but only on essentially unpolluted tiles.",
    "VEE_PlantLife_Decimated": "Plants down to 15% — almost no wood, forage or cover.",
    "VEE_WildRice": "Grows wild rice — a free staple crop already in the ground.",
    "VEE_WildWheat": "Grows wild wheat — a free staple crop already in the ground.",
    "VEE_NoTrees": "No trees grow naturally — every stick of wood must be farmed or imported.",
    "VEE_PoisonousFlora": "🔴 Harvesting ANY wild plant causes toxic buildup; your own planted crops are unaffected.",
    "VEE_MangroveTrees": "Adds mangroves that grow in brackish water. Coastal tiles only.",
    "VEE_Blooming_Buttercup": "Adds wild buttercups — beauty and a little forage, no other mechanical effect.",
    "VEE_Blooming_ForgetMeNot": "Adds wild forget-me-nots — beauty and a little forage, no other mechanical effect.",
    "VEE_Blooming_Knapweed": "Adds wild knapweed — beauty and a little forage, no other mechanical effect.",
    "VEE_Blooming_Loosestrife": "Adds wild loosestrife — beauty and a little forage, no other mechanical effect.",
    "VEE_Cactus_Barrel": "🔑 Adds wild barrel cacti — desert flora that survives where nothing else does.",
    "VEE_Cactus_Beavertail": "🔑 Adds wild beavertail cacti — desert flora.",
    "VEE_Cactus_Hedgehog": "🔑 Adds wild hedgehog cacti — desert flora.",
    "VEE_Cactus_OrganPipe": "🔑 Adds wild organ pipe cacti — desert flora.",
    "VEE_RedDesertPlants": "🔑 Adds cholla and hoodia cacti adapted to red sand.",
    "VEE_VolcanicSandDesertFlora": "🔑 Restricts flora to cacti, agave, drago trees and bushes — and removes grass entirely.",
    "VEE_WildSucculents": "Adds wild aloe, jade plant, peyote and other succulents — drug and medicine flora.",
    "VEE_TropicalBeachFlora": "Restricts flora to palms, cocoa, screw pine and date palm — a food-bearing shoreline.",
    "VEE_LaurelForest": "Restricts flora to laurel, fern and grasses — damp shaded evergreen forest.",
    "VEE_MoorFlora": "Restricts flora to heather, gorse, juniper, gnarled pine, healroot and bulrush.",
    "VEE_FirewoodTrees": "Restricts flora to firewood trees, cacti, agave and berries — a fuel-wood tile.",
    "VEE_AuburnTree_Oaks": "No mechanical effect — the oaks are recoloured to permanent autumn, appearance only.",
    "VEE_AuburnTree_Poplars": "No mechanical effect — the poplars are recoloured to permanent autumn, appearance only.",
    "VEE_AuburnTree_Maples": "No mechanical effect — the maples are recoloured to permanent autumn, appearance only.",
    "VEE_AuburnTree_Birches": "No mechanical effect — the birches are recoloured to permanent autumn, appearance only.",
    "VEE_Mycelium": "Adds light-resistant glowforest-style mushrooms — food that grows without sun.",
    "VEE_PlentifulGrass": "Grass everywhere — grazing for herbivores, and fuel for any fire that starts.",
    "VEE_Mossy": "Scatters mossy soil patches. Low-pollution tiles only.",
    "VEE_Moor": "Scatters peaty waterlogged soil patches — uneven, poorly drained ground.",
    "VEE_LushLavaFields": "Scatters vegetated soil patches over cooled lava — growth on black stone, residual ground heat.",

    # ---- Vanilla Landmarks Expanded: weather and conditions ----
    "VEE_NoWind": "🔴 Game condition: WIND TURBINES PRODUCE NOTHING here, and windy weather is suppressed.",
    "VEE_RagingWind": "🔴 Game condition: constant gale plus +10 windy weather — maximum wind power, and fires run.",
    "VEE_GeomagneticStorm": "🔴 Game condition: ALL ELECTRICAL DEVICES DISABLED in this region. The harshest condition on the sheet.",
    "VEE_SkygazingSpot": "🔴 Game condition: colonists skygaze more often and get more joy from it — a free recreation source.",
    "VEE_TornadoAlley": "🔴 Frequent intense tornadoes sweep the map — a recurring building-destroying event.",
    "VEE_Sandstorms": "🔑 Sandstorm weather at +10 commonality — recurring visibility and accuracy loss on a desert tile.",
    "VEE_RottenStench": "🔴 Game condition: acrid ground vapours burn lungs and sour mood across the map.",
    "VEE_FertileRains": "Nutrient-rich rainfall boosts plant growth while it falls. Tiles above 0°C only.",
    "VEE_DustStorms": "🔑 Dust-storm weather at +10 commonality — vision-impeding storms on a desert tile.",
    "VEE_MoreSolarPower": "Solar panel output +25%.",
    "VEE_LessSolarPower": "Solar panel output −25%.",
    "VEE_FrequentAuroras": "Auroras occur much more often — a recurring free mood boost at night.",
}


# --------------------------------------------------------------------------
# LandmarkDef - derived, not hand-written.
#
# A LandmarkDef is a chooser, not a mechanic: it GUARANTEES a set of mutators
# (`mutatorChances` entries with required=true) and then rolls a bag of optional
# ones. So its real effect is exactly "the mutators it forces", and that is what
# gets composed below. `commonality` says how often the world places it.
# --------------------------------------------------------------------------
def landmark_effect(fields: dict, mutator_labels: dict, mutator_effects: dict) -> str:
    """One sentence for a LandmarkDef, composed from what it forces."""
    chances = fields.get("mutatorChances") or []
    forced = [c.get("mutator") for c in chances if c.get("required")]
    optional = [c for c in chances if not c.get("required")]
    combo = fields.get("comboLandmarkMutators") or []

    # 🔑 Consequence FIRST, provenance in a short parenthetical. An earlier draft
    # led with "Guarantees the X mutator:" and pushed every landmark sentence past
    # 25 words with a preamble that said nothing the label had not already said.
    def tail(what):
        n = " +%d optional rolls" % len(optional) if optional else ""
        c = ", combines with %d landmarks" % len(combo) if combo else ""
        return " (%s%s%s)" % (what, n, c)

    if not forced:
        return ("No mutators are forced — the tile only gets a name, an icon and "
                "%d optional rolls." % len(optional))

    # A single forced mutator IS the landmark's effect. Say that, not a preamble.
    if len(forced) == 1 and forced[0] in mutator_effects:
        core = mutator_effects[forced[0]]
        guess = core.startswith("~ ")
        lead = core[2:] if guess else core
        return ("~ " if guess else "") + lead.rstrip() + tail(
            "forces " + mutator_labels.get(forced[0], forced[0]))

    names = ", ".join(mutator_labels.get(m, m) for m in forced)
    return "Always fires %d mutators at once%s" % (len(forced), tail(names))


def mutator_effect(def_name: str, fields: dict) -> str:
    """One sentence for a TileMutatorDef.

    Authored table first. A def that is not in the table gets a field-derived
    fallback so a mod update that adds content still produces something honest
    rather than a blank line.
    """
    hit = MUTATOR.get(def_name)
    if hit:
        return hit
    return _derive(fields)


_FACTORS = (
    ("animalDensityFactor", "animals"),
    ("plantDensityFactor", "plants"),
    ("junkDensityFactor", "JUNK"),
    ("geyserCountFactor", "steam geysers"),
    ("chunkDensityFactor", "stone chunks"),
    ("fishPopulationFactor", "fish"),
)


def _derive(f: dict) -> str:
    """Last-resort sentence built only from field values. Never a guess."""
    bits = []
    for key, word in _FACTORS:
        v = f.get(key)
        if v is not None and v != 1:
            bits.append("%gx %s" % (v, word))
    if f.get("additionalGameConditions"):
        bits.append("🔴 adds game condition %s" % ", ".join(f["additionalGameConditions"]))
    if f.get("blacklistedRaidStrategies"):
        bits.append("🔴 blocks raid strategies %s" % ", ".join(f["blacklistedRaidStrategies"]))
    if f.get("allowRoofedEdgeWalkIn"):
        bits.append("🔴 raiders may walk in under a roof")
    if f.get("extraGenSteps"):
        bits.append("adds gen steps %s" % ", ".join(f["extraGenSteps"]))
    if f.get("preventGenSteps"):
        bits.append("suppresses gen steps %s" % ", ".join(f["preventGenSteps"]))
    for key, word in (("preventsPondGeneration", "no ponds"),
                      ("preventsLandmarks", "blocks landmarks"),
                      ("preventNaturalElevation", "no natural elevation"),
                      ("preventPatches", "no terrain patches")):
        if f.get(key):
            bits.append(word)
    for key, word in (("hillinessForElevationGen", "elevation rolled as"),
                      ("hillinessForOreGeneration", "ore rolled as")):
        v = f.get(key)
        if v and v != "Undefined":
            bits.append("%s %s" % (word, v))
    if not bits:
        return ("No mechanical effect found in the def — every gameplay field is at "
                "its default, so this is appearance and flavour only.")
    return ("Field-derived, not yet written up: " + "; ".join(bits) + ".").capitalize()
