using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class GaussProjectile : ExpandableProjectile
{
	public float damageFalloff;

	public override int DamageAmount => base.def.gauss.Worker.DamageAmount(this, ((Projectile)this).equipment, hitThings);

	protected override void TickInterval(int delta)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		base.TickInterval(delta);
		if (!stopped && GenView.ShouldSpawnMotesAt(((Projectile)this).ExactPosition, ((Thing)this).Map, true))
		{
			Vector3 val = ((Projectile)this).ExactRotation * Vector3.forward;
			Vector3 val2 = ((Projectile)this).ExactPosition - val;
			float num = Vector3Utility.AngleToFlat(((Projectile)this).ExactPosition, val2) - 90f;
			if (base.def.gauss.lightningGlow)
			{
				VefFleckMaker.MakeLightningGlow(((Thing)this).Map, val2, num, 0.01f * ((ThingDef)base.def).projectile.speed, Rand.Range(0.3f, 0.6f));
			}
			if (base.def.gauss.gaussDistortion)
			{
				VefFleckMaker.MakeGaussDistortion(((Thing)this).Map, val2, num + Rand.Range(-15f, 15f), ((ThingDef)base.def).projectile.speed, Rand.Range(0.2f, 0.5f));
			}
		}
	}

	public override void DoDamage(IntVec3 pos)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		if (stopped)
		{
			return;
		}
		base.DoDamage(pos);
		if (!(pos != ((Projectile)this).launcher.Position) || ((Projectile)this).launcher.Map == null || !GenGrid.InBounds(pos, ((Projectile)this).launcher.Map))
		{
			return;
		}
		List<Thing> list = ((Projectile)this).launcher.Map.thingGrid.ThingsListAt(pos);
		for (int num = list.Count - 1; num >= 0; num--)
		{
			if (IsDamagable(list[num]) && !base.def.gauss.altitudeLayersBlackList.Contains(((BuildableDef)list[num].def).altitudeLayer))
			{
				try
				{
					customImpact = true;
					Impact(list[num]);
				}
				finally
				{
					customImpact = false;
				}
			}
		}
	}

	public override bool IsDamagable(Thing t)
	{
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		Pawn val = (Pawn)(object)((t is Pawn) ? t : null);
		if (val != null && ((LocalTargetInfo)(ref ((Projectile)this).intendedTarget)).Thing != val)
		{
			if (((Projectile)this).launcher != null && ((Thing)val).Faction != null && ((Projectile)this).launcher.Faction != null && !FactionUtility.HostileTo(((Thing)val).Faction, ((Projectile)this).launcher.Faction))
			{
				if (((Projectile)this).preventFriendlyFire)
				{
					return false;
				}
				if (!Rand.Chance(Find.Storyteller.difficulty.friendlyFireChanceFactor))
				{
					return false;
				}
				if (base.def.gauss.includeInterceptChanceFromDistanceForFriendlyFire && !Rand.Chance(VerbUtility.InterceptChanceFactorFromDistance(startingPosition, t.Position)))
				{
					return false;
				}
			}
			if (!Rand.Chance(base.def.gauss.chanceToHitUnintendedLayingTarget) && (int)PawnUtility.GetPosture(val) != 0)
			{
				return false;
			}
		}
		return base.IsDamagable(t);
	}

	public override void Launch(Thing launcher, Vector3 origin, LocalTargetInfo usedTarget, LocalTargetInfo intendedTarget, ProjectileHitFlags hitFlags, bool preventFriendlyFire = false, Thing equipment = null, ThingDef targetCoverDef = null)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		base.Launch(launcher, origin, usedTarget, intendedTarget, hitFlags, preventFriendlyFire, equipment, targetCoverDef);
		if (equipment == null || base.def.gauss.damageModifierStat == null)
		{
			damageFalloff = VEFDefOf.VEF_GaussProjectileDamageModifier.defaultBaseValue;
		}
		else
		{
			damageFalloff = StatExtension.GetStatValue(equipment, base.def.gauss.damageModifierStat, true, -1);
		}
	}

	public override void ExposeData()
	{
		base.ExposeData();
		Scribe_Values.Look<float>(ref damageFalloff, "damageFalloff", 0f, false);
	}
}
