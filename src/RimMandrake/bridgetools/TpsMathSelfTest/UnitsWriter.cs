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
                    RealAppend(p, b, n / 2);                                  // half the bytes reach the disk...
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

        private static void T_WriterBoundCountsInFlight()
        {
            string d = PrepWriter();
            var gate = new ManualResetEventSlim(false);
            W.AppendImpl = (p, b, n) => { gate.Wait(20000); RealAppend(p, b, n); };   // the disk is stuck
            int cap = JawaBenchTpsMath.QueueCapacity - JawaBenchTpsMath.QueueCapacity / 8;   // a full bulk share
            for (int i = 0; i < cap; i++) W.Enqueue("sample", "\"i\":" + i);
            W.Start(d, "abcdef0123", 4242);
            Thread.Sleep(500);                                // the writer takes them as ONE in-flight batch
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
