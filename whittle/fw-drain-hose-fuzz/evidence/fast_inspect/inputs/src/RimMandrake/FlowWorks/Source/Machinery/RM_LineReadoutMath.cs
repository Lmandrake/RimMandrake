namespace RimMandrake.FlowWorks.Machinery
{
	// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 7 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P9):
	// the inspect lines that tell the four crossing cases apart: a cord lying on a deck, a pole-supported pipe span, a hose
	// down a ramp or ladder, and a segment disconnected by a raised drawbridge leaf. Pure: no Verse, no UnityEngine, so the
	// offline SelfTest compiles this file itself (LineReadoutChecks.cs). The game side reads the map and calls these:
	// Building_RM_PowerCord.GetInspectString, CompPipePoleReadout, CompHoseReel.CompInspectStringExtra. The levelling link's
	// own readout is RM_Levelling.Readout (PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL); flow direction stays undisplayed.
	public static class RM_LineReadoutMath
	{
		/// <summary>A cord over a raised leaf (it carries no power until the leaf is lowered).</summary>
		public const string CordLeafCut = "Disconnected: the drawbridge leaf under it is raised. It rejoins when the leaf is lowered.";

		/// <summary>A laid hose whose trail crosses a raised leaf (it has no end until the leaf is lowered).</summary>
		public const string HoseLeafCut = "Disconnected: a raised drawbridge leaf lies across the hose. It rejoins when the leaf is lowered.";

		/// <summary>What a flexible line lying on this surface says about it; null on solid ground (nothing to tell).</summary>
		public static string DeckLine(LineSurface s)
		{
			switch (s)
			{
				case LineSurface.Deck: return "Lying on a bridge deck.";
				case LineSurface.RopeDeck: return "Lying on a rope bridge deck.";
				case LineSurface.DrawbridgeLeaf: return "Lying on a lowered drawbridge leaf.";
				default: return null;
			}
		}

		/// <summary>The cord's crossing line: cut by a raised leaf first (its square then reads as dug ground), else the deck it
		/// lies on, else nothing.</summary>
		public static string CordLine(LineSurface s, bool leafRaisedUnder) => leafRaisedUnder ? CordLeafCut : DeckLine(s);

		/// <summary>A pipe pole's line: how many pipe spans it holds up and whether a pipe at the pole joins them to the liquid
		/// net (a pole is a fitting: a pipe under it or 8-way beside it). Null with no span strung (GSS's own "Pipe spans: 0/3"
		/// already says so).</summary>
		public static string PoleLine(int strungSpans, bool pipeAtPole)
		{
			if (strungSpans <= 0)
			{
				return null;
			}
			string what = strungSpans == 1 ? "Holds up a pipe span" : "Holds up " + strungSpans + " pipe spans";
			return pipeAtPole
				? what + " overhead: it carries the pipe at this pole across."
				: what + " overhead, but no pipe reaches this pole: build one under or beside it to carry liquid.";
		}

		/// <summary>A laid hose's level changes (counted along its lay, each one a ramp or a ladder by the band rule, P5). Null
		/// when it stays on one level.</summary>
		public static string HoseLevelLine(int ramps, int ladders)
		{
			if (ramps < 0) ramps = 0;
			if (ladders < 0) ladders = 0;
			int total = ramps + ladders;
			if (total == 0)
			{
				return null;
			}
			if (total == 1)
			{
				return ramps == 1 ? "Runs down a ramp into the dug ground." : "Hangs down a ladder into the dug ground.";
			}
			string by = ramps > 0 && ladders > 0 ? Count(ramps, "ramp") + " and " + Count(ladders, "ladder")
				: ramps > 0 ? Count(ramps, "ramp") : Count(ladders, "ladder");
			return "Changes level " + total + " times, by " + by + ".";
		}

		private static string Count(int n, string noun) => n == 1 ? "a " + noun : n + " " + noun + "s";
	}
}
