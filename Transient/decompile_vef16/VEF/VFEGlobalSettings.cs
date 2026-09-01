using System.Collections.Generic;
using Verse;

namespace VEF;

public class VFEGlobalSettings : ModSettings
{
	public Dictionary<string, bool> toggablePatch = new Dictionary<string, bool>();

	public bool enableVerboseLogging;

	public bool disableCaching;

	public bool randomStartsAsRandom;

	public bool hideRandomizeButtons;

	public bool enablePipeSystemNoStorageAlert = true;

	public Dictionary<string, bool> weatherDamagesOptions = new Dictionary<string, bool>();

	public bool disableModSourceReport;

	public override void ExposeData()
	{
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Invalid comparison between Unknown and I4
		((ModSettings)this).ExposeData();
		Scribe_Collections.Look<string, bool>(ref toggablePatch, "toggablePatch", (LookMode)1, (LookMode)1);
		Scribe_Values.Look<bool>(ref enableVerboseLogging, "enableVerboseLogging", false, false);
		Scribe_Values.Look<bool>(ref disableCaching, "disableCaching", true, false);
		Scribe_Values.Look<bool>(ref randomStartsAsRandom, "randomStartsAsRandom", false, false);
		Scribe_Values.Look<bool>(ref hideRandomizeButtons, "hideRandomizeButtons", false, true);
		Scribe_Values.Look<bool>(ref disableModSourceReport, "disableModSourceReport", false, false);
		Scribe_Values.Look<bool>(ref enablePipeSystemNoStorageAlert, "enablePipeSystemNoStorageAlert", true, false);
		Scribe_Collections.Look<string, bool>(ref weatherDamagesOptions, "weatherDamagesOptions", (LookMode)1, (LookMode)1);
		if ((int)Scribe.mode == 4)
		{
			if (weatherDamagesOptions == null)
			{
				weatherDamagesOptions = new Dictionary<string, bool>();
			}
			if (toggablePatch == null)
			{
				toggablePatch = new Dictionary<string, bool>();
			}
		}
	}
}
