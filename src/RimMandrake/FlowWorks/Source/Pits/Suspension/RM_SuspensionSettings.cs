using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>Mod Settings section "Suspension bridges" (SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS; the rows of
	/// design/RimMandrake/flowworks_bridges_design_2026-10-17.md §9 this item makes real). Own static class, scribed into the
	/// FlowWorks settings file from RimMandrakeFlowWorksSettings.ExposeData and drawn by its window, the same shape as
	/// RM_SprinklerSettings. Defaults = shipped behaviour. All off: no build buttons, existing bridges stay as plain walkable
	/// decks that never break from weight or a lost anchor; nothing is deleted from a save. Each later suspension item adds its
	/// own §9 rows here (grates: SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP).</summary>
	public static class RM_SuspensionSettings
	{
		public static bool suspensionBridgesBuildable = true;
		public static bool suspensionWeightCollapse = true;
		public static float suspensionLoadMultiplier = 1f;
		public static float suspensionLengthMultiplier = 1f;
		public static bool suspensionAnchorLossFalls = true;
		public static bool vanillaBridgeRefusedOverDug = true;
		public static bool suspensionOwnPeopleFall = true;
		// SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP
		public static bool grateFirePasses = true;
		public static bool grateDrainsSpills = true;

		public static void ExposeData()
		{
			Scribe_Values.Look(ref suspensionBridgesBuildable, "suspensionBridgesBuildable", true);
			Scribe_Values.Look(ref suspensionWeightCollapse, "suspensionWeightCollapse", true);
			Scribe_Values.Look(ref suspensionLoadMultiplier, "suspensionLoadMultiplier", 1f);
			Scribe_Values.Look(ref suspensionLengthMultiplier, "suspensionLengthMultiplier", 1f);
			Scribe_Values.Look(ref suspensionAnchorLossFalls, "suspensionAnchorLossFalls", true);
			Scribe_Values.Look(ref vanillaBridgeRefusedOverDug, "vanillaBridgeRefusedOverDug", true);
			Scribe_Values.Look(ref suspensionOwnPeopleFall, "suspensionOwnPeopleFall", true);
			Scribe_Values.Look(ref grateFirePasses, "grateFirePasses", true);
			Scribe_Values.Look(ref grateDrainsSpills, "grateDrainsSpills", true);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Suspension bridges");
			list.CheckboxLabeled("Suspension bridges can be built", ref suspensionBridgesBuildable,
				"Drag a suspension bridge across a dug hole like a wall, 1 to 3 squares wide, from solid ground to solid ground; "
				+ "posts (anchors) go at both ends and the deck is built from the anchors inward. Off: no build buttons; bridges "
				+ "already built stay.");
			list.CheckboxLabeled("Suspension bridges give way under weight", ref suspensionWeightCollapse,
				"On: when the people, items and buildings on one span (the deck between two supports) weigh more than its rating, "
				+ "the whole span gives way and everyone on it falls into the hole. It sags and creaks from 90%. Off: they break only "
				+ "from damage and lost anchors.");
			list.Label("Load multiplier: x" + suspensionLoadMultiplier.ToString("0.00") + "  (rope 150, timber 600, steel 2,000, heavy 8,000 kg per lane)");
			suspensionLoadMultiplier = Mathf.Round(list.Slider(suspensionLoadMultiplier, 0.25f, 4f) * 20f) / 20f;
			list.Label("Length multiplier: x" + suspensionLengthMultiplier.ToString("0.00") + "  (rope 8, timber 6, steel 10, heavy 14 squares between supports)");
			suspensionLengthMultiplier = Mathf.Round(list.Slider(suspensionLengthMultiplier, 0.5f, 3f) * 20f) / 20f;
			list.CheckboxLabeled("Bridges fall when an anchor or tower goes", ref suspensionAnchorLossFalls,
				"On: losing an anchor or a tower (destroyed or deconstructed) swings the span it held down, square by square from the "
				+ "lost end, dropping whoever is on it. Off: a bridge with no anchor stays up.");
			list.CheckboxLabeled("Game bridges refused over dug ground", ref vanillaBridgeRefusedOverDug,
				"On: the game's own bridge and heavy bridge cannot be placed on a dug square (\"Use a suspension bridge over dug "
				+ "ground\"). Off: allowed, with the risk that a canal that drains leaves the bridge on a dry floor.");
			list.CheckboxLabeled("Your own people fall when a bridge gives way", ref suspensionOwnPeopleFall,
				"On: everyone on a span that gives way falls, your own colonists included. Off: your own people are set down on the "
				+ "nearest anchor instead (others still fall).");
			list.CheckboxLabeled("Grates pass fire to people above", ref grateFirePasses,
				"On: burning liquid under a grated suspension bridge sets the people on it alight far more often than a solid deck "
				+ "(three quarters of the chance down in the fire itself), and the hot grating burns them over time. Off: grated decks "
				+ "shield like solid ones.");
			list.CheckboxLabeled("Grates drain spills into the hole below", ref grateDrainsSpills,
				"On: liquid spilled or poured on a grated suspension bridge over dug ground drains into the hole below it (nothing is "
				+ "lost; items stay on the deck). Off: spills stay on the deck as puddles.");
		}
	}
}
