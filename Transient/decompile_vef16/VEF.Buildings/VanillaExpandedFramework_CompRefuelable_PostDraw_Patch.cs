using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(CompRefuelable), "PostDraw")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_CompRefuelable_PostDraw_Patch
{
	public static bool patchActive;

	private static bool Prepare()
	{
		return patchActive;
	}

	private static void Postfix(CompRefuelable __instance)
	{
		ThingDef def = ((Thing)((ThingComp)__instance).parent).def;
		if (def != null)
		{
			((Def)def).GetModExtension<RefuelableExtension>()?.customFuelGauge?.DrawGauge((Thing)(object)((ThingComp)__instance).parent, __instance.FuelPercentOfMax);
		}
	}
}
