using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using RimMandrake.HugeThings;

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
    /// ROUTE avoidance is Patch_PathGridDoorsBlockedJob_RoofExclusion below
    /// (TITAN_ROOF_AVOIDANCE_1). This step-cost postfix remains only as the
    /// slow crawl of a titan that is already under rock and walking out.
    /// (B2.6) The cost is bounded by the engine itself: 1.6 CostToPayThisTick
    /// raises the payment to nextCellCostTotal/450, so any cost takes at most
    /// about 450 ticks per step, never "~40 in-game hours".
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
        // A step-cost only (route choice never reads it); the engine caps any step at about 450 ticks (B2.6).
        private const float ThickRoofPenalty = 2000f;

        private static void Postfix(Pawn pawn, IntVec3 c, ref float __result)
        {
            if (!RM_HugeThingsSettings.RoofAvoidanceActive) return;
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

    /// <summary>
    /// TITAN_ROOF_AVOIDANCE_1 (owner card #1 of TITANIC_CREATURES_MOD_1: "a titan never paths under rock"; review B3.5 / D3.1 /
    /// D1.4). Route-level exclusion through the per-request providerCost array: 1.6 PathGridDoorsBlockedJob.Execute (a managed
    /// job, run once per path request before the Burst PathFinderJob) fills providerCost, and PathFinderJob.IndexCost treats
    /// ushort.MaxValue as cost 10000, which its neighbour loop skips as impassable (verified against the 1.6 decompile).
    /// For a tiered pawn, every anchor cell whose footprint (its current OccupiedRect, Large Pawns' square when loaded) would
    /// overlap a thick roof is marked impassable. A titan whose footprint is ALREADY under rock gets a high finite cost instead,
    /// so it can still path out by the least-roofed way. Runs off the main thread on scheduled requests: it only reads.
    /// </summary>
    [HarmonyPatch(typeof(PathGridDoorsBlockedJob), nameof(PathGridDoorsBlockedJob.Execute))]
    internal static class Patch_PathGridDoorsBlockedJob_RoofExclusion
    {
        private const ushort EscapeCost = 2000;
        [System.ThreadStatic] private static bool[] thickBuf, markBuf;

        private static void Postfix(PathGridDoorsBlockedJob __instance)
        {
            try
            {
                Apply(__instance);
            }
            catch (System.Exception e)
            {
                Log.ErrorOnce("[RimMandrake.TitanicCreatures] roof route exclusion failed; this path ignores overhead mountain: " + e, 0x52a0f1);
            }
        }

        private static void Apply(PathGridDoorsBlockedJob job)
        {
            if (!RM_HugeThingsSettings.RoofAvoidanceActive) return;
            Pawn pawn = job.pawn;
            Map map = job.map;
            if (pawn == null || map == null || pawn.Map != map || TitanicTierUtility.GetTier(pawn) == TitanicTier.None) return;
            int w = map.Size.x, h = map.Size.z, n = w * h;
            if (!job.providerCost.IsCreated || job.providerCost.Length < n) return;
            if (thickBuf == null || thickBuf.Length != n) { thickBuf = new bool[n]; markBuf = new bool[n]; }
            System.Array.Clear(markBuf, 0, n);
            RoofGrid roofs = map.roofGrid;
            CellIndices idx = map.cellIndices;
            bool any = false;
            for (int i = 0; i < n; i++)
            {
                RoofDef r = roofs.RoofAt(i);
                thickBuf[i] = r != null && r.isThickRoof;
                any |= thickBuf[i];
            }
            if (!any) return;
            IntVec3 pos = pawn.Position;
            CellRect foot = pawn.OccupiedRect();
            bool escaping = false;
            foreach (IntVec3 c in foot)
                if (c.InBounds(map) && thickBuf[idx.CellToIndex(c)]) { escaping = true; break; }
            RM_TitanicKernel.MarkRoofExcluded(w, h, thickBuf, foot.minX - pos.x, foot.minZ - pos.z, foot.maxX - pos.x, foot.maxZ - pos.z, markBuf);
            ushort cost = escaping ? EscapeCost : ushort.MaxValue;
            for (int i = 0; i < n; i++)
            {
                if (!markBuf[i]) continue;
                // CellIndices: index = z * w + x, the same order the kernel used
                if (escaping) { if (job.providerCost[i] < cost) job.providerCost[i] = cost; }
                else job.providerCost[i] = cost;
            }
        }
    }
}
