using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(Pawn_ApparelTracker), "ExposeData")]
public static class VanillaExpandedFramework_Pawn_ApparelTracker_ExposeData_Patch
{
	private static void Postfix(Pawn_ApparelTracker __instance)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Invalid comparison between Unknown and I4
		if ((int)Scribe.mode != 4 || __instance.WornApparel == null)
		{
			return;
		}
		foreach (Apparel item in __instance.WornApparel)
		{
			ApparelExtensionUtilities.EquipGear(__instance.pawn, (Thing)(object)item);
		}
	}
}
