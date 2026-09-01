using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompDiseasesAfterPeriod : ThingComp, PawnGizmoProvider
{
	public int tickCounter;

	public CompProperties_DiseasesAfterPeriod Props => (CompProperties_DiseasesAfterPeriod)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int>(ref tickCounter, "tickCounter", 0, false);
	}

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		tickCounter += delta;
		if (tickCounter < Props.timeToApplyInTicks)
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (val != null && ((Thing)val).Map != null)
		{
			HediffDef val2 = GenCollection.RandomElement<HediffDef>((IEnumerable<HediffDef>)Props.hediffsToApply);
			if (val.health.hediffSet.GetFirstHediffOfDef(val2, false) == null)
			{
				val.health.AddHediff(val2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
		tickCounter = (int)((float)Props.timeToApplyInTicks * Props.percentageOfMaxToReapply);
	}

	public IEnumerable<Gizmo> GetGizmos()
	{
		if (DebugSettings.ShowDevGizmos)
		{
			Command_Action val = new Command_Action();
			((Command)val).defaultLabel = "DEBUG: Give age related diseases";
			((Command)val).icon = (Texture)(object)TexCommand.DesirePower;
			val.action = delegate
			{
				tickCounter = Props.timeToApplyInTicks - 10;
			};
			yield return (Gizmo)(object)val;
		}
	}
}
