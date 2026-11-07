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
        // SyncLayBoundMs is for the budgeted lay on the caller, which the game no longer uses (it lays on a worker, AsyncLay, held to SliceBoundMs below) except for an edge whose
        // worker lay threw. Since a cord can be laid again when it coils on a door or its end (pass 10), one edge there can cost several settles: 20 ms became 30 for that path only.
        private const double BudgetMs = 8.0, SliceBoundMs = 20.0, SyncLayBoundMs = 30.0;

        internal static void Run()
        {
            Slices();
            AsyncSlices();
            AllocBudget();
            GraphWorker();
            SustainedChange();
            Coalesce();
            Window();
            Gate();
        }

        /// <summary>GSS round 9 (live round 8: 40-50 frame rebuilds a second while the worker landed pieces; the slowest slices
        /// were pauses no phase owned, so the lever is fewer slices). LayReadyCoalesced, driven with a chosen clock: it holds
        /// while a graph job runs or nothing landed, opens at CoalescePieces landed, at CoalesceMs of age, at a landed graph
        /// and at the batch's end; a coalesced run of frames rebuilds far less often and still ends bit-identical.</summary>
        private static void Coalesce()
        {
            Func<Cell, bool> live = c => ((c.X * 7 + c.Z * 3) & 1) == 0;
            long sec = Stopwatch.Frequency;
            // (1) the gate's states, the worker held on semaphores so the landed count is the test's
            {
                var graphGo = new System.Threading.SemaphoreSlim(0);
                var layGo = new System.Threading.SemaphoreSlim(0);
                var b = new CordBuilder { GraphJobHook = () => graphGo.Wait(), WorkerLayHook = k => layGo.Wait(), CoalescePieces = 3, CoalesceMs = 100 };
                var sw = Stopwatch.StartNew();
                b.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions { AsyncLay = true }, live);
                bool heldGraph = !b.LayReadyCoalesced(long.MaxValue / 2);
                graphGo.Release();
                while (!b.LayReady && sw.Elapsed.TotalSeconds < 60) System.Threading.Thread.Sleep(1);
                bool openGraph = b.LayReadyCoalesced(0);
                b.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions { AsyncLay = true }, live);
                int pending = b.LastPending;
                bool heldEmpty = !b.LayReadyCoalesced(long.MaxValue / 2);
                layGo.Release(1);
                while (!b.LayReady && sw.Elapsed.TotalSeconds < 60) System.Threading.Thread.Sleep(1);
                // one landed: held at age <= 0 (clock 0 is before it landed), open once it is a second old
                bool heldOne = !b.LayReadyCoalesced(0);
                bool openAged = b.LayReadyCoalesced(Stopwatch.GetTimestamp() + sec);
                layGo.Release(2);
                bool openCount = false;
                while (sw.Elapsed.TotalSeconds < 60) { if (b.LayReadyCoalesced(0)) { openCount = true; break; } System.Threading.Thread.Sleep(1); }
                layGo.Release(100000);
                while (b.LayRunning && sw.Elapsed.TotalSeconds < 60) System.Threading.Thread.Sleep(1);
                bool openEnd = b.LayReadyCoalesced(0);
                Program.Check(pending > 3, $"coalesce: blind, the adopting Build left {pending} edges pending (need more than CoalescePieces)");
                Program.Check(heldGraph && openGraph, $"coalesce: graph job running held {heldGraph}, graph landed opened {openGraph}");
                Program.Check(heldEmpty && heldOne && openAged, $"coalesce: nothing landed held {heldEmpty}, one fresh piece held {heldOne}, one aged piece opened {openAged}");
                Program.Check(openCount && openEnd, $"coalesce: CoalescePieces landed opened {openCount}, batch end opened {openEnd}");
            }
            // (2) frames ~2 ms apart while a slowed worker (2 ms a lay) lands a cold build: rebuild when the per-frame gate
            //     (LayReady) opens, then when the coalesced gate opens. Same final pieces, far fewer rebuilds.
            {
                ulong want = GssFuzz.Digest(new CordBuilder().Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), live));
                int Run(bool coalesced, out ulong dig, out int holds)
                {
                    var b = new CordBuilder { WorkerLayHook = k => System.Threading.Thread.Sleep(2) };
                    int builds = 0;
                    holds = 0;
                    List<LaidPiece> last = null;
                    var sw = Stopwatch.StartNew();
                    while (sw.Elapsed.TotalSeconds < 120)
                    {
                        last = b.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions { AsyncLay = true }, live);
                        builds++;
                        if (b.LastPending == 0 && !b.LayRunning) break;
                        while (sw.Elapsed.TotalSeconds < 120)
                        {
                            System.Threading.Thread.Sleep(2);
                            if (coalesced ? b.LayReadyCoalesced(Stopwatch.GetTimestamp()) : b.LayReady) break;
                            if (b.LayReady) holds++;
                        }
                    }
                    dig = last == null ? 0 : GssFuzz.Digest(last);
                    return builds;
                }
                int perFrame = Run(false, out ulong d0, out _);
                int coal = Run(true, out ulong d1, out int held);
                Program.Check(d0 == want && d1 == want, $"coalesce: the per-frame run ended equal {d0 == want}, the coalesced run {d1 == want} (both must equal one unbudgeted Build)");
                Program.Check(held > 0 && coal * 3 <= perFrame, $"coalesce: {coal} coalesced rebuilds against {perFrame} per-frame ({held} frames held): expected at least 3x fewer");
                Console.WriteLine($"coalesce: cold build rebuilds per-frame {perFrame}, coalesced {coal} ({held} frames held)");
            }
        }

        /// <summary>GSS round 9: the probe's rebuildPhasesMs was the last rebuild's split, not the window maximum's (live round 8
        /// showed 86 ms beside a 6-9 ms split). SliceWindow keeps the max slice's own record and its unattributed gap.</summary>
        private static void Window()
        {
            var w = new SliceWindow();
            long f = 1000;
            w.Reset(0);
            SliceRecord Rec(double total, double build, int gc0)
            {
                var r = new SliceRecord { TotalMs = total, Gc0 = gc0 };
                r.Add("snapBase", 1.0);
                r.Add("build", build);
                r.Add("tail", 0.5);
                return r;
            }
            w.Record(Rec(5, 3, 0), 10, f);
            w.Record(Rec(86, 4, 0), 20, f);      // a pause: the phases sum to 5.5 ms of 86
            w.Record(Rec(165, 2, 1), 30, f);     // a gen-0 collection landed in it
            w.Record(Rec(7, 5, 0), 40, f);       // the LAST slice: what rebuildPhasesMs would have shown
            Program.Check(w.Slices == 4 && w.GcHits == 1, $"slice window: {w.Slices} slices, {w.GcHits} collector hits (want 4, 1)");
            Program.Check(w.Max != null && w.Max.TotalMs == 165 && w.Max.Ordinal == 3, "slice window: the max record is not the 165 ms slice");
            Program.Check(w.MaxNoGc != null && w.MaxNoGc.TotalMs == 86 && w.MaxNoGc.Ordinal == 2 && w.MaxNoGc.Phases[1].Value == 4,
                          "slice window: the uncollected max does not carry its own phases (the 86 ms slice built in 4 ms)");
            Program.Check(Math.Abs(w.MaxNoGc.GapMs - 80.5) < 1e-9 && Math.Abs(w.MaxNoGc.SinceResetMs - 20) < 1e-9,
                          $"slice window: gap {w.MaxNoGc.GapMs} (want 80.5), since reset {w.MaxNoGc.SinceResetMs} ms (want 20)");
            Program.Check(w.First != null && w.First.Ordinal == 1 && w.Json().Contains("\"gapMs\":80.5"), "slice window: first record or JSON gap missing");
            w.Reset(50);
            Program.Check(w.Slices == 0 && w.Max == null && w.MaxNoGc == null && w.First == null, "slice window: Reset kept a record");
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
        /// <summary>GSS_PLAN_FIX_SECOND_PER_FULL_BUILD: under Unity's incremental Boehm collector (boot.config gc-max-time-slice)
        /// an allocation on the frame path pays marking work GC.CollectionCount never sees, and a large one pays by its size: the
        /// live over-bar slices (25.8 ms, every ms in the two allocating phases of a Build whose usual cost is under 0.3 ms) were
        /// that. So the frame Build's allocation is pinned in bytes, a measure a loaded machine cannot move: the changed-graph
        /// hand-off, and an all-reused Build, on 4 lattices of lamps (the live proof's whole scene, E near 1000).</summary>
        private static void AllocBudget()
        {
            const int k = 3;   // three whole lattices and a fourth being spawned
            Func<Cell, bool> live = c => ((c.X * 7 + c.Z * 3) & 1) == 0;
            var (cells, lamps) = CordScaleBench.Lattice(k);
            var opt = new BuildOptions { AsyncLay = true };
            var b = new CordBuilder();
            void Settle(CordWorld w)
            {
                var sw = Stopwatch.StartNew();
                while (sw.Elapsed.TotalSeconds < 120)
                {
                    b.Build(w, opt, live);
                    if (!b.LastGraphPending && b.LastPending == 0 && !b.LayRunning) return;
                    System.Threading.Thread.Sleep(2);
                }
            }
            long Bytes(CordWorld w)
            {
                long a0 = GC.GetAllocatedBytesForCurrentThread();
                b.Build(w, opt, live);
                return GC.GetAllocatedBytesForCurrentThread() - a0;
            }
            CordWorld before = CordScaleBench.World(k, cells.Count, lamps.Count - 6);
            Settle(before);
            long reused = 0;
            for (int i = 0; i < 3; i++) reused = Bytes(before);   // the third: anything a first read memoizes is done
            Program.Check(b.LastReused > 500 && b.LastPlanned == 0 && !b.LastGraphPending, $"alloc budget: blind, the settled Build reused {b.LastReused}, planned {b.LastPlanned}");
            CordWorld after = CordScaleBench.World(k, cells.Count, lamps.Count);
            long handoff = Bytes(after);
            Program.Check(b.LastGraphPending, "alloc budget: blind, the changed world did not take the graph hand-off");
            Console.WriteLine($"alloc budget: E={b.Graph?.Edges.Count} changed-graph hand-off {handoff} bytes, all-reused Build {reused} bytes");
            Program.Check(handoff <= HandoffBytes, $"alloc budget: the changed-graph hand-off allocated {handoff} bytes on the frame (bound {HandoffBytes})");
            Program.Check(reused <= ReusedBytes, $"alloc budget: an all-reused Build allocated {reused} bytes on the frame (bound {ReusedBytes})");
            Settle(after);
        }
        /// <summary>Before the fix, E=980: 76568 and 624552 bytes. After it: 320 and 15256 (twice-ish headroom; a whole-map table is 40 KB up).</summary>
        internal const long HandoffBytes = 4096, ReusedBytes = 32768;

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
            //     (before the fix: 17 ms beside none, 188 ms beside eight, offline .NET 8). GSS_GRAPH_JOB_PROVE_SUSTAINED_CHANGE:
            //     wall-clock ms is a loaded-machine instrument, so it is split. The cause of the regression (whole-map work on
            //     the caller: a graph reduced or an edge laid in a frame Build) is counted and pinned on every attempt; the ms
            //     bounds must hold on one of up to three attempts (a load spike is transient, a regression repeats).
            {
                CordScaleBench.Row r0 = CordScaleBench.Measure(0), best = null;
                int attempts = 0, callerWork = 0;
                bool held = false;
                while (attempts < 3 && !held)
                {
                    CordScaleBench.Row r = CordScaleBench.Measure(8);
                    attempts++;
                    callerWork += r.CallerReduce + r.OnCaller;
                    held = r.WorstNoGcMs <= SliceBoundMs && r.P95Ms <= BudgetMs;
                    if (best == null || held || r.WorstNoGcMs < best.WorstNoGcMs) best = r;
                }
                Program.Check(callerWork == 0, $"graph worker: beside 8 lattices the frame Builds did whole-map work on the caller ({callerWork} reduces + edges over {attempts} attempts)");
                Program.Check(held, $"graph worker: beside 8 lattices (E={best.Edges}) no attempt of {attempts} held the frame: best worst {best.WorstNoGcMs:0.0} ms GC-excluded (bound {SliceBoundMs}), p95 {best.P95Ms:0.0} ms (bound {BudgetMs})");
                Console.WriteLine($"graph worker gate: {attempts} attempt(s), caller work {callerWork}; spawn frame Build worst (GC-excluded) / p95: beside 0 lattices {r0.WorstNoGcMs:0.00} / {r0.P95Ms:0.00} ms, beside 8 (E={best.Edges}) {best.WorstNoGcMs:0.00} / {best.P95Ms:0.00} ms");
            }
        }

        /// <summary>GSS_GRAPH_JOB_PROVE_SUSTAINED_CHANGE (review of 0f395589f2): a landed graph is adopted only when its inputs
        /// equal the Build's, so a map that changes on every frame starves adoption and the cords stay stale. This pins the
        /// tradeoff as a bound counted in Builds and graph jobs, never in ms: (a) through N changing frames, even with the
        /// worker finishing every job before the next frame (its best case), no graph is adopted, nothing is reduced or laid on
        /// the caller, and every frame shows the previous pieces whole (stale, never torn); (b) once the map is quiet the cords
        /// are fresh within QuietBuilds Builds, adopting the job the last change started (no new job), bit-identical to one
        /// unbudgeted Build. So the staleness is the change span plus that one graph job and its lays (QuietBuilds frames when
        /// the worker keeps up); it is not bounded while the change lasts.</summary>
        private static void SustainedChange()
        {
            Func<Cell, bool> live = c => ((c.X * 7 + c.Z * 3) & 1) == 0;
            const int k = 2, QuietBuilds = 2;
            var (cells, lamps) = CordScaleBench.Lattice(k);
            int n = Math.Min(120, cells.Count / 2), nc0 = cells.Count - n;
            var b = new CordBuilder();
            var sw = Stopwatch.StartNew();
            void Idle() { while (b.LayRunning && sw.Elapsed.TotalSeconds < 120) System.Threading.Thread.Sleep(1); }
            // the start: the lattice short of its last n conduits, settled
            ulong want0 = GssFuzz.Digest(new CordBuilder().Build(CordScaleBench.World(k, nc0, lamps.Count), new BuildOptions(), live));
            List<LaidPiece> outp = null;
            for (int i = 0; i < 60; i++)
            {
                outp = b.Build(CordScaleBench.World(k, nc0, lamps.Count), new BuildOptions { AsyncLay = true }, live);
                if (b.LastPending == 0 && !b.LayRunning) break;
                Idle();
            }
            ulong pre = GssFuzz.Digest(outp);
            int preCords = outp.Count(p => p.EndA != null);
            Program.Check(b.LastPending == 0 && pre == want0 && preCords > 0, $"sustained change: the start did not settle equal to one unbudgeted Build ({preCords} cords, pending {b.LastPending})");
            // (a) one more conduit every frame; the worker idles before each frame, so every job lands and is then dropped
            int jobs0 = b.GraphJobs, landed0 = b.GraphLanded, stale = 0, torn = 0, notWaiting = 0, onCaller = 0;
            for (int f = 1; f <= n; f++)
            {
                outp = b.Build(CordScaleBench.World(k, nc0 + f, lamps.Count), new BuildOptions { AsyncLay = true }, live);
                if (!b.LastGraphPending) notWaiting++;
                onCaller += b.LastLaidOnCaller;
                if (GssFuzz.Digest(outp) == pre) stale++; else torn++;
                Idle();
            }
            int jobsDuring = b.GraphJobs - jobs0, landedDuring = b.GraphLanded - landed0;
            Program.Check(jobsDuring == n && landedDuring == 0, $"sustained change: over {n} changing frames {jobsDuring} graph jobs ran (want one a frame: instrument blind otherwise) and {landedDuring} were adopted (want 0: adoption needs equal inputs)");
            Program.Check(notWaiting == 0 && onCaller == 0, $"sustained change: {notWaiting} changing frames did not wait on the worker, {onCaller} edges laid on the caller");
            Program.Check(stale == n && torn == 0, $"sustained change: {torn} of {n} changing frames did not show the previous pieces whole");
            // (b) the map goes quiet (the last changing frame already showed it): the job that frame started is adopted
            ulong want = GssFuzz.Digest(new CordBuilder().Build(CordScaleBench.World(k, cells.Count, lamps.Count), new BuildOptions(), live));
            int jobs1 = b.GraphJobs, landed1 = b.GraphLanded, quiet = 0;
            do
            {
                outp = b.Build(CordScaleBench.World(k, cells.Count, lamps.Count), new BuildOptions { AsyncLay = true }, live);
                quiet++;
                Idle();
            } while ((b.LastPending > 0 || b.LayRunning) && quiet < 60);
            int jobsQuiet = b.GraphJobs - jobs1, landedQuiet = b.GraphLanded - landed1;
            Program.Check(jobsQuiet == 0 && landedQuiet == 1, $"sustained change: once quiet {jobsQuiet} new graph jobs ran and {landedQuiet} were adopted (want 0, 1: the last change's own job)");
            Program.Check(quiet <= QuietBuilds && b.LastPending == 0 && GssFuzz.Digest(outp) == want, $"sustained change: once quiet the cords took {quiet} Builds (bound {QuietBuilds}) and ended equal to one unbudgeted Build {GssFuzz.Digest(outp) == want}");
            Console.WriteLine($"sustained change: {n} changing frames, {jobsDuring} jobs, {landedDuring} adopted, {stale} stale frames ({preCords} cords shown whole); quiet: {jobsQuiet} new job, {landedQuiet} adopted, fresh after {quiet} Builds");
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
            Program.Check(worst <= SyncLayBoundMs, $"slice: a planned build of the live scene (E={edges}) held one Build {worst:0.0} ms (bound {SyncLayBoundMs} ms, budget {BudgetMs} ms)");
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
            Program.Check(worst2 <= SyncLayBoundMs && slices2 > 1, $"slice: an all-keys-changed re-lay held one Build {worst2:0.0} ms over {slices2} Builds");
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
