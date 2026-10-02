using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // CHILL_CRYOPONICS_GROWER_1 / CHILL_FLOOR_GROWING_BED_1 — the four engine
    // checks that stop a deep-bed plant (maxGrowthTemperature -20 C,
    // wildTerrainTags RM_TheChillBed) living in a grower. Decompiled 1.6:
    //   * PlantUtility.GrowthSeasonNow(cell,..)  -> sowing refused / growth 0
    //   * PlantUtility.CanEverPlantAt(..)        -> map-tile temperature test
    //   * Plant.GrowthRateFactor_Temperature     -> growth multiplier
    //   * Plant.DyingBecauseOfTerrainTags        -> plant takes damage off its
    //     wild terrain tag even inside a grower (vanilla never needed this
    //     because no vanilla plant with tags is sown in a grower)
    // The first three are lifted only for an ACTIVE cryoponics vat; the last
    // for either Chill grower, since the floor bed also stands on bare ice
    // bedrock rather than liquid propane.

    [HarmonyPatch(typeof(PlantUtility), nameof(PlantUtility.GrowthSeasonNow),
        new[] { typeof(IntVec3), typeof(Map), typeof(ThingDef) })]
    public static class RM_Patch_CryoGrowthSeason
    {
        [HarmonyPostfix]
        public static void Postfix(IntVec3 c, Map map, ref bool __result)
        {
            if (!__result && RM_Building_CryoGrower.ActiveCryoAt(c, map))
            {
                __result = true;
            }
        }
    }

    [HarmonyPatch(typeof(PlantUtility), nameof(PlantUtility.CanEverPlantAt),
        new[] { typeof(ThingDef), typeof(IntVec3), typeof(Map), typeof(Thing),
                typeof(bool), typeof(bool), typeof(bool) },
        new[] { ArgumentType.Normal, ArgumentType.Normal, ArgumentType.Normal, ArgumentType.Out,
                ArgumentType.Normal, ArgumentType.Normal, ArgumentType.Normal })]
    public static class RM_Patch_CryoCanEverPlant
    {
        [HarmonyPrefix]
        public static void Prefix(IntVec3 c, Map map, ref bool checkMapTemperature)
        {
            if (checkMapTemperature && RM_Building_CryoGrower.ActiveCryoAt(c, map))
            {
                checkMapTemperature = false;
            }
        }
    }

    [HarmonyPatch(typeof(Plant), nameof(Plant.GrowthRateFactor_Temperature), MethodType.Getter)]
    public static class RM_Patch_CryoGrowthRate
    {
        [HarmonyPostfix]
        public static void Postfix(Plant __instance, ref float __result)
        {
            if (__instance.Spawned && RM_Building_CryoGrower.ActiveCryoAt(__instance.Position, __instance.Map))
            {
                __result = 1f;
            }
        }
    }

    [HarmonyPatch(typeof(Plant), nameof(Plant.DyingBecauseOfTerrainTags), MethodType.Getter)]
    public static class RM_Patch_ChillGrowerTerrainTags
    {
        [HarmonyPostfix]
        public static void Postfix(Plant __instance, ref bool __result)
        {
            if (__result && __instance.Spawned
                && RM_Building_CryoGrower.ChillGrowerAt(__instance.Position, __instance.Map))
            {
                __result = false;
            }
        }
    }
}
