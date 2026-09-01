using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_LastStand : CompProperties
{
	public float finalCoolDownMultiplier = 2f;

	public CompProperties_LastStand()
	{
		base.compClass = typeof(CompLastStand);
	}
}
