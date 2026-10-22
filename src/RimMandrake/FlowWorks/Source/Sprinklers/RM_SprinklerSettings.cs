using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Sprinklers
{
	/// <summary>Mod Settings section: sprinklers (SPRINKLER_HEADS_BUILD_PUMP_REQUIRED, design sprinklers_design_2026-10-16.md §5).
	/// Own static class, scribed into the FlowWorks settings file from RimMandrakeFlowWorksSettings.ExposeData and drawn by its
	/// window, the same shape as RM_MapControlSettings. Defaults = the ruled behaviour (OQ-S1..S7).
	/// All off: no native head runs, VFE's sprinkler is exactly as shipped, nothing is sprinkled.</summary>
	public static class RM_SprinklerSettings
	{
		public static bool sprinklersEnabled = true;
		/// <summary>OQ-S1 RULED 0.5.</summary>
		public static float sprinklerLitresPerCellHour = RM_SprinklerKernel.RuledLitresPerCellHour;
		/// <summary>§2 PROPOSED 2.9 (1.9 / 2.9 / 3.9).</summary>
		public static float sprinklerNativeRadius = RM_SprinklerKernel.NativeRadius;
		/// <summary>OQ-S5 RULED on: acid/boiling spray hurts pawns in it; fuels leave flammable filth.</summary>
		public static bool sprinklerNonWaterEffects = true;
		/// <summary>OQ-S3 RULED: on = VFE's waterless boost removed inside our biomes and its head is a pipe consumer; off = VFE
		/// exactly as shipped everywhere.</summary>
		public static bool vfeSprinklerAdapterEnabled = true;
		/// <summary>OQ-S4 RULED: the first VFE upgrade, the moisture (thirst) valve.</summary>
		public static bool vfeThirstValve = true;

		public static readonly float[] RadiusChoices = { 1.9f, 2.9f, 3.9f };

		// FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING: shipped value of every public static bool/float/int setting above. MUST stay
		// below the LAST public setting field (C# runs static initialisers in textual order).
		private static readonly System.Collections.Generic.Dictionary<string, object> shippedDefaults = RM_SettingsReset.Snapshot(typeof(RM_SprinklerSettings));

		/// <summary>The Reset button: every setting on this screen back to its shipped value.</summary>
		public static void ResetAll()
		{
			RM_SettingsReset.ResetAll(typeof(RM_SprinklerSettings), shippedDefaults);
		}

		public static void ExposeData()
		{
			Scribe_Values.Look(ref sprinklersEnabled, "sprinklersEnabled", true);
			Scribe_Values.Look(ref sprinklerLitresPerCellHour, "sprinklerLitresPerCellHour", RM_SprinklerKernel.RuledLitresPerCellHour);
			Scribe_Values.Look(ref sprinklerNativeRadius, "sprinklerNativeRadius", RM_SprinklerKernel.NativeRadius);
			Scribe_Values.Look(ref sprinklerNonWaterEffects, "sprinklerNonWaterEffects", true);
			Scribe_Values.Look(ref vfeSprinklerAdapterEnabled, "vfeSprinklerAdapterEnabled", true);
			Scribe_Values.Look(ref vfeThirstValve, "vfeThirstValve", true);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Sprinklers");
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, ResetAll);
			list.CheckboxLabeled("Sprinkler heads on pipes", ref sprinklersEnabled,
				"A sprinkler head stands on a universal pipe and sprays the liquid its network holds onto the ground around it, "
				+ "once an hour, wetting those squares until the next spray. It needs no power, but a working pump must be on its "
				+ "network (the pump is the pressure). Walls stop the spray. Off: built heads sit idle and draw nothing.");
			list.Label("Water per square per hour: " + sprinklerLitresPerCellHour.ToString("0.0#") + " L  (ruled 0.5)");
			sprinklerLitresPerCellHour = Mathf.Round(list.Slider(sprinklerLitresPerCellHour, 0.1f, 5f) * 20f) / 20f;
			list.Label("Head radius: " + sprinklerNativeRadius.ToString("0.0") + " (default 2.9: about 29 squares watered)");
			int ri = System.Array.IndexOf(RadiusChoices, sprinklerNativeRadius);
			if (ri < 0) ri = 1;
			ri = Mathf.RoundToInt(list.Slider(ri, 0f, RadiusChoices.Length - 1));
			sprinklerNativeRadius = RadiusChoices[Mathf.Clamp(ri, 0, RadiusChoices.Length - 1)];
			list.CheckboxLabeled("Sprayed acid or boiling liquid hurts; sprayed fuel leaves flammable puddles", ref sprinklerNonWaterEffects,
				"On: a pawn standing in a spray of a corrosive or scalding liquid takes that liquid's contact harm once per spray, "
				+ "and a flammable liquid lays its puddles on the sprayed ground. Off: any liquid is sprayed harmlessly.");
			if (RM_SprinklerVFE.VfeLoaded)
			{
				list.CheckboxLabeled("Vanilla Furniture Expanded - Farming sprinkler draws water from pipes", ref vfeSprinklerAdapterEnabled,
					"Needs Vanilla Furniture Expanded - Farming. On: its sprinkler must touch a universal pipe with a working pump on "
					+ "the network and pays for its water like ours; inside this project's own biomes its free daily growth boost "
					+ "is removed (elsewhere VFE runs exactly as shipped). Off: VFE's sprinkler is exactly as shipped everywhere.");
				list.CheckboxLabeled("  VFE sprinkler: moisture valve (water only squares that need it)", ref vfeThirstValve,
					"Needs Vanilla Furniture Expanded - Farming. While powered, it waters only squares with a lit plant that is not "
					+ "already wet from another source, nearest first, within a daily budget and above a reserve floor (its gizmos).");
			}
		}
	}
}
