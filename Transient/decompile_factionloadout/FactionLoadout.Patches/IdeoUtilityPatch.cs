using HarmonyLib;
using RimWorld;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(IdeoUtility), "IdeoChangeToWeight")]
public static class IdeoUtilityPatch
{
	public static bool Active;

	[HarmonyPriority(800)]
	public static bool Prefix(ref float __result)
	{
		if (Active)
		{
			__result = 0f;
			return false;
		}
		return true;
	}
}
