using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_RegrowLimbs : HediffCompProperties
{
	public HediffDef regeneratingHediff;

	public HediffCompProperties_RegrowLimbs()
	{
		base.compClass = typeof(HediffComp_RegrowLimbs);
	}
}
