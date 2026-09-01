using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_AutoPermanentInjury : HediffCompProperties
{
	public HediffCompProperties_AutoPermanentInjury()
	{
		base.compClass = typeof(HediffComp_AutoPermanentInjury);
	}
}
