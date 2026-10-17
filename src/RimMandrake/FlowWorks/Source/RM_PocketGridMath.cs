using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP — the pocket grid's arithmetic, Verse-free so Source/SelfTest/ compiles THIS
	/// production file (design/RimMandrake/relative_depth_climb_design_2026-10-12.md §8.3).
	///
	/// For one climb band K, two N/S/E/W neighbours join when the step between them is allowed for K
	/// (RM_PitTrapMath.StepAllowed; a ramp joins any pair it spans). A POCKET is a component with no cell at D = 0: nothing in
	/// it can walk up to the surface. Gradual slopes never make one, because every step on them is ≤ K (owner, 2026-10-12:
	/// "so that gradual slopes never trap anyone"; "Natural ponds and lakes when pumped dry would leave just such gradual
	/// terrain so no chance to fall in and get stuck").
	///
	/// Walkability is deliberately NOT an input: the grid is depth-only, so building or removing a wall never makes it stale.
	/// Vanilla reachability already accounts for walls, and the reachability seam ANDs the two. Cell index = z × width + x
	/// (RimWorld's CellIndices order). No component is capped (GPT #13: a dried deep lake is just a big component).
	/// </summary>
	public static class RM_PocketGridMath
	{
		public sealed class Labels
		{
			/// <summary>Component label per cell, 0..count-1.</summary>
			public int[] label;
			public int count;
			/// <summary>Per label: some cell is at D = 0.</summary>
			public bool[] surface;
			/// <summary>Per label: cell count.</summary>
			public int[] size;
			public int width;
			public int height;
			public int k;

			public bool IsPocketCell(int i)
			{
				return i >= 0 && i < label.Length && !surface[label[i]];
			}

			public bool IsPocketCell(int x, int z)
			{
				return x >= 0 && z >= 0 && x < width && z < height && !surface[label[z * width + x]];
			}

			public bool SameComponent(int a, int b)
			{
				return a >= 0 && b >= 0 && a < label.Length && b < label.Length && label[a] == label[b];
			}
		}

		/// <summary>Label every cell for band K. depth: effective climb depth per cell (a covered cell reads 0).
		/// rampJoins(i, j), optional: a ramp joins cells i and j (both directions, any band). Null until ramps exist.</summary>
		public static Labels Label(byte[] depth, int width, int height, int k, Func<int, int, bool> rampJoins = null)
		{
			if (depth == null || width <= 0 || height <= 0 || depth.Length < width * height)
			{
				throw new ArgumentException("depth grid does not match " + width + "x" + height);
			}
			int n = width * height;
			var lab = new int[n];
			for (int i = 0; i < n; i++)
			{
				lab[i] = -1;
			}
			var surface = new List<bool>();
			var size = new List<int>();
			var queue = new int[n];
			int count = 0;
			for (int seed = 0; seed < n; seed++)
			{
				if (lab[seed] >= 0)
				{
					continue;
				}
				int id = count++;
				bool surf = false;
				int sz = 0;
				int head = 0, tail = 0;
				queue[tail++] = seed;
				lab[seed] = id;
				while (head < tail)
				{
					int c = queue[head++];
					sz++;
					int d = depth[c];
					if (d == 0)
					{
						surf = true;
					}
					int x = c % width, z = c / width;
					for (int dir = 0; dir < 4; dir++)
					{
						int nx = x, nz = z;
						switch (dir)
						{
							case 0: nz++; break;
							case 1: nx++; break;
							case 2: nz--; break;
							default: nx--; break;
						}
						if (nx < 0 || nz < 0 || nx >= width || nz >= height)
						{
							continue;
						}
						int ni = nz * width + nx;
						if (lab[ni] >= 0)
						{
							continue;
						}
						bool ramp = rampJoins != null && (rampJoins(c, ni) || rampJoins(ni, c));
						if (!RM_PitTrapMath.StepAllowed(d, depth[ni], k, ramp))
						{
							continue;
						}
						lab[ni] = id;
						queue[tail++] = ni;
					}
				}
				surface.Add(surf);
				size.Add(sz);
			}
			return new Labels
			{
				label = lab, count = count, surface = surface.ToArray(), size = size.ToArray(),
				width = width, height = height, k = k,
			};
		}

		/// <summary>Every cell index carrying this label, ascending.</summary>
		public static List<int> CellsOf(Labels l, int label)
		{
			var o = new List<int>();
			for (int i = 0; i < l.label.Length; i++)
			{
				if (l.label[i] == label)
				{
					o.Add(i);
				}
			}
			return o;
		}

		/// <summary>The W×W width rule over a pocket (design §8.1: "measured over the cells of the pawn's own pocket"): true when
		/// EVERY cell of the pocket lies in some W×W square made only of that pocket's cells. A narrower arm anywhere is a
		/// way out for a creature that wide (it braces across and walks out), as ruled in September.</summary>
		public static bool WideEverywhere(Labels l, int label, int w)
		{
			if (w <= 1)
			{
				return true;
			}
			bool In(int x, int z) => x >= 0 && z >= 0 && x < l.width && z < l.height && l.label[z * l.width + x] == label;
			foreach (int i in CellsOf(l, label))
			{
				if (!RM_PitTrapMath.PitWidthAt(In, i % l.width, i / l.width, w))
				{
					return false;
				}
			}
			return true;
		}

		/// <summary>Is a pawn standing in a pocket of its band TRAPPED there (no way out at all)? Only when no ladder it may
		/// use stands anywhere in the pocket and the pocket is wide enough for it on every cell (design §8.3).</summary>
		public static bool Trapped(bool inPocket, bool usableLadderInPocket, bool wideEverywhere)
		{
			return inPocket && !usableLadderInPocket && wideEverywhere;
		}

		/// <summary>V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT: does a ladder that leads out of its pocket count as a way in or out for
		/// this reachability query? A pawn's own query: only one it may climb (raised = nobody, prison-door rule). A PAWNLESS
		/// query sees the cliff masks' structural view: any LOWERED ladder. Vanilla Pawn_PathFollower.StartPath asks
		/// Reachability.CanReach(…, TraverseParms.For(TraverseMode.PassDoors)) — no pawn — before every walk, so counting no
		/// ladder there failed every walk into or out of a laddered pocket (v2 P4/P4f/P5n). The prison-door rule stays per pawn:
		/// the pawn's own CanReach, the ladder offset grid and the step floor.</summary>
		public static bool LadderIsAWay(bool pawnKnown, bool lowered, bool pawnMayClimb)
		{
			return pawnKnown ? pawnMayClimb : lowered;
		}

		/// <summary>The relative rule's reachability veto (design §8.5 step 6): vanilla said yes, but start and destination lie in
		/// different band components, and the trip needs a way out of the start pocket (if any) AND a way into the destination
		/// pocket (if any) (a ladder that is a way for this query, or a pocket too narrow to hold the pawn). Two surface
		/// components (no pocket at either end) stay apart. REACH_VETO_FIX_ONE_END_ENOUGH (GPT C3-F8/C4-F2): one end having a
		/// way used to clear the veto, so a laddered pocket "reached" a sealed one and the pather failed in a loop.</summary>
		public static bool ReachVetoed(bool sameComponent, bool startPocket, bool startWayOut, bool destPocket, bool destWayIn)
		{
			if (sameComponent)
			{
				return false;
			}
			bool outOk = !startPocket || startWayOut;
			bool inOk = !destPocket || destWayIn;
			return !(outOk && inOk && (startPocket || destPocket));
		}

		/// <summary>REACH_VETO_FIX_ONE_END_ENOUGH (GPT C3-F9): does this component hold a cell on the map's border? A surface
		/// component that does not (an island ringed by a sheer trench) never reaches the map edge on foot.</summary>
		public static bool TouchesEdge(Labels l, int label)
		{
			if (l == null || label < 0 || label >= l.count)
			{
				return false;
			}
			int w = l.width, h = l.height;
			for (int x = 0; x < w; x++)
			{
				if (l.label[x] == label || l.label[(h - 1) * w + x] == label)
				{
					return true;
				}
			}
			for (int z = 0; z < h; z++)
			{
				if (l.label[z * w] == label || l.label[z * w + w - 1] == label)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>The band whose grid answers for climb limit K: 1..maxDepth-1 (callers pass the band array length,
		/// RM_PitTrapMath.ClimbBands). K ≥ maxDepth has no grid (returns 0): true only when no step on the map exceeds K, which
		/// is why the band count is sized by the largest climb limit (PIT_DEPTH_WIDEN) and ClimbLimit is capped at it.</summary>
		public static int BandFor(int k, int maxDepth)
		{
			if (k >= maxDepth)
			{
				return 0;
			}
			return Math.Max(1, k);
		}
	}
}
