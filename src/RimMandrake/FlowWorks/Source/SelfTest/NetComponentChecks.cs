// Liquid networks build step L2 (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md rev 2 §3.1, §6 L2): the
// liquid net as COMPONENTS per topology revision, asserted on the PRODUCTION kernel (../Machinery/RM_LiquidNetKernel.cs) over
// HoseNetChecks' fake graph, plus the production revision hooks read from source (RM_LiquidNet.cs). Gates: a tank between two
// runs is in both and the runs do not merge; tank-hose-tank is one component; machines do not conduct; free-end ports attach;
// every listed event bumps the revision; an over-size component is refused, never partly operated.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class NetComponentChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static List<string> Tanks(RM_NetResult r) => r.Tanks.Cast<string>().ToList();

        public static void Run(Action<string, Action> Case)
        {
            Case("Net_tank_between_two_runs_is_in_both_runs_do_not_merge", () =>
            {
                var g = new HoseNetChecks.G();
                g.Run("ca1", "ca2");
                g.Run("cb1", "cb2");
                HoseNetChecks.G.Add(g.PipeOf, "P1", "ca1");
                HoseNetChecks.G.Add(g.PipeOf, "P2", "cb2");
                HoseNetChecks.G.Add(g.PT, "ca2", "T5");     // T5 touches both runs
                HoseNetChecks.G.Add(g.PT, "cb1", "T5");
                HoseNetChecks.G.Add(g.PT, "cb2", "T6");
                var comps = new RM_NetComponents(g);
                Assert(comps.ComponentsOf("T5").Count == 2, "T5 is a member of both runs (" + comps.ComponentsOf("T5").Count + ")");
                Assert(comps.ComponentsOf("P1")[0] != comps.ComponentsOf("P2")[0], "the two runs stay two components");
                Assert(Tanks(comps.StoreOf("P1")).SequenceEqual(new[] { "T5" }), "P1 (run a) holds T5 only, never run b's T6: " + string.Join(",", Tanks(comps.StoreOf("P1"))));
                Assert(Tanks(comps.StoreOf("P2")).SequenceEqual(new[] { "T5", "T6" }), "P2 (run b) holds T5 and T6");
                // can-fail: join the runs with a pipe and P1 sees T6
                g.Run("ca2", "cb1");
                Assert(Tanks(new RM_NetComponents(g).StoreOf("P1")).Contains("T6"), "can-fail: a pipe joining the runs merges them");
            });

            Case("Net_tank_hose_tank_is_one_component_of_one_conductor", () =>
            {
                var g = new HoseNetChecks.G();
                RM_NetLink l = g.Hose("T1", "T2", "H");
                var comps = new RM_NetComponents(g);
                RM_NetComponent c = comps.ComponentOf(l);
                Assert(c.Links.Count == 1 && c.Nodes.Count == 1 && c.Tanks.SequenceEqual(new object[] { "T1", "T2" }) && !c.Refused,
                    "one hose, two tanks attached (" + c.Nodes.Count + " conductors, tanks " + string.Join(",", c.Tanks) + ")");
                Assert(Tanks(comps.StoreOf("T1")).SequenceEqual(new[] { "T2" }) && Tanks(comps.StoreOf("T2")).SequenceEqual(new[] { "T1" }),
                    "each tank's store is the other, over the hose (ruling #9)");
            });

            Case("Net_machines_do_not_conduct", () =>
            {
                var g = new HoseNetChecks.G();
                g.Hose("P1", "PM1", "x");          // pump -hose-> machine -hose-> tank
                g.Hose("PM1", "T", "y");
                g.Run("c1", "c2", "c3");          // a pipe run with a machine standing on its middle cell
                HoseNetChecks.G.Add(g.PipeOf, "PM2", "c2");
                HoseNetChecks.G.Add(g.PipeOf, "P3", "c1");
                HoseNetChecks.G.Add(g.PT, "c3", "T3");
                var comps = new RM_NetComponents(g);
                Assert(Tanks(comps.StoreOf("P1")).Count == 0 && Tanks(comps.StoreOf("PM1")).SequenceEqual(new[] { "T" }), "a machine at a hose end ends it");
                Assert(comps.ComponentsOf("P1")[0] != comps.ComponentsOf("PM1").Last(), "the machine's two hoses are two components");
                Assert(Tanks(comps.StoreOf("P3")).SequenceEqual(new[] { "T3" }) && comps.ComponentsOf("PM2")[0].Machines.Contains("PM2"),
                    "the pipe run conducts past a machine on it, and the machine is attached as a member");
            });

            Case("Net_free_end_ports_attach_to_their_hose_component", () =>
            {
                var g = new HoseNetChecks.G();
                g.Run("c1", "c2");
                HoseNetChecks.G.Add(g.PipeOf, "P1", "c1");
                var intake = new RM_NetPort { Reel = "R9", Cell = "lake", Role = RM_FreeEndRole.Intake };
                var capped = new RM_NetPort { Reel = "R8", Cell = "yard", Role = RM_FreeEndRole.Capped };
                g.Links.Add(new RM_NetLink { Id = g.Links.Count, A = "c2", B = intake, Reel = "R9" });
                g.Links.Add(new RM_NetLink { Id = g.Links.Count, A = "c2", B = capped, Reel = "R8" });
                var comps = new RM_NetComponents(g);
                RM_NetComponent c = comps.ComponentsOf("P1")[0];
                Assert(c.Ports.Count == 1 && c.Ports[0].Role == RM_FreeEndRole.Intake && c.Links.Count == 2,
                    "an Intake end is a port of the pump's component; a Capped end is not (" + c.Ports.Count + " ports)");
                Assert(comps.RouteIn(c, "P1", intake).Select(x => (string)x.Reel).SequenceEqual(new[] { "R9" }), "the route to a port crosses its own hose");
            });

            Case("Net_store_is_origin_independent_and_route_from_the_tree", () =>
            {
                var g = new HoseNetChecks.G();
                g.Run("c1", "c2", "c3");
                HoseNetChecks.G.Add(g.PipeOf, "P1", "c1");
                HoseNetChecks.G.Add(g.PipeOf, "P2", "c3");
                HoseNetChecks.G.Add(g.PT, "c2", "T7");
                HoseNetChecks.G.Add(g.PT, "c3", "T2");
                g.Hose("c3", "T9", "H");
                var first = new RM_NetComponents(g);
                List<string> p1a = Tanks(first.StoreOf("P1"));
                var second = new RM_NetComponents(g);
                second.StoreOf("T9");                         // a different query builds the component first
                List<string> p1b = Tanks(second.StoreOf("P1"));
                Assert(p1a.SequenceEqual(p1b) && p1a.SequenceEqual(new[] { "T2", "T7", "T9" }),
                    "the store does not depend on who asked first: pipe tanks by id, then the hose tank (" + string.Join(",", p1a) + " / " + string.Join(",", p1b) + ")");
                // a long relay chain: one BFS, route = every hose, no per-crossing route copies (G12)
                var chain = new HoseNetChecks.G();
                const int n = 1000;
                chain.Hose("P1", "R0", "h0");
                for (int i = 0; i < n; i++) chain.Hose("R" + i, "R" + (i + 1), "h" + (i + 1));
                chain.Hose("R" + n, "T", "last");
                var sw = Stopwatch.StartNew();
                var cc = new RM_NetComponents(chain);
                RM_NetResult r = cc.StoreOf("P1");
                sw.Stop();
                Assert(Tanks(r).SequenceEqual(new[] { "T" }) && r.Routes["T"].Count == n + 2 && cc.Builds == 1,
                    "a " + (n + 2) + "-hose relay chain: one build, the route crosses every hose (" + r.Routes["T"].Count + ")");
                Assert(sw.Elapsed.TotalMilliseconds < 50, "and it is linear: " + sw.Elapsed.TotalMilliseconds.ToString("0.0") + " ms (< 50)");
            });

            Case("Net_over_size_component_is_refused_never_partly_operated", () =>
            {
                foreach (int cap in new[] { 40, RM_NetComponents.MaxConductors })
                {
                    var g = new HoseNetChecks.G();
                    int cells = cap + 10;
                    var names = Enumerable.Range(0, cells).Select(i => "c" + i).ToArray();
                    g.Run(names);
                    HoseNetChecks.G.Add(g.PipeOf, "P1", "c0");
                    HoseNetChecks.G.Add(g.PipeOf, "P2", "c" + (cells - 1));
                    HoseNetChecks.G.Add(g.PT, "c1", "TA");
                    HoseNetChecks.G.Add(g.PT, "c" + (cells - 2), "TZ");
                    var comps = new RM_NetComponents(g, cap);
                    RM_NetResult a = comps.StoreOf("P1"), z = comps.StoreOf("P2");
                    Assert(a.Tanks.Count == 0 && z.Tanks.Count == 0 && a.Truncated && z.Truncated && comps.TooLarge("P1") && comps.TooLarge("P2"),
                        "cap " + cap + ": both ends see no store and read too large (" + a.Tanks.Count + "/" + z.Tanks.Count + ")");
                    // queried from the far end first, it is refused just the same
                    var comps2 = new RM_NetComponents(g, cap);
                    Assert(comps2.StoreOf("P2").Tanks.Count == 0 && comps2.StoreOf("P1").Tanks.Count == 0, "cap " + cap + ": refused whichever end asks first");
                    // can-fail: a run under the cap works end to end
                    var ok = new RM_NetComponents(g, cells + 20);
                    Assert(Tanks(ok.StoreOf("P1")).SequenceEqual(new[] { "TA", "TZ" }) && !ok.TooLarge("P1"), "can-fail: under the cap both tanks are in the store");
                }
            });

            Case("Net_revision_bumps_on_each_listed_event", () =>
            {
                string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
                // spawn / despawn of a pipe, tank or machine (one patch on Building, cached per def)
                RiverSwitchFlipChecks.Has(net, @"\[HarmonyLib\.HarmonyPatch\(typeof\(Building\), nameof\(Building\.SpawnSetup\)\)\][^{]*\{ public static void Postfix\(Building __instance, Map map\) \{ if \(RM_LiquidNet\.ChangesTopology\(__instance\)\) \{ RM_LiquidNet\.Bump\(map\);",
                    "a building spawn with a hydraulic role bumps");
                RiverSwitchFlipChecks.Has(net, @"\[HarmonyLib\.HarmonyPatch\(typeof\(Building\), nameof\(Building\.DeSpawn\)\)\][^{]*\{ public static void Prefix\(Building __instance, out Map __state\) \{ __state = __instance\.Map; \} public static void Postfix\(Building __instance, Map __state\) \{ if \(RM_LiquidNet\.ChangesTopology\(__instance\)\) \{ RM_LiquidNet\.Bump\(__state\);",
                    "a despawn bumps the map it left");
                RiverSwitchFlipChecks.Has(net, @"topoDefs\[t\.def\] = b = RoleOfKind\(t\) != RM_NetRole\.None;", "pipes, tanks and machines (any hydraulic role) count");
                // a reel state, port, coupling or free-end role change: the link signature (backstop) bumps
                RiverSwitchFlipChecks.Has(net, @"return RM_HoseSettings\.enabled && r\?\.parent != null && r\.parent\.Spawned && r\.carry == HoseCarryState\.Laid && r\.lay != null;",
                    "eligibility (carry state, lay) is read by the signature");
                RiverSwitchFlipChecks.Has(net, @"h = RM_LiquidNetKernel\.SigStep\(h, r\.parent\.thingIDNumber, IdOf\(inlet\), IdOf\(far\)\);", "each live reel's inlet and far identity are in the signature");
                RiverSwitchFlipChecks.Has(net, @"if \(built && h == sig\) \{ return; \} sig = h;.*?RM_LiquidNet\.Bump\(map\); \}", "a changed signature rebuilds the links and bumps");
                RiverSwitchFlipChecks.Has(net, @"far = new RM_NetPort \{ Reel = r, Cell = r\.far, Role = role \};", "a free end with a role is a port (its role is in IdOf)");
                RiverSwitchFlipChecks.Has(net, @"return \(\(long\)\(p\.Cell is IntVec3 pc \? pc\.x \* 7919 \+ pc\.z : 0\) << 8\) \^ \(long\)p\.Role", "the port identity includes its role");
                // a settings change: the two switches are part of the revision key
                RiverSwitchFlipChecks.Has(net, @"long key = RM_LiquidNetKernel\.RevisionKey\(s\.revision, RM_MachinerySettings\.universalPipesEnabled, RM_HoseSettings\.enabled\);",
                    "pipes and hoses switches are in the revision key");
                Assert(RM_LiquidNetKernel.RevisionKey(5, true, true) != RM_LiquidNetKernel.RevisionKey(5, false, true)
                       && RM_LiquidNetKernel.RevisionKey(5, true, true) != RM_LiquidNetKernel.RevisionKey(5, true, false)
                       && RM_LiquidNetKernel.RevisionKey(5, true, true) != RM_LiquidNetKernel.RevisionKey(6, true, true), "the key separates every input");
                // nothing per tick: the per-origin per-tick walk cache is gone
                Assert(!net.Contains("RM_NetCache") && !net.Contains("TicksGame, () =>"), "no per-tick walk cache is left in RM_LiquidNet");
                string kernel = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNetKernel.cs"));
                Assert(!kernel.Contains("class RM_NetCache") && !kernel.Contains("static RM_NetResult Walk(") && !kernel.Contains("static RM_NetResult Across("),
                    "RM_NetCache, Walk and Across are deleted from the kernel");
            });
        }
    }
}
