using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch]
public static class VanillaExpandedFramework_CurrentSocialStateInternal_Patch
{
	[HarmonyPatch(typeof(ThoughtWorker_NeedFood), "CurrentStateInternal")]
	[HarmonyPostfix]
	public static void CurrentStateInternal_Postfix(ref ThoughtState __result, Pawn p)
	{
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		if (((ThoughtState)(ref __result)).Active && GenCollection.Any<GeneExtension>(p.genes.GetActiveGeneExtensions(), (Predicate<GeneExtension>)((GeneExtension x) => x.doubleNegativeFoodThought)))
		{
			int num = ((ThoughtState)(ref __result)).StageIndex * 2;
			if (num == 0)
			{
				num = 1;
			}
			if (num > 6)
			{
				num = 6;
			}
			__result = ThoughtState.ActiveAtStage(num);
		}
	}
}
