// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 build step 7 (design atmospheric_base_god_patterns_2026-10-24 §1.1 P6-P9).
//
// The walkers: primitives that move a few marks over the FIXTURES rather than washing rooms.
//   P6 PROCESSION  k heads along a fixed tour of the fixtures (or of the rooms), each with a tail. Cost Front.
//   P7 COIL        2-3 persistent random walks over the fixture neighbour graph; crossings flare. Cost Heavy.
//   P8 TELL        one fixture takes the layer's (foreign) entry for a beat, then returns. Cost Light.
//   P9 COUNT       a marked set holds one entry, the rest another. Cost Still (Light with tremble / accumulate).
// All of them read the step-4 substrate (graph + fixture set) through RM_WalkMap, built once per (graph, fixtures,
// anchor) and replaced only when one of those instances is replaced (RM_GraphCache keeps them across a pass that changed
// nothing). A fixture with no slot (no fixture set) is Pass: these patterns have no room-local meaning.
//
// The drawn layer (design decision 4: a glow travelling between fixtures in true black) does NOT exist in this mod. The
// layer flag `drawnInBlack` is accepted and validated and changes nothing: the ember is real grid light at the layer's
// entries (author "1~1" over a black palette entry 0). RM_PatternKernel.DrawnLayerBuilt says so; the proof's row for it
// is UNMEASURED until a drawn layer is built.
using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;

namespace RimMandrake.AtmosphericBase
{
    public enum RM_WalkGraph { Adjacency = 0, Rooms, Conduits }
    public enum RM_Step { Walk = 0, Jump }
    public enum RM_Pick { Spread = 0, NearestAnchor, Brightest }

    /// <summary>The walk substrate over one fixture set: a tour (each fixture once, rooms in depth-first order from the
    /// anchor, nearest-neighbour order inside a room), the rooms' order, a neighbour list per fixture, and the COUNT
    /// orders. Fixtures outside the graph (outdoors) form one last group.</summary>
    public sealed class RM_WalkMap
    {
        public int[] tour;          // fixture slots in visit order
        public int[] pos;           // slot -> index in tour
        public int[] group;         // slot -> group index (groups in tour order)
        public int[] groupNode;     // group -> graph node (-1 = the outdoor group)
        public int[] groupSize;
        public int[] rank;          // slot -> rank inside its group (stable hash order, for COUNT)
        public int[] spreadOrder;   // slot -> COUNT order, round robin over the groups
        public int[] nearOrder;     // slot -> COUNT order, groups nearest the anchor first
        public int[][] nb;          // slot -> neighbour slots (same room nearest 3 + the nearest in each adjacent room)
        public int Groups => groupSize.Length;

        private static RM_RoomGraph lastGraph;
        private static RM_FixtureSet lastFixtures;
        private static readonly Dictionary<RM_Anchor, RM_WalkMap> byAnchor = new Dictionary<RM_Anchor, RM_WalkMap>();
        public static int Builds { get; private set; }

        /// <summary>The map for (graph, fixtures, anchor); null when there is no fixture set. Rebuilt only when the graph or
        /// the fixture set instance changes.</summary>
        public static RM_WalkMap For(RM_RoomGraph g, RM_FixtureSet f, RM_Anchor a)
        {
            if (f == null) return null;
            if (!ReferenceEquals(g, lastGraph) || !ReferenceEquals(f, lastFixtures))
            {
                byAnchor.Clear(); lastGraph = g; lastFixtures = f;
            }
            if (byAnchor.TryGetValue(a, out RM_WalkMap m)) return m;
            m = Build(g, f, a);
            byAnchor[a] = m;
            Builds++;
            return m;
        }

        private static float D2(RM_FixtureSet f, int i, int j) { float dx = f.x[i] - f.x[j], dz = f.z[i] - f.z[j]; return dx * dx + dz * dz; }

        private static RM_WalkMap Build(RM_RoomGraph g, RM_FixtureSet f, RM_Anchor a)
        {
            int n = f.Count;
            var m = new RM_WalkMap { pos = new int[n], group = new int[n], rank = new int[n], spreadOrder = new int[n], nearOrder = new int[n], nb = new int[n][] };
            // fixtures by graph node
            int nodes = g?.Count ?? 0;
            var at = new List<int>[nodes + 1];   // [nodes] = the outdoor group
            for (int k = 0; k < n; k++)
            {
                int node = g != null ? g.Node(f.room[k]) : -1;
                int b = node >= 0 ? node : nodes;
                (at[b] ?? (at[b] = new List<int>())).Add(k);
            }
            // rooms in depth-first preorder from the anchor, then the rest, then outdoors
            var order = new List<int>();
            if (g != null)
            {
                var seen = new bool[nodes];
                var starts = new List<int>(g.AnchorNodes(a));
                for (int i = 0; i < nodes; i++) starts.Add(i);
                var stack = new Stack<int>();
                foreach (int s0 in starts)
                {
                    if (seen[s0]) continue;
                    stack.Push(s0);
                    while (stack.Count > 0)
                    {
                        int u = stack.Pop();
                        if (seen[u]) continue;
                        seen[u] = true;
                        order.Add(u);
                        int[] adj = g.adj[u];
                        for (int i = adj.Length - 1; i >= 0; i--) if (!seen[adj[i]]) stack.Push(adj[i]);
                    }
                }
            }
            order.Add(nodes);
            var tour = new List<int>(n);
            var gNode = new List<int>();
            var gSize = new List<int>();
            var groupOfNode = new int[nodes + 1];
            for (int i = 0; i <= nodes; i++) groupOfNode[i] = -1;
            int prev = -1;
            foreach (int b in order)
            {
                List<int> members = at[b];
                if (members == null || members.Count == 0) continue;
                int gi = gNode.Count;
                groupOfNode[b] = gi;
                gNode.Add(b < nodes ? b : -1);
                gSize.Add(members.Count);
                // nearest-neighbour chain, entered from the fixture nearest the previous tour fixture
                var left = new List<int>(members);
                left.Sort();
                int cur = left[0];
                if (prev >= 0) { float bd = float.MaxValue; foreach (int k in left) { float d = D2(f, prev, k); if (d < bd) { bd = d; cur = k; } } }
                while (true)
                {
                    left.Remove(cur);
                    m.group[cur] = gi;
                    m.pos[cur] = tour.Count;
                    tour.Add(cur);
                    prev = cur;
                    if (left.Count == 0) break;
                    float bd = float.MaxValue; int nx = left[0];
                    foreach (int k in left) { float d = D2(f, cur, k); if (d < bd) { bd = d; nx = k; } }
                    cur = nx;
                }
                // stable rank inside the group (COUNT picks): a new lamp moves a pick only if it outranks it
                var byHash = new List<int>(members);
                byHash.Sort((p, q) => { int c = RM_SchemeKernel.Mix(f.ids[p], 13).CompareTo(RM_SchemeKernel.Mix(f.ids[q], 13)); return c != 0 ? c : p.CompareTo(q); });
                for (int r = 0; r < byHash.Count; r++) m.rank[byHash[r]] = r;
            }
            m.tour = tour.ToArray();
            m.groupNode = gNode.ToArray();
            m.groupSize = gSize.ToArray();
            int G = m.groupSize.Length;
            // COUNT orders: spread = round robin over the groups in tour order; nearest = groups by anchor distance
            var bySlotRank = new int[G][];
            for (int gi = 0; gi < G; gi++) bySlotRank[gi] = new int[m.groupSize[gi]];
            for (int k = 0; k < n; k++) bySlotRank[m.group[k]][m.rank[k]] = k;
            int o = 0;
            for (int r = 0; o < n; r++)
                for (int gi = 0; gi < G; gi++) if (r < m.groupSize[gi]) m.spreadOrder[bySlotRank[gi][r]] = o++;
            var gs = new int[G];
            for (int gi = 0; gi < G; gi++) gs[gi] = gi;
            Func<int, int> dist = gi => g == null || m.groupNode[gi] < 0 ? RM_RoomGraph.Unreached + 1 : g.Distance(a, m.groupNode[gi]);
            Array.Sort(gs, (p, q) => { int c = dist(p).CompareTo(dist(q)); return c != 0 ? c : p.CompareTo(q); });
            o = 0;
            foreach (int gi in gs) foreach (int k in bySlotRank[gi]) m.nearOrder[k] = o++;
            // neighbours: the 3 nearest in the same room, plus the nearest fixture of each adjacent room
            for (int k = 0; k < n; k++)
            {
                var list = new List<int>();
                List<int> same = at[m.groupNode[m.group[k]] >= 0 ? m.groupNode[m.group[k]] : nodes];
                var cand = new List<int>(same); cand.Remove(k);
                cand.Sort((p, q) => { int c = D2(f, k, p).CompareTo(D2(f, k, q)); return c != 0 ? c : p.CompareTo(q); });
                for (int i = 0; i < cand.Count && i < 3; i++) list.Add(cand[i]);
                int node = m.groupNode[m.group[k]];
                if (node >= 0)
                    foreach (int v in g.adj[node])
                    {
                        List<int> other = at[v];
                        if (other == null || other.Count == 0) continue;
                        int best = other[0]; float bd = float.MaxValue;
                        foreach (int j in other) { float d = D2(f, k, j); if (d < bd || (d == bd && j < best)) { bd = d; best = j; } }
                        list.Add(best);
                    }
                m.nb[k] = list.ToArray();
            }
            return m;
        }
    }

    // ---------------------------------------------------------------- P6 PROCESSION. Cost Front.
    // Time runs in steps of dwell + hop. During step s head h sits on tour[cursor(s, h)]: lit at hi for the dwell, out
    // for the hop (with `overlap` it stays lit through the hop while the NEXT lamp is already lit: the dark procession).
    // The j-th tail lamp (the head's position j steps ago) shows hi - j, never below lo. `trace` (walk only): every lamp
    // the head has passed on this lap of the tour holds lo. `pair`: the next lamp of the tour is lit with the head.
    // graph = Rooms: the tour is of rooms and a head lights its whole room. Conduits: the conduit graph is UNMEASURED
    // (catalog II-2); it falls back to Adjacency, as CIRCUIT falls back to TIDE(power).
    public sealed class RM_ProcessionPrimitive : RM_IPrimitive
    {
        public const int MaxHeads = 8;
        [ThreadStatic] private static int[] bufA, bufB;

        public RM_CostClass Cost(RM_Layer l) => RM_CostClass.Front;

        /// <summary>The tour positions of all k heads in step s, distinct (k is at most the tour length).</summary>
        public static int[] Cursors(RM_Layer l, long s, int k, int len, int[] b)
        {
            for (int h = 0; h < k; h++)
            {
                int p;
                if (l.step == RM_Step.Walk) p = (int)(((s + (long)h * len / k) % len + len) % len);
                else
                {
                    p = (int)(RM_SchemeKernel.Mix(unchecked((int)s), 7919 * (h + 1)) % (uint)len);
                    for (bool clash = true; clash;)
                    {
                        clash = false;
                        for (int q = 0; q < h; q++) if (b[q] == p) { clash = true; p = (p + 1) % len; break; }
                    }
                }
                b[h] = p;
            }
            return b;
        }

        private static bool Hits(RM_Layer l, int p, int me, int len) => p == me || (l.pair && (p + 1) % len == me);

        public int Index(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            RM_WalkMap w = RM_WalkMap.For(c.graph, c.fixtures, l.anchor);
            if (w == null || c.slot < 0 || c.slot >= w.pos.Length) return RM_PatternKernel.Pass;
            bool rooms = l.graph == RM_WalkGraph.Rooms;
            int len = rooms ? w.Groups : w.tour.Length;
            if (len == 0) return RM_PatternKernel.Pass;
            int me = rooms ? w.group[c.slot] : w.pos[c.slot];
            int k = Math.Min(Math.Min(l.heads, MaxHeads), len);
            int lo = l.Lo(n), hi = l.Hi(n);
            double D = l.dwell + l.hop;
            long s = (long)Math.Floor(t / D);
            bool inHop = t - s * D >= l.dwell;
            int best = RM_PatternKernel.Pass;
            int[] cur = Cursors(l, s, k, len, bufA ?? (bufA = new int[MaxHeads]));
            int[] other = bufB ?? (bufB = new int[MaxHeads]);
            for (int h = 0; h < k; h++)
                if ((!inHop || l.overlap) && Hits(l, cur[h], me, len)) return hi;
            if (inHop && l.overlap)
            {
                int[] nx = Cursors(l, s + 1, k, len, other);
                for (int h = 0; h < k; h++) if (Hits(l, nx[h], me, len)) return hi;
            }
            for (int j = 1; j <= l.tail; j++)
            {
                int[] back = Cursors(l, s - j, k, len, other);
                for (int h = 0; h < k; h++) if (Hits(l, back[h], me, len)) { best = Math.Max(best, Math.Max(lo, hi - j)); break; }
                if (best != RM_PatternKernel.Pass) break;   // the nearest tail position is the brightest
            }
            if (l.trace > 0 && l.step == RM_Step.Walk && best == RM_PatternKernel.Pass)
                for (int h = 0; h < k; h++)
                {
                    int lap = (int)(((s + (long)h * len / k) % len + len) % len);   // how far this head is into its lap
                    int start = (int)(((long)h * len / k) % len);
                    int since = ((me - start) % len + len) % len;                   // where I lie on this head's lap
                    int headSince = ((lap - start) % len + len) % len;
                    if (since <= headSince) { best = lo; break; }
                }
            return best;
        }

        public double NextChange(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            if (c.fixtures == null || c.slot < 0) return RM_PatternKernel.Never;
            double D = l.dwell + l.hop;
            long s = (long)Math.Floor(t / D);
            double next = RM_PatternEvaluator.NextStep(t / D, D, t);
            double dwellEnd = s * D + l.dwell;
            if (l.hop > 0f && t < dwellEnd) next = Math.Min(next, RM_Front.Nudge(dwellEnd, t));
            return next;
        }

        public void Errors(RM_Layer l, int n, List<string> e)
        {
            if (l.heads < 1 || l.heads > MaxHeads) e.Add("heads must lie in 1-" + MaxHeads);
            if (l.hop < 0f || l.dwell < 0f || !(l.hop + l.dwell > 0f)) e.Add("hop and dwell must be >= 0 with hop + dwell > 0");
            if (l.tail < 0 || l.tail > 8) e.Add("tail must lie in 0-8");
            if (l.trace < 0 || l.trace > 1) e.Add("trace must be 0 or 1 (+1: a visited lamp keeps one step up)");
            if (l.trace > 0 && l.step == RM_Step.Jump) e.Add("trace needs step Walk (a jump has no lap to keep)");
            if (!Enum.IsDefined(typeof(RM_WalkGraph), l.graph)) e.Add("graph is not Adjacency, Rooms or Conduits");
        }
    }

    // ---------------------------------------------------------------- P7 COIL. Cost Heavy.
    // `coils` heads each walk the fixture neighbour graph one hop per `hop` s: with chance 1 - turnChance the walk keeps
    // its direction (the neighbour most nearly straight on), else it turns to a random neighbour (never straight back
    // unless it must). The last `length` positions are the coil, hi at the head falling to lo at the tail; a lamp under
    // two coils at once flares to hi. The walks are a hash of (step, coil), so the figure never exactly repeats; the
    // state is advanced incrementally per layer (a fresh fixture set restarts it from t = 0).
    public sealed class RM_CoilPrimitive : RM_IPrimitive
    {
        public const int MaxCoils = 3, MaxLength = 12;

        private sealed class State
        {
            public RM_WalkMap map;
            public long step = -1;
            public int[][] trail;   // [coil][j] slot j steps back (0 = the head)
        }

        private static readonly ConditionalWeakTable<RM_Layer, State> states = new ConditionalWeakTable<RM_Layer, State>();

        public RM_CostClass Cost(RM_Layer l) => RM_CostClass.Heavy;

        private static int Next(RM_Layer l, RM_FixtureSet f, RM_WalkMap w, int coil, long s, int cur, int prev)
        {
            int[] nb = w.nb[cur];
            if (nb.Length == 0) return cur;
            var cand = new List<int>(nb.Length);
            foreach (int v in nb) if (v != prev) cand.Add(v);
            if (cand.Count == 0) return nb[0];
            uint h = RM_SchemeKernel.Mix(unchecked((int)s), 104729 * (coil + 1));
            double roll = (h & 0xFFFF) / 65536.0;
            if (prev < 0 || prev == cur || roll < l.turnChance) return cand[(int)((h >> 16) % (uint)cand.Count)];
            float dx = f.x[cur] - f.x[prev], dz = f.z[cur] - f.z[prev];
            int best = cand[0]; double bd = double.NegativeInfinity;
            foreach (int v in cand)
            {
                float vx = f.x[v] - f.x[cur], vz = f.z[v] - f.z[cur];
                double len = Math.Sqrt(vx * vx + vz * vz) + 1e-6;
                double d = (vx * dx + vz * dz) / len;
                if (d > bd) { bd = d; best = v; }
            }
            return best;
        }

        /// <summary>The coils' trails at step s (advanced forward from the cached step; restarted from 0 when s goes back
        /// or the fixture set changed).</summary>
        public static int[][] Trails(RM_Layer l, RM_FixtureSet f, RM_WalkMap w, long s)
        {
            State st = states.GetOrCreateValue(l);
            int k = Math.Max(1, Math.Min(l.coils, MaxCoils)), len = Math.Max(1, Math.Min(l.length, MaxLength));
            int F = w.tour.Length;
            if (s < 0) s = 0;
            if (!ReferenceEquals(st.map, w) || s < st.step || st.trail == null)
            {
                st.map = w; st.step = 0; st.trail = new int[k][];
                for (int c = 0; c < k; c++)
                {
                    st.trail[c] = new int[len];
                    int p = F == 0 ? 0 : (int)(RM_SchemeKernel.Mix(c + 1, 6151) % (uint)F);
                    for (int j = 0; j < len; j++) st.trail[c][j] = p;
                }
            }
            if (F == 0) return st.trail;
            for (; st.step < s; st.step++)
                for (int c = 0; c < k; c++)
                {
                    int[] tr = st.trail[c];
                    int nx = Next(l, f, w, c, st.step + 1, tr[0], len > 1 ? tr[1] : -1);
                    for (int j = len - 1; j > 0; j--) tr[j] = tr[j - 1];
                    tr[0] = nx;
                }
            return st.trail;
        }

        public int Index(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            RM_WalkMap w = RM_WalkMap.For(c.graph, c.fixtures, l.anchor);
            if (w == null || c.slot < 0 || c.slot >= w.pos.Length || w.tour.Length == 0) return RM_PatternKernel.Pass;
            int lo = l.Lo(n), hi = l.Hi(n);
            int[][] tr = Trails(l, c.fixtures, w, (long)Math.Floor(t / l.hop));
            int best = RM_PatternKernel.Pass, under = 0;
            foreach (int[] coil in tr)
            {
                int len = coil.Length;
                for (int j = 0; j < len; j++)
                    if (coil[j] == c.slot)
                    {
                        under++;
                        int v = len <= 1 ? hi : hi - (int)Math.Round((double)j * (hi - lo) / (len - 1));
                        best = Math.Max(best, v);
                        break;
                    }
            }
            return under >= 2 ? hi : best;
        }

        public double NextChange(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            if (c.fixtures == null || c.slot < 0) return RM_PatternKernel.Never;
            return RM_PatternEvaluator.NextStep(t / l.hop, l.hop, t);
        }

        public void Errors(RM_Layer l, int n, List<string> e)
        {
            if (l.coils < 1 || l.coils > MaxCoils) e.Add("coils must lie in 1-" + MaxCoils);
            if (!(l.hop > 0f)) e.Add("hop must be > 0");
            if (l.turnChance < 0f || l.turnChance > 1f) e.Add("turnChance must lie in 0-1");
            if (l.length < 1 || l.length > MaxLength) e.Add("length must lie in 1-" + MaxLength);
        }
    }

    // ---------------------------------------------------------------- P8 TELL. Cost Light.
    // Time runs in slots of `interval` s. In each slot, at a hashed moment, up to `cap` fixtures take the layer's hi entry
    // (the foreign colour) for `beat` s; otherwise Pass. cap -1 = the integer rule (L6, design P8): 1 when the fleet has
    // at least 8 fixtures, else 0. An explicit cap is clamped to 3 (at most three claimants).
    public sealed class RM_TellPrimitive : RM_IPrimitive
    {
        public const int MaxCap = 3, AutoFleet = 8;

        public RM_CostClass Cost(RM_Layer l) => RM_CostClass.Light;

        public static int CapFor(RM_Layer l, int fleet)
        {
            int cap = l.cap >= 0 ? Math.Min(l.cap, MaxCap) : (fleet >= AutoFleet ? 1 : 0);
            return Math.Max(0, Math.Min(cap, fleet));
        }

        private static double Start(RM_Layer l, long s) => s * (double)l.interval + RM_SchemeKernel.Frac01(unchecked((int)s), 23) * (l.interval - l.beat);

        public static bool Chosen(RM_Layer l, int fleet, long s, int slot)
        {
            int cap = CapFor(l, fleet);
            if (cap == 0) return false;
            int first = -1, second = -1;
            for (int j = 0; j < cap; j++)
            {
                int p = (int)(RM_SchemeKernel.Mix(unchecked((int)s), 337 * (j + 1)) % (uint)fleet);
                while (p == first || p == second) p = (p + 1) % fleet;
                if (p == slot) return true;
                if (j == 0) first = p; else second = p;
            }
            return false;
        }

        public int Index(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            if (c.fixtures == null || c.slot < 0) return RM_PatternKernel.Pass;
            long s = (long)Math.Floor(t / l.interval);
            double st = Start(l, s);
            if (t < st || t >= st + l.beat) return RM_PatternKernel.Pass;
            return Chosen(l, c.fixtures.Count, s, c.slot) ? l.Hi(n) : RM_PatternKernel.Pass;
        }

        public double NextChange(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            if (c.fixtures == null || c.slot < 0) return RM_PatternKernel.Never;
            long s = (long)Math.Floor(t / l.interval);
            double slotEnd = RM_PatternEvaluator.NextStep(t / l.interval, l.interval, t);
            if (!Chosen(l, c.fixtures.Count, s, c.slot)) return slotEnd;
            double st = Start(l, s);
            if (t < st) return RM_Front.Nudge(st, t);
            if (t < st + l.beat) return RM_Front.Nudge(st + l.beat, t);
            return slotEnd;
        }

        public void Errors(RM_Layer l, int n, List<string> e)
        {
            if (!(l.interval > 0f)) e.Add("interval must be > 0");
            if (!(l.beat > 0f) || l.beat > l.interval) e.Add("beat must be > 0 and fit inside interval");
            if (l.cap < -1 || l.cap > MaxCap) e.Add("cap must be -1 (the integer rule) or 0-" + MaxCap);
        }
    }

    // ---------------------------------------------------------------- P9 COUNT. Cost Still (Light with tremble/accumulate).
    // The marked fixtures show markEntry (-1 = the layer's hi), the rest restEntry (-1 = Pass, so the layers under it
    // show). Marked = the first n in the pick order (perRoom: the first n of each room), or with `accumulate` the first
    // floor(t / beat) mod (room size + 1) of each room: one more per beat until the room is full, then clear.
    // `tremble`: a marked fixture alternates markEntry and the entry below it (above, at entry 0) every 0.8-1.5 s.
    // pick Brightest needs the fixtures' light radius, which the fixture set does not carry: it falls back to Spread
    // (the proof row says UNMEASURED).
    public sealed class RM_CountPrimitive : RM_IPrimitive
    {
        public RM_CostClass Cost(RM_Layer l) => l.tremble || l.accumulate ? RM_CostClass.Light : RM_CostClass.Still;

        private static double TremblePeriod(int emitter) => 0.8 + 0.7 * RM_SchemeKernel.Frac01(emitter, 17);

        public static bool Marked(RM_Layer l, RM_WalkMap w, int slot, double t)
        {
            int g = w.group[slot], r = w.rank[slot];
            if (l.accumulate)
            {
                int size = w.groupSize[g];
                long k = (long)Math.Floor(t / l.beat) % (size + 1);
                return r < k;
            }
            if (l.perRoom) return r < l.n;
            int o = l.pick == RM_Pick.NearestAnchor ? w.nearOrder[slot] : w.spreadOrder[slot];
            return o < l.n;
        }

        public int Index(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            RM_WalkMap w = RM_WalkMap.For(c.graph, c.fixtures, l.anchor);
            if (w == null || c.slot < 0 || c.slot >= w.pos.Length) return RM_PatternKernel.Pass;
            if (!Marked(l, w, c.slot, t)) return l.restEntry >= 0 ? l.restEntry : RM_PatternKernel.Pass;
            int mark = l.markEntry >= 0 ? l.markEntry : l.Hi(n);
            if (!l.tremble) return mark;
            double p = TremblePeriod(c.emitter);
            long st = (long)Math.Floor(t / p + RM_SchemeKernel.Frac01(c.emitter, 19));
            int alt = mark > 0 ? mark - 1 : Math.Min(n - 1, mark + 1);
            return (st & 1) == 0 ? mark : alt;
        }

        public double NextChange(RM_Layer l, int n, ref RM_PatternCtx c, double t)
        {
            if (c.fixtures == null || c.slot < 0) return RM_PatternKernel.Never;
            double next = RM_PatternKernel.Never;
            if (l.accumulate) next = RM_PatternEvaluator.NextStep(t / l.beat, l.beat, t);
            if (l.tremble)
            {
                RM_WalkMap w = RM_WalkMap.For(c.graph, c.fixtures, l.anchor);
                if (w != null && c.slot < w.pos.Length && (l.accumulate || Marked(l, w, c.slot, t)))
                {
                    double p = TremblePeriod(c.emitter);
                    next = Math.Min(next, RM_PatternEvaluator.NextStep(t / p + RM_SchemeKernel.Frac01(c.emitter, 19), p, t));
                }
            }
            return next;
        }

        public void Errors(RM_Layer l, int n, List<string> e)
        {
            if (l.n < 0) e.Add("n must be >= 0");
            if (l.markEntry < -1 || l.markEntry >= n) e.Add("markEntry must be -1 (hi) or an entry 0-" + (n - 1));
            if (l.restEntry < -1 || l.restEntry >= n) e.Add("restEntry must be -1 (Pass) or an entry 0-" + (n - 1));
            if (l.accumulate && !(l.beat > 0f)) e.Add("accumulate needs beat > 0");
            if (!Enum.IsDefined(typeof(RM_Pick), l.pick)) e.Add("pick is not Spread, NearestAnchor or Brightest");
        }
    }
}
