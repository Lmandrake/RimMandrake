using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class CompPassiveRegenerator : ThingComp
{
	public List<Pawn> pawnList = new List<Pawn>();

	public Pawn thisPawn;

	public CompProperties_PassiveRegenerator Props => (CompProperties_PassiveRegenerator)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0150: Unknown result type (might be due to invalid IL or missing references)
		//IL_0155: Unknown result type (might be due to invalid IL or missing references)
		//IL_0170: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		if (!AnimalBehaviours_Settings.flagRegeneration || !Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickInterval, delta))
		{
			return;
		}
		ref Pawn reference = ref thisPawn;
		ThingWithComps parent = base.parent;
		reference = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (thisPawn == null || ((Thing)thisPawn).Map == null || thisPawn.Dead || thisPawn.Downed || (Props.needsToBeTamed && (!Props.needsToBeTamed || ((Thing)thisPawn).Faction == null || !((Thing)thisPawn).Faction.IsPlayer)))
		{
			return;
		}
		foreach (Thing item in GenRadial.RadialDistinctThingsAround(((Thing)thisPawn).Position, ((Thing)thisPawn).Map, (float)Props.radius, true))
		{
			Pawn val = (Pawn)(object)((item is Pawn) ? item : null);
			if (val == null || val.Dead || !val.RaceProps.IsFlesh || val == base.parent)
			{
				continue;
			}
			if (Props.showEffect)
			{
				SoundStarter.PlayOneShot(SoundDefOf.PsychicPulseGlobal, SoundInfo.op_Implicit(new TargetInfo(((Thing)base.parent).Position, ((Thing)base.parent).Map, false)));
				FleckMaker.AttachedOverlay((Thing)(object)base.parent, DefDatabase<FleckDef>.GetNamed("PsycastPsychicEffect", true), Vector3.zero, 1f, -1f);
			}
			if (val.health == null)
			{
				continue;
			}
			IEnumerable<Hediff_Injury> enumerable = val.health.hediffSet.GetHediffsTendable().OfType<Hediff_Injury>();
			if (enumerable == null)
			{
				continue;
			}
			Hediff_Injury[] array = enumerable.ToArray();
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
