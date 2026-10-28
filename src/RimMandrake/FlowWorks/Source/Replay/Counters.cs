// HOSE_PERF_BUILD_OFFLINE_REPLAY_HARNESS: per tick, per system: elapsed time, allocated bytes, GC count (exclusive: a child
// scope's cost is not booked to its parent), and per tick work counts. Every array is allocated before the replay starts, so
// the harness's own bookkeeping never shows up inside a measured scope.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Text;

namespace RimMandrake.FlowWorks.Replay
{
    internal enum Sys { World, Recheck, Lay, Settle, Move, Count }

    internal enum Work
    {
        CellsMarked, CellsPatched, Patches, WholeRebuilds, Overflows, Rechecks, CorridorCells, CheckReplans, Retracts, Lays, LayFails,
        CompRevisions, CompBuilds, CompSize, SettleMoves, UnitsSettled, RouteDead, Transfers, TransferRefused, Count
    }

    internal sealed class Counters
    {
        public readonly int Ticks;
        public readonly long[,] Elapsed;   // Stopwatch ticks, [tick, sys]
        public readonly long[,] Bytes;     // allocated bytes, [tick, sys]
        public readonly int[,] Gcs;        // collections that ran inside the scope, [tick, sys]
        public readonly long[,] W;         // work, [tick, work]
        public long PatchBytesWarm;        // HoseWorldPatch.Patch alone, after its first call (the zero-alloc gate)
        public int PatchCallsWarm;

        // a scope stack: exclusive time and bytes
        private readonly Sys[] stack = new Sys[16];
        private readonly long[] t0 = new long[16], b0 = new long[16], childT = new long[16], childB = new long[16];
        private readonly int[] g0 = new int[16], childG = new int[16];
        private int depth;
        public int Tick;

        public Counters(int ticks)
        {
            Ticks = ticks;
            Elapsed = new long[ticks, (int)Sys.Count];
            Bytes = new long[ticks, (int)Sys.Count];
            Gcs = new int[ticks, (int)Sys.Count];
            W = new long[ticks, (int)Work.Count];
        }

        public void Begin(Sys s)
        {
            stack[depth] = s;
            childT[depth] = childB[depth] = 0;
            childG[depth] = 0;
            g0[depth] = GC.CollectionCount(0);
            b0[depth] = GC.GetAllocatedBytesForCurrentThread();
            t0[depth] = Stopwatch.GetTimestamp();
            depth++;
        }

        public void End()
        {
            long t = Stopwatch.GetTimestamp();
            long b = GC.GetAllocatedBytesForCurrentThread();
            int g = GC.CollectionCount(0);
            depth--;
            long dt = t - t0[depth], db = b - b0[depth];
            int dg = g - g0[depth];
            int s = (int)stack[depth];
            Elapsed[Tick, s] += dt - childT[depth];
            Bytes[Tick, s] += db - childB[depth];
            Gcs[Tick, s] += dg - childG[depth];
            if (depth > 0) { childT[depth - 1] += dt; childB[depth - 1] += db; childG[depth - 1] += dg; }
        }

        public void Add(Work w, long n = 1) => W[Tick, (int)w] += n;

        public static double Ms(long sw) => sw * 1000.0 / Stopwatch.Frequency;

        /// <summary>Mean, p99, max and the count of ticks over the bar, of one system's per-tick time (ms). A p99 pass never
        /// excuses a max failure: the report prints both and the bar counts every tick over it.</summary>
        public void TimeStats(Sys s, double barMs, out double mean, out double p99, out double max, out int over, out int worst)
        {
            var v = new double[Ticks];
            double sum = 0; max = 0; over = 0; worst = -1;
            for (int i = 0; i < Ticks; i++)
            {
                v[i] = Ms(Elapsed[i, (int)s]);
                sum += v[i];
                if (v[i] > max) { max = v[i]; worst = i; }
                if (v[i] > barMs) over++;
            }
            mean = Ticks > 0 ? sum / Ticks : 0;
            Array.Sort(v);
            p99 = Ticks > 0 ? v[Math.Min(Ticks - 1, (int)Math.Ceiling(Ticks * 0.99) - 1)] : 0;
        }

        public long WorkMax(Work w, out int at)
        {
            long m = 0; at = -1;
            for (int i = 0; i < Ticks; i++) if (W[i, (int)w] > m) { m = W[i, (int)w]; at = i; }
            return m;
        }

        public long WorkSum(Work w)
        {
            long s = 0;
            for (int i = 0; i < Ticks; i++) s += W[i, (int)w];
            return s;
        }

        public long BytesSum(Sys s)
        {
            long b = 0;
            for (int i = 0; i < Ticks; i++) b += Bytes[i, (int)s];
            return b;
        }

        public long BytesMax(Sys s)
        {
            long b = 0;
            for (int i = 0; i < Ticks; i++) b = Math.Max(b, Bytes[i, (int)s]);
            return b;
        }

        public int GcSum(Sys s)
        {
            int g = 0;
            for (int i = 0; i < Ticks; i++) g += Gcs[i, (int)s];
            return g;
        }
    }
}
