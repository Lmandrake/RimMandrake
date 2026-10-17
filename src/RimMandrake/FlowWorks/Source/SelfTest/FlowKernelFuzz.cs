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
		/// <summary>P7: the fuzz world has no palette cap unless a test sets one (null = unlimited).</summary>
		public Func<object, bool> canClaim;
		public bool CanClaim(object fluid) => canClaim == null || canClaim(fluid);
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
				var states = new HashSet<string> { Snapshot(w) };
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
				if (shipped) { w.k.levelBySurfaceEnabled = true; w.k.levelSetEnabled = true; w.k.viscosityEnabled = true; w.k.creepWaterEnabled = true; }
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

		/// <summary>FLOW_ORDER_EXTERNAL_INPUT_1: a pump-fed flat channel with no natural source. Without an input
		/// seed every flow key is equal and the liquid stays beside the pump; with the pump cell as an external input
		/// it spreads to the far end, and once the pump stops the channel settles (no period-2 shuttle).
		/// Returns "OK ..." or "BROKEN ...".</summary>
		public static string PumpFedChannelSpreads()
		{
			int Run(bool seeded, out bool settled)
			{
				var w = new ArrayWorld(10, 3);
				var digs = new List<int>();
				for (int x = 0; x < 10; x++) { int c = 1 * 10 + x; w.k.depth[c] = 2; digs.Add(c); }
				int pump = digs[0];
				w.k.externalInput = seeded ? (Func<int, bool>)(i => i == pump) : null;
				for (int p = 0; p < 80; p++) { w.k.fill[pump] = 2; if (w.cellFluid[pump] == null) w.cellFluid[pump] = ArrayWorld.Water; w.Pulse(digs); Pulses++; }
				for (int p = 0; p < 60; p++) { w.Pulse(digs); Pulses++; }
				byte[] a = (byte[])w.k.fill.Clone();
				w.Pulse(digs); byte[] b = (byte[])w.k.fill.Clone();
				w.Pulse(digs); byte[] c2 = (byte[])w.k.fill.Clone();
				settled = a.SequenceEqual(b) && b.SequenceEqual(c2);
				return w.k.fill[digs[9]];
			}
			int farSeeded = Run(true, out bool settledSeeded);
			int farPlain = Run(false, out _);
			return farSeeded > 0 && settledSeeded && farPlain == 0
				? $"OK: far end holds {farSeeded} with the pump as input (without: {farPlain}); settled after the pump stops"
				: $"BROKEN: farSeeded={farSeeded} settled={settledSeeded} farPlain={farPlain}";
		}

		/// <summary>PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD (P4, GPT G3.1): the brimming-outlet reload test, on the PRODUCTION
		/// driver-input rule (RM_DriverInputs) and the production kernel. A pump feeds a 6-cell flat channel until it brims and
		/// settles; the game is "reloaded" (the unsaved input set starts empty); the player digs the channel on by 6 dry cells
		/// and the pump keeps running on its 250-tick cycle (pour one level when its cell has room, else it is backed up).
		/// With <paramref name="backedUpMarks"/> false (the shipped rule before P4: only a write that raises the fill marks)
		/// nothing ever re-marks the brimming outlet and the extension stays dry; true is the fix. Returns the far end's fill.
		/// The cycle below restates Building_LiquidPump.TryPour's backed-up condition (Verse, not compiled here);
		/// selftest_flowworks_call_sites.py pins that exact condition and its NoteDriverBackedUp call in the production file.</summary>
		public static int PumpFedReloadFarFill(bool backedUpMarks, bool reload)
		{
			var w = new ArrayWorld(14, 3);
			var digs = new List<int>();
			for (int x = 0; x < 6; x++) { int c = 1 * 14 + x; w.k.depth[c] = 2; digs.Add(c); }
			int pump = digs[0];
			var inputs = new RM_DriverInputs();
			int now = 0;
			void Cycle(bool running)
			{
				now += RM_PumpMath.CycleTicks;
				if (running)
				{
					if (w.k.fill[pump] < w.k.depth[pump])
					{
						int old = w.k.fill[pump];
						w.k.fill[pump] = (byte)(old + 1);
						if (w.cellFluid[pump] == null) w.cellFluid[pump] = ArrayWorld.Water;
						inputs.NoteWrite(pump, old, old + 1, now);
					}
					else if (backedUpMarks)
					{
						inputs.NoteBackedUp(pump, now);
					}
				}
				inputs.Prune(now, i => w.k.depth[i] == 0);
				w.k.externalInput = inputs.Count > 0 ? (Func<int, bool>)inputs.Contains : null;
				w.Pulse(digs); Pulses++;
			}
			for (int p = 0; p < 120; p++) Cycle(true);
			if (reload) inputs = new RM_DriverInputs();
			for (int x = 6; x < 12; x++) { int c = 1 * 14 + x; w.k.depth[c] = 2; digs.Add(c); }
			for (int p = 0; p < 200; p++) Cycle(true);
			return w.k.fill[digs[digs.Count - 1]];
		}

		/// <summary>P4 verdict plus its can-it-fail probe: the fixed rule fills the far end after a reload; the old rule
		/// (backed-up pressure ignored) must leave it dry, or this scene cannot see the defect. Returns "OK ..." or "BROKEN ...".</summary>
		public static string PumpFedChannelResumesAfterReload()
		{
			int fixedFar = PumpFedReloadFarFill(true, true);
			int oldFar = PumpFedReloadFarFill(false, true);
			return fixedFar > 0 && oldFar == 0
				? $"OK: after a reload the far end of the dug-on channel holds {fixedFar} (old rule, probe: {oldFar}, the stall)"
				: $"BROKEN: fixed far end {fixedFar} (want > 0), old-rule probe {oldFar} (want 0 - else the scene cannot fail)";
		}

		/// <summary>FLOWWORKS_PUMP_FIX_D1_CANAL_STALLS (GPT 1core #5): a dry D=1 canal fed ONLY by a driver at its inlet, at the
		/// shipped flags (surface levelling + level-set). The neighbour pass never moves a drop of 1 under level-set, so the
		/// solve must pass the inlet's unit on; if the inlet keeps it for being wet the run sits at 1,0,0,... for ever.
		/// <paramref name="backedUpMarks"/> true = the pump (re-marks a brimming outlet), false = the drill (returns early
		/// when its outlet is full, marks nothing). Returns the far end's fill after 200 driver cycles.</summary>
		public static int DriverFedD1FarFill(bool backedUpMarks)
		{
			const int len = 8;
			var w = new ArrayWorld(len, 1);
			var digs = new List<int>();
			for (int x = 0; x < len; x++) { w.k.depth[x] = 1; digs.Add(x); }
			w.k.viscosityEnabled = true;
			w.k.creepWaterEnabled = true;
			w.k.levelBySurfaceEnabled = true;
			w.k.levelSetEnabled = true;
			int inlet = 0;
			var inputs = new RM_DriverInputs();
			int now = 0;
			for (int p = 0; p < 200; p++)
			{
				now += RM_PumpMath.CycleTicks;
				if (w.k.fill[inlet] < w.k.depth[inlet])
				{
					int old = w.k.fill[inlet];
					w.k.fill[inlet] = (byte)(old + 1);
					if (w.cellFluid[inlet] == null) w.cellFluid[inlet] = ArrayWorld.Water;
					inputs.NoteWrite(inlet, old, old + 1, now);
				}
				else if (backedUpMarks)
				{
					inputs.NoteBackedUp(inlet, now);
				}
				inputs.Prune(now, i => w.k.depth[i] == 0);
				w.k.externalInput = inputs.Count > 0 ? (Func<int, bool>)inputs.Contains : null;
				w.Pulse(digs); Pulses++;
			}
			return w.k.fill[len - 1];
		}

		public static string DriverFedD1CanalFills()
		{
			int pump = DriverFedD1FarFill(true), drill = DriverFedD1FarFill(false);
			return pump == 1 && drill == 1
				? "OK: a D=1 canal fed only at its inlet fills to the far end (pump and drill)"
				: $"BROKEN: far end pump-fed {pump}, drill-fed {drill} (want 1, 1; 0 = the inlet keeps its unit, 1,0,0,0 stall)";
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
					if (w.k.fill[c] == 0) continue;
					if (!first.ContainsKey(c)) first[c] = w.cellFluid[c];
					else if (!ReferenceEquals(first[c], w.cellFluid[c])) ok = false;   // a wet cell changed fluid: mixed
				}
			}
			bool separate = water != tar && water.cells.Count == 2 && tar.cells.Count == 2
				&& water.fluid == ArrayWorld.Water && tar.fluid == ArrayWorld.Tar;
			ok = ok && w.k.fill[chanW] > 0 && w.cellFluid[chanW] == ArrayWorld.Water;   // can-fail: the scene reached the kernel
			// reverse formation order must give the same bodies
			var w2 = new ArrayWorld(4, 3);
			for (int x = 0; x < 4; x++) { w2.natural[x] = true; w2.terrainFluid[x] = x < 2 ? ArrayWorld.Water : ArrayWorld.Tar; }
			var tar2 = w2.BodyAt(3, 1f, false); var water2 = w2.BodyAt(0, 1f, false);
			bool sameReverse = tar2 != water2 && tar2.cells.Count == 2 && water2.cells.Count == 2;
			return separate && ok && sameReverse
				? $"OK: water {water.cells.Count} cells, tar {tar.cells.Count} cells; channel over the tar holds {w.k.fill[chan]} {w.cellFluid[chan]?.name}"
				: $"BROKEN: separate={separate} channelOk={ok} reverseOk={sameReverse} (channel {w.k.fill[chan]}/{w.k.depth[chan]} {w.cellFluid[chan]})";
		}

		/// <summary>FLOW_ORDER_EXTERNAL_INPUT_1 part 2: a network bigger than the partition cap. A 200-cell channel off a
		/// limitless source, cap 50. Control (seams fixed, the shipped behaviour): the first partition fills and the
		/// rest of the channel stays dry forever. Seams moving: the whole channel fills, settles (no shuttle across a
		/// seam), and every pulse's ledger balances. A second control: on a network inside the cap, seams-moving on
		/// gives a pulse-by-pulse identical result to off and never rotates. Returns "OK ..." or "BROKEN ...".</summary>
		public static string OversizedNetworkExchanges()
		{
			int Run(int len, int cap, bool rotate, int pulses, out bool settled, out float worst, out int rotated, List<byte[]> trace)
			{
				var w = new ArrayWorld(len + 2, 1);
				w.natural[0] = true; w.terrainFluid[0] = ArrayWorld.Water;
				w.BodyAt(0, 1f, true);
				var seeds = new List<int>();
				for (int x = 1; x <= len; x++) { w.k.depth[x] = 1; seeds.Add(x); }
				w.k.maxComponentCells = cap;
				w.k.seamRotationEnabled = rotate;
				worst = 0f;
				for (int p = 0; p < pulses; p++)
				{
					w.Pulse(seeds); Pulses++;
					worst = Math.Max(worst, w.k.worstImbalance);
					trace?.Add((byte[])w.k.fill.Clone());
				}
				byte[] a = (byte[])w.k.fill.Clone();
				w.Pulse(seeds); byte[] b = (byte[])w.k.fill.Clone();
				w.Pulse(seeds); byte[] c = (byte[])w.k.fill.Clone();
				settled = a.SequenceEqual(b) && b.SequenceEqual(c);
				rotated = w.k.rotatedNetworks;
				int filled = 0;
				for (int x = 1; x <= len; x++) if (w.k.fill[x] > 0) filled++;
				Cases++;
				return filled;
			}
			int fixedFilled = Run(200, 50, false, 400, out _, out float e1, out int r1, null);
			int movedEarly = Run(200, 50, true, 400, out _, out _, out _, null);
			int wholeEarly = Run(200, 6000, false, 400, out _, out _, out _, null);
			int movedFilled = Run(200, 50, true, 3000, out bool settled, out float e2, out int r2, null);
			var offTrace = new List<byte[]>(); var onTrace = new List<byte[]>();
			Run(40, 6000, false, 60, out _, out float e3, out _, offTrace);
			Run(40, 6000, true, 60, out _, out float e4, out int r4, onTrace);
			bool smallSame = offTrace.Count == onTrace.Count && offTrace.Zip(onTrace, (x, y) => x.SequenceEqual(y)).All(t => t) && r4 == 0;
			bool controlStuck = fixedFilled < 200 && r1 == 0;     // the defect must be visible, or this proves nothing
			bool balanced = Math.Max(Math.Max(e1, e2), Math.Max(e3, e4)) <= 0.001f;
			string line = $"200-cell channel, cap 50: seams fixed {fixedFilled}/200 wet, seams moving {movedFilled}/200 wet after 3000 pulses ({r2} rotated walks; after 400: {movedEarly}, one uncapped piece {wholeEarly}), settled={settled}; 40-cell inside-cap control identical={smallSame}";
			return controlStuck && movedFilled == 200 && settled && balanced && smallSame
				? "OK: " + line
				: $"BROKEN: {line} controlStuck={controlStuck} balanced={balanced}";
		}

		/// <summary>How far (cells down a 40-cell channel off a limitless source) the fill front is after N pulses.</summary>
		public static int FrontAfter(Fluid f, bool creep, int pulses, out float worstImbalance)
		{
			var w = new ArrayWorld(42, 1);
			w.natural[0] = true; w.terrainFluid[0] = f;
			w.BodyAt(0, 1f, true);
			var seeds = new List<int>();
			for (int x = 1; x <= 40; x++) { w.k.depth[x] = 1; seeds.Add(x); }
			w.k.viscosityEnabled = true;
			w.k.creepEnabled = creep;
			worstImbalance = 0f;
			for (int p = 0; p < pulses; p++) { w.Pulse(seeds); worstImbalance = Math.Max(worstImbalance, w.k.worstImbalance); }
			int front = 0;
			for (int x = 1; x <= 40; x++) if (w.k.fill[x] > 0) front = x;
			return front;
		}

		/// <summary>THICK_LIQUID_CREEP_1 (FL-2): measures how fast the front travels down a 40-cell channel. Control: with creep OFF a
		/// tar front races the whole channel on its first moving pulse (this is the defect). With creep ON tar advances one cell per
		/// moving pulse (stride 6: at most pulses/6 + 1 cells), slime slower still, and water is exactly as fast as before.</summary>
		public static string FrontSpeed()
		{
			var tar = ArrayWorld.Tar;
			var slime = new Fluid { name = "slime", tpt = 480 };
			int tarOff = FrontAfter(tar, false, 30, out float e1);
			int tarOn = FrontAfter(tar, true, 30, out float e2);
			int slimeOn = FrontAfter(slime, true, 48, out float e3);
			int waterOff = FrontAfter(ArrayWorld.Water, false, 10, out float e4);
			int waterOn = FrontAfter(ArrayWorld.Water, true, 10, out float e5);
			bool controlRaces = tarOff >= 40;                 // the old behaviour must be visible, or the fixture proves nothing
			bool tarCrawls = tarOn >= 1 && tarOn <= 30 / 6 + 1;
			bool slimeCrawls = slimeOn >= 1 && slimeOn <= 48 / 8 + 1;
			bool waterSame = waterOff == waterOn && waterOn > 0;
			bool balanced = Math.Max(Math.Max(e1, e2), Math.Max(e3, Math.Max(e4, e5))) <= 0.001f;
			string line = $"front after 30 pulses: tar creep-off {tarOff}, tar creep-on {tarOn}; slime after 48: {slimeOn}; water after 10: off {waterOff} on {waterOn}";
			return controlRaces && tarCrawls && slimeCrawls && waterSame && balanced
				? "OK: " + line
				: $"BROKEN: controlRaces={controlRaces} tarCrawls={tarCrawls} slimeCrawls={slimeCrawls} waterSame={waterSame} balanced={balanced} ({line})";
		}

		/// <summary>CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY / CANAL_FRONT_FIX_WRONG_END_WETS_FIRST: plot C's live shape offline. A
		/// LIMITED 60-cell water body (stock 300) beside the mouth of a dead-end 1x10 D=1 channel. With water creep OFF the
		/// level the mouth takes is pulled on in the same pulse (the old race): after 3 pulses the far end is wet and the mouth
		/// dry. With it ON (the shipped default) the wet front advances outward from the mouth, at most one cell a pulse: after
		/// each of the first 3 pulses the mouth is the first wet cell, the farthest wet cell is within p cells of it, and the
		/// body paid exactly the levels the channel holds; after 20 pulses the run is full.</summary>
		public static string CanalMouthDeadEndFillsFromFarEnd()
		{
			string race = CanalRun(false, 3, out string raceAt, out bool _r, out float _w1);
			bool raceShape = raceAt == "0000000111";
			bool order = true, bounded = true, conserved = true;
			float worst = 0f;
			var w = new ArrayWorld(20, 6);
			var bodyCells = new List<int>();
			for (int z = 0; z < 6; z++) for (int x = 0; x < 10; x++) bodyCells.Add(z * 20 + x);
			var body = w.AddBody(false, 300f, bodyCells);
			var digs = Enumerable.Range(10, 10).Select(x => 2 * 20 + x).ToList();
			foreach (int c in digs) w.k.depth[c] = 1;
			w.k.creepWaterEnabled = true;
			var trace = new List<string>();
			for (int p = 1; p <= 3; p++)
			{
				w.Pulse(digs); worst = Math.Max(worst, w.k.worstImbalance);
				string at = string.Join("", digs.Select(c => w.k.fill[c]));
				trace.Add(at);
				int last = at.LastIndexOf('1');
				if (last >= p) bounded = false;
				if (Math.Abs((300f - body.stock) - at.Count(ch => ch == '1')) > 1f) conserved = false;
				if (p == 1 && at != "1000000000") order = false;
			}
			for (int p = 3; p < 20; p++) { w.Pulse(digs); worst = Math.Max(worst, w.k.worstImbalance); }
			string at20 = string.Join("", digs.Select(c => w.k.fill[c]));
			bool full = at20 == "1111111111";
			string line = $"race(off) after 3 = {raceAt}; creep(on) per pulse {string.Join(" ", trace)}, after 20 {at20}, stock {body.stock:F1}; worst imbalance {worst:F3}";
			return raceShape && order && bounded && conserved && full && worst <= 0.001f
				? "OK: " + line
				: $"BROKEN: raceShape={raceShape} mouthFirst={order} bounded={bounded} conserved={conserved} full={full} ({line})";
		}

		private static string CanalRun(bool creepWater, int pulses, out string at, out bool ok, out float worst)
		{
			var w = new ArrayWorld(20, 6);
			var bodyCells = new List<int>();
			for (int z = 0; z < 6; z++) for (int x = 0; x < 10; x++) bodyCells.Add(z * 20 + x);
			w.AddBody(false, 300f, bodyCells);
			var digs = Enumerable.Range(10, 10).Select(x => 2 * 20 + x).ToList();
			foreach (int c in digs) w.k.depth[c] = 1;
			w.k.creepWaterEnabled = creepWater;
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
			w.k.creepWaterEnabled = true;
			w.k.levelBySurfaceEnabled = surface;
			w.k.levelSetEnabled = surface && LevelSet;
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

		/// <summary>A closed, flat D=2 run with all its water at one end (2,2,2,2,0..0): by surface it spreads until no two
		/// cells anywhere in the run differ by more than one unit (no 2,2,1,1,0 terrace), keeps all 8 units, and is at rest well inside 200 pulses. The old rule
		/// moves nothing (a brim-full cell may only overflow down a flow order, and a sourceless, sinkless run has none).</summary>
		public static string SurfaceFlatChannelLevels()
		{
			int[] depths = Enumerable.Repeat(2, 10).ToArray();
			int[] fills = { 2, 2, 2, 2, 0, 0, 0, 0, 0, 0 };
			var on = SurfaceRow(depths, fills, true);
			string end = SurfaceRun(on, 200, out int settled, out float worst, out _);
			int sum = on.k.fill.Sum(f => f);
			int step = MaxNeighbourSurfaceStep(on);
			int spread = on.k.fill.Max(f => f) - on.k.fill.Min(f => f);   // one bed depth: fill spread = surface spread
			string old = SurfaceRun(SurfaceRow(depths, fills, false), 200, out _, out _, out _);
			bool ok = sum == 8 && step <= 1 && spread <= 1 && settled >= 0 && settled < 150 && worst <= 0.001f && old == "2,2,2,2,0,0,0,0,0,0";
			string line = $"surface F={end} (sum {sum}, max neighbour step {step}, spread {spread}, at rest after pulse {settled}, worst imbalance {worst:F3}); old rule F={old}";
			return (ok ? "OK: " : "BROKEN: ") + line;
		}

		/// <summary>A full D=2 run breached into the sink band at x=0 drains to EMPTY by surface (the owner's review-station-1
		/// sighting: the old rule strands the bottom unit of every cell), every unit accounted to the sink.</summary>
		public static string SurfaceEdgeDrainedChannelEmpties()
		{
			int[] depths = Enumerable.Repeat(2, 13).ToArray();
			int[] fills = Enumerable.Repeat(2, 13).ToArray();
			var on = SurfaceRow(depths, fills, true, 1);
			string end = SurfaceRun(on, 200, out int settled, out float worst, out float drained);
			string old = SurfaceRun(SurfaceRow(depths, fills, false, 1), 200, out _, out _, out _);
			bool empty = on.k.fill.All(f => f == 0);
			bool ok = empty && Math.Abs(drained - 26f) < 0.001f && settled >= 0 && worst <= 0.001f && old.Contains("1");
			string line = $"surface F={end} drained {drained:F0}/26 at rest after pulse {settled}; old rule F={old}";
			return (ok ? "OK: " : "BROKEN: ") + line;
		}

		/// <summary>Depth stops deciding: (a) a D=1 trench holding water (1,1,1,1,1) beside an empty D=4 hole pours into
		/// the hole until the surfaces are within one unit; (b) a D=3 cell at 1/3 (surface -2) beside a D=4 hole at 3/4
		/// (surface -1) gives NOTHING: the old GRAVITY rule pushed it uphill into the deeper bed.</summary>
		public static string SurfaceDeepHoleBesideShallowTrench()
		{
			var a = SurfaceRow(new[] { 1, 1, 1, 1, 1, 4 }, new[] { 1, 1, 1, 1, 1, 0 }, true);
			string endA = SurfaceRun(a, 200, out int settledA, out float worstA, out _);
			int stepA = MaxNeighbourSurfaceStep(a);
			bool okA = a.k.fill.Sum(f => f) == 5 && stepA <= 1 && a.k.fill[5] >= 3 && settledA >= 0 && worstA <= 0.001f;
			var b = SurfaceRow(new[] { 3, 4 }, new[] { 1, 3 }, true);
			string endB = SurfaceRun(b, 50, out _, out float worstB, out _);
			string oldB = SurfaceRun(SurfaceRow(new[] { 3, 4 }, new[] { 1, 3 }, false), 50, out _, out _, out _);
			bool okB = endB == "1,3" && oldB == "0,4" && worstB <= 0.001f;
			// (c) review finding: pit 3/4 | channel 1/1 | empty pit 0/4. The channel's one unit goes to a pit and the channel
			// runs dry; the first pit must never be drawn below the channel floor (-1, i.e. F &lt; 3) through that dry square
			// (a "wet region" that outlived its connector mid-pass did exactly that).
			var c = SurfaceRow(new[] { 4, 1, 4 }, new[] { 3, 1, 0 }, true);
			string endC = SurfaceRun(c, 50, out _, out float worstC, out _);
			bool okC = (endC == "3,0,1" || endC == "4,0,0") && worstC <= 0.001f;
			string line = $"(a) trench+hole F={endA} step {stepA} rest {settledA}; (b) 1/3 beside 3/4: surface {endB}, old rule {oldB}; (c) 3/4|1/1|0/4 -> {endC}";
			return (okA && okB && okC ? "OK: " : "BROKEN: ") + line;
		}

		/// <summary>A limitless pond feeding a D=2 run still fills it full, mouth first (creep on), ledger balanced.</summary>
		public static string SurfaceSourceStillFillsChannel()
		{
			var w = new ArrayWorld(11, 1);
			w.AddBody(true, 0f, new[] { 0 });
			var digs = Enumerable.Range(1, 10).ToList();
			foreach (int c in digs) w.k.depth[c] = 2;
			w.k.viscosityEnabled = true; w.k.creepWaterEnabled = true; w.k.levelBySurfaceEnabled = true; w.k.levelSetEnabled = LevelSet;
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
				w.k.edgeSinksEnabled = band > 0; w.k.viscosityEnabled = true; w.k.creepWaterEnabled = true; w.k.levelBySurfaceEnabled = true; w.k.levelSetEnabled = LevelSet;
				float startTotal = w.k.fill.Sum(f => f) + (pond?.stock ?? 0f);
				var digs = Enumerable.Range(0, 64).Where(i => w.k.depth[i] > 0).ToList();
				string prev = null; int lastChange = 0; float worst = 0f, drained = 0f;
				for (int p = 1; p <= 200; p++)
				{
					w.Pulse(digs);
					worst = Math.Max(worst, w.k.worstImbalance);
					drained += w.k.sinkDrained;
					string now = string.Join(",", digs.Select(c => w.k.fill[c]));
					if (now != prev) lastChange = p;
					prev = now;
				}
				float endTotal = w.k.fill.Sum(f => f) + (pond?.stock ?? 0f) + drained;
				bool rest = lastChange <= 150, bal = worst <= 0.001f && Math.Abs(endTotal - startTotal) < 0.001f;
				// At rest, no wet cell stands 2+ above a dug neighbour in its own network (sealed/sink-free scenes only;
				// a sink band empties toward the edge, and a different-fluid wall cannot happen here: one fluid).
				bool level = true;
				if (band == 0)
				{
					for (int i = 0; i < 64 && level; i++)
					{
						if (w.k.depth[i] == 0 || w.k.fill[i] == 0) continue;
						for (int d = 0; d < 4; d++)
						{
							int n = w.k.Cardinal(i, d);
							if (n >= 0 && w.k.depth[n] > 0 && (w.k.fill[i] - w.k.depth[i]) - (w.k.fill[n] - w.k.depth[n]) >= 2) { level = false; break; }
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
			return session == reload && session == (1, 0)
				? $"OK: both orders pay (A,B)={session}"
				: $"BROKEN: session (A,B)={session}, reload {reload}, expected (1, 0) for both";
		}
	}

	/// <summary>Reads scenes (one per line: w h pulses sinkBand nBodies [limitless stock]* nSources [idx body]*
	/// nDigs [idx depth]*), runs the production kernel, writes one line per scene: every dug cell's F after every
	/// pulse, then each body's final stock.</summary>
	internal static class OracleScenes
	{
		public static int Run(System.IO.TextReader input, System.IO.TextWriter output, bool levelBySurface = false, bool levelSet = false)
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
				world.k.levelBySurfaceEnabled = levelBySurface;
				world.k.levelSetEnabled = levelBySurface && levelSet;
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
