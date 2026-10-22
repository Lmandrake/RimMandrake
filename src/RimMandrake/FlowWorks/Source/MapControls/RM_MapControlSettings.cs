using Verse;

namespace RimMandrake.FlowWorks.MapControls
{
	/// <summary>FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS: the map controls' Mod Settings section (same shape as
	/// RM_SprinklerSettings). Defaults = shipped behaviour. Off: every placed map control (flow source, sink and the
	/// FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES six) stands as an inert marker; nothing is removed from the map, so switching
	/// back on resumes them.</summary>
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
			list.Label("Map controls (flow source, sink, meter, level holder, timer, map-edge setter, current painter, thermostat)");
			list.CheckboxLabeled("Map controls work", ref mapControlsEnabled,
				"Map controls are small plain stones a map maker places in development mode (they cannot be built). A source "
				+ "pours a chosen liquid into the dug channel it stands on or beside, at a set rate; a sink takes liquid out the "
				+ "same way; a level holder keeps a channel or pond at a set fill; a meter reads a channel or pond; a timer switches "
				+ "the controls, sluice gates and grates near it by the clock; a map-edge setter seals or drains each map edge; a "
				+ "current painter gives still water a current; a thermostat holds a liquid's room at a set temperature. Off: "
				+ "every placed control stays on the map but does nothing, and the map edges follow the automatic rules.");
		}
	}
}
