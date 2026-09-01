using HarmonyLib;
using RimWorld;

namespace VEF;

[HarmonyPatch(typeof(TransferableUIUtility), "ContentSourceDescription")]
public static class VanillaExpandedFramework_TransferableUIUtility_ContentSourceDescription_Patch
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
