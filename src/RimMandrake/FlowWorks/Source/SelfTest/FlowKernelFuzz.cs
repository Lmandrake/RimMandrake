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

	internal sealed class ArrayWorld : RM_IFlowWorld, RM_ILevelWorld
	{
		public static readonly Fluid Water = new Fluid { name = "water", tpt = 60 };
		public static readonly Fluid Tar = new Fluid { name = "tar", tpt = 360 };
		public static readonly Fluid Oil = new Fluid { name = "oil", tpt = 180 };

		public sealed class Body
		{
			public int id; public bool limitless; public Fluid fluid; public List<int> cells = new List<int>();
			/// <summary>WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: the exact kernel's truth, whole decilitres (long.MinValue = not yet
			/// read: taken from <see cref="stock"/> on first use). Every write keeps <see cref="stock"/> its float view.</summary>
			public long dl = long.MinValue;
			private float stockLevels;
			public float stock { get => stockLevels; set { stockLevels = value; dl = long.MinValue; } }
			public long Dl() { if (dl == long.MinValue) dl = (long)Math.Round(stockLevels * (double)RM_LevelSolve.U); return dl; }
			public void SetDl(long v) { stockLevels = (float)(v / (double)RM_LevelSolve.U); dl = v; }
		}

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
				new List<int>(), new HashSet<int>(), out bool edge, out bool trunc,
				i => (terrainFluid[i] ?? Water) == (terrainFluid[idx] ?? Water));
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

		/// <summary>POND_DEPTH: bed levels of a natural cell (absent = no bed record, drawdown 0).</summary>
		public readonly Dictionary<int, int> bed = new Dictionary<int, int>();

		/// <summary>POND_DEPTH: the drawdown s of the limited body behind source idx (RM_PondDepthMath over its undug cells'
		/// beds; 0 when limitless or bedless). The adapter's RM_LiquidStock.DrawdownOf does the same over the game's body.</summary>
		public int Drawdown(int idx)
		{
			if (bodyOf[idx] < 0) return 0;
			var b = bodies[bodyOf[idx]];
			if (b.limitless) return 0;
			var beds = new List<int>();
			foreach (int c in b.cells) if (k.depth[c] == 0 && bed.TryGetValue(c, out int v)) beds.Add(v);
			if (beds.Count == 0) return 0;
			RM_PondDepthMath.Drawdown(RM_BedMath.SupportedLevels(b.stock, (b.fluid ?? activeFluid).vpt), RM_PondDepthMath.Histogram(beds), out int s, out _);
			return s;
		}

		public bool IsNaturalLiquid(int idx) => natural[idx];
		/// <summary>DISABLED_LIQUID_FIX_LIMITLESS_SOURCE: a liquid switched off in Mod Settings (the adapter's InputAllowed): its
		/// natural bodies supply nothing and read as RM_FlowKernel.LevelBodyDisabled. Null = every liquid allowed.</summary>
		public Fluid disabledFluid;
		private bool Disabled(int idx) => disabledFluid != null && ((BodyAt(idx)?.fluid ?? activeFluid) == disabledFluid);
		public bool CanSupply(int idx) { if (Disabled(idx)) return false; var b = BodyAt(idx); return b == null || RM_StockMath.CanSupply(b.limitless, b.stock, (b.fluid ?? activeFluid).vpt); }
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
		/// <summary>P7: the fuzz world has no palette cap unless a test sets one (null = unlimited).</summary>
		public Func<object, bool> canClaim;
		public bool CanClaim(object fluid) => canClaim == null || canClaim(fluid);
		public int TicksPerTile(object fluid) => ((fluid as Fluid) ?? activeFluid)?.tpt ?? RM_StockMath.WaterTicksPerTile;
		public bool IsSink(int idx) => sink[idx];
		public void ComponentResolved(List<int> component) { }

		// ── RM_ILevelWorld (the exact kernel): a limited body's dL, its bed histogram over its undug cells ──
		public int LevelBodyOf(int src) { if (Disabled(src)) return RM_FlowKernel.LevelBodyDisabled; var b = BodyAt(src); return b == null || b.limitless ? -1 : b.id; }
		public long BodyStockDl(int body) => bodies[body].Dl();
		public void SetBodyStockDl(int body, long dl) => bodies[body].SetDl(dl);
		public int BedAt(int src) => bed.TryGetValue(src, out int v) ? v : RM_FlowKernel.Superdeep;
		public int[] BodyHistogram(int body)
		{
			var beds = new List<int>();
			foreach (int c in bodies[body].cells) if (k.depth[c] == 0) beds.Add(BedAt(c));
			return RM_PondDepthMath.Histogram(beds);
		}
		public void NoteLimitlessDl(object fluid, long dl)
		{
			Fluid f = (fluid as Fluid) ?? activeFluid;
			externalIn[f] = externalIn.GetValueOrDefault(f) + dl / (float)RM_LevelSolve.U;
		}

		/// <summary>A cell's water in levels (fill + part / U): the exact kernel's view, the fill alone otherwise.</summary>
		public float WaterLevels(int i) => k.part != null ? k.WaterOf(i) / (float)RM_LevelSolve.U : k.fill[i];

		/// <summary>RM_MapComponent_Excavation.SyncFluidIdentity's grid half.</summary>
		public void Sync()
		{
			for (int i = 0; i < w * h; i++)
			{
				if (k.depth[i] == 0) continue;
				if (k.fill[i] == 0 && (k.part == null || k.part[i] == 0)) cellFluid[i] = null;
				else if (cellFluid[i] == null) cellFluid[i] = activeFluid;
			}
		}

		public long pulse;
		public void Pulse(IEnumerable<int> seeds) { pulse++; k.Pulse(seeds, pulse); Sync(); }

		public Dictionary<Fluid, float> Totals()
		{
			var t = new Dictionary<Fluid, float>();
			for (int i = 0; i < w * h; i++) if (k.depth[i] > 0 && WaterLevels(i) > 0) t[cellFluid[i]] = t.GetValueOrDefault(cellFluid[i]) + WaterLevels(i);
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
		/// <summary>WATER_LEVELSET_SOLVE: the WATER_SURFACE_REWIRE cases run once with the unit-at-a-time pass and once with the solve.</summary>
		public static bool LevelSet;

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
			var prevFill = new float[n];
			var prevFluid = new Fluid[n];
			var history = new List<string>();
			for (int p = 0; p < s.pulses; p++)
			{
				for (int i = 0; i < n; i++) prevFill[i] = w.WaterLevels(i);
				Array.Copy(w.cellFluid, prevFluid, n);
				var t0 = w.Totals();
				w.externalIn.Clear();
				w.Pulse(seeds);
				Pulses++;
				if (w.k.worstImbalance > 0) return $"pulse {p}: kernel ledger {string.Join("; ", w.k.imbalanceReports)}";
				for (int i = 0; i < n; i++)
				{
					if (w.k.fill[i] > w.k.depth[i] || w.k.depth[i] > 4) return $"pulse {p}: 0<=F<=D<=4 broken at {i}";
					if (w.k.part != null && (w.k.part[i] >= RM_LevelSolve.U || (w.k.part[i] > 0 && w.k.fill[i] >= w.k.depth[i])))
						return $"pulse {p}: exact water above the brim at {i} (fill {w.k.fill[i]}, part {w.k.part[i]}, D {w.k.depth[i]})";
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
							sunk[prevFluid[i]] = sunk.GetValueOrDefault(prevFluid[i]) + Math.Min(prevFill[i], (float)w.k.flowPerPulse);
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
				var states = new HashSet<string> { Snapshot(w) };
				for (int p = 0; p < 24; p++) { w.Pulse(seeds); Pulses++; states.Add(Snapshot(w)); }
				if (states.Count > 1 && SettledExpected(w)) return $"no fixed point after {s.pulses} pulses: {states.Count} distinct states in 24 more\n{w.Grid()}";
			}
			return null;
		}

		private static string Snapshot(ArrayWorld w) => Convert.ToBase64String(w.k.fill)
			+ (w.k.part != null ? Convert.ToBase64String(w.k.part.SelectMany(BitConverter.GetBytes).ToArray()) : "");

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

		/// <param name="shipped">LEVELSET_DIAGNOSE_SHALLOW_RIM_STAYS_DRY: run under the SHIPPED kernel flags (level by surface, the
		/// level-set solve, viscosity, water creep; RimMandrakeFlowWorksMod's defaults). At the C# defaults (all off) this
		/// family passed while the shipped solve left a shallow rim dry beside a limitless source in 194/2000 scenes.</param>
		public static List<string> FillsFromLimitless(int n, int baseSeed, bool shipped = false)
		{
			var fails = new List<string>();
			for (int k = 0; k < n && fails.Count < 5; k++)
			{
				var r = new Random(baseSeed + k);
				Cases++;
				int W = r.Next(3, 10), H = r.Next(3, 10);
				var w = new ArrayWorld(W, H);
				if (shipped) { w.k.viscosityEnabled = true; }
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

		/// <summary>FLOWWORKS_STRIDE_FIX_WALKS_INTO_WALL: over n pulses the seam start visits all n cells, for every n
		/// including multiples of 7919 (the old stride pinned n = 7919 to cell 0).</summary>
		public static string SeamSlotCoversNetwork()
		{
			foreach (int n in new[] { 1, 2, 3, 7, 200, 6001, 7918, 7919, 7920, 15838, 23757, 39595 })
			{
				var seen = new HashSet<int>();
				for (long p = 0; p < n; p++) seen.Add(RM_FlowKernel.SeamSlot(p + 12345L * n, n));
				if (seen.Count != n) return $"BROKEN: n={n}: {n} pulses visit only {seen.Count} distinct seam starts";
			}
			return "OK: seam start visits every cell over n pulses (n incl. 7919, 15838, 23757, 39595)";
		}

		/// <summary>Ruling 1 (owner, 2026-10-06): touching water and tar stay separate bodies, and a channel touching both
		/// never mixes them: once a channel cell is wet its fluid never changes, and the cell over the water really fills
		/// with water (so the scene reaches the kernel). Returns "OK ..." or "BROKEN ...".</summary>
		public static string TouchingFluidsStaySeparate()
		{
			// row z=0: W W T T ; channel (1,1)-(2,1)-(3,1): (1,1) over water, (2,1) touching water's channel and tar, (3,1) over tar
			var w = new ArrayWorld(4, 3);
			for (int x = 0; x < 4; x++) { w.natural[x] = true; w.terrainFluid[x] = x < 2 ? ArrayWorld.Water : ArrayWorld.Tar; }
			var water = w.BodyAt(0, 1f, false);
			var tar = w.BodyAt(3, 1f, false);
			int chan = 1 * 4 + 3;
			int chan2 = 1 * 4 + 2;
			int chanW = 1 * 4 + 1;
			int[] chans = { chanW, chan2, chan };
			foreach (int c in chans) w.k.depth[c] = 1;
			var first = new Dictionary<int, object>();
			bool ok = true;
			for (int p = 0; p < 12; p++)
			{
				w.Pulse(chans);
				foreach (int c in chans)
				{
					if (w.k.WaterOf(c) == 0) continue;
					if (!first.ContainsKey(c)) first[c] = w.cellFluid[c];
					else if (!ReferenceEquals(first[c], w.cellFluid[c])) ok = false;   // a wet cell changed fluid: mixed
				}
			}
			bool separate = water != tar && water.cells.Count == 2 && tar.cells.Count == 2
				&& water.fluid == ArrayWorld.Water && tar.fluid == ArrayWorld.Tar;
			ok = ok && w.k.WaterOf(chanW) > 0 && w.cellFluid[chanW] == ArrayWorld.Water;   // can-fail: the scene reached the kernel
			// reverse formation order must give the same bodies
			var w2 = new ArrayWorld(4, 3);
			for (int x = 0; x < 4; x++) { w2.natural[x] = true; w2.terrainFluid[x] = x < 2 ? ArrayWorld.Water : ArrayWorld.Tar; }
			var tar2 = w2.BodyAt(3, 1f, false); var water2 = w2.BodyAt(0, 1f, false);
			bool sameReverse = tar2 != water2 && tar2.cells.Count == 2 && water2.cells.Count == 2;
			return separate && ok && sameReverse
				? $"OK: water {water.cells.Count} cells, tar {tar.cells.Count} cells; channel over the tar holds {w.k.WaterOf(chan)} dL {w.cellFluid[chan]?.name}"
				: $"BROKEN: separate={separate} channelOk={ok} reverseOk={sameReverse} (channel {w.k.WaterOf(chan)} dL / D{w.k.depth[chan]} {w.cellFluid[chan]})";
		}

		private static string CanalRun(bool creepWater, int pulses, out string at, out bool ok, out float worst)
		{
			var w = new ArrayWorld(20, 6);
			var bodyCells = new List<int>();
			for (int z = 0; z < 6; z++) for (int x = 0; x < 10; x++) bodyCells.Add(z * 20 + x);
			w.AddBody(false, 300f, bodyCells);
			var digs = Enumerable.Range(10, 10).Select(x => 2 * 20 + x).ToList();
			foreach (int c in digs) w.k.depth[c] = 1;
			worst = 0f;
			for (int p = 0; p < pulses; p++) { w.Pulse(digs); worst = Math.Max(worst, w.k.worstImbalance); }
			at = string.Join("", digs.Select(c => w.k.fill[c]));
			ok = true;
			return at;
		}

		// ── WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND (owner 2026-10-16, by card "Level by water surface") ──────────────

		/// <summary>A 1-row world of dug cells x=0..n-1 (depths given), filled as given, water, shipped flags (creep, viscosity,
		/// levelBySurface as asked). Sink band = x &lt; sinkBand.</summary>
		private static ArrayWorld SurfaceRow(int[] depths, int[] fills, bool surface, int sinkBand = 0)
		{
			var w = new ArrayWorld(depths.Length, 1);
			for (int x = 0; x < depths.Length; x++)
			{
				w.k.depth[x] = (byte)depths[x];
				w.k.fill[x] = (byte)fills[x];
				if (fills[x] > 0) w.cellFluid[x] = ArrayWorld.Water;
				w.sink[x] = x < sinkBand;
			}
			w.k.edgeSinksEnabled = sinkBand > 0;
			w.k.viscosityEnabled = true;
			return w;
		}

		/// <summary>Runs <paramref name="pulses"/> pulses over every dug cell. Returns the final F vector; <paramref name="settledAt"/>
		/// is the first pulse after which the F vector never changed again (-1 = still changing on the last pulse);
		/// <paramref name="worst"/> the worst ledger imbalance; <paramref name="drained"/> the units sinks took.</summary>
		private static string SurfaceRun(ArrayWorld w, int pulses, out int settledAt, out float worst, out float drained)
		{
			var digs = Enumerable.Range(0, w.w * w.h).Where(i => w.k.depth[i] > 0).ToList();
			string prev = string.Join(",", digs.Select(c => w.k.fill[c]));
			settledAt = 0; worst = 0f; drained = 0f;
			for (int p = 1; p <= pulses; p++)
			{
				w.Pulse(digs);
				worst = Math.Max(worst, w.k.worstImbalance);
				drained += w.k.sinkDrained;
				string now = string.Join(",", digs.Select(c => w.k.fill[c]));
				if (now != prev) settledAt = p;
				prev = now;
			}
			if (settledAt == pulses) settledAt = -1;
			return prev;
		}

		private static int MaxNeighbourSurfaceStep(ArrayWorld w)
		{
			int worst = 0;
			for (int i = 0; i < w.w * w.h; i++)
			{
				if (w.k.depth[i] == 0) continue;
				for (int d = 0; d < 4; d++)
				{
					int n = w.k.Cardinal(i, d);
					if (n < 0 || w.k.depth[n] == 0) continue;
					worst = Math.Max(worst, Math.Abs((w.k.fill[i] - w.k.depth[i]) - (w.k.fill[n] - w.k.depth[n])));
				}
			}
			return worst;
		}

		/// <summary>A limitless pond feeding a D=2 run still fills it full, mouth first (creep on), ledger balanced.</summary>
		public static string SurfaceSourceStillFillsChannel()
		{
			var w = new ArrayWorld(11, 1);
			w.AddBody(true, 0f, new[] { 0 });
			var digs = Enumerable.Range(1, 10).ToList();
			foreach (int c in digs) w.k.depth[c] = 2;
			w.k.viscosityEnabled = true; 
			w.Pulse(digs);
			float worst = w.k.worstImbalance;   // pulse 1's ledger counts too
			string first = string.Join("", digs.Select(c => w.k.fill[c]));
			for (int p = 1; p < 80; p++) { w.Pulse(digs); worst = Math.Max(worst, w.k.worstImbalance); }
			string end = string.Join("", digs.Select(c => w.k.fill[c]));
			bool ok = first == "1000000000" && end == "2222222222" && worst <= 0.001f;
			return (ok ? "OK: " : "BROKEN: ") + $"after 1 pulse {first}, after 80 {end}, worst imbalance {worst:F3}";
		}

		/// <summary>1000 seeded random 8x8 scenes (random digs D1..4, random fills, optional sink band, optional LIMITED pond):
		/// with levelBySurface on, each conserves (fill + pond stock + sink drain constant, ledger balanced every pulse)
		/// and is at rest by pulse 200 (identical F for the last 50 pulses: no shuttle of any period); in a sinkless scene no
		/// wet cell ends 2+ units of surface above a dug neighbour.</summary>
		public static string SurfaceRandomScenesSettleAndConserve()
		{
			var rng = new Random(20261016);
			int notAtRest = 0, unbalanced = 0, steep = 0, total = 1000;
			string firstBad = null;
			for (int t = 0; t < total; t++)
			{
				var w = new ArrayWorld(8, 8);
				int band = rng.Next(3) == 0 ? 1 : 0;
				ArrayWorld.Body pond = null;
				if (rng.Next(2) == 0)
				{
					int pc = rng.Next(64);
					pond = w.AddBody(false, rng.Next(0, 15), new[] { pc });
				}
				for (int i = 0; i < 40; i++)
				{
					int c = rng.Next(64);
					if (w.natural[c]) continue;
					w.k.depth[c] = (byte)rng.Next(1, 5);
					w.k.fill[c] = (byte)rng.Next(0, w.k.depth[c] + 1);
					w.cellFluid[c] = w.k.fill[c] > 0 ? ArrayWorld.Water : null;
				}
				for (int i = 0; i < 64; i++) { int x = i % 8, z = i / 8; w.sink[i] = band > 0 && (x < band || z < band || x >= 8 - band || z >= 8 - band); }
				w.k.edgeSinksEnabled = band > 0; w.k.viscosityEnabled = true; 
				// WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: totals, rest and the level check read the WATER (fill + part) so the family
				// holds at the shipped exact-level flags as well as at the whole-notch ones (part is null there: water = fill).
				float startTotal = Enumerable.Range(0, 64).Sum(i => w.WaterLevels(i)) + (pond?.stock ?? 0f);
				var digs = Enumerable.Range(0, 64).Where(i => w.k.depth[i] > 0).ToList();
				string prev = null; int lastChange = 0; float worst = 0f, drained = 0f;
				for (int p = 1; p <= 200; p++)
				{
					w.Pulse(digs);
					worst = Math.Max(worst, w.k.worstImbalance);
					drained += w.k.sinkDrained;
					string now = string.Join(",", digs.Select(c => w.k.part != null ? w.k.WaterOf(c) : w.k.fill[c]));
					if (now != prev) lastChange = p;
					prev = now;
				}
				float endTotal = Enumerable.Range(0, 64).Sum(i => w.WaterLevels(i)) + (pond?.stock ?? 0f) + drained;
				bool rest = lastChange <= 150, bal = worst <= 0.001f && Math.Abs(endTotal - startTotal) < 0.001f;
				// At rest, no wet cell stands 2+ above a dug neighbour in its own network (sealed/sink-free scenes only;
				// a sink band empties toward the edge, and a different-fluid wall cannot happen here: one fluid).
				bool level = true;
				if (band == 0)
				{
					for (int i = 0; i < 64 && level; i++)
					{
						if (w.k.depth[i] == 0 || w.WaterLevels(i) == 0) continue;
						for (int d = 0; d < 4; d++)
						{
							int n = w.k.Cardinal(i, d);
							if (n < 0 || w.k.depth[n] == 0) continue;
							// exact: one surface to the decilitre (a step of 3 dL or more is not level); whole notches: within one notch
							bool steepHere = w.k.part != null
								? (w.k.WaterOf(i) - w.k.depth[i] * (long)RM_LevelSolve.U) - (w.k.WaterOf(n) - w.k.depth[n] * (long)RM_LevelSolve.U) >= 3
								: (w.k.fill[i] - w.k.depth[i]) - (w.k.fill[n] - w.k.depth[n]) >= 2;
							if (steepHere) { level = false; break; }
						}
					}
				}
				if (!rest) notAtRest++;
				if (!bal) unbalanced++;
				if (!level) steep++;
				if ((!rest || !bal || !level) && firstBad == null) firstBad = $"scene {t}: rest={rest} (last change {lastChange}) bal={bal} level={level}\n{w.Grid()}";
			}
			string line = $"{total} scenes: {notAtRest} not at rest by pulse 150, {unbalanced} unbalanced, {steep} with a wet step of 2+";
			return notAtRest == 0 && unbalanced == 0 && steep == 0 ? "OK: " + line : "BROKEN: " + line + "\n" + firstBad;
		}

		/// <summary>A channel touching both pools takes the fluid of whichever fills it first and never mixes after.</summary>
		public static string ChannelTouchingBothNeverMixes()
		{
			// W at (0,0), T at (2,0), channel (1,0)-(1,1)... channel cells at (1,0) touch both; (1,1) is its neighbour
			var w = new ArrayWorld(3, 3);
			w.natural[0] = true; w.terrainFluid[0] = ArrayWorld.Water;
			w.natural[2] = true; w.terrainFluid[2] = ArrayWorld.Tar;
			w.BodyAt(0, 1f, false); w.BodyAt(2, 1f, false);
			w.k.depth[1] = 2; w.k.depth[4] = 2;
			for (int p = 0; p < 40; p++) w.Pulse(new[] { 1, 4 });
			var f1 = w.cellFluid[1]; var f4 = w.cellFluid[4];
			bool mixed = f1 != null && f4 != null && f1 != f4 && w.k.fill[1] > 0 && w.k.fill[4] > 0;
			return !mixed && f1 != null
				? $"OK: channel holds only {f1.name} ({w.k.fill[1]}/{w.k.depth[1]}, {w.k.fill[4]}/{w.k.depth[4]})"
				: $"BROKEN: mixed={mixed} fluids {f1?.name}/{f4?.name}";
		}

		/// <summary>FLOWWORKS_SLUICE_TWO_DOORS_1 (owner 2026-10-06): a limitless pond at x=0 feeds a D=2 channel x=1..7
		/// with a door at x=4. A SHUT sluice (sealed) holds the level at x=1..3 and leaves x=4..7 dry; a grate (never
		/// sealed) and a sluice opened afterwards both let it reach x=7. The ledger balances throughout.</summary>
		public static string SluiceSealsGrateDoesNot()
		{
			var w = new ArrayWorld(8, 1);
			w.AddBody(true, 0f, new[] { 0 });
			var digs = Enumerable.Range(1, 7).ToList();
			foreach (int c in digs) w.k.depth[c] = 2;
			bool shut = true;
			w.k.sealedCell = idx => shut && idx == 4;
			float worst = 0f;
			for (int p = 0; p < 40; p++) { w.Pulse(digs); worst = Math.Max(worst, w.k.worstImbalance); }
			string held = string.Join(",", digs.Select(c => w.k.fill[c]));
			bool holds = digs.All(c => w.k.fill[c] == (c < 4 ? 2 : 0));
			shut = false;   // the sluice is opened (a pawn passing, or held open)
			for (int p = 0; p < 40; p++) { w.Pulse(digs); worst = Math.Max(worst, w.k.worstImbalance); }
			bool opened = digs.All(c => w.k.fill[c] == 2);
			var g = new ArrayWorld(8, 1);
			g.AddBody(true, 0f, new[] { 0 });
			foreach (int c in digs) g.k.depth[c] = 2;
			g.k.sealedCell = idx => false;   // a grate: never sealed
			for (int p = 0; p < 40; p++) { g.Pulse(digs); worst = Math.Max(worst, g.k.worstImbalance); }
			bool grate = digs.All(c => g.k.fill[c] == 2);
			return holds && opened && grate && worst < 0.001f
				? $"OK: shut sluice holds F={held}; opened and grate both fill x=1..7"
				: $"BROKEN: shut F={held} holds={holds} opened={opened} grate={grate} worstImbalance={worst}";
		}

		/// <summary>FLOWWORKS_SLUICE_FIX_BELOW_SOURCE_LUCK (GPT 1core #6): a D=1 canal from a limitless source, shut sluice at
		/// x=4, edge sink beyond it. The region above the sluice reaches no sink, so it must solve as FED (mouth deferred), not as
		/// draining because the component has a sink somewhere: drained by index the mouth kept its unit and x=2,3 stayed dry
		/// in one direction only. Both directions must fill the upstream cells. Returns "OK ..." or "BROKEN ...".</summary>
		public static string SealedSinkBelowSourceFillsUpstream()
		{
			string Run(bool west)
			{
				const int len = 8;
				int X(int x) => west ? len - 1 - x : x;
				var w = new ArrayWorld(len, 1);
				w.AddBody(true, 0f, new[] { X(0) });
				var digs = Enumerable.Range(1, len - 1).Select(X).ToList();
				foreach (int c in digs) w.k.depth[c] = 1;
				w.sink[X(len - 1)] = true;
				w.k.edgeSinksEnabled = true;
				w.k.viscosityEnabled = true;
				w.k.sealedCell = idx => idx == X(4);
				for (int p = 0; p < 60; p++) { w.Pulse(digs); Pulses++; }
				return string.Join(",", Enumerable.Range(1, 3).Select(x => w.k.fill[X(x)]));
			}
			string east = Run(false), west = Run(true);
			return east == "1,1,1" && west == "1,1,1"
				? "OK: upstream of a shut sluice fills from the source both ways (x=1..3: 1,1,1)"
				: $"BROKEN: upstream x=1..3 east {east}, west {west} (want 1,1,1 both)";
		}

		/// <summary>GPT FlowWorks review #10: a shut sluice in the sink band neither drains nor fills.</summary>
		public static string SealedSinkHolds()
		{
			Func<bool, int> run = sealedGate =>
			{
				var w = new ArrayWorld(3, 1);
				w.sink[0] = true;
				w.k.edgeSinksEnabled = true;
				w.k.depth[0] = 2; w.k.fill[0] = 2; w.cellFluid[0] = ArrayWorld.Water;
				w.k.sealedCell = idx => sealedGate && idx == 0;
				for (int p = 0; p < 10; p++) w.Pulse(new[] { 0 });
				return w.k.fill[0];
			};
			int shut = run(true), open = run(false);
			return shut == 2 && open == 0
				? "OK: sealed sink keeps F=2; unsealed sink drains to 0"
				: $"BROKEN: sealed sink F={shut} (want 2), unsealed F={open} (want 0)";
		}

		/// <summary>GPT FlowWorks review #28: a body of exactly maxCells is complete, not truncated.</summary>
		public static string CollectBodyExactCapNotTruncated()
		{
			var src = new[] { true, true, true };
			var found = new List<int>();
			RM_FlowKernel.CollectBody(3, 1, 0, i => src[i], i => -1, 3, found, new List<int>(), new HashSet<int>(),
				out bool _, out bool exact);
			RM_FlowKernel.CollectBody(3, 1, 0, i => src[i], i => -1, 2, found, new List<int>(), new HashSet<int>(),
				out bool _, out bool over);
			return !exact && over && found.Count == 2
				? "OK: 3 cells at cap 3 complete; at cap 2 truncated with 2 kept"
				: $"BROKEN: exact={exact} (want false) over={over} (want true) kept={found.Count}";
		}

		/// <summary>Ruling 2 (owner, 2026-10-06): a LIMITED body that cannot pay every inlet pays by cell index, so
		/// dig order (session) and index order (reload) give the same outcome, and the lower index is paid.</summary>
		public static string ScarceSupplyPaidByPosition()
		{
			Func<int[], (long a, long b)> run = order =>
			{
				// a 1-cell pond at (2,0) with stock 1; channels A=(1,0) and B=(3,0)
				var w = new ArrayWorld(5, 1);
				w.natural[2] = true; w.terrainFluid[2] = ArrayWorld.Water;
				// exact water: the pond's bed is one notch, so its one level of stock stands at the brim, above both D1 channels'
				// floors (a superdeep bed would hold that level 1.5 m down, below them, and pay nothing)
				w.bed[2] = 1;
				var b = w.BodyAt(2, 0f, false); b.stock = 1f;
				w.k.depth[1] = 1; w.k.depth[3] = 1;
				w.Pulse(order);
				return (w.k.WaterOf(1), w.k.WaterOf(3));
			};
			var session = run(new[] { 3, 1 });   // dug B first
			var reload = run(new[] { 1, 3 });    // RebuildExcavatedSet: index order
			// exact water (RIMMANDRAKE_DELETE_FILL_N_ONE_WATER_NUMBER_SEVEN_FIXES): dL, the lower index paid first (A's share never
			// below B's), and the dig order changes nothing
			return session == reload && session.a > 0 && session.a >= session.b
				? $"OK: both orders pay (A,B)={session} dL"
				: $"BROKEN: session (A,B)={session} dL, reload {reload}, expected equal with A paid first";
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
				// POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD: an optional tail of source beds (count, then idx bed pairs) for the
				// head-rule mode; the drawdown is RM_PondDepthMath's, as the adapter computes it.
				if (t.Count > 0)
				{
					int nbed = N();
					for (int i = 0; i < nbed; i++) { int idx = N(); world.bed[idx] = N(); }
				}
				// PUMP_CANAL_FEED / HOSE_LEFTOVER / CANAL_FILLIN fixes ("exactops"): an optional tail of events (count, then
				// pulse kind idx dl): after that pulse's line, kind 0 pours dl at idx (LevelOps.Pour), kind 1 fills idx in one
				// notch (LevelOps.FillIn); each prints its result (dL placed / dL destroyed) as "e<n>".
				var events = new List<(int p, int kind, int idx, int dl)>();
				if (t.Count > 0)
				{
					int ne = N();
					for (int i = 0; i < ne; i++) events.Add((N(), N(), N(), N()));
				}
				if (band > 0)
				{
					world.k.edgeSinksEnabled = true;
					for (int i = 0; i < w * h; i++) { int x = i % w, z = i / w; world.sink[i] = x < band || z < band || x >= w - band || z >= h - band; }
				}
				world.k.viscosityEnabled = true;
				// WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: prints every dug cell's WATER in dL and each limited body's dL
				// (northstar/level_water.py, PulseOracle(level_exact=True)); the kernel has no other engine.
				var sb = new System.Text.StringBuilder();
				for (int p = 0; p < pulses; p++)
				{
					// a square filled back in to the surface leaves the excavation's seeds (RM_MapComponent_Excavation.FillIn removes
					// it from excavatedCells), so it leaves the pulse's seeds here too
					world.Pulse(events.Count == 0 ? digs : digs.Where(c => world.k.depth[c] > 0).ToList());
					foreach (int c in digs) sb.Append(world.k.WaterOf(c)).Append(' ');
					foreach (var e in events)
					{
						if (e.p != p) continue;
						long r = e.kind == 0 ? LevelOps.Pour(world, e.idx, e.dl) : LevelOps.FillIn(world, e.idx);
						sb.Append('e').Append(r).Append(' ');
					}
					sb.Append("| ");
					if (world.k.worstImbalance > 0) sb.Append("IMBALANCE ");
				}
				foreach (var b in world.bodies) sb.Append(b.limitless ? "L" : b.Dl().ToString()).Append(' ');
				output.WriteLine(sb.ToString().TrimEnd());
			}
			return 0;
		}
	}
}
