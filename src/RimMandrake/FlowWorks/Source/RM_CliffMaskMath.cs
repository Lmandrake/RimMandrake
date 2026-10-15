using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS — the per-band connectivity mask's arithmetic, Verse-free so Source/SelfTest/
	/// compiles THIS production file (design/RimMandrake/relative_depth_climb_design_2026-10-12.md §8.5 step 2, Alternative A).
	///
	/// RimWorld 1.6's A* (PathFinderJob) only expands the directions set in a per-cell byte (Verse.CellConnection: bit 0 N,
	/// 1 S, 2 E, 3 W, 4 NE, 5 SE, 6 SW, 7 NW, offsets as CellConnectionExtensions.OffsetFromBitIndex). A band's mask is
	/// vanilla's byte AND <see cref="AllowedBits"/>: a direction survives only when the step it takes is allowed for climb
	/// limit K (RM_PitTrapMath.StepAllowed / DiagonalAllowed, the same rule the pocket grid labels with), so the pathfinder
	/// walks ramps and gentle slopes and never a wall. Ramps and ladders join CARDINAL steps only; a diagonal never crosses
	/// a cliff corner (GPT #7).
	/// </summary>
	public static class RM_CliffMaskMath
	{
		/// <summary>Offsets per bit, CellConnection order.</summary>
		public static readonly int[] Dx = { 0, 0, 1, -1, 1, 1, -1, -1 };
		public static readonly int[] Dz = { 1, -1, 0, 0, 1, -1, -1, 1 };

		/// <summary>Index into a 3×3 neighbourhood array: (dz + 1) × 3 + (dx + 1); the centre is 4.</summary>
		public static int N9(int dx, int dz)
		{
			return (dz + 1) * 3 + (dx + 1);
		}

		/// <summary>The directions out of the centre of a 3×3 depth patch that climb limit K may take. d9: depths (an intact
		/// cover reads 0; out of the map, anything: vanilla's own bits are already clear there). joins(bit): a ramp or a
		/// structural ladder joins the centre with that CARDINAL neighbour (bits 0..3), any depth.</summary>
		public static byte AllowedBits(int[] d9, int k, Func<int, bool> joins = null)
		{
			int c = d9[4];
			byte bits = 0;
			for (int b = 0; b < 4; b++)
			{
				int n = d9[N9(Dx[b], Dz[b])];
				if (RM_PitTrapMath.StepAllowed(c, n, k, joins != null && joins(b)))
				{
					bits |= (byte)(1 << b);
				}
			}
			for (int b = 4; b < 8; b++)
			{
				int dx = Dx[b], dz = Dz[b];
				if (RM_PitTrapMath.DiagonalAllowed(c, d9[N9(dx, dz)], d9[N9(dx, 0)], d9[N9(0, dz)], k))
				{
					bits |= (byte)(1 << b);
				}
			}
			return bits;
		}

		/// <summary>A band's byte: vanilla's AND the climb rule's.</summary>
		public static byte Derive(byte vanilla, byte allowed)
		{
			return (byte)(vanilla & allowed);
		}

		/// <summary>Does a ladder standing at depth <paramref name="ladderD"/> join its cell to a cardinal neighbour at
		/// <paramref name="otherD"/>? Design §8.4: "It now joins its cell to ANY shallower cardinal neighbour, whatever the
		/// depth difference." A ladder in the middle of a flat floor joins nothing.</summary>
		public static bool LadderJoins(int ladderD, int otherD)
		{
			return otherD < ladderD;
		}

		/// <summary>Does a ramp at depth <paramref name="rampD"/> facing a neighbour at <paramref name="facingD"/> join them?
		/// Design §8.4: "when that neighbour is 1 to 3 levels shallower" (<paramref name="maxSpan"/>, Mod Setting 1..3).</summary>
		public static bool RampJoins(int rampD, int facingD, int maxSpan)
		{
			int s = rampD - facingD;
			return s >= 1 && s <= Math.Max(1, maxSpan);
		}

		/// <summary>Which bit points from a cell to its cardinal neighbour (dx, dz); -1 if not a cardinal offset.</summary>
		public static int CardinalBit(int dx, int dz)
		{
			for (int b = 0; b < 4; b++)
			{
				if (Dx[b] == dx && Dz[b] == dz)
				{
					return b;
				}
			}
			return -1;
		}
	}
}
