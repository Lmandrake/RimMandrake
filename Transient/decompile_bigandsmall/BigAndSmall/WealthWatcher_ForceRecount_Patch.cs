using HarmonyLib;
using RimWorld;

namespace BigAndSmall;

[HarmonyPatch(typeof(WealthWatcher), "ForceRecount")]
public static class WealthWatcher_ForceRecount_Patch
{
	public static bool raidWealthActive;

	[HarmonyPrefix]
	public static void WealthCountStart(WealthWatcher __instance, bool allowDuringInit)
	{
		raidWealthActive = true;
	}

	[HarmonyPostfix]
	public static void WealthCountEnd(WealthWatcher __instance, bool allowDuringInit)
	{
		raidWealthActive = false;
	}
}
