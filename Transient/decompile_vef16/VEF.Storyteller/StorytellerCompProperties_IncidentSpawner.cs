using RimWorld;

namespace VEF.Storyteller;

public class StorytellerCompProperties_IncidentSpawner : StorytellerCompProperties
{
	public IncidentDef incident;

	public float baseIncidentsPerYear;

	public float minSpacingDays;

	public StorytellerCompProperties_IncidentSpawner()
	{
		base.compClass = typeof(StorytellerComp_IncidentSpawner);
	}
}
