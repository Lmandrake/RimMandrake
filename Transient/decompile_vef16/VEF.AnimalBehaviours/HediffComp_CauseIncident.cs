using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_CauseIncident : HediffComp
{
	public bool waitingForNight;

	public int checkingForNightInterval = 100;

	public HediffCompProperties_CauseIncident Props => (HediffCompProperties_CauseIncident)(object)base.props;

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		Scribe_Values.Look<bool>(ref waitingForNight, "waitingForNight", false, false);
	}

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (!waitingForNight && Gen.IsHashIntervalTick((Thing)(object)((Hediff)base.parent).pawn, Props.checkingInterval, delta) && ((Thing)((Hediff)base.parent).pawn).Map != null && (!Props.requiresTamed || (Props.requiresTamed && ((Thing)((Hediff)base.parent).pawn).Faction != null && ((Thing)((Hediff)base.parent).pawn).Faction.IsPlayer)))
		{
			IncidentDef val = IncidentDef.Named(Props.incidentToCause);
			if (((Def)val).defName == "Aurora")
			{
				waitingForNight = true;
			}
			else
			{
				IncidentParms val2 = StorytellerUtility.DefaultParmsNow(val.category, (IIncidentTarget)(object)((Thing)((Hediff)base.parent).pawn).Map);
				val.Worker.TryExecute(val2);
			}
		}
		if (waitingForNight && Gen.IsHashIntervalTick((Thing)(object)((Hediff)base.parent).pawn, checkingForNightInterval, delta) && ((Thing)((Hediff)base.parent).pawn).Map != null && GenCelestial.CurCelestialSunGlow(((Thing)((Hediff)base.parent).pawn).Map) <= 0.4f && (!Props.requiresTamed || (Props.requiresTamed && ((Thing)((Hediff)base.parent).pawn).Faction != null && ((Thing)((Hediff)base.parent).pawn).Faction.IsPlayer)))
		{
			IncidentDef obj = IncidentDef.Named(Props.incidentToCause);
			IncidentParms val3 = StorytellerUtility.DefaultParmsNow(obj.category, (IIncidentTarget)(object)((Thing)((Hediff)base.parent).pawn).Map);
			obj.Worker.TryExecute(val3);
			waitingForNight = false;
		}
	}
}
