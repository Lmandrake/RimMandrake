using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.SWBestiary
{
    // PORTED_BEAST_MECHANICS_REBUILD_1 — see CompMetalEater.cs for the header.
    //
    // A metal eater must not wander off and graze, or its diet is decoration.
    // The donor did exactly this, as a prefix on the same method; ours differs
    // only in reading the pawn's comp rather than a static registry, and in
    // being switchable from Mod Settings (both the global toggle and a per-def
    // blockNormalFood, so a future creature can eat metal AND food).
    //
    // Returning false skips the original; the method's Job return stays null,
    // which is exactly "this pawn found no ordinary food to seek".
    [HarmonyPatch(typeof(JobGiver_GetFood), "TryGiveJob")]
    public static class Patch_JobGiver_GetFood_TryGiveJob
    {
        [HarmonyPrefix]
        public static bool Prefix(Pawn pawn)
        {
            if (!RSW_BeastMechanicsSettings.metalEatingEnabled)
            {
                return true;
            }
            CompMetalEater comp = pawn?.TryGetComp<CompMetalEater>();
            if (comp != null && comp.Props.blockNormalFood)
            {
                return false;
            }
            return true;
        }
    }
}
