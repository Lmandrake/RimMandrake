using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(TrainableUtility))]
[HarmonyPatch("TamenessCanDecay")]
[HarmonyPatch(new Type[] { typeof(ThingDef) })]
public static class VanillaExpandedFramework_TrainableUtility_TamenessCanDecay_ForThingDef_Patch
{
	[HarmonyPrefix]
	public static bool RemoveTamenessDecayCheck(ThingDef def)
	{
		if (def.IsNoTamingDecayAnimal())
		{
			return false;
		}
		return true;
	}
}
