using Verse;

namespace VEF.AnimalBehaviours;

public class CompHediffAfterHealthLoss : ThingComp
{
	public CompProperties_HediffAfterHealthLoss Props => (CompProperties_HediffAfterHealthLoss)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
	}

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickInterval, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (val == null || ((Thing)val).Map == null || val.Dead || val.Downed)
		{
			return;
		}
		if (val.health.summaryHealth.SummaryHealthPercent < (float)Props.healthPercent / 100f)
		{
			if (!val.health.hediffSet.HasHediff(Props.hediff, false))
			{
				val.health.AddHediff(Props.hediff, val.health.hediffSet.GetBodyPartRecord(Props.bodyPart), (DamageInfo?)null, (DamageResult)null);
			}
			val.health.hediffSet.GetFirstHediffOfDef(Props.hediff, false).Severity = Props.severity;
			val.Drawer.renderer.SetAllGraphicsDirty();
		}
		else if (val.health.hediffSet.HasHediff(Props.hediff, false))
		{
			val.health.RemoveHediff(val.health.hediffSet.GetFirstHediffOfDef(Props.hediff, false));
			val.Drawer.renderer.SetAllGraphicsDirty();
		}
	}
}
