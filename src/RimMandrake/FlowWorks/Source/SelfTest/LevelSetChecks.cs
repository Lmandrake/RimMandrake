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
			a.k.viscosityEnabled = true; 
			return a;
		}

		private static void Wet(ArrayWorld a, int idx, int f) { a.k.SetNotch(idx, f); a.cellFluid[idx] = f > 0 ? ArrayWorld.Water : null; }

		/// <summary>Runs pulses; returns the pulse after which F never changed again (-1 = still moving at the end).</summary>
		public static int Run(ArrayWorld a, int pulses, out float worst, out float drained)
		{
			var digs = Enumerable.Range(0, a.w * a.h).Where(i => a.k.depth[i] > 0).ToList();
			string prev = string.Join(",", digs.Select(c => a.k.Notch(c)));
			int settled = 0; worst = 0f; drained = 0f;
			for (int p = 1; p <= pulses; p++)
			{
				a.Pulse(digs);
				worst = Math.Max(worst, a.k.worstImbalance);
				drained += a.k.sinkDrained;
				string now = string.Join(",", digs.Select(c => a.k.Notch(c)));
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
					sb.Append(a.k.depth[i] > 0 ? (char)('0' + a.k.Notch(i)) : a.natural[i] ? '~' : ' ');
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
				if (a.k.depth[i] == 0 || a.k.Notch(i) == 0 || seen.Contains(i)) continue;
				pieces++;
				var q = new Queue<int>(); q.Enqueue(i); seen.Add(i);
				while (q.Count > 0)
				{
					int c = q.Dequeue();
					for (int d = 0; d < 4; d++)
					{
						int n = a.k.Cardinal(c, d);
						if (n >= 0 && a.k.depth[n] > 0 && a.k.Notch(n) > 0 && seen.Add(n)) q.Enqueue(n);
					}
				}
			}
			return pieces;
		}

		private static int Total(ArrayWorld a) => a.k.water.Sum(f => f / RM_LevelSolve.U);

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
			var surfaces = dug.Select(i => a.k.Notch(i) - a.k.depth[i]).Distinct().ToList();
			bool okA = Total(a) == 120 && surfaces.Count == 1 && surfaces[0] == -1 && rest >= 0 && worst <= 0.001f;
			var s = new ArrayWorld(3, 1);
			s.k.depth[0] = 4; s.k.depth[1] = 1; s.k.depth[2] = 4;
			Wet(s, 0, 3); Wet(s, 1, 1);
			s.k.viscosityEnabled = true; 
			Run(s, 50, out float worstS, out _);
			string sill = string.Join(",", s.k.water.Select(f => f / RM_LevelSolve.U));
			bool okS = sill == "3,0,1" && worstS <= 0.001f;
			string line = $"step D2|D4 surfaces {{{string.Join(",", surfaces)}}} sum {Total(a)}/120 rest {rest}; sill 3/4|1/1|0/4 -> {sill}";
			return (okA && okS ? "OK: " : "BROKEN: ") + line + (okA ? "" : "\n" + FillGrid(a));
		}

		/// <summary>L7's stripe: a dry dug non-sink square with wet squares of one surface on both sides in a line.</summary>
		public static int Stripes(ArrayWorld a) => StripeCells(a).Count;

		public static HashSet<int> StripeCells(ArrayWorld a)
		{
			var n = new HashSet<int>();
			for (int i = 0; i < a.w * a.h; i++)
			{
				if (a.k.depth[i] == 0 || a.k.Notch(i) != 0 || a.sink[i]) continue;
				int x = i % a.w, z = i / a.w;
				foreach (var (dx, dz) in new[] { (1, 0), (0, 1) })
				{
					int ax = x - dx, az = z - dz, bx = x + dx, bz = z + dz;
					if (ax < 0 || az < 0 || bx >= a.w || bz >= a.h) continue;
					int p = az * a.w + ax, q = bz * a.w + bx;
					if (a.k.depth[p] > 0 && a.k.depth[q] > 0 && !a.sink[p] && !a.sink[q] && a.k.Notch(p) > 0 && a.k.Notch(q) > 0
						&& a.k.Notch(p) - a.k.depth[p] == a.k.Notch(q) - a.k.depth[q]) { n.Add(i); break; }
				}
			}
			return n;
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
			bool ok = ms < 40 && worst <= 0.001f && a.k.water.Max() / RM_LevelSolve.U <= 3;
			return (ok ? "OK: " : "BROKEN: ") + $"{ms:F2} ms/pulse over 100 pulses, {Total(a)} units in, worst imbalance {worst:F3}";
		}
	}
}
