using HarmonyLib;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class PawnGenRequestKindPatch
{
	[HarmonyPostfix]
	public static void Postfix(ref PawnKindDef __result, PawnGenerationRequest __instance)
	{
		if (__result != null && ((PawnGenerationRequest)(ref __instance)).Faction != null)
		{
			__result = FactionEdit.GetReplacementForPawnKind(((PawnGenerationRequest)(ref __instance)).Faction.def, __result);
		}
	}
}
