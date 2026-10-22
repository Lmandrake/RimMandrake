// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 2 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P4):
// offline checks on the production dig-break selector (RM_LineDigBreakMath, compiled in), the production commit point
// (RM_MapComponent_Excavation.Deepen and RM_LineDigBreak.cs, read as text) and the production liquid-net kernel
// (RM_NetComponents over HoseNetChecks' fake graph). L1 of the item's verify: dig cancel breaks nothing; dig commit breaks once;
// a repeat commit is idempotent; the liquid net splits where the pipe broke. Each case has a can-fail. NOT proven here: a pawn's
// dig breaking a real pipe in a running game and the net reading two components (L2 live row, owed).
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LineDigBreakChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(System.IO.Path.Combine(rel));

        private static string Body(string src, string signature)
        {
            int a = src.IndexOf(signature, StringComparison.Ordinal);
            Assert(a >= 0, "missing: " + signature);
            int open = src.IndexOf('{', a);
            int depth = 0;
            for (int i = open; i < src.Length; i++)
            {
                if (src[i] == '{') depth++;
                else if (src[i] == '}' && --depth == 0) return src.Substring(a, i - a + 1);
            }
            throw new Exception("unbalanced: " + signature);
        }

        /// <summary>A thing on the dug square: its id, its line tag (null = not a line), and whether it is gone.</summary>
        private sealed class T
        {
            public string Id;
            public LineKind? Kind;
            public bool Gone;
        }

        private static List<T> Square() => new List<T>
        {
            new T { Id = "pipe", Kind = LineKind.RigidPipe },
            new T { Id = "conduit", Kind = LineKind.RigidConduit },
            new T { Id = "cord", Kind = LineKind.FlexCord },
            new T { Id = "hose", Kind = LineKind.Hose },
            new T { Id = "rock", Kind = null },
        };

        /// <summary>One cut on the square, as RM_LineDigBreak.OnDigCommitted does it: select, then destroy (mark gone).</summary>
        private static List<string> Commit(List<T> sq, bool rulesOn, int before, int after)
        {
            List<T> hit = RM_LineDigBreakMath.ToBreak(rulesOn, before, after, sq, t => t.Kind, t => t.Gone);
            foreach (T t in hit) t.Gone = true;
            return hit.Select(t => t.Id).ToList();
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("LineDigBreak_cancelled_or_refused_dig_breaks_nothing", () =>
            {
                List<T> sq = Square();
                Assert(Commit(sq, true, 0, 0).Count == 0, "a dig that did not change the depth (designated, cancelled, cap refused) broke something");
                Assert(Commit(sq, true, 3, 3).Count == 0, "a refused deeper cut broke something");
                Assert(sq.All(t => !t.Gone), "a line went missing without a commit");
                // the commit point: one production call, inside Deepen, after the grid write and after every early return
                string ex = Src("RM_MapComponent_Excavation.cs");
                string deepen = Body(ex, "public byte DeepenWithin(IntVec3 c, int cap)");   // DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL: the one-arg Deepen forwards here
                int write = deepen.IndexOf("depthGrid[i] = d;", StringComparison.Ordinal);
                int call = deepen.IndexOf("RM_LineDigBreak.OnDigCommitted(map, c, before, d)", StringComparison.Ordinal);
                Assert(write > 0 && call > write, "OnDigCommitted is not called after Deepen's grid write");
                Assert(deepen.IndexOf("return", write, StringComparison.Ordinal) > call,
                    "a return sits between the grid write and the break call (a commit could skip the break)");
                int sites = 0;
                foreach (string f in new[] { "RM_MapComponent_Excavation.cs", "Designator_DigCanal.cs", "WorkGiver_DigCanal.cs", "JobDriver_DigCanal.cs", "JobDriver_FillInCanal.cs" })
                {
                    string s = Src(f);
                    for (int i = s.IndexOf("OnDigCommitted(", StringComparison.Ordinal); i >= 0; i = s.IndexOf("OnDigCommitted(", i + 1, StringComparison.Ordinal)) sites++;
                }
                Assert(sites == 1, "the dig break is called from " + sites + " places in the dig code (one: Deepen)");
                // can-fail: a real cut on the same square does break (the zero above is not a blind selector)
                Assert(Commit(sq, true, 0, 1).Count == 3, "sanity: a committed cut broke nothing, so the zeros above prove nothing");
            });

            Case("LineDigBreak_commit_breaks_rigid_and_cords_once_never_hose", () =>
            {
                List<T> sq = Square();
                List<string> got = Commit(sq, true, 0, 1);
                Assert(got.SequenceEqual(new[] { "pipe", "conduit", "cord" }), "a commit broke [" + string.Join(",", got) + "], want pipe,conduit,cord");
                Assert(!sq.First(t => t.Id == "hose").Gone, "a dig destroyed a hose (its re-plan or cut is the hose router's, phase 6)");
                Assert(!sq.First(t => t.Id == "rock").Gone, "a dig destroyed an untagged thing");
                Assert(RM_LineDigBreakMath.BreaksOnDig(LineKind.RigidPipe) && RM_LineDigBreakMath.BreaksOnDig(LineKind.RigidConduit)
                       && RM_LineDigBreakMath.BreaksOnDig(LineKind.FlexCord) && !RM_LineDigBreakMath.BreaksOnDig(LineKind.Hose), "BreaksOnDig table");
                Assert(RM_LineDigBreakMath.Message(0) == null && RM_LineDigBreakMath.Message(1) != null
                       && RM_LineDigBreakMath.Message(3).Contains("3 lines"), "one message per breaking commit, none for a clean one");
                // can-fail: rules off, the same commit leaves every line standing (the pre-ruling behaviour)
                List<T> off = Square();
                Assert(Commit(off, false, 0, 1).Count == 0 && off.All(t => !t.Gone), "rules off still broke lines");
                // production: built lines only, Deconstruct (salvage, no auto-rebuild), behind the setting, counted
                string live = Src("Machinery", "RM_LineDigBreak.cs");
                Assert(live.Contains("RM_MachinerySettings.lineCrossingRulesEnabled"), "the break is not behind lineCrossingRulesEnabled");
                Assert(live.Contains("t.Destroy(DestroyMode.Deconstruct)"), "a broken line is not destroyed in Deconstruct mode");
                string kob = Body(live, "private static LineKind? KindOfBuilt(Thing t)");
                Assert(kob.Contains("t is Blueprint") && kob.Contains("t is Frame") && kob.Contains("RM_LineCrossing.KindOf(t.def)"),
                    "KindOfBuilt must skip blueprints/frames (vanilla cancels them) and read the def tag, never a style");
            });

            Case("LineDigBreak_repeat_commit_is_idempotent", () =>
            {
                List<T> sq = Square();
                Assert(Commit(sq, true, 0, 1).Count == 3, "first commit");
                Assert(Commit(sq, true, 1, 2).Count == 0, "a second (deeper) commit on the same square broke something again");
                Assert(Commit(sq, true, 2, 3).Count == 0, "a third commit broke something again");
                // the same thing listed twice is broken once
                var p = new T { Id = "pipe", Kind = LineKind.RigidPipe };
                var dup = new List<T> { p, p };
                Assert(Commit(dup, true, 0, 1).Count == 1, "a line listed twice was broken twice");
                // can-fail: if 'gone' were ignored, the second commit would break the same three again
                List<T> blind = Square();
                RM_LineDigBreakMath.ToBreak(true, 0, 1, blind, t => t.Kind, t => t.Gone);   // selected but never destroyed
                Assert(RM_LineDigBreakMath.ToBreak(true, 1, 2, blind, t => t.Kind, t => t.Gone).Count == 3,
                    "sanity: a line still standing after a commit is selected again (the idempotence is the 'gone' read)");
                string live = Src("Machinery", "RM_LineDigBreak.cs");
                string on = Body(live, "public static int OnDigCommitted(Map map, IntVec3 c, int depthBefore, int depthAfter)");
                Assert(on.Contains("t => t.Destroyed || !t.Spawned") && on.Contains("if (!t.Destroyed)"),
                    "production teardown does not skip lines already gone");
                Assert(on.Contains("new List<Thing>(c.GetThingList(map))"), "the thing list is not copied before destroying from it");
            });

            Case("LineDigBreak_liquid_net_splits_where_the_pipe_broke", () =>
            {
                // run c1-c2-c3; machine P1 and tank T1 at c1, tank T3 at c3; the dig commits on c2's square
                List<string> before = Store(new[] { "c1", "c2", "c3" });
                Assert(before.SequenceEqual(new[] { "T1", "T3" }), "precondition: one net holds T1 and T3 (" + string.Join(",", before) + ")");
                var sq = new List<T> { new T { Id = "c2", Kind = LineKind.RigidPipe } };
                List<string> broke = Commit(sq, true, 0, 1);
                Assert(broke.SequenceEqual(new[] { "c2" }), "the dig did not break c2");
                string[] alive = new[] { "c1", "c2", "c3" }.Where(c => !broke.Contains(c)).ToArray();
                HoseNetChecks.G g = Graph(alive);
                var comps = new RM_NetComponents(g);
                Assert(comps.ComponentOfNode("c1") != null && comps.ComponentOfNode("c3") != null
                       && comps.ComponentOfNode("c1") != comps.ComponentOfNode("c3"), "c1 and c3 are still one net after c2 broke");
                List<string> after = Store(alive);
                Assert(after.SequenceEqual(new[] { "T1" }), "P1 still reaches T3 across the dug square (" + string.Join(",", after) + ")");
                // can-fail: a hose on c2's square is not broken, so the net stays whole
                var hs = new List<T> { new T { Id = "c2", Kind = LineKind.Hose } };
                Assert(Commit(hs, true, 0, 1).Count == 0 && Store(new[] { "c1", "c2", "c3" }).Count == 2, "sanity: an unbroken run must stay one net");
                // production: the destroy despawns the pipe, and a pipe despawn bumps the net revision
                string net = Src("Machinery", "RM_LiquidNet.cs");
                string desp = Body(net, "public static class RM_Patch_NetTopologyDespawn");
                Assert(net.Contains("[HarmonyLib.HarmonyPatch(typeof(Building), nameof(Building.DeSpawn))]") && desp.Contains("RM_LiquidNet.Bump(__state)"),
                    "a pipe's despawn no longer bumps the liquid net revision, so a dig break would not split the net");
            });
        }

        /// <summary>The fake graph: a straight run over the live cells (adjacent by index), P1 and T1 on c1, T3 on c3.</summary>
        private static HoseNetChecks.G Graph(string[] alive)
        {
            var g = new HoseNetChecks.G();
            var set = new HashSet<string>(alive);
            string[] run = { "c1", "c2", "c3" };
            for (int i = 0; i + 1 < run.Length; i++)
            {
                if (set.Contains(run[i]) && set.Contains(run[i + 1])) g.Run(run[i], run[i + 1]);
            }
            if (set.Contains("c1"))
            {
                HoseNetChecks.G.Add(g.PipeOf, "P1", "c1");
                HoseNetChecks.G.Add(g.PT, "c1", "T1");
            }
            if (set.Contains("c3")) HoseNetChecks.G.Add(g.PT, "c3", "T3");
            return g;
        }

        private static List<string> Store(string[] alive) =>
            new RM_NetComponents(Graph(alive)).StoreOf("P1").Tanks.Cast<string>().OrderBy(s => s).ToList();
    }
}
