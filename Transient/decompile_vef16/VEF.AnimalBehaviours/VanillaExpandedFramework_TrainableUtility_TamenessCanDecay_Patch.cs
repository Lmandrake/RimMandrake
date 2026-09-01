using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(TrainableUtility))]
[HarmonyPatch("TamenessCanDecay")]
[HarmonyPatch(new Type[] { typeof(Pawn) })]
public static class VanillaExpandedFramework_TrainableUtility_TamenessCanDecay_Patch
{
	[HarmonyPrefix]
	public static bool RemoveTamenessDecayCheck(Pawn pawn)
	{
		if (((Thing)pawn).def.IsNoTamingDecayAnimal())
		{
			return false;
		}
		return true;
	}
}
