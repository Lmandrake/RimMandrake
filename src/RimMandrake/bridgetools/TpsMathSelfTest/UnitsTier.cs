// Test tier (telemetry design P2): the PRODUCTION JawaBenchTpsTierCore - histogram bucketing, flight-ring wraparound and
// copy order, the exclusive stage split per tick, the spike trigger, log-signature normalisation and the per-window
// counter, the dump rate limit, the flight directory cap, the flight file format, the 1 s cadence, the new settings
// switches and the writer's side-job queue.
using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;
using System.Threading;
using C = JawaBench.BridgeTools.JawaBenchTpsTierCore;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;
using S = JawaBench.BridgeTools.JawaBenchTpsStages;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static long Ms(double ms) => (long)Math.Ceiling(ms * Freq / 1000.0);

        private static void T_TierHistBuckets()
        {
            var e = C.Hist.EdgesTicks(Freq);
            Check(e.Length == 27, "27 edges for 28 buckets, got " + e.Length);
            Check(Math.Abs(C.Hist.LowerEdgeMs(1) - 0.25) < 1e-12 && Math.Abs(C.Hist.LowerEdgeMs(27) - 4000) < 1e-9 &&
                  Math.Abs(C.Hist.MinMs * Math.Pow(C.Hist.Ratio, 26) - 4000) < 1e-6, "edges run 0.25 ms .. 4000 ms");
            Check(C.Hist.Bucket(0, e) == 0, "0 -> bucket 0");
            Check(C.Hist.Bucket(e[0] - 1, e) == 0 && C.Hist.Bucket(e[0], e) == 1, "0.25 ms is the first edge");
            Check(C.Hist.Bucket(e[26] - 1, e) == 26 && C.Hist.Bucket(e[26], e) == 27, "4 s is the last edge");
            Check(C.Hist.Bucket(Tk(3600), e) == 27 && C.Hist.Bucket(long.MaxValue, e) == 27, "an hour and long.MaxValue -> 27");
            int prev = 0;
            bool mono = true;
            for (double ms = 0.01; ms < 10000; ms *= 1.07) { int b = C.Hist.Bucket(Tk(ms / 1000), e); if (b < prev) mono = false; prev = b; }
            Check(mono, "bucket is monotone in duration");
            for (int i = 1; i < 28; i++)
                Check(C.Hist.Bucket(e[i - 1], e) == i, "lower edge of bucket " + i + " maps to it");
            var counts = new int[C.Hist.Buckets];
            counts[3] = 5; counts[27] = 1;
            string f = C.Hist.TakeFields(counts);
            Check(f == "\"hist\":[[3,5],[27,1]],\"histV\":1", "sparse hist fields: " + f);
            Check(counts.All(c => c == 0), "TakeFields zeroes the counts");
            Check(C.Hist.TakeFields(counts) == "\"hist\":[],\"histV\":1", "an empty window is an empty list");
            Emit("tier-hist", "{" + f + ",\"histEdgesMs\":" + C.Hist.EdgesJson() + "}");
        }

        private static C.TickTier NewTier(int cap)
        {
            var t = new C.TickTier(Freq, cap) { Exc = new C.ExcCounter() };
            t.Allocate();
            t.Clear();
            t.On = true;
            return t;
        }

        private static readonly long[] Zero = new long[S.N];

        private static void T_TierRingWrap()
        {
            var t = NewTier(8);
            var snap = new C.FlightSnap(8);
            for (int i = 1; i <= 5; i++) t.Record(Ms(i), i, Zero, Zero, 100 + i, 0);
            t.CopyTo(snap);
            Check(snap.Count == 5 && snap.Tg.Take(5).SequenceEqual(new[] { 1, 2, 3, 4, 5 }), "unwrapped ring, oldest first: " + string.Join(",", snap.Tg.Take(snap.Count)));
            for (int i = 6; i <= 13; i++) t.Record(Ms(i), i, Zero, Zero, 100 + i, 0);
            t.CopyTo(snap);
            Check(snap.Count == 8 && snap.Tg.SequenceEqual(new[] { 6, 7, 8, 9, 10, 11, 12, 13 }),
                  "wrapped ring keeps the newest 8, oldest first: " + string.Join(",", snap.Tg.Take(snap.Count)));
            Check(snap.Dur.Select((d, i) => Math.Abs(d - (snap.Tg[i] * 1000)) <= 1).All(x => x), "durUs travels with its tg: " + string.Join(",", snap.Dur));
            Check(snap.Gc.All(g => g == 1), "gc0 is the per-tick delta of the gen-0 count");
            Check(snap.TickFrom == 6 && snap.TickTo == 13 && snap.Tg[snap.Worst()] == 13, "tickFrom/tickTo/worst");
            // exactly full, head back at 0
            var t2 = NewTier(4);
            for (int i = 1; i <= 4; i++) t2.Record(Ms(1), i, Zero, Zero, 0, 0);
            var s2 = new C.FlightSnap(4);
            t2.CopyTo(s2);
            Check(s2.Count == 4 && s2.Tg.SequenceEqual(new[] { 1, 2, 3, 4 }), "exactly full ring: " + string.Join(",", s2.Tg));
            t2.Clear();
            t2.CopyTo(s2);
            Check(s2.Count == 0, "Clear empties the ring");
        }

        private static void T_TierExclusiveAndCounters()
        {
            var t = NewTier(4);
            var tb = new long[S.N];
            var tot = new long[S.N];
            tot[S.CNormal] = Ms(4); tot[S.CMapPost] = Ms(3); tot[S.CMapComp] = Ms(1);
            t.Record(Ms(10), 50, tot, tb, 7, 3);      // first tick: deltas are 0 by definition (no baseline)
            t.Record(Ms(10), 51, tot, tb, 9, 8);      // 2 GCs, 5 log errors/warnings during this tick
            var s = new C.FlightSnap(4);
            t.CopyTo(s);
            int b = 1 * S.N;
            Check(Math.Abs(s.Stage[b + S.CTick] - 3000) <= 2, "tickOther = 10 - 4 - 3 ms: " + s.Stage[b + S.CTick]);
            Check(Math.Abs(s.Stage[b + S.CMapPost] - 2000) <= 2, "mapPost excludes mapComp: " + s.Stage[b + S.CMapPost]);
            Check(Math.Abs(s.Stage[b + S.CMapComp] - 1000) <= 2 && Math.Abs(s.Stage[b + S.CNormal] - 4000) <= 2, "children carried");
            Check(s.Gc[0] == 0 && s.Ew[0] == 0 && s.Gc[1] == 2 && s.Ew[1] == 5, "gc0/logEW deltas: " + s.Gc[1] + "/" + s.Ew[1]);
            Check(t.HistCounts.Sum() == 2, "both ticks counted in the histogram");
            var sb = new StringBuilder();
            C.AppendTick(sb, s, 1);
            Check(sb.ToString().StartsWith("[51,10000,") && sb.ToString().EndsWith(",2,5]") && sb.ToString().Split(',').Length == C.FlightFields.Length,
                  "a flight tick row has every field in order: " + sb);
        }

        private static void T_TierSpikeTrigger()
        {
            var t = NewTier(4);
            t.Record(Ms(249), 1, Zero, Zero, 0, 0);
            Check(t.PendingTrigger == null, "249 ms raises nothing");
            t.Record(Ms(250), 2, Zero, Zero, 0, 0);
            Check(t.PendingTrigger == C.TrigTick && t.PendingTg == 2, "250 ms raises the tick trigger with its tg");
            t.Record(Ms(900), 3, Zero, Zero, 0, 0);
            Check(t.PendingTg == 2, "a pending trigger is not overwritten before the frame consumes it");
            t.FlightOn = false;
            t.HistOn = false;
            t.Record(Ms(1), 4, Zero, Zero, 0, 0);
            var s = new C.FlightSnap(4);
            t.CopyTo(s);
            Check(s.Count == 3 && t.HistCounts.Sum() == 3, "flight/histogram switches stop their half only");
        }

        private static void T_TierSignature()
        {
            Check(C.ExcCounter.Signature('E', "Error 123 at 4.5 for Pawn_77", null) == "E:Error ### at #.# for Pawn_##", "digits -> #");
            Check(C.ExcCounter.Signature('O', "x 1", 4242) == "O:x #|key=4242", "ErrorOnce key appended verbatim");
            Check(C.ExcCounter.Signature('W', "a\nb\tc", null) == "W:a b c", "line breaks and tabs flattened");
            string longText = new string('z', 300) + "9";
            Check(C.ExcCounter.Signature('M', longText, null).Length == 2 + C.ExcSigLen, "first 160 chars only");
            Check(C.ExcCounter.Signature('E', null, null) == "E:", "null message");
            Check(C.ExcCounter.Signature('E', "same 1", null) == C.ExcCounter.Signature('E', "same 2", null), "messages differing only by numbers share a signature");
        }

        private static void T_TierExcWindow()
        {
            var x = new C.ExcCounter();
            Check(x.Note('E', "E:a", false), "first sight of a signature");
            Check(!x.Note('E', "E:a", true), "second sight is not first");
            x.Note('M', "M:m", false);
            x.Note('W', "W:w", false);
            for (int i = 0; i < 70; i++) x.Note('E', "E:s" + i, false);
            Check(x.ErrWarnNow == 73, "errors+warnings exclude messages: " + x.ErrWarnNow);
            Check(!x.Note('R', null, false) && x.ErrWarnNow == 73, "a once-repeat is no error, no first sight");
            long n;
            string f = x.TakeFields(out n);
            Check(n == 73, "burst count is errors+warnings only: " + n);
            Check(f.StartsWith("\"exc\":{\"n\":75,\"sup\":1,\"e\":72,\"w\":1,\"m\":1,\"rep\":1,\"over\":") , "exc fields: " + f);
            // 3 signatures first, then 61 of the 70 fit in the 64 cap: 9 overflow
            Check(f.Contains("\"over\":9,"), "64-signature cap with overflow: " + f);
            Check(f.Contains("\"top\":[[\"E:a\",2],"), "top is by count: " + f);
            Emit("tier-exc", "{" + f + "}");
            string g = x.TakeFields(out n);
            Check(n == 0 && g == "\"exc\":{\"n\":0,\"sup\":0,\"e\":0,\"w\":0,\"m\":0,\"rep\":0,\"over\":0,\"top\":[]}", "TakeFields resets the window: " + g);
            Check(!x.Note('E', "E:a", false), "first sight is per SESSION, not per window");
            string line = C.ExcCounter.FirstSightLine("2026-10-11T00:00:00.000Z", "abc123", 'O', "O:x|key=1", 1, true, 99, new string('m', 5000), "stack");
            Emit("tier-exc-first", line);
            Check(line.Contains("\"stack\":\"\"") && line.Contains("\"level\":\"errorOnce\""), "message+stack capped at 4 KB together");
        }

        private static void T_TierGate()
        {
            var g = new C.FlightGate();
            int sup;
            Check(g.TryFire(100, out sup) && sup == 0, "first trigger fires");
            Check(!g.TryFire(110, out sup), "10 s later: limited");
            Check(!g.TryFire(129.9, out sup) && sup == 1, "29.9 s later: limited (second suppressed)");
            Check(g.TryFire(130, out sup) && sup == 2, "30 s later fires and reports 2 suppressed: " + sup);
            Check(g.Fired == 2 && g.Suppressed == 2 && g.SuppressedSinceLast == 0, "counters");
            g.Reset();
            Check(g.TryFire(131, out sup), "Reset (a new arm) clears the limit");
        }

        private static void T_TierPlanCap()
        {
            var del = C.PlanCap(new long[] { 400, 300, 200, 100 }, new double[] { 10, 40, 30, 20 }, 450, 1);
            Check(del.SequenceEqual(new[] { 2, 3, 0 }), "oldest first, never the kept file: " + string.Join(",", del));
            Check(C.PlanCap(new long[] { 10, 10 }, new double[] { 1, 2 }, 100, -1).Count == 0, "under the cap: nothing");
        }

        private static void T_TierFlightFile()
        {
            var t = NewTier(16);
            for (int i = 0; i < 20; i++) t.Record(Ms(i == 17 ? 300 : 2), 1000 + i, Zero, Zero, i, i);
            var s = new C.FlightSnap(16);
            t.CopyTo(s);
            string d = TempDir();
            string path = Path.Combine(Path.Combine(d, "flight"), C.FlightFileName("abc123", 7));
            string header = C.FlightHeader("abc123", 7, C.TrigTick, "2026-10-11T00:00:00.000Z", s, Freq);
            long bytes = C.WriteFlightFile(path, header, s);
            Check(Path.GetFileName(path) == "flight_abc123_0007.jsonl.gz" && bytes > 0 && File.Exists(path) && !File.Exists(path + ".tmp"), "file written: " + path);
            string[] lines;
            using (var gz = new GZipStream(File.OpenRead(path), CompressionMode.Decompress))
            using (var r = new StreamReader(gz)) lines = r.ReadToEnd().Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries);
            Check(lines.Length == 17, "header + 16 ticks: " + lines.Length);
            Emit("tier-flight-header", lines[0]);
            Emit("tier-flight-tick", "{\"row\":" + lines[1] + "}");
            Check(lines[1].StartsWith("[1004,") && lines[16].StartsWith("[1019,"), "ticks oldest first: " + lines[1] + " .. " + lines[16]);
            Check(lines[0].Contains("\"worstTg\":1017") && lines[0].Contains("\"tickFrom\":1004") && lines[0].Contains("\"tickTo\":1019"), "header: " + lines[0]);
            // the cap keeps the file just written
            File.WriteAllBytes(Path.Combine(Path.Combine(d, "flight"), "flight_old_0001.jsonl.gz"), new byte[100]);
            File.SetLastWriteTimeUtc(Path.Combine(Path.Combine(d, "flight"), "flight_old_0001.jsonl.gz"), DateTime.UtcNow.AddDays(-1));
            int n = C.EnforceFlightCap(Path.Combine(d, "flight"), path, 1);
            Check(n == 1 && File.Exists(path), "cap deletes the old dump and keeps the new one even when it alone exceeds the cap");
        }

        private static void T_TierCadence()
        {
            var a = new M.FrameAccumulator { Cadence = 1.0 };
            int closed = 0;
            for (int f = 0; f <= 300; f++)
            {
                a.Pre(f / 60.0, false, 1, f, 0);
                if (a.TakeClosed() != null) closed++;
                a.Post(1, f + 1, 0.001);
            }
            Check(closed == 5, "1 s cadence over 5 s closes 5 windows, got " + closed);
            a.Cadence = M.CadenceSeconds;
            for (int f = 301; f <= 900; f++) { a.Pre(f / 60.0, false, 1, f, 0); if (a.TakeClosed() != null) closed++; a.Post(1, f + 1, 0.001); }
            Check(closed == 7, "back to 5 s: 10 more seconds close 2 more windows, got " + closed);
        }

        private static void T_TierSettings()
        {
            string note;
            var s = LoadText("{\"histogram\":false,\"flight\":true,\"excCounter\":false,\"bridgeOccupancy\":false}", out note);
            Check(!s.Histogram && s.Flight && !s.ExcCounter && !s.BridgeOccupancy && (note == null || !note.Contains("invalid")), "tier switches read: " + note);
            var d = LoadText("{}", out note);
            Check(d.Histogram && d.Flight && d.ExcCounter && d.BridgeOccupancy, "tier switches default on (active only while armed)");
            Refused("tier switch wrong type", "{\"flight\":1}", x => x.Flight);
            Check(new JawaBenchTpsSettings().ToJson().Contains("\"bridgeOccupancy\":true"), "ToJson carries the switches");
        }

        private static void T_TierWriterSideJobs()
        {
            string dir = StartWriter();
            int ran = 0, thread = Thread.CurrentThread.ManagedThreadId, jobThread = -1;
            Check(W.EnqueueSide(() => { jobThread = Thread.CurrentThread.ManagedThreadId; Interlocked.Increment(ref ran); }), "side job accepted");
            Check(W.EnqueueSide(() => { throw new IOException("boom"); }), "a throwing job is accepted");
            Check(W.EnqueueSide(() => Interlocked.Increment(ref ran)), "a job after a throwing one is accepted");
            W.Enqueue("marker", "\"why\":\"x\"");
            for (int i = 0; i < 100 && Volatile.Read(ref ran) < 2; i++) Thread.Sleep(20);
            Check(ran == 2 && jobThread != thread && jobThread != -1, "jobs ran on the writer thread, past a throwing one: ran=" + ran);
            Check(W.SideErrors == 1 && W.SideLastError != null && W.SideLastError.Contains("boom"), "a throwing job is counted, not fatal");
            W.ResetForTest();
            Check(!W.EnqueueSide(() => { }) && W.SideRefused == 1, "refused when the writer is not running");
        }
    }
}
