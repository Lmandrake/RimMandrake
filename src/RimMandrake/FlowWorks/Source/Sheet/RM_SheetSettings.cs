using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Sheet
{
	/// <summary>CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED, Stage 1: the master switch for canal overflow (design
	/// canal_overflow_flooding_2026-10-21.md §4 Stage 3 / D7). Own static class, scribed into the FlowWorks settings file from
	/// RimMandrakeFlowWorksSettings.ExposeData, the same shape as RM_SprinklerSettings.
	///
	/// ⚠ Default OFF until the Stage 4 live acceptance validates it. D7 (owner card) says the shipped default is ON ONCE
	/// VALIDATED; flipping this default is the Stage 4 sign-off, not a tuning choice.
	/// OFF: no new spill is accepted, so every inflow behaves exactly as before (refused at the brim, fill-in's homeless
	/// remainder disclosed as destroyed). Water already standing keeps draining by its normal exits; nothing vanishes.</summary>
	public static class RM_SheetSettings
	{
		public static bool sheetOverflowEnabled = false;

		// stage 3: per-inflow switches (D1, D2). Off: that inflow behaves as before (refused at the brim / disclosed).
		public static bool spillFromPumps = true;
		public static bool spillFromRain = true;
		public static bool spillFromFloods = true;
		public static bool spillFromFillIn = true;
		public static bool spillFromGravity = true;

		// shipped value of every public static setting above (RM_SettingsReset); MUST stay below the last setting field
		private static readonly System.Collections.Generic.Dictionary<string, object> shippedDefaults = RM_SettingsReset.Snapshot(typeof(RM_SheetSettings));

		/// <summary>Does a spill from <paramref name="from"/> enter the sheet now (master switch and that inflow's switch)?</summary>
		public static bool SpillsFrom(RM_SheetMath.Source from)
		{
			if (!sheetOverflowEnabled)
			{
				return false;
			}
			switch (from)
			{
				case RM_SheetMath.Source.Pump: return spillFromPumps;
				case RM_SheetMath.Source.Rain: return spillFromRain;
				case RM_SheetMath.Source.Flood: return spillFromFloods;
				case RM_SheetMath.Source.FillIn: return spillFromFillIn;
				case RM_SheetMath.Source.Gravity: return spillFromGravity;
				default: return false;
			}
		}

		public static void ResetAll()
		{
			RM_SettingsReset.ResetAll(typeof(RM_SheetSettings), shippedDefaults);
		}

		public static void ExposeData()
		{
			Scribe_Values.Look(ref sheetOverflowEnabled, "sheetOverflowEnabled", false);
			Scribe_Values.Look(ref spillFromPumps, "sheetSpillFromPumps", true);
			Scribe_Values.Look(ref spillFromRain, "sheetSpillFromRain", true);
			Scribe_Values.Look(ref spillFromFloods, "sheetSpillFromFloods", true);
			Scribe_Values.Look(ref spillFromFillIn, "sheetSpillFromFillIn", true);
			Scribe_Values.Look(ref spillFromGravity, "sheetSpillFromGravity", true);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Canal overflow (being built: off until tested)");
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, ResetAll);
			list.CheckboxLabeled("Overfilled channels spill water onto the ground", ref sheetOverflowEnabled,
				"On: water that a full channel cannot take (a pump pouring into a brimming canal, rain on a full canal, the water a "
				+ "fill-in squeezes out with nowhere to go) runs over the edge as a thin sheet on the ground around it. The sheet "
				+ "spreads until it is about 1 cm deep, lies level, runs back into any channel or pond with room, soaks in and dries. "
				+ "Every litre is counted. Water only, for now. Off: a full channel refuses the water as before. Water already "
				+ "spilled keeps draining away; turning this off never deletes it.");
			if (Current.ProgramState == ProgramState.Playing && Find.CurrentMap != null)
			{
				RM_MapComponent_Sheet sheet = Find.CurrentMap.GetComponent<RM_MapComponent_Sheet>();
				if (sheet != null)
				{
					list.Label("This map: " + sheet.LedgerLine());
					if (sheet.WetCells > 0 && list.ButtonText("Dry all spilled water on this map now"))
					{
						sheet.DryAll();
					}
				}
			}
		}
	}
}
