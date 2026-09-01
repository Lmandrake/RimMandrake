using System;
using HarmonyLib;
using UnityEngine;
using VEF.Hediffs;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Projectile), "Launch", new Type[]
{
	typeof(Thing),
	typeof(Vector3),
	typeof(LocalTargetInfo),
	typeof(LocalTargetInfo),
	typeof(ProjectileHitFlags),
	typeof(bool),
	typeof(Thing),
	typeof(ThingDef)
})]
public static class VanillaExpandedFramework_Projectile_Launch_Patch
{
	public static void Postfix(Projectile __instance, Thing launcher, Vector3 origin, ref LocalTargetInfo usedTarget, LocalTargetInfo intendedTarget, bool preventFriendlyFire, Thing equipment, ThingDef targetCoverDef)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		if (__instance is ExpandableProjectile)
		{
			return;
		}
		if (__instance.IsHomingProjectile(out var comp))
		{
			__instance.usedTarget = __instance.intendedTarget;
			__instance.SetDestination(((LocalTargetInfo)(ref __instance.intendedTarget)).CenterVector3 + comp.DispersionOffset);
			comp.originLaunchCell = NonPublicFields.Projectile_origin.Invoke(__instance);
			return;
		}
		Pawn val = (Pawn)(object)((launcher is Pawn) ? launcher : null);
		if (val != null && GenCollection.Any<Hediff>(val.health.hediffSet.hediffs, (Predicate<Hediff>)((Hediff x) => HediffUtility.TryGetComp<HediffComp_Targeting>(x)?.Props.neverMiss ?? false)))
		{
			__instance.usedTarget = __instance.intendedTarget;
			__instance.SetDestination(((LocalTargetInfo)(ref __instance.intendedTarget)).CenterVector3);
		}
	}

	public static void SetDestination(this Projectile projectile, Vector3 destination)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		ref Vector3 reference = ref NonPublicFields.Projectile_destination.Invoke(projectile);
		if (Vector3.Distance(Vector3Utility.Yto0(reference), Vector3Utility.Yto0(destination)) >= 0.1f)
		{
			ref Vector3 reference2 = ref NonPublicFields.Projectile_origin.Invoke(projectile);
			Vector3 val = default(Vector3);
			((Vector3)(ref val))._002Ector(projectile.ExactPosition.x, reference2.y, projectile.ExactPosition.z);
			reference2 = val;
			reference = destination;
			NonPublicFields.Projectile_ticksToImpact.Invoke(projectile) = Mathf.CeilToInt(NonPublicProperties.Projectile_get_StartingTicksToImpact(projectile) - 1f);
		}
	}

	public static bool IsHomingProjectile(this Projectile projectile, out CompHomingProjectile comp)
	{
		comp = ((ThingWithComps)projectile).GetComp<CompHomingProjectile>();
		return comp != null;
	}
}
