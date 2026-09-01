using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Projectile), "Impact")]
public static class VanillaExpandedFramework_Projectile_Impact_Patch
{
	public static void Prefix(Projectile __instance, ref Thing hitThing, bool blockedByShield)
	{
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		if (blockedByShield)
		{
			return;
		}
		if (__instance.IsHomingProjectile(out var comp))
		{
			if (hitThing != ((LocalTargetInfo)(ref __instance.intendedTarget)).Thing)
			{
				foreach (Thing item in GenRadial.RadialDistinctThingsAround(((Thing)__instance).Position, ((Thing)__instance).Map, 3f, true))
				{
					if (item == ((LocalTargetInfo)(ref __instance.intendedTarget)).Thing && Vector3.Distance(Vector3Utility.Yto0(item.DrawPos), Vector3Utility.Yto0(__instance.ExactPosition)) <= 0.5f)
					{
						hitThing = item;
					}
				}
			}
			if (hitThing != null && comp.Props.hitSound != null)
			{
				SoundStarter.PlayOneShot(comp.Props.hitSound, SoundInfo.op_Implicit(hitThing));
			}
		}
		if (hitThing == null)
		{
			ProjectileExtension modExtension = ((Def)((Thing)__instance).def).GetModExtension<ProjectileExtension>();
			if (modExtension != null && modExtension.filthOnMiss != null && Rand.Chance(modExtension.filthOnMissChance) && !GridsUtility.Filled(((Thing)__instance).Position, ((Thing)__instance).Map))
			{
				FilthMaker.TryMakeFilth(((Thing)__instance).Position, ((Thing)__instance).Map, modExtension.filthOnMiss, ((IntRange)(ref modExtension.filthOnMissCount)).RandomInRange, (FilthSourceFlags)0, true);
			}
		}
	}
}
