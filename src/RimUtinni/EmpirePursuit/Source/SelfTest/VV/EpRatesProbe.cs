// V&V pilot 1 (design/RimMandrake/vv_methods/pilot1_shipped_matrix_2026-10-16.md): EmpirePursuit's fuzz families with
// honest (uncapped) failure counts. The families stop at 3 failures; this calls each one per seed (n = 1) through
// reflection, so every failing seed is counted. Not part of the normal fuzz build: src/RimMandrake/Utils/vv_shipped_matrix.py
// builds a probe project around it on a D: stage.
//   rates --families ladder,timers,math --n N --base B --cap-seconds S --out FILE

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;

namespace RuthlessPursuingMechanoids.Fuzz.VV
{
	public static class EpRatesProbe
	{
		static string Arg(string[] a, string k, string d = null) { int i = Array.IndexOf(a, k); return i >= 0 && i + 1 < a.Length ? a[i + 1] : d; }

		public static int Main(string[] args)
		{
			var t = typeof(EmpirePursuitFuzz);
			var fams = new Dictionary<string, MethodInfo>
			{
				["ladder"] = t.GetMethod("Ladder", BindingFlags.NonPublic | BindingFlags.Static),
				["timers"] = t.GetMethod("Timers", BindingFlags.NonPublic | BindingFlags.Static),
				["math"] = t.GetMethod("Math_", BindingFlags.NonPublic | BindingFlags.Static),
			};
			if (fams.Values.Any(m => m == null)) { Console.WriteLine("VV: an EmpirePursuitFuzz family was not found by reflection"); return 3; }
			int n = int.Parse(Arg(args, "--n", "1000"));
			int baseSeed = int.Parse(Arg(args, "--base", "500000"));
			double cap = double.Parse(Arg(args, "--cap-seconds", "900"), System.Globalization.CultureInfo.InvariantCulture);
			string outPath = Arg(args, "--out");
			using var w = new StreamWriter(outPath, true);
			foreach (string fam in Arg(args, "--families", "ladder,timers,math").Split(','))
			{
				var m = fams[fam];
				var sw = Stopwatch.StartNew();
				int attempted = 0, completed = 0, failures = 0, exceptions = 0; bool timedOut = false;
				var seeds = new List<int>(); var examples = new List<string>();
				for (int k = 0; k < n; k++)
				{
					if (sw.Elapsed.TotalSeconds > cap) { timedOut = true; break; }
					int seed = baseSeed + k; attempted++;
					List<string> r;
					try { r = (List<string>)m.Invoke(null, new object[] { 1, seed }); }
					catch (Exception e) { r = new List<string> { "EXCEPTION " + (e.InnerException ?? e).Message }; exceptions++; }
					completed++;
					if (r.Count == 0) continue;
					failures++;
					if (seeds.Count < 2000) seeds.Add(seed);
					if (examples.Count < 5) examples.Add(r[0].Length > 1500 ? r[0].Substring(0, 1500) : r[0]);
				}
				string J(string s) => "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n").Replace("\r", "").Replace("\t", "\\t") + "\"";
				w.WriteLine("{\"config\":\"SHIPPED_GATES_IN_DISTRIBUTION\",\"family\":\"ep_" + fam + "\",\"n_requested\":" + n + ",\"base_seed\":" + baseSeed
					+ ",\"attempted\":" + attempted + ",\"completed\":" + completed + ",\"failures\":" + failures + ",\"exceptions\":" + exceptions
					+ ",\"timed_out\":" + (timedOut ? "true" : "false") + ",\"seconds\":" + sw.Elapsed.TotalSeconds.ToString("F2", System.Globalization.CultureInfo.InvariantCulture)
					+ ",\"failing_seeds\":[" + string.Join(",", seeds) + "],\"examples\":[" + string.Join(",", examples.Select(J)) + "]}");
				w.Flush();
				Console.WriteLine($"ep_{fam,-10} {failures,6}/{completed,-7} {(timedOut ? "TIMEOUT " : "")}{sw.Elapsed.TotalSeconds,8:F1}s");
			}
			return 0;
		}
	}
}
