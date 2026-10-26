// GSS_PLAN_FIX_SECOND_PER_FULL_BUILD + GSS_SNAPSHOT_MEASURE_REBUILD_PER_DIG round 3 (live round 4, 2026-10-26).
// (1) A planned build of the live scene (E=248) held one frame ~1 s on Mono (offline .NET 8: ~225 ms, 97% of it the per-strand
//     settle in CordLayer.Sprawl). A budgeted Build lays edges until its budget is spent and leaves the rest to the next Build;
//     the run of Builds must end bit-identical to one unbudgeted Build, and no slice may hold a frame.
// (2) A far dig left the live probe's farSkips unmoved: the skip was counted only when our section layer regenerated, which
//     vanilla does for on-screen sections only. RebuildGate counts it when the dirty event is classified.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class SliceGateChecks
    {
        /// <summary>The slice bound: the game's frame budget (8 ms) plus one worst edge and the node/reach tail, well under
        /// the 20 ms the live re-measure requires.</summary>
        private const double BudgetMs = 8.0, SliceBoundMs = 20.0;

        internal static void Run()
        {
            Slices();
            AsyncSlices();
            GraphWorker();
            Gate();
        }

        /// <summary>GSS_SLICE_FIX_EDGE_OVERSHOOTS_BUDGET: a run of AsyncLay Builds, waiting between them for the worker the way
        /// frames do. Returns the Builds, the slowest one (caller ms), the edges any Build laid on the caller, the fewest edge
        /// pieces any Build showed, and the last Build's pieces.</summary>
        private static (int builds, double worst, int onCaller, int minEdgePieces, List<LaidPiece> last) ConvergeAsync(
            CordBuilder b, Func<CordWorld> world, Func<BuildOptions> opt, Func<Cell, bool> live, Action<int> between = null)
        {
            int builds = 0, onCaller = 0, minPieces = int.MaxValue;
            double worst = 0;
            List<LaidPiece> outp;
            var sw = new Stopwatch();
            var wait = Stopwatch.StartNew();
            while (true)
            {
                CordWorld w = world();
                BuildOptions o = opt();
                o.AsyncLay = true;
                sw.Restart();
                outp = b.Build(w, o, live);
                worst = Math.Max(worst, sw.Elapsed.TotalMilliseconds);
                builds++;
                onCaller += b.LastLaidOnCaller;
                minPieces = Math.Min(minPieces, outp.Count(p => p.EndA != null));
                if (b.LastPending == 0 || wait.Elapsed.TotalSeconds > 120) break;
                between?.Invoke(builds);
                // a frame later: the worker has landed something, or stopped (then the next Build queues what is left)
                System.Threading.Thread.Sleep(2);
                while (!b.LayReady) System.Threading.Thread.Sleep(1);
            }
            return (builds, worst, onCaller, minPieces, outp);
        }

        private static void AsyncSlices()
        {
            // a mixed live function: the worker answers isLive from the two endpoint flags the caller copied
            Func<Cell, bool> live = c => ((c.X * 7 + c.Z * 3) & 1) == 0;
            int miss0 = CordBuilder.LiveMisses;
            List<LaidPiece> fullCold = new CordBuilder().Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), live);
            ulong want = GssFuzz.Digest(fullCold);
            int edges = fullCold.Count(p => p.EndA != null);
            var reused = new CordBuilder();
            reused.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), live);
            var swr = Stopwatch.StartNew();
            reused.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), live);
            double reusedMs = swr.Elapsed.TotalMilliseconds;

            // (1) cold: the frame's Build lays no edge itself, so its cost is an all-reused Build's whatever one edge costs
            var b = new CordBuilder();
            var r = ConvergeAsync(b, () => RebuildPerDigChecks.LiveScene(), () => new BuildOptions(), live);
            Program.Check(r.onCaller == 0, $"async: the frame Builds laid {r.onCaller} edges on the caller (must be 0: one edge alone cost up to 28 ms live)");
            Program.Check(r.builds > 1 && b.LayBatches >= 1, $"async: the cold build finished in {r.builds} Build, {b.LayBatches} batches (the worker never ran: instrument blind)");
            Program.Check(b.LastPending == 0 && GssFuzz.Digest(r.last) == want, "async: the worker-laid Builds did not end bit-identical to one unbudgeted Build");
            Program.Check(r.worst <= SliceBoundMs, $"async: one frame Build held {r.worst:0.0} ms (bound {SliceBoundMs} ms)");
            Program.Check(CordBuilder.LiveMisses == miss0, $"async: a worker lay asked isLive {CordBuilder.LiveMisses - miss0} times outside its endpoints");
            Program.Check(b.LastLayFault == null, "async: a worker lay threw: " + b.LastLayFault);
            Console.WriteLine($"async: cold E={edges} over {r.builds} Builds / {b.LayBatches} batches, worst frame Build {r.worst:0.00} ms, all-reused Build {reusedMs:0.00} ms, laid on caller {r.onCaller}");

            // (2) every key changes at once: each edge keeps showing its previous cord until its new one lands
            Func<BuildOptions> slack8 = () => { var o = new BuildOptions(); o.Lay.SlackScale *= 0.8; return o; };
            ulong want2 = GssFuzz.Digest(new CordBuilder().Build(RebuildPerDigChecks.LiveScene(), slack8(), live));
            var r2 = ConvergeAsync(b, () => RebuildPerDigChecks.LiveScene(), slack8, live);
            Program.Check(r2.onCaller == 0 && r2.builds > 1, $"async: an all-keys-changed re-lay laid {r2.onCaller} on the caller over {r2.builds} Builds");
            Program.Check(GssFuzz.Digest(r2.last) == want2, "async: the all-keys-changed re-lay did not end bit-identical to one unbudgeted Build");
            Program.Check(r2.minEdgePieces == edges, $"async: a mid-re-lay Build showed {r2.minEdgePieces} of {edges} cords (a waiting edge must keep its previous piece)");

            // (3) the world moves under a running batch: a wall dropped onto a cord after the first Builds. A landed piece
            //     laid against the old world must fail the corridor check and be laid again, ending equal to the new world's
            //     unbudgeted Build; the settings move back too, so the batch's remaining keys go stale (skipped, not applied)
            var b3 = new CordBuilder();
            List<LaidPiece> pieces0 = new CordBuilder().Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), live);
            Cell wall = default(Cell);
            bool found = false;
            CordWorld probe = RebuildPerDigChecks.LiveScene();
            foreach (LaidPiece p in pieces0.Where(p => p.EndA != null && p.Strands.Count > 0))
            {
                var pts = p.Strands[0].Pts;
                Cell c = pts[pts.Count / 2].Floor;
                if (probe.IsWalkable(c) && !probe.IsConduit(c)) { wall = c; found = true; break; }
            }
            Program.Check(found, "async: no walkable non-conduit cord cell to wall over (scene changed?)");
            Action<CordWorld> drop = w => w.SetBlocked(wall, BlockKind.Wall);
            ulong want3 = GssFuzz.Digest(new CordBuilder().Build(RebuildPerDigChecks.LiveScene(drop), new BuildOptions(), live));
            bool moved = false;
            var r3 = ConvergeAsync(b3, () => moved ? RebuildPerDigChecks.LiveScene(drop) : RebuildPerDigChecks.LiveScene(),
                                   () => moved ? new BuildOptions() : slack8(), live, n => { if (n == 2) moved = true; });
            Program.Check(moved && r3.onCaller == 0, $"async: the moved-world run laid {r3.onCaller} on the caller (moved {moved})");
            Program.Check(b3.LastPending == 0 && GssFuzz.Digest(r3.last) == want3, $"async: after the world moved under a running batch the Builds did not end equal to the new world's unbudgeted Build (pending {b3.LastPending})");

            // (3b) the world moves while the settings stay put: every cache key is unchanged, so only the corridor hash can tell
            //      a landed piece (laid against the old world, not yet taken by a Build) from a good one. A wall dropped onto a
            //      cord between the worker landing and the next Build must refuse that piece (the Build shows nothing for the
            //      edge yet), not adopt it.
            {
                var b3b = new CordBuilder();
                var sw3 = Stopwatch.StartNew();
                // GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS: a fresh builder's first async Build only starts the graph job; the Build
                // after it lands adopts the graph and queues the lays
                b3b.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions { AsyncLay = true }, live);
                while (b3b.LayRunning) { System.Threading.Thread.Sleep(1); if (sw3.Elapsed.TotalSeconds > 120) break; }
                b3b.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions { AsyncLay = true }, live);
                Program.Check(b3b.GraphLanded == 1 && b3b.LastPending > 0, $"async: the second Build did not adopt the worker's graph (adopted {b3b.GraphLanded}, pending {b3b.LastPending})");
                while (!b3b.LayReady || b3b.LayRunning) { System.Threading.Thread.Sleep(1); if (sw3.Elapsed.TotalSeconds > 120) break; }
                var o3b = new BuildOptions { AsyncLay = true };
                var after3b = b3b.Build(RebuildPerDigChecks.LiveScene(drop), o3b, live);
                var stale = pieces0.Where(p => p.EndA != null && p.CX0 <= wall.X && wall.X <= p.CX1 && p.CZ0 <= wall.Z && wall.Z <= p.CZ1).Select(p => p.Key).ToList();
                Program.Check(stale.Count > 0 && b3b.LastLanded > 0, $"async: stale-corridor case is blind (pieces over the wall {stale.Count}, landed {b3b.LastLanded})");
                int adopted = after3b.Count(p => stale.Contains(p.Key));
                Program.Check(adopted == 0, $"async: {adopted} landed piece(s) laid before the wall dropped were adopted despite a changed corridor");
                while (b3b.LayRunning) System.Threading.Thread.Sleep(1);
            }

            // (5) a worker lay that throws: the fault is recorded, the key is not queued again, and the caller lays it itself,
            //     so the Builds still end equal to one unbudgeted Build (a guard-less loop would wait on the key forever)
            {
                Func<BuildOptions> faulty = () => new BuildOptions();
                var b5 = new CordBuilder { WorkerLayHook = k => throw new InvalidOperationException("selftest worker fault") };
                int builds5 = 0, caller5 = 0;
                List<LaidPiece> last5 = null;
                var sw5 = Stopwatch.StartNew();
                while (builds5 < 60 && sw5.Elapsed.TotalSeconds < 120)
                {
                    BuildOptions o5 = faulty();
                    o5.AsyncLay = true;
                    last5 = b5.Build(RebuildPerDigChecks.LiveScene(), o5, live);
                    builds5++;
                    caller5 += b5.LastLaidOnCaller;
                    if (b5.LastPending == 0) break;
                    while (!b5.LayReady) System.Threading.Thread.Sleep(1);
                }
                Program.Check(b5.LastLayFault != null && b5.LastLayFault.Contains("selftest worker fault"), "async: the worker fault was not recorded (LastLayFault " + (b5.LastLayFault ?? "null") + ")");
                Program.Check(b5.LastPending == 0 && builds5 < 60, $"async: a faulted key stayed pending after {builds5} Builds (it must be laid on the caller)");
                Program.Check(caller5 > 0, "async: no faulted edge was laid on the caller");
                Program.Check(last5 != null && GssFuzz.Digest(last5) == want, "async: the Builds after a worker fault did not end equal to one unbudgeted Build");
                while (b5.LayRunning) System.Threading.Thread.Sleep(1);
            }

            // (4) an unbudgeted Build after an async run is still complete and lays on the caller only what it misses
            var u = new CordBuilder();
            u.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions { AsyncLay = true }, live);
            u.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), live);
            Program.Check(u.LastPending == 0 && GssFuzz.Digest(u.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), live)) == want,
                          "async: an unbudgeted Build after an async Build was not complete");
            while (u.LayRunning) System.Threading.Thread.Sleep(1);
        }

        /// <summary>GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS (live round 6: maxSliceMs 18 -> 39 -> 47/75 -> 87/98 ms as lattices piled
        /// up, every edge already laid on the worker): a frame's Build re-reduced the whole map's graph on the caller (offline
        /// 142 of 188 ms at 8 lattices). A changed graph is now reduced on a worker and adopted only under equal inputs.</summary>
        private static void GraphWorker()
        {
            Func<Cell, bool> live = c => ((c.X * 7 + c.Z * 3) & 1) == 0;
            // (1) a lattice spawned over frames beside two finished ones, the world moving under running graph jobs
            {
                const int k = 2;
                var (cells, lamps) = CordScaleBench.Lattice(k);
                ulong want = GssFuzz.Digest(new CordBuilder().Build(CordScaleBench.World(k, cells.Count, lamps.Count), new BuildOptions(), live));
                var b = new CordBuilder();
                b.Build(CordScaleBench.World(k, 0, 0), new BuildOptions(), live);
                int nc = 0, nl = 0, builds = 0, onCaller = 0, callerReduce = 0, waits = 0;
                List<LaidPiece> last = null;
                var sw = Stopwatch.StartNew();
                while (sw.Elapsed.TotalSeconds < 120)
                {
                    if (nc < cells.Count) nc = Math.Min(cells.Count, nc + 40);
                    else if (nl < lamps.Count) nl = Math.Min(lamps.Count, nl + 6);
                    int adopted = b.GraphLanded;
                    last = b.Build(CordScaleBench.World(k, nc, nl), new BuildOptions { AsyncLay = true }, live);
                    builds++;
                    onCaller += b.LastLaidOnCaller;
                    if (b.LastGraphPending) waits++;
                    else if (!b.LastGraphReused && b.GraphLanded == adopted) callerReduce++;
                    if (nc == cells.Count && nl == lamps.Count && b.LastPending == 0 && !b.LayRunning) break;
                    System.Threading.Thread.Sleep(2);
                }
                Program.Check(callerReduce == 0, $"graph worker: {callerReduce} frame Builds reduced the graph on the caller");
                Program.Check(waits > 0 && b.GraphLanded > 0, $"graph worker: blind (waited {waits} Builds, adopted {b.GraphLanded} graphs)");
                Program.Check(b.GraphJobs > b.GraphLanded, $"graph worker: no job went stale under a moving world ({b.GraphJobs} jobs, {b.GraphLanded} adopted): the drop path is unexercised");
                Program.Check(onCaller == 0 && b.LastGraphFault == null, $"graph worker: laid {onCaller} on the caller, fault {b.LastGraphFault ?? "none"}");
                Program.Check(b.LastPending == 0 && last != null && GssFuzz.Digest(last) == want, "graph worker: the spawn did not end bit-identical to one unbudgeted Build of the final map");
                Console.WriteLine($"graph worker: spawn over {builds} Builds, {waits} waited, {b.GraphJobs} jobs, {b.GraphLanded} adopted");
            }
            // (2) a graph job that throws: recorded, and the builder reduces on the caller from then on (where it would throw)
            {
                ulong want = GssFuzz.Digest(new CordBuilder().Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), live));
                var b = new CordBuilder { GraphJobHook = () => throw new InvalidOperationException("selftest graph fault") };
                List<LaidPiece> last = null;
                int builds = 0;
                var sw = Stopwatch.StartNew();
                while (builds < 60 && sw.Elapsed.TotalSeconds < 120)
                {
                    last = b.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions { AsyncLay = true }, live);
                    builds++;
                    if (b.LastPending == 0 && !b.LayRunning) break;
                    while (!b.LayReady) System.Threading.Thread.Sleep(1);
                }
                Program.Check(b.LastGraphFault != null && b.LastGraphFault.Contains("selftest graph fault"), "graph worker: the job fault was not recorded");
                Program.Check(b.LastPending == 0 && last != null && GssFuzz.Digest(last) == want, $"graph worker: after a job fault the Builds did not end equal to one unbudgeted Build ({builds} Builds)");
            }
            // (3) the instrument: the slowest frame Build while a lattice spawns must not grow with the lattices already there
            //     (before the fix: 17 ms beside none, 188 ms beside eight, offline .NET 8)
            {
                CordScaleBench.Row r0 = CordScaleBench.Measure(0), r8 = CordScaleBench.Measure(8);
                Program.Check(r8.WorstNoGcMs <= SliceBoundMs && r8.P95Ms <= BudgetMs,
                              $"graph worker: beside 8 lattices (E={r8.Edges}) the worst frame Build held {r8.WorstNoGcMs:0.0} ms GC-excluded (bound {SliceBoundMs}), p95 {r8.P95Ms:0.0} ms (bound {BudgetMs})");
                Console.WriteLine($"graph worker: spawn frame Build worst (GC-excluded) / p95: beside 0 lattices {r0.WorstNoGcMs:0.00} / {r0.P95Ms:0.00} ms, beside 8 (E={r8.Edges}) {r8.WorstNoGcMs:0.00} / {r8.P95Ms:0.00} ms");
            }
        }

        private static (int slices, double worst, List<LaidPiece> last, int minEdgePieces) Converge(CordBuilder b, CordWorld w, BuildOptions opt, Func<Cell, bool> live)
        {
            int slices = 0, minPieces = int.MaxValue;
            double worst = 0;
            List<LaidPiece> outp = null;
            var sw = new Stopwatch();
            do
            {
                sw.Restart();
                outp = b.Build(w, opt, live);
                worst = Math.Max(worst, sw.Elapsed.TotalMilliseconds);
                slices++;
                minPieces = Math.Min(minPieces, outp.Count(p => p.EndA != null));
            } while (b.LastPending > 0 && slices < 2000);
            return (slices, worst, outp, minPieces);
        }

        private static void Slices()
        {
            Func<Cell, bool> dead = c => false;
            ulong want = GssFuzz.Digest(new CordBuilder().Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), dead));
            int edges = new CordBuilder().Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), dead).Count(p => p.EndA != null);

            // a cold planned build (the first build on a loaded map, a lattice placed at once)
            var opt = new BuildOptions { LayBudgetMs = BudgetMs };
            var b = new CordBuilder();
            var (slices, worst, last, _) = Converge(b, RebuildPerDigChecks.LiveScene(), opt, dead);
            Program.Check(worst <= SliceBoundMs, $"slice: a planned build of the live scene (E={edges}) held one Build {worst:0.0} ms (bound {SliceBoundMs} ms, budget {BudgetMs} ms)");
            Program.Check(slices > 1, $"slice: the cold build finished in {slices} Build (the budget never deferred an edge: instrument blind)");
            Program.Check(b.LastPending == 0 && GssFuzz.Digest(last) == want, "slice: the budgeted Builds did not end bit-identical to one unbudgeted Build");
            Console.WriteLine($"slice: cold E={edges} planned over {slices} Builds, worst {worst:0.0} ms (budget {BudgetMs} ms)");

            // every key changes at once (the slack setting moved): until the re-lay completes each edge keeps its previous cord
            var opt2 = new BuildOptions { LayBudgetMs = BudgetMs };
            opt2.Lay.SlackScale *= 0.8;
            var full2 = new BuildOptions();
            full2.Lay.SlackScale = opt2.Lay.SlackScale;
            var (slices2, worst2, last2, minEdges2) = Converge(b, RebuildPerDigChecks.LiveScene(), opt2, dead);
            ulong wantLit = GssFuzz.Digest(new CordBuilder().Build(RebuildPerDigChecks.LiveScene(), full2, dead));
            Program.Check(worst2 <= SliceBoundMs && slices2 > 1, $"slice: an all-keys-changed re-lay held one Build {worst2:0.0} ms over {slices2} Builds");
            Program.Check(GssFuzz.Digest(last2) == wantLit, "slice: the all-keys-changed re-lay did not end bit-identical to one unbudgeted Build");
            Program.Check(minEdges2 == edges, $"slice: a mid-re-lay Build showed {minEdges2} of {edges} cords (a deferred edge must keep its previous piece)");

            // an all-reused Build is never sliced, and an unbudgeted Build never defers
            b.Build(RebuildPerDigChecks.LiveScene(), opt2, dead);
            Program.Check(b.LastPending == 0 && b.LastPlanned == 0, $"slice: an all-reused budgeted Build planned {b.LastPlanned}, pending {b.LastPending}");
            var u = new CordBuilder();
            u.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), dead);
            Program.Check(u.LastPending == 0 && u.LastPlanned == edges, $"slice: an unbudgeted Build planned {u.LastPlanned} of {edges}, pending {u.LastPending}");
        }

        private static string Names(ulong f) => "0x" + f.ToString("X");

        /// <summary>The gate on the live lattice and the live far dig 135,120 (flag bits are arbitrary here: only "inside the
        /// benign set or not" matters). The dig is off screen, so no layer regenerate follows it.</summary>
        private static void Gate()
        {
            const ulong terrain = 1, roofs = 2, buildings = 4, fog = 8, power = 16, ours = 32, benign = terrain | roofs | buildings | fog;
            var b = new CordBuilder();
            b.Build(RebuildPerDigChecks.Lattice(), new BuildOptions(), c => true);
            CordReach reach = b.Reach;
            Func<Cell, bool> nothing = c => false;
            var far = new Cell(135, 120);

            var g = new RebuildGate();
            Program.Check(g.RegenerateNeedsBuild(), "gate: a fresh gate (before any build) skipped the first build");
            g.Published(0);
            bool skip = g.Note(false, terrain, benign, reach, far, nothing, Names);
            Program.Check(skip && g.FarSkips == 1 && g.RelevantEvents == 0, $"gate: an off-screen far dig was not counted as a far skip (skip {skip}, farSkips {g.FarSkips}, relevant {g.RelevantEvents})");
            Program.Check(g.LastFarSkip(Names) == "0x1@135,120", $"gate: lastFarSkip '{g.LastFarSkip(Names)}'");
            Program.Check(!g.RegenerateNeedsBuild() && g.RegenSkips == 1, "gate: a regenerate after only a far dig rebuilt");
            g.Note(false, terrain | roofs, benign, reach, far, nothing, Names);
            Program.Check(g.FarSkips == 2, "gate: a second far dig (terrain + roof) was not counted");

            // our own reprint is benign but not a far skip; a powered far cell, a power-grid event and an in-reach dig are relevant
            g.Note(true, ours, benign, reach, new Cell(171, 166), nothing, Names);
            Program.Check(g.FarSkips == 2 && g.RelevantEvents == 0, "gate: our own section dirtying counted as a far skip or relevant");
            Program.Check(!g.Note(false, buildings, benign, reach, far, c => true, Names), "gate: a conduit built at a far cell was benign");
            g.Published(0);
            Program.Check(!g.Note(false, terrain | power, benign, reach, far, nothing, Names), "gate: a far power-grid event was benign");
            g.Published(0);
            Program.Check(!g.Note(false, terrain, benign, reach, new Cell(171, 166), nothing, Names) && g.RegenerateNeedsBuild(),
                          "gate: a dig under a conduit did not force a rebuild");
            Program.Check(g.LastRelevant == "0x1@171,166 inReach", $"gate: lastRelevant '{g.LastRelevant}'");
            Program.Check(!g.Note(false, terrain, benign, null, far, nothing, Names), "gate: with no reach (before the first build) a far dig was benign");

            // a build that left edges pending keeps the cords stale: the next regenerate must rebuild
            g.Published(3);
            g.Note(false, terrain, benign, reach, far, nothing, Names);
            Program.Check(g.RegenerateNeedsBuild(), "gate: a regenerate while a sliced build was pending skipped the rebuild");
            Console.WriteLine($"gate: farSkips {g.FarSkips}, regenSkips {g.RegenSkips}, relevant {g.RelevantEvents}");
        }
    }
}
