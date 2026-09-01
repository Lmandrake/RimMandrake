using HarmonyLib;
using UnityEngine;
using VEF.AestheticScaling;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(PawnRenderer), "BaseHeadOffsetAt")]
public static class VanillaExpandedFramework_PawnRenderer_BaseHeadOffsetAt
{
	public static FieldRef<PawnRenderer, Pawn> pawnFieldRef;

	public static void Postfix(PawnRenderer __instance, ref Vector3 __result)
	{
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawnFromRef = GetPawnFromRef(__instance);
		if (pawnFromRef != null)
		{
			CachedPawnData cacheUltraSpeed = PawnDataCache.GetCacheUltraSpeed(pawnFromRef, canRefresh: false);
			if (cacheUltraSpeed != null)
			{
				__result = new Vector3(__result.x * cacheUltraSpeed.headPositionMultiplier, __result.y, __result.z * cacheUltraSpeed.headPositionMultiplier);
			}
		}
	}

	private static Pawn GetPawnFromRef(PawnRenderer __instance)
	{
		if (pawnFieldRef == null)
		{
			pawnFieldRef = AccessTools.FieldRefAccess<PawnRenderer, Pawn>("pawn");
		}
		return pawnFieldRef.Invoke(__instance);
	}
}
