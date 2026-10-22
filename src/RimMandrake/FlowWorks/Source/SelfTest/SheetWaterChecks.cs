// CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED, Stage 0: offline checks of the sheet-water kernel (RM_SheetMath.cs, the
// production file). design/RimMandrake/canal_overflow_flooding_2026-10-21.md §4 Stage 0 tests 1-9 as amended by §6, plus
// the owner's §5 answers that the kernel carries as data (D2 gravity source, D3 crop week, D4 doors leak, D8 sheets lie
// level, D9 retention and relief are physical, D10 own ice tier and a lowered cap deletes nothing).
// NOT proven here: anything about the game (temp terrain, pictures, path cost, the engine pulse) — Stage 1.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using RimMandrake.FlowWorks;
using static RimMandrake.FlowWorks.RM_SheetMath;

namespace RimMandrake.FlowWorks.SelfTest
{
	internal static class SheetWaterChecks
	{
		private static void Assert(bool ok, string msg)
		{
			if (!ok) throw new Exception(msg);
		}

		private const byte Water = 1, Chemfuel = 2;

		private static SpillOffer Offer(int amount, byte fluid, Source src, params int[] lips) =>
			new SpillOffer { AmountDl = amount, Fluid = fluid, From = src, LipNearestFirst = lips };

		private static int Idx(World w, int x, int z) => z * w.W + x;

		private static void Ring(World w, int x0, int z0, int x1, int z1, Kind k)
		{
			for (int x = x0; x <= x1; x++) { w.Kinds[Idx(w, x, z0)] = k; w.Kinds[Idx(w, x, z1)] = k; }
			for (int z = z0; z <= z1; z++) { w.Kinds[Idx(w, x0, z)] = k; w.Kinds[Idx(w, x1, z)] = k; }
		}

		private static long Inside(State s, World w, int x0, int z0, int x1, int z1)
		{
			long t = 0;
			for (int x = x0; x <= x1; x++) for (int z = z0; z <= z1; z++) t += s.Dl[Idx(w, x, z)];
			return t;
		}

		private static void Run(State s, World w, Params p, int pulses, PulseReport rep = null)
		{
			for (int i = 0; i < pulses; i++)
			{
				Pulse(s, w, p, rep);
				Assert(s.LedgerCloses, $"ledger open after pulse {s.Pulse}: in {s.TotalIn} vs standing {s.Standing} + out {s.TotalOut}");
			}
		}

		/// <summary>A random small world: walls, doors, grates, receivers (some full), a sink, soak and evaporation.</summary>
		private static World RandomWorld(Random r, int W, int H, bool losses)
		{
			var w = new World(W, H);
			for (int c = 0; c < W * H; c++)
			{
				int roll = r.Next(100);
				w.Kinds[c] = roll < 10 ? Kind.Blocked : roll < 13 ? Kind.Door : roll < 15 ? Kind.Grate
					: roll < 20 ? Kind.Receiver : roll < 21 ? Kind.Sink : Kind.Open;
				if (w.Kinds[c] == Kind.Receiver) w.RoomDl[c] = r.Next(3) == 0 ? 0 : r.Next(20000);
				if (w.Kinds[c] == Kind.Sink) w.BodyFluid[c] = Water;
				if (losses) { w.SoakMilliDl[c] = r.Next(0, 3000); w.EvapMilliDl[c] = r.Next(0, 800); }
			}
			w.Fluids[Chemfuel] = new FluidRule { InfiltrationPermille = 0, EvaporationPermille = 3000 };
			return w;
		}

		public static void Run(Action<string, Action> Case)
		{
			Case("Sheet_units_one_cm_is_200_dL_and_a_week_is_1680_pulses", () =>
			{
				Assert(DlPerCm == 200, "1 cm over one 2 m² square must be 20 L = 200 dL, got " + DlPerCm);
				Assert(new Params().CropKillPulses == 1680, "D3: one week at a 250-tick pulse must be 1680 pulses");
			});

			// test 1: conservation over 10k pulses with every exit live
			Case("Sheet_conserves_to_the_dL_over_10k_pulses_with_every_exit", () =>
			{
				var r = new Random(1021);
				var w = RandomWorld(r, 24, 24, true);
				var p = new Params { MaxWetCells = 300 };
				var s = new State(24, 24, 0xC0FFEEu);
				long offered = 0, accepted = 0;
				for (int t = 0; t < 10000; t++)
				{
					if (t % 7 == 0 && t < 8000)
					{
						var offers = new List<SpillOffer>();
						for (int k = 0; k < 3; k++)
						{
							int a = r.Next(1, 6000);
							offers.Add(Offer(a, r.Next(4) == 0 ? Chemfuel : Water, (Source)r.Next(SourceCount), r.Next(576), r.Next(576)));
							offered += a;
						}
						foreach (int a in ResolveSpills(s, w, p, offers)) accepted += a;
					}
					Pulse(s, w, p, null);
					Assert(s.LedgerCloses, $"pulse {t}: in {s.TotalIn} != standing {s.Standing} + out {s.TotalOut}");
					foreach (int c in s.Occ) Assert(s.Dl[c] > 0 && s.Dl[c] <= p.SheetCapDl, $"cell {c} holds {s.Dl[c]}");
				}
				Assert(accepted == s.TotalIn, "accepted offers must be exactly the In ledger");
				Assert(accepted > 0 && accepted < offered, $"the scene must both accept and refuse (accepted {accepted} of {offered})");
				Assert(s.Returned > 0 && s.JoinedLake > 0 && s.Soaked > 0 && s.Evaporated > 0,
					$"every exit should have run: returned {s.Returned} lake {s.JoinedLake} soaked {s.Soaked} evap {s.Evaporated}");
			});

			// test 2: finite extent (§6 item 6): growth stops, wet count ≤ ⌈V/q_min⌉
			Case("Sheet_extent_is_finite_and_bounded_by_V_over_qmin", () =>
			{
				var w = new World(80, 80);
				var p = new Params();
				var s = new State(80, 80, 7u);
				int V = 40000; // 2 m³: 0.2 m on ten squares
				int c0 = Idx(w, 40, 40);
				ResolveSpills(s, w, p, new[] { Offer(9000, Water, Source.Pump, c0), Offer(9000, Water, Source.Pump, c0 + 1),
					Offer(9000, Water, Source.Pump, c0 - 1), Offer(9000, Water, Source.Pump, c0 + 80), Offer(4000, Water, Source.Pump, c0 - 80) });
				Assert(s.TotalIn == V, "the whole spill should be placed, got " + s.TotalIn);
				Run(s, w, p, 400);
				int wet = s.WetCount;
				var snap = (int[])s.Dl.Clone();
				Run(s, w, p, 100);
				for (int c = 0; c < snap.Length; c++) Assert(snap[c] == s.Dl[c], $"cell {c} still moving after settling ({snap[c]} -> {s.Dl[c]})");
				int bound = (V + p.MinReceiveDl - 1) / p.MinReceiveDl;
				Assert(wet <= bound, $"wet {wet} > ⌈V/q_min⌉ {bound}");
				Assert(wet > 50, $"a 2 m³ spill on open flat ground should spread; wet {wet}");
				Assert(s.Standing == V, "no exits on this ground: all of it still stands");
			});

			// test 3: order independence
			Case("Sheet_offer_order_does_not_change_the_outcome", () =>
			{
				var r = new Random(3);
				var w = RandomWorld(r, 20, 20, true);
				var p = new Params { MaxWetCells = 60 };
				var offers = new List<SpillOffer>();
				for (int k = 0; k < 12; k++) offers.Add(Offer(r.Next(100, 9000), k % 3 == 0 ? Chemfuel : Water, (Source)(k % SourceCount), r.Next(400), r.Next(400), r.Next(400)));
				ulong first = 0;
				for (int trial = 0; trial < 6; trial++)
				{
					var sh = new List<SpillOffer>(offers);
					var rr = new Random(trial * 977 + 1);
					for (int i = sh.Count - 1; i > 0; i--) { int j = rr.Next(i + 1); (sh[i], sh[j]) = (sh[j], sh[i]); }
					var s = new State(20, 20, 99u);
					var wc = w.Clone();
					ResolveSpills(s, wc, p, sh);
					Run(s, wc, p, 200);
					ulong h = Hash(s);
					if (trial == 0) first = h;
					else Assert(h == first, $"shuffle {trial} gave a different state");
				}
			});

			// test 4: walls hold, grates pass, doors leak slowly (owner D4: "Leak slowly under them")
			Case("Sheet_walls_hold_grates_pass_doors_leak_slowly", () =>
			{
				long OutsideAfter(Kind gap, int pulses, out long inside)
				{
					var w = new World(30, 30);
					Ring(w, 10, 10, 19, 19, Kind.Blocked);
					if (gap != Kind.Blocked) w.Kinds[Idx(w, 19, 15)] = gap;
					var p = new Params();
					var s = new State(30, 30, 5u);
					var lips = new List<int>();
					for (int x = 11; x <= 18; x++) for (int z = 11; z <= 18; z++) lips.Add(Idx(w, x, z));
					foreach (int c in lips) ResolveSpills(s, w, p, new[] { Offer(4000, Water, Source.Pump, c) }); // 20 cm deep: a pool
					Run(s, w, p, pulses);
					inside = Inside(s, w, 11, 11, 18, 18);
					return s.Standing - inside - Inside(s, w, 19, 15, 19, 15);
				}
				long wallOut = OutsideAfter(Kind.Blocked, 300, out long wallIn);
				long grateOut = OutsideAfter(Kind.Grate, 20, out _);
				long doorOut20 = OutsideAfter(Kind.Door, 20, out long doorIn20);
				long doorOut300 = OutsideAfter(Kind.Door, 300, out long doorIn300);
				Assert(wallOut == 0 && wallIn == 64 * 4000, $"a wall ring must hold every dL (outside {wallOut})");
				Assert(grateOut > 0, "a grate must pass water");
				Assert(doorOut20 > 0, "D4: a door leaks; it does not block");
				Assert(doorOut20 * 4 < grateOut, $"D4: a door leaks SLOWLY (door {doorOut20} vs grate {grateOut} after 20 pulses)");
				Assert(doorOut300 > doorOut20 && doorIn300 < doorIn20, "the door keeps leaking and the pool keeps falling");
			});

			// test 5: return to channel, and a full channel refuses
			// micro-relief (±1 cm, D9: physical) leaves puddles in its dips: with relief OFF every dL of mobile water
			// must run back; with it ON, what stays is bounded by retention + the dip depth
			foreach (int relief in new[] { 0, DlPerCm })
				Case("Sheet_runs_back_into_the_canal_when_it_is_drawn_down_relief_" + relief, () =>
				{
					var w = new World(40, 20);
					for (int x = 0; x < 40; x++) w.Kinds[Idx(w, x, 10)] = Kind.Receiver; // a canal row, brim-full (room 0)
					var p = new Params { ReliefDl = relief };
					var s = new State(40, 20, 11u);
					ResolveSpills(s, w, p, new[] { Offer(30000, Water, Source.Pump, Idx(w, 20, 11), Idx(w, 21, 11), Idx(w, 19, 11)) });
					Run(s, w, p, 60);
					Assert(s.Returned == 0, "a brim-full canal takes nothing back");
					Assert(s.Standing == 30000, "and nothing was lost");
					for (int x = 0; x < 40; x++) w.RoomDl[Idx(w, x, 10)] = 5000; // the pump stops and the canal is drawn down
					var rep = new PulseReport();
					long credited = 0;
					for (int i = 0; i < 400; i++) { Pulse(s, w, p, rep); foreach (var (_, dl) in rep.Returned) credited += dl; Assert(s.LedgerCloses, "ledger"); }
					Assert(credited == s.Returned, "every returned dL is reported for the engine to credit");
					// a flux needs a 2 dL head (1 dL could only swap levels and ping-pong), so diffusion alone left a
					// 1-dL-per-square staircase toward the drain; D8 levelling removes it (measured 0 at both reliefs,
					// 2026-10-22); the 1% bound stays as the gross-regression line
					long residue = 0;
					foreach (int c in s.Occ) residue += Math.Max(0, s.Dl[c] - p.RetentionDl - 2 * relief);
					Console.WriteLine($"      relief {relief}: returned {s.Returned} of 30000, held {s.Standing} on {s.WetCount} squares, residue {residue} dL");
					Assert(residue * 100 <= 30000, $"mobile water stranded above retention + dips: {residue} dL");
					Assert(s.Returned + s.Standing == 30000, "conserved");
					// everything that stays is held moisture (retention), a relief dip, or the residue; the rest ran back
					Assert(s.Returned > 0 && s.Standing <= (long)s.WetCount * (p.RetentionDl + 2 * relief) + residue,
						$"only held moisture may stay (held {s.Standing} on {s.WetCount} squares)");
				});

			// test 6: back-pressure, caps never delete
			Case("Sheet_full_caps_refuse_back_to_the_inflow_and_lowering_a_cap_deletes_nothing", () =>
			{
				var w = new World(30, 30);
				var p = new Params { MaxWetCells = 10, SheetCapDl = 2000 };
				var s = new State(30, 30, 3u);
				int[] acc = ResolveSpills(s, w, p, new[] { Offer(100000, Water, Source.Pump, Idx(w, 15, 15), Idx(w, 16, 15), Idx(w, 14, 15)) });
				Assert(acc[0] == 6000, "three lips × 2000 dL cap = 6000 accepted, got " + acc[0]);
				Run(s, w, p, 200);
				Assert(s.WetCount <= 10, "wet cap " + s.WetCount);
				int[] acc2 = ResolveSpills(s, w, p, new[] { Offer(100000, Water, Source.Rain, Idx(w, 2, 2)) });
				Assert(acc2[0] == 0, "a new dry lip past the wet cap is refused");
				p.MaxWetCells = 3; p.SheetCapDl = 500;
				long before = s.Standing;
				Run(s, w, p, 50);
				Assert(s.Standing == before && s.WetCount >= 3, "lowering a cap must never delete water");
				Assert(s.TotalOut == 0, "and nothing left by an exit");
			});

			// test 7: hysteresis
			Case("Sheet_tier_hysteresis_does_not_flap", () =>
			{
				var p = new Params();
				var t = Tier.Film; int flips = 0;
				for (int i = 0; i < 100; i++)
				{
					var n = NextTier(t, i % 2 == 0 ? 610 : 450, p);
					if (n != t) flips++;
					t = n;
				}
				Assert(flips == 1 && t == Tier.Sheet, "610/450 around the 600 up / 400 down band flips once, got " + flips);
				Assert(NextTier(Tier.Sheet, 399, p) == Tier.Film && NextTier(Tier.Film, 3000, p) == Tier.Pool
					&& NextTier(Tier.Pool, 2700, p) == Tier.Pool && NextTier(Tier.Pool, 2500, p) == Tier.Sheet
					&& NextTier(Tier.Pool, 0, p) == Tier.None, "tier thresholds");
			});

			// test 8: bench (provisional 1 ms target, §6 item 12; only a gross regression fails here)
			Case("Sheet_bench_250x250_4000_wet_three_sweeps", () =>
			{
				var w = new World(250, 250);
				var p = new Params();
				var s = new State(250, 250, 42u);
				var offers = new List<SpillOffer>();
				for (int k = 0; k < 40; k++) offers.Add(Offer(30000, Water, Source.Pump, Idx(w, 20 + (k % 8) * 28, 20 + (k / 8) * 45)));
				for (int i = 0; i < 25; i++) { ResolveSpills(s, w, p, offers); Pulse(s, w, p, null); }
				for (int i = 0; s.WetCount < 3500 && i < 400; i++) Pulse(s, w, p, null);
				int wet = s.WetCount;
				var sw = Stopwatch.StartNew();
				const int N = 50;
				for (int i = 0; i < N; i++) Pulse(s, w, p, null);
				double ms = sw.Elapsed.TotalMilliseconds / N;
				Console.WriteLine($"      sheet bench: {wet} wet cells, {ms:F3} ms per pulse (target 1 ms, provisional)");
				Assert(wet >= 3000, "bench scene too small: " + wet);
				Assert(ms < 50, $"{ms:F2} ms per pulse is a gross regression");
			});

			// test 9: save round-trip AND continuation (§6 item 4)
			Case("Sheet_save_load_continuation_matches_the_uninterrupted_run", () =>
			{
				var r = new Random(9);
				var w0 = RandomWorld(r, 22, 22, true);
				var p = new Params { MaxWetCells = 200, CropKillPulses = 40 };
				var a = new State(22, 22, 1234u); var wa = w0.Clone();
				var b = new State(22, 22, 1234u); var wb = w0.Clone();
				var feed = new List<SpillOffer[]>();
				for (int t = 0; t < 400; t++)
					feed.Add(t % 5 == 0 && t < 300 ? new[] { Offer(r.Next(500, 8000), t % 15 == 0 ? Chemfuel : Water, Source.Gravity, r.Next(484), r.Next(484)) } : new SpillOffer[0]);
				for (int t = 0; t < 400; t++)
				{
					if (t == 173)
					{
						byte[] bytes = Save(b);
						var b2 = Load(bytes);
						Assert(Hash(b2) == Hash(b), "round-trip hash");
						b = b2;
					}
					int[] x = ResolveSpills(a, wa, p, feed[t]), y = ResolveSpills(b, wb, p, feed[t]);
					Assert(x.Length == y.Length && (x.Length == 0 || x[0] == y[0]), $"pulse {t}: accepted differs");
					Pulse(a, wa, p, null); Pulse(b, wb, p, null);
					Assert(Hash(a) == Hash(b), $"pulse {t}: the save/load continuation diverged");
				}
				Assert(a.In[(int)Source.Gravity] > 0, "D2: a gravity feed is an inflow like any other");
				for (int c = 0; c < wa.RoomDl.Length; c++) Assert(wa.RoomDl[c] == wb.RoomDl[c], "receiver credits diverged");
			});

			// D3: crop dies only after a week of standing overflow; film irrigates and never kills
			Case("Sheet_crops_die_after_a_week_of_standing_overflow_film_irrigates", () =>
			{
				var w = new World(12, 12);
				Ring(w, 2, 2, 6, 6, Kind.Blocked);         // a walled yard: 3×3 inside, held at sheet depth
				for (int c = 0; c < 144; c++) w.SoakMilliDl[c] = 1000; // 1 dL a pulse soaks (and irrigates)
				var p = new Params();
				var s = new State(12, 12, 8u);
				var yard = new List<int>();
				for (int x = 3; x <= 5; x++) for (int z = 3; z <= 5; z++) yard.Add(Idx(w, x, z));
				foreach (int c in yard) ResolveSpills(s, w, p, new[] { Offer(5000, Water, Source.Rain, c) }); // 25 cm, plenty for a week of 1 dL
				int film = Idx(w, 9, 9);
				ResolveSpills(s, w, p, new[] { Offer(150, Water, Source.Rain, film) }); // under retention: held moisture, film tier
				var rep = new PulseReport();
				var killedAt = new Dictionary<int, long>();
				long filmSoak = 0;
				for (int i = 0; i < p.CropKillPulses + 50; i++)
				{
					Pulse(s, w, p, rep);
					foreach (int c in rep.CropKilled) { Assert(!killedAt.ContainsKey(c), "a crop is killed once"); killedAt[c] = s.Pulse; }
					foreach (var (c, dl) in rep.Soaked) if (c == film) filmSoak += dl;
				}
				Assert(killedAt.Count == 9, "every yard cell under standing overflow kills its crop after a week, got " + killedAt.Count);
				foreach (var kv in killedAt) Assert(kv.Value == p.CropKillPulses, $"cell {kv.Key} killed at pulse {kv.Value}, not {p.CropKillPulses}");
				Assert(!killedAt.ContainsKey(film) && filmSoak == 150, $"the film irrigates (soaked {filmSoak}) and never kills");
				Assert(s.LedgerCloses, "ledger");
			});

			// §3 blocking rules: no mixing; a limitless lake absorbs and discloses; a foreign body refuses
			Case("Sheet_fluids_never_mix_and_the_lake_absorbs_disclosed", () =>
			{
				var w = new World(20, 5);
				w.Kinds[Idx(w, 19, 2)] = Kind.Sink; w.BodyFluid[Idx(w, 19, 2)] = Water;
				w.Kinds[Idx(w, 0, 2)] = Kind.Receiver; w.RoomDl[Idx(w, 0, 2)] = 100000; w.BodyFluid[Idx(w, 0, 2)] = Water;
				var p = new Params();
				var s = new State(20, 5, 2u);
				ResolveSpills(s, w, p, new[] { Offer(8000, Water, Source.Flood, Idx(w, 17, 2)) });
				int[] acc = ResolveSpills(s, w, p, new[] { Offer(8000, Chemfuel, Source.FillIn, Idx(w, 17, 2), Idx(w, 2, 2)) });
				Assert(acc[0] == 8000 && s.Fluid[Idx(w, 2, 2)] == Chemfuel, "chemfuel refuses the water-wet lip and takes the next");
				Run(s, w, p, 300);
				Assert(s.JoinedLake > 0, "water reaching a limitless lake joins it, disclosed");
				long fuel = 0;
				foreach (int c in s.Occ) if (s.Fluid[c] == Chemfuel) fuel += s.Dl[c];
				Assert(fuel == 8000, "every dL of chemfuel is still chemfuel (no lake or canal took it, nothing mixed): " + fuel);
				Assert(w.RoomDl[Idx(w, 0, 2)] == 100000, "a water canal refuses chemfuel");
			});

			// D8 (owner card 2026-10-22, "sheets lie level"): one pulse levels a walled puddle exactly over its relief;
			// the diffusion kernel alone leaves a slope and a 1-dL staircase
			Case("Sheet_D8_a_puddle_lies_level_in_one_pulse_diffusion_alone_does_not", () =>
			{
				long Spread(bool level, int pulses, out long standing)
				{
					var w = new World(14, 14);
					Ring(w, 1, 1, 12, 12, Kind.Blocked);
					var p = new Params { LevelBasins = level };
					var s = new State(14, 14, 77u);
					for (int x = 2; x <= 11; x++) for (int z = 2; z <= 11; z++)
						ResolveSpills(s, w, p, new[] { Offer(p.RetentionDl + 40 * (x + z), Water, Source.Pump, Idx(w, x, z)) }); // a ramp
					Run(s, w, p, pulses);
					standing = s.Standing;
					long lo = long.MaxValue, hi = long.MinValue;
					for (int x = 2; x <= 11; x++) for (int z = 2; z <= 11; z++)
					{
						int c = Idx(w, x, z);
						if (s.Dl[c] <= p.RetentionDl) continue; // a relief bump above the surface holds only moisture
						long surf = s.Dl[c] + Relief(s.Salt, c, p.ReliefDl);
						lo = Math.Min(lo, surf); hi = Math.Max(hi, surf);
					}
					return hi - lo;
				}
				long lv = Spread(true, 1, out long v1), df1 = Spread(false, 1, out long v2), df60 = Spread(false, 60, out _);
				Console.WriteLine($"      surface spread: levelled {lv} dL after 1 pulse; diffusion alone {df1} after 1, {df60} after 60");
				Assert(lv <= 1, "D8: a levelled puddle's surface varies by at most the 1-dL remainder, got " + lv);
				Assert(df1 > 100 && df60 >= 2, $"the diffusion-only control must still slope (1 pulse {df1}, 60 pulses {df60})");
				Assert(v1 == v2, "levelling conserves to the dL");
			});

			Case("Sheet_D8_levelling_keeps_doors_slow_and_skips_settled_puddles", () =>
			{
				var w = new World(20, 10);
				Ring(w, 0, 0, 19, 9, Kind.Blocked);
				for (int z = 1; z <= 8; z++) w.Kinds[Idx(w, 10, z)] = Kind.Blocked;
				w.Kinds[Idx(w, 10, 4)] = Kind.Door; // two rooms joined by one door
				var p = new Params();
				var s = new State(20, 10, 4u);
				for (int x = 1; x <= 9; x++) for (int z = 1; z <= 8; z++) ResolveSpills(s, w, p, new[] { Offer(3000, Water, Source.Rain, Idx(w, x, z)) });
				Run(s, w, p, 20);
				long east = Inside(s, w, 11, 1, 18, 8);
				Assert(east > 0 && east * 20 < Inside(s, w, 1, 1, 9, 8), $"D4 under D8: the door still leaks slowly (east {east})");
				// a settled puddle with no door falls asleep and levelling stops touching it
				var w2 = new World(8, 8); Ring(w2, 0, 0, 7, 7, Kind.Blocked);
				var s2 = new State(8, 8, 4u);
				for (int c = 0; c < 64; c++) if (w2.Kinds[c] == Kind.Open) ResolveSpills(s2, w2, p, new[] { Offer(1000 + c, Water, Source.Rain, c) });
				Run(s2, w2, p, 30);
				var snap = (int[])s2.Dl.Clone();
				Run(s2, w2, p, 10);
				bool same = true; for (int c = 0; c < 64; c++) same &= snap[c] == s2.Dl[c];
				bool asleep = true; foreach (int c in s2.Occ) asleep &= s2.Calm[c] >= p.SleepAfterPulses;
				Assert(same && asleep, "a levelled puddle is a fixed point and sleeps");
			});

			// D10 (owner card 2026-10-22): below 0 °C a sheet freezes into its own ice tier keeping its volume, and thaws back
			Case("Sheet_D10_freezes_to_its_own_ice_keeping_every_dL_and_thaws_back", () =>
			{
				var w = new World(16, 8);
				for (int x = 0; x < 16; x++) { w.Kinds[Idx(w, x, 0)] = Kind.Receiver; w.RoomDl[Idx(w, x, 0)] = 100000; } // a drawn-down canal
				for (int c = 0; c < w.TempDeciC.Length; c++) { w.TempDeciC[c] = -50; w.SoakMilliDl[c] = 2000; }
				w.Fluids[Chemfuel] = new FluidRule { InfiltrationPermille = 0, EvaporationPermille = 0, NeverFreezes = true };
				var p = new Params();
				var s = new State(16, 8, 6u);
				var water = new List<int>();
				for (int x = 2; x <= 6; x++) for (int z = 3; z <= 5; z++) { water.Add(Idx(w, x, z)); ResolveSpills(s, w, p, new[] { Offer(4000, Water, Source.Rain, Idx(w, x, z)) }); }
				ResolveSpills(s, w, p, new[] { Offer(4000, Chemfuel, Source.Pump, Idx(w, 12, 4)) });
				var rep = new PulseReport();
				Pulse(s, w, p, rep);
				foreach (int c in water) Assert(s.Tiers[c] == Tier.Ice && s.Dl[c] == 4000, $"cell {c}: tier {s.Tiers[c]}, {s.Dl[c]} dL (frozen water keeps its dL)");
				Assert(rep.TierChanged.Exists(t => t.to == Tier.Ice), "the freeze is reported for the picture");
				Assert(s.Tiers[Idx(w, 12, 4)] != Tier.Ice, "chemfuel never freezes");
				var stand = s.Stand[water[0]];
				int[] accIce = ResolveSpills(s, w, p, new[] { Offer(500, Water, Source.Pump, water[0]) });
				Assert(accIce[0] == 0, "an iced lip takes no new spill");
				Run(s, w, p, 200);
				long ice = 0; foreach (int c in water) ice += s.Dl[c];
				Assert(ice == 15 * 4000 && s.Soaked == 0, $"ice neither flows, returns nor soaks (held {ice}, soaked {s.Soaked})");
				Assert(s.Stand[water[0]] == stand, "the D3 crop timer pauses under ice");
				for (int c = 0; c < w.TempDeciC.Length; c++) w.TempDeciC[c] = 5; // +0.5 °C: inside the thaw margin
				Run(s, w, p, 5);
				Assert(s.Tiers[water[0]] == Tier.Ice, "ice does not thaw at +0.5 °C (no flapping at the freezing point)");
				for (int c = 0; c < w.TempDeciC.Length; c++) w.TempDeciC[c] = 30;
				Pulse(s, w, p, rep);
				Assert(rep.TierChanged.Exists(t => t.from == Tier.Ice && t.to == Tier.Pool), "it thaws back to the tier its 20 cm call for");
				Run(s, w, p, 300);
				Assert(s.Returned > 0, "thawed water flows again and runs back into the canal");
				Assert(s.LedgerCloses, "ledger");
			});

			// Stage 1 (§6 item 1): offer → accepted dL. A probe equals the commit and changes nothing.
			Case("Sheet_preview_changes_nothing_and_counts_a_duplicate_lip_once", () =>
			{
				var r = new Random(11);
				for (int t = 0; t < 200; t++)
				{
					var w = RandomWorld(r, 12, 12, false);
					var p = new Params { MaxWetCells = 1 + r.Next(30), SheetCapDl = 200 + r.Next(3000) };
					var s = new State(12, 12, (uint)t);
					for (int k = 0; k < 3; k++)
						ResolveSpills(s, w, p, new[] { Offer(r.Next(20000), Water, Source.Rain, r.Next(144), r.Next(144)) });
					var lips = new int[1 + r.Next(6)];
					for (int k = 0; k < lips.Length; k++) lips[k] = r.Next(144);
					lips[lips.Length - 1] = lips[0]; // a duplicate lip must not be counted twice by the probe
					SpillOffer o = Offer(r.Next(60000), Water, Source.Pump, lips);
					ulong h0 = Hash(s);
					int probe = PreviewSpill(s, w, p, o);
					Assert(Hash(s) == h0, "a probe changed the state");
					int got = ResolveSpills(s, w, p, new[] { o })[0];
					Assert(probe == got, $"probe {probe} != commit {got} (case {t})");
					Assert(s.LedgerCloses, "ledger");
				}
			});

			// Stage 1 (§6 item 1): the engine's credit is atomic; the sheet debits exactly what the receiver took
			Case("Sheet_engine_credit_partial_and_refused_conserve_to_the_dL", () =>
			{
				var w = new World(20, 5);
				var p = new Params { ReliefDl = 0 };
				for (int x = 0; x < 20; x++) w.Kinds[Idx(w, x, 0)] = Kind.Receiver;
				for (int x = 0; x < 20; x++) w.RoomDl[Idx(w, x, 0)] = int.MaxValue / 4;
				long engineTook = 0; int calls = 0;
				w.Credit = (cell, want, fluid) =>
				{
					calls++;
					int took = cell % 3 == 0 ? 0 : cell % 3 == 1 ? want / 3 : want; // refused, partial, whole
					engineTook += took;
					return took;
				};
				var s = new State(20, 5, 9u);
				ResolveSpills(s, w, p, new[] { Offer(40000, Water, Source.FillIn, Idx(w, 10, 2), Idx(w, 9, 2), Idx(w, 11, 2)) });
				Run(s, w, p, 300);
				Assert(calls > 0 && engineTook > 0, $"the engine was asked and took some: calls {calls} took {engineTook} returned {s.Returned} wet {s.WetCount} standing {s.Standing} soaked {s.Soaked}");
				Assert(s.Returned == engineTook, $"returned {s.Returned} must equal what the engine took {engineTook}");
				Assert(s.TotalIn == 30000 && s.LedgerCloses, "three lips x the 0.5 m cap took 30000; the ledger closes with a partial and refusing receiver: in " + s.TotalIn);
			});

			Case("Sheet_hand_over_to_the_engine_is_counted_and_never_overdraws", () =>
			{
				var w = new World(10, 10);
				var p = new Params();
				var s = new State(10, 10, 4u);
				ResolveSpills(s, w, p, new[] { Offer(3000, Water, Source.FillIn, 55) });
				Assert(HandOver(s, 55, 1000, false) == 1000 && s.Returned == 1000 && s.LedgerCloses, "a part handed to a dug cell");
				Assert(HandOver(s, 55, 99999, true) == 2000 && s.JoinedLake == 2000 && s.WetCount == 0, "the rest into a lake, no more");
				Assert(HandOver(s, 55, 5, false) == 0 && s.LedgerCloses, "a dry cell hands over nothing");
			});

			Case("Sheet_dry_all_is_a_disclosed_purge", () =>
			{
				var w = new World(10, 10);
				var p = new Params();
				var s = new State(10, 10, 1u);
				ResolveSpills(s, w, p, new[] { Offer(5000, Water, Source.Pump, 55) });
				Run(s, w, p, 20);
				long purged = PurgeAll(s);
				Assert(purged == 5000 && s.Purged == 5000 && s.WetCount == 0 && s.LedgerCloses, "purge discloses every dL");
				var rep = new PulseReport();
				Pulse(s, w, p, rep);
				Assert(rep.TierChanged.Count > 0, "the purge reports the pictures to clear");
			});

			// FlowWorks GPT review 2026-10-22 (RM_SheetMath.cs:459): a consumer replaying TierChanged IN ORDER must end on each
			// cell's real tier. Purge then refill before the next pulse used to report (None→Film) then (old→None) and clear
			// the refilled cell's picture. Fuzzed with purges, refills and draining canals so in-pulse dry-then-wet is hit too.
			Case("Sheet_tier_reports_replay_in_order_to_the_real_tier_after_purge_and_refill", () =>
			{
				var p = new Params();
				var s = new State(10, 10, 1u);
				var w = new World(10, 10);
				ResolveSpills(s, w, p, new[] { Offer(5000, Water, Source.Pump, 55) });
				var rep = new PulseReport();
				var picture = new Tier[100];
				void Replay() { foreach (var (c, from, to) in rep.TierChanged) picture[c] = to; }
				Pulse(s, w, p, rep); Replay();
				Assert(picture[55] != Tier.None, "a wet cell has a picture");
				PurgeAll(s);
				ResolveSpills(s, w, p, new[] { Offer(5000, Water, Source.Pump, 55) }); // refilled before the pulse reports the purge
				Pulse(s, w, p, rep); Replay();
				Assert(picture[55] == s.Tiers[55] && picture[55] != Tier.None, $"refilled cell shows {picture[55]}, real tier {s.Tiers[55]}");
				var r = new Random(31);
				for (int round = 0; round < 40; round++)
				{
					var wr = RandomWorld(r, 16, 16, true);
					var sr = new State(16, 16, (uint)round);
					var pic = new Tier[256];
					for (int t = 0; t < 120; t++)
					{
						if (t % 7 == 0) ResolveSpills(sr, wr, p, new[] { Offer(r.Next(100, 6000), Water, Source.Rain, r.Next(256), r.Next(256)) });
						if (t % 23 == 22) { PurgeAll(sr); ResolveSpills(sr, wr, p, new[] { Offer(3000, Water, Source.Pump, r.Next(256)) }); }
						Pulse(sr, wr, p, rep);
						foreach (var (c, from, to) in rep.TierChanged) pic[c] = to;
						for (int c = 0; c < 256; c++)
							Assert(pic[c] == sr.Tiers[c], $"round {round} pulse {t}: cell {c} replays to {pic[c]}, real tier {sr.Tiers[c]}");
					}
				}
			});

			// FlowWorks GPT review 2026-10-22 (RM_SheetMath.cs:390): a water-filled DOOR beside a sink or receiver drained at
			// full rate, bypassing DoorLeakPermille (D4). Now each door edge passes at most that share of the mobile water.
			Case("Sheet_a_door_beside_a_drain_leaks_slowly_too", () =>
			{
				long Drained(Kind cell, Kind drain)
				{
					var w = new World(5, 3);
					for (int c = 0; c < 15; c++) w.Kinds[c] = Kind.Blocked;
					int at = Idx(w, 2, 1), to = Idx(w, 3, 1);
					w.Kinds[at] = cell; w.Kinds[to] = drain;
					w.RoomDl[to] = 1000000; w.BodyFluid[to] = Water;
					var p = new Params();
					var s = new State(5, 3, 9u);
					ResolveSpills(s, w, p, new[] { Offer(6000, Water, Source.Pump, at) });
					Pulse(s, w, p, null);
					Assert(s.LedgerCloses, "ledger");
					return s.Returned + s.JoinedLake;
				}
				var pp = new Params();
				long mobile = 6000 - pp.RetentionDl, slow = mobile * pp.DoorLeakPermille / 1000;
				foreach (Kind drain in new[] { Kind.Sink, Kind.Receiver })
				{
					long open = Drained(Kind.Open, drain), door = Drained(Kind.Door, drain);
					Assert(open == mobile, $"{drain}: open ground beside it drains all its mobile water in a pulse ({open})");
					Assert(door == slow, $"{drain}: a door drains only DoorLeakPermille of it ({door}, want {slow})");
				}
			});

			// FlowWorks GPT review 2026-10-22 (RM_SheetMath.cs:267,278,509): every pulse allocated two map-sized bool arrays and
			// scanned the whole map, even dry or asleep. Now the working memory is reused and a dry map returns at once.
			Case("Sheet_pulse_allocates_nothing_in_steady_state", () =>
			{
				var w = new World(250, 250);
				var p = new Params();
				var dry = new State(250, 250, 1u);
				Pulse(dry, w, p, null);
				long a0 = GC.GetAllocatedBytesForCurrentThread();
				for (int i = 0; i < 200; i++) Pulse(dry, w, p, null);
				long dryBytes = GC.GetAllocatedBytesForCurrentThread() - a0;
				var s = new State(250, 250, 2u);
				Ring(w, 100, 100, 130, 130, Kind.Blocked);
				for (int x = 101; x <= 129; x++) ResolveSpills(s, w, p, new[] { Offer(3000, Water, Source.Rain, Idx(w, x, 115)) });
				Run(s, w, p, 80); // a walled puddle: levelled, then asleep
				var rep = new PulseReport();
				Pulse(s, w, p, rep);
				long a1 = GC.GetAllocatedBytesForCurrentThread();
				for (int i = 0; i < 200; i++) Pulse(s, w, p, rep);
				long wetBytes = GC.GetAllocatedBytesForCurrentThread() - a1;
				Console.WriteLine($"      200 pulses allocate: dry map {dryBytes} B, settled 29×29 puddle {wetBytes} B (was ~25 MB: 2 × 62.5 kB a pulse)");
				// the old pulse allocated 125 kB a pulse here (25 MB per 200); a one-off runtime warm-up of a few kB is not per pulse
				Assert(dryBytes < 64 * 1024 && wetBytes < 64 * 1024, $"steady pulses must not allocate per pulse (dry {dryBytes} B, wet {wetBytes} B)");
				Assert(s.LedgerCloses, "ledger");
			});

			Case("Sheet_preview_matches_what_the_spill_accepts", () =>
			{
				var r = new Random(5);
				for (int round = 0; round < 200; round++)
				{
					var w = RandomWorld(r, 12, 12, false);
					var p = new Params { MaxWetCells = r.Next(1, 30), SheetCapDl = r.Next(200, 3000) };
					var s = new State(12, 12, 3u);
					for (int t = 0; t < 10; t++)
					{
						var lips = new int[r.Next(1, 6)];
						for (int i = 0; i < lips.Length; i++) lips[i] = r.Next(-2, 146);
						var o = Offer(r.Next(1, 20000), r.Next(4) == 0 ? Chemfuel : Water, Source.Pump, lips);
						ulong h = Hash(s); // review 2026-10-22: hashed BEFORE the preview (hashing after it compared the state to itself)
						int pre = PreviewSpill(s, w, p, o);
						Assert(Hash(s) == h, "preview changes nothing");
						int got = ResolveSpills(s, w, p, new[] { o })[0];
						Assert(pre == got, $"round {round}: preview {pre} vs accepted {got}");
						Pulse(s, w, p, null);
					}
				}
			});

			// owner 2026-10-22 "Build for all flowworks liquids.": each liquid's sheet rule comes from its own FluidDef
			Case("Sheet_all_liquids_each_follow_their_own_FluidDef", () =>
			{
				FluidRule water = RM_SheetFluidMath.RuleFor(false, false, false, 60, -1, -1);
				Assert(water.InfiltrationPermille == 1000 && water.EvaporationPermille == 1000 && !water.NeverFreezes && water.FreezeDeciC == 0,
					"water soaks and dries at the ground's rate and freezes at 0 C");
				FluidRule tar = RM_SheetFluidMath.RuleFor(true, false, false, 360, -1, -1);
				Assert(tar.InfiltrationPermille == 166 && tar.EvaporationPermille == 166 && tar.NeverFreezes,
					"tar (6x thicker) soaks and dries at a sixth, and a fuel never freezes: " + tar.InfiltrationPermille);
				FluidRule slime = RM_SheetFluidMath.RuleFor(false, false, true, 480, -1, -1);
				Assert(slime.InfiltrationPermille == 125 && slime.NeverFreezes, "slime is thick and slippery: slow, never freezes");
				FluidRule boiling = RM_SheetFluidMath.RuleFor(false, true, false, 60, -1, -1);
				Assert(boiling.EvaporationPermille == 3000 && boiling.NeverFreezes, "a hot liquid dries 3x and never freezes");
				FluidRule propane = RM_SheetFluidMath.RuleFor(true, false, false, 60, 0, 2000);
				Assert(propane.InfiltrationPermille == 0 && propane.EvaporationPermille == 20000, "an authored percent overrides (propane boils off)");
				FluidRule glacial = RM_SheetFluidMath.RuleFor(false, false, false, 100000, -1, -1);
				Assert(glacial.InfiltrationPermille == 100, "the viscosity floor is 10%");
				Assert(RM_SheetFluidMath.PutsOutFire(false) && !RM_SheetFluidMath.PutsOutFire(true), "only a liquid that does not burn puts fire out");
			});

			// fuel_spill_research.md (owner 2026-10-22: "realistic numbers ... if liquid propane or chemfuel (gasoline) or
			// astrofuel (jet fuel) were spilled"): propane boils off on ground heat above -42 C, roof or not; a spill burns
			// down at its fuel's real pool-fire regression rate
			Case("Sheet_real_fuel_numbers_propane_boils_above_its_boiling_point_and_spills_burn_at_pool_fire_rates", () =>
			{
				int boil = RM_SheetFluidMath.BoilMilliDlPerPulse(2f, DlPerCm, 240f);
				Assert(boil == 200 * DlPerCm, "2 cm an hour at 240 pulses a day is 0.2 cm a pulse: " + boil);
				Assert(RM_SheetFluidMath.BoilMilliDlPerPulse(0f, DlPerCm, 240f) == 0, "a liquid that does not boil loses nothing to boiling");
				foreach (int t in new[] { 200, -500 })
				{
					var w = new World(10, 3);
					FluidRule pr = RM_SheetFluidMath.RuleFor(true, false, false, 60, 0, 0);
					pr.BoilMilliDl = boil;
					pr.BoilAboveDeciC = -420;
					w.Fluids[Chemfuel] = pr;
					for (int c = 0; c < w.TempDeciC.Length; c++) { w.TempDeciC[c] = t; w.SoakMilliDl[c] = 0; w.EvapMilliDl[c] = 0; }
					var p = new Params();
					var s = new State(10, 3, 5u);
					ResolveSpills(s, w, p, new[] { Offer(3000, Chemfuel, Source.Flood, Idx(w, 4, 1)) });
					Run(s, w, p, 200);
					Assert(s.LedgerCloses, "the ledger closes while propane boils");
					if (t > -420)
						Assert(s.Evaporated == 3000 && s.WetCount == 0, "at 20 C (no air drying, no soak) the spill boils away entirely: " + s.Evaporated);
					else
						Assert(s.Evaporated == 0, "below -42 C liquid propane stays a pool: " + s.Evaporated);
				}
				int gas = RM_SheetFluidMath.SheetBurnTicksPerNotch(4f, 50, 2500, 1f);
				Assert(gas == 5208, "gasoline 4 mm a game minute: a 50 cm notch in 125 game minutes = 5208 ticks, got " + gas);
				Assert(RM_SheetFluidMath.SheetBurnTicksPerNotch(4f, 50, 2500, 2f) == 2604, "the burn-rate dial halves it at 2");
				Assert(RM_SheetFluidMath.SheetBurnTicksPerNotch(8f, 50, 2500, 1f) < gas
					&& RM_SheetFluidMath.SheetBurnTicksPerNotch(3f, 50, 2500, 1f) > gas, "propane burns faster than gasoline, jet fuel slower");
			});

			// D5: a burning spill loses liquid to the 'burned' exit, conserving the ledger to the dL; a square burned dry leaves
			Case("Sheet_D5_fuel_burns_away_counted_and_the_front_runs_at_the_fuel_speed", () =>
			{
				var w = new World(10, 3);
				w.Fluids[Chemfuel] = RM_SheetFluidMath.RuleFor(true, false, false, 60, -1, -1);
				var p = new Params();
				var s = new State(10, 3, 9u);
				int[] acc = ResolveSpills(s, w, p, new[] { Offer(3000, Chemfuel, Source.Flood, Idx(w, 4, 1)) });
				Assert(acc[0] == 3000, "the fuel spill is accepted");
				Run(s, w, p, 4);
				int c = s.Occ[0];
				int had = s.Dl[c];
				Assert(Burn(s, c, 100) == 100 && s.Burned == 100 && s.LedgerCloses, "a partial burn is counted as burned");
				Assert(Burn(s, c, int.MaxValue) == had - 100 && s.Dl[c] == 0 && !s.Occ.Contains(c) && s.LedgerCloses,
					"burning a square dry takes exactly what stood there and the square leaves the wet set");
				Assert(Burn(s, c, 50) == 0 && Burn(s, -1, 50) == 0, "nothing burns where nothing stands");
				Run(s, w, p, 20);
				// the inferno rate: a level (U dL) every 300 ticks at burn rate 1, carried exactly across 60-tick checks
				int tpl = RM_FuelFireMath.InfernoTicksPerLevelAt(1f), a = 0, sum = 0;
				for (int k = 0; k < 5; k++) sum += RM_SheetFluidMath.BurnDue(ref a, 60, tpl, RM_LevelSolve.U);
				Assert(tpl == 300 && sum == RM_LevelSolve.U && a == 0, "five 60-tick checks of an inferno burn exactly one level: " + sum);
				int tday = RM_FireMath.TicksPerCanalLevel(1f); a = 0; sum = 0;
				for (int k = 0; k < 1000; k++) sum += RM_SheetFluidMath.BurnDue(ref a, 60, tday, RM_LevelSolve.U);
				Assert(sum == RM_LevelSolve.U, "ruling 7: a thousand checks of 60 ticks (one day) burn one notch of oil: " + sum);
				Assert(!RM_SheetFluidMath.FrontReaches(1000, 1119, 120, 1f) && RM_SheetFluidMath.FrontReaches(1000, 1120, 120, 1f),
					"the front reaches the next square fireFrontTicksPerCell after this one lit");
				Assert(RM_SheetFluidMath.FrontReaches(1000, 1060, 120, 2f), "a faster front (the speed dial) gets there sooner");
			});

			// all liquids: a canal or pond of another liquid never takes a spill back, and a spill next to it stays itself
			Case("Sheet_a_body_of_another_liquid_refuses_the_return", () =>
			{
				var w = new World(8, 3);
				int body = Idx(w, 5, 1);
				w.Kinds[body] = Kind.Receiver; w.RoomDl[body] = 100000; w.BodyFluid[body] = Water;
				var p = new Params();
				var s = new State(8, 3, 4u);
				ResolveSpills(s, w, p, new[] { Offer(6000, Chemfuel, Source.Pump, Idx(w, 4, 1)) });
				Run(s, w, p, 200);
				Assert(s.Returned == 0 && w.RoomDl[body] == 100000, "a water channel takes no chemfuel");
				w.BodyFluid[body] = Chemfuel;
				Run(s, w, p, 50);
				Assert(s.Returned > 0 && s.LedgerCloses, "a chemfuel channel beside it takes its own liquid back");
			});

			// wiring (source text): the owner's two rulings of 2026-10-22 are in the production entries
			Case("Sheet_all_liquids_and_silent_release_loss_are_wired", () =>
			{
				string sheet = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Sheet", "RM_MapComponent_Sheet.cs"));
				string set = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Sheet", "RM_SheetSettings.cs"));
				string flood = RiverSwitchFlipChecks.Src("Flood_FlowWorks.cs");
				string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
				string fire = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Sheet", "RM_SheetFire.cs"));
				Assert(set.Contains("public static bool sheetOverflowEnabled = false;"), "the master switch still ships OFF");
				Assert(set.Contains("public static bool otherLiquidsSpillEnabled = true;") && set.Contains("public static bool fuelSpillsBurnEnabled = true;"),
					"all liquids and D5 fuel fire have their own settings");
				Assert(sheet.Contains("(fluid == Water || RM_SheetSettings.otherLiquidsSpillEnabled)") && !sheet.Contains("fluid != null && fluid == Water;"),
					"every liquid is accepted, not only water");
				Assert(sheet.Contains("RM_StockMath.FluidsCompatible(held != null, held, fluid)") && sheet.Contains("RM_StockMath.FluidsCompatible(held != null, held, f)"),
					"the lip walk and the engine credit refuse another liquid (fluids never mix)");
				Assert(sheet.Contains("RM_SheetFluidMath.RuleFor(Burnable(f), f.hot, f.slipperiness > 0f, f.ticksPerTile"), "each liquid's rule is its FluidDef's");
				Assert(fire.Contains("RM_SheetMath.Burn(state, i, dl)") && fire.Contains("RM_SheetSettings.fuelSpillsBurnEnabled"),
					"fuel burns through the counted exit, behind its own setting");
				string end = flood.Substring(flood.IndexOf("private void EndRelease()"));
				Assert(end.Contains("silent: true"), "a release's lost remainder is counted silently (owner card 2026-10-22)");
				Assert(ex.Contains("releaseLostDl += dl;") && ex.Contains("Scribe_Values.Look(ref releaseLostDl"), "it is counted and saved");
				Assert(sheet.Contains("released floods with nowhere to go lost"), "the liquid ledger readout shows it");
			});
		}
	}
}
