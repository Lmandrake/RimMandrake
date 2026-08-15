using HarmonyLib;
using RimWorld;   // Plant lives in RimWorld, not Verse — confirmed against Assembly-CSharp
using Verse;

namespace JawaPlantGrowth
{
    [StaticConstructorOnStartup]
    public static class JawaPlantGrowthMod
    {
        static JawaPlantGrowthMod()
        {
            try
            {
                PlantGrowthConfig.Rebuild();
            }
            catch (System.Exception e)
            {
                Log.Error("[JawaPlantGrowth] failed to build the growth tables, leaving growth vanilla: " + e);
                return;
            }

            new Harmony("mandrake.jawaplantgrowth").PatchAll();

            Log.Message(string.Format(
                "[JawaPlantGrowth] scaling {0} plant defs (default x{1}, tree x{2}), " +
                "{3} exempt, {4} terminator biome(s) at x{5}.",
                PlantGrowthConfig.ScaledCount,
                PlantGrowthConfig.DefaultMultiplier,
                PlantGrowthConfig.TreeMultiplier,
                PlantGrowthConfig.ExemptCount,
                PlantGrowthConfig.TerminatorBiomeCount,
                PlantGrowthConfig.TerminatorMultiplier));
        }
    }

    /// <summary>
    /// GrowthRate is the composite — every GrowthRateFactor_* is already folded in
    /// by the time we see __result. Scaling it here rather than any single factor is
    /// what makes the terminator case come out genuinely SLOWER than vanilla instead
    /// of merely bypassing an environmental penalty. It is also the number the
    /// inspect string reads, so the boost is visible in game.
    ///
    /// This getter runs on every plant tick on every plant, so the body is three
    /// lookups against tables built once at startup: no allocation, no LINQ, no
    /// def-database queries.
    /// </summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.GrowthRate), MethodType.Getter)]
    public static class Patch_Plant_GrowthRate
    {
        [HarmonyPostfix]
        public static void Postfix(Plant __instance, ref float __result)
        {
            // Dormant, frozen or out of its temperature band: vanilla already said
            // zero, and zero times anything is still zero.
            if (!PlantGrowthConfig.Ready || __result <= 0f) return;

            ThingDef def = __instance.def;
            if (PlantGrowthConfig.IsExempt(def)) return;

            // Unspawned or held (caravan, transport pod, minified): no map, so no
            // biome. Fall through to the non-terminator band rather than touching
            // __instance.Map twice or throwing.
            Map map = __instance.Map;

            __result *= (map != null && PlantGrowthConfig.IsTerminatorBiome(map.Biome))
                ? PlantGrowthConfig.TerminatorMultiplier
                : PlantGrowthConfig.MultiplierFor(def);
        }
    }
}
