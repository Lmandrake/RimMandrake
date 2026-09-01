using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class StorytellerComp_IncidentSpawner : StorytellerComp
{
	private StorytellerCompProperties_IncidentSpawner Props => (StorytellerCompProperties_IncidentSpawner)(object)base.props;

	public override IEnumerable<FiringIncident> MakeIntervalIncidents(IIncidentTarget target)
	{
		int incCount = IncidentCycleUtility.IncidentCountThisInterval(target, Find.Storyteller.storytellerComps.IndexOf((StorytellerComp)(object)this), ((StorytellerCompProperties)Props).minDaysPassed, 60f, 0f, Props.minSpacingDays, Props.baseIncidentsPerYear, Props.baseIncidentsPerYear, 1f);
		for (int i = 0; i < incCount; i++)
		{
			IncidentParms val = ((StorytellerComp)this).GenerateParms(Props.incident.category, target);
			if (Props.incident.Worker.CanFireNow(val))
			{
				yield return new FiringIncident(Props.incident, (StorytellerComp)(object)this, val);
			}
		}
	}

	public override string ToString()
	{
		return ((StorytellerComp)this).ToString() + " (" + ((Def)Props.incident).defName + ")";
	}
}
