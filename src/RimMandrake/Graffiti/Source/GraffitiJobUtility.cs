using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // Shared cell-finding logic for both the ordinary joy path
    // (JoyGiver_PaintGraffiti) and the mental-break spree path
    // (JobGiver_GraffitiPaintingSpree) - one implementation, not two copies.
    public static class GraffitiJobUtility
    {
        /// <summary>The ideoligion a pawn paints and reads by, or null when the game is played without one. In Ideology's classic mode
        /// every faction, raiders included, carries the player's hidden ideo (FactionIdeosTracker), so a raider's mark would read as our
        /// own faith and a sigil would paint an icon the player never chose.</summary>
        internal static Ideo IdeoOf(Pawn p)
        {
            Ideo ideo = p?.Ideo;
            if (ideo == null || !ModsConfig.IdeologyActive || ideo.classicMode || (Find.IdeoManager != null && Find.IdeoManager.classicMode)) return null;
            return ideo;
        }

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
                    && !KeptClean(c, map) && (!roomCap || !RoomFull(c, map, marksInRoom));
                cells.Add(c);
                bool marked = usable && AlreadyMarked(c, map);
                states.Add(new RM_MarkCell(usable, marked));
                if (usable && !marked && ++bareSeen >= RM_GraffitiKernel.MaxCandidates) break;
            }
            return PickFrom(cells, states, map, out result);
        }

        /// <summary>Where a hand answers a mark in paint: as near as it can get on bare wall, in the mark's own sight; failing that, over the top of it.</summary>
        /// Live 2026-11-07: the fallback went over whatever stood there, and BW's answer to Mo erased Pell's work too, so Pell took a grudge
        /// against BW over a quarrel that wasn't his. Now the reply needs room clear of everyone but the pawn it answers.
        internal static bool TryFindReplyCell(Pawn pawn, IntVec3 near, out IntVec3 result, Pawn against = null)
        {
            Map map = pawn.Map;
            float need = GraffitiPool.WidthOf(RMGraffitiDefOf.RM_Graffiti_Mockery);
            IntVec3 fallback = IntVec3.Invalid, edge = IntVec3.Invalid;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(near, ReplyRadius, useCenter: true))
            {
                if (!c.InBounds(map) || !c.Standable(map) || !HasCardinalWall(c, map) || KeptClean(c, map) || !pawn.CanReserveAndReach(c, PathEndMode.OnCell, Danger.Some)) continue;
                if (need > System.Math.Min(WallRoom(c, map), BareRoom(c, map, against))) continue;
                bool marked = AlreadyMarked(c, map);
                if (!OnFace(c, map))
                {
                    if (!marked && !edge.IsValid) edge = c;     // a wall seen edge-on: only if no face is near (TryFindMeaningCell)
                    continue;
                }
                if (!marked)
                {
                    result = c;
                    return true;
                }
                if (!fallback.IsValid) fallback = c;     // over the top of the answered pawn's own mark
            }
            result = fallback.IsValid ? fallback : edge;
            return result.IsValid;
        }

        private const float ReplyRadius = 7f;

        /// <summary>Where a hand with something to say about someone says it: the nearest stretch wide enough for it to where that person
        /// sleeps, else where they stand, else where the painter stands. It may go over the painter's own old marks and, for a mockery, the
        /// target's (`over`): nobody else's. A room's share doesn't hold it back (a grudge doesn't wait for wall space); kitchens and hospitals
        /// still do.</summary>
        internal static bool TryFindMeaningCell(Pawn pawn, Pawn subject, float need, Pawn over, out IntVec3 result)
        {
            Map map = pawn.Map;
            var centres = new List<IntVec3>();
            if (subject != null && subject.Spawned && subject.Map == map)
            {
                Building_Bed bed = subject.ownership?.OwnedBed;
                if (bed != null && bed.Spawned && bed.Map == map) centres.Add(bed.Position);
                centres.Add(subject.Position);
            }
            centres.Add(pawn.Position);
            // A message is painted where it will be read: a wall's face, not its edge. Live, pass 10: Lark's mockery of Mo went on a wall
            // seen edge-on, a head-sized scrap on the wall top nobody could read at play zoom. An edge only when no face is near.
            for (int pass = 0; pass < 2; pass++)
            {
                foreach (IntVec3 centre in centres)
                {
                    foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, MeaningRadius, useCenter: true))
                    {
                        if (!c.InBounds(map) || !c.Standable(map) || !HasCardinalWall(c, map) || KeptClean(c, map)) continue;
                        if (pass == 0 && !OnFace(c, map)) continue;
                        if (need > System.Math.Min(WallRoom(c, map), BareRoom(c, map, pawn, over))) continue;
                        if (!pawn.CanReserveAndReach(c, PathEndMode.OnCell, Danger.None)) continue;
                        result = c;
                        return true;
                    }
                }
            }
            result = IntVec3.Invalid;
            return false;
        }

        /// <summary>Does a mark at this floor cell go on a wall's front face, the one the camera sees whole?</summary>
        internal static bool OnFace(IntVec3 c, Map map)
        {
            return RM_GraffitiKernel.FaceOfSide(Filth_Mark.ReadWallSide(c, map)) == RM_GraffitiKernel.FaceFront;
        }

        private const float MeaningRadius = 12f;

        /// <summary>Owner's pick, 2026-11-07: nobody paints a hospital or a kitchen on their own. A mark is filth, and filth there is infection and
        /// food poisoning. Nor, for ten days, a wall the player ordered scrubbed (MapComponent_GraffitiSocial.HeldClean). The player's own order
        /// may still paint there.</summary>
        internal static bool KeptClean(IntVec3 c, Map map)
        {
            if (MapComponent_GraffitiSocial.For(map)?.HeldClean(c) == true) return true;
            RoomRoleDef role = c.GetRoom(map)?.Role;
            return role != null && (role == RoomRoleDefOf.Hospital || role == KitchenRole);
        }

        private static RoomRoleDef kitchen;
        private static RoomRoleDef KitchenRole => kitchen ?? (kitchen = DefDatabase<RoomRoleDef>.GetNamedSilentFail("Kitchen"));

        /// <summary>How wide a mark centred on this floor cell's wall may be before its drawing overlaps a neighbour's on the same face
        /// (RM_GraffitiKernel.WallMarksOverlap's own rule, read from the other side). Unlimited with nothing near.</summary>
        /// `spare`, `spare2`: pawns whose own marks don't count (a reply may go over the work of the one it answers, and only theirs; a
        /// mockery over its painter's own old marks and its target's).
        public static float BareRoom(IntVec3 c, Map map, Pawn spare = null, Pawn spare2 = null)
        {
            int side = Filth_Mark.ReadWallSide(c, map);
            if (side == RM_GraffitiKernel.NoWall) return float.MaxValue;
            int face = RM_GraffitiKernel.FaceOfSide(side);
            RM_GraffitiKernel.AlongOf(face, out int ax, out int az);
            IntVec3 along = new IntVec3(ax, 0, az);
            float room = float.MaxValue;
            for (int k = -BareSearchCells; k <= BareSearchCells; k++)
            {
                IntVec3 floor = c + along * k;
                if (!floor.InBounds(map)) continue;
                foreach (Thing t in floor.GetThingList(map))
                {
                    if (!(t is Filth_Mark m) || m.wallSide != side || (spare != null && m.maker == spare) || (spare2 != null && m.maker == spare2)) continue;
                    if (k == 0) return 0f;
                    room = System.Math.Min(room, 2f * (System.Math.Abs(k) - GraffitiPool.WidthOf(m.def) / 2f) + 0.3f);
                }
            }
            return room;
        }

        private const int BareSearchCells = 6;

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
            // Outside, "the room" is the whole map and its share never fills: live 2026-11-07, three idle days painted the colony's outer west
            // wall solid from end to end. Out there a stretch of wall holds its share instead.
            if (room.PsychologicallyOutdoors || room.CellCount > RM_GraffitiKernel.OpenGroundCells)
            {
                return RM_GraffitiKernel.StretchHoldsEnough(MarksNear(c, map, RM_GraffitiKernel.StretchRadius));
            }
            counts.TryGetValue(room, out int n);
            return RM_GraffitiKernel.RoomHoldsEnough(n, room.CellCount);
        }

        private static int MarksNear(IntVec3 c, Map map, float radius)
        {
            MapComponent_GraffitiSocial comp = MapComponent_GraffitiSocial.For(map);
            if (comp == null) return 0;
            int n = 0;
            foreach (Filth_Mark m in comp.marks)
            {
                if (m.Spawned && m.Position.InHorDistOf(c, radius)) n++;
            }
            return n;
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
            // Nobody stands in a doorway to paint the stub of wall over the lintel, or inside a machine.
            if (c.InBounds(map) && c.GetEdifice(map) != null) return false;
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
