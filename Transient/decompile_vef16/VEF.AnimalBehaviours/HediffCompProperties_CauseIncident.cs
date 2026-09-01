using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_CauseIncident : HediffCompProperties
{
	public int checkingInterval = 450000;

	public bool requiresTamed;

	public string incidentToCause;

	public HediffCompProperties_CauseIncident()
	{
		base.compClass = typeof(HediffComp_CauseIncident);
	}
}
