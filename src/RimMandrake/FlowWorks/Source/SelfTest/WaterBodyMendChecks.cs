// FISH_ROLL_MEND_PONDS_BORN_BARREN (plan P13). The three vanilla water-body traps and the water-plant churn, offline.
//
// WHAT IS REAL vs PORTED: RM_WaterBodyMath.cs (roll sizes, split pieces, plant verdict, the fish memory book and the ORDER of
// the mends, RM_WaterBodyMend) is the PRODUCTION file, compiled in. The tracker below is a PORT of vanilla 1.6's
// RimWorld/WaterBodyTracker.cs (TryCreateBodyOrAddToExisting, RemoveCellFromExistingBody, FloodFillBody) and Verse/WaterBody.cs
// (Initialize -> SetFishTypes at the size then), read through RimSage on 2026-10-17, one water type, int cells; the fishing
// zone is reduced to its cells and settings. The capture-then-mend wrapper (Notify) restates RM_Patch_WaterBodyMend's prefix and
// postfix. Each trap is shown first on the bare port (mends off: the instrument can see the trap), then mended.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
	internal static class WaterBodyMendChecks
	{
		private static void Assert(bool ok, string msg)
		{
			if (!ok) throw new Exception(msg);
		}

		internal sealed class Body
		{
			public int root;
			public int cellCount;
			public HashSet<int> cells = new HashSet<int>();
			public List<string> common = new List<string>();
			public List<string> uncommon = new List<string>();
			public bool shouldHaveFish;
			public float population;
			public int type = 1;
			public bool HasFish => (common.Count > 0 || uncommon.Count > 0) && population > 0f;
			public float MaxPopulation => Math.Max(cellCount < 75 ? 0f : cellCount * 0.5f, 20f);
		}

		internal sealed class Zone
		{
			public int id;
			public HashSet<int> cells = new HashSet<int>();
			public string label;
			public int targetCount = 100;
			public bool registered = true;
		}

		/// <summary>The port of vanilla's tracker (see the header), plus the view the production mends drive.</summary>
		internal sealed class Model : RM_IWaterBodyView
		{
			public readonly int w, h;
			public readonly bool[] wet;
			public readonly List<Body> bodies = new List<Body>();
			public readonly Dictionary<int, Body> byCell = new Dictionary<int, Body>();
			public readonly Dictionary<int, Zone> zoneAt = new Dictionary<int, Zone>();
			public readonly List<Zone> zones = new List<Zone>();
			public readonly RM_FishMemoryBook book = new RM_FishMemoryBook();
			public RM_WaterMendFlags flags;
			public Func<double> rand = () => 0.0;   // 0 = every roll succeeds when its chance is above 0
			public readonly List<int> rollSizes = new List<int>();
			private int nextZone = 1;

			public Model(int w, int h, RM_WaterMendFlags flags)
			{
				this.w = w;
				this.h = h;
				wet = new bool[w * h];
				this.flags = flags;
			}

			public int Width => w;
			public int Height => h;
			public static RM_WaterMendFlags All => new RM_WaterMendFlags { rollOnGrowth = true, fishReturn = true, zoneReturn = true, split = true };
			public static RM_WaterMendFlags None => default;

			private IEnumerable<int> N4(int c)
			{
				int x = c % w, z = c / w;
				if (x > 0) yield return c - 1;
				if (x < w - 1) yield return c + 1;
				if (z > 0) yield return c - w;
				if (z < h - 1) yield return c + w;
			}

			// ── vanilla port ──
			private void SetFishTypes(Body b)
			{
				rollSizes.Add(b.cellCount);
				b.common.Clear();
				b.uncommon.Clear();
				b.shouldHaveFish = rand() < RM_WaterBodyMath.CommonChance(b.cellCount);
				if (b.shouldHaveFish)
				{
					b.common.Add("Fish_Common");
				}
			}

			/// <summary>ConstructBodies at map start: every wet cell flooded into bodies, then Initialize each (rolls at full size).</summary>
			public void Construct()
			{
				for (int c = 0; c < wet.Length; c++)
				{
					if (wet[c] && !byCell.ContainsKey(c))
					{
						TryCreateOrAdd(c);
					}
				}
				foreach (Body b in bodies)
				{
					b.population = b.MaxPopulation;
					SetFishTypes(b);
				}
			}

			private void TryCreateOrAdd(int c)
			{
				if (byCell.ContainsKey(c))
				{
					return;
				}
				Body into = null;
				foreach (int n in N4(c))
				{
					if (wet[n] && byCell.TryGetValue(n, out Body nb) && (into == null || nb.HasFish))
					{
						into = nb;
					}
				}
				if (into != null)
				{
					FloodFill(c, into);
					return;
				}
				var b = new Body { root = c, cellCount = 1 };
				bodies.Add(b);
				b.population = b.MaxPopulation;   // Initialize: population first, then the roll at size 1
				SetFishTypes(b);
				byCell[c] = b;
				b.cells.Add(c);
			}

			private void Remove(int c)
			{
				if (zoneAt.TryGetValue(c, out Zone z))
				{
					z.cells.Remove(c);
					zoneAt.Remove(c);
					if (z.cells.Count == 0)
					{
						z.registered = false;
						zones.Remove(z);
					}
				}
				if (wet[c] || !byCell.TryGetValue(c, out Body b))
				{
					return;
				}
				byCell.Remove(c);
				b.cells.Remove(c);
				b.cellCount--;
				if (b.cellCount == 0)
				{
					bodies.Remove(b);
				}
				else if (b.root == c)
				{
					b.root = byCell.First(kv => kv.Value == b).Key;
				}
			}

			private void FloodFill(int start, Body b)
			{
				var q = new Queue<int>();
				var seen = new HashSet<int> { start };
				q.Enqueue(start);
				while (q.Count > 0)
				{
					int x = q.Dequeue();
					if (byCell.TryGetValue(x, out Body other) && other == b)
					{
						continue;
					}
					if (!wet[x])
					{
						continue;
					}
					if (other != null && other != b)
					{
						bodies.Remove(other);
					}
					b.cellCount++;
					byCell[x] = b;
					b.cells.Add(x);
					foreach (int n in N4(x))
					{
						if (seen.Add(n))
						{
							q.Enqueue(n);
						}
					}
				}
			}

			/// <summary>A square turns wet or dry: vanilla's Notify_TerrainChanged with RM_Patch_WaterBodyMend's capture and mends.</summary>
			public void Set(int c, bool nowWet)
			{
				if (wet[c] == nowWet)
				{
					return;
				}
				// prefix capture
				byCell.TryGetValue(c, out Body before);
				int beforeSize = before?.cellCount ?? 0;
				RM_FishMemoryBook.Record fish = before != null ? Snapshot(before) : null;
				zoneAt.TryGetValue(c, out Zone zone);
				RM_FishMemoryBook.ZoneMemo memo = zone != null ? new RM_FishMemoryBook.ZoneMemo { zoneId = zone.id, label = zone.label, targetCount = zone.targetCount } : null;
				var nsize = new List<KeyValuePair<Body, int>>();
				foreach (int n in N4(c))
				{
					if (byCell.TryGetValue(n, out Body nb))
					{
						nsize.Add(new KeyValuePair<Body, int>(nb, nb.cellCount));
					}
				}
				// vanilla
				wet[c] = nowWet;
				if (nowWet) TryCreateOrAdd(c); else Remove(c);
				// postfix
				if (!nowWet)
				{
					if (memo != null)
					{
						memo.diedDry = zone.cells.Count == 0;
					}
					RM_WaterBodyMend.AfterDried(this, book, flags, c, before, fish, memo);
					return;
				}
				int sizeBefore = 0;
				if (byCell.TryGetValue(c, out Body now))
				{
					sizeBefore = now == before ? beforeSize : nsize.Where(kv => kv.Key == now).Select(kv => kv.Value).DefaultIfEmpty(0).Max();
				}
				RM_WaterBodyMend.AfterWet(this, book, flags, c, sizeBefore);
			}

			public Zone MakeZone(IEnumerable<int> cells, string label, int targetCount)
			{
				var z = new Zone { id = nextZone++, label = label, targetCount = targetCount };
				foreach (int c in cells)
				{
					z.cells.Add(c);
					zoneAt[c] = z;
				}
				zones.Add(z);
				return z;
			}

			public void DeleteZone(Zone z)
			{
				foreach (int c in z.cells) zoneAt.Remove(c);
				z.cells.Clear();
				z.registered = false;
				zones.Remove(z);
			}

			// ── RM_IWaterBodyView ──
			public object BodyAt(int cell) => byCell.TryGetValue(cell, out Body b) ? b : null;
			public bool BodyAlive(object body) => body is Body b && b.cellCount > 0 && bodies.Contains(b);
			public int SizeOf(object body) => ((Body)body).cellCount;
			public int RootOf(object body) => ((Body)body).root;
			public bool InBody(object body, int cell) => ((Body)body).cells.Contains(cell);
			public bool HasCommonFish(object body) => ((Body)body).common.Count > 0;
			public bool HasUncommonFish(object body) => ((Body)body).uncommon.Count > 0;
			public int WaterTypeOf(object body) => ((Body)body).type;

			public RM_FishMemoryBook.Record Snapshot(object body)
			{
				var b = (Body)body;
				var r = new RM_FishMemoryBook.Record { waterType = b.type, population = b.population };
				r.common.AddRange(b.common);
				r.uncommon.AddRange(b.uncommon);
				return r;
			}

			public void Restore(object body, RM_FishMemoryBook.Record r)
			{
				var b = (Body)body;
				b.common = new List<string>(r.common);
				b.uncommon = new List<string>(r.uncommon);
				b.shouldHaveFish = b.common.Count > 0;
				b.population = Math.Min(r.population, b.MaxPopulation);
			}

			public void RollCommon(object body)
			{
				var b = (Body)body;
				SetFishTypes(b);
				if (b.common.Count > 0)
				{
					b.population = b.MaxPopulation;
				}
			}

			public void RollUncommon(object body)
			{
				((Body)body).uncommon.Add("Fish_Uncommon");
			}

			public void SplitOff(object from, List<int> piece, int totalBefore)
			{
				var fb = (Body)from;
				var nb = new Body { root = piece[0], type = fb.type, common = new List<string>(fb.common), uncommon = new List<string>(fb.uncommon), shouldHaveFish = fb.shouldHaveFish };
				foreach (int c in piece)
				{
					fb.cells.Remove(c);
					nb.cells.Add(c);
					byCell[c] = nb;
				}
				nb.cellCount = piece.Count;
				fb.cellCount = fb.cells.Count;
				if (!fb.cells.Contains(fb.root)) fb.root = fb.cells.First();
				float share = totalBefore > 0 ? fb.population * piece.Count / totalBefore : 0f;
				nb.population = share;
				fb.population -= share;
				bodies.Add(nb);
			}

			public int RestoreZoneCell(int cell, RM_FishMemoryBook.ZoneMemo memo)
			{
				if (zoneAt.ContainsKey(cell))
				{
					return -1;
				}
				Zone z = zones.FirstOrDefault(q => q.id == memo.zoneId);
				if (z == null)
				{
					if (!memo.diedDry) return -1;
					z = MakeZone(Array.Empty<int>(), memo.label, memo.targetCount);
				}
				z.cells.Add(cell);
				zoneAt[cell] = z;
				return z.id;
			}

			public List<int> Sizes() => bodies.Select(b => b.cellCount).OrderBy(s => s).ToList();
		}

		/// <summary>True connected pieces of the wet cells (the oracle's own answer, here for the in-process checks).</summary>
		internal static List<int> TrueSizes(Model m)
		{
			var seen = new bool[m.wet.Length];
			var sizes = new List<int>();
			for (int c = 0; c < m.wet.Length; c++)
			{
				if (!m.wet[c] || seen[c]) continue;
				int n = 0;
				var q = new Queue<int>();
				q.Enqueue(c);
				seen[c] = true;
				while (q.Count > 0)
				{
					int x = q.Dequeue();
					n++;
					int cx = x % m.w, cz = x / m.w;
					foreach (int y in new[] { cx > 0 ? x - 1 : -1, cx < m.w - 1 ? x + 1 : -1, cz > 0 ? x - m.w : -1, cz < m.h - 1 ? x + m.w : -1 })
					{
						if (y >= 0 && m.wet[y] && !seen[y]) { seen[y] = true; q.Enqueue(y); }
					}
				}
				sizes.Add(n);
			}
			sizes.Sort();
			return sizes;
		}

		/// <summary>A pond grown square by square, row-major from a corner, to <paramref name="n"/> squares.</summary>
		private static Model Grow(int n, RM_WaterMendFlags f, Func<double> rand, int width = 20)
		{
			var m = new Model(width, (n + width - 1) / width + 2, f) { rand = rand };
			for (int i = 0; i < n; i++)
			{
				m.Set(i, true);
			}
			return m;
		}

		/// <summary>A fished pond present from map start (vanilla rolled it at full size): w×h, all wet, fish certain.</summary>
		private static Model Lake(int w, int h, RM_WaterMendFlags f)
		{
			var m = new Model(w, h, f);
			for (int i = 0; i < w * h; i++) m.wet[i] = true;
			m.Construct();
			return m;
		}

		public static void Run(Action<string, Action> Case)
		{
			Case("Fish_born_small_vanilla_never_rolls_again", () =>
			{
				Model m = Grow(250, Model.None, () => 0.0);
				Assert(m.bodies.Count == 1 && m.bodies[0].cellCount == 250, "one 250-square pond");
				Assert(m.bodies[0].common.Count == 0, "the bare port must reproduce trap (a): rolled once at 1 square, never again");
				Assert(m.rollSizes.SequenceEqual(new[] { 1 }), "vanilla rolled at sizes " + string.Join(",", m.rollSizes));
			});

			Case("Fish_born_small_mended_rolls_at_75_100_200", () =>
			{
				Model never = Grow(250, Model.All, () => 0.999);   // every roll fails until the chance is 1
				Assert(never.rollSizes.SequenceEqual(new[] { 1, 75, 100, 200 }), "rolled at " + string.Join(",", never.rollSizes));
				Assert(never.bodies[0].common.Count > 0, "certain at 200 squares");
				Model l1 = Grow(120, Model.All, () => 0.999);
				Assert(l1.rollSizes.SequenceEqual(new[] { 1, 75, 100 }) && l1.bodies[0].common.Count == 0,
					"the L1 row: grown 1 to 120 has rolled at 75 and 100 (no fish at 0.999): " + string.Join(",", l1.rollSizes));
				Model lucky = Grow(120, Model.All, () => 0.0);
				Assert(lucky.rollSizes.SequenceEqual(new[] { 1, 75 }) && lucky.bodies[0].common.Count > 0, "fish at the first roll that can give them, then no more rolls");
				Model at75 = Grow(75, Model.All, () => 0.0);
				Assert(at75.bodies[0].common.Count > 0 && Math.Abs(at75.bodies[0].population - at75.bodies[0].MaxPopulation) < 1e-3f,
					"a pond that gains fish starts full at that size, as vanilla's new bodies do");
			});

			Case("Fish_two_ponds_merging_past_100_roll", () =>
			{
				var m = new Model(30, 3, Model.All) { rand = () => 0.3 };   // 0.3 < 0.5 (at 100) but > 0.05 (at 75)
				for (int x = 0; x < 30; x++) { if (x != 15) { m.Set(x, true); m.Set(30 + x, true); } }
				for (int x = 0; x < 29; x++) if (x != 15) m.Set(60 + x, true);
				Assert(m.bodies.Count == 2 && m.bodies.All(b => b.common.Count == 0), "two fishless halves under 75");
				m.Set(15, true);
				Assert(m.bodies.Count == 1 && m.bodies[0].cellCount == 87, "joined: 87 squares, got " + string.Join(",", m.Sizes()));
				Assert(m.bodies[0].common.Count == 0, "87 crosses 75 only: 5% chance, roll 0.3 fails");
				var more = new Model(30, 3, Model.All) { rand = () => 0.3 };
				for (int i = 0; i < 90; i++) if (i % 30 != 15) more.Set(i, true);
				more.Set(15, true); more.Set(45, true); more.Set(75, true);
				Assert(more.bodies.Count == 1 && more.bodies[0].cellCount == 90, "one 90-square pond");
				Assert(more.bodies[0].common.Count == 0, "still under 100");
				var big = new Model(40, 3, Model.All) { rand = () => 0.3 };
				for (int i = 0; i < 120; i++) if (i % 40 != 20) big.Set(i, true);
				Assert(big.bodies.Count == 2, "two 60-square halves");
				big.Set(20, true);
				Assert(big.bodies.Count == 1 && big.bodies[0].cellCount == 118 && big.bodies[0].common.Count > 0,
					"60 + 57 + 1 = 118 passes 75 and 100 in one step: rolled at 118 (chance 0.59), 0.3 succeeds");
			});

			Case("Fish_drained_and_refilled_vanilla_loses_fish_and_zone", () =>
			{
				Model m = Lake(10, 10, Model.None);
				Assert(m.bodies[0].common.Count > 0, "a 100-square lake from map start has fish (roll 0 < 0.5)");
				m.MakeZone(new[] { 0, 1, 2, 10, 11, 12 }, "Fishing zone 1", 40);
				for (int i = 99; i >= 0; i--) m.Set(i, false);
				Assert(m.bodies.Count == 0 && m.zones.Count == 0, "dried out: no body, the zone deleted with its last square");
				for (int i = 0; i < 100; i++) m.Set(i, true);
				Assert(m.bodies.Count == 1 && m.bodies[0].common.Count == 0, "the bare port must reproduce trap (b): refilled, fishless");
				Assert(m.zones.Count == 0, "and no zone");
			});

			Case("Fish_drained_and_refilled_mended_same_fish_and_zone_back", () =>
			{
				Model m = Lake(10, 10, Model.All);
				m.bodies[0].common[0] = "Fish_Pike";
				m.bodies[0].uncommon.Add("Fish_Sturgeon");
				m.rand = () => 0.999;   // a fresh roll would give nothing: what comes back is the memory
				m.MakeZone(new[] { 0, 1, 2, 10, 11, 12 }, "Fishing zone 1", 40);
				for (int i = 99; i >= 0; i--) m.Set(i, false);
				Assert(m.bodies.Count == 0 && m.zones.Count == 0, "dried out as vanilla");
				m.Set(55, true);
				Assert(m.bodies.Count == 1 && m.bodies[0].common.SequenceEqual(new[] { "Fish_Pike" }) && m.bodies[0].uncommon.SequenceEqual(new[] { "Fish_Sturgeon" }),
					"the first refilled square brings back the same fish");
				for (int i = 0; i < 100; i++) m.Set(i, true);
				Assert(m.bodies.Count == 1 && m.bodies[0].common.SequenceEqual(new[] { "Fish_Pike" }), "full again, same fish");
				Assert(m.zones.Count == 1 && m.zones[0].cells.SetEquals(new[] { 0, 1, 2, 10, 11, 12 }), "the zone is back with its six squares");
				Assert(m.zones[0].label == "Fishing zone 1" && m.zones[0].targetCount == 40, "with its name and settings");
				m.book.Prune();
				Assert(m.book.fishByCell.Count == 0 && m.book.zoneByCell.Count == 0 && m.book.records.Count == 0 && m.book.zones.Count == 0,
					"nothing left in the book once every square is back");
			});

			Case("Fish_partial_dry_rejoins_live_zone_deleted_zone_stays_deleted", () =>
			{
				Model m = Lake(10, 10, Model.All);
				Zone z = m.MakeZone(new[] { 0, 1, 2 }, "Z", 100);
				m.Set(0, false);
				Assert(!z.cells.Contains(0) && z.registered, "the dried square left the zone, the zone lives");
				m.Set(0, true);
				Assert(z.cells.Contains(0) && m.zones.Count == 1, "it rejoins the same zone");
				m.Set(1, false);
				m.DeleteZone(z);
				m.Set(1, true);
				Assert(m.zones.Count == 0, "a zone the player deleted is never re-made");
				var off = Lake(10, 10, new RM_WaterMendFlags { rollOnGrowth = true, fishReturn = true, split = true });
				Zone z2 = off.MakeZone(new[] { 5 }, "Z2", 100);
				off.Set(5, false);
				off.Set(5, true);
				Assert(off.zones.Count == 0, "zone return off: the base game (the zone died with its square)");
			});

			Case("Fish_refill_veto_rolls_fresh_by_size", () =>
			{
				// Q5b (the veto): fish return off, roll on growth on: the refilled pond is treated as new.
				Model m = Lake(10, 10, new RM_WaterMendFlags { rollOnGrowth = true, zoneReturn = true, split = true });
				m.bodies[0].common[0] = "Fish_Pike";
				m.rand = () => 0.0;
				for (int i = 99; i >= 0; i--) m.Set(i, false);
				m.rollSizes.Clear();
				for (int i = 0; i < 100; i++) m.Set(i, true);
				Assert(m.bodies[0].common.SequenceEqual(new[] { "Fish_Common" }), "a fresh roll, not the remembered pike");
				Assert(m.rollSizes.SequenceEqual(new[] { 1, 75 }), "rolled at 1 (vanilla) and 75: " + string.Join(",", m.rollSizes));
			});

			Case("Body_split_vanilla_stays_one_mended_becomes_two", () =>
			{
				Model v = Lake(10, 3, Model.None);
				for (int z = 0; z < 3; z++) v.Set(z * 10 + 4, false);
				Assert(v.bodies.Count == 1 && TrueSizes(v).SequenceEqual(new[] { 12, 15 }), "the bare port must reproduce trap (c): one body over two pieces");
				Model m = Lake(10, 3, Model.All);
				m.bodies[0].common.Add("Fish_Common");   // 30 squares roll no fish at map start; give it some to follow
				float pop = m.bodies[0].population;
				for (int z = 0; z < 3; z++) m.Set(z * 10 + 4, false);
				Assert(m.Sizes().SequenceEqual(new[] { 12, 15 }), "two bodies of 12 and 15, got " + string.Join(",", m.Sizes()));
				Assert(m.bodies.All(b => b.common.SequenceEqual(new[] { "Fish_Common" })), "both keep the fish");
				Assert(m.bodies.All(b => b.cells.All(c => m.byCell[c] == b)), "every square indexed to its own body");
				float sum = m.bodies.Sum(b => b.population);
				Assert(Math.Abs(sum - pop) < 1e-3f, "population shared, not made: " + sum + " vs " + pop);
				for (int z = 0; z < 3; z++) m.Set(z * 10 + 4, true);
				Assert(m.Sizes().SequenceEqual(new[] { 30 }), "refilled: one body again");
			});

			Case("Body_split_stale_body_vanilla_throws_mended_clean", () =>
			{
				// Found by the oracle's sanity probe (mends off): an unsplit body whose one piece is later swallowed by another
				// body keeps its stale count and root; drying its root square then throws in RemoveCellFromExistingBody
				// ("Sequence contains no matching element", the same throw as FLOWWORKS_WATERBODY_DIAGNOSE_SOIL_THROW by another
				// road). Ported vanilla, not seen live. Strip 0..3 and a fished square at 5; dry 1; wet 4; dry 0.
				Model Build(RM_WaterMendFlags f)
				{
					var m = new Model(6, 1, f) { rand = () => 0.999 };
					foreach (int c in new[] { 0, 1, 2, 3, 5 }) m.wet[c] = true;
					m.Construct();
					Body a = m.byCell[5];
					a.common.Add("Fish_Pike");
					a.population = 20f;
					m.Set(1, false);
					m.Set(4, true);
					return m;
				}
				Model v = Build(Model.None);
				bool threw = false;
				try { v.Set(0, false); }
				catch (InvalidOperationException) { threw = true; }
				Assert(threw, "the bare port must throw on the stale root");
				Model m2 = Build(Model.All);
				m2.Set(0, false);
				Assert(m2.Sizes().SequenceEqual(new[] { 4 }) && m2.Sizes().SequenceEqual(TrueSizes(m2)), "mended: one body of 4 (2..5)");
			});

			Case("Body_split_round_an_island_is_no_split", () =>
			{
				// a ring of water round a 1-square island: taking one ring square leaves a C, still one piece
				var m = new Model(5, 5, Model.All);
				for (int i = 0; i < 25; i++) if (i != 12) m.wet[i] = true;
				m.Construct();
				m.Set(7, false);
				Assert(m.Sizes().SequenceEqual(new[] { 23 }), "23 squares, one body: " + string.Join(",", m.Sizes()));
				foreach (int c in new[] { 2, 17 })
				{
					m.Set(c, false);
					Assert(m.Sizes().SequenceEqual(TrueSizes(m)) && m.bodies.Count == 1, "still one ring after " + c + ": " + string.Join(",", m.Sizes()));
				}
				m.Set(22, false);
				Assert(m.Sizes().SequenceEqual(new[] { 10, 10 }), "cut through top and bottom: two sides of 10, got " + string.Join(",", m.Sizes()));
			});

			Case("Body_split_pieces_match_true_components_fuzz", () =>
			{
				var r = new Random(1313);
				int scenes = 0, splits = 0;
				for (int s = 0; s < 3000; s++)
				{
					int w = r.Next(2, 13), h = r.Next(2, 13);
					var m = new Model(w, h, Model.All) { rand = () => r.NextDouble() };
					double p = 0.4 + r.NextDouble() * 0.5;
					for (int i = 0; i < w * h; i++) m.wet[i] = r.NextDouble() < p;
					m.Construct();
					int steps = r.Next(1, 3 * w * h);
					for (int k = 0; k < steps; k++)
					{
						int before = m.bodies.Count;
						m.Set(r.Next(w * h), r.NextDouble() < 0.45);
						if (m.bodies.Count > before) splits++;
						List<int> want = TrueSizes(m);
						if (!m.Sizes().SequenceEqual(want))
							throw new Exception($"seed {s} step {k}: bodies {string.Join(",", m.Sizes())} vs pieces {string.Join(",", want)}");
						foreach (var kv in m.byCell)
							if (!kv.Value.cells.Contains(kv.Key) || !m.bodies.Contains(kv.Value))
								throw new Exception($"seed {s} step {k}: cell {kv.Key} indexed to a body that does not hold it");
					}
					scenes++;
				}
				Console.WriteLine($"      {scenes} scenes, {splits} steps that added a body");
				Assert(splits > 100, "the fuzz must actually split bodies (" + splits + ")");
			});

			Case("Body_split_local_test_never_misses", () =>
			{
				// SplitAfterRemoval's 8-ring shortcut against a full component count on every cell of random grids
				var r = new Random(77);
				int checks = 0, walked = 0, realSplits = 0;
				for (int s = 0; s < 2000; s++)
				{
					int w = r.Next(1, 10), h = r.Next(1, 10);
					var g = new bool[w * h];
					for (int i = 0; i < g.Length; i++) g[i] = r.NextDouble() < 0.6;
					for (int c = 0; c < g.Length; c++)
					{
						if (!g[c]) continue;
						var before = Pieces(g, w, h);
						int whose = before.FindIndex(pc => pc.Contains(c));
						g[c] = false;
						var after = Pieces(g, w, h);
						int want = after.Count - before.Count + 1;   // pieces the removed square's body became (0 when it was alone)
						var got = RM_WaterBodyMath.SplitAfterRemoval(c, w, h, x => g[x]);
						if (want >= 2) realSplits++;
						int gotN = got == null ? (before[whose].Count == 1 ? 0 : 1) : got.Count;
						if (gotN != want) throw new Exception($"seed {s} cell {c}: {gotN} pieces, want {want}");
						if (got != null) walked++;
						g[c] = true;
						checks++;
					}
				}
				Console.WriteLine($"      {checks} removals, {walked} walked, {realSplits} real splits");
				// review 2026-10-22: can-fail on the input, so a generator that never cuts a piece in two cannot pass silently
				Assert(realSplits > 0, "the random grids must contain removals that really split a piece (" + realSplits + ")");
			});

			Case("Plants_pump_cycle_reeds_live_dry_spell_kills_after_grace", () =>
			{
				const float tol = RM_WaterBodyMath.DefaultPlantDeepToleranceMetres;
				int grace = (int)(RM_WaterBodyMath.DefaultPlantGraceHours * RM_WaterBodyMath.TicksPerHour);
				int since = -1;
				// pump raises a pond square from 0.5 m to 2.6 m (WaterDeep: no shallow tags) and back, every 6 hours, for 10 days
				for (int t = 0; t < 10 * 60000; t += 2000)
				{
					bool high = (t / 15000) % 2 == 1;
					bool suits = !high;
					float metres = high ? 2.6f : 0.5f;
					Assert(RM_WaterBodyMath.PlantLivesOn(suits, true, metres, tol, grace, t, ref since), "reeds die at tick " + t);
				}
				Assert(!RM_WaterBodyMath.PlantLivesOn(false, false, 2.6f, tol, grace, 0, ref since), "an unmanaged square: vanilla (dies)");
				since = -1;
				Assert(RM_WaterBodyMath.PlantLivesOn(false, true, 0f, tol, grace, 1000, ref since) && since == 1000, "dry: the spell starts");
				Assert(RM_WaterBodyMath.PlantLivesOn(false, true, 0f, tol, grace, 1000 + grace - 1, ref since), "alive just inside 24 h");
				Assert(!RM_WaterBodyMath.PlantLivesOn(false, true, 0f, tol, grace, 1000 + grace, ref since), "dry 24 h: withers (vanilla's slow death)");
				since = -1;
				RM_WaterBodyMath.PlantLivesOn(false, true, 0f, tol, grace, 0, ref since);
				RM_WaterBodyMath.PlantLivesOn(true, true, 0.5f, tol, grace, 30000, ref since);
				Assert(since == -1 && RM_WaterBodyMath.PlantLivesOn(false, true, 0f, tol, grace, 30000 + grace - 1, ref since), "water back in time: the spell restarts");
				since = -1;
				Assert(RM_WaterBodyMath.PlantLivesOn(false, true, 3.4f, tol, grace, 0, ref since) && since == 0, "3.4 m: past 3 m, the spell starts");
				Assert(!RM_WaterBodyMath.PlantLivesOn(false, true, 3.4f, tol, grace, grace, ref since), "too deep for a day: dies");
			});

			Case("WaterMend_settings_wired_and_shipped_on", () =>
			{
				string mod = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
				string game = RiverSwitchFlipChecks.Src("RM_WaterBodyMendGame.cs");
				string flip = RiverSwitchFlipChecks.Src("RM_WaterBodyTypeFlipFix.cs");
				Assert(mod.Contains("RM_WaterMendSettings.ExposeData();") && mod.Contains("RM_WaterMendSettings.DoSettingsSection);"), "settings saved and drawn");
				foreach (string f in new[] { "waterBodyMendsEnabled", "fishRollOnGrowth", "fishReturnOnRefill", "fishingZoneReturnOnRefill", "waterBodySplitEnabled", "waterPlantGraceEnabled" })
				{
					Assert(game.Contains("public static bool " + f + " = true;"), f + " ships on");
					Assert(game.Contains("ref " + f + ", \"" + f + "\", true)"), f + " saved with default true");
				}
				Assert(game.Contains("[HarmonyPatch(typeof(WaterBodyTracker), nameof(WaterBodyTracker.Notify_TerrainChanged))]")
					&& game.Contains("[HarmonyPatch(typeof(TerrainGrid), \"DoTerrainChangedEffects\")]")
					&& game.Contains("[HarmonyPatch(typeof(Plant), nameof(Plant.DyingBecauseOfTerrainTags), MethodType.Getter)]"), "the three patch targets");
				Assert(game.Contains("Current.ProgramState != ProgramState.Playing"), "never during map generation");
				Assert(flip.Contains("RM_Patch_WaterBodyMend.SplitAfterDetach(__instance, cell, body);"), "a type flip that cuts a body splits it too");
			});
		}

		private static List<HashSet<int>> Pieces(bool[] g, int w, int h)
		{
			var seen = new bool[g.Length];
			var list = new List<HashSet<int>>();
			for (int c = 0; c < g.Length; c++)
			{
				if (!g[c] || seen[c]) continue;
				var set = new HashSet<int>();
				var q = new Queue<int>();
				q.Enqueue(c);
				seen[c] = true;
				while (q.Count > 0)
				{
					int x = q.Dequeue();
					set.Add(x);
					int cx = x % w, cz = x / w;
					foreach (int y in new[] { cx > 0 ? x - 1 : -1, cx < w - 1 ? x + 1 : -1, cz > 0 ? x - w : -1, cz < h - 1 ? x + w : -1 })
						if (y >= 0 && g[y] && !seen[y]) { seen[y] = true; q.Enqueue(y); }
				}
				list.Add(set);
			}
			return list;
		}

		/// <summary>Oracle mode "bodies" (selftest_flowworks_kernel_oracle.py): each line "w h p0 ... | c wet c wet ..." (initial
		/// wet cells, then toggles); prints the sorted body sizes after every toggle, ";" between steps.</summary>
		public static int OracleRun(TextReader input, TextWriter output)
		{
			string line;
			while ((line = input.ReadLine()) != null)
			{
				if (string.IsNullOrWhiteSpace(line)) continue;
				string[] halves = line.Split('|');
				int[] head = halves[0].Split(' ', StringSplitOptions.RemoveEmptyEntries).Select(int.Parse).ToArray();
				int[] ops = halves.Length > 1 ? halves[1].Split(' ', StringSplitOptions.RemoveEmptyEntries).Select(int.Parse).ToArray() : Array.Empty<int>();
				var m = new Model(head[0], head[1], Model.All);
				for (int i = 2; i < head.Length; i++) m.wet[head[i]] = true;
				m.Construct();
				var steps = new List<string>();
				for (int i = 0; i + 1 < ops.Length; i += 2)
				{
					m.Set(ops[i], ops[i + 1] == 1);
					steps.Add(string.Join(",", m.Sizes()));
				}
				output.WriteLine(string.Join(";", steps));
			}
			return 0;
		}
	}
}
