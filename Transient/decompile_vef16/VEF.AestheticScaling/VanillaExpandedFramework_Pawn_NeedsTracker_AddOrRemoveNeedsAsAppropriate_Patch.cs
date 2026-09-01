using HarmonyLib;
using RimWorld;

namespace VEF.AestheticScaling;

[HarmonyPatch(typeof(Pawn_NeedsTracker), "AddOrRemoveNeedsAsAppropriate")]
public static class VanillaExpandedFramework_Pawn_NeedsTracker_AddOrRemoveNeedsAsAppropriate_Patch
{
	public static void Prefix()
	{
		CachedPawnData.cacheCanBeRecalculated = false;
	}

	public static void Postfix()
	{
		CachedPawnData.cacheCanBeRecalculated = true;
	}
}
