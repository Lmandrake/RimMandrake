using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Card #1's other half: "a titan never paths under rock."
    ///
    /// CORRECTED 2026-09-11 (code-review pass): this patch target does NOT
    /// achieve that outcome and never has. Pawn_PathFollower.CostToMoveIntoCell
    /// (Verse/AI/Pawn_PathFollower.cs) has exactly one caller -
    /// TryEnterNextPathCell - and only computes the tick cost of physically
    /// stepping into a cell the route has ALREADY committed to; it is never
    /// consulted by route selection. RimWorld 1.6's actual A* search
    /// (Verse/PathFinder.cs) runs as a Burst-compiled Unity Job over
    /// PathGrid.CalculatedCostAt (Verse/AI/PathGrid.cs), which Harmony cannot
    /// reach and which has no roof term at all - confirmed by reading both:
    /// CalculatedCostAt costs terrain/things/snow/sand/fire, never
    /// map.roofGrid. So a titan's route is chosen in total ignorance of this
    /// postfix, and the postfix only ever fires AFTER the titan is already
    /// mid-step into a thick-roofed cell.
    ///
    /// Given that, the old 100000f "near-infinite" value was a real bug, not a
    /// safe deterrent: since it can never prevent the route from being chosen,
    /// its only live effect was to make that one already-committed step take
    /// up to 100000 ticks (~40 in-game hours) - a de facto freeze, not
    /// avoidance. Lowered to a bounded slow-down (still well above any normal
    /// terrain cost, so a titan visibly struggles crossing overhead mountain)
    /// rather than a multi-day stall. True route-level avoidance would need a
    /// different hook (e.g. a per-pawn AvoidGrid/IPathFindCostProvider
    /// contribution keyed to roof cells) - not implemented here; flagged via
    /// rimflow rather than built speculatively in a cleaning pass.
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
        // Was 100000f ("near-infinite"), on the false belief that a huge cost
        // here would steer the A* search away from the cell. It cannot - see
        // the class doc - so that value was a genuine bug: a titan whose
        // (roof-blind) route ever required stepping onto a thick-roofed cell
        // would stall on that single step for ~40 in-game hours. This is a
        // bounded slow-down instead, pending a real avoidance mechanism.
        private const float ThickRoofPenalty = 2000f;

        private static void Postfix(Pawn pawn, IntVec3 c, ref float __result)
        {
            if (!RM_TitanicCreaturesSettings.roofAvoidanceEnabled) return;
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
