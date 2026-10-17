using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD (design/RimMandrake/pond_depth_design_2026-10-16.md, D1-D4 RULED). Owner, by card
	/// 2026-10-16: <i>"Should natural water get partial depth like dug cells? → Yes, ponds shallow out"</i>; D2, his words:
	/// <i>"It should slosh around until it levels, pond or canal or otherwise."</i>
	///
	/// A pond is one stock and one bed record; its water is ONE flat surface, <c>s</c> levels below the brim. Nothing new is
	/// stored per square. Verse-free so Source/SelfTest/ compiles THIS file.
	/// <code>
	/// V    = stock / levelUnit (RM_BedMath.SupportedLevels)
	/// H[L] = squares whose bed ≥ L          (L = 1 .. maxBed; H[0] = every square)
	/// s    = the smallest drawdown with Σ_{L&gt;s} H[L] ≤ V
	/// r    = V − Σ_{L&gt;s} H[L]               (0 ≤ r &lt; H[s]: units of band s, the last part-level)
	/// w    = bed − s, +1 on the r-patch       (the r-patch: r squares of bed ≥ s, ONE connected patch)
	/// </code>
	/// 🔑 Design §2 writes the patch as "bed == s" squares getting 1; band s is held by EVERY square of bed ≥ s, so the
	/// patch is drawn from all of them (else Σw ≠ V for any pond with mixed beds). Σw == V always (S1).
	/// </summary>
	public static class RM_PondDepthMath
	{
		/// <summary>Stage ladder (design §4) by water depth w in a square below its full depth.</summary>
		public enum Stage
		{
			/// <summary>w == bed: the square's own original terrain.</summary>
			Original,
			/// <summary>w ≥ 4, below full: vanilla deep water.</summary>
			Deep,
			/// <summary>w == 3: RM_WaterChestDeepStill.</summary>
			ChestDeep,
			/// <summary>w == 2: vanilla shallow water.</summary>
			Shallow,
			/// <summary>w == 1: RM_WaterThin.</summary>
			Thin,
			/// <summary>w == 0, just exposed: vanilla mud (wet ground, riverbank for growth, ruling W2).</summary>
			Mud,
			/// <summary>w == 0 past the mud time: the existing cracked RM_Lakebed_*.</summary>
			Lakebed,
		}

		/// <summary>Mod Setting "pondMudDays" default: days an exposed square stays mud before it cracks.</summary>
		public const float DefaultMudDays = 2f;

		/// <summary>Mod Setting "pondStageWritesPerPulse" default: terrain restages per pulse (cost guard, §8).</summary>
		public const int DefaultStageWritesPerPulse = 400;

		/// <summary>H[L] = squares whose bed ≥ L, L = 0..maxBed (H[0] = all squares with a bed ≥ 0). Length maxBed + 1.</summary>
		public static int[] Histogram(IList<int> beds)
		{
			int max = 0;
			for (int i = 0; i < beds.Count; i++)
			{
				if (beds[i] > max)
				{
					max = beds[i];
				}
			}
			int[] h = new int[max + 1];
			for (int i = 0; i < beds.Count; i++)
			{
				int b = beds[i] < 0 ? 0 : beds[i];
				h[b]++;
			}
			// suffix sum: h[L] = #beds ≥ L
			for (int l = max - 1; l >= 0; l--)
			{
				h[l] += h[l + 1];
			}
			return h;
		}

		/// <summary>The drawdown s and the part-level r for <paramref name="levels"/> whole levels over histogram
		/// <paramref name="h"/>. A pond at or over its brim is s = 0, r = 0 (excess stays in stock and shows nothing). No
		/// levels at all is s = maxBed, r = 0 (every square dry).</summary>
		public static void Drawdown(long levels, int[] h, out int s, out int r)
		{
			int max = h.Length - 1;
			long above = 0;   // Σ_{L > s} H[L], walked from the deepest band up
			s = max;
			r = 0;
			if (max <= 0 || levels <= 0)
			{
				return;
			}
			// Lower s while the band at s fits completely: above + H[s] ≤ V.
			while (s > 0 && above + h[s] <= levels)
			{
				above += h[s];
				s--;
			}
			if (s == 0)
			{
				r = 0;   // full (or over): every square at its bed
				return;
			}
			r = (int)(levels - above);
		}

		/// <summary>Water (levels) a square of bed <paramref name="bed"/> holds at drawdown <paramref name="s"/>;
		/// <paramref name="inPatch"/> = it is one of the r squares holding band s.</summary>
		public static int WaterAt(int bed, int s, bool inPatch)
		{
			if (bed <= 0)
			{
				return 0;
			}
			if (s <= 0)
			{
				return bed;
			}
			if (bed < s)
			{
				return 0;
			}
			return bed - s + (inPatch ? 1 : 0);
		}

		/// <summary>The terrain stage for a square holding <paramref name="w"/> of its <paramref name="bed"/> levels.</summary>
		public static Stage StageFor(int w, int bed, bool mudExpired)
		{
			if (w <= 0)
			{
				return mudExpired ? Stage.Lakebed : Stage.Mud;
			}
			if (w >= bed)
			{
				return Stage.Original;
			}
			if (w >= RM_Volume.LevelsPerSquare)
			{
				return Stage.Deep;
			}
			if (w == 3)
			{
				return Stage.ChestDeep;
			}
			return w == 2 ? Stage.Shallow : Stage.Thin;
		}

		/// <summary>The r squares holding band s: of the squares with bed ≥ s (and <paramref name="eligible"/>, ruling 5: a
		/// dry square with a pawn or building waits), grown best-first as ONE 4-connected patch from the deepest square
		/// (deepest bed, then lowest cell index), so too little water for a sheet is one puddle at the minimum depth, never
		/// 0,1,0,1 (S2). If the eligible set is split, the next patch starts from the best square left. Deterministic.
		/// <paramref name="cells"/>/<paramref name="beds"/> are parallel; cell index = z × width + x.</summary>
		public static HashSet<int> PickPatch(int width, int height, IList<int> cells, IList<int> beds, int s, int r,
			Func<int, bool> eligible = null)
		{
			var picked = new HashSet<int>();
			if (r <= 0 || s <= 0)
			{
				return picked;
			}
			var bedOf = new Dictionary<int, int>(cells.Count);
			for (int i = 0; i < cells.Count; i++)
			{
				if (beds[i] >= s && (eligible == null || eligible(cells[i])))
				{
					bedOf[cells[i]] = beds[i];
				}
			}
			long n = (long)width * height;
			long Key(int c) => (long)(RM_BedMath.MaxStorableDepth - bedOf[c]) * n + c;
			var remaining = new SortedSet<long>();
			foreach (KeyValuePair<int, int> kv in bedOf)
			{
				remaining.Add(Key(kv.Key));
			}
			var frontier = new SortedSet<long>();
			var seen = new HashSet<int>();
			while (picked.Count < r && remaining.Count > 0)
			{
				if (frontier.Count == 0)
				{
					long seed = remaining.Min;
					frontier.Add(seed);
					seen.Add((int)(seed % n));
				}
				long top = frontier.Min;
				frontier.Remove(top);
				remaining.Remove(top);
				int c = (int)(top % n);
				picked.Add(c);
				int x = c % width, z = c / width;
				for (int d = 0; d < 4; d++)
				{
					int nx = x + (d == 1 ? 1 : d == 3 ? -1 : 0);
					int nz = z + (d == 0 ? 1 : d == 2 ? -1 : 0);
					if (nx < 0 || nz < 0 || nx >= width || nz >= height)
					{
						continue;
					}
					int nb = nz * width + nx;
					if (bedOf.ContainsKey(nb) && seen.Add(nb))
					{
						frontier.Add(Key(nb));
					}
				}
			}
			return picked;
		}

		// ── D2, the head rule: one surface across connected water ──────────────────────────────────────

		/// <summary>D2 (owner's words): a pond at drawdown <paramref name="s"/> (its surface −s) gives a level to a dug square
		/// only while its surface stands above that square's water: dug surface (fill − depth) ≤ −s − 1. So water never rises
		/// into a ditch floor above the surface. s = 0 (a brim-full pond, or the rule off) is today's rule exactly: any dug
		/// square with room.</summary>
		public static bool SourceMayGive(int s, int recipientDepth, int recipientFill)
		{
			return recipientDepth - recipientFill >= s + 1;
		}

		/// <summary>D2's other half: a dug square whose water stands two or more above the pond's surface (fill − depth ≥
		/// −s + 2) runs a level back into the pond. The one-level dead band (dug surface −s or −s+1) is what keeps a pond
		/// whose part-level is one square from shuttling a unit back and forth: after a give the dug side sits at the new
		/// surface or one above it, after a return at most one above. A brim-full pond (s = 0) never takes a return here
		/// (fill − depth ≤ 0 &lt; 2): the existing paths (RunIntoBeds, the return leg) are unchanged.</summary>
		public static bool DugMayReturn(int s, int depth, int fill)
		{
			return fill > 0 && depth > 0 && fill - depth >= 2 - s;
		}
	}
}
