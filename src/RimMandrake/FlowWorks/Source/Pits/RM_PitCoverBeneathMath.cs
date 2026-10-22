namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// PIT_COVER_FIX_OCCUPANT_STAYS_BELOW (owner card 2026-10-21: "What should happen to a pawn already in a pit under a
	/// cover? → Stays below, hidden"): the pure rules for a pawn that was down in a pit when a concealed pit's lid was laid
	/// over it. It stays on the floor, hidden by the lid; it is held there; it may leave only along the floor into an OPEN pit
	/// square (no lid) it could step to, after which the ordinary pit rules have it.
	///
	/// Conservative rule (open question for the owner, noted on the item): a step from under one lid to under another lid is
	/// refused, so a pawn under the covered part of a partly covered pit does not wander beneath the lids. Diagonal steps are
	/// refused (a corner square may be ground the pawn would brush past). No Verse types: linked into the SelfTest project.
	/// </summary>
	public static class RM_PitCoverBeneathMath
	{
		/// <summary>Does a pawn standing on the square when a lid is laid go beneath it? Only a living walker down in a dug
		/// square, and only for a lid built now (a loaded save keeps its own saved set).</summary>
		public static bool TakesBeneath(bool dugSquare, bool dead, bool flying, bool loadingSave)
		{
			return dugSquare && !dead && !flying && !loadingSave;
		}

		/// <summary>May a pawn beneath a lid step from its floor (depth fromFloor, notches) to the neighbouring square?
		/// toDug: the square is dug (a pit floor at toFloor); toCovered: an intact lid stands there; k: the pawn's climb limit.</summary>
		public static bool StepAllowed(bool diagonal, bool toDug, bool toCovered, int fromFloor, int toFloor, int k)
		{
			if (diagonal || !toDug || toCovered || toFloor <= 0)
			{
				return false;
			}
			return RM_PitTrapMath.StepAllowed(fromFloor, toFloor, k);
		}

		/// <summary>Sealed in: none of the four neighbouring steps is allowed.</summary>
		public static bool Trapped(bool n, bool e, bool s, bool w)
		{
			return !(n || e || s || w);
		}
	}
}
