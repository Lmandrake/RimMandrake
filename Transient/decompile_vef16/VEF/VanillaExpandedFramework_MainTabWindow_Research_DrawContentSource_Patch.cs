using HarmonyLib;
using RimWorld;

namespace VEF;

[HarmonyPatch(typeof(MainTabWindow_Research), "DrawContentSource")]
public static class VanillaExpandedFramework_MainTabWindow_Research_DrawContentSource_Patch
{
	public static bool Prefix()
	{
		if (VFEGlobal.settings.disableModSourceReport)
		{
			return false;
		}
		return true;
	}
}
