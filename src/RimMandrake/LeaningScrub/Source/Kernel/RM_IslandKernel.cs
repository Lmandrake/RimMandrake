// VENOMVINE_BUILD_SCRUB_GROWS_TEETH (design/RimMandrake/venomvine_design_2026-10-16.md §2, §3, §5, §10 Q1/Q3/Q4).
// Verse-free kernel of the venomvine islands map step and the slow downwind creep: how many islands and how big, how one
// grows on a grid, whether it cuts the map apart, where its rooms go, and the creep's runner roll, neighbour pick and cap.
// SelfTest/LeaningScrubIslandCheck.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.LeaningScrub
{
    public static class RM_IslandKernel
    {
        public const int TicksPerDay = 60000;

        // ── plan ──

        /// <summary>Cells the islands should cover: share of open ground, rounded.</summary>
        public static int TargetCells(int openCells, float share)
        {
            if (openCells <= 0 || share <= 0f) return 0;
            return (int)Math.Round(openCells * (double)Math.Min(share, 0.9f));
        }

        /// <summary>The island count: the rolled count (8 to 14 by default), raised until no island must exceed maxBody to
        /// reach the target ("count PROVISIONAL, scaled up to reach the share"), and lowered so none falls under minBody.</summary>
        public static int IslandCount(int targetCells, int rolled, int minBody, int maxBody)
        {
            if (targetCells <= 0) return 0;
            minBody = Math.Max(1, minBody);
            maxBody = Math.Max(minBody, maxBody);
            int count = Math.Max(1, rolled);
            int needed = (targetCells + maxBody - 1) / maxBody;
            if (count < needed) count = needed;
            int most = Math.Max(1, targetCells / minBody);
            if (count > most) count = most;
            return count;
        }

        /// <summary>Per-island sizes summing to targetCells (as near as the bounds allow), each in [minBody, maxBody], varied
        /// by rand around the mean.</summary>
        public static void SizeIslands(int targetCells, int count, int minBody, int maxBody, Func<double> rand, List<int> sizes)
        {
            sizes.Clear();
            if (count <= 0 || targetCells <= 0) return;
            minBody = Math.Max(1, minBody);
            maxBody = Math.Max(minBody, maxBody);
            int left = targetCells;
            for (int i = 0; i < count; i++)
            {
                int islandsLeft = count - i;
                double mean = left / (double)islandsLeft;
                double s = mean * (0.6 + 0.8 * rand());
                int size = (int)Math.Round(s);
                if (i == count - 1) size = left;
                // keep the rest reachable: what is left after this one must fit the remaining islands' bounds
                int rest = islandsLeft - 1;
                size = Math.Min(size, left - minBody * rest);
                size = Math.Max(size, left - maxBody * rest);
                size = Math.Max(minBody, Math.Min(maxBody, size));
                sizes.Add(size);
                left -= size;
                if (left <= 0) break;
            }
        }

        // ── grow one island ──

        /// <summary>True when no cell of ANOTHER island lies within gap (Chebyshev) of (x, z).</summary>
        public static bool GapOk(int w, int h, int[] owner, int id, int x, int z, int gap)
        {
            for (int dz = -gap; dz <= gap; dz++)
            {
                int zz = z + dz;
                if (zz < 0 || zz >= h) continue;
                for (int dx = -gap; dx <= gap; dx++)
                {
                    int xx = x + dx;
                    if (xx < 0 || xx >= w) continue;
                    int o = owner[zz * w + xx];
                    if (o >= 0 && o != id) return false;
                }
            }
            return true;
        }

        /// <summary>Grows island <paramref name="id"/> from a seed by a randomised frontier, preferring cells inside an
        /// ellipse stretched along the wind (islands stretch sunward, like everything in the Scrub). Writes owner[] and
        /// outCells (indices z*w+x). Returns the cell count (0 if the seed is not allowed).</summary>
        public static int Grow(int w, int h, bool[] allowed, int[] owner, int id, int seedX, int seedZ, int size, int gap,
            float windX, float windZ, float stretch, Func<double> rand, List<int> outCells)
        {
            outCells.Clear();
            if (size <= 0 || seedX < 0 || seedZ < 0 || seedX >= w || seedZ >= h) return 0;
            int seed = seedZ * w + seedX;
            if (!allowed[seed] || owner[seed] >= 0 || !GapOk(w, h, owner, id, seedX, seedZ, gap)) return 0;
            double len = Math.Sqrt(windX * windX + windZ * windZ);
            double ux = len > 1e-6 ? windX / len : 1.0, uz = len > 1e-6 ? windZ / len : 0.0;
            stretch = Math.Max(1f, stretch);
            double r = Math.Sqrt(size / Math.PI);
            double rAlong = r * stretch, rAcross = r / stretch;
            var frontier = new List<int>();
            var inFrontier = new HashSet<int>();
            owner[seed] = id;
            outCells.Add(seed);
            void Push(int c)
            {
                int cx = c % w, cz = c / w;
                for (int k = 0; k < 4; k++)
                {
                    int nx = cx + (k == 0 ? 1 : k == 1 ? -1 : 0), nz = cz + (k == 2 ? 1 : k == 3 ? -1 : 0);
                    if (nx < 0 || nz < 0 || nx >= w || nz >= h) continue;
                    int n = nz * w + nx;
                    if (owner[n] >= 0 || !allowed[n] || inFrontier.Contains(n)) continue;
                    frontier.Add(n);
                    inFrontier.Add(n);
                }
            }
            Push(seed);
            while (outCells.Count < size && frontier.Count > 0)
            {
                int bestI = -1;
                double best = double.NegativeInfinity;
                int samples = Math.Min(6, frontier.Count);
                for (int s = 0; s < samples; s++)
                {
                    int i = (int)(rand() * frontier.Count);
                    if (i >= frontier.Count) i = frontier.Count - 1;
                    int c = frontier[i];
                    double dx = c % w - seedX, dz = c / w - seedZ;
                    double along = dx * ux + dz * uz, across = -dx * uz + dz * ux;
                    double score = rand() * 0.6 - (along * along) / (rAlong * rAlong) - (across * across) / (rAcross * rAcross);
                    if (score > best) { best = score; bestI = i; }
                }
                int pick = frontier[bestI];
                frontier[bestI] = frontier[frontier.Count - 1];
                frontier.RemoveAt(frontier.Count - 1);
                inFrontier.Remove(pick);
                if (owner[pick] >= 0 || !GapOk(w, h, owner, id, pick % w, pick / w, gap)) continue;
                owner[pick] = id;
                outCells.Add(pick);
                Push(pick);
            }
            return outCells.Count;
        }

        /// <summary>Undo an island: its cells go back to owner -1.</summary>
        public static void Ungrow(int[] owner, List<int> cells)
        {
            for (int i = 0; i < cells.Count; i++) owner[cells[i]] = -1;
        }

        // ── traversability ──

        /// <summary>Cells reachable (4-neighbour) from the start over passable cells no island owns.</summary>
        public static int Reach(int w, int h, bool[] passable, int[] owner, int startX, int startZ)
        {
            if (startX < 0 || startZ < 0 || startX >= w || startZ >= h) return 0;
            int s = startZ * w + startX;
            if (!passable[s] || owner[s] >= 0) return 0;
            var seen = new bool[w * h];
            var stack = new Stack<int>();
            stack.Push(s);
            seen[s] = true;
            int count = 0;
            while (stack.Count > 0)
            {
                int c = stack.Pop();
                count++;
                int cx = c % w, cz = c / w;
                for (int k = 0; k < 4; k++)
                {
                    int nx = cx + (k == 0 ? 1 : k == 1 ? -1 : 0), nz = cz + (k == 2 ? 1 : k == 3 ? -1 : 0);
                    if (nx < 0 || nz < 0 || nx >= w || nz >= h) continue;
                    int n = nz * w + nx;
                    if (seen[n] || !passable[n] || owner[n] >= 0) continue;
                    seen[n] = true;
                    stack.Push(n);
                }
            }
            return count;
        }

        /// <summary>An island keeps the map traversable when the open ground reachable from the start shrank by no more than
        /// the island's own passable cells plus a slack (a sliver of cut-off ground at a cliff is tolerated; a sealed valley
        /// is not).</summary>
        public static bool KeepsTraversable(int reachBefore, int reachAfter, int islandPassableCells, int slack)
        {
            return reachBefore - reachAfter <= islandPassableCells + Math.Max(0, slack);
        }

        // ── rooms ──

        public const int RoleEdge = 0, RoleInterior = 1, RoleDownwind = 2, RoleHeart = 3;

        /// <summary>One to three rooms per island, more in bigger islands.</summary>
        public static int RoomCount(int islandCells, double r)
        {
            if (islandCells < 12) return 0;
            int most = islandCells >= 150 ? 3 : islandCells >= 60 ? 2 : 1;
            return 1 + (int)Math.Floor(r * most) % most;
        }

        /// <summary>Picks a row index from cumulative weights (r in [0,1)). -1 when the table is empty.</summary>
        public static int PickWeighted(float[] weights, double r)
        {
            double total = 0;
            for (int i = 0; i < weights.Length; i++) total += Math.Max(0f, weights[i]);
            if (total <= 0) return -1;
            double at = r * total;
            for (int i = 0; i < weights.Length; i++)
            {
                at -= Math.Max(0f, weights[i]);
                if (at < 0) return i;
            }
            return weights.Length - 1;
        }

        /// <summary>Does cell c of the island satisfy a room role? Edge: a neighbour outside the island. Interior: all
        /// eight neighbours inside. Downwind: an edge cell whose projection on the wind is in the island's top quarter.</summary>
        public static bool RoleFits(int role, int w, int h, int[] owner, int id, int c, float windX, float windZ, double alongMin, double alongMax)
        {
            int cx = c % w, cz = c / w;
            int inside = 0, total = 0;
            for (int dz = -1; dz <= 1; dz++)
                for (int dx = -1; dx <= 1; dx++)
                {
                    if (dx == 0 && dz == 0) continue;
                    total++;
                    int nx = cx + dx, nz = cz + dz;
                    if (nx >= 0 && nz >= 0 && nx < w && nz < h && owner[nz * w + nx] == id) inside++;
                }
            bool edge = inside < total;
            switch (role)
            {
                case RoleInterior: return !edge;
                case RoleDownwind:
                    {
                        double along = cx * windX + cz * windZ;
                        return edge && along >= alongMin + 0.75 * (alongMax - alongMin);
                    }
                case RoleHeart: return !edge;
                default: return edge;
            }
        }

        /// <summary>The island cell farthest from its edge (the heart, for the Crown): max of the min Chebyshev distance to a
        /// non-island cell, searched to a small radius. -1 for an empty island.</summary>
        public static int Heart(int w, int h, int[] owner, int id, List<int> cells)
        {
            int best = -1, bestD = -1;
            for (int i = 0; i < cells.Count; i++)
            {
                int c = cells[i], cx = c % w, cz = c / w;
                int d = 0;
                for (int rr = 1; rr <= 8; rr++)
                {
                    bool clear = true;
                    for (int dz = -rr; dz <= rr && clear; dz++)
                        for (int dx = -rr; dx <= rr; dx++)
                        {
                            if (Math.Abs(dx) != rr && Math.Abs(dz) != rr) continue;
                            int nx = cx + dx, nz = cz + dz;
                            if (nx < 0 || nz < 0 || nx >= w || nz >= h || owner[nz * w + nx] != id) { clear = false; break; }
                        }
                    if (!clear) break;
                    d = rr;
                }
                if (d > bestD) { bestD = d; best = c; }
            }
            return best;
        }

        // ── creep ──

        /// <summary>Chance one grown stand puts a runner during one sweep, so the mean wait is daysBetween days.</summary>
        public static double RunnerChance(int sweepTicks, float daysBetween)
        {
            if (sweepTicks <= 0) return 0;
            double ticks = Math.Max(0.1, daysBetween) * TicksPerDay;
            return Math.Min(1.0, sweepTicks / ticks);
        }

        /// <summary>How many more venomvine cells the map cap allows (0 at or over the cap).</summary>
        public static int CapRoom(int vineCells, int openCells, float cap)
        {
            if (openCells <= 0 || cap <= 0f) return 0;
            int max = (int)Math.Floor(openCells * (double)Math.Min(cap, 1f) + 1e-3);
            return Math.Max(0, max - vineCells);
        }

        /// <summary>Picks one of n candidate neighbour offsets (free[i] says it can take a runner). With probability
        /// downwindShare the pick is among the free cells pointing downwind (positive dot with the wind), best-aligned
        /// first with ties broken by r2; otherwise (or if none points downwind, or there is no wind) any free cell by r2.
        /// -1 when none is free.</summary>
        public static int PickNeighbour(int[] dx, int[] dz, bool[] free, int n, float windX, float windZ, float downwindShare,
            double r1, double r2)
        {
            int freeCount = 0;
            for (int i = 0; i < n; i++) if (free[i]) freeCount++;
            if (freeCount == 0) return -1;
            bool hasWind = windX * windX + windZ * windZ > 1e-6f;
            if (hasWind && r1 < downwindShare)
            {
                int down = 0;
                for (int i = 0; i < n; i++) if (free[i] && dx[i] * windX + dz[i] * windZ > 1e-4f) down++;
                if (down > 0)
                {
                    int k = Math.Min(down - 1, (int)(r2 * down));
                    for (int i = 0; i < n; i++)
                    {
                        if (!free[i] || dx[i] * windX + dz[i] * windZ <= 1e-4f) continue;
                        if (k-- == 0) return i;
                    }
                }
            }
            int j = Math.Min(freeCount - 1, (int)(r2 * freeCount));
            for (int i = 0; i < n; i++)
            {
                if (!free[i]) continue;
                if (j-- == 0) return i;
            }
            return -1;
        }
    }
}
