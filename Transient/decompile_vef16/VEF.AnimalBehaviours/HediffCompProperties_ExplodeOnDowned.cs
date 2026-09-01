using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_ExplodeOnDowned : HediffCompProperties
{
	public HediffCompProperties_ExplodeOnDowned()
	{
		base.compClass = typeof(HediffComp_ExplodeOnDowned);
	}
}
