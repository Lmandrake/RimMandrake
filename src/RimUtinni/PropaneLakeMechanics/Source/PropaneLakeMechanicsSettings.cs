using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	/// <summary>
	/// MOD_OPTIONS_RETROFIT_1's standing law: every mod ships a real settings
	/// screen — on/off per mechanic, tuning where a number is the experience,
	/// defaults = shipped behaviour, all-off degrades gracefully. Four
	/// mechanics, four kill switches; the deflagration hook is the one the
	/// design doc itself flags as needing real playtesting, so it gets its own
	/// intensity slider rather than a flat on/off.
	/// </summary>
	public class PropaneLakeMechanicsSettings : ModSettings
	{
		public bool gasVentsEnabled = true;
		public bool pipeNetworksEnabled = true;
		public bool saturationDeflagrationEnabled = true;
		public bool vWakeAgitationEnabled = true;
		public bool saturationHeistRaidEnabled = true;

		/// <summary>Multiplies every deflagration/flashover chance rolled by
		/// Patch_GasSaturationDeflagration. 1.0 = the ruled curve as designed;
		/// 0 has the same effect as disabling the toggle, kept as a slider so a
		/// worried player can dial it down instead of losing the mechanic.</summary>
		public float deflagrationIntensity = 1f;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref gasVentsEnabled, "gasVentsEnabled", true);
			Scribe_Values.Look(ref pipeNetworksEnabled, "pipeNetworksEnabled", true);
			Scribe_Values.Look(ref saturationDeflagrationEnabled, "saturationDeflagrationEnabled", true);
			Scribe_Values.Look(ref vWakeAgitationEnabled, "vWakeAgitationEnabled", true);
			Scribe_Values.Look(ref saturationHeistRaidEnabled, "saturationHeistRaidEnabled", true);
			Scribe_Values.Look(ref deflagrationIntensity, "deflagrationIntensity", 1f);
		}

		public void DoSettingsWindowContents(Rect inRect)
		{
			Listing_Standard listing = new Listing_Standard();
			listing.Begin(inRect);

			listing.CheckboxLabeled("RUT_Settings_GasVentsEnabled".Translate(), ref gasVentsEnabled,
				"RUT_Settings_GasVentsEnabled_Desc".Translate());
			listing.CheckboxLabeled("RUT_Settings_PipeNetworksEnabled".Translate(), ref pipeNetworksEnabled,
				"RUT_Settings_PipeNetworksEnabled_Desc".Translate());
			listing.CheckboxLabeled("RUT_Settings_VWakeAgitationEnabled".Translate(), ref vWakeAgitationEnabled,
				"RUT_Settings_VWakeAgitationEnabled_Desc".Translate());
			listing.CheckboxLabeled("RUT_Settings_SaturationHeistRaidEnabled".Translate(), ref saturationHeistRaidEnabled,
				"RUT_Settings_SaturationHeistRaidEnabled_Desc".Translate());

			listing.Gap();
			listing.CheckboxLabeled("RUT_Settings_DeflagrationEnabled".Translate(), ref saturationDeflagrationEnabled,
				"RUT_Settings_DeflagrationEnabled_Desc".Translate());
			if (saturationDeflagrationEnabled)
			{
				listing.Label("RUT_Settings_DeflagrationIntensity".Translate(deflagrationIntensity.ToStringPercent()));
				deflagrationIntensity = listing.Slider(deflagrationIntensity, 0f, 2f);
			}

			listing.End();
		}
	}
}
