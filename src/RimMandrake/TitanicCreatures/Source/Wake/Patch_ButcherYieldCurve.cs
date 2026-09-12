using HarmonyLib;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Applies YieldCurveUtility to ordinary butchering of a T1/T2 titan
    /// corpse. Pawn.ButcherProducts(Pawn butcher, float efficiency) is a
    /// yield-return iterator; Harmony's Prefix still runs before the
    /// compiler-generated state machine is constructed, so mutating `ref
    /// efficiency` here changes the value baked into that state machine, which
    /// is what MeatAmount/LeatherAmount get multiplied by inside it.
    /// </summary>
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.ButcherProducts))]
    internal static class Patch_ButcherYieldCurve
    {
        private static void Prefix(Pawn __instance, ref float efficiency)
        {
            if (!RM_TitanicCreaturesSettings.yieldCurveEnabled) return;
            TitanicTier tier = TitanicTierUtility.GetTier(__instance);
            if (tier != TitanicTier.T1 && tier != TitanicTier.T2)
            {
                return;
            }
            efficiency *= YieldCurveUtility.SubLinearFactor(__instance, tier);
        }
    }
}
