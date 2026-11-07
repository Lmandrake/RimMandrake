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

        // A calm painter (roomCap) leaves a room alone once it carries its share: a colony's own marks are never
        // cleaned, so without this every bedroom ended up hideous by midgame. A spree has no such manners.
        public static bool TryFindWallMarkCell(Pawn pawn, out IntVec3 result, bool roomCap = false)
        {
            Map map = pawn.Map;
            var cells = new List<IntVec3>();
            var states = new List<RM_MarkCell>();
            var marksInRoom = roomCap ? CountMarksByRoom(map) : null;
            int bareSeen = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, SearchRadius, useCenter: false))
            {
                bool usable = c.InBounds(map) && c.Standable(map) && HasCardinalWall(c, map) && pawn.CanReserveAndReach(c, PathEndMode.OnCell, Danger.None)
                    && (!roomCap || !RoomFull(c, map, marksInRoom));
                cells.Add(c);
                bool marked = usable && AlreadyMarked(c, map);
                states.Add(new RM_MarkCell(usable, marked));
                if (usable && !marked && ++bareSeen >= RM_GraffitiKernel.MaxCandidates) break;
            }
            return PickFrom(cells, states, map, out result);
        }

        private static Dictionary<Room, int> CountMarksByRoom(Map map)
        {
            var counts = new Dictionary<Room, int>();
            foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Filth))
            {
                if (t is Filth_Mark)
                {
                    Room room = t.Position.GetRoom(map);
                    if (room != null)
                    {
                        counts.TryGetValue(room, out int n);
                        counts[room] = n + 1;
                    }
                }
            }
            return counts;
        }

        private static bool RoomFull(IntVec3 c, Map map, Dictionary<Room, int> counts)
        {
            Room room = c.GetRoom(map);
            if (room == null) return false;
            counts.TryGetValue(room, out int n);
            return RM_GraffitiKernel.RoomHoldsEnough(n, room.CellCount);
        }

        private static bool PickFrom(List<IntVec3> cells, List<RM_MarkCell> states, Map map, out IntVec3 result)
        {
            List<int> pool = RM_GraffitiKernel.Gather(states);
            if (pool.Count > 0)
            {
                // A side face shows a sliver; a hand with a whole front face in reach mostly uses it.
                if (Rand.Value < RM_GraffitiKernel.FrontFaceBias)
                {
                    List<int> fronts = pool.FindAll(i => Filth_Mark.ReadWallSide(cells[i], map) == 0);
                    if (fronts.Count > 0) pool = fronts;
                }
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
        //
        // A mark is drawn ON the wall, so "marked" is about the wall, not this floor
        // cell: a one-cell tag beside a three-cell piece is painted over it, and so is
        // a tag on the far side of a one-thick wall, whose drawing lands on the same cell.
        private static bool AlreadyMarked(IntVec3 c, Map map)
        {
            int side = Filth_Mark.ReadWallSide(c, map);
            if (side == RM_GraffitiKernel.NoWall)
            {
                foreach (Thing t in c.GetThingList(map))
                {
                    if (t is Filth_Mark) return true;
                }
                return false;
            }
            return Filth_Mark.MarksOverlapping(c + new Rot4(side).FacingCell, side, 0.5f, map, null).Count > 0;
        }

        /// <summary>How many cells wide a mark centred on this floor cell's wall may be: the unbroken run of this face on either side of
        /// the middle, doubled from the shorter side. A corner, a door or the wall's end limits it; 1 at least. A side face, a sliver, takes
        /// less than a front.</summary>
        public static float WallRoom(IntVec3 c, Map map)
        {
            int side = Filth_Mark.ReadWallSide(c, map);
            if (side == RM_GraffitiKernel.NoWall)
            {
                return 1f;
            }
            int face = RM_GraffitiKernel.FaceOfSide(side);
            IntVec3 wall = c + new Rot4(side).FacingCell;
            RM_GraffitiKernel.AlongOf(face, out int ax, out int az);
            IntVec3 along = new IntVec3(ax, 0, az);
            int a = 0, b = 0;
            while (a < MaxWallReach && WallPlane.FaceAt(wall + along * (a + 1), map, face)) a++;
            while (b < MaxWallReach && WallPlane.FaceAt(wall - along * (b + 1), map, face)) b++;
            return System.Math.Min(1 + 2 * System.Math.Min(a, b), RM_GraffitiKernel.MaxWidthOnFace(face));
        }

        private const int MaxWallReach = 3;

        // RaidExitTagger's own finder: unlike TryFindWallMarkCell, this
        // takes a bare position (not a pawn to reserve-and-path for) -
        // the raider is leaving RIGHT NOW, not walking anywhere, so this
        // is an instant environmental stamp near where they stood, not a
        // job. No CanReserveAndReach gate (nobody needs to path there);
        // still requires a cardinal wall and an in-bounds standable cell,
        // same physical eligibility as the ordinary finder, and the cell
        // must be EXTERIOR (IsExteriorCell): a raider who turned to leave
        // from inside the base must not tag an interior wall.
        private const int RaidExitSearchRadius = 6;

        public static bool TryFindWallMarkCellNear(IntVec3 near, Map map, out IntVec3 result)
        {
            var cells = new List<IntVec3>();
            var states = new List<RM_MarkCell>();
            int bareSeen = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(near, RaidExitSearchRadius, useCenter: true))
            {
                bool usable = c.InBounds(map) && c.Standable(map) && HasCardinalWall(c, map) && IsExteriorCell(c, map);
                cells.Add(c);
                bool marked = usable && AlreadyMarked(c, map);
                states.Add(new RM_MarkCell(usable, marked));
                if (usable && !marked && ++bareSeen >= RM_GraffitiKernel.MaxCandidates) break;
            }
            return PickFrom(cells, states, map, out result);
        }

        /// <summary>An exterior cell: unroofed, and its room known and psychologically outdoors (Verse.Room, rw16).</summary>
        internal static bool IsExteriorCell(IntVec3 c, Map map)
        {
            Room room = c.GetRoom(map);
            return RM_GraffitiKernel.ExteriorFace(c.Roofed(map), room != null, room != null && room.PsychologicallyOutdoors);
        }

        /// <summary>A wall to paint here, on a side the camera can see. A wall south of the cell shows only its cap: nobody would see the mark.</summary>
        internal static bool HasCardinalWall(IntVec3 c, Map map)
        {
            return IsFullWallAt(c + IntVec3.North, map) || IsFullWallAt(c + IntVec3.East, map) || IsFullWallAt(c + IntVec3.West, map);
        }

        /// <summary>The wall test every mark placer and Filth_Mark's wall-face draw share: an in-bounds wall or rock face. Not any
        /// full-fillage edifice: a door swings and a cooler is a machine, and neither is a surface to paint a mark across.</summary>
        internal static bool IsFullWallAt(IntVec3 n, Map map)
        {
            return n.InBounds(map) && n.GetEdifice(map) is Building building && IsPaintableWall(building.def);
        }

        internal static bool IsPaintableWall(ThingDef def)
        {
            return def.Fillage == FillCategory.Full && (def.building?.isNaturalRock == true || def.graphicData?.Linked == true);
        }
    }
}
