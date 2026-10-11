// Hose port step 6 (design FINAL §3.1-3.4, §3.7): the liquid net's rules asserted against the PRODUCTION kernel
// (../Machinery/RM_LiquidNetKernel.cs, compiled in directly) over a small fake graph. Liquid networks L2 (rev 2 §3.1): the
// per-origin Walk/Across became components per topology revision; every assertion below now reads a member's STORE
// (RM_NetComponents.StoreOf) or a hose's component (TanksAcross) with the same expected tanks and routes. One changed meaning:
// a tank's own store now includes the tank across a hose screwed onto it (tank-hose-tank is one component), which is asserted
// directly instead of as the old "walking from the tank" can-fail. Vertices are strings: "P*" machines,
// "T*" tanks, "c*" universal-pipe cells, "R*" relay reels. Each rule carries a can-fail where one is meaningful.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseNetChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "hosenet: " + msg);

        /// <summary>A fake map: roles by name prefix, pipe adjacency, what touches what, and hose links.</summary>
        internal sealed class G : IRM_NetGraph
        {
            public bool Pipes = true;
            public readonly Dictionary<string, List<string>> Touch = new Dictionary<string, List<string>>();   // origin -> tanks (8-way)
            public readonly Dictionary<string, List<string>> PipeOf = new Dictionary<string, List<string>>();  // origin -> pipe cells
            public readonly Dictionary<string, List<string>> Adj = new Dictionary<string, List<string>>();     // pipe cell -> pipe cells
            public readonly Dictionary<string, List<string>> PT = new Dictionary<string, List<string>>();      // pipe cell -> tanks
            public readonly List<RM_NetLink> Links = new List<RM_NetLink>();
            public readonly HashSet<int> Dead = new HashSet<int>();     // links the eligibility rule rejects (not laid, refused lay)

            public bool PipesEnabled => Pipes;
            public RM_NetRole RoleOf(object v)
            {
                string s = v as string ?? "";
                return s.StartsWith("T") ? RM_NetRole.Tank : s.StartsWith("c") ? RM_NetRole.Pipe : s.StartsWith("R") ? RM_NetRole.Relay
                     : s.StartsWith("P") ? RM_NetRole.Machine : RM_NetRole.None;
            }
            private static IEnumerable<object> Get(Dictionary<string, List<string>> d, object k) =>
                d.TryGetValue(k as string ?? "", out List<string> l) ? l.Cast<object>() : Enumerable.Empty<object>();
            public IEnumerable<object> OriginTanks(object o) => Get(Touch, o);
            /// <summary>A machine's cells are PipeOf; a tank's are the cells whose PT lists it (the same contact, read from its side).</summary>
            public IEnumerable<object> OriginPipeCells(object o) =>
                RoleOf(o) == RM_NetRole.Tank ? PT.Where(kv => kv.Value.Contains(o as string)).Select(kv => (object)kv.Key).Concat(Get(PipeOf, o)).Distinct() : Get(PipeOf, o);
            public IEnumerable<object> PipeTanks(object c) => Get(PT, c);
            public IEnumerable<object> PipeMachines(object c) => PipeOf.Where(kv => RoleOf(kv.Key) == RM_NetRole.Machine && kv.Value.Contains(c as string)).Select(kv => (object)kv.Key);
            public int Order(object v) { string s = v as string ?? ""; string d = new string(s.Where(char.IsDigit).ToArray()); return d.Length > 0 && d.Length < 9 ? int.Parse(d) : 0; }
            public IEnumerable<object> PipeNeighbours(object c) => Get(Adj, c);
            public IList<RM_NetLink> LinksAt(object v) => Links.Where(l => !Dead.Contains(l.Id) && (Equals(l.A, v) || Equals(l.B, v))).ToList();

            public RM_NetLink Hose(string a, string b, string reel = null)
            {
                var l = new RM_NetLink { Id = Links.Count, A = a, B = b, Reel = reel ?? ("reel" + Links.Count) };
                Links.Add(l);
                return l;
            }
            public void Run(params string[] cells)
            {
                for (int i = 0; i + 1 < cells.Length; i++)
                {
                    Add(Adj, cells[i], cells[i + 1]);
                    Add(Adj, cells[i + 1], cells[i]);
                }
            }
            public static void Add(Dictionary<string, List<string>> d, string k, string v)
            {
                if (!d.TryGetValue(k, out List<string> l)) d[k] = l = new List<string>();
                l.Add(v);
            }
        }

        /// <summary>The member's store in a fresh revision (the old per-origin Walk's replacement).</summary>
        internal static RM_NetResult Walk(G g, string member) => new RM_NetComponents(g).StoreOf(member);

        private static List<string> Tanks(RM_NetResult r) => r.Tanks.Cast<string>().ToList();
        private static string Route(RM_NetResult r, string t) => r.Routes.TryGetValue(t, out List<RM_NetLink> l) ? string.Join(",", l.Select(x => x.Reel)) : "none";

        public static void Run()
        {
            Basics();
            TankEndpoints();
            ExternalAndRoles();
            PortChanges();
            Relays();
            Leases();
            Tints();
            TankFeed();
        }

        private static void Basics()
        {
            // a pump with a hose screwed on, the far end on tank T1
            var g = new G();
            g.Hose("P1", "T1", "A");
            RM_NetResult r = Walk(g, "P1");
            Check(Tanks(r).SequenceEqual(new[] { "T1" }) && Route(r, "T1") == "A", "a hose from the pump reaches the far tank, route = that hose");
            // a pump at the FAR end of a hose reaches the tank beside the reel (M2: far-end seeding)
            var g2 = new G();
            g2.Hose("T9", "P2", "B");
            Check(Tanks(Walk(g2, "P2")).SequenceEqual(new[] { "T9" }), "a pump at the far end reaches the tank at the reel end");
            // the eligibility rule: a dropped / carried / wound hose or a refused lay forms no link -> nothing
            var g3 = new G();
            RM_NetLink l3 = g3.Hose("P1", "T1");
            g3.Dead.Add(l3.Id);
            Check(Tanks(Walk(g3, "P1")).Count == 0, "a dead link (dropped hose, refused lay) carries nothing");
            // touching tanks still lead, and the origin is never its own tank
            var g4 = new G();
            G.Add(g4.Touch, "P1", "T0");
            G.Add(g4.Touch, "P1", "P1");
            g4.Hose("P1", "T1");
            Check(Tanks(Walk(g4, "P1")).SequenceEqual(new[] { "T0", "T1" }) && Route(Walk(g4, "P1"), "T0") == "",
                  "adjacent tanks lead (empty route), the origin is never a tank of its own net");
            // pipe and hose one net: pump -> pipe run -> hose (coupled to the run's last cell) -> tank (NS_pipe_and_hose_one_net)
            var g5 = new G();
            G.Add(g5.PipeOf, "P1", "c1");
            g5.Run("c1", "c2", "c3");
            g5.Hose("c3", "T5", "H");
            G.Add(g5.PT, "c2", "T2");
            RM_NetResult r5 = Walk(g5, "P1");
            Check(Tanks(r5).SequenceEqual(new[] { "T2", "T5" }) && Route(r5, "T5") == "H" && Route(r5, "T2") == "",
                  "pipe then hose: both tanks; only the hose-side tank's route crosses the hose");
            // review S4: a tank the origin reaches by its pipe run AND by a hose keeps the PIPE route (empty), so that hose is on
            // no route and stays flat; it holds however long the pipe run is, and pipe-reached tanks lead hose-reached ones
            var gS4 = new G();
            G.Add(gS4.PipeOf, "P1", "c1");
            gS4.Run("c1", "c2", "c3");
            G.Add(gS4.PT, "c3", "T7");
            gS4.Hose("P1", "T7", "H");
            gS4.Hose("P1", "T8", "K");
            RM_NetResult rS4 = Walk(gS4, "P1");
            Check(Tanks(rS4).SequenceEqual(new[] { "T7", "T8" }) && Route(rS4, "T7") == "" && Route(rS4, "T8") == "K"
                  && rS4.Routes.Values.All(rt => rt.All(x => (string)x.Reel != "H")),
                  "tank on pipe AND hose: route is the pipe (empty), hose H on no route (stays flat); the pipe tank leads");
            gS4.Pipes = false;
            RM_NetResult rS4b = Walk(gS4, "P1");
            Check(Route(rS4b, "T7") == "H", "can-fail: with the pipes off the same tank is reached by the hose (route H)");
            // universalPipesEnabled off: the pipe conducts nothing, so neither the pipe tank nor the hose beyond it
            g5.Pipes = false;
            Check(Tanks(Walk(g5, "P1")).Count == 0, "pipes off: the pipe run and the hose screwed onto it carry nothing");
            g5.Pipes = true;
            // a hose from the pump to the pipe run's far cell: the pipe conducts from the hose's end too
            var g6 = new G();
            g6.Hose("P1", "c9", "H2");
            g6.Run("c9", "c8");
            G.Add(g6.PT, "c8", "T8");
            RM_NetResult r6 = Walk(g6, "P1");
            Check(Tanks(r6).SequenceEqual(new[] { "T8" }) && Route(r6, "T8") == "H2", "a hose onto a pipe run reaches the run's tanks over the hose");
        }

        private static void TankEndpoints()
        {
            // pump -> pipe -> tank T, and a hose from T to tank TU: TU is NOT reached (tanks never conduct; Q7 adds a tank FEED, not a merge)
            var g = new G();
            G.Add(g.PipeOf, "P1", "c1");
            G.Add(g.PT, "c1", "T");
            g.Hose("T", "TU", "TU");
            RM_NetResult r = Walk(g, "P1");
            Check(Tanks(r).SequenceEqual(new[] { "T" }), "pump -> pipe -> T, T -hose-> TU: TU is not on the pump's net (tank endpoint)");
            // and the other way round: pump -hose-> T reaches T; a pump at T's hose far end reaches T too
            var g2 = new G();
            g2.Hose("P1", "T", "x");
            g2.Hose("T", "P2", "y");
            Check(Tanks(Walk(g2, "P1")).SequenceEqual(new[] { "T" }) && Tanks(Walk(g2, "P2")).SequenceEqual(new[] { "T" }),
                  "pump -hose-> T and pump-at-far-end -hose-> T both reach T, and stop there");
            // two pipe runs never merge through a tank, even with a hose screwed onto it
            var g3 = new G();
            G.Add(g3.PipeOf, "P1", "a1");
            G.Add(g3.PT, "a1", "T");
            G.Add(g3.PT, "b1", "T");
            G.Add(g3.PT, "b1", "TV");
            Check(!Tanks(Walk(g3, "P1")).Contains("TV"), "two pipe runs touching one tank stay two nets");
            // rev 2 §3.1: tank-hose-tank is one component, so T's OWN store holds TU (route = that hose), while the pump's does not
            RM_NetResult rt = Walk(g, "T");
            Check(Tanks(rt).SequenceEqual(new[] { "TU" }) && Route(rt, "TU") == "TU", "tank-hose-tank: T's store is TU over the hose; T is never in its own store");
            // can-fail: if tanks conducted (the pipe run and the hose one component), the pump would reach TU
            var comps = new RM_NetComponents(g);
            Check(comps.ComponentsOf("T").Count == 2 && comps.ComponentsOf("P1").Count == 1 && !comps.ComponentsOf("P1")[0].Tanks.Contains("TU"),
                  "can-fail: T is attached to two components (the pipe run, the hose) and the pump's holds no TU");
        }

        private static void ExternalAndRoles()
        {
            // an external (VE PipeSystem / DBH) pipe between two native runs: role None, so it never joins them
            var g = new G();
            G.Add(g.PipeOf, "P1", "c1");
            g.Hose("c1", "EXT", "e1");
            g.Hose("EXT", "c5", "e2");
            G.Add(g.PT, "c5", "T5");
            Check(!Tanks(Walk(g, "P1")).Contains("T5"), "an external (visual-only) pipe between two native runs does not merge them");
            // a machine is never a conductor: pump -hose-> converter -hose-> tank does not reach the tank from the pump
            var g2 = new G();
            g2.Hose("P1", "P2", "m1");
            g2.Hose("P2", "T", "m2");
            Check(Tanks(Walk(g2, "P1")).Count == 0 && Tanks(Walk(g2, "P2")).SequenceEqual(new[] { "T" }),
                  "a machine at a hose end ends the walk; from that machine its own hose reaches T");
        }

        private static void PortChanges()
        {
            // a port that changes null -> X or X -> Y is a different link set (a new revision: RM_HoseLinks' signature bumps it)
            var g = new G();
            RM_NetLink l = g.Hose("P1", "T1", "A");
            Check(Tanks(Walk(g, "P1")).SequenceEqual(new[] { "T1" }), "port X: T1");
            l.B = "T2";
            Check(Tanks(Walk(g, "P1")).SequenceEqual(new[] { "T2" }), "port X -> Y (the far tank replaced): T2, never the old one");
            g.Dead.Add(l.Id);
            Check(Tanks(Walk(g, "P1")).Count == 0, "port removed (far tank deconstructed): no link, nothing reached");
            g.Dead.Remove(l.Id);
            Check(Tanks(Walk(g, "P1")).SequenceEqual(new[] { "T2" }), "port rebuilt: reached again");
        }

        private static void Relays()
        {
            // pump -A-> relay RB -B-> relay RC -C-> tank: a chain of three conducts, route = all three hoses
            var g = new G();
            g.Hose("P1", "RB", "A");
            g.Hose("RB", "RC", "B");
            g.Hose("RC", "T", "C");
            RM_NetResult r = Walk(g, "P1");
            Check(Tanks(r).SequenceEqual(new[] { "T" }) && Route(r, "T") == "A,B,C", "a relay chain of three conducts, crediting all three hoses (" + Route(r, "T") + ")");
            // a relay with no onward hose is a dead end, not a leak
            var g2 = new G();
            g2.Hose("P1", "RB", "A");
            Check(Tanks(Walk(g2, "P1")).Count == 0, "a relay whose own hose is not laid ends the chain");
            // a ring terminates (visited vertices and links)
            var g3 = new G();
            g3.Hose("P1", "RA", "a");
            g3.Hose("RA", "RB", "b");
            g3.Hose("RB", "RA", "c");
            g3.Hose("RB", "T", "d");
            RM_NetResult r3 = Walk(g3, "P1");
            Check(Tanks(r3).SequenceEqual(new[] { "T" }) && r3.Visited < 10, "a ring of relays terminates and still finds the tank");
            // one route per tank: two parallel hoses to the same tank, only the first-found is credited (S9)
            var g4 = new G();
            g4.Hose("P1", "T", "first");
            g4.Hose("P1", "T", "second");
            Check(Route(Walk(g4, "P1"), "T") == "first", "one route per tank: the parallel hose stays flat (only the first is credited)");
            // pour = draw: the route is undirected, so a pour credits the same hoses a draw does
            Check(Route(Walk(g, "P1"), "T") == Route(r, "T"), "the same route whichever way the liquid moves");
            // route liveness at transfer: a hose wound in after the walk (same tick) drops the route
            var dead = new HashSet<int> { 1 };
            Check(RM_LiquidNetKernel.RouteLive(r.Routes["T"], x => !dead.Contains(x.Id)) == false && RM_LiquidNetKernel.RouteLive(r.Routes["T"], x => true),
                  "a link wound in between the walk and the transfer drops the route (no credit)");
        }

        private static void Leases()
        {
            int nl = RM_LiquidNetKernel.NoLease;
            Check(!RM_LiquidNetKernel.Flowing(nl, 0) && !RM_LiquidNetKernel.Flowing(nl, 1000000), "a never-credited hose is not flowing");
            int u = RM_LiquidNetKernel.Lease(nl, 1000, 250);
            Check(u == 1375 && RM_LiquidNetKernel.Flowing(u, 1375) && !RM_LiquidNetKernel.Flowing(u, 1376), "a pump credit at 1000 leases to 1375 (1.5 x 250)");
            // monotonic: a short-cadence credit never shortens a longer lease; caller order never matters
            int a = RM_LiquidNetKernel.Lease(RM_LiquidNetKernel.Lease(nl, 1000, 500), 1000, 60);
            int b = RM_LiquidNetKernel.Lease(RM_LiquidNetKernel.Lease(nl, 1000, 60), 1000, 500);
            Check(a == b && a == 1750, "lease monotonic and order-independent (" + a + "," + b + ")");
            // a steady 250-tick pump keeps the hose flowing between cycles (no flicker even with a short pulse setting)
            int lease = nl;
            bool gap = false;
            for (int t = 0; t <= 5000; t++)
            {
                if (t % 250 == 0) lease = RM_LiquidNetKernel.Lease(lease, t, 250);
                if (!RM_LiquidNetKernel.Flowing(lease, t)) gap = true;
            }
            Check(!gap, "a steady pump: no tick without flow");
            // can-fail: the old adapter's window (1.5 x the flow PULSE, 60 ticks) against a 250-tick pump flickers
            bool oldGap = false;
            for (int t = 0; t <= 1000; t++) if (!(t - (t / 250) * 250 <= 60 + 60 / 2)) oldGap = true;
            Check(oldGap, "can-fail: a 1.5 x 60-tick window against a 250-tick pump would flicker");
            // the bath: one craft is one plump pulse of the release window
            Check(RM_LiquidNetKernel.Lease(nl, 0, 500) == 750, "a bath credit (cadence = releaseTicks 500) leases one pulse of 750");
            // the plump-off bound (§3.6): last credit live 375, release 500, transition 30 -> flat by ~905 ticks after the last transfer
            Check(RM_LiquidNetKernel.Lease(nl, 0, 250) + 500 + 30 == 905, "flat no later than 1.5 x 250 + releaseTicks + transitionTicks = 905");
        }

        private static void Tints()
        {
            int nl = RM_LiquidNetKernel.NoLease;
            string tint = null, pend = null;
            int since = 0, pu = nl;
            RM_LiquidNetKernel.TintStep(ref tint, ref pend, ref since, ref pu, "water", 100, 250, 600);
            Check(tint == "water" && pend == null, "the first credit on an untinted hose sets the tint at once");
            // a second liquid takes over only after minPlumpDwell of CONTINUOUS candidacy
            for (int t = 350; t <= 850; t += 250) RM_LiquidNetKernel.TintStep(ref tint, ref pend, ref since, ref pu, "tar", t, 250, 600);
            Check(tint == "water" && pend == "tar", "tar credited for 500 < 600 ticks: still water");
            RM_LiquidNetKernel.TintStep(ref tint, ref pend, ref since, ref pu, "tar", 1100, 250, 600);
            Check(tint == "tar" && pend == null, "tar credited continuously for 750 >= 600: the tint switches");
            // a broken run of credits restarts the dwell (no thrash between two pumps of different liquids)
            string t2 = "water", p2 = null;
            int s2 = 0, u2 = nl;
            RM_LiquidNetKernel.TintStep(ref t2, ref p2, ref s2, ref u2, "tar", 0, 250, 600);
            RM_LiquidNetKernel.TintStep(ref t2, ref p2, ref s2, ref u2, "tar", 1000, 250, 600);   // gap 1000 > lease 375
            Check(t2 == "water" && p2 == "tar" && s2 == 1000, "a gap in the candidate's credits restarts the dwell");
            // the tick candidate: most units, ties by name, independent of crediting order
            var d1 = new Dictionary<string, int> { { "b", 5 }, { "a", 5 } };
            var d2 = new Dictionary<string, int> { { "a", 5 }, { "b", 5 } };
            Check(RM_LiquidNetKernel.Candidate(d1) == "a" && RM_LiquidNetKernel.Candidate(d2) == "a" && RM_LiquidNetKernel.Candidate(null) == null,
                  "candidate ties go to the name in any crediting order");
            // a save mid-switch: tint, pending and since are saved; pendingUntil is runtime -> after a load the next credit restarts it
            string t3 = "water", p3 = "tar";
            int s3 = 400, u3 = nl;   // the loaded state: pendingUntil not saved
            RM_LiquidNetKernel.TintStep(ref t3, ref p3, ref s3, ref u3, "tar", 1200, 250, 600);
            Check(t3 == "water" && s3 == 1200, "a load mid-switch keeps the shown tint and restarts the dwell (never flips on load)");
        }

        private static void TankFeed()
        {
            // owner Q7: a tank passes liquid on to a hose screwed into it, no pump needed -- toward an equal fill, 5 units a cycle
            Check(RM_LiquidNetKernel.TankFeedUnits(100, 100, 0, 100, true, 5) == 5, "a full tank feeds an empty one 5 units a cycle");
            Check(RM_LiquidNetKernel.TankFeedUnits(52, 100, 48, 100, true, 5) == 2, "near level: only what levels them (2)");
            Check(RM_LiquidNetKernel.TankFeedUnits(50, 100, 50, 100, true, 5) == 0 && RM_LiquidNetKernel.TankFeedUnits(40, 100, 60, 100, true, 5) == 0,
                  "level or emptier: nothing moves (it never pumps uphill)");
            Check(RM_LiquidNetKernel.TankFeedUnits(100, 100, 0, 100, false, 5) == 0, "another liquid in the destination: nothing moves");
            Check(RM_LiquidNetKernel.TankFeedUnits(300, 300, 0, 25, true, 5) == 5 && RM_LiquidNetKernel.TankFeedUnits(300, 300, 25, 25, true, 5) == 0,
                  "a full destination takes nothing; capacities are by fraction");
            var d = new List<(int, int, bool)> { (90, 100, true), (10, 100, true), (0, 100, false) };
            Check(RM_LiquidNetKernel.FeedTarget(d, 100, 100, 5) == 1, "the feed goes to the emptiest COMPATIBLE tank it reaches");
            // the feed reads only the component of the hose screwed onto the tank: a pipe run the tank stands in is not reached
            var g = new G();
            G.Add(g.PT, "c1", "T");          // T stands in a pipe run c1-c2 with tank W on it
            g.Run("c1", "c2");
            G.Add(g.PT, "c2", "TW");
            RM_NetLink l = g.Hose("T", "TU", "feed");
            RM_NetResult r = new RM_NetComponents(g).TanksAcross(l, "T");
            Check(Tanks(r).SequenceEqual(new[] { "TU" }) && Route(r, "TU") == "feed", "a feed from T reaches TU over its hose, never W in T's pipe run");
            var g2 = new G();
            RM_NetLink l2 = g2.Hose("T", "c5", "f2");
            g2.Run("c5", "c6");
            G.Add(g2.PT, "c6", "TV");
            Check(Tanks(new RM_NetComponents(g2).TanksAcross(l2, "T")).SequenceEqual(new[] { "TV" }), "a feed into a pipe run reaches the run's tanks");
        }
    }
}
