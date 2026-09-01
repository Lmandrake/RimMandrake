using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_Exploder : HediffComp
{
	public HediffCompProperties_Exploder Props => (HediffCompProperties_Exploder)(object)base.props;

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = ((Hediff)base.parent).pawn;
		Corpse val = ((pawn != null) ? pawn.Corpse : null);
		if (val != null && ((Thing)val).Map != null)
		{
			GenExplosion.DoExplosion(((Thing)((Hediff)base.parent).pawn.Corpse).Position, ((Thing)((Hediff)base.parent).pawn.Corpse).Map, Props.explosionForce, Props.damageDef, (Thing)(object)((Hediff)base.parent).pawn.Corpse, -1, -1f, (SoundDef)null, (ThingDef)null, (ThingDef)null, (Thing)null, (ThingDef)null, 0f, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
		}
	}
}
