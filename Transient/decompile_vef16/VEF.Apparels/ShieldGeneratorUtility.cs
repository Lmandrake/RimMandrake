using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Apparels;

public static class ShieldGeneratorUtility
{
	public static bool AffectsShields(this DamageDef damageDef)
	{
		if (!damageDef.ignoreShields)
		{
			if (!damageDef.isExplosive)
			{
				return damageDef == DamageDefOf.EMP;
			}
			return true;
		}
		return false;
	}

	public static void CheckIntercept(Thing thing, Map map, int damageAmount, DamageDef damageDef, Func<IEnumerable<IntVec3>> cellGetter, Func<bool> canIntercept = null, Func<CompShieldField, bool> preIntercept = null, Action<CompShieldField> postIntercept = null)
	{
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		if (canIntercept != null && !canIntercept())
		{
			return;
		}
		HashSet<IntVec3> hashSet = new HashSet<IntVec3>(cellGetter());
		List<CompShieldField> list = CompShieldField.ListerShieldGensActiveIn(map).ToList();
		for (int i = 0; i < list.Count; i++)
		{
			CompShieldField compShieldField = list[i];
			if ((preIntercept != null && !preIntercept(compShieldField)) || compShieldField.coveredCells == null)
			{
				continue;
			}
			bool flag = false;
			foreach (IntVec3 item in hashSet)
			{
				if (compShieldField.coveredCells.Contains(item))
				{
					flag = true;
					break;
				}
			}
			if (flag)
			{
				compShieldField.AbsorbDamage(damageAmount, damageDef, thing);
				postIntercept?.Invoke(compShieldField);
				break;
			}
		}
	}

	public static bool BlockableByShield(this Projectile proj, CompShieldField shieldGen)
	{
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		if (!((Thing)proj).def.projectile.flyOverhead)
		{
			return true;
		}
		if (!shieldGen.coveredCells.Contains(IntVec3Utility.ToIntVec3(NonPublicFields.Projectile_origin.Invoke(proj))))
		{
			return (float)NonPublicFields.Projectile_ticksToImpact.Invoke(proj) / NonPublicProperties.Projectile_get_StartingTicksToImpact(proj) <= 0.5f;
		}
		return false;
	}

	public static bool CheckPodHostility(CompShieldField shield, DropPodIncoming dropPod)
	{
		ThingOwner innerContainer = dropPod.Contents.innerContainer;
		for (int i = 0; i < innerContainer.Count; i++)
		{
			Thing obj = innerContainer[i];
			Pawn val = (Pawn)(object)((obj is Pawn) ? obj : null);
			if (val != null && shield.HostFaction != null && GenHostility.HostileTo((Thing)(object)val, shield.HostFaction))
			{
				return true;
			}
		}
		return false;
	}

	public static void KillPawn(Pawn pawn, IntVec3 position, Map map)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		GenPlace.TryPlaceThing((Thing)(object)pawn, position, map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
		pawn.inventory.DestroyAll((DestroyMode)0);
		((Thing)pawn).Kill((DamageInfo?)new DamageInfo(DamageDefOf.Crush, 100f, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false), (Hediff)null);
		((Thing)pawn.Corpse).Destroy((DestroyMode)0);
	}
}
