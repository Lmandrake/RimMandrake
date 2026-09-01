using System;
using System.Linq;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Hediff), "PostAdd")]
public static class Hediff_PostAdd
{
	public static void Postfix(Hediff __instance)
	{
		if (((Def)(__instance?.def?)).defName == "VRE_PsychicBondBloodlust" && __instance?.pawn?.health != null && __instance.pawn.GetAllActiveGenes().Any((Gene x) => ((Def)(x.def?)).defName == "VU_LethalLover"))
		{
			try
			{
				__instance.pawn.health.RemoveHediff(__instance);
			}
			catch (Exception ex)
			{
				Log.Error("Exception removing hediff:\n" + ex.Message + "\n" + ex.StackTrace);
			}
		}
	}
}
