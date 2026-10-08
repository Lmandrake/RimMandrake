// Verse-free kernel of the Flooded Canyon's other rules: the recede aftermath timers and counts (RM_MapComponent_RecedeAftermath.cs),
// the fossil strata geometry (RM_FossilStrata.cs) and the biome score (RM_BiomeWorker_FloodedCanyon.cs). SelfTest/FloodedCanyonFuzz.cs
// compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.FloodedCanyon
{
    public static class RM_CanyonRulesKernel
    {
        public const int CellsPerIrqit = 8;
        public const int MigrantLeaveRetryTicks = 60000;

        // ── recede aftermath ──
        public static int DryTicks(float soakDecayDays) { return Math.Max(2500, (int)Math.Round(soakDecayDays * 60000f)); }
        public static int SalvageTicks(float salvageDecayDays) { return Math.Max(2500, (int)Math.Round(salvageDecayDays * 60000f)); }
        public static int CohortWant(int cohortMax, int wettedCount) { return Math.Min(cohortMax, wettedCount / CellsPerIrqit); }
        public static bool Due(int tick, int now) { return tick >= 0 && now >= tick; }
        // The migrants' departure pass runs only once their time has come, on the 2500-tick beat.
        public static bool MigrantPassRuns(int leaveTick, int now) { return leaveTick >= 0 && now >= leaveTick && now % 2500 == 0; }
        public static bool MigrantsDone(int remaining, int now, int giveUpTick) { return remaining == 0 || now >= giveUpTick; }
        public static bool SalvageTaken(bool spawned, bool sameMap, bool atItsCell, bool stillForbidden) { return spawned && sameMap && atItsCell && stillForbidden; }

        // ── biome score ──
        public static float BiomeScore(bool waterCovered, float rarity, float temperature, float rainfall, float elevation, bool canyonHills,
                                       float tMin, float tMax, float rMin, float rMax, float eMin, float eMax, float spawnChance, Func<bool> seededGatePass,
                                       float baseScore, float degreeWeight, float rainfallDivisor)
        {
            if (waterCovered) return -100f;
            if (rarity <= 0.001f) return -100f;
            if (temperature < tMin || temperature > tMax) return 0f;
            if (rainfall < rMin || rainfall >= rMax) return 0f;
            if (elevation < eMin || elevation > eMax) return 0f;
            if (!canyonHills) return 0f;
            float gate = spawnChance * rarity;
            if (gate < 1f && !seededGatePass()) return 0f;
            float divisor = (rainfallDivisor > 0.0001f) ? rainfallDivisor : 1f;
            return baseScore + (temperature - tMin) * degreeWeight + (rainfall - rMin) / divisor;
        }

        // ── fossil strata ──
        public const int DeepMinDepth = 3;

        public sealed class Faces
        {
            public readonly List<long> FaceCells = new List<long>();
            public readonly Dictionary<long, int> Depth = new Dictionary<long, int>();
            public readonly List<long> Deep = new List<long>();
        }

        public static long Key(int x, int z) { return ((long)x << 32) ^ (uint)z; }

        // A face is a natural wall rock with an open cardinal neighbour (inside the map, no edifice). Depth is the cardinal distance into
        // the rock from a face (faces are depth 1), explored up to DeepMinDepth + 2; cells at DeepMinDepth or more are "deep".
        public static Faces FindFaces(int w, int h, Func<int, int, bool> wallRock, Func<int, int, bool> noEdifice)
        {
            var f = new Faces();
            var frontier = new Queue<long>();
            int[] dx = { 0, 1, 0, -1 }, dz = { 1, 0, -1, 0 };
            for (int z = 0; z < h; z++)
                for (int x = 0; x < w; x++)
                {
                    if (!wallRock(x, z)) continue;
                    bool face = false;
                    for (int i = 0; i < 4 && !face; i++)
                    {
                        int nx = x + dx[i], nz = z + dz[i];
                        if (nx >= 0 && nz >= 0 && nx < w && nz < h && noEdifice(nx, nz)) face = true;
                    }
                    if (!face) continue;
                    long k = Key(x, z);
                    f.FaceCells.Add(k); f.Depth[k] = 1; frontier.Enqueue(k);
                }
            while (frontier.Count > 0)
            {
                long c = frontier.Dequeue();
                int d = f.Depth[c];
                if (d >= DeepMinDepth + 2) continue;
                int cx = (int)(c >> 32), cz = (int)(c & 0xffffffffL);
                for (int i = 0; i < 4; i++)
                {
                    int nx = cx + dx[i], nz = cz + dz[i];
                    long nk = Key(nx, nz);
                    if (f.Depth.ContainsKey(nk) || nx < 0 || nz < 0 || nx >= w || nz >= h || !wallRock(nx, nz)) continue;
                    f.Depth[nk] = d + 1;
                    if (d + 1 >= DeepMinDepth) f.Deep.Add(nk);
                    frontier.Enqueue(nk);
                }
            }
            return f;
        }

        // The rock cells next to flooded ground (8-neighbourhood), each once.
        public static List<long> RecutCandidates(IEnumerable<long> wetted, Func<int, int, bool> wallRock)
        {
            var set = new HashSet<long>(); var list = new List<long>();
            foreach (long w in wetted)
            {
                int wx = (int)(w >> 32), wz = (int)(w & 0xffffffffL);
                for (int dx = -1; dx <= 1; dx++)
                    for (int dz = -1; dz <= 1; dz++)
                    {
                        if (dx == 0 && dz == 0) continue;
                        int nx = wx + dx, nz = wz + dz;
                        if (wallRock(nx, nz) && set.Add(Key(nx, nz))) list.Add(Key(nx, nz));
                    }
            }
            return list;
        }

        // 0 unique (6%), 1 skeleton (20%), 2 impression (the rest)
        public static int PickSeam(float roll) { return roll < 0.06f ? 0 : roll < 0.26f ? 1 : 2; }
    }
}
