using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_HighlyFlammable : CompProperties
{
	public string hediffToInflict = "";

	public int tickInterval = 50;

	public CompProperties_HighlyFlammable()
	{
		base.compClass = typeof(CompHighlyFlammable);
	}
}
