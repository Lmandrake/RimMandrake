// ANT_HIVE_REAL_GEOMETRY_1. Verse-free planner of a kurreth hive: rooms, tunnels, the walls that bound them and the one
// mouth that lets anything in. RM_GenStep_AntHiveDungeon snapshots the map into a HiveGrid, plans here, then builds what
// comes back. SelfTest/FeverWoodFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.FeverWood
{
    /// <summary>What the planner may know about a map. Cells are x + z * Width.</summary>
    public sealed class HiveGrid
    {
        public readonly int Width, Height;
        public readonly bool[] Passable;  // walkable today
        public readonly bool[] Forbidden; // no part of a hive may stand here (open water, a building, a wreck)
        public readonly bool[] Water;     // registered pool cells; the clearance radius is measured from these

        public HiveGrid(int width, int height)
        {
            Width = width;
            Height = height;
            Passable = new bool[width * height];
            Forbidden = new bool[width * height];
            Water = new bool[width * height];
        }

        public bool InBounds(int x, int z) { return x >= 0 && z >= 0 && x < Width && z < Height; }
    }

    public struct HiveRoom
    {
        public int X, Z;
        public float Radius;
    }

    public struct HivePlanParams
    {
        public int TargetRooms, EdgeMargin, Attempts, CorridorRadius;
        public float RadiusMin, RadiusMax, HopMin, HopMax, WaterClearance;
    }

    /// <summary>The plan. Rooms[0] is the entrance room, the last room the queen's. Floor includes Mouth; a Mouth cell
    /// is open to the sky and unwalled, the way in. Wall lists only cells that need a wall built (rock already bounds
    /// the rest).</summary>
    public sealed class HiveLayout
    {
        public readonly List<HiveRoom> Rooms = new List<HiveRoom>();
        public readonly HashSet<int> Floor = new HashSet<int>();
        public readonly HashSet<int> Mouth = new HashSet<int>();
        public readonly HashSet<int> Wall = new HashSet<int>();
    }

    public static class RM_HiveLayoutKernel
    {
        private static readonly int[,] Dirs = { { 1, 0 }, { 1, 1 }, { 0, 1 }, { -1, 1 }, { -1, 0 }, { -1, -1 }, { 0, -1 }, { 1, -1 } };
        private static readonly HashSet<int> NoCells = new HashSet<int>();

        /// <summary>The best hive this map allows: the first plan that reaches TargetRooms, else the longest of at
        /// least two rooms found in Attempts tries, else null (the caller skips the hive). randFloat(a,b) is uniform on
        /// [a,b]; randInt(n) is uniform on [0,n).</summary>
        public static HiveLayout TryPlan(HiveGrid g, HivePlanParams p, Func<float, float, float> randFloat, Func<int, int> randInt)
        {
            bool[] blocked = BlockedByClearance(g, p.WaterClearance);
            bool[] outdoors = Reachable(g, null);
            HiveLayout best = null;
            for (int attempt = 0; attempt < p.Attempts; attempt++)
            {
                int x = p.EdgeMargin + randInt(Math.Max(1, g.Width - 2 * p.EdgeMargin));
                int z = p.EdgeMargin + randInt(Math.Max(1, g.Height - 2 * p.EdgeMargin));
                if (!g.InBounds(x, z) || !g.Passable[x + z * g.Width] || blocked[x + z * g.Width])
                {
                    continue;
                }

                HiveLayout plan = PlanFrom(g, p, blocked, outdoors, x, z, randFloat, randInt);
                if (plan == null || (best != null && plan.Rooms.Count <= best.Rooms.Count) || !Validate(g, plan, outdoors))
                {
                    continue;
                }

                best = plan;
                if (best.Rooms.Count >= p.TargetRooms)
                {
                    break;
                }
            }

            return best;
        }

        // Every cell a hive may not touch: Forbidden, and everything within the clearance of a registered pool.
        internal static bool[] BlockedByClearance(HiveGrid g, float clearance)
        {
            bool[] blocked = (bool[])g.Forbidden.Clone();
            int r = (int)Math.Ceiling(clearance);
            float sq = clearance * clearance;
            for (int z = 0; z < g.Height; z++)
            {
                for (int x = 0; x < g.Width; x++)
                {
                    if (!g.Water[x + z * g.Width])
                    {
                        continue;
                    }

                    blocked[x + z * g.Width] = true;
                    for (int dz = -r; dz <= r; dz++)
                    {
                        for (int dx = -r; dx <= r; dx++)
                        {
                            if (dx * dx + dz * dz <= sq && g.InBounds(x + dx, z + dz))
                            {
                                blocked[x + dx + (z + dz) * g.Width] = true;
                            }
                        }
                    }
                }
            }

            return blocked;
        }

        private static HiveLayout PlanFrom(HiveGrid g, HivePlanParams p, bool[] blocked, bool[] outdoors, int x, int z,
            Func<float, float, float> randFloat, Func<int, int> randInt)
        {
            HiveLayout plan = new HiveLayout();
            HiveRoom first = new HiveRoom { X = x, Z = z, Radius = randFloat(p.RadiusMin, p.RadiusMax) };
            HashSet<int> firstCells = Disc(g, first.X, first.Z, first.Radius);
            if (!FootprintFree(g, p, blocked, firstCells))
            {
                return null;
            }

            plan.Rooms.Add(first);
            plan.Floor.UnionWith(firstCells);

            while (plan.Rooms.Count < p.TargetRooms && TryExtend(g, p, blocked, plan, randFloat, randInt))
            {
            }

            return plan.Rooms.Count >= 2 && TryCutMouth(g, p, blocked, outdoors, plan) ? plan : null;
        }

        // One more room off the end of the chain. A hop is taken only if the new room keeps a wall's width from every
        // other room and its tunnel touches nothing but the two rooms it joins.
        private static bool TryExtend(HiveGrid g, HivePlanParams p, bool[] blocked, HiveLayout plan,
            Func<float, float, float> randFloat, Func<int, int> randInt)
        {
            HiveRoom prev = plan.Rooms[plan.Rooms.Count - 1];
            for (int attempt = 0; attempt < p.Attempts; attempt++)
            {
                int d = randInt(8);
                float hop = randFloat(p.HopMin, p.HopMax);
                HiveRoom next = new HiveRoom
                {
                    X = prev.X + (int)Math.Round(Dirs[d, 0] * hop),
                    Z = prev.Z + (int)Math.Round(Dirs[d, 1] * hop),
                    Radius = randFloat(p.RadiusMin, p.RadiusMax),
                };
                if (next.X < p.EdgeMargin || next.Z < p.EdgeMargin || next.X >= g.Width - p.EdgeMargin || next.Z >= g.Height - p.EdgeMargin)
                {
                    continue;
                }

                if (RoomCrowded(plan, next))
                {
                    continue;
                }

                HashSet<int> roomCells = Disc(g, next.X, next.Z, next.Radius);
                HashSet<int> tunnel = Tunnel(g, prev.X, prev.Z, next.X, next.Z, p.CorridorRadius);
                HashSet<int> prevCells = Disc(g, prev.X, prev.Z, prev.Radius);
                tunnel.ExceptWith(roomCells);
                tunnel.ExceptWith(prevCells);
                if (!FootprintFree(g, p, blocked, roomCells) || !FootprintFree(g, p, blocked, tunnel)
                    || TouchesFloor(g, plan, tunnel, prevCells) || TouchesFloor(g, plan, roomCells, NoCells))
                {
                    continue;
                }

                plan.Rooms.Add(next);
                plan.Floor.UnionWith(roomCells);
                plan.Floor.UnionWith(tunnel);
                return true;
            }

            return false;
        }

        private static bool RoomCrowded(HiveLayout plan, HiveRoom next)
        {
            for (int i = 0; i < plan.Rooms.Count; i++)
            {
                HiveRoom r = plan.Rooms[i];
                float min = r.Radius + next.Radius + 2f; // the two rims and the wall between them
                float dx = r.X - next.X, dz = r.Z - next.Z;
                if (dx * dx + dz * dz < min * min)
                {
                    return true;
                }
            }

            return false;
        }

        // The way in: a short stub out of the entrance room, turned as far from room 1 as the ground allows, whose tip
        // stands open on ground that really does reach the map edge.
        private static bool TryCutMouth(HiveGrid g, HivePlanParams p, bool[] blocked, bool[] outdoors, HiveLayout plan)
        {
            HiveRoom door = plan.Rooms[0];
            HiveRoom second = plan.Rooms[1];
            List<int> order = new List<int> { 0, 1, 2, 3, 4, 5, 6, 7 };
            order.Sort((a, b) => Facing(a, door, second).CompareTo(Facing(b, door, second)));
            HashSet<int> roomCells = Disc(g, door.X, door.Z, door.Radius);
            foreach (int d in order)
            {
                double len = Math.Sqrt(Dirs[d, 0] * Dirs[d, 0] + Dirs[d, 1] * Dirs[d, 1]);
                float reach = door.Radius + p.CorridorRadius + 2f;
                int tipX = door.X + (int)Math.Round(Dirs[d, 0] / len * reach);
                int tipZ = door.Z + (int)Math.Round(Dirs[d, 1] / len * reach);
                float beyond = reach + p.CorridorRadius + 1f;
                int outX = door.X + (int)Math.Round(Dirs[d, 0] / len * beyond);
                int outZ = door.Z + (int)Math.Round(Dirs[d, 1] / len * beyond);
                if (!g.InBounds(outX, outZ) || !outdoors[outX + outZ * g.Width] || plan.Floor.Contains(outX + outZ * g.Width))
                {
                    continue;
                }

                HashSet<int> stub = Tunnel(g, door.X, door.Z, tipX, tipZ, p.CorridorRadius);
                stub.ExceptWith(roomCells);
                if (!FootprintFree(g, p, blocked, stub) || TouchesFloor(g, plan, stub, roomCells))
                {
                    continue;
                }

                plan.Floor.UnionWith(stub);
                plan.Mouth.UnionWith(Disc(g, tipX, tipZ, p.CorridorRadius));
                plan.Floor.UnionWith(plan.Mouth);
                BuildWalls(g, plan);
                return true;
            }

            return false;
        }

        private static float Facing(int d, HiveRoom door, HiveRoom second)
        {
            return Dirs[d, 0] * (second.X - door.X) + Dirs[d, 1] * (second.Z - door.Z);
        }

        // Every walkable cell touching the hive, diagonals included, unless it only touches the open mouth.
        private static void BuildWalls(HiveGrid g, HiveLayout plan)
        {
            foreach (int cell in plan.Floor)
            {
                if (plan.Mouth.Contains(cell))
                {
                    continue;
                }

                int x = cell % g.Width, z = cell / g.Width;
                for (int d = 0; d < 8; d++)
                {
                    int nx = x + Dirs[d, 0], nz = z + Dirs[d, 1];
                    if (!g.InBounds(nx, nz))
                    {
                        continue;
                    }

                    int n = nx + nz * g.Width;
                    if (!plan.Floor.Contains(n) && g.Passable[n])
                    {
                        plan.Wall.Add(n);
                    }
                }
            }
        }

        /// <summary>True when the built hive is whole: every floor cell reaches the map edge, no outdoor cell was shut
        /// off, and with the mouth stopped nothing inside reaches outdoors (so the walls really enclose it).</summary>
        public static bool Validate(HiveGrid g, HiveLayout plan, bool[] outdoors)
        {
            bool[] open = Reachable(g, plan);
            foreach (int cell in plan.Floor)
            {
                if (!open[cell])
                {
                    return false;
                }
            }

            for (int c = 0; c < outdoors.Length; c++)
            {
                if (outdoors[c] && !open[c] && !plan.Wall.Contains(c))
                {
                    return false;
                }
            }

            bool[] sealedOff = Reachable(g, plan, plan.Mouth);
            foreach (int cell in plan.Floor)
            {
                if (!plan.Mouth.Contains(cell) && sealedOff[cell])
                {
                    return false;
                }
            }

            return true;
        }

        /// <summary>Cells walkable from the map edge, with an optional plan built and optional cells stopped.</summary>
        public static bool[] Reachable(HiveGrid g, HiveLayout plan, HashSet<int> stopped = null)
        {
            bool[] seen = new bool[g.Width * g.Height];
            Stack<int> open = new Stack<int>();
            Action<int> seed = c =>
            {
                if (!seen[c] && Walkable(g, plan, stopped, c))
                {
                    seen[c] = true;
                    open.Push(c);
                }
            };
            for (int x = 0; x < g.Width; x++)
            {
                seed(x);
                seed(x + (g.Height - 1) * g.Width);
            }

            for (int z = 0; z < g.Height; z++)
            {
                seed(z * g.Width);
                seed(g.Width - 1 + z * g.Width);
            }

            while (open.Count > 0)
            {
                int c = open.Pop();
                int x = c % g.Width, z = c / g.Width;
                for (int d = 0; d < 8; d++)
                {
                    int dx = Dirs[d, 0], dz = Dirs[d, 1];
                    int nx = x + dx, nz = z + dz;
                    if (!g.InBounds(nx, nz))
                    {
                        continue;
                    }

                    // The game's own rule: a diagonal step needs both orthogonal neighbours clear.
                    if (dx != 0 && dz != 0
                        && (!Walkable(g, plan, stopped, nx + z * g.Width) || !Walkable(g, plan, stopped, x + nz * g.Width)))
                    {
                        continue;
                    }

                    seed(nx + nz * g.Width);
                }
            }

            return seen;
        }

        private static bool Walkable(HiveGrid g, HiveLayout plan, HashSet<int> stopped, int c)
        {
            if (stopped != null && stopped.Contains(c))
            {
                return false;
            }

            if (plan == null)
            {
                return g.Passable[c];
            }

            return plan.Floor.Contains(c) || (g.Passable[c] && !plan.Wall.Contains(c));
        }

        // Neither the cells nor the ring a wall would stand on may leave the margin or touch anything blocked.
        private static bool FootprintFree(HiveGrid g, HivePlanParams p, bool[] blocked, HashSet<int> cells)
        {
            int min = Math.Max(1, p.EdgeMargin / 2);
            foreach (int cell in cells)
            {
                int x = cell % g.Width, z = cell / g.Width;
                if (x < min || z < min || x >= g.Width - min || z >= g.Height - min)
                {
                    return false;
                }

                for (int dz = -1; dz <= 1; dz++)
                {
                    for (int dx = -1; dx <= 1; dx++)
                    {
                        if (blocked[x + dx + (z + dz) * g.Width])
                        {
                            return false;
                        }
                    }
                }
            }

            return true;
        }

        // Does any new cell (or its ring) meet floor already planned, other than the room it is allowed to open from?
        private static bool TouchesFloor(HiveGrid g, HiveLayout plan, HashSet<int> cells, HashSet<int> allowed)
        {
            foreach (int cell in cells)
            {
                int x = cell % g.Width, z = cell / g.Width;
                for (int dz = -1; dz <= 1; dz++)
                {
                    for (int dx = -1; dx <= 1; dx++)
                    {
                        if (!g.InBounds(x + dx, z + dz))
                        {
                            continue;
                        }

                        int n = x + dx + (z + dz) * g.Width;
                        if (plan.Floor.Contains(n) && !allowed.Contains(n))
                        {
                            return true;
                        }
                    }
                }
            }

            return false;
        }

        internal static HashSet<int> Disc(HiveGrid g, int cx, int cz, float radius)
        {
            HashSet<int> cells = new HashSet<int>();
            int r = (int)Math.Ceiling(radius);
            float sq = radius * radius;
            for (int dz = -r; dz <= r; dz++)
            {
                for (int dx = -r; dx <= r; dx++)
                {
                    if (dx * dx + dz * dz <= sq && g.InBounds(cx + dx, cz + dz))
                    {
                        cells.Add(cx + dx + (cz + dz) * g.Width);
                    }
                }
            }

            return cells;
        }

        internal static HashSet<int> Tunnel(HiveGrid g, int ax, int az, int bx, int bz, int radius)
        {
            HashSet<int> cells = new HashSet<int>();
            double dist = Math.Sqrt((bx - ax) * (bx - ax) + (bz - az) * (bz - az));
            int steps = (int)Math.Ceiling(dist);
            for (int i = 0; i <= steps; i++)
            {
                double t = steps == 0 ? 0 : (double)i / steps;
                cells.UnionWith(Disc(g, (int)Math.Round(ax + (bx - ax) * t), (int)Math.Round(az + (bz - az) * t), radius));
            }

            return cells;
        }
    }
}
