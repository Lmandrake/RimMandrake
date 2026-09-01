using HarmonyLib;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(Thing), "TakeDamage")]
public static class Patch_TakeDamage
{
	public static Thing instigatorToSet;

	public static void Prefix(Thing __instance, DamageInfo dinfo)
	{
		if (instigatorToSet != null && ((DamageInfo)(ref dinfo)).Instigator == null)
		{
			AccessTools.Field(typeof(DamageInfo), "instigatorInt").SetValueDirect(__makeref(dinfo), instigatorToSet);
		}
	}
}
