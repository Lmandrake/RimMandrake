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
		public static bool weirCatchesFish = true;
		public static float weirCatchIntervalHours = 6f;      // PROVISIONAL
		public static int weirHeldCatchCap = 30;              // PROVISIONAL
		// Owner card 2: plus drift, BIOME-RELEVANT per biome (RM_RiverDriftDef), never generic wood.
		public static bool weirCatchesDrift = true;
		public static float weirDriftChance = 0.25f;          // PROVISIONAL, per catch interval
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

		public static bool CurrentActive => riverWorksEnabled && surfaceCurrentEnabled;

		public static bool WorksActive => riverWorksEnabled && bankWorksEnabled;

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
			Scribe_Values.Look(ref weirCatchesFish, "weirCatchesFish", true);
			Scribe_Values.Look(ref weirCatchIntervalHours, "weirCatchIntervalHours", 6f);
			Scribe_Values.Look(ref weirHeldCatchCap, "weirHeldCatchCap", 30);
			Scribe_Values.Look(ref weirCatchesDrift, "weirCatchesDrift", true);
			Scribe_Values.Look(ref weirDriftChance, "weirDriftChance", 0.25f);
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
			l.CheckboxLabeled("Surface rivers have a current", ref RM_RiversSettings.surfaceCurrentEnabled,
				"Moving river water shoves pawns and loose items downstream. Chest-deep water is the fast "
			  + "lane and cannot be waded out of; shallow water is the edge lane and can still be crossed. "
			  + "Off: rivers are vanilla. Safe to change mid-game (the flow is read from the map itself).");
			l.Label("Current strength: x" + RM_RiversSettings.currentStrength.ToString("F2"));
			RM_RiversSettings.currentStrength = l.Slider(RM_RiversSettings.currentStrength, 0.25f, 3f);
			l.Label("Fast lane: ticks per cell " + RM_RiversSettings.centreTicksPerCell);
			RM_RiversSettings.centreTicksPerCell = Mathf.RoundToInt(l.Slider(RM_RiversSettings.centreTicksPerCell, 10f, 200f));
			l.Label("Edge lane: ticks per cell " + RM_RiversSettings.marginTicksPerCell);
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
				l.CheckboxLabeled("  Spring (seasonal) floods count", ref RM_RiversSettings.countSeasonalFloods);
				l.CheckboxLabeled("  Torrential-rain floods count", ref RM_RiversSettings.countTorrentialRainFloods);
			}
			l.CheckboxLabeled("Carry animals", ref RM_RiversSettings.carryAnimals);
			l.CheckboxLabeled("Carry visitors and raiders", ref RM_RiversSettings.carryStrangers);
			l.CheckboxLabeled("Carry loose items and corpses", ref RM_RiversSettings.carryItems);
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
			  + "where they are told. Takes effect after a restart.");
			l.CheckboxLabeled("Being swept is dangerous", ref RM_RiversSettings.crossingHazardsEnabled,
				"In the fast lane a carried pawn can be bruised and can drop what it is carrying.");
			if (RM_RiversSettings.crossingHazardsEnabled)
			{
				l.Label("Bruise chance per cell: " + RM_RiversSettings.bruiseChancePerStep.ToStringPercent());
				RM_RiversSettings.bruiseChancePerStep = l.Slider(RM_RiversSettings.bruiseChancePerStep, 0f, 1f);
				l.Label("Drop-carried chance per cell: " + RM_RiversSettings.dropChancePerStep.ToStringPercent());
				RM_RiversSettings.dropChancePerStep = l.Slider(RM_RiversSettings.dropChancePerStep, 0f, 1f);
			}
			l.GapLine();
			l.Label("WORKS");
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
				l.Label("Stake snap: ticks per cell " + RM_RiversSettings.stakeSnapTicksPerCell);
				RM_RiversSettings.stakeSnapTicksPerCell = Mathf.RoundToInt(l.Slider(RM_RiversSettings.stakeSnapTicksPerCell, 10f, 1000f));
				l.CheckboxLabeled("  Breach washes the held catch downstream", ref RM_RiversSettings.breachWashesCatch);
				if (RM_RiversSettings.breachWashesCatch)
				{
					l.Label("  Washed this many cells: " + RM_RiversSettings.breachWashCells);
					RM_RiversSettings.breachWashCells = Mathf.RoundToInt(l.Slider(RM_RiversSettings.breachWashCells, 1f, 20f));
				}
			}
			l.CheckboxLabeled("A continuous stake-line holds floods (levee)", ref RM_RiversSettings.stakeLineLevee,
				"Floodwater cannot pass a stake. Any gap lets it in. Off: floods flow through stake-lines.");
			l.Label("Weir calms this many cells upstream: " + RM_RiversSettings.weirPoolLength + " (0 = its own cell only)");
			RM_RiversSettings.weirPoolLength = Mathf.RoundToInt(l.Slider(RM_RiversSettings.weirPoolLength, 0f, 20f));
			l.CheckboxLabeled("Weirs catch fish", ref RM_RiversSettings.weirCatchesFish,
				"From the river's own stock, the same stock your fishing zones draw on.");
			l.CheckboxLabeled("Weirs catch drift from upriver", ref RM_RiversSettings.weirCatchesDrift,
				"Things that belong to this biome's rivers wash into the weir now and then.");
			l.Label("Catch every " + RM_RiversSettings.weirCatchIntervalHours.ToString("F1") + " hours");
			RM_RiversSettings.weirCatchIntervalHours = l.Slider(RM_RiversSettings.weirCatchIntervalHours, 1f, 48f);
			l.Label("Drift chance per catch: " + RM_RiversSettings.weirDriftChance.ToStringPercent());
			RM_RiversSettings.weirDriftChance = l.Slider(RM_RiversSettings.weirDriftChance, 0f, 1f);
			l.Label("Weir holds at most " + RM_RiversSettings.weirHeldCatchCap + " items before it stops catching");
			RM_RiversSettings.weirHeldCatchCap = Mathf.RoundToInt(l.Slider(RM_RiversSettings.weirHeldCatchCap, 5f, 200f));
			l.CheckboxLabeled("Silt-traps richen the bank", ref RM_RiversSettings.siltRichening);
			if (RM_RiversSettings.siltRichening)
			{
				l.Label("One cell richened every " + RM_RiversSettings.siltIntervalDays.ToString("F2") + " days");
				RM_RiversSettings.siltIntervalDays = l.Slider(RM_RiversSettings.siltIntervalDays, 0.1f, 5f);
			}
			l.CheckboxLabeled("Rope ferries", ref RM_RiversSettings.ferryEnabled,
				"Two ferry posts facing each other across a river string a rope: nothing standing on the rope "
			  + "line is carried. Drafted colonists cross along it.");
			if (RM_RiversSettings.ferryEnabled)
			{
				l.Label("Longest rope: " + RM_RiversSettings.ferryMaxSpan + " cells");
				RM_RiversSettings.ferryMaxSpan = Mathf.RoundToInt(l.Slider(RM_RiversSettings.ferryMaxSpan, 5f, 80f));
				l.CheckboxLabeled("  Colonists use the rope to cross", ref RM_RiversSettings.ferryRopeGuidesColonists,
					"On: everyday jobs treat a strung rope as a crossing, the way they treat a ford or a bridge, "
				  + "instead of walking the long way round. Off: only drafted colonists cross on the rope.");
			}

		}
	}
}
