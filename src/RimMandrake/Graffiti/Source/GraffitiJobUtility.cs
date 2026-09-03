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
        private const int MaxCandidates = 12;

        public static bool TryFindWallMarkCell(Pawn pawn, out IntVec3 result)
        {
            Map map = pawn.Map;
            List<IntVec3> bare = new List<IntVec3>();
            List<IntVec3> anyValid = new List<IntVec3>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, SearchRadius, useCenter: false))
            {
                if (!c.InBounds(map)) continue;
                if (!c.Standable(map)) continue;
                if (!HasCardinalWall(c, map)) continue;
                if (!pawn.CanReserveAndReach(c, PathEndMode.Touch, Danger.None)) continue;

                if (!AlreadyMarked(c, map))
                {
                    bare.Add(c);
                    if (bare.Count >= MaxCandidates) break;
                }
                else if (anyValid.Count < MaxCandidates)
                {
                    anyValid.Add(c);
                }
            }
            List<IntVec3> pool = bare.Count > 0 ? bare : anyValid;
            if (pool.Count > 0)
            {
                result = pool.RandomElement();
                return true;
            }
            result = IntVec3.Invalid;
            return false;
        }

        private static bool AlreadyMarked(IntVec3 c, Map map)
        {
            List<Thing> things = c.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i].def == RMGraffitiDefOf.RM_Graffiti_Vandal) return true;
            }
            return false;
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
