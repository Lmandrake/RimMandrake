using HarmonyLib;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Projectile), "Tick")]
public static class VanillaExpandedFramework_Projectile_Tick_Patch
{
	public static void Postfix(Projectile __instance)
	{
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		if (__instance.IsHomingProjectile(out var comp) && comp.CanChangeTrajectory())
		{
			__instance.SetDestination(((LocalTargetInfo)(ref __instance.intendedTarget)).CenterVector3);
		}
	}
}
