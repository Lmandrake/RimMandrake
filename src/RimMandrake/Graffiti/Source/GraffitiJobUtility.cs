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

        public static bool TryFindWallMarkCell(Pawn pawn, out IntVec3 result)
        {
            Map map = pawn.Map;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, SearchRadius, useCenter: false))
            {
                if (!c.InBounds(map)) continue;
                if (!c.Standable(map)) continue;
                if (!HasCardinalWall(c, map)) continue;
                if (!pawn.CanReserveAndReach(c, PathEndMode.Touch, Danger.None)) continue;
                result = c;
                return true;
            }
            result = IntVec3.Invalid;
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
