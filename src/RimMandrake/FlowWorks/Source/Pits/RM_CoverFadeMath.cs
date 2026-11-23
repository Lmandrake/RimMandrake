namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// RIMMANDRAKE_FADE_EVERY_PIT_COVER_TRANSPARENT_OVER_A_PAWN_LIGHTEN_PLEASED_HIM (owner, 2026-11-22: "It would be even
	/// cooler if they became transparent rather than merely lightened, to show both 'over and under' at the same time. This
	/// should be applied to any 'covering' that a pit can have, bridge, planks, hidden, etc."). The pure look of a span
	/// square while a pawn is down beneath it: the opaque print of that square is held back (the hole and the pawn show),
	/// the span is drawn over them at <see cref="UnderAlpha"/>, and the pawn beneath is drawn. With nobody beneath, the span
	/// prints as ever. Read by Building_SuspensionDeck.Print, Building_PitCover.Print, the fade pass in
	/// RM_MapComponent_SuspensionBridges.MapComponentUpdate and the pit lip occluder (RM_SuspensionUnderpass.SeenDepthAt).
	/// </summary>
	public static class RM_CoverFadeMath
	{
		/// <summary>The span's alpha over a pawn beneath it: the bridge fade the owner liked at station 51 (2026-11-22,
		/// RM_MapComponent_SuspensionBridges.UnderFade, 0.6).</summary>
		public const float UnderAlpha = 0.6f;

		/// <summary>Every kind of covering a pit can have.</summary>
		public enum SpanLook
		{
			/// <summary>A suspension bridge's deck square (and a raised-leaf drawbridge's, which is one).</summary>
			SuspensionDeck = 0,
			/// <summary>A pit cover printing its own art (plank, woven, reinforced lid beside an open pit square).</summary>
			PitCoverArt = 1,
			/// <summary>A concealed pit cover printing the surrounding ground (or the terrain mimic).</summary>
			PitCoverConcealed = 2,
		}

		public struct Look
		{
			/// <summary>The square's opaque print is held back (so what is beneath shows through).</summary>
			public bool PrintSuppressed;
			/// <summary>The span drawn over the square at this alpha (0 = no overdraw).</summary>
			public float OverAlpha;
			/// <summary>The pawn beneath is drawn (with its name label).</summary>
			public bool PawnDrawn;

			public Look(bool printSuppressed, float overAlpha, bool pawnDrawn)
			{
				PrintSuppressed = printSuppressed;
				OverAlpha = overAlpha;
				PawnDrawn = pawnDrawn;
			}
		}

		/// <summary>The look of one span square of this kind, with or without a pawn beneath it.</summary>
		public static Look For(SpanLook kind, bool pawnBeneath)
		{
			if (!pawnBeneath)
			{
				return new Look(false, 0f, true);
			}
			return new Look(true, UnderAlpha, true);
		}

		/// <summary>The depth a square SHOWS to the pit lip search: an intact lid that is not faded shows its walking height
		/// (ground), so it occludes a pawn in the hole beside it; a faded lid (someone beneath) and anything else show the
		/// hollow depth.</summary>
		public static int SeenDepth(int hollow, bool lid, bool faded, int walkDepth)
		{
			return hollow > 0 && lid && !faded ? walkDepth : hollow;
		}
	}
}
