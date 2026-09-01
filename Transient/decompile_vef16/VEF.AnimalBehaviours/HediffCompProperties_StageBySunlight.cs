using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_StageBySunlight : HediffCompProperties
{
	public float sunlightStageIndex = 0.1f;

	public float sunlessStageIndex = 1f;

	public HediffCompProperties_StageBySunlight()
	{
		base.compClass = typeof(HediffComp_StageBySunlight);
	}
}
