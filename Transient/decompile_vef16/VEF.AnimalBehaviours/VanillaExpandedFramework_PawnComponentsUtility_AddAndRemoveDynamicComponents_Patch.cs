using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(PawnComponentsUtility))]
[HarmonyPatch("AddAndRemoveDynamicComponents")]
public static class VanillaExpandedFramework_PawnComponentsUtility_AddAndRemoveDynamicComponents_Patch
{
	[HarmonyPostfix]
	private static void AddDraftability(Pawn pawn)
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Expected O, but got Unknown
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Expected O, but got Unknown
		bool num = ((Thing)pawn).Faction != null && ((Thing)pawn).Faction.IsPlayer;
		bool flag = StaticCollectionsClass.draftable_animals.Contains((Thing)(object)pawn);
		if (num && flag)
		{
			if (pawn.drafter == null)
			{
				pawn.drafter = new Pawn_DraftController(pawn);
			}
			if (pawn.equipment == null)
			{
				pawn.equipment = new Pawn_EquipmentTracker(pawn);
			}
		}
	}
}
