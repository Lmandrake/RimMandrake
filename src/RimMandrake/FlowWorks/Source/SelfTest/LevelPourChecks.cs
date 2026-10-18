// PUMP_CANAL_FEED_FIX_ONE_NOTCH_ONLY, HOSE_LEFTOVER_FIX_NO_VANISHING_LITRES, CANAL_FILLIN_FIX_SHEET_WATER_DESTROYED (live day 2,
// Transient/fw_scenes/live_day2_report.md findings 1-3). Owner: "conservation of mass is true everywhere"; filling in "does not
// destroy liquid if there's a place for it to go". The PRODUCTION walk (RM_LevelPour.Spread, the one the excavation's pour,
// hose drain and fill-in displacement call) driven over the PRODUCTION exact kernel at the shipped flags: a pump into a canal
// that already holds a sheet keeps delivering until the canal is brim-full or the pond is dry (live: stopped at 1,000 L),
// a hose's leftover poured onto a sheet lands in the canal (live: 973 L vanished), a sheet filled in is displaced, not
// destroyed (live: 91 L), and the one sanctioned loss (S5.D, a full run with nowhere to go) is exactly what overflows.
// LevelOps is also the kernel side of the oracle differential's "exactops" mode (selftest_flowworks_kernel_oracle.py), whose
// Python twin is northstar/level_water.py's spread / pour / fill_in.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
	/// <summary>The excavation's pour and fill-in, on plain arrays (ArrayWorld), through the production RM_LevelPour.</summary>
	internal static class LevelOps
	{
		private const int U = RM_LevelSolve.U;

		private static void EnsurePart(ArrayWorld w)
		{
			if (w.k.part == null || w.k.part.Length != w.w * w.h) w.k.part = new ushort[w.w * w.h];
		}

		private static long Room(ArrayWorld w, int i)
		{
			if (w.k.depth[i] == 0) return 0;
			long r = w.k.depth[i] * (long)U - w.k.WaterOf(i);
			return r > 0 ? r : 0;
		}

		/// <summary>Pour up to <paramref name="dl"/> at dug square <paramref name="idx"/> (the square, then the canal it joins,
		/// nearest first); returns what was placed (0 on an undug square). The production TryPourDl is all-or-nothing on the
		/// amount the pump asked for after reading PourRoomDl, which is this same plan.</summary>
		public static long Pour(ArrayWorld w, int idx, long dl)
		{
			if (idx < 0 || w.k.depth[idx] == 0 || dl <= 0) return 0;
			EnsurePart(w);
			var credits = new List<KeyValuePair<int, long>>();
			long placed = RM_LevelPour.Spread(idx, dl, true, w.k.Cardinal, i => w.k.depth[i] != 0 && !w.k.IsSealed(i), null,
				i => Room(w, i), RM_LevelPour.PourWalkCap, credits, null);
			foreach (var cr in credits)
			{
				w.k.SetWaterOf(cr.Key, w.k.WaterOf(cr.Key) + cr.Value);
				if (w.cellFluid[cr.Key] == null) w.cellFluid[cr.Key] = w.activeFluid;
			}
			return placed;
		}

		/// <summary>Raise <paramref name="idx"/> one notch (RM_MapComponent_Excavation.FillIn's decilitre rule): what no longer
		/// fits is displaced over the canal (phase 1), then into the ponds the walk touched (phase 2, up to capacity); returns
		/// the dL destroyed (the disclosed overflow).</summary>
		public static long FillIn(ArrayWorld w, int idx)
		{
			if (idx < 0 || w.k.depth[idx] == 0) return 0;
			EnsurePart(w);
			int d = w.k.depth[idx], newD = d - 1;
			long water = Math.Min(w.k.WaterOf(idx), d * (long)U);
			long kept = RM_LevelPour.KeptOnFillIn(water, newD, newD == 0);
			long displaced = water - kept;
			w.k.depth[idx] = (byte)newD;
			w.k.SetWaterOf(idx, kept);
			if (kept == 0) w.cellFluid[idx] = null;
			if (displaced <= 0) return 0;
			var credits = new List<KeyValuePair<int, long>>();
			var sources = new List<int>();
			long remaining = displaced - RM_LevelPour.Spread(idx, displaced, false, w.k.Cardinal,
				i => (w.k.depth[i] != 0 || w.k.IsSource(i)) && !w.k.IsSealed(i), i => w.k.IsSource(i), i => Room(w, i),
				w.w * w.h, credits, sources);
			foreach (var cr in credits)
			{
				w.k.SetWaterOf(cr.Key, w.k.WaterOf(cr.Key) + cr.Value);
				if (w.cellFluid[cr.Key] == null) w.cellFluid[cr.Key] = w.activeFluid;
			}
			foreach (int s in sources)
			{
				if (remaining <= 0) break;
				var b = w.BodyAt(s);
				if (b == null) continue;
				if (b.limitless) { remaining = 0; break; }
				long cap = U * (long)b.cells.Where(c => w.k.depth[c] == 0).Sum(c => w.BedAt(c));
				long take = Math.Max(0, Math.Min(remaining, cap - b.Dl()));
				b.SetDl(b.Dl() + take);
				remaining -= take;
			}
			return remaining;
		}

		/// <summary>The pump's world-to-world step (Building_LiquidPump.TryDraw, exact-level): up to one level, what the pond
		/// holds and what the canal takes at <paramref name="outlet"/>. Returns the dL moved.</summary>
		public static long PumpStep(ArrayWorld w, ArrayWorld.Body src, int outlet)
		{
			long avail = src.limitless ? U : src.Dl();
			long room = RM_LevelPour.Spread(outlet, U, true, w.k.Cardinal, i => w.k.depth[i] != 0 && !w.k.IsSealed(i), null,
				i => Room(w, i), RM_LevelPour.PourWalkCap, null, null);
			long amt = Math.Min(U, Math.Min(avail, room));
			if (amt <= 0) return 0;
			if (!src.limitless) src.SetDl(src.Dl() - amt);
			long placed = Pour(w, outlet, amt);
			if (placed != amt) throw new Exception("the pour placed " + placed + " of the " + amt + " its plan promised");
			return amt;
		}
	}

	internal static class LevelPourChecks
	{
		private const int U = RM_LevelSolve.U;

		private static void Assert(bool ok, string msg)
		{
			if (!ok) throw new Exception(msg);
		}

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

		/// <summary>An enclosed pond of <paramref name="pondSquares"/> squares (bed 4) at row 2 from x=1, holding
		/// <paramref name="levels"/>; a canal of <paramref name="len"/> squares, <paramref name="depth"/> deep, from x0 on row 2.</summary>
		private static (ArrayWorld w, List<int> canal, ArrayWorld.Body body) Scene(int pondSquares, float levels, int x0, int len, int depth)
		{
			var w = World(24, 5);
			var pond = Enumerable.Range(1, pondSquares).Select(x => 2 * 24 + x).ToList();
			var body = w.AddBody(false, levels, pond);
			foreach (int c in pond) w.bed[c] = 4;
			var canal = Enumerable.Range(x0, len).Select(x => 2 * 24 + x).ToList();
			foreach (int c in canal) w.k.depth[c] = (byte)depth;
			return (w, canal, body);
		}

		public static void Run(Action<string, Action> Case)
		{
			Case("LevelPour_spread_fills_the_square_then_the_canal_nearest_first", () =>
			{
				var w = World(8, 3);
				var canal = Enumerable.Range(0, 6).Select(x => 1 * 8 + x).ToList();
				foreach (int c in canal) { w.k.depth[c] = 1; }
				w.k.part = new ushort[24];
				foreach (int c in canal) w.k.SetWaterOf(c, 1667);   // live S3: 1,000 L over 6 squares
				var credits = new List<KeyValuePair<int, long>>();
				long placed = RM_LevelPour.Spread(canal[0], U, true, w.k.Cardinal, i => w.k.depth[i] != 0, null,
					i => w.k.depth[i] * (long)U - w.k.WaterOf(i), RM_LevelPour.PourWalkCap, credits, null);
				Assert(placed == U, "a whole level fits the canal (6 x 8,333 dL of room): " + placed);
				Assert(credits.Count == 2 && credits[0].Key == canal[0] && credits[0].Value == U - 1667 && credits[1].Key == canal[1] && credits[1].Value == 1667,
					"the square first (8,333), then its neighbour (1,667): " + string.Join(" ", credits.Select(c => c.Key + ":" + c.Value)));
				// can-fail: the old rule (a whole notch of room in ONE square) refuses every square of this canal
				Assert(canal.All(c => (w.k.depth[c] * (long)U - w.k.WaterOf(c)) / U == 0), "under the whole-notch rule no square has room: the live stall");
				Assert(RM_LevelPour.Spread(canal[0], U, false, w.k.Cardinal, i => w.k.depth[i] != 0, null, i => 0, 1024, null, null) == 0, "no room anywhere: nothing placed");
				Assert(RM_LevelPour.KeptOnFillIn(12000, 1, false) == U && RM_LevelPour.KeptOnFillIn(900, 1, false) == 900
					&& RM_LevelPour.KeptOnFillIn(900, 0, true) == 0, "fill-in keeps what fits under the new brim, nothing at the surface");
			});

			Case("LevelPour_S3_pump_fills_the_canal_to_the_brim_not_one_notch", () =>
			{
				// S3: an enclosed 12-square pond (48 levels) -> pump -> a 6-square, 0.5 m canal touching no water.
				var (w, canal, body) = Scene(12, 48f, 16, 6, 1);
				long t0 = Total(w), moved = 0;
				for (int cycle = 0; cycle < 40; cycle++)
				{
					moved += LevelOps.PumpStep(w, body, canal[0]);
					w.Pulse(canal);
					Assert(Total(w) == t0 && w.k.worstImbalance == 0, "conserved to the dL at cycle " + cycle);
				}
				Assert(moved == 6L * U, "the pump delivered 6,000 L (the canal's whole volume), not 1,000: " + moved);
				Assert(canal.All(c => w.k.WaterOf(c) == U), "all six squares at 0.5 m: " + string.Join(" ", canal.Select(c => w.k.WaterOf(c))));
				Assert(body.Dl() == 42L * U, "the pond paid exactly 6,000 L: " + body.Dl());
			});

			Case("LevelPour_S5G_pump_empties_a_one_square_pond_into_six_level_squares", () =>
			{
				// S5.G redrawn under level water: 4,000 L over six 0.5 m squares = 0.333 m each, one surface; the pond dry.
				var (w, canal, body) = Scene(1, 4f, 3, 6, 1);
				long t0 = Total(w), moved = 0;
				for (int cycle = 0; cycle < 30; cycle++)
				{
					moved += LevelOps.PumpStep(w, body, canal[0]);
					w.Pulse(canal);
					Assert(Total(w) == t0, "pond + canal = 4,000 L at cycle " + cycle);
				}
				Assert(moved == 4L * U && body.Dl() == 0, "the pond empties: moved " + moved + ", left " + body.Dl());
				long lo = canal.Min(c => w.k.WaterOf(c)), hi = canal.Max(c => w.k.WaterOf(c));
				Assert(hi - lo <= 1 && canal.Sum(c => w.k.WaterOf(c)) == 4L * U, "one surface over six squares (6,666/6,667 dL): " + lo + ".." + hi);
				Assert(LevelExactChecks.WorstGap(w, out _) < 0.001, "surface gap under 1 mm");
			});

			Case("LevelPour_hose_leftover_on_a_sheet_lands_in_the_canal", () =>
			{
				// live S3: the hose drains 9,734 units (973 L) onto canal cell 1, which holds a sheet: it must land, never vanish
				var (w, canal, body) = Scene(12, 48f, 16, 6, 1);
				w.k.part = new ushort[w.w * w.h];
				foreach (int c in canal) w.k.SetWaterOf(c, 1667);
				long t0 = Total(w);
				long placed = LevelOps.Pour(w, canal[0], 9734);
				Assert(placed == 9734 && Total(w) == t0 + 9734, "all 973.4 L placed: " + placed);
				for (int p = 0; p < 10; p++) w.Pulse(canal);
				Assert(Total(w) == t0 + 9734 && LevelExactChecks.WorstGap(w, out _) < 0.001, "conserved and level after the pulses");
			});

			Case("LevelPour_S5C_filling_in_a_sheet_displaces_it_nothing_destroyed", () =>
			{
				// S5.B then C: a 1-square pond (4,000 L) and a 10-square canal settle to 4.5 cm; fill in canal cell 1 (91 L).
				var (w, canal, body) = Scene(1, 4f, 2, 10, 1);
				for (int p = 0; p < 200; p++) w.Pulse(canal);
				long cell1 = w.k.WaterOf(canal[0]);
				Assert(cell1 > 800 && cell1 < 1000, "cell 1 holds the 4.5 cm sheet (about 910 dL): " + cell1);
				long t0 = Total(w);
				long destroyed = LevelOps.FillIn(w, canal[0]);
				Assert(destroyed == 0, "nothing destroyed (live: 91 L were): " + destroyed);
				Assert(Total(w) == t0 && t0 == 4L * U, "canal and pond still hold 4,000 L");
				for (int p = 0; p < 60; p++) w.Pulse(canal);
				Assert(Total(w) == 4L * U, "and after 60 more pulses");
			});

			Case("LevelPour_S5D_full_run_with_nowhere_to_go_loses_exactly_1000_L", () =>
			{
				var w = World(8, 3);
				var run = Enumerable.Range(2, 3).Select(x => 1 * 8 + x).ToList();
				w.k.part = new ushort[24];
				foreach (int c in run) { w.k.depth[c] = 1; w.k.SetWaterOf(c, U); w.cellFluid[c] = w.activeFluid; }
				long destroyed = LevelOps.FillIn(w, run[1]);
				Assert(destroyed == U, "exactly 1,000 L destroyed (the sanctioned, announced overflow): " + destroyed);
				Assert(w.k.WaterOf(run[0]) == U && w.k.WaterOf(run[2]) == U && w.k.depth[run[1]] == 0, "the ends keep theirs");
				// a deeper square raised one notch keeps what fits and displaces only the rest
				var v = World(8, 3);
				v.k.part = new ushort[24];
				int a = 9, b = 10;
				v.k.depth[a] = 2; v.k.SetWaterOf(a, 12000); v.cellFluid[a] = v.activeFluid;
				v.k.depth[b] = 1;
				long lost = LevelOps.FillIn(v, a);
				Assert(lost == 0 && v.k.WaterOf(a) == U && v.k.WaterOf(b) == 2000, "2 -> 1 notch: keeps 10,000, 2,000 dL go next door: "
					+ v.k.WaterOf(a) + " / " + v.k.WaterOf(b));
			});

			Case("LevelPour_production_sites_use_the_decilitre_walk", () =>
			{
				string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
				string sp = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidSpill.cs"));
				string pump = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
				RiverSwitchFlipChecks.Has(ex, @"return RM_LevelPour\.Spread\(start, want, true, NeighbourIndex, Joins, null, Room, RM_LevelPour\.PourWalkCap, credits, null\);", "the pour walks the canal");
				RiverSwitchFlipChecks.Has(ex, @"if \(LevelExact\) \{ return TryPourDl\(c, fluid, RM_LevelSolve\.U\); \}", "a whole-level pour spreads under exact-level water");
				RiverSwitchFlipChecks.Has(pump, @"int amt = \(int\)System\.Math\.Min\(units, System\.Math\.Min\(avail, room\)\);", "the pump moves what the source holds and the canal takes");
				Assert(!sp.Contains("the liquid left the network anyway"), "no spill leaves the ledger unannounced any more");
				RiverSwitchFlipChecks.Has(sp, @"RM_SuperdeepTrap\.EngineOf\(map\)\?\.ReportLiquidLost\(cell, rest, ""Spilled """, "the only loss is announced with its amount");
				Assert(!ex.Contains("partLost"), "a fill-in no longer destroys a sheet's part-notch");
			});

			Case("LevelPour_whole_level_pour_is_all_or_nothing", () =>
			{
				// review day 3: TryPourDl with exact-level water off poured level by level and returned false after a partial
				// pour; the room for every level is now checked before its one write.
				string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
				RiverSwitchFlipChecks.Has(ex, @"if \(!CanPourLevelWhole\(c, fluid\) \|\| RoomNotches\(map\.cellIndices\.CellToIndex\(c\)\) < levels\) \{ return false; \} return TrySetDriverFill\(c, FillAt\(c\) \+ \(int\)levels, fluid\);",
					"room for every level checked before the single write");
				Assert(!ex.Contains("checked per level before each write"), "the per-level partial pour is gone");
			});
		}
	}
}
