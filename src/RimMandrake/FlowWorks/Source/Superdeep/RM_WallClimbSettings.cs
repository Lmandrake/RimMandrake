using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS Mod Settings (own static class, scribed into the FlowWorks settings like
	/// RM_SuspensionSettings). Defaults are the ruling: on, speed 1, raiders climb too (owner by card 2026-10-18: "colonists
	/// AND raiders"). All off: walls block gear-wearers as they block everyone, and the pit-wall climbing is unaffected.
	/// </summary>
	public static class RM_WallClimbSettings
	{
		public static bool wallClimbEnabled = true;
		public static float wallClimbSpeed = 1f;
		public static bool raidersMayClimbWalls = true;

		public static void ExposeData()
		{
			Scribe_Values.Look(ref wallClimbEnabled, "wallClimbEnabled", true);
			Scribe_Values.Look(ref wallClimbSpeed, "wallClimbSpeed", 1f);
			Scribe_Values.Look(ref raidersMayClimbWalls, "raidersMayClimbWalls", true);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Climbing over walls");
			list.CheckboxLabeled("Climbing gear scales built walls", ref wallClimbEnabled,
				"On, a pawn wearing climbing gear climbs over a built wall or impassable fence (up to "
			  + RM_WallClimbMath.MaxWallSquares + " squares thick) when the wall and the squares on both sides are unroofed, "
			  + "slowly, either way. Colonists: right-click the wall. Raiders climb instead of breaking through. Needs "
			  + "\"Climbing gear\" on. Off: walls stop everyone.");
			int seconds = Mathf.RoundToInt(RM_WallClimbMath.ClimbTicks(1, wallClimbSpeed, RM_WallClimbMath.NormalMoveSpeed) / 60f);
			list.Label("Wall climbing speed: x" + wallClimbSpeed.ToString("0.00") + "  (about " + seconds
			  + " s a wall square for a person)", tooltip:
				"How fast a gear-wearer climbs over a wall. Faster or slower walkers climb faster or slower.");
			wallClimbSpeed = Mathf.Round(list.Slider(wallClimbSpeed, 0.25f, 4f) * 20f) / 20f;
			list.CheckboxLabeled("Raiders may climb walls", ref raidersMayClimbWalls,
				"On, raiders and other pawns not yours who wear climbing gear climb over unroofed walls into the colony "
			  + "instead of breaking through them. Off: only your own people climb.");
		}
	}
}
