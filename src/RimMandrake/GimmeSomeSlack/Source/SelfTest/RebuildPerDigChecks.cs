// GSS_SNAPSHOT_MEASURE_REBUILD_PER_DIG (live 2026-10-26, BENCH wave 2): a dig anywhere rebuilt every cord, and a rebuild in
// which every cord was reused still cost O(E) (15 ms at E=206, about 70% of it the graph reduce, offline split). The scene is
// the live recipe's lattice (lat.py: conduit rows and columns every 4 cells over 37x37 at 155,150 on a 250x250 map) and the
// live far dig cell 135,120.
//
// The fix: (1) CordBuilder keeps its last graph when the reduce inputs are unchanged (compared exactly); (2) CordReach says
// whether a terrain/roof change at a cell can alter the next Build, so the map component skips the rebuild for a far dig.
// New members are reached by reflection so this file also compiles against the pre-fix builder (the before run).
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class RebuildPerDigChecks
    {
        private static readonly Cell FarDig = new Cell(135, 120);

        internal static CordWorld Lattice(Action<CordWorld> edit = null, bool withMachine = true)
        {
            const int x0 = 155, z0 = 150, size = 37, step = 4;
            var w = new CordWorld(250, 250);
            for (int z = z0; z < z0 + size; z++)
                for (int x = x0; x < x0 + size; x++)
                    if ((z - z0) % step == 0 || (x - x0) % step == 0) w.SetConduit(new Cell(x, z));
            if (withMachine)
            {
                // a battery beside the lattice's south-west corner, wired to it, and a wall run the corner cord passes
                w.Machines.Add(new MachineInfo { Id = "Battery1", Kind = MachineKind.Battery, X0 = 150, Z0 = 150, W = 2, H = 3, Hookups = new List<Cell> { new Cell(155, 150) } });
                for (int x = 160; x < 166; x++) w.SetBlocked(new Cell(x, 147), BlockKind.Wall);
            }
            edit?.Invoke(w);
            return w;
        }

        private static object Reach(CordBuilder b) =>
            typeof(CordBuilder).GetProperty("Reach", BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance)?.GetValue(b);

        private static bool? Reaches(CordBuilder b, Cell c)
        {
            object r = Reach(b);
            if (r == null) return null;
            return (bool)r.GetType().GetMethod("Reaches").Invoke(r, new object[] { c });
        }

        internal static void Run()
        {
            var opt = new BuildOptions();
            var b = new CordBuilder();
            var sw = Stopwatch.StartNew();
            List<LaidPiece> first = b.Build(Lattice(), opt, c => true);
            double tFirst = sw.Elapsed.TotalMilliseconds;
            CordGraph g0 = b.Graph;
            int edges = b.LastPlanned;
            Program.Check(edges >= 150, $"rebuild-per-dig: the lattice lays {edges} cord edges (expected the live recipe's ~200)");

            // all-reused: a fresh snapshot of the same map must not re-reduce the graph, and re-lays nothing
            double best = double.MaxValue;
            List<LaidPiece> again = null;
            for (int i = 0; i < 5; i++)
            {
                CordWorld w2 = Lattice();
                sw.Restart();
                again = b.Build(w2, opt, c => true);
                best = Math.Min(best, sw.Elapsed.TotalMilliseconds);
            }
            Program.Check(ReferenceEquals(b.Graph, g0), "rebuild-per-dig: an all-reused Build re-reduced the graph (O(conduit cells) per dirty event, 70% of the live 15 ms)");
            Program.Check(b.LastPlanned == 0 && b.LastReused == edges, $"rebuild-per-dig: all-reused Build planned {b.LastPlanned} reused {b.LastReused} of {edges}");
            Program.Check(GssFuzz.Digest(again) == GssFuzz.Digest(first), "rebuild-per-dig: an all-reused Build changed the cords");
            sw.Restart();
            CordGraph.Reduce(Lattice(), opt.Seed);
            double tReduce = sw.Elapsed.TotalMilliseconds;
            Console.WriteLine($"rebuild-per-dig: E={edges} first Build {tFirst:0.0} ms, all-reused Build {best:0.00} ms (one graph reduce alone {tReduce:0.00} ms)");

            // (1) the live far dig (15+ cells from any conduit) is outside the reach; cells under and beside the cords are inside
            Program.Check(Reaches(b, FarDig) == false, "rebuild-per-dig: the live far dig cell 135,120 reaches the cords (a dig anywhere rebuilds)");
            Program.Check(Reaches(b, new Cell(171, 166)) == true, "rebuild-per-dig: a conduit cell does not reach");
            Program.Check(Reaches(b, new Cell(162, 147)) == true, "rebuild-per-dig: the wall beside the battery cord does not reach");
            Program.Check(Reaches(b, new Cell(151, 151)) == true, "rebuild-per-dig: the battery's footprint does not reach");
            Program.Check(Reaches(b, new Cell(155 + 36 + 4, 150 + 18)) == true, "rebuild-per-dig: a cell 4 east of the lattice edge does not reach (margin 3 + block rounding)");

            // a far dig really is invisible to the Build: same graph, same cords as a fresh builder on the dug map
            CordWorld dug = Lattice(w => { w.SetBlocked(FarDig, BlockKind.Water); w.SetBlocked(new Cell(136, 120), BlockKind.Water); });
            List<LaidPiece> afterFar = b.Build(dug, opt, c => true);
            Program.Check(ReferenceEquals(b.Graph, g0) && b.LastPlanned == 0, "rebuild-per-dig: a far dig changed the graph or re-planned a cord");
            Program.Check(GssFuzz.Digest(afterFar) == GssFuzz.Digest(new CordBuilder().Build(Lattice(w => { w.SetBlocked(FarDig, BlockKind.Water); w.SetBlocked(new Cell(136, 120), BlockKind.Water); }), opt, c => true)),
                          "rebuild-per-dig: far dig incremental != fresh");

            // a dig UNDER a conduit must still change the graph (buried kind) and match a fresh build
            Action<CordWorld> under = w => w.SetBlocked(new Cell(171, 166), BlockKind.Water);
            List<LaidPiece> afterUnder = b.Build(Lattice(under), opt, c => true);
            Program.Check(!ReferenceEquals(b.Graph, g0), "rebuild-per-dig: a dig under a conduit reused the stale graph");
            Program.Check(GssFuzz.Digest(afterUnder) == GssFuzz.Digest(new CordBuilder().Build(Lattice(under), opt, c => true)), "rebuild-per-dig: dig under a conduit incremental != fresh");

            // a machine edit (inputs beyond conduit cells) and a removed conduit re-reduce too, and match fresh
            CordGraph g1 = b.Graph;
            Action<CordWorld> moved = w => { under(w); w.Machines[0].HasHome = true; w.Machines[0].HomeX = 150; w.Machines[0].HomeZ = 149; };
            List<LaidPiece> afterMach = b.Build(Lattice(moved), opt, c => true);
            Program.Check(!ReferenceEquals(b.Graph, g1), "rebuild-per-dig: a re-homed machine reused the stale graph");
            Program.Check(GssFuzz.Digest(afterMach) == GssFuzz.Digest(new CordBuilder().Build(Lattice(moved), opt, c => true)), "rebuild-per-dig: machine edit incremental != fresh");
            CordGraph g2 = b.Graph;
            Action<CordWorld> cut = w => { moved(w); w.SetConduit(new Cell(173, 166), false); };
            List<LaidPiece> afterCut = b.Build(Lattice(cut), opt, c => true);
            Program.Check(!ReferenceEquals(b.Graph, g2), "rebuild-per-dig: a removed conduit reused the stale graph");
            Program.Check(GssFuzz.Digest(afterCut) == GssFuzz.Digest(new CordBuilder().Build(Lattice(cut), opt, c => true)), "rebuild-per-dig: removed conduit incremental != fresh");

            // reduce options are graph inputs: turning tangles off must re-reduce
            CordGraph g3 = b.Graph;
            var noTangles = new BuildOptions { Tangles = false };
            List<LaidPiece> afterOpt = b.Build(Lattice(cut), noTangles, c => true);
            Program.Check(!ReferenceEquals(b.Graph, g3), "rebuild-per-dig: a reduce option change reused the stale graph");
            Program.Check(GssFuzz.Digest(afterOpt) == GssFuzz.Digest(new CordBuilder().Build(Lattice(cut), noTangles, c => true)), "rebuild-per-dig: option change incremental != fresh");

            // a whole-map corridor (a diving cord) makes every cell reach
            object r = Reach(b);
            if (r != null)
            {
                var cr = (CordReach)r;
                var all = new CordReach(250, 250);
                all.AddAll();
                Program.Check(all.Reaches(FarDig) && !cr.All, "rebuild-per-dig: AddAll did not make the far cell reach, or the lattice reach is All");
            }
            Soundness();
        }

        /// <summary>The reach is a promise the map component acts on (it skips the rebuild): over the cord fuzz's worlds, any
        /// terrain/tree change confined to cells outside the reach must leave a fresh Build's cords bit-identical.</summary>
        private static void Soundness()
        {
            int worlds = 0, probed = 0, bad = 0;
            string first = null;
            foreach (var (seed, step, w, opt, live) in GssFuzz.CordWorlds(30))
            {
                var b = new CordBuilder();
                ulong before = GssFuzz.Digest(b.Build(w, opt, live));
                object r = Reach(b);
                if (r == null) { bad++; first ??= "no reach"; break; }
                var reach = (CordReach)r;
                var rng = CordRng.Of("reachprobe", seed, step);
                int n = 0;
                for (int t = 0; t < 400 && n < 24; t++)
                {
                    var c = new Cell(rng.Int(0, w.Width - 1), rng.Int(0, w.Height - 1));
                    if (reach.Reaches(c)) continue;
                    n++;
                    switch (t % 4)
                    {
                        case 0: w.SetBlocked(c, BlockKind.Wall); break;
                        case 1: w.SetBlocked(c, BlockKind.Water); break;
                        case 2: w.SetBlocked(c, BlockKind.None); break;
                        default: w.SetExtraCost(c, 1.5f); break;
                    }
                }
                worlds++;
                probed += n;
                if (n == 0) continue;
                ulong after = GssFuzz.Digest(new CordBuilder().Build(w, opt, live));
                if (after != before) { bad++; first ??= $"seed {seed} step {step}"; }
            }
            Program.Check(bad == 0, $"rebuild-per-dig: a change outside the reach altered the cords ({bad} worlds, first {first})");
            Program.Check(probed > 200, $"rebuild-per-dig: soundness probed only {probed} out-of-reach cells over {worlds} worlds (instrument blind)");
            Console.WriteLine($"rebuild-per-dig: reach soundness {worlds} worlds, {probed} out-of-reach cells changed, {bad} altered");
        }
    }
}
