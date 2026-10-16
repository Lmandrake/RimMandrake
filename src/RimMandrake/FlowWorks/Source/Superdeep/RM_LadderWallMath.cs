namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_LADDER_REDRAW_HUNG_ON_THE_WALL — owner, 2026-10-16: <i>"It clearly needs to be installed along a side of the pit,
	/// like a door to a room, and have a 'slid up' version that's inaccessible to the prisoners below or a 'slid down' version
	/// that is clearly visible. These will look different for north, south, or east/west attached ladders."</i>
	///
	/// The ladder stands on the PIT square (the deeper side of the edge, so the trap's per-cell read, the closed-ladder grid
	/// and the pocket scan keep their one cell), and its rotation names the WALL it hangs on: the cardinal neighbour it
	/// faces, which must be shallower (RM_CliffMaskMath.LadderJoins). It joins its square to THAT neighbour only — a door
	/// between two rooms — never to every shallower side as before. Rotation in Rot4 order: 0 north, 1 east, 2 south, 3 west.
	///
	/// Orientation like a door's (RM_FlowDoorFacingMath is the door analogue for sluices): the placed rotation stands when it
	/// faces a wall; otherwise the ladder turns to the wall with the biggest drop, ties to the first in Rot4 order (north
	/// first: the far wall is the one the camera sees). No wall at all: placement is refused (-1). Verse-free, so the
	/// SelfTest compiles this production file.
	/// </summary>
	public static class RM_LadderWallMath
	{
		/// <summary>Facing offsets per Rot4 index (Rot4.FacingCell).</summary>
		public static readonly int[] FX = { 0, 1, 0, -1 };
		public static readonly int[] FZ = { 1, 0, -1, 0 };

		/// <summary>Is the side at <paramref name="sideD"/> a wall a ladder on a square at <paramref name="ladderD"/> can hang
		/// on? Only a dug square has walls; the side must be on the map and shallower.</summary>
		public static bool IsWall(int ladderD, int sideD, bool inBounds)
		{
			return inBounds && ladderD > 0 && RM_CliffMaskMath.LadderJoins(ladderD, sideD);
		}

		/// <summary>The wall the ladder hangs on (Rot4 index), or -1 when the square has none. sideD / inBounds: per Rot4
		/// index, the neighbour's depth and whether it is on the map.</summary>
		public static int Resolve(int placedRot, int ladderD, int[] sideD, bool[] inBounds)
		{
			if (placedRot >= 0 && placedRot < 4 && IsWall(ladderD, sideD[placedRot], inBounds[placedRot]))
			{
				return placedRot;
			}
			int best = -1, bestDrop = 0;
			for (int r = 0; r < 4; r++)
			{
				if (IsWall(ladderD, sideD[r], inBounds[r]) && ladderD - sideD[r] > bestDrop)
				{
					best = r;
					bestDrop = ladderD - sideD[r];
				}
			}
			return best;
		}

		/// <summary>Does a ladder turned to <paramref name="rot"/> face the neighbour at offset (dx, dz)?</summary>
		public static bool Faces(int rot, int dx, int dz)
		{
			return rot >= 0 && rot < 4 && FX[rot] == dx && FZ[rot] == dz;
		}

		/// <summary>Does a ladder turned to <paramref name="rot"/> on a square at <paramref name="ladderD"/> join it to the
		/// neighbour at offset (dx, dz) and depth <paramref name="otherD"/>? Only the wall it hangs on, and only while that
		/// side is still a wall (fill the rim in and the ladder leads nowhere).</summary>
		public static bool Joins(int rot, int ladderD, int dx, int dz, int otherD)
		{
			return Faces(rot, dx, dz) && RM_CliffMaskMath.LadderJoins(ladderD, otherD);
		}
	}
}
