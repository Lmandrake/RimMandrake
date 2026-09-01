using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class ProjectileGorgonStareProjectile : Projectile
{
	protected override void Impact(Thing hitThing, bool blockedByShield = false)
	{
		if (blockedByShield || ((Thing)this).def.projectile.explosionDelay == 0)
		{
			Explode();
			return;
		}
		base.landed = true;
		GenExplosion.NotifyNearbyPawnsOfDangerousExplosive((Thing)(object)this, ((Thing)this).def.projectile.damageDef, base.launcher.Faction, base.launcher);
	}

	protected virtual void Explode()
	{
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		Map map = ((Thing)this).Map;
		((Thing)this).Destroy((DestroyMode)0);
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
		int damageAmount = ((Projectile)this).DamageAmount;
		float armorPenetration = ((Projectile)this).ArmorPenetration;
		ThingDef equipmentDef = base.equipmentDef;
		ThingDef def = ((Thing)this).def;
		Thing thing = ((LocalTargetInfo)(ref base.intendedTarget)).Thing;
		ThingDef postExplosionSpawnThingDef = ((Thing)this).def.projectile.postExplosionSpawnThingDef;
		ThingDef postExplosionSpawnThingDefWater = ((Thing)this).def.projectile.postExplosionSpawnThingDefWater;
		float postExplosionSpawnChance = ((Thing)this).def.projectile.postExplosionSpawnChance;
		int postExplosionSpawnThingCount = ((Thing)this).def.projectile.postExplosionSpawnThingCount;
		GasType? postExplosionGasType = ((Thing)this).def.projectile.postExplosionGasType;
		ThingDef preExplosionSpawnThingDef = ((Thing)this).def.projectile.preExplosionSpawnThingDef;
		float preExplosionSpawnChance = ((Thing)this).def.projectile.preExplosionSpawnChance;
		int preExplosionSpawnThingCount = ((Thing)this).def.projectile.preExplosionSpawnThingCount;
		bool applyDamageToExplosionCellsNeighbors = ((Thing)this).def.projectile.applyDamageToExplosionCellsNeighbors;
		float explosionChanceToStartFire = ((Thing)this).def.projectile.explosionChanceToStartFire;
		bool explosionDamageFalloff = ((Thing)this).def.projectile.explosionDamageFalloff;
		float? num = Vector3Utility.AngleToFlat(base.origin, base.destination);
		FloatRange? val = null;
		float expolosionPropagationSpeed = ((Thing)this).def.projectile.damageDef.expolosionPropagationSpeed;
		float screenShakeFactor = ((Thing)this).def.projectile.screenShakeFactor;
		GenExplosion.DoExplosion(position, map, explosionRadius, damageDef, launcher, damageAmount, armorPenetration, (SoundDef)null, equipmentDef, def, thing, postExplosionSpawnThingDef, postExplosionSpawnChance, postExplosionSpawnThingCount, postExplosionGasType, (float?)null, 255, applyDamageToExplosionCellsNeighbors, preExplosionSpawnThingDef, preExplosionSpawnChance, preExplosionSpawnThingCount, explosionChanceToStartFire, explosionDamageFalloff, num, (List<Thing>)null, val, false, expolosionPropagationSpeed, 0f, false, postExplosionSpawnThingDefWater, screenShakeFactor, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
	}
}
