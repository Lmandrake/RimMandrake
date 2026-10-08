using System;
using System.Collections.Generic;

namespace RimMandrake.Stillsand
{
    // Verse-free decisions of the dune gale (RM_DuneGale.cs): the 8-way wind step and its bearing name, the carry walk, the
    // exit/return edges of a pawn carried off the map, the return outcome, the carried-pawn book scans and the emergence
    // row filter. The mod calls these with the same expressions; the offline fuzz drives them against a grid model.

    public enum RM_Edge { North, East, South, West }

    public enum RM_ReturnOutcome { LostMissing, LostDead, SpawnAlive, SpawnThenKill }

    public struct RM_CarryResult
    {
        public bool offMap;
        public int x, z;
        public int moved;
    }

    public static class RM_GaleKernel
    {
        // north, northeast, east, southeast, south, southwest, west, northwest (x east, z north)
        public static readonly int[] DirX = { 0, 1, 1, 1, 0, -1, -1, -1 };
        public static readonly int[] DirZ = { 1, 1, 0, -1, -1, -1, 0, 1 };
        public static readonly string[] DirNames = { "north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest" };

        public const int CarriedScanInterval = 2000;

        /// <summary>Bearing word for one of the 8 unit steps; "downwind" for anything else.</summary>
        public static string BearingName(int dx, int dz)
        {
            for (int i = 0; i < 8; i++)
            {
                if (DirX[i] == dx && DirZ[i] == dz)
                {
                    return DirNames[i];
                }
            }
            return "downwind";
        }

        /// <summary>The 8-way step index for a shadow vector (x, y): the way the wind blows TOWARD, along the shadows.</summary>
        public static int WindIndexFromShadow(float x, float y)
        {
            float deg = (float)Math.Atan2(x, y) * 57.29578f;
            if (deg < 0f)
            {
                deg += 360f;
            }
            return (int)Math.Round(deg / 45f) & 7;
        }

        public static bool CarryEligible(float bodySize, float carryMaxBodySize, bool roofed, bool onCrest, bool dead)
        {
            return !(bodySize > carryMaxBodySize || roofed || !onCrest || dead);
        }

        /// <summary>Walk up to `steps` cells downwind: stops at the first blocked cell, or flags the walk off the map edge.
        /// onLeave is called with the cell being left on every step taken.</summary>
        public static RM_CarryResult CarryWalk(int x, int z, int wx, int wz, int steps, Func<int, int, bool> inBounds,
            Func<int, int, bool> walkable, Action<int, int> onLeave)
        {
            var r = new RM_CarryResult { x = x, z = z };
            for (int s = 0; s < steps; s++)
            {
                int nx = r.x + wx, nz = r.z + wz;
                if (!inBounds(nx, nz))
                {
                    r.offMap = true;
                    break;
                }
                if (!walkable(nx, nz))
                {
                    break;
                }
                if (onLeave != null)
                {
                    onLeave(r.x, r.z);
                }
                r.x = nx;
                r.z = nz;
                r.moved++;
            }
            return r;
        }

        /// <summary>The map edge a pawn exits through when carried off by this wind (a diagonal exits east/west).</summary>
        public static RM_Edge ExitEdge(int wx, int wz)
        {
            int sx = Math.Sign(wx);
            int sz = wx == 0 ? Math.Sign(wz) : 0;
            if (sz > 0) return RM_Edge.North;
            if (sx > 0) return RM_Edge.East;
            if (sz < 0) return RM_Edge.South;
            if (sx < 0) return RM_Edge.West;
            return RM_Edge.North;
        }

        /// <summary>The edge it comes back in from: the way it left. A zero wind is treated as south.</summary>
        public static RM_Edge ReturnEdge(int wx, int wz)
        {
            if (wx == 0 && wz == 0)
            {
                wz = -1;
            }
            return Math.Abs(wx) >= Math.Abs(wz)
                ? (wx > 0 ? RM_Edge.East : RM_Edge.West)
                : (wz > 0 ? RM_Edge.North : RM_Edge.South);
        }

        /// <summary>Back in from the edge: up to 4 steps upwind while the cell is in bounds and standable.</summary>
        public static void WalkIn(ref int x, ref int z, int wx, int wz, Func<int, int, bool> inBounds, Func<int, int, bool> standable)
        {
            if (wx == 0 && wz == 0)
            {
                wz = -1;
            }
            for (int k = 0; k < 4; k++)
            {
                int nx = x - wx, nz = z - wz;
                if (!inBounds(nx, nz) || !standable(nx, nz))
                {
                    break;
                }
                x = nx;
                z = nz;
            }
        }

        public static RM_ReturnOutcome Decide(bool pawnMissing, bool mapMissing, bool dead, bool aliveRoll)
        {
            if (pawnMissing || mapMissing)
            {
                return RM_ReturnOutcome.LostMissing;
            }
            if (dead)
            {
                return RM_ReturnOutcome.LostDead;
            }
            return aliveRoll ? RM_ReturnOutcome.SpawnAlive : RM_ReturnOutcome.SpawnThenKill;
        }

        /// <summary>The carried-pawn book is only scanned on every 2000th tick, and only when it holds anything.</summary>
        public static bool ShouldScanCarried(int count, int now)
        {
            return !(count == 0 || now % CarriedScanInterval != 0);
        }

        public static bool IsDue(int returnTick, int now)
        {
            return returnTick <= now;
        }

        /// <summary>Remove and return (last to first) every record the predicate selects.</summary>
        public static List<T> TakeWhere<T>(IList<T> book, Func<T, bool> pick)
        {
            var taken = new List<T>();
            for (int i = book.Count - 1; i >= 0; i--)
            {
                if (pick(book[i]))
                {
                    taken.Add(book[i]);
                    book.RemoveAt(i);
                }
            }
            return taken;
        }

        /// <summary>One emergence row is a candidate: weight, its toggle, and the world it needs (a placeable skeleton, a rock face).</summary>
        public static bool EmergenceOk(float weight, bool allowed, bool needsSkeleton, bool skeletonAvailable, bool needsCave, bool caveFound)
        {
            return weight > 0f && allowed && (!needsSkeleton || skeletonAvailable) && (!needsCave || caveFound);
        }
    }
}
