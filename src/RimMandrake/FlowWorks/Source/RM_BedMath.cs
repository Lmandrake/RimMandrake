using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// POND_ELEVATION_BUILD_LAKES_RUN_DEEP (design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md §9; owner by card
	/// 2026-10-15, "Deeper ponds (lakes deeper than 4) ... Today? → Build it today"). Owner, 2026-10-12: <i>"There's nothing
	/// wrong with saying the center of ponds or especially large rivers and lakes and oceans might go down way past 4."</i>
	///
	/// Three pieces, all Verse-free so Source/SelfTest/ compiles THIS production file:
	/// <list type="bullet">
	/// <item>The floor: RM_LakeFloorMath (LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP, owner R11), per lake and per the map's
	/// roughness, recorded once at formation. Its way-out pass keeps owner ruling 4 (<i>"Natural ponds and lakes when pumped
	/// dry would leave just such gradual terrain so no chance to fall in and get stuck"</i>) for people.</item>
	/// <item>§9.3 the drawdown: a pond's stock covers a number of LEVELS (stock ÷ the fill-units one level is worth), and its
	/// wet squares are the ones whose beds those levels fill. Recession sheds the SHALLOWEST bed first (the rim, then the
	/// shelves, the deep middle last, as a real lake drops), then the old outside-in order; Restore re-wets last-in-first-out,
	/// each square only when its whole bed fits, so a refilled pond is the exact old shape.</item>
	/// <item><see cref="RM_RecessionSet"/>: the recession's live set on map-indexed arrays, so a 40,000-square lake sheds a
	/// cell in one pass over a list instead of a dictionary rebuilt and rescanned per cell.</item>
	/// </list>
	/// </summary>
	public static class RM_BedMath
	{
		/// <summary>The deepest natural floor by default, in notches (100 = 50 m). Mod Setting "deepBedMaxDepth". Each lake's floor
		/// is RM_LakeFloorMath's (LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP, owner R11), which replaced §9.4's radial slope.</summary>
		public const int DefaultMaxBedDepth = RM_LakeFloorMath.DefaultCeilingNotches;

		/// <summary>The bed record is a byte grid; nothing deeper is storable.</summary>
		public const int MaxStorableDepth = 250;

		/// <summary>LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (owner D2 by card 2026-10-17: the lake floor ceiling is settable to 125 m):
		/// the top of the "deepBedMaxDepth" slider, in notches (250 = 125 m, the byte grid's limit).</summary>
		public const int MaxBedCeiling = MaxStorableDepth;

		/// <summary>The old flood-fill cap (RM_LiquidStock.MaxBodyCells): a body bigger than this was limitless whatever it
		/// touched. Kept for oceans; an inland lake is now walked up to <see cref="DefaultDrainableLakeCells"/>.</summary>
		public const int OceanWalkCells = 4000;

		/// <summary>Mod Setting "drainableLakeMaxCells" default: an inland (not edge-touching) body up to this many squares is
		/// a drainable lake. A 250×250 map has 62,500 squares.</summary>
		public const int DefaultDrainableLakeCells = 40000;

		/// <summary>The whole levels a stock covers: stock ÷ <paramref name="levelUnit"/> (fill-units per level), floored,
		/// with a hair of slack so a full pond (stock == capacity) never reads one level short to float rounding.</summary>
		public static int SupportedLevels(float stock, float levelUnit)
		{
			if (!(levelUnit > 0f) || !(stock > 0f))
			{
				return 0;
			}
			double v = (double)stock / levelUnit + 1e-4;
			return v >= int.MaxValue ? int.MaxValue : (int)Math.Floor(v);
		}

		/// <summary>Recession: shed another wet square while the wet beds hold more levels than the stock covers — except the
		/// last wet square of a body that still has stock, when <paramref name="keepLast"/> (LIQUID_RECESSION_TOPOLOGY_1).</summary>
		public static bool ShouldShed(long wetLevels, int wetCells, int supportedLevels, float stock, bool keepLast)
		{
			if (wetCells <= 0 || wetLevels <= supportedLevels)
			{
				return false;
			}
			return !(keepLast && stock > 0f && wetCells <= 1);
		}

		/// <summary>Restore: re-wet a dried square of <paramref name="bed"/> levels when its whole bed fits in the stock beside
		/// the squares already wet (so a refill never shows water it has not got), or when it would be the only wet square
		/// of a body with stock (keepLast, the mirror of <see cref="ShouldShed"/>).</summary>
		public static bool CanRestore(long wetLevels, int wetCells, int bed, int supportedLevels, float stock, bool keepLast)
		{
			if (wetLevels + bed <= supportedLevels)
			{
				return true;
			}
			return keepLast && wetCells == 0 && stock > 0f;
		}

		/// <summary>Fill-units one bed level is worth in a body: capacity ÷ the footprint's bed sum at formation, kept on the
		/// body so digging squares out and filling them back in, in any order, scales capacity exactly
		/// (POND_CAPACITY_FIX_DOUBLING_BED).</summary>
		public static float LevelUnit(float capacity, int bedSum)
		{
			return bedSum > 0 && capacity > 0f ? capacity / bedSum : 0f;
		}

		/// <summary>A body's capacity for a footprint whose beds sum to <paramref name="bedSum"/>: always the same level unit
		/// times the beds, so it is a function of WHICH squares are in the pond, never of the order they left and came back.</summary>
		public static float CapacityForBeds(float levelUnit, int bedSum)
		{
			return bedSum > 0 && levelUnit > 0f ? levelUnit * bedSum : 0f;
		}

		/// <summary>A footprint in 4 bytes a square (x, z as little-endian ushort), in list order (the order is the recession
		/// stack's). RM_LiquidBody saves a body past <see cref="OceanWalkCells"/> squares this way (deflated by the Scribe).</summary>
		public static byte[] PackXZ(int count, Func<int, int> x, Func<int, int> z)
		{
			byte[] b = new byte[Math.Max(0, count) * 4];
			for (int k = 0; k < count; k++)
			{
				int vx = x(k), vz = z(k);
				b[k * 4] = (byte)vx;
				b[k * 4 + 1] = (byte)(vx >> 8);
				b[k * 4 + 2] = (byte)vz;
				b[k * 4 + 3] = (byte)(vz >> 8);
			}
			return b;
		}

		public static int PackedCount(byte[] b)
		{
			return b == null ? 0 : b.Length / 4;
		}

		public static int PackedX(byte[] b, int k)
		{
			return b[k * 4] | (b[k * 4 + 1] << 8);
		}

		public static int PackedZ(byte[] b, int k)
		{
			return b[k * 4 + 2] | (b[k * 4 + 3] << 8);
		}

		/// <summary>The recession order with the drawdown key in front of §5's: a square feeding a dug channel recedes last
		/// (POND_RECESSION_STRANDS_CHANNEL_1), then the SHALLOWER bed first, then fewest neighbours, furthest from the centroid,
		/// lowest index (RM_StockMath.PrefersCandidate). With every bed equal this is exactly the old order.</summary>
		public static bool PrefersCandidate(bool outflow, int bed, int neighbours, int distSquared, int cellIndex,
			bool bestOutflow, int bestBed, int bestNeighbours, int bestDistSquared, int bestCellIndex)
		{
			if (outflow != bestOutflow)
			{
				return !outflow;
			}
			if (bed != bestBed)
			{
				return bed < bestBed;
			}
			return RM_StockMath.PrefersCandidate(neighbours, distSquared, cellIndex, bestNeighbours, bestDistSquared, bestCellIndex);
		}
	}

	/// <summary>
	/// POND_ELEVATION_BUILD_LAKES_RUN_DEEP: one body's wet squares during a pulse's recession, on map-sized arrays reused across
	/// bodies and pulses (one instance per RM_LiquidStock, i.e. per map: no session-wide state). Same picks as the
	/// LIQUID_RECESSION_TOPOLOGY_1 dictionary walk it replaces (order-free keys, the same local 3×3 test and bounded whole-body
	/// split check), plus the bed key. Verse-free; cell index = z × width + x.
	/// </summary>
	public sealed class RM_RecessionSet
	{
		private int width, height;
		private byte[] live;       // 1 = wet square of the body being worked
		private byte[] neighbours; // 8-way wet neighbours
		private byte[] feeds;      // 1 = feeds a dug channel (recedes last)
		private int[] bedOf;
		private int[] slot;        // position in `cells`
		private int[] seenStamp;
		private int[] cutMark;     // == stamp: an articulation point of the live set (MarkCuts)
		private int[] disc, low, parent;
		private byte[] iter;
		private readonly List<int> dfs = new List<int>();
		private int stamp;
		private readonly List<int> cells = new List<int>();
		private readonly Queue<int> bfs = new Queue<int>();
		private readonly List<int> unsafeLocal = new List<int>();
		private int cx, cz;

		/// <summary>Σ bed levels over the wet squares.</summary>
		public long WetLevels { get; private set; }

		/// <summary>Wet squares.</summary>
		public int Count => cells.Count;

		/// <summary>Σ bed levels over the WHOLE footprint (wet or not): the denominator of the level unit.</summary>
		public long FootprintLevels { get; private set; }

		/// <summary>How many whole-body split checks one pick may run (as before).</summary>
		public const int GlobalSplitChecks = 4;

		/// <summary>Set up for one body. <paramref name="footprint"/>: every footprint square (the centroid is over all of
		/// them, as before); <paramref name="wet"/>: still natural liquid; <paramref name="bed"/>: its bed levels;
		/// <paramref name="feedsChannel"/>: null = no square is spared.</summary>
		public void Begin(int width, int height, IList<int> footprint, Func<int, bool> wet, Func<int, int> bed, Func<int, bool> feedsChannel)
		{
			Clear();
			int n = width * height;
			if (live == null || live.Length != n)
			{
				live = new byte[n];
				neighbours = new byte[n];
				feeds = new byte[n];
				bedOf = new int[n];
				slot = new int[n];
				seenStamp = new int[n];
				cutMark = new int[n];
				disc = new int[n];
				low = new int[n];
				parent = new int[n];
				iter = new byte[n];
				stamp = 0;
			}
			this.width = width;
			this.height = height;
			long sx = 0, sz = 0;
			long all = 0;
			for (int k = 0; k < footprint.Count; k++)
			{
				int i = footprint[k];
				if (i < 0 || i >= n)
				{
					continue;
				}
				sx += i % width;
				sz += i / width;
				int b = bed(i);
				all += b;
				if (live[i] == 0 && wet(i))
				{
					live[i] = 1;
					bedOf[i] = b;
					slot[i] = cells.Count;
					cells.Add(i);
					WetLevels += b;
				}
			}
			FootprintLevels = all;
			// Centroid(body) of the old walk: integer mean over EVERY footprint square (truncated, coordinates are ≥ 0).
			cx = footprint.Count > 0 ? (int)(sx / footprint.Count) : 0;
			cz = footprint.Count > 0 ? (int)(sz / footprint.Count) : 0;
			for (int k = 0; k < cells.Count; k++)
			{
				int i = cells[k];
				int x = i % width, z = i / width;
				int c = 0;
				for (int dz = -1; dz <= 1; dz++)
				{
					for (int dx = -1; dx <= 1; dx++)
					{
						if ((dx != 0 || dz != 0) && IsLive(x + dx, z + dz))
						{
							c++;
						}
					}
				}
				neighbours[i] = (byte)c;
				feeds[i] = (byte)(feedsChannel != null && feedsChannel(i) ? 1 : 0);
			}
		}

		/// <summary>Forget the current body (marks cleared; arrays kept).</summary>
		public void Clear()
		{
			for (int k = 0; k < cells.Count; k++)
			{
				live[cells[k]] = 0;
			}
			cells.Clear();
			WetLevels = 0;
			FootprintLevels = 0;
		}

		public bool IsLive(int x, int z)
		{
			return x >= 0 && z >= 0 && x < width && z < height && live[z * width + x] != 0;
		}

		public int BedOf(int i)
		{
			return bedOf[i];
		}

		/// <summary>The next square to dry, or -1 when none can go without splitting the body.</summary>
		public int Pick(bool useBeds)
		{
			int best = -1;
			bool bestOut = true;
			int bestBed = int.MaxValue, bestN = int.MaxValue, bestDist = -1, bestIdx = int.MaxValue;
			unsafeLocal.Clear();
			for (int k = 0; k < cells.Count; k++)
			{
				int c = cells[k];
				int x = c % width, z = c / width;
				int dist = (x - cx) * (x - cx) + (z - cz) * (z - cz);
				bool f = feeds[c] != 0;
				int b = useBeds ? bedOf[c] : 0;
				if (!RM_BedMath.PrefersCandidate(f, b, neighbours[c], dist, c, bestOut, bestBed, bestN, bestDist, bestIdx))
				{
					continue;
				}
				if (!RM_StockMath.LocalRemovalKeepsConnected(RingMask(x, z)))
				{
					unsafeLocal.Add(c);
					continue;
				}
				bestOut = f;
				bestBed = b;
				bestN = neighbours[c];
				bestDist = dist;
				bestIdx = c;
				best = c;
			}
			if (best >= 0 && unsafeLocal.Count > 0)
			{
				// DRAWDOWN_DIAGNOSE_THIRTEEN_BEFORE_TWELVE: a locally-unsafe square (its 8-ring reads as two wet arcs) with a
				// better (outflow, bed) key than the best safe one is often safe for the whole body: a rough floor's loops close
				// the arcs elsewhere. Taking the deeper safe square instead dried bed 13 while bed 12 stayed wet. One
				// articulation-point pass (O(wet squares)) decides them all exactly; it runs only when the bed key is at stake,
				// so equal beds keep the old order and cost.
				int alt = -1;
				for (int k = 0; k < unsafeLocal.Count; k++)
				{
					int c = unsafeLocal[k];
					if (!KeyBetter(feeds[c] != 0, useBeds ? bedOf[c] : 0, bestOut, bestBed))
					{
						continue;
					}
					if (alt < 0)
					{
						MarkCuts();
					}
					if (cutMark[c] == stamp)
					{
						continue;
					}
					if (alt < 0 || RM_BedMath.PrefersCandidate(feeds[c] != 0, useBeds ? bedOf[c] : 0, neighbours[c], Dist(c), c,
						feeds[alt] != 0, useBeds ? bedOf[alt] : 0, neighbours[alt], Dist(alt), alt))
					{
						alt = c;
					}
				}
				return alt >= 0 ? alt : best;
			}
			if (best >= 0 || unsafeLocal.Count == 0)
			{
				return best;
			}
			// Every candidate failed the local test (a one-wide ring or snake): check a few of the best against the whole body.
			unsafeLocal.Sort((a, b) =>
			{
				if (a == b) return 0;
				return RM_BedMath.PrefersCandidate(feeds[a] != 0, useBeds ? bedOf[a] : 0, neighbours[a], Dist(a), a,
					feeds[b] != 0, useBeds ? bedOf[b] : 0, neighbours[b], Dist(b), b) ? -1 : 1;
			});
			int before = ComponentCount(-1);
			for (int i = 0; i < unsafeLocal.Count && i < GlobalSplitChecks; i++)
			{
				if (ComponentCount(unsafeLocal[i]) <= before)
				{
					return unsafeLocal[i];
				}
			}
			return -1;
		}

		private static bool KeyBetter(bool outflow, int bed, bool bestOutflow, int bestBed)
		{
			if (outflow != bestOutflow)
			{
				return !outflow;
			}
			return bed < bestBed;
		}

		/// <summary>Marks every articulation point of the live set's 8-way graph (cutMark[i] == stamp after the call): the squares
		/// whose removal would split a piece of the body. Iterative Tarjan, so a 40,000-square lake cannot overflow the stack.</summary>
		private void MarkCuts()
		{
			if (++stamp == int.MaxValue)
			{
				Array.Clear(seenStamp, 0, seenStamp.Length);
				Array.Clear(cutMark, 0, cutMark.Length);
				stamp = 1;
			}
			int time = 0;
			for (int r = 0; r < cells.Count; r++)
			{
				int root = cells[r];
				if (seenStamp[root] == stamp)
				{
					continue;
				}
				int rootChildren = 0;
				seenStamp[root] = stamp;
				disc[root] = low[root] = ++time;
				parent[root] = -1;
				iter[root] = 0;
				dfs.Clear();
				dfs.Add(root);
				while (dfs.Count > 0)
				{
					int v = dfs[dfs.Count - 1];
					if (iter[v] < 8)
					{
						int k = iter[v]++;
						int ux = v % width + RingX[k], uz = v / width + RingZ[k];
						if (!IsLive(ux, uz))
						{
							continue;
						}
						int u = uz * width + ux;
						if (seenStamp[u] != stamp)
						{
							seenStamp[u] = stamp;
							disc[u] = low[u] = ++time;
							parent[u] = v;
							iter[u] = 0;
							dfs.Add(u);
							if (v == root)
							{
								rootChildren++;
							}
						}
						else if (u != parent[v] && disc[u] < low[v])
						{
							low[v] = disc[u];
						}
						continue;
					}
					dfs.RemoveAt(dfs.Count - 1);
					int p = parent[v];
					if (p < 0)
					{
						continue;
					}
					if (low[v] < low[p])
					{
						low[p] = low[v];
					}
					if (p != root && low[v] >= disc[p])
					{
						cutMark[p] = stamp;
					}
				}
				if (rootChildren > 1)
				{
					cutMark[root] = stamp;
				}
			}
		}

		/// <summary>The square dried: out of the live set, its neighbours' counts down, its bed out of the wet levels.</summary>
		public void Remove(int c)
		{
			if (c < 0 || live[c] == 0)
			{
				return;
			}
			live[c] = 0;
			WetLevels -= bedOf[c];
			int s = slot[c];
			int last = cells[cells.Count - 1];
			cells[s] = last;
			slot[last] = s;
			cells.RemoveAt(cells.Count - 1);
			int x = c % width, z = c / width;
			for (int dz = -1; dz <= 1; dz++)
			{
				for (int dx = -1; dx <= 1; dx++)
				{
					if ((dx != 0 || dz != 0) && IsLive(x + dx, z + dz))
					{
						neighbours[(z + dz) * width + x + dx]--;
					}
				}
			}
		}

		private int Dist(int c)
		{
			int x = c % width, z = c / width;
			return (x - cx) * (x - cx) + (z - cz) * (z - cz);
		}

		// Ring order N, NE, E, SE, S, SW, W, NW (RM_StockMath.LocalRemovalKeepsConnected's bit order).
		private static readonly int[] RingX = { 0, 1, 1, 1, 0, -1, -1, -1 };
		private static readonly int[] RingZ = { 1, 1, 0, -1, -1, -1, 0, 1 };

		private int RingMask(int x, int z)
		{
			int mask = 0;
			for (int k = 0; k < 8; k++)
			{
				if (IsLive(x + RingX[k], z + RingZ[k]))
				{
					mask |= 1 << k;
				}
			}
			return mask;
		}

		/// <summary>8-way components of the live set with <paramref name="without"/> (-1 = none) left out.</summary>
		private int ComponentCount(int without)
		{
			if (++stamp == int.MaxValue)
			{
				Array.Clear(seenStamp, 0, seenStamp.Length);
				Array.Clear(cutMark, 0, cutMark.Length);
				stamp = 1;
			}
			int comps = 0;
			for (int k = 0; k < cells.Count; k++)
			{
				int s = cells[k];
				if (s == without || seenStamp[s] == stamp)
				{
					continue;
				}
				comps++;
				seenStamp[s] = stamp;
				bfs.Enqueue(s);
				while (bfs.Count > 0)
				{
					int c = bfs.Dequeue();
					int x = c % width, z = c / width;
					for (int dz = -1; dz <= 1; dz++)
					{
						for (int dx = -1; dx <= 1; dx++)
						{
							if ((dx == 0 && dz == 0) || !IsLive(x + dx, z + dz))
							{
								continue;
							}
							int m = (z + dz) * width + x + dx;
							if (m != without && seenStamp[m] != stamp)
							{
								seenStamp[m] = stamp;
								bfs.Enqueue(m);
							}
						}
					}
				}
			}
			return comps;
		}
	}
}
