using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // Shared cell-finding logic for both the ordinary joy path
    // (JoyGiver_PaintGraffiti) and the mental-break spree path
    // (JobGiver_GraffitiPaintingSpree) - one implementation, not two copies.
    public static class GraffitiJobUtility
    {
        private const int SearchRadius = 12;

        // Fixed 2026-09-02 (opus code review): RadialCellsAround yields cells in
        // fixed ascending-distance order, so returning the FIRST valid match
        // meant a stationary pawn got the exact same cell every call, and
        // nothing here excluded a cell that already carries the mark - a whole
        // mental-break spree effectively repainted one wall, contradicting the
        // break's own letter ("will randomly smear walls"). Now gathers a bag
        // of candidates (capped, so this stays bounded on a big open room) that
        // don't already carry the mark, and picks one at random; only falls
        // back to an already-marked cell if nothing bare was found.

        public static bool TryFindWallMarkCell(Pawn pawn, out IntVec3 result)
        {
            Map map = pawn.Map;
            var cells = new List<IntVec3>();
            var states = new List<RM_MarkCell>();
            int bareSeen = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, SearchRadius, useCenter: false))
            {
                bool usable = c.InBounds(map) && c.Standable(map) && HasCardinalWall(c, map) && pawn.CanReserveAndReach(c, PathEndMode.Touch, Danger.None);
                cells.Add(c);
                bool marked = usable && AlreadyMarked(c, map);
                states.Add(new RM_MarkCell(usable, marked));
                if (usable && !marked && ++bareSeen >= RM_GraffitiKernel.MaxCandidates) break;
            }
            return PickFrom(cells, states, out result);
        }

        private static bool PickFrom(List<IntVec3> cells, List<RM_MarkCell> states, out IntVec3 result)
        {
            List<int> pool = RM_GraffitiKernel.Gather(states);
            if (pool.Count > 0)
            {
                result = cells[pool.RandomElement()];
                return true;
            }
            result = IntVec3.Invalid;
            return false;
        }

        // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1: with a pool of marks (not just
        // RM_Graffiti_Vandal) now in play, "already marked" means any
        // Filth_Mark, not one specific def - otherwise the spree would
        // happily stack a Tag right on top of a Stencil at the same cell
        // instead of finding a bare wall (going-over is for placers that
        // WANT to cover a rival's mark, not the ordinary wander target).
        private static bool AlreadyMarked(IntVec3 c, Map map)
        {
            List<Thing> things = c.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Filth_Mark) return true;
                if (things[i].def == RMGraffitiDefOf.RM_Graffiti_Vandal) return true;
            }
            return false;
        }

        // RaidExitTagger's own finder: unlike TryFindWallMarkCell, this
        // takes a bare position (not a pawn to reserve-and-path for) -
        // the raider is leaving RIGHT NOW, not walking anywhere, so this
        // is an instant environmental stamp near where they stood, not a
        // job. No CanReserveAndReach gate (nobody needs to path there);
        // still requires a cardinal wall and an in-bounds standable cell,
        // same physical eligibility as the ordinary finder.
        private const int RaidExitSearchRadius = 6;

        public static bool TryFindWallMarkCellNear(IntVec3 near, Map map, out IntVec3 result)
        {
            var cells = new List<IntVec3>();
            var states = new List<RM_MarkCell>();
            int bareSeen = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(near, RaidExitSearchRadius, useCenter: true))
            {
                bool usable = c.InBounds(map) && c.Standable(map) && HasCardinalWall(c, map);
                cells.Add(c);
                bool marked = usable && AlreadyMarked(c, map);
                states.Add(new RM_MarkCell(usable, marked));
                if (usable && !marked && ++bareSeen >= RM_GraffitiKernel.MaxCandidates) break;
            }
            return PickFrom(cells, states, out result);
        }

        private static bool HasCardinalWall(IntVec3 c, Map map)
        {
            foreach (IntVec3 adj in GenAdj.CardinalDirections)
            {
                IntVec3 n = c + adj;
                if (!n.InBounds(map)) continue;
                if (n.GetEdifice(map) is Building building && building.def.Fillage == FillCategory.Full)
                {
                    return true;
                }
            }
            return false;
        }
    }
}
