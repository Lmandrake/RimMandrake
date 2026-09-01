using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Pawn_WorkSettings), "Notify_DisabledWorkTypesChanged")]
public static class Pawn_WorkSettings_Notify_DisabledWorkTypesChanged
{
	public static void Postfix(Pawn_WorkSettings __instance)
	{
		if (__instance.priorities == null || __instance.pawn == null)
		{
			return;
		}
		BSCache cachePrepatched = __instance.pawn.GetCachePrepatched();
		if (cachePrepatched == null || !GenCollection.Any<WorkTypeDef>(cachePrepatched.disabledWorkTypes))
		{
			return;
		}
		foreach (WorkTypeDef disabledWorkType in cachePrepatched.disabledWorkTypes)
		{
			__instance.Disable(disabledWorkType);
			List<WorkTypeDef> cachedDisabledWorkTypes = __instance.pawn.cachedDisabledWorkTypes;
			if (cachedDisabledWorkTypes != null)
			{
				GenCollection.AddDistinct<WorkTypeDef>(cachedDisabledWorkTypes, disabledWorkType);
			}
			List<WorkTypeDef> cachedDisabledWorkTypesPermanent = __instance.pawn.cachedDisabledWorkTypesPermanent;
			if (cachedDisabledWorkTypesPermanent != null)
			{
				GenCollection.AddDistinct<WorkTypeDef>(cachedDisabledWorkTypesPermanent, disabledWorkType);
			}
		}
	}
}
