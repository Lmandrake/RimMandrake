using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_MindEffecter : CompProperties
{
	public int radius = 1;

	public int tickInterval = 1000;

	public string mentalState = "Berserk";

	public bool notOnlyAffectColonists;

	public CompProperties_MindEffecter()
	{
		base.compClass = typeof(CompMindEffecter);
	}
}
