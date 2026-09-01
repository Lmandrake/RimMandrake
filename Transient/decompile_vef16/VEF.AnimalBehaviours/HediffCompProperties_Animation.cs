using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_Animation : HediffCompProperties
{
	public AnimationDef animation;

	public bool shamblerParticles;

	public HediffCompProperties_Animation()
	{
		base.compClass = typeof(HediffComp_Animation);
	}
}
