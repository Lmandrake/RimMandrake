using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_ReducePrisonerResistance : HediffComp
{
	public HediffCompProperties_ReducePrisonerResistance Props => (HediffCompProperties_ReducePrisonerResistance)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.checkingInterval, delta))
		{
			((HediffComp)this).Pawn.guest.resistance = Mathf.Max(0f, ((HediffComp)this).Pawn.guest.resistance - (float)Props.checkingInterval * Props.resistancePerTick);
		}
	}
}
