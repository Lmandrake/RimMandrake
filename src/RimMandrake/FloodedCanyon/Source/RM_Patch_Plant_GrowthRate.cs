using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // Bootstraps Harmony. Follows the sibling RimUtinni PlantGrowth mod's
    // own pattern exactly (Patch_Plant_GrowthRate.cs): patch the GETTER so
    // every GrowthRateFactor_* vanilla already folded in is still respected
    // — this only adds one more multiplier on top, never bypasses the rest.
    [StaticConstructorOnStartup]
    public static class RM_FloodedCanyonHarmony
    {
        static RM_FloodedCanyonHarmony()
        {
            new Harmony("mandrake.rm.floodedcanyon").PatchAll();
        }
    }

    // Soak-driven growth coupling (FLOOD_CANYON_BIOME_1 spec: "soak-driven
    // explosive plant growth where applicable"). Deliberately light: a
    // decaying GrowthRate multiplier on ground the flood just soaked, NOT
    // the full mesh-rebuild / visible-swelling / burst engine drafted for
    // the separate, larger, unbuilt EXPLOSIVE_PLANT_GROWTH_1 item.
    [HarmonyPatch(typeof(Plant), nameof(Plant.GrowthRate), MethodType.Getter)]
    public static class RM_Patch_Plant_GrowthRate
    {
        [HarmonyPostfix]
        public static void Postfix(Plant __instance, ref float __result)
        {
            if (!RM_FloodedCanyonSettings.growthCouplingEnabled || __result <= 0f)
            {
                return;
            }

            Map map = __instance.Map;
            if (map == null)
            {
                // Unspawned or held (caravan, minified): no map, no soak state.
                return;
            }

            RM_MapComponent_CanyonFlood comp = map.GetComponent<RM_MapComponent_CanyonFlood>();
            if (comp == null)
            {
                return;
            }

            float factor = comp.SoakFactorAt(__instance.Position, Find.TickManager.TicksGame);
            if (factor != 1f)
            {
                __result *= factor;
            }
        }
    }
}
