using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// TITAN_TRENCHES_WIRE_MIND_THE_GAP — which dug cells a big creature steps over, Verse-free so Source/SelfTest/ compiles THIS
	/// production file. Owner, by card 2026-10-18 (BIG_CREATURES_DESIGN_WALLS_AND_SLOTS §8 Q3): titans step over trenches narrower
	/// than a quarter of their breadth; wider trenches hold as today. The breadth rule is HugeThings' (WallsSlots.StepsOverTrench);
	/// FlowWorks only receives a STRIDE s per pawn (the widest trench, in cells, it steps over; RM_TrenchStride.StrideOf).
	///
	/// A trench's width at a cell is its RUN: along X and along Z, the maximal contiguous run of dug cells (depth &gt; 0, an intact
	/// cover or deck already read as ground by RM_PocketGrid.EffectiveDepth) through the cell, counted only when BOTH flank cells
	/// past the run's ends are in bounds and undug (depth 0: the banks the creature stands on). The cell's width is the narrower
	/// qualifying axis. A creature of stride s treats every cell of width &lt;= s as ground (depth 0); nothing else changes.
	/// Consequences, each a selftest case: a 1-wide trench of any length (straight, bent, or a diagonal staircase) is bridged for
	/// s &gt;= 1; a 2-wide one only for s &gt;= 2; a pit wider than s on both axes never is; a run that reaches the map edge has no far
	/// bank and is never bridged. Not modelled (v1): a narrow trench cut into a deeper floor (its banks are not ground).
	/// </summary>
	public static class RM_TrenchStrideMath
	{
		/// <summary>The widest stride any creature is given (B 13+ is body size 156+). StrideOf clamps to this.</summary>
		public const int MaxStride = 3;

		/// <summary>0 = never bridged.</summary>
		public static int ClampStride(int s)
		{
			return s <= 0 ? 0 : (s > MaxStride ? MaxStride : s);
		}

		/// <summary>Per cell: its trench width (1..MaxStride) when some axis run qualifies, else 0 (undug, too wide, no bank).</summary>
		public static byte[] RunWidths(byte[] depth, int w, int h)
		{
			var runs = new byte[w * h];
			if (depth == null || depth.Length < w * h)
			{
				return runs;
			}
			for (int z = 0; z < h; z++)
			{
				for (int x = 0; x < w; x++)
				{
					int i = z * w + x;
					if (depth[i] == 0)
					{
						continue;
					}
					int best = Math.Min(AxisRun(depth, w, h, x, z, 1, 0), AxisRun(depth, w, h, x, z, 0, 1));
					runs[i] = best <= MaxStride ? (byte)best : (byte)0;
				}
			}
			return runs;
		}

		/// <summary>The run of dug cells through (x, z) along (dx, dz), banked by undug in-bounds cells at both ends; int.MaxValue
		/// when it is wider than MaxStride or a bank is missing.</summary>
		private static int AxisRun(byte[] depth, int w, int h, int x, int z, int dx, int dz)
		{
			int n = 1;
			for (int sign = -1; sign <= 1; sign += 2)
			{
				int cx = x + sign * dx, cz = z + sign * dz;
				while (true)
				{
					if (cx < 0 || cz < 0 || cx >= w || cz >= h)
					{
						return int.MaxValue; // no far bank
					}
					if (depth[cz * w + cx] == 0)
					{
						break;
					}
					if (++n > MaxStride)
					{
						return int.MaxValue;
					}
					cx += sign * dx;
					cz += sign * dz;
				}
			}
			return n;
		}

		/// <summary>Does a creature of this stride treat a cell of this run width as ground?</summary>
		public static bool Bridged(int run, int stride)
		{
			return run > 0 && stride > 0 && run <= stride;
		}

		/// <summary>The depth a stride-s creature sees: depth with every bridged cell read as 0. A fresh array.</summary>
		public static byte[] BridgedDepth(byte[] depth, byte[] runs, int stride)
		{
			var o = (byte[])depth.Clone();
			for (int i = 0; i < o.Length && i < runs.Length; i++)
			{
				if (Bridged(runs[i], stride))
				{
					o[i] = 0;
				}
			}
			return o;
		}

		/// <summary>How many cells stride s bridges (0: its view IS the plain one).</summary>
		public static int CountBridged(byte[] runs, int stride)
		{
			int c = 0;
			if (runs == null || stride <= 0)
			{
				return 0;
			}
			for (int i = 0; i < runs.Length; i++)
			{
				if (Bridged(runs[i], stride))
				{
					c++;
				}
			}
			return c;
		}

		/// <summary>TRENCH_STRIDE_UNDERPASS_FIX_ONE_BUG: which cliff-mask view a strider's path request plans on. The suspension
		/// underpass hands the FLOOR view (decks the floor band passes under read as the floor) to a pawn in the floor band or down
		/// in a hole (<paramref name="cliffFloorView"/>, RM_SuspensionUnderpass.UsesFloorView); a strider standing astride a
		/// trench it steps over is NOT down in a hole (it stands on the banks, at ground), so it keeps the deck view unless it is
		/// in the floor band. The stride masks are then the chosen view's depth with that view's narrow trenches bridged.</summary>
		public static bool StriderUsesFloorView(bool cliffFloorView, bool inFloorBand, bool standsOnBridged)
		{
			return cliffFloorView && (inFloorBand || !standsOnBridged);
		}

		/// <summary>The smallest stride whose view equals stride s's (views of strides with the same bridged count are the same
		/// cells, since bridged sets nest): masks and pocket grids are kept once per distinct view. 0: the plain view.</summary>
		public static int CanonicalStride(byte[] runs, int stride)
		{
			int s = ClampStride(stride);
			int count = CountBridged(runs, s);
			if (count == 0)
			{
				return 0;
			}
			while (s > 1 && CountBridged(runs, s - 1) == count)
			{
				s--;
			}
			return s;
		}
	}
}
