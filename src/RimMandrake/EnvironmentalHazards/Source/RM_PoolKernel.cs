using System;
using System.Collections.Generic;

namespace RimMandrake.EnvironmentalHazards
{
    // Verse-free grid logic of the stranding pools (RM_MapComponent_StrandingPools): connected-component labelling of
    // the water cells, which component is the main network, which tracked pool a component continues, the "has this
    // pool reconnected" bounded flood-fill, the decay target and the shoreline-first cell pick. Cells are plain grid
    // indices (z * width + x, the order Map.AllCells walks) and water is asked through a delegate so the live terrain
    // is read lazily exactly as before. Same BFS order, same cardinal direction order (N, E, S, W as GenAdj), same
    // tie-breaks as the inline code it replaced. No `using Verse;` here - the selftest project compiles this file alone.
    public static class RM_PoolKernel
    {
        // GenAdj.CardinalDirections: (0,+1) (+1,0) (0,-1) (-1,0) in (x,z).
        private static readonly int[] DX = { 0, 1, 0, -1 };
        private static readonly int[] DZ = { 1, 0, -1, 0 };

        public static float Clamp01(float value)
        {
            if (value < 0f) return 0f;
            if (value > 1f) return 1f;
            return value;
        }

        // DetectPools step 1. 4-connected components of water cells in index-scan order; each component lists its
        // cells in BFS dequeue order (so element 0 is the lowest index of the component).
        public static List<List<int>> Components(int width, int height, Func<int, bool> isWater)
        {
            int n = width * height;
            bool[] visited = new bool[n];
            List<List<int>> components = new List<List<int>>();
            for (int start = 0; start < n; start++)
            {
                if (visited[start] || !isWater(start))
                {
                    continue;
                }
                List<int> comp = new List<int>();
                Queue<int> queue = new Queue<int>();
                visited[start] = true;
                queue.Enqueue(start);
                while (queue.Count > 0)
                {
                    int cur = queue.Dequeue();
                    comp.Add(cur);
                    int cx = cur % width, cz = cur / width;
                    for (int d = 0; d < 4; d++)
                    {
                        int nx = cx + DX[d], nz = cz + DZ[d];
                        if (nx < 0 || nz < 0 || nx >= width || nz >= height)
                        {
                            continue;
                        }
                        int nb = nz * width + nx;
                        if (visited[nb] || !isWater(nb))
                        {
                            continue;
                        }
                        visited[nb] = true;
                        queue.Enqueue(nb);
                    }
                }
                components.Add(comp);
            }
            return components;
        }

        // DetectPools step 2. The main network is the first largest component (a later one must be strictly bigger).
        public static int MainIndex(List<List<int>> components)
        {
            int main = 0;
            for (int i = 1; i < components.Count; i++)
            {
                if (components[i].Count > components[main].Count)
                {
                    main = i;
                }
            }
            return main;
        }

        // DetectPools step 3. For each component: the index of the tracked pool it continues, or -1 for none (and the
        // main network always -1). A component continues the pool owning its FIRST cell that any pool owns; where
        // tracked pools share a cell, the later pool owns it. Computed against the pools as they stood before this
        // pass, so a pool created by this pass is never matched.
        public static int[] MatchPools(int width, int height, List<List<int>> components, int main, List<List<int>> poolCells)
        {
            int[] owner = new int[width * height];
            for (int i = 0; i < owner.Length; i++)
            {
                owner[i] = -1;
            }
            for (int p = 0; p < poolCells.Count; p++)
            {
                List<int> cells = poolCells[p];
                for (int i = 0; i < cells.Count; i++)
                {
                    owner[cells[i]] = p;
                }
            }
            int[] match = new int[components.Count];
            for (int i = 0; i < components.Count; i++)
            {
                match[i] = -1;
                if (i == main)
                {
                    continue;
                }
                List<int> comp = components[i];
                for (int c = 0; c < comp.Count; c++)
                {
                    int o = owner[comp[c]];
                    if (o >= 0)
                    {
                        match[i] = o;
                        break;
                    }
                }
            }
            return match;
        }

        // IsReconnected. Bounded flood-fill from the pool's first cell (which need not still be water). True when it
        // reaches a map-edge cell, or the visited set outgrows the cap, either way read as "joined to something big".
        public static bool Reconnected(int width, int height, List<int> poolCells, Func<int, bool> isWater)
        {
            if (poolCells.Count == 0)
            {
                return false;
            }
            int cap = Math.Max(200, poolCells.Count * 8);
            HashSet<int> visited = new HashSet<int> { poolCells[0] };
            Queue<int> queue = new Queue<int>();
            queue.Enqueue(poolCells[0]);
            while (queue.Count > 0)
            {
                if (visited.Count > cap)
                {
                    return true;
                }
                int cur = queue.Dequeue();
                int cx = cur % width, cz = cur / width;
                if (cx == 0 || cz == 0 || cx == width - 1 || cz == height - 1)
                {
                    return true;
                }
                for (int d = 0; d < 4; d++)
                {
                    int nx = cx + DX[d], nz = cz + DZ[d];
                    if (nx < 0 || nz < 0 || nx >= width || nz >= height)
                    {
                        continue;
                    }
                    int nb = nz * width + nx;
                    if (visited.Contains(nb) || !isWater(nb))
                    {
                        continue;
                    }
                    visited.Add(nb);
                    queue.Enqueue(nb);
                }
            }
            return false;
        }

        // DecayPool step 1. false = nothing to do this pass; otherwise the cell count the pool should be down to.
        public static bool TryDecayTarget(int elapsedTicks, int decayTotalTicks, int originalCellCount, out int targetCount)
        {
            targetCount = 0;
            if (elapsedTicks <= 0 || decayTotalTicks <= 0 || originalCellCount <= 0)
            {
                return false;
            }
            float remainingFraction = Clamp01(1f - (float)elapsedTicks / decayTotalTicks);
            targetCount = (int)Math.Round(originalCellCount * remainingFraction);
            return true;
        }

        // PickEdgeCellToRemove. The first listed cell with a cardinal neighbour that is not water (off-map counts as
        // not water); with none, the last listed cell. Returns the position in the list. List must not be empty.
        public static int PickEdgeIndex(int width, int height, List<int> poolCells, Func<int, bool> isWater)
        {
            for (int i = 0; i < poolCells.Count; i++)
            {
                int c = poolCells[i];
                int cx = c % width, cz = c / width;
                for (int d = 0; d < 4; d++)
                {
                    int nx = cx + DX[d], nz = cz + DZ[d];
                    if (nx < 0 || nz < 0 || nx >= width || nz >= height || !isWater(nz * width + nx))
                    {
                        return i;
                    }
                }
            }
            return poolCells.Count - 1;
        }
    }
}
