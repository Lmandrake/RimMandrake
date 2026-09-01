using HarmonyLib;
using VEF.Apparels;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Verb), "Available")]
public static class VanillaExpandedFramework_Verb_Available_Patch
{
	public static void Postfix(Verb __instance, ref bool __result)
	{
		if (__result && __instance.EquipmentSource != null && ((Thing)(object)__instance.EquipmentSource).IsShield(out var shieldComp))
		{
			__result = shieldComp.UsableNow;
		}
	}
}
