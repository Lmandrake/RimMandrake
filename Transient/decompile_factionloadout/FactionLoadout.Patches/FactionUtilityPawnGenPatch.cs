using HarmonyLib;
using RimWorld;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(FactionUtility), "HostileTo")]
public static class FactionUtilityPawnGenPatch
{
	public static bool Active;

	[HarmonyPriority(800)]
	private static bool Prefix(ref bool __result)
	{
		if (!Active)
		{
			return true;
		}
		__result = false;
		return false;
	}
}
