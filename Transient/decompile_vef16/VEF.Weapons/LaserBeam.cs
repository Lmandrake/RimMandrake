using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class LaserBeam : Bullet
{
	private LaserBeamDef def => ((Thing)this).def as LaserBeamDef;

	private void TriggerEffect(EffecterDef effect, Vector3 position)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		TriggerEffect(effect, IntVec3.FromVector3(position));
	}

	private void TriggerEffect(EffecterDef effect, IntVec3 dest)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		if (effect != null)
		{
			TargetInfo val = default(TargetInfo);
			((TargetInfo)(ref val))._002Ector(dest, ((Thing)this).Map, false);
			Effecter obj = effect.Spawn();
			obj.Trigger(val, val, -1);
			obj.Cleanup();
		}
	}

	private void SpawnBeam(Vector3 a, Vector3 b)
	{
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		LaserBeamGraphic laserBeamGraphic = ThingMaker.MakeThing(def.beamGraphic, (ThingDef)null) as LaserBeamGraphic;
		laserBeamGraphic.laserBeam = this;
		if (laserBeamGraphic != null)
		{
			laserBeamGraphic.Setup(((Projectile)this).launcher, a, b);
			GenSpawn.Spawn((Thing)(object)laserBeamGraphic, IntVec3Utility.ToIntVec3(((Projectile)this).origin), ((Thing)this).Map, (WipeMode)0);
		}
	}

	private void SpawnBeamReflections(Vector3 a, Vector3 b, int count)
	{
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		for (int i = 0; i < count; i++)
		{
			Vector3 val = b - a;
			Vector3 normalized = ((Vector3)(ref val)).normalized;
			Vector3 b2 = b - Vector3Utility.RotatedBy(normalized, Rand.Range(-22.5f, 22.5f)) * Rand.Range(1f, 4f);
			SpawnBeam(b, b2);
		}
	}

	protected override void Impact(Thing hitThing, bool blockedByShield = false)
	{
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0179: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_017c: Unknown result type (might be due to invalid IL or missing references)
		//IL_018c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0191: Unknown result type (might be due to invalid IL or missing references)
		//IL_0192: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_022f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0230: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0204: Unknown result type (might be due to invalid IL or missing references)
		//IL_0284: Unknown result type (might be due to invalid IL or missing references)
		bool flag = (hitThing.IsShielded() && def.IsWeakToShields) || blockedByShield;
		LaserGunDef laserGunDef = ((Projectile)this).equipmentDef as LaserGunDef;
		Vector3 val = ((Projectile)this).destination - ((Projectile)this).origin;
		Vector3 normalized = ((Vector3)(ref val)).normalized;
		normalized.y = 0f;
		Vector3 val2 = ((Projectile)this).origin + normalized * (laserGunDef?.barrelLength ?? 0.9f);
		Vector3 val3 = ((flag && hitThing != null) ? (GenThing.TrueCenter(hitThing) - Vector3Utility.RotatedBy(normalized, Rand.Range(-22.5f, 22.5f)) * 0.8f) : ((Projectile)this).destination);
		val2.y = (val3.y = ((BuildableDef)def).Altitude);
		SpawnBeam(val2, val3);
		if (def.canExplode && ((ThingDef)def).projectile.explosionRadius > 0f)
		{
			Explode(hitThing);
			GenExplosion.NotifyNearbyPawnsOfDangerousExplosive((Thing)(object)this, ((ThingDef)def).projectile.damageDef, ((Projectile)this).launcher.Faction, (Thing)null);
		}
		Thing launcher = ((Projectile)this).launcher;
		Pawn val4 = (Pawn)(object)((launcher is Pawn) ? launcher : null);
		IDrawnWeaponWithRotation drawnWeaponWithRotation = null;
		if (val4 != null && val4.equipment != null)
		{
			drawnWeaponWithRotation = val4.equipment.Primary as IDrawnWeaponWithRotation;
		}
		if (drawnWeaponWithRotation == null && ((Projectile)this).launcher is Building_LaserGun building_LaserGun)
		{
			drawnWeaponWithRotation = ((Building_TurretGun)building_LaserGun).gun as IDrawnWeaponWithRotation;
		}
		if (drawnWeaponWithRotation != null)
		{
			float num = Vector3Utility.AngleFlat(val3 - val2) - Vector3Utility.AngleFlat(((LocalTargetInfo)(ref ((Projectile)this).intendedTarget)).CenterVector3 - val2);
			drawnWeaponWithRotation.RotationOffset = (num + 180f) % 360f - 180f;
		}
		if (hitThing == null)
		{
			TriggerEffect(def.explosionEffect, ((Projectile)this).destination);
			if (def.causefireChance > 0f && Rand.Chance(def.causefireChance))
			{
				FireUtility.TryStartFireIn(IntVec3Utility.ToIntVec3(((Projectile)this).destination), ((Projectile)this).launcher.Map, 0.05f, (Thing)null, (SimpleCurve)null);
			}
		}
		else
		{
			if (hitThing is Pawn && flag)
			{
				SpawnBeamReflections(val2, val3, 5);
			}
			if (def.causefireChance > 0f && Rand.Range(0f, 1f) > def.causefireChance)
			{
				FireUtility.TryAttachFire(hitThing, 0.05f, (Thing)null);
			}
			TriggerEffect(def.explosionEffect, ((Projectile)this).ExactPosition);
		}
		((Bullet)this).Impact(hitThing, blockedByShield);
	}

	protected virtual void Explode(Thing hitThing, bool destroy = false)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		Map map = ((Thing)this).Map;
		IntVec3 val = ((hitThing != null) ? hitThing.PositionHeld : IntVec3Utility.ToIntVec3(((Projectile)this).destination));
		if (destroy)
		{
			((Thing)this).Destroy((DestroyMode)0);
		}
		if (((ThingDef)def).projectile.explosionEffect != null)
		{
			Effecter obj = ((ThingDef)def).projectile.explosionEffect.Spawn();
			obj.Trigger(new TargetInfo(val, map, false), new TargetInfo(val, map, false), -1);
			obj.Cleanup();
		}
		Map val2 = map;
		float explosionRadius = ((ThingDef)def).projectile.explosionRadius;
		DamageDef damageDef = ((ThingDef)def).projectile.damageDef;
		Thing launcher = ((Projectile)this).launcher;
		int damageAmount = ((ThingDef)def).projectile.GetDamageAmount(1f, (Thing)null, (StringBuilder)null);
		SoundDef soundExplode = ((ThingDef)def).projectile.soundExplode;
		ThingDef equipmentDef = ((Projectile)this).equipmentDef;
		ThingDef val3 = (ThingDef)(object)def;
		ThingDef postExplosionSpawnThingDef = ((ThingDef)def).projectile.postExplosionSpawnThingDef;
		float postExplosionSpawnChance = ((ThingDef)def).projectile.postExplosionSpawnChance;
		int postExplosionSpawnThingCount = ((ThingDef)def).projectile.postExplosionSpawnThingCount;
		ThingDef preExplosionSpawnThingDef = ((ThingDef)def).projectile.preExplosionSpawnThingDef;
		GenExplosion.DoExplosion(val, val2, explosionRadius, damageDef, launcher, damageAmount, 0f, soundExplode, equipmentDef, val3, (Thing)null, postExplosionSpawnThingDef, postExplosionSpawnChance, postExplosionSpawnThingCount, ((ThingDef)def).projectile.postExplosionGasType, (float?)null, 255, ((ThingDef)def).projectile.applyDamageToExplosionCellsNeighbors, preExplosionSpawnThingDef, ((ThingDef)def).projectile.preExplosionSpawnChance, ((ThingDef)def).projectile.preExplosionSpawnThingCount, ((ThingDef)def).projectile.explosionChanceToStartFire, ((ThingDef)def).projectile.explosionDamageFalloff, (float?)null, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
	}
}
