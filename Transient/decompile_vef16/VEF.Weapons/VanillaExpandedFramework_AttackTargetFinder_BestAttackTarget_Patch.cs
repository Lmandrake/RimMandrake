using HarmonyLib;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

[HarmonyPatch(typeof(AttackTargetFinder), "BestAttackTarget")]
public static class VanillaExpandedFramework_AttackTargetFinder_BestAttackTarget_Patch
{
	public static void Prefix(IAttackTargetSearcher searcher, ref float maxDist)
	{
		Pawn val = (Pawn)(object)((searcher is Pawn) ? searcher : null);
		if (val != null)
		{
			Verb meleeVerb = val.GetMeleeVerb();
			float meleeReachRange = val.GetMeleeReachRange(meleeVerb);
			if (meleeReachRange > 1.42f)
			{
				maxDist = Mathf.Max(maxDist, meleeReachRange);
			}
		}
	}
}
