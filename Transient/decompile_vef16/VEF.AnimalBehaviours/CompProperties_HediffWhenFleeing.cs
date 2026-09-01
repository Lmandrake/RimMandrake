using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_HediffWhenFleeing : CompProperties
{
	public int tickInterval = 60;

	public HediffDef hediffToCause;

	public bool graphicAndSoundEffect;

	public bool hediffOnRadius;

	public float radius = 3f;

	public CompProperties_HediffWhenFleeing()
	{
		base.compClass = typeof(CompHediffWhenFleeing);
	}
}
