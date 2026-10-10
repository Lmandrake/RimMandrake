// Installation and shutdown semantics (MUST 16).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;
using I = JawaBench.BridgeTools.JawaBenchTpsInstall;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static void T_InstallRollback()
        {
            var patched = new List<string>();
            bool rolledBack = false;
            var targets = new List<I.Target>
            {
                new I.Target("tick", true, () => "m1"),
                new I.Target("root", true, () => "m2"),
                new I.Target("save", false, () => "m3"),
            };
            string status = I.Run(targets, (name, m) => { if (name == "root") throw new InvalidOperationException("injected"); patched.Add(name); },
                                  () => { rolledBack = true; patched.Clear(); }, out var detail);
            Check(status == "failed" && rolledBack && patched.Count == 0,
                  "a patch that throws mid-install rolls back every earlier patch: status " + status + " rolledBack " + rolledBack + " left " + string.Join(",", patched));
            patched.Clear();
            targets[1] = new I.Target("root", true, () => "m2");
            targets[2] = new I.Target("save", false, () => null);       // optional target missing
            status = I.Run(targets, (name, m) => patched.Add(name), () => patched.Clear(), out detail);
            Check(status == "partial" && patched.Count == 2 && detail.Contains("save: missing"),
                  "a missing OPTIONAL target is 'partial', named, never 'complete': " + status + " / " + detail);
            targets[0] = new I.Target("tick", true, () => null);        // required target missing
            patched.Clear();
            status = I.Run(targets, (name, m) => patched.Add(name), () => patched.Clear(), out detail);
            Check(status == "failed" && patched.Count == 0, "a missing REQUIRED target patches nothing: " + status + " " + string.Join(",", patched));
        }

        private static void T_ShutdownBounded()
        {
            string d = PrepWriter();
            W.Start(d, "5d0e11", 9);
            var t0 = System.Diagnostics.Stopwatch.StartNew();
            var r = W.Shutdown("\"windows\":3", () => { Thread.Sleep(10000); return "never"; }, 1000, 1500);
            Check(t0.Elapsed.TotalSeconds < 5, "shutdown is bounded even when the log copy hangs: " + t0.Elapsed.TotalSeconds + " s");
            W.Drain(3000);
            string all = string.Join("\n", Directory.GetFiles(d, "tps_*.jsonl").Select(File.ReadAllText));
            Check(all.Contains("\"kind\":\"shutdown\"") && all.Contains("\"kind\":\"shutdown-complete\"") &&
                  all.Contains("\"archived\":false") && all.Contains("\"archiveTimedOut\":true"),
                  "intent and a completion row that states what did NOT finish: " + r);
            W.ResetForTest();
        }
    }
}
