using Verse;

namespace FactionLoadout;

public class MySettings : ModSettings
{
	public static string ActivePreset = null;

	public static bool VanillaRestrictions = true;

	public static bool VerboseLogging = false;

	public static bool PatchKindInRequests = false;

	public static bool IgnorePriceLimits = false;

	public static bool OverrideForcedIdeos = false;

	public override void ExposeData()
	{
		((ModSettings)this).ExposeData();
		Scribe_Values.Look<string>(ref ActivePreset, "activePreset", (string)null, false);
		Scribe_Values.Look<bool>(ref VanillaRestrictions, "vanillaRestrictions", true, false);
		Scribe_Values.Look<bool>(ref VerboseLogging, "verboseLogging", false, false);
		Scribe_Values.Look<bool>(ref PatchKindInRequests, "patchKindInRequests", false, false);
		Scribe_Values.Look<bool>(ref IgnorePriceLimits, "ignorePriceLimits", false, false);
		Scribe_Values.Look<bool>(ref OverrideForcedIdeos, "overrideForcedIdeos", false, false);
	}
}
