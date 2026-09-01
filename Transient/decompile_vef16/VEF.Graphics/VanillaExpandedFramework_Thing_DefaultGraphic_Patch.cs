using HarmonyLib;
using Verse;

namespace VEF.Graphics;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_Thing_DefaultGraphic_Patch
{
	public static bool Prefix(Thing __instance, ref Graphic __result)
	{
		if (ReflectionCache.itemGraphic.Invoke(__instance) == null && !(__instance is Mote))
		{
			CompGraphicCustomization compGraphicCustomization = ThingCompUtility.TryGetComp<CompGraphicCustomization>(__instance);
			if (compGraphicCustomization != null)
			{
				__result = (ReflectionCache.itemGraphic.Invoke(__instance) = compGraphicCustomization.Graphic);
				return false;
			}
		}
		return true;
	}
}
