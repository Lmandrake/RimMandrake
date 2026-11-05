// JawaBenchAllocCore.cs - the Verse-free half of jawa/alloc_probe (MONO_ALLOC_MEASURE_PER_TICK_ON_GAME): calibrating an
// allocation counter against a KNOWN allocation, metering bytes per tick per system, and classifying GC landings.
// Compiled by the companion and, whole, by bridgetools/AllocProbeSelfTest (net8, CoreCLR) for the offline proof.
//
// Why a calibration and not a trust: on RimWorld 1.6's Unity Mono (Boehm GC) GC.GetAllocatedBytesForCurrentThread reads 0
// across a fresh 1 MB array (lesson 20261028T083727Z: Mono's Boehm back end does not implement it). A per-thread zero from
// a blind counter is not zero allocation. So every counter is judged here first: allocate a known number of bytes, read
// the counter's change, subtract a paired control (the same loop allocating nothing: other threads' allocations and lazy
// sweeping land in an all-thread heap counter too), and take the median over GC-free trials.
//   PASS  |median(net) / expected - 1| <= Tolerance (10 %, the item's bar)
//   BLIND median read of the known allocation is 0 (the counter does not move at all)
//   OFF   it moves, but outside the tolerance (the ratio is reported)
//   UNMEASURED fewer than MinTrials GC-free trials
// The known allocations are sized so the allocator's rounding stays inside 2 % on both runtimes: byte[4000] (a 4032 B Mono
// object, a 4096 B Boehm block; 4024 B on CoreCLR) and byte[47] (79-80 B on Mono, 72 B on CoreCLR: the expected size per
// object is passed in, from ObjectBytes).

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchAllocCore
    {
        internal const double Tolerance = 0.10;
        internal const int MinTrials = 5;
        internal const int LargePayload = 4000, LargeCount = 1024;     // ~4 MB in large objects
        internal const int SmallPayload = 47, SmallCount = 32768;      // ~2.6 MB in small objects
        internal const double SlowGcMs = 100.0;                         // a landing whose frame or host call took this long is "slow"

        internal const string Pass = "PASS", Blind = "BLIND", Off = "OFF", Unmeasured = "UNMEASURED";

        /// <summary>Managed size of a byte[payload] on this runtime: Mono's array header is 32 B (object 16 + bounds 8 + length
        /// 8) and Boehm hands out 16 B granules; CoreCLR's is 24 B, 8-aligned.</summary>
        internal static long ObjectBytes(int payload, bool mono)
        {
            long raw = payload + (mono ? 32 : 24);
            long g = mono ? 16 : 8;
            return (raw + g - 1) / g * g;
        }

        internal static double Median(List<long> xs)
        {
            if (xs == null || xs.Count == 0) return double.NaN;
            var a = xs.ToArray();
            Array.Sort(a);
            int n = a.Length;
            return n % 2 == 1 ? a[n / 2] : (a[n / 2 - 1] + a[n / 2]) / 2.0;
        }

        internal sealed class Calibration
        {
            internal string Instrument, Probe;
            internal long Expected;
            internal readonly List<long> Reads = new List<long>(), Controls = new List<long>(), Nets = new List<long>();
            internal int Discarded;                                     // trials a collection landed in
            internal string Absent;                                     // the counter does not exist here (why)

            internal double MedianRead => Median(Reads);
            internal double MedianControl => Controls.Count == 0 ? 0 : Median(Controls);
            /// <summary>Median of the PAIRED differences (read minus its own trial's control), over the expected bytes.</summary>
            internal double Ratio => Expected <= 0 || Nets.Count == 0 ? double.NaN : Median(Nets) / Expected;

            internal string Verdict
            {
                get
                {
                    if (Absent != null || Reads.Count < MinTrials) return Unmeasured;
                    if (MedianRead == 0) return Blind;
                    return Math.Abs(Ratio - 1.0) <= Tolerance ? Pass : Off;
                }
            }

            internal string Render()
            {
                var sb = new StringBuilder();
                sb.Append(Instrument).Append('/').Append(Probe).Append(' ').Append(Verdict);
                if (Absent != null) return sb.Append(" (").Append(Absent).Append(')').ToString();
                sb.Append(" ratio=").Append(F(Ratio, 3)).Append(" expected=").Append(Expected).Append("B medianRead=").Append(F(MedianRead, 0))
                  .Append("B medianControl=").Append(F(MedianControl, 0)).Append("B trials=").Append(Reads.Count).Append(" gcDiscarded=").Append(Discarded);
                return sb.ToString();
            }
        }

        /// <summary>Run one calibration. counter: the instrument (null = absent); gcCount: a collection counter (a trial it
        /// moved in is discarded); alloc(true) allocates the known bytes, alloc(false) runs the same loop allocating nothing.
        /// Trials alternate control and allocation so a drift in other threads' allocation lands in both.</summary>
        internal static Calibration Calibrate(string instrument, string probe, Func<long> counter, Func<int> gcCount,
                                              Action<bool> alloc, long expected, int trials, int maxAttempts)
        {
            var c = new Calibration { Instrument = instrument, Probe = probe, Expected = expected };
            if (counter == null) { c.Absent = "absent in this runtime"; return c; }
            for (int i = 0; i < maxAttempts && c.Reads.Count < trials; i++)
            {
                int g0 = gcCount();
                long a = counter();
                alloc(false);
                long b = counter();
                alloc(true);
                long d = counter();
                if (gcCount() != g0) { c.Discarded++; continue; }
                c.Controls.Add(b - a);
                c.Reads.Add(d - b);
                c.Nets.Add((d - b) - (b - a));
            }
            return c;
        }

        /// <summary>The instrument the per-system table may use: the first whose every probe PASSed; null if none.</summary>
        internal static string Trusted(IList<Calibration> cals, IList<string> order)
        {
            foreach (var name in order)
            {
                bool any = false, all = true;
                foreach (var c in cals)
                    if (c.Instrument == name) { any = true; all &= c.Verdict == Pass; }
                if (any && all) return name;
            }
            return null;
        }

        /// <summary>One system's tally over a window. Bytes are counted only from calls no collection landed in (a
        /// collection inside a call makes the heap counter's change meaningless); those calls are counted apart.</summary>
        internal sealed class Meter
        {
            internal long Calls, ByteCalls, Bytes, GcCalls, MaxBytes, Ticks /* Stopwatch */, MaxTicks, NegCalls;

            internal void Add(long bytes, long sw, bool gcLanded)
            {
                Calls++;
                Ticks += sw;
                if (sw > MaxTicks) MaxTicks = sw;
                if (gcLanded) { GcCalls++; return; }
                ByteCalls++;
                if (bytes < 0) { NegCalls++; bytes = 0; }               // lazy sweeping freed blocks mid-call: no allocation
                Bytes += bytes;
                if (bytes > MaxBytes) MaxBytes = bytes;
            }

            internal void Clear() { Calls = ByteCalls = Bytes = GcCalls = MaxBytes = Ticks = MaxTicks = NegCalls = 0; }
        }

        /// <summary>A row of the per-system table. bytesPerTick = bytes in GC-free calls scaled to all calls, over the
        /// game ticks the window ran; controlBytesPerTick = what the control rate (other threads' allocation per
        /// Stopwatch tick, from the calibration's paired controls) predicts for the same time, so a row under it is noise.</summary>
        internal static string Row(string key, Meter m, long gameTicks, double controlPerSw, double freq)
        {
            double scale = m.ByteCalls == 0 ? 0 : (double)m.Calls / m.ByteCalls;
            double bpt = gameTicks <= 0 || m.ByteCalls == 0 ? double.NaN : m.Bytes * scale / gameTicks;   // no GC-free call: unknown, not 0
            double cpt = gameTicks <= 0 ? double.NaN : controlPerSw * m.Ticks / gameTicks;
            double ms = m.Ticks * 1000.0 / freq;
            return key + " calls=" + m.Calls + " bytesPerTick=" + F(bpt, 1) + " controlBytesPerTick=" + F(cpt, 1)
                 + " overControl=" + (double.IsNaN(bpt) || double.IsNaN(cpt) ? "?" : bpt > cpt ? "yes" : "no")
                 + " maxCallBytes=" + m.MaxBytes + " gcCalls=" + m.GcCalls + " negCalls=" + m.NegCalls
                 + " msPerTick=" + F(gameTicks <= 0 ? double.NaN : ms / gameTicks, 4) + " maxCallMs=" + F(m.MaxTicks * 1000.0 / freq, 2);
        }

        /// <summary>One collection seen landing: in a frame (Root.Update cadence), the system or tick part running when
        /// the count moved, the heap counter before (last reading) and after, and any explicit collect call since the
        /// previous frame (its caller).</summary>
        internal struct Landing
        {
            internal int Tick, Count;
            internal double FrameMs, HostMs;
            internal string Host, ExplicitCaller;
            internal long HeapBefore, HeapAfter, AllocSincePrev;
        }

        /// <summary>The landing's class: explicit (a GC.Collect-family call ran in the frame the count moved in), else
        /// implicit (the collector started on its own: allocation-driven), split by the OBSERVED time of the frame or the host
        /// call it landed in (an upper bound on the pause: other work shares it): implicit-slow (>= SlowGcMs) or implicit-fast.
        /// Whether a slow one was the incremental collector's stop-the-world fallback is not observable from here.</summary>
        internal static string Classify(Landing l)
        {
            if (!string.IsNullOrEmpty(l.ExplicitCaller)) return "explicit";
            double pause = Math.Max(l.FrameMs, l.HostMs);
            return pause >= SlowGcMs ? "implicit-slow" : "implicit-fast";
        }

        internal static string RenderLanding(Landing l)
        {
            return Classify(l) + " tick=" + l.Tick + " collections=" + l.Count + " frameMs=" + F(l.FrameMs, 1) + " host=" + (l.Host ?? "outside-tick")
                 + " hostMs=" + F(l.HostMs, 1) + " heapBeforeMB=" + F(l.HeapBefore / 1048576.0, 1) + " heapAfterMB=" + F(l.HeapAfter / 1048576.0, 1)
                 + " allocSincePrevMB=" + F(l.AllocSincePrev / 1048576.0, 1) + (l.ExplicitCaller == null ? "" : " caller=" + l.ExplicitCaller);
        }

        /// <summary>The trigger line: the slow landings' classes counted, and for implicit ones the heap they fired at.
        /// explicitHooked false (a GC.Collect hook failed) turns an implicit or mixed verdict into unknown.</summary>
        internal static string Trigger(IList<Landing> ls, bool explicitHooked = true)
        {
            int slow = 0, expl = 0, full = 0;
            var callers = new Dictionary<string, int>();
            var heaps = new List<long>();
            var allocs = new List<long>();
            foreach (var l in ls)
            {
                string k = Classify(l);
                bool isSlow = Math.Max(l.FrameMs, l.HostMs) >= SlowGcMs;
                if (!isSlow) continue;
                slow++;
                if (k == "explicit") { expl++; callers.TryGetValue(l.ExplicitCaller, out int n); callers[l.ExplicitCaller] = n + 1; }
                else { full++; heaps.Add(l.HeapBefore); allocs.Add(l.AllocSincePrev); }
            }
            if (slow == 0) return "NONE: no landing >= " + SlowGcMs + " ms in the window (" + ls.Count + " landings)";
            var sb = new StringBuilder("slow=" + slow + " explicit=" + expl + " implicitSlow=" + full);
            foreach (var kv in callers) sb.Append(" caller[").Append(kv.Key).Append("]=").Append(kv.Value);
            if (full > 0) sb.Append(" implicitMedianHeapMB=").Append(F(Median(heaps) / 1048576.0, 1)).Append(" implicitMedianAllocSincePrevMB=").Append(F(Median(allocs) / 1048576.0, 1));
            // an implicit verdict needs every GC.Collect overload hooked: an unseen explicit call would look implicit
            sb.Append(" verdict=").Append(expl == slow ? "explicit GC.Collect" : !explicitHooked ? "unknown (a GC.Collect hook failed: explicit calls may be unseen)"
                : full == slow ? "implicit (no GC.Collect call: the collector fired on allocation)" : "mixed");
            return sb.ToString();
        }

        internal static string F(double v, int dp) =>
            double.IsNaN(v) || double.IsInfinity(v) ? "?" : v.ToString("F" + dp, CultureInfo.InvariantCulture);
    }
}
