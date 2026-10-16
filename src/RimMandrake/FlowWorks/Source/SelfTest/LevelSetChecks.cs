// WATER_LEVELSET_SOLVE (owner 2026-10-16 at review station 1: "Please select an algorithm that will allow the fluid to
// levelset down to a smooth 0 or 1 across a too-wide field like this, not 0, deep, 0"). The PRODUCTION kernel
// (RM_FlowKernel.cs) on plain arrays, with the shipped flags (viscosity, water creep, level by surface, level solve).

using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
	internal static class LevelSetChecks
	{
		public static ArrayWorld Basin(int w, int h, int x0, int z0, int bw, int bh, int depth, bool levelSet)
		{
			var a = new ArrayWorld(w, h);
			for (int z = z0; z < z0 + bh; z++)
				for (int x = x0; x < x0 + bw; x++)
					a.k.depth[z * w + x] = (byte)depth;
			a.k.viscosityEnabled = true; a.k.creepWaterEnabled = true; a.k.levelBySurfaceEnabled = true; a.k.levelSetEnabled = levelSet;
			return a;
		}

		private static void Wet(ArrayWorld a, int idx, int f) { a.k.fill[idx] = (byte)f; a.cellFluid[idx] = f > 0 ? ArrayWorld.Water : null; }

		/// <summary>Runs pulses; returns the pulse after which F never changed again (-1 = still moving at the end).</summary>
		public static int Run(ArrayWorld a, int pulses, out float worst, out float drained)
		{
			var digs = Enumerable.Range(0, a.w * a.h).Where(i => a.k.depth[i] > 0).ToList();
			string prev = string.Join(",", digs.Select(c => a.k.fill[c]));
			int settled = 0; worst = 0f; drained = 0f;
			for (int p = 1; p <= pulses; p++)
			{
				a.Pulse(digs);
				worst = Math.Max(worst, a.k.worstImbalance);
				drained += a.k.sinkDrained;
				string now = string.Join(",", digs.Select(c => a.k.fill[c]));
				if (now != prev) settled = p;
				prev = now;
			}
			return settled == pulses ? -1 : settled;
		}

		public static string FillGrid(ArrayWorld a)
		{
			var sb = new System.Text.StringBuilder();
			for (int z = a.h - 1; z >= 0; z--)
			{
				for (int x = 0; x < a.w; x++)
				{
					int i = z * a.w + x;
					sb.Append(a.k.depth[i] > 0 ? (char)('0' + a.k.fill[i]) : a.natural[i] ? '~' : ' ');
				}
				sb.Append('|');
			}
			return sb.ToString();
		}

		/// <summary>Number of 4-connected pieces of wet dug squares.</summary>
		private static int WetPieces(ArrayWorld a)
		{
			var seen = new HashSet<int>(); int pieces = 0;
			for (int i = 0; i < a.w * a.h; i++)
			{
				if (a.k.depth[i] == 0 || a.k.fill[i] == 0 || seen.Contains(i)) continue;
				pieces++;
				var q = new Queue<int>(); q.Enqueue(i); seen.Add(i);
				while (q.Count > 0)
				{
					int c = q.Dequeue();
					for (int d = 0; d < 4; d++)
					{
						int n = a.k.Cardinal(c, d);
						if (n >= 0 && a.k.depth[n] > 0 && a.k.fill[n] > 0 && seen.Add(n)) q.Enqueue(n);
					}
				}
			}
			return pieces;
		}

		private static int Total(ArrayWorld a) => a.k.fill.Sum(f => f);

		/// <summary>(1) The owner's station-1 field: a wide flat D3 basin (12x12), 30 units. (a) dumped as a deep 3-high
		/// blob in the middle; (b) poured in through a canal from a LIMITED pond. Both end as ONE contiguous patch of
		/// depth 1 (no square 2 or deeper, no stripes), conserved to the unit, at rest. The unit-at-a-time pass is run on
		/// (b) for the record (it stripes 0,1,0,1 and walks the water to the far wall).</summary>
		public static string LowVolumeWideBasinOnePatch()
		{
			var a = Basin(16, 16, 2, 2, 12, 12, 3, true);
			for (int z = 7; z < 9; z++) for (int x = 7; x < 12; x++) Wet(a, z * 16 + x, 3);   // 10 squares x 3 = 30
			int restA = Run(a, 300, out float worstA, out _);
			bool okA = Total(a) == 30 && a.k.fill.Max() == 1 && WetPieces(a) == 1 && restA >= 0 && worstA <= 0.001f;

			ArrayWorld Fed(bool ls)
			{
				var b = Basin(18, 16, 6, 2, 12, 12, 3, ls);
				for (int x = 1; x < 6; x++) b.k.depth[8 * 18 + x] = 3;
				b.AddBody(false, 30f, new[] { 7 * 18, 8 * 18, 9 * 18 });
				return b;
			}
			var on = Fed(true);
			int restB = Run(on, 400, out float worstB, out _);
			bool okB = Total(on) == 30 && on.bodies[0].stock == 0f && on.k.fill.Max() == 1 && WetPieces(on) == 1 && restB >= 0 && worstB <= 0.001f;
			var off = Fed(false);
			Run(off, 400, out _, out _);
			string line = $"(a) blob -> max {a.k.fill.Max()}, pieces {WetPieces(a)}, sum {Total(a)}/30, rest {restA}; (b) pond-fed -> max {on.k.fill.Max()}, pieces {WetPieces(on)}, sum {Total(on)}/30, rest {restB}; unit pass: pieces {WetPieces(off)}";
			return (okA && okB ? "OK: " : "BROKEN: ") + line + (okA && okB ? "" : "\n" + FillGrid(a) + "\n" + FillGrid(on));
		}

		/// <summary>(2) Enough volume: a closed 10x10 D2 basin holding 100 units all in its west half (fill 2) ends a
		/// uniform sheet at fill 1 everywhere; 150 units ends 1 everywhere plus ONE contiguous patch of 2.</summary>
		public static string EnoughVolumeFlatSheet()
		{
			var a = Basin(12, 12, 1, 1, 10, 10, 2, true);
			for (int z = 1; z < 11; z++) for (int x = 1; x < 6; x++) Wet(a, z * 12 + x, 2);
			int restA = Run(a, 300, out float worstA, out _);
			var dug = Enumerable.Range(0, 144).Where(i => a.k.depth[i] > 0).ToList();
			bool okA = Total(a) == 100 && dug.All(i => a.k.fill[i] == 1) && restA >= 0 && worstA <= 0.001f;
			var b = Basin(12, 12, 1, 1, 10, 10, 2, true);
			for (int z = 1; z < 11; z++) { for (int x = 1; x < 8; x++) Wet(b, z * 12 + x, 2); Wet(b, z * 12 + 8, 1); }   // 140 + 10
			int startB = Total(b);
			int restB = Run(b, 300, out float worstB, out _);
			var twos = new ArrayWorld(12, 12);
			for (int i = 0; i < 144; i++) if (b.k.fill[i] == 2) { twos.k.depth[i] = 1; twos.k.fill[i] = 1; }
			bool okB = Total(b) == startB && dug.All(i => b.k.fill[i] >= 1 && b.k.fill[i] <= 2) && WetPieces(twos) == 1 && restB >= 0 && worstB <= 0.001f;
			string line = $"100 units -> all 1: {okA} (rest {restA}); {startB} units -> min {dug.Min(i => b.k.fill[i])} max {dug.Max(i => b.k.fill[i])}, pieces of 2: {WetPieces(twos)}, rest {restB}";
			return (okA && okB ? "OK: " : "BROKEN: ") + line + (okA && okB ? "" : "\n" + FillGrid(a) + "\n" + FillGrid(b));
		}

		/// <summary>(3) Stepped floor: a closed 10x6 basin, west half D2 brim-full (surface 0), east half D4 at fill 2
		/// (surface -2). The free surface ends FLAT at -1 (D2 holds 1, D4 holds 3), 120 units kept. Plus the sill case:
		/// pit 3/4 | channel 1/1 | pit 0/4 ends 3,0,1 — the first pit is never drawn down through the dry channel.</summary>
		public static string SteppedFloorFlatSurface()
		{
			var a = Basin(12, 8, 1, 1, 10, 6, 2, true);
			for (int z = 1; z < 7; z++) for (int x = 1; x < 11; x++)
			{
				int i = z * 12 + x;
				if (x >= 6) a.k.depth[i] = 4;
				Wet(a, i, 2);
			}
			int rest = Run(a, 300, out float worst, out _);
			var dug = Enumerable.Range(0, 96).Where(i => a.k.depth[i] > 0).ToList();
			var surfaces = dug.Select(i => a.k.fill[i] - a.k.depth[i]).Distinct().ToList();
			bool okA = Total(a) == 120 && surfaces.Count == 1 && surfaces[0] == -1 && rest >= 0 && worst <= 0.001f;
			var s = new ArrayWorld(3, 1);
			s.k.depth[0] = 4; s.k.depth[1] = 1; s.k.depth[2] = 4;
			Wet(s, 0, 3); Wet(s, 1, 1);
			s.k.viscosityEnabled = true; s.k.creepWaterEnabled = true; s.k.levelBySurfaceEnabled = true; s.k.levelSetEnabled = true;
			Run(s, 50, out float worstS, out _);
			string sill = string.Join(",", s.k.fill);
			bool okS = sill == "3,0,1" && worstS <= 0.001f;
			string line = $"step D2|D4 surfaces {{{string.Join(",", surfaces)}}} sum {Total(a)}/120 rest {rest}; sill 3/4|1/1|0/4 -> {sill}";
			return (okA && okS ? "OK: " : "BROKEN: ") + line + (okA ? "" : "\n" + FillGrid(a));
		}

		/// <summary>(4) Conservation to the unit and the edge drain (the coordinator's station-1 save read: the lower canal
		/// held 16 levels as 1,0,1,0 where it should drain off the edge). (a) A LIMITED pond (40 units) pours down a 30-long
		/// D2 canal whose west end is the sink band: once the pond is spent the canal ends EMPTY and the sink took exactly
		/// 40. (b) 500 seeded random 10x10 scenes (random depths, fills, optional pond and sink band): fill + pond + drained
		/// constant to the unit, the ledger balanced every pulse, and at rest by pulse 250.</summary>
		public static string ConservesAndDrains()
		{
			var c = new ArrayWorld(32, 1);
			c.AddBody(false, 40f, new[] { 31 });
			for (int x = 0; x < 31; x++) { c.k.depth[x] = 2; c.sink[x] = x < 1; }
			c.k.edgeSinksEnabled = true; c.k.viscosityEnabled = true; c.k.creepWaterEnabled = true; c.k.levelBySurfaceEnabled = true; c.k.levelSetEnabled = true;
			int restC = Run(c, 400, out float worstC, out float drainedC);
			bool okC = Total(c) == 0 && Math.Abs(drainedC - 40f) < 0.001f && c.bodies[0].stock == 0f && restC >= 0 && worstC <= 0.001f;

			var rng = new Random(20261016 + 1);
			int bad = 0; string firstBad = null;
			for (int t = 0; t < 500; t++)
			{
				var w = new ArrayWorld(10, 10);
				int band = rng.Next(3) == 0 ? 1 : 0;
				ArrayWorld.Body pond = null;
				if (rng.Next(2) == 0) pond = w.AddBody(false, rng.Next(0, 20), new[] { rng.Next(100) });
				for (int i = 0; i < 70; i++)
				{
					int cc = rng.Next(100);
					if (w.natural[cc]) continue;
					w.k.depth[cc] = (byte)rng.Next(1, 5);
					Wet(w, cc, rng.Next(0, w.k.depth[cc] + 1));
				}
				for (int i = 0; i < 100; i++) { int x = i % 10, z = i / 10; w.sink[i] = band > 0 && (x < band || z < band || x >= 10 - band || z >= 10 - band); }
				w.k.edgeSinksEnabled = band > 0; w.k.viscosityEnabled = true; w.k.creepWaterEnabled = true; w.k.levelBySurfaceEnabled = true; w.k.levelSetEnabled = true;
				float start = Total(w) + (pond?.stock ?? 0f);
				int rest = Run(w, 300, out float worst, out float drained);
				float end = Total(w) + (pond?.stock ?? 0f) + drained;
				bool ok = Math.Abs(end - start) < 0.001f && worst <= 0.001f && rest >= 0 && rest <= 250;
				if (!ok) { bad++; firstBad ??= $"scene {t}: start {start} end {end} worst {worst} rest {rest}\n{FillGrid(w)}"; }
			}
			string line = $"(a) pond 40 down a drained canal: left {Total(c)}, drained {drainedC:F0}/40, rest {restC}; (b) 500 random scenes, {bad} failing";
			return (okC && bad == 0 ? "OK: " : "BROKEN: ") + line + (okC ? "" : "\n" + FillGrid(c)) + (bad == 0 ? "" : "\n" + firstBad);
		}

		/// <summary>(5) Cost: a 120x120 D3 basin (14,400 squares, so the 6000-square cap partitions it as in game, seams
		/// moving) with its west half holding 3 levels (21,600 units), fed from a limitless pond, 100 pulses. Reports ms
		/// per pulse; the bar is 40 ms (a pulse runs every 250 ticks).</summary>
		public static string WideBasinCost()
		{
			var a = Basin(124, 124, 2, 2, 120, 120, 3, true);
			a.AddBody(true, 0f, new[] { 62 * 124 + 1 });
			a.k.seamRotationEnabled = true;
			for (int z = 2; z < 122; z++) for (int x = 2; x < 62; x++) Wet(a, z * 124 + x, 3);
			var digs = Enumerable.Range(0, a.w * a.h).Where(i => a.k.depth[i] > 0).ToList();
			var clock = System.Diagnostics.Stopwatch.StartNew();
			float worst = 0f;
			for (int p = 0; p < 100; p++) { a.Pulse(digs); worst = Math.Max(worst, a.k.worstImbalance); }
			double ms = clock.Elapsed.TotalMilliseconds / 100;
			bool ok = ms < 40 && worst <= 0.001f && a.k.fill.Max() <= 3;
			return (ok ? "OK: " : "BROKEN: ") + $"{ms:F2} ms/pulse over 100 pulses, {Total(a)} units in, worst imbalance {worst:F3}";
		}
	}
}
