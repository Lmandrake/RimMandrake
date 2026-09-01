using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_ExplodeOnFire : HediffComp
{
	public bool onCoolDown;

	public int coolDownCounter;

	public HediffCompProperties_ExplodeOnFire Props => (HediffCompProperties_ExplodeOnFire)(object)base.props;

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		Scribe_Values.Look<bool>(ref onCoolDown, "onCoolDown", false, true);
		Scribe_Values.Look<int>(ref coolDownCounter, "coolDownCounter", 0, false);
	}

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (!onCoolDown && Gen.IsHashIntervalTick((Thing)(object)((Hediff)base.parent).pawn, Props.checkInterval, delta) && ((Thing)((Hediff)base.parent).pawn).Map != null && FireUtility.IsBurning((Thing)(object)((Hediff)base.parent).pawn) && ((Fire)AttachmentUtility.GetAttachment((Thing)(object)((Hediff)base.parent).pawn, ThingDefOf.Fire)).fireSize >= (float)Props.minFireToExplode)
		{
			GenExplosion.DoExplosion(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map, Props.radius, Props.damageType, (Thing)(object)((Hediff)base.parent).pawn, Props.damageAmount, -1f, (SoundDef)null, (ThingDef)null, (ThingDef)null, (Thing)null, (ThingDef)null, 0f, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
			onCoolDown = true;
		}
		if (onCoolDown)
		{
			coolDownCounter += delta;
			if (coolDownCounter > Props.ticksToRecheck)
			{
				onCoolDown = false;
			}
		}
	}
}
