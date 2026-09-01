using System;
using HarmonyLib;
using Verse;

namespace BigAndSmall.Balancing;

[HarmonyPatch(typeof(VerbProperties), "AdjustedMeleeDamageAmount", new Type[]
{
	typeof(Tool),
	typeof(Pawn),
	typeof(ThingDef),
	typeof(ThingDef),
	typeof(HediffComp_VerbGiver)
})]
public static class AdjustedMeleeDamageAmount_Patch_2
{
	public static void Postfix(ref float __result, Tool tool, Pawn attacker, ThingDef equipment, ThingDef equipmentStuff, HediffComp_VerbGiver hediffCompSource, VerbProperties __instance)
	{
		__result = AdjustedMeleeDamageAmount_Patch.GetSizeAdjustedBaseDamage(__result, attacker, tool, __instance);
	}
}
