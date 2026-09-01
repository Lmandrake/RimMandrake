using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(IncidentWorker_Disease))]
[HarmonyPatch("PotentialVictims")]
public static class VanillaExpandedFramework_IncidentWorker_Disease_PotentialVictims_Patch
{
	public static IEnumerable<Pawn> Postfix(IEnumerable<Pawn> values)
	{
		List<Pawn> list = new List<Pawn>();
		foreach (Pawn value in values)
		{
			if (!StaticCollectionsClass.nodisease_animals.Contains((Thing)(object)value))
			{
				list.Add(value);
			}
		}
		return list;
	}
}
