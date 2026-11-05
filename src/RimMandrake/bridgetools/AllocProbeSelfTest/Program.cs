// Units for JawaBenchAllocCore (selftest_alloc_probe.py). Each prints "U <name> ok" or "U <name> <why>".
// On CoreCLR GC.GetAllocatedBytesForCurrentThread is exact, so it is the known-good counter here; the game's Mono
// counterpart is the live clause A1.

using System;
using System.Collections.Generic;
using A = JawaBench.BridgeTools.JawaBenchAllocCore;

namespace JawaBench.BridgeTools
{
    internal static class Program
    {
        private static readonly object[] Sink = new object[A.SmallCount];
        private static int _fails;

        private static void U(string name, Func<string> body)
        {
            string r;
            try { r = body(); } catch (Exception e) { r = "threw " + e.GetType().Name + ": " + e.Message; }
            Console.WriteLine("U " + name + " " + (r ?? "ok"));
            if (r != null) _fails++;
        }

        private static Action<bool> Alloc(int payload, int count) => real =>
        {
            if (real) for (int i = 0; i < count; i++) Sink[i] = new byte[payload];
            else for (int i = 0; i < count; i++) Sink[i] = null;
        };

        private static A.Calibration Cal(Func<long> counter, int payload, int count, Func<int> gc = null) =>
            A.Calibrate("t", "p", counter, gc ?? (() => GC.CollectionCount(0)), Alloc(payload, count),
                        count * A.ObjectBytes(payload, false), 9, 40);

        private static int Main()
        {
            Func<long> exact = GC.GetAllocatedBytesForCurrentThread;
            U("CalExactLargePasses", () => { var c = Cal(exact, A.LargePayload, A.LargeCount); return c.Verdict == A.Pass ? null : c.Render(); });
            U("CalExactSmallPasses", () => { var c = Cal(exact, A.SmallPayload, A.SmallCount); return c.Verdict == A.Pass ? null : c.Render(); });
            U("CalBlindReadsBlind", () => { var c = Cal(() => 0L, A.LargePayload, 64); return c.Verdict == A.Blind ? null : c.Render(); });
            U("CalDoubleReadsOff", () =>
            {
                var c = Cal(() => 2 * GC.GetAllocatedBytesForCurrentThread(), A.LargePayload, A.LargeCount);
                return c.Verdict == A.Off && Math.Abs(c.Ratio - 2.0) < 0.1 ? null : c.Render();
            });
            U("CalJustOutsideTolerance", () =>
            {
                // a counter reading 12 % high is OFF, 8 % high is PASS: the bar is 10 %, both sides
                var hi = Cal(() => (long)(1.12 * GC.GetAllocatedBytesForCurrentThread()), A.LargePayload, A.LargeCount);
                var ok = Cal(() => (long)(0.92 * GC.GetAllocatedBytesForCurrentThread()), A.LargePayload, A.LargeCount);
                return hi.Verdict == A.Off && ok.Verdict == A.Pass ? null : hi.Render() + " | " + ok.Render();
            });
            U("CalControlSubtracted", () =>
            {
                // another thread's steady allocation lands in both halves of a trial: a counter that adds 1 MB per read
                // still PASSes because the paired control carries it
                long extra = 0;
                var c = Cal(() => { extra += 1 << 20; return GC.GetAllocatedBytesForCurrentThread() + extra; }, A.LargePayload, A.LargeCount);
                return c.Verdict == A.Pass && c.MedianControl >= 1 << 20 ? null : c.Render();
            });
            U("CalAbsentUnmeasured", () => { var c = Cal(null, A.LargePayload, 8); return c.Verdict == A.Unmeasured && c.Absent != null ? null : c.Render(); });
            U("CalGcTrialsDiscarded", () =>
            {
                int g = 0;
                var c = Cal(exact, A.LargePayload, 8, () => g++);
                return c.Verdict == A.Unmeasured && c.Reads.Count == 0 && c.Discarded == 40 ? null : c.Render();
            });
            U("ObjectBytesPerRuntime", () =>
                A.ObjectBytes(4000, true) == 4032 && A.ObjectBytes(47, true) == 80 && A.ObjectBytes(1, true) == 48 && A.ObjectBytes(4000, false) == 4024 && A.ObjectBytes(47, false) == 72
                    ? null : "sizes " + A.ObjectBytes(4000, true) + "," + A.ObjectBytes(47, true) + "," + A.ObjectBytes(4000, false) + "," + A.ObjectBytes(47, false));
            U("TrustedNeedsEveryProbe", () =>
            {
                var pass = Cal(exact, A.LargePayload, A.LargeCount);
                var blind = Cal(() => 0L, A.LargePayload, 64);
                pass.Instrument = "heap"; blind.Instrument = "heap";
                var pass2 = Cal(exact, A.LargePayload, A.LargeCount); pass2.Instrument = "mono";
                var t1 = A.Trusted(new List<A.Calibration> { pass, blind, pass2 }, new[] { "heap", "mono" });
                var t2 = A.Trusted(new List<A.Calibration> { blind }, new[] { "heap" });
                return t1 == "mono" && t2 == null ? null : "t1=" + t1 + " t2=" + t2;
            });
            U("MeterGcCallsCarryNoBytes", () =>
            {
                var m = new A.Meter();
                m.Add(1000, 10, false); m.Add(5000000, 10, true); m.Add(-300, 10, false); m.Add(3000, 10, false);
                return m.Calls == 4 && m.ByteCalls == 3 && m.Bytes == 4000 && m.GcCalls == 1 && m.NegCalls == 1 && m.MaxBytes == 3000 ? null
                    : "calls " + m.Calls + " byteCalls " + m.ByteCalls + " bytes " + m.Bytes + " gc " + m.GcCalls;
            });
            U("RowScalesToAllCalls", () =>
            {
                var m = new A.Meter();
                for (int i = 0; i < 3; i++) m.Add(100, 1000, false);
                m.Add(0, 1000, true);                                  // 4 calls, bytes known for 3: 300 * 4/3 = 400 over 2 ticks
                string r = A.Row("X", m, 2, 0.01, 1e7);
                var g = new A.Meter();
                g.Add(500, 1000, true);                                // every call hit a collection: unknown, never 0
                string rg = A.Row("G", g, 2, 0.01, 1e7);
                return r.Contains("bytesPerTick=200.0") && r.Contains("controlBytesPerTick=20.0") && r.Contains("overControl=yes")
                       && rg.Contains("bytesPerTick=?") ? null : r + " | " + rg;
            });
            U("ClassifyLandings", () =>
            {
                var e = new A.Landing { FrameMs = 130, ExplicitCaller = "Verse.X:Y" };
                var f = new A.Landing { FrameMs = 130 };
                var h = new A.Landing { FrameMs = 20, HostMs = 125 };
                var i = new A.Landing { FrameMs = 18 };
                string s = A.Classify(e) + "," + A.Classify(f) + "," + A.Classify(h) + "," + A.Classify(i);
                return s == "explicit,implicit-slow,implicit-slow,implicit-fast" ? null : s;
            });
            U("TriggerNamesTheCause", () =>
            {
                var none = A.Trigger(new List<A.Landing> { new A.Landing { FrameMs = 10 } });
                var heap = A.Trigger(new List<A.Landing> { new A.Landing { FrameMs = 130, HeapBefore = 900L << 20, AllocSincePrev = 300L << 20 }, new A.Landing { FrameMs = 10 } });
                var expl = A.Trigger(new List<A.Landing> { new A.Landing { FrameMs = 140, ExplicitCaller = "Verse.MemoryUtility:Clear" } });
                var mix = A.Trigger(new List<A.Landing> { new A.Landing { FrameMs = 140, ExplicitCaller = "a:b" }, new A.Landing { FrameMs = 120 } });
                var unhooked = A.Trigger(new List<A.Landing> { new A.Landing { FrameMs = 130 } }, false);
                bool ok = none.StartsWith("NONE") && heap.Contains("verdict=implicit (no GC.Collect call") && heap.Contains("implicitMedianHeapMB=900.0")
                          && expl.Contains("verdict=explicit GC.Collect") && expl.Contains("caller[Verse.MemoryUtility:Clear]=1") && mix.Contains("verdict=mixed") && unhooked.Contains("verdict=unknown");
                return ok ? null : none + " | " + heap + " | " + expl + " | " + mix + " | " + unhooked;
            });
            Console.WriteLine("U-count " + _fails);
            return _fails == 0 ? 0 : 1;
        }
    }
}
