using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(SkillRecord), "Notify_SkillDisablesChanged")]
public static class SkillRecord_Notify_SkillDisablesChanged
{
	public static void Postfix(SkillRecord __instance)
	{
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		if (__instance?.pawn != null)
		{
			BSCache cachePrepatched = __instance.pawn.GetCachePrepatched();
			if (cachePrepatched != null && GenCollection.Any<SkillDef>(cachePrepatched.skillsDisabledByExtensions) && cachePrepatched.skillsDisabledByExtensions.Contains(__instance.def))
			{
				__instance.cachedPermanentlyDisabled = (BoolUnknown)0;
				__instance.cachedTotallyDisabled = (BoolUnknown)0;
			}
		}
	}
}
