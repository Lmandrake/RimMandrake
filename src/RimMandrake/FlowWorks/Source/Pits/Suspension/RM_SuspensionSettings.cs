using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>Mod Settings section "Suspension bridges" (SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS; the rows of
	/// design/RimMandrake/flowworks_bridges_design_2026-10-17.md §9 this item makes real). Own static class, scribed into the
	/// FlowWorks settings file from RimMandrakeFlowWorksSettings.ExposeData and drawn by its window, the same shape as
	/// RM_SprinklerSettings. Defaults = shipped behaviour. All off: no build buttons, existing bridges stay as plain walkable
	/// decks that never break from weight or a lost anchor; nothing is deleted from a save. Each later suspension item adds its
	/// own §9 rows here (grates: SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP; walk under, sunken: SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD; water, sea, floods: SUSPENSION_WATERS_BUILD_MAY_BACKTRACK).</summary>
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
		// SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD
		public static bool suspensionWalkUnder = true;
		public static bool sunkenBridges = true;
		// SUSPENSION_WATERS_BUILD_MAY_BACKTRACK
		public static bool suspensionOverWater = true;
		public static bool suspensionOverSea = true;
		public static bool floodsDamageLightBridges = true;

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
			Scribe_Values.Look(ref suspensionWalkUnder, "suspensionWalkUnder", true);
			Scribe_Values.Look(ref sunkenBridges, "sunkenBridges", true);
			Scribe_Values.Look(ref suspensionOverWater, "suspensionOverWater", true);
			Scribe_Values.Look(ref suspensionOverSea, "suspensionOverSea", true);
			Scribe_Values.Look(ref floodsDamageLightBridges, "floodsDamageLightBridges", true);
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
			bool walkUnder = suspensionWalkUnder;
			list.CheckboxLabeled("People can walk under suspension bridges", ref suspensionWalkUnder,
				"On: people down in a hole walk under a suspension bridge when its floor is at least 2 m below the deck (shallower, "
				+ "it is a wall from below). Only these bridges: no roof or dug passage lets anyone under it. Raiders in a deep moat "
				+ "walk under too. Off: every deck is a wall from below.");
			if (walkUnder != suspensionWalkUnder)
			{
				RM_PocketGrid.SettingsChanged();
			}
			list.CheckboxLabeled("Sunken bridges (below ground)", ref sunkenBridges,
				"On: a suspension bridge can be dragged between two dry ledges at the same depth inside a deeper hole (for example "
				+ "across the core of a stepped pit), reached from a ledge, ramp or ladder at its height. Off: bridges only at the "
				+ "surface; sunken bridges already built stay.");
			list.CheckboxLabeled("Suspension bridges over rivers and lakes", ref suspensionOverWater,
				"On: a suspension bridge may cross natural water (a river, a lake), anchored on the banks, with towers in the water "
				+ "for a long crossing. The river's current never carries anyone on the deck. Off: only dug ground; bridges already "
				+ "built stay.");
			list.CheckboxLabeled("Suspension bridges over the sea", ref suspensionOverSea,
				"On: the same over the ocean (towers stand in the sea). Off: no new crossings over the sea; bridges already built "
				+ "stay.");
			list.CheckboxLabeled("Floods damage light bridges", ref floodsDamageLightBridges,
				"On: a rope or timber suspension bridge awash in a flood loses about 5% of its hit points an hour (and gives way if a "
				+ "square breaks); steel and heavy ones shrug it off. Off: floods do them no harm.");
		}
	}
}
