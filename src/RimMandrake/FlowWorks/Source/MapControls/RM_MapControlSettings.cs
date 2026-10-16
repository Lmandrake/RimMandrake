using Verse;

namespace RimMandrake.FlowWorks.MapControls
{
	/// <summary>FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS: the map controls' Mod Settings section (same shape as
	/// RM_SluiceGateSettings). Defaults = shipped behaviour. Off: every placed flow source and flow sink stands as an inert
	/// marker that moves no liquid; nothing is removed from the map, so switching back on resumes them.</summary>
	public static class RM_MapControlSettings
	{
		public static bool mapControlsEnabled = true;

		public static void ExposeData()
		{
			Scribe_Values.Look(ref mapControlsEnabled, "mapControlsEnabled", true);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Map controls (flow sources and sinks)");
			list.CheckboxLabeled("Flow sources and flow sinks work", ref mapControlsEnabled,
				"Flow sources and flow sinks are plain markers a map maker places in development mode (they cannot be "
				+ "built). A source pours a chosen liquid into the dug channel it stands on or beside, at a set rate; a sink "
				+ "takes liquid out the same way. Off: every placed source and sink stays on the map but moves nothing.");
		}
	}
}
