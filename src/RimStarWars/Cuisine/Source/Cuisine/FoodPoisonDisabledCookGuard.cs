using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Cuisine
{
    // ROAST_STICK_FIX_DISABLED_COOK_STAT_ERRORS: roast-on-a-stick is a BasicWorker bill, so a Cooking-incapable pawn can
    // make food. Vanilla CompFoodPoisonable.Notify_RecipeProduced then reads pawn.GetStatValue(FoodPoisonChance), a stat
    // that is disabled for that pawn (skillNeedFactors Cooking), and StatWorker logs a dev-mode red ErrorOnce.
    // This prefix runs ONLY when that stat is disabled for the worker, repeats vanilla's logic exactly, and substitutes
    // the level-0 cook value (base 1 x Cooking-level-0 factor 0.05, Core Stats_Pawns_WorkRecipes.xml) for the stat read.
    // Every pawn whose stat is enabled takes the vanilla path untouched.
    public static class FoodPoisonDisabledCookGuard
    {
        public const float LevelZeroCookPoisonChance = 0.05f;
        public const string HarmonyId = "mandrake.rsw.cuisine";

        public static void Apply()
        {
            Harmony harmony = new Harmony(HarmonyId);
            harmony.CreateClassProcessor(typeof(Patch_CompFoodPoisonable_Notify_RecipeProduced)).Patch();
        }
    }

    [StaticConstructorOnStartup]
    public static class CuisineHarmonyBoot
    {
        static CuisineHarmonyBoot()
        {
            try { FoodPoisonDisabledCookGuard.Apply(); }
            catch (System.Exception e) { Log.Error("[RimStarWarsCuisine] food-poison guard not applied: " + e); }
        }
    }

    [HarmonyPatch(typeof(CompFoodPoisonable), nameof(CompFoodPoisonable.Notify_RecipeProduced))]
    public static class Patch_CompFoodPoisonable_Notify_RecipeProduced
    {
        public static bool Prefix(CompFoodPoisonable __instance, Pawn pawn)
        {
            if (pawn == null || !StatDefOf.FoodPoisonChance.Worker.IsDisabledFor(pawn))
            {
                return true;
            }
            if (Rand.Chance(pawn.GetRoom()?.GetStat(RoomStatDefOf.FoodPoisonChance) ?? RoomStatDefOf.FoodPoisonChance.roomlessScore))
            {
                __instance.SetPoisoned(FoodPoisonCause.FilthyKitchen);
            }
            else if (Rand.Chance(FoodPoisonDisabledCookGuard.LevelZeroCookPoisonChance))
            {
                __instance.SetPoisoned(FoodPoisonCause.IncompetentCook);
            }
            return false;
        }
    }
}
