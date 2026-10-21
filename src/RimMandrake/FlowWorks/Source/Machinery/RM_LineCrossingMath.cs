namespace RimMandrake.FlowWorks.Machinery
{
	// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 1 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md
	// §Ruled design P1, P2): the four kinds of line and the one crossing table. Pure: no Verse, no UnityEngine, so the offline
	// SelfTest compiles this file itself (LineCrossingChecks.cs). The map side (which surface a square is, the def tag, the
	// Harmony gates) is RM_LineCrossing.cs.

	/// <summary>P1: what a line IS, set on its def (RM_LineKindExtension), never read from its style or from
	/// building.isPowerConduit: Gimme Some Slack restyles vanilla PowerConduit, and a restyled conduit is still rigid (review
	/// answer 5).</summary>
	public enum LineKind
	{
		/// <summary>RM_UniversalPipe.</summary>
		RigidPipe = 0,
		/// <summary>Vanilla PowerConduit and the conduits inheriting it (hidden, waterproof), with or without the GSS restyle.</summary>
		RigidConduit = 1,
		/// <summary>The flexible power cord (its def is POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS; not built yet).</summary>
		FlexCord = 2,
		/// <summary>The FlowWorks hose (a route laid from a reel, not a buildable def: its router reads this table).</summary>
		Hose = 3,
	}

	/// <summary>P2's rows: what a square is, as a line sees it. A deck or cover over a dug square is the deck or cover; a
	/// raised drawbridge leaf is not ground (the hole under it is whole again), so its square reads Excavated.</summary>
	public enum LineSurface
	{
		SolidGround = 0,
		/// <summary>A dug square of any depth: pit, trench, canal, moat (owner follow-up 2026-10-20: any dug channel).</summary>
		Excavated = 1,
		/// <summary>An intact pit cover.</summary>
		Cover = 2,
		/// <summary>An intact timber, steel or heavy suspension deck (a jetty included).</summary>
		Deck = 3,
		/// <summary>An intact rope suspension deck: same row as Deck, kept apart so the table is checked on rope by name.</summary>
		RopeDeck = 4,
		/// <summary>A lowered drawbridge leaf square.</summary>
		DrawbridgeLeaf = 5,
	}

	public enum CrossingVerdict
	{
		Allowed = 0,
		Refused = 1,
		/// <summary>A hose into an excavated square: only down a ramp or a ladder (P5; the hose router enforces it).</summary>
		RampOrLadderOnly = 2,
	}

	/// <summary>What stands on a square, read off the map by RM_LineCrossing.SurfaceAt and folded here.</summary>
	public enum DeckOnSquare
	{
		None = 0,
		Cover = 1,
		Deck = 2,
		RopeDeck = 3,
		DrawbridgeLeaf = 4,
	}

	public static class RM_LineCrossingMath
	{
		public const int KindCount = 4;
		public const int SurfaceCount = 6;

		/// <summary>Cords and hoses bend; pipe and conduit do not.</summary>
		public static bool IsFlexible(LineKind k) => k == LineKind.FlexCord || k == LineKind.Hose;

		/// <summary>The P2 table. Rigid pipe and conduit: solid ground only (owner answer 1: "Can't build there"). Cords and
		/// hoses: any deck, rope included, and a lowered drawbridge leaf (answer 4 and its follow-up; a raised leaf disconnects
		/// them, RM_Drawbridges.LineCutAt). A cover carries nothing (answer 3). A hose may enter a dug square only by a ramp or a
		/// ladder (answer 5); a cord never lies in one.</summary>
		public static CrossingVerdict Verdict(LineKind k, LineSurface s)
		{
			switch (s)
			{
				case LineSurface.SolidGround:
					return CrossingVerdict.Allowed;
				case LineSurface.Cover:
					return CrossingVerdict.Refused;
				case LineSurface.Excavated:
					return k == LineKind.Hose ? CrossingVerdict.RampOrLadderOnly : CrossingVerdict.Refused;
				case LineSurface.Deck:
				case LineSurface.RopeDeck:
				case LineSurface.DrawbridgeLeaf:
					return IsFlexible(k) ? CrossingVerdict.Allowed : CrossingVerdict.Refused;
				default:
					return CrossingVerdict.Refused;
			}
		}

		/// <summary>May a BUILT line (placement, frame completion, rebuild) of this kind stand on this surface? A hose is never a
		/// built line, and RampOrLadderOnly is a router rule, so only Allowed passes here.</summary>
		public static bool MayBuild(LineKind k, LineSurface s) => Verdict(k, s) == CrossingVerdict.Allowed;

		/// <summary>The surface from the two facts the map gives: is the square dug, and what intact deck stands on it. A deck or
		/// cover wins over the hole under it.</summary>
		public static LineSurface Classify(bool excavated, DeckOnSquare deck)
		{
			switch (deck)
			{
				case DeckOnSquare.Cover: return LineSurface.Cover;
				case DeckOnSquare.Deck: return LineSurface.Deck;
				case DeckOnSquare.RopeDeck: return LineSurface.RopeDeck;
				case DeckOnSquare.DrawbridgeLeaf: return LineSurface.DrawbridgeLeaf;
				default: return excavated ? LineSurface.Excavated : LineSurface.SolidGround;
			}
		}

		public static string KindLabel(LineKind k)
		{
			switch (k)
			{
				case LineKind.RigidPipe: return "Pipe";
				case LineKind.RigidConduit: return "Conduit";
				case LineKind.FlexCord: return "A power cord";
				default: return "A hose";
			}
		}

		/// <summary>The refusal shown on the blueprint, or null when the line may stand there.</summary>
		public static string RefusalReason(LineKind k, LineSurface s)
		{
			CrossingVerdict v = Verdict(k, s);
			if (v == CrossingVerdict.Allowed)
			{
				return null;
			}
			string who = KindLabel(k);
			switch (s)
			{
				case LineSurface.Cover:
					return "A pit cover carries no lines.";
				case LineSurface.Excavated:
					return v == CrossingVerdict.RampOrLadderOnly
						? "A hose goes down into a dug square only by a ramp or a ladder."
						: who + " cannot be built on dug ground. Cross a pit, trench or canal on poles.";
				default:
					return who + " cannot be built on a bridge deck: it is rigid. Cross on poles, or use a flexible line.";
			}
		}
	}
}
