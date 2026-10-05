using UnityEngine;
using Verse;

namespace RimMandrake.RiverWorks
{
	/// <summary>
	/// River Works Mod Settings (design §5). Defaults = shipped behaviour; all-off degrades to
	/// still vanilla rivers, never an error. No toggle changes map generation: the current is
	/// derived from vanilla's own saved riverFlowMap, so flipping it mid-game is safe.
	/// Numbers marked PROVISIONAL are guesses awaiting a live look, not rulings.
	/// </summary>
	public class RM_RiverWorksSettings : ModSettings
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
		// Owner card 1: colonists path around strong water to bridges/fords (drafted still go).
		public static bool pathfinderAvoidsCurrents = true;
		// Owner card 2: being swept bruises and can make a pawn drop what it carries.
		public static bool crossingHazardsEnabled = true;
		public static float bruiseChancePerStep = 0.15f;   // PROVISIONAL
		public static float dropChancePerStep = 0.25f;     // PROVISIONAL
		public static bool fordsEnabled = true;

		public static bool CurrentActive => riverWorksEnabled && surfaceCurrentEnabled;

		public override void ExposeData()
		{
			base.ExposeData();
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
			Scribe_Values.Look(ref pathfinderAvoidsCurrents, "pathfinderAvoidsCurrents", true);
			Scribe_Values.Look(ref crossingHazardsEnabled, "crossingHazardsEnabled", true);
			Scribe_Values.Look(ref bruiseChancePerStep, "bruiseChancePerStep", 0.15f);
			Scribe_Values.Look(ref dropChancePerStep, "dropChancePerStep", 0.25f);
			Scribe_Values.Look(ref fordsEnabled, "fordsEnabled", true);
		}
	}

	public class RM_RiverWorksMod : Mod
	{
		private static Vector2 scroll;

		public RM_RiverWorksMod(ModContentPack content) : base(content)
		{
			GetSettings<RM_RiverWorksSettings>();
		}

		public override string SettingsCategory()
		{
			return "RimMandrake: River Works";
		}

		public override void DoSettingsWindowContents(Rect inRect)
		{
			Rect view = new Rect(0f, 0f, inRect.width - 20f, 1100f);
			Widgets.BeginScrollView(inRect, ref scroll, view);
			Listing_Standard l = new Listing_Standard();
			l.Begin(view);

			l.CheckboxLabeled("River Works enabled", ref RM_RiverWorksSettings.riverWorksEnabled,
				"Master switch. Off: rivers are vanilla still water and nothing here does anything.");
			l.GapLine();
			l.Label("THE CURRENT");
			l.CheckboxLabeled("Surface rivers have a current", ref RM_RiverWorksSettings.surfaceCurrentEnabled,
				"Moving river water shoves pawns and loose items downstream. Chest-deep water is the fast "
			  + "lane and cannot be waded out of; shallow water is the edge lane and can still be crossed. "
			  + "Off: rivers are vanilla. Safe to change mid-game (the flow is read from the map itself).");
			l.Label("Current strength: x" + RM_RiverWorksSettings.currentStrength.ToString("F2"));
			RM_RiverWorksSettings.currentStrength = l.Slider(RM_RiverWorksSettings.currentStrength, 0.25f, 3f);
			l.Label("Fast lane: ticks per cell " + RM_RiverWorksSettings.centreTicksPerCell);
			RM_RiverWorksSettings.centreTicksPerCell = Mathf.RoundToInt(l.Slider(RM_RiverWorksSettings.centreTicksPerCell, 10f, 200f));
			l.Label("Edge lane: ticks per cell " + RM_RiverWorksSettings.marginTicksPerCell);
			RM_RiverWorksSettings.marginTicksPerCell = Mathf.RoundToInt(l.Slider(RM_RiverWorksSettings.marginTicksPerCell, 20f, 400f));
			l.Label("Items drift slower by x" + RM_RiverWorksSettings.itemDriftFactor.ToString("F1"));
			RM_RiverWorksSettings.itemDriftFactor = l.Slider(RM_RiverWorksSettings.itemDriftFactor, 1f, 5f);
			l.CheckboxLabeled("Bigger rivers shove harder", ref RM_RiverWorksSettings.scaleWithRiverSize,
				"Creeks barely push; huge rivers are lethal. Off: every river shoves the same.");
			l.CheckboxLabeled("Floods make the river fiercer", ref RM_RiverWorksSettings.floodSurgeEnabled,
				"While a flood is on the map the edge lane behaves as the fast lane and the fast lane "
			  + "moves twice as fast.");
			if (RM_RiverWorksSettings.floodSurgeEnabled)
			{
				l.CheckboxLabeled("  Spring (seasonal) floods count", ref RM_RiverWorksSettings.countSeasonalFloods);
				l.CheckboxLabeled("  Torrential-rain floods count", ref RM_RiverWorksSettings.countTorrentialRainFloods);
			}
			l.CheckboxLabeled("Carry animals", ref RM_RiverWorksSettings.carryAnimals);
			l.CheckboxLabeled("Carry visitors and raiders", ref RM_RiverWorksSettings.carryStrangers);
			l.CheckboxLabeled("Carry loose items and corpses", ref RM_RiverWorksSettings.carryItems);
			l.CheckboxLabeled("Washed off the map at the edge", ref RM_RiverWorksSettings.washOffMapEdge,
				"A pawn carried to the edge of the map is washed away. Your own people walk home a few days "
			  + "later; a letter says so when it happens. Off: the current stops at the map edge.");
			if (RM_RiverWorksSettings.washOffMapEdge)
			{
				l.Label("Days before a washed-away colonist walks home: "
				  + RM_RiverWorksSettings.washedAwayMinDays.ToString("F1") + " to " + RM_RiverWorksSettings.washedAwayMaxDays.ToString("F1"));
				RM_RiverWorksSettings.washedAwayMinDays = l.Slider(RM_RiverWorksSettings.washedAwayMinDays, 0.25f, 10f);
				RM_RiverWorksSettings.washedAwayMaxDays = Mathf.Max(RM_RiverWorksSettings.washedAwayMinDays,
					l.Slider(RM_RiverWorksSettings.washedAwayMaxDays, 0.25f, 15f));
			}
			l.CheckboxLabeled("Colonists avoid strong water", ref RM_RiverWorksSettings.pathfinderAvoidsCurrents,
				"Undrafted colonists route around moving water to bridges and fords. Drafted orders still go "
			  + "where they are told. Takes effect after a restart.");
			l.CheckboxLabeled("Being swept is dangerous", ref RM_RiverWorksSettings.crossingHazardsEnabled,
				"In the fast lane a carried pawn can be bruised and can drop what it is carrying.");
			if (RM_RiverWorksSettings.crossingHazardsEnabled)
			{
				l.Label("Bruise chance per cell: " + RM_RiverWorksSettings.bruiseChancePerStep.ToStringPercent());
				RM_RiverWorksSettings.bruiseChancePerStep = l.Slider(RM_RiverWorksSettings.bruiseChancePerStep, 0f, 1f);
				l.Label("Drop-carried chance per cell: " + RM_RiverWorksSettings.dropChancePerStep.ToStringPercent());
				RM_RiverWorksSettings.dropChancePerStep = l.Slider(RM_RiverWorksSettings.dropChancePerStep, 0f, 1f);
			}
			l.GapLine();
			l.Label("WORKS");
			l.CheckboxLabeled("Fords stop the current", ref RM_RiverWorksSettings.fordsEnabled,
				"Nothing is carried on or beside ford stones. Off: fords are just stone footing.");

			l.End();
			Widgets.EndScrollView();
		}
	}
}
