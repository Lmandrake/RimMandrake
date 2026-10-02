// Messy Conduit core: Verse-free (see CordMath.cs header).
// Port of nodal.NodeGraph (src/RimMandrake/Utils/mockups/messy_conduit/nodal.py), design §8.2.2:
// conduit cells -> node graph (machines, junctions, terminals, stubs, tangles), needless spurs pruned.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.MessyConduit.Core
{
    /// <summary>Vertex id. T: 'c' floor conduit cell, 'w' buried conduit cell, 's' stub (A = walk
    /// cell, B = buried cell), 'm' machine (M = id), 't' tangle, 'k' small dense blob (K = index).</summary>
    public struct VId : IEquatable<VId>, IComparable<VId>
    {
        public readonly char T;
        public readonly Cell A, B;
        public readonly string M;
        public readonly int K;

        private VId(char t, Cell a, Cell b, string m, int k) { T = t; A = a; B = b; M = m; K = k; }
        public static VId C(Cell c) => new VId('c', c, default(Cell), null, 0);
        public static VId W(Cell c) => new VId('w', c, default(Cell), null, 0);
        public static VId S(Cell walk, Cell buried) => new VId('s', walk, buried, null, 0);
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
        public V2 Pos;
        public Cell Cell;
        public MachineInfo Machine;
        /// <summary>Stub: unit vector from the walk cell into the buried cell; Face = the cell face.</summary>
        public V2 Into, Face;
        public Cell Buried;
        /// <summary>Stub whose buried run ENDS inside the wall/rock: a wall terminal (§8.7.2).</summary>
        public bool WallTerminal;
        /// <summary>Terminal: the open side, and whether it faces a real gap.</summary>
        public Cell Out;
        public bool Gap;
        /// <summary>Junction: 'x' (4-way) or 't'.</summary>
        public char Cls;
        public List<Cell> Cells;      // tangle field / blob cells
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
        public V2 PA, PB;
        public List<V2> Knots = new List<V2>();

        /// <summary>Every conduit cell on the edge's own chain (for the "connected only" check
        /// and for the per-edge cache key).</summary>
        public IEnumerable<VId> Chain() { yield return A; foreach (var v in Via) yield return v; yield return B; }
    }

    public sealed class CordGraph
    {
        public const int TangleMin = 9;
        public const int SpurMax = 2;

        public readonly CordWorld World;
        public readonly HashSet<Cell> Cells = new HashSet<Cell>();
        public readonly HashSet<Cell> BuriedCells = new HashSet<Cell>();
        public readonly Dictionary<VId, List<Cell>> Clusters = new Dictionary<VId, List<Cell>>();
        public readonly Dictionary<VId, CordNode> Nodes = new Dictionary<VId, CordNode>();
        public readonly List<CordEdge> Edges = new List<CordEdge>();
        public readonly List<KeyValuePair<VId, List<Cell>>> SpurKnots = new List<KeyValuePair<VId, List<Cell>>>();
        public readonly Dictionary<VId, MachineInfo> MachineOf = new Dictionary<VId, MachineInfo>();

        private readonly Dictionary<Cell, VId> owner = new Dictionary<Cell, VId>();
        private readonly Dictionary<VId, List<VId>> adj = new Dictionary<VId, List<VId>>();
        private readonly Dictionary<(VId, VId), Cell> linkCell = new Dictionary<(VId, VId), Cell>();
        private readonly HashSet<VId> keep = new HashSet<VId>();
        private readonly HashSet<Cell> hookCells = new HashSet<Cell>();
        private readonly Dictionary<Cell, List<Cell>> nb = new Dictionary<Cell, List<Cell>>();
        private readonly ulong seed;

        public readonly int tangleMin, spurMax;

        public static CordGraph Reduce(CordWorld world, ulong seed = 1, int tangleMin = TangleMin, int spurMax = SpurMax) =>
            new CordGraph(world, seed, tangleMin, spurMax);

        private CordGraph(CordWorld world, ulong seed, int tangleMin, int spurMax)
        {
            World = world;
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
            foreach (MachineInfo m in world.Machines)
            {
                VId mv = VId.Mach(m.Id);
                bool any = false;
                foreach (Cell h in m.Hookups)
                    if (Cells.Contains(h)) { Link(mv, Vid(h), null, h); any = true; }
                foreach (string other in m.MachineLinks)
                    if (world.Machines.Any(x => x.Id == other)) { Link(mv, VId.Mach(other), null, null); any = true; }
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

        /// <summary>render.Net.end_class, only the "break" answer matters: a dead end facing
        /// another conduit cell within 3 cells across a gap.</summary>
        private bool FacesGap(Cell c)
        {
            if (NetDeg(c) != 1 || hookCells.Contains(c)) return false;
            Cell o = OutDir(c);
            for (int k = 1; k <= 3; k++)
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
                return new CordNode { Type = t, Pos = PlugPoint(m, hook), Cell = hook, Machine = m };
            }
            if (v.T == 's')
            {
                Cell w = v.A, hid = v.B;
                var into = new V2(hid.X - w.X, hid.Z - w.Z);
                BlockKind k = World.BuriedKind(hid);
                NodeType t = k == BlockKind.Rock ? NodeType.StubRock : k == BlockKind.Water ? NodeType.StubWater :
                             k == BlockKind.Device ? NodeType.StubDevice : k == BlockKind.Hidden ? NodeType.StubHidden :
                             NodeType.StubWall;
                return new CordNode { Type = t, Pos = w.Centre + into * 0.44, Cell = w, Into = into, Face = w.Centre + into * 0.5, Buried = hid };
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

        private V2 Knot(Cell c)
        {
            CordRng r = CordRng.Of(seed, "knot", c.X, c.Z);
            return new V2(c.X + 0.5 + r.Range(-0.08, 0.08), c.Z + 0.5 + r.Range(-0.08, 0.08));
        }

        private V2 Away(VId v)
        {
            CordEdge e = Edges.First(x => x.A == v || x.B == v);
            VId o = e.A == v ? e.B : e.A;
            VId nxt = e.Via.Count > 0 ? (e.A == v ? e.Via[0] : e.Via[e.Via.Count - 1]) : o;
            V2 p = nxt.IsCellish ? nxt.A.Centre : v.A.Centre + new V2(1, 0);
            return (v.A.Centre - p).Norm();
        }

        /// <summary>Where a cord enters a machine: the footprint point nearest the hookup, just outside.</summary>
        public static V2 PlugPoint(MachineInfo m, Cell hookup)
        {
            if (m.Kind == MachineKind.Lamp) return new V2(m.X0 + 0.5, m.Z0 + 1.02);
            double hx = hookup.X + 0.5, hz = hookup.Z + 0.5;
            double x0 = m.X0, z0 = m.Z0, x1 = m.X0 + m.W, z1 = m.Z0 + m.H;
            double qx = Geo.Clamp(hx, x0 + 0.25, x1 - 0.25), qz = Geo.Clamp(hz, z0 + 0.25, z1 - 0.25);
            if (hx >= x1) qx = x1 + 0.08;
            else if (hx <= x0) qx = x0 - 0.08;
            else if (hz >= z1) qz = z1 + 0.08;
            else if (hz <= z0) qz = z0 - 0.08;
            return new V2(qx, qz);
        }

        private void WallTerminals()
        {
            foreach (CordEdge e in Edges)
            {
                if (!e.Hidden) continue;
                for (int side = 0; side < 2; side++)
                {
                    VId s = side == 0 ? e.A : e.B, h = side == 0 ? e.B : e.A;
                    if (s.T == 's' && Nodes.TryGetValue(h, out CordNode hn) && hn.Type == NodeType.HiddenEnd)
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
                if (linkCell.TryGetValue((nxt, v), out Cell hc)) p = PlugPoint(nd.Machine, hc);
            }
            return p;
        }

        public V2 NodePos(VId v)
        {
            if (v.T == 'k') return Mean(Clusters[v]);
            if (v.IsCellish) return v.A.Centre;
            return Nodes[v].Pos;
        }

        public IEnumerable<CordEdge> CordEdges() => Edges.Where(e => !e.Hidden);

        /// <summary>The conduit cell a node stands for (oracle's node["cell"]).</summary>
        public Cell CellOf(VId v) => Nodes[v].Cell;
    }
}
