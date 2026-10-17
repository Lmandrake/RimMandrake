// WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES (plan P3 of FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG). Owner, 2026-10-17: "We need VERY
// smooth water. That's water's one primary characteristic: a level surface." Ruled exactly level by card.
// The PRODUCTION exact kernel (RM_FlowKernel.levelExactEnabled + RM_LevelSolve) at the SHIPPED flags on plain arrays: the
// redrawn S5/S6 numbers (design/RimMandrake/flowworks_level_surface_2026-10-17.md §1, worked by hand), conservation to the
// decilitre, one surface per body (the R9 bar's offline twin, read with the same RM_SurfaceGap the live proof uses), a
// sill that splits a falling body and joins a rising one, the save migration's arithmetic, and the look by true metres.
// The Python twin is northstar/level_water.py; selftest_flowworks_kernel_oracle.py (modes exact, exactpond) diffs them.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
	internal static class LevelExactChecks
	{
		private const int U = RM_LevelSolve.U;

		private static void Assert(bool ok, string msg)
		{
			if (!ok) throw new Exception(msg);
		}

		/// <summary>The shipped kernel flags (RimMandrakeFlowWorksSettings defaults through DoPulse's copy lines).</summary>
		private static ArrayWorld World(int w, int h)
		{
			var world = new ArrayWorld(w, h);
			world.k.levelBySurfaceEnabled = true;
			world.k.levelSetEnabled = true;
			world.k.creepWaterEnabled = true;
			world.k.creepEnabled = true;
			world.k.viscosityEnabled = true;
			world.k.levelExactEnabled = true;
			return world;
		}

		private static long Total(ArrayWorld w)
		{
			long t = 0;
			for (int i = 0; i < w.w * w.h; i++) if (w.k.depth[i] > 0) t += w.k.WaterOf(i);
			foreach (var b in w.bodies) if (!b.limitless) t += b.Dl();
			return t;
		}

		private static double M(long dl) => RM_LevelSolve.Metres(dl);

		/// <summary>Worst surface gap (metres) over every body of the world (RM_SurfaceGap, the live diagnostic's maths).</summary>
		public static double WorstGap(ArrayWorld w, out int bodies)
		{
			var cells = Enumerable.Range(0, w.w * w.h).Where(i => w.k.depth[i] > 0).ToList();
			var list = RM_SurfaceGap.Measure(cells, i => w.k.depth[i], i => w.k.WaterOf(i), i => w.cellFluid[i],
				(i, d) => w.k.Cardinal(i, d),
				i => !w.k.IsSource(i) ? -1 : w.LevelBodyOf(i) < 0 ? -2 : w.LevelBodyOf(i),
				b => RM_LevelSolve.PondSurfaceHeight(w.BodyHistogram(b), w.BodyStockDl(b)),
				i => w.BedAt(i));
			bodies = list.Count;
			return list.Count == 0 ? 0.0 : list[0].gapM;
		}

		/// <summary>A 3x3 (or 1-square) enclosed pond of bed 4 holding <paramref name="levels"/> and a dry canal off its east middle.</summary>
		private static (ArrayWorld w, List<int> canal, ArrayWorld.Body body) PondAndCanal(int pondSquares, float levels, int canalLen, int canalDepth)
		{
			var w = World(20, 5);
			var pond = new List<int>();
			if (pondSquares == 9) { for (int z = 1; z <= 3; z++) for (int x = 1; x <= 3; x++) pond.Add(z * 20 + x); }
			else pond.Add(2 * 20 + 1);
			var body = w.AddBody(false, levels, pond);
			foreach (int c in pond) w.bed[c] = 4;
			int x0 = pondSquares == 9 ? 4 : 2;
			var canal = Enumerable.Range(x0, canalLen).Select(x => 2 * 20 + x).ToList();
			foreach (int c in canal) w.k.depth[c] = (byte)canalDepth;
			return (w, canal, body);
		}

		private static void Settle(ArrayWorld w, List<int> seeds, int pulses, out bool conserved)
		{
			long t0 = Total(w);
			conserved = true;
			for (int p = 0; p < pulses; p++)
			{
				w.Pulse(seeds);
				if (Total(w) != t0 || w.k.worstImbalance > 0) conserved = false;
			}
		}

		public static void Run(Action<string, Action> Case)
		{
			Case("Exact_S5A_full_pond_wets_all_ten_canal_squares_at_0237", () =>
			{
				var (w, canal, body) = PondAndCanal(9, 36f, 10, 1);
				Settle(w, canal, 200, out bool cons);
				var depths = canal.Select(c => Math.Round(M(w.k.WaterOf(c)), 3)).ToArray();
				Assert(depths.All(d => d == 0.237), "all ten canal squares 0.237 m: " + string.Join(" ", depths));
				double surf = M((long)Math.Round(RM_LevelSolve.PondSurfaceHeight(w.BodyHistogram(body.id), body.Dl())));
				Assert(Math.Abs(surf + 5.0 / 19) < 1e-3, "pond surface -5/19 m (1.737 m deep): " + surf.ToString("F4"));
				Assert(cons, "36,000 L conserved to the decilitre at every pulse, ledger balanced");
				Assert(WorstGap(w, out int nb) < 0.001 && nb == 1, "one body, surface gap under 1 mm: " + WorstGap(w, out _));
			});

			Case("Exact_S5B_one_pond_square_wets_all_ten_at_45mm", () =>
			{
				var (w, canal, body) = PondAndCanal(1, 4f, 10, 1);
				Settle(w, canal, 200, out bool cons);
				var depths = canal.Select(c => M(w.k.WaterOf(c))).ToArray();
				Assert(depths.All(d => Math.Abs(d - 0.0455) < 0.0006), "all ten at 4.5 cm: " + string.Join(" ", depths.Select(d => d.ToString("F4"))));
				Assert(cons && Total(w) == 4L * U, "4,000 L conserved to the decilitre");
				Assert(WorstGap(w, out _) < 0.001, "surface gap under 1 mm: " + WorstGap(w, out _));
			});

			Case("Exact_S5F_pond_square_and_dug_pit_level_at_one_metre_each", () =>
			{
				var (w, canal, body) = PondAndCanal(1, 4f, 1, 4);
				Settle(w, canal, 50, out bool cons);
				Assert(w.k.WaterOf(canal[0]) == 2L * U && body.Dl() == 2L * U, $"1 m + 1 m: {w.k.WaterOf(canal[0])} / {body.Dl()}");
			});

			Case("Exact_S5_control_low_pond_feeds_no_shallow_canal", () =>
			{
				var (w, canal, body) = PondAndCanal(9, 26f, 10, 1);
				Settle(w, canal, 60, out bool cons);
				Assert(canal.All(c => w.k.WaterOf(c) == 0) && body.Dl() == 26L * U, "a pond whose surface is 0.56 m down feeds no 0.5 m canal");
			});

			Case("Exact_S5E_wide_basin_one_flat_sheet", () =>
			{
				var w = World(8, 8);
				var basin = new List<int>();
				for (int z = 1; z <= 6; z++) for (int x = 1; x <= 6; x++) { int c = z * 8 + x; basin.Add(c); w.k.depth[c] = 2; }
				foreach (int c in new[] { 3 * 8 + 3, 3 * 8 + 4, 4 * 8 + 3, 4 * 8 + 4 }) { w.k.fill[c] = 2; w.cellFluid[c] = ArrayWorld.Water; }
				Settle(w, basin, 60, out bool cons);
				var d = basin.Select(c => Math.Round(M(w.k.WaterOf(c)), 3)).Distinct().ToArray();
				Assert(d.Length == 1 && d[0] == 0.111, "one 0.111 m sheet: " + string.Join(" ", d));
				Assert(cons, "8,000 L kept to the decilitre");
			});

			Case("Exact_S6_pond_alone_nine_squares_at_1444", () =>
			{
				int[] h = RM_PondDepthMath.Histogram(Enumerable.Repeat(4, 9).ToList());
				double s = RM_LevelSolve.PondSurfaceHeight(h, 26L * U);
				double w = RM_LevelSolve.PondSquareWater(4, s);
				Assert(Math.Round(M((long)Math.Round(w)), 3) == 1.444, "1.444 m in every square: " + M((long)Math.Round(w)));
				Assert(RM_PondDepthMath.StageForExact(w, 4) == RM_PondDepthMath.Stage.ChestDeep,
					"1.44 m shows the 1.5 m (chest-deep) look in all nine: " + RM_PondDepthMath.StageForExact(w, 4));
				Assert(RM_PondDepthMath.StageForExact(39999, 4) == RM_PondDepthMath.Stage.Original, "a nearly full square keeps its own water");
				Assert(RM_PondDepthMath.StageForExact(0.2, 4) == RM_PondDepthMath.Stage.Mud, "under half a decilitre is mud");
			});

			Case("Exact_S1_limitless_canal_fills_by_pulse_10_unbroken", () =>
			{
				var w = World(20, 3);
				var lake = new List<int>();
				for (int x = 0; x < 8; x++) for (int z = 0; z < 3; z++) lake.Add(z * 20 + x);
				w.AddBody(true, 0f, lake);
				var canal = Enumerable.Range(8, 8).Select(x => 20 + x).ToList();
				foreach (int c in canal) w.k.depth[c] = 1;
				int fullAt = -1;
				for (int p = 1; p <= 20; p++)
				{
					w.Pulse(canal);
					var wet = canal.Select(c => w.k.WaterOf(c) > 0).ToList();
					int k = wet.IndexOf(false); if (k < 0) k = wet.Count;
					Assert(!wet.Skip(k).Any(x => x), $"pulse {p}: the wet run is unbroken from the mouth");
					if (fullAt < 0 && canal.All(c => w.k.WaterOf(c) == U)) fullAt = p;
				}
				Assert(fullAt > 0 && fullAt <= 10, "full end to end by pulse 10: " + fullAt);
			});

			Case("Exact_sill_splits_a_falling_body_and_joins_a_rising_one", () =>
			{
				// rising: a fed 1 m channel, a 0.5 m sill, then a dry 1 m channel
				var w = World(12, 3);
				w.AddBody(true, 0f, new[] { 1 * 12 + 0 });
				var left = Enumerable.Range(1, 4).Select(x => 12 + x).ToList();
				int sill = 12 + 5;
				var right = Enumerable.Range(6, 4).Select(x => 12 + x).ToList();
				foreach (int c in left.Concat(right)) w.k.depth[c] = 2;
				w.k.depth[sill] = 1;
				var all = left.Concat(new[] { sill }).Concat(right).ToList();
				bool order = true;
				for (int p = 0; p < 60; p++)
				{
					w.Pulse(all);
					if (right.Any(c => w.k.WaterOf(c) > 0) && left.Any(c => w.k.WaterOf(c) < U)) order = false;
				}
				Assert(order, "the far basin wets only once the near one stands at the sill floor");
				Assert(all.All(c => w.k.WaterOf(c) == w.k.depth[c] * (long)U), "then it fills: one body");
				// falling: the same, settled full, drained from the far end through a sink: the near basin keeps its 0.5 m
				var f = World(12, 3);
				foreach (int c in left.Concat(right)) { f.k.depth[c] = 2; f.k.fill[c] = 2; f.cellFluid[c] = ArrayWorld.Water; }
				f.k.depth[sill] = 1; f.k.fill[sill] = 1; f.cellFluid[sill] = ArrayWorld.Water;
				f.k.depth[12 + 10] = 2; f.k.depth[12 + 11] = 2;
				f.sink[12 + 11] = true; f.k.edgeSinksEnabled = true;
				var allF = all.Concat(new[] { 12 + 10, 12 + 11 }).ToList();
				long t0 = Total(f); float drained = 0f; bool kept = true;
				for (int p = 0; p < 150; p++)
				{
					f.Pulse(allF);
					drained += f.k.sinkDrained;
					if (left.Any(c => f.k.WaterOf(c) < U)) kept = false;
				}
				Assert(kept && left.All(c => f.k.WaterOf(c) == U) && f.k.WaterOf(sill) == 0, "the near basin keeps 0.5 m below the sill floor");
				Assert(right.All(c => f.k.WaterOf(c) == 0), "the far basin drains to the last decilitre");
				Assert(Math.Abs(Total(f) + drained * U - t0) < 1, "kept + drained = start");
			});

			Case("Exact_fuzz_conserves_to_the_decilitre_and_rests_level", () =>
			{
				int scenes = 600, rested = 0;
				for (int seed = 0; seed < scenes; seed++)
				{
					var r = new Random(9100 + seed);
					int W = r.Next(3, 10), H = r.Next(3, 10);
					var w = World(W, H);
					int nb = r.Next(0, 3);
					for (int b = 0; b < nb; b++)
					{
						int x0 = r.Next(W), z0 = r.Next(H), bw = r.Next(1, 4), bh = r.Next(1, 4);
						var cells = new List<int>();
						for (int x = x0; x < Math.Min(W, x0 + bw); x++) for (int z = z0; z < Math.Min(H, z0 + bh); z++) if (!w.natural[z * W + x]) cells.Add(z * W + x);
						if (cells.Count == 0) continue;
						foreach (int c in cells) w.bed[c] = new[] { 2, 4, 4, 6 }[r.Next(4)];
						int cap = cells.Sum(c => w.bed[c]);
						w.AddBody(r.Next(4) == 0, r.Next(0, cap + 1), cells);
					}
					var digs = new List<int>();
					for (int d = 0; d < r.Next(1, W * H / 2 + 1); d++)
					{
						int c = r.Next(W * H);
						if (w.natural[c]) continue;
						w.k.depth[c] = (byte)Math.Max(w.k.depth[c], r.Next(1, 5));
						if (!digs.Contains(c)) digs.Add(c);
					}
					foreach (int c in digs) if (r.Next(3) == 0) { w.k.fill[c] = (byte)r.Next(0, w.k.depth[c] + 1); if (w.k.fill[c] > 0) w.cellFluid[c] = ArrayWorld.Water; }
					bool sinks = r.Next(4) == 0;
					if (sinks) { w.k.edgeSinksEnabled = true; for (int i = 0; i < W * H; i++) w.sink[i] = i % W == 0; }
					long t0 = Total(w);
					float drainedLv = 0f, paidLv = 0f;
					string prev = null; int still = 0;
					for (int p = 0; p < 400 && still < 3; p++)
					{
						w.externalIn.Clear();
						w.Pulse(digs);
						drainedLv += w.k.sinkDrained;
						paidLv += w.externalIn.Values.Sum();
						Assert(w.k.worstImbalance == 0, $"seed {seed} pulse {p}: kernel ledger {string.Join("; ", w.k.imbalanceReports)}");
						for (int i = 0; i < W * H; i++)
							Assert(w.k.depth[i] == 0 || (w.k.WaterOf(i) >= 0 && w.k.WaterOf(i) <= w.k.depth[i] * (long)U), $"seed {seed}: bounds at {i}");
						long now = Total(w);
						long want = t0 - (long)Math.Round(drainedLv * U) + (long)Math.Round(paidLv * U);
						Assert(Math.Abs(now - want) <= 1, $"seed {seed} pulse {p}: total {now} dL, start {t0} - drained + paid = {want}");
						string snap = string.Join(",", digs.Select(c => w.k.WaterOf(c))) + "|" + string.Join(",", w.bodies.Select(b => b.Dl()))
							+ "|" + w.k.exactCreditDl + "|" + w.k.exactDrainDl;
						still = snap == prev && w.k.exactCreditDl == 0 && w.k.exactDrainDl == 0 ? still + 1 : 0;
						prev = snap;
					}
					if (still >= 3)
					{
						rested++;
						double g = WorstGap(w, out _);
						Assert(g < 0.001, $"seed {seed}: at rest, a body's surface varies by {g:F4} m\n{w.Grid()}");
					}
				}
				Assert(rested > scenes / 2, $"only {rested} of {scenes} scenes came to rest (the gap check needs still water)");
			});

			Case("Exact_migration_reads_float_stock_to_the_decilitre", () =>
			{
				// RM_LiquidBody's load path: a save from before the exact model holds a float stock; stockDl = round(stock x U).
				foreach (float f in new[] { 0f, 1f, 26f, 25.37f, 3999.5f, 123456.7f })
				{
					long dl = (long)Math.Round(f * (double)U);
					Assert(Math.Abs(dl / (double)U - f) <= 0.5 / U + f * 6e-8, $"{f} levels -> {dl} dL keeps every litre");
				}
				// a whole-notch canal grid loads as W = F x U, part 0: unchanged
				var w = World(4, 1);
				w.k.depth[1] = 3; w.k.fill[1] = 2; w.cellFluid[1] = ArrayWorld.Water;
				w.k.part = new ushort[4];
				Assert(w.k.WaterOf(1) == 2L * U, "an old 2-notch square is 20,000 dL");
			});

			Case("Exact_look_follows_true_metres", () =>
			{
				Assert(RM_LevelSolve.LookBand(0) == 0, "dry");
				Assert(RM_LevelSolve.LookBand(4737) == 1, "0.237 m: the very-shallow look (hook)");
				Assert(RM_LevelSolve.LookBand(U) == 2, "0.5 m");
				Assert(RM_LevelSolve.LookBand(2 * U) == 3, "1 m");
				Assert(RM_LevelSolve.LookBand(28889) == 4, "1.44 m reads as 1.5 m");
				Assert(RM_LevelSolve.LookBand(4 * U) == 5 && RM_LevelSolve.LookBand(12 * U) == 5, "2 m and deeper");
				Assert(RM_LevelSolve.LookBand(U / 2) == 2 && RM_LevelSolve.LookBand(U / 2 - 1) == 1, "the 25 cm line");
			});

			Case("Exact_surface_gap_sees_a_step", () =>
			{
				// can the instrument go red? two wet squares of one run at different surfaces read as a gap
				var w = World(3, 1);
				w.k.part = new ushort[3];
				w.k.depth[0] = 2; w.k.depth[1] = 2; w.k.fill[0] = 2; w.k.fill[1] = 1;
				w.cellFluid[0] = w.cellFluid[1] = ArrayWorld.Water;
				double g = WorstGap(w, out int nb);
				Assert(nb == 1 && Math.Abs(g - 0.5) < 1e-9, "a 0.5 m step in one body reads 0.5 m: " + g);
			});
		}
	}
}
