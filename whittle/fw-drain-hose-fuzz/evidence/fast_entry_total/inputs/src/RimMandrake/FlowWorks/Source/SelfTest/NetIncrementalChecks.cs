// LIQUIDNET_REBUILD_SHRINK_TO_AFFECTED (design/RimMandrake/hose_wire_algorithms_advisory_2026-10-28.md §4 #7): a topology bump
// rebuilds only the components the change touched. Asserted on the PRODUCTION kernel (../Machinery/RM_LiquidNetKernel.cs):
//   - every component's BFS tree hangs from a canonical root, so the tree (and every hose route read from it) does not depend
//     on which member asked first: an incremental revision equals a fresh rebuild exactly, and a reload rebuilds the same;
//   - a change rebuilds the components it touched and keeps the others;
//   - randomized edit sequences on a grid model of the adapter: the incremental chain equals a fresh rebuild after every edit.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class NetIncrementalChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Route(RM_NetResult r, object t) =>
            r.Routes.TryGetValue(t, out List<RM_NetLink> l) ? string.Join(",", l.Select(x => x.Reel)) : "none";

        public static void Run(Action<string, Action> Case)
        {
            Case("Net_tree_root_is_canonical_routes_do_not_depend_on_who_asked_first", () =>
            {
                // a ring of four relays; TA hangs off R1, TB off R3: two equally long ways round. The route must not depend on
                // which tank's query built the component.
                HoseNetChecks.G Ring()
                {
                    var g = new HoseNetChecks.G();
                    g.Hose("TA", "R1", "ha");
                    g.Hose("R1", "R2", "h1");
                    g.Hose("R3", "R4", "h2");
                    g.Hose("R2", "R3", "h3");
                    g.Hose("R4", "R1", "h4");
                    g.Hose("R3", "TB", "hb");
                    return g;
                }
                var first = new RM_NetComponents(Ring());
                string a = Route(first.StoreOf("TA"), "TB");
                var second = new RM_NetComponents(Ring());
                second.StoreOf("TB");                            // TB's query builds the component this time
                string b = Route(second.StoreOf("TA"), "TB");
                Assert(a == b, "TA->TB route depends on who asked first: " + a + " / " + b);
                Assert(a.Split(',').Length == 4, "and it is a shortest way round (4 hoses): " + a);
            });

            Case("Net_incremental_rebuilds_only_the_touched_component", () =>
            {
                // two pipe runs, a tank on each, both built; a pipe added beside run A rebuilds A only
                var g = new Grid(12, 6);
                for (int x = 0; x < 4; x++) g.Pipes.Add(new Cell(x, 1));
                for (int x = 7; x < 11; x++) g.Pipes.Add(new Cell(x, 4));
                Th ta = g.Spawn(RM_NetRole.Tank, 0, 2, 1, 1), tb = g.Spawn(RM_NetRole.Tank, 10, 5, 1, 1);
                Th ma = g.Spawn(RM_NetRole.Machine, 3, 0, 1, 1), mb = g.Spawn(RM_NetRole.Machine, 7, 3, 1, 1);
                var prev = new RM_NetComponents(g, 50);
                Assert(prev.StoreOf(ma).Tanks.Contains(ta) && prev.StoreOf(mb).Tanks.Contains(tb) && prev.Builds == 2, "setup: two runs, two builds");
                var d = g.NewDelta();
                g.Pipes.Add(new Cell(4, 1));
                d.Thing(new object(), g.Around(new Cell(4, 1)));
                var inc = new RM_NetComponents(g, 50, prev, d);
                Assert(inc.Kept == 1, "run B is kept, run A is not (kept " + inc.Kept + ")");
                inc.StoreOf(ma);
                inc.StoreOf(mb);
                Assert(inc.Builds == 1, "only run A rebuilds (" + inc.Builds + " builds)");
                Assert(ReferenceEquals(inc.StoreOf(mb), prev.StoreOf(mb)), "run B's machine keeps its cached store");
                // a hose from run B's tank to a new tank: B's link-end tank's caches drop; run A is untouched by that
                var d2 = g.NewDelta();
                Th tc = g.Spawn(RM_NetRole.Tank, 11, 0, 1, 1);
                d2.Thing(tc, g.Around(tc));
                g.Reels.Add(new Reel { Name = "hz", A = tb, B = tc });
                g.Relink(d2);
                var inc2 = new RM_NetComponents(g, 50, inc, d2);
                Assert(inc2.Kept == 2 && inc2.StoreOf(ma) == inc.StoreOf(ma), "a hose between two tanks keeps both pipe runs (kept " + inc2.Kept + ")");
                Assert(inc2.StoreOf(tb).Tanks.Contains(tc) && inc2.Builds == 1, "and the new hose is one new component (" + inc2.Builds + " builds)");
                // can-fail: a full delta keeps nothing
                var full = new RM_NetDelta { Full = true };
                Assert(new RM_NetComponents(g, 50, inc2, full).Kept == 0, "can-fail: a full delta keeps nothing");
            });

            Case("Net_relink_reuses_unchanged_links_and_records_the_rest", () =>
            {
                var t1 = new Th { Name = "T1", Kind = RM_NetRole.Tank };
                var p = new RM_NetPort { Reel = "r2", Cell = new Cell(1, 1), Role = RM_FreeEndRole.Intake };
                var c = new Cell(0, 0);
                var d = new RM_NetDelta();
                Func<object, bool> isMember = v => v is Th;
                var old = RM_NetLinkDiff.Relink(null, new[] { E("r1", c, t1), E("r2", c, p) }, null, isMember);
                var same = RM_NetLinkDiff.Relink(old, new[] { E("r1", c, t1), E("r2", c, new RM_NetPort { Reel = "r2", Cell = new Cell(1, 1), Role = RM_FreeEndRole.Intake }) }, d, isMember);
                Assert(ReferenceEquals(same[0], old[0]) && ReferenceEquals(same[1], old[1]) && d.Empty, "unchanged reels keep their link objects, nothing recorded");
                var flip = RM_NetLinkDiff.Relink(same, new[] { E("r1", c, t1), E("r2", c, new RM_NetPort { Reel = "r2", Cell = new Cell(1, 1), Role = RM_FreeEndRole.Outflow }) }, d, isMember);
                Assert(ReferenceEquals(flip[0], old[0]) && !ReferenceEquals(flip[1], old[1]), "a port role change is a new link");
                Assert(d.Touched.Contains(old[1]) && d.Touched.Contains(flip[1]) && d.Touched.Contains(c) && !d.Touched.Contains(old[0]) && !d.Members.Contains(t1),
                    "the old and new link and their conductor end are touched; the unchanged link and its tank are not");
                var d2 = new RM_NetDelta();
                var gone = RM_NetLinkDiff.Relink(flip, new[] { E("r2", c, flip[1].B) }, d2, isMember);
                Assert(gone.Count == 1 && gone[0].Id == 0 && d2.Touched.Contains(old[0]) && d2.Members.Contains(t1), "a removed reel's link is touched, its tank end is a dirty member");
            });

            Case("Net_incremental_equals_fresh_rebuild_randomized", () =>
            {
                int checks = 0, kept = 0;
                for (int seed = 1; seed <= 400; seed++) checks += Fuzz(seed, ref kept);
                Assert(kept > checks / 20, "the fuzz exercised keeping (" + kept + " kept components over " + checks + " checks)");
                Console.WriteLine("    incremental == fresh: 400 seeds, " + checks + " query comparisons, " + kept + " components kept");
            });
        }

        private static KeyValuePair<object, KeyValuePair<object, object>> E(object reel, object a, object b) =>
            new KeyValuePair<object, KeyValuePair<object, object>>(reel, new KeyValuePair<object, object>(a, b));

        // ------------------------------------------------------------------ a grid model of RM_LiquidNet.MapGraph
        internal readonly struct Cell : IEquatable<Cell>
        {
            public readonly int X, Z;
            public Cell(int x, int z) { X = x; Z = z; }
            public bool Equals(Cell o) => X == o.X && Z == o.Z;
            public override bool Equals(object o) => o is Cell c && Equals(c);
            public override int GetHashCode() => X * 7919 + Z;
            public override string ToString() => "c" + X + "_" + Z;
        }

        internal sealed class Th
        {
            public string Name;
            public int Id;
            public RM_NetRole Kind;
            public int X, Z, W = 1, H = 1;
            public bool Spawned = true, Foreign;
            public bool Covers(Cell c) => c.X >= X && c.X < X + W && c.Z >= Z && c.Z < Z + H;
            public override string ToString() => Name;
        }

        internal sealed class Relay
        {
            public int Id;
            public override string ToString() => "R" + Id;
        }

        internal sealed class Reel
        {
            public string Name;
            public object A, B;
            public override string ToString() => Name;
        }

        /// <summary>MapGraph's rules on a grid: pipes conduct cardinally; a tank or machine attaches to pipes 8-way around or
        /// under it; a foreign member (liquid theft off) has no role; relays conduct through links only.</summary>
        internal sealed class Grid : IRM_NetGraph, IRM_NetNodeOrder
        {
            public readonly int W, H;
            public readonly HashSet<Cell> Pipes = new HashSet<Cell>();
            public readonly List<Th> Things = new List<Th>();
            public readonly List<Reel> Reels = new List<Reel>();
            public List<RM_NetLink> Links = new List<RM_NetLink>();
            public bool PipesOn = true;
            private int ids;

            public Grid(int w, int h) { W = w; H = h; }

            public Th Spawn(RM_NetRole kind, int x, int z, int w, int h)
            {
                var t = new Th { Name = (kind == RM_NetRole.Tank ? "T" : "M") + (++ids), Id = ids, Kind = kind, X = x, Z = z, W = w, H = h };
                Things.Add(t);
                return t;
            }

            public bool In(Cell c) => c.X >= 0 && c.Z >= 0 && c.X < W && c.Z < H;

            public IEnumerable<object> Rect(int x0, int z0, int x1, int z1)
            {
                for (int z = z0; z <= z1; z++)
                    for (int x = x0; x <= x1; x++)
                    {
                        var c = new Cell(x, z);
                        if (In(c)) yield return c;
                    }
            }

            /// <summary>The adapter's delta cells: a thing's rect grown by one (a cell: its 3x3).</summary>
            public IEnumerable<object> Around(object v) =>
                v is Th t ? Rect(t.X - 1, t.Z - 1, t.X + t.W, t.Z + t.H) : v is Cell c ? Rect(c.X - 1, c.Z - 1, c.X + 1, c.Z + 1) : Enumerable.Empty<object>();

            public RM_NetDelta NewDelta() => new RM_NetDelta { MemberCells = m => m is Th t ? Around(t) : Enumerable.Empty<object>() };

            public void Relink(RM_NetDelta d)
            {
                Links = RM_NetLinkDiff.Relink(Links, Reels.Select(r => E(r, r.A, r.B)), d, v => v is Th);
            }

            private IEnumerable<Th> ThingsAt(Cell c) => Things.Where(t => t.Spawned && t.Covers(c));
            private RM_NetRole RoleOfThing(Th t) => t.Spawned && !t.Foreign ? t.Kind : RM_NetRole.None;

            public bool PipesEnabled => PipesOn;
            public RM_NetRole RoleOf(object v)
            {
                if (v is Cell c) return In(c) && Pipes.Contains(c) ? RM_NetRole.Pipe : RM_NetRole.None;
                if (v is Relay) return RM_NetRole.Relay;
                if (v is RM_NetPort) return RM_NetRole.Port;
                return v is Th t ? RoleOfThing(t) : RM_NetRole.None;
            }
            private IEnumerable<object> Ring(Th t) => Rect(t.X - 1, t.Z - 1, t.X + t.W, t.Z + t.H).Where(c => !t.Covers((Cell)c));
            private IEnumerable<object> ThingsIn(IEnumerable<object> cells, object exclude, RM_NetRole role)
            {
                foreach (Cell c in cells)
                    foreach (Th t in ThingsAt(c))
                        if (t != exclude && RoleOfThing(t) == role) yield return t;
            }
            public IEnumerable<object> OriginTanks(object m) =>
                m is Th t && t.Spawned && RoleOfThing(t) == RM_NetRole.Machine ? ThingsIn(Ring(t), t, RM_NetRole.Tank) : Enumerable.Empty<object>();
            public IEnumerable<object> OriginPipeCells(object m) =>
                m is Th t && t.Spawned ? Ring(t).Concat(Rect(t.X, t.Z, t.X + t.W - 1, t.Z + t.H - 1)).Where(c => Pipes.Contains((Cell)c)) : Enumerable.Empty<object>();
            public IEnumerable<object> PipeTanks(object pc) => ThingsIn(Around(pc), null, RM_NetRole.Tank).Distinct();
            public IEnumerable<object> PipeMachines(object pc) => ThingsIn(Around(pc), null, RM_NetRole.Machine).Distinct();
            public IEnumerable<object> PipeNeighbours(object pc)
            {
                var c = (Cell)pc;
                foreach (Cell n in new[] { new Cell(c.X, c.Z + 1), new Cell(c.X + 1, c.Z), new Cell(c.X, c.Z - 1), new Cell(c.X - 1, c.Z) })
                    if (In(n) && Pipes.Contains(n)) yield return n;
            }
            public IList<RM_NetLink> LinksAt(object v) => At(Links, v);
            public static IList<RM_NetLink> At(List<RM_NetLink> links, object v) => links.Where(l => Equals(l.A, v) || Equals(l.B, v)).ToList();
            public int Order(object m) => m is Th t ? t.Id : 0;

            public int CompareNodes(object a, object b)
            {
                int ra = Rank(a), rb = Rank(b);
                if (ra != rb) return ra.CompareTo(rb);
                if (a is Cell ca && b is Cell cb) return (ca.Z * W + ca.X).CompareTo(cb.Z * W + cb.X);
                if (a is Relay xa && b is Relay xb) return xa.Id.CompareTo(xb.Id);
                if (a is RM_NetLink la && b is RM_NetLink lb)
                {
                    int c = string.CompareOrdinal(la.Reel?.ToString(), lb.Reel?.ToString());
                    return c != 0 ? c : la.Id.CompareTo(lb.Id);
                }
                return 0;
            }
            private static int Rank(object v) => v is Cell ? 0 : v is Relay ? 1 : 2;
        }

        /// <summary>The grid with its links built from scratch (no Relink reuse), so the fresh side of the fuzz never shares
        /// a link-diff bug with the incremental side.</summary>
        internal sealed class FreshView : IRM_NetGraph, IRM_NetNodeOrder
        {
            private readonly Grid g;
            public readonly List<RM_NetLink> Links;
            public FreshView(Grid g)
            {
                this.g = g;
                Links = RM_NetLinkDiff.Relink(null, g.Reels.Select(r => E(r, r.A, r.B)), null, v => v is Th);
            }
            public bool PipesEnabled => g.PipesEnabled;
            public RM_NetRole RoleOf(object v) => g.RoleOf(v);
            public IEnumerable<object> OriginTanks(object m) => g.OriginTanks(m);
            public IEnumerable<object> OriginPipeCells(object m) => g.OriginPipeCells(m);
            public IEnumerable<object> PipeTanks(object pc) => g.PipeTanks(pc);
            public IEnumerable<object> PipeMachines(object pc) => g.PipeMachines(pc);
            public IEnumerable<object> PipeNeighbours(object pc) => g.PipeNeighbours(pc);
            public IList<RM_NetLink> LinksAt(object v) => Grid.At(Links, v);
            public int Order(object m) => g.Order(m);
            public int CompareNodes(object a, object b) => g.CompareNodes(a, b);
        }

        // ------------------------------------------------------------------ describing answers, so two revisions can be compared
        private static string Name(object v) => v is RM_NetLink l ? "L" + l.Reel : v is RM_NetPort p ? "port" + p.Reel + p.Role : v?.ToString() ?? "null";

        private static string Describe(RM_NetComponent c)
        {
            if (c == null) return "-";
            if (c.Refused) return "REFUSED";
            var sb = new System.Text.StringBuilder();
            for (int i = 0; i < c.Nodes.Count; i++) sb.Append(Name(c.Nodes[i])).Append('<').Append(c.Parent[i]).Append('@').Append(c.Depth[i]).Append(' ');
            sb.Append("| T ").Append(string.Join(",", c.Tanks.Select(Name)));
            sb.Append(" | M ").Append(string.Join(",", c.Machines.Select(Name)));
            sb.Append(" | P ").Append(string.Join(",", c.Ports.Select(Name)));
            sb.Append(" | L ").Append(string.Join(",", c.Links.Select(Name)));
            foreach (object m in c.Tanks.Concat(c.Machines).Concat(c.Ports.Cast<object>()))
                sb.Append(" | ").Append(Name(m)).Append('@').Append(string.Join(",", c.Attach[m]));
            sb.Append(" | size ").Append(c.Size);
            return sb.ToString();
        }

        private static string Describe(RM_NetResult r) =>
            (r.Truncated ? "TRUNC " : "") + string.Join(" ", r.Tanks.Select(t => Name(t) + "[" + string.Join(",", r.Routes[t].Select(Name)) + "]"));

        /// <summary>One seed: a random grid, random edits, after each edit the same random queries on the incremental revision
        /// and on a fresh one; every answer must be equal. Returns the number of compared answers.</summary>
        private static int Fuzz(int seed, ref int keptTotal)
        {
            var rnd = new Random(seed);
            var g = new Grid(rnd.Next(5, 11), rnd.Next(5, 11));
            int cap = rnd.Next(3) == 0 ? rnd.Next(8, 30) : RM_NetComponents.MaxConductors;
            var relays = new List<Relay>();
            for (int i = 0; i < 3; i++) relays.Add(new Relay { Id = i });
            int reelIds = 0;
            Cell RandCell() => new Cell(rnd.Next(g.W), rnd.Next(g.H));
            object RandEnd(Reel r)
            {
                switch (rnd.Next(5))
                {
                    case 0: return RandCell();
                    case 1: case 2:
                        List<Th> ts = g.Things;
                        return ts.Count > 0 ? ts[rnd.Next(ts.Count)] : (object)RandCell();
                    case 3: return relays[rnd.Next(relays.Count)];
                    default: return new RM_NetPort { Reel = r, Cell = RandCell(), Role = (RM_FreeEndRole)rnd.Next(3) };
                }
            }
            for (int i = 0; i < rnd.Next(5, 30); i++) g.Pipes.Add(RandCell());
            for (int i = 0; i < rnd.Next(1, 6); i++)
                g.Spawn(rnd.Next(2) == 0 ? RM_NetRole.Tank : RM_NetRole.Machine, rnd.Next(g.W), rnd.Next(g.H), rnd.Next(1, 3), rnd.Next(1, 3));
            for (int i = 0; i < rnd.Next(0, 5); i++)
            {
                var r = new Reel { Name = "h" + (reelIds++) };
                r.A = RandEnd(r);
                r.B = RandEnd(r);
                g.Reels.Add(r);
            }
            g.Relink(null);
            RM_NetComponents inc = new RM_NetComponents(g, cap);
            int compared = 0;
            int edits = rnd.Next(10, 40);
            for (int e = 0; e <= edits; e++)
            {
                RM_NetDelta d = g.NewDelta();
                if (e > 0)
                {
                    int k = rnd.Next(10);
                    if (k <= 2)
                    {
                        Cell c = RandCell();
                        if (!g.Pipes.Remove(c)) g.Pipes.Add(c);
                        d.Thing(new object(), g.Around(c));
                    }
                    else if (k == 3)
                    {
                        Th t = g.Spawn(rnd.Next(2) == 0 ? RM_NetRole.Tank : RM_NetRole.Machine, rnd.Next(g.W), rnd.Next(g.H), rnd.Next(1, 3), rnd.Next(1, 3));
                        d.Thing(t, g.Around(t));
                    }
                    else if (k == 4 && g.Things.Count > 0)
                    {
                        Th t = g.Things[rnd.Next(g.Things.Count)];
                        if (rnd.Next(2) == 0) t.Spawned = !t.Spawned; else t.Foreign = !t.Foreign;
                        d.Thing(t, g.Around(t));
                    }
                    else if (k == 5 && g.Things.Count > 0)
                    {
                        // a reinstall elsewhere: despawn here, spawn there (both places dirty)
                        Th t = g.Things[rnd.Next(g.Things.Count)];
                        d.Thing(t, g.Around(t));
                        t.X = rnd.Next(g.W);
                        t.Z = rnd.Next(g.H);
                        d.Thing(t, g.Around(t));
                    }
                    else if (k == 6)
                    {
                        var r = new Reel { Name = "h" + (reelIds++) };
                        r.A = RandEnd(r);
                        r.B = RandEnd(r);
                        g.Reels.Add(r);
                    }
                    else if (k == 7 && g.Reels.Count > 0)
                    {
                        g.Reels.RemoveAt(rnd.Next(g.Reels.Count));
                    }
                    else if (k == 8 && g.Reels.Count > 0)
                    {
                        Reel r = g.Reels[rnd.Next(g.Reels.Count)];
                        if (rnd.Next(2) == 0) r.A = RandEnd(r); else r.B = RandEnd(r);
                    }
                    else if (g.Reels.Count > 0)
                    {
                        // a port's role flips (the same reel, a new port value)
                        Reel r = g.Reels[rnd.Next(g.Reels.Count)];
                        if (r.B is RM_NetPort p) r.B = new RM_NetPort { Reel = r, Cell = p.Cell, Role = (RM_FreeEndRole)(((int)p.Role + 1) % 3) };
                    }
                    if (rnd.Next(25) == 0) { g.PipesOn = !g.PipesOn; d.Full = true; }
                    g.Relink(d);
                    inc = new RM_NetComponents(g, cap, inc, d);
                    keptTotal += inc.Kept;
                }
                var view = new FreshView(g);
                var fresh = new RM_NetComponents(view, cap);
                int queries = rnd.Next(0, 12);
                for (int q = 0; q < queries; q++)
                {
                    string a, b, what;
                    int kind = rnd.Next(4);
                    if (kind == 0 && g.Things.Count > 0)
                    {
                        Th t = g.Things[rnd.Next(g.Things.Count)];
                        what = "StoreOf(" + t + ")";
                        a = Describe(inc.StoreOf(t)) + " | " + inc.TooLarge(t) + " | " + string.Join(" / ", inc.ComponentsOf(t).Select(Describe));
                        b = Describe(fresh.StoreOf(t)) + " | " + fresh.TooLarge(t) + " | " + string.Join(" / ", fresh.ComponentsOf(t).Select(Describe));
                    }
                    else if (kind == 1 && g.Links.Count > 0)
                    {
                        int li = rnd.Next(g.Links.Count);
                        RM_NetLink l = g.Links[li];
                        what = "ComponentOf(" + Name(l) + ")";
                        a = Describe(inc.ComponentOf(l));
                        b = Describe(fresh.ComponentOf(view.Links[li]));
                    }
                    else if (kind == 2 && g.Things.Count > 1)
                    {
                        Th t1 = g.Things[rnd.Next(g.Things.Count)], t2 = g.Things[rnd.Next(g.Things.Count)];
                        what = "RouteIn(" + t1 + "," + t2 + ")";
                        a = string.Join(" / ", inc.ComponentsOf(t1).Select(c => c.Refused ? "R" : Describe(c) + "=>" + string.Join(",", (inc.RouteIn(c, t1, t2) ?? new List<RM_NetLink>()).Select(Name))));
                        b = string.Join(" / ", fresh.ComponentsOf(t1).Select(c => c.Refused ? "R" : Describe(c) + "=>" + string.Join(",", (fresh.RouteIn(c, t1, t2) ?? new List<RM_NetLink>()).Select(Name))));
                    }
                    else
                    {
                        Cell c = RandCell();
                        what = "ComponentOfNode(" + c + ")";
                        a = Describe(inc.ComponentOfNode(c));
                        b = Describe(fresh.ComponentOfNode(c));
                    }
                    compared++;
                    if (a != b) throw new Exception("seed " + seed + " edit " + e + " query " + q + " " + what + ":\n      incremental " + a + "\n      fresh       " + b);
                }
            }
            return compared;
        }
    }
}
