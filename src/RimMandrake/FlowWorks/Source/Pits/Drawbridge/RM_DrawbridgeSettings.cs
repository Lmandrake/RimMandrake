using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS Mod Settings (design R11): "Drawbridges can be built", "Raise speed ×", the
	/// per-material longest leaf, "Raids bring planks" and the share of raids that do. Own static class, scribed into the
	/// FlowWorks settings like RM_SuspensionSettings. Defaults = shipped behaviour. All off: a drawbridge is a suspension
	/// bridge stuck lowered (a raised leaf is set down without a crash) and no raid carries planks; nothing is deleted.</summary>
	public static class RM_DrawbridgeSettings
	{
		public static bool drawbridgesEnabled = true;
		public static float raiseSpeed = 1f;
		public static int maxLeafTimber = 4;
		public static int maxLeafSteel = 8;
		public static bool raidsBringPlanks = true;
		/// <summary>PROVISIONAL: "some raids bring their own planks": the share of raids (on a map with a drawbridge) that do.</summary>
		public static float raidPlankChance = 0.35f;

		// FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING: shipped value of every public static bool/float/int setting above. MUST stay
		// below the LAST public setting field (C# runs static initialisers in textual order).
		private static readonly System.Collections.Generic.Dictionary<string, object> shippedDefaults = RM_SettingsReset.Snapshot(typeof(RM_DrawbridgeSettings));

		/// <summary>The Reset button: every setting on this screen back to its shipped value.</summary>
		public static void ResetAll()
		{
			RM_SettingsReset.ResetAll(typeof(RM_DrawbridgeSettings), shippedDefaults);
		}

		public static void ExposeData()
		{
			Scribe_Values.Look(ref drawbridgesEnabled, "rmDrawbridgesEnabled", true);
			Scribe_Values.Look(ref raiseSpeed, "rmDrawbridgeRaiseSpeed", 1f);
			Scribe_Values.Look(ref maxLeafTimber, "rmDrawbridgeMaxLeafTimber", 4);
			Scribe_Values.Look(ref maxLeafSteel, "rmDrawbridgeMaxLeafSteel", 8);
			Scribe_Values.Look(ref raidsBringPlanks, "rmDrawbridgeRaidPlanks", true);
			Scribe_Values.Look(ref raidPlankChance, "rmDrawbridgeRaidPlankChance", 0.35f);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Drawbridges");
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, ResetAll);
			list.CheckboxLabeled("Drawbridges can be built", ref drawbridgesEnabled,
				"On, a timber or steel suspension bridge can be built as a drawbridge: its leaf raises at a winch house and the moat "
			  + "under it is a whole pit again. Off: no drawbridge is offered, and any existing one is set down (not crashed) and "
			  + "stays a plain lowered bridge.");
			list.Label("  Raise speed: x" + raiseSpeed.ToString("0.00"), tooltip:
				"x1: a timber leaf about 4 s a square by hand, a steel leaf about 2 s by motor (PROVISIONAL).");
			raiseSpeed = Mathf.Round(list.Slider(raiseSpeed, 0.25f, 4f) * 20f) / 20f;
			list.Label("  Longest timber leaf: " + maxLeafTimber + " squares (a bridge up to " + (2 * maxLeafTimber) + " is two leaves)");
			maxLeafTimber = Mathf.RoundToInt(list.Slider(maxLeafTimber, 2f, 8f));
			list.Label("  Longest steel leaf: " + maxLeafSteel + " squares (a bridge up to " + (2 * maxLeafSteel) + " is two leaves)");
			maxLeafSteel = Mathf.RoundToInt(list.Slider(maxLeafSteel, 2f, 14f));
			list.CheckboxLabeled("  Raids bring planks", ref raidsBringPlanks,
				"Some raids against a colony with a drawbridge carry planks: a raider lays one across a moat gap of up to "
			  + RM_DrawbridgeMath.RaidPlankMaxSpan + " squares between banks of one height. A laid plank is a light bridge: it "
			  + "sags, burns and breaks like one.");
			int pct = Mathf.RoundToInt(raidPlankChance * 100f);
			list.Label("  Raids that bring planks: " + pct + "%");
			raidPlankChance = Mathf.Round(list.Slider(raidPlankChance, 0f, 1f) * 20f) / 20f;
		}
	}
}
