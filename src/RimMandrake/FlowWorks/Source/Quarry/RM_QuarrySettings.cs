using Verse;

namespace RimMandrake.FlowWorks.Quarry
{
	/// <summary>Mod Settings section: sluice box and panning (rivers carry minerals) (FOUNDRY builder Y, 2026-10-05). Own static class, scribed into the
	/// FlowWorks settings file from RimMandrakeFlowWorksSettings.ExposeData and drawn by its window, the same
	/// shape as RM_RiversSettings / RM_MachinerySettings. Defaults = shipped behaviour. All off = the sluice box
	/// washes nothing and no one is offered panning; nothing errors. No toggle changes map generation.
	/// Numbers are PROVISIONAL (design §2f) until the mineral registry's review sheet sets them.</summary>
	public static class RM_QuarrySettings
	{
		public static bool sluiceBoxEnabled = true;
		public static bool panningEnabled = true;
		/// <summary>Owner card 2026-10-03: a spring flood tops the river's stock back up.</summary>
		public static bool placerFloodRefill = true;
		/// <summary>The river's yearly stock as a % of the heavy minerals the land holds. PROVISIONAL.</summary>
		public static float placerStockPercent = 2f;
		public static float sluiceYieldMultiplier = 1f;
		public static float panningYieldMultiplier = 1f;

		/// <summary>Both features also need the Rivers master switch (they read its current field).</summary>
		public static bool SluiceActive => sluiceBoxEnabled && Rivers.RM_RiversSettings.riverWorksEnabled;
		public static bool PanningActive => panningEnabled && Rivers.RM_RiversSettings.riverWorksEnabled;

		public static void ExposeData()
		{
			Scribe_Values.Look(ref sluiceBoxEnabled, "sluiceBoxEnabled", true);
			Scribe_Values.Look(ref panningEnabled, "panningEnabled", true);
			Scribe_Values.Look(ref placerFloodRefill, "placerFloodRefill", true);
			Scribe_Values.Look(ref placerStockPercent, "placerStockPercent", 2f);
			Scribe_Values.Look(ref sluiceYieldMultiplier, "sluiceYieldMultiplier", 1f);
			Scribe_Values.Look(ref panningYieldMultiplier, "panningYieldMultiplier", 1f);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Rivers carry minerals (sluice box, panning)");
			list.CheckboxLabeled("Sluice boxes wash ore out of rivers", ref sluiceBoxEnabled,
				"A sluice box straddles the bank with one end in shallow moving river water. Once a day it washes a "
				+ "little of what the river carries onto its bank end. Calm water (a weir's slack pool) and still "
				+ "water wash nothing. Off: sluice boxes stand idle.");
			list.CheckboxLabeled("Colonists can pan for minerals", ref panningEnabled,
				"A panning spot on the bank beside shallow moving water is Mining work: a colonist squats there for "
				+ "a couple of hours and usually finds nothing, sometimes a few units. Off: nobody pans.");
			list.CheckboxLabeled("A flood refills the river's stock", ref placerFloodRefill,
				"Sluice boxes and panners share one stock per map that regrows over a year. On: a spring flood or "
				+ "torrential-rain flood tops it back to full.");
			list.Label("River stock: " + placerStockPercent.ToString("F1") + "% a year of the heavy minerals in this map's rock");
			placerStockPercent = list.Slider(placerStockPercent, 0f, 20f);
			list.Label("Sluice box yield: x" + sluiceYieldMultiplier.ToString("F2") + "  (1x = about 1.2 units a day)");
			sluiceYieldMultiplier = list.Slider(sluiceYieldMultiplier, 0f, 10f);
			list.Label("Panning yield: x" + panningYieldMultiplier.ToString("F2") + "");
			panningYieldMultiplier = list.Slider(panningYieldMultiplier, 0f, 10f);
		}
	}
}
