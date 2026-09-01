using HarmonyLib;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(DamageWorker_AddInjury), "ApplyDamageToPart")]
public static class VanillaExpandedFramework_DamageWorker_AddInjury_ApplyDamageToPart_Patch
{
	public static void Prefix(ref DamageInfo dinfo, Pawn pawn, DamageResult result)
	{
		if (((DamageInfo)(ref dinfo)).Weapon != null)
		{
			StorytellerDefExtension modExtension = ((Def)Find.Storyteller.def).GetModExtension<StorytellerDefExtension>();
			if (modExtension != null && modExtension.storytellerThreat != null)
			{
				((DamageInfo)(ref dinfo)).SetAmount(((DamageInfo)(ref dinfo)).Amount * modExtension.storytellerThreat.allDamagesMultiplier);
			}
		}
	}
}
