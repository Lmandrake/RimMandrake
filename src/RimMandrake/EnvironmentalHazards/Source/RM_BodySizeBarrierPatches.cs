using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // VENOMVINE_FORTRESS_PASSABILITY_1, the two engine hooks. Both are
    // no-ops on any map that has never had a RM_CompBodySizeBarrier on it,
    // and both bail on a field read before touching the map at all.
    //
    // Armed from EnvironmentalHazardsMod's static constructor, which logs
    // and declines rather than throwing if either signature has moved.
    public static class RM_BodySizeBarrierPatches
    {
        // Pawn_PathFollower caps a cell at 450 ticks (MEASURED: `if (num >
        // 450f) num = 450f;` in CostToMoveIntoCell). Anything larger is
        // charged as 450 anyway, so clamping here keeps the number the
        // player is shown honest.
        private const int MaxCellCost = 450;

        // PREFIX on:
        //   PathFinder.CreateRequest(IntVec3 start, LocalTargetInfo target,
        //       IntVec3? dest, TraverseParms traverseParms,
        //       PathFinderCostTuning? mtuning, PathEndMode peMode, Pawn pawn,
        //       PathRequest.IPathGridCustomizer customizer)
        //
        // This is the overload that actually constructs the PathRequest; the
        // pawn-shaped overload beside it delegates here, so patching this one
        // covers every pawn path request in the game, including the one
        // Pawn_PathFollower.GenerateNewPathRequest makes.
        //
        // It only ever FILLS IN a customizer nobody supplied. Breach raids
        // (BreachingGrid.CustomTuning) and road generation
        // (UsedRectPathGridCustomizer) pass their own, and those are left
        // exactly alone — the engine takes one customizer per request and
        // overwriting theirs would break a vanilla mechanic to add ours.
        public static void CreateRequest_Prefix(IntVec3 start, Pawn pawn, ref PathRequest.IPathGridCustomizer customizer)
        {
            if (!RM_EnvironmentalHazardsSettings.bodySizeBarrierEnabled)
            {
                return; // mod option: body-size barriers disabled
            }

            if (customizer != null || pawn == null)
            {
                return;
            }

            // Flyers are over the thicket, not in it — the same carve-out
            // MapComponent_ContactVenom makes, and the same one vanilla's own
            // traps make. The engine already routes a flying pawn on the
            // Flying path grid, so this is belt and braces.
            if (pawn.Flying)
            {
                return;
            }

            Map map = pawn.Map;
            if (map == null)
            {
                return;
            }

            RM_MapComponent_BodySizeBarrier barrier = map.GetComponent<RM_MapComponent_BodySizeBarrier>();
            if (barrier == null || !barrier.AnyBarriers)
            {
                return;
            }

            customizer = barrier.CustomizerFor(pawn.BodySize, start);
        }

        // POSTFIX on:
        //   Pawn_PathFollower.GetPawnCellBaseCostOverride(Pawn pawn, IntVec3 c)
        //
        // Two consumers, and both are wanted here:
        //
        //   Pawn_PathFollower.CostToMoveIntoCell feeds it to
        //   PathGrid.CalculatedCostAt as baseCostOverride, which is what a
        //   step into the cell actually COSTS. This is the "slowly thread"
        //   half — a humanlike crossing a thicket pays ~33x a normal step.
        //
        //   RCellFinder rejects a candidate wander/rest cell outright when
        //   (GetPawnCellBaseCostOverride(pawn, c) ?? pathGrid.Cost(c)) > 20.
        //   So a large animal stops CHOOSING thicket cells as destinations,
        //   which is what stops a blocked pawn generating path requests it
        //   can never satisfy.
        //
        // Vanilla returns a value here only for water (Pawn.WaterCellCost).
        // Water and these plants cannot coexist on a cell (fertilityMin), but
        // if some future pair does, the larger cost wins rather than one
        // silently erasing the other.
        public static void GetPawnCellBaseCostOverride_Postfix(Pawn pawn, IntVec3 c, ref int? __result)
        {
            if (!RM_EnvironmentalHazardsSettings.bodySizeBarrierEnabled)
            {
                return; // mod option: body-size barriers disabled
            }

            if (pawn == null || pawn.Flying)
            {
                return;
            }

            Map map = pawn.Map;
            if (map == null)
            {
                return;
            }

            RM_MapComponent_BodySizeBarrier barrier = map.GetComponent<RM_MapComponent_BodySizeBarrier>();
            if (barrier == null || !barrier.AnyBarriers)
            {
                return;
            }

            int cost = barrier.MoveCostFor(c, pawn.BodySize);
            if (cost <= 0)
            {
                return;
            }

            cost = Mathf.Clamp(
                Mathf.RoundToInt(cost * RM_EnvironmentalHazardsSettings.bodySizeBarrierThreadCostMultiplier),
                0,
                MaxCellCost);

            if (cost <= 0)
            {
                return;
            }

            if (!__result.HasValue || __result.Value < cost)
            {
                __result = cost;
            }
        }
    }
}
