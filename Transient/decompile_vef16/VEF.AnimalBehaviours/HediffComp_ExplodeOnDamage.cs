using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_ExplodeOnDamage : HediffComp
{
	public HediffCompProperties_ExplodeOnDamage Props => (HediffCompProperties_ExplodeOnDamage)(object)base.props;

	public override void Notify_PawnPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).Notify_PawnPostApplyDamage(dinfo, totalDamageDealt);
		if (totalDamageDealt >= (float)Props.minDamageToExplode && ((Thing)((Hediff)base.parent).pawn).Map != null)
		{
			GenExplosion.DoExplosion(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map, Props.radius, Props.damageType, (Thing)(object)((Hediff)base.parent).pawn, Props.damageAmount, -1f, Props.sound, (ThingDef)null, (ThingDef)null, (Thing)null, Props.spawnThingDef, Props.spawnThingChance, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
		}
	}
}
