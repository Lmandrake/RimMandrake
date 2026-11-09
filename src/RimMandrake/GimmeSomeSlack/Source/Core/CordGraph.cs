// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// Port of nodal.NodeGraph (src/RimMandrake/Utils/mockups/messy_conduit/nodal.py), design §8.2.2:
// conduit cells -> node graph (machines, junctions, terminals, stubs, tangles), needless spurs pruned.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>Vertex id. T: 'c' floor conduit cell, 'w' buried conduit cell, 's' stub (A = walk
    /// cell, B = buried cell), 'm' machine (M = id), 't' tangle, 'k' small dense blob (K = index).</summary>
    public struct VId : IEquatable<VId>, IComparable<VId>
    {
        public readonly char T;
        internal readonly Cell A, B;
        public readonly string M;
        public readonly int K;

        private VId(char t, Cell a, Cell b, string m, int k) { T = t; A = a; B = b; M = m; K = k; }
        internal static VId C(Cell c) => new VId('c', c, default(Cell), null, 0);
        internal static VId W(Cell c) => new VId('w', c, default(Cell), null, 0);
        internal static VId S(Cell walk, Cell buried) => new VId('s', walk, buried, null, 0);
        public static VId Mach(string id) => new VId('m', default(Cell), default(Cell), id, 0);
        public static VId Cluster(char t, int k) => new VId(t, default(Cell), default(Cell), null, k);

        public bool Equals(VId o) => T == o.T && A == o.A && B == o.B && M == o.M && K == o.K;
        public override bool Equals(object obj) => obj is VId v && Equals(v);
        public override int GetHashCode() => unchecked(T * 31 + A.GetHashCode() * 17 + B.GetHashCode() * 7 + (M?.GetHashCode() ?? 0) + K * 1009);
        public int CompareTo(VId o)
        {
            if (T != o.T) return T.CompareTo(o.T);
            int c = A.CompareTo(o.A);
            if (c != 0) return c;
            c = B.CompareTo(o.B);
            if (c != 0) return c;
            c = string.CompareOrdinal(M ?? "", o.M ?? "");
            return c != 0 ? c : K.CompareTo(o.K);
        }
        public static bool operator ==(VId a, VId b) => a.Equals(b);
        public static bool operator !=(VId a, VId b) => !a.Equals(b);
        public bool IsCellish => T == 'c' || T == 'w';
        public override string ToString() => T == 'm' ? "m:" + M : T == 's' ? "s:" + A + B : T == 't' || T == 'k' ? T + ":" + K : T + ":" + A;
    }

    public enum NodeType
    {
        Source, Battery, Consumer, Lamp, Transmitter, Junction, Terminal, Isolated,
        StubWall, StubRock, StubWater, StubDevice, StubHidden,
        HiddenEnd, HiddenOffmap, HiddenJunction, Tangle
    }

    public sealed class CordNode
    {
        public NodeType Type;
        internal V2 Pos;
        internal Cell Cell;
        internal MachineInfo Machine;
        /// <summary>Stub: unit vector from the walk cell into the buried cell; Face = the cell face.</summary>
        internal V2 Into, Face;
        internal Cell Buried;
        /// <summary>Stub whose buried run ENDS inside the wall/rock: a wall terminal (§8.7.2).</summary>
        public bool WallTerminal;
        /// <summary>Terminal: the open side, and whether it faces a real gap.</summary>
        internal Cell Out;
        public bool Gap;
        /// <summary>GSS pre-release A3: the one cell promoted to cut a closed ring of degree-2 conduit (no device on it). It is
        /// a Terminal in the graph (the oracle's reading) but not an END: the cord closes on itself there, so no frayed end,
        /// limp tail, whip or end readout is drawn for it.</summary>
        public bool Seam;
        /// <summary>Junction: 'x' (4-way) or 't'.</summary>
        public char Cls;
        internal List<Cell> Cells;      // tangle field / blob cells
        public bool IsBlob;

        public bool IsMachine => Type == NodeType.Source || Type == NodeType.Battery || Type == NodeType.Consumer ||
                                 Type == NodeType.Lamp || Type == NodeType.Transmitter;
        public bool IsStub => Type == NodeType.StubWall || Type == NodeType.StubRock || Type == NodeType.StubWater ||
                              Type == NodeType.StubDevice || Type == NodeType.StubHidden;

        /// <summary>Oracle-compatible type name (nodal.py's strings).</summary>
        public string OracleName
        {
            get
            {
                switch (Type)
                {
                    case NodeType.Source: return "source";
                    case NodeType.Battery: return "battery";
                    case NodeType.Consumer: return "consumer";
                    case NodeType.Lamp: return "lamp";
                    case NodeType.Transmitter: return "transmitter";
                    case NodeType.Junction: return "junction";
                    case NodeType.Terminal: return "terminal";
                    case NodeType.Isolated: return "isolated";
                    case NodeType.StubWall: return "stub_wall";
                    case NodeType.StubRock: return "stub_rock";
                    case NodeType.StubWater: return "stub_water";
                    case NodeType.StubDevice: return "stub_device";
                    case NodeType.StubHidden: return "stub_hidden";
                    case NodeType.HiddenEnd: return "hidden_end";
                    case NodeType.HiddenOffmap: return "hidden_offmap";
                    case NodeType.HiddenJunction: return "hidden_junction";
                    default: return "tangle";
                }
            }
        }
    }

    public sealed class CordEdge
    {
        public VId A, B;
        public List<VId> Via = new List<VId>();
        public bool Hidden;
        public List<VId> LoopAt = new List<VId>();
        internal V2 PA, PB;
        internal List<V2> Knots = new List<V2>();

        /// <summary>Every conduit cell on the edge's own chain (for the "connected only" check
        /// and for the per-edge cache key).</summary>
        public IEnumerable<VId> Chain() { yield return A; foreach (var v in Via) yield return v; yield return B; }
    }

    public sealed class CordGraph
    {
        public const int TangleMin = 9;
        public const int SpurMax = 2;

        internal readonly CordWorld World;
        internal readonly HashSet<Cell> Cells = new HashSet<Cell>();
        internal readonly HashSet<Cell> BuriedCells = new HashSet<Cell>();
        internal readonly Dictionary<VId, List<Cell>> Clusters = new Dictionary<VId, List<Cell>>();
        public readonly Dictionary<VId, CordNode> Nodes = new Dictionary<VId, CordNode>();
        public readonly List<CordEdge> Edges = new List<CordEdge>();
        internal readonly List<KeyValuePair<VId, List<Cell>>> SpurKnots = new List<KeyValuePair<VId, List<Cell>>>();
        internal readonly Dictionary<VId, MachineInfo> MachineOf = new Dictionary<VId, MachineInfo>();

        private readonly Dictionary<Cell, VId> owner = new Dictionary<Cell, VId>();
        private readonly Dictionary<VId, List<VId>> adj = new Dictionary<VId, List<VId>>();
        private readonly Dictionary<(VId, VId), Cell> linkCell = new Dictionary<(VId, VId), Cell>();
        private readonly HashSet<VId> keep = new HashSet<VId>();
        private readonly HashSet<VId> ringSeams = new HashSet<VId>();
        private readonly HashSet<Cell> hookCells = new HashSet<Cell>();
        private readonly Dictionary<Cell, List<Cell>> nb = new Dictionary<Cell, List<Cell>>();
        private readonly ulong seed;

        public readonly int tangleMin, spurMax;
        /// <summary>BuildOptions.SlideUnder: machine plug points sit off every cell-edge midpoint (see <see cref="PlugPoint"/>).</summary>
        public readonly bool slideUnder;
        private readonly ICollection<string> straightPlug;

        /// <summary>Does a cord into this machine slide under it (not a lamp, not a drawn connector such as the tap clamp)?</summary>
        internal bool Slides(MachineInfo m) => slideUnder && m != null && m.Kind != MachineKind.Lamp && !m.Foot && !straightPlug.Contains(m.Id ?? "");

        internal static CordGraph Reduce(CordWorld world, ulong seed = 1, int tangleMin = TangleMin, int spurMax = SpurMax, bool slideUnder = true,
                                         ICollection<string> straightPlug = null) =>
            new CordGraph(world, seed, tangleMin, spurMax, slideUnder, straightPlug);

        private CordGraph(CordWorld world, ulong seed, int tangleMin, int spurMax, bool slideUnder, ICollection<string> straightPlug)
        {
            World = world;
            this.slideUnder = slideUnder;
            this.straightPlug = straightPlug ?? (ICollection<string>)new HashSet<string>();
            this.seed = seed;
            this.tangleMin = tangleMin;
            this.spurMax = spurMax;
            foreach (Cell c in world.ConduitCells()) Cells.Add(c);
            foreach (Cell c in Cells)
            {
                var l = new List<Cell>();
                foreach (Cell d in Cell.Dirs4)
                {
                    Cell q = c + d;
                    if (Cells.Contains(q) && (world.LinkAllowed == null || world.LinkAllowed(c, q))) l.Add(q);
                }
                nb[c] = l;
                if (world.IsBuried(c)) BuriedCells.Add(c);
            }
            foreach (MachineInfo m in world.Machines)
                foreach (Cell h in m.Hookups) hookCells.Add(h);

            var walk = new HashSet<Cell>(Cells.Where(c => !BuriedCells.Contains(c)));
            List<List<Cell>> comps = DenseClusters(walk);
            for (int k = 0; k < comps.Count; k++)
            {
                List<Cell> comp = comps[k];
                bool two = comp.Any(c => walk.Contains(c) && walk.Contains(new Cell(c.X + 1, c.Z)) &&
                                         walk.Contains(new Cell(c.X, c.Z + 1)) && walk.Contains(new Cell(c.X + 1, c.Z + 1)));
                char kind;
                if (comp.Count >= tangleMin) kind = 't';
                else if (two) kind = 'k';
                else continue;
                VId v = VId.Cluster(kind, k);
                Clusters[v] = comp;
                foreach (Cell c in comp) owner[c] = v;
            }

            foreach (Cell c in Cells) Adj(Vid(c));
            var sorted = Cells.ToList();
            sorted.Sort();
            foreach (Cell c in sorted)
            {
                foreach (Cell q in nb[c])
                {
                    if (q.CompareTo(c) <= 0) continue;
                    bool bc = BuriedCells.Contains(c), bq = BuriedCells.Contains(q);
                    if (bc == bq)
                        Link(Vid(c), Vid(q), c, q);
                    else
                    {
                        Cell w = bq ? c : q, hid = bq ? q : c;
                        VId s = VId.S(w, hid);
                        Link(Vid(w), s, w, null);
                        Link(s, Vid(hid), null, hid);
                    }
                }
            }
            MergeStubs();
            HookupPick.ChainTransmitters(world.Machines);   // round 3: a transmitter fed through the one it touches gets its cord
            foreach (MachineInfo m in world.Machines)
            {
                VId mv = VId.Mach(m.Id);
                bool any = false;
                foreach (Cell h in m.Hookups)
                {
                    if (!Cells.Contains(h)) continue;
                    any = true;
                    // conduit run inside a wall or rock: the machine's cord comes out of the face nearest it, as any other stub
                    // (a hidden-conduit hookup stays hidden: M3); with no open face left it stays in the wall too
                    if (BuriedCells.Contains(h) && FaceFor(m, h) is VId face)
                    {
                        machineStubs.Add(face);
                        Link(mv, face, null, null);
                        Link(face, Vid(face.B), null, face.B);
                    }
                    else Link(mv, Vid(h), null, h);
                }
                foreach (string other in m.MachineLinks)
                {
                    MachineInfo om = world.Machines.FirstOrDefault(x => x.Id == other);
                    if (om == null) continue;
                    Link(mv, VId.Mach(other), null, null);
                    MachineOf[VId.Mach(other)] = om;   // a machine reached only through a link still needs its node
                    any = true;
                }
                if (any) MachineOf[mv] = m;
            }
            foreach (var kv in adj) kv.Value.Sort();
            foreach (VId v in adj.Keys)
                if (v.T == 'm' || v.T == 's' || v.T == 't' || adj[v].Count != 2) keep.Add(v);
            WalkChains();
            PruneSpurs();
            foreach (VId v in keep) Nodes[v] = Classify(v);
            WallTerminals();
            Endpoints();
            BuildStripLeads();
            CordBuilder.PrepareIncidentIndex(this);
        }

        private readonly HashSet<VId> machineStubs = new HashSet<VId>();

        /// <summary>The stub a machine hooked to buried cell h draws its cord from: the open face of that buried run closest to the
        /// machine, h's own first. A machine standing against the face has no cord to draw, and null keeps it the hidden link.</summary>
        private VId? FaceFor(MachineInfo m, Cell h)
        {
            BlockKind kh = World.BuriedKind(h);
            if (kh != BlockKind.Wall && kh != BlockKind.Rock) return null;
            V2 c = CordBuilder.ArtTarget(m);
            VId? best = null;
            double bd = double.MaxValue;
            foreach (Cell hid in new[] { h }.Concat(BuriedCells.Where(b => b != h && V2.Dist(b.Centre, h.Centre) < 3).OrderBy(b => b)))
            {
                BlockKind k = World.BuriedKind(hid);
                if (k != BlockKind.Wall && k != BlockKind.Rock) continue;
                foreach (Cell dd in Cell.Dirs4)
                {
                    Cell w = hid + dd;
                    if (m.Contains(w)) return null;
                    if (!World.InBounds(w) || World.IsBuried(w)) continue;
                    double d = V2.Dist(w.Centre, c);
                    if (d < bd) { bd = d; best = VId.S(w, hid); }
                }
                if (best != null) break;      // h's own face is the one vanilla's wire went to
            }
            return best;
        }

        private VId Vid(Cell c)
        {
            if (owner.TryGetValue(c, out VId v)) return v;
            return BuriedCells.Contains(c) ? VId.W(c) : VId.C(c);
        }

        private List<VId> Adj(VId v)
        {
            if (!adj.TryGetValue(v, out List<VId> l)) { l = new List<VId>(); adj[v] = l; }
            return l;
        }

        private void Link(VId a, VId b, Cell? ca, Cell? cb)
        {
            if (a == b) return;
            List<VId> la = Adj(a), lb = Adj(b);
            if (!la.Contains(b)) la.Add(b);
            if (!lb.Contains(a)) lb.Add(a);
            if (ca.HasValue && !linkCell.ContainsKey((a, b))) linkCell[(a, b)] = ca.Value;
            if (cb.HasValue && !linkCell.ContainsKey((b, a))) linkCell[(b, a)] = cb.Value;
        }

        // ------------------------------------------------------------------ stub merge (§8.7.3, phase 1b B2)
        /// <summary>Stubs of ONE buried run (same buried component) whose walk cells lie on the same
        /// floor chain within 2 cells (floor-conduit path distance) are one opening: the middle one is
        /// kept, the rest are unlinked, so a run hugging a wall that carries its own buried conduit
        /// shows one hole instead of a comb. Stubs on opposite faces of a wall are never merged (their
        /// walk cells are not floor-connected within 2), so a run through a wall keeps both openings.
        /// Connectivity is unchanged: every dropped stub's walk cell reaches the kept one over floor.</summary>
        private void MergeStubs()
        {
            var stubs = adj.Keys.Where(v => v.T == 's').ToList();
            if (stubs.Count < 2) return;
            stubs.Sort();
            var comp = new Dictionary<Cell, int>();
            int k = 0;
            var buried = BuriedCells.ToList();
            buried.Sort();
            foreach (Cell c in buried)
            {
                if (comp.ContainsKey(c)) continue;
                var st = new Stack<Cell>();
                st.Push(c);
                comp[c] = k;
                while (st.Count > 0)
                {
                    Cell q = st.Pop();
                    foreach (Cell n in nb[q])
                        if (BuriedCells.Contains(n) && !comp.ContainsKey(n)) { comp[n] = k; st.Push(n); }
                }
                k++;
            }
            int Floor2(Cell a, Cell b)
            {
                if (a == b) return 0;
                var seenF = new HashSet<Cell> { a };
                var frontier = new List<Cell> { a };
                for (int d = 1; d <= 2; d++)
                {
                    var nextF = new List<Cell>();
                    foreach (Cell q in frontier)
                        foreach (Cell n in nb[q])
                        {
                            if (BuriedCells.Contains(n) || !seenF.Add(n)) continue;
                            if (n == b) return d;
                            nextF.Add(n);
                        }
                    frontier = nextF;
                }
                return -1;
            }
            var parent = new int[stubs.Count];
            for (int i = 0; i < parent.Length; i++) parent[i] = i;
            int Find(int i) { while (parent[i] != i) i = parent[i] = parent[parent[i]]; return i; }
            for (int i = 0; i < stubs.Count; i++)
                for (int j = i + 1; j < stubs.Count; j++)
                {
                    VId a = stubs[i], b = stubs[j];
                    if (Math.Abs(a.A.X - b.A.X) > 2 || Math.Abs(a.A.Z - b.A.Z) > 2) continue;
                    if (comp[a.B] != comp[b.B]) continue;
                    if (Floor2(a.A, b.A) < 0) continue;
                    parent[Find(i)] = Find(j);
                }
            var groups = new Dictionary<int, List<VId>>();
            for (int i = 0; i < stubs.Count; i++)
            {
                int r = Find(i);
                if (!groups.TryGetValue(r, out List<VId> l)) groups[r] = l = new List<VId>();
                l.Add(stubs[i]);
            }
            foreach (List<VId> grp in groups.Values)
            {
                if (grp.Count < 2) continue;
                grp.Sort();
                VId keepStub = grp[grp.Count / 2];
                foreach (VId s in grp)
                {
                    if (s == keepStub) continue;
                    foreach (VId o in adj[s])
                    {
                        adj[o].Remove(s);
                        linkCell.Remove((o, s));
                        linkCell.Remove((s, o));
                    }
                    adj.Remove(s);
                    MergedStubs++;
                }
            }
        }

        /// <summary>How many stubs MergeStubs folded into a neighbour (probe/SelfTest evidence).</summary>
        public int MergedStubs;

        // ------------------------------------------------------------------ dense fields (§8.7.4)
        private static List<List<Cell>> DenseClusters(HashSet<Cell> cells)
        {
            var d0 = new HashSet<Cell>();
            foreach (Cell c in cells)
            {
                bool block = true;
                for (int a = 0; a <= 1 && block; a++)
                    for (int b = 0; b <= 1; b++)
                        if (!cells.Contains(new Cell(c.X + a, c.Z + b))) { block = false; break; }
                if (block)
                    for (int a = 0; a <= 1; a++)
                        for (int b = 0; b <= 1; b++) d0.Add(new Cell(c.X + a, c.Z + b));
                int n = 0;
                for (int a = -1; a <= 1; a++)
                    for (int b = -1; b <= 1; b++)
                        if (cells.Contains(new Cell(c.X + a, c.Z + b))) n++;
                if (n >= 6) d0.Add(c);
            }
            var dense = new HashSet<Cell>(d0);
            bool grow = true;
            while (grow)
            {
                var add = new List<Cell>();
                foreach (Cell c in cells)
                {
                    if (dense.Contains(c)) continue;
                    int k = 0;
                    foreach (Cell d in Cell.Dirs4) if (dense.Contains(c + d)) k++;
                    if (k >= 2) add.Add(c);
                }
                foreach (Cell c in add) dense.Add(c);
                grow = add.Count > 0;
            }
            foreach (List<Cell> comp in Components(dense, null))
            {
                if (comp.Count < 4) continue;
                int x0 = comp.Min(c => c.X), x1 = comp.Max(c => c.X), z0 = comp.Min(c => c.Z), z1 = comp.Max(c => c.Z);
                var box = new HashSet<Cell>(cells.Where(c => c.X >= x0 && c.X <= x1 && c.Z >= z0 && c.Z <= z1));
                foreach (Cell c in comp) box.Add(c);
                foreach (Cell c in Components(box, comp[0])[0]) dense.Add(c);
            }
            return Components(dense, null);
        }

        private static List<List<Cell>> Components(HashSet<Cell> set, Cell? seedCell)
        {
            var comps = new List<List<Cell>>();
            var seen = new HashSet<Cell>();
            List<Cell> order;
            if (seedCell.HasValue) order = new List<Cell> { seedCell.Value };
            else { order = set.ToList(); order.Sort(); }
            foreach (Cell c in order)
            {
                if (seen.Contains(c)) continue;
                var comp = new List<Cell>();
                var stack = new Stack<Cell>();
                stack.Push(c);
                seen.Add(c);
                while (stack.Count > 0)
                {
                    Cell q = stack.Pop();
                    comp.Add(q);
                    foreach (Cell d in Cell.Dirs4)
                    {
                        Cell n = q + d;
                        if (set.Contains(n) && !seen.Contains(n)) { seen.Add(n); stack.Push(n); }
                    }
                }
                comp.Sort();
                comps.Add(comp);
            }
            return comps;
        }

        // ------------------------------------------------------------------ chains between kept vertices
        private void WalkChains()
        {
            var seen = new HashSet<string>();
            var keepSorted = keep.ToList();
            keepSorted.Sort();
            foreach (VId k in keepSorted) WalkFrom(k, seen);
            var done = new HashSet<VId>(keep);
            foreach (CordEdge e in Edges) foreach (VId v in e.Chain()) done.Add(v);
            var all = adj.Keys.ToList();
            all.Sort();
            foreach (VId v in all)            // closed rings of degree-2 cells: promote one cell
            {
                if (done.Contains(v)) continue;
                keep.Add(v);
                ringSeams.Add(v);
                WalkFrom(v, seen);
                foreach (CordEdge e in Edges) foreach (VId u in e.Chain()) done.Add(u);
            }
        }

        private void WalkFrom(VId k, HashSet<string> seen)
        {
            foreach (VId n in adj[k])
            {
                var path = new List<VId> { k, n };
                while (!keep.Contains(path[path.Count - 1]))
                {
                    List<VId> two = adj[path[path.Count - 1]];
                    VId prev = path[path.Count - 2];
                    path.Add(two[0] != prev ? two[0] : two[1]);
                }
                string key;
                if (path.Count == 2)
                {
                    var ends = new List<string> { path[0].ToString(), path[1].ToString() };
                    ends.Sort(StringComparer.Ordinal);
                    key = "direct|" + ends[0] + "|" + ends[1];
                }
                else
                {
                    var steps = new List<string>();
                    for (int i = 0; i < path.Count - 1; i++)
                    {
                        string a = path[i].ToString(), b = path[i + 1].ToString();
                        steps.Add(string.CompareOrdinal(a, b) < 0 ? a + "~" + b : b + "~" + a);
                    }
                    steps.Sort(StringComparer.Ordinal);
                    key = string.Join("|", steps.Distinct());
                }
                if (!seen.Add(key)) continue;
                var e = new CordEdge { A = path[0], B = path[path.Count - 1], Hidden = path.Any(v => v.T == 'w') };
                for (int i = 1; i < path.Count - 1; i++) e.Via.Add(path[i]);
                Edges.Add(e);
            }
        }

        public int Deg(VId v)
        {
            int d = 0;
            foreach (CordEdge e in Edges) d += (e.A == v ? 1 : 0) + (e.B == v ? 1 : 0);
            return d;
        }

        private int NetDeg(Cell c) => nb.TryGetValue(c, out List<Cell> l) ? l.Count : 0;

        private Cell OutDir(Cell c)
        {
            Cell n = nb[c][0];
            return new Cell(c.X - n.X, c.Z - n.Z);
        }

        /// <summary>render.Net.end_class, only the "break" answer matters: a dead end facing another conduit cell across a gap of up to 5 cells.
        /// Was 3 reach, which a blast's gap of 3 cells beat: both short stumps of a real cut were pruned as needless spurs and the cut drew no ends at all.</summary>
        private bool FacesGap(Cell c)
        {
            if (NetDeg(c) != 1 || hookCells.Contains(c)) return false;
            Cell o = OutDir(c);
            for (int k = 1; k <= 6; k++)
            {
                var q = new Cell(c.X + o.X * k, c.Z + o.Z * k);
                if (Cells.Contains(q)) return true;
                if (!World.InBounds(q)) break;
            }
            return false;
        }

        // ------------------------------------------------------------------ needless spurs (§8.7.5)
        private void PruneSpurs()
        {
            bool changed = true;
            while (changed)
            {
                changed = false;
                foreach (CordEdge e in Edges.ToList())
                {
                    for (int side = 0; side < 2 && !changed; side++)
                    {
                        VId end = side == 0 ? e.A : e.B, other = side == 0 ? e.B : e.A;
                        if (end.T != 'c' || Deg(end) != 1 || e.Hidden) continue;
                        Cell c = end.A;
                        if (hookCells.Contains(c) || FacesGap(c)) continue;
                        if (e.Via.Count + 1 > spurMax || !(other.T == 'c' || other.T == 'k' || other.T == 't') || Deg(other) < 3)
                            continue;
                        Edges.Remove(e);
                        keep.Remove(end);
                        var spur = new List<Cell> { end.A };
                        spur.AddRange(e.Via.Where(v => v.T == 'c').Select(v => v.A));
                        SpurKnots.Add(new KeyValuePair<VId, List<Cell>>(other, spur));
                        if (Deg(other) == 2 && (other.T == 'c' || other.T == 'k'))
                        {
                            var two = Edges.Where(x => x.A == other || x.B == other).ToList();
                            if (two.Count == 2 && !two[0].Hidden && !two[1].Hidden)
                            {
                                CordEdge e1 = two[0], e2 = two[1];
                                var s1 = new List<VId>();
                                if (e1.A == other) { s1.Add(e1.B); s1.AddRange(Enumerable.Reverse(e1.Via)); }
                                else { s1.Add(e1.A); s1.AddRange(e1.Via); }
                                var s2 = new List<VId>();
                                if (e2.A == other) { s2.AddRange(e2.Via); s2.Add(e2.B); }
                                else { s2.AddRange(Enumerable.Reverse(e2.Via)); s2.Add(e2.A); }
                                Edges.Remove(e1);
                                Edges.Remove(e2);
                                var merged = new CordEdge { A = s1[0], B = s2[s2.Count - 1], Hidden = false };
                                merged.Via.AddRange(s1.Skip(1));
                                merged.Via.Add(other);
                                merged.Via.AddRange(s2.Take(s2.Count - 1));
                                merged.LoopAt.AddRange(e1.LoopAt);
                                merged.LoopAt.Add(other);
                                merged.LoopAt.AddRange(e2.LoopAt);
                                Edges.Add(merged);
                                keep.Remove(other);
                            }
                        }
                        changed = true;
                    }
                    if (changed) break;
                }
            }
        }

        // ------------------------------------------------------------------ classification (§8.2.1)
        private CordNode Classify(VId v)
        {
            int d = Deg(v);
            if (v.T == 'm')
            {
                MachineInfo m = MachineOf[v];
                NodeType t = m.Kind == MachineKind.Source ? NodeType.Source :
                             m.Kind == MachineKind.Battery ? NodeType.Battery :
                             m.Kind == MachineKind.Lamp ? NodeType.Lamp :
                             m.Kind == MachineKind.Transmitter ? NodeType.Transmitter : NodeType.Consumer;
                Cell hook = m.Hookups.Count > 0 ? m.Hookups[0] : new Cell(m.X0, m.Z0);
                return new CordNode { Type = t, Pos = MachinePlugPoint(World, m, hook, Slides(m)), Cell = hook, Machine = m };
            }
            if (v.T == 's')
            {
                Cell w = v.A, hid = v.B;
                var into = new V2(hid.X - w.X, hid.Z - w.Z);
                BlockKind k = World.BuriedKind(hid);
                NodeType t = k == BlockKind.Rock ? NodeType.StubRock : k == BlockKind.Water ? NodeType.StubWater :
                             k == BlockKind.Device ? NodeType.StubDevice : k == BlockKind.Hidden ? NodeType.StubHidden :
                             NodeType.StubWall;
                // a machine's own stub has no conduit in its walk cell: it stands for the buried cell, the one on the net
                return new CordNode { Type = t, Pos = w.Centre + into * 0.44, Cell = Cells.Contains(w) ? w : hid, Into = into, Face = w.Centre + into * 0.5, Buried = hid };
            }
            if (v.T == 't' || v.T == 'k')
            {
                List<Cell> comp = Clusters[v];
                V2 mean = Mean(comp);
                if (v.T == 't')
                    return new CordNode { Type = NodeType.Tangle, Pos = mean, Cell = comp[comp.Count / 2], Cells = comp };
                return new CordNode { Type = NodeType.Junction, Pos = mean, Cell = comp[0], Cls = d >= 4 ? 'x' : 't', Cells = comp, IsBlob = true };
            }
            Cell c = v.A;
            if (v.T == 'w')
            {
                bool offmap = Cell.Dirs4.Any(dd => !World.InBounds(c + dd));
                NodeType t = offmap && d <= 1 ? NodeType.HiddenOffmap : d >= 3 ? NodeType.HiddenJunction : NodeType.HiddenEnd;
                return new CordNode { Type = t, Pos = c.Centre, Cell = c };
            }
            if (d >= 3) return new CordNode { Type = NodeType.Junction, Pos = Knot(c), Cell = c, Cls = d >= 4 ? 'x' : 't' };
            if (d == 0) return new CordNode { Type = NodeType.Isolated, Pos = c.Centre, Cell = c };
            if (d == 2 && ringSeams.Contains(v)) return new CordNode { Type = NodeType.Terminal, Pos = c.Centre, Cell = c, Seam = true };
            V2 o = NetDeg(c) == 1 ? new V2(OutDir(c).X, OutDir(c).Z) : Away(v);
            return new CordNode
            {
                Type = NodeType.Terminal, Pos = c.Centre + o * 0.36, Cell = c,
                Out = new Cell((int)Math.Round(o.X), (int)Math.Round(o.Z)), Gap = FacesGap(c)
            };
        }

        private static V2 Mean(List<Cell> cells)
        {
            double x = 0, z = 0;
            foreach (Cell c in cells) { x += c.X + 0.5; z += c.Z + 0.5; }
            return new V2(x / cells.Count, z / cells.Count);
        }

        /// <summary>A junction sits on its cell centre: the junction art's arms run along the conduit
        /// axes, so a jittered centre put two neighbouring junctions' arms out of line (polish pass
        /// 2026-10-02; the old +-0.08 jitter predates the real art).</summary>
        private V2 Knot(Cell c) => c.Centre;

        private V2 Away(VId v)
        {
            CordEdge e = Edges.First(x => x.A == v || x.B == v);
            VId o = e.A == v ? e.B : e.A;
            VId nxt = e.Via.Count > 0 ? (e.A == v ? e.Via[0] : e.Via[e.Via.Count - 1]) : o;
            V2 p = nxt.IsCellish ? nxt.A.Centre : v.A.Centre + new V2(1, 0);
            return (v.A.Centre - p).Norm();
        }

        /// <summary>Where a cord enters a machine: the footprint point nearest the hookup, just outside. With
        /// <paramref name="slide"/> (CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT, owner 2026-10-23: "the electrical plug is shown going
        /// into a pipe slot. Weird. It should favor diagonal approaches sliding underneath"): the point moves along that side
        /// to <see cref="SlideFrac"/> of the hookup's cell, never a cell-edge midpoint, where pipe and hose ports sit; the
        /// cord then arrives at a diagonal (<see cref="SlideArrive"/>) and runs on under the art to the centroid.</summary>
        internal static V2 PlugPoint(MachineInfo m, Cell hookup, bool slide = false)
        {
            if (BaseLampApproach(m)) return CordBuilder.LampEntry(m, hookup.Centre);
            if (m.Kind == MachineKind.Lamp) return new V2(m.X0 + 0.5, m.Z0 + 1.02);
            if (m.Foot) return new V2(m.X0 + m.W / 2.0, m.Z0 - 0.08);   // a pole or mast: in from below, under its foot, whatever side vanilla hooked
            double hx = hookup.X + 0.5, hz = hookup.Z + 0.5;
            double x0 = m.X0, z0 = m.Z0, x1 = m.X0 + m.W, z1 = m.Z0 + m.H;
            double qx = Geo.Clamp(hx, x0 + 0.25, x1 - 0.25), qz = Geo.Clamp(hz, z0 + 0.25, z1 - 0.25);
            bool sideX = false, sideZ = false;
            if (hx >= x1) { qx = x1 + 0.08; sideX = true; }
            else if (hx <= x0) { qx = x0 - 0.08; sideX = true; }
            else if (hz >= z1) { qz = z1 + 0.08; sideZ = true; }
            else if (hz <= z0) { qz = z0 - 0.08; sideZ = true; }
            if (slide && sideZ) qx = SlideAlong(hx, x0, x1, m);
            else if (slide && sideX) qz = SlideAlong(hz, z0, z1, m);
            return new V2(qx, qz);
        }

        /// <summary>A machine approach must not put the planner's endpoint in an adjacent wall: A* permits its endpoint cell,
        /// and that cell is not a dive. Prefer the existing plug point, then an open side nearest the hookup. With no open
        /// exterior approach, end under the machine itself so surrounding barriers remain intermediate dive cells.</summary>
        internal static V2 MachinePlugPoint(CordWorld w, MachineInfo m, Cell hookup, bool slide)
        {
            V2 preferred = BaseLampApproach(m)
                ? CordBuilder.LampEntryOnFloor(w, m, hookup.Centre)
                : PlugPoint(m, hookup, slide);
            if (w.IsWalkable(preferred.Floor) || m.Contains(preferred.Floor)) return preferred;
            int hx = Math.Max(m.X0, Math.Min(m.X0 + m.W - 1, hookup.X));
            int hz = Math.Max(m.Z0, Math.Min(m.Z0 + m.H - 1, hookup.Z));
            V2 best = default(V2);
            double nearest = double.MaxValue;
            foreach (Cell side in new[]
            {
                new Cell(hx, m.Z0 + m.H),
                new Cell(m.X0 + m.W, hz),
                new Cell(hx, m.Z0 - 1),
                new Cell(m.X0 - 1, hz)
            })
            {
                V2 q = m.Kind == MachineKind.Lamp && m.W == 1 && m.H == 1
                    ? CordBuilder.LampEntry(m, side.Centre)
                    : PlugPoint(m, side, slide);
                if (!w.IsWalkable(q.Floor)) continue;
                double d = V2.Dist(q, hookup.Centre);
                if (d < nearest) { nearest = d; best = q; }
            }
            if (nearest < double.MaxValue) return best;
            return m.Foot
                ? new V2(m.X0 + m.W / 2.0, m.Z0 + CordBuilder.FootTuck)
                : CordBuilder.ArtTarget(m);
        }

        /// <summary>How far into its cell (along the side) a sliding plug point sits: well clear of the 0.5 midpoint.</summary>
        public const double SlideFrac = 0.18;

        /// <summary>The along-side coordinate of a sliding plug point: in the footprint cell facing the hookup, SlideFrac in from
        /// the cell's OUTER corner side (away from the centroid), so the diagonal arrival heads in toward the middle; a cell
        /// centred on the centroid picks its side by the footprint's position (deterministic).</summary>
        private static double SlideAlong(double h, double lo, double hi, MachineInfo m)
        {
            double k = Math.Floor(Geo.Clamp(h, lo + 0.01, hi - 0.01));
            double mid = (lo + hi) / 2, cc = k + 0.5;
            bool low = cc < mid - 1e-6 || (Math.Abs(cc - mid) <= 1e-6 && ((m.X0 + m.Z0) & 1) == 0);
            return low ? k + SlideFrac : k + 1 - SlideFrac;
        }

        /// <summary>A one-cell lamp base needs a direct approach. Ordinary machines retain their diagonal flange entry.</summary>
        internal static bool BaseLampApproach(MachineInfo m) =>
            m != null && m.W == 1 && m.H == 1 && m.BaseDz != 0 && !m.Foot && !m.HasHome;

        /// <summary>Base lamps arrive horizontally at the foot or radially upward
        /// through the bottom; ordinary sliding plugs retain their diagonal under the flange.</summary>
        internal static V2 SlideArrive(MachineInfo m, V2 tip, V2 into)
        {
            if (BaseLampApproach(m))
            {
                V2 c = CordBuilder.ArtTarget(m);
                if (tip.Z < m.Z0)
                    return (c - tip).Norm();
                return new V2(tip.X < c.X ? 1 : -1, 0);
            }
            double along = into.X != 0 ? tip.Z : tip.X;
            double f = along - Math.Floor(along);
            double s = f < 0.5 ? 1 : -1;
            V2 tan = into.X != 0 ? new V2(0, s) : new V2(s, 0);
            return (into + tan).Norm();
        }

        private void WallTerminals()
        {
            foreach (CordEdge e in Edges)
            {
                if (!e.Hidden) continue;
                for (int side = 0; side < 2; side++)
                {
                    VId s = side == 0 ? e.A : e.B, h = side == 0 ? e.B : e.A;
                    if (s.T == 's' && !machineStubs.Contains(s) && Nodes.TryGetValue(h, out CordNode hn) && hn.Type == NodeType.HiddenEnd)
                        Nodes[s].WallTerminal = true;
                }
            }
        }

        private void Endpoints()
        {
            foreach (CordEdge e in Edges)
            {
                e.PA = EndPos(e, true);
                e.PB = EndPos(e, false);
                var loops = new HashSet<VId>(e.LoopAt);
                foreach (VId v in e.Via)
                    if (loops.Contains(v) || v.T == 'k') e.Knots.Add(NodePos(v));
            }
        }

        private V2 EndPos(CordEdge e, bool atA)
        {
            VId v = atA ? e.A : e.B;
            CordNode nd = Nodes[v];
            V2 p = nd.Pos;
            if (v.T == 't')
            {
                VId nxt = e.Via.Count > 0 ? (atA ? e.Via[0] : e.Via[e.Via.Count - 1]) : (atA ? e.B : e.A);
                // the machine edge also connects to the tangle's own cell (link_cell (vid(h), m) = h)
                if (linkCell.TryGetValue((v, nxt), out Cell lc))
                {
                    V2 toward = nxt.IsCellish ? new V2(nxt.A.X - lc.X, nxt.A.Z - lc.Z) : new V2(0, 0);
                    p = lc.Centre + toward * 0.3;
                }
            }
            // a machine with several hookups: plug toward THIS edge's hookup cell
            if (v.T == 'm' && nd.Machine.Hookups.Count > 1)
            {
                VId nxt = e.Via.Count > 0 ? (atA ? e.Via[0] : e.Via[e.Via.Count - 1]) : (atA ? e.B : e.A);
                if (linkCell.TryGetValue((nxt, v), out Cell hc)) p = MachinePlugPoint(World, nd.Machine, hc, Slides(nd.Machine));
            }
            return p;
        }

        internal V2 NodePos(VId v)
        {
            if (v.T == 'k') return Mean(Clusters[v]);
            if (v.IsCellish) return v.A.Centre;
            return Nodes[v].Pos;
        }

        public IEnumerable<CordEdge> CordEdges() => Edges.Where(e => !e.Hidden);

        private List<KeyValuePair<string, string>> hiddenLinks;

        /// <summary>The cell tokens each hidden edge joins, as a laid piece's net tokens name them; tabled once per graph.</summary>
        internal List<KeyValuePair<string, string>> HiddenLinks
        {
            get
            {
                if (hiddenLinks == null)
                {
                    var l = new List<KeyValuePair<string, string>>();
                    foreach (CordEdge e in Edges)
                        if (e.Hidden && Nodes.TryGetValue(e.A, out CordNode a) && Nodes.TryGetValue(e.B, out CordNode b))
                            l.Add(new KeyValuePair<string, string>(a.Cell.X + "," + a.Cell.Z, b.Cell.X + "," + b.Cell.Z));
                    hiddenLinks = l;
                }
                return hiddenLinks;
            }
        }

        private Dictionary<VId, HashSet<Cell>> armTable;

        /// <summary>The cardinal directions a node's cords leave it in, tabled once per graph: posing a junction reads this for
        /// each of its cords, on the lay worker and the frame alike, and a whole-graph walk per read was quadratic.</summary>
        internal HashSet<Cell> ArmsOf(VId v)
        {
            Dictionary<VId, HashSet<Cell>> t = System.Threading.Volatile.Read(ref armTable);
            if (t == null)
            {
                t = new Dictionary<VId, HashSet<Cell>>();
                void Arm(VId n, CordEdge e, bool atA)
                {
                    if (Nodes[n].Type != NodeType.Junction) return;
                    if (!t.TryGetValue(n, out HashSet<Cell> s)) t[n] = s = new HashSet<Cell>();
                    V2 a = CordBuilder.ArmDir(this, e, atA);
                    s.Add(new Cell((int)a.X, (int)a.Z));
                }
                foreach (CordEdge e in CordEdges()) { Arm(e.A, e, true); Arm(e.B, e, false); }
                System.Threading.Volatile.Write(ref armTable, t);
            }
            return t.TryGetValue(v, out HashSet<Cell> arms) ? arms : new HashSet<Cell>();
        }

        private Dictionary<long, List<KeyValuePair<VId, CordNode>>> nodeGrid;
        private const int NodeGridSize = 8;

        /// <summary>The graph's nodes that are neither a machine nor a seam (boxes, strips, heaps, cut ends, plates) with their cell in the rectangle, in a fixed order: what a cord laid
        /// again keeps off (CordBuilder.OtherBoxes) and what goes into its edge's key, so a box that appears beside a cord re-lays it.</summary>
        internal List<KeyValuePair<VId, CordNode>> NodesNear(int x0, int z0, int x1, int z1)
        {
            Dictionary<long, List<KeyValuePair<VId, CordNode>>> t = System.Threading.Volatile.Read(ref nodeGrid);
            if (t == null)
            {
                t = new Dictionary<long, List<KeyValuePair<VId, CordNode>>>();
                foreach (KeyValuePair<VId, CordNode> kv in Nodes.OrderBy(kv => kv.Key.ToString(), StringComparer.Ordinal))
                {
                    if (kv.Value.IsMachine || kv.Value.Seam) continue;
                    Cell c = kv.Value.Cell;
                    long k = ((long)Math.Floor(c.X / (double)NodeGridSize) << 32) ^ (uint)(int)Math.Floor(c.Z / (double)NodeGridSize);
                    if (!t.TryGetValue(k, out List<KeyValuePair<VId, CordNode>> l)) t[k] = l = new List<KeyValuePair<VId, CordNode>>();
                    l.Add(kv);
                }
                System.Threading.Volatile.Write(ref nodeGrid, t);
            }
            var o = new List<KeyValuePair<VId, CordNode>>();
            for (int gx = (int)Math.Floor(x0 / (double)NodeGridSize); gx <= (int)Math.Floor(x1 / (double)NodeGridSize); gx++)
                for (int gz = (int)Math.Floor(z0 / (double)NodeGridSize); gz <= (int)Math.Floor(z1 / (double)NodeGridSize); gz++)
                    if (t.TryGetValue(((long)gx << 32) ^ (uint)gz, out List<KeyValuePair<VId, CordNode>> l))
                        foreach (KeyValuePair<VId, CordNode> kv in l)
                        {
                            Cell c = kv.Value.Cell;
                            if (c.X >= x0 && c.X <= x1 && c.Z >= z0 && c.Z <= z1) o.Add(kv);
                        }
            return o;
        }

        private Dictionary<VId, HashSet<Cell>> machineArmTable;
        /// <summary>How far a machine's plug may be from a junction for the machine to count as right beside it, cells.</summary>
        public const double BesideMachine = 1.6;

        /// <summary>The arms of a junction whose cord is a short lead into a machine right beside it.</summary>
        internal HashSet<Cell> MachineArmsOf(VId v)
        {
            Dictionary<VId, HashSet<Cell>> t = System.Threading.Volatile.Read(ref machineArmTable);
            if (t == null)
            {
                t = new Dictionary<VId, HashSet<Cell>>();
                void Arm(VId n, VId other, CordEdge e, bool atA)
                {
                    if (Nodes[n].Type != NodeType.Junction || !Nodes[other].IsMachine) return;
                    if (V2.Dist(Nodes[n].Pos, atA ? e.PB : e.PA) > BesideMachine) return;
                    if (!t.TryGetValue(n, out HashSet<Cell> s)) t[n] = s = new HashSet<Cell>();
                    V2 a = CordBuilder.ArmDir(this, e, atA);
                    s.Add(new Cell((int)a.X, (int)a.Z));
                }
                foreach (CordEdge e in CordEdges()) { Arm(e.A, e.B, e, true); Arm(e.B, e.A, e, false); }
                System.Threading.Volatile.Write(ref machineArmTable, t);
            }
            return t.TryGetValue(v, out HashSet<Cell> arms) ? arms : NoArms;
        }
        private static readonly HashSet<Cell> NoArms = new HashSet<Cell>();

        private Dictionary<VId, HashSet<Cell>> wallArmTable;
        /// <summary>How far a wall or rock face may be from a junction for the conduit to count as going into the wall right beside it, cells.</summary>
        public const double BesideWall = 1.0;

        /// <summary>The arms of a junction whose cord is a short hop into a wall or rock face right beside it.</summary>
        internal HashSet<Cell> WallArmsOf(VId v)
        {
            Dictionary<VId, HashSet<Cell>> t = System.Threading.Volatile.Read(ref wallArmTable);
            if (t == null)
            {
                t = new Dictionary<VId, HashSet<Cell>>();
                void Arm(VId n, VId other, CordEdge e, bool atA)
                {
                    NodeType o = Nodes[other].Type;
                    if (Nodes[n].Type != NodeType.Junction || (o != NodeType.StubWall && o != NodeType.StubRock)) return;
                    if (V2.Dist(Nodes[n].Pos, atA ? e.PB : e.PA) > BesideWall) return;
                    if (!t.TryGetValue(n, out HashSet<Cell> s)) t[n] = s = new HashSet<Cell>();
                    V2 a = CordBuilder.ArmDir(this, e, atA);
                    s.Add(new Cell((int)a.X, (int)a.Z));
                }
                foreach (CordEdge e in CordEdges()) { Arm(e.A, e.B, e, true); Arm(e.B, e.A, e, false); }
                System.Threading.Volatile.Write(ref wallArmTable, t);
            }
            return t.TryGetValue(v, out HashSet<Cell> arms) ? arms : NoArms;
        }

        private readonly Dictionary<VId, CordEdge> stripLeadTable = new Dictionary<VId, CordEdge>();

        /// <summary>A strip's upstream edge: an adjacent uncut wall outlet first, otherwise toward a supply or
        /// uncut wall/rock outlet by graph distance. Equal candidates use deterministic edge order.
        /// Device branches never supply a strip. Built once before the graph is published.</summary>
        internal CordEdge StripLeadOf(VId v) => stripLeadTable.TryGetValue(v, out CordEdge lead) ? lead : null;

        private void BuildStripLeads()
        {
                var links = new Dictionary<VId, List<VId>>();
                foreach (VId n in Nodes.Keys) links[n] = new List<VId>();
                foreach (CordEdge e in Edges)
                {
                    links[e.A].Add(e.B);
                    links[e.B].Add(e.A);
                }
                var distance = new Dictionary<VId, int>();
                var queue = new Queue<VId>();
                foreach (var kv in Nodes.OrderBy(kv => kv.Key))
                {
                    CordNode nd = kv.Value;
                    bool supply = nd.Type == NodeType.Source || nd.Type == NodeType.Battery || nd.Type == NodeType.Transmitter;
                    bool outlet = !nd.WallTerminal && (nd.Type == NodeType.StubWall || nd.Type == NodeType.StubRock);
                    if (!supply && !outlet) continue;
                    distance[kv.Key] = 0;
                    queue.Enqueue(kv.Key);
                }
                while (queue.Count > 0)
                {
                    VId n = queue.Dequeue();
                    foreach (VId other in links[n])
                    {
                        if (distance.ContainsKey(other)) continue;
                        distance[other] = distance[n] + 1;
                        queue.Enqueue(other);
                    }
                }
                Dictionary<VId, CordEdge> t = stripLeadTable;
                var best = new Dictionary<VId, (int Priority, int Distance)>();
                void Pick(VId n, VId other, CordEdge e)
                {
                    if (n == other || Nodes[n].Type != NodeType.Junction) return;
                    CordNode far = Nodes[other];
                    NodeType kind = far.Type;
                    if (kind == NodeType.Consumer || kind == NodeType.Lamp) return;
                    if (!distance.TryGetValue(other, out int d)) return;
                    bool adjacentWall = kind == NodeType.StubWall && !far.WallTerminal
                        && V2.Dist(Nodes[n].Pos, e.A == n ? e.PB : e.PA) <= BesideWall;
                    int priority = adjacentWall ? 0 : 1;
                    if (best.TryGetValue(n, out var old)
                        && (priority > old.Priority || (priority == old.Priority && d >= old.Distance))) return;
                    best[n] = (priority, d);
                    t[n] = e;
                }
                // Pick retains the first equal-ranked candidate; make that order explicit,
                // including parallel edges whose endpoint pair is the same.
                foreach (CordEdge e in CordEdges().OrderBy(e => e.A).ThenBy(e => e.B)
                    .ThenBy(e => string.Join(";", e.Via), StringComparer.Ordinal))
                {
                    Pick(e.A, e.B, e);
                    Pick(e.B, e.A, e);
                }
        }

        /// <summary>The conduit cell a node stands for (oracle's node["cell"]).</summary>
        internal Cell CellOf(VId v) => Nodes[v].Cell;
    }
}
