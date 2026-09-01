using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_CauseIncident : CompProperties
{
	public int checkingInterval = 450000;

	public bool requiresTamed;

	public string incidentToCause;

	public CompProperties_CauseIncident()
	{
		base.compClass = typeof(CompCauseIncident);
	}
}
