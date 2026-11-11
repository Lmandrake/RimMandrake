namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT (stage S0 of design/RimMandrake/flowworks_bridges_design_2026-10-17.md):
	/// the Verse-free half of the one read every "is this cell decked?" call site makes. A deck gives a cell a WALKING
	/// height (metres below ground, 0 = the surface) apart from its FLOOR; everything that walks reads the walking
	/// height, while water, fire and flow stay at the floor (design §2). A pit cover is the trap tier: always at the
	/// surface, and nothing passes under it.
	///
	/// Compiled into the FlowWorks SelfTest (SpanBaseChecks) so these rules are proved on the production code.
	/// </summary>
	public static class RM_SpanMath
	{
		/// <summary>One depth notch, in metres (the dig model's 0.5 m step).</summary>
		public const float NotchM = 0.5f;

		/// <summary>The F − H ≥ 0.5 m rule (design §2 rule 3): a deck needs at least one notch of drop under it.</summary>
		public const int MinDropNotches = 1;

		/// <summary>Floor at least this many notches below the deck lets pawns pass under (2 m, design §2 rule 1, Q2). Read
		/// by SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD; a cover never sets the flag.</summary>
		public const int UnderpassClearanceNotches = 4;

		public struct DeckRead
		{
			public bool Decked;
			/// <summary>The walking height, metres below ground (0 = a surface deck).</summary>
			public float DeckHeightM;
			/// <summary>The floor band passes under this deck (pawns in the hole walk beneath it). Always false for a cover.</summary>
			public bool FloorBandPassesUnder;

			public DeckRead(bool decked, float deckHeightM, bool floorBandPassesUnder)
			{
				Decked = decked;
				DeckHeightM = decked ? (deckHeightM < 0f ? 0f : deckHeightM) : 0f;
				FloorBandPassesUnder = decked && floorBandPassesUnder;
			}

			public static DeckRead None => new DeckRead(false, 0f, false);

			public int DeckNotches => Notches(DeckHeightM);
		}

		/// <summary>The read every intact pit cover gives (the trap tier): decked, at the surface, nothing under.</summary>
		public static DeckRead CoverRead => new DeckRead(true, 0f, false);

		/// <summary>Metres below ground to whole notches (rounded to the nearest; never negative).</summary>
		public static int Notches(float metres)
		{
			if (metres <= 0f)
			{
				return 0;
			}
			return (int)(metres / NotchM + 0.5f);
		}

		/// <summary>The depth (notches) a walker on this cell reads: the deck's height on a decked cell (never deeper than
		/// the floor itself), the floor otherwise. A cover reads 0, the old "a covered cell is ground" rule.</summary>
		public static int WalkingDepth(int floorNotches, DeckRead read)
		{
			if (!read.Decked)
			{
				return floorNotches;
			}
			int h = read.DeckNotches;
			return h < floorNotches ? h : floorNotches;
		}

		/// <summary>Design §2 rule 3: a span over this floor at this deck height has its drop (for the builders' place workers).</summary>
		public static bool HasDrop(int floorNotches, int deckNotches)
		{
			return floorNotches - deckNotches >= MinDropNotches;
		}

		/// <summary>Design §2 rule 1: pawns may pass beneath a deck when the floor is at least 2 m below it.</summary>
		public static bool ClearsUnderpass(int floorNotches, int deckNotches)
		{
			return floorNotches - deckNotches >= UnderpassClearanceNotches;
		}
	}
}
