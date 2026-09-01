using HarmonyLib;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(Verb_LaunchProjectile), "TryCastShot")]
public static class Verb_LaunchProjectile_TryCastShot_Patch
{
	public static void Postfix(Verb_LaunchProjectile __instance, bool __result)
	{
		if (__result)
		{
			Thing caster = ((Verb)__instance).caster;
			((caster != null) ? ThingCompUtility.TryGetComp<CompRefuelable_DualFuel>(caster) : null)?.ConsumeSecondaryFuel(1f);
		}
	}
}
