using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SEABED_FLOOR_AMBIENT_CARRYOVER_1 — plants and ongoing fauna on a sea-floor LAYER map.
    //
    // The hatch's pocket maps used the SEA biome itself (pocketMapProperties.biome) plus the
    // RM_SeaFloorHabitat mutator (animalDensityFactor 30). A layer map uses the FLOOR biome of its
    // tile, which shipped with plantDensity 0, animalDensity 0 and no cast, so the vanilla Plants
    // step grew nothing and WildAnimalSpawner never refilled a cleared floor.
    //
    // At startup each floor biome takes its sea's flora and cast: the sea is whichever surface
    // biome names this floor through RM_SeabedAccessExtension.floorBiome (data that already
    // exists; no per-sea code, and no cross-reference that breaks when the seas' mod is absent).
    //   plants:  wildPlants + plantDensity + wildPlantRegrowDays copied as-is (the pocket map used
    //            the sea biome with no plant mutator, so this is the same growth);
    //   animals: wildAnimals copied, animalDensity = sea x RM_SeabedFloorExtension.animalDensityFactor
    //            (30, the hatch mutator's factor; TileInfo.AnimalDensity reads the floor biome).
    // Commonalities come from the sea's own CommonalityOfPlant/OfAnimal, so patch-added and
    // wildBiomes-declared entries carry over too.
    //
    // Temperature is not here: each floor biome carries constantOutdoorTemperature in XML, which
    // MapTemperature.OutdoorTemp/SeasonalTemp return for any map on that biome (RimSage-read).
    //
    // Plant growth-rate guard (Patch_SeabedPlantGrowthGuard): decompile-read 2026-10-03, the path
    // it insures (TileTemperaturesComp.RetrieveCachedData) keys its cache per LayerDef and sizes it
    // from tile.Layer.TilesCount, so no seabed-specific throw was found. The guard stays as cheap
    // insurance until a floor map with plants has loaded live.
    [StaticConstructorOnStartup]
    public static class RM_SeabedFloorLife
    {
        public static readonly Dictionary<BiomeDef, BiomeDef> SeaOfFloor = new Dictionary<BiomeDef, BiomeDef>();
        private static readonly Dictionary<BiomeDef, float> FactorOfFloor = new Dictionary<BiomeDef, float>();

        static RM_SeabedFloorLife()
        {
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.seabedFloorLifeEnabled)
            {
                return;
            }

            foreach (BiomeDef sea in DefDatabase<BiomeDef>.AllDefsListForReading)
            {
                BiomeDef floor = sea.GetModExtension<RM_SeabedAccessExtension>()?.floorBiome;
                RM_SeabedFloorExtension ext = floor?.GetModExtension<RM_SeabedFloorExtension>();
                if (ext == null)
                {
                    continue;
                }

                if (SeaOfFloor.TryGetValue(floor, out BiomeDef earlier))
                {
                    Log.Warning("[RimMandrake.DivingInteraction] " + floor.defName + " is named as the floor of both "
                        + earlier.defName + " and " + sea.defName + "; keeping " + earlier.defName + "'s life.");
                    continue;
                }

                SeaOfFloor[floor] = sea;
                FactorOfFloor[floor] = ext.animalDensityFactor;
                CopyLife(sea, floor, ext.animalDensityFactor);
            }
        }

        // MEASURED 2026-10-06 (live, full list): Map Designer (zylle.mapdesigner) snapshots every biome's densities in
        // its own static constructor (ctor 835 of 1610, before this one at 1607) and writes them back when a game
        // starts ("[Map Designer] Applying settings"), so the floor's XML 0 returned: the copied plant/animal LISTS
        // survived, both densities read 0.0, and a Grey floor map grew 0 of its 16 plants. Densities are therefore
        // re-asserted right before a floor map generates and whenever a game finishes initialising.
        public static void Reassert(BiomeDef floor)
        {
            if (floor == null || !SeaOfFloor.TryGetValue(floor, out BiomeDef sea))
            {
                return;
            }

            float animals = sea.animalDensity * FactorOfFloor[floor];
            if (floor.plantDensity != sea.plantDensity || floor.animalDensity != animals)
            {
                Log.Message("[RimMandrake.DivingInteraction] " + floor.defName + " densities were reset by another mod (plant "
                    + floor.plantDensity + ", animal " + floor.animalDensity + "); restored from " + sea.defName
                    + " (plant " + sea.plantDensity + ", animal " + animals + ")");
                floor.plantDensity = sea.plantDensity;
                floor.animalDensity = animals;
            }
        }

        public static void ReassertAll()
        {
            foreach (BiomeDef floor in SeaOfFloor.Keys)
            {
                Reassert(floor);
            }
        }

        public static void CopyLife(BiomeDef sea, BiomeDef floor, float animalDensityFactor)
        {
            var plants = new List<BiomePlantRecord>();
            foreach (ThingDef plant in sea.AllWildPlants)
            {
                plants.Add(new BiomePlantRecord { plant = plant, commonality = sea.CommonalityOfPlant(plant) });
            }

            var animals = new List<BiomeAnimalRecord>();
            foreach (PawnKindDef kind in sea.AllWildAnimals)
            {
                float c = sea.CommonalityOfAnimal(kind);
                if (c > 0f)
                {
                    animals.Add(new BiomeAnimalRecord { animal = kind, commonality = c });
                }
            }

            floor.wildPlants = plants;
            floor.plantDensity = sea.plantDensity;
            floor.wildPlantRegrowDays = sea.wildPlantRegrowDays;
            Traverse.Create(floor).Field("wildAnimals").SetValue(animals);
            floor.animalDensity = sea.animalDensity * animalDensityFactor;

            // Drop every lazily built cache so the copied lists are what the engine reads.
            foreach (string f in new[] { "cachedAnimalCommonalities", "cachedPlantCommonalities", "cachedWildPlants",
                                         "cachedLowestWildPlantOrder", "cachedMaxWildPlantsClusterRadius" })
            {
                Traverse.Create(floor).Field(f).SetValue(null);
            }
        }
    }

    [HarmonyPatch(typeof(Game), nameof(Game.FinalizeInit))]
    public static class Patch_SeabedFloorLifeReassert
    {
        public static void Postfix()
        {
            RM_SeabedFloorLife.ReassertAll();
        }
    }
}
