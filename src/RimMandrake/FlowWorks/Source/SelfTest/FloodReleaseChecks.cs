// CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED step 1: the four Flood_FlowWorks accounting faults the design filed (§6 item 15 of
// design/RimMandrake/canal_overflow_flooding_2026-10-21.md), proven on the PRODUCTION RM_FloodReleaseMath.cs and, where the rule
// lives in Verse code, on the production Flood_FlowWorks.cs text.
//   1. no silent exit: every end goes through EndRelease (sheet, then disclosed loss); the ledger closes to the dL;
//   2. whole decilitres, never a float notch: a dug square takes exactly what is poured, nothing is overdrawn;
//   3. refusals are saved: a save/load continuation walks exactly like an uninterrupted release;
//   4. deterministic walk: the same release draws the same cells on every run, with no global Rand.
// NOT proven here: the live game (bridge rows belong to northstar/sheet_overflow_proof.py).
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using RimMandrake.FlowWorks;
using static RimMandrake.FlowWorks.RM_FloodReleaseMath;

namespace RimMandrake.FlowWorks.SelfTest
{
	internal static class FloodReleaseChecks
	{
		private static void Assert(bool ok, string msg)
		{
			if (!ok) throw new Exception(msg);
		}

		private enum CellKind { Surface, Dug, Foreign, Blocked }

		/// <summary>A release walk over a synthetic grid, mirroring Flood_FlowWorks.SpreadOneTile/PlaceFluid/Tick, so the
		/// production math can be driven step by step. Its whole state is public, so a test can "save" and "load" it.</summary>
		private sealed class Walk
		{
			public int W, H, Salt;
			public CellKind[] Kinds;
			public long[] Room;           // dug: dL of room left
			public long[] Credited;       // what the world received per cell
			public bool LevelExact;
			public long PerTile = U;
			public Ledger L;
			public long Step;
			public List<int> Frontier = new List<int>(), Placed = new List<int>(), Refused = new List<int>();
			public HashSet<int> Lookup = new HashSet<int>();
			public List<int> Order = new List<int>(); // cells placed, in order (the trajectory)

			public Walk Clone(bool keepRefused)
			{
				var w = (Walk)MemberwiseClone();
				w.Room = (long[])Room.Clone(); w.Credited = (long[])Credited.Clone();
				w.L = new Ledger { In = L.In, Placed = L.Placed, Spilled = L.Spilled, Lost = L.Lost, Remaining = L.Remaining };
				w.Frontier = new List<int>(Frontier); w.Placed = new List<int>(Placed); w.Refused = new List<int>(Refused);
				w.Order = new List<int>(Order);
				// what a load rebuilds: placed always; refused only when they were saved
				w.Lookup = new HashSet<int>(Placed);
				if (keepRefused) foreach (int c in Refused) w.Lookup.Add(c);
				else w.Refused.Clear();
				return w;
			}

			private int N(int c, int d)
			{
				int x = c % W + (d == 1 ? 1 : d == 3 ? -1 : 0), z = c / W + (d == 0 ? 1 : d == 2 ? -1 : 0);
				return x < 0 || z < 0 || x >= W || z >= H ? -1 : z * W + x;
			}

			private bool CanFloodInto(int n) => n >= 0 && !Lookup.Contains(n) && Kinds[n] != CellKind.Blocked;

			private void Reached(int c) { Placed.Add(c); Lookup.Add(c); Frontier.Add(c); Order.Add(c); }
			private void Refuse(int c) { Lookup.Add(c); Refused.Add(c); }

			/// <summary>One expand interval. False once the frontier is empty.</summary>
			public bool SpreadOne()
			{
				int attempts = Frontier.Count;
				while (attempts-- > 0 && Frontier.Count > 0)
				{
					long step = Step++;
					int pick = Pick(Salt, step, 0, Frontier.Count);
					int from = Frontier[pick], target = -1, seen = 0;
					for (int i = 0; i < 4; i++)
					{
						int n = N(from, i);
						if (!CanFloodInto(n)) continue;
						seen++;
						if (Pick(Salt, step, 1 + i, seen) == 0) target = n;
					}
					if (target < 0) { Frontier.RemoveAt(pick); continue; }
					Place(target);
					return true;
				}
				return Frontier.Count > 0;
			}

			private void Place(int c)
			{
				switch (Kinds[c])
				{
					case CellKind.Foreign: Refuse(c); return;
					case CellKind.Dug:
						if (Room[c] <= 0) { Reached(c); return; }
						long want = DugPourDl(L.Remaining, Room[c], LevelExact);
						if (want > 0)
						{
							Room[c] -= want; Credited[c] += want; Reached(c);
							Assert(L.Place(want) == want, "a dug pour debits exactly what it poured");
							return;
						}
						Frontier.Clear(); // less than a whole notch left: the walk ends, the rest drains to the sheet
						return;
					default:
						long d = SurfaceDebitDl(L.Remaining, PerTile);
						Credited[c] += d; Reached(c);
						Assert(L.Place(d) == d, "a surface tile debits exactly its cost");
						return;
				}
			}

			/// <summary>Tick until the release ends, the way Flood_FlowWorks.Tick does; the sheet takes up to sheetRoom.</summary>
			public void RunToEnd(long sheetRoom, int maxSteps = 100000)
			{
				for (int i = 0; i < maxSteps && L.Remaining > 0 && Frontier.Count > 0; i++)
				{
					SpreadOne();
					Assert(L.Closes, "ledger open mid-walk: " + Line());
				}
				// EndRelease: the sheet, then the disclosed loss
				long got = Math.Min(sheetRoom, L.Remaining);
				Assert(L.Spill(got) == got, "the sheet's acceptance is debited exactly");
				L.Lose();
				Assert(L.Remaining == 0 && L.Closes, "an ended release holds nothing and its books close: " + Line());
			}

			public string Line() => $"in {L.In} placed {L.Placed} spilled {L.Spilled} lost {L.Lost} held {L.Remaining}";
		}

		private static Walk RandomWalk(Random r, int salt, bool levelExact, long inDl)
		{
			int W = 9 + r.Next(8), H = 9 + r.Next(8);
			var w = new Walk { W = W, H = H, Salt = salt, LevelExact = levelExact, Kinds = new CellKind[W * H], Room = new long[W * H], Credited = new long[W * H] };
			for (int c = 0; c < W * H; c++)
			{
				int roll = r.Next(100);
				w.Kinds[c] = roll < 15 ? CellKind.Blocked : roll < 22 ? CellKind.Foreign : roll < 70 ? CellKind.Dug : CellKind.Surface;
				if (w.Kinds[c] == CellKind.Dug)
				{
					// a dug square's room: 0..4 notches, with part-notch water already standing (the case the old rule broke)
					w.Room[c] = r.Next(3) == 0 ? 0 : r.Next(1, 4) * U - r.Next(0, (int)U);
				}
			}
			int seed = (H / 2) * W + W / 2;
			w.Kinds[seed] = CellKind.Dug;
			w.L = Ledger.Start(inDl);
			w.Frontier.Add(seed);
			return w;
		}

		public static void Run(Action<string, Action> Case)
		{
			Case("FloodRelease_volume_is_whole_decilitres_one_notch_is_10000", () =>
			{
				Assert(U == 10000 && U == RM_LevelSolve.U, "one notch over one square is 10,000 dL, the engine's U");
				Assert(NotchesToDl(1f) == 10000 && NotchesToDl(12f) == 120000 && NotchesToDl(0f) == 0 && NotchesToDl(-3f) == 0, "notches to dL");
				Assert(NotchesToDl(0.25f) == 2500 && PerTileDl(1f) == 10000 && PerTileDl(0f) == 1, "fractions and the 1 dL floor");
				Assert(PayableTiles(30 * U, U) == 30 && PayableTiles(30 * U + 1, U) == 31 && PayableTiles(0, U) == 1, "payable tiles");
			});

			Case("FloodRelease_dug_pour_never_overdraws_and_old_float_rule_did", () =>
			{
				// 0.3 notch left, a square with 1.6 notches of room (part-notch water standing): the new rule pours 3,000 dL and
				// debits 3,000; the old rule (P5, float) filled a whole level and debited one whole level, creating 7,000 dL.
				long rem = 3000, room = 16000;
				Assert(DugPourDl(rem, room, true) == 3000, "exact water: all 3,000 dL go in");
				Assert(DugPourDl(rem, room, false) == 0, "whole-notch water: less than a notch buys nothing");
				Assert(DugPourDl(25000, room, true) == 16000 && DugPourDl(25000, room, false) == 10000, "capped by the room, whole notches");
				int oldTarget = RM_StockMath.FloodFillTarget(4, 2, rem / (float)U, 1f);
				float oldDebitNotches = RM_StockMath.FloodLevelDebit(2, oldTarget, 1f);
				Assert(oldTarget == 3 && Math.Abs(oldDebitNotches * U - rem) > 1, "can-fail: the old rule debited a level for 0.3 of one");
				Assert(SurfaceDebitDl(4000, U) == 4000 && SurfaceDebitDl(25000, U) == U && SurfaceDebitDl(0, U) == 0, "surface: cost or the last of it");
			});

			Case("FloodRelease_conserves_to_the_dL_over_2000_random_releases", () =>
			{
				var r = new Random(20261022);
				for (int t = 0; t < 2000; t++)
				{
					bool exact = t % 2 == 0;
					long inDl = r.Next(1, 60) * (long)U + (exact ? r.Next(0, (int)U) : 0);
					Walk w = RandomWalk(r, r.Next(), exact, inDl);
					long sheetRoom = r.Next(3) == 0 ? 0 : r.Next(0, 200000);
					w.RunToEnd(sheetRoom);
					long world = w.Credited.Sum();
					Assert(world == w.L.Placed, $"release {t}: the world received {world} dL but the ledger placed {w.L.Placed}");
					Assert(w.L.In == world + w.L.Spilled + w.L.Lost, $"release {t}: in {w.L.In} != world {world} + spilled {w.L.Spilled} + lost {w.L.Lost}");
					for (int c = 0; c < w.Room.Length; c++)
						Assert(w.Room[c] >= 0, $"release {t}: square {c} overfilled ({w.Room[c]} dL room)");
					if (!exact)
						for (int c = 0; c < w.Room.Length; c++)
							Assert(w.Kinds[c] != CellKind.Dug || w.Credited[c] % U == 0, "whole-notch water pours whole notches");
				}
			});

			Case("FloodRelease_walk_is_deterministic_and_draws_are_fair", () =>
			{
				var r = new Random(7);
				for (int t = 0; t < 200; t++)
				{
					int salt = r.Next();
					var r1 = new Random(t); var r2 = new Random(t);
					Walk a = RandomWalk(r1, salt, true, 40 * U), b = RandomWalk(r2, salt, true, 40 * U);
					a.RunToEnd(0); b.RunToEnd(0);
					Assert(a.Order.SequenceEqual(b.Order), $"walk {t}: the same release drew different cells");
				}
				var hist = new int[4];
				for (long s = 0; s < 40000; s++) hist[Pick(12345, s, 0, 4)]++;
				Assert(hist.All(h => h > 9000 && h < 11000), "Pick is fair over 4: " + string.Join(",", hist));
				Assert(Pick(1, 2, 3, 1) == 0 && Pick(1, 2, 3, 0) == 0, "n <= 1 draws 0");
			});

			Case("FloodRelease_save_load_continuation_walks_like_uninterrupted_and_only_with_refusals_saved", () =>
			{
				var r = new Random(99);
				int diverged = 0;
				for (int t = 0; t < 400; t++)
				{
					int salt = r.Next();
					var seedR = new Random(1000 + t);
					Walk whole = RandomWalk(seedR, salt, t % 2 == 0, 50 * U);
					Walk part = whole.Clone(true);
					int cut = 1 + t % 9;
					for (int i = 0; i < cut && part.Frontier.Count > 0 && part.L.Remaining > 0; i++) part.SpreadOne();
					Walk saved = part.Clone(true), lostRefusals = part.Clone(false);
					whole.RunToEnd(0); saved.RunToEnd(0); lostRefusals.RunToEnd(0);
					Assert(whole.Order.SequenceEqual(saved.Order) && whole.L.Placed == saved.L.Placed,
						$"walk {t}: a save/load continuation must walk exactly like the uninterrupted release");
					if (part.Refused.Count > 0 && !whole.Order.SequenceEqual(lostRefusals.Order)) diverged++;
				}
				Assert(diverged > 0, "can-fail: dropping the refused squares on load must change some walk (else this proves nothing)");
			});

			Case("Depth_engine_switch_applies_on_reload_only", () =>
			{
				// owner 2026-10-22: "We shouldn't be supporting live changes to the physics." The game keeps the value it started with.
				object key = null; bool snap = true; object g1 = new object(), g2 = new object();
				Assert(EngineSwitch.Resolve(ref key, ref snap, g1, true, false), "game 1 starts with the engine on");
				Assert(EngineSwitch.Resolve(ref key, ref snap, g1, false, false), "flipping it off mid-game changes nothing");
				Assert(!EngineSwitch.Resolve(ref key, ref snap, g2, false, false), "the next load (a new game) reads the new value");
				Assert(!EngineSwitch.Resolve(ref key, ref snap, g2, true, false), "...and keeps it until the next reload");
				Assert(EngineSwitch.Resolve(ref key, ref snap, g2, true, true), "the harness switch reads the live value (can-fail: without it the live value is ignored)");
				string src = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs") + RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Sheet", "RM_MapComponent_Sheet.cs"));
				Assert(!src.Contains("RimMandrakeFlowWorksSettings.depthEngineEnabled"), "the pulse and the spill gate read DepthEngineActive, never the live checkbox");
			});

			Case("Overflow_settings_ship_owner_defaults_master_off_every_field_saved", () =>
			{
				// owner card 2026-10-22: the placeholder loss rates are the Mod Settings defaults; D7: the master switch ships OFF
				// until stage 4 signs it off; the proof script (sheet_overflow_proof.py) sets sheetCapCm / cropDrownPulses by name
				string f = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Sheet", "RM_SheetSettings.cs"));
				foreach (string d in new[] { "public static bool sheetOverflowEnabled = false;", "public static float soakCmPerDaySand = 4f, soakCmPerDaySoil = 2f, soakCmPerDayGravel = 1f;",
					"public static float dryCmPerDayAt20C = 0.5f;", "public static float roofedDryPercent = 30f;", "public static int sheetCapCm = 50;",
					"public static int cropDrownPulses = 1680;", "public static int maxWetSquares = 4000;", "public static float retentionCm = 1f;" })
					Assert(f.Contains(d), "shipped default: " + d);
				Assert(new RM_SheetMath.Params().CropKillPulses == 1680 && new RM_SheetMath.Params().SheetCapDl == 50 * RM_SheetMath.DlPerCm,
					"the settings' defaults equal the kernel's own (1 week, 50 cm)");
				foreach (Match m in Regex.Matches(f, @"public static (bool|int|float) (\w+) = ([^;,]+)[;,]"))
				{
					string name = m.Groups[2].Value;
					Assert(Regex.IsMatch(f, @"Scribe_Values\.Look\(ref " + name + @", ""\w+"", " + Regex.Escape(m.Groups[3].Value.Trim()) + @"\);"),
						"setting " + name + " is saved with its shipped default");
				}
				string sheet = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Sheet", "RM_MapComponent_Sheet.cs"));
				Assert(sheet.Contains("prm.SheetCapDl = Math.Max(DlPerCm, RM_SheetSettings.sheetCapCm * DlPerCm);")
					&& sheet.Contains("prm.CropKillPulses = Math.Max(1, RM_SheetSettings.cropDrownPulses);"), "the kernel reads the settings");
				Assert(sheet.Contains("RM_SheetSettings.SpillsFrom(from)"), "every spill asks the per-inflow switch");
			});

			Case("FloodRelease_production_text_one_end_saved_refusals_no_global_Rand", () =>
			{
				string f = RiverSwitchFlipChecks.Src("Flood_FlowWorks.cs");
				Assert(!Regex.IsMatch(f, @"\bRand\.(Range|Value|Chance|Bool|Element|Int)"), "the walk draws through RM_FloodReleaseMath.Pick, never the global Rand");
				Assert(Regex.Matches(f, @"\bDestroy\(\);").Count == 1, "one Destroy() in the release: EndRelease's");
				string end = f.Substring(f.IndexOf("private void EndRelease()"));
				end = end.Substring(0, end.IndexOf("Destroy();"));
				Assert(end.Contains("DrainToSheet()") && end.Contains("ledger.Lose()") && end.Contains("ReportLiquidLost("),
					"EndRelease offers the rest to the sheet, then discloses the loss, before it destroys the release");
				Assert(f.Contains("Scribe_Collections.Look(ref refusedCells, \"refusedCells\", LookMode.Value);")
					&& f.Contains("placedLookup.Add(refusedCells[i]);"), "refused squares are saved and rebuilt into the lookup");
				Assert(f.Contains("Scribe_Values.Look(ref ledger.Remaining, \"remainingDl\", 0L);"), "the remainder is saved in dL");
				Assert(f.Contains("Pick(thingIDNumber, step, 0, frontier.Count)"), "the frontier pick is the deterministic draw");
				Assert(f.Contains("Sheet.RM_MapComponent_Sheet.SpillRelease(map, Position, ledger.Remaining, fluidDef)"),
					"a release's leftover is offered to the sheet (D2 floods)");
			});
		}
	}
}
