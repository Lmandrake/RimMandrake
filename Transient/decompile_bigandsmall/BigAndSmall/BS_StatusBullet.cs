using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class BS_StatusBullet : Bullet
{
	public ModExtension_StatusAfflicter Props => ((Def)((Thing)this).def).GetModExtension<ModExtension_StatusAfflicter>();

	protected override void Impact(Thing hitThing, bool blockedByShield = false)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		Map map = ((Thing)this).Map;
		IntVec3 position = ((Thing)this).Position;
		if (Props != null && ((Thing)this).def.projectile.explosionRadius > 0f)
		{
			Explode(map, position);
		}
		else if (Props != null && hitThing != null)
		{
			Pawn val = (Pawn)(object)((hitThing is Pawn) ? hitThing : null);
			if (val != null && !blockedByShield)
			{
				ApplyStatusTo(val, 1f);
			}
		}
		((Thing)this).Destroy((DestroyMode)0);
	}

	protected virtual void Explode(Map map, IntVec3 position)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_018d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0193: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0202: Unknown result type (might be due to invalid IL or missing references)
		List<Pawn> list = (from c in GenRadial.RadialCellsAround(position, ((Thing)this).def.projectile.explosionRadius, true)
			where GenSight.LineOfSight(position, c, map)
			select c).ToList().SelectMany((IntVec3 c) => (from t in GridsUtility.GetThingList(c, map)
			where t is Pawn
			select t).Select((Func<Thing, Pawn>)((Thing t) => (Pawn)t))).ToList();
		ProjectileProperties projectile = ((Thing)this).def.projectile;
		if (((Thing)this).def.projectile.explosionEffect != null)
		{
			Effecter val = ((Thing)this).def.projectile.explosionEffect.Spawn();
			if (((Thing)this).def.projectile.explosionEffectLifetimeTicks != 0)
			{
				EffecterMaintainer effecterMaintainer = map.effecterMaintainer;
				IntVec3 position2 = ((Thing)this).Position;
				effecterMaintainer.AddEffecterToMaintain(val, IntVec3Utility.ToIntVec3(((IntVec3)(ref position2)).ToVector3()), ((Thing)this).def.projectile.explosionEffectLifetimeTicks);
			}
			else
			{
				val.Trigger(new TargetInfo(((Thing)this).Position, map, false), new TargetInfo(((Thing)this).Position, map, false), -1);
				val.Cleanup();
			}
		}
		IntVec3 val2 = position;
		Map obj = map;
		float explosionRadius = projectile.explosionRadius;
		DamageDef damageDef = projectile.damageDef;
		Thing launcher = ((Projectile)this).launcher;
		int damageAmount = ((Projectile)this).DamageAmount;
		float armorPenetration = ((Projectile)this).ArmorPenetration;
		SoundDef soundExplode = projectile.soundExplode;
		bool explosionDamageFalloff = projectile.explosionDamageFalloff;
		ThingDef equipmentDef = ((Projectile)this).equipmentDef;
		ThingDef def = ((Thing)this).def;
		ThingDef postExplosionSpawnThingDef = projectile.postExplosionSpawnThingDef;
		float postExplosionSpawnChance = projectile.postExplosionSpawnChance;
		int postExplosionSpawnThingCount = projectile.postExplosionSpawnThingCount;
		GasType? postExplosionGasType = projectile.postExplosionGasType;
		bool applyDamageToExplosionCellsNeighbors = projectile.applyDamageToExplosionCellsNeighbors;
		ThingDef preExplosionSpawnThingDef = projectile.preExplosionSpawnThingDef;
		float preExplosionSpawnChance = projectile.preExplosionSpawnChance;
		int preExplosionSpawnThingCount = projectile.preExplosionSpawnThingCount;
		float? num = Vector3Utility.AngleToFlat(((Projectile)this).origin, ((Projectile)this).destination);
		GenExplosion.DoExplosion(val2, obj, explosionRadius, damageDef, launcher, damageAmount, armorPenetration, soundExplode, equipmentDef, def, (Thing)null, postExplosionSpawnThingDef, postExplosionSpawnChance, postExplosionSpawnThingCount, postExplosionGasType, (float?)null, 255, applyDamageToExplosionCellsNeighbors, preExplosionSpawnThingDef, preExplosionSpawnChance, preExplosionSpawnThingCount, 0f, explosionDamageFalloff, num, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
		foreach (Pawn item in list)
		{
			float num2 = IntVec3Utility.DistanceTo(position, ((Thing)item).Position);
			float effect = 1f;
			if (((Thing)this).def.projectile.explosionDamageFalloff)
			{
				effect = 1f - num2 / ((Thing)this).def.projectile.explosionRadius;
			}
			ApplyStatusTo(item, effect);
		}
	}

	private void ApplyStatusTo(Pawn pawn, float effect)
	{
		float num = Props.severity;
		if (Props.scaleSeverityByDamage && ((Thing)this).def.projectile.damageDef != null)
		{
			num *= (float)((Projectile)this).DamageAmount;
		}
		float num2 = Props.severityPart;
		if (Props.softScaleSeverityByBodySize && pawn.BodySize > 1f)
		{
			num /= Mathf.Sqrt(pawn.BodySize);
			num2 /= Mathf.Sqrt(pawn.BodySize);
		}
		if (effect != 1f)
		{
			num *= effect;
		}
		if (Props.hediffToAdd != null)
		{
			Pawn_HealthTracker health = pawn.health;
			object obj;
			if (health == null)
			{
				obj = null;
			}
			else
			{
				HediffSet hediffSet = health.hediffSet;
				obj = ((hediffSet != null) ? hediffSet.GetFirstHediffOfDef(Props.hediffToAdd, false) : null);
			}
			Hediff val = (Hediff)obj;
			if (val != null)
			{
				val.Severity += num;
			}
			else
			{
				Hediff val2 = HediffMaker.MakeHediff(Props.hediffToAdd, pawn, (BodyPartRecord)null);
				val2.Severity = num;
				pawn.health.AddHediff(val2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
		if (Props.hediffToAddToPart != null)
		{
			BodyPartRecord val3 = GenCollection.RandomElement<BodyPartRecord>(pawn.health.hediffSet.GetNotMissingParts((BodyPartHeight)0, (BodyPartDepth)0, (BodyPartTagDef)null, (BodyPartRecord)null));
			Hediff val4 = HediffMaker.MakeHediff(Props.hediffToAddToPart, pawn, val3);
			val4.Severity = num2;
			pawn.health.AddHediff(val4, val3, (DamageInfo?)null, (DamageResult)null);
		}
	}
}
