using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_SINK_GEYSER_INTO_PIT_BUBBLING_HOT_TUB Mod Settings (own static class, scribed into the FlowWorks settings
	/// like RM_WallClimbSettings). Defaults are the shipped behaviour (spec design/specs/geyser_in_pit_hot_tub_2026-11-12.md
	/// section 3.5): every switch on. All off is today's game: the geyser stays drawn at the surface and puffs through any
	/// liquid, no plume, no pool. None affects worldgen.
	/// </summary>
	public static class RM_GeyserPitSettings
	{
		public static bool geyserSinksEnabled = true;
		public static bool geyserPlumeEnabled = true;
		public static float geyserPlumeDensity = 1f;
		public static bool geyserPoolEnabled = true;
		public static float geyserPoolReach = RM_GeyserTubMath.DefaultReach;
		public static float geyserPoolHealing = RM_GeyserTubMath.DefaultHealing;
		public static bool geyserPoolAfterglowEnabled = true;
		public static bool geyserPoolMoodEnabled = true;
		public static float geyserPoolMoodFactor = 1f;
		public static bool geyserPoolHidesClothes = true;
		public static bool geyserBathTarEnabled = true;
		public static bool geyserBathOilEnabled = true;
		public static bool geyserBathBloodEnabled = true;
		public static bool geyserBathSlimeEnabled = true;
		public static bool geyserBathFilthEnabled = true;
		public static bool geyserBathMoodCostEnabled = true;
		public static bool geyserBathSlipEnabled = true;
		public static bool geyserGeneratorOnSunkEnabled = true;

		// shipped value of every public static bool/float/int setting above. MUST stay below the LAST public setting field
		// (C# runs static initialisers in textual order).
		private static readonly System.Collections.Generic.Dictionary<string, object> shippedDefaults = RM_SettingsReset.Snapshot(typeof(RM_GeyserPitSettings));

		/// <summary>The Reset button: every setting on this screen back to its shipped value.</summary>
		public static void ResetAll()
		{
			RM_SettingsReset.ResetAll(typeof(RM_GeyserPitSettings), shippedDefaults);
		}

		public static void ExposeData()
		{
			Scribe_Values.Look(ref geyserSinksEnabled, "geyserSinksEnabled", true);
			Scribe_Values.Look(ref geyserPlumeEnabled, "geyserPlumeEnabled", true);
			Scribe_Values.Look(ref geyserPlumeDensity, "geyserPlumeDensity", 1f);
			Scribe_Values.Look(ref geyserPoolEnabled, "geyserPoolEnabled", true);
			Scribe_Values.Look(ref geyserPoolReach, "geyserPoolReach", RM_GeyserTubMath.DefaultReach);
			Scribe_Values.Look(ref geyserPoolHealing, "geyserPoolHealing", RM_GeyserTubMath.DefaultHealing);
			Scribe_Values.Look(ref geyserPoolAfterglowEnabled, "geyserPoolAfterglowEnabled", true);
			Scribe_Values.Look(ref geyserPoolMoodEnabled, "geyserPoolMoodEnabled", true);
			Scribe_Values.Look(ref geyserPoolMoodFactor, "geyserPoolMoodFactor", 1f);
			Scribe_Values.Look(ref geyserPoolHidesClothes, "geyserPoolHidesClothes", true);
			Scribe_Values.Look(ref geyserBathTarEnabled, "geyserBathTarEnabled", true);
			Scribe_Values.Look(ref geyserBathOilEnabled, "geyserBathOilEnabled", true);
			Scribe_Values.Look(ref geyserBathBloodEnabled, "geyserBathBloodEnabled", true);
			Scribe_Values.Look(ref geyserBathSlimeEnabled, "geyserBathSlimeEnabled", true);
			Scribe_Values.Look(ref geyserBathFilthEnabled, "geyserBathFilthEnabled", true);
			Scribe_Values.Look(ref geyserBathMoodCostEnabled, "geyserBathMoodCostEnabled", true);
			Scribe_Values.Look(ref geyserBathSlipEnabled, "geyserBathSlipEnabled", true);
			Scribe_Values.Look(ref geyserGeneratorOnSunkEnabled, "geyserGeneratorOnSunkEnabled", true);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Geysers in pits");
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, ResetAll);
			list.CheckboxLabeled("A geyser sinks with the pit dug on it", ref geyserSinksEnabled,
				"Dig all four squares of a steam geyser and it settles on the pit floor, at the depth of its shallowest square, "
			  + "and its steam rises from there. Fill the pit back in and it rises with it. Off: the geyser stays at the surface, "
			  + "no bubbles, no hot pool (every switch below needs this one).");
			list.CheckboxLabeled("A sunk geyser bubbles through liquid over it", ref geyserPlumeEnabled,
				"Liquid deeper than the vent mound over a sunk geyser turns its steam into a plume of bubbles in the liquid's own "
			  + "colour: strong while it sprays, gentle between. Thick liquids throw fewer, bigger bubbles. Drawing only. Off: a "
			  + "covered geyser neither puffs nor bubbles.");
			list.Label("How many plume bubbles: x" + geyserPlumeDensity.ToString("F1"));
			geyserPlumeDensity = Mathf.Round(list.Slider(geyserPlumeDensity, 0.2f, 3f) * 10f) / 10f;
			list.CheckboxLabeled("Pawns soak in a bubbling geyser pool", ref geyserPoolEnabled,
				"Up to " + RM_GeyserTubMath.MaxBathers + " pawns at a time soak in the bathable liquid around a covered, uncapped "
			  + "geyser as meditative recreation, or when ordered (right-click the geyser). While soaking: comfortable 50 degrees "
			  + "further either way, faster natural healing and better blood filtration. Off: bubbles only.");
			list.Label("Pool reach: " + geyserPoolReach.ToString("F1") + " squares from the vent's centre");
			geyserPoolReach = Mathf.Round(list.Slider(geyserPoolReach, 1.5f, 4.5f) * 2f) / 2f;
			list.Label("Natural healing while soaking and after: x" + geyserPoolHealing.ToString("F2") + " (shipped x"
			  + RM_GeyserTubMath.DefaultHealing.ToString("F2") + "; x1.00 keeps the joy and comfort, no healing)");
			geyserPoolHealing = Mathf.Round(list.Slider(geyserPoolHealing, 1f, 2f) * 20f) / 20f;
			list.CheckboxLabeled("After the pool: healing for about a day", ref geyserPoolAfterglowEnabled,
				"A soak leaves \"after the hot pool\": the same healing and blood filtration for about a day and a quarter. Off: the "
			  + "benefit ends when the soak does.");
			list.CheckboxLabeled("A soak gives the hot spring memory", ref geyserPoolMoodEnabled,
				"The game's own hot spring memory (+2 mood for about 2.4 hours) when a soak ends.");
			list.Label("Hot spring memory strength: x" + geyserPoolMoodFactor.ToString("F1"));
			geyserPoolMoodFactor = Mathf.Round(list.Slider(geyserPoolMoodFactor, 1f, 3f) * 10f) / 10f;
			list.CheckboxLabeled("Bathers set their clothes aside", ref geyserPoolHidesClothes,
				"A soaking pawn is drawn without clothes or headgear (never in portraits). Drawing only.");
			list.Label("Which liquids make a pool (water always does; acid, poison, boiling or icy water and fuels never do):");
			list.CheckboxLabeled("  Tar", ref geyserBathTarEnabled, "A tar bath: comes out tracking tar and a little sorry.");
			list.CheckboxLabeled("  Oil", ref geyserBathOilEnabled, "An oil bath: comes out dripping.");
			list.CheckboxLabeled("  Blood", ref geyserBathBloodEnabled, "A blood bath: comes out bloody and upset (psychopaths and the bloodlusting don't mind).");
			list.CheckboxLabeled("  Slime", ref geyserBathSlimeEnabled, "A slime bath: slips climbing out.");
			list.Label("The costs of a strange bath:");
			list.CheckboxLabeled("  Filth: bathers leave the liquid behind them", ref geyserBathFilthEnabled,
				"A few patches of tar, oil, blood or slime where the bather climbs out.");
			list.CheckboxLabeled("  Mood: a tar or blood bath is unpleasant", ref geyserBathMoodCostEnabled,
				"Tar: -2 mood for half a day. Blood: -4 for a day.");
			list.CheckboxLabeled("  Slipping: slime bathers fall climbing out", ref geyserBathSlipEnabled,
				"A two-second stun when the soak in slime ends.");
			list.CheckboxLabeled("A geothermal generator can cap a dry sunk geyser", ref geyserGeneratorOnSunkEnabled,
				"A generator may be built on a sunk geyser while no liquid stands over it. It caps the vent: power, but no bubbles "
			  + "and no pool, even if the pit is filled later. Off: a sunk geyser takes no generator.");
		}
	}
}
