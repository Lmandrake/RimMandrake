namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR (owner 2026-10-16: "For the sluice gate, they should intelligently rotate the
	/// same way doors do after placement. They are, in fact, a kind of door. This is true for all the water-blocking
	/// structures we built for canals."). Verse-free, so the SelfTest covers it.
	///
	/// Vanilla (DoorUtility.DoorRotationAt, redone every frame a 1x1 door or its blueprint draws) scores each cardinal
	/// side (AlignQualityAgainst: impassable 9, a door 1 or 5, a fence 1 or 10, else 0), sums East+West against
	/// North+South, and turns the door to North (leaf spans East-West) when East+West &gt;= North+South, else East. In a
	/// canal that has nothing to grip: the banks are walkable ground (0) and a superdeep channel cell is impassable (9),
	/// so a gate would turn to lie ALONG a superdeep channel. For a flow door standing on a dug cell this rule re-scores
	/// each side: a channel cell (dug, or natural liquid the canal opens into) is never a wall (0); a bank (anything else
	/// in bounds) is at least <see cref="BankQuality"/>; a neighbouring door keeps vanilla's door score, so gates set
	/// side by side across a wide canal line up as one barrier. The sum and tie-break are vanilla's.
	/// </summary>
	public static class RM_FlowDoorFacingMath
	{
		/// <summary>A bank's pull: below a real wall (vanilla 9) and a paired door (5), above a lone door (1).</summary>
		public const int BankQuality = 3;

		/// <param name="doorOnChannel">the flow door's own cell is dug; false = vanilla's score untouched</param>
		/// <param name="inBounds">the side cell is on the map</param>
		/// <param name="sideIsChannel">the side cell is dug or natural liquid</param>
		/// <param name="sideHasDoor">a door or door blueprint stands on the side cell</param>
		/// <param name="vanillaQuality">DoorUtility.AlignQualityAgainst for that side</param>
		public static int SideQuality(bool doorOnChannel, bool inBounds, bool sideIsChannel, bool sideHasDoor, int vanillaQuality)
		{
			if (!doorOnChannel)
			{
				return vanillaQuality;
			}
			if (!inBounds)
			{
				return 0;
			}
			if (sideHasDoor)
			{
				return vanillaQuality;
			}
			if (sideIsChannel)
			{
				return 0;
			}
			return vanillaQuality > BankQuality ? vanillaQuality : BankQuality;
		}

		/// <summary>Vanilla's sum and tie-break: true = Rot4.North (the leaf spans East-West), false = Rot4.East.</summary>
		public static bool FacesNorth(int east, int west, int north, int south)
		{
			return east + west >= north + south;
		}
	}
}
