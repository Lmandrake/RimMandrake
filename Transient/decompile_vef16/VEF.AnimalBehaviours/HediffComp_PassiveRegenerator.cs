using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class HediffComp_PassiveRegenerator : HediffComp
{
	public List<Pawn> pawnList = new List<Pawn>();

	public Pawn thisPawn;

	public HediffCompProperties_PassiveRegenerator Props => (HediffCompProperties_PassiveRegenerator)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0140: Unknown result type (might be due to invalid IL or missing references)
		//IL_0156: Unknown result type (might be due to invalid IL or missing references)
		//IL_015b: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.tickInterval, delta))
		{
			return;
		}
		thisPawn = ((Hediff)base.parent).pawn;
		if (thisPawn == null || ((Thing)thisPawn).Map == null || thisPawn.Dead || thisPawn.Downed || (Props.needsToBeTamed && (!Props.needsToBeTamed || ((Thing)thisPawn).Faction == null || !((Thing)thisPawn).Faction.IsPlayer)))
		{
			return;
		}
		foreach (Thing item in GenRadial.RadialDistinctThingsAround(((Thing)thisPawn).Position, ((Thing)thisPawn).Map, (float)Props.radius, true))
		{
			Pawn val = (Pawn)(object)((item is Pawn) ? item : null);
			if (val == null || val.Dead || !val.RaceProps.IsFlesh || val == ((Hediff)base.parent).pawn)
			{
				continue;
			}
			if (Props.showEffect)
			{
				SoundStarter.PlayOneShot(SoundDefOf.PsychicPulseGlobal, SoundInfo.op_Implicit(new TargetInfo(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map, false)));
				FleckMaker.AttachedOverlay((Thing)(object)((Hediff)base.parent).pawn, DefDatabase<FleckDef>.GetNamed("PsycastPsychicEffect", true), Vector3.zero, 1f, -1f);
			}
			if (val.health == null)
			{
				continue;
			}
			Hediff_Injury[] array = val.health.hediffSet.GetHediffsTendable().OfType<Hediff_Injury>().ToArray();
			if (!array.Any())
			{
				continue;
			}
			if (Props.healAll)
			{
				Hediff_Injury[] array2 = array;
				int num = 0;
				if (num < array2.Length)
				{
					Hediff_Injury obj = array2[num];
					((Hediff)obj).Severity = ((Hediff)obj).Severity - Props.healAmount;
				}
			}
			else
			{
				Hediff_Injury obj2 = GenCollection.RandomElement<Hediff_Injury>((IEnumerable<Hediff_Injury>)array);
				((Hediff)obj2).Severity = ((Hediff)obj2).Severity - Props.healAmount;
			}
		}
	}
}
