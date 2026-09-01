using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(VerbProperties), "AdjustedMeleeDamageAmount", new Type[]
{
	typeof(Verb),
	typeof(Pawn)
})]
public static class VanillaExpandedFramework_AdjustedMeleeDamageAmount_Patch
{
	public static void Postfix(Verb ownerVerb, Pawn attacker, ref float __result)
	{
		__result *= StatExtension.GetStatValue((Thing)(object)attacker, VEFDefOf.VEF_MeleeAttackDamageFactor, true, -1);
	}
}
