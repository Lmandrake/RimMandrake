using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(Verb), "Available")]
public static class Verb_Available_Patch
{
	public static void Postfix(Verb __instance, ref bool __result)
	{
		if (__result)
		{
			Thing caster = __instance.caster;
			CompRefuelable_DualFuel compRefuelable_DualFuel = ((caster != null) ? ThingCompUtility.TryGetComp<CompRefuelable_DualFuel>(caster) : null);
			if (compRefuelable_DualFuel != null && (!((CompRefuelable)compRefuelable_DualFuel).HasFuel || !compRefuelable_DualFuel.HasSecondaryFuel))
			{
				__result = false;
			}
		}
	}
}
