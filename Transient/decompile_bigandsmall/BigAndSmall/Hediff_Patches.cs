using System;
using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class Hediff_Patches
{
	[HarmonyPriority(600)]
	[HarmonyPatch(typeof(Hediff), "PostRemoved")]
	[HarmonyPostfix]
	public static void Hediff_PostRemove(Hediff __instance)
	{
		Pawn val = __instance?.pawn;
		if (val != null)
		{
			List<PawnExtension> list = __instance?.def?.GetAllPawnExtensionsOnHediff();
			if (GenCollection.Any<PawnExtension>(list, (Predicate<PawnExtension>)((PawnExtension x) => x.RequiresCacheRefresh())) || (((val == null) ? null : val.Drawer?.renderer) != null && ((Thing)val).Spawned))
			{
				HumanoidPawnScaler.ShedueleForceRegenerateSafe(val, 40);
			}
			else
			{
				HumanoidPawnScaler.GetInvalidateLater(val, 40);
			}
		}
	}

	[HarmonyPatch(typeof(Hediff), "OnStageIndexChanged")]
	[HarmonyPostfix]
	public static void OnStageIndexChanged(Hediff __instance, int stageIndex)
	{
		if (__instance != null)
		{
			Pawn pawn = __instance.pawn;
			bool? obj;
			if (pawn == null)
			{
				obj = null;
			}
			else
			{
				RaceProperties raceProps = pawn.RaceProps;
				obj = ((raceProps != null) ? new bool?(raceProps.Humanlike) : ((bool?)null));
			}
			bool? flag = obj;
			if (flag == true)
			{
				HumanoidPawnScaler.GetInvalidateLater(__instance.pawn, 60);
			}
		}
	}

	[HarmonyPatch(typeof(Hediff), "PostAdd")]
	[HarmonyPostfix]
	public static void Hediff_PostAdd(Hediff __instance, DamageInfo? dinfo)
	{
		Pawn val = __instance?.pawn;
		if (val != null && __instance != null)
		{
			HumanoidPawnScaler.GetInvalidateLater(val, 30);
		}
	}

	[HarmonyPatch(typeof(Hediff), "GetTooltip")]
	[HarmonyPostfix]
	public static void Hediff_GetTooltip(Hediff __instance, ref string __result)
	{
		List<PawnExtension> list = __instance?.def?.GetAllPawnExtensionsOnHediff();
		if (!GenCollection.Any<PawnExtension>(list))
		{
			return;
		}
		try
		{
			if (list.TryGetDescription(out var content))
			{
				__result = __result + "\n\n" + content;
			}
		}
		catch (Exception ex)
		{
			Log.Error("Error generating Hediff.Description.\n" + ex.Message + "\n" + ex.StackTrace);
		}
	}
}
