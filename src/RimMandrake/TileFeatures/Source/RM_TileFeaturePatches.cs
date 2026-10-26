using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.TileFeatures
{
    // RM_PoisonousFlora: harvesting a wild (unsown) plant on such a tile gives the harvester toxic buildup.
    [HarmonyPatch(typeof(Plant), nameof(Plant.PlantCollected))]
    [RimMandrake.Shared.PatchFeature("Poisonous flora", typeof(RM_TileFeaturesSettings), "floraEnabled")]
    public static class Patch_Plant_PlantCollected
    {
        public static void Prefix(Plant __instance, out Map __state)
        {
            __state = __instance?.Map; // the plant may despawn during the call
        }

        public static void Postfix(Plant __instance, Pawn by, Map __state)
        {
            if (!RM_TileFeaturesSettings.floraEnabled || __instance == null || __instance.sown || by == null || by.Dead) return;
            if (by.RaceProps == null || !by.RaceProps.IsFlesh) return;
            if (!RM_TileFeatureApplier.On(__state ?? by.Map, RM_TileFeatureDefOf.RM_PoisonousFlora)) return;
            float sev = RM_TileFeaturesSettings.poisonSeverityPerHarvest * (1f - by.GetStatValue(StatDefOf.ToxicResistance));
            if (sev > 0f) HealthUtility.AdjustSeverity(by, HediffDefOf.ToxicBuildup, sev);
        }
    }

    // RM_IncreasedInfestations: the storyteller's chance of an infestation on such a map is multiplied.
    [HarmonyPatch(typeof(IncidentWorker), nameof(IncidentWorker.ChanceFactorNow))]
    [RimMandrake.Shared.PatchFeature("More infestations", typeof(RM_TileFeaturesSettings), "infestationsEnabled")]
    public static class Patch_IncidentWorker_ChanceFactorNow
    {
        public static void Postfix(IncidentWorker __instance, IIncidentTarget target, ref float __result)
        {
            if (!RM_TileFeaturesSettings.infestationsEnabled || !(__instance is IncidentWorker_Infestation)) return;
            if (target is Map map && RM_TileFeatureApplier.On(map, RM_TileFeatureDefOf.RM_IncreasedInfestations))
                __result *= RM_TileFeaturesSettings.infestationFactor;
        }
    }
}
