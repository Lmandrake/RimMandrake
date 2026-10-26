// GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS (live round 6, 2026-10-26): with every edge laid on the worker, the frame's Build still
// grew with the cords already on the map: maxSliceMs 18 -> 39 -> 47/75 -> 87/98 ms over four 469-conduit lattices on the 325
// map. The instrument: k finished lattices already on the map, then one more lattice spawned over frames (conduits in
// batches, then its lamps), an AsyncLay Build per frame. The slowest frame Build must not grow with k.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class CordScaleBench
    {
        private const int Size = 37, Step = 6, Lamp = 3, Pitch = 52, PerRow = 6;

        private static (int x0, int z0) Origin(int i) => (8 + (i % PerRow) * Pitch, 8 + (i / PerRow) * Pitch);

        /// <summary>One live-recipe lattice's conduit cells and lamps, in spawn order.</summary>
        internal static (List<Cell> cells, List<MachineInfo> lamps) Lattice(int i)
        {
            var (x0, z0) = Origin(i);
            var cells = new List<Cell>();
            for (int z = z0; z < z0 + Size; z++)
                for (int x = x0; x < x0 + Size; x++)
                    if ((z - z0) % Step == 0 || (x - x0) % Step == 0) cells.Add(new Cell(x, z));
            var at = new SortedSet<(int, int)>();
            for (int k = 0; k < Size; k += Step)
                for (int j = 0; j < Size; j++)
                    if (j % Step == Lamp) { at.Add((x0 + j, z0 + k)); at.Add((x0 + k, z0 + j)); }
            var lamps = at.Select(p => new MachineInfo
            {
                Id = "c" + (1000 + p.Item1 * 400 + p.Item2), Kind = MachineKind.Lamp, X0 = p.Item1, Z0 = p.Item2,
                Hookups = new List<Cell> { new Cell(p.Item1, p.Item2) }
            }).ToList();
            return (cells, lamps);
        }

        /// <summary>k finished lattices plus the first nCells conduits and nLamps lamps of lattice k: a fresh world, as the
        /// adapter snapshots one per rebuild.</summary>
        internal static CordWorld World(int k, int nCells, int nLamps)
        {
            var w = new CordWorld(325, 325);
            for (int i = 0; i <= k; i++)
            {
                var (cells, lamps) = Lattice(i);
                int nc = i < k ? cells.Count : nCells, nl = i < k ? lamps.Count : nLamps;
                for (int j = 0; j < nc; j++) w.SetConduit(cells[j]);
                for (int j = 0; j < nl; j++)
                    w.Machines.Add(new MachineInfo { Id = lamps[j].Id, Kind = lamps[j].Kind, X0 = lamps[j].X0, Z0 = lamps[j].Z0, Hookups = new List<Cell>(lamps[j].Hookups) });
            }
            return w;
        }

        internal sealed class Row
        {
            public int K, Edges, Frames;
            public double AllReusedMs, WorstMs, Inputs, Reduce, EdgesMs, Keys, Corr, Nodes, Reach;
            public int OnCaller, GcFrames;
            public double WorstNoGcMs, P95Ms;
            public List<(double, string)> Top;
        }

        /// <summary>One k: warm the map, then spawn lattice k over frames (cellBatch conduits, then lampBatch lamps, per frame).</summary>
        internal static Row Measure(int k, int cellBatch = 25, int lampBatch = 6)
        {
            Func<Cell, bool> live = c => false;      // the live lamps had no generator
            var b = new CordBuilder();
            var (cells, lamps) = Lattice(k);
            b.Build(World(k, 0, 0), new BuildOptions(), live);
            var row = new Row { K = k, Edges = b.LastPlanned + b.LastReused };
            var sw = new Stopwatch();
            row.AllReusedMs = double.MaxValue;
            for (int i = 0; i < 3; i++)
            {
                CordWorld w0 = World(k, 0, 0);
                sw.Restart();
                b.Build(w0, new BuildOptions { AsyncLay = true }, live);
                row.AllReusedMs = Math.Min(row.AllReusedMs, sw.Elapsed.TotalMilliseconds);
            }
            int nc = 0, nl = 0;
            var wall = Stopwatch.StartNew();
            var times = new List<double>();
            row.Top = new List<(double, string)>();
            while (true)
            {
                if (nc < cells.Count) nc = Math.Min(cells.Count, nc + cellBatch);
                else if (nl < lamps.Count) nl = Math.Min(lamps.Count, nl + lampBatch);
                CordWorld w = World(k, nc, nl);
                int gc0 = GC.CollectionCount(0);
                sw.Restart();
                b.Build(w, new BuildOptions { AsyncLay = true }, live);
                double t = sw.Elapsed.TotalMilliseconds;
                bool gc = GC.CollectionCount(0) != gc0;
                row.Frames++;
                times.Add(t);
                if (gc) row.GcFrames++;
                else row.WorstNoGcMs = Math.Max(row.WorstNoGcMs, t);
                row.OnCaller += b.LastLaidOnCaller;
                row.Top.Add((t, $"{t:0.00}ms f{row.Frames} key {b.PhKeyMs:0.00} cor {b.PhCorridorMs:0.00} adopted {b.GraphLanded} waiting {b.LastGraphPending} planned {b.LastPlanned} pend {b.LastPending} gc {gc}"));
                if (t > row.WorstMs)
                {
                    row.WorstMs = t;
                    row.Inputs = b.PhInputsMs; row.Reduce = b.PhReduceMs; row.EdgesMs = b.PhEdgesMs; row.Keys = b.PhKeyMs;
                    row.Corr = b.PhCorridorMs; row.Nodes = b.PhNodesMs; row.Reach = b.PhReachMs;
                }
                if (nc == cells.Count && nl == lamps.Count && b.LastPending == 0 && !b.LayRunning) break;
                if (wall.Elapsed.TotalSeconds > 300) break;
                System.Threading.Thread.Sleep(4);    // a frame: the worker gets time, as it does between live frames
            }
            times.Sort();
            row.P95Ms = times[(int)Math.Floor(0.95 * (times.Count - 1))];
            row.Top = row.Top.OrderByDescending(x => x.Item1).Take(4).ToList();
            return row;
        }

        internal static void Run(string[] args)
        {
            int ki = Array.IndexOf(args, "--scale-bench");
            string ks = ki >= 0 && ki + 1 < args.Length && !args[ki + 1].StartsWith("--") ? args[ki + 1] : "0,1,2,4,8,16";
            Measure(1);                              // JIT warm-up, discarded
            Console.WriteLine("scale-bench: k edgesBefore allReusedMs | frames worstFrameMs worstNoGc p95 gcFrames | worst = inputs reduce edges(keys corr) nodes reach | onCaller");
            foreach (int k in ks.Split(',').Select(int.Parse))
            {
                Row r = Measure(k);
                Console.WriteLine($"scale-bench: k={r.K,2} E={r.Edges,5} allReused {r.AllReusedMs,7:0.00} | frames {r.Frames,3} worst {r.WorstMs,7:0.00} noGC {r.WorstNoGcMs,6:0.00} p95 {r.P95Ms,6:0.00} gcFrames {r.GcFrames} | worst = " +
                                  $"in {r.Inputs:0.00} red {r.Reduce:0.00} edg {r.EdgesMs:0.00} (key {r.Keys:0.00} cor {r.Corr:0.00}) nod {r.Nodes:0.00} rch {r.Reach:0.00} | caller {r.OnCaller}");
                if (args.Contains("--trace")) foreach (var x in r.Top) Console.WriteLine("scale-bench:    top " + x.Item2);
            }
        }
    }
}
