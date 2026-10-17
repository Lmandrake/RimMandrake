// V&V pilot 1 (design/RimMandrake/vv_methods/pilot1_shipped_matrix_2026-10-16.md): the FlowWorks fuzz/property families
// run at the kernel flags the mod SHIPS, with honest (uncapped) failure counts.
//
// NOT part of the normal SelfTest build: RimMandrakeFlowWorks.SelfTest.csproj has EnableDefaultCompileItems=false and
// does not list this file. src/RimMandrake/Utils/vv_shipped_matrix.py stages the SelfTest tree on D:, inserts ONE hook
// line into the STAGED copy of ArrayWorld.Pulse (MatrixFlags.Apply(k) just before k.Pulse - the same moment the adapter,
// RM_MapComponent_Excavation.DoPulse, writes the settings into the kernel) and one into Program.Case (the case name),
// and builds a probe project around this file. Nothing in the clone is modified.
//
// Modes (args):
//   rates  --config NAME --set f=v;f=v --families a,b --n N --base B --cap-seconds S --out FILE
//          per-seed run of each family; every failure counted (no stop at K); first 5 messages kept.
//   suite  [--set f=v;...] --out FILE [--record]
//          runs the real Program.Main once (every case), optionally forcing the flags; with --record tallies, per case,
//          which value each kernel flag held at every pulse (the dynamic flag lint).
// --set empty = AUTHORED (each family keeps the flags it sets itself).

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

namespace RimMandrake.FlowWorks.SelfTest.VV
{
	public static class MatrixFlags
	{
		public static bool Override, Record;
		public static string CurrentCase = "(none)";
		public static readonly List<(FieldInfo f, object v)> Forced = new List<(FieldInfo, object)>();
		public static readonly List<FieldInfo> Tracked = new List<FieldInfo>();
		// (case, field, value) -> pulses; (case, tuple) -> pulses
		public static readonly Dictionary<string, long> FieldTally = new Dictionary<string, long>();
		public static readonly Dictionary<string, long> TupleTally = new Dictionary<string, long>();
		public static long HookCalls;

		public static void Configure(string set, IEnumerable<string> track)
		{
			Forced.Clear(); Tracked.Clear();
			var t = typeof(RM_FlowKernel);
			foreach (string name in track)
			{
				var f = t.GetField(name, BindingFlags.Public | BindingFlags.Instance);
				if (f == null) throw new Exception("VV: RM_FlowKernel has no public field " + name + " (the adapter list and the kernel drifted)");
				Tracked.Add(f);
			}
			Override = false;
			if (string.IsNullOrEmpty(set)) return;
			foreach (string kv in set.Split(';', StringSplitOptions.RemoveEmptyEntries))
			{
				string[] p = kv.Split('=');
				var f = t.GetField(p[0], BindingFlags.Public | BindingFlags.Instance);
				if (f == null) throw new Exception("VV: RM_FlowKernel has no public field " + p[0]);
				object v = f.FieldType == typeof(bool) ? (object)(p[1] == "1" || p[1] == "true") : Convert.ChangeType(p[1], f.FieldType, System.Globalization.CultureInfo.InvariantCulture);
				Forced.Add((f, v));
			}
			Override = Forced.Count > 0;
		}

		/// <summary>Called by the staged ArrayWorld.Pulse just before RM_FlowKernel.Pulse.</summary>
		public static void Apply(RM_FlowKernel k)
		{
			HookCalls++;
			if (Override) foreach (var (f, v) in Forced) f.SetValue(k, v);
			if (!Record) return;
			var sb = new StringBuilder();
			foreach (var f in Tracked)
			{
				string v = Convert.ToString(f.GetValue(k), System.Globalization.CultureInfo.InvariantCulture);
				string key = CurrentCase + "\t" + f.Name + "\t" + v;
				FieldTally[key] = FieldTally.GetValueOrDefault(key) + 1;
				sb.Append(f.Name).Append('=').Append(v).Append(';');
			}
			string tk = CurrentCase + "\t" + sb;
			TupleTally[tk] = TupleTally.GetValueOrDefault(tk) + 1;
		}
	}

	public static class ShippedMatrixProbe
	{
		static string Arg(string[] a, string k, string d = null) { int i = Array.IndexOf(a, k); return i >= 0 && i + 1 < a.Length ? a[i + 1] : d; }

		// ── reflection into FlowKernelFuzz's private generator and runner (no edit to the test file) ──
		static readonly Type FKF = typeof(FlowKernelFuzz);
		static readonly MethodInfo GenM = FKF.GetMethod("Gen", BindingFlags.NonPublic | BindingFlags.Static);
		static readonly MethodInfo RunM = FKF.GetMethod("Run", BindingFlags.NonPublic | BindingFlags.Static);
		static readonly FieldInfo DigsF = GenM?.ReturnType.GetField("digs");

		static string KernelFuzzOne(int seed)
		{
			object s = GenM.Invoke(null, new object[] { seed });
			return (string)RunM.Invoke(null, new object[] { s, DigsF.GetValue(s) });
		}

		// by reflection: the negative-control build compiles the pre-fix FlowKernelFuzz.cs, whose FillsFromLimitless has no
		// `shipped` parameter yet (the forced flags do that job there)
		static readonly MethodInfo FillsM = FKF.GetMethod("FillsFromLimitless", BindingFlags.Public | BindingFlags.Static);
		static List<string> Fills(int seed, bool shippedArg)
		{
			var ps = FillsM.GetParameters();
			if (ps.Length >= 3) return (List<string>)FillsM.Invoke(null, new object[] { 1, seed, shippedArg });
			if (shippedArg) throw new Exception("this FlowKernelFuzz.cs has no shipped argument");
			return (List<string>)FillsM.Invoke(null, new object[] { 1, seed });
		}

		static string FirstOf(List<string> l) => l.Count == 0 ? null : l[0];

		/// <summary>Per-seed families. Each returns null (held) or a failure message. shrunk(seed) gives the family's own
		/// shrunk report where it has one (called for the first 5 failures only).</summary>
		static readonly Dictionary<string, (Func<int, string> one, Func<int, string> shrunk)> Families = new Dictionary<string, (Func<int, string>, Func<int, string>)>
		{
			["kernel_fuzz"] = (KernelFuzzOne, s => FirstOf(FlowKernelFuzz.Fuzz(1, s))),
			["fills_from_limitless"] = (s => FirstOf(Fills(s, false)), null),
			["fills_from_limitless_shippedarg"] = (s => FirstOf(Fills(s, true)), null),
			["seq_sequences"] = (s => FirstOf(SequenceFuzz.Sequences(1, s)), null),
			["seq_orders"] = (s => FirstOf(SequenceFuzz.Orders(1, s)), null),
			["seq_conversion"] = (s => FirstOf(SequenceFuzz.Conversion(1, s)), null),
			["seq_pitwidth"] = (s => FirstOf(SequenceFuzz.PitWidth(1, s)), null),
		};

		public static int Main(string[] args)
		{
			string mode = args.Length > 0 ? args[0] : "";
			string outPath = Arg(args, "--out");
			var track = (Arg(args, "--track", "") ?? "").Split(',', StringSplitOptions.RemoveEmptyEntries);
			MatrixFlags.Configure(Arg(args, "--set", ""), track);
			if (GenM == null || RunM == null || DigsF == null) { Console.WriteLine("VV: FlowKernelFuzz.Gen/Run not found by reflection"); return 3; }
			if (mode == "rates") return Rates(args, outPath);
			if (mode == "suite") return Suite(args, outPath);
			if (mode == "trace") return Trace(args);
			Console.WriteLine("usage: rates|suite ...");
			return 2;
		}

		static int Rates(string[] args, string outPath)
		{
			string config = Arg(args, "--config", "?");
			int n = int.Parse(Arg(args, "--n", "1000"));
			int baseSeed = int.Parse(Arg(args, "--base", "500000"));
			double cap = double.Parse(Arg(args, "--cap-seconds", "900"), System.Globalization.CultureInfo.InvariantCulture);
			var fams = Arg(args, "--families", string.Join(",", Families.Keys)).Split(',', StringSplitOptions.RemoveEmptyEntries);
			using var w = new StreamWriter(outPath, true);
			foreach (string fam in fams)
			{
				var sw = Stopwatch.StartNew();
				long hook0 = MatrixFlags.HookCalls;
				int attempted = 0, completed = 0, failures = 0, errors = 0;
				var seeds = new List<int>(); var examples = new List<string>();
				bool timedOut = false;
				if (fam.StartsWith("surface_random"))
				{
					// fixed-seed family (rng 20261016, 1000 scenes), already uncapped: parse its own counts
					FlowKernelFuzz.LevelSet = fam.EndsWith("_levelset");
					string r = FlowKernelFuzz.SurfaceRandomScenesSettleAndConserve();
					FlowKernelFuzz.LevelSet = false;
					attempted = completed = 1000;
					var m = System.Text.RegularExpressions.Regex.Match(r, @"(\d+) not at rest by pulse 150, (\d+) unbalanced, (\d+) with a wet step");
					if (!m.Success) { errors = 1; examples.Add("unparsed: " + r); }
					else
					{
						// a scene can fail more than one check: the family reports per-check counts, so the union is bounded by the sum
						int a = int.Parse(m.Groups[1].Value), b = int.Parse(m.Groups[2].Value), c = int.Parse(m.Groups[3].Value);
						failures = Math.Max(a, Math.Max(b, c));   // lower bound of failing scenes; the per-check split is in the example
						if (a + b + c > 0) examples.Add(r.Length > 1500 ? r.Substring(0, 1500) : r);
					}
				}
				else if (fam == "hose" || fam == "trail")
				{
					var (cases, fails, text) = HoseFamily(fam, n);
					attempted = completed = cases; failures = fails;
					if (fails > 0) examples.Add(text.Length > 2500 ? text.Substring(0, 2500) : text);
				}
				else
				{
					if (!Families.TryGetValue(fam, out var f)) { Console.WriteLine("VV: unknown family " + fam); return 2; }
					for (int k = 0; k < n; k++)
					{
						if (sw.Elapsed.TotalSeconds > cap) { timedOut = true; break; }
						int seed = baseSeed + k;
						attempted++;
						string err;
						try { err = f.one(seed); }
						catch (Exception e) { err = "EXCEPTION " + (e.InnerException ?? e).GetType().Name + ": " + (e.InnerException ?? e).Message; errors++; }
						completed++;
						if (err == null) continue;
						failures++;
						if (seeds.Count < 2000) seeds.Add(seed);
						if (examples.Count < 5)
						{
							string sh = null;
							try { sh = f.shrunk?.Invoke(seed); } catch (Exception e) { sh = "shrink threw " + e.Message; }
							string ex = "seed " + seed + ": " + (sh ?? err);
							examples.Add(ex.Length > 1500 ? ex.Substring(0, 1500) : ex);
						}
					}
				}
				sw.Stop();
				var rec = new Dictionary<string, object>
				{
					["config"] = config, ["family"] = fam, ["n_requested"] = fam.StartsWith("surface_random") ? 1000 : n, ["base_seed"] = baseSeed,
					["attempted"] = attempted, ["completed"] = completed, ["failures"] = failures, ["exceptions"] = errors,
					["timed_out"] = timedOut, ["seconds"] = Math.Round(sw.Elapsed.TotalSeconds, 2),
					["kernel_pulses_hooked"] = MatrixFlags.HookCalls - hook0,
					["failing_seeds"] = seeds, ["examples"] = examples,
				};
				w.WriteLine(Json(rec)); w.Flush();
				Console.WriteLine($"{config,-28} {fam,-32} {failures,6}/{completed,-7} {(timedOut ? "TIMEOUT " : "")}{sw.Elapsed.TotalSeconds,8:F1}s");
			}
			return 0;
		}

		/// <summary>The hose/trail fuzz already counts every failure (HoseFuzz.Tally): run it at a scale and read its report.</summary>
		static (int cases, int fails, string text) HoseFamily(string fam, int n)
		{
#if VV_HOSE
			double scale = n / 1500.0;
			var old = Console.Out; var sb = new StringWriter(); Console.SetOut(sb);
			try { HoseFuzz.Run(new[] { "--fuzz-scale", scale.ToString(System.Globalization.CultureInfo.InvariantCulture), "--fuzz-only", fam }); }
			finally { Console.SetOut(old); }
			string text = sb.ToString();
			var mc = System.Text.RegularExpressions.Regex.Match(text, @"fuzz " + fam + @"\s+(\d+) cases");
			int cases = mc.Success ? int.Parse(mc.Groups[1].Value) : -1;
			int fails = 0;
			foreach (System.Text.RegularExpressions.Match g in System.Text.RegularExpressions.Regex.Matches(text, @"^\s{4}(\d+) x ", System.Text.RegularExpressions.RegexOptions.Multiline)) fails += int.Parse(g.Groups[1].Value);
			return (cases, fails, text);
#else
			return (-1, 0, "hose family not compiled into this probe (VV_HOSE undefined)");
#endif
		}

		/// <summary>Reproducer for a classified finding: CanalMouthDeadEndFillsFromFarEnd's scene (a 60-cell water body beside
		/// the mouth of a dead-end 1x10 D=1 channel), under the forced flags, printing the channel after every pulse.
		/// --body limited|limitless.</summary>
		static int Trace(string[] args)
		{
			bool limitless = Arg(args, "--body", "limited") == "limitless";
			int pulses = int.Parse(Arg(args, "--pulses", "12"));
			var w = new ArrayWorld(20, 6);
			var bodyCells = new List<int>();
			for (int z = 0; z < 6; z++) for (int x = 0; x < 10; x++) bodyCells.Add(z * 20 + x);
			var body = w.AddBody(limitless, 300f, bodyCells);
			var digs = Enumerable.Range(10, 10).Select(x => 2 * 20 + x).ToList();
			foreach (int c in digs) w.k.depth[c] = 1;
			w.k.creepWaterEnabled = true;
			int mouthDry = 0;
			for (int p = 1; p <= pulses; p++)
			{
				w.Pulse(digs);
				string at = string.Join("", digs.Select(c => w.k.fill[c]));
				bool full = at.All(ch => ch == '1');
				if (!full && w.k.fill[digs[0]] == 0) mouthDry++;
				Console.WriteLine($"pulse {p,3}: {at}  stock {(limitless ? "inf" : body.stock.ToString("F0"))}");
			}
			Console.WriteLine($"pulses with the mouth dry while the channel is not yet full: {mouthDry}");
			return 0;
		}

		static int Suite(string[] args, string outPath)
		{
			MatrixFlags.Record = Array.IndexOf(args, "--record") >= 0;
			var main = typeof(FlowKernelFuzz).Assembly.GetType("RimMandrake.FlowWorks.SelfTest.Program")?.GetMethod("Main", BindingFlags.NonPublic | BindingFlags.Static);
			if (main == null) { Console.WriteLine("VV: Program.Main not found"); return 3; }
			int rc = (int)main.Invoke(null, new object[] { new string[0] });
			var rec = new Dictionary<string, object>
			{
				["mode"] = "suite", ["override"] = MatrixFlags.Override, ["rc"] = rc, ["hook_calls"] = MatrixFlags.HookCalls,
				["field_tally"] = MatrixFlags.FieldTally.Select(kv => kv.Key + "\t" + kv.Value).ToList(),
				["tuple_tally"] = MatrixFlags.TupleTally.Select(kv => kv.Key + "\t" + kv.Value).ToList(),
			};
			File.WriteAllText(outPath, Json(rec));
			Console.WriteLine($"VV suite rc={rc} hookCalls={MatrixFlags.HookCalls}");
			return 0;
		}

		// ── a tiny JSON writer (no package references in the probe) ──
		static string Json(object o)
		{
			switch (o)
			{
				case null: return "null";
				case string s: return "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n").Replace("\r", "").Replace("\t", "\\t") + "\"";
				case bool b: return b ? "true" : "false";
				case int or long: return Convert.ToString(o, System.Globalization.CultureInfo.InvariantCulture);
				case double d: return d.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
				case Dictionary<string, object> m: return "{" + string.Join(",", m.Select(kv => Json(kv.Key) + ":" + Json(kv.Value))) + "}";
				case System.Collections.IEnumerable e: return "[" + string.Join(",", e.Cast<object>().Select(Json)) + "]";
				default: return Json(o.ToString());
			}
		}
	}
}
