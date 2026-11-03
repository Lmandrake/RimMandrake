using System;
using System.Collections.Generic;

namespace RimMandrake.Biomes
{
    // The river graph behind "Planet: drawn rivers" (RIVERS_ROADS_REDESIGN_WORTH_LOOKING_AT; how it is used:
    // RM_WorldPathsDrawn.cs). PURE: System only, no Unity, no RimWorld, so
    // src/RimMandrake/BiomesShell/selftest_world_paths_drawn.py compiles THIS FILE into a console harness and checks
    // it against its Python mirror on swept random river forests.
    //  * heads: leaves that are neither a mouth nor the dry end; taper by mean head distance of a link's two tiles;
    //  * mouths: water tiles in a river system, and leaves next to water;
    //  * dry end: in a system with no mouth, its widest leaf (ties: lowest tile id).
    public static class RM_RiverGraph
    {
        // Mirrored by src/RimMandrake/BiomesShell/selftest_world_paths_drawn.py, which parses these constants from here.
        public const float HeadMin = 0.45f;
        public const float TaperTiles = 6f;
        public const float MouthFan = 1.5f;
        public const float DryMin = 0.3f;
        public const float DryTiles = 4f;
        const int Far = 1 << 20;

        public struct Link { public int a, b; public float width; }

        public sealed class Result
        {
            public readonly Dictionary<long, float> linkFactor = new Dictionary<long, float>();
            public readonly Dictionary<int, float> dryness = new Dictionary<int, float>();   // 0..1, absent = 0
            public int links, heads, mouths, dryEnds, systems;
        }

        public static long Key(int a, int b) => a < b ? ((long)a << 32) | (uint)b : ((long)b << 32) | (uint)a;

        /// <summary>Pure: links (each undirected link may be given once or twice), water(t) = tile is water,
        /// touchesWater(t) = tile is water or has a water neighbour (asked only of leaves).</summary>
        public static Result Analyse(List<Link> input, Func<int, bool> water, Func<int, bool> touchesWater)
        {
            var res = new Result();
            var adj = new Dictionary<int, List<int>>();
            var width = new Dictionary<long, float>();
            foreach (Link l in input)
            {
                if (l.a == l.b) continue;
                long k = Key(l.a, l.b);
                if (width.TryGetValue(k, out float w)) { width[k] = Math.Max(w, l.width); continue; }
                width[k] = l.width;
                if (!adj.TryGetValue(l.a, out List<int> la)) adj[l.a] = la = new List<int>();
                if (!adj.TryGetValue(l.b, out List<int> lb)) adj[l.b] = lb = new List<int>();
                la.Add(l.b); lb.Add(l.a);
            }
            res.links = width.Count;

            var seen = new HashSet<int>();
            var tiles = new List<int>(adj.Keys);
            tiles.Sort();
            var comp = new List<int>();
            var queue = new Queue<int>();
            var headDist = new Dictionary<int, int>();
            var dryDist = new Dictionary<int, int>();
            var mouth = new HashSet<int>();
            foreach (int start in tiles)
            {
                if (!seen.Add(start)) continue;
                comp.Clear(); queue.Enqueue(start);
                while (queue.Count > 0)
                {
                    int t = queue.Dequeue(); comp.Add(t);
                    foreach (int n in adj[t]) if (seen.Add(n)) queue.Enqueue(n);
                }
                comp.Sort();
                res.systems++;
                var leaves = new List<int>();
                foreach (int t in comp)
                {
                    if (water(t)) mouth.Add(t);
                    else if (adj[t].Count == 1) { leaves.Add(t); if (touchesWater(t)) mouth.Add(t); }
                }
                int dryRoot = -1;
                bool anyMouth = false;
                foreach (int t in comp) if (mouth.Contains(t)) { anyMouth = true; break; }
                if (!anyMouth && leaves.Count > 0)
                {
                    float best = -1f;
                    foreach (int t in leaves)   // leaves are in ascending id order: ties go to the lowest id
                    {
                        float w = width[Key(t, adj[t][0])];
                        if (w > best) { best = w; dryRoot = t; }
                    }
                    res.dryEnds++;
                }
                var heads = new List<int>();
                foreach (int t in leaves) if (!mouth.Contains(t) && t != dryRoot) heads.Add(t);
                res.heads += heads.Count;
                foreach (int t in comp) if (mouth.Contains(t)) res.mouths++;
                Bfs(heads, adj, headDist);
                if (dryRoot >= 0) Bfs(new List<int> { dryRoot }, adj, dryDist);
            }

            foreach (KeyValuePair<long, float> kv in width)
            {
                int a = (int)(kv.Key >> 32), b = (int)(uint)kv.Key;
                float f = 1f;
                if (headDist.TryGetValue(a, out int ha) && headDist.TryGetValue(b, out int hb))
                    f = HeadMin + (1f - HeadMin) * Clamp01((ha + hb) * 0.5f / TaperTiles);
                if (mouth.Contains(a) || mouth.Contains(b)) f *= MouthFan;
                if (dryDist.TryGetValue(a, out int da) && dryDist.TryGetValue(b, out int db))
                {
                    float dm = (da + db) * 0.5f;
                    if (dm < DryTiles) f *= DryMin + (1f - DryMin) * dm / DryTiles;
                }
                res.linkFactor[kv.Key] = f;
            }
            foreach (KeyValuePair<int, int> kv in dryDist)
                if (kv.Value < DryTiles) res.dryness[kv.Key] = 1f - kv.Value / DryTiles;
            return res;
        }

        static void Bfs(List<int> sources, Dictionary<int, List<int>> adj, Dictionary<int, int> dist)
        {
            var q = new Queue<int>();
            foreach (int s in sources) if (!dist.ContainsKey(s)) { dist[s] = 0; q.Enqueue(s); }
            while (q.Count > 0)
            {
                int t = q.Dequeue(); int d = dist[t];
                foreach (int n in adj[t]) if (!dist.ContainsKey(n)) { dist[n] = d + 1; q.Enqueue(n); }
            }
        }

        static float Clamp01(float v) => v < 0f ? 0f : v > 1f ? 1f : v;

        // Road wear: a stable per-link number in [0,1), the same from both tiles (selftest mirrors it).
        public static float LinkHash(int a, int b)
        {
            unchecked
            {
                uint x = (uint)Math.Min(a, b) * 73856093u ^ (uint)Math.Max(a, b) * 19349663u;
                x ^= x >> 13; x *= 0x5bd1e995u; x ^= x >> 15;
                return (x & 0xFFFFFF) / 16777216f;
            }
        }
    }

}
