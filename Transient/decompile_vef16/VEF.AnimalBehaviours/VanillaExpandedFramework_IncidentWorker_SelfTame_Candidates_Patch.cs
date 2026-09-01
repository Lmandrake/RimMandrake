using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(IncidentWorker_SelfTame))]
[HarmonyPatch("Candidates")]
public static class VanillaExpandedFramework_IncidentWorker_SelfTame_Candidates_Patch
{
	public static IEnumerable<Pawn> Postfix(IEnumerable<Pawn> values)
	{
		List<PawnKindDef> list = new List<PawnKindDef>();
		foreach (AnimalsUnaffectedBySelfTameDef item in DefDatabase<AnimalsUnaffectedBySelfTameDef>.AllDefsListForReading)
		{
			list.AddRange(item.unaffectedBySelfTamePawns);
		}
		if (list.Count > 0)
		{
			List<Pawn> list2 = new List<Pawn>();
			{
				foreach (Pawn value in values)
				{
					if (!list.Contains(value.kindDef))
					{
						list2.Add(value);
					}
				}
				return list2;
			}
		}
		return values;
	}
}
