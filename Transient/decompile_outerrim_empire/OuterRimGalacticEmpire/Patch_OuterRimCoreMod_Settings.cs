using HarmonyLib;
using OuterRimCore;
using Verse;

namespace OuterRimGalacticEmpire;

[HarmonyPatch(typeof(OuterRimCoreMod), "DoOptionsCategoryContents")]
public static class Patch_OuterRimCoreMod_Settings
{
	[HarmonyPostfix]
	public static void Postfix(ref Listing_Standard listing)
	{
		OuterRimGalacticEmpireMod.mod.DoOptionsCategoryContents(listing);
	}
}
