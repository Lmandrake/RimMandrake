using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Machinery.Logistics
{
	/// <summary>Mod Settings section: sluice gates (a gate that opens and closes a canal cell's flow) (FOUNDRY builder Y, 2026-10-05). Own static class, scribed into the
	/// FlowWorks settings file from RimMandrakeFlowWorksSettings.ExposeData and drawn by its window, the same
	/// shape as RM_RiversSettings / RM_MachinerySettings. Defaults = shipped behaviour.
	/// Off: every gate is permanently open — it never blocks liquid, never errors; the buildings stay as
	/// harmless catwalks. Delays are PROVISIONAL first guesses awaiting a live look.</summary>
	public static class RM_SluiceGateSettings
	{
		public static bool sluiceGatesEnabled = true;
		/// <summary>Ticks between a pawn cranking the gate open and liquid passing. PROVISIONAL.</summary>
		public static int sluiceGateOpenDelayTicks = 120;
		/// <summary>Ticks between a pawn cranking the gate shut and the cell blocking. PROVISIONAL.</summary>
		public static int sluiceGateCloseDelayTicks = 240;

		public static void ExposeData()
		{
			Scribe_Values.Look(ref sluiceGatesEnabled, "sluiceGatesEnabled", true);
			Scribe_Values.Look(ref sluiceGateOpenDelayTicks, "sluiceGateOpenDelayTicks", 120);
			Scribe_Values.Look(ref sluiceGateCloseDelayTicks, "sluiceGateCloseDelayTicks", 240);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Sluice gates");
			list.CheckboxLabeled("Sluice gates hold back liquid when shut", ref sluiceGatesEnabled,
				"A sluice gate sits on a canal cell. Shut, no liquid crosses that cell in either direction; "
				+ "open, the channel flows as if the gate were not there. A colonist cranks it open or shut "
				+ "(the gate's toggle). Off: every gate stays open and holds nothing back.");
			list.Label("Time to open after cranking: " + (sluiceGateOpenDelayTicks / 60f).ToString("F1") + " s  (first-guess number)");
			sluiceGateOpenDelayTicks = Mathf.RoundToInt(list.Slider(sluiceGateOpenDelayTicks, 0f, 2500f));
			list.Label("Time to shut after cranking: " + (sluiceGateCloseDelayTicks / 60f).ToString("F1") + " s  (first-guess number)");
			sluiceGateCloseDelayTicks = Mathf.RoundToInt(list.Slider(sluiceGateCloseDelayTicks, 0f, 2500f));
		}
	}
}
