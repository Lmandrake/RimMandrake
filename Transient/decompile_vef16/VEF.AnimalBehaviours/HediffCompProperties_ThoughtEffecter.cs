using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_ThoughtEffecter : HediffCompProperties
{
	public int radius = 1;

	public int tickInterval = 1000;

	public string thoughtDef = "AteWithoutTable";

	public bool showEffect;

	public bool needsToBeTamed;

	public bool conditionalOnWellBeing;

	public string thoughtDefWhenSuffering = "AteWithoutTable";

	public HediffCompProperties_ThoughtEffecter()
	{
		base.compClass = typeof(HediffComp_ThoughtEffecter);
	}
}
