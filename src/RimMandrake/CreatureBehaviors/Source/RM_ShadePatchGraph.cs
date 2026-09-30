using System;
using System.Collections.Generic;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // SOLAR_HEAT_EXPOSURE_1 §5: the shade-patch graph and dash-range math.
    //
    // This file uses System only, like RM_SunHeatMath, so that the offline
    // selftest (Source/SelfTest) can compile this exact file. It covers
    // patch labelling, the rim, the distance-to-shade field, the edges
    // between patches, and the dash-range arithmetic.
    //
    // Grids are row-major (index = z * width + x), the same layout as
    // CellIndices. Distances are in cost units: 10 for a cardinal step and
    // 14 for a diagonal one, so a distance divided by 10 is "cells".
    // ════════════════════════════════════════════════════════════════════
    public sealed class RM_ShadePatchGraph
    {
        public const int NoPatch = -1;
        public const int Unreached = int.MaxValue;
        public const int CardinalCost = 10;
        public const int DiagonalCost = 14;

        public sealed class Patch
        {
            public int id;
            public int cellCount;
            /// <summary>Shade cells of this patch that touch walkable open sun.</summary>
            public readonly List<int> rim = new List<int>();
            public readonly List<Edge> edges = new List<Edge>();
        }

        /// <summary>One hop between two patches, across open sun. fromCell is
        /// the rim cell to leave from, toCell the rim cell to arrive at, and
        /// cost is the shortest open-ground distance between them.</summary>
        public struct Edge
        {
            public int to;
            public int cost;
            public int fromCell;
            public int toCell;
        }

        public readonly int width;
        public readonly int height;

        /// <summary>The patch id for each cell, or NoPatch for open sun or a
        /// blocked cell.</summary>
        public readonly int[] patchOf;

        /// <summary>Cost to the nearest shade cell over walkable ground, up to
        /// the cap. 0 on a shade cell. Unreached when beyond the cap or cut
        /// off.</summary>
        public readonly int[] distToShade;

        /// <summary>The rim (or shade) cell that distToShade leads to, or -1.</summary>
        public readonly int[] nearestShade;

        public readonly List<Patch> patches = new List<Patch>();

        private RM_ShadePatchGraph(int width, int height)
        {
            this.width = width;
            this.height = height;
            int n = width * height;
            patchOf = new int[n];
            distToShade = new int[n];
            nearestShade = new int[n];
        }

        public int PatchCount => patches.Count;

        public int EdgeCount
        {
            get
            {
                int e = 0;
                for (int i = 0; i < patches.Count; i++)
                {
                    e += patches[i].edges.Count;
                }
                return e / 2;
            }
        }

        /// <summary>
        /// Builds the graph from two per-cell masks.
        ///   shade:    the cell counts as shade (low exposure).
        ///   walkable: a pawn can stand on and cross the cell.
        /// Shade patches are 8-connected groups of shade and walkable cells.
        /// A group smaller than minPatchCells is not a patch, since a one-cell
        /// fleck behind a pebble is no place to rest, and its cells count as
        /// open sun. The distance field is a multi-source Dijkstra over open
        /// walkable cells from every rim, capped at capCost. Two patches get
        /// an edge when the fronts spreading from each of them meet within
        /// capCost. Cost is O(cells) and it allocates once.
        /// </summary>
        public static RM_ShadePatchGraph Build(int width, int height, bool[] shade, bool[] walkable,
            int capCost, int minPatchCells)
        {
            RM_ShadePatchGraph g = new RM_ShadePatchGraph(width, height);
            int n = width * height;
            for (int i = 0; i < n; i++)
            {
                g.patchOf[i] = NoPatch;
                g.distToShade[i] = Unreached;
                g.nearestShade[i] = -1;
            }
            g.Label(shade, walkable, Math.Max(1, minPatchCells));
            g.Spread(walkable, Math.Max(0, capCost));
            return g;
        }

        private void Label(bool[] shade, bool[] walkable, int minPatchCells)
        {
            int n = width * height;
            Stack<int> stack = new Stack<int>();
            List<int> members = new List<int>();
            bool[] seen = new bool[n];
            for (int start = 0; start < n; start++)
            {
                if (seen[start] || !shade[start] || !walkable[start])
                {
                    continue;
                }
                members.Clear();
                seen[start] = true;
                stack.Push(start);
                while (stack.Count > 0)
                {
                    int u = stack.Pop();
                    members.Add(u);
                    int ux = u % width, uz = u / width;
                    for (int dz = -1; dz <= 1; dz++)
                    {
                        for (int dx = -1; dx <= 1; dx++)
                        {
                            if (dx == 0 && dz == 0) continue;
                            int vx = ux + dx, vz = uz + dz;
                            if (vx < 0 || vz < 0 || vx >= width || vz >= height) continue;
                            int v = vz * width + vx;
                            if (seen[v] || !shade[v] || !walkable[v]) continue;
                            seen[v] = true;
                            stack.Push(v);
                        }
                    }
                }
                if (members.Count < minPatchCells)
                {
                    continue; // a fleck, which counts as open sun
                }
                Patch p = new Patch { id = patches.Count, cellCount = members.Count };
                patches.Add(p);
                for (int k = 0; k < members.Count; k++)
                {
                    patchOf[members[k]] = p.id;
                }
            }
            // Rims: shade cells with a walkable open neighbour.
            for (int i = 0; i < n; i++)
            {
                int pid = patchOf[i];
                if (pid == NoPatch) continue;
                distToShade[i] = 0;
                nearestShade[i] = i;
                int ix = i % width, iz = i / width;
                bool rim = false;
                for (int dz = -1; dz <= 1 && !rim; dz++)
                {
                    for (int dx = -1; dx <= 1; dx++)
                    {
                        if (dx == 0 && dz == 0) continue;
                        int vx = ix + dx, vz = iz + dz;
                        if (vx < 0 || vz < 0 || vx >= width || vz >= height) continue;
                        int v = vz * width + vx;
                        if (walkable[v] && patchOf[v] == NoPatch)
                        {
                            rim = true;
                            break;
                        }
                    }
                }
                if (rim)
                {
                    patches[pid].rim.Add(i);
                }
            }
        }

        private void Spread(bool[] walkable, int capCost)
        {
            int n = width * height;
            // For each cell, the patch its nearest shade belongs to.
            int[] srcPatch = new int[n];
            for (int i = 0; i < n; i++)
            {
                srcPatch[i] = patchOf[i];
            }
            // Dial's bucket queue: costs are small integers up to capCost.
            List<int>[] buckets = new List<int>[capCost + 1];
            for (int p = 0; p < patches.Count; p++)
            {
                List<int> rim = patches[p].rim;
                for (int k = 0; k < rim.Count; k++)
                {
                    (buckets[0] ??= new List<int>()).Add(rim[k]);
                }
            }
            for (int c = 0; c <= capCost; c++)
            {
                List<int> b = buckets[c];
                if (b == null) continue;
                for (int k = 0; k < b.Count; k++)
                {
                    int u = b[k];
                    if (distToShade[u] != c) continue; // a stale entry
                    int ux = u % width, uz = u / width;
                    for (int dz = -1; dz <= 1; dz++)
                    {
                        for (int dx = -1; dx <= 1; dx++)
                        {
                            if (dx == 0 && dz == 0) continue;
                            int vx = ux + dx, vz = uz + dz;
                            if (vx < 0 || vz < 0 || vx >= width || vz >= height) continue;
                            int v = vz * width + vx;
                            if (!walkable[v] || patchOf[v] != NoPatch) continue;
                            int nd = c + (dx != 0 && dz != 0 ? DiagonalCost : CardinalCost);
                            if (nd > capCost || nd >= distToShade[v]) continue;
                            distToShade[v] = nd;
                            nearestShade[v] = nearestShade[u];
                            srcPatch[v] = srcPatch[u];
                            (buckets[nd] ??= new List<int>()).Add(v);
                        }
                    }
                }
                buckets[c] = null;
            }
            // Edges: wherever two fronts touch, the hop is dist(u) + step + dist(v).
            Dictionary<long, Edge> best = new Dictionary<long, Edge>();
            for (int u = 0; u < n; u++)
            {
                int pa = srcPatch[u];
                if (pa == NoPatch || distToShade[u] == Unreached) continue;
                int ux = u % width, uz = u / width;
                for (int dz = -1; dz <= 1; dz++)
                {
                    for (int dx = -1; dx <= 1; dx++)
                    {
                        if (dx == 0 && dz == 0) continue;
                        int vx = ux + dx, vz = uz + dz;
                        if (vx < 0 || vz < 0 || vx >= width || vz >= height) continue;
                        int v = vz * width + vx;
                        int pb = srcPatch[v];
                        if (pb == NoPatch || pb <= pa || distToShade[v] == Unreached || !walkable[v]) continue;
                        int total = distToShade[u] + distToShade[v] + (dx != 0 && dz != 0 ? DiagonalCost : CardinalCost);
                        if (total > capCost) continue;
                        long key = ((long)pa << 32) | (uint)pb;
                        if (!best.TryGetValue(key, out Edge e) || total < e.cost)
                        {
                            best[key] = new Edge { to = pb, cost = total, fromCell = nearestShade[u], toCell = nearestShade[v] };
                        }
                    }
                }
            }
            foreach (KeyValuePair<long, Edge> kv in best)
            {
                int pa = (int)(kv.Key >> 32);
                Edge e = kv.Value;
                patches[pa].edges.Add(e);
                patches[e.to].edges.Add(new Edge { to = pa, cost = e.cost, fromCell = e.toCell, toCell = e.fromCell });
            }
        }

        public int PatchAt(int index)
        {
            return index >= 0 && index < patchOf.Length ? patchOf[index] : NoPatch;
        }

        /// <summary>Octile distance in cost units between two cells, the
        /// straight-line lower bound on a walk between them.</summary>
        public static int Octile(int ax, int az, int bx, int bz)
        {
            int dx = Math.Abs(ax - bx), dz = Math.Abs(az - bz);
            int lo = Math.Min(dx, dz), hi = Math.Max(dx, dz);
            return lo * DiagonalCost + (hi - lo) * CardinalCost;
        }

        /// <summary>§6 ring: every cell a pawn at `origin` can reach and still
        /// get back into shade within rangeCost, measured as the straight
        /// line out (octile) plus the field's walk from there to the nearest
        /// shade. Cells in shade qualify on the way out alone. Scans only the
        /// (2r+1)² square around the origin.</summary>
        public void ReachableWithReturn(int origin, int rangeCost, List<int> result)
        {
            result.Clear();
            if (rangeCost <= 0 || origin < 0 || origin >= patchOf.Length)
            {
                return;
            }
            int ox = origin % width, oz = origin / width;
            int r = rangeCost / CardinalCost;
            for (int z = Math.Max(0, oz - r); z <= Math.Min(height - 1, oz + r); z++)
            {
                for (int x = Math.Max(0, ox - r); x <= Math.Min(width - 1, ox + r); x++)
                {
                    int i = z * width + x;
                    int back = distToShade[i];
                    if (back == Unreached) continue;
                    int outCost = Octile(ox, oz, x, z);
                    if (outCost + back <= rangeCost)
                    {
                        result.Add(i);
                    }
                }
            }
        }
    }

    /// <summary>§5 dash range: how far a creature will cross open sun, from
    /// tranche 1's exposure model and vanilla's own Heatstroke rate.</summary>
    public static class RM_DashMath
    {
        /// <summary>HediffGiver_Heat runs every 60 ticks (Pawn_HealthTracker,
        /// IsHashIntervalTick(60)).</summary>
        public const int HeatIntervalTicks = 60;

        /// <summary>Heatstroke added per interval, given the vanilla overage
        /// curve already evaluated at (felt − safe max). This is
        /// HediffGiver_Heat.OnIntervalPassed: max(curve × 6.45e-5, 0.000375).</summary>
        public static float SeverityPerInterval(float curvedOverage)
        {
            return Math.Max(curvedOverage * 6.45E-05f, 0.000375f);
        }

        /// <summary>Ticks a creature can spend in full sun before it gains
        /// `budget` Heatstroke. int.MaxValue when full sun does not push it
        /// past its safe max at all, or when it has no budget left
        /// (budget ≤ 0 gives 0).</summary>
        public static int ToleratedTicks(float feltInSunC, float safeMaxC, float curvedOverage, float budget)
        {
            if (budget <= 0f)
            {
                return 0;
            }
            if (feltInSunC <= safeMaxC)
            {
                return int.MaxValue;
            }
            float per = SeverityPerInterval(curvedOverage);
            double ticks = budget / per * HeatIntervalTicks;
            return ticks >= int.MaxValue ? int.MaxValue : (int)ticks;
        }

        /// <summary>Ticks for one cardinal cell at a locomotion factor (Sprint
        /// 0.75, Jog 1; from Pawn_PathFollower.CostToMoveIntoCell), never
        /// below 1.</summary>
        public static float TicksPerCell(float ticksPerMoveCardinal, float urgencyFactor)
        {
            float t = ticksPerMoveCardinal * urgencyFactor;
            return t < 1f ? 1f : t;
        }

        /// <summary>Dash range in cost units (10 per cell): the cells coverable
        /// in the tolerated ticks, × strictness (the Mod Settings dial), and
        /// clamped to [minCells, maxCells]. With no budget left the range is 0,
        /// because an overheated creature stays in its shade.</summary>
        public static int DashRangeCost(int toleratedTicks, float ticksPerCell, float strictnessRange,
            float minCells, float maxCells)
        {
            if (toleratedTicks <= 0 || strictnessRange <= 0f)
            {
                return 0;
            }
            double cells = toleratedTicks == int.MaxValue ? maxCells : toleratedTicks / (double)ticksPerCell;
            cells *= strictnessRange;
            if (cells > maxCells) cells = maxCells;
            if (cells < minCells) cells = minCells;
            return (int)Math.Round(cells * RM_ShadePatchGraph.CardinalCost);
        }
    }
}
