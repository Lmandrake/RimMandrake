namespace RimMandrake.FlowWorks.Machinery
{
	// POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P2):
	// when a power cord carries power. Pure: no Verse, no UnityEngine, so the offline SelfTest compiles this file itself
	// (PowerCordChecks.cs). The map side is Building_RM_PowerCord.cs.
	public static class RM_PowerCordMath
	{
		/// <summary>A cord transmits when its power comp would (vanilla: CompProperties_Power.transmitsPower) and no raised
		/// drawbridge leaf is under it. Raised, it is cut: the power net splits there and machines on the far side go dark;
		/// lowered, it rejoins. Flooding does not cut it (owner follow-up 2026-10-20: cords are insulated).</summary>
		public static bool TransmitsNow(bool compTransmits, bool leafRaisedUnder) => compTransmits && !leafRaisedUnder;

		/// <summary>The inspect line of a cut cord (null while it carries power).</summary>
		public static string CutLine(bool leafRaisedUnder) => leafRaisedUnder ? RM_LineReadoutMath.CordLeafCut : null;
	}
}
