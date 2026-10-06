// Approach B, phase 1 (design/RimMandrake/flowworks_offline_kernel_B.md): seeded random ACTION SEQUENCES over
// the existing Verse-free production math (RM_StockMath, RM_FireMath, RM_PumpMath, RM_ConversionMath,
// RM_PitTrapMath), checked against design invariants after every step. A failing sequence is shrunk by
// deleting actions and printed with its seed, so it replays exactly.
//
// WHAT IS REAL: every number comes from a production function. WHAT IS NOT: the composition — which cell
// touches which body, the order an adapter would call the functions in — is this file's own small model, not
// the game's grid walk. The grid transition itself is phase 2 (RM_FlowKernel, see FlowKernelFuzz.cs).

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.FlowWorks;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
	internal static class SequenceFuzz
	{
		public static long Cases;
		public static long Steps;

		// ── one action in a cell/body/tank sequence ───────────────────────────
		internal struct Act
		{
			public int kind, cell, arg;
			public override string ToString()
			{
				string[] names = { "Deepen", "FillIn", "Supply", "Pump", "Pour", "Burn", "Refill", "Rain" };
				return names[kind] + "(c" + cell + "," + arg + ")";
			}
		}

		private sealed class Body
		{
			public int fluid; public float vpt; public bool limitless; public int cells; public float cap, stock;
		}

		private sealed class World
		{
			public int[] D, F, Fl, acc, adj;      // per cell: depth, fill, fluid key (0 dry), burn accumulator, adjacent body
			public Body[] bodies;
			public int[] tank;                    // per fluid, tank units
			public float[] vptOf;                 // per fluid key
			public double[] ledger;               // per fluid: inputs - outputs, in fill-units
			public double[] start;
		}

		private static World Make(int seed)
		{
			var r = new Random(seed);
			int nf = 3;
			var w = new World();
			int n = r.Next(1, 7);
			w.D = new int[n]; w.F = new int[n]; w.Fl = new int[n]; w.acc = new int[n]; w.adj = new int[n];
			w.vptOf = new float[nf + 1];
			float[] vpts = { 0.5f, 1f, 1f, 2f, 3f };
			for (int f = 1; f <= nf; f++) w.vptOf[f] = vpts[r.Next(vpts.Length)];
			int nb = r.Next(1, 4);
			w.bodies = new Body[nb];
			for (int b = 0; b < nb; b++)
			{
				var body = new Body { fluid = r.Next(1, nf + 1), limitless = r.Next(4) == 0, cells = r.Next(1, 30) };
				body.vpt = w.vptOf[body.fluid];
				body.cap = RM_StockMath.BodyCapacity(body.cells, 5f, body.vpt, (float)(0.25 + r.NextDouble() * 2));
				body.stock = Math.Min(body.cap, (float)Math.Round(body.cap * r.NextDouble(), 2));
				w.bodies[b] = body;
			}
			for (int c = 0; c < n; c++) w.adj[c] = r.Next(nb);
			w.tank = new int[nf + 1];
			w.ledger = new double[nf + 1];
			w.start = Totals(w);
			return w;
		}

		private static double[] Totals(World w)
		{
			var t = new double[w.vptOf.Length];
			for (int c = 0; c < w.D.Length; c++) if (w.F[c] > 0) t[w.Fl[c]] += w.F[c] * w.vptOf[w.Fl[c]];
			foreach (var b in w.bodies) if (!b.limitless) t[b.fluid] += b.stock;
			for (int f = 1; f < t.Length; f++) t[f] += w.tank[f] / (double)RM_PumpMath.TankUnitsPerLevel * w.vptOf[f];
			return t;
		}

		/// <summary>Apply one action; throw on any invariant breach. Returns nothing: the world IS the result.</summary>
		private static void Step(World w, Act a, int seed)
		{
			int c = a.cell % w.D.Length;
			Body b = w.bodies[w.adj[c]];
			int fb = b.fluid;
			int oldFl = w.Fl[c];
			int oldF = w.F[c];
			switch (a.kind)
			{
				case 0: // Deepen: D only ever goes down, at most to superdeep
					w.D[c] = Math.Min(4, w.D[c] + 1);
					break;
				case 1: // FillIn: raise one level; what no longer fits goes back to the adjacent same-fluid body or overflows
				{
					if (w.D[c] == 0) break;
					int disp = RM_StockMath.DisplacedLevels(w.D[c], w.F[c]);
					Check(disp >= 0 && disp <= 1, "DisplacedLevels raising by ONE level displaces 0 or 1, got " + disp);
					w.D[c] -= 1;
					w.F[c] -= disp;
					int fl = w.Fl[c];
					if (w.F[c] == 0) w.Fl[c] = 0;
					if (disp > 0)
					{
						double vol = disp * w.vptOf[fl];
						if (fl == fb)
						{
							int take = RM_StockMath.CreditableLevels(b.limitless, b.stock, b.cap, disp, b.vpt);
							Check(take >= 0 && take <= disp, "CreditableLevels out of [0, offered]");
							float units = take * b.vpt;
							float acc = RM_StockMath.CreditAccepted(b.limitless, b.stock, b.cap, units);
							Check(Math.Abs(acc - units) < 1e-4, $"CreditableLevels promised {take} level(s) = {units} units but CreditAccepted took {acc}");
							if (!b.limitless) b.stock += acc;
							// what the body took stays in the system; the rest (and all of a limitless credit) leaves
							w.ledger[fl] -= vol - (b.limitless ? 0 : acc);
						}
						else w.ledger[fl] -= vol; // overflow: disclosed loss
					}
					break;
				}
				case 2: // Supply one level from the adjacent body
				{
					if (w.D[c] == 0 || RM_StockMath.CellRoom(w.D[c], w.F[c]) <= 0) break;
					if (!RM_StockMath.FluidsCompatible(w.F[c] > 0, FluidRef[w.Fl[c]], FluidRef[fb])) break;
					bool can = RM_StockMath.CanSupply(b.limitless, b.stock, b.vpt);
					bool deb = RM_StockMath.CanDebit(b.limitless, b.stock, b.vpt);
					Check(can == deb, "CanSupply and CanDebit disagree on the same unit (a stuttering source)");
					if (!deb) break;
					if (!b.limitless) b.stock -= b.vpt; else w.ledger[fb] += b.vpt; // limitless = declared external input
					if (w.F[c] == 0) w.Fl[c] = fb;
					w.F[c] += 1;
					break;
				}
				case 3: // Pump one level into the tank of its fluid
					if (w.F[c] == 0) break;
					w.tank[w.Fl[c]] += RM_PumpMath.TankUnitsPerLevel;
					w.F[c] -= 1;
					if (w.F[c] == 0) w.Fl[c] = 0;
					break;
				case 4: // Pour one level from a tank of fluid (arg % 3 + 1)
				{
					int f = a.arg % 3 + 1;
					if (w.tank[f] < RM_PumpMath.TankUnitsPerLevel || w.D[c] == 0 || w.F[c] >= w.D[c]) break;
					if (w.F[c] > 0 && w.Fl[c] != f) break;
					w.tank[f] -= RM_PumpMath.TankUnitsPerLevel;
					if (w.F[c] == 0) w.Fl[c] = f;
					w.F[c] += 1;
					break;
				}
				case 5: // Burn for arg*997 ticks
				{
					int tpl = RM_FireMath.TicksPerCanalLevel(0.05f + (a.arg % 7) * 0.3f);
					int before = w.acc[c];
					int add = (a.arg + 1) * 997;
					int due = RM_FireMath.LevelsDue(ref w.acc[c], add, tpl);
					Check(w.acc[c] >= 0 && w.acc[c] < tpl, "burn accumulator left outside [0, ticksPerLevel)");
					Check((long)due * tpl + w.acc[c] == (long)before + add, "LevelsDue lost or invented ticks");
					int burn = Math.Min(due, w.F[c]);
					if (burn > 0) { w.ledger[w.Fl[c]] -= burn * w.vptOf[w.Fl[c]]; w.F[c] -= burn; if (w.F[c] == 0) w.Fl[c] = 0; }
					break;
				}
				case 6: // Refill the adjacent body for one pulse of arg*250 ticks
				{
					if (b.limitless) break;
					var band = (RM_StockMath.SeasonBand)(a.arg % 4);
					float perDay = RM_StockMath.RefillPerDay(0.13f, b.cells, 3f, (a.arg % 5) / 4f, band, 1f);
					float gained = RM_StockMath.RefillForPulse(perDay, (a.arg % 40 + 1) * 250, 60000);
					Check(gained >= 0f, "negative refill");
					float old = b.stock;
					b.stock = RM_StockMath.ClampToCapacity(b.stock, gained, b.cap);
					Check(b.stock >= old - 1e-5f || old > b.cap, "refill lowered stock");
					w.ledger[fb] += b.stock - old; // declared external input: what actually landed
					break;
				}
				case 7: // Rain one level of water (fluid key 1) where dry or water
					if (w.D[c] == 0 || w.F[c] >= w.D[c] || (w.F[c] > 0 && w.Fl[c] != 1)) break;
					if (w.F[c] == 0) w.Fl[c] = 1;
					w.F[c] += 1;
					w.ledger[1] += w.vptOf[1];
					break;
			}
			// ── invariants ──
			for (int i = 0; i < w.D.Length; i++)
			{
				Check(0 <= w.F[i] && w.F[i] <= w.D[i] && w.D[i] <= 4, $"0<=F<=D<=4 broken at c{i}: D={w.D[i]} F={w.F[i]}");
				Check((w.F[i] > 0) == (w.Fl[i] != 0), $"c{i} wet without a fluid or dry with one (F={w.F[i]} fl={w.Fl[i]})");
			}
			Check(!(oldF > 0 && w.F[c] > 0 && oldFl != w.Fl[c]), $"wet c{c} changed fluid {oldFl}->{w.Fl[c]} (fluids never mix)");
			foreach (var body in w.bodies)
			{
				if (body.limitless) continue;
				Check(body.stock >= -1e-4f, "limited body stock went negative: an unaffordable debit");
				Check(body.stock <= body.cap + 1e-3f, $"stock {body.stock} above capacity {body.cap}");
				int sup = RM_StockMath.SupportedCells(body.stock, RM_StockMath.PerCellVolume(body.cap, body.cells));
				Check(sup >= 0 && sup <= body.cells, $"SupportedCells {sup} outside [0,{body.cells}] at stock {body.stock}/{body.cap}");
			}
			var t = Totals(w);
			for (int f = 1; f < t.Length; f++)
			{
				double want = w.start[f] + w.ledger[f];
				Check(Math.Abs(t[f] - want) < 1e-2, $"fluid {f} ledger: holds {t[f]:F3}, declared {want:F3}");
			}
		}

		// One shared object per fluid key, so FluidsCompatible's reference test means "same fluid".
		private static readonly string[] FluidRef = { null, "fluid1", "fluid2", "fluid3" };

		private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

		private static string RunSeq(int seed, List<Act> acts, bool restore)
		{
			try
			{
				var w = Make(seed);
				foreach (var a in acts) { Step(w, a, seed); Steps++; }
				if (restore)
				{
					// Restoration: filling every cell back in returns the ground to D=0, F=0 with the ledger balanced.
					for (int c = 0; c < w.D.Length; c++)
						for (int g = 0; g < 5 && w.D[c] > 0; g++) { Step(w, new Act { kind = 1, cell = c }, seed); Steps++; }
					for (int c = 0; c < w.D.Length; c++) Check(w.D[c] == 0 && w.F[c] == 0, $"c{c} not restored: D={w.D[c]} F={w.F[c]}");
				}
				return null;
			}
			catch (Exception ex) { return ex.Message; }
		}

		private static List<Act> Gen(Random r, int len)
		{
			var l = new List<Act>(len);
			for (int i = 0; i < len; i++) l.Add(new Act { kind = r.Next(8), cell = r.Next(6), arg = r.Next(1000) });
			return l;
		}

		/// <summary>Delta-debugging shrink: drop chunks, then single actions, while the failure persists.</summary>
		internal static List<T> Shrink<T>(List<T> acts, Func<List<T>, bool> fails)
		{
			var cur = new List<T>(acts);
			for (int chunk = Math.Max(1, cur.Count / 2); chunk >= 1; chunk /= 2)
			{
				bool progress = true;
				while (progress)
				{
					progress = false;
					for (int i = 0; i + chunk <= cur.Count; i++)
					{
						var trial = new List<T>(cur);
						trial.RemoveRange(i, chunk);
						if (fails(trial)) { cur = trial; progress = true; break; }
					}
				}
			}
			return cur;
		}

		/// <summary>The cell/body/tank sequence machine. Returns failures as "seed: msg | minimal sequence".</summary>
		public static List<string> Sequences(int n, int baseSeed)
		{
			var fails = new List<string>();
			for (int k = 0; k < n; k++)
			{
				int seed = baseSeed + k;
				var r = new Random(seed * 7919 + 1);
				var acts = Gen(r, r.Next(5, 80));
				Cases++;
				string err = RunSeq(seed, acts, true);
				if (err == null) continue;
				var min = Shrink(acts, t => RunSeq(seed, t, true) != null);
				fails.Add($"seed {seed}: {RunSeq(seed, min, true)} | {string.Join(" ", min)}");
				if (fails.Count >= 5) break;
			}
			return fails;
		}

		// ── order properties: the flow and recession orders must be STRICT orders, or a level can come back ──

		public static List<string> Orders(int n, int baseSeed)
		{
			var fails = new List<string>();
			var r = new Random(baseSeed);
			for (int k = 0; k < n; k++)
			{
				Cases++;
				int[] a = { r.Next(6), r.Next(6), r.Next(1, 5) }, b = { r.Next(6), r.Next(6), r.Next(1, 5) }, c = { r.Next(6), r.Next(6), r.Next(1, 5) };
				Func<int[], int[], bool> m = (x, y) => RM_StockMath.MayFlowBetween(x[0], x[1], x[2], y[0], y[1], y[2]);
				if (m(a, a)) fails.Add($"MayFlowBetween reflexive at ({string.Join(",", a)})");
				if (m(a, b) && m(b, a)) fails.Add($"MayFlowBetween symmetric pair ({string.Join(",", a)})<->({string.Join(",", b)}): a level can shuttle");
				if (m(a, b) && m(b, c) && m(c, a)) fails.Add($"MayFlowBetween 3-cycle ({string.Join(",", a)})->({string.Join(",", b)})->({string.Join(",", c)})");
				int[] p = { r.Next(9), r.Next(50), r.Next(100) }, q = { r.Next(9), r.Next(50), r.Next(100) };
				bool pq = RM_StockMath.PrefersCandidate(p[0], p[1], p[2], q[0], q[1], q[2]);
				bool qp = RM_StockMath.PrefersCandidate(q[0], q[1], q[2], p[0], p[1], p[2]);
				bool same = p[0] == q[0] && p[1] == q[1] && p[2] == q[2];
				if (!same && pq == qp) fails.Add($"PrefersCandidate not a strict total order on ({string.Join(",", p)}),({string.Join(",", q)})");
				int tpt = r.Next(1, 2000);
				int s = RM_StockMath.ViscosityStride(tpt);
				if (s < 1 || RM_StockMath.ViscosityStride(tpt + 1) < s) fails.Add($"ViscosityStride not >=1 and monotone at {tpt}");
				// over any window of s consecutive pulses a viscous donor moves exactly once
				long p0 = r.Next(100000);
				int moves = 0;
				for (long t = p0; t < p0 + s; t++) if (RM_StockMath.FluidMovesThisPulse(t, tpt)) moves++;
				if (moves != 1) fails.Add($"FluidMovesThisPulse moved {moves} times in one stride of {s} (tpt {tpt})");
				if (fails.Count >= 5) break;
			}
			return fails;
		}

		// ── converter: never spends input it lacks, never overfills output, recipe ratio exact ──

		public static List<string> Conversion(int n, int baseSeed)
		{
			var fails = new List<string>();
			for (int k = 0; k < n && fails.Count < 5; k++)
			{
				var r = new Random(baseSeed + k);
				Cases++;
				int inU = r.Next(0, 12), outU = r.Next(0, 12);
				float perTick = RM_ConversionMath.BudgetPerRareTick(r.Next(0, 200), (float)r.NextDouble() * 2, 1f, r.Next(3) == 0 ? 0f : 1f);
				float accrued = 0;
				int input = r.Next(0, 200), output = 0, cap = r.Next(-1, 150);
				long consumed = 0, produced = 0;
				int steps = r.Next(1, 500);
				for (int s = 0; s < steps; s++)
				{
					Steps++;
					if (r.Next(10) == 0) input += r.Next(0, 30);
					if (r.Next(15) == 0) output = Math.Max(0, output - r.Next(0, 40));
					accrued = RM_ConversionMath.CapAccrued(accrued + perTick, Math.Max(1, inU), perTick);
					int room = cap < 0 ? -1 : cap - output;
					int bn = RM_ConversionMath.Batches(accrued, inU, outU, input, room);
					if (bn < 0 || bn * inU > input || (room >= 0 && bn * outU > room) || bn * inU > accrued + 1e-3f)
					{
						fails.Add($"seed {baseSeed + k} step {s}: Batches={bn} in={inU} out={outU} have={input} room={room} accrued={accrued}");
						break;
					}
					input -= bn * inU; output += bn * outU; accrued -= bn * inU;
					consumed += bn * inU; produced += bn * outU;
					if (accrued < -1e-3f) { fails.Add($"seed {baseSeed + k}: accrued budget went negative ({accrued})"); break; }
				}
				if (inU > 0 && outU > 0 && consumed * outU != produced * inU) fails.Add($"seed {baseSeed + k}: recipe ratio broken {consumed}:{produced} vs {inU}:{outU}");
			}
			return fails;
		}

		// ── pit width: adding superdeep cells never narrows a pit; the measured width is the largest that fits ──

		public static List<string> PitWidth(int n, int baseSeed)
		{
			var fails = new List<string>();
			for (int k = 0; k < n && fails.Count < 5; k++)
			{
				var r = new Random(baseSeed + k);
				Cases++;
				int S = 8;
				var g = new bool[S, S];
				double density = 0.4 + r.NextDouble() * 0.6;
				for (int x = 0; x < S; x++) for (int z = 0; z < S; z++) g[x, z] = r.NextDouble() < density;
				Func<int, int, bool> sd = (x, z) => x >= 0 && z >= 0 && x < S && z < S && g[x, z];
				int cx = r.Next(S), cz = r.Next(S);
				int w = RM_PitTrapMath.MeasuredPitWidth(sd, cx, cz);
				if (w > 0 && !RM_PitTrapMath.PitWidthAt(sd, cx, cz, w)) fails.Add($"seed {baseSeed + k}: measured width {w} does not fit");
				if (w < RM_PitTrapMath.MaxWidth && RM_PitTrapMath.PitWidthAt(sd, cx, cz, w + 1)) fails.Add($"seed {baseSeed + k}: width {w + 1} also fits but measured {w}");
				int ax = r.Next(S), az = r.Next(S);
				g[ax, az] = true;
				int w2 = RM_PitTrapMath.MeasuredPitWidth(sd, cx, cz);
				if (w2 < w) fails.Add($"seed {baseSeed + k}: digging ({ax},{az}) narrowed the pit at ({cx},{cz}) from {w} to {w2}");
				Steps += 2;
			}
			return fails;
		}
	}
}
