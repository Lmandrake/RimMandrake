using Verse;

namespace VEF.AnimalBehaviours;

public class CompHediffByTemperature : ThingComp
{
	public CompProperties_HediffByTemperature Props => (CompProperties_HediffByTemperature)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
	}

	public override void CompTickInterval(int delta)
	{
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
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
		float temperature = GridsUtility.GetTemperature(((Thing)val).Position, ((Thing)val).Map);
		if (Props.doTemperatureAbove && temperature > Props.temperatureAbove)
		{
			if (!val.health.hediffSet.HasHediff(Props.hediffAbove, false))
			{
				val.health.AddHediff(Props.hediffAbove, val.health.hediffSet.GetBodyPartRecord(Props.bodyPart), (DamageInfo?)null, (DamageResult)null);
			}
			val.health.hediffSet.GetFirstHediffOfDef(Props.hediffAbove, false).Severity = Props.severity;
			val.Drawer.renderer.SetAllGraphicsDirty();
		}
		else if (Props.hediffAbove != null && val.health.hediffSet.HasHediff(Props.hediffAbove, false))
		{
			val.health.RemoveHediff(val.health.hediffSet.GetFirstHediffOfDef(Props.hediffAbove, false));
			val.Drawer.renderer.SetAllGraphicsDirty();
		}
		if (Props.doTemperatureBelow && temperature < Props.temperatureBelow)
		{
			if (!val.health.hediffSet.HasHediff(Props.hediffBelow, false))
			{
				val.health.AddHediff(Props.hediffBelow, val.health.hediffSet.GetBodyPartRecord(Props.bodyPart), (DamageInfo?)null, (DamageResult)null);
			}
			val.health.hediffSet.GetFirstHediffOfDef(Props.hediffBelow, false).Severity = Props.severity;
			val.Drawer.renderer.SetAllGraphicsDirty();
		}
		else if (Props.hediffBelow != null && val.health.hediffSet.HasHediff(Props.hediffBelow, false))
		{
			val.health.RemoveHediff(val.health.hediffSet.GetFirstHediffOfDef(Props.hediffBelow, false));
			val.Drawer.renderer.SetAllGraphicsDirty();
		}
	}
}
