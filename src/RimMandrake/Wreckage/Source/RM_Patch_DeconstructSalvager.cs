using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Wreckage
{
    // Who is stripping this wreck? ThingComp.PostDestroy is not told, and
    // JobDriver_Deconstruct.FinishedRemoving is exactly
    //   base.Target.Destroy(DestroyMode.Deconstruct);
    //   pawn.records.Increment(RecordDefOf.ThingsDeconstructed);
    // (RimSage, read 2026-10-06), so a prefix that notes the pawn and a
    // finalizer that clears it bracket the Destroy call, and every comp's
    // PostDestroy inside it can read the salvager. Ninefold already postfixes
    // the same method (Patch_BuildingDeconstructed.cs); a prefix/finalizer
    // pair does not interact with that postfix.
    public static class RM_SalvageContext
    {
        [ThreadStatic]
        public static Pawn Salvager;
    }

    [HarmonyPatch(typeof(JobDriver_Deconstruct), "FinishedRemoving")]
    public static class RM_Patch_DeconstructSalvager
    {
        public static void Prefix(JobDriver_Deconstruct __instance)
        {
            RM_SalvageContext.Salvager = __instance.pawn;
        }

        public static Exception Finalizer(Exception __exception)
        {
            RM_SalvageContext.Salvager = null;
            return __exception;
        }
    }
}
