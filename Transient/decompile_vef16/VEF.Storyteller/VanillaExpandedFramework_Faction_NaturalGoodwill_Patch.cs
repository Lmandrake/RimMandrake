using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_Faction_NaturalGoodwill_Patch
{
	public static void Postfix(Faction __instance, ref int __result)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		if (__instance.IsPlayer)
		{
			return;
		}
		StorytellerDefExtension modExtension = ((Def)Find.Storyteller.def).GetModExtension<StorytellerDefExtension>();
		if (modExtension == null)
		{
			return;
		}
		StorytellerThreat storytellerThreat = modExtension.storytellerThreat;
		if (storytellerThreat != null)
		{
			_ = storytellerThreat.naturallGoodwillForAllFactions;
			if (true)
			{
				__result = (int)((IntRange)(ref modExtension.storytellerThreat.naturallGoodwillForAllFactions)).Average;
			}
		}
	}
}
