// Approach B, phase 2 (design/RimMandrake/flowworks_offline_kernel_B.md): the PRODUCTION grid transition,
// RM_FlowKernel.cs (the same file RM_MapComponent_Excavation.DoPulse calls in game), driven by generated scenes on
// plain arrays. The only test-side code is ArrayWorld: bodies, fluids and sinks as arrays, with bodies formed by
// the production RM_FlowKernel.CollectBody walk.

using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
	internal sealed class Fluid
	{
		public string name; public int tpt; public float vpt = 1f;
		public override string ToString() => name;
	}

	internal sealed class ArrayWorld : RM_IFlowWorld
	{
		public static readonly Fluid Water = new Fluid { name = "water", tpt = 60 };
		public static readonly Fluid Tar = new Fluid { name = "tar", tpt = 360 };
		public static readonly Fluid Oil = new Fluid { name = "oil", tpt = 180 };

		public sealed class Body { public int id; public bool limitless; public float stock; public Fluid fluid; public List<int> cells = new List<int>(); }

		public readonly int w, h;
		public readonly RM_FlowKernel k;
		public readonly bool[] natural;
		public readonly Fluid[] terrainFluid;     // which liquid the natural terrain is
		public readonly Fluid[] cellFluid;        // the fluid grid of excavated cells
		public readonly bool[] sink;
		public readonly int[] bodyOf;
		public readonly List<Body> bodies = new List<Body>();
		public readonly Dictionary<Fluid, float> externalIn = new Dictionary<Fluid, float>();
		public Fluid activeFluid = Water;

		public ArrayWorld(int w, int h)
		{
			this.w = w; this.h = h;
			k = new RM_FlowKernel(w, h) { world = this, depth = new byte[w * h], fill = new byte[w * h] };
			natural = new bool[w * h]; terrainFluid = new Fluid[w * h]; cellFluid = new Fluid[w * h];
			sink = new bool[w * h]; bodyOf = Enumerable.Repeat(-1, w * h).ToArray();
		}

		/// <summary>RM_LiquidStock.BodyAt/FormBody's shape: lazily, with the production walk; fluid from the seed.</summary>
		public Body BodyAt(int idx, float stockFraction = 1f, bool limitless = false)
		{
			if (bodyOf[idx] >= 0) return bodies[bodyOf[idx]];
			if (!k.IsSource(idx)) return null;
			var found = new List<int>();
			int owned = RM_FlowKernel.CollectBody(w, h, idx, i => k.IsSource(i), i => bodyOf[i], 4000, found,
				new List<int>(), new HashSet<int>(), out bool edge, out bool trunc);
			if (owned >= 0) { foreach (int f in found) bodyOf[f] = owned; return bodies[owned]; }
			var b = new Body { id = bodies.Count, limitless = limitless, fluid = terrainFluid[idx] ?? Water, cells = found };
			b.stock = (float)Math.Floor(found.Count * 5 * stockFraction);
			bodies.Add(b);
			foreach (int f in found) bodyOf[f] = b.id;
			return b;
		}

		/// <summary>A body given outright (the oracle's bodies are declared, not walked).</summary>
		public Body AddBody(bool limitless, float stock, IEnumerable<int> cells)
		{
			var b = new Body { id = bodies.Count, limitless = limitless, stock = stock, fluid = Water, cells = cells.ToList() };
			bodies.Add(b);
			foreach (int c in b.cells) { natural[c] = true; terrainFluid[c] = Water; bodyOf[c] = b.id; }
			return b;
		}

		public bool IsNaturalLiquid(int idx) => natural[idx];
		public bool CanSupply(int idx) { var b = BodyAt(idx); return b == null || RM_StockMath.CanSupply(b.limitless, b.stock, (b.fluid ?? activeFluid).vpt); }
		public bool TryDebitLevel(int idx)
		{
			var b = BodyAt(idx);
			if (b == null) return true;
			float unit = (b.fluid ?? activeFluid).vpt;
			if (b.limitless) { externalIn[b.fluid] = externalIn.GetValueOrDefault(b.fluid) + 1; return true; }
			if (!RM_StockMath.CanDebit(false, b.stock, unit)) return false;
			b.stock -= unit;
			return true;
		}
		public object DonorFluid(int idx, bool source) => source ? BodyAt(idx)?.fluid : cellFluid[idx];
		public object CellFluid(int idx) => cellFluid[idx];
		public void Claim(int idx, object fluid) => cellFluid[idx] = (fluid as Fluid) ?? activeFluid;
		public int TicksPerTile(object fluid) => ((fluid as Fluid) ?? activeFluid)?.tpt ?? RM_StockMath.WaterTicksPerTile;
		public bool IsSink(int idx) => sink[idx];
		public void ComponentResolved(List<int> component) { }

		/// <summary>RM_MapComponent_Excavation.SyncFluidIdentity's grid half.</summary>
		public void Sync()
		{
			for (int i = 0; i < w * h; i++)
			{
				if (k.depth[i] == 0) continue;
				if (k.fill[i] == 0) cellFluid[i] = null;
				else if (cellFluid[i] == null) cellFluid[i] = activeFluid;
			}
		}

		public long pulse;
		public void Pulse(IEnumerable<int> seeds) { pulse++; k.Pulse(seeds, pulse); Sync(); }

		public Dictionary<Fluid, float> Totals()
		{
			var t = new Dictionary<Fluid, float>();
			for (int i = 0; i < w * h; i++) if (k.depth[i] > 0 && k.fill[i] > 0) t[cellFluid[i]] = t.GetValueOrDefault(cellFluid[i]) + k.fill[i];
			foreach (var b in bodies) if (!b.limitless) t[b.fluid] = t.GetValueOrDefault(b.fluid) + b.stock;
			return t;
		}

		public string Grid()
		{
			var sb = new System.Text.StringBuilder();
			for (int z = h - 1; z >= 0; z--)
			{
				for (int x = 0; x < w; x++)
				{
					int i = z * w + x;
					if (k.depth[i] > 0) sb.Append(k.fill[i]).Append('/').Append(k.depth[i]).Append(cellFluid[i]?.name[0] ?? '.').Append(' ');
					else if (natural[i]) sb.Append(" ~").Append(terrainFluid[i].name[0]).Append("  ");
					else sb.Append(" ..  ");
				}
				sb.Append('\n');
			}
			return sb.ToString();
		}
	}

	internal static class FlowKernelFuzz
	{
		public static long Cases, Pulses;

		// ── a generated scene: grid, liquids, dig list (seed order = dig order), sinks, pulses ──
		internal struct Scene
		{
			public int seed, w, h, pulses; public bool limitless, sinks, viscosity, multiFluid; public float stock;
			public List<(int idx, int depth)> digs; public List<(int idx, Fluid f)> liquid;
		}

		private static Scene Gen(int seed)
		{
			var r = new Random(seed);
			var s = new Scene { seed = seed, w = r.Next(4, 11), h = r.Next(4, 11), pulses = r.Next(5, 120) };
			s.limitless = r.Next(3) == 0; s.sinks = r.Next(4) == 0; s.viscosity = r.Next(2) == 0; s.multiFluid = r.Next(2) == 0;
			s.stock = (float)r.NextDouble();
			s.liquid = new List<(int, Fluid)>();
			s.digs = new List<(int, int)>();
			int blobs = r.Next(1, 4);
			Fluid[] fl = s.multiFluid ? new[] { ArrayWorld.Water, ArrayWorld.Tar, ArrayWorld.Oil } : new[] { ArrayWorld.Water };
			for (int b = 0; b < blobs; b++)
			{
				int x0 = r.Next(s.w), z0 = r.Next(s.h), bw = r.Next(1, 4), bh = r.Next(1, 4);
				Fluid f = fl[r.Next(fl.Length)];
				for (int x = x0; x < Math.Min(s.w, x0 + bw); x++) for (int z = z0; z < Math.Min(s.h, z0 + bh); z++) s.liquid.Add((z * s.w + x, f));
			}
			int nd = r.Next(1, s.w * s.h / 2);
			for (int d = 0; d < nd; d++) s.digs.Add((r.Next(s.w * s.h), r.Next(1, 5)));
			return s;
		}

		private static ArrayWorld Build(Scene s, List<(int idx, int depth)> digs)
		{
			var w = new ArrayWorld(s.w, s.h);
			foreach (var (idx, f) in s.liquid) { w.natural[idx] = true; w.terrainFluid[idx] = f; }
			foreach (var (idx, d) in digs)
			{
				if (w.natural[idx]) continue; // digging into a source is a different game path
				w.k.depth[idx] = (byte)Math.Max(w.k.depth[idx], d);
			}
			w.k.edgeSinksEnabled = s.sinks;
			w.k.viscosityEnabled = s.viscosity;
			if (s.sinks) for (int i = 0; i < s.w * s.h; i++) { int x = i % s.w, z = i / s.w; w.sink[i] = x == 0 || z == 0; }
			// form every body up front (stock and limitless are scene properties)
			for (int i = 0; i < s.w * s.h; i++) if (w.natural[i]) w.BodyAt(i, s.stock, s.limitless);
			return w;
		}

		private static List<int> SeedOrder(ArrayWorld w, List<(int idx, int depth)> digs)
		{
			var seen = new HashSet<int>(); var l = new List<int>();
			foreach (var (idx, _) in digs) if (w.k.depth[idx] > 0 && seen.Add(idx)) l.Add(idx);
			return l;
		}

		/// <summary>Run a scene; null = every invariant held.</summary>
		private static string Run(Scene s, List<(int idx, int depth)> digs)
		{
			var w = Build(s, digs);
			var seeds = SeedOrder(w, digs);
			int n = w.w * w.h;
			var prevFill = new byte[n];
			var prevFluid = new Fluid[n];
			var history = new List<string>();
			for (int p = 0; p < s.pulses; p++)
			{
				Array.Copy(w.k.fill, prevFill, n);
				Array.Copy(w.cellFluid, prevFluid, n);
				var t0 = w.Totals();
				w.externalIn.Clear();
				w.Pulse(seeds);
				Pulses++;
				if (w.k.worstImbalance > 0) return $"pulse {p}: kernel ledger {string.Join("; ", w.k.imbalanceReports)}";
				for (int i = 0; i < n; i++)
				{
					if (w.k.fill[i] > w.k.depth[i] || w.k.depth[i] > 4) return $"pulse {p}: 0<=F<=D<=4 broken at {i}";
					// (A cell MAY change fluid across a pulse: it can give or drain its last level and then be claimed
					// by another fluid in the same pulse - measured, seed 4764. "Never mix" is enforced below as
					// per-fluid conservation, which a transmutation cannot pass.)
				}
				foreach (var b in w.bodies) if (!b.limitless && b.stock < 0) return $"pulse {p}: body {b.id} stock {b.stock}: unaffordable debit";
				var t1 = w.Totals();
				float in0 = t0.Values.Sum(), in1 = t1.Values.Sum(), ext = w.externalIn.Values.Sum();
				if (Math.Abs(in1 - (in0 + ext - w.k.sinkDrained)) > 1e-3) return $"pulse {p}: total volume {in0}->{in1}, +{ext} in, -{w.k.sinkDrained} sunk";
				// Sinks drain before any flow and components are disjoint, so a sink cell drains min(F, perPulse) of
				// the fluid it held at the start of the pulse.
				var sunk = new Dictionary<Fluid, float>();
				if (s.sinks)
					for (int i = 0; i < n; i++)
						if (w.sink[i] && w.k.depth[i] > 0 && prevFill[i] > 0)
							sunk[prevFluid[i]] = sunk.GetValueOrDefault(prevFluid[i]) + Math.Min(prevFill[i], w.k.flowPerPulse);
				if (Math.Abs(sunk.Values.Sum() - w.k.sinkDrained) > 1e-3) return $"pulse {p}: sink drained {w.k.sinkDrained}, cells account for {sunk.Values.Sum()}";
				foreach (var f in t0.Keys.Union(t1.Keys))
					{
						float want = t0.GetValueOrDefault(f) + w.externalIn.GetValueOrDefault(f) - sunk.GetValueOrDefault(f);
						if (Math.Abs(t1.GetValueOrDefault(f) - want) > 1e-3) return $"pulse {p}: {f} volume {t0.GetValueOrDefault(f)}->{t1.GetValueOrDefault(f)} (+{w.externalIn.GetValueOrDefault(f)} declared): one fluid became another";
					}
			}
			// No shuttle: with the inputs exhausted or steady, the grid settles. Allow the longest viscosity stride
			// (8) times two, then demand a fixed point over a further 24 pulses (lcm of strides 1,3,6,8).
			if (!s.sinks && s.pulses >= 100)
			{
				string a = Snapshot(w);
				var states = new HashSet<string>();
				for (int p = 0; p < 24; p++) { w.Pulse(seeds); Pulses++; states.Add(Snapshot(w)); }
				if (states.Count > 1 && SettledExpected(w)) return $"no fixed point after {s.pulses} pulses: {states.Count} distinct states in 24 more\n{w.Grid()}";
			}
			return null;
		}

		private static string Snapshot(ArrayWorld w) => Convert.ToBase64String(w.k.fill);

		// A still-filling grid legitimately changes. Settled is expected when no source can still give.
		private static bool SettledExpected(ArrayWorld w) => w.bodies.All(b => !b.limitless && b.stock < 1f);

		public static List<string> Fuzz(int n, int baseSeed)
		{
			var fails = new List<string>();
			for (int k = 0; k < n && fails.Count < 5; k++)
			{
				var s = Gen(baseSeed + k);
				Cases++;
				string err = Run(s, s.digs);
				if (err == null) continue;
				var min = SequenceFuzz.Shrink(s.digs, d => Run(s, d) != null);
				var w = Build(s, min);
				fails.Add($"seed {s.seed} ({s.w}x{s.h}, {s.pulses} pulses, limitless={s.limitless} sinks={s.sinks} visc={s.viscosity}): " +
					$"{Run(s, min)}\n        digs (idx:depth, in order) {string.Join(" ", min.Select(d => d.idx + ":" + d.depth))}\n{w.Grid()}");
			}
			return fails;
		}

		// ── single-fluid liveness: a limitless water source fills every cell connected to it ──

		public static List<string> FillsFromLimitless(int n, int baseSeed)
		{
			var fails = new List<string>();
			for (int k = 0; k < n && fails.Count < 5; k++)
			{
				var r = new Random(baseSeed + k);
				Cases++;
				int W = r.Next(3, 10), H = r.Next(3, 10);
				var w = new ArrayWorld(W, H);
				int src = r.Next(W * H);
				w.natural[src] = true; w.terrainFluid[src] = ArrayWorld.Water;
				var digs = new List<int>();
				for (int d = 0; d < r.Next(1, W * H); d++) { int c = r.Next(W * H); if (c != src && w.k.depth[c] == 0) { w.k.depth[c] = (byte)r.Next(1, 5); digs.Add(c); } }
				w.BodyAt(src, 1f, true);
				for (int p = 0; p < W * H * 8 + 8; p++) { w.Pulse(digs); Pulses++; }
				// every excavated cell 4-connected to the source through excavated cells must be full
				var q = new Queue<int>(); var seen = new HashSet<int> { src }; q.Enqueue(src);
				while (q.Count > 0)
				{
					int c = q.Dequeue();
					for (int d = 0; d < 4; d++) { int m = w.k.Cardinal(c, d); if (m >= 0 && w.k.depth[m] > 0 && seen.Add(m)) q.Enqueue(m); }
				}
				foreach (int c in seen)
					if (c != src && w.k.fill[c] < w.k.depth[c]) { fails.Add($"seed {baseSeed + k}: cell {c} connected to a limitless source ends {w.k.fill[c]}/{w.k.depth[c]}\n{w.Grid()}"); break; }
			}
			return fails;
		}

		// ── regression cases for the confirmed findings (flowworks_playtest_automation_2026-10-06.md) ──

		/// <summary>Finding #1: touching water and tar terrain form ONE body carrying the seed's fluid, so a channel
		/// dug beside the tar fills with water. Returns the observed outcome; REPRODUCED means the defect is live.</summary>
		public static string Finding1TouchingBodies()
		{
			// row z=0: W W T T ; channel at (3,1) above the tar
			var w = new ArrayWorld(4, 3);
			for (int x = 0; x < 4; x++) { w.natural[x] = true; w.terrainFluid[x] = x < 2 ? ArrayWorld.Water : ArrayWorld.Tar; }
			var body = w.BodyAt(0, 1f, false); // the game forms lazily from whichever cell is asked first
			int chan = 1 * 4 + 3;
			w.k.depth[chan] = 1;
			for (int p = 0; p < 12; p++) w.Pulse(new[] { chan });
			bool merged = body.cells.Count == 4;
			bool wrong = w.k.fill[chan] > 0 && w.cellFluid[chan] == ArrayWorld.Water;
			return merged && wrong
				? $"REPRODUCED: water+tar formed one {body.cells.Count}-cell {body.fluid} body; the channel over the TAR filled with {w.cellFluid[chan]}"
				: $"not reproduced (merged={merged}, channel {w.k.fill[chan]}/{w.k.depth[chan]} {w.cellFluid[chan]})";
		}

		/// <summary>Finding #2: a LIMITED body that cannot pay every inlet pays the first-SEEDED component first.
		/// In session the seed order is dig order; after a load RebuildExcavatedSet walks the depth grid in cell
		/// index order. So dig B (higher index) then A, and the reload gives the scarce level to A instead.</summary>
		public static string Finding2ReloadOrder()
		{
			Func<int[], (int a, int b)> run = order =>
			{
				// a 1-cell pond at (2,0) with stock 1; channels A=(1,0) and B=(3,0)
				var w = new ArrayWorld(5, 1);
				w.natural[2] = true; w.terrainFluid[2] = ArrayWorld.Water;
				var b = w.BodyAt(2, 0f, false); b.stock = 1f;
				w.k.depth[1] = 1; w.k.depth[3] = 1;
				w.Pulse(order);
				return (w.k.fill[1], w.k.fill[3]);
			};
			var session = run(new[] { 3, 1 });   // dug B first
			var reload = run(new[] { 1, 3 });    // RebuildExcavatedSet: index order
			return session != reload
				? $"REPRODUCED: same world, session order paid (A,B)={session}, after reload {reload}"
				: $"not reproduced: both orders give {session}";
		}
	}

	/// <summary>Reads scenes (one per line: w h pulses sinkBand nBodies [limitless stock]* nSources [idx body]*
	/// nDigs [idx depth]*), runs the production kernel, writes one line per scene: every dug cell's F after every
	/// pulse, then each body's final stock.</summary>
	internal static class OracleScenes
	{
		public static int Run(System.IO.TextReader input, System.IO.TextWriter output)
		{
			string line;
			while ((line = input.ReadLine()) != null)
			{
				if (line.Trim().Length == 0) continue;
				var t = new Queue<string>(line.Split(' ', StringSplitOptions.RemoveEmptyEntries));
				int N() => int.Parse(t.Dequeue());
				int w = N(), h = N(), pulses = N(), band = N();
				var world = new ArrayWorld(w, h);
				int nb = N();
				var lim = new bool[nb]; var stock = new float[nb];
				for (int b = 0; b < nb; b++) { lim[b] = N() == 1; stock[b] = N(); }
				int ns = N();
				var cellsOf = Enumerable.Range(0, nb).Select(_ => new List<int>()).ToArray();
				for (int i = 0; i < ns; i++) { int idx = N(); cellsOf[N()].Add(idx); }
				for (int b = 0; b < nb; b++) world.AddBody(lim[b], stock[b], cellsOf[b]);
				int nd = N();
				var digs = new List<int>();
				for (int i = 0; i < nd; i++)
				{
					int idx = N(), d = N();
					world.k.depth[idx] = (byte)Math.Min(4, world.k.depth[idx] + d);
					if (!digs.Contains(idx)) digs.Add(idx);
				}
				if (band > 0)
				{
					world.k.edgeSinksEnabled = true;
					for (int i = 0; i < w * h; i++) { int x = i % w, z = i / w; world.sink[i] = x < band || z < band || x >= w - band || z >= h - band; }
				}
				world.k.viscosityEnabled = true;
				var sb = new System.Text.StringBuilder();
				for (int p = 0; p < pulses; p++)
				{
					world.Pulse(digs);
					foreach (int c in digs) sb.Append(world.k.fill[c]).Append(' ');
					sb.Append("| ");
				}
				foreach (var b in world.bodies) sb.Append(b.limitless ? "L" : b.stock.ToString("F0")).Append(' ');
				output.WriteLine(sb.ToString().TrimEnd());
			}
			return 0;
		}
	}
}
