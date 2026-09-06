#!/usr/bin/env python3
"""Ash'karr's flora, ASSIGNED rather than inherited — one signature roster per biome.

🔴 **OWNER, 2026-08-23, verbatim:** *"I thought you had distributed the plants per biome for
me? If not, PLEASE do that right now. You, agent Decide, make those calls right now and do it…
Try to avoid using the same plant across different biome types. It's ok to draw from Tinctora,
Healroot, and other normally player-grown plants as you decorate the biomes."*
Plus, minutes later: *"We can set the appropriate temperatures later, don't worry about that as
a constraint"* ⇒ climate tolerance is `NORMALIZE_TEMPERATURE_TOLERANCES_1`, not a filter here.
**Assignment is by LOOK and LORE.**

🔑 **The rule that shapes every list below: no plant appears in two FAMILIES.** The eight
families are the design; inside one, a shared plant is deliberate kinship, across two it is the
zoo effect the owner objected to. `--check` fails the build if any plant crosses a family.

🔴 **`wildPlants` IS a `LoadDataFromXmlCustom` field and `<li>` DESTROYS THE DEF.** Read from
source, not assumed — `BiomePlantRecord.LoadDataFromXmlCustom` takes the **node NAME** as the
plant defName and the node's **value** as the commonality:

    <wildPlants>
      <Plant_TreeDrago>0.08</Plant_TreeDrago>     ✅
      <li><plant>Plant_TreeDrago</plant>…</li>    ⛔ discards the WHOLE BiomeDef, silently
    </wildPlants>

That is the same trap that cost 26 BiomeDefs and 101 CharacterDefs on 2026-08-23.

⛔ **FOUR PLANTS ARE CUT AND MUST NEVER APPEAR IN ANY ROSTER BELOW:**
`Plant_TreePine` · `Plant_TreeBirch` · `Plant_TreePoplar` · `RG_Plant_Raspberry`.
The owner cut them with Cherry Picker (`design/Jawa/mods/plant_decisions.json`, decision
`cut`), which DELETES the ThingDef at load. A BiomeDef that still names one throws
`Could not resolve cross-reference` — a red error on every load. Adding one back is a
defect, not a preference; `--check` cannot catch it because the def dump predates the cut.

    python3 design/Jawa/mods/biome_flora.py --check     # families, overlaps, defNames resolve
    python3 design/Jawa/mods/biome_flora.py --write     # emit the patch
    python3 design/Jawa/mods/biome_flora.py --doc       # regenerate the readable roster doc

⭐ `--doc` used to be a throwaway script that was written, run once and deleted, so the doc
went stale the moment anyone edited `FAMILIES`. It lives here now: one file owns the rosters,
the patch and the prose about them.
"""
import argparse, collections, csv, json, os, sqlite3, sys, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
from game_paths import DUMP_ROOT  # noqa: E402
DB = os.path.join(DUMP_ROOT, "defs.sqlite")
TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')
PATCH = os.path.join(ROOT, 'src', 'Jawa', 'Jawa_Patches', 'Patches', 'BiomeFlora_Ashkarr.xml')
POOL = os.path.join(HERE, 'plant_pool.csv')
DOC = os.path.join(ROOT, 'design', 'Jawa', 'worldbuilding', 'biome_flora_rosters.md')

# ---------------------------------------------------------------- the design
# family -> biome -> {plant defName: commonality}
# Commonality scale, held consistent so one biome does not out-shout another:
#   2.0+  the ground cover you always see      0.5-1.0  the mid layer you notice
#   0.2-0.5  punctuation                       <0.2     trees and set pieces
FAMILIES = {

 'A. dayside desert': {
  'Desert': {                       # 4,648 tiles - the face of the planet
    'AB_HardyGrass': 2.2, 'Plant_PincushionCactus': 0.8, 'Plant_Agave': 0.6,
    'Plant_DesertDandelion': 0.45, 'AB_BrownBarrelCactus': 0.25,
    'Plant_PebbleCactus': 0.35,     # tree - walk list: reads correctly for desert ground
    'Plant_SaguaroCactus': 0.12,    # tree
    'Plant_TreeDrago': 0.08,  # tree - owner: "I love the strange drago tree"
    # --- second pass 2026-08-23: use the content we already have ---
    'AreebianCactus': 0.30, 'RG_FlowerCactus': 0.25, 'GRimPebbleCactus': 0.22,
    'GRim1PebbleCactus': 0.20, 'GRimPincushionCactus': 0.35, 'GRim1PincushionCactus': 0.30,
    'GRimAgave': 0.30, 'GRimSaguaroCactus': 0.10, 'GRim1SaguaroCactus': 0.10,
    'VEE_Plant_HoodiaCactus': 0.18, 'AB_DessertTree': 0.06, 'TreeDragoberry': 0.15,
    'Plant_HubbaGourd_Wild': 0.25, 'Plant_Chakroot_Wild': 0.30, 'Plant_HubbaGourd': 0.05,
    'Plant_Chakroot': 0.05, 'GRimYellowGrass': 0.60, 'AB_Aaklac': 0.12,
    # --- residue sweep 2026-08-23: clones follow their twin into the same biome ---
    'GRimAgavePlant': 0.24,
    # --- third pass 2026-08-23, DECIDE: succulents on a desert world (1 of 3) ---
    'VCE_Plant_JadePlant': 0.30, 'VCE_Plant_AloeVera': 0.28, 'VCE_Plant_SnakePlant': 0.25},
  'ExtremeDesert': {                # 3,214 - plantDensity 0.008, all but sterile
    'AB_EuphorbiaRimworldia': 0.30, 'VCE_Plant_PincushionPlant': 0.25,
    'AB_GargantuanLithops': 0.20,   # living stones
    'AB_EuphorbiaDesiccata': 0.06,  # tree
    # --- second pass 2026-08-23: use the content we already have ---
    'AB_DeadBowerTree': 0.05, 'TreeDead': 0.04, 'GRimTreeDead': 0.04, 'AB_GiantStikehr': 0.04,
    'Plant_Bloddle': 0.10,
    # --- third pass 2026-08-23, DECIDE: succulents on a desert world (2 of 3) ---
    # the small water-hoarders, which is all this ground will carry
    'VCE_Plant_Echeveria': 0.25, 'VCE_Plant_FairyWashboard': 0.22,
    'VCE_Plant_SweetheartPlant': 0.20},
  'AridShrubland': {                # 709 - scrub, and the planet's herb garden
    'Plant_ShrubLow': 1.4, 'VEE_Gorse': 0.7, 'VEE_Heather': 0.6,
    'VEE_Plant_JuniperBush': 0.5, 'Plant_Ripthorn': 0.3,
    'Plant_HealrootWild': 0.25,  # owner licensed player-grown flora
    # --- second pass 2026-08-23: use the content we already have ---
    'GRim1Bush': 0.35, 'GRim2Bush': 0.35, 'GRim3Bush': 0.30, 'GRim4Bush': 0.30,
    'GRimBush': 0.35, 'AreebianBush': 0.30, 'BushDandys': 0.25, 'Grim3Shrub': 0.25,
    'NewGreenBush': 0.25, 'GRim1ShrubLow': 0.40, 'GRim2ShrubLow': 0.40, 'GRimShrubLow': 0.40,
    'Plant_Bush': 0.30, 'Plant_Brambles': 0.30, 'RG_Plant_BramblesRed': 0.25,
    'RG_Plant_BramblesYellow': 0.25, 'GRimBrambles': 0.25, 'VEE_Knapweed': 0.30,
    'VEE_Loosestrife': 0.30, 'VEE_ButtercupFlower': 0.25, 'VEE_ForgetMeNot': 0.25,
    'RG_Plant_AridGrass': 0.70, 'RG_Plant_Oxalis': 0.25, 'RG_Plant_Dervish': 0.20,
    'RG_Plant_CreepStern': 0.20, 'RG_Plant_CrimsonCushion': 0.20,
    'RG_Plant_LupineIceland': 0.20, 'RG_Plant_TigerLily': 0.18, 'Plant_Astragalus': 0.25,
    'Plant_Clivia': 0.20, 'Plant_Daylily': 0.20, 'Plant_Rose': 0.15,
    'RG_Plant_Plumeria': 0.15, 'GRimClivia': 0.18, 'IronScruff_Juniper': 0.25,
    'Plant_MujaFruit_Wild': 0.22, 'Plant_Nysyllin_Wild': 0.22, 'Plant_MujaFruit': 0.05,
    'Plant_Nysyllin': 0.05, 'Plant_Berry': 0.20, 'GRimBerryBush': 0.18,
    'GRim1BerryBush': 0.15, 'GRim2BerryBush': 0.15, 'GRim3BerryBush': 0.15,
    'GRim4BerryBush': 0.15, 'GRim5BerryBush': 0.15,
    # --- residue sweep 2026-08-23: clones follow their twin into the same biome ---
    'Plant_Healroot': 0.20, 'GRim1BushPoplar': 0.28, 'GRim2BushPoplar': 0.28,
    'GRimBushPoplar': 0.28, 'ZBiome_Plant_WildDaylily': 0.16, 'ZBiome_Plant_WildRose': 0.12,
    'Plant_Berry_Leafless': 0.16, 'Plant_Brambles_Leafless': 0.24,
    'Plant_Bush_Leafless': 0.24,
    # --- third pass 2026-08-23, DECIDE: the ornamentals, and the rose ---
    'VEE_Plant_Bluebell': 0.15, 'VEE_Plant_Gardenia': 0.15, 'VEE_Plant_Gentian': 0.15,
    'VEE_Plant_Petunia': 0.15, 'RotR_RoseOfRebirth': 0.12},
  'ZBiome_Badlands': {              # 545 - the cactus garden, kept whole in one place
    'VEE_Plant_ChollaCactus': 0.40, 'VEE_Plant_HedgehogCactus': 0.40,
    'VEE_Plant_BeavertailCactus': 0.35, 'VEE_Plant_BarrelCactus': 0.30,
    'VEE_Plant_OrganPipeCactus': 0.25,
    'Plant_Psychoid_Wild': 0.20,  # player-grown
    # --- second pass 2026-08-23: use the content we already have ---
    'GRim1Ripthorn': 0.30, 'GRim2Ripthorn': 0.30, 'GRimRipthorn': 0.30,
    'GRim1Thornvine': 0.28, 'GRim2Thornvine': 0.28, 'GRimThornvine': 0.28,
    'RG_Plant_LureWeed': 0.20, 'AB_RavenNettle': 0.25, 'AB_RedBugloss': 0.25,
    'Plant_TookeTrap_Wild': 0.20, 'Plant_TookeTrap': 0.05, 'BMT_Plant_Mantrap': 0.15,
    # --- residue sweep 2026-08-23: clones follow their twin into the same biome ---
    'Plant_Psychoid': 0.16, 'Plant_Thornvine': 0.22,
    # --- third pass 2026-08-23, DECIDE: succulents (3 of 3) - the CACTUS three,
    # which belong with the cactus garden rather than out on the open sand ---
    'VCE_Plant_BunnyEarsCactus': 0.32, 'VCE_Plant_PeyotePlant': 0.28,
    'VCE_Plant_Schlumbergera': 0.25},
  'ZBiome_DesertOasis': {           # 227 - the only place that reads WET on the dayside
    'Plant_Reeds': 1.2, 'Plant_Bulrush': 1.0, 'Plant_Alocasia': 0.6,
    'VEE_Plant_DatePalm': 0.35, 'AB_FanPalm': 0.30,
    'Plant_Smokeleaf_Wild': 0.20,   # player-grown
    'Plant_Ambrosia': 0.12,
    # --- second pass 2026-08-23: use the content we already have ---
    'GRimReeds': 0.60, 'GRim1Reeds': 0.60, 'GRimBulrush': 0.55, 'GRim1Alocasia': 0.35,
    'GRim2Alocasia': 0.35, 'GRimAlocasia': 0.35, 'TreePalma': 0.20, 'GRim1RatPalm': 0.18,
    'GRim2RatPalm': 0.18, 'GRimRatPalm': 0.18, 'Plant_RatPalm': 0.18,
    'RG_Plant_TallPalmTree': 0.15, 'RG_Plant_TreeDwarfPalm': 0.15, 'Plant_TreePalm': 0.15,
    'VEE_Plant_ScrewPine': 0.12, 'RG_Plant_Tidalis': 0.20, 'Plant_Rafflesia': 0.10,
    'Plant_JoganTree_Wild': 0.18, 'Plant_Meiloorun_Wild': 0.18, 'Plant_JoganTree': 0.05,
    'Plant_Meiloorun': 0.05, 'Plant_HydenockTree_Wild': 0.15, 'Plant_HydenockTree': 0.04,
    'Plant_Hops': 0.12, 'Plant_Strawberry': 0.10,
    # ⛔ RG_Plant_Raspberry removed 2026-08-23 - the owner CUT it. See the header.
    # --- residue sweep 2026-08-23: clones follow their twin into the same biome ---
    'Plant_Smokeleaf': 0.16, 'Plant_MotherAmbrosiaLGE': 0.10, 'Plant_Strawberry_Wild': 0.08,
    # --- third pass 2026-08-23, DECIDE's rulings: the oasis grove ---
    # The surviving hardwoods. They get Star Wars names in a separate rename patch, so
    # they will not read as Earth trees standing in a desert oasis.
    'Plant_TreeOak': 0.08, 'Plant_TreeMaple': 0.08, 'VEE_Plant_TreeOak_Auburn': 0.07,
    'VEE_Plant_TreeMaple_Auburn': 0.07, 'VEE_Plant_TreeBirch_Auburn': 0.06,
    'VEE_Plant_TreePoplar_Auburn': 0.06, 'VEE_Plant_Laurel': 0.06,
    'VEE_Plant_Firewood': 0.06, 'RG_Plant_TreeSplitpine': 0.05,
    # crops and drinks - the oasis is the only dayside ground worth planting
    'VBE_Plant_Coffee': 0.25, 'VBE_Plant_Tea': 0.25, 'VBE_Plant_Tobacco': 0.22,
    'VCE_Allspice': 0.20,
    # standing water, the one place on the dayside that has any
    'Plant_LilyPad': 0.30, 'Plant_Lotus': 0.25},
  'ZBiome_Grasslands': {            # 233 - hot grass plain
    'Plant_YellowGrass': 2.4, 'Plant_YellowTallGrass': 2.0, 'Plant_Haygrass': 0.5,
    'Plant_Tinctoria_Wild': 0.30,   # owner named tinctoria by name
    'Plant_Cotton_Wild': 0.30,
    # --- second pass 2026-08-23: use the content we already have ---
    'GRimBlackGrass': 0.50, 'GRimBlueGrass': 0.50, 'GRimGreenGrass': 0.50,
    'GRimNavyGrass': 0.50, 'GRimOrangeGrass': 0.50, 'GRimPurpleGrass': 0.50,
    'GRimRedGrass': 0.50, 'GRimTealGrass': 0.50, 'GRimBlackTallGrass': 0.40,
    'GRimBlueTallGrass': 0.40, 'GRimGreenTallGrass': 0.40, 'GRimNavyTallGrass': 0.40,
    'GRimOrangeTallGrass': 0.40, 'GRimPurpleTallGrass': 0.40, 'GRimRedTallGrass': 0.40,
    'GRimTealTallGrass': 0.40, 'GRimYellowTallGrass': 0.40, 'DandyGrass': 0.45,
    'DandyTallGrass': 0.40, 'Dandys': 0.35, 'Plant_Grass': 0.80, 'Plant_TallGrass': 0.70,
    'PlantTallYellowGrass': 0.50, 'Plant_Dandelion': 0.35, 'RG_Plant_BlueDandelion': 0.25,
    'RG_Plant_RedDandelion': 0.25, 'Plant_Corn': 0.10, 'Plant_Rice': 0.08,
    'Plant_Potato': 0.10, 'Plant_Dantuber_Wild': 0.20, 'Plant_Dantuber': 0.05,
    'SavannaBush': 0.30, 'SavannaTreeAcacia': 0.10, 'SavannaTreeBaobab': 0.06,
    # --- residue sweep 2026-08-23: clones follow their twin into the same biome ---
    'Plant_Cotton': 0.24, 'Plant_Tinctoria': 0.24,
    # --- third pass 2026-08-23, DECIDE: the field crops go where a field is ---
    'VCE_Wheat': 0.30, 'VCE_Sugarcane': 0.25, 'Plant_Fibercorn_Wild': 0.25,
    'Plant_Fibercorn': 0.20},
 },

 'B. contamination': {              # §6c: the danger is the GROUND, not the wildlife
  'Wasteland': {                    # 1,721
    'RG_Plant_ToxiGrass': 2.0, 'RG_Plant_TallToxiGrass': 1.2,
    'BMT_Plant_GutterPlantain': 0.6, 'BMT_Plant_ToxicIvy': 0.5,
    'BMT_Plant_TwistedDandelion': 0.5, 'BMT_Plant_ScorchedStars': 0.30,
    'BMT_Plant_WildRashroot': 0.20, 'BMT_Plant_Doomsprout': 0.15,
    # --- second pass 2026-08-23: use the content we already have ---
    'PoisonAlocasia': 0.30, 'PoisonBrambles': 0.30, 'PoisonRafflesia': 0.12,
    'PoisonShrub': 0.35, 'PoisonPlantBush': 0.30, 'PoisonPlantDandelion': 0.30,
    'PoisonPlantTallGrass': 0.50, 'PoisonMushroom': 0.20, 'PoisonPlantRaspberry': 0.15,
    'AB_ToxiGrass': 0.60, 'AB_ToxiBulb': 0.10, 'AB_GiantToxicFlower': 0.08,
    'AB_WeepingToxberry': 0.20, 'BMT_Plant_CottonCap': 0.20, 'BMT_Plant_GreyFern': 0.30,
    'BMT_Plant_PigsEars': 0.25, 'BMT_RainbowTongue': 0.15, 'BMT_Plant_PoxSorghum': 0.25,
    'RG_Plant_TreeToxipine': 0.10, 'RG_Plant_TreeToxiTeak': 0.10,
    'PoisonPlantTreeCecropia': 0.08, 'PoisonTreeCypress': 0.08, 'PoisonTreePalm': 0.08,
    'PoisonPlantTreeTeak': 0.08, 'PoisonTreeWillow': 0.08, 'BMT_Plant_EclipsusFlower': 0.15,
    'BMT_Plant_EclipsusLeaves': 0.15,
    # --- residue sweep 2026-08-23: clones follow their twin into the same biome ---
    'BMT_Plant_Rashroot': 0.16, 'Plant_TreeCypress': 0.06,
    # --- third pass 2026-08-23, DECIDE: the last of the Polluted Lands ground ---
    'Plant_GrayGrass': 0.35, 'BMT_Plant_Snaketails': 0.30,
    'BMT_Plant_TumorbulbHyacinth': 0.25, 'BMT_SpinyHops': 0.22, 'Plant_Toxipotato': 0.20,
    # the polux pair EAT pollution, so they belong where the pollution is
    'Plant_TreePolux': 0.10, 'VRE_PoluxBush': 0.08},
  'AB_TarPits': {                   # 57
    'AB_TarPuddle': 1.5, 'BMT_Plant_BloomingCorpse': 0.30,
    'BMT_Plant_TreeSnakeWillow': 0.15, 'BMT_Plant_TreeSeepingEucalyptus': 0.12,
    # --- second pass 2026-08-23: use the content we already have ---
    'AB_PollutedStikehr': 0.10, 'BMT_Plant_TreeBarbedLarch': 0.10,
    'BMT_Plant_TreeClawhandCitron': 0.10, 'BMT_Plant_CryingWolfberryBush': 0.12,
    'RG_Plant_SwampPod': 0.20},
 },

 'C. mycoid belt': {                # 2,968 tiles, ZERO river tiles - watered by the terminator
  'AB_MycoticJungle': {             # 1,939 - Alpha Biomes' fungal set, kept intact
    'AB_Agarilux': 1.2, 'AB_GlowingAgarilux': 0.6, 'AB_AgaricusDomeCap': 0.5,
    'AB_RecurvedStropharia': 0.4, 'AB_SlimyPholiota': 0.4, 'AB_WitchesOyster': 0.35,
    'AB_GiantAgarilux': 0.30, 'AB_DribblingCap': 0.20,
    'AB_GiantAgariTox': 0.15,       # tree
    'Plant_Devilstrand': 0.10,  # player-grown, and it is genuinely a fungus
    # --- second pass 2026-08-23: use the content we already have ---
    'AB_AgariluxPrime': 0.30, 'AB_Glowstool': 0.40, 'AB_Bryolux': 0.40, 'AB_LandCoral': 0.25,
    'AB_ArbuscularMycorrhiza': 0.20, 'AB_Gomphoeria': 0.25, 'AB_LilacBeacon': 0.25,
    'AB_Iashiphus': 0.20, 'AB_WildRadagast': 0.20, 'AB_SugarFamewort': 0.20,
    'AB_TangleTea': 0.20, 'AB_TinkleGrass': 0.35, 'AB_Flowers': 0.30, 'AB_GlowingGrass': 0.50,
    'AB_GiantSeptimum': 0.08, 'AB_LuminescentTree': 0.08, 'AB_GiantSunflower': 0.06,
    'AB_GiantTulip': 0.06, 'Plant_ManaxFungus': 0.25, 'Plant_MunchFungus_Wild': 0.22,
    'Plant_MunchFungus': 0.05, 'Plant_Bubblespore_Wild': 0.22, 'Plant_Bubblespore': 0.05,
    'Plant_FelucianGlowspore_Wild': 0.14, 'Plant_FelucianGlowspore': 0.04},
  'BMT_FungalForest': {             # 425 - Biomes! Caverns' set, kept intact
    'BMT_Wrinklecap': 1.0, 'BMT_Fibershroom': 0.8, 'BMT_Gleamtip': 0.6,
    'BMT_Chromacap': 0.5, 'BMT_Greatbulb': 0.4,
    'BMT_Shimbershroom': 0.25, 'BMT_Poptop': 0.20, 'BMT_Dishcap': 0.20,
    'BMT_Shinecap': 0.18,
    # --- second pass 2026-08-23: use the content we already have ---
    'BMT_BalefulBolete': 0.25, 'BMT_BleedingTooth': 0.25, 'BMT_BrightWispcap': 0.30,
    'BMT_BrightWisptoll': 0.12, 'BMT_DarkWispcap': 0.30, 'BMT_DarkWisptoll': 0.12,
    'BMT_Candlesnuff': 0.12, 'BMT_CarveShroom': 0.25, 'BMT_Chubshroom': 0.30,
    'BMT_CoralClub': 0.25, 'BMT_CrimsonCap': 0.25, 'BMT_Curlbranch': 0.12,
    'BMT_Dewshrooms': 0.30, 'BMT_ExplodingAngel': 0.10, 'BMT_FlakespireFungus': 0.12,
    'BMT_FloorMold': 0.40, 'BMT_Frigu': 0.12, 'BMT_Fungusfern': 0.35, 'BMT_GiantLeaf': 0.20,
    'BMT_Glittercap': 0.25, 'BMT_GlowingSucculent': 0.20, 'BMT_LuminousSpout': 0.25,
    'BMT_FruitingBodies': 0.35, 'BMT_Mycelium': 0.40, 'BMT_CavernMycelium': 0.35,
    'BMT_Nogtyl': 0.12, 'BMT_NogtylMarsh': 0.10, 'BMT_Nuitae': 0.25, 'BMT_NuitaeMarsh': 0.20,
    'BMT_PowerFungus': 0.20, 'BMT_Pusmelon': 0.20, 'BMT_Ravelmush': 0.12,
    'BMT_Brightbell': 0.25, 'BMT_Skulltop': 0.12, 'BMT_StinkLattice': 0.12,
    'BMT_FungalTendril': 0.30, 'BMT_VioletWimple': 0.25, 'BMT_WatOrbs': 0.25,
    'BMT_Wheelshroom': 0.25, 'BMT_Arpeau': 0.12, 'BMT_GreenArpeau': 0.12,
    'BMT_BiolumiAlgaeCarnelian': 0.20, 'BMT_BiolumiAlgaeChrysoberyl': 0.20,
    'BMT_BiolumiAlgaeCitrine': 0.20, 'BMT_BiolumiAlgaeKunzite': 0.20,
    'BMT_BiolumiAlgaeTanzanite': 0.20, 'BMT_BiolumiAlgaeTurquoise': 0.20,
    'BMT_BlackLily': 0.20, 'BMT_WrinklecapMarsh': 0.25, 'RG_SychiCap': 0.20,
    'RG_Cibarius': 0.20, 'RG_NeoAmanita': 0.20, 'RG_Potokus': 0.20, 'RG_Tripaloski': 0.20,
    'VEE_Plant_MysticCap': 0.15, 'BMT_JuiceCactus': 0.15, 'BMT_BloomingCactus': 0.15,
    'Plant_Timbershroom': 0.10,
    # --- third pass 2026-08-23, DECIDE: the two Caverns strays ---
    'BMT_HealrootGrass': 0.25, 'BMT_YumBulbs': 0.22},
  'PoisonForest': {                 # 604 - Polluted Lands' set
    'BMT_Plant_PaganThorns': 0.8, 'BMT_Plant_PlagueFans': 0.7,
    'BMT_Plant_Toxcaps': 0.6, 'BMT_Plant_Pestia': 0.5,
    'BMT_Plant_WeepingHagbloom': 0.30,
    'BMT_Plant_TreeTwistingThornwood': 0.18,  # owner: "I love the … twisting thornwood"
    'BMT_Plant_TreeBlotBirch': 0.15, 'BMT_Plant_TreeScalpedCypress': 0.12,
    'BMT_Plant_TreeMartyr': 0.10,   # owner: "I love the … martyr"
    'BMT_Plant_TreeWormoak': 0.10,
    # --- second pass 2026-08-23: use the content we already have ---
    'GRim1Witchwood': 0.12, 'GRim2Witchwood': 0.12, 'GRimWitchwood': 0.12,
    'GRim1TreeSnagroot': 0.12, 'GRimTreeSnagroot': 0.12, 'Mushpine': 0.12, 'GrimMush': 0.30,
    'GrimShroom': 0.30, 'GRimPsilocap': 0.20, 'VEE_DayBoomshroom': 0.15,
    'VEE_DayPsilocap': 0.15, 'VEE_DayWillowgill': 0.15, 'RG_Plant_MutatedFern': 0.25,
    'RG_Plant_MutatedFungus': 0.25, 'RG_Plant_Cathedralis': 0.15, 'RG_Plant_GlowLeaf': 0.20,
    # --- residue sweep 2026-08-23: clones follow their twin into the same biome ---
    'Plant_Witchwood': 0.10, 'Boomshroom': 0.12, 'Plant_Psilocap': 0.12,
    'Plant_TreeSnagroot': 0.10, 'Plant_Willowgill': 0.12, 'Plant_Psilocap_Farmed': 0.12,
    # --- third pass 2026-08-23, DECIDE: beside their sibling thornwood ---
    'BMT_Plant_TwistingThorngrass': 0.30, 'BMT_Plant_TwistingThornweed': 0.25,
    'BMT_Plant_TreeWhistlingCane': 0.10},
 },

 'D. river jungle': {               # 599 tiles, 233 of them river - it stands in water
  'AB_FeraliskInfestedJungle': {    # 534
    'AB_TallSlimyGrass': 1.8, 'AB_GreenRockFern': 0.7,
    'AB_JungleTree': 0.30, 'AB_JungleTree_Polluted': 0.15,
    'AB_KeeningCordax': 0.12, 'AB_GiantFlower': 0.10,
    # --- second pass 2026-08-23: use the content we already have ---
    'RG_Plant_TropicalFern': 0.40, 'RG_Plant_TropicalIvy': 0.35,
    'RG_Plant_TropicalBrambles': 0.30, 'RG_Plant_TropicalChokevine': 0.30,
    'JungleShrub': 0.35, 'GRim1Chokevine': 0.25, 'GRim2Chokevine': 0.25,
    'GRim3Chokevine': 0.25, 'GRimChokevine': 0.25, 'Plant_Chokevine': 0.30,
    'Plant_TreeCecropia': 0.12, 'Plant_TreeTeak': 0.10, 'Plant_TreeBamboo': 0.12,
    'TreeCedar': 0.08, 'SwordFern': 0.35, 'RG_Plant_TemperateFern': 0.30,
    'RG_Plant_BorealFern': 0.25, 'VEE_Plant_Fern': 0.30, 'GRim1BambooBush': 0.25,
    'GRimBambooBush': 0.25, 'TreeAreeb': 0.10, 'TreeBlareebian': 0.10, 'TreeCypre': 0.08,
    'TreeGralma': 0.08, 'TreeGrimber': 0.08, 'GRimTreePolux': 0.08, 'GrimPepper': 0.15,
    'Plant_TreeCocoa': 0.08,
    # --- residue sweep 2026-08-23: clones follow their twin into the same biome ---
    'Plant_TreeCocoa_Wild': 0.06, 'RG_Plant_TemperateIvy': 0.28, 'VCE_ChocolateBush': 0.06,
    # --- third pass 2026-08-23, DECIDE: it stands in water, so the water flora lands here ---
    'VFEI2_TendrilmossVines': 0.30, 'Plant_TreeArchean': 0.06},
  'AB_MiasmicMangrove': {           # 65
    'BMT_Plant_SewerReed': 1.2, 'AB_ParasiticMangrove': 0.4,
    'AB_MangroveTree': 0.35, 'AB_MangrovePalm': 0.30,
    'BMT_Plant_TreeTanglerootMangrove': 0.20, 'VEE_Mangrove': 0.20,
    # --- second pass 2026-08-23: use the content we already have ---
    'WetlandTreeMangrove': 0.15, 'GrimCoral': 0.25, 'CoralTreeBlack': 0.12,
    'CoralTreeBlue': 0.12, 'CoralTreeOrange': 0.12, 'BiomesIslands_CoconutPalm': 0.15,
    'GRimTreeWillow': 0.10, 'Plant_TreeWillow': 0.10, 'RG_Plant_TreeWhiteWillow': 0.10,
    'RG_Plant_TreeCornish': 0.08},
 },

 'E. frozen nightside': {
  'AB_RockyCrags': {                # 3,816 - the dark. Sparse on purpose.
    'AB_FrostLeaf': 0.9, 'AB_RimeNodules': 0.6, 'BMT_RimeFlower': 0.4,
    'AB_FlashFrozenTree': 0.10,
    # --- second pass 2026-08-23: use the content we already have ---
    'RG_Plant_Coldheart': 0.30, 'RG_Plant_TundraGrass': 0.45,
    'RG_Plant_TundraTallGrass': 0.35, 'RG_Plant_TundraCotton': 0.25, 'BMT_ReindeerMoss': 0.40,
    'GRim1Moss': 0.35, 'GRim2Moss': 0.35, 'GRim3Moss': 0.35, 'GRim4Moss': 0.35,
    'GRimMoss': 0.35, 'Plant_Moss': 0.40, 'RG_Plant_Nightguide': 0.25,
    'RG_Tree_TundraTreePine': 0.06, 'VEE_Plant_GnarledPine': 0.05, 'GRim1TreeGrayPine': 0.05,
    'GRim2TreeGrayPine': 0.05, 'GRimTreeGrayPine': 0.05,
    'Plant_TreeGrayPine': 0.05,     # was 0.00 - a 0.0 entry NEVER spawns; matched to its
                                    # three GRiNDTerra siblings above
    # --- residue sweep 2026-08-23: clones follow their twin into the same biome ---
    # ⛔ Plant_TreePine removed 2026-08-23 - the owner CUT it. See the header.
    'RG_Plant_BlueTreePine': 0.05, 'RG_Plant_LargeTreePine': 0.05,
    'RG_Plant_OrangeTreePine': 0.05,
    # --- third pass 2026-08-23, DECIDE: the night plants, on the permanent nightside.
    # That is the whole point of them. ---
    'Plant_Nightgrass': 0.35, 'Plant_NightRafflesia': 0.20},
  'AB_PropaneLakes': {              # 554 - an industrial accident, frozen
    'AB_CrystalFlower': 0.5, 'AB_CrystalHorn': 0.4, 'BMT_Crystal_BlueSowable': 0.30,
    # --- second pass 2026-08-23: use the content we already have ---
    'CaveCrystal': 0.45, 'TreeCrystal': 0.10, 'BMT_RimeFlowerGrowable': 0.20},
  'HorrorWastes': {                 # 468 - BIOWEAPON class. The danger is the wildlife.
    'HorrorWeb': 1.2,               # its own mod's plant, used by nothing until now
    'AB_BloodBouquet': 0.5, 'AB_GlobularPlant': 0.4, 'AB_TentacularPlant': 0.35,
    'AB_FleshTree': 0.12,  # ⛔ Plant_Agave is GONE - a desert succulent at -49 C
    # --- second pass 2026-08-23: use the content we already have ---
    'Grimtacle': 0.55, 'AB_GlobularPlant_Polluted': 0.18,
    # --- third pass 2026-08-23, DECIDE: bioweapon rot ---
    'AA_RottingMound': 0.25},
  'BMT_CrystalCaverns': {           # 127
    'CrystalSmall': 1.0, 'BMT_CrystaltipBrambles': 0.8, 'CrystalShard': 0.6,
    'CrystalBig': 0.30, 'BMT_Crystalcap': 0.30,
    # --- second pass 2026-08-23: use the content we already have ---
    'BMT_Gleamcap': 0.35, 'BMT_Glowbulb': 0.35, 'BMT_Brightbells': 0.30,
    'BMT_Greyfields': 0.30, 'BMT_RoyalBracket': 0.25, 'BMT_Shimmershroom': 0.30,
    'BMT_MoonlessStripesPlant': 0.25, 'BMT_MortalMorelPlant': 0.25,
    'BMT_StarchstalkPlant': 0.25, 'BMT_Stimquill': 0.20, 'BMT_KessingerPlant': 0.20,
    'BMT_JadeGlintsCrop': 0.20, 'BMT_DulcisPlant': 0.20, 'BMT_CapscoolFungus': 0.20,
    'BMT_AmbrosyxFungus': 0.20, 'BMT_Blastpod': 0.15, 'BMT_GreyLady': 0.15,
    'BMT_AbyssalGrapesVine': 0.20, 'Agarilux': 0.30, 'Bryolux': 0.30, 'Glowstool': 0.30,
    'CaveShroom': 0.30, 'Plant_Fibershroom': 0.25, 'Plant_Cottonshroom': 0.20,
    'Plant_DevilShroom': 0.20, 'Plant_GoldShroom': 0.20, 'Plant_NeutroShroom': 0.20,
    'Plant_PsychoidShroom': 0.20, 'Plant_SteelShroom': 0.20, 'Plant_Psykshroom': 0.20,
    'Plant_Giantshroom': 0.20, 'Plant_Healshroom': 0.20, 'Plant_Jellyshroom': 0.20,
    'Plant_Meatshroom': 0.20, 'Plant_Microshroom': 0.20, 'Plant_Timbercap': 0.15,
    'Plant_Nutrifungus': 0.15},
 },

 'F. volcanic': {
  'Volcano': {                      # 23 - owner ruled it needs NO wood, so no tree here
    'Plant_Fireweed': 0.9, 'GRimMagmaCactus': 0.6, 'BMT_Sagecrust': 0.4,
    # --- second pass 2026-08-23: use the content we already have ---
    'GRimFireweed': 0.50,
    # --- residue sweep 2026-08-23: clones follow their twin into the same biome ---
    'GRim1Fireweed': 0.72,
    # --- third pass 2026-08-23, DECIDE: geysers are volcanic (1 of 2) ---
    'IronScruff_PrimordialGrass': 0.35, 'IronScruff_PrimordialTallGrass': 0.30},
  'LavaField': {                    # 15
    'Plant_MagmaCactus': 0.7, 'BMT_FireLavender': 0.6, 'BMT_HeatsinkFungus': 0.20,
    # --- third pass 2026-08-23, DECIDE: geysers are volcanic (2 of 2) ---
    'IronScruff_Bindweed': 0.25},
  'AB_PyroclasticConflagration': {  # 31
    'AG_Gamma': 0.5, 'AB_GiantGamma': 0.30, 'AB_FirevineTree': 0.20,
    'AB_ToxicGamma': 0.15,
    # --- second pass 2026-08-23: use the content we already have ---
    'AG_Septimum': 0.25},
 },

 'G. machine and scar': {
  'AB_MechanoidIntrusion': {        # 236 - contamination class, computronium ground
    'BMT_VoltaicFungus': 0.30, 'AB_TechnoTree': 0.15, 'AB_SessileMechanoid': 0.12,
    'AB_GoldenCubeTree': 0.08},
  'Scarlands': {                    # 90 - where a weapon was used and left
    'BMT_RustPuff': 0.8, 'BMT_BurnedMushroom': 0.6, 'AG_DarkGamma': 0.4,
    'BurnedTree': 0.20},
 },

 'H. alien': {                      # bioweapon class, but ENGINEERED LIFE rather than cold
  'AB_GelatinousSuperorganism': {   # 96
    'AB_SlimyFern': 0.9, 'AB_Slimecasia': 0.6, 'AB_SlimyTree': 0.30,
    'AB_LargeSlimyTree': 0.20,
    # --- third pass 2026-08-23, DECIDE: VEE's alien flora reads genuinely alien (1 of 2) ---
    'VEE_Plant_VyspStrands': 0.30, 'VEE_Plant_CyllenCluster': 0.25,
    'VEE_Plant_MyrloxTree': 0.20},
  'AB_OcularForest': {              # 3 - it watches
    'AB_EyeGrass': 1.2, 'AB_RedLeaves': 0.7, 'AB_RedPlantsTall': 0.5,
    'AB_AlienTree': 0.4, 'AB_AlienTree_Polluted': 0.20, 'AB_HalfAlienTree': 0.15,
    # --- second pass 2026-08-23: use the content we already have ---
    'AA_AlienTree': 0.20, 'AA_AlienGrass': 0.60, 'AA_RedLeaves': 0.40,
    'AA_RedPlantsTall': 0.35, 'AB_AlienGrass': 0.50, 'AA_Heat_Ambrosia': 0.10,
    'AA_Plant_PollenTrumpet': 0.20,
    # --- third pass 2026-08-23, DECIDE: VEE's alien flora (2 of 2) ---
    'VEE_Plant_PinkGrass': 0.35, 'VEE_Plant_TallPinkGrass': 0.30,
    'VEE_Plant_PhoraxTree': 0.22, 'VEE_Plant_XyrilTree': 0.20},
 },

 # ══════════════════════════════════════════════════════════════════════════════════════
 # DELIBERATELY UNPLACED - DECIDE's third-pass ruling, 2026-08-23. NOT an oversight.
 # Each of these is absent from every roster above for a reason. Do not "finish the job"
 # by adding one; check here first.
 #
 #   ANIMA and GAURANLEN (16)  Plant_TreeAnima · Plant_GrassAnima · Plant_TreeGauranlen ·
 #     Plant_PodGauranlen · Plant_MossGauranlen · AM_Plant_CorruptedPodGauranlen ·
 #     VEE_Plant_AnimaBell · VEE_Plant_AnimaBrambles · VEE_Plant_AnimaBush ·
 #     VEE_Plant_AnimaHeartBlossom · VEE_Plant_AnimaHusk · VEE_Plant_AnimaRoot ·
 #     VEE_Plant_FakeAnimaTree · VEE_Plant_GrandAnimaTree · VEE_Plant_TreeAnima_Ancient ·
 #     VEE_Plant_YoungAnimaTree
 #     They arrive by their OWN mechanisms - meditation focus, Gauranlen pods and Dryads,
 #     VLE landmark spawns - never through a biome's wildPlants. A wildPlants entry would
 #     scatter sacred trees like weeds and break the mechanic that gives them meaning.
 #
 #   EVENT- AND ENTITY-SPAWNED   Plant_PsychicLotus · Plant_PsychicLotusSeedling ·
 #     Plant_TreeHarbinger. The lotus arrives with its event; the harbinger tree arrives
 #     with the entity. Neither is terrain.
 #
 #   Plant_TreeBonsai            decorative only - sowTags is DecorativeTree.
 #   Plant_HydroDevilstrand_GT   hydroponics-only variant of Plant_Devilstrand, which is
 #                               already placed in AB_MycoticJungle.
 #   VGE_OxyalgaePlant           gravship life support. Not terrain flora at all.
 #
 #   ⛔ CUT BY THE OWNER, and this is the hard one:
 #     Plant_TreePine · Plant_TreeBirch · Plant_TreePoplar · RG_Plant_Raspberry
 #     Cherry Picker DELETES these ThingDefs at load. Naming one in a BiomeDef throws
 #     `Could not resolve cross-reference` on every single load. See the header.
 #
 #   Also unplaced and not worth a line each: every ChoppedStump_*/SmashedStump_* (they
 #   are what a felled tree leaves behind), every *_Wilted VEE variant (an event state),
 #   and the *Planted/*Cultivated/*Decorative/*Growable player-sown twins of plants
 #   already placed wild.
 # ══════════════════════════════════════════════════════════════════════════════════════
}

PLANTLESS = {'Ocean', 'Lake', 'SeaIce', 'IceSheet'}   # by design, not by omission

# 🔴 DECIDE'S DENSITY RULING, 2026-08-23 (`BARE_BIOMES_NEED_DENSITY_1`).
# A roster nobody sees fixes nothing. Two biomes ship a `plantDensity` so low that whatever
# we assign them reads as bare ground — together 4,935 tiles, 22.6% of the planet.
# ⛔ Only these two are touched. Density is a DIFFERENT lever from roster and it feeds the
# fire ecology (`hydrology_and_fire_ecology.md` R-H3 makes plant growth the fuel), so this
# is a named exception list, never a sweep.
DENSITY = {
  # biome: (new, shipped, why)
  'Wasteland': (0.12, 0.0099,
     "1,721 tiles of CONTAMINATION-class ground carrying an eight-plant toxic roster - "
     "toxigrass, gutter plantain, twisted dandelion, scorched stars - that exists to say "
     "THIS GROUND IS POISONED. At 0.0099 it says nothing. Poisoned ground reads more "
     "strongly with sick plants on it than with nothing. 12x up, still visibly barren."),
}
# ⛔ `ExtremeDesert` stays at its shipped 0.008 and that is a RULING, not an oversight.
# It is the lethal core of the dayside, median 48.2 C, and its four succulents are MEANT to
# be scarce. Bare ground there is the honest reading of the place; a player crossing 3,214
# tiles of genuinely dead sand is experiencing the planet, not a defect.


# ── the head-and-tail rule ────────────────────────────────────────────────────────
# 🔴 **DECIDE's ruling, 2026-08-23.** A biome whose plants all carry a similar weight has
# no dominant flora, and a biome with no dominant flora has no identity. The third pass
# ("the 84 leftovers land") fixed the zoo effect ACROSS biomes and quietly recreated it
# WITHIN the big ones: `BMT_FungalForest`'s top five carried 19.7% of 69 plants, against
# 84% for `HorrorWastes` — and HorrorWastes is the one you can name by looking at it.
#
# 🔑 **The ROSTER is not touched; only the WEIGHTS are.** Every plant keeps its home, so
# the no-crossing guarantee cannot reopen and no plant is made homeless. The transform is
# `w ** p`, which is monotone — it NEVER reorders two plants, it only widens the gap the
# author already wrote.
#
# ✅ **Fuel-neutral, and that was CHECKED, not assumed.** `WildPlantSpawner.cs:699` picks a
# plant with `GetCommonalityOfPlant(plant) / PlantsCommonalitiesSum` — a RELATIVE weight —
# while the NUMBER of plants comes from `GetDesiredPlantsCountAt(cell, plantDensityFactor)`.
# Rescaling commonalities cannot change plant MASS, so the fire-ecology rule R-H3 in
# `hydrology_and_fire_ecology.md` is not in play here.
HEAD_N      = 5      # "the flora you actually notice"
HEAD_FLOOR  = 0.50   # below this share the biome reads as soup — shape it
HEAD_TARGET = 0.60   # shape up to here and no further; a 95% head is a monoculture
TAIL_FLOOR  = 0.01   # ⛔ never 0 — a 0.0 commonality NEVER spawns (cf. Plant_TreeGrayPine)


def _head_share(ws, n=HEAD_N):
    ws = sorted(ws, reverse=True)
    tot = sum(ws)
    return sum(ws[:n]) / tot if tot else 0.0


def shape(roster):
    """Widen an over-flat roster until its top HEAD_N carry ~HEAD_TARGET of the weight.

    Returns (roster, exponent). An exponent of 1.0 means the roster was already shaped
    and nothing was changed.
    """
    if len(roster) <= HEAD_N or _head_share(roster.values()) >= HEAD_FLOOR:
        return roster, 1.0
    lo, hi = 1.0, 8.0
    for _ in range(50):                              # bisect for the gentlest exponent
        mid = (lo + hi) / 2
        if _head_share([w ** mid for w in roster.values()]) < HEAD_TARGET:
            lo = mid
        else:
            hi = mid
    top = max(roster.values())
    scale = top / (top ** hi)                        # keep the head's authored number
    return {k: max(TAIL_FLOOR, round((w ** hi) * scale, 4))
            for k, w in roster.items()}, hi


def load():
    con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    plants, biomes = {}, {}
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='ThingDef'"):
        d = json.loads(j)
        if d['fields'].get('plant'):
            plants[d['defName']] = d
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='BiomeDef'"):
        d = json.loads(j)
        biomes[d['defName']] = d
    return plants, biomes


def placed():
    from verify_frozen import warn_if_stale
    warn_if_stale(TILES)
    c = collections.Counter(r['biome'] for r in csv.DictReader(open(TILES, encoding='utf-8')))
    return c


def check(plants, biomes, tiles):
    bad = 0
    owner = {}                       # plant -> family
    for fam, bs in FAMILIES.items():
        for b, roster in bs.items():
            if b not in biomes:
                print(f"🔴 BIOME NOT IN DEFS: {b}"); bad += 1
            if b not in tiles:
                print(f"🔴 BIOME NOT ON THE MAP: {b}"); bad += 1
            for p in roster:
                if p not in plants:
                    print(f"🔴 PLANT NOT IN DEFS: {p}  (biome {b})"); bad += 1
                prev = owner.get(p)
                if prev and prev != fam:
                    print(f"🔴 CROSS-FAMILY REUSE: {p}  in '{prev}' and '{fam}'"); bad += 1
                owner.setdefault(p, fam)
    covered = {b for bs in FAMILIES.values() for b in bs}
    missing = set(tiles) - covered - PLANTLESS
    for b in sorted(missing):
        print(f"🔴 PLACED BIOME WITH NO ROSTER: {b} ({tiles[b]} tiles)"); bad += 1
    return bad, owner


def _tile_temps():
    from verify_frozen import warn_if_stale
    warn_if_stale(TILES)
    t = collections.defaultdict(list)
    for r in csv.DictReader(open(TILES, encoding='utf-8')):
        t[r['biome']].append(float(r['temp_c']))
    return t


def doc(plants, biomes, tiles):
    """Regenerate design/Jawa/worldbuilding/biome_flora_rosters.md from FAMILIES."""
    temps = _tile_temps()
    nb = sum(len(bs) for bs in FAMILIES.values())
    ndistinct = len({p for bs in FAMILIES.values() for r in bs.values() for p in r})

    cold = pool = 0
    if os.path.exists(POOL):
        for r in csv.DictReader(open(POOL, encoding='utf-8')):
            pool += 1
            try:
                cold += float(r['minGrowthTemp']) >= 0   # >= : a plant whose floor IS 0 °C
                                                        # also will not grow below it
            except (TypeError, ValueError):
                pass

    o = ["# Ash'karr's flora — what grows where, and why", '',
         '> 🔴 **GENERATED** by `design/Jawa/mods/biome_flora.py --doc`. The rosters live in that',
         "> file's `FAMILIES` dict; edit there and regenerate, never here.", '',
         '**Owner\'s brief, 2026-08-23, verbatim:** *"distribute the plants per biome… You, agent Decide,',
         'make those calls right now… Try to avoid using the same plant across different biome types.',
         "It's ok to draw from Tinctora, Healroot, and other normally player-grown plants as you",
         'decorate the biomes."*', '',
         '🔑 **The rule that shapes everything below: no plant appears in two FAMILIES.** Inside one',
         'family a shared plant is kinship; across two it is the zoo effect he objected to. The',
         'generator refuses to build if any plant crosses.', '',
         '⭐ **His three named favourites all have a home** — `Plant_TreeDrago` in `Desert`,',
         '`BMT_Plant_TreeTwistingThornwood` and `BMT_Plant_TreeMartyr` in `PoisonForest`, where the',
         'rest of the Polluted Lands trees live.', '',
         '⛔ **Four plants are CUT and appear nowhere below** — `Plant_TreePine`, `Plant_TreeBirch`,',
         '`Plant_TreePoplar`, `RG_Plant_Raspberry`. The owner removed them with Cherry Picker, which',
         'deletes the ThingDef at load; a BiomeDef still naming one throws a red cross-reference error',
         'on every load. The full list of everything left unplaced ON PURPOSE — anima, Gauranlen,',
         'event-spawned and hydroponics-only flora — is the comment block at the foot of `FAMILIES`.', '']
    if pool:
        o += ['⚠️ **Climate was deliberately NOT a filter.** He ruled *"we can set the appropriate',
              f'temperatures later"* — {cold} of {pool} plants will not grow below 0 °C and half this planet is',
              'colder than that. Making these rosters actually live is `NORMALIZE_TEMPERATURE_TOLERANCES_1`.', '']
    o += [f'**{len(FAMILIES)} families · {nb} biomes · {ndistinct} plants, all distinct.** '
          f'{len(PLANTLESS)} biomes carry no flora by design: '
          + ', '.join(f'`{b}`' for b in sorted(PLANTLESS)) + '.', '']

    for fam, bs in FAMILIES.items():
        o += [f'## {fam}', '']
        for b, roster in sorted(bs.items(), key=lambda kv: -tiles.get(kv[0], 0)):
            f = biomes[b]['fields']
            dens = f.get('plantDensity') or 0.0
            ts = temps.get(b) or [0.0]
            med = sorted(ts)[len(ts) // 2]
            warn = ('  🔴 **`plantDensity` is near zero — this roster will almost never be seen**'
                    if dens < 0.05 else '')
            o.append(f'### `{b}` — {tiles.get(b, 0):,} tiles · {min(ts):.0f} … {max(ts):.0f} °C '
                     f'(median {med:.0f}) · plantDensity {dens:g}{warn}')
            o += ['', f'*was {len(f.get("wildPlants") or [])} inherited plants → '
                      f'now **{len(roster)}** assigned*', '',
                  '| commonality | plant | | mod |', '|---:|---|---|---|']
            for p, w in sorted(roster.items(), key=lambda kv: -kv[1]):
                d = plants[p]
                tree = '🌳' if (d['fields']['plant'].get('treeCategory') or 'None') != 'None' else ''
                o.append(f'| {w:g} | **{d["fields"].get("label") or p}** | {tree} | '
                         f'`{p}` · {d.get("modName") or "?"} |')
            o.append('')
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    open(DOC, 'w', encoding='utf-8').write('\n'.join(o).rstrip() + '\n')
    print(f'wrote {DOC}  ({nb} biomes, {ndistinct} plants)')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--doc', action='store_true')
    a = ap.parse_args()
    if not os.path.exists(DB):
        print(f'UNMEASURED no defs.sqlite at {DB} — run `measure build`'); return 2
    plants, biomes = load()
    tiles = placed()
    bad, owner = check(plants, biomes, tiles)

    shaped = []
    for _fam, _bs in FAMILIES.items():
        for _b in list(_bs):
            _new, _p = shape(_bs[_b])
            if _p != 1.0:
                _bs[_b] = _new
                shaped.append((_b, _p))

    nb = sum(len(bs) for bs in FAMILIES.values())
    print(f"\n{len(FAMILIES)} families · {nb} biomes · {len(owner)} distinct plants · "
          f"{sum(len(r) for bs in FAMILIES.values() for r in bs.values())} assignments")
    print(f"{len(PLANTLESS)} biomes plantless by design: {', '.join(sorted(PLANTLESS))}")
    if bad:
        print(f"\n🔴 {bad} problem(s) — nothing written."); return 1
    print("✅ every defName resolves · no plant crosses a family · every placed biome covered")
    if shaped:
        print(f"head-and-tail rule reshaped {len(shaped)} over-flat roster(s): "
              + ", ".join(f"{b} ^{p:.2f}" for b, p in sorted(shaped, key=lambda kv: -kv[1])))
    if a.doc:
        doc(plants, biomes, tiles)
    if not a.write:
        if not a.doc:
            print("\n(pass --write to emit the patch, --doc to regenerate the roster doc)")
        return 0

    out = ['<?xml version="1.0" encoding="utf-8"?>', '<Patch>',
           '  <!-- GENERATED by design/Jawa/mods/biome_flora.py - do not hand-edit.',
           '',
           "       Ash'karr's flora, ASSIGNED rather than inherited. Owner's brief 2026-08-23:",
           '       distribute the plants per biome, avoid using the same plant across different',
           '       biome types, and player-grown flora (tinctoria, healroot) may decorate.',
           '',
           '       🔴 wildPlants is a LoadDataFromXmlCustom field: the node NAME is the plant',
           '       defName and its VALUE is the commonality. An <li> here discards the whole',
           '       BiomeDef, silently. -->', '']
    for fam, bs in FAMILIES.items():
        out.append(f'  <!-- ============ {fam} ============ -->')
        for b, roster in sorted(bs.items(), key=lambda kv: -tiles.get(kv[0], 0)):
            # ⛔ NO MayRequire. The dump's packageId names the mod that last RETEXTURED a
            # def, not the one that defines it: Core's `Desert` reports GRiNDTerra, so a
            # MayRequire built from it would skip Core biomes whenever that mod is absent.
            # PatchOperationConditional is the correct guard and it is sufficient — a biome
            # that does not exist simply fails the xpath and the <match> never runs.
            out.append('  <Operation Class="PatchOperationConditional">')
            out.append(f'    <xpath>/Defs/BiomeDef[defName="{b}"]/wildPlants</xpath>')
            out.append('    <match Class="PatchOperationReplace">')
            out.append(f'      <xpath>/Defs/BiomeDef[defName="{b}"]/wildPlants</xpath>')
            out.append('      <value>')
            out.append('        <wildPlants>')
            for p, w in sorted(roster.items(), key=lambda kv: -kv[1]):
                lab = plants[p].get('label') or ''
                tree = ' - tree' if (plants[p]['fields']['plant'].get('treeCategory') or 'None') != 'None' else ''
                out.append(f'          <{p}>{w}</{p}> <!-- {lab}{tree} -->')
            out.append('        </wildPlants>')
            out.append('      </value>')
            out.append('    </match>')
            out.append('  </Operation>')
            out.append('')
    out.append('  <!-- ============ plantDensity - the named exception list ============ -->')
    for b, (new_d, old_d, why) in DENSITY.items():
        out.append(f'  <!-- {b}: {old_d} -> {new_d}.')
        for line in textwrap.wrap(why, 92):
            out.append(f'       {line}')
        out.append('  -->')
        out.append('  <Operation Class="PatchOperationConditional">')
        out.append(f'    <xpath>/Defs/BiomeDef[defName="{b}"]/plantDensity</xpath>')
        out.append('    <match Class="PatchOperationReplace">')
        out.append(f'      <xpath>/Defs/BiomeDef[defName="{b}"]/plantDensity</xpath>')
        out.append(f'      <value><plantDensity>{new_d}</plantDensity></value>')
        out.append('    </match>')
        out.append('  </Operation>')
        out.append('')
    out.append('</Patch>')
    os.makedirs(os.path.dirname(PATCH), exist_ok=True)
    open(PATCH, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print(f"\nwrote {PATCH}  ({nb} roster + {len(DENSITY)} density operations)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
