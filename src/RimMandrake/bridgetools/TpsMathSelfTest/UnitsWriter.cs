// Writer fault injection (MUST 4, MUST 14): the PRODUCTION JawaBenchTpsWriter, its real thread and real files
// in a temp dir, with JawaBenchTpsWriter.AppendImpl swapped to fail at chosen points.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static readonly Action<string, byte[], int> RealAppend = W.AppendImpl;

        private static string StartWriter() { string d = PrepWriter(); W.Start(d, "abcdef0123", 4242); return d; }

        /// <summary>Reset the writer and return a temp dir WITHOUT starting it: lines enqueued before Start()
        /// reach the writer thread as ONE batch, which is what a batch-boundary test needs.</summary>
        private static string PrepWriter()
        {
            W.ResetForTest();
            W.AppendImpl = RealAppend;
            return TempDir();
        }

        /// <summary>Every line of every segment: (parsed seq or -1 for an unparseable line).</summary>
        private static List<long> Seqs(string dir, out int badLines)
        {
            var seqs = new List<long>();
            badLines = 0;
            foreach (var f in Directory.GetFiles(dir, "tps_*.jsonl").OrderBy(x => x, StringComparer.Ordinal))
                foreach (var ln in File.ReadAllText(f).Split('\n'))
                {
                    if (ln.Length == 0) continue;
                    var m = Regex.Match(ln, "^\\{\"seq\":(\\d+),.*\\}$");
                    if (m.Success && Regex.Matches(ln, "\\{\"seq\":").Count == 1) seqs.Add(long.Parse(m.Groups[1].Value));
                    else badLines++;
                }
            return seqs;
        }

        private static string Big(int kb) => "\"pad\":\"" + new string('x', kb * 1024) + "\"";

        private static void T_WriterReplayAfterPartialBatch()
        {
            string d = PrepWriter();
            int calls = 0;
            W.AppendImpl = (p, b, n) =>
            {
                // first append (segment 0) succeeds; the second (segment 1, after rotation) fails once
                if (Interlocked.Increment(ref calls) == 2) throw new IOException("injected: disk full");
                RealAppend(p, b, n);
            };
            for (int i = 0; i < 3; i++) W.Enqueue("sample", Big(800));      // 3 x 800 KB: rotation after two
            W.Start(d, "abcdef0123", 4242);
            Check(W.Drain(15000), "drained after the injected failure");
            int bad;
            var seqs = Seqs(d, out bad);
            Check(seqs.Count == 3 && seqs.Distinct().Count() == 3,
                  "each committed line is on disk ONCE after a retry: seqs " + string.Join(",", seqs));
            Check(bad == 0, bad + " unparseable lines");
            W.ResetForTest();
        }

        private static void T_WriterTornTail()
        {
            string d = PrepWriter();
            int calls = 0;
            W.AppendImpl = (p, b, n) =>
            {
                if (Interlocked.Increment(ref calls) == 1)
                {
                    // half of the FIRST line reaches the disk... (not n / 2: the four rows are the same length,
                    // so half the chunk ends exactly on a line boundary and no line was ever torn)
                    RealAppend(p, b, Array.IndexOf(b, (byte)'\n') / 2);
                    throw new IOException("injected: torn write");           // ...then the write fails
                }
                RealAppend(p, b, n);
            };
            for (int i = 0; i < 4; i++) W.Enqueue("sample", "\"i\":" + i);
            W.Start(d, "abcdef0123", 4242);
            Check(W.Drain(15000), "drained after the torn write");
            int bad;
            var seqs = Seqs(d, out bad);
            Check(bad == 0, "a torn tail never joins a later row: " + bad + " unparseable line(s)");
            Check(seqs.Count == 4 && seqs.Distinct().Count() == 4, "all four rows once: " + string.Join(",", seqs));
            W.ResetForTest();
        }

        /// <summary>JAWABENCH_TPSSTARTUP_HARDEN_REMAINING_BG_JIT: a deferred writer starts no thread and writes nothing
        /// until Go(); Go() writes the queued rows on the CALLING thread before it returns (that pass is what compiles
        /// the writer's code off the patching race), then the thread takes later rows; a second Go/Start is a no-op.</summary>
        private static void T_WriterDeferredStartDrainsOnCaller()
        {
            string d = PrepWriter();
            W.Start(d, "abcdef0123", 4242, deferThread: true);
            W.Enqueue("session", "\"pid\":4242");
            W.Enqueue("marker", "\"why\":\"start\"");
            int bad;
            Check(!W.Running, "deferred: no writer thread before Go");
            Thread.Sleep(200);
            Check(Seqs(d, out bad).Count == 0, "deferred: nothing on disk before Go");
            Check(!W.EnqueueSide(() => { }), "deferred: side jobs refused until the thread runs");
            W.Go();
            var seqs = Seqs(d, out bad);
            Check(bad == 0 && seqs.Count == 2 && seqs[0] == 1 && seqs[1] == 2,
                  "Go wrote the queued rows synchronously on the caller: " + string.Join(",", seqs) + " bad " + bad);
            Check(W.Running, "Go started the writer thread");
            W.Go();
            W.Start(d, "abcdef0123", 4242);
            W.Enqueue("menu", "\"programState\":\"Entry\"");
            Check(W.Drain(15000), "the thread writes rows queued after Go");
            seqs = Seqs(d, out bad);
            Check(bad == 0 && seqs.Count == 3 && seqs.Distinct().Count() == 3, "three rows once each: " + string.Join(",", seqs));
            W.ResetForTest();
            // a never-started record: Go is a no-op and never throws
            W.Go();
            Check(!W.Running, "Go without Start starts nothing");
        }

        private static void T_WriterBoundCountsInFlight()
        {
            string d = PrepWriter();
            var gate = new ManualResetEventSlim(false);
            W.AppendImpl = (p, b, n) => { gate.Wait(20000); RealAppend(p, b, n); };   // the disk is stuck
            int cap = JawaBenchTpsMath.QueueCapacity - JawaBenchTpsMath.QueueCapacity / 8;   // a full bulk share
            for (int i = 0; i < cap; i++) W.Enqueue("sample", "\"i\":" + i);
            W.Start(d, "abcdef0123", 4242);
            // the writer takes them as ONE in-flight batch: wait until it says so, or the bound below is not tested
            // (while the batch still sits in Pending the queue is full anyway and the check passes for free)
            string flying = "\"wfly\":" + cap + ",";
            var waited = System.Diagnostics.Stopwatch.StartNew();
            while (!W.HealthFields().Contains(flying) && waited.ElapsedMilliseconds < 10000) Thread.Sleep(20);
            Check(W.HealthFields().Contains(flying), "the stuck writer holds the whole batch in flight: " + W.HealthFields());
            int more = 0;
            for (int i = 0; i < cap; i++) if (W.Enqueue("sample", "\"j\":" + i) > 0) more++;
            Check(more <= JawaBenchTpsMath.QueueCapacity / 8,
                  "outstanding work is bounded INCLUDING the in-flight batch: " + more + " more accepted while " + cap +
                  " were in flight");
            long crit = W.Enqueue("error", "\"where\":\"test\"");
            Check(crit > 0, "a critical row (error) still has reserved room when samples fill the queue");
            Check(W.HealthFields().Contains("\"wfly\":"), "health shows in-flight work: " + W.HealthFields());
            gate.Set();
            W.Drain(15000);
            W.ResetForTest();
        }
    }
}
