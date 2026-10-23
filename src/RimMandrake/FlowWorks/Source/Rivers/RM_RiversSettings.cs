using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Rivers
{
	/// <summary>
	/// The Rivers section of FlowWorks' Mod Settings (design §5; River Works merged into FlowWorks
	/// 2026-10-05, owner: "I think river works needs to be part of flow works."). Not a ModSettings of
	/// its own: RimMandrakeFlowWorksSettings.ExposeData scribes these fields into FlowWorks' one settings
	/// file, and its window draws DoSettingsSection under a "Rivers" heading. Keys are unique across
	/// that file (selftest_flowworks_rivers.py checks). Defaults = shipped behaviour; all-off degrades to
	/// still vanilla rivers, never an error. No toggle changes map generation: the current is
	/// derived from vanilla's own saved riverFlowMap, so flipping it mid-game is safe.
	/// Numbers marked PROVISIONAL are guesses awaiting a live look, not rulings.
	/// </summary>
	public static class RM_RiversSettings
	{
		public static bool riverWorksEnabled = true;
		public static bool surfaceCurrentEnabled = true;
		public static float currentStrength = 1f;
		public static int centreTicksPerCell = 45;
		public static int marginTicksPerCell = 90;
		public static float itemDriftFactor = 2f;
		// Owner card 1 (2026-10-03): bigger rivers shove harder. Curve PROVISIONAL (RM_RiverMath.SizeFactor).
		public static bool scaleWithRiverSize = true;
		// Owner card 1: a spring flood makes the river fiercer.
		public static bool floodSurgeEnabled = true;
		public static bool countSeasonalFloods = true;
		public static bool countTorrentialRainFloods = true;
		public static bool carryAnimals = true;
		public static bool carryStrangers = true;
		public static bool carryItems = true;
		// Owner by card 2026-10-23 07:19 ("Flotsam? -> Yes, occasional flotsam"): the river brings its biome's drift onto the
		// map at the upstream edge as real floating things; what reaches the downstream edge floats on off the map.
		public static bool flotsamEnabled = true;
		public static float flotsamPerDay = 1f;               // PROVISIONAL, "default modest"
		// Owner card 1: swept to the map edge = washed away, walks home later, with a letter.
		public static bool washOffMapEdge = true;
		public static float washedAwayMinDays = 1f;   // PROVISIONAL
		public static float washedAwayMaxDays = 3f;   // PROVISIONAL
		// TAKEN_BY_LAND_SERVICE_1: a ground trace at the spot a pawn was taken (every taker that uses the service).
		public static bool takenByLandTraceEnabled = true;
		// Owner card 1: colonists path around strong water to bridges/fords (drafted still go).
		public static bool pathfinderAvoidsCurrents = true;
		// Owner card 2: being swept bruises and can make a pawn drop what it carries.
		public static bool crossingHazardsEnabled = true;
		public static float bruiseChancePerStep = 0.15f;   // PROVISIONAL
		public static float dropChancePerStep = 0.25f;     // PROVISIONAL
		public static bool fordsEnabled = true;

		// ── the works (slice 2: moved out of TerminalBiomes) ─────────────────
		public static bool bankWorksEnabled = true;
		public static float wearRateMultiplier = 1f;          // PROVISIONAL
		// Owner on TWILIGHT_CHANNEL_CURRENT_1: "breach at default".
		public static bool breachEnabled = true;
		public static float breachHpFraction = 0.5f;          // PROVISIONAL
		public static int stakeSnapTicksPerCell = 150;        // PROVISIONAL
		// Owner card (2026-10-03): a continuous stake-line holds spring floods like a levee.
		public static bool stakeLineLevee = true;
		// Owner card 2: the weir calms a long stretch, ~8 cells upstream.
		public static int weirPoolLength = 8;
		// Owner 2026-10-23 (WEIR_CATCH_FIX_NO_FREE_FISH): "they should just capture anything floating downstream. No auto
		// fish capture." The weir lifts what the current carried into it onto its bank; it creates nothing.
		public static bool weirCapturesFloating = true;
		public static int weirHeldCatchCap = 30;              // PROVISIONAL
		// Owner 2026-10-23 (WEIR_LOOK_REDESIGN_WHITEWATER_FROZEN_SOLID): white water "needs to be an animated effect".
		public static bool weirWhiteWater = true;
		// Owner ruling 4: a breach washes the held catch a few cells downstream.
		public static bool breachWashesCatch = true;
		public static int breachWashCells = 4;                // PROVISIONAL
		public static bool siltRichening = true;
		public static float siltIntervalDays = 0.5f;          // PROVISIONAL
		// Owner card 3: the rope ferry is in the first version.
		public static bool ferryEnabled = true;
		public static int ferryMaxSpan = 40;                  // PROVISIONAL
		// Taken over 2026-10-05 (slice 2's known limit): undrafted colonists treat the rope as a crossing.
		public static bool ferryRopeGuidesColonists = true;

		public static bool CurrentActive => RM_RiverMath.CurrentOn(riverWorksEnabled, surfaceCurrentEnabled);

		public static bool WorksActive => RM_RiverMath.WorksOn(riverWorksEnabled, bankWorksEnabled);

		// FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING: shipped values (MUST stay below the LAST public setting field) and the two
		// section lists the window's Reset buttons use (THE CURRENT with the master switch; WORKS with fords).
		private static readonly System.Collections.Generic.Dictionary<string, object> shippedDefaults = RM_SettingsReset.Snapshot(typeof(RM_RiversSettings));
		public static readonly string[] CurrentFields = { "riverWorksEnabled", "surfaceCurrentEnabled", "currentStrength", "centreTicksPerCell", "marginTicksPerCell", "itemDriftFactor", "scaleWithRiverSize", "floodSurgeEnabled", "countSeasonalFloods", "countTorrentialRainFloods", "carryAnimals", "carryStrangers", "carryItems", "flotsamEnabled", "flotsamPerDay", "washOffMapEdge", "washedAwayMinDays", "washedAwayMaxDays", "takenByLandTraceEnabled", "pathfinderAvoidsCurrents", "crossingHazardsEnabled", "bruiseChancePerStep", "dropChancePerStep" };
		public static readonly string[] WorksFields = { "fordsEnabled", "bankWorksEnabled", "wearRateMultiplier", "breachEnabled", "breachHpFraction", "stakeSnapTicksPerCell", "stakeLineLevee", "weirPoolLength", "weirCapturesFloating", "weirHeldCatchCap", "weirWhiteWater", "breachWashesCatch", "breachWashCells", "siltRichening", "siltIntervalDays", "ferryEnabled", "ferryMaxSpan", "ferryRopeGuidesColonists" };

		public static void ResetFields(string[] names) => RM_SettingsReset.Reset(typeof(RM_RiversSettings), shippedDefaults, names);

		public static void ExposeData()
		{
			Scribe_Values.Look(ref riverWorksEnabled, "riverWorksEnabled", true);
			Scribe_Values.Look(ref surfaceCurrentEnabled, "surfaceCurrentEnabled", true);
			Scribe_Values.Look(ref currentStrength, "currentStrength", 1f);
			Scribe_Values.Look(ref centreTicksPerCell, "centreTicksPerCell", 45);
			Scribe_Values.Look(ref marginTicksPerCell, "marginTicksPerCell", 90);
			Scribe_Values.Look(ref itemDriftFactor, "itemDriftFactor", 2f);
			Scribe_Values.Look(ref scaleWithRiverSize, "scaleWithRiverSize", true);
			Scribe_Values.Look(ref floodSurgeEnabled, "floodSurgeEnabled", true);
			Scribe_Values.Look(ref countSeasonalFloods, "countSeasonalFloods", true);
			Scribe_Values.Look(ref countTorrentialRainFloods, "countTorrentialRainFloods", true);
			Scribe_Values.Look(ref carryAnimals, "carryAnimals", true);
			Scribe_Values.Look(ref carryStrangers, "carryStrangers", true);
			Scribe_Values.Look(ref carryItems, "carryItems", true);
			Scribe_Values.Look(ref flotsamEnabled, "flotsamEnabled", true);
			Scribe_Values.Look(ref flotsamPerDay, "flotsamPerDay", 1f);
			Scribe_Values.Look(ref washOffMapEdge, "washOffMapEdge", true);
			Scribe_Values.Look(ref washedAwayMinDays, "washedAwayMinDays", 1f);
			Scribe_Values.Look(ref washedAwayMaxDays, "washedAwayMaxDays", 3f);
			Scribe_Values.Look(ref takenByLandTraceEnabled, "takenByLandTraceEnabled", true);
			Scribe_Values.Look(ref pathfinderAvoidsCurrents, "pathfinderAvoidsCurrents", true);
			Scribe_Values.Look(ref crossingHazardsEnabled, "crossingHazardsEnabled", true);
			Scribe_Values.Look(ref bruiseChancePerStep, "bruiseChancePerStep", 0.15f);
			Scribe_Values.Look(ref dropChancePerStep, "dropChancePerStep", 0.25f);
			Scribe_Values.Look(ref fordsEnabled, "fordsEnabled", true);
			Scribe_Values.Look(ref bankWorksEnabled, "bankWorksEnabled", true);
			Scribe_Values.Look(ref wearRateMultiplier, "wearRateMultiplier", 1f);
			Scribe_Values.Look(ref breachEnabled, "breachEnabled", true);
			Scribe_Values.Look(ref breachHpFraction, "breachHpFraction", 0.5f);
			Scribe_Values.Look(ref stakeSnapTicksPerCell, "stakeSnapTicksPerCell", 150);
			Scribe_Values.Look(ref stakeLineLevee, "stakeLineLevee", true);
			Scribe_Values.Look(ref weirPoolLength, "weirPoolLength", 8);
			Scribe_Values.Look(ref weirCapturesFloating, "weirCapturesFloating", true);
			Scribe_Values.Look(ref weirHeldCatchCap, "weirHeldCatchCap", 30);
			Scribe_Values.Look(ref weirWhiteWater, "weirWhiteWater", true);
			Scribe_Values.Look(ref breachWashesCatch, "breachWashesCatch", true);
			Scribe_Values.Look(ref breachWashCells, "breachWashCells", 4);
			Scribe_Values.Look(ref siltRichening, "siltRichening", true);
			Scribe_Values.Look(ref siltIntervalDays, "siltIntervalDays", 0.5f);
			Scribe_Values.Look(ref ferryEnabled, "ferryEnabled", true);
			Scribe_Values.Look(ref ferryMaxSpan, "ferryMaxSpan", 40);
			Scribe_Values.Look(ref ferryRopeGuidesColonists, "ferryRopeGuidesColonists", true);
		}
	}

	public static class RM_RiversSettingsWindow
	{
		/// <summary>Drawn inside FlowWorks' settings window, after its own sections.</summary>
		public static void DoSettingsSection(Listing_Standard l)
		{
			l.GapLine();
			Text.Font = GameFont.Medium;
			l.Label("Rivers");
			Text.Font = GameFont.Small;

			l.CheckboxLabeled("Rivers enabled", ref RM_RiversSettings.riverWorksEnabled,
				"Master switch for everything in this section. Off: rivers are vanilla still water and none of it does anything.");
			l.GapLine();
			l.Label("THE CURRENT");
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(l, () => RM_RiversSettings.ResetFields(RM_RiversSettings.CurrentFields));
			l.CheckboxLabeled("Surface rivers have a current", ref RM_RiversSettings.surfaceCurrentEnabled,
				"Moving river water shoves pawns and loose items downstream. Chest-deep water is the fast "
			  + "lane and cannot be waded out of; shallow water is the edge lane and can still be crossed. "
			  + "Off: rivers are vanilla. Safe to change mid-game (the flow is read from the map itself).");
			l.Label("Current strength: x" + RM_RiversSettings.currentStrength.ToString("F2"));
			RM_RiversSettings.currentStrength = l.Slider(RM_RiversSettings.currentStrength, 0.25f, 3f);
			l.Label("Fast lane: " + (RM_RiversSettings.centreTicksPerCell / 60f).ToString("0.00") + " s to cross a square");
			RM_RiversSettings.centreTicksPerCell = Mathf.RoundToInt(l.Slider(RM_RiversSettings.centreTicksPerCell, 10f, 200f));
			l.Label("Edge lane: " + (RM_RiversSettings.marginTicksPerCell / 60f).ToString("0.00") + " s to cross a square");
			RM_RiversSettings.marginTicksPerCell = Mathf.RoundToInt(l.Slider(RM_RiversSettings.marginTicksPerCell, 20f, 400f));
			l.Label("Items drift slower by x" + RM_RiversSettings.itemDriftFactor.ToString("F1"));
			RM_RiversSettings.itemDriftFactor = l.Slider(RM_RiversSettings.itemDriftFactor, 1f, 5f);
			l.CheckboxLabeled("Bigger rivers shove harder", ref RM_RiversSettings.scaleWithRiverSize,
				"Creeks barely push; huge rivers are lethal. Off: every river shoves the same.");
			l.CheckboxLabeled("Floods make the river fiercer", ref RM_RiversSettings.floodSurgeEnabled,
				"While a flood is on the map the edge lane behaves as the fast lane and the fast lane "
			  + "moves twice as fast.");
			if (RM_RiversSettings.floodSurgeEnabled)
			{
				l.CheckboxLabeled("  Spring (seasonal) floods count", ref RM_RiversSettings.countSeasonalFloods,
					"On, the yearly spring flood of a river makes its current fiercer too. Off: spring floods leave the current as it is.");
				l.CheckboxLabeled("  Torrential-rain floods count", ref RM_RiversSettings.countTorrentialRainFloods,
					"On, a flood from torrential rain makes the current fiercer too. Off: rain floods leave the current as it is.");
			}
			l.CheckboxLabeled("Carry animals", ref RM_RiversSettings.carryAnimals,
				"On, a strong current can sweep animals off their feet and carry them downstream. Off: animals are never carried.");
			l.CheckboxLabeled("Carry visitors and raiders", ref RM_RiversSettings.carryStrangers,
				"On, a strong current can carry visitors and raiders downstream. Off: they are never swept away.");
			l.CheckboxLabeled("Carry loose items and corpses", ref RM_RiversSettings.carryItems,
				"On, loose items and corpses lying in strong water drift downstream. Off: they stay where they lie.");
			l.CheckboxLabeled("Rivers bring flotsam", ref RM_RiversSettings.flotsamEnabled,
				"Now and then the river carries something of this country onto the map at its upstream edge - fruit, forage, "
			  + "hides - which drifts down with the current. A weir catches it; what reaches the downstream edge floats on off "
			  + "the map. It drifts only while items are carried (above).");
			if (RM_RiversSettings.flotsamEnabled)
			{
				l.Label("  About " + RM_RiversSettings.flotsamPerDay.ToString("0.0") + " pieces a day per map");
				RM_RiversSettings.flotsamPerDay = l.Slider(RM_RiversSettings.flotsamPerDay, 0.1f, 10f);
			}
			l.CheckboxLabeled("Washed off the map at the edge", ref RM_RiversSettings.washOffMapEdge,
				"A pawn carried to the edge of the map is washed away. Your own people walk home a few days "
			  + "later; a letter says so when it happens. Off: the current stops at the map edge.");
			if (RM_RiversSettings.washOffMapEdge)
			{
				l.Label("Days before a washed-away colonist walks home: "
				  + RM_RiversSettings.washedAwayMinDays.ToString("F1") + " to " + RM_RiversSettings.washedAwayMaxDays.ToString("F1"));
				RM_RiversSettings.washedAwayMinDays = l.Slider(RM_RiversSettings.washedAwayMinDays, 0.25f, 10f);
				RM_RiversSettings.washedAwayMaxDays = Mathf.Max(RM_RiversSettings.washedAwayMinDays,
					l.Slider(RM_RiversSettings.washedAwayMaxDays, 0.25f, 15f));
			}
			l.CheckboxLabeled("A trace marks where someone was taken", ref RM_RiversSettings.takenByLandTraceEnabled,
				"When the river (or the dune gale) takes a pawn away, a drag mark is left on the ground where they stood, so no one "
			  + "vanishes without a readable sign. Needs Creature Behaviors for the mark. Off: no mark, the letter still comes.");
			l.CheckboxLabeled("Colonists avoid strong water", ref RM_RiversSettings.pathfinderAvoidsCurrents,
				"Undrafted colonists route around moving water to bridges and fords. Drafted orders still go "
			  + "where they are told.");
			l.CheckboxLabeled("Being swept is dangerous", ref RM_RiversSettings.crossingHazardsEnabled,
				"In the fast lane a carried pawn can be bruised and can drop what it is carrying.");
			if (RM_RiversSettings.crossingHazardsEnabled)
			{
				l.Label("Bruise chance per square: " + RM_RiversSettings.bruiseChancePerStep.ToStringPercent());
				RM_RiversSettings.bruiseChancePerStep = l.Slider(RM_RiversSettings.bruiseChancePerStep, 0f, 1f);
				l.Label("Drop-carried chance per square: " + RM_RiversSettings.dropChancePerStep.ToStringPercent());
				RM_RiversSettings.dropChancePerStep = l.Slider(RM_RiversSettings.dropChancePerStep, 0f, 1f);
			}
			l.GapLine();
			l.Label("WORKS");
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(l, () => RM_RiversSettings.ResetFields(RM_RiversSettings.WorksFields));
			l.CheckboxLabeled("Fords stop the current", ref RM_RiversSettings.fordsEnabled,
				"Nothing is carried on or beside ford stones. Off: fords are just stone footing.");
			l.CheckboxLabeled("Bank works active (weir, stakes, silt-trap, ferry)", ref RM_RiversSettings.bankWorksEnabled,
				"Off: the works stand inert - no wear, no catch, no breach, no richening, no ferry rope.");
			l.Label("Wear rate: x" + RM_RiversSettings.wearRateMultiplier.ToString("F2"));
			RM_RiversSettings.wearRateMultiplier = l.Slider(RM_RiversSettings.wearRateMultiplier, 0f, 3f);
			l.CheckboxLabeled("Untended weirs breach in a flood", ref RM_RiversSettings.breachEnabled,
				"A weir run below the threshold when a flood arrives breaks: its catch washes downstream, the "
			  + "stake-line below it snaps post by post, and nearby silt-traps lose their richened ground.");
			if (RM_RiversSettings.breachEnabled)
			{
				l.Label("Breach below HP: " + RM_RiversSettings.breachHpFraction.ToStringPercent());
				RM_RiversSettings.breachHpFraction = l.Slider(RM_RiversSettings.breachHpFraction, 0.05f, 1f);
				l.Label("Stake snap: " + (RM_RiversSettings.stakeSnapTicksPerCell / 60f).ToString("0.00") + " s a square");
				RM_RiversSettings.stakeSnapTicksPerCell = Mathf.RoundToInt(l.Slider(RM_RiversSettings.stakeSnapTicksPerCell, 10f, 1000f));
				l.CheckboxLabeled("  Breach washes the held catch downstream", ref RM_RiversSettings.breachWashesCatch,
					"On, a weir that breaches lets the catch it was holding wash downstream. Off: the catch stays on the bank.");
				if (RM_RiversSettings.breachWashesCatch)
				{
					l.Label("  Washed this many squares: " + RM_RiversSettings.breachWashCells);
					RM_RiversSettings.breachWashCells = Mathf.RoundToInt(l.Slider(RM_RiversSettings.breachWashCells, 1f, 20f));
				}
			}
			l.CheckboxLabeled("A continuous stake-line holds floods (levee)", ref RM_RiversSettings.stakeLineLevee,
				"Floodwater cannot pass a stake. Any gap lets it in. Off: floods flow through stake-lines.");
			l.Label("Weir calms this many squares upstream: " + RM_RiversSettings.weirPoolLength + " (0 = its own square only)");
			RM_RiversSettings.weirPoolLength = Mathf.RoundToInt(l.Slider(RM_RiversSettings.weirPoolLength, 0f, 20f));
			l.CheckboxLabeled("Weirs catch what floats into them", ref RM_RiversSettings.weirCapturesFloating,
				"Items and corpses the current carries into a weir are lifted onto its bank as its catch, to be hauled. "
			  + "A weir never makes fish or anything else. Off: things pile up against the wall in the water.");
			if (RM_RiversSettings.weirCapturesFloating)
			{
				l.Label("  Weir holds at most " + RM_RiversSettings.weirHeldCatchCap + " items before it stops catching");
				RM_RiversSettings.weirHeldCatchCap = Mathf.RoundToInt(l.Slider(RM_RiversSettings.weirHeldCatchCap, 5f, 200f));
			}
			l.CheckboxLabeled("Animated white water below weirs", ref RM_RiversSettings.weirWhiteWater,
				"Tumbling foam where the river falls over a weir, stronger in fast water and floods. Off: no foam is drawn.");
			l.CheckboxLabeled("Silt-traps richen the bank", ref RM_RiversSettings.siltRichening,
				"On, a silt-trap slowly makes the bank soil beside it richer. Off: it only holds the silt.");
			if (RM_RiversSettings.siltRichening)
			{
				l.Label("One square richened every " + RM_RiversSettings.siltIntervalDays.ToString("F2") + " days");
				RM_RiversSettings.siltIntervalDays = l.Slider(RM_RiversSettings.siltIntervalDays, 0.1f, 5f);
			}
			l.CheckboxLabeled("Rope ferries", ref RM_RiversSettings.ferryEnabled,
				"Two ferry posts facing each other across a river string a rope: nothing standing on the rope "
			  + "line is carried. Drafted colonists cross along it.");
			if (RM_RiversSettings.ferryEnabled)
			{
				l.Label("Longest rope: " + RM_RiversSettings.ferryMaxSpan + " squares");
				RM_RiversSettings.ferryMaxSpan = Mathf.RoundToInt(l.Slider(RM_RiversSettings.ferryMaxSpan, 5f, 80f));
				l.CheckboxLabeled("  Colonists use the rope to cross", ref RM_RiversSettings.ferryRopeGuidesColonists,
					"On: everyday jobs treat a strung rope as a crossing, the way they treat a ford or a bridge, "
				  + "instead of walking the long way round. Off: only drafted colonists cross on the rope.");
			}

		}
	}
}
