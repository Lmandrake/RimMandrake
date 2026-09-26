using HarmonyLib;
using RimWorld;   // Plant lives in RimWorld, not Verse — confirmed against Assembly-CSharp
using Verse;

namespace RimMandrake.Utinni.PlantGrowth
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
                Log.Error("[RimMandrake.Utinni.PlantGrowth] failed to build the growth tables, leaving growth vanilla: " + e);
                return;
            }

            new Harmony("mandrake.rut.plantgrowth").PatchAll();

            Log.Message(string.Format(
                "[RimMandrake.Utinni.PlantGrowth] scaling {0} plant defs (default x{1}, tree x{2}), " +
                "{3} exempt, {4} terminator biome(s) at x{5}, {6} wet-ambient biome(s) at x{7} (tree x{8}).",
                PlantGrowthConfig.ScaledCount,
                PlantGrowthConfig.DefaultMultiplier,
                PlantGrowthConfig.TreeMultiplier,
                PlantGrowthConfig.ExemptCount,
                PlantGrowthConfig.TerminatorBiomeCount,
                PlantGrowthConfig.TerminatorMultiplier,
                PlantGrowthConfig.WetAmbientBiomeCount,
                PlantGrowthConfig.WetAmbientMultiplier,
                PlantGrowthConfig.WetAmbientTreeMultiplier));
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
            if (!PlantGrowthSettings.growthEnabled) return;

            // Dormant, frozen or out of its temperature band: vanilla already said
            // zero, and zero times anything is still zero.
            if (!PlantGrowthConfig.Ready || __result <= 0f) return;

            ThingDef def = __instance.def;
            if (PlantGrowthConfig.IsExempt(def)) return;

            // Unspawned or held (caravan, transport pod, minified): no map, so no
            // biome. Fall through to the non-terminator band rather than touching
            // __instance.Map twice or throwing.
            Map map = __instance.Map;

            // Three ambient bands, exactly one applies (they REPLACE each
            // other, never stack): terminator x0.4, the three wet biomes x10
            // (ruling 6, 2026-09-21), everywhere else x4. The explosive-growth
            // SOAK multiplier is a separate event tier owned by
            // mandrake.rm.explosivegrowth's own postfix and multiplies on top
            // of whichever band this picks — do not fold it in here.
            BiomeDef biome = map?.Biome;
            if (biome != null && PlantGrowthConfig.IsTerminatorBiome(biome))
                __result *= PlantGrowthConfig.TerminatorMultiplier;
            else if (biome != null && PlantGrowthConfig.IsWetAmbientBiome(biome))
                __result *= PlantGrowthConfig.WetAmbientMultiplierFor(def);
            else
                __result *= PlantGrowthConfig.MultiplierFor(def);
        }
    }
}
