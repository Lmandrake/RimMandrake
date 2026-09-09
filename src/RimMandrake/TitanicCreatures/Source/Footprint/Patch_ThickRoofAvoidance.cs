using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Card #1's other half: "a titan never paths under rock." Implemented as
    /// a near-infinite cost penalty on Pawn_PathFollower's private static
    /// CostToMoveIntoCell(Pawn, IntVec3) (Verse/AI/Pawn_PathFollower.cs) rather
    /// than a hard block: the pathfinder will always find another route around
    /// an overhead-mountain cell if one exists (the intended "never paths under
    /// rock" outcome), while a titan that is somehow ALREADY there (forced
    /// spawn, teleport) is not permanently stuck with no legal move at all.
    ///
    /// Large Pawns patches this exact method for its own square-cost purposes
    /// (confirmed by decompile - "Pawn_PathFollower.CostToMoveIntoCell | square
    /// cost"); Harmony composes multiple postfixes on the same target, so this
    /// coexists with it rather than replacing it.
    ///
    /// Roof identification: RoofDef.isThickRoof (Verse/RoofDef.cs) -
    /// RoofRockThick ("overhead mountain") is the only shipped RoofDef with it
    /// true; RoofRockThin and RoofConstructed are both false and are left to
    /// TitanicWakeProcessor to destroy on transit instead of avoiding.
    /// </summary>
    [HarmonyPatch(typeof(Pawn_PathFollower), "CostToMoveIntoCell", typeof(Pawn), typeof(IntVec3))]
    internal static class Patch_ThickRoofAvoidance
    {
        private const float ThickRoofPenalty = 100000f;

        private static void Postfix(Pawn pawn, IntVec3 c, ref float __result)
        {
            if (pawn?.Map == null || TitanicTierUtility.GetTier(pawn) == TitanicTier.None)
            {
                return;
            }
            RoofDef roof = c.GetRoof(pawn.Map);
            if (roof != null && roof.isThickRoof)
            {
                __result = Mathf.Max(__result, ThickRoofPenalty);
            }
        }
    }
}
