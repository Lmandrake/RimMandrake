using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(SanguophageUtility), "DoBite")]
public static class SanguophageUtility_DoBite_Patch
{
	public static void Postfix(Pawn biter, Pawn victim, float targetHemogenGain, float nutritionGain, float targetBloodLoss, float victimResistanceGain, IntRange bloodFilthToSpawnRange, ThoughtDef thoughtDefToGiveTarget = null, ThoughtDef opinionThoughtToGiveTarget = null)
	{
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		List<Gene> allActiveEndoGenes = GeneHelpers.GetAllActiveEndoGenes(biter);
		bool flag = GenCollection.Any<Gene>(allActiveEndoGenes, (Predicate<Gene>)((Gene x) => ((Def)x.def).defName == "VU_WhiteRoseBite"));
		bool num = GenCollection.Any<Gene>(allActiveEndoGenes, (Predicate<Gene>)((Gene x) => ((Def)x.def).defName == "VU_SuccubusBloodFeeder"));
		if (flag)
		{
			CompAbilityEffect_WhiteRoseBite.WhiteRoseBite(victim);
		}
		if (num && victim.IsPrisoner)
		{
			Pawn_GuestTracker guest = victim.guest;
			float num2 = victim.guest.resistance - 1f;
			FloatRange value = victim.kindDef.initialResistanceRange.Value;
			guest.resistance = Mathf.Min(num2, ((FloatRange)(ref value)).TrueMax);
			Pawn_GuestTracker guest2 = victim.guest;
			float num3 = victim.guest.will - 2f;
			value = victim.kindDef.initialWillRange.Value;
			guest2.will = Mathf.Min(num3, ((FloatRange)(ref value)).TrueMax);
		}
	}
}
