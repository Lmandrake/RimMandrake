using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.Abilities;

public class AbilityProjectile : Projectile
{
	public Ability ability;

	protected override void Impact(Thing hitThing, bool blockedByShield = false)
	{
		Map map = ((Thing)this).Map;
		((Projectile)this).Impact(hitThing, false);
		DoImpact(hitThing, map);
	}

	protected virtual void DoImpact(Thing hitThing, Map map)
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Expected O, but got Unknown
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0241: Unknown result type (might be due to invalid IL or missing references)
		//IL_0248: Unknown result type (might be due to invalid IL or missing references)
		//IL_024d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0258: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_028a: Unknown result type (might be due to invalid IL or missing references)
		//IL_026b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0131: Unknown result type (might be due to invalid IL or missing references)
		//IL_0136: Unknown result type (might be due to invalid IL or missing references)
		//IL_01de: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0215: Unknown result type (might be due to invalid IL or missing references)
		BattleLogEntry_RangedImpact val = new BattleLogEntry_RangedImpact(base.launcher, hitThing, ((LocalTargetInfo)(ref base.intendedTarget)).Thing, base.equipmentDef ?? ((Thing)ability.pawn).def, ((Thing)this).def, base.targetCoverDef);
		Find.BattleLog.Add((LogEntry)(object)val);
		ability.TargetEffects((GlobalTargetInfo[])(object)new GlobalTargetInfo[1]
		{
			new GlobalTargetInfo(((Thing)this).Position, map, false)
		});
		AbilityExtension_Projectile modExtension = ((Def)ability.def).GetModExtension<AbilityExtension_Projectile>();
		if (modExtension != null && modExtension.soundOnImpact != null)
		{
			SoundStarter.PlayOneShot(modExtension.soundOnImpact, SoundInfo.op_Implicit(new TargetInfo(((Thing)this).Position, map, false)));
		}
		float powerForPawn = ability.GetPowerForPawn();
		if (hitThing != null)
		{
			DamageDef damageDef = ((Thing)this).def.projectile.damageDef;
			Quaternion exactRotation = ((Projectile)this).ExactRotation;
			DamageInfo val2 = default(DamageInfo);
			((DamageInfo)(ref val2))._002Ector(damageDef, powerForPawn, float.MaxValue, ((Quaternion)(ref exactRotation)).eulerAngles.y, base.launcher, (BodyPartRecord)null, base.equipmentDef, (SourceCategory)0, ((LocalTargetInfo)(ref base.intendedTarget)).Thing, true, true, (QualityCategory)2, true, false);
			hitThing.TakeDamage(val2).AssociateWithLog((LogEntry_DamageResult)(object)val);
			Pawn val3 = (Pawn)(object)((hitThing is Pawn) ? hitThing : null);
			if (val3 != null)
			{
				ability.ApplyHediffs((GlobalTargetInfo[])(object)new GlobalTargetInfo[1]
				{
					new GlobalTargetInfo((Thing)(object)val3)
				});
				if (val3.stances != null && val3.BodySize <= ((Thing)this).def.projectile.stoppingPower + 0.001f)
				{
					val3.stances.stagger.StaggerFor(95, 0.17f);
				}
			}
			if (((Thing)this).def.projectile.extraDamages != null)
			{
				DamageInfo val4 = default(DamageInfo);
				foreach (ExtraDamage extraDamage in ((Thing)this).def.projectile.extraDamages)
				{
					if (Rand.Chance(extraDamage.chance))
					{
						DamageDef def = extraDamage.def;
						float amount = extraDamage.amount;
						float num = extraDamage.AdjustedArmorPenetration();
						exactRotation = ((Projectile)this).ExactRotation;
						((DamageInfo)(ref val4))._002Ector(def, amount, num, ((Quaternion)(ref exactRotation)).eulerAngles.y, base.launcher, (BodyPartRecord)null, base.equipmentDef, (SourceCategory)0, ((LocalTargetInfo)(ref base.intendedTarget)).Thing, true, true, (QualityCategory)2, true, false);
						hitThing.TakeDamage(val4).AssociateWithLog((LogEntry_DamageResult)(object)val);
					}
				}
			}
		}
		else
		{
			SoundStarter.PlayOneShot(SoundDefOf.BulletImpact_Ground, SoundInfo.op_Implicit(new TargetInfo(((Thing)this).Position, map, false)));
			if (GridsUtility.GetTerrain(((Thing)this).Position, map).takeSplashes)
			{
				FleckMaker.WaterSplash(((Projectile)this).ExactPosition, map, Mathf.Sqrt(powerForPawn) * 1f, 4f);
			}
			else
			{
				FleckMaker.Static(((Projectile)this).ExactPosition, map, FleckDefOf.ShotHit_Dirt, 1f);
			}
		}
		if (((Thing)this).def.projectile.explosionRadius > 0f)
		{
			DoExplosion(map, powerForPawn);
		}
	}

	protected virtual void DoExplosion(Map map, float power)
	{
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0148: Unknown result type (might be due to invalid IL or missing references)
		//IL_014e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)this).def.projectile.explosionEffect != null)
		{
			Effecter obj = ((Thing)this).def.projectile.explosionEffect.Spawn();
			obj.Trigger(new TargetInfo(((Thing)this).Position, map, false), new TargetInfo(((Thing)this).Position, map, false), -1);
			obj.Cleanup();
		}
		IntVec3 position = ((Thing)this).Position;
		float explosionRadius = ((Thing)this).def.projectile.explosionRadius;
		DamageDef damageDef = ((Thing)this).def.projectile.damageDef;
		Thing launcher = base.launcher;
		int num = Mathf.RoundToInt(power);
		SoundDef soundExplode = ((Thing)this).def.projectile.soundExplode;
		ThingDef equipmentDef = base.equipmentDef;
		ThingDef def = ((Thing)this).def;
		Thing thing = ((LocalTargetInfo)(ref base.intendedTarget)).Thing;
		ThingDef postExplosionSpawnThingDef = ((Thing)this).def.projectile.postExplosionSpawnThingDef;
		float postExplosionSpawnChance = ((Thing)this).def.projectile.postExplosionSpawnChance;
		int postExplosionSpawnThingCount = ((Thing)this).def.projectile.postExplosionSpawnThingCount;
		ThingDef preExplosionSpawnThingDef = ((Thing)this).def.projectile.preExplosionSpawnThingDef;
		float preExplosionSpawnChance = ((Thing)this).def.projectile.preExplosionSpawnChance;
		int preExplosionSpawnThingCount = ((Thing)this).def.projectile.preExplosionSpawnThingCount;
		bool applyDamageToExplosionCellsNeighbors = ((Thing)this).def.projectile.applyDamageToExplosionCellsNeighbors;
		float explosionChanceToStartFire = ((Thing)this).def.projectile.explosionChanceToStartFire;
		bool explosionDamageFalloff = ((Thing)this).def.projectile.explosionDamageFalloff;
		float? num2 = Vector3Utility.AngleToFlat(base.origin, base.destination);
		GenExplosion.DoExplosion(position, map, explosionRadius, damageDef, launcher, num, float.MaxValue, soundExplode, equipmentDef, def, thing, postExplosionSpawnThingDef, postExplosionSpawnChance, postExplosionSpawnThingCount, (GasType?)null, (float?)null, 255, applyDamageToExplosionCellsNeighbors, preExplosionSpawnThingDef, preExplosionSpawnChance, preExplosionSpawnThingCount, explosionChanceToStartFire, explosionDamageFalloff, num2, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
	}

	public override void ExposeData()
	{
		((Projectile)this).ExposeData();
		Scribe_References.Look<Ability>(ref ability, "ability", false);
	}
}
