using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompCauseIncident : ThingComp
{
	public bool waitingForNight;

	public int checkingForNightInterval = 100;

	public CompProperties_CauseIncident Props => (CompProperties_CauseIncident)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<bool>(ref waitingForNight, "waitingForNight", false, false);
	}

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		if (!waitingForNight && Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.checkingInterval, delta) && ((Thing)base.parent).Map != null && (!Props.requiresTamed || (Props.requiresTamed && ((Thing)base.parent).Faction != null && ((Thing)base.parent).Faction.IsPlayer)))
		{
			IncidentDef val = IncidentDef.Named(Props.incidentToCause);
			if (((Def)val).defName == "Aurora")
			{
				waitingForNight = true;
			}
			else
			{
				IncidentParms val2 = StorytellerUtility.DefaultParmsNow(val.category, (IIncidentTarget)(object)((Thing)base.parent).Map);
				val.Worker.TryExecute(val2);
			}
		}
		if (waitingForNight && Gen.IsHashIntervalTick((Thing)(object)base.parent, checkingForNightInterval, delta) && ((Thing)base.parent).Map != null && GenCelestial.CurCelestialSunGlow(((Thing)base.parent).Map) <= 0.4f && (!Props.requiresTamed || (Props.requiresTamed && ((Thing)base.parent).Faction != null && ((Thing)base.parent).Faction.IsPlayer)))
		{
			IncidentDef obj = IncidentDef.Named(Props.incidentToCause);
			IncidentParms val3 = StorytellerUtility.DefaultParmsNow(obj.category, (IIncidentTarget)(object)((Thing)base.parent).Map);
			obj.Worker.TryExecute(val3);
			waitingForNight = false;
		}
	}
}
