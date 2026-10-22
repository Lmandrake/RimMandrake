using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS Mod Settings (own static class, scribed into the FlowWorks settings like
	/// RM_SuspensionSettings). Defaults are the rulings: on, raiders climb too (owner by card 2026-10-18: "colonists AND
	/// raiders"); a wall square costs 20 of the pawn's steps and gear-wearers route over when that is still shorter (by card:
	/// "They can route when shorter, but climbing should be SLOOOWW. Like x20 slow"); raiders of the named factions, a few
	/// light tribal and pirate raiders, and breachers and sappers carry the gear (by card: "Then breachers and sappers from
	/// anyone"). All off: walls block gear-wearers as they block everyone, and the pit-wall climbing is unaffected.
	/// </summary>
	public static class RM_WallClimbSettings
	{
		public static bool wallClimbEnabled = true;
		public static float wallClimbSlowFactor = RM_WallClimbMath.DefaultSlowFactor;
		public static bool raidersMayClimbWalls = true;
		public static bool wallClimbAutoRoute = true;
		public static bool raidersCarryClimbingGear = true;
		public static float raiderGearChanceScale = 1f;
		public static float breacherSapperGearChance = 1f;

		// FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING: shipped value of every public static bool/float/int setting above. MUST stay
		// below the LAST public setting field (C# runs static initialisers in textual order).
		private static readonly System.Collections.Generic.Dictionary<string, object> shippedDefaults = RM_SettingsReset.Snapshot(typeof(RM_WallClimbSettings));

		/// <summary>The Reset button: every setting on this screen back to its shipped value.</summary>
		public static void ResetAll()
		{
			RM_SettingsReset.ResetAll(typeof(RM_WallClimbSettings), shippedDefaults);
		}

		public static void ExposeData()
		{
			Scribe_Values.Look(ref wallClimbEnabled, "wallClimbEnabled", true);
			Scribe_Values.Look(ref wallClimbSlowFactor, "wallClimbSlowFactor", RM_WallClimbMath.DefaultSlowFactor);
			Scribe_Values.Look(ref raidersMayClimbWalls, "raidersMayClimbWalls", true);
			Scribe_Values.Look(ref wallClimbAutoRoute, "wallClimbAutoRoute", true);
			Scribe_Values.Look(ref raidersCarryClimbingGear, "raidersCarryClimbingGear", true);
			Scribe_Values.Look(ref raiderGearChanceScale, "raiderGearChanceScale", 1f);
			Scribe_Values.Look(ref breacherSapperGearChance, "breacherSapperGearChance", 1f);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Climbing over walls");
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, ResetAll);
			list.CheckboxLabeled("Climbing gear scales built walls", ref wallClimbEnabled,
				"On, a pawn wearing climbing gear climbs over a built wall or impassable fence (up to "
			  + RM_WallClimbMath.MaxWallSquares + " squares thick) when the wall and the squares on both sides are unroofed, "
			  + "slowly, either way. Colonists: right-click the wall. Raiders climb instead of breaking through. Needs "
			  + "\"Climbing gear\" on. Off: walls stop everyone.");
			int seconds = Mathf.RoundToInt(RM_WallClimbMath.ClimbTicks(1, wallClimbSlowFactor, RM_WallClimbMath.PersonTicksPerCell) / 60f);
			list.Label("Wall climbing slowness: x" + wallClimbSlowFactor.ToString("0") + " a walking step  (about " + seconds
			  + " s a wall square for a person)", tooltip:
				"How many of the pawn's own walking steps one wall square takes to climb. Slower or faster walkers climb slower "
			  + "or faster. The route planner charges the same, so a higher number means fewer automatic climbs.");
			wallClimbSlowFactor = Mathf.Round(list.Slider(wallClimbSlowFactor, 5f, 60f));
			list.CheckboxLabeled("Gear-wearers route over walls when shorter", ref wallClimbAutoRoute,
				"On, a pawn wearing climbing gear (yours or a raider) going somewhere it can already walk to climbs over one of "
			  + "your climbable walls on the way when that is quicker than walking round, even at the slow climb. Off: a climb "
			  + "only when ordered (right-click) or when a raider has no other way in.");
			list.CheckboxLabeled("Raiders may climb walls", ref raidersMayClimbWalls,
				"On, raiders and other pawns not yours who wear climbing gear climb over unroofed walls into the colony "
			  + "instead of breaking through them. Off: only your own people climb.");
			list.CheckboxLabeled("Raiders carry climbing gear", ref raidersCarryClimbingGear,
				"On, some raiders arrive wearing climbing gear: the Wildsteam, Junker, Blackstar, Jawa and deep desert tribe "
			  + "factions often, light tribal and pirate raiders now and then, and breachers and sappers of any faction. Off: "
			  + "no pawn not yours is generated with it (gear already worn stays).");
			list.Label("Raider climbing gear chance: x" + raiderGearChanceScale.ToString("0.00"), tooltip:
				"Scales every faction's and pawn kind's chance of carrying climbing gear. 0: none.");
			raiderGearChanceScale = Mathf.Round(list.Slider(raiderGearChanceScale, 0f, 3f) * 20f) / 20f;
			list.Label("Breachers and sappers with climbing gear: " + (breacherSapperGearChance * 100f).ToString("0") + "%",
				tooltip: "The chance a breacher or sapper of any faction carries climbing gear (before the scale above).");
			breacherSapperGearChance = Mathf.Round(list.Slider(breacherSapperGearChance, 0f, 1f) * 20f) / 20f;
		}
	}
}
