using System.Collections.Generic;
using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class Ability_Explode : Ability
{
	public override void Cast(params GlobalTargetInfo[] targets)
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		base.Cast(targets);
		AbilityExtension_Explosion modExtension = ((Def)def).GetModExtension<AbilityExtension_Explosion>();
		if (modExtension != null)
		{
			for (int i = 0; i < targets.Length; i++)
			{
				GlobalTargetInfo val = targets[i];
				GenExplosion.DoExplosion(modExtension.onCaster ? ((Thing)pawn).Position : ((GlobalTargetInfo)(ref val)).Cell, ((Thing)pawn).Map, modExtension.explosionRadius, modExtension.explosionDamageDef, (Thing)(object)pawn, modExtension.explosionDamageAmount, modExtension.explosionArmorPenetration, modExtension.explosionSound, (ThingDef)null, (ThingDef)null, (Thing)null, modExtension.postExplosionSpawnThingDef, modExtension.postExplosionSpawnChance, modExtension.postExplosionSpawnThingCount, modExtension.postExplosionGasType, modExtension.postExplosionGasRadiusOverride, modExtension.postExplosionGasAmount, modExtension.applyDamageToExplosionCellsNeighbors, modExtension.preExplosionSpawnThingDef, modExtension.preExplosionSpawnChance, modExtension.preExplosionSpawnThingCount, modExtension.chanceToStartFire, modExtension.damageFalloff, modExtension.explosionDirection, modExtension.casterImmune ? new List<Thing> { (Thing)(object)pawn } : null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
			}
		}
	}
}
