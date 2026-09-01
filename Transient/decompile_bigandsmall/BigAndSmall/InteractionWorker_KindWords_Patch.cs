using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(InteractionWorker_KindWords), "RandomSelectionWeight")]
public static class InteractionWorker_KindWords_Patch
{
	public static void Postfix(ref float __result, Pawn initiator, Pawn recipient)
	{
		if (initiator.story.traits.HasTrait(BSDefs.BS_Gentle))
		{
			__result = 0.01f;
		}
	}
}
