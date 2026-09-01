using HarmonyLib;
using Verse;
using Verse.Sound;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Thing), "TakeDamage")]
public static class VanillaExpandedFramework_Thing_TakeDamage_Patch
{
	public static void Postfix(Thing __instance, DamageInfo dinfo)
	{
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		DamageDef def = ((DamageInfo)(ref dinfo)).Def;
		DamageExtension damageExtension = ((def != null) ? ((Def)def).GetModExtension<DamageExtension>() : null);
		if (damageExtension != null && damageExtension.soundOnDamage != null)
		{
			SoundStarter.PlayOneShot(damageExtension.soundOnDamage, SoundInfo.op_Implicit(__instance));
		}
	}
}
