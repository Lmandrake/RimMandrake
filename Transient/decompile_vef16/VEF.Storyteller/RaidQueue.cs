using System;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class RaidQueue : IExposable
{
	public IncidentDef incidentDef;

	public IncidentParms parms;

	public int tickToFire;

	public RaidQueue()
	{
	}

	public RaidQueue(IncidentDef incidentDef, IncidentParms parms, int tickToFire)
	{
		this.incidentDef = incidentDef;
		this.parms = parms;
		this.tickToFire = tickToFire;
	}

	public void ExposeData()
	{
		Scribe_Defs.Look<IncidentDef>(ref incidentDef, "incidentDef");
		Scribe_Deep.Look<IncidentParms>(ref parms, "parms", Array.Empty<object>());
		Scribe_Values.Look<int>(ref tickToFire, "tickToFire", 0, false);
	}
}
