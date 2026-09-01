using Verse;

namespace VEF.Storyteller;

public class StorytellerDefExtension : DefModExtension
{
	private static readonly StorytellerDefExtension DefaultValues = new StorytellerDefExtension();

	public RaidRestlessness raidRestlessness;

	public StorytellerThreat storytellerThreat;

	public IncidentSpawnOptions incidentSpawnOptions;

	public static StorytellerDefExtension Get(Def def)
	{
		return def.GetModExtension<StorytellerDefExtension>() ?? DefaultValues;
	}
}
