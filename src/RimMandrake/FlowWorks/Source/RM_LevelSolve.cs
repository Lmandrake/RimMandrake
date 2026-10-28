using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES (plan P3 of FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG). Owner, 2026-10-17: <i>"We need
	/// VERY smooth water. That's water's one primary characteristic: a level surface."</i> Ruled exactly level by card the same
	/// day (design/RimMandrake/flowworks_level_surface_2026-10-17.md, Option 1).
	///
	/// The fill-and-spill solve that gives each connected body of water ONE surface, exact to the decilitre. Verse-free, so
	/// Source/SelfTest/ compiles THIS file; its Python twin is northstar/level_water.py (<c>solve</c>), and the two are
	/// differential-tested to the dL (selftest_flowworks_kernel_oracle.py, mode "exact"): same integer arithmetic, same key
	/// order, same tie-breaks.
	/// <list type="bullet">
	/// <item>Water is in decilitres. <see cref="U"/> = one 0.5 m notch over one 2 m² square (1,000 L).</item>
	/// <item>A node is a dug square (D notches, holding up to D·U) or a POND (its floor histogram H[L] = squares whose bed is
	/// at least L notches; it holds up to U·ΣH and fills its deepest band first). Band L is the layer between L−1 and L
	/// notches below ground.</item>
	/// <item>An edge joins two nodes down to band <c>cap</c> (two squares: the shallower one's depth; a square and a pond: the
	/// shallower of the square and the pond's shore square). At each band the nodes that reach it split into pieces connected
	/// by edges that reach it.</item>
	/// <item>Bottom up, a piece counts the water already at or below its band (trapped behind its sill). Top down, it fills its
	/// deeper pieces in key order, then lays what is left EVENLY over every node of its band (a pond weighs its H[L] squares),
	/// the remainder dL one each in key order. Every piece ends with one surface; water never climbs a sill; nothing is
	/// created or lost (checked: a solve that would not conserve is refused).</item>
	/// </list>
	/// Node order IS key order: the caller adds nodes sorted by their key.
	/// </summary>
	public sealed class RM_LevelSolve
	{
		/// <summary>Decilitres in one notch over one square (RM_Volume.UnitsPerLevel: 1,000 L = 10,000 dL).</summary>
		public const int U = RM_Volume.UnitsPerLevel;

		/// <summary>Metres of surface per decilitre over one square (0.5 m / U).</summary>
		public const double MetresPerUnit = 0.5 / U;

		private int n;
		private bool[] isPond = new bool[16];
		private int[] depth = new int[16];
		private int[][] hist = new int[16][];
		private long[][] suffix = new long[16][];
		private long[] water = new long[16];
		private long[] result = new long[16];
		// STEPPULSE_SHRINK_STEADY_SLICE_COST: edges kept flat and laid out per node (CSR) once a solve, instead of two List<int>
		// per node: the band walks below were most of the exact pulse's cost. A piece's members, numbering and children never
		// depended on neighbour order (pieces are numbered by their lowest node), so the result is the same to the dL.
		private int edgeCount;
		private int[] edgeA = new int[16];
		private int[] edgeB = new int[16];
		private int[] edgeCap = new int[16];
		private int[] adjStart = new int[17];
		private int[] adjNode = new int[32];
		private int[] adjEdgeCap = new int[32];

		private sealed class Piece
		{
			public int band;
			public readonly List<int> members = new List<int>();
			public readonly List<int> children = new List<int>();
			public long water;
			public long cap;
		}

		private readonly List<Piece> pieces = new List<Piece>();
		private int pieceCount;
		private int[] prevPiece = new int[16];
		private int[] curPiece = new int[16];
		private readonly List<int> bfs = new List<int>();

		public int Count => n;

		public void Clear()
		{
			n = 0;
			edgeCount = 0;
		}

		private void Grow()
		{
			int cap = Math.Max(16, isPond.Length * 2);
			Array.Resize(ref isPond, cap);
			Array.Resize(ref depth, cap);
			Array.Resize(ref hist, cap);
			Array.Resize(ref suffix, cap);
			Array.Resize(ref water, cap);
			Array.Resize(ref result, cap);
			Array.Resize(ref prevPiece, cap);
			Array.Resize(ref curPiece, cap);
		}

		private int AddNode(bool pond, int d, int[] h, long w)
		{
			if (n == isPond.Length)
			{
				Grow();
			}
			int i = n++;
			isPond[i] = pond;
			depth[i] = d;
			hist[i] = h;
			water[i] = w;
			result[i] = 0;
			if (pond)
			{
				long[] s = suffix[i];
				if (s == null || s.Length < h.Length + 1)
				{
					s = suffix[i] = new long[h.Length + 1];
				}
				s[h.Length] = 0;
				for (int l = h.Length - 1; l >= 1; l--)
				{
					s[l] = s[l + 1] + h[l];
				}
				s[0] = h.Length > 1 ? s[1] : 0;
			}
			return i;
		}

		/// <summary>A dug square of <paramref name="d"/> notches holding <paramref name="w"/> dL. Returns its node index.</summary>
		public int AddCell(int d, long w)
		{
			return AddNode(false, d, null, w);
		}

		/// <summary>A pond over histogram <paramref name="h"/> (H[L], L = 0..maxBed) holding <paramref name="w"/> dL (at most its
		/// capacity). The array is read, never kept past the next <see cref="Clear"/>.</summary>
		public int AddPond(int[] h, long w)
		{
			return AddNode(true, 0, h, w);
		}

		public void AddEdge(int a, int b, int cap)
		{
			if (edgeCount == edgeA.Length)
			{
				int grown = edgeA.Length * 2;
				Array.Resize(ref edgeA, grown);
				Array.Resize(ref edgeB, grown);
				Array.Resize(ref edgeCap, grown);
			}
			edgeA[edgeCount] = a;
			edgeB[edgeCount] = b;
			edgeCap[edgeCount] = cap;
			edgeCount++;
		}

		/// <summary>Lays the edges out per node: node a's neighbours are adjNode[adjStart[a] .. adjStart[a+1]).</summary>
		private void BuildAdjacency()
		{
			if (adjStart.Length < n + 1)
			{
				adjStart = new int[Math.Max(n + 1, adjStart.Length * 2)];
			}
			if (adjNode.Length < 2 * edgeCount)
			{
				int len = Math.Max(2 * edgeCount, adjNode.Length * 2);
				adjNode = new int[len];
				adjEdgeCap = new int[len];
			}
			Array.Clear(adjStart, 0, n + 1);
			for (int e = 0; e < edgeCount; e++)
			{
				adjStart[edgeA[e] + 1]++;
				adjStart[edgeB[e] + 1]++;
			}
			for (int i = 0; i < n; i++)
			{
				adjStart[i + 1] += adjStart[i];
			}
			// curPiece as the fill cursor (Solve resets it before reading it)
			for (int i = 0; i < n; i++)
			{
				curPiece[i] = adjStart[i];
			}
			for (int e = 0; e < edgeCount; e++)
			{
				int a = edgeA[e], b = edgeB[e], c = edgeCap[e];
				int ia = curPiece[a]++;
				adjNode[ia] = b;
				adjEdgeCap[ia] = c;
				int ib = curPiece[b]++;
				adjNode[ib] = a;
				adjEdgeCap[ib] = c;
			}
		}

		public long WaterOf(int i) => water[i];
		public long ResultOf(int i) => result[i];
		public void SetWater(int i, long w) => water[i] = w;

		private int MaxBand(int i)
		{
			return isPond[i] ? hist[i].Length - 1 : depth[i];
		}

		private long Weight(int i, int band)
		{
			if (!isPond[i])
			{
				return band <= depth[i] ? 1 : 0;
			}
			int[] h = hist[i];
			return band < h.Length ? h[band] : 0;
		}

		/// <summary>Capacity (dL) of this node's bands at or below <paramref name="band"/>.</summary>
		public long CapBelow(int i, int band)
		{
			if (!isPond[i])
			{
				return Math.Max(0, depth[i] - band + 1) * (long)U;
			}
			long[] s = suffix[i];
			return band < hist[i].Length ? (long)U * s[band] : 0;
		}

		/// <summary>Solves every node to its settled water (read with <see cref="ResultOf"/>). False (and no result) only if the
		/// solve would not conserve, which cannot happen.</summary>
		public bool Solve()
		{
			if (n == 0)
			{
				return true;
			}
			int maxBand = 0;
			for (int i = 0; i < n; i++)
			{
				maxBand = Math.Max(maxBand, MaxBand(i));
				result[i] = 0;
			}
			BuildAdjacency();
			// STEPPULSE_SHRINK_STEADY_SLICE_COST: a band whose pieces are the band above's (the same nodes reach it and no edge
			// stops at the band above) copies them instead of walking again: same members, same numbering (by lowest node),
			// same parent links, so the same result. A dug run of even depth walks once instead of once a notch.
			if (capStops.Length < maxBand + 1)
			{
				capStops = new bool[maxBand + 1];
			}
			Array.Clear(capStops, 0, maxBand + 1);
			for (int e = 0; e < edgeCount; e++)
			{
				int c = edgeCap[e];
				if (c >= 0 && c <= maxBand)
				{
					capStops[c] = true;
				}
			}
			pieceCount = 0;
			int prevFirst = 0, prevCount = 0;
			for (int band = 1; band <= maxBand; band++)
			{
				int first = pieceCount;
				if (band > 1 && !capStops[band - 1] && SameNodesAsAbove(band))
				{
					for (int j = 0; j < prevCount; j++)
					{
						int k = pieceCount;
						Piece above = pieces[prevFirst + j];
						Piece p = NewPiece(band);
						above.children.Add(k);
						p.members.AddRange(above.members);
					}
					for (int a = 0; a < n; a++)
					{
						int pk = prevPiece[a];
						if (pk < 0)
						{
							curPiece[a] = -1;
							continue;
						}
						int k = pk - prevFirst + first;
						curPiece[a] = k;
						Piece p = pieces[k];
						long cb = CapBelow(a, band);
						p.water += Math.Min(water[a], cb);
						p.cap += cb;
					}
					int[] sw = prevPiece;
					prevPiece = curPiece;
					curPiece = sw;
					prevFirst = first;
					continue;
				}
				for (int i = 0; i < n; i++)
				{
					curPiece[i] = -1;
				}
				for (int i = 0; i < n; i++)
				{
					if (Weight(i, band) == 0 || curPiece[i] >= 0)
					{
						continue;
					}
					int k = pieceCount;
					NewPiece(band);
					curPiece[i] = k;
					bfs.Clear();
					bfs.Add(i);
					for (int head = 0; head < bfs.Count; head++)
					{
						int a = bfs[head];
						int end = adjStart[a + 1];
						for (int e = adjStart[a]; e < end; e++)
						{
							int b = adjNode[e];
							if (adjEdgeCap[e] >= band && curPiece[b] < 0 && Weight(b, band) > 0)
							{
								curPiece[b] = k;
								bfs.Add(b);
							}
						}
					}
					if (band > 1)
					{
						pieces[prevPiece[i]].children.Add(k);
					}
				}
				// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: each piece's members in ascending node order (what sorting each BFS
				// gave), by one pass over the nodes instead of a sort per piece; the sums are the same.
				for (int a = 0; a < n; a++)
				{
					int k = curPiece[a];
					if (k < 0)
					{
						continue;
					}
					Piece p = pieces[k];
					p.members.Add(a);
					long cb = CapBelow(a, band);
					p.water += Math.Min(water[a], cb);
					p.cap += cb;
				}
				prevFirst = first;
				prevCount = pieceCount - first;
				int[] t = prevPiece;
				prevPiece = curPiece;
				curPiece = t;
			}
			long before = 0, after = 0;
			for (int i = 0; i < n; i++)
			{
				before += water[i];
			}
			for (int k = 0; k < pieceCount; k++)
			{
				if (pieces[k].band == 1)
				{
					Assign(k, pieces[k].water);
				}
			}
			for (int i = 0; i < n; i++)
			{
				after += result[i];
			}
			return before == after;
		}

		private bool[] capStops = new bool[16];

		/// <summary>True if exactly the nodes in a piece of the band above reach <paramref name="band"/>.</summary>
		private bool SameNodesAsAbove(int band)
		{
			for (int i = 0; i < n; i++)
			{
				if ((Weight(i, band) > 0) != (prevPiece[i] >= 0))
				{
					return false;
				}
			}
			return true;
		}

		private Piece NewPiece(int band)
		{
			if (pieceCount == pieces.Count)
			{
				pieces.Add(new Piece());
			}
			Piece p = pieces[pieceCount++];
			p.band = band;
			p.members.Clear();
			p.children.Clear();
			p.water = 0;
			p.cap = 0;
			return p;
		}

		private void Assign(int k, long amount)
		{
			Piece p = pieces[k];
			long free = amount;
			for (int j = 0; j < p.children.Count; j++)
			{
				free -= pieces[p.children[j]].water;
			}
			for (int j = 0; j < p.children.Count; j++)
			{
				Piece ch = pieces[p.children[j]];
				long give = Math.Max(0, Math.Min(free, ch.cap - ch.water));
				free -= give;
				Assign(p.children[j], ch.water + give);
			}
			if (free <= 0)
			{
				return;
			}
			int band = p.band;
			long wt = 0;
			for (int m = 0; m < p.members.Count; m++)
			{
				wt += Weight(p.members[m], band);
			}
			// a square weighs 1: its share is free / wt, divided once (STEPPULSE_SHRINK_STEADY_SLICE_COST: two 64-bit divides a
			// member were most of a big piece's lay)
			long perOne = free / wt;
			long laid = 0;
			for (int m = 0; m < p.members.Count; m++)
			{
				long w1 = Weight(p.members[m], band);
				laid += w1 == 1 ? perOne : free * w1 / wt;
			}
			long left = free - laid;
			for (int m = 0; m < p.members.Count; m++)
			{
				int a = p.members[m];
				long w1 = Weight(a, band);
				long share = (w1 == 1 ? perOne : free * w1 / wt) + (m < left ? 1 : 0);
				result[a] = CapBelow(a, band + 1) + share;
			}
		}

		// ── ponds: the exact surface ─────────────────────────────────────────────────────────────────

		/// <summary>The pond's capacity: U · Σ_{L ≥ 1} H[L].</summary>
		public static long PondCapacity(int[] h)
		{
			long s = 0;
			for (int l = 1; l < h.Length; l++)
			{
				s += h[l];
			}
			return s * U;
		}

		/// <summary>The pond's ONE surface for <paramref name="dl"/> dL over histogram <paramref name="h"/>: the water stands in
		/// band <paramref name="band"/> with <paramref name="rem"/> dL laid on it (0 ≤ rem &lt; U·H[band]); band 0 = at or over
		/// the brim. Twin of level_water.pond_surface.</summary>
		public static void PondSurface(int[] h, long dl, out int band, out long rem)
		{
			int mx = h.Length - 1;
			band = 0;
			rem = 0;
			if (mx <= 0)
			{
				return;
			}
			long left = Math.Max(0, dl);
			for (int b = mx; b >= 1; b--)
			{
				long cap = (long)U * h[b];
				if (left < cap)
				{
					band = b;
					rem = left;
					return;
				}
				left -= cap;
			}
		}

		/// <summary>The pond surface in dL-per-square height (0 = brim, negative below ground).</summary>
		public static double PondSurfaceHeight(int[] h, long dl)
		{
			PondSurface(h, dl, out int band, out long rem);
			if (band == 0)
			{
				return 0.0;
			}
			return -(double)band * U + rem / (double)h[band];
		}

		/// <summary>The water (dL) a pond square of <paramref name="bed"/> notches stands in under that surface.</summary>
		public static double PondSquareWater(int bed, double surfaceHeight)
		{
			if (bed <= 0)
			{
				return 0.0;
			}
			return Math.Max(0.0, Math.Min((double)bed * U, bed * (double)U + surfaceHeight));
		}

		/// <summary>C# integer division truncates toward zero; the Python twin uses trunc_div.</summary>
		public static long TruncDiv(long a, long b)
		{
			return a / b;
		}

		// ── what the player sees: the look by TRUE metres ────────────────────────────────────────────

		/// <summary>The water look for <paramref name="waterDl"/> dL in one square, by true metres, nearest band (unified depth
		/// spec §4.1): 0 dry; 1 under 25 cm (the very-shallow look, new art: VERY_SHALLOW_WATER_RESKIN_HE_SEES_FIRST, until it
		/// lands FluidDef shows the 0.5 m look); 2 ≈ 0.5 m; 3 ≈ 1 m; 4 ≈ 1.5 m; 5 = 2 m and deeper.</summary>
		public static int LookBand(long waterDl)
		{
			if (waterDl <= 0) return 0;
			if (waterDl < U / 2) return 1;            // < 0.25 m
			if (waterDl < 3L * U / 2) return 2;       // < 0.75 m
			if (waterDl < 5L * U / 2) return 3;       // < 1.25 m
			if (waterDl < 7L * U / 2) return 4;       // < 1.75 m
			return 5;
		}

		public static double Metres(long dl)
		{
			return dl * MetresPerUnit;
		}
	}

	/// <summary>
	/// The per-body surface-gap diagnostic (owner R9, 2026-10-17: every square of connected still water stands at the same
	/// surface height, to within 1 cm, read from game state). Twin of level_water.surface_gaps. A body is a 4-way run of wet
	/// dug squares of one fluid, plus every limitless source a wet square of it touches (surface 0) and every pond JOINED to
	/// it below the surface (its link reaches min(D, shore bed) notches down; the pond joins only when its surface or the
	/// square's stands above that floor). Runs joined to the SAME pond are one body, transitively through chains of runs and
	/// ponds (SURFACEGAP_MERGE_ARMS_THROUGH_POND: an arm 0.95 cm above a pond and another 0.95 cm below it are one gap of
	/// 1.9 cm, not two of 0.95). RM_NorthstarProofs.ProofLevelSurface reports it live;
	/// northstar/level_surface_bar.py judges it.
	/// </summary>
	public static class RM_SurfaceGap
	{
		public struct Body
		{
			public int squares;
			public double gapM;
			public double minM;
			public double maxM;
			public int firstCell;
		}

		/// <summary>Over the cells <paramref name="cells"/> (any order): they are the whole domain, a run never leaves them (a
		/// scene rect clips, as the Python twin). <paramref name="depthOf"/>, <paramref name="waterOf"/> and
		/// <paramref name="fluidOf"/> read a dug cell; <paramref name="cardinal"/> gives neighbour d (0..3) or -1;
		/// <paramref name="pondOf"/> names the pond behind a source cell (-1 none, -2 limitless); <paramref name="pondSurface"/>
		/// gives a pond's surface height in dL-per-square; <paramref name="bedOf"/> a source cell's bed notches. As the solve
		/// (RM_FlowKernel.ExactTouchSource) a body never passes a shut sluice: a <paramref name="sealedCell"/> square, dug or
		/// source, is skipped; and a run joins a source only when <paramref name="sourceFluidOf"/> (its DonorFluid) is
		/// compatible with the run's fluid (RM_StockMath.FluidsCompatible; null = compatible). Ties in gap list in first-cell
		/// order (SURFACEGAP_PARITY_FIX_TIES_ARE_UNSORTED).</summary>
		public static List<Body> Measure(IEnumerable<int> cells, Func<int, int> depthOf, Func<int, long> waterOf,
			Func<int, object> fluidOf, Func<int, int, int> cardinal, Func<int, int> pondOf, Func<int, double> pondSurface,
			Func<int, int> bedOf, Func<int, bool> sealedCell = null, Func<int, object> sourceFluidOf = null)
		{
			var sorted = new List<int>(cells);
			sorted.Sort();
			var domain = new HashSet<int>(sorted);
			var seen = new HashSet<int>();
			var run = new List<int>();
			var touched = new SortedSet<int>();
			var psurf = new Dictionary<int, double>();
			// one entry per 4-way run, in seed order; then runs joined through a shared pond are unioned into one body
			var runLo = new List<double>();
			var runHi = new List<double>();
			var runN = new List<int>();
			var runSeed = new List<int>();
			var parent = new List<int>();
			var firstRunOfPond = new Dictionary<int, int>();
			for (int s = 0; s < sorted.Count; s++)
			{
				int c0 = sorted[s];
				if (seen.Contains(c0) || depthOf(c0) <= 0 || waterOf(c0) <= 0 || (sealedCell != null && sealedCell(c0)))
				{
					continue;
				}
				object fl = fluidOf(c0);
				run.Clear();
				run.Add(c0);
				seen.Add(c0);
				touched.Clear();
				bool lim = false;
				double lo = double.MaxValue, hi = double.MinValue;
				for (int head = 0; head < run.Count; head++)
				{
					int a = run[head];
					int da = depthOf(a);
					double sa = waterOf(a) - (double)da * RM_LevelSolve.U;
					lo = Math.Min(lo, sa);
					hi = Math.Max(hi, sa);
					for (int d = 0; d < 4; d++)
					{
						int nb = cardinal(a, d);
						if (nb < 0)
						{
							continue;
						}
						if (depthOf(nb) > 0)
						{
							if (domain.Contains(nb) && !seen.Contains(nb) && waterOf(nb) > 0 && ReferenceEquals(fluidOf(nb), fl)
								&& (sealedCell == null || !sealedCell(nb)))
							{
								seen.Add(nb);
								run.Add(nb);
							}
							continue;
						}
						if ((sealedCell != null && sealedCell(nb))
							|| (sourceFluidOf != null && !RM_StockMath.FluidsCompatible(true, fl, sourceFluidOf(nb))))
						{
							continue;
						}
						int p = pondOf(nb);
						if (p == -2)
						{
							lim = true;
						}
						else if (p >= 0)
						{
							if (!psurf.TryGetValue(p, out double ps))
							{
								ps = psurf[p] = pondSurface(p);
							}
							double link = -(double)Math.Min(da, bedOf(nb)) * RM_LevelSolve.U;
							if (Math.Max(sa, ps) > link)
							{
								touched.Add(p);
							}
						}
					}
				}
				foreach (int p in touched)
				{
					lo = Math.Min(lo, psurf[p]);
					hi = Math.Max(hi, psurf[p]);
				}
				if (lim)
				{
					lo = Math.Min(lo, 0.0);
					hi = Math.Max(hi, 0.0);
				}
				int r = runN.Count;
				runLo.Add(lo);
				runHi.Add(hi);
				runN.Add(run.Count);
				runSeed.Add(c0);
				parent.Add(r);
				foreach (int p in touched)
				{
					if (firstRunOfPond.TryGetValue(p, out int other))
					{
						int ra = Root(parent, other), rb = Root(parent, r);
						if (ra != rb)
						{
							parent[Math.Max(ra, rb)] = Math.Min(ra, rb);
						}
					}
					else
					{
						firstRunOfPond[p] = r;
					}
				}
			}
			// fold each run into its root (the body's earliest run, whose seed is the body's first cell)
			var outList = new List<Body>();
			var bodyOfRoot = new Dictionary<int, int>();
			var bodyLo = new List<double>();
			var bodyHi = new List<double>();
			for (int r = 0; r < runN.Count; r++)
			{
				int root = Root(parent, r);
				if (!bodyOfRoot.TryGetValue(root, out int bi))
				{
					bi = bodyOfRoot[root] = outList.Count;
					outList.Add(new Body { squares = 0, firstCell = runSeed[root] });
					bodyLo.Add(double.MaxValue);
					bodyHi.Add(double.MinValue);
				}
				Body body = outList[bi];
				body.squares += runN[r];
				outList[bi] = body;
				bodyLo[bi] = Math.Min(bodyLo[bi], runLo[r]);
				bodyHi[bi] = Math.Max(bodyHi[bi], runHi[r]);
			}
			for (int bi = 0; bi < outList.Count; bi++)
			{
				Body body = outList[bi];
				body.gapM = (bodyHi[bi] - bodyLo[bi]) * RM_LevelSolve.MetresPerUnit;
				body.minM = bodyLo[bi] * RM_LevelSolve.MetresPerUnit;
				body.maxM = bodyHi[bi] * RM_LevelSolve.MetresPerUnit;
				outList[bi] = body;
			}
			outList.Sort((a, b) => b.gapM != a.gapM ? b.gapM.CompareTo(a.gapM) : a.firstCell.CompareTo(b.firstCell));
			return outList;
		}

		private static int Root(List<int> parent, int r)
		{
			while (parent[r] != r)
			{
				parent[r] = parent[parent[r]];
				r = parent[r];
			}
			return r;
		}
	}
}
