// Retention on real files (MUST 11): another ACTIVE process's files survive; this process trims only its own
// closed segments; an old inactive session goes as a whole bundle.
using System;
using System.IO;
using System.Linq;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static void Touch(string dir, string name, int bytes, double ageDays)
        {
            string p = Path.Combine(dir, name);
            File.WriteAllBytes(p, new byte[bytes]);
            File.SetLastWriteTimeUtc(p, DateTime.UtcNow.AddDays(-ageDays));
        }

        private static void T_RetentionLeasesAndBundles()
        {
            string d = PrepWriter();
            W.Start(d, "c0ffee", 1);                                   // this process: session c0ffee
            string mine0 = Path.GetFileName(W.CurrentPath);
            W.Enqueue("marker", "\"why\":\"test\"");
            W.Drain(5000);                                            // the live segment now exists on disk
            // this process's own closed segments (old), then its live one is W.CurrentPath
            Touch(d, "tps_20261001T000000Z_c0ffee_1_000.jsonl", 3000, 2);
            Touch(d, "tps_20261001T000000Z_c0ffee_1_001.jsonl", 3000, 1);
            // ANOTHER live RimWorld: fresh heartbeat lease, old closed segment
            Touch(d, "tps_20261002T000000Z_beef01_2_000.jsonl", 3000, 3);
            Touch(d, "tps_20261002T000000Z_beef01_2_001.jsonl", 3000, 0.01);
            Touch(d, "hb_beef01.json", 100, 0);
            Touch(d, "session_beef01.json", 100, 3);
            // an old INACTIVE session: segment, heartbeat and manifest
            Touch(d, "tps_20260901T000000Z_dead00_3_000.jsonl", 3000, 9);
            Touch(d, "hb_dead00.json", 100, 9);
            Touch(d, "session_dead00.json", 100, 9);
            W.RetentionCapBytes = 8000;
            W.RunRetention();
            var left = Directory.GetFiles(d).Select(Path.GetFileName).ToList();
            Check(left.Contains("tps_20261002T000000Z_beef01_2_000.jsonl") && left.Contains("tps_20261002T000000Z_beef01_2_001.jsonl")
                  && left.Contains("hb_beef01.json") && left.Contains("session_beef01.json"),
                  "another ACTIVE process keeps every file: " + string.Join(",", left));
            Check(!left.Any(f => f.Contains("dead00")), "the old inactive session went as a bundle: " + string.Join(",", left));
            Check(!left.Contains("tps_20261001T000000Z_c0ffee_1_000.jsonl") && left.Contains(mine0),
                  "this process trimmed its OLDEST closed segment, never its live one: " + string.Join(",", left));
            W.RetentionCapBytes = JawaBenchTpsMath.RetentionBytes;
            W.ResetForTest();
        }
    }
}
