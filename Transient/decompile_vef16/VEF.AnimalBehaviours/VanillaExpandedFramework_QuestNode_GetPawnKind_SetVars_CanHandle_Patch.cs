using System.Reflection;
using HarmonyLib;
using RimWorld.QuestGen;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch]
public static class VanillaExpandedFramework_QuestNode_GetPawnKind_SetVars_CanHandle_Patch
{
	private static MethodBase TargetMethod()
	{
		return typeof(QuestNode_GetPawnKind).GetNestedType("<>c__DisplayClass7_0", BindingFlags.Instance | BindingFlags.NonPublic).GetMethod("<GetKindDef>g__CanHandle|1", BindingFlags.Instance | BindingFlags.NonPublic);
	}

	public static void Postfix(PawnKindDef animal, ref bool __result)
	{
		if (StaticCollectionsClass.questDisabledAnimals.Contains(animal))
		{
			__result = false;
		}
	}
}
