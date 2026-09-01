using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_CorpseDecayer : CompProperties
{
	public int radius = 5;

	public int tickInterval = 500;

	public int decayOnHitPoints = 1;

	public float nutritionGained = 0.2f;

	public string corpseSound = "";

	public CompProperties_CorpseDecayer()
	{
		base.compClass = typeof(CompCorpseDecayer);
	}
}
