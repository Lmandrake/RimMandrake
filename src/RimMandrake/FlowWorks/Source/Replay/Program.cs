// HOSE_PERF_BUILD_OFFLINE_REPLAY_HARNESS: the command line.
//   gen  --scenario NAME --out FILE                         write one generated trace
//   run  (--scenario NAME|all | --trace FILE) --out DIR      replay, report, gate (exit 0 = every gate green)
//        [--inject FAULT[,FAULT]] [--baseline FILE] [--write-baseline FILE] [--no-oracle] [--bar-ms 0.05]
// Gates: conserve, noflow, patch, comps, determinism, alloc, ceiling (see ReplayTick.Fault). Time is reported, never gated.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;

namespace RimMandrake.FlowWorks.Replay
{
    internal static class Program
    {
        private static int Main(string[] args)
        {
            try { return Run(args); }
            catch (Exception e) { Console.Error.WriteLine("hose_replay: " + e); return 3; }
        }

        private static string Opt(string[] a, string name, string dflt = null)
        {
            for (int i = 0; i < a.Length - 1; i++) if (a[i] == name) return a[i + 1];
            return dflt;
        }

        private static bool Flag(string[] a, string name) => Array.IndexOf(a, name) >= 0;

        private static int Run(string[] a)
        {
            if (a.Length == 0) { Console.Error.WriteLine("usage: gen|run ... (see Program.cs)"); return 2; }
            if (a[0] == "gen")
            {
                Trace t = TraceGen.Make(Opt(a, "--scenario"));
                t.Save(Opt(a, "--out"));
                Console.WriteLine("wrote " + Opt(a, "--out") + " (" + t.Events.Count + " events, " + t.Ticks + " ticks)");
                return 0;
            }
            if (a[0] != "run") { Console.Error.WriteLine("unknown verb " + a[0]); return 2; }

            string outDir = Opt(a, "--out") ?? ".";
            Directory.CreateDirectory(outDir);
            Fault fault = Fault.None;
            foreach (string f in (Opt(a, "--inject") ?? "").Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries))
                fault |= (Fault)Enum.Parse(typeof(Fault), f, true);
            bool oracle = !Flag(a, "--no-oracle");
            double bar = double.Parse(Opt(a, "--bar-ms", "0.05"), CultureInfo.InvariantCulture);
            Dictionary<string, long> baseline = Opt(a, "--baseline") is string bp && File.Exists(bp) ? LoadBaseline(bp) : null;
            if (Opt(a, "--baseline") != null && baseline == null) { Console.Error.WriteLine("baseline missing: " + Opt(a, "--baseline")); return 2; }

            var traces = new List<Func<Trace>>();
            if (Opt(a, "--trace") is string tp) traces.Add(() => Trace.Load(tp));
            else
            {
                string sc = Opt(a, "--scenario", "all");
                foreach (string s in sc == "all" ? TraceGen.Scenarios : sc.Split(','))
                {
                    string name = s;
                    traces.Add(() => TraceGen.Make(name));
                }
            }

            var newBaseline = new StringBuilder();
            newBaseline.Append("# hose replay op-count ceilings: scenario.work.sum|max value (written by --write-baseline; deterministic)\n");
            bool allGreen = true;
            var summary = new StringBuilder();
            foreach (Func<Trace> make in traces)
            {
                Trace t = make();
                ReplayResult r1 = new ReplayTick(t, fault, oracle).Run();
                ReplayResult r2 = new ReplayTick(make(), fault, false).Run();
                var gates = new SortedDictionary<string, string>();
                foreach (string g in new[] { "conserve", "noflow", "patch", "comps" })
                    gates[g] = r1.GateFails.TryGetValue(g, out int n) ? "RED x" + n : "green";
                int firstDiff = FirstDiff(r1.Fingerprints, r2.Fingerprints);
                gates["determinism"] = firstDiff < 0 ? "green" : "RED first diff at tick " + firstDiff;
                gates["alloc"] = r2.C.PatchBytesWarm == 0 ? "green" : "RED " + r2.C.PatchBytesWarm + " B in " + r2.C.PatchCallsWarm + " warm patches";
                var ceil = new List<string>();
                for (Work w = 0; w < Work.Count; w++)
                {
                    long sum = r1.C.WorkSum(w), max = r1.C.WorkMax(w, out _);
                    newBaseline.Append(t.Name).Append('.').Append(w).Append(".sum ").Append(sum).Append('\n');
                    newBaseline.Append(t.Name).Append('.').Append(w).Append(".max ").Append(max).Append('\n');
                    if (baseline == null) continue;
                    Check(baseline, t.Name + "." + w + ".sum", sum, ceil);
                    Check(baseline, t.Name + "." + w + ".max", max, ceil);
                }
                gates["ceiling"] = baseline == null ? "unchecked (no --baseline)" : ceil.Count == 0 ? "green" : "RED " + string.Join("; ", ceil.Take(4));
                bool green = gates.Values.All(v => !v.StartsWith("RED"));
                allGreen &= green;

                string report = Report(t, r1, r2, gates, bar, oracle, fault);
                File.WriteAllText(Path.Combine(outDir, t.Name + ".txt"), report);
                File.WriteAllText(Path.Combine(outDir, t.Name + ".fp"), string.Join("\n", r1.Fingerprints.Select(f => f.ToString("x16"))) + "\n");
                string line = "RESULT " + t.Name + " " + (green ? "PASS" : "FAIL") + " " + string.Join(" ", gates.Select(kv => kv.Key + "=" + (kv.Value.StartsWith("RED") ? "RED" : kv.Value.StartsWith("green") ? "green" : "skip")));
                Console.WriteLine(line);
                summary.Append(line).Append('\n');
            }
            File.WriteAllText(Path.Combine(outDir, "summary.txt"), summary.ToString());
            if (Opt(a, "--write-baseline") is string wb) { File.WriteAllText(wb, newBaseline.ToString()); Console.WriteLine("baseline written: " + wb); }
            return allGreen ? 0 : 1;
        }

        private static void Check(Dictionary<string, long> b, string key, long v, List<string> fails)
        {
            if (!b.TryGetValue(key, out long ceiling)) { fails.Add(key + " has no baseline"); return; }
            if (v > ceiling) fails.Add(key + " " + v + " > " + ceiling);
        }

        private static Dictionary<string, long> LoadBaseline(string path)
        {
            var d = new Dictionary<string, long>();
            foreach (string line in File.ReadAllLines(path))
            {
                if (line.Length == 0 || line[0] == '#') continue;
                string[] f = line.Split(' ');
                d[f[0]] = long.Parse(f[1], CultureInfo.InvariantCulture);
            }
            return d;
        }

        private static int FirstDiff(ulong[] a, ulong[] b)
        {
            if (a.Length != b.Length) return 0;
            for (int i = 0; i < a.Length; i++) if (a[i] != b[i]) return i;
            return -1;
        }

        private static string Report(Trace t, ReplayResult r1, ReplayResult r2, SortedDictionary<string, string> gates, double bar, bool oracle, Fault fault)
        {
            var sb = new StringBuilder();
            var inv = CultureInfo.InvariantCulture;
            sb.Append("hose replay: ").Append(t.Name).Append("  ticks ").Append(t.Ticks).Append("  map ").Append(t.Width).Append('x').Append(t.Height)
              .Append("  reels ").Append(t.Reels.Count).Append("  tanks ").Append(t.Tanks.Count).Append("  events ").Append(t.Events.Count)
              .Append("  runtime ").Append(System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription)
              .Append("  inject ").Append(fault).Append("  oracle checks ").Append(r1.OracleChecks).Append('\n');
            sb.Append("\nGATES\n");
            foreach (var kv in gates) sb.Append("  ").Append(kv.Key.PadRight(12)).Append(kv.Value).Append('\n');
            foreach (string f in r1.Failures) sb.Append("    ").Append(f).Append('\n');
            sb.Append("\nTIME per tick, ms (run 2, no oracle; advisory, never gated; tick 0 includes JIT). bar ").Append(bar.ToString(inv)).Append(" ms\n");
            sb.Append("  system    mean      p99       max       over-bar  worst-tick  bytes-sum    bytes-max  gc0\n");
            Counters c = r2.C;
            for (Sys s = 0; s < Sys.Count; s++)
            {
                c.TimeStats(s, bar, out double mean, out double p99, out double max, out int over, out int worst);
                sb.Append("  ").Append(s.ToString().PadRight(9)).Append(F(mean)).Append(F(p99)).Append(F(max))
                  .Append(over.ToString(inv).PadRight(10)).Append(worst.ToString(inv).PadRight(12))
                  .Append(c.BytesSum(s).ToString(inv).PadRight(13)).Append(c.BytesMax(s).ToString(inv).PadRight(11)).Append(c.GcSum(s)).Append('\n');
            }
            sb.Append("  warm HoseWorldPatch.Patch: ").Append(c.PatchCallsWarm).Append(" calls, ").Append(c.PatchBytesWarm).Append(" bytes\n");
            sb.Append("\nWORK (run 1)  sum / max-per-tick @tick\n");
            for (Work w = 0; w < Work.Count; w++)
            {
                long max = r1.C.WorkMax(w, out int at);
                sb.Append("  ").Append(w.ToString().PadRight(16)).Append(r1.C.WorkSum(w).ToString(inv).PadRight(12)).Append(max).Append(" @").Append(at).Append('\n');
            }
            sb.Append("  moves with no shared component: ").Append(r1.NoCompMoves).Append('\n');
            // the worst ticks over all systems, with the events that landed on them
            var total = new double[t.Ticks];
            for (int i = 0; i < t.Ticks; i++) for (Sys s = 0; s < Sys.Count; s++) total[i] += Counters.Ms(c.Elapsed[i, (int)s]);
            sb.Append("\nWORST TICKS (all systems, run 2)\n");
            foreach (int i in Enumerable.Range(0, t.Ticks).OrderByDescending(i => total[i]).Take(5))
            {
                sb.Append("  tick ").Append(i).Append("  ").Append(total[i].ToString("0.000", inv)).Append(" ms  [");
                for (Sys s = 0; s < Sys.Count; s++) sb.Append(' ').Append(s).Append('=').Append(Counters.Ms(c.Elapsed[i, (int)s]).ToString("0.000", inv));
                sb.Append(" ]  events:");
                int shown = 0;
                foreach (TraceEvent e in t.Events)
                {
                    if (e.Tick != i) continue;
                    if (shown++ == 6) { sb.Append(" ..."); break; }
                    sb.Append(' ').Append(e.Kind);
                    foreach (int v in e.A) sb.Append(':').Append(v);
                }
                if (shown == 0) sb.Append(" (none: schedule only)");
                sb.Append('\n');
            }
            return sb.ToString();
        }

        private static string F(double v) => v.ToString("0.0000", CultureInfo.InvariantCulture).PadRight(10);
    }
}
