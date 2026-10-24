// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 pattern grammar, build step 4 -- the graph substrate
// (design/RimMandrake/atmospheric_base_god_patterns_2026-10-24.md §4 "Graph substrate").
//
// One per-map structure shared by TIDE, RIPPLE, SWEEP, PROCESSION and COIL: rooms as nodes, doors as edges (a doorway
// is collapsed into an edge by the game-side builder, so a door is never a hop of its own), with hop-distance fields
// from named anchors cached on the instance. Its TopologyKey covers rooms and doors only, never the taken fixtures, so a
// lamp taken or released reuses every cached field and only a wall or door edit rebuilds (GPT review: invalidate on
// topology change, not membership change). The fixture set is a separate, cheap structure keyed by membership.
// Anchor meanings are proposals (inference) until the owner sitting: Core = least eccentric room, Medoid = least total
// distance, Threshold = rooms that open onto the outside, Open = most doors, Grandest = most cells, Shrine / Power =
// rooms the builder flags; an anchor with no room falls back to Core so a pattern never loses its geometry.
using System;
using System.Collections.Generic;

namespace RimMandrake.AtmosphericBase
{
    public enum RM_Anchor { Core = 0, Medoid, Threshold, Open, Grandest, Shrine, Power }

    public struct RM_RoomFacts
    {
        public int id;
        public int cells;
        public bool threshold, shrine, power;
    }

    public sealed class RM_RoomGraph
    {
        public const int Unreached = 1 << 20;

        public readonly int[] roomIds;
        public readonly int[][] adj;
        public readonly RM_RoomFacts[] facts;
        public readonly ulong TopologyKey;
        private readonly Dictionary<int, int> nodeOf = new Dictionary<int, int>();
        private readonly Dictionary<RM_Anchor, int[]> fields = new Dictionary<RM_Anchor, int[]>();
        private readonly Dictionary<RM_Anchor, int> maxOf = new Dictionary<RM_Anchor, int>();
        public int FieldsBuilt { get; private set; }

        public int Count => roomIds.Length;
        public int Node(int roomId) => nodeOf.TryGetValue(roomId, out int n) ? n : -1;

        private RM_RoomGraph(RM_RoomFacts[] f, int[][] a, ulong key)
        {
            facts = f; adj = a; TopologyKey = key;
            roomIds = new int[f.Length];
            for (int i = 0; i < f.Length; i++) { roomIds[i] = f[i].id; nodeOf[f[i].id] = i; }
        }

        /// <summary>Nodes sorted by room id; edges deduplicated, self-loops and unknown rooms dropped. Input order never
        /// matters (the key and every field are the same for any permutation).</summary>
        public static RM_RoomGraph Build(IList<RM_RoomFacts> rooms, IList<KeyValuePair<int, int>> doors)
        {
            var byId = new SortedDictionary<int, RM_RoomFacts>();
            if (rooms != null) foreach (RM_RoomFacts r in rooms) byId[r.id] = r;
            var f = new RM_RoomFacts[byId.Count];
            var idx = new Dictionary<int, int>();
            int k = 0;
            foreach (KeyValuePair<int, RM_RoomFacts> kv in byId) { f[k] = kv.Value; idx[kv.Key] = k; k++; }
            var sets = new SortedSet<int>[f.Length];
            for (int i = 0; i < f.Length; i++) sets[i] = new SortedSet<int>();
            if (doors != null)
                foreach (KeyValuePair<int, int> d in doors)
                    if (idx.TryGetValue(d.Key, out int a) && idx.TryGetValue(d.Value, out int b) && a != b) { sets[a].Add(b); sets[b].Add(a); }
            var adj = new int[f.Length][];
            ulong h = 1469598103934665603UL;
            for (int i = 0; i < f.Length; i++)
            {
                adj[i] = new int[sets[i].Count];
                sets[i].CopyTo(adj[i]);
                h = (h ^ (uint)f[i].id) * 1099511628211UL;
                h = (h ^ (uint)f[i].cells) * 1099511628211UL;
                h = (h ^ (uint)((f[i].threshold ? 1 : 0) | (f[i].shrine ? 2 : 0) | (f[i].power ? 4 : 0))) * 1099511628211UL;
                foreach (int j in adj[i]) if (j > i) h = (h ^ ((ulong)(uint)f[i].id << 32 | (uint)f[j].id)) * 1099511628211UL;
            }
            return new RM_RoomGraph(f, adj, h);
        }

        public int[] Bfs(IEnumerable<int> sources)
        {
            var d = new int[Count];
            for (int i = 0; i < d.Length; i++) d[i] = Unreached;
            var q = new Queue<int>();
            foreach (int s in sources) if (s >= 0 && s < Count && d[s] != 0) { d[s] = 0; q.Enqueue(s); }
            while (q.Count > 0)
            {
                int u = q.Dequeue();
                foreach (int v in adj[u]) if (d[v] == Unreached) { d[v] = d[u] + 1; q.Enqueue(v); }
            }
            return d;
        }

        public List<int> AnchorNodes(RM_Anchor a)
        {
            var outp = new List<int>();
            if (Count == 0) return outp;
            switch (a)
            {
                case RM_Anchor.Threshold: for (int i = 0; i < Count; i++) if (facts[i].threshold) outp.Add(i); break;
                case RM_Anchor.Shrine: for (int i = 0; i < Count; i++) if (facts[i].shrine) outp.Add(i); break;
                case RM_Anchor.Power: for (int i = 0; i < Count; i++) if (facts[i].power) outp.Add(i); break;
                case RM_Anchor.Open: outp.Add(ArgBest(i => adj[i].Length * 100000L + facts[i].cells)); break;
                case RM_Anchor.Grandest: outp.Add(ArgBest(i => facts[i].cells)); break;
                case RM_Anchor.Medoid: outp.Add(ArgBest(i => -SumOrEcc(i, false))); break;
                default: outp.Add(ArgBest(i => -SumOrEcc(i, true))); break;
            }
            if (outp.Count == 0) return AnchorNodes(RM_Anchor.Core);
            return outp;
        }

        /// <summary>The highest score; ties to the lowest room id (nodes are id-sorted), so the pick is stable.</summary>
        private int ArgBest(Func<int, long> score)
        {
            int best = 0; long bs = score(0);
            for (int i = 1; i < Count; i++) { long s = score(i); if (s > bs) { bs = s; best = i; } }
            return best;
        }

        /// <summary>Eccentricity (max distance) or total distance from node i; an unreachable room counts as Count hops,
        /// so a node in a big component beats an island.</summary>
        private long SumOrEcc(int i, bool ecc)
        {
            int[] d = Bfs(new[] { i });
            long acc = 0;
            foreach (int x in d) { long v = x == Unreached ? Count : x; acc = ecc ? Math.Max(acc, v) : acc + v; }
            return acc;
        }

        /// <summary>Hop distance from the anchor for every node, cached until the topology changes.</summary>
        public int[] Field(RM_Anchor a)
        {
            if (fields.TryGetValue(a, out int[] f)) return f;
            f = Bfs(AnchorNodes(a));
            int mx = 0;
            foreach (int x in f) if (x != Unreached && x > mx) mx = x;
            fields[a] = f; maxOf[a] = mx; FieldsBuilt++;
            return f;
        }

        public int MaxDistance(RM_Anchor a) { Field(a); return maxOf[a]; }

        /// <summary>A room's distance from the anchor; a fixture with no known room (outdoors) sits one hop past the
        /// farthest room, so fronts still reach it last and never skip it.</summary>
        public int Distance(RM_Anchor a, int node)
        {
            int[] f = Field(a);
            if (node < 0 || node >= f.Length || f[node] == Unreached) return MaxDistance(a) + 1;
            return f[node];
        }
    }

    /// <summary>The taken fixtures, sorted by id: position, room, and their centroid. Rebuilt on a
    /// membership change; never touches the room graph's cached fields.</summary>
    public sealed class RM_FixtureSet
    {
        public readonly int[] ids, room;   // room = room id (-1 outdoors / not in the graph)
        public readonly float[] x, z;
        public readonly float cx, cz;
        public readonly ulong Key;
        private readonly Dictionary<int, int> slotOf = new Dictionary<int, int>();

        public int Count => ids.Length;
        public int Slot(int emitter) => slotOf.TryGetValue(emitter, out int s) ? s : -1;

        public RM_FixtureSet(IList<int> emitters, IList<int> rooms, IList<float> xs, IList<float> zs)
        {
            int n = emitters?.Count ?? 0;
            var order = new int[n];
            for (int i = 0; i < n; i++) order[i] = i;
            Array.Sort(order, (a, b) => emitters[a].CompareTo(emitters[b]));
            ids = new int[n]; room = new int[n]; x = new float[n]; z = new float[n];
            ulong h = 1469598103934665603UL;
            double sx = 0, sz = 0;
            for (int k = 0; k < n; k++)
            {
                int i = order[k];
                ids[k] = emitters[i]; room[k] = rooms[i]; x[k] = xs[i]; z[k] = zs[i];
                slotOf[ids[k]] = k;
                sx += x[k]; sz += z[k];
                h = (h ^ (uint)ids[k]) * 1099511628211UL;
                h = (h ^ (uint)room[k]) * 1099511628211UL;
                h = (h ^ (uint)BitConverter.ToInt32(BitConverter.GetBytes(x[k]), 0)) * 1099511628211UL;
                h = (h ^ (uint)BitConverter.ToInt32(BitConverter.GetBytes(z[k]), 0)) * 1099511628211UL;
            }
            cx = n > 0 ? (float)(sx / n) : 0f; cz = n > 0 ? (float)(sz / n) : 0f;
            Key = h;
        }
    }
}
