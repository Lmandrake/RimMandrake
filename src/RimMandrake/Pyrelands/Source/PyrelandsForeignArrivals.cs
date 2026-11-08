using System;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Pyrelands
{
    // pyre_animal_distribution_correct: "no other kind wanders in". Vanilla tries a biome's own animals first, then falls back to
    // every animal in the game that tolerates the temperature (RimSage, IncidentWorker_HerdMigration.TryFindAnimalKind,
    // AggressiveAnimalIncidentUtility.TryFindAggressiveAnimalKind). Those fallbacks are what these postfixes close on this biome.
    [StaticConstructorOnStartup]
    public static class PyrelandsForeignArrivals
    {
        static PyrelandsForeignArrivals()
        {
            try
            {
                var h = new Harmony("mandrake.rm.pyrelands.foreignarrivals");
                h.Patch(AccessTools.Method(typeof(IncidentWorker_HerdMigration), "TryFindAnimalKind"),
                    postfix: new HarmonyMethod(typeof(PyrelandsForeignArrivals), nameof(HerdPostfix)));
                h.Patch(AccessTools.Method(typeof(AggressiveAnimalIncidentUtility), nameof(AggressiveAnimalIncidentUtility.TryFindAggressiveAnimalKind),
                        new[] { typeof(float), typeof(Map), typeof(PawnKindDef).MakeByRefType() }),
                    postfix: new HarmonyMethod(typeof(PyrelandsForeignArrivals), nameof(AggressiveMapPostfix)));
                h.Patch(AccessTools.Method(typeof(AggressiveAnimalIncidentUtility), nameof(AggressiveAnimalIncidentUtility.TryFindAggressiveAnimalKind),
                        new[] { typeof(float), typeof(PlanetTile), typeof(PawnKindDef).MakeByRefType() }),
                    postfix: new HarmonyMethod(typeof(PyrelandsForeignArrivals), nameof(AggressiveTilePostfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] foreign-arrivals: patch FAILED, other animals can wander in: " + e);
            }
        }

        private static bool IsPyrelands(BiomeDef b)
        {
            return b != null && PyrelandsMechanicsGate.On && Array.IndexOf(PyrelandsTuning.PyrelandsBiomeDefNames, b.defName) >= 0;
        }

        public static void HerdPostfix(Map map, ref PawnKindDef animalKind, ref bool __result)
        {
            BiomeDef b = map?.Biome;
            if (__result && IsPyrelands(b) && !b.AllWildAnimals.Contains(animalKind))
            {
                animalKind = null;
                __result = false;
            }
        }

        public static void AggressiveMapPostfix(Map map, ref PawnKindDef animalKind, ref bool __result)
        {
            Restrict(map?.Biome, ref animalKind, ref __result);
        }

        public static void AggressiveTilePostfix(PlanetTile tile, ref PawnKindDef animalKind, ref bool __result)
        {
            if (tile.Valid) Restrict(Find.WorldGrid[tile].PrimaryBiome, ref animalKind, ref __result);
        }

        // A foreign pick (the points fit nothing on the roster) becomes the roster's cheapest animal, so the threat still arrives.
        private static void Restrict(BiomeDef b, ref PawnKindDef animalKind, ref bool __result)
        {
            if (!__result || !IsPyrelands(b) || b.AllWildAnimals.Contains(animalKind)) return;
            animalKind = b.AllWildAnimals.Where(k => k.RaceProps.Animal && k.canArriveManhunter).OrderBy(k => k.combatPower).FirstOrDefault();
            __result = animalKind != null;
        }
    }
}
