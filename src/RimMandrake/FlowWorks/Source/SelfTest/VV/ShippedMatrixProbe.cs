// V&V pilot 1 (design/RimMandrake/vv_methods/pilot1_shipped_matrix_2026-10-16.md): the FlowWorks fuzz/property families
// run at the kernel flags the mod SHIPS, with honest (uncapped) failure counts.
//
// NOT-COMPILED by the normal SelfTest build (effective_def_lint's compile_include reads this marker and warns): RimMandrakeFlowWorks.SelfTest.csproj has EnableDefaultCompileItems=false and
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
		/// <summary>RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS: a planted break (--plant), so a law family is seen to go red
		/// at the shipped settings. "volume": ONE decilitre (the kernel's smallest unit of water) appears from nowhere in a
		/// wet cell (breaks volume conservation; RIMMANDRAKE_SHARPEN_FLOWWORKS_VOLUME_LAW_ONE_DECILITRE_SLIPS_BY: the law
		/// used to compare float levels with a 1e-3 tolerance, ten decilitres, so a one-decilitre leak slipped by); "bounds": a dug cell's depth is set to 5 (breaks 0 &lt;= F &lt;= D &lt;= 4), both on every seventh
		/// hook call; "shuttle": on EVERY hook call one decilitre moves between one KEPT pair of wet, non-sink cells of the
		/// same fluid, in different dug components where the grid has them (so the kernel cannot level the move away),
		/// the direction flipping each call (a settled scene's water is often under a level a cell); a move is made only when the
		/// donor has the decilitre and the receiver has room (a dry receiver is claimed for the pair's fluid), so
		/// volume, bounds, each fluid's total and the sinks are kept and only the settling law should see it
		/// (RIMMANDRAKE_PLANT_FLOWWORKS_SETTLING_LAW_SHUTTLE_TRIPS_OTHERS: the old shuttle tripped the fluid and sink laws
		/// first, and could not reverse its own move). After the flags, never in a
		/// normal run (Plant is null).</summary>
		public static string Plant;
		public static long Planted;
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

		private static RM_FlowKernel shK;
		private static int shA = -1, shB = -1;
		private static object shFluid;
		private static bool shToB;

		/// <summary>A cell the shuttle may use: dug, not a sink, and dry or holding the pair's fluid.</summary>
		private static bool Usable(RM_FlowKernel k, int i, object fluid)
		{
			if (k.depth[i] == 0 || k.world.IsSink(i)) return false;
			object f = k.world.CellFluid(i);
			return k.water[i] == 0 ? true : f != null && Equals(f, fluid);
		}
		private static bool CanMove(RM_FlowKernel k, int from, int to) =>
			k.water[from] >= 1 && k.water[to] + 1 <= k.depth[to] * RM_LevelSolve.U;   // a decilitre to give; room for it

		/// <summary>The dug component (4-neighbour, depth &gt; 0) of every cell: -1 for an undug one.</summary>
		private static int[] Components(RM_FlowKernel k)
		{
			int n = k.depth.Length, wd = k.width, c = 0;
			var comp = Enumerable.Repeat(-1, n).ToArray();
			var stack = new Stack<int>();
			for (int s = 0; s < n; s++)
			{
				if (k.depth[s] == 0 || comp[s] >= 0) continue;
				comp[s] = c; stack.Push(s);
				while (stack.Count > 0)
				{
					int i = stack.Pop(), x = i % wd, y = i / wd;
					foreach (int j in new[] { x > 0 ? i - 1 : -1, x < wd - 1 ? i + 1 : -1, y > 0 ? i - wd : -1, y < k.height - 1 ? i + wd : -1 })
						if (j >= 0 && k.depth[j] > 0 && comp[j] < 0) { comp[j] = c; stack.Push(j); }
				}
				c++;
			}
			return comp;
		}

		/// <summary>Pick a wet donor and a partner that can trade a level with it, preferring two dug components (the
		/// kernel cannot level water between them, so the move is not undone).</summary>
		private static void Pick(RM_FlowKernel k)
		{
			shA = shB = -1;
			var comp = Components(k);
			for (int pass = 0; pass < 2 && shA < 0; pass++)
				for (int a = 0; a < k.depth.Length && shA < 0; a++)
				{
					if (k.water[a] == 0 || k.depth[a] == 0 || k.world.IsSink(a) || k.world.CellFluid(a) == null) continue;
					object f = k.world.CellFluid(a);
					for (int b = 0; b < k.depth.Length; b++)
						if (b != a && Usable(k, b, f) && (pass == 1 || comp[a] != comp[b]) && (CanMove(k, a, b) || CanMove(k, b, a)))
						{ shA = a; shB = b; shFluid = f; break; }
				}
		}

		private static void Shuttle(RM_FlowKernel k)
		{
			if (!ReferenceEquals(shK, k)) { shK = k; shA = shB = -1; }
			for (int attempt = 0; attempt < 2; attempt++)
			{
				bool kept = shA >= 0 && Usable(k, shA, shFluid) && Usable(k, shB, shFluid) && (k.water[shA] > 0 || k.water[shB] > 0);
				if (!kept) Pick(k);
				if (shA < 0) return;
				int from = shToB ? shA : shB, to = shToB ? shB : shA;
				if (!CanMove(k, from, to)) (from, to) = (to, from);
				if (CanMove(k, from, to))
				{
					if (k.water[to] == 0) k.world.Claim(to, shFluid);   // a dry receiver holds the pair's fluid, as a first level does
					k.water[from] -= 1; k.water[to] += 1; Planted++;
					shToB = to != shB;   // next call: back the other way
					return;
				}
				shA = shB = -1;   // the kept pair can move neither way now: pick again, once
			}
		}

		/// <summary>Called by the staged ArrayWorld.Pulse just before RM_FlowKernel.Pulse.</summary>
		public static void Apply(RM_FlowKernel k)
		{
			HookCalls++;
			if (Override) foreach (var (f, v) in Forced) f.SetValue(k, v);
			if (Plant == "shuttle" && k.depth != null && k.water != null && k.world != null) Shuttle(k);
			if (Plant != null && Plant != "shuttle" && HookCalls % 7 == 3 && k.depth != null && k.water != null)
			{
				for (int i = 0; i < k.depth.Length; i++)
				{
					if (k.depth[i] == 0) continue;
					if (Plant == "volume" && k.water[i] > 0 && k.water[i] + 1 <= k.depth[i] * RM_LevelSolve.U) { k.water[i] += 1; Planted++; break; }
					if (Plant == "bounds") { k.depth[i] = 5; Planted++; break; }
				}
			}
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
			MatrixFlags.Plant = Arg(args, "--plant");
			if (MatrixFlags.Plant != null && MatrixFlags.Plant != "volume" && MatrixFlags.Plant != "bounds" && MatrixFlags.Plant != "shuttle") { Console.WriteLine("VV: unknown --plant " + MatrixFlags.Plant); return 2; }
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
			bool anyUnmeasured = false;
			foreach (string fam in fams)
			{
				var sw = Stopwatch.StartNew();
				long hook0 = MatrixFlags.HookCalls;
				int attempted = 0, completed = 0, failures = 0, errors = 0;
				var seeds = new List<int>(); var examples = new List<string>();
				bool timedOut = false, unmeasured = false;
				if (fam.StartsWith("surface_random"))
				{
					// fixed-seed family (rng 20261016, 1000 scenes), already uncapped: parse its own counts
					FlowKernelFuzz.LevelSet = fam.EndsWith("_levelset");
					string r = FlowKernelFuzz.SurfaceRandomScenesSettleAndConserve();
					FlowKernelFuzz.LevelSet = false;
					attempted = 1000;
					var m = System.Text.RegularExpressions.Regex.Match(r, @"(\d+) not at rest by pulse 150, (\d+) unbalanced, (\d+) with a wet step");
					// an unreadable answer is UNMEASURED with no completed count, never a measured 0/1000 (Codex review 2026-11-18)
					if (!m.Success) { errors = 1; unmeasured = true; completed = 0; examples.Add("unparsed: " + r); }
					else
					{
						completed = 1000;
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
					// cases < 0: the family never ran (VV_HOSE undefined) or its report did not parse. That is UNMEASURED,
					// never a clean record: count it as an error, keep the explanation, and fail the process (GPT FE_cs_selftests_4.3)
					if (cases < 0) { errors++; unmeasured = true; }
					if (fails > 0 || cases < 0) examples.Add(text.Length > 2500 ? text.Substring(0, 2500) : text);
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
					["timed_out"] = timedOut, ["unmeasured"] = unmeasured, ["seconds"] = Math.Round(sw.Elapsed.TotalSeconds, 2),
					["kernel_pulses_hooked"] = MatrixFlags.HookCalls - hook0, ["plant"] = MatrixFlags.Plant, ["planted"] = MatrixFlags.Planted,
					["failing_seeds"] = seeds, ["examples"] = examples,
				};
				anyUnmeasured |= unmeasured;
				w.WriteLine(Json(rec)); w.Flush();
				Console.WriteLine($"{config,-28} {fam,-32} {failures,6}/{completed,-7} {(timedOut ? "TIMEOUT " : "")}{sw.Elapsed.TotalSeconds,8:F1}s");
			}
			return anyUnmeasured ? 3 : 0;
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
			int mouthDry = 0;
			for (int p = 1; p <= pulses; p++)
			{
				w.Pulse(digs);
				string at = string.Join("", digs.Select(c => w.k.Notch(c)));
				bool full = at.All(ch => ch == '1');
				if (!full && w.k.Notch(digs[0]) == 0) mouthDry++;
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
