using HarmonyLib;
using System;
using System.Collections.Generic;
using Verse;
using RimMandrake.HugeThings;

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
        internal static bool Prefix(Pawn __instance, ref float efficiency, ref IEnumerable<Thing> __result)
        {
            TitanicTier tier = TitanicTierUtility.GetTier(__instance);
            // Site placement, load order and the T1/T2 yield toggle must never reopen ordinary full-yield T3 butchering.
            if (RM_HugeThingsSettings.CorpseSiteActive && tier == TitanicTier.T3)
            {
                __result = Array.Empty<Thing>();
                return false;
            }
            if (!RM_HugeThingsSettings.YieldCurveActive) return true;
            if (tier != TitanicTier.T1 && tier != TitanicTier.T2)
            {
                return true;
            }
            efficiency *= YieldCurveUtility.SubLinearFactor(__instance, tier);
            return true;
        }
    }
}
