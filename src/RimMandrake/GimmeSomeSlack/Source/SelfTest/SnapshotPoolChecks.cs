// GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS round 10 (live round 9: a first slice of 44.6 ms with no collection counted, 20.5 ms
// of it the per-rebuild clone of the snapshot base into a new whole-map world). SnapshotPool refills a retired world in place.
// What must hold: (1) a pooled world reads exactly as a clone of its source; (2) a world the builder may still read -- its
// graph's, a running lay batch's, a running or landed graph job's -- is never refilled; (3) the live recipe built through the
// pool ends bit-identical to the same recipe with a fresh world per frame; (4) a steady pooled snapshot allocates nothing.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class SnapshotPoolChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "snapshot-pool: " + msg);

        /// <summary>Every accessor a reader uses, over every cell, plus the machines: "" when equal, else the first difference.</summary>
        internal static string Diff(CordWorld a, CordWorld b)
        {
            if (a.Width != b.Width || a.Height != b.Height) return "size";
            if (a.HasBands != b.HasBands) return "HasBands";
            if (a.HasBusy != b.HasBusy) return "HasBusy";
            for (int z = 0; z < a.Height; z++)
                for (int x = 0; x < a.Width; x++)
                {
                    var c = new Cell(x, z);
                    if (a.IsConduit(c) != b.IsConduit(c)) return "conduit " + c;
                    if (a.BlockAt(c) != b.BlockAt(c)) return "block " + c;
                    if (a.IsDoor(c) != b.IsDoor(c)) return "door " + c;
                    if (a.ExtraCost(c) != b.ExtraCost(c)) return "cost " + c;
                    if (a.IsBuried(c) != b.IsBuried(c)) return "buried " + c;
                    if (a.IsBusy(c) != b.IsBusy(c)) return "busy " + c;
                    if (a.BandAt(c) != b.BandAt(c)) return "band " + c;
                    if (a.LinkMask(c) != b.LinkMask(c)) return "links " + c;
                }
            if (a.Machines.Count != b.Machines.Count) return "machines";
            for (int i = 0; i < a.Machines.Count; i++) if (!ReferenceEquals(a.Machines[i], b.Machines[i])) return "machine " + i;
            return "";
        }

        private static CordWorld Rich(int seed, int w = 40, int h = 30)
        {
            var r = new Random(seed);
            var o = new CordWorld(w, h);
            for (int i = 0; i < 300; i++)
            {
                var c = new Cell(r.Next(w), r.Next(h));
                switch (r.Next(7))
                {
                    case 0: o.SetConduit(c); break;
                    case 1: o.SetBlocked(c, (BlockKind)(1 + r.Next(5))); break;
                    case 2: o.SetDoor(c); break;
                    case 3: o.SetExtraCost(c, 1.5f); break;
                    case 4: o.SetBusy(c); break;
                    case 5: o.SetBand(c, 1 + r.Next(3)); break;
                    default: o.SetForcedBuried(c); break;
                }
            }
            if (seed % 2 == 0) o.LinkBands(new Cell(1, 1), new Cell(1, 2));
            o.Machines.Add(new MachineInfo { Id = "m" + seed, Kind = MachineKind.Lamp, X0 = 2, Z0 = 2, Hookups = new List<Cell> { new Cell(2, 2) } });
            return o;
        }

        internal static void Run()
        {
            // (1) a refilled world reads as a clone, whatever the retired world held (bands/busy set or not, either way round)
            var pool = new SnapshotPool();
            CordWorld first = pool.Take(Rich(1), null);
            Check(pool.Allocated == 1 && pool.Reused == 0, "an empty pool clones");
            CordWorld last = first;
            for (int s = 2; s < 12; s++)
            {
                CordWorld src = s % 3 == 0 ? new CordWorld(40, 30) : Rich(s);
                pool.Retire(last);
                CordWorld got = pool.Take(src, null);
                Check(ReferenceEquals(got, last), $"seed {s}: the retired world is refilled, not a new one");
                string d = Diff(got, src.Clone());
                Check(d == "", $"seed {s}: a refilled world reads as src.Clone() (first difference: {d})");
                Check(!ReferenceEquals(got, src), $"seed {s}: never hands out the source itself");
                last = got;
            }
            pool.Retire(new CordWorld(10, 10));
            CordWorld other = pool.Take(Rich(3), null);
            Check(other.Width == 40 && pool.Count == 1, "a retired world of another size is never refilled");
            for (int i = 0; i < SnapshotPool.Cap + 3; i++) pool.Retire(new CordWorld(40, 30));
            Check(pool.Count == SnapshotPool.Cap, $"the pool keeps at most {SnapshotPool.Cap} worlds (has {pool.Count})");

            HeldChecks();
            Identical();
            NoGarbage();
        }

        /// <summary>(2) worker-held worlds: a graph job blocked on the worker, a lay batch blocked on the worker, the adopted graph.</summary>
        private static void HeldChecks()
        {
            Func<Cell, bool> live = c => false;
            var b = new CordBuilder();
            CordWorld w0 = CordScaleBench.World(0, 0, 0);
            b.Build(w0, new BuildOptions(), live);
            var pool = new SnapshotPool();
            pool.Retire(w0);
            Check(!ReferenceEquals(pool.Take(CordScaleBench.World(0, 0, 0), b), w0), "the current graph's world is never refilled");

            // a changed graph goes to the graph worker, which is held mid-job
            var gate = new ManualResetEventSlim(false);
            b.GraphJobHook = () => gate.Wait(20000);
            CordWorld w1 = CordScaleBench.World(0, 60, 0);
            b.Build(w1, new BuildOptions { AsyncLay = true }, live);
            Check(b.GraphWorkerBusy, "setup: the graph job is running");
            pool = new SnapshotPool();
            pool.Retire(w1);
            CordWorld t1 = pool.Take(CordScaleBench.World(0, 60, 0), b);
            Check(!ReferenceEquals(t1, w1), "a running graph job's world is never refilled");
            gate.Set();
            for (int i = 0; i < 2000 && b.GraphWorkerBusy; i++) Thread.Sleep(5);
            b.GraphJobHook = null;
            pool = new SnapshotPool();
            pool.Retire(w1);
            Check(!ReferenceEquals(pool.Take(CordScaleBench.World(0, 60, 0), b), w1), "a landed (not yet adopted) graph's world is never refilled");

            // the next Build adopts that graph and queues the lays on the lay worker, held on its first edge
            var layGate = new ManualResetEventSlim(false);
            b.WorkerLayHook = k => layGate.Wait(20000);
            CordWorld w2 = CordScaleBench.World(0, 60, 0);
            b.Build(w2, new BuildOptions { AsyncLay = true }, live);
            Check(b.LayWorkerBusy, "setup: the lay batch is running");
            pool = new SnapshotPool();
            pool.Retire(w2);
            pool.Retire(w1);
            CordWorld t2 = pool.Take(CordScaleBench.World(0, 60, 0), b);
            Check(!ReferenceEquals(t2, w2) && !ReferenceEquals(t2, w1), "a running lay batch's world and its graph's world are never refilled");
            layGate.Set();
            for (int i = 0; i < 4000 && b.LayRunning; i++) Thread.Sleep(5);
            b.WorkerLayHook = null;
            pool = new SnapshotPool();
            pool.Retire(w2);
            CordWorld t3 = pool.Take(CordScaleBench.World(0, 60, 0), b);
            Check(ReferenceEquals(t3, w2), "once the lay batch ended, its world (not the graph's) is refilled again");
        }

        /// <summary>(3) the live recipe (lattice 1 over lattice 0, conduits then lamps, an AsyncLay Build per frame) through
        /// the pool ends with the same pieces as with a fresh world per frame.</summary>
        private static void Identical()
        {
            List<string> Recipe(bool pooled)
            {
                Func<Cell, bool> live = c => false;
                var b = new CordBuilder();
                var pool = new SnapshotPool();
                CordWorld prev = null;
                CordWorld Snap(int nc, int nl)
                {
                    CordWorld src = CordScaleBench.World(1, nc, nl);
                    if (!pooled) return src;
                    CordWorld w = pool.Take(src, b);
                    pool.Retire(prev);
                    prev = w;
                    return w;
                }
                b.Build(Snap(0, 0), new BuildOptions(), live);
                var (cells, lamps) = CordScaleBench.Lattice(1);
                int c = 0, l = 0;
                List<LaidPiece> outp = null;
                var t0 = DateTime.UtcNow;
                while ((DateTime.UtcNow - t0).TotalSeconds < 240)
                {
                    if (c < cells.Count) c = Math.Min(cells.Count, c + 25);
                    else if (l < lamps.Count) l = Math.Min(lamps.Count, l + 6);
                    outp = b.Build(Snap(c, l), new BuildOptions { AsyncLay = true }, live);
                    if (c == cells.Count && l == lamps.Count && b.LastPending == 0 && !b.LayRunning) break;
                    Thread.Sleep(2);
                }
                Check(pooled ? pool.Reused > 0 : true, $"pooled run reused worlds (reused {pool.Reused}, allocated {pool.Allocated})");
                return GssFuzz.Sigs(outp);
            }
            List<string> fresh = Recipe(false), pooled2 = Recipe(true);
            Check(fresh.Count > 0 && fresh.SequenceEqual(pooled2), $"pooled snapshots build the same pieces as fresh ones ({fresh.Count} vs {pooled2.Count})");
        }

        /// <summary>(4) a steady pooled snapshot of a 325 map allocates nothing; the clone it replaces allocates the whole map.</summary>
        private static void NoGarbage()
        {
            CordWorld src = CordScaleBench.World(2, 0, 0);
            src.SetBusy(new Cell(5, 5));
            var pool = new SnapshotPool();
            CordWorld prev = null;
            for (int i = 0; i < 3; i++) { CordWorld w = pool.Take(src, null); pool.Retire(prev); prev = w; }
            long a0 = GC.GetAllocatedBytesForCurrentThread();
            for (int i = 0; i < 20; i++) { CordWorld w = pool.Take(src, null); pool.Retire(prev); prev = w; }
            long pooled = (GC.GetAllocatedBytesForCurrentThread() - a0) / 20;
            a0 = GC.GetAllocatedBytesForCurrentThread();
            CordWorld cl = src.Clone();
            long clone = GC.GetAllocatedBytesForCurrentThread() - a0;
            Console.WriteLine($"snapshot-pool: bytes per snapshot copy, 325 map: clone {clone}, pooled {pooled}");
            Check(pooled < 1024, $"a steady pooled snapshot allocates under 1 KB (allocated {pooled} B; a clone {clone} B)");
            Check(clone > 500_000, $"sanity: the instrument sees a whole-map clone ({clone} B)");
            GC.KeepAlive(cl);
        }
    }
}
